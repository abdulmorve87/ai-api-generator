# Design Document: Scraped Data Parser

## Overview

The Scraped Data Parser is a Python-based component that transforms raw scraped data from the scraping layer into structured JSON responses based on user requirements. This feature acts as an intelligent data transformation layer, using DeepSeek AI to parse, extract, and format scraped content according to user-specified fields and structure.

The system integrates with the existing scraping layer (which returns `ScrapingResult` objects) and the AI layer (which provides DeepSeek client capabilities). It bridges the gap between raw HTML/text data and clean, structured JSON API responses by leveraging AI to understand context and extract relevant information.

## Architecture

The system follows a pipeline architecture with clear data flow:

```
┌─────────────────────────────────────────┐
│         Streamlit UI Layer              │
│  (app.py, components/results.py)        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Scraping Layer (Existing)          │
│  - ScrapingEngine                       │
│  - Returns ScrapingResult               │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    Scraped Data Parser (NEW)            │
│  - Data Extraction                      │
│  - Prompt Construction                  │
│  - AI-Powered Parsing                   │
│  - Response Validation                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      DeepSeek Client (Existing)         │
│  - API Communication                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         DeepSeek API                    │
└─────────────────────────────────────────┘
```

**Design Rationale:**

- Reuses existing DeepSeek client infrastructure for consistency
- Integrates seamlessly with existing scraping layer output format
- Separates data extraction logic from AI prompting for testability
- Validates both input (scraped data) and output (parsed JSON) for reliability
- Maintains clear separation of concerns for future extensibility

## Components and Interfaces

### 1. Scraped Data Parser (`ai_layer/scraped_data_parser.py`)

**Responsibility:** Orchestrate the transformation of scraped data into structured JSON.

**Interface:**

```python
class ScrapedDataParser:
    def __init__(self, deepseek_client: DeepSeekClient):
        """Initialize parser with DeepSeek client"""

    def parse_scraped_data(
        self,
        scraping_result: ScrapingResult,
        user_requirements: Dict[str, Any]
    ) -> ParsedDataResponse:
        """
        Parse scraped data into structured JSON based on user requirements.

        Args:
            scraping_result: Result from scraping layer containing raw data
            user_requirements: Dictionary containing:
                - data_description: str
                - data_source: str (optional)
                - desired_fields: str (optional, newline-separated)
                - response_structure: str (optional, JSON string)
                - update_frequency: str

        Returns:
            ParsedDataResponse with structured JSON and metadata

        Raises:
            EmptyDataError: When scraping_result contains no data
            ParsingError: When AI fails to parse the data
            ValidationError: When parsed output is invalid
        """

    def _extract_text_from_scraped_data(
        self,
        scraping_result: ScrapingResult
    ) -> str:
        """
        Extract text content from ScrapingResult for AI processing.

        Handles various data formats (HTML, JSON, text) and extracts
        relevant content while removing noise.

        Args:
            scraping_result: Result from scraping layer

        Returns:
            Cleaned text representation of scraped data
        """

    def _build_parsing_prompt(
        self,
        scraped_text: str,
        user_requirements: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Construct prompt for AI to parse scraped data.

        Args:
            scraped_text: Extracted text from scraped data
            user_requirements: User's desired output format

        Returns:
            List of message dicts for DeepSeek API
        """

    def _validate_parsed_response(
        self,
        ai_output: str,
        user_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate AI-parsed response meets requirements.

        Args:
            ai_output: Raw AI response
            user_requirements: User's requirements

        Returns:
            Validated and parsed JSON object

        Raises:
            ValidationError: When response is invalid
        """
```

**Implementation Details:**

- Reuses `DeepSeekClient` from existing AI layer
- Handles `ScrapingResult` objects from scraping layer
- Extracts text from various data formats (HTML, JSON, plain text)
- Constructs specialized prompts for data parsing (different from mock generation)
- Validates output contains requested fields
- Implements retry logic for parsing failures

### 2. Data Extraction Utility (`ai_layer/data_extractor.py`)

**Responsibility:** Extract and clean text content from scraped data.

**Interface:**

