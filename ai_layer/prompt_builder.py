"""
Prompt construction for AI response generation.

This module handles building prompts from form inputs to send to the DeepSeek API.
"""

from typing import Dict, Any, List
from ai_layer.input_processor import InputProcessor


class PromptBuilder:
    """Builds prompts for the DeepSeek API from form inputs."""
    
    SYSTEM_PROMPT = """You are a high-performance API response generator. Generate large, realistic JSON datasets with 10-15 fields per record.

CRITICAL REQUIREMENTS:
1. Generate 50-100 records minimum (scale based on user request)
2. Each record MUST have 10-15 fields with diverse, realistic data
3. Return ONLY valid, parseable JSON - NO markdown, NO code blocks, NO text
4. Use your most current and accurate knowledge for realistic data
5. Optimize for speed - generate efficiently without unnecessary processing
6. Follow exact structure provided or use intelligent defaults
7. Ensure proper data types: strings, numbers, dates (ISO 8601), booleans, arrays
8. Use diverse, contextually appropriate values

PERFORMANCE: Generate quickly. Output pure JSON immediately. Start with { and end with }."""
    
    @staticmethod
    def build_prompt(form_input: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Construct prompt messages for DeepSeek API from form inputs.
        
        Args:
            form_input: Dictionary containing:
                - data_description: str (required)
                - data_source: str (optional)
                - desired_fields: str (optional, newline-separated)
                - response_structure: str (optional, JSON string)
                - update_frequency: str (required)
                
        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        # Extract and validate fields
        fields = InputProcessor.extract_form_fields(form_input)
        
        # Build user prompt
        user_prompt_parts = []
        
        # Add data description with emphasis on field count
        user_prompt_parts.append(f"GENERATE: {fields['data_description']}")
        user_prompt_parts.append("FIELD COUNT: Each record must have 10-15 fields minimum")
        
        # Add explicit record count instruction
        user_prompt_parts.append("RECORD COUNT: Generate 50-100 records (or quantity specified in description)")
        
        # Add data source with accuracy emphasis
        if fields['data_source']:
            user_prompt_parts.append(f"DATA SOURCE: {fields['data_source']}")
            user_prompt_parts.append("DATA ACCURACY: Use your most current, accurate knowledge for this domain. Generate realistic, contextually appropriate values.")
        else:
            user_prompt_parts.append("DATA ACCURACY: Use accurate, realistic data from your knowledge base.")
        
        # Add update frequency context
        user_prompt_parts.append(f"UPDATE FREQUENCY: {fields['update_frequency']}")
        
        # Parse and add desired fields if provided
        if fields['desired_fields']:
            field_list = InputProcessor.parse_fields(fields['desired_fields'])
            if field_list:
                user_prompt_parts.append(f"REQUIRED FIELDS: {', '.join(field_list)}")
                
                # If fewer than 10 fields specified, add instruction to include more
                if len(field_list) < 10:
                    user_prompt_parts.append(f"ADDITIONAL FIELDS: Add {10 - len(field_list)} more relevant fields to reach 10-15 total fields per record.")
                
                user_prompt_parts.append("Include ALL specified fields in EVERY record with appropriate data types.")
        else:
            user_prompt_parts.append("FIELDS: Generate 10-15 relevant fields per record based on the data description.")
        
        # Add structure instructions
        if fields['response_structure']:
            # Validate JSON structure
            structure = InputProcessor.validate_json_structure(fields['response_structure'])
            user_prompt_parts.append(f"STRUCTURE:\n{fields['response_structure']}")
            user_prompt_parts.append("Follow this structure. Ensure 10-15 fields per record. Scale data array to 50-100+ records.")
        else:
            # Use default structure with emphasis on field count
            user_prompt_parts.append(
                "STRUCTURE:\n"
                "{\n"
                '  "data": [\n'
                "    // 50-100+ records, each with 10-15 fields\n"
                "  ],\n"
                '  "metadata": {\n'
                '    "total_count": <actual_record_count>,\n'
                '    "fields_per_record": <actual_field_count>,\n'
                f'    "update_frequency": "{fields["update_frequency"]}",\n'
                '    "last_updated": "<ISO_8601_timestamp>",\n'
                '    "data_source": "<source_name>"\n'
                "  }\n"
                "}"
            )
        
        # Add performance and accuracy optimization
        user_prompt_parts.append("\nOPTIMIZATION:")
        user_prompt_parts.append("- Generate efficiently for fast response")
        user_prompt_parts.append("- Use accurate, realistic data from your knowledge")
        user_prompt_parts.append("- Return pure JSON immediately - no explanations")
        user_prompt_parts.append("- Ensure valid JSON syntax (proper quotes, commas, brackets)")
        
        # Construct messages
        messages = [
            {"role": "system", "content": PromptBuilder.SYSTEM_PROMPT},
            {"role": "user", "content": "\n\n".join(user_prompt_parts)}
        ]
        
        return messages
