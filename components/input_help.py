"""
Input format help component for the UI.

Provides quick reference guides and examples for user inputs.
"""

import streamlit as st


def render_input_format_guide():
    """Render a comprehensive input format guide in the sidebar"""
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📖 Input Format Guide")
    
    with st.sidebar.expander("🔗 URL Formats"):
        st.markdown("""
**Single URL:**
```
https://example.com/data
```

**Multiple URLs:**
```
https://site1.com
https://site2.com
```
or
```
https://site1.com, https://site2.com
```

**Rules:**
- Must start with `http://` or `https://`
- No spaces in URLs
- Leave blank for AI to find sources
        """)
    
    with st.sidebar.expander("📝 Field Formats"):
        st.markdown("""
**One per line (recommended):**
```
company_name
listing_date
issue_price
```

**Comma-separated:**
```
name, date, price
```

**Rules:**
- Start with letter or underscore
- Use letters, numbers, `_`, `-` only
- No spaces or special characters
        """)
    
    with st.sidebar.expander("📋 JSON Format"):
        st.markdown("""
**Example structure:**
```json
{
  "data": [
    {
      "field1": "string",
      "field2": "number"
    }
  ]
}
```

**Rules:**
- Must be valid JSON
- Must be object `{}`, not array `[]`
- Use double quotes
- Check commas and brackets
        """)
    
    with st.sidebar.expander("✅ Validation Tips"):
        st.markdown("""
**Common Mistakes:**
- ❌ `www.site.com` → ✅ `https://www.site.com`
- ❌ `123field` → ✅ `field_123`
- ❌ `field name` → ✅ `field_name`
- ❌ `{'key': 'value'}` → ✅ `{"key": "value"}`

**Best Practices:**
- Test URLs before submitting
- Use snake_case for fields
- Validate JSON at jsonlint.com
- One field per line for clarity
        """)


def render_inline_help(field_type: str):
    """
    Render inline help for a specific field type.
    
    Args:
        field_type: One of 'url', 'fields', 'json'
    """
    
    if field_type == 'url':
        st.info("""
**URL Format Examples:**
- Single: `https://example.com/data`
- Multiple: `https://site1.com, https://site2.com`
- Or one per line
        """)
    
    elif field_type == 'fields':
        st.info("""
**Field Format Examples:**
- One per line: `company_name`, `listing_date`, `price`
- Or comma-separated: `name, date, price`
- Must start with letter/underscore
        """)
    
    elif field_type == 'json':
        st.info("""
**JSON Format Example:**
```json
{
  "data": [
    {"field1": "string", "field2": "number"}
  ]
}
```
Must be valid JSON object (not array).
        """)


def show_validation_summary(standardized_input):
    """
    Show a summary of validated inputs.
    
    Args:
        standardized_input: StandardizedInput object
    """
    
    st.success("✅ All inputs validated successfully!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        url_count = len(standardized_input.data_sources)
        st.metric("URLs", url_count if url_count > 0 else "AI will find")
    
    with col2:
        field_count = len(standardized_input.desired_fields)
        st.metric("Fields", field_count if field_count > 0 else "Auto-detect")
    
    with col3:
        has_structure = bool(standardized_input.response_structure)
        st.metric("JSON Structure", "✓ Custom" if has_structure else "Default")
    
    # Show details in expander
    with st.expander("📋 View Validated Inputs"):
        if standardized_input.data_sources:
            st.markdown("**URLs:**")
            for i, url in enumerate(standardized_input.data_sources, 1):
                st.write(f"{i}. {url}")
        
        if standardized_input.desired_fields:
            st.markdown("**Fields:**")
            st.write(", ".join(standardized_input.desired_fields))
        
        if standardized_input.response_structure:
            st.markdown("**JSON Structure:**")
            import json
            st.code(json.dumps(standardized_input.response_structure, indent=2), language="json")
