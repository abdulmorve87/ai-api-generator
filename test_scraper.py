#!/usr/bin/env python3
"""
Test script for the Universal Scraping Layer.

This script allows you to test the scraping layer with real URLs
and see the output on the console.
"""

import asyncio
import sys
from typing import Dict, Any, List
from unittest.mock import AsyncMock, Mock

# Import our scraping layer components
from scraping_layer.models import (
    ScriptConfig, ScrapingStrategy, WebsiteAnalysis, 
    FrameworkType, FrameworkInfo, StaticScrapingConfig
)
from scraping_layer.engine import ScrapingEngine
from scraping_layer.interfaces import (
    IContentDetector, IStaticScraper, IScriptExecutor, IDynamicScraper,
    IBrowserManager, IDataExtractor, ICacheManager, IErrorHandler
)

# Simple implementations for testing
class SimpleContentDetector(IContentDetector):
    """Simple content detector for testing."""
    
    async def analyze_website(self, url: str) -> WebsiteAnalysis:
        """Analyze website - defaults to static for most sites."""
        print(f"🔍 Analyzing website: {url}")
        
        # For testing, let's prefer static scraping for most sites
        # Only use dynamic for obvious SPA indicators
        dynamic_indicators = ['app.', 'spa.', 'react.', 'angular.', 'vue.']
        is_dynamic = any(indicator in url.lower() for indicator in dynamic_indicators)
        
        # Default to static unless clearly dynamic
        is_static = not is_dynamic
        
        return WebsiteAnalysis(
            is_static=is_static,
            framework=None,
            requires_javascript=is_dynamic,
            recommended_strategy=ScrapingStrategy.STATIC if is_static else ScrapingStrategy.DYNAMIC,
            confidence_score=0.8
        )
    
    def detect_framework(self, html: str) -> FrameworkInfo:
        """Detect framework from HTML."""
        if 'react' in html.lower():
            return FrameworkInfo(framework=FrameworkType.REACT, confidence=0.7)
        elif 'angular' in html.lower():
            return FrameworkInfo(framework=FrameworkType.ANGULAR, confidence=0.7)
        elif 'vue' in html.lower():
            return FrameworkInfo(framework=FrameworkType.VUE, confidence=0.7)
        else:
            return FrameworkInfo(framework=FrameworkType.UNKNOWN, confidence=0.5)
    
    async def requires_javascript(self, url: str) -> bool:
        """Check if JavaScript is required."""
        return 'spa' in url.lower() or 'app' in url.lower()
    
    async def detect_anti_bot_measures(self, url: str) -> List[str]:
        """Detect anti-bot measures."""
        return []


