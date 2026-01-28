"""
Product endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional

from app.core.config import settings
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.product import Product
from app.models.tracked_product import TrackedProduct
from app.schemas.product import (
    ProductResponse,
    ProductWithPriceChange,
    TrackedProductCreate,
    TrackedProductResponse,
    ScrapeProductRequest
)
from app.services.scraper.jumia_scraper import JumiaScraper
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
        if scrape_data.marketplace == "jumia":
            async with JumiaScraper() as scraper:
                product_data = await scraper.scrape_product(scrape_data.url)
        elif scrape_data.marketplace == "amazon":
            async with AmazonScraper() as scraper:
                product_data = await scraper.scrape_product(scrape_data.url)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Marketplace non supporté"
            )
        
        if not product_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de scraper ce produit"
            )
        
        # Create product
        product = Product(**product_data)
        db.add(product)
        await db.commit()
        await db.refresh(product)
        
        return product
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du scraping: {str(e)}"
        )
