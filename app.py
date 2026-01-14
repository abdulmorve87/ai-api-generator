import streamlit as st
import time
import requests
import os
from utils.ui_components import render_header, render_success_box, render_endpoint_box
from utils.styles import load_custom_css
from components.form import render_api_form
from components.results import render_results_tabs, render_download_section
from data.mock_data import generate_response
from ai_integration import ai_integration

# Configuration
API_SERVER_URL = "http://localhost:8000"
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")

def check_api_server():
    """Check if API server is running"""
    try:
        response = requests.get(f"{API_SERVER_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_live_api_data(api_name):
    """Get live data from API server"""
    try:
        response = requests.get(f"{API_SERVER_URL}/api/{api_name}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def format_api_response_for_display(api_data, form_data):
    """Format API response for display in the UI"""
    if not api_data or api_data.get('status') != 'success':
        return load_mock_response()  # Fallback to mock data
    
    # Extract data and metadata
    data = api_data.get('data', [])
    metadata = api_data.get('metadata', {})
    api_info = metadata.get('api_info', {})
    
    # Create display format similar to mock data
    formatted_response = {
        "endpoint": f"{API_SERVER_URL}/api/{api_info.get('name', 'unknown')}",
        "method": "GET",
        "authentication": "API Key required in header: X-API-Key",
        "rate_limit": "100 requests per hour",
        "response_structure": {
            "status": "success",
            "data": data[:2] if len(data) > 2 else data,  # Show first 2 records
            "metadata": {
                "total_results": metadata.get('total_count', len(data)),
                "returned_count": metadata.get('returned_count', len(data)),
                "last_updated": api_info.get('last_updated'),
                "data_source": api_info.get('data_source', 'AI Layer')
            }
        },
        "example_curl": f"""curl -X GET "{API_SERVER_URL}/api/{api_info.get('name', 'unknown')}" \\
  -H "X-API-Key: your_api_key_here" \\
  -H "Content-Type: application/json" """,
        "python_example": f"""import requests

url = "{API_SERVER_URL}/api/{api_info.get('name', 'unknown')}"
headers = {{
    "X-API-Key": "your_api_key_here",
    "Content-Type": "application/json"
}}

response = requests.get(url, headers=headers)
data = response.json()
print(data)""",
        "query_parameters": {
            "limit": "Number of results to return (default: 100)",
            "offset": "Pagination offset (default: 0)",
            "search": "Search term for filtering results"
        }
    }
    
    return formatted_response

# Page configuration
st.set_page_config(
    page_title="AI API Generator",
    page_icon="🚀",
    layout="wide"
)

# Load custom CSS
load_custom_css()

# Check API server status
server_status = check_api_server()

# Render header
render_header()

# Show server status
if server_status:
    st.success("🟢 API Server is running")
else:
    st.warning("🟡 API Server is not running. Start it with: `python api_server.py`")

# Show existing APIs
if server_status:
    try:
        apis_response = requests.get(f"{API_SERVER_URL}/apis")
        if apis_response.status_code == 200:
            apis_data = apis_response.json()
            if apis_data.get('apis'):
                st.subheader("🔗 Available APIs")
                for api in apis_data['apis']:
                    with st.expander(f"📊 {api['name']} - {api['description'][:100]}..."):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Endpoint:** `{API_SERVER_URL}{api['endpoint']}`")
                            st.write(f"**Data Source:** {api['data_source']}")
                            st.write(f"**Update Frequency:** {api['update_frequency']}")
                        with col2:
                            st.write(f"**Created:** {api['created_at']}")
                            st.write(f"**Last Updated:** {api['updated_at']}")
                            if st.button(f"View Data", key=f"view_{api['name']}"):
                                api_data = get_live_api_data(api['name'])
                                if api_data:
                                    st.json(api_data)
    except:
        pass

# Render main form and get submission status
form_data = render_api_form()

# Handle form submission
if form_data['submitted']:
    if not form_data['data_description']:
        st.error("⚠️ Please provide a data description to continue")
    else:
        # Show loading state
        with st.spinner("🤖 AI is analyzing your requirements and generating the API..."):
            # Call colleague's AI layer to generate API response
            ai_generated_data = generate_response(form_data)
            
            # Check if AI generation was successful
            if ai_generated_data.get("status") == "error":
                st.error(f"❌ AI Generation Error: {ai_generated_data.get('message', 'Unknown error')}")
                st.code(ai_generated_data.get('raw', 'No raw output'), language="text")
            else:
                # Extract data from AI response
                endpoint = ai_generated_data.get("endpoint", "https://api.example.com/data")
                api_name = endpoint.split("/")[-1].replace("-", "_")
                
                # Prepare data for API server
                response_data = ai_generated_data.get("response", {})
                data_items = response_data.get("data", [])
                
                # If data is a dict, convert to list
                if isinstance(data_items, dict):
                    data_items = [data_items]
                
                # Infer schema from data
                if data_items and len(data_items) > 0:
                    first_item = data_items[0]
                    schema_properties = {}
                    for key, value in first_item.items():
                        if isinstance(value, int):
                            schema_properties[key] = {"type": "integer", "description": key.replace("_", " ").title()}
                        elif isinstance(value, float):
                            schema_properties[key] = {"type": "number", "description": key.replace("_", " ").title()}
                        elif isinstance(value, bool):
                            schema_properties[key] = {"type": "boolean", "description": key.replace("_", " ").title()}
                        elif isinstance(value, list):
                            schema_properties[key] = {"type": "array", "description": key.replace("_", " ").title()}
                        else:
                            schema_properties[key] = {"type": "string", "description": key.replace("_", " ").title()}
                    
                    schema = {
                        "type": "object",
                        "properties": schema_properties
                    }
                else:
                    schema = {"type": "object", "properties": {}}
                
                # Send to API server if it's running
                if server_status:
                    try:
                        api_payload = {
                            "api_name": api_name,
                            "description": form_data.get('data_description', 'AI Generated API'),
                            "data": data_items,
                            "schema": schema,
                            "data_source": f"AI Generated ({AI_PROVIDER})",
                            "update_frequency": form_data.get('update_frequency', 'on-demand')
                        }
                        
                        result = ai_integration.receive_ai_data(api_payload)
                        
                        if result["status"] == "success":
                            st.success(f"✅ API created successfully: {result.get('api_endpoint', 'unknown')}")
                            # Update endpoint to use the actual API server
                            ai_generated_data["endpoint"] = f"{API_SERVER_URL}{result.get('api_endpoint', '')}"
                        else:
                            st.warning(f"⚠️ Could not store in API server: {result.get('message', 'Unknown error')}")
                    except Exception as e:
                        st.warning(f"⚠️ Could not connect to API server: {e}")
        
        # Render success message
        render_success_box()
        
        # Display endpoint
        st.subheader("🔗 Your API Endpoint")
        render_endpoint_box(ai_generated_data.get("endpoint", "https://api.example.com/data"))
        
        # Show AI provider info
        ai_provider = os.getenv("AI_PROVIDER", "gemini")
        st.info(f"🤖 **Generated by**: {ai_provider.title()} AI | **Stored in**: API Server Database")
        
        # Render results tabs
        render_results_tabs(ai_generated_data, form_data)
        
        # Render download section
        render_download_section(ai_generated_data)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>Built for Hackathon 2025 | Powered by AI</p>
    <p style="font-size: 0.9rem;">🔒 All generated APIs include authentication, rate limiting, and comprehensive documentation</p>
</div>
""", unsafe_allow_html=True)