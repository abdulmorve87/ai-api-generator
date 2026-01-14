import  streamlit as st
import json
from utils.code_examples import get_javascript_example, generate_openapi_spec, generate_postman_collection, generate_readme

def render_results_tabs(mock_data, form_data):
    """Render the results tabs with API information"""
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Response Structure", "💻 Code Examples", "⚙️ Configuration", "📚 Documentation"])
    
    with tab1:
        render_response_structure_tab(mock_data)
    
    with tab2:
        render_code_examples_tab(mock_data)
    
    with tab3:
        render_configuration_tab(mock_data, form_data)
    
    with tab4:
        render_documentation_tab(mock_data)

def render_response_structure_tab(mock_data):
    """Render response structure tab"""
    st.subheader("Expected Response Structure")
    st.json(mock_data["response_structure"])
    
    st.subheader("Query Parameters")
    for param, description in mock_data["query_parameters"].items():
        st.markdown(f"**`{param}`**: {description}")

def render_code_examples_tab(mock_data):
    """Render code examples tab"""
    st.subheader("cURL Example")
    st.code(mock_data["example_curl"], language="bash")
    
    st.subheader("Python Example")
    st.code(mock_data["python_example"], language="python")
    
    st.subheader("JavaScript Example")
    st.code(get_javascript_example(), language="javascript")

def render_configuration_tab(mock_data, form_data):
    """Render configuration tab"""
    st.subheader("API Configuration")
    
    st.metric("Method", mock_data["method"])
    st.metric("Rate Limit", mock_data["rate_limit"])
    st.metric("Update Frequency", form_data['update_frequency'])

def render_documentation_tab(mock_data):
    """Render documentation tab"""
    st.subheader("Authentication")
    st.markdown(f"""
    {mock_data["authentication"]}
    
    Include your API key in the request header:
    ```
    X-API-Key: your_api_key_here
    ```
    """)
    
    st.subheader("Rate Limiting")
    st.markdown(f"""
    - **Limit**: {mock_data["rate_limit"]}
    - **Overage**: Returns 429 Too Many Requests
    - **Headers**: `X-RateLimit-Remaining` and `X-RateLimit-Reset` included in response
    """)
    
    st.subheader("Error Codes")
    error_codes = {
        "200": "Success",
        "400": "Bad Request - Invalid parameters",
        "401": "Unauthorized - Invalid API key",
        "429": "Too Many Requests - Rate limit exceeded",
        "500": "Internal Server Error"
    }
    for code, description in error_codes.items():
        st.markdown(f"**{code}**: {description}")

def render_download_section(mock_data):
    """Render download documentation section"""
    st.subheader("📥 Download Documentation")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        openapi_spec = generate_openapi_spec(mock_data)
        st.download_button(
            label="OpenAPI Spec",
            data=openapi_spec,
            file_name="api_spec.json",
            mime="application/json"
        )
    
    with col2:
        postman_collection = generate_postman_collection(mock_data)
        st.download_button(
            label="Postman Collection",
            data=postman_collection,
            file_name="postman_collection.json",
            mime="application/json"
        )
    
    with col3:
        readme = generate_readme(mock_data)
        st.download_button(
            label="README.md",
            data=readme,
            file_name="README.md",
            mime="text/markdown"
        )


# AI Response Generator UI Components

