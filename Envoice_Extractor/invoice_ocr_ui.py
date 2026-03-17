import streamlit as st
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from PIL import Image
import io

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="InvoiceLens OCR", page_icon="🧾", layout="wide")

# --- CUSTOM CSS FOR NEWSROOM/TECH THEME ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .main-header { color: #00FF88; font-weight: 800; font-size: 2.5rem; text-shadow: 0px 0px 10px #00FF88; }
    .stFileUploader { border: 2px dashed #00FF88 !important; border-radius: 10px; }
    .result-card { background-color: #161B22; padding: 20px; border-radius: 15px; border-left: 5px solid #00FF88; margin-top: 10px; }
    div.stButton > button { background-color: #00FF88 !important; color: #0E1117 !important; font-weight: bold; border-radius: 8px; width: 100%; border: none; }
    div.stButton > button:hover { box-shadow: 0px 0px 15px #00FF88; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<h1 class="main-header">🧾 InvoiceLens AI</h1>', unsafe_allow_html=True)
st.write("Extract printed and handwritten billing data using Azure AI Vision OCR.")

# --- SIDEBAR (CONFIG) ---
with st.sidebar:
    st.header("⚙️ Azure Config")
    api_key = st.text_input("Vision API Key", type="password")
    endpoint = st.text_input("Vision Endpoint")
    st.divider()
    st.info("Upload an invoice to see the OCR engine in action.")

# --- MAIN LAYOUT ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📁 Upload Invoice")
    uploaded_file = st.file_uploader("Choose an image (JPG, PNG, PDF)", type=["jpg", "jpeg", "png", "pdf"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Document Preview", use_container_width=True)

with col2:
    st.subheader("📄 Extracted Text")
    
    if st.button("RUN OCR ANALYSIS 🔍"):
        if not api_key or not endpoint:
            st.error("Please provide your Azure Vision credentials in the sidebar.")
        elif not uploaded_file:
            st.warning("Please upload an invoice first.")
        else:
            try:
                # Convert uploaded file to bytes for the API
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format)
                image_data = img_byte_arr.getvalue()

                # Initialize Azure AI Vision Client
                client = ImageAnalysisClient(
                    endpoint=endpoint,
                    credential=AzureKeyCredential(api_key)
                )

                with st.spinner('Scanning document for handwritten & printed text...'):
                    # Perform OCR (Text Extraction)
                    result = client.analyze(
                        image_data=image_data,
                        visual_features=[VisualFeatures.READ]
                    )

                # Display Results
                if result.read is not None:
                    full_text = ""
                    for line in result.read.blocks[0].lines:
                        full_text += line.text + "\n"
                    
                    st.markdown(f'<div class="result-card">{full_text}</div>', unsafe_allow_html=True)
                    st.success("Analysis Complete!")
                else:
                    st.info("No text detected in this document.")

            except Exception as e:
                st.error(f"API Error: {str(e)}")
    else:
        st.info("The extracted data will appear here.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #8B949E;'>Powered by Azure AI Vision Read API</p>", unsafe_allow_html=True)