"""
FastAPI main application
"""
import sys
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings, ALLOWED_ORIGINS
# Import all models to register them with SQLAlchemy
from app.models import (
    User,
    Alert,
    PriceHistory,
    Product,
    Subscription,
    TrackedProduct,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events
    """
    # Startup
    print(f"🚀{settings.APP_NAME} v{settings.APP_VERSION} is starting...")
    print(f"📊 Database: {settings.DATABASE_URL.split('@')[-1]}")  # Hide credentials
    print(f"🔴 Redis: {settings.REDIS_URL}")
    
    yield
    
    # Shutdown
    print(f"👋 {settings.APP_NAME} is shutting down...")


# Create FastAPI app
# Ensure proper asyncio event loop policy on Windows for subprocess (Playwright)
# WindowsSelectorEventLoopPolicy is required for asyncio subprocess on Windows in some environments
if sys.platform.startswith("win"):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        # Fallback silently; uvicorn may already have initialized the loop
        pass

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Application de suivi de prix intelligent pour le marché béninois",
    lifespan=lifespan,
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "message": "API de suivi de prix pour le marché béninois 🇧🇯"
    }


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Include API routers
from app.api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")
