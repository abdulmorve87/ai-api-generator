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

**MANDATORY**: Every generated script MUST include a DEFAULT_URLS list at the top with at least 2 PUBLIC URLs that:
- Do NOT require authentication or login
- Do NOT have aggressive anti-scraping measures (avoid Amazon, Goodreads)
- Are publicly accessible without API keys
- Actually contain the requested data

Example of GOOD public URLs for books:
- https://www.georgerrmartin.com/book-category/ (author's official site)
- https://openlibrary.org/authors/OL2856508A/George_R._R._Martin (Open Library - public API)
- https://en.wikipedia.org/wiki/George_R._R._Martin_bibliography (Wikipedia - always public)

Example of BAD URLs (require auth or block scrapers):
- https://www.goodreads.com/* (requires login for full data)
- https://www.amazon.com/* (aggressive anti-bot)
- Any URL with /login, /signin, /account

**FORMAT**: Add this at the top of the script after imports:
```python
# Default URLs for scraping (public, no-auth required)
DEFAULT_URLS = [
    'https://example-public-site.com/data',
    'https://another-public-site.org/info',
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
- Return **structured data with proper error metadata**
- Include **noise filtering, confidence scoring, and deduplication**

### Function Signature
```python
def scrape_data(url: str, timeout: int = 30) -> Dict[str, Any]:
```

### Return Format (ALWAYS return this structure)
```python
{
    'data': [
        {'field1': 'value1', 'confidence_score': 6, ...},
    ],
    'metadata': {
        'source_url': str,
        'total_count': int,
        'filtered_count': int,  # Records removed by noise/score filtering
        'duplicate_count': int,  # Records removed as duplicates
        'scraped_at': 'ISO timestamp',
        'scraping_method': str,  # 'table', 'cards', 'generic'
        'confidence': str,  # 'high', 'medium', 'low'
        'update_frequency': str,
        'error': str or None
    }
}
```

## CODE TEMPLATE (PLATFORM CORE)

```python
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional, Tuple
import datetime
import re

# ============================================================
# CONFIGURATION
# ============================================================

MIN_TITLE_LENGTH = 3
BLACKLIST_WORDS = {'login', 'subscribe', 'cookie', 'privacy', 'terms', 'sign in', 'sign up', 'newsletter', 'advertisement', 'sponsored'}
MIN_CONFIDENCE_SCORE = 4

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
# NOISE CONTROL
# ============================================================

def is_noise(record: Dict[str, Any]) -> bool:
    \"\"\"Check if a record is noise/junk data.\"\"\"
    title = str(record.get('title', '')).lower()
    
    # Check minimum title length
    if len(title) < MIN_TITLE_LENGTH:
        return True
    
    # Check blacklist words
    for word in BLACKLIST_WORDS:
        if word in title:
            return True
    
    return False

