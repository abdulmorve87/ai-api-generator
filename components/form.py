import streamlit as st

def render_api_form():
    """Render the main API generation form"""
    with st.form("api_generator_form"):
        st.subheader("📝 Describe Your API Requirements")
        
        # Data Description
        data_description = st.text_area(
            "1. What data do you need?",
            placeholder="e.g., Current IPOs listed on Indian stock market with their grey market premium history",
            height=100,
            help="Describe the data you want to access through the API"
        )
        
        # Data Source
        data_source = st.text_input(
            "2. Where is this data available? (Optional)",
            placeholder="e.g., Chittorgarh.com, Investorgain.com, or leave blank for AI to find sources",
            help="Provide known data sources or let AI discover them"
        )
        
        # Desired Fields
        desired_fields = st.text_area(
            "3. What fields should the response contain?",
            placeholder="company_name\nlisting_date\nissue_price\ngrey_market_premium\ngrey_market_history",
            height=120,
            help="Enter each field on a new line"
        )
        
        # Response Structure
        response_structure = st.text_area(
            "4. Preferred JSON structure (Optional)",
            placeholder='{\n  "data": [\n    {\n      "company_name": "string",\n      "listing_date": "date",\n      "grey_market_premium": "number"\n    }\n  ]\n}',
            height=150,
            help="Provide an example JSON structure or leave blank for default"
        )
        
        # Update Frequency and API Format
        col1, col2 = st.columns([1, 1])
        with col1:
            update_frequency = st.selectbox(
                "5. Update Frequency",
                ["Real-time", "Hourly", "Daily", "Weekly", "Monthly"],
                index=2,
                help="How often should the data be refreshed?"
            )
        
        with col2:
            api_format = st.selectbox(
                "6. API Format",
                ["REST", "GraphQL", "WebSocket"],
                index=0,
                help="Choose your preferred API format"
            )
        
        # Submit button
        submitted = st.form_submit_button("🎯 Generate API Endpoint", use_container_width=True)
    
    return {
        'submitted': submitted,
        'data_description': data_description,
        'data_source': data_source,
        'desired_fields': desired_fields,
        'response_structure': response_structure,
        'update_frequency': update_frequency,
        'api_format': api_format
    }
