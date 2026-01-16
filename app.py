import streamlit as st
from utils.ui_components import render_header
from utils.styles import load_custom_css
from components.form import render_api_form
from components.results import render_error, render_parsed_response
from components.input_help import render_input_format_guide, show_validation_summary

# Console Logger for colorful output
from utils.console_logger import logger as console_logger

# AI Layer imports
from ai_layer import (
    DeepSeekConfig,
    DeepSeekClient,
    ScraperScriptGenerator,
    ConfigurationError,
    ScrapedDataParser,
    EmptyDataError,
    ParsingError,
    InputStandardizer,
    StandardizedInput
)
from ai_layer.script_prompt_builders.script_prompt_builder import ScriptPromptBuilder
from ai_layer.script_prompt_builders.script_validator import ScriptValidator
from ai_layer.script_prompt_builders.light_script_propmt_builder import HTMLExtractorPromptBuilder
from ai_layer.script_prompt_builders.light_script_validator import ScriptValidator as LightScriptValidator
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
import json

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
        
        # Initialize standard (traditional) script generator
        standard_prompt_builder = ScriptPromptBuilder(scraping_config)
        standard_validator = ScriptValidator()
        standard_script_generator = ScraperScriptGenerator(
            client, scraping_config, standard_prompt_builder, standard_validator
        )
        
        # Initialize light script generator
        light_prompt_builder = HTMLExtractorPromptBuilder(scraping_config)
        light_validator = LightScriptValidator()
        light_script_generator = ScraperScriptGenerator(
            client, scraping_config, light_prompt_builder, light_validator
        )
        
        # Initialize the dynamic executor for running generated scripts
        execution_config = ExecutionConfig(timeout_seconds=60)
        executor = DynamicScriptExecutor(execution_config)
        formatter = ConsoleOutputFormatter(use_colors=False, max_records_display=20)
        
        # Initialize the scraped data parser
        data_parser = ScrapedDataParser(client)
        
        return standard_script_generator, light_script_generator, executor, formatter, data_parser, None
    except ConfigurationError as e:
        return None, None, None, None, None, e

standard_script_generator, light_script_generator, executor, formatter, data_parser, config_error = initialize_ai_components()

# Initialize API Server
@st.cache_resource
def initialize_api_server():
    """Initialize the API Server for serving parsed data as endpoints."""
    try:
        console_logger.section("API Server Initialization", "🔌")
        
        data_store = DataStore()
        console_logger.success(f"DataStore initialized (db: {data_store.db_path})")
        
        endpoint_manager = EndpointManager(data_store)
        console_logger.success("EndpointManager initialized")
        
        api_server = APIServer(data_store)
        console_logger.success(f"APIServer created (target port: {api_server.port})")
        
        # Start the server
        base_url = api_server.start()
        endpoint_manager.set_base_url(base_url)
        
        console_logger.success(f"Server started at {base_url}")
        console_logger.info(f"API docs available at {base_url}/docs")
        
        return api_server, endpoint_manager, None
    except Exception as e:
        console_logger.error(f"API Server initialization failed: {str(e)}")
        return None, None, e

api_server, endpoint_manager, api_server_error = initialize_api_server()

# Render header
render_header()

