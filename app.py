import streamlit as st
import time
from utils.ui_components import render_header, render_success_box, render_endpoint_box
from utils.styles import load_custom_css
from components.form import render_api_form
from components.results import (
    render_results_tabs, 
    render_download_section,
    render_generated_response,
    render_error
)
from data.mock_data import load_mock_response

# AI Layer imports
from ai_layer import (
    DeepSeekConfig,
    DeepSeekClient,
    AIResponseGenerator,
    ConfigurationError
)

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
def initialize_ai_generator():
    """Initialize the AI Response Generator with configuration."""
    try:
        config = DeepSeekConfig.from_env()
        client = DeepSeekClient(config.api_key, config.base_url)
        generator = AIResponseGenerator(client)
        return generator, None
    except ConfigurationError as e:
        return None, e

ai_generator, config_error = initialize_ai_generator()

# Render header
render_header()

# Render main form and get submission status
form_data = render_api_form()

# Handle form submission
if form_data['submitted']:
    if not form_data['data_description']:
        st.error("⚠️ Please provide a data description to continue")
    else:
        # Check if AI generator is available
        if config_error:
            render_error(config_error)
        elif ai_generator is None:
            st.error("⚠️ AI Generator not initialized. Please check your configuration.")
        else:
            # Show loading state
            with st.spinner("🤖 AI is generating your API response..."):
                try:
                    # Generate response using AI
                    response = ai_generator.generate_response(form_data)
                    
                    # Display the generated response
                    render_generated_response(response)
                    
                    # Optional: Show the old mock data tabs for comparison/additional info
                    with st.expander("📚 View Additional API Documentation"):
                        mock_data = load_mock_response()
                        render_results_tabs(mock_data, form_data)
                        render_download_section(mock_data)
                
                except Exception as e:
                    # Display error with helpful troubleshooting
                    render_error(e)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>Built for Hackathon 2025 | Powered by AI</p>
    <p style="font-size: 0.9rem;">🔒 All generated APIs include authentication, rate limiting, and comprehensive documentation</p>
</div>
""", unsafe_allow_html=True)