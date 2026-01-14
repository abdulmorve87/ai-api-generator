import streamlit as st
import time
import requests
import os
from utils.ui_components import render_header, render_success_box, render_endpoint_box
from utils.styles import load_custom_css
from components.form import render_api_form
from components.results import render_results_tabs, render_download_section
from data.mock_data import generate_response, load_mock_response
from ai_integration import ai_integration

# Configuration
API_SERVER_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="AI API Generator",
    page_icon="🚀",
    layout="wide"
)

# Load custom CSS
load_custom_css()

def check_api_server():
    """Check if API server is running"""
    try:
        response = requests.get(f"{API_SERVER_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

# Render header
render_header()

# Check API server status
server_status = check_api_server()
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
                                api_data = requests.get(f"{API_SERVER_URL}{api['endpoint']}")
                                if api_data.status_code == 200:
                                    st.json(api_data.json())
    except Exception as e:
        st.error(f"Error loading APIs: {e}")

# Render main form and get submission status
form_data = render_api_form()

# Handle form submission
if form_data['submitted']:
    if not form_data['data_description']:
        st.error("⚠️ Please provide a data description to continue")
    else:
        # Show loading state with progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔧 Initializing AI layer...")
            progress_bar.progress(10)
            
            status_text.text("🤖 Sending request to DeepSeek AI...")
            progress_bar.progress(30)
            
            # Generate response using AI Layer (DeepSeek)
            ai_generated_data = generate_response(form_data)
            
            progress_bar.progress(90)
            status_text.text("✅ Processing response...")
            progress_bar.progress(100)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Error: {str(e)}")
            st.stop()
            
            # Check if AI generation was successful
            if ai_generated_data.get("status") == "error":
                st.error(f"❌ AI Generation Error: {ai_generated_data.get('message', 'Unknown error')}")
                if ai_generated_data.get('raw'):
                    st.code(ai_generated_data.get('raw', 'No raw output'), language="text")
            else:
                # Extract data from AI response
                response_data = ai_generated_data.get("response", {})
                data_items = response_data.get("data", [])
                
                # If data is a dict, convert to list
                if isinstance(data_items, dict):
                    data_items = [data_items]
                
                # Generate API name from description
                api_name = form_data.get('data_description', 'data').lower()
                api_name = ''.join(c if c.isalnum() else '_' for c in api_name)[:50]
                
                # Infer schema from data
                schema = {"type": "object", "properties": {}}
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
                    schema["properties"] = schema_properties
                
                # Send to API server if it's running
                if server_status:
                    try:
                        api_payload = {
                            "api_name": api_name,
                            "description": form_data.get('data_description', 'AI Generated API'),
                            "data": data_items,
                            "schema": schema,
                            "data_source": "DeepSeek AI",
                            "update_frequency": form_data.get('update_frequency', 'on-demand')
                        }
                        
                        result = ai_integration.receive_ai_data(api_payload)
                        
                        if result["status"] == "success":
                            st.success(f"✅ API created successfully!")
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
                st.info(f"🤖 **Generated by**: DeepSeek AI | **Stored in**: API Server Database")
                
                # Render results tabs
                render_results_tabs(ai_generated_data, form_data)
                
                # Render download section
                render_download_section(ai_generated_data)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>Built for Hackathon 2025 | Powered by DeepSeek AI</p>
    <p style="font-size: 0.9rem;">🔒 All generated APIs include authentication, rate limiting, and comprehensive documentation</p>
</div>
""", unsafe_allow_html=True)