# ============================================================================
# SIDEBAR - Reorganized order: 1) Server Status, 2) Endpoints, 3) Instructions
# ============================================================================
with st.sidebar:
    # 1. API SERVER STATUS (First - most important)
    st.markdown("### 🔌 API Server Status")
    
    if api_server_error:
        st.error(f"❌ Server Error")
        with st.expander("Error Details"):
            st.code(str(api_server_error))
    elif api_server is None:
        st.warning("⚠️ Not Initialized")
    elif api_server.is_running():
        server_url = api_server.get_base_url()
        st.success(f"✅ Live")
        st.caption(f"Running at: `{server_url}`")
    else:
        st.warning("⚠️ Not Running")
    
    st.markdown("---")
    
    # 2. API ENDPOINTS (Second - user's created endpoints)
    st.markdown("### 📋 API Endpoints")
    
    if endpoint_manager and api_server and api_server.is_running():
        try:
            endpoints = endpoint_manager.list_endpoints()
            
            if endpoints:
                st.caption(f"{len(endpoints)} endpoint(s) available")
                
                for ep in endpoints:
                    display_title = ep.description[:40] + "..." if len(ep.description) > 40 else ep.description
                    
                    with st.expander(f"🔗 {display_title}", expanded=False):
                        st.markdown(f"**URL:**")
                        st.code(ep.access_url, language="text")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Records", ep.records_count)
                        with col2:
                            st.caption(f"Created: {ep.created_at.strftime('%m/%d %H:%M')}")
                        
                        if st.button("🗑️ Delete", key=f"del_{ep.endpoint_id}", use_container_width=True):
                            if endpoint_manager.delete_endpoint(ep.endpoint_id):
                                st.success("Deleted!")
                                st.rerun()
            else:
                st.info("No endpoints yet. Create one below!")
        except Exception as e:
            st.error(f"Error loading endpoints")
            with st.expander("Error Details"):
                st.code(str(e))
    else:
        st.info("Server must be running to view endpoints")
    
    st.markdown("---")
    
    # 3. INSTRUCTIONS (Third - help documentation)
    st.markdown("### 📖 Instructions")

# Render input format guide (now under Instructions section)
render_input_format_guide()

# Render main form and get submission status
form_data = render_api_form()

