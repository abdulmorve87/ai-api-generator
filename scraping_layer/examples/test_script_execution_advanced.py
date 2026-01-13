#!/usr/bin/env python3
"""
Advanced test cases for script execution layer.

This script demonstrates various scraping scenarios:
1. Basic static scraping
2. Complex selector patterns
3. Multiple field extraction
4. Error handling
"""

import asyncio
import sys
import os
from typing import Dict, Any, List
from unittest.mock import AsyncMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import scraping layer components
from scraping_layer.script_execution import ScrapingScript, ScriptExecutor
from scraping_layer.models import ScrapingStrategy, InteractionStep
from scraping_layer.engine import ScrapingEngine

# Import test implementations
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from scraping_layer.examples.test_scraper import (
    SimpleContentDetector, SimpleStaticScraper, SimpleDataExtractor, MockCacheManager
)


def create_test_scripts() -> List[ScrapingScript]:
    """Create various test scripts for different scenarios."""
    
    scripts = []
    
    # Script 1: Basic example.com scraping
    scripts.append(ScrapingScript(
        script_id="basic_example",
        name="Basic Example.com Scraper",
        description="Simple scraper for example.com to extract title and content",
        url="https://example.com",
        strategy=ScrapingStrategy.STATIC,
        selectors={
            'title': 'h1',
            'content': 'p',
            'domain': 'a'
        },
        expected_fields=['title', 'content'],
        tags=['basic', 'example']
    ))
    
    # Script 2: HTTPBin HTML test
    scripts.append(ScrapingScript(
        script_id="httpbin_test",
        name="HTTPBin HTML Test",
        description="Test scraper for HTTPBin HTML endpoint",
        url="https://httpbin.org/html",
        strategy=ScrapingStrategy.STATIC,
        selectors={
            'main_title': 'h1',
            'text_content': 'p',
            'all_headings': 'h1, h2, h3'
        },
        expected_fields=['main_title', 'text_content'],
        tags=['test', 'httpbin']
    ))
    
    # Script 3: Wikipedia test (more complex)
    scripts.append(ScrapingScript(
        script_id="wikipedia_test",
        name="Wikipedia Web Scraping Article",
        description="Extract information from Wikipedia article about web scraping",
        url="https://en.wikipedia.org/wiki/Web_scraping",
        strategy=ScrapingStrategy.STATIC,
        selectors={
            'article_title': 'h1.firstHeading',
            'summary': 'p',
            'section_headings': 'h2 .mw-headline',
            'infobox': '.infobox',
            'categories': '#mw-normal-catlinks a'
        },
        expected_fields=['article_title', 'summary', 'section_headings'],
        timeout=45,
        tags=['wikipedia', 'complex']
    ))
    
    # Script 4: Error test (invalid URL)
    scripts.append(ScrapingScript(
        script_id="error_test",
        name="Error Test Script",
        description="Test script with invalid URL to test error handling",
        url="https://this-domain-does-not-exist-12345.com",
        strategy=ScrapingStrategy.STATIC,
        selectors={
            'title': 'h1',
            'content': 'p'
        },
        expected_fields=['title', 'content'],
        timeout=10,
        tags=['error', 'test']
    ))
    
    return scripts


