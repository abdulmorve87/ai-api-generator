"""
HTML Extractor Prompt Builder - Constructs prompts for generating raw HTML extraction scripts.

This module handles building prompts that instruct the AI to generate
simple HTML extractor scripts that fetch raw HTML without any parsing or data extraction.
The extracted HTML is then passed to AI models for intelligent data extraction.
"""

from typing import Dict, Any, List
from ai_layer.input_processor import InputProcessor
from scraping_layer.config import ScrapingConfig


class HTMLExtractorPromptBuilder:
    """Builds prompts for generating raw HTML extraction scripts."""
    
    SYSTEM_PROMPT = """You are an expert Python web scraping engineer. Your task is to generate a simple, production-ready HTML extraction script.

## PURPOSE
This script fetches the RAW HTML content from URLs without any parsing or data extraction.
The raw HTML will be passed to AI models for intelligent data extraction later in the pipeline.

## CRITICAL REQUIREMENT: DEFAULT URLs

**MANDATORY**: Every generated script MUST include a DEFAULT_URLS list at the top with 3-5 PUBLIC URLs.

### URL SOURCING RULES (FOLLOW IN ORDER):

1. **USER-PROVIDED URLs ARE MANDATORY**: If the user provides data source URLs, they MUST ALL be included in DEFAULT_URLS first, regardless of how many.

2. **AI-SUGGESTED URLs**: Based on the user's data description, desired fields, and other inputs, YOU MUST find and add additional relevant URLs to reach 3-5 total URLs.

3. **URL QUALITY REQUIREMENTS** (for AI-suggested URLs only):
   - Do NOT require authentication or login
   - Do NOT have aggressive anti-scraping measures (avoid Amazon, Goodreads)
   - Are publicly accessible without API keys
   - Actually contain the requested data type

### BAD URLs TO AVOID (for AI suggestions):
- https://www.goodreads.com/* (requires login for full data)
- https://www.amazon.com/* (aggressive anti-bot)
- Any URL with /login, /signin, /account

## TECHNICAL SPECIFICATIONS

The script uses:
- **requests** library for HTTP requests
- **NO HTML parsing** - just return raw HTML text (response.text)
- **NO BeautifulSoup** - do not import or use bs4
- **NO data extraction** - do not parse or structure the HTML
- **Proper HTTP headers** to avoid 403 Forbidden errors

## CRITICAL: HTTP HEADERS FOR AVOIDING 403 ERRORS

**IMPORTANT**: Many sites (especially Wikipedia) block requests without proper headers.
ALWAYS use these headers to avoid 403 Forbidden errors:

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}
```

## FUNCTION SIGNATURE (MUST BE EXACTLY THIS)
```python
def scrape_data(url: str, timeout: int = 30) -> Dict[str, Any]:
```

## RETURN FORMAT (ALWAYS return this EXACT structure)
```python
{
    'data': [
        {
            'html': str,  # The complete raw HTML content from the page
            'source_url': str,  # The URL that was scraped
        }
    ],
    'metadata': {
        'source_url': str,
        'total_count': 1,  # Always 1 since we return one HTML document
        'scraped_at': 'ISO timestamp',
        'scraping_method': 'raw_html',
        'content_length': int,  # Length of HTML content
        'status_code': int,  # HTTP status code
        'content_type': str,  # Response content type
        'update_frequency': str,
        'error': str or None
    }
}
```

## COMPLETE CODE TEMPLATE

```python
import requests
from typing import Dict, Any, List
import datetime

# ============================================================
# DEFAULT URLs - MUST BE POPULATED WITH 3-5 URLs
# ============================================================

DEFAULT_URLS = [
    # User-provided URLs go here first (MANDATORY)
    # AI-suggested URLs to reach 3-5 total
]

# ============================================================
# MAIN SCRAPING FUNCTION - MUST BE NAMED scrape_data
# ============================================================

def scrape_data(url: str, timeout: int = 30) -> Dict[str, Any]:
    \"\"\"
    Fetch raw HTML content from a URL.
    NO parsing, NO data extraction - just fetch the complete HTML.
    
    Args:
        url: The URL to fetch HTML from
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with 'data' list and 'metadata' dict
    \"\"\"
    metadata = {
        'source_url': url,
        'total_count': 0,
        'scraped_at': datetime.datetime.utcnow().isoformat(),
        'scraping_method': 'raw_html',
        'content_length': 0,
        'status_code': None,
        'content_type': None,
        'update_frequency': '[FREQUENCY]',
        'error': None
    }
    
    # Full headers to avoid 403 Forbidden errors
    headers = {
        'User-Agent': '[USER_AGENT]',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Get the raw HTML
        html_content = response.text
        
        # Update metadata
        metadata['status_code'] = response.status_code
        metadata['content_type'] = response.headers.get('Content-Type', 'unknown')
        metadata['content_length'] = len(html_content)
        metadata['total_count'] = 1
        
        # Return raw HTML in the expected format
        return {
            'data': [
                {
                    'html': html_content,
                    'source_url': url
                }
            ],
            'metadata': metadata
        }
        
    except requests.exceptions.Timeout:
        metadata['error'] = f'Request timed out after {timeout}s'
        return {'data': [], 'metadata': metadata}
    except requests.exceptions.HTTPError as e:
        metadata['error'] = f'HTTP error: {e.response.status_code}'
        metadata['status_code'] = e.response.status_code
        return {'data': [], 'metadata': metadata}
    except requests.exceptions.RequestException as e:
        metadata['error'] = f'Network error: {str(e)}'
        return {'data': [], 'metadata': metadata}
    except Exception as e:
        metadata['error'] = f'Extraction error: {str(e)}'
        return {'data': [], 'metadata': metadata}
```

## SAFETY REQUIREMENTS
- NO exec, eval, os.system, subprocess, __import__
- NO file system operations
- Only use requests for HTTP calls
- Proper exception handling with error metadata
- NO BeautifulSoup, lxml, or any HTML parsing libraries

## OUTPUT
Return ONLY valid Python code. NO markdown, NO code blocks, NO explanations.
Start with 'import' statements."""

    def __init__(self, scraping_config: ScrapingConfig):
        """Initialize the HTML extractor prompt builder."""
        self.scraping_config = scraping_config
    
    def build_script_prompt(self, form_input: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build prompt messages for HTML extraction script generation."""
        fields = InputProcessor.extract_form_fields(form_input)
        
        user_prompt_parts = []
        
        # DATA DESCRIPTION (for context on what URLs to suggest)
        user_prompt_parts.append("=" * 60)
        user_prompt_parts.append("DATA CONTEXT (for URL suggestions)")
        user_prompt_parts.append("=" * 60)
        user_prompt_parts.append(f"\nWhat data will be extracted from the HTML: {fields['data_description']}")
        
        # DATA SOURCES
        user_prompt_parts.append("\n" + "=" * 60)
        user_prompt_parts.append("DATA SOURCES - CRITICAL URL REQUIREMENTS")
        user_prompt_parts.append("=" * 60)
        
        if fields['data_source']:
            user_prompt_parts.append("\n** USER-PROVIDED SOURCES (MANDATORY - MUST ALL BE INCLUDED) **")
            user_prompt_parts.append(f"User provided URLs/sources: {fields['data_source']}")
            user_prompt_parts.append("\n!! CRITICAL INSTRUCTIONS !!")
            user_prompt_parts.append("1. ALL user-provided URLs MUST be included in DEFAULT_URLS - no exceptions")
            user_prompt_parts.append("2. These URLs will be fetched and their raw HTML returned")
            user_prompt_parts.append("\n** AI-SUGGESTED ADDITIONAL SOURCES **")
            user_prompt_parts.append("Based on the data description above, YOU MUST find and add")
            user_prompt_parts.append("additional relevant public URLs to reach 3-5 total URLs in DEFAULT_URLS.")
        else:
            user_prompt_parts.append("\n** NO USER URLs PROVIDED - AI MUST SUGGEST 3-5 URLs **")
            user_prompt_parts.append("\nBased on the data description above,")
            user_prompt_parts.append("YOU MUST find and provide 3-5 relevant public URLs in DEFAULT_URLS.")
        
        # FIELDS (for context only - not used in extraction)
        if fields['desired_fields']:
            user_prompt_parts.append("\n" + "=" * 60)
            user_prompt_parts.append("FIELDS CONTEXT (for URL selection)")
            user_prompt_parts.append("=" * 60)
            field_list = InputProcessor.parse_fields(fields['desired_fields'])
            if field_list:
                user_prompt_parts.append("\n** Fields that will be extracted by AI from the HTML **")
                for field in field_list:
                    user_prompt_parts.append(f"  - {field}")
                user_prompt_parts.append("\nNote: This is for context only. Your script just fetches HTML.")
        
        # CONFIGURATION
        user_prompt_parts.append("\n" + "=" * 60)
        user_prompt_parts.append("CONFIGURATION VALUES")
        user_prompt_parts.append("=" * 60)
        user_prompt_parts.append(f"\nTimeout: {self.scraping_config.network.request_timeout} seconds")
        user_prompt_parts.append(f"User-Agent: {self.scraping_config.network.user_agent}")
        user_prompt_parts.append(f"Update Frequency: {fields['update_frequency']}")
        user_prompt_parts.append("\nReplace [USER_AGENT] and [FREQUENCY] placeholders with these values!")
        
        # CRITICAL REMINDERS
        user_prompt_parts.append("\n" + "=" * 60)
        user_prompt_parts.append("CRITICAL REMINDERS")
        user_prompt_parts.append("=" * 60)
        user_prompt_parts.append("\n1. Function MUST be named 'scrape_data' (not extract_html)")
        user_prompt_parts.append("2. DO NOT parse HTML - just return response.text in the data list")
        user_prompt_parts.append("3. DO NOT extract data - AI will handle that later")
        user_prompt_parts.append("4. DO NOT import BeautifulSoup or any parsing library")
        user_prompt_parts.append("5. DO include proper headers to avoid 403 errors")
        user_prompt_parts.append("6. DO handle all error cases with proper metadata")
        user_prompt_parts.append("7. DEFAULT_URLS must have 3-5 URLs total")
        user_prompt_parts.append("8. Return format: {'data': [{'html': ..., 'source_url': ...}], 'metadata': {...}}")
        
        # FINAL
        user_prompt_parts.append("\n" + "=" * 60)
        user_prompt_parts.append("GENERATE THE SCRIPT")
        user_prompt_parts.append("=" * 60)
        user_prompt_parts.append("\nGenerate a simple HTML extraction script with:")
        user_prompt_parts.append("1. DEFAULT_URLS list with 3-5 URLs total")
        user_prompt_parts.append("2. scrape_data(url, timeout) function that returns raw HTML")
        user_prompt_parts.append("3. Proper headers and timeout handling")
        user_prompt_parts.append("4. Complete error handling with metadata")
        user_prompt_parts.append("5. NO HTML parsing or data extraction")
        user_prompt_parts.append("6. Return {'data': [...], 'metadata': {...}} format")
        user_prompt_parts.append("\nReturn ONLY Python code. NO markdown, NO explanations.")
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": "\n".join(user_prompt_parts)}
        ]
        
        return messages


# Alias for backward compatibility
ScriptPromptBuilder = HTMLExtractorPromptBuilder