# Handle form submission
if form_data['submitted']:
    # Validate and standardize inputs FIRST
    standardized_input, validation_errors = InputStandardizer.standardize_form_input(form_data)
    
    if validation_errors:
        # Show validation errors to user
        error_message = InputStandardizer.format_validation_errors(validation_errors)
        st.error(error_message)
        
        # Show examples for fixing errors
        with st.expander("💡 Need help with input formats?"):
            examples = InputStandardizer.get_input_examples()
            
            if any('URL' in err or 'url' in err.lower() for err in validation_errors):
                st.markdown("**URL Format:**")
                st.info(examples['data_source'])
            
            if any('field' in err.lower() for err in validation_errors):
                st.markdown("**Field Format:**")
                st.info(examples['desired_fields'])
            
            if any('JSON' in err or 'json' in err.lower() for err in validation_errors):
                st.markdown("**JSON Format:**")
                st.info(examples['response_structure'])
        
        st.stop()  # Stop execution if validation fails
    
    # Show validation summary
    show_validation_summary(standardized_input)
    
    if not form_data['data_description']:
        st.error("⚠️ Please provide a data description to continue")
    else:
        # Check if script generator is available
        if config_error:
            render_error(config_error)
        elif standard_script_generator is None or light_script_generator is None:
            st.error("⚠️ Script Generator not initialized. Please check your configuration.")
        else:
            # Choose the appropriate script generator based on toggle
            script_generator = light_script_generator if form_data.get('use_light_scraping', False) else standard_script_generator
            scraping_mode = "Light Scraping (HTML + AI)" if form_data.get('use_light_scraping', False) else "Traditional Scraping (BeautifulSoup)"
            
            # Start colorful console logging for the entire workflow
            console_logger.start_api_generation(form_data)
            
            # Show loading state
            with st.spinner(f"🤖 AI is generating scraper script using {scraping_mode}..."):
                try:
                    # PHASE 1: Script Generation
                    console_logger.log_script_generation_start(scraping_mode)
                    
                    # Generate script (ONLY AI call now)
                    generated_script = script_generator.generate_script(form_data)
                    
                    # Log script generation results
                    console_logger.log_script_generation_complete(
                        generated_script.validation_result,
                        generated_script.metadata
                    )
                    
                    print("\n" + "="*80)
                    # Show success message on UI
                    st.success(f"✅ Scraper script generated successfully using {scraping_mode}!")
                    
                except Exception as e:
                    console_logger.log_workflow_error("Script Generation", e)
                    render_error(e)
                    generated_script = None
            
            # Execute the generated script if valid
            if generated_script and generated_script.is_valid and executor:
                # Execute with spinner, then display results outside spinner
                execution_result = None
                urls_to_try = []
                
                try:
                    with st.spinner("🔄 Executing scraper script..."):
                        # Get target URLs from form or extract from script
                        user_url = form_data.get('data_source', '').strip()
                        script_urls = _extract_all_urls_from_script(generated_script.script_code)
                        
                        # Build list of URLs to try (user URL first, then script URLs, avoiding duplicates)
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
                            console_logger.warning("No target URL provided or found in script")
                            st.warning("⚠️ No target URL provided. Please enter a data source URL to scrape.")
                            st.info("💡 Tip: The generated script is ready. Add a URL in the 'Data Source' field and submit again.")
                            raise ValueError("No target URL available for scraping")
                        
                        # PHASE 2: Data Scraping
                        console_logger.log_scraping_start(urls_to_try)
                        
                        # Execute against all URLs using multi-source execution
                        # This properly aggregates data from all sources
                        if len(urls_to_try) > 1:
                            # Use multi-source execution for multiple URLs
                            execution_result = executor.execute_multi_source(
                                script_code=generated_script.script_code,
                                target_urls=urls_to_try
                            )
                        else:
                            # Single URL - use regular execution
                            target_url = urls_to_try[0]
                            # Single URL - use regular execution with progress
                            with console_logger.scraping_progress([target_url]) as progress:
                                progress.start_url(target_url, 0)
                                execution_result = executor.execute_code(
                                    script_code=generated_script.script_code,
                                    target_url=target_url
                                )
                                if execution_result.success and execution_result.data:
                                    progress.complete_url(target_url, len(execution_result.data), success=True)
                                else:
                                    progress.complete_url(target_url, 0, success=False)
                                progress.finish(len(execution_result.data) if execution_result.data else 0)
                        
                        # Log scraping completion
                        if execution_result and execution_result.success:
                            console_logger.log_scraping_complete(
                                len(execution_result.data) if execution_result.data else 0,
                                execution_result.source_results
                            )
                    
                    # Show result summary on UI (OUTSIDE spinner context)
                    if execution_result and execution_result.success and execution_result.data:
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
                        
                        # PHASE 3: Parse scraped data into structured JSON
                        if data_parser:
                            st.markdown("---")
                            
                            # Store execution result and form data for re-parsing
                            st.session_state['execution_result'] = execution_result
                            st.session_state['standardized_input'] = standardized_input
                            st.session_state['is_light_scraping'] = form_data.get('use_light_scraping', False)
                            
                            # Get successful sources for light scraping mode
                            successful_sources = [sr for sr in execution_result.source_results if sr.success]
                            
                            # Store info about available sources for re-parsing UI
                            st.session_state['available_sources'] = successful_sources
                            
                            # Convert standardized input to parser format (used in all parsing attempts)
                            parser_requirements = {
                                'data_description': standardized_input.data_description,
                                'data_source': ', '.join(standardized_input.data_sources) if standardized_input.data_sources else '',
                                'desired_fields': '\n'.join(standardized_input.desired_fields),
                                'response_structure': json.dumps(standardized_input.response_structure) if standardized_input.response_structure else '',
                                'update_frequency': standardized_input.update_frequency
                            }
                            
                            parsed_response = None
                            
                            # For light scraping: try sources one by one until we get records
                            if form_data.get('use_light_scraping', False) and len(successful_sources) > 1:
                                from scraping_layer.dynamic_execution.models import ExecutionResult as ExecResult
                                
                                for source_idx, source in enumerate(successful_sources):
                                    source_url = source.source_url
                                    data_for_parsing = [
                                        record for record in execution_result.data
                                        if record.get('_source_url') == source_url
                                    ]
                                    
                                    if not data_for_parsing:
                                        continue
                                    
                                    console_logger.info(
                                        f"Light scraping: Trying source {source_idx + 1}/{len(successful_sources)} "
                                        f"({len(data_for_parsing)} records)"
                                    )
                                    
                                    if source_idx == 0:
                                        st.info(f"💡 Light scraping: Parsing data from top source ({source_url})")
                                    else:
                                        st.info(f"💡 Previous source returned 0 records. Trying source {source_idx + 1}: {source_url}")
                                    
                                    # Parse with spinner
                                    with st.spinner(f"🤖 AI is parsing data from source {source_idx + 1}..."):
                                        try:
                                            console_logger.log_parsing_start(len(data_for_parsing))
                                            
                                            # Create filtered result for this source
                                            filtered_source_results = [sr for sr in execution_result.source_results 
                                                                      if sr.success and sr.source_url == source_url]
                                            
                                            parsing_result = ExecResult(
                                                success=execution_result.success,
                                                data=data_for_parsing,
                                                metadata=execution_result.metadata,
                                                errors=execution_result.errors,
                                                source_results=filtered_source_results,
                                                execution_time_ms=execution_result.execution_time_ms,
                                                scraped_at=execution_result.scraped_at
                                            )
                                            
                                            parsed_response = data_parser.parse_scraped_data(
                                                scraping_result=parsing_result,
                                                user_requirements=parser_requirements
                                            )
                                            
                                            console_logger.log_parsing_complete(parsed_response.metadata)
                                            
                                            # Check if we got any records
                                            records_count = parsed_response.metadata.records_parsed
                                            if records_count > 0:
                                                # Success! Store current source and break
                                                st.session_state['current_parsing_sources'] = [source_url]
                                                st.success(f"✅ Successfully parsed {records_count} records from source {source_idx + 1}")
                                                break  # Exit loop with valid parsed_response
                                            else:
                                                # No records, try next source
                                                console_logger.warning(f"Source {source_idx + 1} returned 0 records, trying next source...")
                                                if source_idx < len(successful_sources) - 1:
                                                    st.warning(f"⚠️ Source {source_idx + 1} returned 0 records. Trying next source...")
                                                    parsed_response = None  # Reset for next attempt
                                                else:
                                                    # Last source also returned 0 - keep the response but warn user
                                                    st.warning(f"⚠️ All sources returned 0 records. You can try re-parsing with multiple sources.")
                                                    # Keep parsed_response so user can still see the structure
                                            
                                        except (EmptyDataError, ParsingError) as e:
                                            console_logger.log_workflow_error(f"Data Parsing (Source {source_idx + 1})", e)
                                            if source_idx < len(successful_sources) - 1:
                                                st.warning(f"⚠️ Source {source_idx + 1} failed. Trying next source...")
                                                parsed_response = None
                                            else:
                                                render_error(e)
                                        except Exception as e:
                                            console_logger.log_workflow_error(f"Data Parsing (Source {source_idx + 1})", e)
                                            if source_idx < len(successful_sources) - 1:
                                                st.warning(f"⚠️ Source {source_idx + 1} error: {str(e)}. Trying next source...")
                                                parsed_response = None
                                            else:
                                                st.error(f"❌ Data parsing failed: {str(e)}")
                                
                                # If we still don't have a response, set current sources to first one for re-parsing UI
                                if not parsed_response:
                                    st.session_state['current_parsing_sources'] = [successful_sources[0].source_url]
                            
                            else:
                                # Traditional scraping or single source - parse all data
                                data_for_parsing = execution_result.data
                                st.session_state['current_parsing_sources'] = [sr.source_url for sr in successful_sources]
                                
                                with st.spinner("🤖 AI is parsing scraped data into structured JSON..."):
                                    try:
                                        console_logger.log_parsing_start(len(data_for_parsing))
                                        
                                        from scraping_layer.dynamic_execution.models import ExecutionResult as ExecResult
                                        parsing_result = execution_result
                                        
                                        parsed_response = data_parser.parse_scraped_data(
                                            scraping_result=parsing_result,
                                            user_requirements=parser_requirements
                                        )
                                        
                                        console_logger.log_parsing_complete(parsed_response.metadata)
                                        
                                    except (EmptyDataError, ParsingError) as e:
                                        console_logger.log_workflow_error("Data Parsing", e)
                                        render_error(e)
                                        parsed_response = None
                                    except Exception as e:
                                        console_logger.log_workflow_error("Data Parsing", e)
                                        st.error(f"❌ Data parsing failed: {str(e)}")
                                        parsed_response = None
                            
                            # Render results OUTSIDE the spinner context
                            if parsed_response:
                                render_parsed_response(parsed_response)
                                
                                # Store parsed_response in session state for API endpoint creation
                                st.session_state['last_parsed_response'] = parsed_response
                                st.session_state['last_form_data'] = form_data
                                st.session_state['show_create_endpoint'] = True
                                st.session_state['show_reparse_option'] = True
                    elif execution_result:
                        console_logger.error("Scraping failed for all URLs")
                        st.error(f"❌ Scraping failed for all URLs")
                        
                        # Show errors in expander
                        if execution_result.errors:
                            with st.expander("🔍 Error Details"):
                                for error in execution_result.errors:
                                    st.error(error)
                    
                except Exception as e:
                        console_logger.log_workflow_error("Script Execution", e)
                        st.error(f"❌ Script execution failed: {str(e)}")

