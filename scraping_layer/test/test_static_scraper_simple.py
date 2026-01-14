"""
Simple test script for StaticScraper - Tests basic functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import scraping_layer
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scraping_layer import StaticScraper, ScrapingEngine, ScriptConfig, ScrapingStrategy


async def test_example_com():
    """Test scraping example.com"""
    print("=" * 60)
    print("Testing StaticScraper with example.com")
    print("=" * 60)
    
    # Create scraper and engine
    scraper = StaticScraper()
    engine = ScrapingEngine(static_scraper=scraper)
    
    # Configure scraping
    config = ScriptConfig(
        url="https://example.com",
        selectors={
            "title": "h1",
            "description": "p"
        },
        timeout=30,
        script_type=ScrapingStrategy.STATIC
    )
    
    # Execute scraping
    print(f"\n📡 Scraping: {config.url}")
    print(f"🔍 Selectors: {config.selectors}")
    
    result = await engine.scrape(config)
    
    # Display results
    print(f"\n{'='*60}")
    print(f"✅ Success: {result.success}")
    print(f"📊 Items extracted: {len(result.data)}")
    print(f"⏱️  Duration: {result.performance_metrics.total_duration:.2f}s")
    print(f"{'='*60}")
    
    if result.success and result.data:
        print("\n📋 Extracted Data:")
        for i, item in enumerate(result.data, 1):
            print(f"\nItem {i}:")
            for key, value in item.items():
                print(f"  {key}: {value}")
    else:
        print("\n❌ No data extracted")
        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error.error_type}: {error.message}")
    
    return result


async def test_formula1():
    """Test scraping Formula 1 2025 racing calendar"""
    print("\n" + "=" * 60)
    print("Testing StaticScraper with Formula 1 2025 Calendar")
    print("=" * 60)
    
    # Create scraper and engine
    scraper = StaticScraper()
    engine = ScrapingEngine(static_scraper=scraper)
    
    # Configure scraping - using selectors that exist in static HTML
    config = ScriptConfig(
        url="https://www.formula1.com/en/racing/2025",
        selectors={
            "page_title": "h1",
            "partners_heading": "h2",
            # These selectors are from the actual HTML structure
            "first_race_card": ".group\\/schedule-card",
            "race_location": ".typography-module_display-xl-bold__Gyl5W"
        },
        timeout=30,
        script_type=ScrapingStrategy.STATIC
    )
    
    # Execute scraping
    print(f"\n📡 Scraping: {config.url}")
    print(f"🔍 Selectors: {list(config.selectors.keys())}")
    print(f"\n⚠️  NOTE: Formula 1 uses Next.js/React (JavaScript-rendered)")
    print(f"    Static scraper can only get initial HTML, not dynamic content")
    
    result = await engine.scrape(config)
    
    # Display results
    print(f"\n{'='*60}")
    print(f"✅ Success: {result.success}")
    print(f"📊 Items extracted: {len(result.data)}")
    print(f"⏱️  Duration: {result.performance_metrics.total_duration:.2f}s")
    print(f"📄 Response Status: {result.metadata.response_status}")
    print(f"{'='*60}")
    
    if result.success and result.data:
        print("\n📋 FULL EXTRACTED DATA:")
        print("=" * 60)
        for i, item in enumerate(result.data, 1):
            print(f"\n🏎️  Item {i}:")
            print("-" * 60)
            for key, value in item.items():
                # Show FULL value without truncation
                if value:  # Only show non-empty values
                    print(f"  ✓ {key}:")
                    print(f"      {value}")
                else:
                    print(f"  ✗ {key}: (empty - likely JavaScript-rendered)")
        print("\n" + "=" * 60)
        
        # Additional analysis
        print("\n🔍 ANALYSIS:")
        print("-" * 60)
        print("  • Page Title: Successfully extracted from static HTML")
        print("  • Race Cards: Likely rendered by JavaScript (Next.js)")
        print("  • Recommendation: Use Phase 3 (Dynamic Scraper with Playwright)")
        print("=" * 60)
    else:
        print("\n❌ No data extracted")
        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error.error_type}: {error.message}")
    
    return result


async def main():
    """Run all tests"""
    print("\n🚀 Starting StaticScraper Tests\n")
    
    try:
        # Test 1: example.com
        result1 = await test_example_com()
        
        # Test 2: Formula 1 2025 Calendar
        result2 = await test_formula1()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        print(f"Test 1 (example.com): {'✅ PASSED' if result1.success else '❌ FAILED'}")
        print(f"Test 2 (Formula 1 2025): {'✅ PASSED' if result2.success else '❌ FAILED'}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
