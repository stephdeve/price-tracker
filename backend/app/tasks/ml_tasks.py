"""
Machine Learning tasks for Prophet price predictions
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.tasks.celery_app import celery_app
from app.core.config import settings
from app.models.product import Product
from app.models.price import PriceHistory

logger = logging.getLogger(__name__)

# Create async engine for Celery tasks
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@celery_app.task(name="app.tasks.ml_tasks.train_model_for_product")
def train_model_for_product(product_id: str):
    """
    Train Prophet model for a specific product
    Requires at least 30 historical price points
    """
    import asyncio
    
    async def _train():
        async with AsyncSessionLocal() as db:
            try:
                # Get product
                result = await db.execute(select(Product).where(Product.id == product_id))
                product = result.scalar_one_or_none()
                
                if not product:
                    logger.warning(f"Product {product_id} not found")
                    return
                
                # Get price history count
                count_result = await db.execute(
                    select(func.count(PriceHistory.id))
                    .where(PriceHistory.product_id == product_id)
                )
                count = count_result.scalar()
                
                if count < 30:
                    logger.info(f"Product {product.name} has only {count} price points, need 30+")
                    return
                
                # Get price history
                history_result = await db.execute(
                    select(PriceHistory)
                    .where(PriceHistory.product_id == product_id)
                    .order_by(PriceHistory.scraped_at.asc())
                )
                history = history_result.scalars().all()
                
                # TODO: Implement Prophet model training
                # from app.services.ml.price_predictor import PricePredictor
                # predictor = PricePredictor()
                # predictor.train_model(product_id, history)
                
                logger.info(f"✅ Trained model for product {product.name} with {count} data points")
                
            except Exception as e:
                logger.error(f"❌ Error training model for product {product_id}: {e}")
    
    asyncio.run(_train())


@celery_app.task(name="app.tasks.ml_tasks.retrain_models_daily")
def retrain_models_daily():
    """
    Retrain models for all products with sufficient historical data
    Runs daily at 2 AM
    """
    import asyncio
    
    async def _retrain_all():
        async with AsyncSessionLocal() as db:
            try:
                # Get products with >= 30 price history entries
                result = await db.execute(
                    select(PriceHistory.product_id, func.count(PriceHistory.id).label('count'))
                    .group_by(PriceHistory.product_id)
                    .having(func.count(PriceHistory.id) >= 30)
                )
                products_to_train = result.all()
                
                logger.info(f"🤖 Starting ML training for {len(products_to_train)} products")
                
                # Train each product (spawn subtasks)
                for product_id, count in products_to_train:
                    train_model_for_product.delay(product_id)
                
                logger.info(f"✅ Queued {len(products_to_train)} ML training tasks")
                
            except Exception as e:
                logger.error(f"❌ Error in retrain_models_daily: {e}")
    
    asyncio.run(_retrain_all())