# ============================================================================
# RE-PARSING SECTION (For light scraping - allows user to select different sources)
# ============================================================================
if (st.session_state.get('show_reparse_option') and 
    st.session_state.get('is_light_scraping') and 
    st.session_state.get('available_sources') and 
    len(st.session_state.get('available_sources', [])) > 1):
    
    available_sources = st.session_state['available_sources']
    current_sources = st.session_state.get('current_parsing_sources', [])
    
    st.markdown("---")
    
    # More presentable UI with better styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); 
                padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
        <h4 style="color: #fff; margin: 0 0 0.5rem 0;">🔄 Try Different Data Sources</h4>
        <p style="color: #b8d4e8; margin: 0; font-size: 0.9rem;">
            Not satisfied? Select different source(s) below and re-parse.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Select data source(s) to parse:**")
    
    # Create checkboxes WITHOUT form to avoid full page blur
    # Read checkbox states directly from session state
    selected_sources_for_reparse = []
    for idx, sr in enumerate(available_sources):
        from urllib.parse import urlparse
        domain = urlparse(sr.source_url).netloc.replace('www.', '')
        
        col1, col2, col3 = st.columns([0.5, 3, 1])
        with col1:
            # Default to current sources on first render
            default_val = sr.source_url in current_sources
            checked = st.checkbox(
                f"Select {domain}", 
                value=default_val,
                key=f"reparse_cb_{idx}",
                label_visibility="collapsed"
            )
            if checked:
                selected_sources_for_reparse.append(sr.source_url)
        with col2:
            st.markdown(f"**{domain}**")
            st.caption(sr.source_url)
        with col3:
            st.markdown(f"<span style='background:#3d5a80; padding:2px 8px; border-radius:4px; font-size:0.8rem;'>{sr.record_count} records</span>", unsafe_allow_html=True)
    
    st.markdown("")  # Spacer
    st.caption("💡 Tip: Selecting multiple sources increases parsing time")
    
    # Re-parse button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        reparse_clicked = st.button("🔄 Re-parse Selected", type="primary", use_container_width=True, key="reparse_btn")
    
    # Create a placeholder for the loading indicator and results
    reparse_status_placeholder = st.empty()
    reparse_results_placeholder = st.empty()
    
    # Handle button click
    if reparse_clicked:
        selected_sources = selected_sources_for_reparse
        
        if not selected_sources:
            reparse_status_placeholder.error("Please select at least one data source")
        else:
            # Get stored data
            execution_result = st.session_state.get('execution_result')
            standardized_input = st.session_state.get('standardized_input')
            
            if execution_result and standardized_input and data_parser:
                # Filter data for selected sources
                selected_source_urls = set(selected_sources)
                data_for_parsing = [
                    record for record in execution_result.data
                    if record.get('_source_url') in selected_source_urls
                ]
                
                console_logger.info(
                    f"Re-parsing with {len(selected_sources)} source(s): {len(data_for_parsing)} records"
                )
                
                # Update current parsing sources
                st.session_state['current_parsing_sources'] = selected_sources
                
                # Show loading indicator
                reparse_status_placeholder.info(f"🔄 Re-parsing data from {len(selected_sources)} source(s)...")
                
                try:
                    console_logger.log_parsing_start(len(data_for_parsing))
                    
                    parser_requirements = {
                        'data_description': standardized_input.data_description,
                        'data_source': ', '.join(standardized_input.data_sources) if standardized_input.data_sources else '',
                        'desired_fields': '\n'.join(standardized_input.desired_fields),
                        'response_structure': json.dumps(standardized_input.response_structure) if standardized_input.response_structure else '',
                        'update_frequency': standardized_input.update_frequency
                    }
                    
                    # Create filtered result
                    from scraping_layer.dynamic_execution.models import ExecutionResult as ExecResult
                    filtered_source_results = [sr for sr in execution_result.source_results 
                                              if sr.success and sr.source_url in selected_source_urls]
                    
                    parsing_result = ExecResult(
                        success=execution_result.success,
                        data=data_for_parsing,
                        metadata=execution_result.metadata,
                        errors=execution_result.errors,
                        source_results=filtered_source_results,
                        execution_time_ms=execution_result.execution_time_ms,
                        scraped_at=execution_result.scraped_at
                    )
                    
                    # Call AI parser
                    parsed_response = data_parser.parse_scraped_data(
                        scraping_result=parsing_result,
                        user_requirements=parser_requirements
                    )
                    
                    console_logger.log_parsing_complete(parsed_response.metadata)
                    
                    # Update session state with new results
                    st.session_state['last_parsed_response'] = parsed_response
                    st.session_state['show_create_endpoint'] = True
                    st.session_state['reparse_completed'] = True
                    
                    # Show success message
                    reparse_status_placeholder.success(f"✅ Re-parsing complete! Parsed {parsed_response.metadata.records_parsed} records from {len(selected_sources)} source(s)")
                    
                    # Render the parsed response in the results placeholder
                    with reparse_results_placeholder.container():
                        render_parsed_response(parsed_response)
                    
                except (EmptyDataError, ParsingError) as e:
                    console_logger.log_workflow_error("Re-parsing", e)
                    reparse_status_placeholder.empty()
                    render_error(e)
                except Exception as e:
                    console_logger.log_workflow_error("Re-parsing", e)
                    reparse_status_placeholder.error(f"❌ Re-parsing failed: {str(e)}")

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
            with st.spinner("Creating endpoint..."):
                try:
                    parsed_response = st.session_state['last_parsed_response']
                    
                    # PHASE 4: Create API Endpoint (logging handled by endpoint_manager)
                    endpoint_info = endpoint_manager.create_endpoint(
                        parsed_response=parsed_response,
                        description=endpoint_desc
                    )
                    
                    # Log workflow completion
                    console_logger.log_workflow_complete()
                    
                    st.success(f"✅ API Endpoint Created Successfully!")
                    st.code(endpoint_info.access_url, language="text")
                    st.info(f"📊 {endpoint_info.records_count} records available at this endpoint")
                    
                    # Clear the create endpoint flag and trigger rerun to refresh sidebar
                    st.session_state['show_create_endpoint'] = False
                    st.rerun()
                    
                except EndpointCreationError as e:
                    console_logger.log_workflow_error("Endpoint Creation", e)
                    st.error(f"❌ Failed to create endpoint: {str(e)}")
                except Exception as e:
                    console_logger.log_workflow_error("Endpoint Creation", e)
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("⚠️ API Server not available. Cannot create endpoints.")
        console_logger.warning("API Server not available - cannot create endpoints")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>Built for Hackathon 2025 | Powered by AI</p>
    <p style="font-size: 0.9rem;">🔒 All generated APIs include authentication, rate limiting, and comprehensive documentation</p>
</div>
""", unsafe_allow_html=True)