```python
class DataExtractor:
    """Utility for extracting clean text from scraped data."""

    @staticmethod
    def extract_from_scraping_result(result: ScrapingResult) -> str:
        """
        Extract text from ScrapingResult.

        Args:
            result: ScrapingResult from scraping layer

        Returns:
            Cleaned text representation

        Raises:
            EmptyDataError: When result contains no data
        """

    @staticmethod
    def extract_from_html(html: str) -> str:
        """
        Extract text from HTML content.

        Uses BeautifulSoup to parse HTML and extract text,
        removing scripts, styles, and other noise.

        Args:
            html: Raw HTML string

        Returns:
            Cleaned text content
        """

    @staticmethod
    def extract_from_dict(data: Dict[str, Any]) -> str:
        """
        Convert dictionary data to readable text format.

        Args:
            data: Dictionary data

        Returns:
            Formatted text representation
        """

    @staticmethod
    def truncate_if_needed(text: str, max_length: int = 50000) -> str:
        """
        Truncate text if it exceeds maximum length.

        Args:
            text: Text to truncate
            max_length: Maximum allowed length

        Returns:
            Truncated text with indicator if truncated
        """
```

**Implementation Details:**

- Uses BeautifulSoup4 for HTML parsing
- Removes script tags, style tags, and comments
- Handles nested data structures (lists of dicts)
- Implements intelligent truncation for large datasets
- Preserves data structure information for AI context

### 3. Parsing Prompt Builder (`ai_layer/parsing_prompt_builder.py`)

**Responsibility:** Construct specialized prompts for data parsing.

**Interface:**

```python
class ParsingPromptBuilder:
    """Builds prompts for parsing scraped data."""

    def build_parsing_prompt(
        self,
        scraped_text: str,
        user_requirements: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Build prompt messages for data parsing.

        Args:
            scraped_text: Extracted text from scraped data
            user_requirements: User's requirements

        Returns:
            List of message dicts for DeepSeek API
        """

    def _build_system_prompt(self) -> str:
        """
        Build system prompt for data parsing.

        Returns:
            System prompt instructing AI on parsing task
        """

    def _build_user_prompt(
        self,
        scraped_text: str,
        user_requirements: Dict[str, Any]
    ) -> str:
        """
        Build user prompt with scraped data and requirements.

        Args:
            scraped_text: Extracted text
            user_requirements: User's requirements

        Returns:
            User prompt string
        """

    def _parse_desired_fields(self, fields_text: str) -> List[str]:
        """Parse newline-separated field list"""

    def _validate_json_structure(self, structure_text: str) -> Dict:
        """Validate and parse JSON structure template"""
```

**Prompt Engineering Strategy:**

The system prompt instructs the AI to:

1. Act as a data parser and extractor
2. Extract information from provided scraped content
3. Map extracted data to user-specified fields
4. Follow user-specified structure or use sensible defaults
5. Handle missing data gracefully (use null or indicate unavailable)
6. Return ONLY valid JSON without markdown formatting
7. Preserve data types (numbers as numbers, dates as strings, etc.)

The user prompt includes:

- The scraped text content (truncated if necessary)
- Data description for context
- Desired fields list with clear instructions
- Example JSON structure (if provided)
- Instructions for handling missing data

### 4. Data Models (`ai_layer/parsing_models.py`)

**New Models:**

```python
@dataclass
class ParsedDataResponse:
    """Container for parsed data response."""
    data: Dict[str, Any]  # The parsed JSON response
    metadata: ParsingMetadata
    raw_ai_output: str  # Original AI output for debugging
    source_metadata: ScrapingMetadata  # From original scraping result

@dataclass
class ParsingMetadata:
    """Metadata about the parsing process."""
    timestamp: datetime
    model: str
    tokens_used: int
    parsing_time_ms: int
    records_parsed: int
    fields_extracted: List[str]
    data_sources: List[str]  # URLs that were scraped

class EmptyDataError(Exception):
    """Raised when scraping result contains no data"""

class ParsingError(Exception):
    """Raised when AI fails to parse data"""

class ValidationError(Exception):
    """Raised when parsed output is invalid"""
```

### 5. Parsing Response Validator (`ai_layer/parsing_validator.py`)

**Responsibility:** Validate parsed responses meet requirements.

**Interface:**

