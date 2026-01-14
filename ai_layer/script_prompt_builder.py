"""
Script Prompt Builder - Constructs prompts for generating scraper scripts.

This module handles building prompts that include:
- Scraping layer configuration (timeout, user-agent)
- Required libraries and imports
- Expected function signature and return format
- User requirements (URL, fields, structure)
"""

from typing import Dict, Any, List
from ai_layer.input_processor import InputProcessor
from scraping_layer.config import ScrapingConfig


class ScriptPromptBuilder:
    """Builds prompts for generating BeautifulSoup scraper scripts."""
    
    SYSTEM_PROMPT = """You are an expert Python web scraping engineer. Generate production-ready BeautifulSoup scraper scripts.

CRITICAL REQUIREMENTS:
1. Use ONLY BeautifulSoup4 (bs4) and requests libraries
2. Follow the exact function signature: def scrape_data(url: str, timeout: int = 30) -> Dict[str, Any]
3. Return data in the specified format with 'data' list and 'metadata' dict
4. Include comprehensive error handling for network and parsing errors
5. Use the provided timeout and user-agent configuration
6. Generate appropriate CSS selectors for the target website
7. Return ONLY valid Python code - NO markdown, NO code blocks, NO explanations
8. Include comments explaining the scraping logic
9. Handle cases where selectors don't match (return empty data, not errors)

DATA SOURCE INTELLIGENCE:
- If user provides URLs: Use those URLs as the primary targets (You can add others if needed)
- If NO URL provided: Based on the data description, suggest 2-3 appropriate URLs in comments
- You can include multiple URL options in the script comments for the user to choose from
- The script should work with the most common/reliable source for that data

SAFETY REQUIREMENTS:
- NO dangerous operations: exec, eval, os.system, subprocess, __import__
- NO file system operations
- NO network requests except to the specified URL using requests library
- Proper exception handling for all operations

CODE STRUCTURE:
```python
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any
from datetime import datetime

def scrape_data(url: str, timeout: int = 30) -> Dict[str, Any]:
    \"\"\"
    Scrape data from the target website.
    
    Args:
        url: Target URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with 'data' list and 'metadata' dict
    
    Suggested URLs (if not provided by user):
    - Option 1: [most reliable source]
    - Option 2: [alternative source]
    - Option 3: [backup source]
    \"\"\"
    try:
        # Configure headers with user-agent
        headers = {
            'User-Agent': '[PROVIDED_USER_AGENT]'
        }
        
        # Fetch HTML
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extract data using CSS selectors
        data = []
        
        # [YOUR SCRAPING LOGIC HERE]
        
        # Return in expected format
        return {
            'data': data,
            'metadata': {
                'total_count': len(data),
                'source_url': url,
                'scraped_at': datetime.utcnow().isoformat(),
                'update_frequency': '[PROVIDED_FREQUENCY]'
            }
        }
        
    except requests.RequestException as e:
        return {
            'data': [],
            'metadata': {
                'error': 'network_error',
                'message': f'Failed to fetch URL: {str(e)}',
                'source_url': url
            }
        }
    except Exception as e:
        return {
            'data': [],
            'metadata': {
                'error': 'scraping_error',
                'message': f'Failed to extract data: {str(e)}',
                'source_url': url
            }
        }
```

OUTPUT: Return ONLY the complete Python function code. Start with 'import' statements."""

    def __init__(self, scraping_config: ScrapingConfig):
        """
        Initialize the script prompt builder.
        
        Args:
            scraping_config: Scraping layer configuration
        """
        self.scraping_config = scraping_config
    
    def build_script_prompt(
        self,
        form_input: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Build prompt messages for script generation.
        
        Args:
            form_input: Dictionary containing:
                - data_description: str (required)
                - data_source: str (required for script generation)
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
        
        # Add data description (always required)
        user_prompt_parts.append(f"DATA TO SCRAPE: {fields['data_description']}")
        
        # Add data source handling (intelligent URL discovery)
        if fields['data_source']:
            # User provided a URL or website name
            if fields['data_source'].startswith('http://') or fields['data_source'].startswith('https://'):
                user_prompt_parts.append(f"\nTARGET URL (provided by user): {fields['data_source']}")
                user_prompt_parts.append("Use this URL as the primary target.")
            else:
                # User provided a website name, not a full URL
                user_prompt_parts.append(f"\nWEBSITE NAME (provided by user): {fields['data_source']}")
                user_prompt_parts.append("Construct the most appropriate URL for this website based on the data description.")
                user_prompt_parts.append("Include the constructed URL in the function docstring.")
        else:
            # No URL provided - AI should suggest sources
            user_prompt_parts.append(f"\nTARGET URL: Not provided by user")
            user_prompt_parts.append("IMPORTANT: Based on the data description, identify 2-3 reliable websites where this data is available.")
            user_prompt_parts.append("Include these suggested URLs in the function docstring as comments.")
            user_prompt_parts.append("Example format:")
            user_prompt_parts.append("    Suggested data sources:")
            user_prompt_parts.append("    - https://example1.com/data (most reliable)")
            user_prompt_parts.append("    - https://example2.com/data (alternative)")
            user_prompt_parts.append("Generate CSS selectors that would work for the most common/reliable source.")
        
        # Add configuration
        user_prompt_parts.append(f"\nCONFIGURATION:")
        user_prompt_parts.append(f"- Timeout: {self.scraping_config.network.request_timeout} seconds")
        user_prompt_parts.append(f"- User-Agent: {self.scraping_config.network.user_agent}")
        user_prompt_parts.append(f"- Update Frequency: {fields['update_frequency']}")
        
        # Add desired fields if provided
        if fields['desired_fields']:
            field_list = InputProcessor.parse_fields(fields['desired_fields'])
            if field_list:
                user_prompt_parts.append(f"\nREQUIRED FIELDS (include in each record):")
                for field in field_list:
                    user_prompt_parts.append(f"  - {field}")
        
        # Add structure instructions
        if fields['response_structure']:
            # Validate JSON structure
            structure = InputProcessor.validate_json_structure(fields['response_structure'])
            user_prompt_parts.append(f"\nDESIRED OUTPUT STRUCTURE:")
            user_prompt_parts.append(fields['response_structure'])
            user_prompt_parts.append("\nMatch this structure in the 'data' list. Each item should follow this format.")
        else:
            user_prompt_parts.append(f"\nOUTPUT FORMAT:")
            user_prompt_parts.append("Return dictionary with:")
            user_prompt_parts.append("  - 'data': list of extracted records (each record is a dict)")
            user_prompt_parts.append("  - 'metadata': dict with total_count, source_url, scraped_at, update_frequency")
        
        # Add scraping instructions
        user_prompt_parts.append(f"\nSCRAPING INSTRUCTIONS:")
        user_prompt_parts.append("1. Analyze the target URL structure")
        user_prompt_parts.append("2. Generate appropriate CSS selectors for the data")
        user_prompt_parts.append("3. Extract all specified fields")
        user_prompt_parts.append("4. Handle missing elements gracefully (use empty string or None)")
        user_prompt_parts.append("5. Return data in the specified format")
        
        # Add example selector patterns
        user_prompt_parts.append(f"\nCSS SELECTOR EXAMPLES:")
        user_prompt_parts.append("  - soup.select('div.item') - select all items")
        user_prompt_parts.append("  - item.select_one('h2.title').get_text(strip=True) - extract text")
        user_prompt_parts.append("  - item.select_one('a')['href'] - extract attribute")
        user_prompt_parts.append("  - item.select_one('span.price', default='N/A') - with default")
        
        # Final reminder
        user_prompt_parts.append(f"\nREMEMBER:")
        user_prompt_parts.append(f"- Use timeout={self.scraping_config.network.request_timeout} in requests.get()")
        user_prompt_parts.append(f"- Use User-Agent='{self.scraping_config.network.user_agent}' in headers")
        user_prompt_parts.append("- Return ONLY Python code, no markdown or explanations")
        user_prompt_parts.append("- Include error handling for network and parsing errors")
        user_prompt_parts.append("- Add comments explaining the scraping logic")
        
        # Construct messages
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": "\n".join(user_prompt_parts)}
        ]
        
        return messages
