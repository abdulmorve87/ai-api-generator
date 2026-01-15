# AI Layer Tests

This directory contains test scripts for the AI Response Generator.

## Test Files

### 1. `test_connection.py`

Tests basic connectivity to the DeepSeek API.

**Run:**

```bash
python -m ai_layer.test.test_connection
```

**What it tests:**

- API key configuration
- Network connectivity
- API endpoint accessibility
- Authentication

### 2. `test_ai_layer.py`

Basic test of the AI layer with a simple weather data request.

**Run:**

```bash
python -m ai_layer.test.test_ai_layer
```

**What it tests:**

- Configuration loading
- Client initialization
- Response generation
- Basic JSON output

### 3. `test_25_records.py`

Tests generating 25 records with specified fields.

**Run:**

```bash
python -m ai_layer.test.test_25_records
```

**What it tests:**

- Record count (25 records)
- Field presence
- Data structure
- Response metadata

### 4. `test_10_15_fields.py`

Tests the 10-15 fields per record feature.

**Run:**

```bash
python -m ai_layer.test.test_10_15_fields
```

**What it tests:**

- Field count (10-15 per record)
- Auto-field generation
- Field diversity
- Data quality

### 5. `test_comprehensive.py`

Comprehensive test of all optimized features.

**Run:**

```bash
python -m ai_layer.test.test_comprehensive
```

**What it tests:**

- 10-15 fields per record
- Valid JSON output
- Data accuracy
- Response speed
- Overall system performance

## Running All Tests

To run all tests sequentially:

```bash
# From project root
python -m ai_layer.test.run_all_tests
```

## Output Files

Test outputs are saved in this directory:

- `output_25_records.json`
- `output_10_15_fields.json`
- `output_comprehensive.json`

## Prerequisites

- DEEPSEEK_API_KEY environment variable must be set
- Internet connection required
- All dependencies installed (`pip install -r requirements.txt`)

## Troubleshooting

### Connection Errors

Run `test_connection.py` first to diagnose network issues.

### Import Errors

Make sure you're running from the project root directory.

### API Key Errors

Check that your `.env` file contains:

```
DEEPSEEK_API_KEY=your_key_here
```

### Timeout Errors

Some tests may take 2-5 minutes. Be patient!

## Test Configuration

Tests use the optimized configuration:

- Temperature: 0.3 (faster, more consistent)
- Max Tokens: 8000 (larger datasets)
- Model: deepseek-chat

## Notes

- Tests make real API calls and consume tokens
- Response times vary based on record count and field complexity
- Some tests may fail if API rate limits are exceeded
- All tests save output to JSON files for inspection
