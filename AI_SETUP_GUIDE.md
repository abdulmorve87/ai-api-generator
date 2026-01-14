# 🤖 AI Layer Setup Guide

## Overview

Your colleague has integrated an AI layer that uses **Gemini** or **DeepSeek** APIs to dynamically generate API responses based on user descriptions. This guide explains how to set it up and use it.

## 🔑 Step 1: Get API Keys

### Option A: Gemini (Google AI) - Recommended
1. Visit: https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

### Option B: DeepSeek
1. Visit: https://platform.deepseek.com/
2. Sign up for an account
3. Navigate to API Keys section
4. Create and copy your API key

## ⚙️ Step 2: Configure Environment

1. **Create `.env` file** in the project root:
```bash
# Copy the example file
copy .env.example .env
```

2. **Edit `.env` file** with your API keys:
```env
# Choose your AI provider
AI_PROVIDER=gemini

# Add your Gemini API key
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Or add your DeepSeek API key
DEEPSEEK_API_KEY=your_actual_deepseek_api_key_here
```

## 📦 Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `python-dotenv` - Environment variable management
- `google-genai` - Gemini AI SDK

## 🚀 Step 4: Test the Integration

### Test 1: Check AI Layer
```bash
python -c "from data.mock_data import generate_response; print('AI layer working!')"
```

### Test 2: Generate Sample API
```bash
python -c "
from data.mock_data import generate_response
result = generate_response({'data_description': 'cryptocurrency prices', 'desired_fields': 'symbol, price'})
print(result)
"
```

### Test 3: Full System Test
```bash
# Start API server
python api_server.py

# In another terminal, start Streamlit
streamlit run app.py
```

## 🔄 How It Works

### 1. User Input (Streamlit UI)
User describes what data they need:
- "Get cryptocurrency prices"
- "Latest news articles"
- "Weather data for Indian cities"

### 2. AI Processing (`data/mock_data.py`)
```python
generate_response(form_data)
```
- Sends user description to Gemini/DeepSeek
- AI generates structured JSON response
- Returns API endpoint and data

### 3. API Server Integration (`app.py`)
```python
ai_integration.receive_ai_data(api_payload)
```
- Extracts data from AI response
- Infers schema from data structure
- Stores in database via API server
- Creates REST endpoint

### 4. Result
- Live REST API endpoint created
- Data accessible via `http://localhost:8000/api/{api_name}`
- Automatic documentation at `/docs`

## 📊 Data Flow

```
User Input → AI Layer (Gemini/DeepSeek) → JSON Response → 
API Server → Database → REST Endpoint → User Access
```

## 🎯 Example Usage

### In Streamlit UI:

1. **Describe your data**:
   ```
   Get current cryptocurrency prices with market cap
   ```

2. **Specify fields** (optional):
   ```
   symbol
   name
   price
   market_cap
   ```

3. **Click "Generate API Endpoint"**

4. **Result**:
   - AI generates structured data
   - API endpoint created: `http://localhost:8000/api/cryptocurrency_prices`
   - Data stored in database
   - Ready to use!

### Test the Generated API:
```bash
curl http://localhost:8000/api/cryptocurrency_prices
```

## 🔧 Configuration Options

### Switch AI Provider

Edit `.env`:
```env
# Use Gemini
AI_PROVIDER=gemini

# Or use DeepSeek
AI_PROVIDER=deepseek
```

### Customize AI Prompts

Edit `data/mock_data.py` to modify the prompt sent to AI:
```python
prompt = f"""
Your custom instructions here...
Query: {user_query}
Fields: {fields}
"""
```

## 🆘 Troubleshooting

### Issue: "GEMINI_API_KEY not found"
**Solution**: Create `.env` file with your API key
```bash
echo "GEMINI_API_KEY=your_key_here" > .env
```

### Issue: "AI did not return valid JSON"
**Solution**: 
1. Check your API key is valid
2. Check your internet connection
3. Try switching AI provider in `.env`

### Issue: "Module 'genai' not found"
**Solution**: Install dependencies
```bash
pip install google-genai python-dotenv
```

### Issue: API server not storing data
**Solution**: 
1. Make sure API server is running: `python api_server.py`
2. Check server logs for errors
3. Verify database file exists: `api_data.db`

## 🎉 Success Indicators

✅ **AI Layer Working**: No errors when generating response  
✅ **API Created**: Endpoint appears in API server list  
✅ **Data Accessible**: Can curl the endpoint and get data  
✅ **UI Shows Result**: Streamlit displays generated API  

## 📝 Modified Files

Your colleague modified these files:

1. **`data/mock_data.py`**
   - Added AI integration (Gemini/DeepSeek)
   - `generate_response()` function calls AI
   - Returns structured JSON

2. **`components/results.py`**
   - Updated to handle AI-generated response format
   - Displays endpoint and data structure

3. **`utils/code_examples.py`**
   - Updated to generate docs from AI response
   - Creates OpenAPI spec, Postman collection

## 🚀 Next Steps

1. ✅ Set up API keys in `.env`
2. ✅ Install dependencies
3. ✅ Test AI generation
4. ✅ Start API server
5. ✅ Use Streamlit UI to generate APIs
6. ✅ Access generated APIs via REST

**Your AI-powered API generator is now fully operational!** 🎉