"""
Static Scraper - Extracts data from static HTML websites using HTTP requests and BeautifulSoup.
"""

import logging
from typing import Dict, List, Any
import aiohttp
from bs4 import BeautifulSoup

from .interfaces import IStaticScraper
from .models import StaticScrapingConfig
from .config import get_config


class StaticScraper(IStaticScraper):
    """Scraper for static HTML websites using HTTP requests and BeautifulSoup."""
    
    def __init__(self, logger: logging.Logger = None):
        """Initialize the static scraper."""
        self.logger = logger or logging.getLogger(__name__)
        self.config = get_config()
    
    async def scrape_static(self, config: StaticScrapingConfig) -> List[Dict[str, Any]]:
        """
        Scrape data from a static HTML website.
        
        Args:
            config: Configuration containing URL, selectors, and timeout
            
        Returns:
            List of dictionaries containing extracted data
        """
        self.logger.info(f"Fetching HTML from {config.url}")
        
        # Fetch HTML content
        html = await self._fetch_html(config.url, config.timeout, config.headers)
        
        if not html:
            self.logger.warning("No HTML content received")
            return []
        
        self.logger.info(f"Parsing HTML ({len(html)} bytes)")
        
        # Extract data using selectors
        data = self.extract_with_selectors(html, config.selectors)
        
        # Return as list (even if single item)
        if data:
            return [data] if isinstance(data, dict) else data
        return []
    
    async def _fetch_html(self, url: str, timeout: int, headers: Dict[str, str] = None) -> str:
        """
        Fetch HTML content from URL using aiohttp.
        
        Args:
            url: Target URL
            timeout: Request timeout in seconds
            headers: Optional HTTP headers
            
        Returns:
            HTML content as string
        """
        # Prepare headers
        request_headers = {
            'User-Agent': self.config.network.user_agent
        }
        if headers:
            request_headers.update(headers)
        
        try:
            # Create timeout object
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            
            # Make HTTP GET request
            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                async with session.get(url, headers=request_headers) as response:
                    response.raise_for_status()
                    html = await response.text()
                    self.logger.info(f"Successfully fetched {len(html)} bytes from {url}")
                    return html
                    
        except aiohttp.ClientError as e:
            self.logger.error(f"HTTP request failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching HTML: {e}")
            raise
    
    def extract_with_selectors(self, html: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract data from HTML using CSS selectors.
        
        Args:
            html: HTML content as string
            selectors: Dictionary mapping field names to CSS selectors
            
        Returns:
            Dictionary with extracted data
        """
        if not html or not selectors:
            return {}
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract data for each selector
        extracted_data = {}
        
        for field_name, selector in selectors.items():
            try:
                # Find element using CSS selector
                element = soup.select_one(selector)
                
                if element:
                    # Extract text content (strip whitespace)
                    text = element.get_text(strip=True)
                    extracted_data[field_name] = text
                    self.logger.debug(f"Extracted '{field_name}': {text[:50]}...")
                else:
                    # Selector didn't match anything
                    extracted_data[field_name] = ""
                    self.logger.debug(f"No match for selector '{selector}' (field: {field_name})")
                    
            except Exception as e:
                self.logger.warning(f"Error extracting field '{field_name}' with selector '{selector}': {e}")
                extracted_data[field_name] = ""
        
        return extracted_data
