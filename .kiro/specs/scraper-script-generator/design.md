# Design Document: Scraper Script Generator

## Overview

The Scraper Script Generator is a Python-based component that uses AI (DeepSeek) to automatically generate executable BeautifulSoup scraper scripts from user requirements. This feature bridges the AI layer and the scraping layer, transforming natural language descriptions into working Python code that can extract data from websites.

The system takes form inputs (data description, source URL, desired fields) and generates a complete Python script that:

- Uses BeautifulSoup4 and requests for scraping
- Follows the scraping layer's configuration (timeout, user-agent)
- Returns data in the ScrapingResult format
- Includes proper error handling and CSS selectors

This design extends the existing AI Response Generator to produce executable code instead of mock JSON data, enabling true web scraping capabilities.

## Architecture

The system consists of five main layers:

```
┌─────────────────────────────────────────┐
│         Streamlit UI Layer              │
│  (components/form.py, results.py)       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Scraper Script Generator Layer         │
│  - Script Prompt Construction           │
│  - Script Validation                    │
│  - Configuration Integration            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      DeepSeek Client Layer              │
│  - API Authentication                   │
│  - Request/Response Handling            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         DeepSeek API                    │
│  (Generates Python Script)              │
└─────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Script Execution Layer             │
│  (scraping_layer/script_execution)      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Scraping Engine                    │
│  (Executes Generated Script)            │
└─────────────────────────────────────────┘
```

**Design Rationale:**

- Reuses existing DeepSeek Client for AI communication
- Separates script generation from script execution for safety
- Integrates scraping layer configuration to ensure compatibility
- Validates generated scripts before execution
- Maintains clear separation between AI generation and scraping execution

## Components and Interfaces

### 1. Scraper Script Generator (`ai_layer/scraper_script_generator.py`)

**Responsibility:** Generate executable BeautifulSoup scripts from form inputs using AI.

**Interface:**

```python
class ScraperScriptGenerator:
    def __init__(
        self,
        deepseek_client: DeepSeekClient,
        scraping_config: ScrapingConfig
    ):
        """
        Initialize the script generator.

        Args:
            deepseek_client: Configured DeepSeek API client
            scraping_config: Scraping layer configuration
        """

    def generate_script(
        self,
        form_input: Dict[str, Any],
        model: str = "deepseek-chat",
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> GeneratedScript:
        """
        Generate a BeautifulSoup scraper script from form inputs.

        Args:
            form_input: Dictionary containing:
                - data_description: str (required)
                - data_source: str (required - target URL)
                - desired_fields: str (optional, newline-separated)
                - response_structure: str (optional, JSON string)
                - update_frequency: str (required)
            model: DeepSeek model to use
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Maximum tokens in response

        Returns:
            GeneratedScript object with Python code and metadata

        Raises:
            ValidationError: When form inputs are invalid
            GenerationError: When AI generation fails
            ScriptValidationError: When generated script is invalid
        """

    def _build_script_prompt(
        self,
        form_input: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Construct prompt messages for script generation.

        Includes:
        - Scraping layer configuration (timeout, user-agent)
        - Required libraries (BeautifulSoup4, requests)
        - Expected function signature and return format
        - User requirements (URL, fields, structure)
        """

    def _validate_script(self, script_code: str) -> ScriptValidationResult:
        """
        Validate generated Python script.

        Checks:
        - Syntax correctness (compile check)
        - Required imports present
        - Main function exists with correct signature
        - No dangerous operations (exec, eval, os.system)
        """
```

### 2. Script Prompt Builder (`ai_layer/script_prompt_builder.py`)

**Responsibility:** Construct prompts that include scraping layer configuration and requirements.

**Interface:**

