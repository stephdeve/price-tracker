"""
Scraping and alert checking Celery tasks
"""
import logging
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.tasks.celery_app import celery_app
from app.core.config import settings
from app.models.product import Product
from app.models.tracked_product import TrackedProduct
from app.models.price import PriceHistory, PriceSource
from app.models.alert import Alert, AlertType
from app.models.user import User
from app.services.scraper.jumia_scraper import JumiaScraper
from app.services.scraper.amazon_scraper import AmazonScraper

logger = logging.getLogger(__name__)

# Create async engine for Celery tasks
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_db():
    """Get async DB session for tasks"""
    async with AsyncSessionLocal() as session:
        yield session


@celery_app.task(name="app.tasks.scraping_tasks.scrape_product")
def scrape_product_task(product_id: str):
    """
    Scrape a single product and update price
    """
    import asyncio
    
    async def _scrape():
        async with AsyncSessionLocal() as db:
            try:
                # Get product
                result = await db.execute(select(Product).where(Product.id == product_id))
                product = result.scalar_one_or_none()
                
                if not product:
                    logger.warning(f"Product {product_id} not found")
                    return
                
                # Select scraper
                if product.marketplace == "jumia":
                    async with JumiaScraper() as scraper:
                        data = await scraper.scrape_product(product.url)
                elif product.marketplace == "amazon":
                    async with AmazonScraper() as scraper:
                        data = await scraper.scrape_product(product.url)
                else:
                    logger.warning(f"Unsupported marketplace: {product.marketplace}")
                    return
                
                if not data:
                    logger.error(f"Failed to scrape product {product_id}")
                    return
                
                # Update product
                product.current_price = data.get('price', product.current_price)
                product.is_available = data.get('is_available', True)
                product.last_scraped_at = datetime.utcnow()
                
                # Save price history
                price_history = PriceHistory(
                    product_id=product.id,
                    price=data['price'],
                    currency=data.get('currency', 'XOF'),
                    source=PriceSource.SCRAPING
                )
                db.add(price_history)
                
                await db.commit()
                
                logger.info(f"✅ Scraped product {product.name}: {data['price']} XOF")
                
            except Exception as e:
                logger.error(f"❌ Error scraping product {product_id}: {e}")
                await db.rollback()
    
    asyncio.run(_scrape())


@celery_app.task(name="app.tasks.scraping_tasks.scrape_all_tracked_products")
def scrape_all_tracked_products():
    """
    Scrape all unique products that are being tracked
    """
    import asyncio
    
    async def _scrape_all():
        async with AsyncSessionLocal() as db:
            try:
                # Get all unique product IDs being tracked
                result = await db.execute(
                    select(TrackedProduct.product_id).distinct()
                )
                product_ids = [row[0] for row in result.all()]
                
                logger.info(f"🔍 Starting to scrape {len(product_ids)} tracked products")
                
                # Scrape each product (this will spawn subtasks)
                for product_id in product_ids:
                    scrape_product_task.delay(product_id)
                
                logger.info(f"✅ Queued {len(product_ids)} scraping tasks")
                
            except Exception as e:
                logger.error(f"❌ Error in scrape_all_tracked_products: {e}")
    
    asyncio.run(_scrape_all())


@celery_app.task(name="app.tasks.scraping_tasks.check_price_alerts")
def check_price_alerts():
    """
    Check all active alerts and send notifications if conditions are met
    """
    import asyncio
    
    async def _check_alerts():
        async with AsyncSessionLocal() as db:
            try:
                # Get all active alerts
                result = await db.execute(
                    select(Alert).where(Alert.is_active == True)
                )
                alerts = result.scalars().all()
                
                logger.info(f"🔔 Checking {len(alerts)} active alerts")
                
                triggered_count = 0
                
                for alert in alerts:
                    # Load relationships
                    await db.refresh(alert, ["product", "user"])
                    
                    product = alert.product
                    user = alert.user
                    
                    should_trigger = False
                    
                    # Check alert conditions
                    if alert.alert_type == AlertType.TARGET_PRICE:
                        if product.current_price <= alert.threshold_value:
                            should_trigger = True
                    
                    elif alert.alert_type == AlertType.PERCENTAGE_DROP:
                        # Get previous price
                        prev_result = await db.execute(
                            select(PriceHistory)
                            .where(PriceHistory.product_id == product.id)
                            .order_by(PriceHistory.scraped_at.desc())
                            .offset(1)
                            .limit(1)
                        )
                        prev_price = prev_result.scalar_one_or_none()
                        
                        if prev_price:
                            drop_pct = ((prev_price.price - product.current_price) / prev_price.price) * 100
                            if drop_pct >= alert.threshold_value:
                                should_trigger = True
                    
                    elif alert.alert_type == AlertType.AVAILABILITY:
                        if product.is_available:
                            should_trigger = True
                    
                    # Send notification if triggered
                    if should_trigger:
                        # TODO: Send actual notification via Telegram/WhatsApp
                        logger.info(f"🔔 Alert triggered for user {user.email}, product {product.name}")
                        
                        alert.last_triggered_at = datetime.utcnow()
                        triggered_count += 1
                
                await db.commit()
                logger.info(f"✅ Triggered {triggered_count} alerts")
                
            except Exception as e:
                logger.error(f"❌ Error checking alerts: {e}")
                await db.rollback()
    
    asyncio.run(_check_alerts())