```python
class ParsingValidator:
    """Validates parsed data responses."""

    def validate_parsed_response(
        self,
        ai_output: str,
        user_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate AI-parsed response.

        Args:
            ai_output: Raw AI response
            user_requirements: User's requirements

        Returns:
            Validated JSON object

        Raises:
            ValidationError: When validation fails
        """

    def _validate_json(self, text: str) -> Dict[str, Any]:
        """Validate and parse JSON"""

    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON from markdown or mixed text"""

    def _validate_required_fields(
        self,
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> bool:
        """Check if required fields are present"""

    def _validate_data_structure(
        self,
        data: Dict[str, Any],
        expected_structure: Dict[str, Any]
    ) -> bool:
        """Validate data follows expected structure"""
```

**Validation Rules:**

1. Output must be valid JSON
2. If user specified fields, all must be present (or explicitly null)
3. If user specified structure, output must follow it
4. Data types should match expectations (numbers, strings, arrays)
5. Arrays should contain consistent object structures

### 6. UI Integration Updates

**Update `app.py`:**

```python
# After scraping execution succeeds
if execution_result.success and execution_result.data:
    # NEW: Parse scraped data into structured JSON
    with st.spinner("🤖 AI is parsing scraped data..."):
        try:
            # Initialize parser
            parser = ScrapedDataParser(client)

            # Convert execution_result to ScrapingResult format
            scraping_result = ScrapingResult(
                success=True,
                data=execution_result.data,
                metadata=ScrapingMetadata(
                    strategy_used=ScrapingStrategy.STATIC,
                    final_url=target_url
                )
            )

            # Parse data
            parsed_response = parser.parse_scraped_data(
                scraping_result=scraping_result,
                user_requirements=form_data
            )

            # Display parsed JSON
            st.success("✅ Data parsed successfully!")
            st.subheader("📊 Structured JSON Response")
            st.json(parsed_response.data)

            # Show metadata
            with st.expander("📈 Parsing Metadata"):
                st.write(f"Records Parsed: {parsed_response.metadata.records_parsed}")
                st.write(f"Fields Extracted: {', '.join(parsed_response.metadata.fields_extracted)}")
                st.write(f"Parsing Time: {parsed_response.metadata.parsing_time_ms}ms")
                st.write(f"Model: {parsed_response.metadata.model}")

        except Exception as e:
            st.error(f"❌ Parsing failed: {str(e)}")
```

**Update `components/results.py`:**

```python
def render_parsed_response(response: ParsedDataResponse) -> None:
    """
    Display parsed data response with formatting and actions.

    Args:
        response: ParsedDataResponse object to display
    """
    # Display JSON with syntax highlighting
    st.json(response.data)

    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(response.data, indent=2),
            file_name="parsed_data.json",
            mime="application/json"
        )
    with col2:
        if st.button("📋 Copy to Clipboard"):
            st.code(json.dumps(response.data, indent=2))

    # Metadata display
    with st.expander("📊 Parsing Details"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Records", response.metadata.records_parsed)
        with col2:
            st.metric("Fields", len(response.metadata.fields_extracted))
        with col3:
            st.metric("Time", f"{response.metadata.parsing_time_ms}ms")

        st.write("**Extracted Fields:**")
        st.write(", ".join(response.metadata.fields_extracted))

        st.write("**Data Sources:**")
        for url in response.metadata.data_sources:
            st.write(f"- {url}")
```

## Data Models

### Input: ScrapingResult (from scraping layer)

```python
{
    "success": True,
    "data": [
        {
            "field1": "value1",
            "field2": "value2",
            # ... raw scraped data
        },
        # ... more records
    ],
    "metadata": {
        "strategy_used": "STATIC",
        "final_url": "https://example.com",
        "response_status": 200,
        "timestamp": "2026-01-15T10:30:00Z"
    },
    "errors": [],
    "performance_metrics": {
        "start_time": "2026-01-15T10:30:00Z",
        "end_time": "2026-01-15T10:30:05Z",
        "total_duration": 5.2,
        "items_extracted": 25
    }
}
```

### Input: User Requirements (from form)

```python
{
    "data_description": "Current IPOs with grey market premium",
    "data_source": "https://example.com/ipos",  # Optional
    "desired_fields": "company_name\nlisting_date\nissue_price\ngrey_market_premium",
    "response_structure": '{"data": [{"company_name": "string", ...}]}',  # Optional
    "update_frequency": "Daily"
}
```

