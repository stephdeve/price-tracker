"""
Simple test script to verify scraping functionality
Run: python test_scraper.py
"""
import asyncio
import sys
from app.services.scraper.jumia_scraper import JumiaScraper

# Test URLs (replace with actual Jumia Benin products)
TEST_URLS = [
    # Add real Jumia Benin product URLs here
    # Example: "https://www.jumia.com.bj/samsung-galaxy-a54-..."
]


async def test_single_product(url: str):
    """Test scraping a single product"""
    print(f"\n{'='*70}")
    print(f"🔍 Testing URL: {url}")
    print('='*70)
    
    async with JumiaScraper() as scraper:
        data = await scraper.scrape_product(url)
        
        if data:
            print(f"✅ SUCCESS!")
            print(f"  📦 Name: {data.get('name', 'N/A')}")
            print(f"  💰 Price: {data.get('price', 0)} {data.get('currency', 'XOF')}")
            print(f"  📁 Category: {data.get('category', 'N/A')}")
            print(f"  🏪 Marketplace: {data.get('marketplace', 'N/A')}")
            print(f"  ✔️  Available: {data.get('is_available', False)}")
            print(f"  🔗 URL: {data.get('url', 'N/A')[:60]}...")
            if data.get('image_url'):
                print(f"  📸 Image: {data.get('image_url', '')[:60]}...")
            return True
        else:
            print(f"❌ FAILED - No data returned")
            return False


async def main():
    """Main test function"""
    if len(sys.argv) > 1:
        # URL provided as command line argument
        url = sys.argv[1]
        await test_single_product(url)
    elif TEST_URLS:
        # Test all URLs in the list
        print(f"🚀 Testing {len(TEST_URLS)} product(s)...")
        
        results = []
        for url in TEST_URLS:
            success = await test_single_product(url)
            results.append(success)
        
        # Summary
        print(f"\n{'='*70}")
        print(f"📊 SUMMARY")
        print(f"{'='*70}")
        print(f"  Total: {len(results)}")
        print(f"  ✅ Success: {sum(results)}")
        print(f"  ❌ Failed: {len(results) - sum(results)}")
    else:
        print("⚠️  No test URLs configured!")
        print("\nUsage:")
        print("  1. Add URLs to TEST_URLS in this file")
        print("  2. Or run: python test_scraper.py <URL>")
        print("\nExample:")
        print('  python test_scraper.py "https://www.jumia.com.bj/..."')


if __name__ == "__main__":
    asyncio.run(main())
