"""
Import all models here for Alembic to detect them
"""
from app.database.session import Base

# Import all models for Alembic autogenerate
from app.models.user import User
from app.models.product import Product
from app.models.price import PriceHistory
from app.models.tracked_product import TrackedProduct
from app.models.alert import Alert
from app.models.subscription import Subscription

__all__ = ["Base", "User", "Product", "PriceHistory", "TrackedProduct", "Alert", "Subscription"]
