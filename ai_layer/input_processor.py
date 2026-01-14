"""
Form input processing and validation.

This module handles extracting, parsing, and validating user form inputs
before they are used to construct prompts for the AI.
"""

import json
from typing import Dict, Any, List
from ai_layer.exceptions import ValidationError


class InputProcessor:
    """Processes and validates form inputs."""
    
    @staticmethod
    def extract_form_fields(form_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract all form fields from input dictionary.
        
        Args:
            form_input: Dictionary containing form data
            
        Returns:
            Dictionary with extracted fields:
                - data_description: str
                - data_source: str (may be empty)
                - desired_fields: str (may be empty)
                - response_structure: str (may be empty)
                - update_frequency: str
                
        Raises:
            ValidationError: If required fields are missing
        """
        required_fields = ['data_description', 'update_frequency']
        optional_fields = ['data_source', 'desired_fields', 'response_structure']
        
        # Check required fields
        for field in required_fields:
            if field not in form_input:
                raise ValidationError(
                    f"Required field '{field}' is missing",
                    field=field
                )
            if not form_input[field] or not form_input[field].strip():
                raise ValidationError(
                    f"Required field '{field}' cannot be empty",
                    field=field
                )
        
        # Extract all fields, using empty string for missing optional fields
        extracted = {
            'data_description': form_input['data_description'].strip(),
            'update_frequency': form_input['update_frequency'].strip(),
        }
        
        # Add optional fields (default to empty string if missing)
        for field in optional_fields:
            extracted[field] = form_input.get(field, '').strip() if form_input.get(field) else ''
        
        return extracted
    
    @staticmethod
    def parse_fields(fields_text: str) -> List[str]:
        """
        Parse newline-separated field list.
        
        Args:
            fields_text: Newline-separated string of field names
            
        Returns:
            List of trimmed, non-empty field names
        """
        if not fields_text:
            return []
        
        # Split by newlines, trim whitespace, filter empty lines
        fields = [
            line.strip()
            for line in fields_text.split('\n')
            if line.strip()
        ]
        
        return fields
    
    @staticmethod
    def validate_json_structure(structure_text: str) -> Dict[str, Any]:
        """
        Validate and parse JSON structure string.
        
        Args:
            structure_text: JSON string to validate
            
        Returns:
            Parsed JSON object as dictionary
            
        Raises:
            ValidationError: If JSON is invalid
        """
        if not structure_text:
            return {}
        
        try:
            parsed = json.loads(structure_text)
            if not isinstance(parsed, dict):
                raise ValidationError(
                    "JSON structure must be an object (dictionary), not an array or primitive",
                    field='response_structure'
                )
            return parsed
        except json.JSONDecodeError as e:
            raise ValidationError(
                f"Invalid JSON structure: {str(e)}",
                field='response_structure'
            )
