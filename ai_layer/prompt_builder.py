"""
Prompt construction for AI response generation.

This module handles building prompts from form inputs to send to the DeepSeek API.
"""

from typing import Dict, Any, List
from ai_layer.input_processor import InputProcessor


class PromptBuilder:
    """Builds prompts for the DeepSeek API from form inputs."""
    
    SYSTEM_PROMPT = """You are an API response generator. Your task is to generate realistic, well-structured JSON API responses based on user requirements.

Guidelines:
1. Generate realistic, diverse sample data (3-5 records)
2. Follow the user's specified structure exactly, or use sensible defaults
3. Include all requested fields with appropriate data types
4. Use realistic values appropriate for the data source
5. Return ONLY valid JSON without markdown formatting, code blocks, or explanations
6. Ensure all JSON is properly formatted and parseable

Your response should be pure JSON that can be directly parsed."""
    
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
        
        # Add data description
        user_prompt_parts.append(f"Data Description: {fields['data_description']}")
        
        # Add data source if provided
        if fields['data_source']:
            user_prompt_parts.append(f"Data Source: {fields['data_source']}")
            user_prompt_parts.append("Generate realistic data appropriate for this source.")
        
        # Add update frequency context
        user_prompt_parts.append(f"Update Frequency: {fields['update_frequency']}")
        
        # Parse and add desired fields if provided
        if fields['desired_fields']:
            field_list = InputProcessor.parse_fields(fields['desired_fields'])
            if field_list:
                user_prompt_parts.append(f"Required Fields: {', '.join(field_list)}")
        
        # Add structure instructions
        if fields['response_structure']:
            # Validate JSON structure
            structure = InputProcessor.validate_json_structure(fields['response_structure'])
            user_prompt_parts.append(f"Follow this exact JSON structure:\n{fields['response_structure']}")
        else:
            # Use default structure
            user_prompt_parts.append(
                "Use this default structure:\n"
                "{\n"
                '  "data": [\n'
                "    { /* your generated records here */ }\n"
                "  ],\n"
                '  "metadata": {\n'
                '    "total_count": <number>,\n'
                f'    "update_frequency": "{fields["update_frequency"]}",\n'
                '    "last_updated": "<ISO timestamp>"\n'
                "  }\n"
                "}"
            )
        
        # Construct messages
        messages = [
            {"role": "system", "content": PromptBuilder.SYSTEM_PROMPT},
            {"role": "user", "content": "\n\n".join(user_prompt_parts)}
        ]
        
        return messages
