"""
Parsing Response Validator for the Scraped Data Parser.

This module provides utilities for validating AI-parsed responses
to ensure they meet user requirements and contain valid JSON.
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple

from ai_layer.parsing_models import ParsingError
from ai_layer.exceptions import ValidationError


class ParsingValidator:
    """Validates parsed data responses from AI."""
    
    def validate_parsed_response(
        self,
        ai_output: str,
        user_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate AI-parsed response meets requirements.
        
        Args:
            ai_output: Raw AI response string
            user_requirements: User's requirements
            
        Returns:
            Validated and parsed JSON object
            
        Raises:
            ParsingError: When validation fails
        """
        # Step 1: Extract and validate JSON
        try:
            parsed_data = self._validate_json(ai_output)
        except ParsingError as e:
            # Try to extract JSON from mixed text
            extracted = self._extract_json_from_text(ai_output)
            if extracted:
                try:
                    parsed_data = self._validate_json(extracted)
                except ParsingError:
                    raise e
            else:
                raise e
        
        # Step 2: Validate required fields if specified
        desired_fields_text = user_requirements.get('desired_fields', '')
        if desired_fields_text:
            desired_fields = self._parse_field_list(desired_fields_text)
            missing_fields = self._validate_required_fields(parsed_data, desired_fields)
            if missing_fields:
                # Add missing fields as null rather than failing
                parsed_data = self._add_missing_fields(parsed_data, missing_fields)
        
        # Step 3: Validate structure if specified
        response_structure = user_requirements.get('response_structure', '')
        if response_structure:
            try:
                expected_structure = json.loads(response_structure)
                self._validate_data_structure(parsed_data, expected_structure)
            except json.JSONDecodeError:
                pass  # Invalid structure template, skip validation
        
        return parsed_data
    
    def _validate_json(self, text: str) -> Dict[str, Any]:
        """
        Validate and parse JSON string.
        
        Args:
            text: String to parse as JSON
            
        Returns:
            Parsed JSON object
            
        Raises:
            ParsingError: When JSON is invalid
        """
        if not text or not text.strip():
            raise ParsingError(
                "AI returned empty response",
                details="The AI did not return any content"
            )
        
        try:
            data = json.loads(text)
            if not isinstance(data, dict):
                # Wrap non-dict responses
                data = {"data": data}
            return data
        except json.JSONDecodeError as e:
            raise ParsingError(
                f"Invalid JSON in AI response: {str(e)}",
                details=f"JSON parse error at position {e.pos}: {e.msg}"
            )
    
    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """
        Extract JSON from markdown code blocks or mixed text.
        
        Args:
            text: Text that may contain JSON
            
        Returns:
            Extracted JSON string or None
        """
        if not text:
            return None
        
        # Try to find JSON in markdown code blocks
        patterns = [
            r'```json\s*([\s\S]*?)\s*```',  # ```json ... ```
            r'```\s*([\s\S]*?)\s*```',       # ``` ... ```
            r'\{[\s\S]*\}',                   # Raw JSON object
            r'\[[\s\S]*\]',                   # Raw JSON array
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                candidate = match.strip() if isinstance(match, str) else match
                try:
                    json.loads(candidate)
                    return candidate
                except json.JSONDecodeError:
                    continue
        
        # Try to find JSON by looking for { and }
        start = text.find('{')
        if start != -1:
            # Find matching closing brace
            depth = 0
            for i, char in enumerate(text[start:], start):
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        candidate = text[start:i+1]
                        try:
                            json.loads(candidate)
                            return candidate
                        except json.JSONDecodeError:
                            break
        
        return None
    
    def _parse_field_list(self, fields_text: str) -> List[str]:
        """
        Parse comma or newline-separated field list.
        
        Args:
            fields_text: Comma or newline-separated field names
            
        Returns:
            List of field names
        """
        if not fields_text:
            return []
        
        # Split by both commas and newlines to handle both formats
        fields = re.split(r'[,\n]', fields_text)
        return [f.strip() for f in fields if f.strip()]
    
    def _validate_required_fields(
        self,
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> List[str]:
        """
        Check if required fields are present in the data.
        
        Args:
            data: Parsed data dictionary
            required_fields: List of required field names
            
        Returns:
            List of missing field names
        """
        if not required_fields:
            return []
        
        # Get all fields from the data (including nested in 'data' key)
        present_fields = set()
        
        def collect_fields(obj, prefix=''):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    full_key = f"{prefix}.{key}" if prefix else key
                    present_fields.add(key)
                    present_fields.add(full_key)
                    collect_fields(value, full_key)
            elif isinstance(obj, list) and obj:
                for item in obj[:5]:  # Check first 5 items
                    collect_fields(item, prefix)
        
        collect_fields(data)
        
        # Check for missing fields
        missing = []
        for field in required_fields:
            field_lower = field.lower()
            # Check if field exists (case-insensitive)
            if not any(f.lower() == field_lower for f in present_fields):
                missing.append(field)
        
        return missing
    
    def _add_missing_fields(
        self,
        data: Dict[str, Any],
        missing_fields: List[str]
    ) -> Dict[str, Any]:
        """
        Add missing fields as null to the data.
        
        Args:
            data: Parsed data dictionary
            missing_fields: List of missing field names
            
        Returns:
            Data with missing fields added as null
        """
        # If data has a 'data' key with a list, add to each record
        if 'data' in data and isinstance(data['data'], list):
            for record in data['data']:
                if isinstance(record, dict):
                    for field in missing_fields:
                        if field not in record:
                            record[field] = None
        else:
            # Add to top level
            for field in missing_fields:
                if field not in data:
                    data[field] = None
        
        return data
    
    def _validate_data_structure(
        self,
        data: Dict[str, Any],
        expected_structure: Dict[str, Any]
    ) -> bool:
        """
        Validate data follows expected structure.
        
        Args:
            data: Parsed data dictionary
            expected_structure: Expected structure template
            
        Returns:
            True if structure matches
            
        Raises:
            ValidationError: When structure doesn't match
        """
        def check_structure(actual, expected, path=''):
            if isinstance(expected, dict):
                if not isinstance(actual, dict):
                    raise ValidationError(
                        f"Expected object at {path or 'root'}, got {type(actual).__name__}",
                        field=path
                    )
                for key in expected:
                    if key not in actual:
                        # Missing key is okay, we'll add it as null
                        continue
                    check_structure(
                        actual[key],
                        expected[key],
                        f"{path}.{key}" if path else key
                    )
            elif isinstance(expected, list) and expected:
                if not isinstance(actual, list):
                    raise ValidationError(
                        f"Expected array at {path or 'root'}, got {type(actual).__name__}",
                        field=path
                    )
                if actual:
                    check_structure(actual[0], expected[0], f"{path}[0]")
        
        check_structure(data, expected_structure)
        return True
    
    def generate_error_message(
        self,
        ai_output: str,
        error: Exception
    ) -> str:
        """
        Generate a clear error message for parsing failures.
        
        Args:
            ai_output: The AI output that failed to parse
            error: The exception that occurred
            
        Returns:
            User-friendly error message
        """
        if isinstance(error, ParsingError):
            base_msg = str(error)
            if error.details:
                base_msg += f"\nDetails: {error.details}"
        else:
            base_msg = str(error)
        
        # Add context about the AI output
        if ai_output:
            preview = ai_output[:200] + "..." if len(ai_output) > 200 else ai_output
            base_msg += f"\n\nAI Output Preview:\n{preview}"
        
        return base_msg
