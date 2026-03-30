import os
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

# Load .env from the project root (one level up from the backend folder)
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(os.path.dirname(current_dir), ".env")
load_dotenv(dotenv_path=env_path)

# Attempt to get key from OS environment or Streamlit Secrets fallback
try:
    api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print(f"Warning: GEMINI_API_KEY not found. Checked .env at: {env_path}")

genai.configure(api_key=api_key)

def get_ai_explanation(language, code):
    prompt = (
        f"Analyze this {language} code snippet.\n"
        "Provide the output in the following format:\n"
        "1. 🧩 **About the Language**: Brief details about the programming language and its key features.\n"
        "2. 📦 **About the Libraries**: Explain the purpose of any libraries or modules used in the code.\n"
        "3. 📊 **Difficulty Level**: Estimate the complexity (Beginner, Intermediate, or Advanced) with a short reason.\n"
        "4. 🪜 **Step-by-step Execution**: Detailed walkthrough of how the code executes line by line.\n"
        "5.  **Predicted Output**: Show the expected output of this code. If there are inputs required, mention them.\n"
        "6. 🛠️ **Error Analysis & Debugging**: Check for any syntax or logical errors. If found, name the error type, explain it, and provide the corrected code. If no errors, state 'No errors found'.\n"
        "7. 💡 **Code Explanation**: Breakdown of the logic and purpose.\n"
        "8. ⏳ **Time and Space Complexity**: Analyze the performance.\n"
        "9. 🚀 **Suggested Improvements**: Recommendations for better code quality or optimization.\n\n"
        f"Code:\n{code}"
    )
    try:
        # Try preferred models in order
        models_to_try = ['gemini-1.5-flash', 'gemini-pro', 'gemini-1.5-pro-latest']
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text
            except Exception:
                continue
        
        # If all predefined models fail, list available models and try the first Gemini one
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        gemini_model = next((m for m in available_models if 'gemini' in m), None)
        
        if gemini_model:
            model = genai.GenerativeModel(gemini_model)
            response = model.generate_content(prompt)
            return response.text
            
        return f"AI Error: No compatible Gemini models found. Available: {available_models}"

    except Exception as e:
        return f"AI Error: {str(e)}"