### Output: ParsedDataResponse

```python
{
    "data": {
        "data": [
            {
                "company_name": "Example Corp",
                "listing_date": "2026-01-20",
                "issue_price": 150.00,
                "grey_market_premium": 25.50
            },
            # ... more records
        ],
        "metadata": {
            "total_count": 25,
            "update_frequency": "Daily",
            "last_updated": "2026-01-15T10:30:00Z"
        }
    },
    "metadata": {
        "timestamp": "2026-01-15T10:30:10Z",
        "model": "deepseek-chat",
        "tokens_used": 3500,
        "parsing_time_ms": 2800,
        "records_parsed": 25,
        "fields_extracted": ["company_name", "listing_date", "issue_price", "grey_market_premium"],
        "data_sources": ["https://example.com/ipos"]
    },
    "raw_ai_output": "...",  # For debugging
    "source_metadata": {
        "strategy_used": "STATIC",
        "final_url": "https://example.com/ipos",
        "response_status": 200
    }
}
```

## Configuration

### Environment Variables

Reuses existing configuration:

```python
DEEPSEEK_API_KEY: str          # Required: API key from DeepSeek platform
DEEPSEEK_BASE_URL: str         # Optional: Default "https://api.deepseek.com"
DEEPSEEK_MODEL: str            # Optional: Default "deepseek-chat"
```

### Parsing Configuration

```python
# ai_layer/parsing_config.py
@dataclass
class ParsingConfig:
    """Configuration for data parsing."""
    max_text_length: int = 50000  # Maximum text length to send to AI
    temperature: float = 0.3  # Lower for more consistent parsing
    max_tokens: int = 8000  # Increased for large datasets
    retry_attempts: int = 2  # Number of retry attempts for parsing failures

    @classmethod
    def default(cls) -> 'ParsingConfig':
        """Get default configuration"""
        return cls()
```

## Correctness Properties

_A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees._

Before writing the correctness properties, I need to analyze the acceptance criteria for testability.

### Property 1: ScrapingResult Acceptance

_For any_ valid ScrapingResult object, the parser should accept it without raising exceptions during initialization or data extraction.
**Validates: Requirements 1.1**

### Property 2: Empty Data Rejection

_For any_ ScrapingResult with an empty data list, the parser should raise an EmptyDataError indicating no data was found.
**Validates: Requirements 1.2**

### Property 3: Multiple Source Handling

_For any_ ScrapingResult containing data from multiple sources, the parser should process all records regardless of their source.
**Validates: Requirements 1.3**

### Property 4: Error Information Handling

_For any_ ScrapingResult with success=False and error information, the parser should handle it gracefully without crashing.
**Validates: Requirements 1.4**

### Property 5: Format Flexibility

_For any_ data format (HTML strings, JSON objects, plain text), the data extractor should successfully extract text content.
**Validates: Requirements 1.5**

### Property 6: Requirements Field Extraction

_For any_ user requirements dictionary containing the required fields, the parser should successfully extract all fields without data loss.
**Validates: Requirements 2.1**

### Property 7: Field List Parsing

_For any_ newline-separated string of field names, the parser should produce a list where each element corresponds to a trimmed, non-empty line.
**Validates: Requirements 2.2**

### Property 8: Optional Field Defaults

_For any_ user requirements with empty optional fields, the parser should process the input without raising exceptions and produce valid output.
**Validates: Requirements 2.4**

### Property 9: Prompt Construction Completeness

_For any_ valid scraped data and user requirements, the constructed prompt should include both the scraped content and all non-empty user-provided information.
**Validates: Requirements 3.1**

### Property 10: Requested Fields Presence

_For any_ parsed response and list of desired fields, all requested fields should be present in the output (either with values or explicitly null).
**Validates: Requirements 3.2, 5.2**

### Property 11: Structure Compliance

_For any_ user-provided response structure template, the parsed output should follow the same structure (same keys at same nesting levels).
**Validates: Requirements 2.3, 3.3**

### Property 12: Field Filtering

_For any_ parsed response with desired fields specified, the output should contain only the requested fields (no extra fields beyond metadata).
**Validates: Requirements 3.4**

