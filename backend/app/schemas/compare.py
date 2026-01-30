"""
Pydantic schemas for aggregated product comparison responses
"""
from __future__ import annotations

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class AggregatedOfferResponse(BaseModel):
    product_id: str
    title: str
    marketplace: str
    price: float
    currency: str
    is_available: bool
    url: str
    image_url: Optional[str] = None


class AggregatedGroupResponse(BaseModel):
    canonical_title: str
    brand: Optional[str] = None
    attributes: Dict[str, Any]
    offers: List[AggregatedOfferResponse]
    best_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