```python
class ScriptPromptBuilder:
    """Builds prompts for generating scraper scripts."""

    SYSTEM_PROMPT = """You are an expert Python web scraping engineer. Generate production-ready BeautifulSoup scraper scripts.

CRITICAL REQUIREMENTS:
1. Use ONLY BeautifulSoup4 and requests libraries
2. Follow the exact function signature provided
3. Return data in the specified format (ScrapingResult-compatible)
4. Include comprehensive error handling
5. Use the provided timeout and user-agent configuration
6. Generate CSS selectors appropriate for the target website
7. Return ONLY valid Python code - NO markdown, NO explanations
8. Include comments explaining the scraping logic

SAFETY:
- No dangerous operations (exec, eval, os.system, subprocess)
- No file system operations
- No network requests except to the specified URL
- Proper exception handling for all operations"""

    def build_script_prompt(
        self,
        form_input: Dict[str, Any],
        scraping_config: ScrapingConfig
    ) -> List[Dict[str, str]]:
        """
        Build prompt for script generation.

        Includes:
        - System prompt with requirements
        - User requirements (data description, URL, fields)
        - Scraping configuration (timeout, user-agent)
        - Expected function signature
        - Example output format
        """
```

### 3. Script Validator (`ai_layer/script_validator.py`)

**Responsibility:** Validate generated scripts for safety and correctness.

**Interface:**

```python
class ScriptValidator:
    """Validates generated scraper scripts."""

    REQUIRED_IMPORTS = ['bs4', 'requests']
    FORBIDDEN_OPERATIONS = ['exec', 'eval', 'os.system', 'subprocess', '__import__']

    def validate_script(self, script_code: str) -> ScriptValidationResult:
        """
        Validate a generated script.

        Checks:
        1. Syntax correctness (compile check)
        2. Required imports present
        3. Main function exists
        4. No forbidden operations
        5. Function signature matches expected

        Returns:
            ScriptValidationResult with success status and details
        """

    def check_syntax(self, script_code: str) -> Tuple[bool, Optional[str]]:
        """Check if script has valid Python syntax."""

    def check_imports(self, script_code: str) -> Tuple[bool, List[str]]:
        """Check if required imports are present."""

    def check_forbidden_operations(self, script_code: str) -> Tuple[bool, List[str]]:
        """Check for dangerous operations."""

    def check_function_signature(self, script_code: str) -> Tuple[bool, Optional[str]]:
        """Check if main scraping function exists with correct signature."""
```

### 4. Generated Script Models (`ai_layer/script_models.py`)

**Data Models:**

```python
@dataclass
class GeneratedScript:
    """Container for AI-generated scraper script."""
    script_code: str  # The Python code
    metadata: ScriptMetadata
    validation_result: ScriptValidationResult
    raw_output: str  # Original AI output

@dataclass
class ScriptMetadata:
    """Metadata about script generation."""
    timestamp: datetime
    model: str
    tokens_used: int
    generation_time_ms: int
    target_url: str
    required_fields: List[str]

@dataclass
class ScriptValidationResult:
    """Result of script validation."""
    is_valid: bool
    syntax_valid: bool
    imports_valid: bool
    no_forbidden_ops: bool
    function_signature_valid: bool
    errors: List[str]
    warnings: List[str]

class ScriptValidationError(Exception):
    """Raised when script validation fails."""
```

### 5. Script Execution Integration (`scraping_layer/script_execution/ai_script_executor.py`)

**Responsibility:** Execute AI-generated scripts safely within the scraping layer.

**Interface:**

```python
class AIScriptExecutor:
    """Executes AI-generated scraper scripts."""

    def __init__(self, scraping_engine: ScrapingEngine):
        """Initialize with scraping engine."""

    async def execute_generated_script(
        self,
        generated_script: GeneratedScript,
        timeout: int = 30
    ) -> ScriptResult:
        """
        Execute an AI-generated script safely.

        Args:
            generated_script: Validated script from generator
            timeout: Execution timeout in seconds

        Returns:
            ScriptResult with extracted data or errors

        Raises:
            ScriptExecutionError: When execution fails
        """

    def _create_safe_execution_environment(self) -> Dict[str, Any]:
        """Create restricted execution environment."""

    def _execute_in_sandbox(
        self,
        script_code: str,
        url: str,
        timeout: int
    ) -> Dict[str, Any]:
        """Execute script in sandboxed environment."""
```

