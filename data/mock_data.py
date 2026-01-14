from dotenv import load_dotenv
load_dotenv()

import os
import json
from datetime import datetime

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")  # gemini or deepseek

# Initialize Gemini client only if API key is provided
gemini_client = None
if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    try:
        from google import genai
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Warning: Could not initialize Gemini client: {e}")


def call_gemini(prompt):
    if not gemini_client:
        raise ValueError("Gemini API key not configured. Please set GEMINI_API_KEY in .env file")
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text


def call_deepseek(prompt):
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
        raise ValueError("DeepSeek API key not configured. Please set DEEPSEEK_API_KEY in .env file")
    import requests
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You generate structured JSON APIs from user needs."},
            {"role": "user", "content": prompt}
        ]
    }
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def generate_response(form_data):
    user_query = form_data.get("data_description", "")
    fields = form_data.get("desired_fields", "")

    prompt = f"""
User wants public data as API.

Query: {user_query}
Fields needed: {fields}

Rules:
- Return ONLY raw JSON.
- Do NOT wrap in quotes.
- Do NOT use markdown.
- Do NOT add explanations.

Format:
{{
  "endpoint": "...",
  "method": "GET",
  "response": {{
    "status": "success",
    "data": {{ ... }},
    "generated_at": "..."
  }}
}}
"""


    if AI_PROVIDER == "deepseek":
        ai_text = call_deepseek(prompt)
    else:
        ai_text = call_gemini(prompt)

    ai_text = ai_text.strip()

    # Remove markdown fences
    if ai_text.startswith("```"):
        ai_text = ai_text.replace("```json", "").replace("```", "").strip()

    # If JSON is wrapped in quotes, unwrap it
    if ai_text.startswith('"') and ai_text.endswith('"'):
        ai_text = ai_text[1:-1]

    try:
        
        result = json.loads(ai_text)        
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": "AI did not return valid JSON",
            "raw": ai_text,
        "parse_error": str(e)
    }
