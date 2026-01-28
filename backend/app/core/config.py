"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    APP_NAME: str = "Price Tracker Bénin"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "mysql+aiomysql://price_user:price_password@localhost:3306/price_tracker"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Security
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Ollama AI (Local - Free)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_USERNAME: str = ""
    
    # WhatsApp (Twilio)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_FROM: str = ""
    
    # KKiapay Payment
    KKIAPAY_PUBLIC_KEY: str = ""
    KKIAPAY_PRIVATE_KEY: str = ""
    KKIAPAY_SECRET: str = ""
    KKIAPAY_WEBHOOK_SECRET: str = ""
    
    # BCEAO API
    BCEAO_API_URL: str = "https://api.bceao.int"
    BCEAO_API_KEY: str = ""
    
    # Scraping Configuration
    SCRAPING_USER_AGENT_POOL: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64), Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    SCRAPING_RATE_LIMIT_SECONDS: int = 5
    SCRAPING_MAX_RETRIES: int = 3
    
    # Subscription Pricing (XOF - Franc CFA)
    PREMIUM_MONTHLY_PRICE_XOF: int = 1000  # ~1.5 EUR
    PREMIUM_YEARLY_PRICE_XOF: int = 10000  # ~15 EUR
    
    # Free Tier Limits
    FREE_TIER_MAX_TRACKED_PRODUCTS: int = 5
    PREMIUM_MAX_TRACKED_PRODUCTS: int = 9999  # Unlimited
    
    # Sentry (Optional)
    SENTRY_DSN: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
