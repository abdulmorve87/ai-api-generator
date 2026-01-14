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
        st.download_button("README.md", readme, "README.md")
