# Design Document: AI Response Generator

## Overview

The AI Response Generator is a Python-based component that integrates with the DeepSeek API to transform user form inputs into structured JSON API responses. The system uses DeepSeek's OpenAI-compatible API to generate realistic mock data based on user requirements, providing immediate feedback on what their API will return.

The design follows a layered architecture with clear separation between API communication, prompt engineering, response validation, and UI presentation. This Phase 1 implementation focuses on generating mock responses that demonstrate the desired data structure without actual web scraping.

## Architecture

The system consists of four main layers:

```
┌─────────────────────────────────────────┐
│         Streamlit UI Layer              │
│  (components/form.py, results.py)       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    AI Response Generator Layer          │
│  - Prompt Construction                  │
│  - Response Validation                  │
│  - Error Handling                       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      DeepSeek Client Layer              │
│  - API Authentication                   │
│  - Request/Response Handling            │
│  - Rate Limiting                        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         DeepSeek API                    │
│  (https://api.deepseek.com)             │
└─────────────────────────────────────────┘
```

**Design Rationale:**

- Layered architecture enables independent testing and future extensibility
- DeepSeek Client is isolated to allow easy swapping of AI providers
- Prompt construction is separated from API calls for better prompt engineering iteration
- Response validation ensures data quality before UI presentation

## Components and Interfaces

### 1. DeepSeek Client (`ai_layer/deepseek_client.py`)

**Responsibility:** Handle all communication with the DeepSeek API using OpenAI-compatible format.

**Interface:**

```python
class DeepSeekClient:
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        """Initialize client with API credentials"""

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Send a chat completion request to DeepSeek API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (default: "deepseek-chat")
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response

        Returns:
            Generated text content

        Raises:
            DeepSeekAPIError: When API returns an error
            DeepSeekAuthError: When authentication fails
            DeepSeekRateLimitError: When rate limit is exceeded
        """
```

**Implementation Details:**

