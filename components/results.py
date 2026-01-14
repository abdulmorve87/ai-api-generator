import streamlit as st
from utils.code_examples import get_javascript_example, generate_openapi_spec, generate_postman_collection, generate_readme

def render_results_tabs(mock_data, form_data):
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Response Structure", "💻 Code Examples", "⚙️ Configuration", "📚 Documentation"]
    )

    with tab1:
        render_response_structure_tab(mock_data)

    with tab2:
        render_code_examples_tab(mock_data)

    with tab3:
        render_configuration_tab(mock_data, form_data)

    with tab4:
        render_documentation_tab(mock_data)

def render_response_structure_tab(mock_data):
    st.subheader("Expected Response Structure")

    # New AI format
    if "response" in mock_data:
        st.json(mock_data["response"])
    else:
        st.json(mock_data)

    st.subheader("Endpoint")
    st.code(mock_data.get("endpoint", "N/A"))

def render_code_examples_tab(mock_data):
    endpoint = mock_data.get("endpoint", "https://api.example.com")

    st.subheader("cURL Example")
    st.code(f"""curl -X {mock_data.get("method","GET")} "{endpoint}" \\
  -H "Content-Type: application/json"
""", language="bash")

    st.subheader("Python Example")
    st.code(f"""
import requests

url = "{endpoint}"
r = requests.get(url)
print(r.json())
""", language="python")

    st.subheader("JavaScript Example")
    st.code(get_javascript_example(), language="javascript")

def render_configuration_tab(mock_data, form_data):
    st.subheader("API Configuration")

    st.metric("Method", mock_data.get("method", "GET"))
    st.metric("Update Frequency", form_data.get("update_frequency", "N/A"))
    st.metric("Rate Limit", mock_data.get("rate_limit", "Not specified"))

def render_documentation_tab(mock_data):
    st.subheader("Authentication")
    st.markdown("""
This API may require authentication using an API key.

Include your API key in the request header:

""")

    st.subheader("Rate Limiting")
    st.markdown(f"""
- **Limit**: {mock_data.get("rate_limit","Not specified")}
- **Overage**: Returns 429 Too Many Requests
""")

    st.subheader("Error Codes")
    error_codes = {
        "200": "Success",
        "400": "Bad Request",
        "401": "Unauthorized",
        "429": "Too Many Requests",
        "500": "Internal Server Error"
    }
    for code, description in error_codes.items():
        st.markdown(f"**{code}**: {description}")

def render_download_section(mock_data):
    st.subheader("📥 Download Documentation")
    col1, col2, col3 = st.columns(3)

    with col1:
        openapi_spec = generate_openapi_spec(mock_data)
        st.download_button("OpenAPI Spec", openapi_spec, "api_spec.json")

    with col2:
        postman_collection = generate_postman_collection(mock_data)
        st.download_button("Postman Collection", postman_collection, "postman_collection.json")

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