def render_generated_response(response):
    """
    Display the AI-generated JSON response with formatting and actions.
    
    Args:
        response: GeneratedResponse object from ai_layer
    """
    st.success("✅ API Response Generated Successfully!")
    
    # Display the generated JSON
    st.subheader("Generated JSON Response")
    st.json(response.data)
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        # Copy to clipboard button (using st.code for easy copying)
        st.download_button(
            label="📋 Copy JSON",
            data=json.dumps(response.data, indent=2),
            file_name="api_response.json",
            mime="application/json",
            help="Download the generated JSON response"
        )
    
    with col2:
        # Download button
        st.download_button(
            label="💾 Download JSON",
            data=response.to_json(),
            file_name="generated_api_response.json",
            mime="application/json",
            help="Download the complete response with metadata"
        )
    
    # Display metadata in an expander
    with st.expander("📊 Generation Metadata"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Model", response.metadata.model)
        
        with col2:
            st.metric("Tokens Used", response.metadata.tokens_used)
        
        with col3:
            st.metric("Generation Time", f"{response.metadata.generation_time_ms}ms")
        
        with col4:
            st.metric("Timestamp", response.metadata.timestamp.strftime("%H:%M:%S"))
        
        # Show raw output for debugging
        if st.checkbox("Show raw AI output"):
            st.code(response.raw_output, language="json")


def render_generated_script(generated_script):
    """
    Display the AI-generated scraper script with formatting and actions.
    
    Args:
        generated_script: GeneratedScript object from ai_layer
    """
    # Show validation status
    if generated_script.is_valid:
        st.success("✅ Scraper Script Generated Successfully!")
    else:
        st.warning("⚠️ Script Generated with Validation Warnings")
    
    # Display validation results
    with st.expander("🔍 Validation Results", expanded=not generated_script.is_valid):
        col1, col2, col3, col4 = st.columns(4)
        
        result = generated_script.validation_result
        
        with col1:
            status = "✅" if result.syntax_valid else "❌"
            st.metric("Syntax", status)
        
        with col2:
            status = "✅" if result.imports_valid else "❌"
            st.metric("Imports", status)
        
        with col3:
            status = "✅" if result.no_forbidden_ops else "❌"
            st.metric("Safety", status)
        
        with col4:
            status = "✅" if result.function_signature_valid else "❌"
            st.metric("Signature", status)
        
        if result.errors:
            st.error("**Validation Errors:**")
            for error in result.errors:
                st.markdown(f"- {error}")
        
        if result.warnings:
            st.warning("**Warnings:**")
            for warning in result.warnings:
                st.markdown(f"- {warning}")
    
    # Display the generated script
    st.subheader("Generated Scraper Script")
    st.code(generated_script.script_code, language="python")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="💾 Download Script",
            data=generated_script.script_code,
            file_name="scraper_script.py",
            mime="text/x-python",
            help="Download the generated Python script"
        )
    
    with col2:
        st.download_button(
            label="📋 Download with Metadata",
            data=generated_script.to_json(),
            file_name="script_with_metadata.json",
            mime="application/json",
            help="Download script with generation metadata"
        )
    
    with col3:
        if st.button("📖 View Usage Instructions"):
            st.session_state.show_script_instructions = True
    
    # Usage instructions
    if st.session_state.get('show_script_instructions', False):
        with st.expander("📖 How to Use This Script", expanded=True):
            st.markdown(f"""
            ### Running the Script
            
            1. **Save the script** to a file (e.g., `scraper.py`)
            
            2. **Install dependencies:**
            ```bash
            pip install requests beautifulsoup4 lxml
            ```
            
            3. **Run the script:**
            ```python
            python scraper.py
            ```
            
            4. **Or import and use in your code:**
            ```python
            from scraper import scrape_data
            
            result = scrape_data("{generated_script.metadata.target_url}")
            print(result)
            ```
            
            ### Expected Output Format
            
            The script returns a dictionary with:
            - `data`: List of extracted records
            - `metadata`: Information about the scraping operation
            
            ### Troubleshooting
            
            - **No data returned**: Check if the website structure has changed
            - **Network errors**: Verify the URL is accessible
            - **Parsing errors**: The CSS selectors may need adjustment
            
            ### Next Steps
            
            1. Test the script with the target URL
            2. Adjust CSS selectors if needed
            3. Integrate with your application
            4. Set up scheduled execution if needed
            """)
    
    # Display metadata
    with st.expander("📊 Generation Metadata"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Model", generated_script.metadata.model)
            st.metric("Target URL", generated_script.metadata.target_url)
        
        with col2:
            st.metric("Tokens Used", generated_script.metadata.tokens_used)
            st.metric("Generation Time", f"{generated_script.metadata.generation_time_ms}ms")
        
        with col3:
            st.metric("Timestamp", generated_script.metadata.timestamp.strftime("%H:%M:%S"))
            if generated_script.metadata.required_fields:
                st.metric("Required Fields", len(generated_script.metadata.required_fields))
        
        if generated_script.metadata.required_fields:
            st.markdown("**Required Fields:**")
            st.markdown(", ".join(generated_script.metadata.required_fields))
        
        # Show raw output for debugging
        if st.checkbox("Show raw AI output", key="script_raw_output"):
            st.code(generated_script.raw_output, language="text")


def render_error(error):
    """
    Display error messages with appropriate styling and troubleshooting hints.
    
    Args:
        error: Exception that occurred during generation
    """
    from ai_layer.exceptions import (
        ConfigurationError,
        DeepSeekAuthError,
        DeepSeekRateLimitError,
        DeepSeekConnectionError,
        ValidationError,
        GenerationError,
        DeepSeekAPIError
    )
    from ai_layer.script_models import (
        ScriptValidationError,
        ScriptGenerationError
    )
    
    # Determine error type and customize message
    if isinstance(error, ConfigurationError):
        st.error("⚙️ Configuration Error")
        st.markdown(f"""
        **Error:** {str(error)}
        
        **How to fix:**
        1. Create a `.env` file in your project root
        2. Add your DeepSeek API key: `DEEPSEEK_API_KEY=your_key_here`
        3. Get your API key from [DeepSeek Platform](https://platform.deepseek.com)
        4. Restart the application
        """)
    
    elif isinstance(error, DeepSeekAuthError):
        st.error("🔐 Authentication Error")
        st.markdown(f"""
        **Error:** {str(error)}
        
        **How to fix:**
        1. Verify your API key is correct in the `.env` file
        2. Check that the key hasn't expired
        3. Get a new key from [DeepSeek Platform](https://platform.deepseek.com) if needed
        """)
    
    elif isinstance(error, DeepSeekRateLimitError):
        st.error("⏱️ Rate Limit Exceeded")
        retry_after = getattr(error, 'retry_after', 60)
        st.markdown(f"""
        **Error:** {str(error)}
        
        **How to fix:**
        - Wait {retry_after} seconds before trying again
        - Consider upgrading your API plan for higher limits
        - Reduce the frequency of requests
        """)
    
    elif isinstance(error, DeepSeekConnectionError):
        st.error("🌐 Connection Error")
        st.markdown(f"""
        **Error:** {str(error)}
        
        **How to fix:**
        1. Check your internet connection
        2. Verify you can access https://api.deepseek.com
        3. Check if a firewall is blocking the connection
        4. Try again in a few moments
        """)
    
    elif isinstance(error, ValidationError):
        st.error("❌ Validation Error")
        field = getattr(error, 'field', None)
        if field:
            st.markdown(f"""
            **Field:** `{field}`
            
            **Error:** {str(error)}
            
            **How to fix:**
            - Check that all required fields are filled
            - Ensure JSON structure is valid (if provided)
            - Verify field names are on separate lines
            """)
        else:
            st.markdown(f"""
            **Error:** {str(error)}
            
            **How to fix:**
            - Review your input and correct any validation errors
            - Ensure all required fields are provided
            """)
    
    elif isinstance(error, GenerationError):
        st.error("🤖 Generation Error")
        st.markdown(f"""
        **Error:** {str(error)}
        
        **How to fix:**
        - Try simplifying your requirements
        - Provide a clearer structure example
        - Reduce the number of fields requested
        - Try again (AI responses can vary)
        """)
    
    elif isinstance(error, ScriptGenerationError):
        st.error("🤖 Script Generation Error")
        st.markdown(f"""
        **Error:** {str(error)}
        
        **How to fix:**
        - Ensure the target URL is provided
        - Try simplifying your requirements
        - Provide a clearer data description
        - Verify the URL is accessible
        - Try again (AI responses can vary)
        """)
    
    elif isinstance(error, ScriptValidationError):
        st.error("⚠️ Script Validation Error")
        st.markdown(f"""
        **Error:** {str(error)}
        
        The generated script failed validation checks.
        
        **How to fix:**
        - Try regenerating the script
        - Simplify your requirements
        - Check the validation details below
        """)
        
        if hasattr(error, 'validation_result') and error.validation_result:
            st.markdown("**Validation Details:**")
            result = error.validation_result
            st.markdown(f"- Syntax Valid: {'✅' if result.syntax_valid else '❌'}")
            st.markdown(f"- Imports Valid: {'✅' if result.imports_valid else '❌'}")
            st.markdown(f"- No Forbidden Ops: {'✅' if result.no_forbidden_ops else '❌'}")
            st.markdown(f"- Function Signature Valid: {'✅' if result.function_signature_valid else '❌'}")
            
            if result.errors:
                st.markdown("**Errors:**")
                for err in result.errors:
                    st.markdown(f"- {err}")
    
    elif isinstance(error, DeepSeekAPIError):
        st.error("🔧 API Error")
        st.markdown(f"""
        **Error:** {str(error)}
        
        **How to fix:**
        - The DeepSeek service may be temporarily unavailable
        - Try again in a few moments
        - Check [DeepSeek Status](https://status.deepseek.com) for service updates
        """)
    
    else:
        st.error("❌ Unexpected Error")
        st.markdown(f"""
        **Error:** {str(error)}
        
        **Type:** {type(error).__name__}
        
        **How to fix:**
        - Try again
        - If the problem persists, please report this issue
        """)
    
    # Show detailed error in expander for debugging
    with st.expander("🔍 Technical Details"):
        st.code(f"{type(error).__name__}: {str(error)}")
        if hasattr(error, '__traceback__'):
            import traceback
            st.code(traceback.format_exc())
