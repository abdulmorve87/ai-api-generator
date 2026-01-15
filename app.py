import streamlit as st
from utils.ui_components import render_header
from utils.styles import load_custom_css
from components.form import render_api_form
from components.results import render_error, render_parsed_response

# AI Layer imports
from ai_layer import (
    DeepSeekConfig,
    DeepSeekClient,
    ScraperScriptGenerator,
    ConfigurationError,
    ScrapedDataParser,
    EmptyDataError,
    ParsingError
)
from scraping_layer.config import ScrapingConfig

# Dynamic Execution imports (AI-Scraping Integration)
from scraping_layer.dynamic_execution import (
    AIScrapingIntegration,
    DynamicScriptExecutor,
    ConsoleOutputFormatter,
    ExecutionConfig
)

# API Server imports
from api_server import (
    APIServer,
    EndpointManager,
    DataStore,
    EndpointCreationError
)

import re

def _extract_url_from_script(script_code: str) -> str:
    """
    Extract a suggested URL from the generated script's DEFAULT_URLS list or comments.
    
    AI-generated scripts should include a DEFAULT_URLS list at the top like:
    DEFAULT_URLS = ['https://example.com/data', 'https://other.com/info']
    
    Returns:
        First valid URL found, or empty string if none found
    """
    # Pattern to match DEFAULT_URLS list - highest priority
    default_urls_pattern = r'DEFAULT_URLS\s*=\s*\[(.*?)\]'
    match = re.search(default_urls_pattern, script_code, re.DOTALL)
    if match:
        urls_content = match.group(1)
        # Extract URLs from the list
        url_matches = re.findall(r'[\'\"](https?://[^\s\'\"\,]+)[\'\"]\s*,?', urls_content)
        for url in url_matches:
            url = url.strip().rstrip('.,;:\'\"')
            # Skip placeholder/example URLs
            if 'example.com' not in url and 'example-' not in url and url.startswith('http'):
                return url
    
    # Fallback patterns for URLs in comments or assignments
    url_patterns = [
        # Match URLs in comments with dash prefix (common format)
        r'#\s*-?\s*(https?://[^\s<>]+)',
        # Match test_url or example_url assignments
        r'(?:test_url|example_url|url)\s*=\s*[\'"](https?://[^\s<>]+)[\'"]',
        # Match any URL in quotes
        r'[\'"](https?://[^\s<>]+)[\'"]',
    ]
    
    for pattern in url_patterns:
        matches = re.findall(pattern, script_code, re.IGNORECASE)
        for match in matches:
            url = match.strip().rstrip('.,;:\'\"')
            # Skip example.com and sites that require auth
            skip_domains = ['example.com', 'example-', 'goodreads.com', 'amazon.com']
            if any(domain in url for domain in skip_domains):
                continue
            if url.startswith('http'):
                return url
    
    return ''


def _extract_all_urls_from_script(script_code: str) -> list:
    """
    Extract all URLs from the generated script's DEFAULT_URLS list.
    
    Returns:
        List of valid URLs found
    """
    urls = []
    
    # Pattern to match DEFAULT_URLS list
    default_urls_pattern = r'DEFAULT_URLS\s*=\s*\[(.*?)\]'
    match = re.search(default_urls_pattern, script_code, re.DOTALL)
    if match:
        urls_content = match.group(1)
        # Extract URLs from the list
        url_matches = re.findall(r'[\'\"](https?://[^\s\'\"\,]+)[\'\"]\s*,?', urls_content)
        for url in url_matches:
            url = url.strip().rstrip('.,;:\'\"')
            # Skip placeholder/example URLs
            if 'example.com' not in url and 'example-' not in url and url.startswith('http'):
                urls.append(url)
    
    return urls

# Page configuration
st.set_page_config(
    page_title="AI API Generator",
    page_icon="🚀",
    layout="wide"
)

# Load custom CSS
load_custom_css()

