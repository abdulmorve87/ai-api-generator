import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any
import datetime
import re

# ============================================================
# DEFAULT URLS (3-5 PUBLIC URLs)
# ============================================================
# 1. User-provided URL (MANDATORY)
# 2-3. AI-suggested relevant public URLs for IPO GMP data
DEFAULT_URLS = [
    'https://www.chittorgarh.com/report/ipo-grey-market-premium-gmp/73/',
    'https://www.ipo-watch.in/ipo-grey-market-premium/',
    'https://ipowatch.in/ipo-gmp/',
    'https://www.tradebrains.in/ipo-grey-market-premium/',
    'https://www.5paisa.com/ipo/ipo-grey-market-premium'
]

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_text_safe(element, default: str = '') -> str:
    """Safely extract text from an element."""
    if element is None:
        return default
    text = element.get_text(separator=' ', strip=True)
    return text if text else default

def get_attr_safe(element, attr: str, default: str = '') -> str:
    """Safely extract attribute from an element."""
    if element is None:
        return default
    return element.get(attr, default) or default

def is_navigation_element(element) -> bool:
    """Check if element is part of navigation/chrome - MUST SKIP THESE."""
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
    """Clean and normalize header text to field name."""
    if not text:
        return ''
    # Remove special chars, convert to snake_case
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = re.sub(r'\s+', '_', text.strip().lower())
    return text

def has_actual_data(record: dict) -> bool:
    """Check if record has actual data values, not just links."""
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
    """
    Detect the best scraping strategy based on page structure.
    Returns strategy name.
    
    Priority: table > cards > articles > generic
    """
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
    """Extract ALL data from HTML tables - skip navigation tables."""
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
            
            # Map extracted fields to required field names based on header content
            mapped_record = {}
            for key, value in record.items():
                key_lower = key.lower()
                if 'company' in key_lower or 'name' in key_lower:
                    mapped_record['company_name'] = value
                elif 'price' in key_lower or 'issue' in key_lower:
                    mapped_record['ipo_price'] = value
                elif 'gmp' in key_lower or 'premium' in key_lower:
                    mapped_record['gmp'] = value
                elif 'date' in key_lower or 'listing' in key_lower:
                    mapped_record['listing_date'] = value
                elif 'exchange' in key_lower or 'bse' in key_lower or 'nse' in key_lower:
                    mapped_record['exchange'] = value
                else:
                    mapped_record[key] = value
            
            # Only add records that have actual data values (not just links)
            if has_actual_data(mapped_record):
                data.append(mapped_record)
    
    return data

def scrape_card_data(soup: BeautifulSoup, required_fields: List[str]) -> List[Dict[str, Any]]:
    """Extract ALL data from card/item layouts - skip navigation."""
    data = []
    
    # Find main content area
    main_content = soup.select_one('main, #content, .content, [role="main"], #mainContent, .main-content')
    search_area = main_content if main_content else soup
    
    cards = search_area.select('[class*="card"]:not(nav *), [class*="item"]:not(nav *):not(header *):not(footer *), [class*="list-item"], article:not(nav *)')
    
    for card in cards:
        if is_navigation_element(card):
            continue
            
        record = {}
        
        # Extract company name
        title_elem = card.select_one('h1, h2, h3, h4, [class*="title"], [class*="name"], [class*="heading"]')
        if title_elem:
            text = get_text_safe(title_elem)
            if text and len(text) > 2:
                record['company_name'] = text
        
        # Extract description for potential price/GMP info
        desc_elem = card.select_one('p:not([class*="date"]), [class*="desc"], [class*="summary"]')
        if desc_elem:
            text = get_text_safe(desc_elem)
            if text:
                # Try to extract price and GMP from description text
                price_match = re.search(r'(?:₹|Rs\.?|INR)\s*[\d,]+(?:\.\d+)?', text)
                if price_match:
                    record['ipo_price'] = price_match.group(0)
                gmp_match = re.search(r'GMP\s*[:\-]?\s*(?:₹|Rs\.?|INR)?\s*[\d,]+(?:\.\d+)?', text, re.IGNORECASE)
                if gmp_match:
                    record['gmp'] = gmp_match.group(0)
        
        # Extract date
        date_elem = card.select_one('[class*="date"], time, [datetime]')
        if date_elem:
            text = get_text_safe(date_elem) or get_attr_safe(date_elem, 'datetime')
            if text:
                record['listing_date'] = text
        
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
                if 'gmp' in str(price_elem.get('class', '')).lower():
                    record['gmp'] = text
                else:
                    record['ipo_price'] = text
        
        # Extract exchange if mentioned
        exchange_elem = card.select_one('[class*="exchange"], [class*="bse"], [class*="nse"]')
        if exchange_elem:
            text = get_text_safe(exchange_elem)
            if text:
                record['exchange'] = text
        
        # Only add records with actual data
        if has_actual_data(record):
            data.append(record)
    
    return data

def scrape_generic(soup: BeautifulSoup, required_fields: List[str]) -> List[Dict[str, Any]]:
    """Generic fallback scraper - extract ALL data found from main content."""
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
            record['company_name'] = title
            
        desc = get_text_safe(item.select_one('p, [class*="desc"], span:not([class*="date"])'))
        if desc and len(desc) > 5:
            # Try to extract financial data from description
            price_match = re.search(r'(?:₹|Rs\.?|INR)\s*[\d,]+(?:\.\d+)?', desc)
            if price_match:
                record['ipo_price'] = price_match.group(0)
            gmp_match = re.search(r'GMP\s*[:\-]?\s*(?:₹|Rs\.?|INR)?\s*[\d,]+(?:\.\d+)?', desc, re.IGNORECASE)
            if gmp_match:
                record['gmp'] = gmp_match.group(0)
            
        date = get_text_safe(item.select_one('[class*="date"], time'))
        if date:
            record['listing_date'] = date
            
        link = get_attr_safe(item.select_one('a'), 'href')
        if link and not link.startswith('#'):
            record['link'] = link
        
        # Check for exchange mentions
        full_text = get_text_safe(item)
        if 'BSE' in full_text or 'NSE' in full_text:
            if 'BSE' in full_text:
                record['exchange'] = 'BSE'
            if 'NSE' in full_text:
                record['exchange'] = 'NSE'
        
        if has_actual_data(record):
            data.append(record)
    
    return data

# ============================================================
# MAIN SCRAPING FUNCTION
# ============================================================

def scrape_data(url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Scrape RAW data from a URL using adaptive strategy detection.
    NO FILTERING - Extract everything found. Processing happens later in pipeline.
    
    Args:
        url: The URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with 'data' list and 'metadata' dict
    """
    metadata = {
        'source_url': url,
        'total_count': 0,
        'scraped_at': datetime.datetime.utcnow().isoformat(),
        'scraping_method': 'unknown',
        'update_frequency': 'Daily',
        'error': None
    }
    
    # Full headers to avoid 403 Forbidden errors
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AIAPIGenerator/1.0 (Educational/Research Project; Contact: admin@example.com)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Detect best scraping strategy
        strategy = detect_scraping_strategy(soup, url)
        metadata['scraping_method'] = strategy
        
        # Required fields for IPO GMP data
        required_fields = ['company_name', 'ipo_price', 'gmp', 'listing_date', 'exchange']
        
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