"""
Celery application configuration
"""
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "price_tracker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.scraping_tasks",
        "app.tasks.ml_tasks",
    ]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max per task
    task_soft_time_limit=25 * 60,  # Soft limit at 25 minutes
)

# Task routing
celery_app.conf.task_routes = {
    "app.tasks.scraping_tasks.*": {"queue": "scraping"},
    "app.tasks.ml_tasks.*": {"queue": "ml"},
}

# Scheduled tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    # Scrape all tracked products every 12 hours
    "scrape-tracked-products": {
        "task": "app.tasks.scraping_tasks.scrape_all_tracked_products",
        "schedule": crontab(hour="*/12", minute=0),  # Every 12 hours
    },
    
    # Check price alerts every hour
    "check-price-alerts": {
        "task": "app.tasks.scraping_tasks.check_price_alerts",
        "schedule": crontab(minute=0),  # Every hour
    },
    
    # Retrain ML models daily at 2 AM
    "retrain-ml-models": {
        "task": "app.tasks.ml_tasks.retrain_models_daily",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}

if __name__ == "__main__":
    celery_app.start()
