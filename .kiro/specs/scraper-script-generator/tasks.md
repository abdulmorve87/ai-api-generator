# Implementation Plan: Scraper Script Generator

## Overview

This implementation plan breaks down the Scraper Script Generator feature into discrete coding tasks. The feature generates executable BeautifulSoup scraper scripts from user form inputs using AI, validates them for safety, and integrates with the existing scraping layer for execution.

## Tasks

- [x] 1. Create data models for script generation

  - Create `ai_layer/script_models.py` with GeneratedScript, ScriptMetadata, ScriptValidationResult dataclasses
  - Add ScriptValidationError and ScriptExecutionError exception classes
  - Include proper type hints and docstrings
  - _Requirements: 2.5, 4.5, 5.3_

- [ ]\* 1.1 Write unit tests for script models

  - Test dataclass instantiation and serialization
  - Test exception raising and error messages
  - _Requirements: 2.5, 4.5_

- [x] 2. Implement Script Validator component

  - [x] 2.1 Create `ai_layer/script_validator.py` with ScriptValidator class

    - Implement `validate_script()` method that performs all validation checks
    - Implement `check_syntax()` using Python's compile() function
    - Implement `check_imports()` to verify bs4 and requests are imported
    - Implement `check_forbidden_operations()` to scan for dangerous functions
    - Implement `check_function_signature()` to verify main function exists with `urls: List[str]` signature (updated for multi-source)
    - _Requirements: 4.1, 4.3, 4.4, 4.5_

  - [ ]\* 2.2 Write property test for syntax validation

    - **Property 9: Syntax Validation**
    - **Validates: Requirements 4.1**

  - [ ]\* 2.3 Write property test for import checking

    - **Property 5: Required Imports Presence**
    - **Validates: Requirements 2.1, 2.2, 4.3**

  - [ ]\* 2.4 Write property test for validation error messages

    - **Property 10: Validation Error Messages**
    - **Validates: Requirements 4.5, 8.1**

  - [ ]\* 2.5 Write unit tests for forbidden operations detection
    - Test detection of exec, eval, os.system, subprocess, **import**
    - Test scripts with safe operations pass validation
    - _Requirements: 4.1_

- [x] 3. Implement Script Prompt Builder component

  - [x] 3.1 Create `ai_layer/script_prompt_builder.py` with ScriptPromptBuilder class

    - Define SYSTEM_PROMPT constant with script generation instructions
    - Implement `build_script_prompt()` method
    - Include scraping layer configuration (timeout, user-agent) in prompt
    - Include required libraries (BeautifulSoup4, requests, lxml parser) in prompt
    - Include expected function signature `scrape_data(urls: List[str])` for multi-source scraping
    - Include user requirements (data description, optional URLs, fields, structure)
    - Support AI-suggested URLs when user doesn't provide data sources
    - Prioritize user-provided URLs over AI suggestions
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

  - [ ]\* 3.2 Write property test for prompt completeness

    - **Property 4: Prompt Construction Completeness**
    - **Validates: Requirements 1.4, 1.5, 6.1, 6.4, 6.5, 6.6, 6.7**

  - [ ]\* 3.3 Write property test for configuration integration

    - **Property 13: Configuration Integration**
    - **Validates: Requirements 6.2, 6.3, 7.1, 7.2, 7.3**

  - [ ]\* 3.4 Write unit tests for prompt builder
    - Test prompt with all fields provided
    - Test prompt with optional fields empty
    - Test prompt includes scraping configuration
    - _Requirements: 6.1, 6.2, 6.3_

- [ ] 4. Checkpoint - Ensure validation and prompt building tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement Scraper Script Generator component

  - [x] 5.1 Create `ai_layer/scraper_script_generator.py` with ScraperScriptGenerator class

    - Implement `__init__()` to accept DeepSeekClient and ScrapingConfig
    - Implement `generate_script()` main method
    - Implement `_extract_form_fields()` to extract form inputs
    - Implement `_build_script_prompt()` using ScriptPromptBuilder
    - Implement `_validate_script()` using ScriptValidator
    - Add error handling for generation and validation failures
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 4.1, 4.2_

  - [ ]\* 5.2 Write property test for form field extraction

    - **Property 1: Form Field Extraction Completeness**
    - **Validates: Requirements 1.1**

  - [ ]\* 5.3 Write property test for target URL inclusion

    - **Property 2: Target URL Inclusion**
    - **Validates: Requirements 1.2**

  - [ ]\* 5.4 Write property test for empty URL handling

    - **Property 3: Empty URL Handling**
    - **Validates: Requirements 1.3**

  - [ ]\* 5.5 Write unit tests for script generator
    - Test successful script generation flow
    - Test generation with missing required fields
    - Test generation with invalid JSON structure
    - Test validation failure handling
    - _Requirements: 1.1, 1.2, 4.2_

