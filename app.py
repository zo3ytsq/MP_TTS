import streamlit as st
from utils import extract_text_from_pptx
import edge_tts
import asyncio
import tempfile
import time
import os

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(page_title="Slide Narrator", layout="wide")

# ======================
# USER THEME SELECTION
# ======================
theme = st.sidebar.radio("Theme", ["Light", "Dark"])

if theme == "Light":
    BG_COLOR = "#f4f7fb"
    TEXTBOX_BG = "#e0f2ff"
    CARD_BG = "#ffffff"
    TEXT_COLOR = "#000000"
else:
    BG_COLOR = "#0f1116"
    TEXTBOX_BG = "#002b47"
    CARD_BG = "#0d2136"
    TEXT_COLOR = "#ffffff"

# ======================
# FRIENDLY VOICE MAPPING
# ======================
VOICE_MAP = {
    "Aria (US)": "en-US-AriaNeural",
    "Guy (US)": "en-US-GuyNeural",
    "Jenny (US)": "en-US-JennyNeural",
    "Michelle (US)": "en-US-MichelleNeural",
    "Jason (US)": "en-US-JasonNeural",
    "Libby (UK)": "en-GB-LibbyNeural",
    "Ryan (UK)": "en-GB-RyanNeural",
    "Natasha (AU)": "en-AU-NatashaNeural",
    "William (AU)": "en-AU-WilliamNeural",
}

# ======================
# HEADER
# ======================
st.markdown(f"""
    <div style="background-color:#003366;padding:1.5rem 0;text-align:center;">
        <h1 style="color:white;font-size:2.4rem;margin:0;">Slide Narrator</h1>
    </div>
""", unsafe_allow_html=True)

# ======================
# MAIN LAYOUT
# ======================
left, right = st.columns([1,1.3])

with left:
    st.image("sonic_bear_mascot.png", use_column_width=True)

with right:
    st.markdown(f"""
        <div style="background-color:{CARD_BG};padding:2rem;border-radius:10px;
             box-shadow:0 0 12px rgba(0,0,0,0.1);font-size:1.2rem;color:{TEXT_COLOR};">
            <div style="background-color:{TEXTBOX_BG};padding:1.5rem;border-radius:6px;color:{TEXT_COLOR};">
                <b style="color:{TEXT_COLOR};">Sonic Bear says:</b><br>
                Upload your PowerPoint and I’ll narrate your slides for you!<br>
                <small style="color:{TEXT_COLOR};">This is a prototype. Remove any <b>personal or sensitive info</b> before uploading.<br>
                Only <b>.pptx</b> files are accepted. The process may take up to <b>45 seconds</b>, depending on file size.</small>
            </div>
    """, unsafe_allow_html=True)

    pptx_file = st.file_uploader("Choose PowerPoint File (.pptx)", type=["pptx"])

    voice_display = st.selectbox("Select Voice", list(VOICE_MAP.keys()))
    selected_voice = VOICE_MAP[voice_display]

    # ======================
    # BUTTON — GENERATE
    # ======================
    if pptx_file and st.button("Generate Narration"):
        with st.spinner("Processing text and generating narration... please wait..."):
            timestamp = int(time.time())
            temp_ppt_path = os.path.join(tempfile.gettempdir(), f"{timestamp}.pptx")

            with open(temp_ppt_path, "wb") as f:
                f.write(pptx_file.getbuffer())

            slides = extract_text_from_pptx(temp_ppt_path)

            narration_text = ""
            for idx, slide_text in enumerate(slides, 1):
                clean_text = '\n'.join(slide_text) if isinstance(slide_text, list) else str(slide_text)
                narration_text += f"Slide {idx}.\n{clean_text}.\n\n"

            output_audio = os.path.join(tempfile.gettempdir(), f"{timestamp}_narration.mp3")

            try:
                asyncio.run(edge_tts.Communicate(
                    text=narration_text, 
                    voice=selected_voice
                ).save(output_audio))
            except:
                st.warning("Selected voice unavailable — using backup voice Aria (US)")
                asyncio.run(edge_tts.Communicate(
                    text=narration_text, 
                    voice="en-US-AriaNeural"
                ).save(output_audio))

            st.success("Narration generated! 🎉")

            with open(output_audio, "rb") as audio:
                st.download_button(
                    label="Download Narration MP3",
                    data=audio,
                    file_name="narration.mp3",
                    mime="audio/mpeg"
                )

            st.write(f"<h3 style='color:{TEXT_COLOR}'>Slide Narration Script:</h3>", unsafe_allow_html=True)
            for idx, slide in enumerate(slides, 1):
                st.write(f"**Slide {idx}:**")
                st.write(slide)

# ======================
# FOOTER
# ======================
st.markdown(f"""
    <hr>
    <div style="text-align:center;color:{TEXT_COLOR};font-size:0.9rem;padding:1rem;">
    © 2025 Temasek Polytechnic | Educational Prototype
    </div>
""", unsafe_allow_html=True)
