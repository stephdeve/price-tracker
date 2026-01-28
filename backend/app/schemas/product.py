"""
Product Pydantic schemas
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

from app.models.product import Marketplace


# Base schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    marketplace: Marketplace
    url: str


# Create schema
class ProductCreate(ProductBase):
    external_id: Optional[str] = None
    current_price: float = Field(..., gt=0)
    currency: str = "XOF"


# Response schemas
class ProductResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    category: Optional[str]
    image_url: Optional[str]
    marketplace: Marketplace
    url: str
    current_price: float
    currency: str
    is_available: bool
    last_scraped_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductWithPriceChange(ProductResponse):
    """Product with price change indicator"""
    price_change_percentage: Optional[float] = None
    price_trend: Optional[str] = None  # "up", "down", "stable"
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None


# Tracked Product schemas
class TrackedProductCreate(BaseModel):
    product_id: str
    target_price: Optional[float] = Field(None, gt=0)


class TrackedProductResponse(BaseModel):
    id: str
    product_id: str
    user_id: str
    target_price: Optional[float]
    created_at: datetime
    product: ProductResponse
    
    class Config:
        from_attributes = True


# Product search
class ProductSearchParams(BaseModel):
    q: Optional[str] = Field(None, min_length=2, max_length=200)
    category: Optional[str] = None
    marketplace: Optional[Marketplace] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


# Scraping request
class ScrapeProductRequest(BaseModel):
    url: str = Field(..., min_length=10)
    marketplace: Marketplace