## Data Models

### Form Input Structure (Extended)

```python
{
    "data_description": str,      # Required: What data to scrape
    "data_source": str,            # Required: Target URL for scraping
    "desired_fields": str,         # Optional: Newline-separated field names
    "response_structure": str,     # Optional: JSON structure template
    "update_frequency": str        # Required: How often data updates
}
```

### Generated Script Structure

```python
# Example generated script
"""
Scraper script for: [data_description]
Target URL: [data_source]
Generated: [timestamp]
"""

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
        headers = {
            'User-Agent': '[configured_user_agent]'
        }

        # Fetch HTML
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, 'lxml')

        # Extract data using CSS selectors
        data = []

        # [Generated selector logic based on user requirements]
        items = soup.select('[css_selector]')

        for item in items:
            record = {
                'field1': item.select_one('[selector1]').get_text(strip=True),
                'field2': item.select_one('[selector2]').get_text(strip=True),
                # ... more fields
            }
            data.append(record)

        # Return in expected format
        return {
            'data': data,
            'metadata': {
                'total_count': len(data),
                'source_url': url,
                'scraped_at': datetime.utcnow().isoformat(),
                'update_frequency': '[update_frequency]'
            }
        }

    except requests.RequestException as e:
        return {
            'error': 'network_error',
            'message': f'Failed to fetch URL: {str(e)}',
            'data': []
        }
    except Exception as e:
        return {
            'error': 'scraping_error',
            'message': f'Failed to extract data: {str(e)}',
            'data': []
        }

# Entry point
if __name__ == '__main__':
    result = scrape_data('[target_url]')
    print(result)
```

### Script Validation Result Structure

```python
{
    "is_valid": bool,
    "syntax_valid": bool,
    "imports_valid": bool,
    "no_forbidden_ops": bool,
    "function_signature_valid": bool,
    "errors": [
        "Syntax error on line 15: unexpected indent",
        "Missing required import: bs4"
    ],
    "warnings": [
        "Consider adding timeout handling",
        "CSS selector may be too specific"
    ]
}
```

## Configuration

### Scraping Layer Configuration Integration

The script generator reads configuration from the scraping layer:

```python
# From scraping_layer/config.py
@dataclass
class NetworkConfig:
    request_timeout: int = 30
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Script generator uses this configuration
scraping_config = get_config()

# Includes in prompt:
# - Timeout: {scraping_config.network.request_timeout}
# - User-Agent: {scraping_config.network.user_agent}
```

### Environment Variables

```python
# Existing AI layer configuration
DEEPSEEK_API_KEY: str          # Required: API key
DEEPSEEK_MODEL: str            # Optional: Default "deepseek-chat"
DEEPSEEK_TEMPERATURE: float    # Optional: Default 0.3 (lower for code)
DEEPSEEK_MAX_TOKENS: int       # Optional: Default 4000 (for scripts)

# Scraping layer configuration (already exists)
SCRAPING_REQUEST_TIMEOUT: int  # Optional: Default 30
SCRAPING_USER_AGENT: str       # Optional: Default Mozilla string
```

## Correctness Properties

_A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees._

### Property 1: Form Field Extraction Completeness

_For any_ form input dictionary containing the required fields (data_description, data_source, desired_fields, response_structure, update_frequency), the script generator should extract all fields without data loss.
**Validates: Requirements 1.1**

### Property 2: Target URL Inclusion

_For any_ provided data_source URL, the generated script should include that URL as the target for scraping operations.
**Validates: Requirements 1.2**

### Property 3: Empty URL Handling

