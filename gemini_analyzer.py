# gemini_analyzer.py
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("⚠️ No Gemini key found in env.")

MODEL = "gemini-1.5-flash-latest"  # try this; if failing, switch to a model your key supports

def analyze_with_gemini(description):
    """
    Returns dict: {'score': int, 'summary': str}
    """
    try:
        model = genai.GenerativeModel(MODEL)
        prompt = f"""
You are an AI internship analyzer. Score this internship description from 1 to 10 for relevance to AI/ML.
Return output strictly as JSON with keys "score" and "summary".

Description:
{description}
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        # try parse JSON
        try:
            data = json.loads(text)
            return {"score": int(data.get("score", 0)), "summary": data.get("summary", "")}
        except Exception:
            # fallback: return 0 score with raw text as summary
            return {"score": 0, "summary": text}
    except Exception as e:
        print("⚠️ Gemini analysis failed:", e)
        return {"score": 0, "summary": "Analysis failed"}
