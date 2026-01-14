"""
AI Layer for generating API responses using DeepSeek AI.

This module provides components for:
- DeepSeek API client integration
- Form input processing and validation
- AI response generation and validation
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
from ai_layer.models import GeneratedResponse, ResponseMetadata
from ai_layer.deepseek_client import DeepSeekClient
from ai_layer.response_generator import AIResponseGenerator

__all__ = [
    'DeepSeekConfig',
    'ConfigurationError',
    'DeepSeekAPIError',
    'DeepSeekAuthError',
    'DeepSeekRateLimitError',
    'DeepSeekConnectionError',
    'ValidationError',
    'GenerationError',
    'GeneratedResponse',
    'ResponseMetadata',
    'DeepSeekClient',
    'AIResponseGenerator',
]
