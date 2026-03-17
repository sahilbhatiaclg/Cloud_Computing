import streamlit as st
import requests
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="MultiTalk AI", page_icon="🌐", layout="wide")

# --- CUSTOM CSS FOR ATTRACTIVE UI/UX ---
st.markdown("""
    <style>
    /* Dark Theme with Emerald Glow */
    .stApp { background-color: #0B0E11; color: #E0E0E0; }
    
    /* Title Styling */
    .main-title { color: #00FF88; font-family: 'Segoe UI', sans-serif; font-weight: 800; font-size: 3rem; text-align: center; margin-bottom: 0px; text-shadow: 0px 0px 10px #00FF88; }
    
    /* Input & Output Boxes */
    .stTextArea textarea { background-color: #161B22 !important; color: #00FF88 !important; border: 1px solid #30363D !important; border-radius: 12px; font-size: 1.1rem; }
    .stTextArea textarea:focus { border: 1px solid #00FF88 !important; box-shadow: 0px 0px 10px #00FF88; }
    
    /* Translation Card */
    .translation-card { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(0, 255, 136, 0.3); margin-top: 20px; }
    
    /* Button Styling */
    div.stButton > button { background-color: #00FF88 !important; color: #0B0E11 !important; font-weight: bold; border-radius: 10px; height: 3em; width: 100%; border: none; transition: 0.3s; }
    div.stButton > button:hover { box-shadow: 0px 0px 20px #00FF88; transform: translateY(-2px); }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<p class="main-title">MultiTalk AI</p>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8B949E;'>Translate global feedback to English instantly via MS Foundry</p>", unsafe_allow_html=True)

# --- SIDEBAR (CONTROL PANEL) ---
with st.sidebar:
    st.image("https://img.icons8.com/fluent/100/000000/azure-api_manager.png")
    st.header("Azure Config")
    api_key = st.text_input("Translator Key", type="password")
    endpoint = st.text_input("Foundry Endpoint", placeholder="https://api.cognitive.microsofttranslator.com")
    location = st.text_input("Resource Region", placeholder="e.g., eastus")
    st.divider()
    st.caption("Status: Connected to Azure AI Engine" if api_key else "Status: Waiting for Credentials")

# --- MAIN INTERFACE (NO SCROLL) ---
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📥 Multilingual Input")
    text_to_translate = st.text_area("Enter feedback (Spanish, French, Hindi, etc.):", height=200, placeholder="Type here...")

with col2:
    st.subheader("📤 English Translation")
    
    if st.button("CONVERT TO ENGLISH ⚡"):
        if not api_key or not endpoint:
            st.error("Missing API Key or Endpoint in the sidebar!")
        elif not text_to_translate.strip():
            st.warning("Please enter text to translate.")
        else:
            try:
                # Azure Translator API Logic
                path = '/translate?api-version=3.0'
                params = '&to=en'
                constructed_url = endpoint + path + params

                headers = {
                    'Ocp-Apim-Subscription-Key': api_key,
                    'Ocp-Apim-Subscription-Region': location,
                    'Content-type': 'application/json',
                    'X-ClientTraceId': str(uuid.uuid4())
                }

                body = [{'text': text_to_translate}]
                
                with st.spinner('Synchronizing with Foundry...'):
                    response = requests.post(constructed_url, headers=headers, json=body)
                    response.raise_for_status()
                    translated_data = response.json()
                
                # Extract results
                translated_text = translated_data[0]['translations'][0]['text']
                detected_lang = translated_data[0]['detectedLanguage']['language']

                st.markdown(f"""
                    <div class="translation-card">
                        <p style='color: #8B949E; font-size: 0.8rem;'>Detected Language: <b>{detected_lang.upper()}</b></p>
                        <p style='font-size: 1.2rem;'>{translated_text}</p>
                    </div>
                """, unsafe_allow_html=True)
                st.balloons()

            except Exception as e:
                st.error(f"API Connection Error: {str(e)}")
    else:
        st.info("Results will appear here once you click translate.")

st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 0.7rem; color: #484F58;'>Powered by Microsoft AI Foundry & Azure Neural Translation</p>", unsafe_allow_html=True)