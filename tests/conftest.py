"""
Pytest configuration and shared fixtures for the Universal Scraping Layer tests.
"""

import pytest
import asyncio
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta

from scraping_layer.models import (
    ScriptConfig, ScrapingStrategy, BrowserRequirements, RetryConfig,
    WebsiteAnalysis, FrameworkInfo, FrameworkType, ScrapingResult,
    ScrapingMetadata, PerformanceMetrics
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_script_config() -> ScriptConfig:
    """Provide a sample ScriptConfig for testing."""
    return ScriptConfig(
        url="https://example.com",
        script_type=ScrapingStrategy.STATIC,
        selectors={"title": "h1", "content": ".content"},
        cache_ttl=3600,
        timeout=30
    )


@pytest.fixture
def sample_dynamic_config() -> ScriptConfig:
    """Provide a sample dynamic ScriptConfig for testing."""
    return ScriptConfig(
        url="https://spa-example.com",
        script_type=ScrapingStrategy.DYNAMIC,
        selectors={"items": ".item", "title": ".item-title"},
        browser_requirements=BrowserRequirements(
            headless=True,
            javascript_enabled=True
        ),
        cache_ttl=1800
    )


@pytest.fixture
def sample_website_analysis() -> WebsiteAnalysis:
    """Provide a sample WebsiteAnalysis for testing."""
    return WebsiteAnalysis(
        is_static=True,
        framework=FrameworkInfo(
            framework=FrameworkType.REACT,
            version="18.0.0",
            confidence=0.9
        ),
        requires_javascript=False,
        has_anti_bot=False,
        estimated_load_time=1.5,
        recommended_strategy=ScrapingStrategy.STATIC,
        confidence_score=0.85
    )


@pytest.fixture
def sample_scraping_result() -> ScrapingResult:
    """Provide a sample ScrapingResult for testing."""
    return ScrapingResult(
        success=True,
        data=[
            {"title": "Test Title", "content": "Test Content"},
            {"title": "Another Title", "content": "More Content"}
        ],
        metadata=ScrapingMetadata(
            strategy_used=ScrapingStrategy.STATIC,
            framework_detected=FrameworkType.REACT,
            final_url="https://example.com",
            response_status=200
        ),
        performance_metrics=PerformanceMetrics(
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=2),
            total_duration=2.0,
            items_extracted=2
        )
    )


@pytest.fixture
def mock_html_content() -> str:
    """Provide mock HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    </head>
    <body>
        <div id="root">
            <h1>Test Title</h1>
            <div class="content">Test Content</div>
            <div class="item">
                <div class="item-title">Item 1</div>
            </div>
            <div class="item">
                <div class="item-title">Item 2</div>
            </div>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def mock_spa_html() -> str:
    """Provide mock SPA HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SPA Test</title>
        <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    </head>
    <body>
        <div id="root">Loading...</div>
        <script>
            // Simulate React app loading
            setTimeout(() => {
                document.getElementById('root').innerHTML = 
                    '<div class="app"><h1>SPA Content</h1><div class="items"></div></div>';
            }, 1000);
        </script>
    </body>
    </html>
    """


@pytest.fixture
def mock_browser():
    """Provide a mock browser instance for testing."""
    browser = AsyncMock()
    browser.new_page = AsyncMock()
    browser.close = AsyncMock()
    return browser


@pytest.fixture
def mock_page():
    """Provide a mock page instance for testing."""
    page = AsyncMock()
    page.goto = AsyncMock()
    page.content = AsyncMock(return_value="<html><body>Mock content</body></html>")
    page.wait_for_selector = AsyncMock()
    page.click = AsyncMock()
    page.fill = AsyncMock()
    page.evaluate = AsyncMock()
    page.close = AsyncMock()
    return page


@pytest.fixture
def sample_extracted_data() -> List[Dict[str, Any]]:
    """Provide sample extracted data for testing."""
    return [
        {
            "title": "First Article",
            "content": "This is the first article content.",
            "author": "John Doe",
            "date": "2024-01-15"
        },
        {
            "title": "Second Article", 
            "content": "This is the second article content.",
            "author": "Jane Smith",
            "date": "2024-01-16"
        }
    ]


@pytest.fixture
def sample_malformed_data() -> List[Dict[str, Any]]:
    """Provide sample malformed data for testing."""
    return [
        {
            "title": "Article &amp; Title",  # HTML entity
            "content": "Content with\n\nextra   spaces",  # Whitespace issues
            "author": "",  # Empty field
            "date": None  # Missing field
        },
        {
            "title": "&lt;script&gt;alert('xss')&lt;/script&gt;",  # Potential XSS
            "content": "Normal content",
            # Missing author field entirely
            "date": "invalid-date-format"
        }
    ]


# Property-based testing helpers
class PropertyTestHelpers:
    """Helper functions for property-based testing."""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if a URL is valid for testing."""
        return url.startswith(('http://', 'https://')) and len(url) > 10
    
    @staticmethod
    def is_valid_selector(selector: str) -> bool:
        """Check if a CSS selector is valid for testing."""
        return len(selector) > 0 and not selector.isspace()
    
    @staticmethod
    def contains_framework_signature(html: str, framework: FrameworkType) -> bool:
        """Check if HTML contains framework signatures."""
        signatures = {
            FrameworkType.REACT: ['react', 'React', 'ReactDOM'],
            FrameworkType.ANGULAR: ['angular', 'ng-', '@angular'],
            FrameworkType.VUE: ['vue', 'Vue', 'v-'],
            FrameworkType.JQUERY: ['jquery', 'jQuery', '$']
        }
        
        if framework in signatures:
            return any(sig in html for sig in signatures[framework])
        return False


@pytest.fixture
def property_helpers() -> PropertyTestHelpers:
    """Provide property testing helper functions."""
    return PropertyTestHelpers()