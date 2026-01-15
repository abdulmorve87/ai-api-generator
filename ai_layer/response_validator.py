"""
Response validation and JSON extraction.

This module handles validating AI-generated responses and extracting
JSON from various formats (plain JSON, markdown code blocks, etc.).
"""

import json
import re
from typing import Dict, Any, Tuple
from ai_layer.exceptions import GenerationError


class ResponseValidator:
    """Validates and extracts JSON from AI responses."""
    
    @staticmethod
    def validate_json(ai_output: str) -> Dict[str, Any]:
        """
        Validate AI output as valid JSON and parse it.
        
        Args:
            ai_output: Raw output from AI
            
        Returns:
            Parsed JSON object as dictionary
            
        Raises:
            GenerationError: If JSON is invalid and cannot be extracted
        """
        if not ai_output or not ai_output.strip():
            raise GenerationError("AI returned empty response")
        
        # First, try to parse as-is
        try:
            parsed = json.loads(ai_output)
            if isinstance(parsed, dict):
                return parsed
            else:
                raise GenerationError("AI response is not a JSON object (expected dictionary)")
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON
            pass
        
        # Try to extract JSON from markdown or mixed text
        extracted_json = ResponseValidator.extract_json_from_text(ai_output)
        if extracted_json:
            try:
                parsed = json.loads(extracted_json)
                if isinstance(parsed, dict):
                    return parsed
                else:
                    raise GenerationError("Extracted JSON is not an object (expected dictionary)")
            except json.JSONDecodeError as e:
                raise GenerationError(f"Failed to parse extracted JSON: {str(e)}")
        
        # If all extraction attempts fail, provide helpful error
        raise GenerationError(
            "Failed to generate valid JSON response. "
            "The AI output could not be parsed as JSON. "
            "Please try again or simplify your requirements."
        )
    
    @staticmethod
    def extract_json_from_text(text: str) -> str:
        """
        Extract JSON from text that may contain markdown code blocks or other formatting.
        
        Args:
            text: Text that may contain JSON
            
        Returns:
            Extracted JSON string, or empty string if not found
        """
        # Pattern 1: JSON in markdown code blocks (```json ... ``` or ``` ... ```)
        code_block_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
        matches = re.findall(code_block_pattern, text, re.DOTALL)
        if matches:
            # Try each match
            for match in matches:
                if match.strip().startswith('{') or match.strip().startswith('['):
                    return match.strip()
        
        # Pattern 2: Look for JSON object boundaries
        # Find the first { and last } that might form a valid JSON object
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            potential_json = text[first_brace:last_brace + 1]
            # Quick validation - count braces
            if potential_json.count('{') == potential_json.count('}'):
                return potential_json
        
        # Pattern 3: Look for JSON array boundaries
        first_bracket = text.find('[')
        last_bracket = text.rfind(']')
        
        if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
            potential_json = text[first_bracket:last_bracket + 1]
            # Quick validation - count brackets
            if potential_json.count('[') == potential_json.count(']'):
                return potential_json
        
        return ""
    
    @staticmethod
    def generate_error_message(ai_output: str, error: Exception) -> str:
        """
        Generate a clear error message for parsing failures.
        
        Args:
            ai_output: The AI output that failed to parse
            error: The exception that occurred
            
        Returns:
            User-friendly error message with details
        """
        preview = ai_output[:200] + "..." if len(ai_output) > 200 else ai_output
        
        return (
            f"Failed to parse AI response as JSON.\n\n"
            f"Error: {str(error)}\n\n"
            f"AI Output Preview:\n{preview}\n\n"
            f"Suggestion: Try simplifying your requirements or providing a clearer structure example."
        )