_For any_ form input with an empty data_source, the constructed prompt should include instructions for the AI to suggest appropriate data sources.
**Validates: Requirements 1.3**

### Property 4: Prompt Construction Completeness

_For any_ form input, the constructed prompt should include all non-empty user-provided information (data description, URL, desired fields, response structure) and system instructions for script generation.
**Validates: Requirements 1.4, 1.5, 6.1, 6.4, 6.5, 6.6, 6.7**

### Property 5: Required Imports Presence

_For any_ generated script, the script should contain imports for both BeautifulSoup (from bs4) and requests libraries.
**Validates: Requirements 2.1, 2.2, 4.3**

### Property 6: Error Handling Presence

_For any_ generated script, the code should include try-except blocks or conditional checks for handling network failures and missing HTML elements.
**Validates: Requirements 2.3, 2.4**

### Property 7: Main Function Signature

_For any_ generated script, the script should include a callable main function that accepts a URL parameter.
**Validates: Requirements 3.1, 4.4**

### Property 8: Code Documentation

_For any_ generated script, the code should include comments explaining the scraping logic.
**Validates: Requirements 3.3**

### Property 9: Syntax Validation

_For any_ generated script, the validator should successfully compile the code using Python's compile() function, confirming syntactic correctness.
**Validates: Requirements 4.1**

### Property 10: Validation Error Messages

_For any_ script that fails validation, the validator should return a non-empty error message with specific details about the failure.
**Validates: Requirements 4.5, 8.1**

### Property 11: Script Executor Interface

_For any_ generated script string, the script executor should accept it as input and execute it safely within a controlled environment.
**Validates: Requirements 5.2**

### Property 12: Execution Result Format

_For any_ script execution (successful or failed), the executor should return a ScrapingResult object with the appropriate success status and data or errors.
**Validates: Requirements 5.3**

### Property 13: Configuration Integration

_For any_ script generation request, the generator should read the scraping layer's NetworkConfig and include the configured timeout and user-agent in both the prompt and the generated script.
**Validates: Requirements 6.2, 6.3, 7.1, 7.2, 7.3**

### Property 14: Script Return Structure

_For any_ successfully executed script, the return value should be a dictionary containing a "data" key with a list of records and a "metadata" key with scraping metadata.
**Validates: Requirements 9.1, 9.2**

### Property 15: Record Field Consistency

_For any_ script execution that returns multiple records, all records in the data list should have the same set of field names.
**Validates: Requirements 9.5**

## Error Handling

### Error Categories and Handling Strategy

**1. Form Input Validation Errors**

- **Trigger:** Missing required fields (data_description, data_source), invalid JSON structure
- **Exception:** `ValidationError`
- **User Message:** "Invalid input: {field_name} is required" or "Invalid JSON structure provided"
- **Recovery:** Display error inline with form, allow user to correct

**2. Script Generation Errors**

- **Trigger:** AI fails to generate valid Python code, API timeout, rate limiting
- **Exception:** `GenerationError`
- **User Message:** "Failed to generate scraper script. Please try again or simplify your requirements."
- **Recovery:** Allow retry, suggest simplifying requirements

**3. Script Validation Errors**

- **Trigger:** Generated script has syntax errors, missing imports, forbidden operations
- **Exception:** `ScriptValidationError`
- **User Message:** "Generated script failed validation: {specific_errors}"
- **Recovery:** Attempt automatic regeneration (1 retry), then ask user for guidance

**4. Script Execution Errors**

- **Trigger:** Runtime errors during script execution, network failures, timeout
- **Exception:** `ScriptExecutionError`
- **User Message:** "Script execution failed: {error_details}"
- **Recovery:** Display error with context, suggest checking URL or regenerating script

**5. Network Errors**

- **Trigger:** Target URL unreachable, DNS failure, connection timeout
- **Exception:** `NetworkError`
- **User Message:** "Unable to reach {url}. Please verify the URL is correct and accessible."
- **Recovery:** Allow user to correct URL and retry

