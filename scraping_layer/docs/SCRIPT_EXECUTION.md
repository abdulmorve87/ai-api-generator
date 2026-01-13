# Script Execution Layer

The Script Execution Layer provides a simplified interface for executing pre-written scraping scripts without requiring AI generation. This layer focuses on accepting scraping scripts and executing them using the Universal Scraping Layer.

## Overview

Instead of generating scripts through AI, this layer allows you to:

1. **Define scraping scripts** with explicit configurations
2. **Execute scripts** using the scraping engine
3. **Get structured results** with metadata and performance info
4. **Track execution history** for monitoring and debugging

## Key Components

### ScrapingScript

Defines a complete scraping configuration:

```python
from scraping_layer.script_execution import ScrapingScript
from scraping_layer.models import ScrapingStrategy

script = ScrapingScript(
    script_id="my_script_001",
    name="Example.com Scraper",
    description="Extract title and content from example.com",
    url="https://example.com",
    strategy=ScrapingStrategy.STATIC,
    selectors={
        'title': 'h1',
        'content': 'p',
        'links': 'a'
    },
    expected_fields=['title', 'content'],
    timeout=30,
    tags=['example', 'basic']
)
```

### ScriptExecutor

Executes scripts and manages results:

```python
from scraping_layer.script_execution import ScriptExecutor

# Initialize with scraping engine
executor = ScriptExecutor(scraping_engine)

# Execute script
result = await executor.execute_script(script)

# Check results
if result.success:
    print(f"Extracted {result.total_items} items")
    for item in result.data:
        print(item)
else:
    print(f"Errors: {result.errors}")
```

## Usage Examples

### Basic Static Scraping

```python
import asyncio
from scraping_layer.script_execution import ScrapingScript, ScriptExecutor
from scraping_layer.models import ScrapingStrategy

async def basic_example():
    # Define script
    script = ScrapingScript(
        script_id="basic_001",
        name="Basic Example",
        description="Simple static scraping",
        url="https://example.com",
        strategy=ScrapingStrategy.STATIC,
        selectors={
            'title': 'h1',
            'description': 'p'
        }
    )

    # Execute (assuming you have an executor set up)
    result = await executor.execute_script(script)

    return result

# Run
result = asyncio.run(basic_example())
```

### Form-Based Script Generation

You can create scripts based on form inputs:

```python
def create_script_from_form(form_data):
    """Convert form data to scraping script."""

    # Parse desired fields
    fields = form_data['desired_fields'].split('\n')

    # Create selectors (simplified mapping)
    selectors = {}
    for field in fields:
        if 'title' in field.lower():
            selectors[field] = 'h1, h2, .title'
        elif 'content' in field.lower():
            selectors[field] = 'p, .content'
        elif 'date' in field.lower():
            selectors[field] = '.date, time'
        else:
            selectors[field] = f'.{field.replace("_", "-")}'

    # Create script
    script = ScrapingScript(
        script_id=f"form_{int(time.time())}",
        name=f"Script for: {form_data['data_description'][:50]}",
        description=form_data['data_description'],
        url=determine_url(form_data['data_source']),
        strategy=ScrapingStrategy.STATIC,
        selectors=selectors,
        expected_fields=fields
    )

    return script
```

### Error Handling

```python
async def robust_execution(script):
    """Execute script with proper error handling."""

    try:
        result = await executor.execute_script(script)

        if result.success:
            print(f"✅ Success: {result.total_items} items")

            # Check for warnings
            if result.warnings:
                print(f"⚠️ Warnings: {result.warnings}")

            return result.data

        else:
            print(f"❌ Failed: {result.errors}")
            return []

    except Exception as e:
        print(f"💥 Exception: {e}")
        return []
```

## Script Configuration Options

### Selectors

Define CSS selectors for data extraction:

```python
selectors = {
    'title': 'h1, .main-title',           # Multiple selectors
    'content': 'p.description',           # Specific class
    'price': '[data-price]',              # Attribute selector
    'links': 'a[href^="http"]',           # Attribute starts with
    'items': '.item-list > .item'         # Child selector
}
```

### Expected Fields

Specify fields you expect to find:

```python
expected_fields = ['title', 'content', 'date', 'author']
```

The executor will warn if these fields are missing from results.

### Strategies

Choose scraping strategy:

- `ScrapingStrategy.STATIC` - For regular HTML pages
- `ScrapingStrategy.DYNAMIC` - For JavaScript-heavy sites
- `ScrapingStrategy.HYBRID` - Try dynamic, fallback to static

### Timeouts

Set appropriate timeouts:

```python
script = ScrapingScript(
    # ... other config
    timeout=45,  # 45 seconds for slow sites
)
```

## Result Structure

### ScriptResult

```python
@dataclass
class ScriptResult:
    success: bool                    # Whether execution succeeded
    script_id: str                   # ID of executed script
    execution_id: str                # Unique execution ID
    data: List[Dict[str, Any]]       # Extracted data
    metadata: ScriptMetadata         # Execution metadata
    errors: List[str]                # Error messages
    warnings: List[str]              # Warning messages
    total_items: int                 # Number of items extracted
    execution_time: float            # Time taken in seconds
```

### Metadata

```python
@dataclass
class ScriptMetadata:
    script_id: str                   # Script identifier
    execution_id: str                # Execution identifier
    strategy_used: ScrapingStrategy  # Strategy that was used
    url_processed: str               # URL that was scraped
    items_found: int                 # Items found
    execution_time: float            # Execution time
    timestamp: datetime              # When executed
```

## Execution History

Track all executions:

```python
# Get all execution history
history = executor.get_execution_history()

# Get history for specific script
script_history = executor.get_execution_history(script_id="my_script_001")

# Get specific execution result
result = executor.get_execution_result(execution_id="abc-123")

# Clean old history
executor.clear_history(older_than_hours=24)
```

## Testing

### Run Basic Test

```bash
python test_script_execution.py
```

### Run Advanced Tests

```bash
python scraping_layer/examples/test_script_execution_advanced.py
```

### Run Single Test

```bash
python scraping_layer/examples/test_script_execution_advanced.py --single
```

## Integration with Form UI

The script execution layer integrates well with form-based UIs:

1. **User fills form** (data description, source, fields)
2. **Create script** from form data using helper functions
3. **Execute script** using ScriptExecutor
4. **Display results** in UI with success/error status
5. **Store history** for user to review past executions

## Performance Considerations

- **Caching**: Scripts use the engine's caching system
- **Timeouts**: Set appropriate timeouts for different sites
- **Memory**: Large datasets are handled efficiently
- **History**: Old execution history is automatically cleaned

## Error Types

Common errors and handling:

- **Network errors**: Connection timeouts, DNS failures
- **Parsing errors**: Invalid selectors, missing elements
- **Validation errors**: Missing expected fields
- **Timeout errors**: Site too slow to respond

All errors are captured in the result object with descriptive messages.
