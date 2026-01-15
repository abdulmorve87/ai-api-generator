import streamlit as st

def render_api_form():
    """Render the main API generation form with input format examples"""
    with st.form("api_generator_form"):
        st.subheader("📝 Describe Your API Requirements")
        
        # Data Description
        data_description = st.text_area(
            "1. What data do you need? *",
            placeholder="e.g., Current IPOs listed on Indian stock market with their grey market premium history",
            height=100,
            help="Describe the data you want to access through the API"
        )
        
        # Data Source with format examples
        st.markdown("**2. Where is this data available? (Optional)**")
        with st.expander("📖 See URL format examples"):
            st.markdown("""
**Accepted formats:**
- **Single URL:** `https://example.com/data`
- **Multiple URLs (comma-separated):** `https://site1.com, https://site2.com`
- **Multiple URLs (one per line):**
  ```
  https://site1.com
  https://site2.com
  https://site3.com
  ```
- **Leave blank** to let AI find sources automatically

**Requirements:**
- Must start with `http://` or `https://`
- No spaces within URLs
- Each URL on a new line or separated by commas
            """)
        
        data_source = st.text_area(
            "Enter URL(s)",
            placeholder="https://example.com\nor leave blank for AI to find sources",
            height=80,
            help="Provide known data sources or let AI discover them",
            label_visibility="collapsed"
        )
        
        # Desired Fields with format examples
        st.markdown("**3. What fields should the response contain? (Optional)**")
        with st.expander("📖 See field format examples"):
            st.markdown("""
**Accepted formats:**
- **One per line (recommended):**
  ```
  company_name
  listing_date
  issue_price
  grey_market_premium
  ```
- **Comma-separated:** `name, date, price, premium`

**Requirements:**
- Field names must start with a letter or underscore
- Can contain letters, numbers, underscores, and hyphens
- No duplicate field names
- No special characters or spaces
            """)
        
        desired_fields = st.text_area(
            "Enter field names",
            placeholder="company_name\nlisting_date\nissue_price\ngrey_market_premium",
            height=120,
            help="Enter each field on a new line or comma-separated",
            label_visibility="collapsed"
        )
        
        # Response Structure with format examples
        st.markdown("**4. Preferred JSON structure (Optional)**")
        with st.expander("📖 See JSON format examples"):
            st.markdown("""
**Example structure:**
```json
{
  "data": [
    {
      "company_name": "string",
      "listing_date": "date",
      "issue_price": "number",
      "grey_market_premium": "number"
    }
  ],
  "metadata": {
    "total_count": "number",
    "last_updated": "timestamp"
  }
}
```

**Requirements:**
- Must be valid JSON format
- Must be an object `{}`, not an array `[]`
- Use double quotes for keys and string values
- Check for missing commas or brackets
            """)
        
        response_structure = st.text_area(
            "Enter JSON structure",
            placeholder='{\n  "data": [\n    {\n      "company_name": "string",\n      "listing_date": "date"\n    }\n  ]\n}',
            height=150,
            help="Provide an example JSON structure or leave blank for default",
            label_visibility="collapsed"
        )
        
        # Update Frequency
        update_frequency = st.selectbox(
            "5. Update Frequency *",
            ["Real-time", "Hourly", "Daily", "Weekly", "Monthly"],
            index=2,
            help="How often should the data be refreshed?"
        )
        
        st.markdown("---")
        
        # Light Scraping Toggle
        use_light_scraping = st.toggle(
            "🪶 Toggle to use light scraping",
            value=False,
            help="Light scraping fetches raw HTML and uses AI for data extraction. Traditional scraping uses BeautifulSoup for parsing."
        )
        
        st.caption("* Required fields")
        
        # Submit button
        submitted = st.form_submit_button("🎯 Generate API Endpoint", use_container_width=True)
    
    return {
        'submitted': submitted,
        'data_description': data_description,
        'data_source': data_source,
        'desired_fields': desired_fields,
        'response_structure': response_structure,
        'update_frequency': update_frequency,
        'use_light_scraping': use_light_scraping,
    }