**6. Safety Violations**

- **Trigger:** Generated script contains forbidden operations (exec, eval, os.system)
- **Exception:** `SecurityError`
- **User Message:** "Generated script contains unsafe operations and cannot be executed."
- **Recovery:** Regenerate script with stricter safety constraints

### Error Handling Flow

```
Form Input → Validation → Script Generation → Script Validation → Script Execution
     ↓            ↓              ↓                   ↓                  ↓
  Validate    Validate      Generate Code      Validate Code      Execute Code
   Form       JSON          via AI             Syntax/Safety      in Sandbox
     ↓            ↓              ↓                   ↓                  ↓
   Error      Error          Error              Error              Error
  Message    Message        Message            Message            Message
```

### Retry Strategy

```python
# Script generation retry configuration
MAX_GENERATION_RETRIES = 2
MAX_VALIDATION_RETRIES = 1

# Execution timeout
SCRIPT_EXECUTION_TIMEOUT = 60  # seconds

def handle_generation_failure(attempt: int) -> bool:
    """Determine if generation should be retried."""
    if attempt < MAX_GENERATION_RETRIES:
        # Retry with adjusted temperature (more deterministic)
        return True
    return False

def handle_validation_failure(attempt: int) -> bool:
    """Determine if validation failure should trigger regeneration."""
    if attempt < MAX_VALIDATION_RETRIES:
        # Regenerate with stricter safety constraints
        return True
    return False
```

### Safety Constraints

**Script Validation Safety Checks:**

1. **Syntax Check:** Compile script to ensure valid Python
2. **Import Check:** Verify only allowed imports (bs4, requests, typing, datetime)
3. **Forbidden Operations:** Scan for dangerous functions (exec, eval, **import**, os.system, subprocess)
4. **Function Signature:** Verify main function exists with correct parameters
5. **Return Type:** Check function returns dictionary structure

**Execution Safety:**

1. **Timeout Enforcement:** Kill script execution after timeout
2. **Resource Limits:** Limit memory and CPU usage (if possible)
3. **Network Restrictions:** Only allow requests to specified URL
4. **Sandboxed Environment:** Execute in restricted namespace

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests:

**Unit Tests** verify specific examples, edge cases, and error conditions:

- Specific malformed scripts (missing imports, syntax errors)
- Known URL patterns and field configurations
- Error message formatting
- Integration with scraping layer
- Edge cases like empty fields, special characters

**Property-Based Tests** verify universal properties across all inputs:

- Form field extraction works for any valid input dictionary
- Prompt construction includes all provided information
- Script validation correctly identifies syntax errors
- Generated scripts contain required imports
- Configuration is properly integrated

Both testing approaches are complementary and necessary. Unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across the input space.

### Testing Framework

