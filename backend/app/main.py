"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings


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
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Application de suivi de prix intelligent pour le marché béninois",
    lifespan=lifespan,
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
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
