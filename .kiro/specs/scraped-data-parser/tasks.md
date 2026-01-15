# Implementation Plan: Scraped Data Parser

## Overview

This implementation plan breaks down the Scraped Data Parser into discrete coding tasks. The approach follows a bottom-up strategy: building data extraction utilities first, then prompt construction, then the main parser orchestration, and finally UI integration. Each task includes property-based tests to validate correctness properties from the design document.

## Tasks

- [x] 1. Set up project structure and data models

  - Create parsing-specific exception classes
  - Create ParsedDataResponse and ParsingMetadata dataclasses
  - Add JSON serialization methods
  - _Requirements: 1.1, 5.5, 6.2_

- [ ]\* 1.1 Write property test for metadata inclusion

  - **Property 18: Metadata Inclusion**
  - **Validates: Requirements 6.2**

- [x] 2. Implement data extraction utilities

  - [x] 2.1 Create DataExtractor class with HTML extraction

    - Implement extract_from_html using BeautifulSoup
    - Remove script tags, style tags, and comments
    - Extract clean text content
    - _Requirements: 4.1_

  - [ ]\* 2.2 Write property test for HTML text extraction

    - **Property 14: HTML Text Extraction**
    - **Validates: Requirements 4.1**

  - [x] 2.3 Implement extract_from_dict method

    - Convert dictionary data to readable text format
    - Handle nested structures (lists of dicts)
    - _Requirements: 1.5_

  - [x] 2.4 Implement extract_from_scraping_result method

    - Handle ScrapingResult objects
    - Extract text from various data formats
    - Validate data is not empty
    - _Requirements: 1.1, 1.2, 1.5_

  - [ ]\* 2.5 Write property test for ScrapingResult acceptance

    - **Property 1: ScrapingResult Acceptance**
    - **Validates: Requirements 1.1**

  - [ ]\* 2.6 Write property test for format flexibility

    - **Property 5: Format Flexibility**
    - **Validates: Requirements 1.5**

  - [x] 2.7 Implement truncate_if_needed method

    - Truncate text exceeding max length (50KB)
    - Add truncation indicator
    - _Requirements: 8.2_

  - [ ]\* 2.8 Write property test for large data truncation
    - **Property 19: Large Data Truncation**
    - **Validates: Requirements 8.2**

- [ ] 3. Checkpoint - Ensure data extraction tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement parsing prompt builder

  - [x] 4.1 Create ParsingPromptBuilder class

    - Implement \_build_system_prompt method
    - Define instructions for AI data parsing
    - _Requirements: 3.1_

  - [x] 4.2 Implement field parsing utilities

    - Implement \_parse_desired_fields method
    - Parse newline-separated field lists
    - Trim whitespace and filter empty lines
    - _Requirements: 2.2_

  - [ ]\* 4.3 Write property test for field list parsing

    - **Property 7: Field List Parsing**
    - **Validates: Requirements 2.2**

  - [x] 4.4 Implement JSON structure validator

    - Implement \_validate_json_structure method
    - Validate and parse JSON structure templates
    - _Requirements: 2.3_

  - [x] 4.5 Implement user prompt builder

    - Implement \_build_user_prompt method
    - Include scraped text and user requirements
    - Handle optional fields appropriately
    - _Requirements: 3.1_

  - [x] 4.6 Implement main build_parsing_prompt method

    - Combine system and user prompts
    - Return message list for DeepSeek API
    - _Requirements: 3.1_

  - [ ]\* 4.7 Write property test for requirements field extraction

    - **Property 6: Requirements Field Extraction**
    - **Validates: Requirements 2.1**

  - [ ]\* 4.8 Write property test for optional field defaults

    - **Property 8: Optional Field Defaults**
    - **Validates: Requirements 2.4**

  - [ ]\* 4.9 Write property test for prompt construction completeness
    - **Property 9: Prompt Construction Completeness**
    - **Validates: Requirements 3.1**

- [x] 5. Implement parsing response validator

  - [x] 5.1 Create ParsingValidator class

    - Implement \_validate_json method
    - Parse and validate JSON strings
    - _Requirements: 5.1_

  - [ ]\* 5.2 Write property test for JSON validation

    - **Property 16: JSON Validation**
    - **Validates: Requirements 5.1**

  - [x] 5.3 Implement JSON extraction from text

    - Implement \_extract_json_from_text method
    - Extract JSON from markdown code blocks
    - Handle mixed text and JSON
    - _Requirements: 5.4_

  - [x] 5.4 Implement field validation

    - Implement \_validate_required_fields method
    - Check if all requested fields are present
    - _Requirements: 5.2_

  - [ ]\* 5.5 Write property test for requested fields presence

    - **Property 10: Requested Fields Presence**
    - **Validates: Requirements 3.2, 5.2**

  - [x] 5.6 Implement structure validation

    - Implement \_validate_data_structure method
    - Verify output follows expected structure
    - _Requirements: 2.3, 3.3_

  - [ ]\* 5.7 Write property test for structure compliance

    - **Property 11: Structure Compliance**
    - **Validates: Requirements 2.3, 3.3**

  - [x] 5.8 Implement main validate_parsed_response method

    - Combine all validation steps
    - Generate clear error messages
    - _Requirements: 5.1, 5.2, 5.5_

  - [ ]\* 5.9 Write property test for error message clarity
    - **Property 17: Error Message Clarity**
    - **Validates: Requirements 5.5**

