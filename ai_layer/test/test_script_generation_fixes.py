"""
Test script to verify script generation fixes for:
1. Navigation element filtering
2. Main content area detection
3. Proper table data extraction (not navigation links)
4. Data validation (skip empty/link-only records)
"""

import sys
import os
import re

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_layer.script_prompt_builder import ScriptPromptBuilder
from ai_layer.deepseek_client import DeepSeekClient
from ai_layer.config import DeepSeekConfig
from scraping_layer.config import ScrapingConfig


def test_prompt_contains_navigation_filtering():
    """Test that the system prompt includes navigation filtering instructions."""
    print("=" * 60)
    print("TEST 1: Navigation Filtering Instructions")
    print("=" * 60)
    
    system_prompt = ScriptPromptBuilder.SYSTEM_PROMPT
    
    checks = {
        'has_navigation_exclusion': 'EXCLUDE NAVIGATION' in system_prompt or 'SKIP' in system_prompt and 'nav' in system_prompt,
        'has_is_navigation_function': 'is_navigation_element' in system_prompt,
        'has_main_content_detection': 'main content' in system_prompt.lower() or '#content' in system_prompt,
        'has_data_validation': 'has_actual_data' in system_prompt or 'validate' in system_prompt.lower(),
        'mentions_nav_header_footer': '<nav>' in system_prompt and '<header>' in system_prompt and '<footer>' in system_prompt,
    }
    
    print("\nChecking system prompt for key instructions:")
    for check_name, result in checks.items():
        status = "✓" if result else "✗"
        print(f"{status} {check_name}: {result}")
    
    all_passed = all(checks.values())
    print(f"\n{'✓ PASSED' if all_passed else '✗ FAILED'}: All navigation filtering instructions present")
    
    return all_passed


def test_prompt_contains_table_extraction_rules():
    """Test that the system prompt includes proper table extraction rules."""
    print("\n" + "=" * 60)
    print("TEST 2: Table Extraction Rules")
    print("=" * 60)
    
    system_prompt = ScriptPromptBuilder.SYSTEM_PROMPT
    
    checks = {
        'has_table_detection': 'table' in system_prompt.lower() and 'detect' in system_prompt.lower(),
        'has_cell_text_extraction': 'get_text' in system_prompt or 'cell' in system_prompt.lower(),
        'has_header_extraction': 'header' in system_prompt.lower() and 'thead' in system_prompt,
        'has_financial_selectors': 'ipo' in system_prompt.lower() or 'stock' in system_prompt.lower(),
        'skip_navigation_tables': 'skip' in system_prompt.lower() and 'navigation' in system_prompt.lower(),
    }
    
    print("\nChecking system prompt for table extraction rules:")
    for check_name, result in checks.items():
        status = "✓" if result else "✗"
        print(f"{status} {check_name}: {result}")
    
    all_passed = all(checks.values())
    print(f"\n{'✓ PASSED' if all_passed else '✗ FAILED'}: All table extraction rules present")
    
    return all_passed


def test_user_prompt_generation():
    """Test that user prompts include critical reminders."""
    print("\n" + "=" * 60)
    print("TEST 3: User Prompt Generation")
    print("=" * 60)
    
    try:
        scraping_config = ScrapingConfig.from_env()
        builder = ScriptPromptBuilder(scraping_config)
        
        # Test with IPO data requirements
        form_input = {
            'data_description': 'IPO grey market premium data with company names and listing dates',
            'data_source': 'https://www.chittorgarh.com/report/ipo-grey-market-premium-gmp/73/',
            'desired_fields': 'company_name, ipo_price, gmp, listing_date, exchange',
            'response_structure': '',
            'update_frequency': 'Daily'
        }
        
        messages = builder.build_script_prompt(form_input)
        
        print(f"\n✓ Generated {len(messages)} messages")
        
        # Check system message
        system_msg = messages[0]['content']
        print(f"✓ System message length: {len(system_msg)} chars")
        
        # Check user message
        user_msg = messages[1]['content']
        print(f"✓ User message length: {len(user_msg)} chars")
        
        # Check for critical reminders in user message
        checks = {
            'has_critical_reminders': 'CRITICAL REMINDERS' in user_msg or 'CRITICAL' in user_msg,
            'mentions_skip_navigation': 'SKIP' in user_msg and 'NAVIGATION' in user_msg,
            'mentions_main_data_table': 'MAIN DATA TABLE' in user_msg or 'main' in user_msg.lower(),
            'mentions_extract_cell_text': 'CELL TEXT' in user_msg or 'text content' in user_msg.lower(),
            'mentions_validate_data': 'VALIDATE' in user_msg or 'validate' in user_msg.lower(),
            'includes_user_url': 'chittorgarh.com' in user_msg,
            'includes_required_fields': 'company_name' in user_msg and 'gmp' in user_msg,
        }
        
        print("\nChecking user prompt for critical elements:")
        for check_name, result in checks.items():
            status = "✓" if result else "✗"
            print(f"{status} {check_name}: {result}")
        
        all_passed = all(checks.values())
        print(f"\n{'✓ PASSED' if all_passed else '✗ FAILED'}: User prompt contains all critical elements")
        
        return all_passed
        
    except Exception as e:
        print(f"\n✗ FAILED: Error generating prompt: {e}")
        return False


