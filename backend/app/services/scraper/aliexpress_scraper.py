"""
AliExpress scraper for international products
"""
from typing import Optional, Dict, Any, List
from playwright.async_api import Page
import logging
import re
import json
import asyncio

from app.services.scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class AliExpressScraper(BaseScraper):
    """
    Scraper for AliExpress (www.aliexpress.com)
    Supports both JSON data extraction and HTML fallback
    """
    
    BASE_URL = "https://www.aliexpress.com"
    
    @staticmethod
    def is_aliexpress_url(url: str) -> bool:
        """Check if URL is a valid AliExpress URL"""
        return 'aliexpress.com' in url.lower()
    
    async def extract_data(self, page: Page) -> Dict[str, Any]:
        """
        Extract product data from AliExpress product page
        Tries JSON extraction first, falls back to HTML parsing
        """
        try:
            # Wait for page to load
            try:
                await page.wait_for_selector(
                    "h1, .product-title, [class*='title']",
                    timeout=10000
                )
            except:
                pass
            
            # Try to extract data from window.runParams JSON
            json_data = await self._extract_json_data(page)
            if json_data:
                return json_data
            
            # Fallback to HTML parsing
            return await self._extract_html_data(page)
            
        except Exception as e:
            logger.error(f"❌ Failed to extract AliExpress data: {e}")
            raise
    
    async def _extract_json_data(self, page: Page) -> Optional[Dict[str, Any]]:
        """
        Extract data from embedded JSON (window.runParams)
        """
        try:
            # Get page content
            content = await page.content()
            
            # Look for window.runParams
            match = re.search(r'window\.runParams\s*=\s*({.+?});', content, re.DOTALL)
            if not match:
                return None
            
            data = json.loads(match.group(1))
            
            # Extract product info from JSON structure
            product_data = data.get('data', {})
            
            # Product name
            name = product_data.get('titleModule', {}).get('subject', '')
            
            # Price - AliExpress has complex pricing
            price_module = product_data.get('priceModule', {})
            price = 0.0
            
            # Try different price fields
            if 'minActivityAmount' in price_module:
                price_str = price_module['minActivityAmount'].get('value', '0')
            elif 'minAmount' in price_module:
                price_str = price_module['minAmount'].get('value', '0')
            else:
                price_str = '0'
            
            price = self.clean_price(str(price_str))
            
            # Currency
            currency = price_module.get('minActivityAmount', {}).get('currency', 'USD')
            if not currency:
                currency = price_module.get('minAmount', {}).get('currency', 'USD')
            
            # Image
            image_module = product_data.get('imageModule', {})
            image_url = ''
            if 'imagePathList' in image_module and image_module['imagePathList']:
                image_url = image_module['imagePathList'][0]
                if image_url.startswith('//'):
                    image_url = 'https:' + image_url
            
            # Category
            category = ''
            page_module = product_data.get('pageModule', {})
            if 'categoryPath' in page_module and page_module['categoryPath']:
                category = page_module['categoryPath'][-1].get('name', '')
            
            # External ID from URL
            current_url = page.url
            external_id = ''
            match = re.search(r'/(\d+)\.html', current_url)
            if match:
                external_id = match.group(1)
            
            # Availability
            is_available = True
            action_module = product_data.get('actionModule', {})
            if action_module.get('itemStatus') == 'soldOut':
                is_available = False
            
            if not name or not price:
                return None
            
            data = {
                "name": name,
                "price": price or 0.0,
                "currency": currency,
                "image_url": image_url,
                "category": category,
                "is_available": is_available,
                "url": current_url,
                "external_id": external_id,
                "marketplace": "aliexpress"
            }
            
            logger.info(f"✅ Scraped AliExpress product (JSON): {name} - {price} {currency}")
            return data
            
        except Exception as e:
            logger.warning(f"⚠️ JSON extraction failed: {e}")
            return None
    
    async def _extract_html_data(self, page: Page) -> Dict[str, Any]:
        """
        Fallback HTML parsing when JSON extraction fails
        """
        # Product name
        name = ""
        name_selectors = [
            "h1",
            ".product-title",
            "[class*='title']",
            "[data-pl='product-title']"
        ]
        for selector in name_selectors:
            try:
                name_elem = page.locator(selector).first
                name = await name_elem.text_content()
                if name and name.strip():
                    name = name.strip()
                    break
            except:
                continue
        
        # Price
        price = 0.0
        price_selectors = [
            ".product-price-value",
            "[class*='price']",
            "[itemprop='price']",
            ".uniform-banner-box-price"
        ]
        for selector in price_selectors:
            try:
                price_elem = page.locator(selector).first
                price_text = await price_elem.text_content()
                if price_text:
                    price = self.clean_price(price_text)
                    if price and price > 0:
                        break
            except:
                continue
        
        # Image
        image_url = ""
        image_selectors = [
            ".magnifier-image",
            "[class*='image'] img",
            "img[alt*='product']"
        ]
        for selector in image_selectors:
            try:
                img_elem = page.locator(selector).first
                image_url = await img_elem.get_attribute("src")
                if image_url:
                    if image_url.startswith("//"):
                        image_url = "https:" + image_url
                    if image_url.startswith("http"):
                        break
            except:
                continue
        
        # Category from breadcrumb
        category = ""
        try:
            breadcrumb = page.locator("[class*='breadcrumb']").first
            category_text = await breadcrumb.text_content()
            categories = [c.strip() for c in category_text.split('>')]
            category = categories[-1] if categories else ""
        except:
            pass
        
        # External ID from URL
        current_url = page.url
        external_id = ""
        match = re.search(r'/(\d+)\.html', current_url)
        if match:
            external_id = match.group(1)
        
        # Check availability
        is_available = True
        try:
            sold_out = await page.locator("text=/sold out/i").count()
            is_available = sold_out == 0
        except:
            pass
        
        data = {
            "name": name or "Product",
            "price": price or 0.0,
            "currency": "USD",  # Default for AliExpress
            "image_url": image_url,
            "category": category,
            "is_available": is_available,
            "url": current_url,
            "external_id": external_id,
            "marketplace": "aliexpress"
        }
        
        logger.info(f"✅ Scraped AliExpress product (HTML): {name} - {price} USD")
        return data
    
    async def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single AliExpress product
        """
        logger.info(f"🔍 Scraping AliExpress product: {url}")
        return await self.safe_scrape(url)
    
    async def scrape_category(self, category_url: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Scrape a category page on AliExpress
        """
        logger.info(f"🔍 Scraping AliExpress category: {category_url} (limit: {limit})")
        products = []
        
        try:
            page = await self.create_page()
            await page.goto(category_url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for products to load
            await asyncio.sleep(3)
            
            # Extract product links
            product_links = await page.locator("a[href*='/item/']").all()
            
            count = 0
            seen_urls = set()
            
            for link in product_links:
                if count >= limit:
                    break
                
                try:
                    href = await link.get_attribute("href")
                    if href and '/item/' in href:
                        # Build full URL
                        if href.startswith('//'):
                            full_url = 'https:' + href
                        elif href.startswith('/'):
                            full_url = self.BASE_URL + href
                        else:
                            full_url = href
                        
                        # Avoid duplicates
                        if full_url in seen_urls:
                            continue
                        seen_urls.add(full_url)
                        
                        # Scrape individual product
                        product_data = await self.scrape_product(full_url)
                        if product_data:
                            products.append(product_data)
                            count += 1
                            
                except Exception as e:
                    logger.error(f"❌ Failed to scrape product link: {e}")
                    continue
            
            await page.close()
            logger.info(f"✅ Scraped {len(products)} products from AliExpress category")
            
        except Exception as e:
            logger.error(f"❌ Failed to scrape AliExpress category: {e}")
        
        return products
