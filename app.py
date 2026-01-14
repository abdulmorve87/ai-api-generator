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
    ScraperScriptGenerator,
    ConfigurationError
)
from scraping_layer.config import ScrapingConfig

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
    """Initialize the AI Response Generator and Script Generator with configuration."""
    try:
        deepseek_config = DeepSeekConfig.from_env()
        scraping_config = ScrapingConfig.from_env()
        
        client = DeepSeekClient(deepseek_config.api_key, deepseek_config.base_url)
        
        response_generator = AIResponseGenerator(client)
        script_generator = ScraperScriptGenerator(client, scraping_config)
        
        return response_generator, script_generator, None
    except ConfigurationError as e:
        return None, None, e

ai_generator, script_generator, config_error = initialize_ai_components()

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
                    
                    # BACKGROUND: Generate scraper script and print to console
                    if script_generator:
                        try:
                            print("\n" + "="*80)
                            print("GENERATING SCRAPER SCRIPT IN BACKGROUND...")
                            print("="*80)
                            print(f"Data Description: {form_data['data_description']}")
                            print(f"Data Source: {form_data.get('data_source', 'Not provided - AI will suggest URLs')}")
                            print(f"Desired Fields: {form_data.get('desired_fields', 'N/A')}")
                            print("="*80)
                            
                            # Generate script
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
                            
                        except Exception as script_error:
                            print("\n" + "="*80)
                            print("SCRAPER SCRIPT GENERATION FAILED")
                            print("="*80)
                            print(f"Error: {str(script_error)}")
                            print("="*80 + "\n")
                    
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