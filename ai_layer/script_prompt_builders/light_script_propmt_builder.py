"""
HTML Extractor Prompt Builder - Constructs prompts for generating smart HTML extraction scripts.

This module handles building prompts that instruct the AI to generate
scripts that fetch HTML and extract only the useful text content,
stripping out scripts, styles, navigation, and other noise.
The extracted content is then passed to AI models for intelligent data extraction.
"""

from typing import Dict, Any, List
from ai_layer.input_processor import InputProcessor
from scraping_layer.config import ScrapingConfig


class HTMLExtractorPromptBuilder:
    """Builds prompts for generating smart HTML content extraction scripts."""
    
    SYSTEM_PROMPT = """You are an expert Python web scraping engineer. Your task is to generate a smart, production-ready content extraction script.

## PURPOSE
This script fetches HTML from URLs and extracts ONLY the useful text content, removing all noise.
The extracted content will be passed to AI models for intelligent data extraction later.

## CRITICAL: CONTENT SIZE REDUCTION

**THE MAIN GOAL**: Extract useful text content while reducing HTML size.

### WHAT TO REMOVE (NOISE):
- All `<script>` tags and their content
- All `<style>` tags and their content  
- All `<noscript>` tags
- All `<iframe>` tags
- All `<svg>` elements

### WHAT TO KEEP (USEFUL CONTENT):
- ALL text content from the page
- Tables (`<table>`) - often contain structured data
- Lists (`<ul>`, `<ol>`) - often contain data items
- Headings (`<h1>` to `<h5>`) - provide context
- Paragraphs and divs with text
- Navigation text (might contain useful links/data)
- Footer text (might contain useful info)

**BE INCLUSIVE**: Keep more content rather than less. The AI parser can handle extra text.

## CRITICAL REQUIREMENT: DEFAULT URLs

**MANDATORY**: Every generated script MUST include a DEFAULT_URLS list at the top with 3-5 PUBLIC URLs.

### URL SOURCING RULES (FOLLOW IN ORDER):

1. **USER-PROVIDED URLs ARE MANDATORY**: If the user provides data source URLs, they MUST ALL be included in DEFAULT_URLS first.

2. **AI-SUGGESTED URLs**: Based on the user's data description, add additional relevant URLs to reach 3-5 total.

3. **URL QUALITY REQUIREMENTS**:
   - Publicly accessible without login
   - No aggressive anti-scraping (avoid Amazon, Goodreads)
   - Actually contain the requested data type

## TECHNICAL SPECIFICATIONS

The script uses:
- **requests** library for HTTP requests
- **BeautifulSoup** for HTML parsing and content extraction
- **re** for text cleaning
- Smart content extraction to reduce size

## CRITICAL: HTTP HEADERS FOR AVOIDING 403 ERRORS

ALWAYS use these COMPLETE headers:

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
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
            'content': str,  # The extracted text content (NOT raw HTML)
            'source_url': str,  # The URL that was scraped
            'tables': List[str],  # Any tables found, as text
            'lists': List[str],  # Any lists found, as text
            'headings': List[str],  # Headings for context
        }
    ],
    'metadata': {
        'source_url': str,
        'total_count': 1,
        'scraped_at': 'ISO timestamp',
        'scraping_method': 'smart_extract',
        'original_size': int,  # Original HTML size in bytes
        'extracted_size': int,  # Extracted content size in bytes
        'reduction_percent': float,  # Size reduction percentage
        'status_code': int,
        'content_type': str,
        'update_frequency': str,
        'error': str or None
    }
}
```

## COMPLETE CODE TEMPLATE

```python
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import datetime
import re

# ============================================================
# DEFAULT URLs - MUST BE POPULATED WITH 3-5 URLs
# ============================================================

DEFAULT_URLS = [
    # User-provided URLs go here first (MANDATORY)
    # AI-suggested URLs to reach 3-5 total
]

# ============================================================
# NOISE REMOVAL - MINIMAL LIST (keep more content)
# ============================================================

NOISE_TAGS = ['script', 'style', 'noscript', 'iframe', 'svg']

# ============================================================
# CONTENT EXTRACTION FUNCTIONS
# ============================================================

def clean_text(text: str) -> str:
    \"\"\"Clean and normalize text content.\"\"\"
    if not text:
        return ""
    text = re.sub(r'\\s+', ' ', text)
    lines = [line.strip() for line in text.split('\\n') if line.strip()]
    return '\\n'.join(lines)

def extract_tables(soup) -> List[str]:
    \"\"\"Extract table content as readable text.\"\"\"
    tables = []
    for table in soup.find_all('table'):
        rows = []
        for row in table.find_all('tr'):
            cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
            if any(cells):
                rows.append(' | '.join(cells))
        if rows:
            tables.append('\\n'.join(rows))
    return tables

def extract_lists(soup) -> List[str]:
    \"\"\"Extract list content as readable text.\"\"\"
    lists = []
    for lst in soup.find_all(['ul', 'ol']):
        items = [li.get_text(strip=True) for li in lst.find_all('li', recursive=False)]
        items = [item for item in items if item and len(item) > 2]
        if items:
            lists.append('\\n- '.join([''] + items))
    return lists

def extract_headings(soup) -> List[str]:
    \"\"\"Extract headings for context.\"\"\"
    headings = []
    for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
        text = h.get_text(strip=True)
        if text and len(text) > 2:
            headings.append(text)
    return headings[:30]

def extract_main_content(soup) -> str:
    \"\"\"Extract main text content from the page.\"\"\"
    # Remove only essential noise tags
    for tag in NOISE_TAGS:
        for element in soup.find_all(tag):
            element.decompose()
    
    # Try to find main content area first
    main_content = None
    for selector in ['main', 'article', '[role="main"]', '#content', '.content']:
        main_content = soup.select_one(selector)
        if main_content:
            break
    
    if main_content:
        text = main_content.get_text(separator='\\n', strip=True)
    else:
        body = soup.find('body')
        text = body.get_text(separator='\\n', strip=True) if body else soup.get_text(separator='\\n', strip=True)
    
    return clean_text(text)

# ============================================================
# MAIN SCRAPING FUNCTION - MUST BE NAMED scrape_data
# ============================================================

def scrape_data(url: str, timeout: int = 30) -> Dict[str, Any]:
    \"\"\"
    Fetch HTML and extract useful text content.
    
    Args:
        url: The URL to fetch content from
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with 'data' list and 'metadata' dict
    \"\"\"
    metadata = {
        'source_url': url,
        'total_count': 0,
        'scraped_at': datetime.datetime.utcnow().isoformat(),
        'scraping_method': 'smart_extract',
        'original_size': 0,
        'extracted_size': 0,
        'reduction_percent': 0.0,
        'status_code': None,
        'content_type': None,
        'update_frequency': '[FREQUENCY]',
        'error': None
    }
    
    headers = {
        'User-Agent': '[USER_AGENT]',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        html_content = response.text
        original_size = len(html_content)
        metadata['original_size'] = original_size
        metadata['status_code'] = response.status_code
        metadata['content_type'] = response.headers.get('Content-Type', 'unknown')
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract structured content
        tables = extract_tables(soup)
        lists = extract_lists(soup)
        headings = extract_headings(soup)
        main_content = extract_main_content(soup)
        
        # Calculate sizes
        extracted_size = len(main_content) + sum(len(t) for t in tables) + sum(len(l) for l in lists)
        
        metadata['extracted_size'] = extracted_size
        metadata['reduction_percent'] = round((1 - extracted_size / original_size) * 100, 1) if original_size > 0 else 0
        metadata['total_count'] = 1
        
        return {
            'data': [
                {
                    'content': main_content,
                    'source_url': url,
                    'tables': tables,
                    'lists': lists,
                    'headings': headings
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

## IMPORTANT NOTES

1. **Keep it simple**: Don't over-engineer the extraction. Basic text extraction works well.
2. **Handle errors gracefully**: Always return the expected format even on errors.
3. **No class/id filtering**: Don't filter elements by class or id names - this causes errors.

## SAFETY REQUIREMENTS
- NO exec, eval, os.system, subprocess, __import__
- NO file system operations
- Only use requests and BeautifulSoup
- Proper exception handling with error metadata

## OUTPUT
Return ONLY valid Python code. NO markdown, NO code blocks, NO explanations.
Start with 'import' statements."""

    def __init__(self, scraping_config: ScrapingConfig):
        """Initialize the HTML extractor prompt builder."""
        self.scraping_config = scraping_config
    
    def build_script_prompt(self, form_input: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build prompt messages for smart content extraction script generation."""
        fields = InputProcessor.extract_form_fields(form_input)
        
        user_prompt_parts = []
        
        # DATA DESCRIPTION
        user_prompt_parts.append("=" * 60)
        user_prompt_parts.append("DATA CONTEXT")
        user_prompt_parts.append("=" * 60)
        user_prompt_parts.append(f"\nWhat data to extract: {fields['data_description']}")
        
        # DATA SOURCES
        user_prompt_parts.append("\n" + "=" * 60)
        user_prompt_parts.append("DATA SOURCES")
        user_prompt_parts.append("=" * 60)
        
        if fields['data_source']:
            user_prompt_parts.append(f"\n** USER-PROVIDED URLs (MANDATORY): **")
            user_prompt_parts.append(f"{fields['data_source']}")
            user_prompt_parts.append("\nAdd more URLs to reach 3-5 total in DEFAULT_URLS.")
        else:
            user_prompt_parts.append("\n** NO USER URLs - Suggest 3-5 relevant public URLs **")
        
        # FIELDS
        if fields['desired_fields']:
            user_prompt_parts.append("\n" + "=" * 60)
            user_prompt_parts.append("FIELDS TO EXTRACT (for context)")
            user_prompt_parts.append("=" * 60)
            field_list = InputProcessor.parse_fields(fields['desired_fields'])
            if field_list:
                for field in field_list:
                    user_prompt_parts.append(f"  - {field}")
        
        # CONFIGURATION
        user_prompt_parts.append("\n" + "=" * 60)
        user_prompt_parts.append("CONFIGURATION")
        user_prompt_parts.append("=" * 60)
        user_prompt_parts.append(f"\nTimeout: {self.scraping_config.network.request_timeout} seconds")
        user_prompt_parts.append(f"User-Agent: {self.scraping_config.network.user_agent}")
        user_prompt_parts.append(f"Update Frequency: {fields['update_frequency']}")
        user_prompt_parts.append("\nReplace [USER_AGENT] and [FREQUENCY] placeholders!")
        
        # CRITICAL REMINDERS
        user_prompt_parts.append("\n" + "=" * 60)
        user_prompt_parts.append("CRITICAL REQUIREMENTS")
        user_prompt_parts.append("=" * 60)
        user_prompt_parts.append("\n1. Function MUST be named 'scrape_data'")
        user_prompt_parts.append("2. Remove only: script, style, noscript, iframe, svg tags")
        user_prompt_parts.append("3. Keep ALL text content - don't filter by class/id")
        user_prompt_parts.append("4. Extract tables, lists, and headings separately")
        user_prompt_parts.append("5. Return {'data': [...], 'metadata': {...}} format")
        user_prompt_parts.append("6. Handle all errors gracefully")
        
        user_prompt_parts.append("\n" + "=" * 60)
        user_prompt_parts.append("GENERATE THE SCRIPT")
        user_prompt_parts.append("=" * 60)
        user_prompt_parts.append("\nReturn ONLY Python code. NO markdown, NO explanations.")
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": "\n".join(user_prompt_parts)}
        ]
        
        return messages


# Alias for backward compatibility
ScriptPromptBuilder = HTMLExtractorPromptBuilder
