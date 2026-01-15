# Implementation Plan: API Endpoint Server

## Overview

This implementation creates a local API server that exposes parsed JSON data from the Scraped Data Parser as HTTP endpoints. The implementation follows a bottom-up approach: data models first, then storage layer, endpoint management, and finally the HTTP server with integration into the Streamlit app.

## Tasks

- [x] 1. Set up project structure and data models

  - [x] 1.1 Create api_server directory with **init**.py

    - Create `api_server/` directory structure
    - Add `__init__.py` with module exports
    - _Requirements: 1.1, 1.2_

  - [x] 1.2 Implement data models (EndpointData, EndpointMetadata, EndpointInfo)

    - Create `api_server/models.py` with dataclasses
    - Implement to_dict() and from_dict() methods for serialization
    - Add EndpointCreationError, EndpointNotFoundError, ServerStartError exceptions
    - _Requirements: 1.2, 6.3, 6.4_

  - [ ]\* 1.3 Write property test for data model serialization round-trip
    - **Property 2: Data Persistence Round-Trip (partial - model serialization)**
    - **Validates: Requirements 6.4**

- [x] 2. Implement DataStore (SQLite persistence layer)

  - [x] 2.1 Create DataStore class with SQLite initialization

    - Create `api_server/data_store.py`
    - Implement **init** with database path and table creation
    - Create endpoints table with schema from design
    - _Requirements: 6.1, 6.2_

  - [x] 2.2 Implement store_endpoint method

    - Generate unique endpoint_id using UUID
    - Serialize JSON data and metadata
    - Insert into SQLite database
    - _Requirements: 1.2, 6.3_

  - [x] 2.3 Implement get_endpoint and list_endpoints methods

    - Retrieve endpoint by ID with deserialization
    - List all endpoints with metadata only
    - _Requirements: 2.1, 3.1, 3.2_

  - [x] 2.4 Implement delete_endpoint method

    - Delete by endpoint_id
    - Return True if deleted, False if not found
    - _Requirements: 4.1_

  - [ ]\* 2.5 Write property test for DataStore round-trip
    - **Property 2: Data Persistence Round-Trip (storage layer)**
    - **Validates: Requirements 1.2, 6.4**

- [x] 3. Checkpoint - Verify data layer

  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement EndpointManager

  - [x] 4.1 Create EndpointManager class

    - Create `api_server/endpoint_manager.py`
    - Initialize with DataStore instance
    - Implement create_endpoint method with validation
    - _Requirements: 1.1, 1.3, 1.4_

  - [x] 4.2 Implement endpoint retrieval and listing

    - Implement get_endpoint method
    - Implement list_endpoints method
    - Implement get_access_url helper
    - _Requirements: 2.1, 3.1, 3.2_

  - [x] 4.3 Implement delete_endpoint method

    - Delete endpoint via DataStore
    - Return success/failure status
    - _Requirements: 4.1, 4.2_

  - [ ]\* 4.4 Write property test for endpoint creation uniqueness

    - **Property 1: Endpoint Creation Uniqueness**
    - **Validates: Requirements 1.1**

  - [ ]\* 4.5 Write property test for invalid input rejection
    - **Property 4: Invalid Input Rejection**
    - **Validates: Requirements 1.4**

- [x] 5. Implement APIServer (FastAPI)

  - [x] 5.1 Create FastAPI application with routes

    - Create `api_server/server.py`
    - Implement GET /api/data/{endpoint_id} route
    - Implement GET /api/endpoints route
    - Implement DELETE /api/endpoints/{endpoint_id} route
    - Implement GET /health route
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 4.1, 4.2, 4.3_

  - [x] 5.2 Implement metadata query parameter support

    - Add ?metadata=true query parameter handling
    - Return data with or without metadata based on parameter
    - _Requirements: 2.4_

  - [x] 5.3 Implement server lifecycle management

    - Create APIServer class wrapper
    - Implement start() method with background thread
    - Implement stop() method for graceful shutdown
    - Handle port configuration and fallback
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ]\* 5.4 Write property test for 404 responses

    - **Property 5: Non-Existent Endpoint Returns 404**
    - **Validates: Requirements 2.2, 4.3**

  - [ ]\* 5.5 Write property test for list consistency

    - **Property 8: List Consistency**
    - **Validates: Requirements 3.1, 3.2**

  - [ ]\* 5.6 Write property test for delete removes endpoint
    - **Property 9: Delete Removes Endpoint**
    - **Validates: Requirements 4.1, 4.2**

- [x] 6. Checkpoint - Verify API server

  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Integrate with Streamlit app

  - [x] 7.1 Add API server initialization to app.py

    - Import APIServer and EndpointManager
    - Initialize server on app startup
    - Add server status indicator to UI
    - _Requirements: 5.1, 5.2_

  - [x] 7.2 Add "Create API Endpoint" button after parsing

    - Add button in results section after successful parsing
    - Call EndpointManager.create_endpoint on click
    - Display access URL to user
    - _Requirements: 1.1, 1.3_

  - [x] 7.3 Add endpoint management UI section
    - Display list of created endpoints
    - Add delete button for each endpoint
    - Show endpoint access URLs
    - _Requirements: 3.1, 3.2, 4.1_

- [x] 8. Final checkpoint - End-to-end verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- FastAPI provides automatic OpenAPI documentation at /docs