# Initialize AI Layer (with error handling for missing API key)
@st.cache_resource
def initialize_ai_components():
    """Initialize the Script Generator and Data Parser with configuration."""
    try:
        deepseek_config = DeepSeekConfig.from_env()
        scraping_config = ScrapingConfig.from_env()
        
        client = DeepSeekClient(deepseek_config.api_key, deepseek_config.base_url)
        script_generator = ScraperScriptGenerator(client, scraping_config)
        
        # Initialize the dynamic executor for running generated scripts
        execution_config = ExecutionConfig(timeout_seconds=60)
        executor = DynamicScriptExecutor(execution_config)
        formatter = ConsoleOutputFormatter(use_colors=False, max_records_display=20)
        
        # Initialize the scraped data parser
        data_parser = ScrapedDataParser(client)
        
        return script_generator, executor, formatter, data_parser, None
    except ConfigurationError as e:
        return None, None, None, None, e

script_generator, executor, formatter, data_parser, config_error = initialize_ai_components()

# Initialize API Server
@st.cache_resource
def initialize_api_server():
    """Initialize the API Server for serving parsed data as endpoints."""
    try:
        print("\n" + "="*80)
        print("INITIALIZING API SERVER...")
        print("="*80)
        
        data_store = DataStore()
        print(f"✓ DataStore initialized (db: {data_store.db_path})")
        
        endpoint_manager = EndpointManager(data_store)
        print("✓ EndpointManager initialized")
        
        api_server = APIServer(data_store)
        print(f"✓ APIServer created (target port: {api_server.port})")
        
        # Start the server
        base_url = api_server.start()
        endpoint_manager.set_base_url(base_url)
        
        print(f"✓ Server started at {base_url}")
        print("="*80 + "\n")
        
        return api_server, endpoint_manager, None
    except Exception as e:
        import traceback
        print("\n" + "="*80)
        print("API SERVER INITIALIZATION FAILED")
        print("="*80)
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        print("="*80 + "\n")
        return None, None, e

api_server, endpoint_manager, api_server_error = initialize_api_server()

# Render header
render_header()

# Show API Server status in sidebar
with st.sidebar:
    st.subheader("🔌 API Server")
    
    # Debug info
    print(f"[Sidebar] Checking API server status...")
    print(f"[Sidebar] api_server_error={api_server_error}")
    print(f"[Sidebar] api_server={api_server}")
    print(f"[Sidebar] endpoint_manager={endpoint_manager}")
    
    if api_server_error:
        st.error(f"❌ Server Error: {api_server_error}")
        print(f"[Sidebar] Displaying error: {api_server_error}")
    elif api_server is None:
        st.warning("⚠️ API Server not initialized")
        print(f"[Sidebar] API Server is None")
    elif api_server.is_running():
        server_url = api_server.get_base_url()
        st.success(f"✅ Running at {server_url}")
        print(f"[Sidebar] Server running at {server_url}")
        
        # Show existing endpoints
        if endpoint_manager:
            try:
                endpoints = endpoint_manager.list_endpoints()
                print(f"[Sidebar] Found {len(endpoints)} endpoints")
                if endpoints:
                    st.markdown("---")
                    st.subheader("📋 Your Endpoints")
                    for ep in endpoints:
                        # Show description as the main title
                        display_title = ep.description if ep.description else ep.endpoint_id
                        with st.expander(f"🔗 {display_title}"):
                            # Make URL clickable
                            st.markdown(f"**URL:** [{ep.access_url}]({ep.access_url})")
                            st.write(f"**ID:** `{ep.endpoint_id}`")
                            st.write(f"**Records:** {ep.records_count}")
                            st.write(f"**Created:** {ep.created_at.strftime('%Y-%m-%d %H:%M')}")
                            if st.button("🗑️ Delete", key=f"del_{ep.endpoint_id}"):
                                if endpoint_manager.delete_endpoint(ep.endpoint_id):
                                    st.success("Deleted!")
                                    st.rerun()
            except Exception as e:
                print(f"[Sidebar] Error listing endpoints: {e}")
                st.error(f"Error listing endpoints: {e}")
    else:
        st.warning("⚠️ Server not running")
        print(f"[Sidebar] Server not running")

# Render main form and get submission status
form_data = render_api_form()

