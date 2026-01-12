import streamlit as st
import time
from utils.ui_components import render_header, render_success_box, render_endpoint_box
from utils.styles import load_custom_css
from components.form import render_api_form
from components.results import render_results_tabs, render_download_section
from data.mock_data import load_mock_response

# Page configuration
st.set_page_config(
    page_title="AI API Generator",
    page_icon="🚀",
    layout="wide"
)

# Load custom CSS
load_custom_css()

# Render header
render_header()

# Render main form and get submission status
form_data = render_api_form()

# Handle form submission
if form_data['submitted']:
    if not form_data['data_description']:
        st.error("⚠️ Please provide a data description to continue")
    else:
        # Show loading state
        with st.spinner("🤖 AI is analyzing your requirements and generating the API..."):
            time.sleep(2)  # Simulate API call
            mock_data = load_mock_response()
        
        # Render success message
        render_success_box()
        
        # Display endpoint
        st.subheader("🔗 Your API Endpoint")
        render_endpoint_box(mock_data["endpoint"])
        
        # Render results tabs
        render_results_tabs(mock_data, form_data)
        
        # Render download section
        render_download_section(mock_data)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>Built for Hackathon 2025 | Powered by AI</p>
    <p style="font-size: 0.9rem;">🔒 All generated APIs include authentication, rate limiting, and comprehensive documentation</p>
</div>
""", unsafe_allow_html=True)