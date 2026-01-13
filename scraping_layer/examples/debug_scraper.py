#!/usr/bin/env python3
"""
Debug version of the scraper to test individual components.
"""

import asyncio
import os
import sys
import requests
from bs4 import BeautifulSoup

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from scraping_layer.models import StaticScrapingConfig


async def test_direct_scraping():
    """Test scraping directly without the engine."""
    
    url = "https://httpbin.org/html"
    print(f"🔍 Testing direct scraping of: {url}")
    
    try:
        # Make request
        print("📡 Making HTTP request...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        print(f"✅ Response: {response.status_code}")
        print(f"📄 Content length: {len(response.content)} bytes")
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic info
        title = soup.find('title')
        h1 = soup.find('h1')
        paragraphs = soup.find_all('p')[:3]
        
        print(f"\n📋 EXTRACTED DATA:")
        print(f"Title: {title.get_text(strip=True) if title else 'No title found'}")
        print(f"H1: {h1.get_text(strip=True) if h1 else 'No H1 found'}")
        print(f"Paragraphs found: {len(paragraphs)}")
        
        for i, p in enumerate(paragraphs, 1):
            text = p.get_text(strip=True)
            if text:
                print(f"  P{i}: {text[:100]}{'...' if len(text) > 100 else ''}")
        
        # Test with selectors
        print(f"\n🎯 Testing with selectors:")
        selectors = {'title': 'h1', 'content': 'p'}
        
        for field, selector in selectors.items():
            elements = soup.select(selector)
            print(f"  {field} ('{selector}'): {len(elements)} elements found")
            if elements:
                text = elements[0].get_text(strip=True)
                print(f"    First: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_static_scraper_class():
    """Test our StaticScraper class directly."""
    
    print(f"\n🔧 Testing StaticScraper class...")
    
    # Import our scraper
    from test_scraper import SimpleStaticScraper
    
    scraper = SimpleStaticScraper()
    
    config = StaticScrapingConfig(
        url="https://httpbin.org/html",
        selectors={'title': 'h1', 'content': 'p'},
        timeout=30
    )
    
    try:
        results = await scraper.scrape_static(config)
        print(f"✅ Scraper returned {len(results)} items")
        
        for i, item in enumerate(results, 1):
            print(f"\nItem {i}:")
            for key, value in item.items():
                if isinstance(value, list):
                    print(f"  {key}: {len(value)} items - {value}")
                else:
                    display_value = str(value)[:100]
                    print(f"  {key}: {display_value}")
        
        return results
        
    except Exception as e:
        print(f"❌ Scraper error: {e}")
        import traceback
        traceback.print_exc()
        return []


async def test_engine_integration():
    """Test the full engine integration."""
    
    print(f"\n🚀 Testing full engine integration...")
    
    from test_scraper import test_scraper
    
    # Test with a simple URL and selectors
    url = "https://httpbin.org/html"
    selectors = {'title': 'h1', 'content': 'p'}
    
    result = await test_scraper(url, selectors)
    
    if result:
        print(f"✅ Engine test completed")
        return result
    else:
        print(f"❌ Engine test failed")
        return None


async def main():
    """Run all tests."""
    
    print("🧪 SCRAPER DEBUG TESTS")
    print("=" * 50)
    
    # Test 1: Direct scraping
    print("\n1️⃣ DIRECT SCRAPING TEST")
    success1 = await test_direct_scraping()
    
    # Test 2: StaticScraper class
    print("\n2️⃣ STATIC SCRAPER CLASS TEST")
    results2 = await test_static_scraper_class()
    
    # Test 3: Full engine
    print("\n3️⃣ FULL ENGINE TEST")
    result3 = await test_engine_integration()
    
    print(f"\n📊 SUMMARY")
    print(f"Direct scraping: {'✅' if success1 else '❌'}")
    print(f"Scraper class: {'✅' if results2 else '❌'}")
    print(f"Full engine: {'✅' if result3 else '❌'}")


if __name__ == "__main__":
    asyncio.run(main())