- [ ] 6. Checkpoint - Ensure validation logic tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement main ScrapedDataParser orchestration

  - [x] 7.1 Create ScrapedDataParser class

    - Initialize with DeepSeek client
    - Set up data extractor, prompt builder, and validator
    - _Requirements: 1.1_

  - [x] 7.2 Implement empty data validation

    - Check if ScrapingResult contains data
    - Raise EmptyDataError if no data
    - _Requirements: 1.2_

  - [ ]\* 7.3 Write property test for empty data rejection

    - **Property 2: Empty Data Rejection**
    - **Validates: Requirements 1.2**

  - [x] 7.4 Implement error handling for failed scraping

    - Handle ScrapingResult with success=False
    - Process error information gracefully
    - _Requirements: 1.4_

  - [ ]\* 7.5 Write property test for error information handling

    - **Property 4: Error Information Handling**
    - **Validates: Requirements 1.4**

  - [x] 7.6 Implement main parse_scraped_data method

    - Extract text from ScrapingResult
    - Build parsing prompt
    - Call DeepSeek API
    - Validate response
    - Create ParsedDataResponse with metadata
    - _Requirements: 1.1, 2.1, 3.1, 3.2, 4.2, 5.1, 6.2_

  - [ ]\* 7.7 Write property test for multiple source handling

    - **Property 3: Multiple Source Handling**
    - **Validates: Requirements 1.3**

  - [ ]\* 7.8 Write property test for record count preservation

    - **Property 15: Record Count Preservation**
    - **Validates: Requirements 4.2**

  - [x] 7.9 Implement retry logic for parsing failures

    - Retry on ParsingError and ValidationError
    - Maximum 2 retry attempts
    - _Requirements: 5.4_

  - [ ]\* 7.10 Write integration tests for parsing flow
    - Test end-to-end parsing with mocked DeepSeek API
    - Test error handling across component boundaries
    - _Requirements: 1.1, 3.1, 5.1_

- [ ] 8. Implement additional validation properties

  - [ ]\* 8.1 Write property test for field filtering

    - **Property 12: Field Filtering**
    - **Validates: Requirements 3.4**

  - [ ]\* 8.2 Write property test for missing data indication
    - **Property 13: Missing Data Indication**
    - **Validates: Requirements 3.5, 4.5**

- [ ] 9. Checkpoint - Ensure parser orchestration tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement UI components

  - [x] 10.1 Create render_parsed_response function

    - Display JSON with syntax highlighting
    - Add download and copy buttons
    - Show parsing metadata
    - _Requirements: 6.1, 6.2, 6.5_

  - [x] 10.2 Update render_error function

    - Add handling for EmptyDataError
    - Add handling for ParsingError
    - Add handling for ValidationError
    - Include troubleshooting suggestions
    - _Requirements: 6.4, 7.1, 7.2, 7.3_

  - [x] 10.3 Write unit tests for UI components
    - Test parsed response rendering with sample data
    - Test error rendering with different exception types
    - Verify metadata display
    - _Requirements: 6.2, 6.4_

- [x] 11. Integrate with existing app.py

  - [x] 11.1 Import ScrapedDataParser components

    - Add imports for parser, models, and exceptions
    - _Requirements: 1.1_

  - [x] 11.2 Initialize parser after scraping execution

    - Create ScrapedDataParser instance with DeepSeek client
    - Convert execution_result to ScrapingResult format
    - _Requirements: 1.1_

  - [x] 11.3 Add parsing step after successful scraping

    - Call parse_scraped_data with scraping result and form data
    - Display loading indicator during parsing
    - Handle parsing errors gracefully
    - _Requirements: 5.1, 6.3_

  - [x] 11.4 Update UI to display parsed JSON

    - Replace raw data preview with parsed JSON display
    - Show parsing metadata in expander
    - Add download/copy buttons for parsed JSON
    - _Requirements: 6.1, 6.2, 6.5_

  - [x] 11.5 Add error handling for parsing failures
    - Display clear error messages for each error type
    - Provide troubleshooting suggestions
    - Allow user to retry or modify requirements
    - _Requirements: 6.4, 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 12. Add configuration and documentation

  - [x] 12.1 Create ParsingConfig dataclass

    - Define default configuration values
    - Add max_text_length, temperature, max_tokens
    - _Requirements: 8.2_

  - [x] 12.2 Update README with parsing feature documentation
    - Document the parsing flow
    - Add examples of parsed output
    - Include troubleshooting section
    - _Requirements: 6.4_

- [ ] 13. Final checkpoint - End-to-end testing
  - Ensure all tests pass, ask the user if questions arise.
  - Manually test with various scraped data formats
  - Verify error handling for empty data
  - Test with actual DeepSeek API (if key available)
  - Verify UI displays parsed JSON correctly

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each property test task references a specific correctness property from the design document
- Checkpoints ensure incremental validation and allow for user feedback
- The implementation follows a bottom-up approach: utilities → prompt building → validation → orchestration → UI
- All property tests should run with minimum 100 iterations
- Mock the DeepSeek API for unit and property tests; use actual API only for manual integration testing
- The parser reuses existing DeepSeek client infrastructure for consistency
- Integration with app.py happens after core parsing logic is complete and tested
