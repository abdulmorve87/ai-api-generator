"""
Dynamic Execution Example - Demonstrates AI-Scraping Layer Integration.

This example shows how to:
1. Execute AI-generated scraper scripts
2. Handle single and multiple data sources
3. Display formatted results on the console

Usage:
    python -m scraping_layer.examples.dynamic_execution_example
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scraping_layer.dynamic_execution import (
    AIScrapingIntegration,
    DynamicScriptExecutor,
    ConsoleOutputFormatter,
    ExecutionConfig,
    create_integration,
    configure_logging
)
import logging


def example_single_source():
    """Example: Execute a script against a single data source."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Single Data Source Execution")
    print("=" * 80 + "\n")
    
    # Create integration
    integration = create_integration(use_colors=True)
    
    # Example AI-generated script (simulated)
    script_code = '''
def scrape_data(url):
    """Scrape F1 calendar data from a URL."""
    from datetime import datetime
    
    # Simulated data (in real scenario, this would fetch from the URL)
    data = [
        {
            'title': 'Australian Grand Prix',
            'date': '2025-03-16',
            'circuit': 'Albert Park Circuit',
            'location': 'Melbourne, Australia',
            'round': 1
        },
        {
            'title': 'Chinese Grand Prix',
            'date': '2025-03-23',
            'circuit': 'Shanghai International Circuit',
            'location': 'Shanghai, China',
            'round': 2
        },
        {
            'title': 'Japanese Grand Prix',
            'date': '2025-04-06',
            'circuit': 'Suzuka Circuit',
            'location': 'Suzuka, Japan',
            'round': 3
        }
    ]
    
    return {
        'data': data,
        'metadata': {
            'source_url': url,
            'total_count': len(data),
            'filtered_count': 0,
            'duplicate_count': 0,
            'scraping_method': 'table',
            'confidence': 'high',
            'scraped_at': datetime.utcnow().isoformat(),
            'update_frequency': 'Daily'
        }
    }
'''
    
    # Execute and display
    result = integration.execute_and_display(
        script_code=script_code,
        target_url='https://www.formula1.com/en/racing/2025.html'
    )
    
    print(f"\nResult success: {result.success}")
    print(f"Total records: {len(result.data)}")


def example_multi_source():
    """Example: Execute a script against multiple data sources."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Multiple Data Sources Execution")
    print("=" * 80 + "\n")
    
    # Create integration
    integration = create_integration(use_colors=True)
    
    # Script that handles different sources
    script_code = '''
def scrape_data(url):
    """Scrape data from various F1 news sources."""
    from datetime import datetime
    
    # Simulate different data based on source
    if 'formula1.com' in url:
        data = [
            {'title': 'Official F1 News 1', 'source': 'F1 Official'},
            {'title': 'Official F1 News 2', 'source': 'F1 Official'}
        ]
        method = 'cards'
        confidence = 'high'
    elif 'skysports' in url:
        data = [
            {'title': 'Sky Sports F1 Update', 'source': 'Sky Sports'},
            {'title': 'Race Preview', 'source': 'Sky Sports'},
            {'title': 'Driver Interview', 'source': 'Sky Sports'}
        ]
        method = 'articles'
        confidence = 'medium'
    elif 'motorsport' in url:
        data = [
            {'title': 'Motorsport Analysis', 'source': 'Motorsport.com'}
        ]
        method = 'generic'
        confidence = 'low'
    else:
        data = []
        method = 'unknown'
        confidence = 'low'
    
    return {
        'data': data,
        'metadata': {
            'source_url': url,
            'total_count': len(data),
            'scraping_method': method,
            'confidence': confidence
        }
    }
'''
    
    # Multiple sources
    urls = [
        'https://www.formula1.com/en/latest.html',
        'https://www.skysports.com/f1/news',
        'https://www.motorsport.com/f1/news/'
    ]
    
    # Execute against all sources
    result = integration.execute_code(
        script_code=script_code,
        target_urls=urls
    )
    
    # Display results
    integration.display_results(result)
    
    print(f"\nResult success: {result.success}")
    print(f"Total records: {len(result.data)}")
    print(f"Sources processed: {len(result.source_results)}")
    for sr in result.source_results:
        print(f"  - {sr.source_url}: {sr.record_count} records")


def example_error_handling():
    """Example: Demonstrate error handling."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Error Handling")
    print("=" * 80 + "\n")
    
    integration = create_integration(use_colors=True)
    
    # Script with a runtime error
    error_script = '''
def scrape_data(url):
    # This will cause a runtime error
    result = 1 / 0
    return {'data': []}
'''
    
    result = integration.execute_and_display(
        script_code=error_script,
        target_url='http://example.com'
    )
    
    print(f"\nResult success: {result.success}")
    print(f"Errors: {len(result.errors)}")


def example_security_sandbox():
    """Example: Demonstrate security sandbox blocking forbidden operations."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Security Sandbox")
    print("=" * 80 + "\n")
    
    integration = create_integration(use_colors=True)
    
    # Script attempting forbidden operation
    forbidden_script = '''
import os
def scrape_data(url):
    # This will be blocked by the sandbox
    os.system('echo "This should not run"')
    return {'data': []}
'''
    
    result = integration.execute_and_display(
        script_code=forbidden_script,
        target_url='http://example.com'
    )
    
    print(f"\nResult success: {result.success}")
    print(f"Security blocked: {'Security error' in str(result.errors)}")


def example_json_output():
    """Example: Output results as JSON."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: JSON Output Format")
    print("=" * 80 + "\n")
    
    integration = create_integration(use_colors=False)
    
    script_code = '''
def scrape_data(url):
    return {
        'data': [{'id': 1, 'name': 'Test Item'}],
        'metadata': {'total_count': 1, 'source_url': url}
    }
'''
    
    result = integration.execute_code(script_code, 'http://example.com')
    
    # Display as JSON
    integration.display_results(result, format_type='json')


def main():
    """Run all examples."""
    # Configure logging
    configure_logging(level=logging.WARNING)  # Reduce noise for examples
    
    print("=" * 80)
    print("AI-SCRAPING LAYER INTEGRATION EXAMPLES")
    print("=" * 80)
    
    # Run examples
    example_single_source()
    example_multi_source()
    example_error_handling()
    example_security_sandbox()
    example_json_output()
    
    print("\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 80)


if __name__ == '__main__':
    main()
