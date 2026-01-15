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
import time

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
        
        # Heuristic for single-fact queries (speed optimization)
        desc = (form_data.get("data_description") or "").lower()
        single_fact = any(x in desc for x in ["current", "who is", "what is", "latest", "today"])
        max_tokens = 400 if single_fact else 2000
        temperature = 0.0 if single_fact else 0.3

        t0 = time.time()
        response = generator.generate_response(form_data, max_tokens=max_tokens, temperature=temperature)
        t1 = time.time()
        logger.info(f"DeepSeek generation took {t1 - t0:.2f}s (single_fact={single_fact}, max_tokens={max_tokens})")
        
        # Format response for UI display
        data = response.data
        
        # Apply desired fields filtering only if provided (UI response shaping)
        desired_fields_text = (form_data.get("desired_fields") or "").strip()
        if desired_fields_text and isinstance(data, dict):
            desired_field_list = [line.strip() for line in desired_fields_text.split("\n") if line.strip()]
            if desired_field_list and isinstance(data.get("data"), list):
                data["data"] = [{k: item.get(k) for k in desired_field_list} for item in data["data"] if isinstance(item, dict)]

        # Apply response structure only if provided (UI response shaping)
        response_structure_text = (form_data.get("response_structure") or "").strip()
        if response_structure_text:
            try:
                template = json.loads(response_structure_text)
                if isinstance(template, dict):
                    records = []
                    if isinstance(data, dict):
                        records = data.get("data", [])
                    if isinstance(records, dict):
                        records = [records]
                    if not isinstance(records, list):
                        records = []

                    # Enforce allowed keys from template["data"][0] if desired_fields not provided
                    allowed_keys = None
                    tmpl_data = template.get("data")
                    if isinstance(tmpl_data, list) and len(tmpl_data) > 0 and isinstance(tmpl_data[0], dict):
                        allowed_keys = list(tmpl_data[0].keys())

                    if allowed_keys:
                        filtered = []
                        for item in records:
                            if isinstance(item, dict):
                                filtered.append({k: item.get(k) for k in allowed_keys})
                        records = filtered

                    template["data"] = records
                    data = template
            except Exception:
                # If structure JSON is invalid, keep current behavior (do not crash)
                pass
        
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