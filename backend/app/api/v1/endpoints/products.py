"""
Product endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.product import Product, Marketplace
from app.models.tracked_product import TrackedProduct
from app.models.price import PriceHistory, PriceSource
from app.schemas.product import (
    ProductResponse,
    ProductWithPriceChange,
    TrackedProductCreate,
    TrackedProductResponse,
    ScrapeProductRequest
)
from app.schemas.prediction import PriceHistoryResponse, PriceDropItem
from app.schemas.compare import AggregatedGroupResponse, AggregatedOfferResponse
from app.services.aggregator import group_products
from app.services.scraper.jumia_scraper import JumiaScraper, simple_scrape_jumia
from app.services.scraper.amazon_scraper import AmazonScraper

router = APIRouter(tags=["Products"])


@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    marketplace: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all available products with pagination
    
    - **page**: Page number (default: 1)
    - **limit**: Items per page (max: 100)
    - **category**: Filter by category
    - **marketplace**: Filter by marketplace (jumia, amazon, local_market)
    - **search**: Search in product name
    """
    query = select(Product)
    
    # Apply filters
    filters = []
    if category:
        filters.append(Product.category == category)
    if marketplace:
        filters.append(Product.marketplace == marketplace)
    if search:
        filters.append(Product.name.ilike(f"%{search}%"))
    
    if filters:
        query = query.where(and_(*filters))
    
    # Pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Product.created_at.desc())
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return products


@router.get("/products/price-drops", response_model=List[PriceDropItem])
async def get_price_drops(
    window_days: int = Query(30, ge=7, le=180),
    min_drop_pct: float = Query(10.0, ge=1.0, le=90.0),
    min_z: float = Query(-1.0, ge=-5.0, le=0.0),
    sample_limit: int = Query(500, ge=10, le=2000),
    db: AsyncSession = Depends(get_db),
):
    """
    Detect price drops using rolling mean/std over a time window.
    Conditions:
    - latest price below previous mean by at least `min_drop_pct` percent
    - optional z-score threshold (latest vs mean/std) <= min_z (negative)
    """
    # Select a sample of recent products to limit workload
    prod_res = await db.execute(
        select(Product).order_by(Product.created_at.desc()).limit(sample_limit)
    )
    products = prod_res.scalars().all()

    from datetime import datetime, timedelta
    since = datetime.utcnow() - timedelta(days=window_days)

    drops: List[PriceDropItem] = []
    for p in products:
        hist_res = await db.execute(
            select(PriceHistory)
            .where(PriceHistory.product_id == p.id)
            .where(PriceHistory.scraped_at >= since)
            .order_by(PriceHistory.scraped_at.asc())
        )
        rows = hist_res.scalars().all()
        if len(rows) < 2:
            continue
        # latest is last
        latest = rows[-1]
        prior = rows[:-1]
        prior_prices = [r.price for r in prior if r.price is not None]
        if len(prior_prices) < 1:
            continue
        avg = sum(prior_prices) / len(prior_prices)
        # std
        if len(prior_prices) > 1:
            var = sum((x - avg) ** 2 for x in prior_prices) / (len(prior_prices) - 1)
            std = var ** 0.5
        else:
            std = 0.0
        if avg <= 0:
            continue
        drop_pct = (avg - latest.price) / avg * 100.0
        if drop_pct < min_drop_pct:
            continue
        z = None
        if std and std > 0:
            z = (latest.price - avg) / std
            if z > min_z:
                # Not significant drop by z-score
                continue
        drops.append(
            PriceDropItem(
                product_id=p.id,
                name=p.name,
                marketplace=str(p.marketplace),
                current_price=latest.price,
                currency=latest.currency,
                drop_pct=round(drop_pct, 2),
                previous_mean=round(avg, 2),
                previous_std=round(std, 2) if std else None,
                last_change_at=latest.scraped_at,
                url=p.url,
                image_url=p.image_url,
            )
        )

    # Sort by drop percentage desc, take top N
    drops.sort(key=lambda d: d.drop_pct, reverse=True)
    return drops[:50]


@router.get("/products/{product_id}/history", response_model=List[PriceHistoryResponse])
async def get_product_history(
    product_id: str,
    limit: int = Query(365, ge=1, le=2000),
    db: AsyncSession = Depends(get_db)
):
    """
    Return chronological price history for a product.
    """
    result = await db.execute(
        select(PriceHistory)
        .where(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.scraped_at.asc())
        .limit(limit)
    )
    rows = result.scalars().all()
    # Map scraped_at -> date in response
    return [PriceHistoryResponse(date=r.scraped_at, price=r.price, currency=r.currency) for r in rows]