class SimpleStaticScraper(IStaticScraper):
    """Simple static scraper using requests and BeautifulSoup."""
    
    async def scrape_static(self, config: StaticScrapingConfig) -> List[Dict[str, Any]]:
        """Scrape static content."""
        print(f"📄 Scraping static content from: {config.url}")
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Make HTTP request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            print("🌐 Making HTTP request...")
            response = requests.get(config.url, headers=headers, timeout=config.timeout)
            response.raise_for_status()
            
            print(f"✅ Response received: {response.status_code}")
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data based on selectors
            results = []
            
            if config.selectors:
                print(f"🎯 Extracting data with selectors: {config.selectors}")
                
                # If we have multiple selectors, try to extract structured data
                if len(config.selectors) > 1:
                    # Try to find common container elements
                    containers = soup.find_all(['article', 'div', 'section'])[:10]  # Limit to first 10
                    
                    for i, container in enumerate(containers):
                        item = {}
                        for field, selector in config.selectors.items():
                            element = container.select_one(selector)
                            if element:
                                item[field] = element.get_text(strip=True)
                        
                        if item:  # Only add if we found some data
                            results.append(item)
                
                # If no structured data found, extract individual elements
                if not results:
                    item = {}
                    for field, selector in config.selectors.items():
                        elements = soup.select(selector)
                        if elements:
                            if len(elements) == 1:
                                item[field] = elements[0].get_text(strip=True)
                            else:
                                item[field] = [el.get_text(strip=True) for el in elements[:5]]  # Limit to 5
                    
                    if item:
                        results.append(item)
            
            # If no selectors provided, extract basic page info
            if not config.selectors or not results:
                print("📋 No selectors provided or no data found, extracting basic page info...")
                
                title = soup.find('title')
                headings = soup.find_all(['h1', 'h2', 'h3'])[:5]
                paragraphs = soup.find_all('p')[:3]
                
                basic_info = {
                    'title': title.get_text(strip=True) if title else 'No title',
                    'headings': [h.get_text(strip=True) for h in headings],
                    'paragraphs': [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
                }
                results.append(basic_info)
            
            print(f"✨ Extracted {len(results)} items")
            return results
            
        except Exception as e:
            print(f"❌ Error scraping: {e}")
            return [{'error': str(e), 'url': config.url}]
    
    def extract_with_selectors(self, html: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract data using selectors."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        result = {}
        for field, selector in selectors.items():
            element = soup.select_one(selector)
            if element:
                result[field] = element.get_text(strip=True)
        
        return result
    
    async def handle_pagination(self, base_url: str, pagination_config: Dict[str, Any]) -> List[str]:
        """Handle pagination."""
        return [base_url]  # Simple implementation
    
    async def submit_form(self, url: str, form_data: Dict[str, Any]) -> str:
        """Submit form."""
        return ""  # Placeholder


class SimpleDataExtractor(IDataExtractor):
    """Simple data extractor."""
    
    def validate_data(self, data: List[Dict[str, Any]], schema: Dict[str, Any]):
        """Validate data."""
        from scraping_layer.models import ValidationResult
        return ValidationResult(is_valid=True)
    
    def clean_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and normalize data."""
        print("🧹 Cleaning extracted data...")
        
        cleaned = []
        for item in data:
            cleaned_item = {}
            for key, value in item.items():
                if isinstance(value, str):
                    # Clean whitespace and decode HTML entities
                    import html
                    cleaned_value = html.unescape(value.strip())
                    cleaned_item[key] = cleaned_value
                elif isinstance(value, list):
                    # Clean list items
                    cleaned_item[key] = [str(v).strip() for v in value if str(v).strip()]
                else:
                    cleaned_item[key] = value
            
            if cleaned_item:
                cleaned.append(cleaned_item)
        
        return cleaned
    
    def decode_html_entities(self, text: str) -> str:
        """Decode HTML entities."""
        import html
        return html.unescape(text)
    
    def handle_missing_fields(self, data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """Handle missing fields."""
        for field in required_fields:
            if field not in data:
                data[field] = None
        return data


# Mock implementations for components we haven't built yet
class MockCacheManager(ICacheManager):
    async def get_cached_data(self, cache_key: str): return None
    async def store_data(self, cache_key: str, data: Dict[str, Any], ttl: int): pass
    async def invalidate_cache(self, pattern: str): pass
    def get_cache_info(self, cache_key: str): return None
    async def cleanup_expired(self) -> int: return 0


async def test_scraper(url: str, selectors: Dict[str, str] = None):
    """Test the scraper with a given URL."""
    
    print("🚀 Universal Scraping Layer Test")
    print("=" * 50)
    print(f"Target URL: {url}")
    
    if selectors:
        print(f"Selectors: {selectors}")
    else:
        print("Selectors: None (will extract basic page info)")
    
    print()
    
    # Create scraping configuration
    config = ScriptConfig(
        url=url,
        script_type=ScrapingStrategy.STATIC,  # Start with static
        selectors=selectors or {},
        cache_ttl=0  # No caching for testing
    )
    
    # Create component instances
    content_detector = SimpleContentDetector()
    static_scraper = SimpleStaticScraper()
    data_extractor = SimpleDataExtractor()
    
    # Create mock components
    script_executor = AsyncMock()
    dynamic_scraper = AsyncMock()
    browser_manager = AsyncMock()
    cache_manager = MockCacheManager()
    error_handler = AsyncMock()
    
    # Create scraping engine
    engine = ScrapingEngine(
        content_detector=content_detector,
        script_executor=script_executor,
        static_scraper=static_scraper,
        dynamic_scraper=dynamic_scraper,
        browser_manager=browser_manager,
        data_extractor=data_extractor,
        cache_manager=cache_manager,
        error_handler=error_handler
    )
    
    try:
        # Execute scraping
        print("🔄 Starting scraping operation...")
        print(" Engine: Starting scrape for", url)
        
        # Analyze website first
        print(" Engine: Analyzing website...")
        analysis = await engine.analyze_url(url)
        print(f" Engine: Analysis - Static: {analysis.is_static}, Strategy: {analysis.recommended_strategy.value}")
        
        result = await engine.scrape(config)
        print(" Engine: Scraping completed")
        
        print("\n📊 SCRAPING RESULTS")
        print("=" * 50)
        print(f"Success: {result.success}")
        print(f"Items extracted: {len(result.data)}")
        print(f"Strategy used: {result.metadata.strategy_used.value}")
        
        if result.performance_metrics:
            print(f"Duration: {result.performance_metrics.total_duration:.2f} seconds")
        
        if result.errors:
            print(f"Errors: {len(result.errors)}")
            for error in result.errors:
                print(f"  - {error.error_type}: {error.message}")
        
        print("\n📋 EXTRACTED DATA:")
        print("-" * 30)
        
        for i, item in enumerate(result.data, 1):
            print(f"\nItem {i}:")
            for key, value in item.items():
                if isinstance(value, list):
                    print(f"  {key}: {value}")
                else:
                    # Truncate long values for display
                    display_value = str(value)
                    if len(display_value) > 100:
                        display_value = display_value[:97] + "..."
                    print(f"  {key}: {display_value}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ SCRAPING FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function to run the scraper test."""
    
    # Default test cases
    test_cases = [
        {
            'name': 'Example.com (Basic)',
            'url': 'https://example.com',
            'selectors': {'title': 'h1', 'content': 'p'}
        },
        {
            'name': 'HTTPBin (JSON API)',
            'url': 'https://httpbin.org/html',
            'selectors': {'title': 'h1', 'paragraphs': 'p'}
        },
        {
            'name': 'Wikipedia (Complex)',
            'url': 'https://en.wikipedia.org/wiki/Web_scraping',
            'selectors': {'title': 'h1', 'summary': 'p', 'headings': 'h2'}
        }
    ]
    
    if len(sys.argv) > 1:
        # Custom URL provided
        url = sys.argv[1]
        selectors = {}
        
        # Parse selectors if provided as key=value pairs
        if len(sys.argv) > 2:
            for arg in sys.argv[2:]:
                if '=' in arg:
                    key, value = arg.split('=', 1)
                    selectors[key] = value
        
        print(f"Testing custom URL: {url}")
        asyncio.run(test_scraper(url, selectors))
    
    else:
        # Run predefined test cases
        print("🧪 Running predefined test cases...")
        print("Usage: python test_scraper.py <url> [key=selector ...]")
        print("\nExample: python test_scraper.py https://example.com title=h1 content=p")
        print("\nRunning default test case...")
        
        # Run just the first test case
        test_case = test_cases[0]
        print(f"\n🎯 Testing: {test_case['name']}")
        asyncio.run(test_scraper(test_case['url'], test_case['selectors']))


if __name__ == "__main__":
    main()