
import streamlit as st

def render_header():
    """Render the application header"""
    st.markdown('<div class="main-header">🚀 AI-Powered API Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Describe your data needs, get a production-ready API endpoint</div>', unsafe_allow_html=True)

def render_success_box():
    """Render success message box"""
    st.markdown('<div class="success-box"><h3>✅ API Endpoint Successfully Generated!</h3></div>', unsafe_allow_html=True)

def render_endpoint_box(endpoint):
    """Render endpoint display box"""
    st.markdown(f'<div class="endpoint-box"><code style="font-size: 1.1rem;">{endpoint}</code></div>', unsafe_allow_html=True)