### Property 13: Missing Data Indication

_For any_ parsed response where scraped data lacks requested fields, those fields should be either null or explicitly marked as unavailable.
**Validates: Requirements 3.5, 4.5**

### Property 14: HTML Text Extraction

_For any_ HTML string, the extracted text should not contain HTML tags (no angle brackets except in actual content).
**Validates: Requirements 4.1**

### Property 15: Record Count Preservation

_For any_ ScrapingResult with N records, the parsed response should contain N records (or indicate why some were filtered).
**Validates: Requirements 4.2**

### Property 16: JSON Validation

_For any_ AI output string, the validator should correctly identify whether it represents valid JSON and either return the parsed object or raise a ValidationError.
**Validates: Requirements 5.1**

### Property 17: Error Message Clarity

_For any_ validation or parsing failure, the error message should be non-empty and contain relevant details about what went wrong.
**Validates: Requirements 5.5**

### Property 18: Metadata Inclusion

_For any_ successfully parsed response, the ParsedDataResponse should include complete metadata (timestamp, model, tokens_used, parsing_time_ms, records_parsed, fields_extracted, data_sources).
**Validates: Requirements 6.2**

### Property 19: Large Data Truncation

_For any_ scraped text exceeding the maximum length (50KB), the extractor should truncate it and include an indicator that truncation occurred.
**Validates: Requirements 8.2**

## Error Handling

### Error Categories and Handling Strategy

**1. Empty Data Errors**

- **Trigger:** ScrapingResult contains no data (empty list)
- **Exception:** `EmptyDataError`
- **User Message:** "No data was found in the scraped results. Please verify the data source URL and try again."
- **Recovery:** User must check data source or modify scraping configuration

**2. Parsing Errors**

- **Trigger:** AI fails to parse data, returns invalid JSON, or parsing times out
- **Exception:** `ParsingError`
- **User Message:** "Failed to parse scraped data: {details}. The AI may need clearer requirements or the data format may be too complex."
- **Recovery:** Retry with simplified requirements, or check scraped data quality

**3. Validation Errors**

- **Trigger:** Parsed output doesn't meet requirements (missing fields, wrong structure)
- **Exception:** `ValidationError`
- **User Message:** "Parsed data validation failed: {details}. Please verify your field requirements match the available data."
- **Recovery:** User should adjust requirements or check scraped data

**4. API Errors**

- **Trigger:** DeepSeek API errors (auth, rate limit, service unavailable)
- **Exception:** `DeepSeekAPIError`, `DeepSeekAuthError`, `DeepSeekRateLimitError`
- **User Message:** Inherited from DeepSeek client error messages
- **Recovery:** Inherited from DeepSeek client retry logic

**5. Data Extraction Errors**

- **Trigger:** Cannot extract text from scraped data (corrupt HTML, unknown format)
- **Exception:** `DataExtractionError`
- **User Message:** "Failed to extract text from scraped data: {details}. The data format may not be supported."
- **Recovery:** Check scraping configuration, verify data source returns valid content

### Error Handling Flow

```
Scraped Data → Validation → Text Extraction → Prompt Building → AI Call → Response Parsing → Validation → UI Display
     ↓              ↓              ↓                 ↓             ↓              ↓              ↓              ↓
  Check Empty   Check Format   Extract Text    Build Prompt   Handle API   Validate JSON   Check Fields   Display
     ↓              ↓              ↓                 ↓             ↓              ↓              ↓              ↓
   Error          Error          Error            Error         Error          Error          Error          Error
  Message        Message        Message          Message       Message        Message        Message        Message
```

### Retry Strategy

```python
# Parsing retry configuration
MAX_PARSING_RETRIES = 2
RETRY_DELAY = 2.0  # seconds

def retry_parsing(attempt: int) -> bool:
    """
    Determine if parsing should be retried.

    Args:
        attempt: Current attempt number (0-indexed)

    Returns:
        True if should retry, False otherwise
    """
    return attempt < MAX_PARSING_RETRIES
```

**Retry Logic:**

