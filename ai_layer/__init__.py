"""
AI Layer for generating API responses and scraper scripts using DeepSeek AI.

This module provides components for:
- DeepSeek API client integration
- Form input processing and validation
- AI response generation and validation
- Scraper script generation and validation
- Configuration management
"""

from ai_layer.config import DeepSeekConfig, ConfigurationError
from ai_layer.exceptions import (
    DeepSeekAPIError,
    DeepSeekAuthError,
    DeepSeekRateLimitError,
    DeepSeekConnectionError,
    ValidationError,
    GenerationError
)

# Parsing models and exceptions
from ai_layer.parsing_models import (
    ParsedDataResponse,
    ParsingMetadata,
    EmptyDataError,
    ParsingError,
    DataExtractionError
)

# Scraped data parser components
from ai_layer.scraped_data_parser import ScrapedDataParser
from ai_layer.data_extractor import DataExtractor
from ai_layer.parsing_prompt_builder import ParsingPromptBuilder
from ai_layer.parsing_validator import ParsingValidator
from ai_layer.models import GeneratedResponse, ResponseMetadata
from ai_layer.deepseek_client import DeepSeekClient
from ai_layer.response_generator import AIResponseGenerator

# Script generation components
from ai_layer.script_models import (
    GeneratedScript,
    ScriptMetadata,
    ScriptValidationResult,
    ScriptValidationError,
    ScriptExecutionError,
    ScriptGenerationError
)
from ai_layer.scraper_script_generator import ScraperScriptGenerator
from ai_layer.script_validator import ScriptValidator
from ai_layer.script_prompt_builder import ScriptPromptBuilder

__all__ = [
    # Configuration
    'DeepSeekConfig',
    'ConfigurationError',
    # Exceptions
    'DeepSeekAPIError',
    'DeepSeekAuthError',
    'DeepSeekRateLimitError',
    'DeepSeekConnectionError',
    'ValidationError',
    'GenerationError',
    # Response generation
    'GeneratedResponse',
    'ResponseMetadata',
    'DeepSeekClient',
    'AIResponseGenerator',
    # Script generation
    'GeneratedScript',
    'ScriptMetadata',
    'ScriptValidationResult',
    'ScriptValidationError',
    'ScriptExecutionError',
    'ScriptGenerationError',
    'ScraperScriptGenerator',
    'ScriptValidator',
    'ScriptPromptBuilder',
    # Parsing models and exceptions
    'ParsedDataResponse',
    'ParsingMetadata',
    'EmptyDataError',
    'ParsingError',
    'DataExtractionError',
    # Scraped data parser components
    'ScrapedDataParser',
    'DataExtractor',
    'ParsingPromptBuilder',
    'ParsingValidator',
]
