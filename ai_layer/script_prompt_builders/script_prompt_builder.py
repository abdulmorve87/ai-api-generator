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

## SCRAPING LAYER SPECIFICATIONS

Our scraping layer uses:
- **BeautifulSoup4** (bs4) for HTML parsing with 'lxml' parser
- **requests** library for HTTP requests
- Parser: 'lxml' (NOT 'html.parser')

## CRITICAL: HTTP HEADERS FOR AVOIDING 403 ERRORS

**IMPORTANT**: Many sites (ESPN, Cricbuzz, Wikipedia, ICC, etc.) block requests without proper browser-like headers.
ALWAYS use these COMPLETE headers to avoid 403 Forbidden errors:

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
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

**WHY THESE HEADERS**: Modern websites check for Sec-Fetch-* and sec-ch-ua-* headers to detect bots. Without them, you get 403 errors.

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

## CRITICAL: DATA EXTRACTION RULES

### EXCLUDE NAVIGATION AND SITE CHROME - THIS IS MANDATORY
**NEVER extract data from these elements:**
- `<nav>`, `<header>`, `<footer>` elements and their children
- Elements with classes containing: nav, menu, sidebar, header, footer, breadcrumb, pagination, topbar, navbar
- Links that are clearly navigation (short text like "Home", "About", "Login")
- Empty records or records with only link fields and no actual data values

### IDENTIFY THE MAIN DATA CONTENT - THIS IS CRITICAL
**ALWAYS look for the PRIMARY data container FIRST:**
1. Find the MAIN content area: `main`, `#content`, `.content`, `[role="main"]`, `#mainContent`
2. Look for DATA TABLES within the main content (not navigation tables)
3. Look for repeating data patterns with ACTUAL VALUES (numbers, dates, prices, names)

### TABLE EXTRACTION - CRITICAL RULES FOR FINANCIAL/DATA SITES
When scraping tables (especially for IPO, stock, financial data):

1. **Find the RIGHT table** - Look for tables with:
   - Multiple columns of actual data (not just links)
   - Headers that match user's requested fields (company_name, price, date, etc.)
   - Data rows with text content, numbers, dates, percentages
   - Classes like: `data`, `results`, `listing`, `records`, `table-striped`, `table-bordered`

2. **SKIP navigation tables** - Ignore tables that:
   - Only contain links with no data values
   - Have single column with menu items
   - Are inside `<nav>`, `<header>`, `<footer>`
   - Have classes like: `nav`, `menu`, `sidebar`

3. **Extract CELL VALUES properly**:
   - Get the TEXT content of each cell (not just links)
   - For cells with links, get BOTH the link text AND href separately
   - Handle cells with multiple elements (get all text)
   - Preserve numbers, dates, percentages, currency values as-is

4. **Validate data rows**:
   - A valid data row has at least 2-3 cells with actual text content
   - Skip rows where most cells are empty
   - Skip rows that only contain navigation links

## CODE TEMPLATE (PLATFORM CORE)

