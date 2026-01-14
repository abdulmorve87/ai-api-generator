"""
Mock data generator using AI Layer (DeepSeek).
This module integrates with the ai_layer package for generating API responses.
"""

import os
import logging

# Fix SSL certificate issues on Windows (PostgreSQL, Google Cloud SDK interference)
for var in ['SSL_CERT_FILE', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE']:
    if var in os.environ:
        del os.environ[var]

from ai_layer import (
    DeepSeekConfig,
    DeepSeekClient,
    AIResponseGenerator,
    ConfigurationError,
    GenerationError
)
import json

logger = logging.getLogger(__name__)

# Initialize AI generator (cached)
_ai_generator = None

def get_ai_generator():
    """Get or initialize the AI generator."""
    global _ai_generator
    if _ai_generator is None:
        try:
            config = DeepSeekConfig.from_env()
            client = DeepSeekClient(config.api_key, config.base_url)
            _ai_generator = AIResponseGenerator(client)
        except ConfigurationError as e:
            logger.error(f"AI configuration error: {e}")
            raise
    return _ai_generator


def generate_response(form_data):
    """
    Generate API response using DeepSeek AI Layer.
    
    Args:
        form_data: Dictionary containing:
            - data_description: str (required)
            - data_source: str (optional)
            - desired_fields: str (optional)
            - response_structure: str (optional)
            - update_frequency: str (required)
    
    Returns:
        Dictionary with generated API response data
    """
    try:
        # Get AI generator
        generator = get_ai_generator()
        
        # Generate response using AI layer
        response = generator.generate_response(form_data)
        
        # Format response for UI display
        data = response.data
        
        # Extract endpoint name from data description
        api_name = form_data.get('data_description', 'data').lower()
        api_name = ''.join(c if c.isalnum() else '_' for c in api_name)[:50]
        
        return {
            "endpoint": f"https://api.example.com/{api_name}",
            "method": "GET",
            "response": data,
            "metadata": {
                "model": response.metadata.model,
                "generation_time_ms": response.metadata.generation_time_ms,
                "timestamp": response.metadata.timestamp.isoformat()
            }
        }
        
    except ConfigurationError as e:
        return {
            "status": "error",
            "message": f"Configuration error: {str(e)}",
            "raw": ""
        }
    except GenerationError as e:
        return {
            "status": "error",
            "message": f"Generation error: {str(e)}",
            "raw": ""
        }
    except Exception as e:
        logger.error(f"Unexpected error in generate_response: {e}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "raw": ""
        }


def load_mock_response():
    """Load a fallback mock response for testing."""
    return {
        "endpoint": "https://api.example.com/sample",
        "method": "GET",
        "response": {
            "status": "success",
            "data": [
                {"id": 1, "name": "Sample Item 1"},
                {"id": 2, "name": "Sample Item 2"}
            ]
        }
    }