# Handle form submission
if form_data['submitted']:
    if not form_data['data_description']:
        st.error("⚠️ Please provide a data description to continue")
    else:
        # Check if script generator is available
        if config_error:
            render_error(config_error)
        elif script_generator is None:
            st.error("⚠️ Script Generator not initialized. Please check your configuration.")
        else:
            # Show loading state
            with st.spinner("🤖 AI is generating scraper script..."):
                try:
                    # Generate scraper script and print to console
                    print("\n" + "="*80)
                    print("GENERATING SCRAPER SCRIPT...")
                    print("="*80)
                    print(f"Data Description: {form_data['data_description']}")
                    print(f"Data Source: {form_data.get('data_source', 'Not provided - AI will suggest URLs')}")
                    print(f"Desired Fields: {form_data.get('desired_fields', 'N/A')}")
                    print("="*80)
                    
                    # Generate script (ONLY AI call now)
                    generated_script = script_generator.generate_script(form_data)
                    
                    print("\n" + "="*80)
                    print("SCRAPER SCRIPT GENERATED SUCCESSFULLY")
                    print("="*80)
                    print(f"Validation Status: {'✓ VALID' if generated_script.is_valid else '✗ INVALID'}")
                    print(f"  - Syntax Valid: {generated_script.validation_result.syntax_valid}")
                    print(f"  - Imports Valid: {generated_script.validation_result.imports_valid}")
                    print(f"  - No Forbidden Ops: {generated_script.validation_result.no_forbidden_ops}")
                    print(f"  - Function Signature Valid: {generated_script.validation_result.function_signature_valid}")
                    
                    if generated_script.validation_result.errors:
                        print("\nValidation Errors:")
                        for error in generated_script.validation_result.errors:
                            print(f"  - {error}")
                    
                    print("\n" + "="*80)
                    print("GENERATED SCRIPT CODE:")
                    print("="*80)
                    print(generated_script.script_code)
                    print("="*80)
                    print(f"Generation Time: {generated_script.metadata.generation_time_ms}ms")
                    print(f"Tokens Used: {generated_script.metadata.tokens_used}")
                    print(f"Model: {generated_script.metadata.model}")
                    print("="*80 + "\n")
                    
                    # Show success message on UI
                    st.success("✅ Scraper script generated successfully!")
                    
                except Exception as e:
                    print("\n" + "="*80)
                    print("SCRAPER SCRIPT GENERATION FAILED")
                    print("="*80)
                    print(f"Error: {str(e)}")
                    print("="*80 + "\n")
                    render_error(e)
                    generated_script = None
            
            # Execute the generated script if valid
            if generated_script and generated_script.is_valid and executor:
                with st.spinner("🔄 Executing scraper script..."):
                    try:
                        print("\n" + "="*80)
                        print("EXECUTING SCRAPER SCRIPT...")
                        print("="*80)
                        
                        # Get target URLs from form or extract from script
                        user_url = form_data.get('data_source', '').strip()
                        script_urls = _extract_all_urls_from_script(generated_script.script_code)
                        
                        # Build list of URLs to try (user URL first, then script URLs, avoiding duplicates)
                        urls_to_try = []
                        seen_urls = set()
                        
                        # Add user URL first (highest priority)
                        if user_url and user_url not in seen_urls:
                            urls_to_try.append(user_url)
                            seen_urls.add(user_url)
                        
                        # Add script URLs (avoiding duplicates)
                        for script_url in script_urls:
                            if script_url not in seen_urls:
                                urls_to_try.append(script_url)
                                seen_urls.add(script_url)
                        
                        if not urls_to_try:
                            print("No target URL provided or found in script")
                            print("="*80 + "\n")
                            st.warning("⚠️ No target URL provided. Please enter a data source URL to scrape.")
                            st.info("💡 Tip: The generated script is ready. Add a URL in the 'Data Source' field and submit again.")
                            raise ValueError("No target URL available for scraping")
                        
                        print(f"URLs to scrape: {urls_to_try}")
                        print("="*80 + "\n")
                        
                        # Execute against all URLs using multi-source execution
                        # This properly aggregates data from all sources
                        if len(urls_to_try) > 1:
                            # Use multi-source execution for multiple URLs
                            execution_result = executor.execute_multi_source(
                                script_code=generated_script.script_code,
                                target_urls=urls_to_try
                            )
                            
                            # Log individual source results
                            for source_result in execution_result.source_results:
                                if source_result.success:
                                    print(f"--- Trying URL: {source_result.source_url} ---")
                                    print(f"✓ Success! Got {source_result.record_count} records")
                                else:
                                    print(f"--- Trying URL: {source_result.source_url} ---")
                                    print(f"✗ Failed: {source_result.error}")
                        else:
                            # Single URL - use regular execution
                            target_url = urls_to_try[0]
                            print(f"--- Trying URL: {target_url} ---")
                            execution_result = executor.execute_code(
                                script_code=generated_script.script_code,
                                target_url=target_url
                            )
                            if execution_result.success and execution_result.data:
                                print(f"✓ Success! Got {len(execution_result.data)} records")
                            else:
                                print(f"✗ Failed: {execution_result.errors[0] if execution_result.errors else 'No data returned'}")
                        
                        # Print formatted results to console
                        print("\n" + "="*80)
                        print("SCRAPING EXECUTION RESULT")
                        print("="*80)
                        formatted_output = formatter.format_result(execution_result)
                        print(formatted_output)
                        print("="*80 + "\n")
                        
                        # Show result summary on UI
                        if execution_result.success and execution_result.data:
                            st.success(f"✅ Scraping completed! Extracted {len(execution_result.data)} records")
                            
                            # Show data preview in UI
                            st.subheader("📊 Extracted Data Preview")
                            
                            # Show first few records
                            import pandas as pd
                            preview_data = execution_result.data[:10]
                            
                            # Clean up internal fields for display
                            clean_data = []
                            for record in preview_data:
                                clean_record = {k: v for k, v in record.items() if not k.startswith('_')}
                                clean_data.append(clean_record)
                            
                            if clean_data:
                                df = pd.DataFrame(clean_data)
                                st.dataframe(df, use_container_width=True)
                            
                            if len(execution_result.data) > 10:
                                st.info(f"Showing 10 of {len(execution_result.data)} records. Check console for full output.")
                            
                            # Show metadata
                            with st.expander("📈 Execution Metadata"):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Total Records", len(execution_result.data))
                                with col2:
                                    st.metric("URLs Tried", len(urls_to_try))
                                with col3:
                                    st.metric("Errors", len(execution_result.errors))
                                
                                # Show source results if available
                                if execution_result.source_results:
                                    st.write("**Source Results:**")
                                    for sr in execution_result.source_results:
                                        status = "✓" if sr.success else "✗"
                                        st.write(f"{status} {sr.source_url}: {sr.record_count} records ({sr.scraping_method}, {sr.confidence} confidence)")
                                
                                st.write(f"**Scraping Method:** {execution_result.metadata.scraping_method}")
                                st.write(f"**Confidence:** {execution_result.metadata.confidence}")
                            
                            # NEW: Parse scraped data into structured JSON
                            if data_parser:
                                st.markdown("---")
                                with st.spinner("🤖 AI is parsing scraped data into structured JSON..."):
                                    try:
                                        print("\n" + "="*80)
                                        print("PARSING SCRAPED DATA...")
                                        print("="*80)
                                        print(f"Records to parse: {len(execution_result.data)}")
                                        print(f"User requirements: {form_data.get('desired_fields', 'N/A')}")
                                        print("="*80)
                                        
                                        # Parse the scraped data
                                        parsed_response = data_parser.parse_scraped_data(
                                            scraping_result=execution_result,
                                            user_requirements=form_data
                                        )
                                        
                                        print("\n" + "="*80)
                                        print("DATA PARSED SUCCESSFULLY")
                                        print("="*80)
                                        print(f"Records parsed: {parsed_response.metadata.records_parsed}")
                                        print(f"Fields extracted: {', '.join(parsed_response.metadata.fields_extracted)}")
                                        print(f"Parsing time: {parsed_response.metadata.parsing_time_ms}ms")
                                        print("="*80)
                                        print("PARSED JSON OUTPUT:")
                                        print("="*80)
                                        import json
                                        print(json.dumps(parsed_response.data, indent=2, default=str))
                                        print("="*80 + "\n")
                                        
                                        # Render the parsed response in UI
                                        render_parsed_response(parsed_response)
                                        
                                        # Store parsed_response in session state for API endpoint creation
                                        st.session_state['last_parsed_response'] = parsed_response
                                        st.session_state['last_form_data'] = form_data
                                        st.session_state['show_create_endpoint'] = True
                                        
                                    except (EmptyDataError, ParsingError) as e:
                                        print("\n" + "="*80)
                                        print("DATA PARSING FAILED")
                                        print("="*80)
                                        print(f"Error: {str(e)}")
                                        print("="*80 + "\n")
                                        render_error(e)
                                    except Exception as e:
                                        print("\n" + "="*80)
                                        print("DATA PARSING FAILED")
                                        print("="*80)
                                        print(f"Error: {str(e)}")
                                        import traceback
                                        print(traceback.format_exc())
                                        print("="*80 + "\n")
                                        st.error(f"❌ Data parsing failed: {str(e)}")
                        else:
                            st.error(f"❌ Scraping failed for all URLs")
                            
                            # Show errors in expander
                            if execution_result.errors:
                                with st.expander("🔍 Error Details"):
                                    for error in execution_result.errors:
                                        st.error(error)
                        
                    except Exception as e:
                        print("\n" + "="*80)
                        print("SCRIPT EXECUTION FAILED")
                        print("="*80)
                        print(f"Error: {str(e)}")
                        import traceback
                        print(traceback.format_exc())
                        print("="*80 + "\n")
                        st.error(f"❌ Script execution failed: {str(e)}")

