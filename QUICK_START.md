# Quick Start Guide - DeepSeek AI Integration

## ✅ Integration Complete!

The DeepSeek AI layer has been successfully integrated with your API server. Here's what's been set up:

### What's Working

1. **AI Layer** (`ai_layer/`) - Complete DeepSeek client with error handling
2. **Integration Layer** (`ai_integration.py`) - Bridges AI and API server  
3. **API Server** (`api_server.py`) - FastAPI server (currently running on port 8000)
4. **UI** (`app.py`) - Streamlit interface ready to use

### ⚠️ Important: API Key Required

Your `.env` file currently has a placeholder API key. To use the system:

1. Get your DeepSeek API key from: https://platform.deepseek.com/
2. Edit `.env` file and replace:
   ```bash
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   ```
   with your actual key:
   ```bash
   DEEPSEEK_API_KEY=sk-your-actual-key-here
   ```

### 🚀 Start Using the System

#### Option 1: Start Everything (Recommended)
```bash
python start_all.py
```

This will:
- Start the API server on port 8000
- Start the Streamlit UI on port 8501
- Open your browser automatically

#### Option 2: Manual Start
```bash
# Terminal 1: Start API Server
python api_server.py

# Terminal 2: Start Streamlit UI
streamlit run app.py
```

### 🧪 Test the Integration

Once you have a valid API key:

```bash
python test_integration.py
```

This will test:
- ✅ Configuration loading
- ✅ API server connectivity
- ✅ AI generation with DeepSeek
- ✅ Data integration
- ✅ API endpoint access

### 📝 Usage Example

1. Open http://localhost:8501
2. Fill in the form:
   - **Data Description**: "Top 10 programming languages"
   - **Desired Fields**: name, rank, popularity_score
   - **Update Frequency**: monthly
3. Click "Generate API"
4. Wait 10-30 seconds
5. Your API is ready at `http://localhost:8000/api/...`

### 🔧 Troubleshooting

#### SSL Certificate Error
**Fixed!** The system now automatically handles SSL certificate issues on Windows (PostgreSQL/Google Cloud SDK interference).

#### API Server Already Running
If you see "port 8000 already in use":
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Then restart
python api_server.py
```

#### Invalid API Key
Make sure your `.env` file has a valid DeepSeek API key starting with `sk-`.

### 📚 Documentation

- **Full Integration Guide**: `DEEPSEEK_INTEGRATION.md`
- **Integration README**: `INTEGRATION_README.md`
- **API Documentation**: http://localhost:8000/docs (when server is running)

### 🎯 Next Steps

1. **Add your API key** to `.env`
2. **Run tests**: `python test_integration.py`
3. **Start the UI**: `streamlit run app.py`
4. **Generate your first API!**

### 💡 Key Features

- **AI-Powered**: Uses DeepSeek to generate realistic data
- **Automatic Schema**: Infers JSON schema from generated data
- **REST API**: Full REST API with pagination, search, filtering
- **Documentation**: Auto-generated API docs
- **Database**: Persistent storage with SQLite
- **Error Handling**: Comprehensive error handling and retry logic

### 🆘 Need Help?

- Check logs in the terminal
- Run `python test_ssl.py` to verify SSL configuration
- Run `python test_integration.py` for full system test
- Review `DEEPSEEK_INTEGRATION.md` for detailed documentation

---

**Status**: ✅ Integration Complete | ⚠️ API Key Required
