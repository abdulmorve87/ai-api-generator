"""
Script Prompt Builder - Constructs prompts for generating scraper scripts.

This module handles building prompts that instruct the AI to generate
scraper scripts compatible with the scraping_layer implementation.
"""

from typing import Dict, Any, List
from ai_layer.input_processor import InputProcessor
from scraping_layer.config import ScrapingConfig


class ScriptPromptBuilder:
    """Builds prompts for generating BeautifulSoup scraper scripts."""
    
    SYSTEM_PROMPT = """You are an expert Python web scraping engineer. Your task is to generate production-ready, flexible scraper scripts that work as a reusable scraper framework (Platform Core).

## CRITICAL REQUIREMENT: DEFAULT URLs

**MANDATORY**: Every generated script MUST include a DEFAULT_URLS list at the top with 3-5 PUBLIC URLs.

### URL SOURCING RULES (FOLLOW IN ORDER):

1. **USER-PROVIDED URLs ARE MANDATORY**: If the user provides data source URLs, they MUST ALL be included in DEFAULT_URLS first, regardless of how many.

2. **AI-SUGGESTED URLs**: Based on the user's data description, desired fields, and other inputs, YOU MUST find and add additional relevant URLs to reach 3-5 total URLs. Use your knowledge to identify:
   - Official websites related to the data topic
   - Public databases and open data portals
   - Wikipedia pages with relevant data
   - Government or institutional sites
   - Community/fan sites with public data

3. **URL QUALITY REQUIREMENTS** (for AI-suggested URLs only):
   - Do NOT require authentication or login
   - Do NOT have aggressive anti-scraping measures (avoid Amazon, Goodreads)
   - Are publicly accessible without API keys
   - Actually contain the requested data type

### EXAMPLES:

**User wants**: "Formula 1 race schedule"
**User provides**: "https://www.formula1.com/en/racing/2024"
**DEFAULT_URLS should include**:
```python
DEFAULT_URLS = [
    'https://www.formula1.com/en/racing/2024',  # User-provided (MANDATORY)
    'https://en.wikipedia.org/wiki/2024_Formula_One_World_Championship',  # AI-suggested
    'https://www.motorsport.com/f1/schedule/',  # AI-suggested
    'https://www.espn.com/f1/schedule',  # AI-suggested
]
```

**User wants**: "Books by George R.R. Martin"
**User provides**: NO URLs
**DEFAULT_URLS should include**:
```python
DEFAULT_URLS = [
    'https://www.georgerrmartin.com/book-category/',  # AI-suggested (official site)
    'https://openlibrary.org/authors/OL2856508A/George_R._R._Martin',  # AI-suggested
    'https://en.wikipedia.org/wiki/George_R._R._Martin_bibliography',  # AI-suggested
    'https://www.isfdb.org/cgi-bin/ea.cgi?27',  # AI-suggested (SciFi database)
]
```

### BAD URLs TO AVOID (for AI suggestions):
- https://www.goodreads.com/* (requires login for full data)
- https://www.amazon.com/* (aggressive anti-bot)
- Any URL with /login, /signin, /account

**FORMAT**: Add this at the top of the script after imports:
```python
# Default URLs for scraping (public, no-auth required)
# User-provided URLs are listed first, followed by AI-suggested URLs
DEFAULT_URLS = [
    'https://user-provided-url.com/data',  # User-provided
    'https://ai-suggested-url.com/info',   # AI-suggested based on data requirements
    # ... 3-5 total URLs
]
```

## SCRAPING LAYER SPECIFICATIONS

Our scraping layer uses:
- **BeautifulSoup4** (bs4) for HTML parsing with 'lxml' parser
- **requests** library for HTTP requests
- Parser: 'lxml' (NOT 'html.parser')

## ARCHITECTURE REQUIREMENTS

### Design Philosophy
- Generate a **scraper framework**, NOT a hard-coded scraper
- Script should work with ANY URL passed to it
- Use **dynamic URL-pattern detection** to choose scraping strategy
- Include **robust CSS selectors with fallbacks**
- Return **RAW, UNFILTERED data** - NO filtering, NO confidence scoring, NO deduplication
- Extract ALL data found - the pipeline will handle processing later
- Return **error metadata** for debugging

### Function Signature
```python
def scrape_data(url: str, timeout: int = 30) -> Dict[str, Any]:
```

### Return Format (ALWAYS return this structure)
```python
{
    'data': [
        {'field1': 'value1', 'field2': 'value2', ...},  # RAW extracted data, no filtering
    ],
    'metadata': {
        'source_url': str,
        'total_count': int,  # Total records extracted (no filtering applied)
        'scraped_at': 'ISO timestamp',
        'scraping_method': str,  # 'table', 'cards', 'generic'
        'update_frequency': str,
        'error': str or None
    }
}
```

## CODE TEMPLATE (PLATFORM CORE)

```python
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import datetime

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_text_safe(element, default: str = '') -> str:
    \"\"\"Safely extract text from an element.\"\"\"
    if element is None:
        return default
    return element.get_text(strip=True) or default

def get_attr_safe(element, attr: str, default: str = '') -> str:
    \"\"\"Safely extract attribute from an element.\"\"\"
    if element is None:
        return default
    return element.get(attr, default) or default

# ============================================================
# STRATEGY DETECTION
# ============================================================

def detect_scraping_strategy(soup: BeautifulSoup, url: str) -> str:
    \"\"\"
    Detect the best scraping strategy based on page structure.
    Returns strategy name.
    
    Priority: table > cards > articles > generic
    \"\"\"
    has_table = bool(soup.select('table[class*="data"], table[class*="schedule"], table[class*="result"], table.results, table tbody tr'))
    has_cards = bool(soup.select('[class*="card"], [class*="item"], [class*="list-item"]'))
    has_articles = bool(soup.select('article, [class*="event"], [class*="entry"]'))
    
    # Prefer table if it exists (most structured)
    if has_table:
        return 'table'
    
    # Cards are second preference
    if has_cards:
        return 'cards'
    
    # Articles third
    if has_articles:
        return 'articles'
    
    # Generic fallback
    return 'generic'

# ============================================================
# SCRAPING STRATEGIES - RAW DATA EXTRACTION
# ============================================================

def scrape_table_data(soup: BeautifulSoup, required_fields: List[str]) -> List[Dict[str, Any]]:
    \"\"\"Extract ALL data from HTML tables - no filtering.\"\"\"
    data = []
    tables = soup.select('table[class*="data"], table[class*="schedule"], table[class*="result"], table.results, table')
    
    for table in tables:
        # Get headers
        headers = [th.get_text(strip=True).lower().replace(' ', '_').replace('-', '_') 
                   for th in table.select('th')]
        
        if not headers:
            # Try first row as headers
            first_row = table.select_one('tr')
            if first_row:
                headers = [td.get_text(strip=True).lower().replace(' ', '_').replace('-', '_') 
                          for td in first_row.select('td, th')]
        
        # Get data rows
        rows = table.select('tbody tr') or table.select('tr')[1:]
        
        for row in rows:
            cells = row.select('td')
            if cells:
                record = {}
                for i, cell in enumerate(cells):
                    if i < len(headers) and headers[i]:
                        record[headers[i]] = get_text_safe(cell)
                    # Also try to get link from cell
                    link = cell.select_one('a')
                    if link and 'link' not in record:
                        record['link'] = get_attr_safe(link, 'href')
                
                # Extract ALL data - no filtering
                if record:  # Add any record with data
                    data.append(record)
    
    return data

def scrape_card_data(soup: BeautifulSoup, required_fields: List[str]) -> List[Dict[str, Any]]:
    \"\"\"Extract ALL data from card/item layouts - no filtering.\"\"\"
    data = []
    cards = soup.select('[class*="card"], [class*="item"]:not(nav *):not(header *):not(footer *), [class*="list-item"], article')
    
    for card in cards:
        record = {}
        
        # Extract all possible fields
        record['title'] = get_text_safe(
            card.select_one('h1, h2, h3, h4, [class*="title"], [class*="name"], [class*="heading"]')
        )
        
        record['description'] = get_text_safe(
            card.select_one('p:not([class*="date"]), [class*="desc"], [class*="summary"], [class*="content"], [class*="text"]')
        )
        
        date_elem = card.select_one('[class*="date"], time, [datetime], [class*="time"]')
        record['date'] = get_text_safe(date_elem) or get_attr_safe(date_elem, 'datetime')
        
        link_elem = card.select_one('a[href]')
        record['link'] = get_attr_safe(link_elem, 'href')
        
        record['location'] = get_text_safe(
            card.select_one('[class*="location"], [class*="venue"], [class*="place"], [class*="circuit"]')
        )
        
        # Add ALL records - no filtering
        if record:
            data.append(record)
    
    return data

def scrape_generic(soup: BeautifulSoup, required_fields: List[str]) -> List[Dict[str, Any]]:
    \"\"\"Generic fallback scraper - extract ALL data found.\"\"\"
    data = []
    
    # Try to find any repeating content blocks
    containers = soup.select(
        'main, article, .content, #content, [class*="main"], '
        '[class*="calendar"], [class*="schedule"], [class*="event"], '
        '[class*="list"], [class*="results"], [class*="entries"]'
    )
    
    if not containers:
        containers = [soup.body] if soup.body else [soup]
    
    for container in containers:
        items = container.select(
            '[class*="item"]:not(nav *):not(header *):not(footer *), '
            '[class*="entry"], [class*="row"]:not(nav *), '
            '[class*="event"], [class*="card"], '
            'li:not(nav li):not(footer li)'
        )
        
        for item in items:
            record = {}
            record['title'] = get_text_safe(item.select_one('h1, h2, h3, h4, a, [class*="title"]'))
            record['description'] = get_text_safe(item.select_one('p, [class*="desc"], span:not([class*="date"])'))
            record['date'] = get_text_safe(item.select_one('[class*="date"], time'))
            record['link'] = get_attr_safe(item.select_one('a'), 'href')
            
            # Add ALL records - no filtering
            if record:
                data.append(record)
    
    return data

# ============================================================
# MAIN SCRAPING FUNCTION
# ============================================================

def scrape_data(url: str, timeout: int = 30) -> Dict[str, Any]:
    \"\"\"
    Scrape RAW data from a URL using adaptive strategy detection.
    NO FILTERING - Extract everything found. Processing happens later in pipeline.
    
    Args:
        url: The URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with 'data' list and 'metadata' dict
    \"\"\"
    metadata = {
        'source_url': url,
        'total_count': 0,
        'scraped_at': datetime.datetime.utcnow().isoformat(),
        'scraping_method': 'unknown',
        'update_frequency': '[FREQUENCY]',
        'error': None
    }
    
    headers = {
        'User-Agent': '[USER_AGENT]'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Detect best scraping strategy
        strategy = detect_scraping_strategy(soup, url)
        metadata['scraping_method'] = strategy
        
        # Required fields from user (customize extraction)
        required_fields = []  # Will be populated based on user input
        
        # Apply appropriate scraping strategy
        if strategy == 'table':
            data = scrape_table_data(soup, required_fields)
        elif strategy in ('cards', 'articles'):
            data = scrape_card_data(soup, required_fields)
        else:
            data = scrape_generic(soup, required_fields)
        
        # NO FILTERING - Return ALL extracted data
        metadata['total_count'] = len(data)
        
        return {'data': data, 'metadata': metadata}
        
    except requests.exceptions.Timeout:
        metadata['error'] = f'Request timed out after {timeout}s'
        return {'data': [], 'metadata': metadata}
    except requests.exceptions.HTTPError as e:
        metadata['error'] = f'HTTP error: {e.response.status_code}'
        return {'data': [], 'metadata': metadata}
    except requests.exceptions.RequestException as e:
        metadata['error'] = f'Network error: {str(e)}'
        return {'data': [], 'metadata': metadata}
    except Exception as e:
        metadata['error'] = f'Scraping error: {str(e)}'
        return {'data': [], 'metadata': metadata}
```

## CUSTOMIZATION INSTRUCTIONS

Based on user requirements, you should:

1. **Customize selectors** - Add domain-specific CSS selectors for known sites
2. **Customize field extraction** - Map to user's exact field names
3. **Extract ALL data** - Do not filter, trim, or validate data quality

## SAFETY REQUIREMENTS
- NO exec, eval, os.system, subprocess, __import__
- NO file system operations
- Only use requests for HTTP calls
- Proper exception handling with error metadata

## OUTPUT
Return ONLY valid Python code. NO markdown, NO code blocks, NO explanations.
Start with 'import' statements."""

    def __init__(self, scraping_config: ScrapingConfig):
        """Initialize the script prompt builder."""
        self.scraping_config = scraping_config
    
    def build_script_prompt(self, form_input: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build prompt messages for script generation."""
        fields = InputProcessor.extract_form_fields(form_input)
        
        user_prompt_parts = []
        
        # DATA DESCRIPTION
        user_prompt_parts.append("=" * 60)
        user_prompt_parts.append("DATA REQUIREMENTS")
        user_prompt_parts.append("=" * 60)
        user_prompt_parts.append(f"\nWhat to scrape: {fields['data_description']}")
        
        # DATA SOURCES
        user_prompt_parts.append("\n" + "=" * 60)
        user_prompt_parts.append("DATA SOURCES - CRITICAL URL REQUIREMENTS")
        user_prompt_parts.append("=" * 60)
        
        if fields['data_source']:
            user_prompt_parts.append("\n** USER-PROVIDED SOURCES (MANDATORY - MUST ALL BE INCLUDED) **")
            user_prompt_parts.append(f"User provided URLs/sources: {fields['data_source']}")
            user_prompt_parts.append("\n!! CRITICAL INSTRUCTIONS !!")
            user_prompt_parts.append("1. ALL user-provided URLs MUST be included in DEFAULT_URLS - no exceptions")
            user_prompt_parts.append("2. Add domain-specific selector logic for these sites")
            user_prompt_parts.append("3. Extract ALL data found - no filtering or validation")
            user_prompt_parts.append("\n** AI-SUGGESTED ADDITIONAL SOURCES **")
            user_prompt_parts.append("Based on the data description and fields above, YOU MUST find and add")
            user_prompt_parts.append("additional relevant public URLs to reach 3-5 total URLs in DEFAULT_URLS.")
            user_prompt_parts.append("Use your knowledge to identify official sites, Wikipedia, open databases, etc.")
        else:
            user_prompt_parts.append("\n** NO USER URLs PROVIDED - AI MUST SUGGEST 3-5 URLs **")
            user_prompt_parts.append("\nBased on the data description and required fields above,")
            user_prompt_parts.append("YOU MUST find and provide 3-5 relevant public URLs in DEFAULT_URLS.")
            user_prompt_parts.append("\nConsider:")
            user_prompt_parts.append(f"- Data topic: {fields['data_description']}")
            if fields['desired_fields']:
                user_prompt_parts.append(f"- Fields needed: {fields['desired_fields']}")
            user_prompt_parts.append("\nSearch your knowledge for:")
            user_prompt_parts.append("- Official websites for this data type")
            user_prompt_parts.append("- Wikipedia pages with relevant structured data")
            user_prompt_parts.append("- Open data portals and public databases")
            user_prompt_parts.append("- Government or institutional sources")
            user_prompt_parts.append("- Community sites with public, scrapable data")
        
        # REQUIRED FIELDS
        user_prompt_parts.append("\n" + "=" * 60)
        user_prompt_parts.append("REQUIRED FIELDS TO EXTRACT")
        user_prompt_parts.append("=" * 60)
        
        if fields['desired_fields']:
            field_list = InputProcessor.parse_fields(fields['desired_fields'])
            if field_list:
                user_prompt_parts.append("\n** MUST EXTRACT THESE FIELDS **")
                for field in field_list:
                    user_prompt_parts.append(f"  - {field}")
                user_prompt_parts.append("\nInstructions:")
                user_prompt_parts.append("1. Add specific selectors for each field")
                user_prompt_parts.append("2. Map to these exact field names in output")
                user_prompt_parts.append("3. Extract ALL values found - even empty or partial data")
        else:
            user_prompt_parts.append("\n** EXTRACT RELEVANT FIELDS BASED ON DATA DESCRIPTION **")
        
        # OUTPUT STRUCTURE
        if fields['response_structure']:
            user_prompt_parts.append("\n" + "=" * 60)
            user_prompt_parts.append("OUTPUT STRUCTURE")
            user_prompt_parts.append("=" * 60)
            user_prompt_parts.append(fields['response_structure'])
        
        # CONFIGURATION
        user_prompt_parts.append("\n" + "=" * 60)
        user_prompt_parts.append("CONFIGURATION VALUES")
        user_prompt_parts.append("=" * 60)
        user_prompt_parts.append(f"\nTimeout: {self.scraping_config.network.request_timeout} seconds")
        user_prompt_parts.append(f"User-Agent: {self.scraping_config.network.user_agent}")
        user_prompt_parts.append(f"Update Frequency: {fields['update_frequency']}")
        user_prompt_parts.append("\nReplace [USER_AGENT] and [FREQUENCY] placeholders!")
        
        # FINAL
        user_prompt_parts.append("\n" + "=" * 60)
        user_prompt_parts.append("GENERATE THE SCRIPT")
        user_prompt_parts.append("=" * 60)
        user_prompt_parts.append("\nGenerate a Platform Core scraper with:")
        user_prompt_parts.append("1. DEFAULT_URLS list with 3-5 URLs total:")
        if fields['data_source']:
            user_prompt_parts.append(f"   - MUST include ALL user-provided URLs: {fields['data_source']}")
            user_prompt_parts.append("   - ADD additional AI-suggested URLs to reach 3-5 total")
        else:
            user_prompt_parts.append("   - AI MUST suggest 3-5 relevant public URLs based on data requirements")
        user_prompt_parts.append("2. Smart strategy detection (table > cards > generic)")
        user_prompt_parts.append("3. RAW data extraction - NO filtering, NO confidence scoring")
        user_prompt_parts.append("4. Extract ALL data found - the pipeline will process it later")
        user_prompt_parts.append("5. Robust error handling with metadata")
        user_prompt_parts.append("\nReturn ONLY Python code.")
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": "\n".join(user_prompt_parts)}
        ]
        
        return messages
