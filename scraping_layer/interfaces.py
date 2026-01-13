"""
Core interfaces for the Universal Scraping Layer.

This module defines the abstract base classes and protocols that all
components must implement, ensuring consistent behavior across the system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Protocol
from playwright.async_api import Browser, Page

from .models import (
    ScriptConfig, ScrapingResult, WebsiteAnalysis, ValidationResult,
    ExecutionContext, ExecutionResult, SecurityValidation, SandboxEnvironment,
    StaticScrapingConfig, DynamicScrapingConfig, BrowserRequirements,
    FrameworkInfo, CacheInfo
)


class IContentDetector(ABC):
    """Interface for website content analysis and detection."""
    
    @abstractmethod
    async def analyze_website(self, url: str) -> WebsiteAnalysis:
        """Analyze a website to determine optimal scraping strategy."""
        pass
    
    @abstractmethod
    def detect_framework(self, html: str) -> FrameworkInfo:
        """Detect JavaScript framework from HTML content."""
        pass
    
    @abstractmethod
    async def requires_javascript(self, url: str) -> bool:
        """Determine if a website requires JavaScript for content rendering."""
        pass
    
    @abstractmethod
    async def detect_anti_bot_measures(self, url: str) -> List[str]:
        """Detect anti-bot protection mechanisms."""
        pass


class IScriptExecutor(ABC):
    """Interface for secure script execution."""
    
    @abstractmethod
    async def execute_script(self, script: str, context: ExecutionContext) -> ExecutionResult:
        """Execute an AI-generated scraping script safely."""
        pass
    
    @abstractmethod
    def validate_script_safety(self, script: str) -> SecurityValidation:
        """Validate script for security issues."""
        pass
    
    @abstractmethod
    def create_sandbox(self) -> SandboxEnvironment:
        """Create an isolated execution environment."""
        pass
    
    @abstractmethod
    async def cleanup_sandbox(self, sandbox_id: str) -> None:
        """Clean up sandbox resources."""
        pass


class IStaticScraper(ABC):
    """Interface for static HTML scraping."""
    
    @abstractmethod
    async def scrape_static(self, config: StaticScrapingConfig) -> List[Dict[str, Any]]:
        """Scrape data from static HTML websites."""
        pass
    
    @abstractmethod
    def extract_with_selectors(self, html: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract data using CSS/XPath selectors."""
        pass
    
    @abstractmethod
    async def handle_pagination(self, base_url: str, pagination_config: Dict[str, Any]) -> List[str]:
        """Handle paginated content extraction."""
        pass
    
    @abstractmethod
    async def submit_form(self, url: str, form_data: Dict[str, Any]) -> str:
        """Submit forms and return response HTML."""
        pass


class IDynamicScraper(ABC):
    """Interface for dynamic JavaScript-rendered content scraping."""
    
    @abstractmethod
    async def scrape_dynamic(self, config: DynamicScrapingConfig) -> List[Dict[str, Any]]:
        """Scrape data from JavaScript-rendered websites."""
        pass
    
    @abstractmethod
    async def wait_for_content(self, page: Page, selector: str, timeout: int) -> bool:
        """Wait for dynamic content to load."""
        pass
    
    @abstractmethod
    async def simulate_interactions(self, page: Page, interactions: List[Any]) -> None:
        """Simulate user interactions like clicks and form submissions."""
        pass
    
    @abstractmethod
    async def execute_custom_js(self, page: Page, script: str) -> Any:
        """Execute custom JavaScript for data extraction."""
        pass


class IBrowserManager(ABC):
    """Interface for browser instance management."""
    
    @abstractmethod
    async def get_browser(self, requirements: BrowserRequirements) -> Browser:
        """Get a browser instance matching requirements."""
        pass
    
    @abstractmethod
    async def release_browser(self, browser: Browser) -> None:
        """Release a browser instance back to the pool."""
        pass
    
    @abstractmethod
    def cleanup_idle_browsers(self) -> None:
        """Clean up idle browser instances."""
        pass
    
    @abstractmethod
    async def restart_browser(self, browser: Browser) -> Browser:
        """Restart a browser instance due to memory issues."""
        pass
    
    @abstractmethod
    def get_browser_stats(self) -> Dict[str, Any]:
        """Get statistics about browser usage."""
        pass


