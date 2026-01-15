# Scraper Script Generator Examples

This directory contains examples and tests for the Scraper Script Generator feature.

## Overview

The Scraper Script Generator uses AI (DeepSeek) to automatically generate executable BeautifulSoup scraper scripts from natural language descriptions. This bridges the AI layer and scraping layer, enabling automatic web scraping based on user requirements.

## Features

- **AI-Powered Generation**: Uses DeepSeek to generate Python scraping code
- **Safety Validation**: Validates scripts for syntax, imports, and forbidden operations
- **Configuration Integration**: Automatically includes scraping layer configuration (timeout, user-agent)
- **Error Handling**: Comprehensive error handling for network and parsing errors
- **Retry Logic**: Automatically retries generation if validation fails

## Files

### `script_generation_example.py`

Complete example demonstrating:

- Configuration setup
- Script generation from form inputs
- Validation results
- Saving generated scripts
- Error handling

**Usage:**

```bash
# Set your DeepSeek API key
export DEEPSEEK_API_KEY="your-api-key-here"

# Run the example
python ai_layer/examples/script_generation_example.py
```

### `test_script_generation.py`

Integration tests for script generation components:

- Script models instantiation
- Script validator with various test cases
- Prompt builder functionality

**Usage:**

```bash
python ai_layer/examples/test_script_generation.py
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Required
export DEEPSEEK_API_KEY="your-api-key-here"

# Optional (with defaults)
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export DEEPSEEK_MODEL="deepseek-chat"
export SCRAPING_REQUEST_TIMEOUT="30"
export SCRAPING_USER_AGENT="Mozilla/5.0 ..."
```

### 3. Generate a Script

```python
from ai_layer import (
    DeepSeekConfig,
    DeepSeekClient,
    ScraperScriptGenerator
)
from scraping_layer.config import ScrapingConfig

# Load configuration
deepseek_config = DeepSeekConfig.from_env()
scraping_config = ScrapingConfig.from_env()

# Initialize components
client = DeepSeekClient(
    api_key=deepseek_config.api_key,
    base_url=deepseek_config.base_url
)

generator = ScraperScriptGenerator(
    deepseek_client=client,
    scraping_config=scraping_config
)

# Prepare form input
form_input = {
    'data_description': 'Product listings with prices',
    'data_source': 'https://example.com/products',
    'desired_fields': 'product_name\nprice\nrating',
    'response_structure': '',
    'update_frequency': 'Daily'
}

# Generate script
generated_script = generator.generate_script(form_input)

# Check if valid
if generated_script.is_valid:
    print("Script generated successfully!")
    print(generated_script.script_code)
else:
    print("Validation errors:", generated_script.validation_result.errors)
```

## Form Input Format

The script generator expects a dictionary with these fields:

```python
{
    'data_description': str,      # Required: What data to scrape
    'data_source': str,            # Required: Target URL
    'desired_fields': str,         # Optional: Newline-separated field names
    'response_structure': str,     # Optional: JSON structure template
    'update_frequency': str        # Required: Update frequency
}
```

## Generated Script Format

Generated scripts follow this structure:

```python
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any
from datetime import datetime

def scrape_data(url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Scrape data from the target website.

    Args:
        url: Target URL to scrape
        timeout: Request timeout in seconds

    Returns:
        Dictionary with 'data' list and 'metadata' dict
    """
    try:
        # Configure headers
        headers = {'User-Agent': '...'}

        # Fetch HTML
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, 'lxml')

        # Extract data
        data = []
        # ... scraping logic ...

        return {
            'data': data,
            'metadata': {
                'total_count': len(data),
                'source_url': url,
                'scraped_at': datetime.utcnow().isoformat(),
                'update_frequency': 'Daily'
            }
        }

    except requests.RequestException as e:
        return {
            'data': [],
            'metadata': {
                'error': 'network_error',
                'message': f'Failed to fetch URL: {str(e)}'
            }
        }
    except Exception as e:
        return {
            'data': [],
            'metadata': {
                'error': 'scraping_error',
                'message': f'Failed to extract data: {str(e)}'
            }
        }
```

## Validation Checks

Generated scripts are validated for:

1. **Syntax Correctness**: Valid Python syntax
2. **Required Imports**: `bs4` and `requests` must be imported
3. **No Forbidden Operations**: No `exec`, `eval`, `os.system`, `subprocess`, etc.
4. **Function Signature**: Must have `scrape_data(url: str, ...)` function
5. **Return Format**: Should return dict with 'data' and 'metadata' keys

## Error Handling

The generator handles various error scenarios:

- **ValidationError**: Invalid form inputs
- **ScriptGenerationError**: AI generation fails
- **ScriptValidationError**: Generated script fails validation
- **DeepSeekAPIError**: API communication errors

Example:

```python
try:
    script = generator.generate_script(form_input)
except ScriptGenerationError as e:
    print(f"Generation failed: {e}")
except ScriptValidationError as e:
    print(f"Validation failed: {e.validation_result.errors}")
```

## Configuration

### DeepSeek Configuration

```python
DEEPSEEK_API_KEY: str          # Required
DEEPSEEK_BASE_URL: str         # Default: "https://api.deepseek.com"
DEEPSEEK_MODEL: str            # Default: "deepseek-chat"
DEEPSEEK_TEMPERATURE: float    # Default: 0.3 (for code generation)
DEEPSEEK_MAX_TOKENS: int       # Default: 4000
```

### Scraping Configuration

```python
SCRAPING_REQUEST_TIMEOUT: int  # Default: 30 seconds
SCRAPING_USER_AGENT: str       # Default: Mozilla string
```

## Best Practices

1. **Provide Clear Descriptions**: The more specific your data description, the better the generated script
2. **Specify Target URL**: Always provide the actual URL you want to scrape
3. **List Required Fields**: Explicitly list all fields you need extracted
4. **Review Generated Scripts**: Always review scripts before running them
5. **Test Incrementally**: Test scripts on sample pages before full deployment
6. **Handle Errors**: Generated scripts include error handling, but always monitor execution

## Troubleshooting

### Script Generation Fails

- Check your DEEPSEEK_API_KEY is valid
- Verify internet connection
- Try simplifying the data description
- Check API rate limits

### Validation Errors

- Review validation error messages
- Check if required imports are present
- Verify function signature is correct
- Look for forbidden operations

### Script Execution Fails

- Verify target URL is accessible
- Check if website structure matches expectations
- Review CSS selectors in generated code
- Test with different timeout values

## Next Steps

After generating a script:

1. **Review the Code**: Check the generated CSS selectors and logic
2. **Test Manually**: Run the script standalone to verify it works
3. **Integrate**: Use with the scraping layer for automated execution
4. **Monitor**: Track execution results and adjust as needed
5. **Iterate**: Regenerate with refined requirements if needed

## Support

For issues or questions:

- Check the main README.md
- Review the spec documents in `.kiro/specs/scraper-script-generator/`
- Examine the design document for architecture details