- Uses `requests` library for HTTP communication
- Implements Bearer token authentication via Authorization header
- Follows OpenAI-compatible API format ([source](https://api-docs.deepseek.com/))
- Handles streaming and non-streaming responses
- Implements exponential backoff for rate limiting
- Validates API key on initialization

### 2. AI Response Generator (`ai_layer/response_generator.py`)

**Responsibility:** Orchestrate the conversion of form inputs to JSON responses.

**Interface:**

```python
class AIResponseGenerator:
    def __init__(self, deepseek_client: DeepSeekClient):
        """Initialize with a DeepSeek client instance"""

    def generate_response(self, form_input: Dict[str, Any]) -> GeneratedResponse:
        """
        Generate a JSON API response from form inputs.

        Args:
            form_input: Dictionary containing:
                - data_description: str
                - data_source: str (optional)
                - desired_fields: str (optional, newline-separated)
                - response_structure: str (optional, JSON string)
                - update_frequency: str

        Returns:
            GeneratedResponse object with JSON data and metadata

        Raises:
            ValidationError: When inputs are invalid
            GenerationError: When AI generation fails
        """

    def _build_prompt(self, form_input: Dict[str, Any]) -> List[Dict[str, str]]:
        """Construct the prompt messages for DeepSeek"""

    def _parse_fields(self, fields_text: str) -> List[str]:
        """Parse newline-separated field list"""

    def _validate_json_structure(self, structure_text: str) -> Dict:
        """Validate and parse JSON structure"""

    def _validate_response(self, ai_output: str) -> Dict:
        """Validate and parse AI-generated JSON"""
```

**Prompt Engineering Strategy:**
The system prompt instructs the AI to:

1. Act as an API response generator
2. Generate realistic, diverse sample data (3-5 records)
3. Follow the user's specified structure or use sensible defaults
4. Include all requested fields with appropriate data types
5. Return ONLY valid JSON without markdown formatting

The user prompt includes:

- Data description and context
- Data source (if provided) for realistic data generation
- Desired fields list
- Example JSON structure (if provided)
- Update frequency context

### 3. Data Models (`ai_layer/models.py`)

**Response Models:**

```python
@dataclass
class GeneratedResponse:
    """Container for AI-generated API response"""
    data: Dict[str, Any]  # The generated JSON response
    metadata: ResponseMetadata
    raw_output: str  # Original AI output for debugging

@dataclass
class ResponseMetadata:
    """Metadata about the generation process"""
    timestamp: datetime
    model: str
    tokens_used: int
    generation_time_ms: int

class DeepSeekAPIError(Exception):
    """Base exception for DeepSeek API errors"""

class DeepSeekAuthError(DeepSeekAPIError):
    """Authentication failure"""

class DeepSeekRateLimitError(DeepSeekAPIError):
    """Rate limit exceeded"""

class ValidationError(Exception):
    """Input validation error"""

class GenerationError(Exception):
    """AI generation error"""
```

### 4. UI Integration (`components/results.py`)

**Responsibility:** Display generated responses in the Streamlit interface.

**Interface:**

```python
def render_generated_response(response: GeneratedResponse) -> None:
    """
    Display the generated JSON response with formatting and actions.

    Args:
        response: GeneratedResponse object to display
    """

def render_error(error: Exception) -> None:
    """
    Display error messages with appropriate styling.

    Args:
        error: Exception that occurred during generation
    """
```

**UI Features:**

- Syntax-highlighted JSON display using `st.json()`
- Copy to clipboard button
- Download as JSON file button
- Metadata display (model, timestamp, tokens)
- Error messages with troubleshooting hints
- Loading spinner during generation

## Data Models

### Form Input Structure

```python
{
    "data_description": str,      # Required: What data to generate
    "data_source": str,            # Optional: Where data comes from
    "desired_fields": str,         # Optional: Newline-separated field names
    "response_structure": str,     # Optional: JSON structure template
    "update_frequency": str        # Required: How often data updates
}
```

### Generated Response Structure

```python
{
    "data": {
        # User-specified or default structure
        # Example default:
        "data": [
            {
                "field1": "value1",
                "field2": "value2",
                # ... more fields
            },
            # ... more records (3-5 samples)
        ],
        "metadata": {
            "total_count": int,
            "update_frequency": str,
            "last_updated": str
        }
    },
    "metadata": {
        "timestamp": "2026-01-14T10:30:00Z",
        "model": "deepseek-chat",
        "tokens_used": 450,
        "generation_time_ms": 1250
    },
    "raw_output": str  # For debugging
}
```

### Error Response Structure

```python
{
    "error": {
        "type": str,           # "auth_error", "rate_limit", "validation_error", etc.
        "message": str,        # User-friendly error message
        "details": str,        # Technical details
        "suggestion": str      # How to fix the issue
    }
}
```

## Configuration

### Environment Variables

```python
DEEPSEEK_API_KEY: str          # Required: API key from DeepSeek platform
DEEPSEEK_BASE_URL: str         # Optional: Default "https://api.deepseek.com"
DEEPSEEK_MODEL: str            # Optional: Default "deepseek-chat"
DEEPSEEK_TEMPERATURE: float    # Optional: Default 0.7
DEEPSEEK_MAX_TOKENS: int       # Optional: Default 2000
```

### Configuration Loading

```python
# ai_layer/config.py
@dataclass
class DeepSeekConfig:
    api_key: str
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 2000

    @classmethod
    def from_env(cls) -> 'DeepSeekConfig':
        """Load configuration from environment variables"""
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ConfigurationError("DEEPSEEK_API_KEY environment variable is required")

        return cls(
            api_key=api_key,
            base_url=os.getenv('DEEPSEEK_BASE_URL', cls.base_url),
            model=os.getenv('DEEPSEEK_MODEL', cls.model),
            temperature=float(os.getenv('DEEPSEEK_TEMPERATURE', cls.temperature)),
            max_tokens=int(os.getenv('DEEPSEEK_MAX_TOKENS', cls.max_tokens))
        )
```

## Correctness Properties

_A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees._

### Property 1: API Key Loading

_For any_ valid environment configuration, when the DeepSeek client initializes, it should successfully load the API key from the DEEPSEEK_API_KEY environment variable and store it for authentication.
**Validates: Requirements 1.1**

### Property 2: Authentication Header Presence

_For any_ request sent to the DeepSeek API, the request headers should always include a properly formatted Authorization header with Bearer token authentication.
**Validates: Requirements 1.3**

### Property 3: Response Parsing and Validation

_For any_ valid JSON response from the DeepSeek API, the client should successfully parse the content and return the generated text without errors.
**Validates: Requirements 1.4, 4.1**

### Property 4: Error Exception Mapping

_For any_ error response from the DeepSeek API, the client should raise an appropriate exception type (DeepSeekAPIError, DeepSeekAuthError, or DeepSeekRateLimitError) that matches the error category.
**Validates: Requirements 1.5**

### Property 5: Form Field Extraction

_For any_ form input dictionary containing the required fields, the AI Response Generator should successfully extract all fields (data_description, data_source, desired_fields, response_structure, update_frequency) without data loss.
**Validates: Requirements 2.1**

### Property 6: Field List Parsing

_For any_ newline-separated string of field names, the parser should produce a list where each element corresponds to a trimmed, non-empty line from the input.
**Validates: Requirements 2.2**

### Property 7: JSON Structure Validation

_For any_ string input, the JSON structure validator should correctly identify whether it represents valid JSON and either return the parsed object or raise a validation error.
**Validates: Requirements 2.3**

### Property 8: Optional Field Handling

_For any_ form input with empty optional fields (data_source, desired_fields, response_structure), the AI Response Generator should process the input without raising exceptions and construct a valid prompt.
**Validates: Requirements 2.4**

### Property 9: Prompt Construction Completeness

_For any_ valid form input, the constructed prompt should include all non-empty user-provided information (data description, source, fields, structure) and system instructions for JSON generation.
**Validates: Requirements 2.5**

### Property 10: Request Format Compliance

_For any_ prompt sent to DeepSeek, the request payload should conform to the OpenAI-compatible format with required fields (model, messages) and proper message structure.
**Validates: Requirements 3.1**

### Property 11: Default Structure Inclusion

_For any_ form input without a user-provided response_structure, the constructed prompt should include instructions to use a default structure with a "data" array.
**Validates: Requirements 3.5**

### Property 12: Invalid JSON Extraction

_For any_ AI output containing JSON embedded in markdown or other text, the extraction function should attempt to locate and extract the JSON content.
**Validates: Requirements 4.2**

### Property 13: Metadata Inclusion

_For any_ successfully generated response, the returned GeneratedResponse object should include complete metadata (timestamp, model, tokens_used, generation_time_ms).
**Validates: Requirements 4.5**

### Property 14: Parsing Error Messages

_For any_ invalid JSON output from the AI, the system should generate a clear error message that includes details about the parsing failure.
**Validates: Requirements 6.3**

## Error Handling

### Error Categories and Handling Strategy

**1. Configuration Errors**

- **Trigger:** Missing DEEPSEEK_API_KEY environment variable
- **Exception:** `ConfigurationError`
- **User Message:** "DeepSeek API key not configured. Please set the DEEPSEEK_API_KEY environment variable."
- **Recovery:** User must configure environment variable and restart application

**2. Authentication Errors**

- **Trigger:** Invalid API key, 401 response from DeepSeek
- **Exception:** `DeepSeekAuthError`
- **User Message:** "Authentication failed. Please verify your DeepSeek API key is correct."
- **Recovery:** User must update API key in environment

**3. Rate Limit Errors**

- **Trigger:** 429 response from DeepSeek API
- **Exception:** `DeepSeekRateLimitError`
- **User Message:** "Rate limit exceeded. Please wait {retry_after} seconds before trying again."
- **Recovery:** Implement exponential backoff, display retry timer to user

**4. Network Errors**

- **Trigger:** Connection timeout, DNS failure, network unreachable
- **Exception:** `DeepSeekConnectionError`
- **User Message:** "Unable to connect to DeepSeek API. Please check your internet connection."
- **Recovery:** Retry with exponential backoff (3 attempts), then fail gracefully

**5. Validation Errors**

- **Trigger:** Invalid form inputs, malformed JSON structure
- **Exception:** `ValidationError`
- **User Message:** "Invalid input: {specific_field} - {reason}"
- **Recovery:** Display error inline with form field, allow user to correct

**6. Generation Errors**

- **Trigger:** AI returns invalid JSON, parsing fails after extraction attempts
- **Exception:** `GenerationError`
- **User Message:** "Failed to generate valid JSON response. Please try again or simplify your requirements."
- **Recovery:** Allow retry, suggest simplifying inputs

**7. API Errors**

- **Trigger:** 500/503 responses from DeepSeek, service unavailable
- **Exception:** `DeepSeekAPIError`
- **User Message:** "DeepSeek service is temporarily unavailable. Please try again in a few moments."
- **Recovery:** Retry with exponential backoff, display service status

### Error Handling Flow

```
User Input → Validation → API Call → Response Parsing → UI Display
     ↓            ↓           ↓              ↓              ↓
  Validate    Validate   Handle API    Validate JSON   Display
   Form       JSON       Errors        Extract/Fix     Result
     ↓            ↓           ↓              ↓              ↓
   Error      Error       Error          Error          Error
  Message    Message     Message        Message        Message
```

### Retry Strategy

```python
# Exponential backoff configuration
MAX_RETRIES = 3
BASE_DELAY = 1.0  # seconds
MAX_DELAY = 30.0  # seconds

def calculate_retry_delay(attempt: int) -> float:
    """Calculate delay with exponential backoff and jitter"""
    delay = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
    jitter = random.uniform(0, delay * 0.1)
    return delay + jitter
```

### Logging Strategy

All errors should be logged with appropriate severity:

- **ERROR:** Authentication failures, API errors, generation failures
- **WARNING:** Rate limits, retries, validation errors
- **INFO:** Successful generations, API calls
- **DEBUG:** Request/response payloads, prompt construction

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests** verify specific examples, edge cases, and error conditions:

- Specific error scenarios (missing API key, invalid JSON)
- Integration points between components
- UI rendering functions with known inputs
- Edge cases like empty fields, malformed JSON

**Property-Based Tests** verify universal properties across all inputs:

- API key loading works for any valid environment
- Authentication headers are present in all requests
- JSON validation works for any string input
- Field extraction works for any form input dictionary
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
- Tag format: `# Feature: ai-response-generator, Property {number}: {property_text}`

**Example Property Test:**

```python
from hypothesis import given, strategies as st
import pytest

# Feature: ai-response-generator, Property 6: Field List Parsing
@given(st.lists(st.text(min_size=1), min_size=1))
def test_field_list_parsing_property(field_names):
    """For any list of field names, parsing newline-separated string produces correct list"""
    # Arrange
    input_text = "\n".join(field_names)
    generator = AIResponseGenerator(mock_client)

    # Act
    result = generator._parse_fields(input_text)

    # Assert
    assert len(result) == len(field_names)
    assert all(field.strip() == expected for field, expected in zip(result, field_names))
```

### Test Coverage Requirements

**Component Test Coverage:**

1. **DeepSeek Client (ai_layer/deepseek_client.py)**

   - Unit tests: API key validation, error response handling, specific error codes
   - Property tests: Authentication headers (Property 2), response parsing (Property 3), error mapping (Property 4)

2. **AI Response Generator (ai_layer/response_generator.py)**

   - Unit tests: Empty input handling, specific JSON structures, error messages
   - Property tests: Field extraction (Property 5), field parsing (Property 6), JSON validation (Property 7), optional fields (Property 8), prompt construction (Property 9), default structure (Property 11), metadata inclusion (Property 13)

3. **Configuration (ai_layer/config.py)**

   - Unit tests: Missing API key, invalid values
   - Property tests: API key loading (Property 1)

4. **Response Validation**

   - Unit tests: Specific malformed JSON examples, markdown-wrapped JSON
   - Property tests: JSON extraction (Property 12), error messages (Property 14)

5. **UI Components (components/results.py)**
   - Unit tests: Error display, response rendering with known data
   - No property tests (UI is visual)

### Mocking Strategy

**External Dependencies to Mock:**

- DeepSeek API HTTP requests (use `responses` library or `unittest.mock`)
- Environment variables (use `unittest.mock.patch.dict`)
- File system operations for download functionality

**Do Not Mock:**

- Internal business logic (prompt construction, field parsing, JSON validation)
- Data models and validation functions
- Error handling logic

### Integration Testing

While this design focuses on unit and property tests, integration tests should verify:

- End-to-end flow from form submission to response display
- Actual DeepSeek API calls (in separate integration test suite)
- Error handling across component boundaries
- UI state management during generation

Integration tests should be marked separately and run less frequently than unit/property tests.
