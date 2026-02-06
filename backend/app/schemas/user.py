"""
User Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re

from app.models.user import NotificationChannel


# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: str = Field(..., min_length=8, max_length=20)


# Create/Update schemas
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('phone')
    def validate_benin_phone(cls, v):
        """Validate Beninese phone number format"""
        # Remove spaces and special chars
        cleaned = re.sub(r'[^\d+]', '', v)
        
        # Benin format: +229XXXXXXXX or 229XXXXXXXX or just XXXXXXXX
        if cleaned.startswith('+229'):
            if len(cleaned) != 12:
                raise ValueError('Numéro béninois invalide (format: +229XXXXXXXX)')
        elif cleaned.startswith('229'):
            if len(cleaned) != 11:
                raise ValueError('Numéro béninois invalide (format: 229XXXXXXXX)')
        else:
            if len(cleaned) != 8:
                raise ValueError('Numéro béninois invalide (8 chiffres requis)')
            cleaned = f'+229{cleaned}'
        
        return cleaned


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = None
    telegram_id: Optional[str] = None
    whatsapp_number: Optional[str] = None
    preferred_notification: Optional[NotificationChannel] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Response schemas
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    is_premium: bool
    is_verified: bool
    premium_expires_at: Optional[datetime] = None
    preferred_notification_channel: NotificationChannel
    telegram_user_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """User statistics"""
    tracked_products_count: int
    active_alerts_count: int
    is_premium: bool
    tracking_limit: int
    tracking_remaining: int


# Token schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # user_id
    exp: int
    type: str  # "access" or "refresh"


class RefreshTokenRequest(BaseModel):
    refresh_token: str
