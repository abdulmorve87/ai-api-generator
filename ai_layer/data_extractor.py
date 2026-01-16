"""
Data Extractor utility for the Scraped Data Parser.

This module provides utilities for extracting and cleaning text content
from various data formats (HTML, JSON, plain text) returned by the scraping layer.
"""

import json
import re
from typing import Dict, Any, List, Union
from bs4 import BeautifulSoup

from ai_layer.parsing_models import EmptyDataError, DataExtractionError


class DataExtractor:
    """Utility for extracting clean text from scraped data."""
    
    # Default maximum text length (50KB)
    DEFAULT_MAX_LENGTH = 50000
    
    @staticmethod
    def extract_from_scraping_result(result: Any) -> str:
        """
        Extract text from ScrapingResult or execution result.
        
        Args:
            result: ScrapingResult from scraping layer or execution result
            
        Returns:
            Cleaned text representation of the data
            
        Raises:
            EmptyDataError: When result contains no data
            DataExtractionError: When extraction fails
        """
        try:
            # Handle different result types
            if hasattr(result, 'data'):
                data = result.data
            elif isinstance(result, dict) and 'data' in result:
                data = result['data']
            elif isinstance(result, list):
                data = result
            else:
                raise DataExtractionError(
                    "Unable to extract data from result",
                    data_format=type(result).__name__
                )
            
            # Check for empty data
            if not data:
                raise EmptyDataError(
                    "No data was found in the scraped results. "
                    "Please verify the data source URL and try again."
                )
            
            # Convert data to text
            if isinstance(data, list):
                return DataExtractor.extract_from_list(data)
            elif isinstance(data, dict):
                return DataExtractor.extract_from_dict(data)
            elif isinstance(data, str):
                # Check if it's HTML
                if DataExtractor._looks_like_html(data):
                    return DataExtractor.extract_from_html(data)
                return data
            else:
                return str(data)
                
        except (EmptyDataError, DataExtractionError):
            raise
        except Exception as e:
            raise DataExtractionError(
                f"Failed to extract text from scraped data: {str(e)}",
                data_format=type(result).__name__ if result else "unknown"
            )
    
    @staticmethod
    def extract_from_html(html: str) -> str:
        """
        Extract text from HTML content.
        
        Uses BeautifulSoup to parse HTML and extract text,
        removing scripts, styles, and other noise.
        
        Args:
            html: Raw HTML string
            
        Returns:
            Cleaned text content without HTML tags
        """
        if not html or not html.strip():
            return ""
        
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'meta', 'link', 'noscript']):
                element.decompose()
            
            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
                comment.extract()
            
            # Get text content
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            return text
            
        except Exception as e:
            # If parsing fails, try to strip tags manually
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
    
    @staticmethod
    def extract_from_dict(data: Dict[str, Any]) -> str:
        """
        Convert dictionary data to readable text format.
        
        Args:
            data: Dictionary data
            
        Returns:
            Formatted text representation
        """
        if not data:
            return ""
        
        try:
            # Try to format as JSON for readability
            return json.dumps(data, indent=2, default=str, ensure_ascii=False)
        except Exception:
            # Fallback to string representation
            return str(data)
    
    @staticmethod
    def extract_from_list(data: List[Any]) -> str:
        """
        Convert list data to readable text format.
        
        Handles both traditional scraped data and smart-extracted content
        with 'content', 'tables', 'lists', 'headings' fields.
        
        Args:
            data: List of data items
            
        Returns:
            Formatted text representation
        """
        if not data:
            return ""
        
        try:
            # Check if this is smart-extracted content (light scraping)
            if data and isinstance(data[0], dict):
                first_item = data[0]
                
                # Check for smart extraction format (has 'content' key instead of 'html')
                if 'content' in first_item and 'tables' in first_item:
                    return DataExtractor._extract_smart_content(data)
                
                # Check for raw HTML format (old light scraping)
                if 'html' in first_item:
                    return DataExtractor._extract_html_content(data)
            
            # Default: format as JSON array for readability
            return json.dumps(data, indent=2, default=str, ensure_ascii=False)
        except Exception:
            # Fallback to string representation
            return str(data)
    
    @staticmethod
    def _extract_smart_content(data: List[Dict[str, Any]]) -> str:
        """
        Extract text from smart-extracted content format.
        
        Args:
            data: List of smart-extracted content items
            
        Returns:
            Combined text content
        """
        all_content = []
        
        for item in data:
            source_url = item.get('source_url', 'Unknown source')
            all_content.append(f"\n{'='*60}")
            all_content.append(f"SOURCE: {source_url}")
            all_content.append('='*60)
            
            # Add headings for context
            headings = item.get('headings', [])
            if headings:
                all_content.append("\n## HEADINGS:")
                for h in headings[:10]:  # Limit to 10 headings
                    all_content.append(f"  - {h}")
            
            # Add tables (important for structured data)
            tables = item.get('tables', [])
            if tables:
                all_content.append("\n## TABLES:")
                for i, table in enumerate(tables[:5], 1):  # Limit to 5 tables
                    all_content.append(f"\n[Table {i}]")
                    all_content.append(table[:5000])  # Limit table size
            
            # Add lists
            lists = item.get('lists', [])
            if lists:
                all_content.append("\n## LISTS:")
                for lst in lists[:10]:  # Limit to 10 lists
                    all_content.append(lst[:2000])  # Limit list size
            
            # Add main content
            content = item.get('content', '')
            if content:
                all_content.append("\n## MAIN CONTENT:")
                all_content.append(content[:30000])  # Limit content size
        
        return '\n'.join(all_content)
    
    @staticmethod
    def _extract_html_content(data: List[Dict[str, Any]]) -> str:
        """
        Extract text from raw HTML content format (legacy).
        
        Args:
            data: List of items with 'html' field
            
        Returns:
            Extracted text content
        """
        all_content = []
        
        for item in data:
            source_url = item.get('source_url', 'Unknown source')
            html = item.get('html', '')
            
            if html:
                all_content.append(f"\n{'='*60}")
                all_content.append(f"SOURCE: {source_url}")
                all_content.append('='*60)
                
                # Extract text from HTML
                text = DataExtractor.extract_from_html(html)
                all_content.append(text)
        
        return '\n'.join(all_content)
    
    @staticmethod
    def truncate_if_needed(text: str, max_length: int = None) -> str:
        """
        Truncate text if it exceeds maximum length.
        
        Args:
            text: Text to truncate
            max_length: Maximum allowed length (default: 50000)
            
        Returns:
            Truncated text with indicator if truncated
        """
        if max_length is None:
            max_length = DataExtractor.DEFAULT_MAX_LENGTH
        
        if not text or len(text) <= max_length:
            return text
        
        # Truncate and add indicator
        truncated = text[:max_length]
        
        # Try to truncate at a natural boundary (newline or space)
        last_newline = truncated.rfind('\n', max_length - 1000, max_length)
        last_space = truncated.rfind(' ', max_length - 500, max_length)
        
        if last_newline > max_length - 1000:
            truncated = truncated[:last_newline]
        elif last_space > max_length - 500:
            truncated = truncated[:last_space]
        
        truncated += "\n\n[... TRUNCATED - Data exceeds maximum length ...]"
        
        return truncated
    
    @staticmethod
    def _looks_like_html(text: str) -> bool:
        """
        Check if text appears to be HTML content.
        
        Args:
            text: Text to check
            
        Returns:
            True if text looks like HTML
        """
        if not text:
            return False
        
        text = text.strip()
        
        # Check for common HTML indicators
        html_indicators = [
            text.startswith('<!DOCTYPE'),
            text.startswith('<html'),
            text.startswith('<HTML'),
            '<head>' in text or '<HEAD>' in text,
            '<body>' in text or '<BODY>' in text,
            bool(re.search(r'<[a-zA-Z][^>]*>', text[:1000]))  # Check first 1000 chars for tags
        ]
        
        return any(html_indicators)
    
    @staticmethod
    def get_record_count(data: Any) -> int:
        """
        Get the number of records in the data.
        
        Args:
            data: Data to count records from
            
        Returns:
            Number of records
        """
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            # Check if it has a 'data' key with a list
            if 'data' in data and isinstance(data['data'], list):
                return len(data['data'])
            return 1
        elif hasattr(data, 'data') and isinstance(data.data, list):
            return len(data.data)
        return 0
    
    @staticmethod
    def extract_field_names(data: Any) -> List[str]:
        """
        Extract field names from the data.
        
        Args:
            data: Data to extract field names from
            
        Returns:
            List of field names found in the data
        """
        fields = set()
        
        def extract_keys(obj):
            if isinstance(obj, dict):
                for key in obj.keys():
                    if not key.startswith('_'):  # Skip internal fields
                        fields.add(key)
                    extract_keys(obj[key])
            elif isinstance(obj, list):
                for item in obj[:10]:  # Check first 10 items
                    extract_keys(item)
        
        # Handle different data types
        if hasattr(data, 'data'):
            extract_keys(data.data)
        elif isinstance(data, (dict, list)):
            extract_keys(data)
        
        return sorted(list(fields))
