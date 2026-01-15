"""
Custom exception classes for the AI Layer.

This module defines all custom exceptions used throughout the AI Response Generator,
providing clear error categorization and user-friendly error messages.
"""


class DeepSeekAPIError(Exception):
    """Base exception for DeepSeek API errors."""
    pass


class DeepSeekAuthError(DeepSeekAPIError):
    """Authentication failure with DeepSeek API."""
    pass


class DeepSeekRateLimitError(DeepSeekAPIError):
    """Rate limit exceeded on DeepSeek API."""
    
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after


class DeepSeekConnectionError(DeepSeekAPIError):
    """Network connection error when calling DeepSeek API."""
    pass


class ValidationError(Exception):
    """Input validation error."""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.field = field


class GenerationError(Exception):
    """AI generation error."""
    pass


class ConfigurationError(Exception):
    """Configuration error (e.g., missing API key)."""
    pass
