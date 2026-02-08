"""
Prometheus metrics configuration for FastAPI
"""
from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator

# Custom metrics
scraping_requests_total = Counter(
    'scraping_requests_total',
    'Total number of scraping requests',
    ['marketplace', 'status']
)

scraping_duration_seconds = Histogram(
    'scraping_duration_seconds',
    'Time spent scraping products',
    ['marketplace']
)

products_scraped_total = Counter(
    'products_scraped_total',
    'Total number of products scraped',
    ['marketplace']
)

price_alerts_sent_total = Counter(
    'price_alerts_sent_total',
    'Total number of price alerts sent',
    ['channel']  # telegram, email, whatsapp
)

active_products = Gauge(
    'active_products_total',
    'Total number of active tracked products'
)

celery_tasks_total = Counter(
    'celery_tasks_total',
    'Total number of Celery tasks',
    ['task_name', 'status']
)

celery_task_duration_seconds = Histogram(
    'celery_task_duration_seconds',
    'Time spent executing Celery tasks',
    ['task_name']
)


def setup_metrics(app):
    """Setup Prometheus metrics for FastAPI app"""
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )
    
    instrumentator.instrument(app).expose(app, endpoint="/metrics")
    
    return instrumentator