```python
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import datetime
import re

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_text_safe(element, default: str = '') -> str:
    \"\"\"Safely extract text from an element.\"\"\"
    if element is None:
        return default
    text = element.get_text(separator=' ', strip=True)
    return text if text else default

def get_attr_safe(element, attr: str, default: str = '') -> str:
    \"\"\"Safely extract attribute from an element.\"\"\"
    if element is None:
        return default
    return element.get(attr, default) or default

def is_navigation_element(element) -> bool:
    \"\"\"Check if element is part of navigation/chrome - MUST SKIP THESE.\"\"\"
    if element is None:
        return True
    # Check if inside nav/header/footer
    if element.find_parent(['nav', 'header', 'footer']):
        return True
    # Check class names for navigation indicators
    classes = ' '.join(element.get('class', [])).lower()
    nav_keywords = ['nav', 'menu', 'sidebar', 'header', 'footer', 'breadcrumb', 
                    'pagination', 'topbar', 'navbar', 'dropdown']
    return any(kw in classes for kw in nav_keywords)

def clean_header(text: str) -> str:
    \"\"\"Clean and normalize header text to field name.\"\"\"
    if not text:
        return ''
    # Remove special chars, convert to snake_case
    text = re.sub(r'[^a-zA-Z0-9\\s]', '', text)
    text = re.sub(r'\\s+', '_', text.strip().lower())
    return text

def has_actual_data(record: dict) -> bool:
    \"\"\"Check if record has actual data values, not just links.\"\"\"
    for key, value in record.items():
        if key == 'link' or key.endswith('_link'):
            continue
        if value and str(value).strip():
            return True
    return False

# ============================================================
# STRATEGY DETECTION
# ============================================================

def detect_scraping_strategy(soup: BeautifulSoup, url: str) -> str:
    \"\"\"
    Detect the best scraping strategy based on page structure.
    Returns strategy name.
    
    Priority: table > cards > articles > generic
    \"\"\"
    # Look for main content area first
    main_content = soup.select_one('main, #content, .content, [role="main"], #mainContent, .main-content')
    search_area = main_content if main_content else soup
    
    # Find data tables (not navigation tables)
    data_tables = []
    for table in search_area.select('table'):
        if is_navigation_element(table):
            continue
        rows = table.select('tr')
        if len(rows) >= 2:  # At least header + 1 data row
            cells_in_row = len(rows[0].select('td, th'))
            if cells_in_row >= 2:  # Multiple columns = likely data table
                data_tables.append(table)
    
    if data_tables:
        return 'table'
    
    # Look for card layouts (not in navigation)
    cards = search_area.select('[class*="card"]:not(nav *), [class*="item"]:not(nav *):not(header *):not(footer *)')
    if len(cards) >= 3:
        return 'cards'
    
    # Look for article layouts
    articles = search_area.select('article:not(nav *), [class*="entry"]:not(nav *)')
    if len(articles) >= 2:
        return 'articles'
    
    return 'generic'

# ============================================================
# SCRAPING STRATEGIES - RAW DATA EXTRACTION
# ============================================================

def scrape_table_data(soup: BeautifulSoup, required_fields: List[str]) -> List[Dict[str, Any]]:
    \"\"\"Extract ALL data from HTML tables - skip navigation tables.\"\"\"
    data = []
    
    # Find main content area first - CRITICAL for avoiding navigation
    main_content = soup.select_one('main, #content, .content, [role="main"], #mainContent, .main-content, .container, article')
    search_area = main_content if main_content else soup
    
    # Find data tables with specific selectors, then fallback to generic
    table_selectors = [
        'table[class*="data"]', 'table[class*="listing"]', 'table[class*="result"]',
        'table[class*="ipo"]', 'table[class*="stock"]', 'table[class*="schedule"]',
        'table[class*="gmp"]', 'table[class*="premium"]',
        'table.table-bordered', 'table.table-striped', 'table.table',
        'table[id*="data"]', 'table[id*="list"]', 'table[id*="result"]',
        'table'  # Fallback
    ]
    
    tables = []
    for selector in table_selectors:
        found = search_area.select(selector)
        for t in found:
            if t not in tables and not is_navigation_element(t):
                # Additional check: table should have multiple columns
                first_row = t.select_one('tr')
                if first_row and len(first_row.select('td, th')) >= 2:
                    tables.append(t)
    
    for table in tables:
        # Get headers from thead or first row
        headers = []
        thead = table.select_one('thead')
        if thead:
            headers = [clean_header(th.get_text(strip=True)) for th in thead.select('th, td')]
        
        if not headers:
            first_row = table.select_one('tr')
            if first_row:
                headers = [clean_header(cell.get_text(strip=True)) for cell in first_row.select('th, td')]
        
        # Filter out empty headers and assign default names
        headers = [h if h else f'column_{i}' for i, h in enumerate(headers)]
        
        # Get data rows (skip header row)
        rows = table.select('tbody tr') if table.select('tbody') else table.select('tr')[1:]
        
        for row in rows:
            cells = row.select('td')
            if not cells or len(cells) < 2:  # Skip rows with too few cells
                continue
                
            record = {}
            
            for i, cell in enumerate(cells):
                if i < len(headers):
                    field_name = headers[i]
                    # Get text content properly - this is the ACTUAL DATA
                    text = cell.get_text(separator=' ', strip=True)
                    record[field_name] = text if text else None
                    
                    # Also extract link if present (as separate field)
                    link = cell.select_one('a[href]')
                    if link:
                        href = link.get('href', '')
                        if href and not href.startswith('#') and not href.startswith('javascript:'):
                            record[f'{field_name}_link'] = href
            
            # Only add records that have actual data values (not just links)
            if has_actual_data(record):
                data.append(record)
    
    return data

def scrape_card_data(soup: BeautifulSoup, required_fields: List[str]) -> List[Dict[str, Any]]:
    \"\"\"Extract ALL data from card/item layouts - skip navigation.\"\"\"
    data = []
    
    # Find main content area
    main_content = soup.select_one('main, #content, .content, [role="main"], #mainContent, .main-content')
    search_area = main_content if main_content else soup
    
    cards = search_area.select('[class*="card"]:not(nav *), [class*="item"]:not(nav *):not(header *):not(footer *), [class*="list-item"], article:not(nav *)')
    
    for card in cards:
        if is_navigation_element(card):
            continue
            
        record = {}
        
        # Extract title/name
        title_elem = card.select_one('h1, h2, h3, h4, [class*="title"], [class*="name"], [class*="heading"]')
        if title_elem:
            text = get_text_safe(title_elem)
            if text and len(text) > 2:  # Skip very short titles (likely icons)
                record['title'] = text
        
        # Extract description
        desc_elem = card.select_one('p:not([class*="date"]), [class*="desc"], [class*="summary"]')
        if desc_elem:
            text = get_text_safe(desc_elem)
            if text:
                record['description'] = text
        
        # Extract date
        date_elem = card.select_one('[class*="date"], time, [datetime]')
        if date_elem:
            text = get_text_safe(date_elem) or get_attr_safe(date_elem, 'datetime')
            if text:
                record['date'] = text
        
        # Extract link
        link_elem = card.select_one('a[href]')
        if link_elem:
            href = get_attr_safe(link_elem, 'href')
            if href and not href.startswith('#') and len(href) > 1:
                record['link'] = href
        
        # Extract price/value if present
        price_elem = card.select_one('[class*="price"], [class*="value"], [class*="amount"]')
        if price_elem:
            text = get_text_safe(price_elem)
            if text:
                record['price'] = text
        
        # Only add records with actual data
        if has_actual_data(record):
            data.append(record)
    
    return data

def scrape_generic(soup: BeautifulSoup, required_fields: List[str]) -> List[Dict[str, Any]]:
    \"\"\"Generic fallback scraper - extract ALL data found from main content.\"\"\"
    data = []
    
    # Find main content area - CRITICAL
    main_content = soup.select_one('main, #content, .content, [role="main"], #mainContent, .main-content, article')
    search_area = main_content if main_content else soup.body if soup.body else soup
    
    # Try to find repeating content blocks (not navigation)
    items = search_area.select(
        '[class*="item"]:not(nav *):not(header *):not(footer *), '
        '[class*="entry"]:not(nav *), [class*="row"]:not(nav *):not(thead *), '
        '[class*="record"], [class*="result"], '
        'li:not(nav li):not(footer li):not(header li):not([class*="menu"])'
    )
    
    for item in items:
        if is_navigation_element(item):
            continue
            
        record = {}
        
        title = get_text_safe(item.select_one('h1, h2, h3, h4, a, [class*="title"]'))
        if title and len(title) > 2:
            record['title'] = title
            
        desc = get_text_safe(item.select_one('p, [class*="desc"], span:not([class*="date"])'))
        if desc and len(desc) > 5:
            record['description'] = desc
            
        date = get_text_safe(item.select_one('[class*="date"], time'))
        if date:
            record['date'] = date
            
        link = get_attr_safe(item.select_one('a'), 'href')
        if link and not link.startswith('#'):
            record['link'] = link
        
        if has_actual_data(record):
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
    
    # Full headers to avoid 403 Forbidden errors (especially for Wikipedia)
    headers = {
        'User-Agent': '[USER_AGENT]',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
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
4. **Target the main data table/content** - Skip navigation and site chrome
5. **For financial sites (IPO, stocks, etc.)** - Look for tables with company names, prices, dates, percentages

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
        else:
            user_prompt_parts.append("\n** NO USER URLs PROVIDED - AI MUST SUGGEST 3-5 URLs **")
            user_prompt_parts.append("\nBased on the data description and required fields above,")
            user_prompt_parts.append("YOU MUST find and provide 3-5 relevant public URLs in DEFAULT_URLS.")
        
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
                user_prompt_parts.append("4. SKIP navigation links - only extract actual data from tables/content")
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
        
        # CRITICAL REMINDERS
        user_prompt_parts.append("\n" + "=" * 60)
        user_prompt_parts.append("CRITICAL REMINDERS - READ CAREFULLY")
        user_prompt_parts.append("=" * 60)
        user_prompt_parts.append("\n1. SKIP ALL NAVIGATION ELEMENTS - Do not extract from nav, header, footer, menu")
        user_prompt_parts.append("2. FIND THE MAIN DATA TABLE - Look for tables with actual data values (numbers, dates, names)")
        user_prompt_parts.append("3. EXTRACT CELL TEXT - Get the text content of table cells, not just links")
        user_prompt_parts.append("4. VALIDATE DATA ROWS - Only include rows that have actual data values")
        user_prompt_parts.append("5. For IPO/financial data - Look for tables with company names, prices, dates, percentages")
        
        # FINAL
        user_prompt_parts.append("\n" + "=" * 60)
        user_prompt_parts.append("GENERATE THE SCRIPT")
        user_prompt_parts.append("=" * 60)
        user_prompt_parts.append("\nGenerate a Platform Core scraper with:")
        user_prompt_parts.append("1. DEFAULT_URLS list with 3-5 URLs total")
        user_prompt_parts.append("2. Smart strategy detection (table > cards > generic)")
        user_prompt_parts.append("3. Navigation element filtering (CRITICAL)")
        user_prompt_parts.append("4. Proper table cell text extraction")
        user_prompt_parts.append("5. Data validation (skip empty/navigation-only records)")
        user_prompt_parts.append("6. Robust error handling with metadata")
        user_prompt_parts.append("\nReturn ONLY Python code.")
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": "\n".join(user_prompt_parts)}
        ]
        
        return messages
