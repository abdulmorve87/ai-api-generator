"""
DeepSeek API client for generating AI responses.

This module provides a client for communicating with the DeepSeek API
using the OpenAI-compatible format.
"""

import requests
import time
import random
from typing import List, Dict, Any
from ai_layer.exceptions import (
    DeepSeekAPIError,
    DeepSeekAuthError,
    DeepSeekRateLimitError,
    DeepSeekConnectionError
)


class DeepSeekClient:
    """Client for interacting with the DeepSeek API."""
    
    # Retry configuration
    MAX_RETRIES = 3
    BASE_DELAY = 1.0  # seconds
    MAX_DELAY = 30.0  # seconds
    REQUEST_TIMEOUT = 60  # seconds - increased for larger responses
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        """
        Initialize DeepSeek client with API credentials.
        
        Args:
            api_key: API key from DeepSeek platform
            base_url: Base URL for the API (default: https://api.deepseek.com)
            
        Raises:
            ValueError: If api_key is empty or None
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
        
        # Fix SSL certificate issues on Windows
        # Try to use certifi's certificate bundle
        try:
            import certifi
            import os
            cert_path = certifi.where()
            if os.path.exists(cert_path):
                self.session.verify = cert_path
            else:
                # If certifi path doesn't exist, use True (default verification)
                self.session.verify = True
        except (ImportError, Exception):
            # If certifi is not available or fails, use default verification
            self.session.verify = True
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """
        Calculate delay with exponential backoff and jitter.
        
        Args:
            attempt: Current retry attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        delay = min(self.BASE_DELAY * (2 ** attempt), self.MAX_DELAY)
        jitter = random.uniform(0, delay * 0.1)
        return delay + jitter
    
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> str:
        """
        Send a chat completion request to DeepSeek API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (default: "deepseek-chat")
            temperature: Sampling temperature 0.0 to 1.0 (default: 0.7)
            max_tokens: Maximum tokens in response (default: 2000)
            stream: Whether to stream the response (default: False)
            
        Returns:
            Generated text content
            
        Raises:
            DeepSeekAuthError: When authentication fails (401)
            DeepSeekRateLimitError: When rate limit is exceeded (429)
            DeepSeekConnectionError: When network connection fails
            DeepSeekAPIError: For other API errors
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        last_exception = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.post(url, json=payload, timeout=self.REQUEST_TIMEOUT)
                
                # Handle different HTTP status codes
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content']
                
                elif response.status_code == 401:
                    raise DeepSeekAuthError(
                        "Authentication failed. Please verify your DeepSeek API key is correct."
                    )
                
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    raise DeepSeekRateLimitError(
                        f"Rate limit exceeded. Please wait {retry_after} seconds before trying again.",
                        retry_after=retry_after
                    )
                
                elif response.status_code >= 500:
                    # Server errors - retry with backoff
                    error_msg = f"DeepSeek service error (HTTP {response.status_code})"
                    if attempt < self.MAX_RETRIES - 1:
                        delay = self._calculate_retry_delay(attempt)
                        time.sleep(delay)
                        continue
                    raise DeepSeekAPIError(
                        f"{error_msg}. Please try again in a few moments."
                    )
                
                else:
                    # Other errors
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    except:
                        error_msg = response.text or f"HTTP {response.status_code}"
                    
                    raise DeepSeekAPIError(f"API error: {error_msg}")
            
            except requests.exceptions.Timeout:
                last_exception = DeepSeekConnectionError(
                    "Request timed out. Please check your internet connection."
                )
                if attempt < self.MAX_RETRIES - 1:
                    delay = self._calculate_retry_delay(attempt)
                    time.sleep(delay)
                    continue
            
            except requests.exceptions.ConnectionError:
                last_exception = DeepSeekConnectionError(
                    "Unable to connect to DeepSeek API. Please check your internet connection."
                )
                if attempt < self.MAX_RETRIES - 1:
                    delay = self._calculate_retry_delay(attempt)
                    time.sleep(delay)
                    continue
            
            except (DeepSeekAuthError, DeepSeekRateLimitError, DeepSeekAPIError):
                # Don't retry auth errors, rate limits, or explicit API errors
                raise
        
        # If we exhausted retries, raise the last exception
        if last_exception:
            raise last_exception
        
        raise DeepSeekAPIError("Failed to generate completion after multiple retries")