**Property-Based Testing Library:** [Hypothesis](https://hypothesis.readthedocs.io/) for Python

- Industry-standard PBT library for Python
- Excellent integration with pytest
- Smart test case generation and shrinking
- Built-in strategies for common data types

**Unit Testing Framework:** pytest

- Standard Python testing framework
- Good integration with Hypothesis
- Clear test output and debugging

### Test Configuration

**Property Test Requirements:**

- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property
- Tag format: `# Feature: scraper-script-generator, Property {number}: {property_text}`

**Example Property Test:**

```python
from hypothesis import given, strategies as st
import pytest

# Feature: scraper-script-generator, Property 1: Form Field Extraction Completeness
@given(st.dictionaries(
    keys=st.sampled_from(['data_description', 'data_source', 'desired_fields',
                          'response_structure', 'update_frequency']),
    values=st.text(min_size=1),
    min_size=5
))
def test_form_field_extraction_property(form_input):
    """For any form input with required fields, extraction should preserve all data"""
    # Arrange
    generator = ScraperScriptGenerator(mock_client, mock_config)

    # Act
    extracted = generator._extract_form_fields(form_input)

    # Assert
    assert all(key in extracted for key in form_input.keys())
    assert all(extracted[key] == form_input[key] for key in form_input.keys())
```

### Test Coverage Requirements

**Component Test Coverage:**

1. **Scraper Script Generator (ai_layer/scraper_script_generator.py)**

   - Unit tests: Specific form inputs, error scenarios, integration with DeepSeek
   - Property tests: Field extraction (Property 1), URL inclusion (Property 2), prompt completeness (Property 4), configuration integration (Property 13)

2. **Script Prompt Builder (ai_layer/script_prompt_builder.py)**

   - Unit tests: Specific prompt formats, configuration formatting
   - Property tests: Prompt completeness (Property 4), configuration inclusion (Property 13)

3. **Script Validator (ai_layer/script_validator.py)**

   - Unit tests: Specific syntax errors, forbidden operations, known malformed scripts
   - Property tests: Syntax validation (Property 9), import checking (Property 5), error messages (Property 10)

4. **AI Script Executor (scraping_layer/script_execution/ai_script_executor.py)**

   - Unit tests: Timeout handling, specific execution errors, sandbox setup
   - Property tests: Executor interface (Property 11), result format (Property 12)

5. **Integration Tests**
   - End-to-end: Form input → Script generation → Validation → Execution → Result
   - Error scenarios: Invalid URLs, unreachable sites, malformed scripts
   - Configuration: Different timeout and user-agent settings

### Mocking Strategy

**External Dependencies to Mock:**

- DeepSeek API HTTP requests (use `responses` library or `unittest.mock`)
- Network requests in generated scripts (mock `requests.get`)
- Scraping layer configuration (mock `get_config()`)
- File system operations (if any)

**Do Not Mock:**

- Script validation logic (syntax checking, import detection)
- Prompt construction logic
- Data structure transformations
- Error handling logic

### Integration Testing

Integration tests should verify:

- Complete flow from form submission to script execution
- Actual DeepSeek API calls (in separate integration test suite)
- Real script execution with actual websites (using test URLs)
- Error handling across component boundaries
- Configuration propagation through all layers

Integration tests should be marked separately and run less frequently than unit/property tests.

## Implementation Notes

### Phase 1 Scope

This design focuses on:

- Generating BeautifulSoup scripts for static HTML scraping
- Basic CSS selector generation
- Single-page scraping (no pagination)
- Synchronous execution

### Future Enhancements (Out of Scope)

- Dynamic website scraping (JavaScript rendering)
- Pagination handling
- Rate limiting and politeness delays
- Selector optimization and testing
- Script caching and reuse
- Multi-page scraping workflows

### Security Considerations

1. **Code Execution Safety:** All generated scripts must be validated before execution
2. **Sandbox Environment:** Scripts should execute in restricted environment
3. **Resource Limits:** Enforce timeout and memory limits
4. **Input Sanitization:** Validate all user inputs before passing to AI
5. **API Key Protection:** Never include API keys in generated scripts

### Performance Considerations

1. **Script Generation Time:** Target < 5 seconds for script generation
2. **Validation Time:** Target < 1 second for script validation
3. **Execution Timeout:** Default 60 seconds, configurable
4. **Caching:** Consider caching generated scripts for identical inputs (future)

### Dependencies

**New Dependencies:**

- None (reuses existing dependencies)

**Existing Dependencies:**

- `requests`: HTTP requests (already in scraping layer)
- `beautifulsoup4`: HTML parsing (already in scraping layer)
- `lxml`: BeautifulSoup parser (already in scraping layer)
- `aiohttp`: Async HTTP (already in scraping layer)

**Development Dependencies:**

- `pytest`: Testing framework
- `hypothesis`: Property-based testing
- `pytest-asyncio`: Async test support