class IDataExtractor(ABC):
    """Interface for data extraction and validation."""
    
    @abstractmethod
    def validate_data(self, data: List[Dict[str, Any]], schema: Dict[str, Any]) -> ValidationResult:
        """Validate extracted data against expected schema."""
        pass
    
    @abstractmethod
    def clean_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and normalize extracted data."""
        pass
    
    @abstractmethod
    def decode_html_entities(self, text: str) -> str:
        """Decode HTML entities to plain text."""
        pass
    
    @abstractmethod
    def handle_missing_fields(self, data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """Handle missing required fields in extracted data."""
        pass


class ICacheManager(ABC):
    """Interface for data caching and storage."""
    
    @abstractmethod
    async def get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached data if available and fresh."""
        pass
    
    @abstractmethod
    async def store_data(self, cache_key: str, data: Dict[str, Any], ttl: int) -> None:
        """Store data in cache with TTL."""
        pass
    
    @abstractmethod
    async def invalidate_cache(self, pattern: str) -> None:
        """Invalidate cached entries matching pattern."""
        pass
    
    @abstractmethod
    def get_cache_info(self, cache_key: str) -> Optional[CacheInfo]:
        """Get information about cached data."""
        pass
    
    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Clean up expired cache entries."""
        pass


class IErrorHandler(ABC):
    """Interface for error handling and recovery."""
    
    @abstractmethod
    async def handle_network_error(self, error: Exception, attempt: int) -> bool:
        """Handle network-related errors with retry logic."""
        pass
    
    @abstractmethod
    async def handle_anti_bot_detection(self, url: str) -> Dict[str, Any]:
        """Handle anti-bot detection with countermeasures."""
        pass
    
    @abstractmethod
    async def fallback_to_static(self, config: DynamicScrapingConfig) -> Optional[List[Dict[str, Any]]]:
        """Fallback from dynamic to static scraping."""
        pass
    
    @abstractmethod
    def preserve_partial_results(self, results: List[Dict[str, Any]], error: Exception) -> Dict[str, Any]:
        """Preserve partial results when critical errors occur."""
        pass


class IScrapingEngine(ABC):
    """Interface for the main scraping orchestrator."""
    
    @abstractmethod
    async def scrape(self, script_config: ScriptConfig) -> ScrapingResult:
        """Execute a complete scraping operation."""
        pass
    
    @abstractmethod
    async def validate_script(self, script: str) -> ValidationResult:
        """Validate an AI-generated script."""
        pass
    
    @abstractmethod
    def get_supported_strategies(self) -> List[str]:
        """Get list of supported scraping strategies."""
        pass
    
    @abstractmethod
    async def analyze_url(self, url: str) -> WebsiteAnalysis:
        """Analyze a URL to determine optimal strategy."""
        pass


# Protocol for template execution
class TemplateExecutor(Protocol):
    """Protocol for template execution systems."""
    
    async def execute_template(self, template_type: str, template_data: Dict[str, Any]) -> ExecutionResult:
        """Execute a scraping template."""
        ...
    
    def validate_template(self, template: str) -> ValidationResult:
        """Validate template syntax and safety."""
        ...


# Protocol for logging
class Logger(Protocol):
    """Protocol for logging operations."""
    
    def log_operation_start(self, operation: str, details: Dict[str, Any]) -> None:
        """Log the start of an operation."""
        ...
    
    def log_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Log an error with context."""
        ...
    
    def log_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log performance metrics."""
        ...
    
    def log_security_alert(self, alert: str, details: Dict[str, Any]) -> None:
        """Log security alerts."""
        ...