async def run_script_tests():
    """Run all test scripts and display results."""
    
    print("🧪 Advanced Script Execution Tests")
    print("=" * 60)
    
    # Set up scraping engine
    print("⚙️  Setting up scraping engine...")
    
    content_detector = SimpleContentDetector()
    static_scraper = SimpleStaticScraper()
    data_extractor = SimpleDataExtractor()
    cache_manager = MockCacheManager()
    
    # Mock unused components
    script_executor_mock = AsyncMock()
    dynamic_scraper = AsyncMock()
    browser_manager = AsyncMock()
    error_handler = AsyncMock()
    
    engine = ScrapingEngine(
        content_detector=content_detector,
        script_executor=script_executor_mock,
        static_scraper=static_scraper,
        dynamic_scraper=dynamic_scraper,
        browser_manager=browser_manager,
        data_extractor=data_extractor,
        cache_manager=cache_manager,
        error_handler=error_handler
    )
    
    executor = ScriptExecutor(engine)
    
    # Get test scripts
    scripts = create_test_scripts()
    
    print(f"📋 Running {len(scripts)} test scripts...\n")
    
    results = []
    
    for i, script in enumerate(scripts, 1):
        print(f"🎯 Test {i}/{len(scripts)}: {script.name}")
        print(f"   URL: {script.url}")
        print(f"   Strategy: {script.strategy.value}")
        print(f"   Expected Fields: {script.expected_fields}")
        print()
        
        try:
            result = await executor.execute_script(script)
            results.append(result)
            
            # Display result summary
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            print(f"   Result: {status}")
            print(f"   Items: {result.total_items}")
            print(f"   Time: {result.execution_time:.2f}s")
            
            if result.errors:
                print(f"   Errors: {len(result.errors)}")
                for error in result.errors[:2]:  # Show first 2 errors
                    print(f"     - {error[:80]}...")
            
            if result.warnings:
                print(f"   Warnings: {len(result.warnings)}")
            
            # Show sample data
            if result.data and result.success:
                print("   Sample Data:")
                sample_item = result.data[0]
                for key, value in list(sample_item.items())[:3]:  # Show first 3 fields
                    display_value = str(value)
                    if len(display_value) > 50:
                        display_value = display_value[:47] + "..."
                    print(f"     {key}: {display_value}")
            
        except Exception as e:
            print(f"   Result: ❌ EXCEPTION - {str(e)}")
            results.append(None)
        
        print("-" * 60)
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r and r.success)
    failed = sum(1 for r in results if r and not r.success)
    exceptions = sum(1 for r in results if r is None)
    
    print(f"Total Tests: {len(scripts)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Exceptions: {exceptions}")
    
    total_items = sum(r.total_items for r in results if r)
    total_time = sum(r.execution_time for r in results if r)
    
    print(f"Total Items Extracted: {total_items}")
    print(f"Total Execution Time: {total_time:.2f} seconds")
    
    # Execution history
    print(f"\n📚 EXECUTION HISTORY:")
    print("-" * 30)
    history = executor.get_execution_history()
    
    for result in history:
        status = "✅" if result.success else "❌"
        print(f"{status} {result.script_id}: {result.total_items} items "
              f"({result.execution_time:.1f}s)")
    
    return results


def main():
    """Main function."""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--single':
            # Run single test
            print("Running single test with example.com...")
            
            async def single_test():
                # Set up engine (simplified)
                content_detector = SimpleContentDetector()
                static_scraper = SimpleStaticScraper()
                data_extractor = SimpleDataExtractor()
                cache_manager = MockCacheManager()
                
                engine = ScrapingEngine(
                    content_detector=content_detector,
                    script_executor=AsyncMock(),
                    static_scraper=static_scraper,
                    dynamic_scraper=AsyncMock(),
                    browser_manager=AsyncMock(),
                    data_extractor=data_extractor,
                    cache_manager=cache_manager,
                    error_handler=AsyncMock()
                )
                
                executor = ScriptExecutor(engine)
                
                script = ScrapingScript(
                    script_id="single_test",
                    name="Single Test",
                    description="Quick single test",
                    url="https://example.com",
                    strategy=ScrapingStrategy.STATIC,
                    selectors={'title': 'h1', 'content': 'p'},
                    expected_fields=['title', 'content']
                )
                
                result = await executor.execute_script(script)
                
                print(f"Result: {'SUCCESS' if result.success else 'FAILED'}")
                print(f"Items: {result.total_items}")
                print(f"Data: {result.data}")
                
                return result.success
            
            success = asyncio.run(single_test())
            return 0 if success else 1
        
        elif sys.argv[1] == '--help':
            print("Usage:")
            print("  python test_script_execution_advanced.py          # Run all tests")
            print("  python test_script_execution_advanced.py --single # Run single test")
            print("  python test_script_execution_advanced.py --help   # Show this help")
            return 0
    
    # Run all tests
    results = asyncio.run(run_script_tests())
    
    # Return appropriate exit code
    successful = sum(1 for r in results if r and r.success)
    return 0 if successful > 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)