- [ ] 6. Implement AI Script Executor component

  - [ ] 6.1 Create `scraping_layer/script_execution/ai_script_executor.py` with AIScriptExecutor class

    - Implement `__init__()` to accept ScrapingEngine
    - Implement `execute_generated_script()` method
    - Implement `_create_safe_execution_environment()` for sandboxing
    - Implement `_execute_in_sandbox()` with timeout enforcement
    - Add error handling for execution failures
    - Return ScriptResult with data or errors
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ]\* 6.2 Write property test for executor interface

    - **Property 11: Script Executor Interface**
    - **Validates: Requirements 5.2**

  - [ ]\* 6.3 Write property test for execution result format

    - **Property 12: Execution Result Format**
    - **Validates: Requirements 5.3**

  - [ ]\* 6.4 Write unit tests for script executor
    - Test successful script execution
    - Test execution with runtime errors
    - Test timeout enforcement
    - Test sandbox environment creation
    - _Requirements: 5.2, 5.3, 5.4, 5.5_

- [ ] 7. Checkpoint - Ensure core components work together

  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Add property tests for generated script structure

  - [ ]\* 8.1 Write property test for required imports in generated scripts

    - **Property 5: Required Imports Presence**
    - **Validates: Requirements 2.1, 2.2, 4.3**

  - [ ]\* 8.2 Write property test for error handling in generated scripts

    - **Property 6: Error Handling Presence**
    - **Validates: Requirements 2.3, 2.4**

  - [ ]\* 8.3 Write property test for main function signature

    - **Property 7: Main Function Signature**
    - **Validates: Requirements 3.1, 4.4**

  - [ ]\* 8.4 Write property test for code documentation

    - **Property 8: Code Documentation**
    - **Validates: Requirements 3.3**

  - [ ]\* 8.5 Write property test for script return structure

    - **Property 14: Script Return Structure**
    - **Validates: Requirements 9.1, 9.2**

  - [ ]\* 8.6 Write property test for record field consistency
    - **Property 15: Record Field Consistency**
    - **Validates: Requirements 9.5**

- [ ] 9. Create integration module for end-to-end flow

  - [ ] 9.1 Create `ai_layer/script_generation_service.py` with ScriptGenerationService class

    - Implement high-level service that orchestrates: form input → script generation → validation → execution
    - Add configuration loading from environment
    - Add comprehensive error handling and logging
    - Return results in consistent format for UI
    - _Requirements: 1.1, 2.1, 4.1, 5.1, 8.1_

  - [ ]\* 9.2 Write integration tests for end-to-end flow
    - Test complete flow from form input to script execution
    - Test error handling at each stage
    - Test configuration propagation
    - _Requirements: 1.1, 2.1, 4.1, 5.1_

- [ ] 10. Update existing components for integration

  - [x] 10.1 Update `ai_layer/__init__.py` to export new classes

    - Export ScraperScriptGenerator, ScriptValidator, ScriptPromptBuilder
    - Export script models and exceptions
    - _Requirements: N/A_

  - [ ] 10.2 Update `scraping_layer/script_execution/__init__.py` to export AIScriptExecutor
    - Export AIScriptExecutor class
    - _Requirements: N/A_

- [ ] 11. Add example usage and documentation

  - [x] 11.1 Create `ai_layer/examples/script_generation_example.py`

    - Demonstrate basic script generation usage
    - Show configuration setup
    - Show error handling
    - _Requirements: N/A_

  - [ ]\* 11.2 Update README with script generation feature documentation
    - Document new feature capabilities
    - Provide usage examples
    - Document configuration options
    - _Requirements: N/A_

- [x] 12. Final checkpoint - Run all tests and verify integration
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests verify end-to-end functionality
- The implementation reuses existing DeepSeek Client and Scraping Engine components
- All generated scripts must pass validation before execution for safety