def filter_noise(data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
    \"\"\"Remove noise records. Returns (cleaned_data, removed_count).\"\"\"
    cleaned = [r for r in data if not is_noise(r)]
    removed = len(data) - len(cleaned)
    return cleaned, removed

# ============================================================
# CONFIDENCE SCORING
# ============================================================

def calculate_confidence_score(record: Dict[str, Any]) -> int:
    \"\"\"Calculate confidence score for a record.\"\"\"
    score = 0
    
    # Title: +2 points
    if record.get('title') and len(str(record['title'])) >= MIN_TITLE_LENGTH:
        score += 2
    
    # Date: +2 points
    if record.get('date') and str(record['date']).strip():
        score += 2
    
    # Location/Circuit/Venue: +2 points
    if record.get('circuit') or record.get('location') or record.get('venue'):
        score += 2
    
    # Round/Number: +1 point
    if record.get('round') or record.get('number') or record.get('index'):
        score += 1
    
    # Link: +1 point
    if record.get('link') and str(record['link']).startswith(('http', '/')):
        score += 1
    
    # Description: +1 point
    if record.get('description') and len(str(record['description'])) > 10:
        score += 1
    
    return score

def filter_low_confidence(data: List[Dict[str, Any]], min_score: int = MIN_CONFIDENCE_SCORE) -> Tuple[List[Dict[str, Any]], int]:
    \"\"\"Remove records below minimum confidence score.\"\"\"
    # Add scores to all records
    for record in data:
        record['confidence_score'] = calculate_confidence_score(record)
    
    # Filter by score
    cleaned = [r for r in data if r['confidence_score'] >= min_score]
    removed = len(data) - len(cleaned)
    return cleaned, removed

# ============================================================
# DEDUPLICATION
# ============================================================

def deduplicate(data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
    \"\"\"Remove duplicate records by title+date. Returns (cleaned_data, duplicate_count).\"\"\"
    seen = set()
    cleaned = []
    
    for record in data:
        # Create dedup key from title and date
        title = str(record.get('title', '')).lower().strip()
        date = str(record.get('date', '')).strip()
        key = (title, date)
        
        if key not in seen:
            seen.add(key)
            cleaned.append(record)
    
    duplicate_count = len(data) - len(cleaned)
    return cleaned, duplicate_count

# ============================================================
# STRATEGY DETECTION (IMPROVED)
# ============================================================

def detect_scraping_strategy(soup: BeautifulSoup, url: str) -> Tuple[str, str]:
    \"\"\"
    Detect the best scraping strategy based on page structure.
    Returns (strategy, confidence).
    
    Priority: table > cards > articles > generic
    \"\"\"
    has_table = bool(soup.select('table[class*="data"], table[class*="schedule"], table[class*="result"], table.results, table tbody tr'))
    has_cards = bool(soup.select('[class*="card"], [class*="item"], [class*="list-item"]'))
    has_articles = bool(soup.select('article, [class*="event"], [class*="entry"]'))
    
    # Prefer table if it exists (most structured)
    if has_table:
        return 'table', 'high'
    
    # Cards are second preference
    if has_cards:
        return 'cards', 'high'
    
    # Articles third
    if has_articles:
        return 'articles', 'medium'
    
    # Generic fallback - lower confidence
    return 'generic', 'low'

# ============================================================
# SCRAPING STRATEGIES
# ============================================================

def scrape_table_data(soup: BeautifulSoup, required_fields: List[str]) -> List[Dict[str, Any]]:
    \"\"\"Extract data from HTML tables.\"\"\"
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
            if cells and headers and len(cells) >= 1:
                record = {}
                for i, cell in enumerate(cells):
                    if i < len(headers) and headers[i]:
                        record[headers[i]] = get_text_safe(cell)
                    # Also try to get link from cell
                    link = cell.select_one('a')
                    if link and 'link' not in record:
                        record['link'] = get_attr_safe(link, 'href')
                
                # Map to standard fields
                record['title'] = record.get('name') or record.get('title') or record.get('event') or ''
                record['date'] = record.get('date') or record.get('start_date') or ''
                
                if record.get('title') or len(record) > 2:
                    data.append(record)
    
    return data

def scrape_card_data(soup: BeautifulSoup, required_fields: List[str]) -> List[Dict[str, Any]]:
    \"\"\"Extract data from card/item layouts.\"\"\"
    data = []
    cards = soup.select('[class*="card"], [class*="item"]:not(nav *):not(header *):not(footer *), [class*="list-item"], article')
    
    for card in cards:
        record = {}
        
        # Title with multiple fallbacks
        record['title'] = get_text_safe(
            card.select_one('h1, h2, h3, h4, [class*="title"], [class*="name"], [class*="heading"]')
        )
        
        # Description
        record['description'] = get_text_safe(
            card.select_one('p:not([class*="date"]), [class*="desc"], [class*="summary"], [class*="content"], [class*="text"]')
        )
        
        # Date with fallbacks
        date_elem = card.select_one('[class*="date"], time, [datetime], [class*="time"]')
        record['date'] = get_text_safe(date_elem) or get_attr_safe(date_elem, 'datetime')
        
        # Link
        link_elem = card.select_one('a[href]')
        record['link'] = get_attr_safe(link_elem, 'href')
        
        # Location/venue
        record['location'] = get_text_safe(
            card.select_one('[class*="location"], [class*="venue"], [class*="place"], [class*="circuit"]')
        )
        
        if record['title']:
            data.append(record)
    
    return data

def scrape_generic(soup: BeautifulSoup, required_fields: List[str]) -> List[Dict[str, Any]]:
    \"\"\"Generic fallback scraper using flexible selectors.\"\"\"
    data = []
    
    # Try to find any repeating content blocks
    containers = soup.select(
        'main, article, .content, #content, [class*="main"], '
        '[class*="calendar"], [class*="schedule"], [class*="event"], '
        '[class*="list"], [class*="results"], [class*="entries"]'
    )
    
    if not containers:
        containers = [soup.body] if soup.body else [soup]
    
    for container in containers[:3]:  # Limit containers to avoid noise
        items = container.select(
            '[class*="item"]:not(nav *):not(header *):not(footer *), '
            '[class*="entry"], [class*="row"]:not(nav *), '
            '[class*="event"], [class*="card"], '
            'li:not(nav li):not(footer li)'
        )[:50]  # Limit items
        
        for item in items:
            record = {}
            record['title'] = get_text_safe(item.select_one('h1, h2, h3, h4, a, [class*="title"]'))
            record['description'] = get_text_safe(item.select_one('p, [class*="desc"], span:not([class*="date"])'))
            record['date'] = get_text_safe(item.select_one('[class*="date"], time'))
            record['link'] = get_attr_safe(item.select_one('a'), 'href')
            
            if record['title'] and len(record['title']) >= MIN_TITLE_LENGTH:
                data.append(record)
    
    return data

# ============================================================
# MAIN SCRAPING FUNCTION
# ============================================================

def scrape_data(url: str, timeout: int = 30) -> Dict[str, Any]:
    \"\"\"
    Scrape data from a URL using adaptive strategy detection.
    Includes noise filtering, confidence scoring, and deduplication.
    
    Args:
        url: The URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with 'data' list and 'metadata' dict
    \"\"\"
    metadata = {
        'source_url': url,
        'total_count': 0,
        'filtered_count': 0,
        'duplicate_count': 0,
        'scraped_at': datetime.datetime.utcnow().isoformat(),
        'scraping_method': 'unknown',
        'confidence': 'low',
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
        strategy, confidence = detect_scraping_strategy(soup, url)
        metadata['scraping_method'] = strategy
        metadata['confidence'] = confidence
        
        # Required fields from user (customize extraction)
        required_fields = []  # Will be populated based on user input
        
        # Apply appropriate scraping strategy
        if strategy == 'table':
            data = scrape_table_data(soup, required_fields)
        elif strategy in ('cards', 'articles'):
            data = scrape_card_data(soup, required_fields)
        else:
            data = scrape_generic(soup, required_fields)
        
        raw_count = len(data)
        
        # Step 1: Filter noise
        data, noise_removed = filter_noise(data)
        
        # Step 2: Calculate confidence scores and filter low-confidence
        data, low_conf_removed = filter_low_confidence(data)
        
        # Step 3: Deduplicate
        data, duplicate_count = deduplicate(data)
        
        metadata['total_count'] = len(data)
        metadata['filtered_count'] = noise_removed + low_conf_removed
        metadata['duplicate_count'] = duplicate_count
        
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

1. **Customize confidence scoring** - Add/adjust field weights based on required fields
2. **Customize selectors** - Add domain-specific CSS selectors for known sites
3. **Customize field extraction** - Map to user's exact field names
4. **Adjust thresholds** - MIN_TITLE_LENGTH, MIN_CONFIDENCE_SCORE, BLACKLIST_WORDS

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
        user_prompt_parts.append("DATA SOURCES")
        user_prompt_parts.append("=" * 60)
        
        if fields['data_source']:
            user_prompt_parts.append("\n** USER-PROVIDED SOURCES **")
            user_prompt_parts.append(f"User input: {fields['data_source']}")
            user_prompt_parts.append("\nInstructions:")
            user_prompt_parts.append("1. Add domain-specific selector logic for these sites")
            user_prompt_parts.append("2. Customize confidence scoring for this data type")
        else:
            user_prompt_parts.append("\n** NO SPECIFIC URLS PROVIDED **")
            user_prompt_parts.append("\nGenerate a generic scraper. Suggest example URLs in comments.")
        
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
                user_prompt_parts.append("1. Update calculate_confidence_score() to weight these fields")
                user_prompt_parts.append("2. Add specific selectors for each field")
                user_prompt_parts.append("3. Map to these exact field names in output")
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
        user_prompt_parts.append("1. Noise filtering (blacklist, min length)")
        user_prompt_parts.append("2. Confidence scoring (customized for required fields)")
        user_prompt_parts.append("3. Deduplication (by title+date)")
        user_prompt_parts.append("4. Smart strategy detection (table > cards > generic)")
        user_prompt_parts.append("\nReturn ONLY Python code.")
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": "\n".join(user_prompt_parts)}
        ]
        
        return messages
