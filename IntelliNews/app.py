import os
import streamlit as st
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables from .env
load_dotenv()

# --- AZURE CLIENT INITIALIZATION ---
def get_summarizer():
    endpoint = os.getenv("LANGUAGE_ENDPOINT")
    key = os.getenv("LANGUAGE_KEY")
    return TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

def get_translator():
    # Note: Translator uses a different credential class in some SDK versions, 
    # but AzureKeyCredential is standard for the latest TextTranslationClient.
    key = os.getenv("TRANSLATOR_KEY")
    region = os.getenv("REGION")
    return TextTranslationClient(credential=AzureKeyCredential(key), region=region)

# --- CORE AI LOGIC ---
def summarize_text(text):
    client = get_summarizer()
    # Updated method name for latest SDK
    poller = client.begin_abstract_summary([text], sentence_count=3)
    result = poller.result()
    
    summary = ""
    # Correct way to iterate through ItemPaged results
    for doc in result:
        if not doc.is_error:
            summary = " ".join([s.text for s in doc.summaries])
        else:
            st.error(f"Summarization Error: {doc.error.message}")
            return None
    
    # Ensure it stays around 60 words
    return " ".join(summary.split()[:60])

def translate_summary(text, target_lang_code):
    client = get_translator()
    # Translate the 60-word summary
    response = client.translate(body=[text], to_language=[target_lang_code])
    return response[0].translations[0].text

def play_audio(text, lang_name):
    speech_key = os.getenv("SPEECH_KEY")
    region = os.getenv("REGION")
    
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=region)
    
    # Mapping languages to specific Neural Voices for Accessibility
    voice_map = {
        "English": "en-US-AvaNeural",
        "Hindi": "hi-IN-SwaraNeural",
        "German": "de-DE-KatjaNeural",
        "French": "fr-FR-DeniseNeural",
        "Punjabi": "pa-IN-NavjotNeural"
    }
    speech_config.speech_synthesis_voice_name = voice_map.get(lang_name, "en-US-AvaNeural")
    
    # Speak through default system speakers
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    synthesizer.speak_text_async(text)

# --- UI DESIGN (INTELLINEWS) ---
st.set_page_config(page_title="IntelliNews", page_icon="📰", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .title { color: #0078d4; font-family: 'Helvetica'; font-weight: bold; text-align: center; }
    .stButton>button { background-color: #0078d4; color: white; width: 100%; border-radius: 5px; }
    .result-card { background: white; padding: 20px; border-radius: 10px; border-left: 5px solid #0078d4; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title'>📰 IntelliNews AI</h1>", unsafe_allow_html=True)
st.write("<p style='text-align: center;'>Educational Intelligence: Summarize, Translate, and Listen</p>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.subheader("1. Input News Content")
    news_input = st.text_area("Paste the long news article here:", height=350, placeholder="Start typing or paste...")

with col2:
    st.subheader("2. Settings")
    languages = {
        "English": "en",
        "Hindi": "hi",
        "German": "de",
        "French": "fr",
        "Punjabi": "pa"
    }
    selected_lang = st.selectbox("Translate Result To:", list(languages.keys()))
    
    st.write("---")
    
    if st.button("✨ Process IntelliNews"):
        if news_input:
            with st.spinner("Analyzing and Translating..."):
                # Step 1: Summarize (English)
                eng_summary = summarize_text(news_input)
                
                # Step 2: Translate to selected language
                if eng_summary:
                    final_summary = translate_summary(eng_summary, languages[selected_lang])
                    st.session_state['result_text'] = final_summary
                    st.session_state['lang_label'] = selected_lang
        else:
            st.error("Please provide an article first.")

# --- RESULTS SECTION ---
if 'result_text' in st.session_state:
    st.divider()
    res_col1, res_col2 = st.columns([3, 1])
    
    with res_col1:
        st.markdown(f"### 📄 {st.session_state['lang_label']} Summary")
        st.markdown(f'<div class="result-card">{st.session_state["result_text"]}</div>', unsafe_allow_html=True)
    
    with res_col2:
        st.markdown("### 🔊 Accessibility")
        st.write("Listen to the summary:")
        if st.button("▶️ Play Audio"):
            play_audio(st.session_state['result_text'], st.session_state['lang_label'])
            st.success("Playing audio via system speakers...")