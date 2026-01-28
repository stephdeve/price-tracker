"""
Jumia scraper for Benin market
"""
from typing import Optional, Dict, Any, List
from playwright.async_api import Page
import logging
import re

from app.services.scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class JumiaScraper(BaseScraper):
    """
    Scraper for Jumia Bénin (www.jumia.com.bj)
    """
    
    BASE_URL = "https://www.jumia.com.bj"
    
    async def extract_data(self, page: Page) -> Dict[str, Any]:
        """
        Extract product data from Jumia product page
        """
        try:
            # Check if product is available
            is_available = True
            try:
                out_of_stock = await page.locator("text=Out of stock").count()
                is_available = out_of_stock == 0
            except:
                pass
            
            # Extract product name
            name = ""
            try:
                name_elem = await page.locator("h1.-fs20.-pts.-pbxs").first
                name = await name_elem.text_content()
                name = name.strip() if name else ""
            except:
                # Fallback selector
                try:
                    name_elem = await page.locator(".name").first
                    name = await name_elem.text_content()
                    name = name.strip() if name else ""
                except:
                    logger.warning("⚠️ Could not extract product name")
            
            # Extract price
            price = 0.0
            try:
                price_elem = await page.locator(".-b.-lh12.-fs24.-pts.-pbxs").first
                price_text = await price_elem.text_content()
                price = self.clean_price(price_text) if price_text else 0.0
            except:
                # Fallback selector
                try:
                    price_elem = await page.locator(".price").first
                    price_text = await price_elem.text_content()
                    price = self.clean_price(price_text) if price_text else 0.0
                except:
                    logger.warning("⚠️ Could not extract price")
            
            # Extract image URL
            image_url = ""
            try:
                img_elem = await page.locator("img.-fw.-mh").first
                image_url = await img_elem.get_attribute("src")
                if image_url and image_url.startswith("//"):
                    image_url = "https:" + image_url
            except:
                try:
                    img_elem = await page.locator(".image-wrapper img").first
                    image_url = await img_elem.get_attribute("src")
                except:
                    logger.warning("⚠️ Could not extract image")
            
            # Extract category
            category = ""
            try:
                breadcrumb = await page.locator(".-df.-i-ctr").first
                category_text = await breadcrumb.text_content()
                # Extract last category from breadcrumb
                categories = [c.strip() for c in category_text.split('>')]
                category = categories[-1] if categories else ""
            except:
                logger.warning("⚠️ Could not extract category")
            
            # Get current URL (may have redirected)
            current_url = page.url
            
            # Extract external ID from URL
            external_id = ""
            match = re.search(r'/([a-z0-9-]+)\.html', current_url)
            if match:
                external_id = match.group(1)
            
            data = {
                "name": name,
                "price": price,
                "currency": "XOF",
                "image_url": image_url,
                "category": category,
                "is_available": is_available,
                "url": current_url,
                "external_id": external_id,
                "marketplace": "jumia"
            }
            
            logger.info(f"✅ Scraped Jumia product: {name} - {price} XOF")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to extract Jumia data: {e}")
            raise
    
    async def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single Jumia product
        """
        logger.info(f"🔍 Scraping Jumia product: {url}")
        return await self.safe_scrape(url)
    
    async def scrape_category(self, category_url: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Scrape a category page on Jumia (for initial catalog population)
        """
        logger.info(f"🔍 Scraping Jumia category: {category_url} (limit: {limit})")
        products = []
        
        try:
            page = await self.create_page()
            await page.goto(category_url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for products to load
            await page.wait_for_selector("article.prd", timeout=10000)
            
            # Extract product links
            product_links = await page.locator("article.prd a.core").all()
            
            count = 0
            for link in product_links:
                if count >= limit:
                    break
                
                try:
                    href = await link.get_attribute("href")
                    if href:
                        full_url = self.BASE_URL + href if href.startswith('/') else href
                        
                        # Scrape individual product
                        product_data = await self.scrape_product(full_url)
                        if product_data:
                            products.append(product_data)
                            count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to scrape product link: {e}")
                    continue
            
            await page.close()
            logger.info(f"✅ Scraped {len(products)} products from category")
            
        except Exception as e:
            logger.error(f"❌ Failed to scrape Jumia category: {e}")
        
        return products