- Retry on ParsingError (AI returned invalid JSON)
- Retry on ValidationError (output didn't meet requirements)
- Do NOT retry on EmptyDataError (no data to parse)
- Do NOT retry on API errors (handled by DeepSeek client)
- Do NOT retry on DataExtractionError (data format issue)

### Logging Strategy

All operations should be logged with appropriate severity:

- **ERROR:** Parsing failures, validation failures, data extraction errors
- **WARNING:** Retries, truncation, missing fields
- **INFO:** Successful parsing, record counts, field extraction
- **DEBUG:** Prompt construction, AI responses, validation details

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests** verify specific examples, edge cases, and error conditions:

- Specific error scenarios (empty data, invalid JSON, missing fields)
- Integration points between components
- UI rendering functions with known inputs
- Edge cases like HTML with special characters, very large datasets

**Property-Based Tests** verify universal properties across all inputs:

- ScrapingResult acceptance works for any valid result
- Field extraction works for any requirements dictionary
- HTML extraction works for any HTML string
- JSON validation works for any string input
- Prompt construction includes all provided information

Both testing approaches are complementary and necessary for comprehensive coverage. Unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across the input space.

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
- Tag format: `# Feature: scraped-data-parser, Property {number}: {property_text}`

**Example Property Test:**

```python
from hypothesis import given, strategies as st
import pytest
from scraping_layer.models import ScrapingResult, ScrapingMetadata, ScrapingStrategy
from ai_layer.scraped_data_parser import ScrapedDataParser

# Feature: scraped-data-parser, Property 1: ScrapingResult Acceptance
@given(st.lists(st.dictionaries(st.text(), st.text()), min_size=1))
def test_scraping_result_acceptance_property(data_records):
    """For any valid ScrapingResult, parser should accept it without exceptions"""
    # Arrange
    scraping_result = ScrapingResult(
        success=True,
        data=data_records,
        metadata=ScrapingMetadata(
            strategy_used=ScrapingStrategy.STATIC,
            final_url="https://example.com"
        )
    )
    parser = ScrapedDataParser(mock_client)

    # Act & Assert - should not raise exception
    try:
        text = parser._extract_text_from_scraped_data(scraping_result)
        assert isinstance(text, str)
        assert len(text) > 0
    except Exception as e:
        pytest.fail(f"Parser should accept valid ScrapingResult but raised: {e}")
```

### Test Coverage Requirements

**Component Test Coverage:**

1. **Scraped Data Parser (ai_layer/scraped_data_parser.py)**

   - Unit tests: Empty data handling, specific parsing scenarios, error messages
   - Property tests: ScrapingResult acceptance (Property 1), empty data rejection (Property 2), multiple sources (Property 3), error handling (Property 4), prompt construction (Property 9), field presence (Property 10), structure compliance (Property 11), metadata inclusion (Property 18)

2. **Data Extractor (ai_layer/data_extractor.py)**

   - Unit tests: Specific HTML examples, edge cases with special characters
   - Property tests: Format flexibility (Property 5), HTML extraction (Property 14), truncation (Property 19)

3. **Parsing Prompt Builder (ai_layer/parsing_prompt_builder.py)**

   - Unit tests: Specific prompt examples, edge cases with empty fields
   - Property tests: Field extraction (Property 6), field list parsing (Property 7), optional fields (Property 8)

4. **Parsing Validator (ai_layer/parsing_validator.py)**

   - Unit tests: Specific invalid JSON examples, markdown-wrapped JSON
   - Property tests: JSON validation (Property 16), field filtering (Property 12), missing data indication (Property 13), error messages (Property 17)

5. **UI Components (components/results.py)**
   - Unit tests: Response rendering with known data, error display
   - No property tests (UI is visual)

### Mocking Strategy

**External Dependencies to Mock:**

- DeepSeek API HTTP requests (use `responses` library or `unittest.mock`)
- ScrapingResult objects (create test fixtures)
- File system operations for download functionality

**Do Not Mock:**

- Internal business logic (text extraction, prompt construction, validation)
- Data models and validation functions
- Error handling logic

### Integration Testing

While this design focuses on unit and property tests, integration tests should verify:

- End-to-end flow from scraping result to parsed JSON display
- Actual DeepSeek API calls with real scraped data (in separate integration test suite)
- Error handling across component boundaries
- UI state management during parsing

Integration tests should be marked separately and run less frequently than unit/property tests.
