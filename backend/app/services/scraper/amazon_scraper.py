"""
Amazon scraper
"""
from typing import Optional, Dict, Any, List
from playwright.async_api import Page
import logging
import re

from app.services.scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class AmazonScraper(BaseScraper):
    """
    Scraper for Amazon (consider using Amazon Product Advertising API as alternative)
    Note: Amazon has strong anti-scraping. This is a basic implementation.
    """
    
    BASE_URL = "https://www.amazon.com"
    
    async def extract_data(self, page: Page) -> Dict[str, Any]:
        """
        Extract product data from Amazon product page
        """
        try:
            # Check availability
            is_available = True
            try:
                out_of_stock = await page.locator("text=Currently unavailable").count()
                is_available = out_of_stock == 0
            except:
                pass
            
            # Extract product name
            name = ""
            try:
                name_elem = await page.locator("#productTitle").first
                name = await name_elem.text_content()
                name = name.strip() if name else ""
            except:
                logger.warning("⚠️ Could not extract Amazon product name")
            
            # Extract price (Amazon has multiple price formats)
            price = 0.0
            price_usd = 0.0
            try:
                # Try whole price
                price_whole = await page.locator(".a-price-whole").first
                price_fraction = await page.locator(".a-price-fraction").first
                
                whole_text = await price_whole.text_content()
                fraction_text = await price_fraction.text_content()
                
                price_str = f"{whole_text}.{fraction_text}".replace(',', '')
                price_usd = float(price_str) if price_str else 0.0
                
                # Convert USD to XOF (approximate rate: 1 USD = 600 XOF)
                # TODO: Use BCEAO API for real-time exchange rate
                price = price_usd * 600
                
            except:
                logger.warning("⚠️ Could not extract Amazon price")
            
            # Extract image
            image_url = ""
            try:
                img_elem = await page.locator("#landingImage").first
                image_url = await img_elem.get_attribute("src")
            except:
                logger.warning("⚠️ Could not extract Amazon image")
            
            # Extract category (from breadcrumb)
            category = ""
            try:
                breadcrumb = await page.locator("#wayfinding-breadcrumbs_container").first
                category_text = await breadcrumb.text_content()
                categories = [c.strip() for c in category_text.split('›')]
                category = categories[-1] if categories else ""
            except:
                logger.warning("⚠️ Could not extract Amazon category")
            
            # Get current URL
            current_url = page.url
            
            # Extract ASIN (Amazon product ID)
            external_id = ""
            match = re.search(r'/dp/([A-Z0-9]{10})', current_url)
            if match:
                external_id = match.group(1)
            
            data = {
                "name": name,
                "price": price,
                "price_original_usd": price_usd,
                "currency": "XOF",
                "image_url": image_url,
                "category": category,
                "is_available": is_available,
                "url": current_url,
                "external_id": external_id,
                "marketplace": "amazon"
            }
            
            logger.info(f"✅ Scraped Amazon product: {name} - ${price_usd} USD ({price} XOF)")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to extract Amazon data: {e}")
            raise
    
    async def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single Amazon product
        """
        logger.info(f"🔍 Scraping Amazon product: {url}")
        logger.warning("⚠️ Consider using Amazon Product Advertising API for more reliable data")
        return await self.safe_scrape(url)
    
    async def scrape_category(self, category_url: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Scrape Amazon category (basic implementation)
        """
        logger.info(f"🔍 Scraping Amazon category: {category_url}")
        logger.warning("⚠️ Amazon category scraping is challenging due to anti-bot measures")
        
        products = []
        # TODO: Implement category scraping or use Amazon API
        return products
