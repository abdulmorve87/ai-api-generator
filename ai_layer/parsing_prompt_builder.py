"""
Parsing Prompt Builder for the Scraped Data Parser.

This module provides utilities for constructing prompts that instruct
the AI to parse scraped data into structured JSON based on user requirements.
"""

import json
from typing import Dict, Any, List, Optional


class ParsingPromptBuilder:
    """Builds prompts for parsing scraped data into structured JSON."""
    
    def build_parsing_prompt(
        self,
        scraped_text: str,
        user_requirements: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Build prompt messages for data parsing.
        
        Args:
            scraped_text: Extracted text from scraped data
            user_requirements: User's requirements containing:
                - data_description: str
                - data_source: str (optional)
                - desired_fields: str (optional, newline-separated)
                - response_structure: str (optional, JSON string)
                - update_frequency: str
                
        Returns:
            List of message dicts for DeepSeek API
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(scraped_text, user_requirements)
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def _build_system_prompt(self) -> str:
        """
        Build system prompt for data parsing.
        
        Returns:
            System prompt instructing AI on parsing task
        """
        return """You are a data parser and extractor. Your task is to extract and structure data from scraped web content into clean, well-formatted JSON.

CRITICAL RULES:
1. Return ONLY valid JSON - no markdown, no explanations, no code blocks
2. Extract ALL relevant data records from the provided content
3. Map extracted data to the user-specified fields
4. If a requested field is not found in the data, use null
5. Preserve data types: numbers as numbers, dates as ISO strings, text as strings
6. Remove any HTML artifacts, special characters, or noise from values
7. If the data contains multiple records, return them as an array
8. Follow the user's specified structure exactly if provided
9. If no structure is provided, use a sensible default with a "data" array

OUTPUT FORMAT:
- Return a JSON object with a "data" key containing the extracted records
- Include a "metadata" key with total_count and extraction_timestamp
- Each record should have consistent field names

EXAMPLE OUTPUT:
{
  "data": [
    {"field1": "value1", "field2": 123, "field3": null},
    {"field1": "value2", "field2": 456, "field3": "available"}
  ],
  "metadata": {
    "total_count": 2,
    "extraction_timestamp": "2026-01-15T10:30:00Z"
  }
}"""
    
    def _build_user_prompt(
        self,
        scraped_text: str,
        user_requirements: Dict[str, Any]
    ) -> str:
        """
        Build user prompt with scraped data and requirements.
        
        Args:
            scraped_text: Extracted text from scraped data
            user_requirements: User's requirements
            
        Returns:
            User prompt string
        """
        # Extract requirements
        data_description = user_requirements.get('data_description', '')
        data_source = user_requirements.get('data_source', '')
        desired_fields_text = user_requirements.get('desired_fields', '')
        response_structure = user_requirements.get('response_structure', '')
        update_frequency = user_requirements.get('update_frequency', 'Daily')
        
        # Parse desired fields
        desired_fields = self._parse_desired_fields(desired_fields_text)
        
        # Build prompt parts
        prompt_parts = []
        
        # Data description
        prompt_parts.append(f"DATA DESCRIPTION:\n{data_description}")
        
        # Data source (if provided)
        if data_source:
            prompt_parts.append(f"\nDATA SOURCE:\n{data_source}")
        
        # Desired fields
        if desired_fields:
            fields_list = "\n".join(f"- {field}" for field in desired_fields)
            prompt_parts.append(f"\nREQUIRED FIELDS (extract these from the data):\n{fields_list}")
        else:
            prompt_parts.append("\nREQUIRED FIELDS:\nExtract all relevant fields from the data.")
        
        # Response structure
        if response_structure:
            validated_structure = self._validate_json_structure(response_structure)
            if validated_structure:
                prompt_parts.append(f"\nOUTPUT STRUCTURE (follow this format):\n{json.dumps(validated_structure, indent=2)}")
        
        # Update frequency context
        prompt_parts.append(f"\nUPDATE FREQUENCY: {update_frequency}")
        
        # Scraped data
        prompt_parts.append(f"\n\nSCRAPED DATA TO PARSE:\n{scraped_text}")
        
        # Final instruction
        prompt_parts.append("\n\nParse the above scraped data and return a structured JSON response with the requested fields. Return ONLY valid JSON, no explanations.")
        
        return "\n".join(prompt_parts)
    
    def _parse_desired_fields(self, fields_text: str) -> List[str]:
        """
        Parse newline-separated field list.
        
        Args:
            fields_text: Newline-separated field names
            
        Returns:
            List of trimmed, non-empty field names
        """
        if not fields_text:
            return []
        
        fields = []
        for line in fields_text.split('\n'):
            field = line.strip()
            if field:
                fields.append(field)
        
        return fields
    
    def _validate_json_structure(self, structure_text: str) -> Optional[Dict[str, Any]]:
        """
        Validate and parse JSON structure template.
        
        Args:
            structure_text: JSON structure string
            
        Returns:
            Parsed JSON object or None if invalid
        """
        if not structure_text or not structure_text.strip():
            return None
        
        try:
            return json.loads(structure_text)
        except json.JSONDecodeError:
            # Try to fix common issues
            cleaned = structure_text.strip()
            
            # Remove markdown code block markers
            if cleaned.startswith('```'):
                lines = cleaned.split('\n')
                lines = [l for l in lines if not l.strip().startswith('```')]
                cleaned = '\n'.join(lines)
            
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                return None
    
    def extract_requirements_fields(
        self,
        user_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract and validate all fields from user requirements.
        
        Args:
            user_requirements: Raw user requirements dictionary
            
        Returns:
            Dictionary with extracted fields
        """
        return {
            'data_description': user_requirements.get('data_description', ''),
            'data_source': user_requirements.get('data_source', ''),
            'desired_fields': self._parse_desired_fields(
                user_requirements.get('desired_fields', '')
            ),
            'response_structure': self._validate_json_structure(
                user_requirements.get('response_structure', '')
            ),
            'update_frequency': user_requirements.get('update_frequency', 'Daily')
        }
