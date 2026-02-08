"""
Test script for AliExpress scraper
"""
import asyncio
import sys
sys.path.insert(0, '/home/steven/dev/price-tracker/backend')

from app.services.scraper.aliexpress_scraper import AliExpressScraper


async def test_aliexpress_product():
    """Test scraping a single AliExpress product"""
    print("🧪 Testing AliExpress Product Scraper...")
    print("=" * 60)
    
    # Example AliExpress product URL
    test_url = "https://www.aliexpress.com/item/1005004788603863.html"
    
    async with AliExpressScraper() as scraper:
        product_data = await scraper.scrape_product(test_url)
        
        if product_data:
            print("\n✅ Successfully scraped product:")
            print(f"   Name: {product_data['name']}")
            print(f"   Price: {product_data['price']} {product_data['currency']}")
            print(f"   Category: {product_data['category']}")
            print(f"   Available: {product_data['is_available']}")
            print(f"   Image: {product_data['image_url'][:80]}...")
            print(f"   External ID: {product_data['external_id']}")
        else:
            print("\n❌ Failed to scrape product")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(test_aliexpress_product())
