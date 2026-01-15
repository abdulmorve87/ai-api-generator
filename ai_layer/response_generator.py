"""
AI Response Generator - Main orchestration component.

This module provides the main AIResponseGenerator class that coordinates
all the components to generate JSON API responses from form inputs.
"""

import time
from datetime import datetime
from typing import Dict, Any
from ai_layer.deepseek_client import DeepSeekClient
from ai_layer.prompt_builder import PromptBuilder
from ai_layer.response_validator import ResponseValidator
from ai_layer.models import GeneratedResponse, ResponseMetadata
from ai_layer.exceptions import GenerationError


class AIResponseGenerator:
    """Orchestrates the conversion of form inputs to JSON responses."""
    
    def __init__(self, deepseek_client: DeepSeekClient):
        """
        Initialize the AI Response Generator.
        
        Args:
            deepseek_client: Configured DeepSeek API client
        """
        self.client = deepseek_client
        self.prompt_builder = PromptBuilder()
        self.validator = ResponseValidator()
    
    def generate_response(
        self,
        form_input: Dict[str, Any],
        model: str = "deepseek-chat",
        temperature: float = 0.1,  # Lower for faster, more consistent output
        max_tokens: int = 2000  # Increased for larger datasets
    ) -> GeneratedResponse:
        """
        Generate a JSON API response from form inputs.
        
        Args:
            form_input: Dictionary containing:
                - data_description: str (required)
                - data_source: str (optional)
                - desired_fields: str (optional, newline-separated)
                - response_structure: str (optional, JSON string)
                - update_frequency: str (required)
            model: DeepSeek model to use (default: "deepseek-chat")
            temperature: Sampling temperature (default: 0.7)
            max_tokens: Maximum tokens in response (default: 2000)
            
        Returns:
            GeneratedResponse object with JSON data and metadata
            
        Raises:
            ValidationError: When form inputs are invalid
            GenerationError: When AI generation fails
            DeepSeekAPIError: When API communication fails
        """
        # Step 1: Build prompt from form inputs
        try:
            messages = self.prompt_builder.build_prompt(form_input)
        except Exception as e:
            raise GenerationError(f"Failed to build prompt: {str(e)}")
        
        # Step 2: Call DeepSeek API
        start_time = time.time()
        try:
            ai_output = self.client.generate_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            # Re-raise API errors as-is
            raise
        
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        # Step 3: Validate and parse response
        try:
            parsed_data = self.validator.validate_json(ai_output)
        except GenerationError as e:
            # Add helpful context to generation errors
            error_msg = self.validator.generate_error_message(ai_output, e)
            raise GenerationError(error_msg)
        
        # Step 4: Create response object with metadata
        metadata = ResponseMetadata(
            timestamp=datetime.utcnow(),
            model=model,
            tokens_used=self._estimate_tokens(ai_output),
            generation_time_ms=generation_time_ms
        )
        
        return GeneratedResponse(
            data=parsed_data,
            metadata=metadata,
            raw_output=ai_output
        )
    
    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """
        Estimate token count for text.
        
        This is a rough approximation. For accurate counts, use tiktoken library.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 characters per token for English text
        return len(text) // 4