# ============================================================================
# API ENDPOINT CREATION SECTION (Outside form submission to handle button clicks)
# ============================================================================
if st.session_state.get('show_create_endpoint') and st.session_state.get('last_parsed_response'):
    print("[CreateEndpoint] Session state has parsed response, showing create endpoint UI")
    
    if endpoint_manager:
        st.markdown("---")
        st.subheader("🚀 Create API Endpoint")
        st.write("Mount this data as a REST API endpoint for easy access.")
        
        # Get description from session state
        last_form_data = st.session_state.get('last_form_data', {})
        default_desc = last_form_data.get('data_description', 'API Endpoint')[:100]
        
        col1, col2 = st.columns([3, 1])
        with col1:
            endpoint_desc = st.text_input(
                "Endpoint Description (optional)",
                value=default_desc,
                key="endpoint_description_input"
            )
        with col2:
            st.write("")  # Spacer
            st.write("")  # Spacer
            create_clicked = st.button("🔗 Create Endpoint", type="primary", key="create_endpoint_btn")
        
        if create_clicked:
            print("\n" + "="*80)
            print("[CreateEndpoint] BUTTON CLICKED - Creating API endpoint...")
            print("="*80)
            
            try:
                parsed_response = st.session_state['last_parsed_response']
                print(f"[CreateEndpoint] Got parsed_response from session state")
                print(f"[CreateEndpoint] Data keys: {list(parsed_response.data.keys()) if parsed_response.data else 'None'}")
                
                endpoint_info = endpoint_manager.create_endpoint(
                    parsed_response=parsed_response,
                    description=endpoint_desc
                )
                
                st.success(f"✅ API Endpoint Created Successfully!")
                st.code(endpoint_info.access_url, language="text")
                st.info(f"📊 {endpoint_info.records_count} records available at this endpoint")
                st.balloons()
                
                print(f"[CreateEndpoint] ✅ SUCCESS!")
                print(f"[CreateEndpoint] Endpoint ID: {endpoint_info.endpoint_id}")
                print(f"[CreateEndpoint] Access URL: {endpoint_info.access_url}")
                print(f"[CreateEndpoint] Records: {endpoint_info.records_count}")
                print("="*80 + "\n")
                
                # Clear the flag so it doesn't show again after rerun
                # st.session_state['show_create_endpoint'] = False
                
            except EndpointCreationError as e:
                print(f"[CreateEndpoint] EndpointCreationError: {e}")
                st.error(f"❌ Failed to create endpoint: {str(e)}")
            except Exception as e:
                import traceback
                print(f"[CreateEndpoint] Unexpected error: {e}")
                print(traceback.format_exc())
                st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("⚠️ API Server not available. Cannot create endpoints.")
        print("[CreateEndpoint] endpoint_manager is None")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>Built for Hackathon 2025 | Powered by AI</p>
    <p style="font-size: 0.9rem;">🔒 All generated APIs include authentication, rate limiting, and comprehensive documentation</p>
</div>
""", unsafe_allow_html=True)