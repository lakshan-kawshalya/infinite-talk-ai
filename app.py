import streamlit as st
import requests
from PIL import Image
import io

# --- 1. CONFIGURATION & STATE ---
st.set_page_config(
    page_title="Infinite Talk AI",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State to store the API URL across re-runs
if 'api_url' not in st.session_state:
    st.session_state['api_url'] = ""

# --- 2. UI STYLING ---
st.markdown("""
    <style>
    .main-title { font-size: 3rem; font-weight: 800; color: #2C3E50; }
    .subtitle { font-size: 1.2rem; color: #7F8C8D; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .status-ok { color: green; font-weight: bold; }
    .status-err { color: red; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR: SERVER CONNECTION ---
with st.sidebar:
    st.image("https://img.icons8.com/cloud/100/null/cloud-lighting.png", width=80)
    st.title("⚙️ System Config")
    st.markdown("---")

    st.info("💡 **Architecture:** This Client connects to a remote Google Colab GPU server.")

    # Input for the Ngrok URL generated in Colab
    url_input = st.text_input(
        "Backend API URL",
        placeholder="https://xxxx-xxxx.ngrok-free.app",
        help="Paste the public URL from the Colab notebook here."
    )

    # Save URL to session state
    if url_input:
        st.session_state['api_url'] = url_input.rstrip('/')

    # Connection Test
    if st.button("🔌 Test Connection"):
        if not st.session_state['api_url']:
            st.error("Please enter a URL first.")
        else:
            try:
                # We hit the /health endpoint of our FastAPI server
                response = requests.get(f"{st.session_state['api_url']}/health", timeout=5)
                if response.status_code == 200:
                    st.markdown('<p class="status-ok">✅ Server Online (GPU Active)</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p class="status-err">❌ Server Error (500)</p>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<p class="status-err">❌ Connection Failed: {e}</p>', unsafe_allow_html=True)

# --- 4. MAIN INTERFACE ---
st.markdown('<div class="main-title">Infinite Talk AI 🗣️</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Distributed Generative Video Platform | Powered by Wav2Lip-GAN</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1️⃣ Source Avatar")
    uploaded_file = st.file_uploader("Upload Portrait (JPG/PNG)", type=['jpg', 'png', 'jpeg'])

    if uploaded_file:
        # Display the uploaded image
        st.image(uploaded_file, caption="Source Image", use_column_width=True)

with col2:
    st.subheader("2️⃣ Scripting")
    script_text = st.text_area(
        "Enter Dialogue",
        height=150,
        placeholder="Hello! I am a digital avatar created by Xpersive Labs."
    )

    voice_option = st.selectbox(
        "Select Voice Model",
        ["en-US-ChristopherNeural", "en-US-AriaNeural", "en-GB-SoniaNeural", "en-IN-PrabhatNeural"]
    )

    st.divider()

    generate_btn = st.button("🚀 Generate Video", type="primary", disabled=(not uploaded_file or not script_text))

# --- 5. GENERATION LOGIC ---
if generate_btn:
    if not st.session_state['api_url']:
        st.error("⚠️ Backend URL missing! Please configure the server in the sidebar.")
    else:
        with st.status("Processing Request...", expanded=True) as status:
            try:
                # A. Prepare Data
                status.write("📤 Uploading assets to Cloud GPU...")
                files = {'image': ('avatar.jpg', uploaded_file.getvalue(), 'image/jpeg')}
                data = {'text': script_text, 'voice': voice_option}

                # B. Call API
                api_endpoint = f"{st.session_state['api_url']}/generate"
                status.write("🧠 Running Inference (Wav2Lip-GAN)...")

                response = requests.post(api_endpoint, files=files, data=data, timeout=300)

                if response.status_code == 200:
                    status.update(label="✅ Complete!", state="complete", expanded=False)

                    # C. Display & Download
                    st.success("Video generated successfully!")
                    st.video(response.content)

                    st.download_button(
                        label="Download MP4",
                        data=response.content,
                        file_name="infinite_talk_output.mp4",
                        mime="video/mp4"
                    )
                else:
                    status.update(label="❌ Server Error", state="error")
                    st.error(f"Backend Error: {response.text}")

            except requests.exceptions.ConnectionError:
                status.update(label="❌ Connection Failed", state="error")
                st.error("Could not connect to Colab. Is the Ngrok tunnel active?")
            except Exception as e:
                status.update(label="❌ Unexpected Error", state="error")
                st.error(f"Error: {e}")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888;'>"
    "Architecture: Streamlit (Client) ↔ Ngrok ↔ FastAPI (Colab GPU) <br>"
    "Developed by <b>Xpersive Labs</b>"
    "</div>",
    unsafe_allow_html=True
)