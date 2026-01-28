"""
Price and Prediction Pydantic schemas
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Price History
class PriceHistoryResponse(BaseModel):
    date: datetime
    price: float
    currency: str
    
    class Config:
        from_attributes = True


class PriceHistoryStats(BaseModel):
    """Statistics from price history"""
    current_price: float
    average_price: float
    lowest_price: float
    highest_price: float
    price_change_7d: Optional[float] = None
    price_change_30d: Optional[float] = None
    currency: str


# Predictions
class PricePredictionPoint(BaseModel):
    date: datetime
    predicted_price: float
    lower_bound: float  # Confidence interval
    upper_bound: float


class PricePredictionResponse(BaseModel):
    product_id: str
    current_price: float
    predictions: List[PricePredictionPoint]
    forecast_days: int
    best_buy_date: Optional[datetime] = None
    predicted_lowest_price: Optional[float] = None
    confidence_score: float  # 0-1


class PriceChartData(BaseModel):
    """Combined historical and prediction data for charts"""
    product_id: str
    product_name: str
    current_price: float
    currency: str
    historical_prices: List[PriceHistoryResponse]
    predictions: Optional[List[PricePredictionPoint]] = None
    stats: PriceHistoryStats