@router.get("/products/{product_id}/compare", response_model=AggregatedGroupResponse)
async def compare_product(
    product_id: str,
    max_candidates: int = Query(200, ge=10, le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    Group a product with similar offers across sources using matching heuristics.
    """
    # Load target product
    result = await db.execute(select(Product).where(Product.id == product_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produit non trouvé")

    # Build a simple candidate query using tokens from name and same category
    tokens = [t for t in (target.name or "").split() if len(t) > 2]
    filters = []
    for t in tokens[:6]:
        filters.append(Product.name.ilike(f"%{t}%"))
    if target.category:
        filters.append(Product.category == target.category)

    cand_query = select(Product).where(or_(*filters)).limit(max_candidates)
    cand_res = await db.execute(cand_query)
    candidates = cand_res.scalars().all()

    groups = group_products([target] + [p for p in candidates if p.id != target.id])

    # Find the group containing the target
    from app.schemas.compare import AggregatedOfferResponse
    for g in groups:
        contains = any(o.product_id == target.id for o in g.offers)
        if contains:
            return AggregatedGroupResponse(
                canonical_title=g.canonical_title,
                brand=g.brand,
                attributes=g.attributes,
                offers=[
                    AggregatedOfferResponse(
                        product_id=o.product_id,
                        title=o.title,
                        marketplace=o.marketplace,
                        price=o.price,
                        currency=o.currency,
                        is_available=o.is_available,
                        url=o.url,
                        image_url=o.image_url,
                    )
                    for o in g.offers
                ],
                best_price=g.best_price,
                min_price=g.min_price,
                max_price=g.max_price,
            )

    # Fallback: single-offer group
    return AggregatedGroupResponse(
        canonical_title=target.name,
        brand=None,
        attributes={},
        offers=[
            AggregatedOfferResponse(
                product_id=target.id,
                title=target.name,
                marketplace=str(target.marketplace),
                price=target.current_price,
                currency=target.currency,
                is_available=target.is_available,
                url=target.url,
                image_url=target.image_url,
            )
        ],
        best_price=target.current_price,
        min_price=target.current_price,
        max_price=target.current_price,
    )


@router.get("/products/compare/search", response_model=List[AggregatedGroupResponse])
async def compare_by_search(
    q: str = Query(..., min_length=2, max_length=200),
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    Aggregate comparable products across sources for a free-text search.
    Returns groups with best price and offers per source.
    """
    query = select(Product).where(
        or_(
            Product.name.ilike(f"%{q}%"),
            Product.description.ilike(f"%{q}%"),
        )
    ).limit(limit)

    result = await db.execute(query)
    products = result.scalars().all()

    groups = group_products(products)

    def to_response(g):
        return AggregatedGroupResponse(
            canonical_title=g.canonical_title,
            brand=g.brand,
            attributes=g.attributes,
            offers=[
                AggregatedOfferResponse(
                    product_id=o.product_id,
                    title=o.title,
                    marketplace=o.marketplace,
                    price=o.price,
                    currency=o.currency,
                    is_available=o.is_available,
                    url=o.url,
                    image_url=o.image_url,
                )
                for o in g.offers
            ],
            best_price=g.best_price,
            min_price=g.min_price,
            max_price=g.max_price,
        )

    return [to_response(g) for g in groups]


@router.get("/products/search", response_model=List[ProductResponse])
async def search_products(
    q: str = Query(..., min_length=2, max_length=200),
    db: AsyncSession = Depends(get_db)
):
    """
    Search products by name or description
    """
    query = select(Product).where(
        or_(
            Product.name.ilike(f"%{q}%"),
            Product.description.ilike(f"%{q}%")
        )
    ).limit(50)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return products


@router.post("/products/track", response_model=TrackedProductResponse, status_code=status.HTTP_201_CREATED)
async def track_product(
    track_data: TrackedProductCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a product to tracking list
    
    Free tier: 5 products max
    Premium: Unlimited
    """
    # Check if product exists
    result = await db.execute(select(Product).where(Product.id == track_data.product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produit non trouvé"
        )
    
    # Check if already tracking
    result = await db.execute(
        select(TrackedProduct).where(
            and_(
                TrackedProduct.user_id == current_user.id,
                TrackedProduct.product_id == track_data.product_id
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous suivez déjà ce produit"
        )
    
    # Check tracking limit for free users
    if not current_user.is_premium:
        result = await db.execute(
            select(func.count(TrackedProduct.id)).where(
                TrackedProduct.user_id == current_user.id
            )
        )
        count = result.scalar()
        
        if count >= settings.FREE_TIER_MAX_TRACKED_PRODUCTS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Limite atteinte ({settings.FREE_TIER_MAX_TRACKED_PRODUCTS} produits). Passez en Premium pour un suivi illimité."
            )
    
    # Create tracked product
    tracked = TrackedProduct(
        user_id=current_user.id,
        product_id=track_data.product_id,
        target_price=track_data.target_price
    )
    
    db.add(tracked)
    await db.commit()
    await db.refresh(tracked)
    
    # Load product relationship
    await db.refresh(tracked, ["product"])
    
    return tracked


@router.get("/products/tracked", response_model=List[TrackedProductResponse])
async def get_tracked_products(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's tracked products
    """
    result = await db.execute(
        select(TrackedProduct)
        .where(TrackedProduct.user_id == current_user.id)
        .order_by(TrackedProduct.created_at.desc())
    )
    tracked_products = result.scalars().all()
    
    # Load product relationships
    for tracked in tracked_products:
        await db.refresh(tracked, ["product"])
    
    return tracked_products


@router.delete("/products/tracked/{tracked_id}", status_code=status.HTTP_204_NO_CONTENT)
async def untrack_product(
    tracked_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove product from tracking
    """
    result = await db.execute(
        select(TrackedProduct).where(
            and_(
                TrackedProduct.id == tracked_id,
                TrackedProduct.user_id == current_user.id
            )
        )
    )
    tracked = result.scalar_one_or_none()
    
    if not tracked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produit suivi non trouvé"
        )
    
    await db.delete(tracked)
    await db.commit()
    
    return None


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get product details by ID
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produit non trouvé"
        )
    
    return product


@router.post("/products/scrape", response_model=ProductResponse)
async def scrape_and_add_product(
    scrape_data: ScrapeProductRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Scrape a product URL and add to database
    
    Premium feature or limited use for free tier
    """
    # Check if product URL already exists
    result = await db.execute(select(Product).where(Product.url == scrape_data.url))
    existing = result.scalar_one_or_none()
    
    if existing:
        return existing
    
    # Scrape product
    try:
        # Auto-detect marketplace from URL if not provided
        # Handle Enum value safely
        try:
            mp = scrape_data.marketplace.value  # type: ignore[attr-defined]
        except Exception:
            mp = str(scrape_data.marketplace)
        marketplace = mp.lower()
        url_lower = scrape_data.url.lower()
        
        if marketplace == "jumia" or "jumia." in url_lower:
            product_data = None
            if not ("amazon" in url_lower):  # Make sure it's not accidentally amazon
                try:
                    async with JumiaScraper() as scraper:
                        product_data = await scraper.scrape_product(scrape_data.url)
                except Exception:
                    # Fallback to lightweight HTTP scraper when Playwright is unavailable
                    product_data = await simple_scrape_jumia(scrape_data.url)
        elif marketplace == "amazon" or "amazon" in url_lower:
            async with AmazonScraper() as scraper:
                product_data = await scraper.scrape_product(scrape_data.url)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Marketplace non supporté. Utilisez Jumia (jumia.ci, jumia.ma, etc.) ou Amazon."
            )
        
        if not product_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de scraper ce produit. Vérifiez que l'URL est valide et accessible."
            )
        
        # Normalize payload for Product model (map price -> current_price)
        payload = {
            "name": product_data.get("name"),
            "description": product_data.get("description"),
            "category": product_data.get("category"),
            "image_url": product_data.get("image_url"),
            "marketplace": Marketplace(product_data.get("marketplace") or marketplace),
            "url": product_data.get("url") or scrape_data.url,
            "current_price": product_data.get("price") or product_data.get("current_price"),
            "currency": product_data.get("currency") or "XOF",
            "is_available": product_data.get("is_available", True),
            "external_id": product_data.get("external_id"),
            "last_scraped_at": datetime.utcnow(),
        }

        if not payload.get("current_price"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prix non détecté sur la page produit"
            )

        # Create product
        product = Product(**payload)
        db.add(product)
        await db.commit()
        await db.refresh(product)
        
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors du scraping: {error_detail[:200]}"
        )
