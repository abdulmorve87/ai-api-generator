"""
Configuration management for the AI Layer.

This module handles loading and validating configuration from environment variables,
providing a centralized configuration object for the DeepSeek API client.
"""

import os
from dataclasses import dataclass
from ai_layer.exceptions import ConfigurationError

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip
    pass


@dataclass
class DeepSeekConfig:
    """Configuration for DeepSeek API client."""
    
    api_key: str
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    temperature: float = 0.3  # Lower for faster, more consistent output
    max_tokens: int = 8000  # Increased for larger datasets
    
    @classmethod
    def from_env(cls) -> 'DeepSeekConfig':
        """
        Load configuration from environment variables.
        
        Required environment variables:
            DEEPSEEK_API_KEY: API key from DeepSeek platform
            
        Optional environment variables:
            DEEPSEEK_BASE_URL: Base URL for API (default: https://api.deepseek.com)
            DEEPSEEK_MODEL: Model name (default: deepseek-chat)
            DEEPSEEK_TEMPERATURE: Sampling temperature (default: 0.7)
            DEEPSEEK_MAX_TOKENS: Maximum tokens in response (default: 2000)
            
        Returns:
            DeepSeekConfig: Configuration object
            
        Raises:
            ConfigurationError: If DEEPSEEK_API_KEY is not set
        """
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ConfigurationError(
                "DEEPSEEK_API_KEY environment variable is required. "
                "Please set it to your DeepSeek API key."
            )
        
        return cls(
            api_key=api_key,
            base_url=os.getenv('DEEPSEEK_BASE_URL', cls.__dataclass_fields__['base_url'].default),
            model=os.getenv('DEEPSEEK_MODEL', cls.__dataclass_fields__['model'].default),
            temperature=float(os.getenv('DEEPSEEK_TEMPERATURE', cls.__dataclass_fields__['temperature'].default)),
            max_tokens=int(os.getenv('DEEPSEEK_MAX_TOKENS', cls.__dataclass_fields__['max_tokens'].default))
        )
