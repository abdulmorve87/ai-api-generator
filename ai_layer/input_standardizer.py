"""
Input Standardization and Validation Module (Phase 1)

This module standardizes and validates user inputs before processing:
1. Multiple URLs - comma or newline separated
2. Response fields - newline separated list
3. JSON structure - valid JSON format

Provides clear error messages and examples for users.
"""

import json
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from ai_layer.exceptions import ValidationError


@dataclass
class StandardizedInput:
    """Container for standardized and validated inputs."""
    data_description: str
    data_sources: List[str]  # List of URLs
    desired_fields: List[str]  # List of field names
    response_structure: Dict[str, Any]  # Parsed JSON structure
    update_frequency: str
    
    # Original raw inputs for reference
    raw_data_source: str
    raw_desired_fields: str
    raw_response_structure: str


class InputStandardizer:
    """Standardizes and validates form inputs with clear error messages."""
    
    # URL validation regex
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    @staticmethod
    def get_input_examples() -> Dict[str, str]:
        """
        Get example formats for all input fields.
        
        Returns:
            Dictionary with field names as keys and example strings as values
        """
        return {
            'data_source': """Examples:
• Single URL: https://example.com/data
• Multiple URLs (comma): https://site1.com, https://site2.com
• Multiple URLs (newline):
  https://site1.com
  https://site2.com
• Leave blank to let AI find sources""",
            
            'desired_fields': """Examples:
• One per line:
  company_name
  listing_date
  issue_price
  grey_market_premium
• Or comma-separated: name, date, price""",
            
            'response_structure': """Example JSON structure:
{
  "data": [
    {
      "company_name": "string",
      "listing_date": "date",
      "issue_price": "number",
      "grey_market_premium": "number"
    }
  ],
  "metadata": {
    "total_count": "number",
    "last_updated": "timestamp"
  }
}"""
        }
    
    @staticmethod
    def standardize_urls(url_input: str) -> Tuple[List[str], List[str]]:
        """
        Parse and validate multiple URLs from user input.
        
        Supports:
        - Single URL: https://example.com
        - Comma-separated: https://site1.com, https://site2.com
        - Newline-separated:
          https://site1.com
          https://site2.com
        - Mixed whitespace and delimiters
        
        Args:
            url_input: Raw URL input string
            
        Returns:
            Tuple of (valid_urls, error_messages)
            - valid_urls: List of validated URLs
            - error_messages: List of validation errors (empty if all valid)
        """
        if not url_input or not url_input.strip():
            return [], []
        
        # Split by both commas and newlines
        raw_urls = re.split(r'[,\n]', url_input)
        
        valid_urls = []
        errors = []
        
        for i, url in enumerate(raw_urls, 1):
            url = url.strip()
            if not url:
                continue
            
            # Validate URL format
            if not InputStandardizer.URL_PATTERN.match(url):
                errors.append(f"URL #{i} is invalid: '{url}' (must start with http:// or https://)")
                continue
            
            # Check for common mistakes
            if ' ' in url:
                errors.append(f"URL #{i} contains spaces: '{url}'")
                continue
            
            valid_urls.append(url)
        
        return valid_urls, errors
    
    @staticmethod
    def standardize_fields(fields_input: str) -> Tuple[List[str], List[str]]:
        """
        Parse and validate field names from user input.
        
        Supports:
        - Newline-separated (preferred):
          field1
          field2
        - Comma-separated: field1, field2, field3
        - Mixed format
        
        Args:
            fields_input: Raw fields input string
            
        Returns:
            Tuple of (valid_fields, error_messages)
            - valid_fields: List of validated field names
            - error_messages: List of validation errors (empty if all valid)
        """
        if not fields_input or not fields_input.strip():
            return [], []
        
        # Split by both commas and newlines
        raw_fields = re.split(r'[,\n]', fields_input)
        
        valid_fields = []
        errors = []
        seen_fields = set()
        
        for i, field in enumerate(raw_fields, 1):
            field = field.strip()
            if not field:
                continue
            
            # Validate field name (alphanumeric, underscore, hyphen)
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*$', field):
                errors.append(
                    f"Field #{i} has invalid name: '{field}' "
                    "(must start with letter/underscore, contain only letters, numbers, underscores, hyphens)"
                )
                continue
            
            # Check for duplicates
            field_lower = field.lower()
            if field_lower in seen_fields:
                errors.append(f"Duplicate field: '{field}'")
                continue
            
            seen_fields.add(field_lower)
            valid_fields.append(field)
        
        return valid_fields, errors
    
    @staticmethod
    def standardize_json_structure(json_input: str) -> Tuple[Dict[str, Any], List[str]]:
        """
        Parse and validate JSON structure from user input.
        
        Args:
            json_input: Raw JSON input string
            
        Returns:
            Tuple of (parsed_json, error_messages)
            - parsed_json: Parsed JSON object (empty dict if invalid)
            - error_messages: List of validation errors (empty if valid)
        """
        if not json_input or not json_input.strip():
            return {}, []
        
        errors = []
        
        try:
            parsed = json.loads(json_input)
            
            # Validate it's a dictionary
            if not isinstance(parsed, dict):
                errors.append(
                    "JSON structure must be an object ({}), not an array ([]) or primitive value"
                )
                return {}, errors
            
            # Check for empty object
            if not parsed:
                errors.append("JSON structure is empty")
                return {}, errors
            
            return parsed, []
            
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON syntax: {str(e)}")
            errors.append("Tip: Check for missing commas, quotes, or brackets")
            return {}, errors
    
    @staticmethod
    def validate_required_fields(form_data: Dict[str, Any]) -> List[str]:
        """
        Validate that all required fields are present and non-empty.
        
        Args:
            form_data: Dictionary containing form inputs
            
        Returns:
            List of validation error messages (empty if all valid)
        """
        errors = []
        
        # Check data_description (required)
        if not form_data.get('data_description', '').strip():
            errors.append("Data description is required - please describe what data you need")
        
        # Check update_frequency (required)
        if not form_data.get('update_frequency', '').strip():
            errors.append("Update frequency is required - please select how often data should refresh")
        
        return errors
    
    @staticmethod
    def standardize_form_input(form_data: Dict[str, Any]) -> Tuple[StandardizedInput, List[str]]:
        """
        Main entry point: Standardize and validate all form inputs.
        
        Args:
            form_data: Raw form data dictionary with keys:
                - data_description (required)
                - data_source (optional)
                - desired_fields (optional)
                - response_structure (optional)
                - update_frequency (required)
        
        Returns:
            Tuple of (standardized_input, all_errors)
            - standardized_input: StandardizedInput object (may be partial if errors exist)
            - all_errors: List of all validation errors (empty if all valid)
        """
        all_errors = []
        
        # Validate required fields first
        required_errors = InputStandardizer.validate_required_fields(form_data)
        all_errors.extend(required_errors)
        
        # Extract and standardize each field
        data_description = form_data.get('data_description', '').strip()
        update_frequency = form_data.get('update_frequency', '').strip()
        
        # Standardize URLs
        raw_data_source = form_data.get('data_source', '').strip()
        data_sources, url_errors = InputStandardizer.standardize_urls(raw_data_source)
        all_errors.extend(url_errors)
        
        # Standardize fields
        raw_desired_fields = form_data.get('desired_fields', '').strip()
        desired_fields, field_errors = InputStandardizer.standardize_fields(raw_desired_fields)
        all_errors.extend(field_errors)
        
        # Standardize JSON structure
        raw_response_structure = form_data.get('response_structure', '').strip()
        response_structure, json_errors = InputStandardizer.standardize_json_structure(raw_response_structure)
        all_errors.extend(json_errors)
        
        # Create standardized input object
        standardized = StandardizedInput(
            data_description=data_description,
            data_sources=data_sources,
            desired_fields=desired_fields,
            response_structure=response_structure,
            update_frequency=update_frequency,
            raw_data_source=raw_data_source,
            raw_desired_fields=raw_desired_fields,
            raw_response_structure=raw_response_structure
        )
        
        return standardized, all_errors
    
    @staticmethod
    def format_validation_errors(errors: List[str]) -> str:
        """
        Format validation errors into a user-friendly message.
        
        Args:
            errors: List of error messages
            
        Returns:
            Formatted error string with bullet points
        """
        if not errors:
            return ""
        
        if len(errors) == 1:
            return f"❌ Validation Error:\n• {errors[0]}"
        
        error_list = "\n• ".join(errors)
        return f"❌ Found {len(errors)} validation errors:\n• {error_list}"
