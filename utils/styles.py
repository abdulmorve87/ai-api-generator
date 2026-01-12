import streamlit as st

def load_custom_css():
    st.markdown("""
        <style>
        .main-header {
            color: #your-color;
        }
        </style>
    """, unsafe_allow_html=True)