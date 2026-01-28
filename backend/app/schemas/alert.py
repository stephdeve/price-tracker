"""
Alert Pydantic schemas
"""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING
from datetime import datetime

from app.models.alert import AlertType
from app.models.user import NotificationChannel

if TYPE_CHECKING:
    from app.schemas.product import ProductResponse


# Base schemas
class AlertBase(BaseModel):
    product_id: str
    alert_type: AlertType
    threshold_value: Optional[float] = Field(None, gt=0)
    notification_channel: NotificationChannel


# Create/Update schemas
class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    alert_type: Optional[AlertType] = None
    threshold_value: Optional[float] = Field(None, gt=0)
    notification_channel: Optional[NotificationChannel] = None
    is_active: Optional[bool] = None


# Response schemas
class AlertResponse(BaseModel):
    id: str
    user_id: str
    product_id: str
    alert_type: AlertType
    threshold_value: Optional[float]
    is_active: bool
    notification_channel: NotificationChannel
    last_triggered_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AlertWithProduct(AlertResponse):
    """Alert with product details"""
    product: ProductResponse
