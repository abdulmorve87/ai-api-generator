"""
Parsing Prompt Builder for the Scraped Data Parser.

This module provides utilities for constructing prompts that instruct
the AI to parse scraped data into structured JSON based on user requirements.
"""

import json
from typing import Dict, Any, List, Optional


# Maximum records to return to prevent excessive response sizes
MAX_RECORDS_LIMIT = 500


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
                - desired_fields: str (optional, newline/comma-separated)
                - response_structure: str (optional, JSON string)
                
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
        return f"""You are a data parser and extractor. Your task is to extract and structure data from scraped web content into clean, well-formatted JSON.

USER INPUT STANDARDS (Phase 1):
The user inputs follow these standardized formats:
- Data Description: Plain text describing what data is needed
- Important Fields: Comma or newline-separated field names (e.g., "company_name, listing_date" or one per line)
  - Field names use snake_case or kebab-case (e.g., company_name, listing-date)
  - These are the KEY fields the user wants, but you should also include other useful data
- JSON Structure: If provided, a valid JSON object template to follow EXACTLY

CRITICAL RULES:
1. Return ONLY valid JSON - no markdown, no explanations, no code blocks
2. DO NOT TRUNCATE DATA - Extract ALL records from the scraped content that match the requirements
   - If there are 24 race records, return all 24
   - If there are 50 products, return all 50
   - Maximum limit: {MAX_RECORDS_LIMIT} records (only truncate if exceeding this)
3. Preserve data types: numbers as numbers, dates as ISO strings, text as strings
4. Remove any HTML artifacts, special characters, or noise from values

FIELD HANDLING RULES:
5. Important Fields provided by user:
   - Add these as keys in the JSON response
   - If data for a field is not found, set its value to null
   - These are NOT the only fields - also include other useful/relevant data from the scraped content
   - Use the field names as keys only (ignore any example values the user may have provided)

6. JSON Structure Template (if provided by user):
   - This is STRICT MODE - follow the structure EXACTLY
   - Add ALL keys from the user's JSON template to the response
   - If no data found for a key, use null as the value
   - DO NOT add any additional keys beyond what the user specified
   - This overrides the "include other useful data" rule

OUTPUT FORMAT (when NO JSON structure template provided):
- Return a JSON object with a "data" key containing the extracted records array
- Include a "metadata" key with total_count and extraction_timestamp
- Each record should have consistent field names

EXAMPLE OUTPUT (no template):
{{
  "data": [
    {{"company_name": "ABC Corp", "listing_date": "2026-01-15", "price": 123, "sector": "Technology"}},
    {{"company_name": "XYZ Ltd", "listing_date": "2026-01-16", "price": 456, "sector": "Finance"}}
  ],
  "metadata": {{
    "total_count": 2,
    "extraction_timestamp": "2026-01-15T10:30:00Z"
  }}
}}"""
    
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
        # Extract requirements (no data_source or update_frequency - not needed for parsing)
        data_description = user_requirements.get('data_description', '')
        desired_fields_text = user_requirements.get('desired_fields', '')
        response_structure = user_requirements.get('response_structure', '')
        
        # Parse desired fields
        desired_fields = self._parse_desired_fields(desired_fields_text)
        
        # Check if user provided a JSON structure template
        validated_structure = self._validate_json_structure(response_structure)
        has_strict_structure = validated_structure is not None
        
        # Build prompt parts
        prompt_parts = []
        
        # Data description
        prompt_parts.append(f"DATA DESCRIPTION:\n{data_description}")
        
        # Important fields (if provided and no strict structure)
        if desired_fields and not has_strict_structure:
            fields_list = "\n".join(f"- {field}" for field in desired_fields)
            prompt_parts.append(f"\nIMPORTANT FIELDS (include these as keys, use null if not found, also add other useful data):\n{fields_list}")
        elif desired_fields and has_strict_structure:
            # When strict structure is provided, fields are just for reference
            fields_list = "\n".join(f"- {field}" for field in desired_fields)
            prompt_parts.append(f"\nREFERENCE FIELDS (for context only - follow the JSON structure below strictly):\n{fields_list}")
        
        # Response structure (STRICT MODE)
        if has_strict_structure:
            prompt_parts.append(f"\n⚠️ STRICT JSON STRUCTURE (follow EXACTLY - only use these keys, no additional fields):\n{json.dumps(validated_structure, indent=2)}")
        
        # Scraped data
        prompt_parts.append(f"\n\nSCRAPED DATA TO PARSE (extract ALL records, do not truncate):\n{scraped_text}")
        
        # Final instruction based on mode
        if has_strict_structure:
            prompt_parts.append("\n\nParse the above scraped data and return JSON following the EXACT structure provided. Use null for missing values. Return ONLY valid JSON, no explanations.")
        else:
            prompt_parts.append("\n\nParse the above scraped data and return a structured JSON response. Include the important fields as keys (null if not found) plus any other useful data. Return ONLY valid JSON, no explanations.")
        
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
        
        Note: data_source and update_frequency are not included as they are
        not needed for the parsing phase (already used by scraper layer).
        
        Args:
            user_requirements: Raw user requirements dictionary
            
        Returns:
            Dictionary with extracted fields for parsing
        """
        return {
            'data_description': user_requirements.get('data_description', ''),
            'desired_fields': self._parse_desired_fields(
                user_requirements.get('desired_fields', '')
            ),
            'response_structure': self._validate_json_structure(
                user_requirements.get('response_structure', '')
            )
        }
