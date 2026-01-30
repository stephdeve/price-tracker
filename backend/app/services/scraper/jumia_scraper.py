"""
Jumia scraper for Benin market
"""
from typing import Optional, Dict, Any, List
from playwright.async_api import Page
import logging
import re
import asyncio
import json

from app.services.scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class JumiaScraper(BaseScraper):
    """
    Scraper for Jumia (supports all Jumia domains: jumia.ci, jumia.ma, jumia.com.bj, etc.)
    """
    
    # Support multiple Jumia regional domains
    SUPPORTED_DOMAINS = ['jumia.', 'www.jumia.']
    
    @staticmethod
    def is_jumia_url(url: str) -> bool:
        """Check if URL is a valid Jumia URL"""
        return any(domain in url.lower() for domain in JumiaScraper.SUPPORTED_DOMAINS)
    
    async def extract_data(self, page: Page) -> Dict[str, Any]:
        """
        Extract product data from Jumia product page
        Supports multiple Jumia regional sites (jumia.ci, jumia.ma, jumia.com.bj, etc.)
        """
        try:
            # Try to wait for core elements (name/price) to be present
            try:
                await page.wait_for_selector(
                    "h1, .name, [data-testid='product-name'], .product-title",
                    timeout=8000
                )
            except:
                pass
            try:
                await page.wait_for_selector(
                    ".prc, .-b.-lh12.-fs24.-pts.-pbxs, [class*='price'], [data-testid*='price'], h2.-b.-fs24",
                    timeout=8000
                )
            except:
                pass
            # Check if product is available
            is_available = True
            try:
                out_of_stock = await page.locator("text=Out of stock").count()
                is_available = out_of_stock == 0
            except:
                pass
            
            # Extract product name - try multiple selectors
            name = ""
            name_selectors = [
                "h1.-fs20.-pts.-pbxs",
                "h1[class*='heading']",
                "h1",
                ".name",
                "[data-testid='product-name']",
                ".product-title"
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
            
            if not name:
                logger.warning(" Could not extract product name")
            
            # Extract price - try multiple selectors
            price = 0.0
            price_selectors = [
                ".-b.-lh12.-fs24.-pts.-pbxs",
                "[class*='price']",
                ".prc",
                "[data-testid*='price']",
                ".product-price",
                "h2.-b.-fs24"
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
            
            if price <= 0:
                logger.warning(" Could not extract price")
            
            # Extract image URL - try multiple selectors
            image_url = ""
            image_selectors = [
                "img.-fw.-mh",
                ".image-wrapper img",
                "[class*='product-image'] img",
                ".gallery img",
                "img[alt*='product']",
                "img[class*='img']"
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
            
            if not image_url:
                logger.warning(" Could not extract image")
            
            # Extract category
            category = ""
            try:
                breadcrumb = page.locator(".-df.-i-ctr").first
                category_text = await breadcrumb.text_content()
                # Extract last category from breadcrumb
                categories = [c.strip() for c in category_text.split('>')]
                category = categories[-1] if categories else ""
            except:
                try:
                    breadcrumb = page.locator("[class*='breadcrumb']").first
                    category_text = await breadcrumb.text_content()
                    categories = [c.strip() for c in category_text.split('>')]
                    category = categories[-1] if categories else ""
                except:
                    logger.warning(" Could not extract category")
            
            # Get current URL (may have redirected)
            current_url = page.url
            
            # Extract external ID from URL
            external_id = ""
            match = re.search(r'/([a-z0-9-]+)\.html', current_url)
            if match:
                external_id = match.group(1)
            
            # Currency by domain (minimal mapping)
            currency = "XOF"
            url_l = current_url.lower()
            if "jumia.ma" in url_l:
                currency = "MAD"
            
            data = {
                "name": name or "Product",
                "price": price or 0.0,
                "currency": currency,
                "image_url": image_url,
                "category": category,
                "is_available": is_available,
                "url": current_url,
                "external_id": external_id,
                "marketplace": "jumia"
            }
            
            logger.info(f" Scraped Jumia product: {name} - {price} XOF from {current_url}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to extract Jumia data: {e}")
            raise
    
    async def scrape_product(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single Jumia product
        """
        logger.info(f" Scraping Jumia product: {url}")
        return await self.safe_scrape(url)
    
    async def scrape_category(self, category_url: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Scrape a category page on Jumia (for initial catalog population)
        """
        logger.info(f" Scraping Jumia category: {category_url} (limit: {limit})")
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
                    logger.error(f" Failed to scrape product link: {e}")
                    continue
            
            await page.close()
            logger.info(f" Scraped {len(products)} products from category")
            
        except Exception as e:
            logger.error(f" Failed to scrape Jumia category: {e}")
        
        return products


# -----------------------------
# Lightweight HTTP fallback (no Playwright)
# -----------------------------
async def _fetch_html(url: str, headers: Dict[str, str]) -> Optional[str]:
    try:
        import httpx  # type: ignore
        async with httpx.AsyncClient(follow_redirects=True, timeout=20.0, headers=headers) as client:
            r = await client.get(url)
            if r.status_code == 200:
                return r.text
            return None
    except Exception:
        try:
            import requests  # type: ignore
            def _get():
                resp = requests.get(url, headers=headers, timeout=20)
                return resp.text if resp.status_code == 200 else None
            return await asyncio.to_thread(_get)
        except Exception:
            try:
                from urllib.request import Request, urlopen
                def _uget():
                    req = Request(url, headers=headers)
                    with urlopen(req, timeout=20) as resp:  # nosec - controlled URL from user input validated elsewhere
                        return resp.read().decode('utf-8', errors='ignore')
                return await asyncio.to_thread(_uget)
            except Exception:
                return None


def _extract_meta(content: str, name: str) -> Optional[str]:
    # property or name attribute
    m = re.search(rf'<meta[^>]+(?:property|name)=["\\\\']{name}["\"][^>]+content=["\\\\']([^"\"]+)["\"][^>]*>', content, re.IGNORECASE)
    return m.group(1).strip() if m else None


def _extract_price_from_jsonld(content: str) -> tuple[Optional[str], Optional[str]]:
    # Find JSON-LD blocks
    for script in re.findall(r'<script[^>]+type=["\\\\']application/ld\+json["\"][^>]*>(.*?)</script>', content, re.IGNORECASE | re.DOTALL):
        try:
            data = json.loads(script)
            # data may be list or dict
            candidates = data if isinstance(data, list) else [data]
            for d in candidates:
                offers = d.get('offers') if isinstance(d, dict) else None
                if isinstance(offers, list):
                    for o in offers:
                        price = o.get('price')
                        curr = o.get('priceCurrency')
                        if price:
                            return str(price), str(curr) if curr else None
                elif isinstance(offers, dict):
                    price = offers.get('price')
                    curr = offers.get('priceCurrency')
                    if price:
                        return str(price), str(curr) if curr else None
        except Exception:
            continue
    return None, None


async def simple_scrape_jumia(url: str) -> Optional[Dict[str, Any]]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    html = await _fetch_html(url, headers)
    if not html:
        return None

    # Name via og:title or h1
    name = _extract_meta(html, 'og:title') or _extract_meta(html, 'twitter:title')
    if not name:
        m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
        if m:
            name = re.sub('<[^<]+?>', '', m.group(1)).strip()

    # Image via og:image
    image_url = _extract_meta(html, 'og:image')

    # Price and currency via JSON-LD
    price_str, curr = _extract_price_from_jsonld(html)
    # Fallback: look for class="prc">...<
    if not price_str:
        m = re.search(r'class=["\\\\']prc[^"\"]*["\"][^>]*>([^<]+)<', html, re.IGNORECASE)
        if m:
            price_str = m.group(1)

    # Domain-based currency fallback
    url_l = url.lower()
    currency = curr or ("MAD" if "jumia.ma" in url_l else "XOF")

    # Clean price
    from app.services.scraper.base_scraper import BaseScraper
    # create a tiny helper subclass to access method
    class _Tmp(BaseScraper):
        async def extract_data(self, page): ...
        async def scrape_product(self, url): ...
        async def scrape_category(self, category_url: str, limit: int = 50): ...
    parser = _Tmp()
    price = parser.clean_price(price_str) if price_str else None

    # External ID
    external_id = ""
    mm = re.search(r'/([a-z0-9-]+)\.html', url_l)
    if mm:
        external_id = mm.group(1)

    if not price:
        return None

    return {
        "name": name or "Product",
        "price": float(price),
        "currency": currency,
        "image_url": image_url,
        "category": None,
        "is_available": True,
        "url": url,
        "external_id": external_id,
        "marketplace": "jumia",
    }
