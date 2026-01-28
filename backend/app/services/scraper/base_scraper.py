"""
Base scraper class with common functionality
"""
import asyncio
import random
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, Browser, Page
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for scrapers
    """
    
    def __init__(self):
        self.user_agents = settings.SCRAPING_USER_AGENT_POOL.split(', ')
        self.rate_limit = settings.SCRAPING_RATE_LIMIT_SECONDS
        self.max_retries = settings.SCRAPING_MAX_RETRIES
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.init_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close_browser()
    
    async def init_browser(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            logger.info("✅ Browser initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize browser: {e}")
            raise
    
    async def close_browser(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            logger.info("🔒 Browser closed")
        if self.playwright:
            await self.playwright.stop()
    
    async def create_page(self) -> Page:
        """Create a new page with random user agent"""
        if not self.browser:
            await self.init_browser()
        
        context = await self.browser.new_context(
            user_agent=random.choice(self.user_agents),
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        # Block unnecessary resources to speed up scraping
        await page.route("**/*.{png,jpg,jpeg,gif,svg,mp4,mp3,webp,woff,woff2}", lambda route: route.abort())
        
        return page
    
    async def safe_scrape(self, url: str, retry_count: int = 0) -> Optional[Dict[str, Any]]:
        """
        Scrape with retry logic and error handling
        """
        try:
            # Rate limiting
            await asyncio.sleep(self.rate_limit)
            
            page = await self.create_page()
            
            try:
                # Navigate with timeout
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                # Wait a bit for JS to load
                await asyncio.sleep(random.uniform(1, 3))
                
                # Extract data (implemented by subclasses)
                data = await self.extract_data(page)
                
                return data
                
            finally:
                await page.close()
                
        except Exception as e:
            logger.error(f"❌ Scraping failed for {url}: {e}")
            
            # Retry logic
            if retry_count < self.max_retries:
                logger.info(f"🔄 Retrying... (Attempt {retry_count + 1}/{self.max_retries})")
                await asyncio.sleep(random.uniform(3, 7))  # Random delay before retry
                return await self.safe_scrape(url, retry_count + 1)
            
            return None
    
    @abstractmethod
    async def extract_data(self, page: Page) -> Dict[str, Any]:
        """
        Extract data from page (to be implemented by subclasses)
        """
        pass
    
    @abstractmethod
    async def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single product (to be implemented by subclasses)
        """
        pass
    
    @abstractmethod
    async def scrape_category(self, category_url: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Scrape a category of products (to be implemented by subclasses)
        """
        pass
    
    def clean_price(self, price_str: str) -> Optional[float]:
        """
        Clean and convert price string to float
        Example: "245,000 XOF" -> 245000.0
        """
        try:
            # Remove currency symbols and spaces
            cleaned = price_str.replace('XOF', '').replace('FCFA', '').replace('CFA', '')
            cleaned = cleaned.replace(' ', '').replace(',', '').replace('.', '')
            cleaned = cleaned.strip()
            
            # Convert to float (assuming last 3 digits are decimals if present)
            if cleaned:
                return float(cleaned)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to clean price '{price_str}': {e}")
            return None
