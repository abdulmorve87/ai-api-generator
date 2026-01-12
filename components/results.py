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