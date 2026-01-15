"""
Data models for the Scraped Data Parser.

This module defines data classes for representing parsed data responses,
metadata, and other data structures used throughout the Scraped Data Parser.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
import json


@dataclass
class ParsingMetadata:
    """Metadata about the parsing process."""
    
    timestamp: datetime
    model: str
    tokens_used: int
    parsing_time_ms: int
    records_parsed: int
    fields_extracted: List[str]
    data_sources: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary with ISO format timestamp."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'model': self.model,
            'tokens_used': self.tokens_used,
            'parsing_time_ms': self.parsing_time_ms,
            'records_parsed': self.records_parsed,
            'fields_extracted': self.fields_extracted,
            'data_sources': self.data_sources
        }


@dataclass
class ParsedDataResponse:
    """Container for parsed data response."""
    
    data: Dict[str, Any]
    metadata: ParsingMetadata
    raw_ai_output: str
    source_metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            'data': self.data,
            'metadata': self.metadata.to_dict(),
            'raw_ai_output': self.raw_ai_output,
            'source_metadata': self.source_metadata
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert response to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def get_data_only_json(self, indent: int = 2) -> str:
        """Get only the parsed data as JSON string (without metadata)."""
        return json.dumps(self.data, indent=indent, default=str)


# Parsing-specific exceptions

class EmptyDataError(Exception):
    """Raised when scraping result contains no data."""
    
    def __init__(self, message: str = "No data was found in the scraped results."):
        super().__init__(message)


class ParsingError(Exception):
    """Raised when AI fails to parse data."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(message)
        self.details = details


class DataExtractionError(Exception):
    """Raised when text extraction from scraped data fails."""
    
    def __init__(self, message: str, data_format: str = None):
        super().__init__(message)
        self.data_format = data_format



@dataclass
class ParsingConfig:
    """Configuration for data parsing."""
    
    max_text_length: int = 50000  # Maximum text length to send to AI
    temperature: float = 0.3  # Lower for more consistent parsing
    max_tokens: int = 8000  # Increased for large datasets
    retry_attempts: int = 2  # Number of retry attempts for parsing failures
    model: str = "deepseek-chat"  # Default model to use
    
    @classmethod
    def default(cls) -> 'ParsingConfig':
        """Get default configuration."""
        return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'max_text_length': self.max_text_length,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'retry_attempts': self.retry_attempts,
            'model': self.model
        }
