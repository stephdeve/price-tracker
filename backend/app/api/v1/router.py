"""
API v1 Router - Combines all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, products, alerts

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(products.router, prefix="")
api_router.include_router(alerts.router, prefix="")