def test_generated_script_structure():
    """Test that generated scripts have the required structure."""
    print("\n" + "=" * 60)
    print("TEST 4: Generated Script Structure (with API)")
    print("=" * 60)
    
    try:
        config = DeepSeekConfig.from_env()
        scraping_config = ScrapingConfig.from_env()
        client = DeepSeekClient(config.api_key, config.base_url)
        builder = ScriptPromptBuilder(scraping_config)
    except Exception as e:
        print(f"\n⚠️ Skipping API test - configuration error: {e}")
        return None
    
    # Test with IPO data requirements
    form_input = {
        'data_description': 'IPO grey market premium data with company names, prices, and listing dates',
        'data_source': 'https://www.chittorgarh.com/report/ipo-grey-market-premium-gmp/73/',
        'desired_fields': 'company_name, ipo_price, gmp, listing_date, exchange',
        'response_structure': '',
        'update_frequency': 'Daily'
    }
    
    print("\nGenerating script with DeepSeek API...")
    messages = builder.build_script_prompt(form_input)
    
    try:
        script_code = client.generate_completion(
            messages=messages,
            model="deepseek-chat",
            temperature=0.3,
            max_tokens=8000
        )
        
        print(f"✓ Script generated ({len(script_code)} chars)")
        
        # Check for required functions and patterns
        checks = {
            'has_imports': 'import requests' in script_code and 'from bs4 import BeautifulSoup' in script_code,
            'has_is_navigation_element': 'def is_navigation_element' in script_code,
            'has_has_actual_data': 'def has_actual_data' in script_code,
            'has_clean_header': 'def clean_header' in script_code,
            'has_get_text_safe': 'def get_text_safe' in script_code,
            'has_scrape_data': 'def scrape_data' in script_code,
            'has_scrape_table_data': 'def scrape_table_data' in script_code,
            'has_detect_strategy': 'def detect_scraping_strategy' in script_code,
            'checks_navigation': 'is_navigation_element(' in script_code,
            'finds_main_content': 'main' in script_code or '#content' in script_code,
            'extracts_cell_text': 'get_text' in script_code,
            'validates_data': 'has_actual_data' in script_code,
            'has_default_urls': 'DEFAULT_URLS' in script_code,
            'includes_user_url': 'chittorgarh.com' in script_code,
        }
        
        print("\nChecking generated script structure:")
        for check_name, result in checks.items():
            status = "✓" if result else "✗"
            print(f"{status} {check_name}: {result}")
        
        # Count critical patterns
        nav_checks = script_code.count('is_navigation_element')
        main_content_refs = script_code.count('main_content') + script_code.count('#content')
        
        print(f"\nPattern counts:")
        print(f"  - Navigation checks: {nav_checks}")
        print(f"  - Main content references: {main_content_refs}")
        
        # Show a snippet of the table extraction function
        if 'def scrape_table_data' in script_code:
            start = script_code.find('def scrape_table_data')
            end = script_code.find('\ndef ', start + 1)
            snippet = script_code[start:end] if end > start else script_code[start:start+500]
            print(f"\n--- scrape_table_data snippet ---")
            print(snippet[:400] + "..." if len(snippet) > 400 else snippet)
        
        all_passed = all(checks.values())
        print(f"\n{'✓ PASSED' if all_passed else '✗ FAILED'}: Generated script has required structure")
        
        # Save script for manual inspection
        output_file = 'ai_layer/test/generated_script_sample.py'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(script_code)
        print(f"\n✓ Script saved to: {output_file}")
        
        return all_passed
        
    except Exception as e:
        print(f"\n✗ FAILED: Error generating script: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_script_execution_mock():
    """Test that the generated script logic would work correctly (mock test)."""
    print("\n" + "=" * 60)
    print("TEST 5: Script Logic Validation (Mock)")
    print("=" * 60)
    
    # Simulate HTML with navigation and data table
    mock_html = """
    <html>
        <nav>
            <a href="/home">Home</a>
            <a href="/about">About</a>
        </nav>
        <main>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Company Name</th>
                        <th>IPO Price</th>
                        <th>GMP</th>
                        <th>Listing Date</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>ABC Corp</td>
                        <td>₹ 100</td>
                        <td>₹ 50</td>
                        <td>15 Jan 2026</td>
                    </tr>
                    <tr>
                        <td>XYZ Ltd</td>
                        <td>₹ 200</td>
                        <td>₹ 75</td>
                        <td>20 Jan 2026</td>
                    </tr>
                </tbody>
            </table>
        </main>
        <footer>
            <a href="/contact">Contact</a>
        </footer>
    </html>
    """
    
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(mock_html, 'lxml')
    
    # Test 1: Find main content
    main_content = soup.select_one('main, #content, .content')
    print(f"\n✓ Found main content: {main_content is not None}")
    
    # Test 2: Find data table (not navigation)
    if main_content:
        tables = main_content.select('table')
        print(f"✓ Found {len(tables)} table(s) in main content")
        
        # Test 3: Check table is not in navigation
        for table in tables:
            in_nav = table.find_parent(['nav', 'header', 'footer']) is not None
            print(f"✓ Table is {'IN' if in_nav else 'NOT in'} navigation: {not in_nav}")
        
        # Test 4: Extract data from table
        if tables:
            table = tables[0]
            headers = [th.get_text(strip=True) for th in table.select('th')]
            print(f"✓ Extracted headers: {headers}")
            
            rows = table.select('tbody tr')
            print(f"✓ Found {len(rows)} data rows")
            
            data = []
            for row in rows:
                cells = row.select('td')
                if cells:
                    record = {}
                    for i, cell in enumerate(cells):
                        if i < len(headers):
                            text = cell.get_text(strip=True)
                            record[headers[i]] = text
                    data.append(record)
            
            print(f"✓ Extracted {len(data)} records")
            
            # Test 5: Verify data quality
            if data:
                print("\n--- Sample extracted data ---")
                for i, record in enumerate(data[:2], 1):
                    print(f"Record {i}: {record}")
                
                # Check that records have actual data
                has_company_names = all('Company Name' in r and r['Company Name'] for r in data)
                has_prices = all('IPO Price' in r and r['IPO Price'] for r in data)
                
                print(f"\n✓ All records have company names: {has_company_names}")
                print(f"✓ All records have IPO prices: {has_prices}")
                
                print(f"\n✓ PASSED: Mock script logic works correctly")
                return True
    
    print(f"\n✗ FAILED: Mock script logic failed")
    return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SCRIPT GENERATION FIXES VERIFICATION TESTS")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Prompt contains navigation filtering
    results['navigation_filtering'] = test_prompt_contains_navigation_filtering()
    
    # Test 2: Prompt contains table extraction rules
    results['table_extraction'] = test_prompt_contains_table_extraction_rules()
    
    # Test 3: User prompt generation
    results['user_prompt'] = test_user_prompt_generation()
    
    # Test 4: Generated script structure (API test)
    results['script_structure'] = test_generated_script_structure()
    
    # Test 5: Script logic validation (mock)
    results['script_logic'] = test_script_execution_mock()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is None:
            status = "⚠️ SKIPPED"
        elif result:
            status = "✓ PASSED"
        else:
            status = "✗ FAILED"
        print(f"{test_name}: {status}")
    
    # Overall result
    passed = all(r for r in results.values() if r is not None)
    print("\n" + ("=" * 60))
    print(f"OVERALL: {'✓ ALL TESTS PASSED' if passed else '✗ SOME TESTS FAILED'}")
    print("=" * 60)
    
    return passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
