import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Set up Page Configuration
st.set_page_config(page_title="AI Code Explainer", page_icon="🤖", layout="wide")

# 3. Securely Retrieve API Key
# It checks both the local .env file and Streamlit Cloud Secrets
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Gemini API Key not found! Please check your .env file or Streamlit Secrets.")
    st.stop()

try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Failed to configure Gemini: {e}")
    st.stop()

@st.cache_resource
def get_available_models():
    """Fetch and cache available models to improve performance."""
    try:
        return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except Exception:
        return []

def explain_code_with_fallback(prompt, temperature):
    """Tries multiple models to ensure the request succeeds even if specific models are unavailable."""
    available_models = get_available_models()
    if not available_models:
        raise Exception("Failed to list models. Please check your API key.")

    # 2. Prioritize models in order of performance/cost
    preferred_order = [
        'models/gemini-1.5-flash', 
        'models/gemini-1.5-pro', 
        'models/gemini-pro',
        'gemini-1.5-flash',
        'gemini-pro'
    ]
    
    # Create a list of models to try that actually exist in your account
    models_to_try = [m for m in preferred_order if m in available_models or m.replace('models/', '') in available_models]
    
    if not models_to_try:
        # Fallback to the first available model if none of our preferences are found
        models_to_try = [available_models[0]] if available_models else []
    
    last_error = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name=model_name)
            response = model.generate_content(
                prompt,
                generation_config={"temperature": temperature}
            )
            return response.text
        except Exception as e:
            last_error = e
            continue
    raise Exception(f"All models failed. Last error: {last_error}")

# 4. Main UI
st.title("🚀 Project 1: AI Code Explanation Tool")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    verbosity = st.select_slider("Explanation Verbosity", options=["Brief", "Standard", "Comprehensive"], value="Standard")
    temperature = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.3)
    if st.button("Clear History"):
        st.rerun()

st.markdown("### 🔍 Analyze & Understand Code\nSelect the programming language and paste your code snippet below to get a professional breakdown.")

languages = ["Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "HTML/CSS", "SQL", "TypeScript", "Other"]
selected_language = st.selectbox("Select Programming Language", languages, index=0)

code_input = st.text_area("Enter your code here:", height=250, placeholder="def my_function():\n    return 'Hello World'")

if st.button("Explain Code", type="primary"):
    if not code_input.strip():
        st.warning("⚠️ Please provide a code snippet first.")
    else:
        with st.spinner("Analyzing your code..."):
            try:
                # Enhanced prompt engineering
                prompt = (
                    "You are an expert software engineer. "
                    f"Analyze this {selected_language} code snippet and provide a {verbosity} explanation.\n\n"
                    f"Code:\n```\n{code_input}\n```\n\n"
                    "Please include the following structured sections:\n"
                    "### 1. 🪜 Step-by-Step Explanation\nProvide a detailed walkthrough of how the code executes line by line.\n\n"
                    "### 2. ⏳ Time and Space Complexity\nAnalyze the performance using Big O notation.\n\n"
                    "### 3. 🚀 Suggested Improvements\nProvide specific recommendations for better code quality, performance, or security."
                )
                
                # Use the fallback logic
                explanation = explain_code_with_fallback(prompt, temperature)
                
                st.divider()
                st.subheader("💡 Code Analysis")
                st.markdown(explanation)
                
            except Exception as e:
                st.error(f"An error occurred during generation: {e}")
