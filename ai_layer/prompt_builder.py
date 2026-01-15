"""
Prompt construction for AI response generation.

This module handles building prompts from form inputs to send to the DeepSeek API.
"""

from typing import Dict, Any, List
from ai_layer.input_processor import InputProcessor


class PromptBuilder:
    """Builds prompts for the DeepSeek API from form inputs."""
    
    SYSTEM_PROMPT = """You are a high-performance API response generator.

CRITICAL REQUIREMENTS:
1. Generate all records (scale based on user request)
2. Each record MUST have 5-7 fields with diverse, realistic data
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
        """
        fields = InputProcessor.extract_form_fields(form_input)

        user_prompt_parts: List[str] = []

        user_prompt_parts.append(f"GENERATE: {fields['data_description']}")
        user_prompt_parts.append("FIELD COUNT: Each record must have 5-7 fields")
        user_prompt_parts.append("RECORD COUNT: Generate all records")
        user_prompt_parts.append(
            "RECORD COUNT: If the request is a single fact/person/current value, generate EXACTLY 1 record. "
            "Otherwise generate all records."
        )
        user_prompt_parts.append("UNIQUENESS: All records must be distinct. Do not repeat identical records.")

        if fields['data_source']:
            user_prompt_parts.append(f"DATA SOURCE: {fields['data_source']}")
            user_prompt_parts.append(
                "DATA ACCURACY: Use your most current, accurate knowledge for this domain. "
                "Generate realistic, contextually appropriate values."
            )
        else:
            user_prompt_parts.append("DATA ACCURACY: Use accurate, realistic data from your knowledge base.")

        user_prompt_parts.append(f"UPDATE FREQUENCY: {fields['update_frequency']}")

        if fields['desired_fields']:
            field_list = InputProcessor.parse_fields(fields['desired_fields'])
            if field_list:
                user_prompt_parts.append(f"REQUIRED FIELDS: {', '.join(field_list)}")

                if len(field_list) < 3:
                    user_prompt_parts.append(
                        f"ADDITIONAL FIELDS: Add {3 - len(field_list)} more relevant fields to reach 3-5 total fields per record."
                    )

                user_prompt_parts.append("Include ALL specified fields in EVERY record with appropriate data types.")
        else:
            user_prompt_parts.append("FIELDS: Generate 5-7 relevant fields per record based on the data description.")

        default_structure = (
            "STRUCTURE:\n"
            "{\n"
            '  "data": [],\n'
            '  "metadata": {\n'
            '    "total_count": 0,\n'
            f'    "update_frequency": "{fields["update_frequency"]}",\n'
            '    "last_updated": "1970-01-01T00:00:00Z",\n'
            '    "data_source": "unknown"\n'
            "  }\n"
            "}"
        )

        if fields['response_structure']:
            try:
                InputProcessor.validate_json_structure(fields['response_structure'])
                user_prompt_parts.append(f"STRUCTURE:\n{fields['response_structure']}")
                user_prompt_parts.append(
                    "Follow this structure. Ensure 5-7 fields per record. Scale data array to all records."
                )
            except Exception:
                user_prompt_parts.append(default_structure)
        else:
            user_prompt_parts.append(default_structure)

        user_prompt_parts.append("\nOPTIMIZATION:")
        user_prompt_parts.append("- Generate efficiently for fast response")
        user_prompt_parts.append("- Use accurate, realistic data from your knowledge")
        user_prompt_parts.append("- Return pure JSON immediately - no explanations")
        user_prompt_parts.append("- Ensure valid JSON syntax (proper quotes, commas, brackets)")
        user_prompt_parts.append("- Do not include comments or placeholder tokens like <...> or // ...")

        messages = [
            {"role": "system", "content": PromptBuilder.SYSTEM_PROMPT},
            {"role": "user", "content": "\n\n".join(user_prompt_parts)}
        ]

        return messages