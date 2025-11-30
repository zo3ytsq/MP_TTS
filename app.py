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
# HEADER BAR (BLUE)
# ======================
st.markdown("""
    <div style="background-color:#003366;padding:1.5rem 0;text-align:center;">
        <h1 style="color:white;font-size:2.4rem;margin:0;">Slide Narrator</h1>
    </div>
""", unsafe_allow_html=True)

# ======================
# UI LAYOUT → LEFT = MASCOT | RIGHT = MAIN BOX
# ======================
left, right = st.columns([1,1.3])

with left:
    st.image("sonic_bear_mascot.png", use_column_width=True)

with right:
    # White card box
    st.markdown("""
        <div style="background-color:#ffffff;padding:2rem;border-radius:10px;
             box-shadow:0 0 12px rgba(0,0,0,0.1);font-size:1.2rem;">
            <div style="background-color:#e0f2ff;padding:1.5rem;border-radius:6px;">
                <b>Sonic Bear says:</b><br>
                Upload your PowerPoint and I’ll narrate your slides for you!<br>
                <small>This is a prototype. Remove any <b>personal or sensitive info</b> before uploading.<br>
                Only <b>.pptx</b> files are accepted. The process may take up to <b>45 seconds</b>, depending on file size.</small>
            </div>
    """, unsafe_allow_html=True)

    # PPT UPLOAD
    pptx_file = st.file_uploader("Choose PowerPoint File (.pptx)", type=["pptx"])

    # VOICE SELECTION
    selected_voice = st.selectbox("Select Voice", [
        "en-GB-SoniaNeural",
        "en-GB-RyanNeural",
        "en-US-JennyNeural",
        "en-US-GuyNeural",
        "en-SG-LunaNeural",
        "en-SG-WayneNeural"
    ])

    # ======================
    # BUTTON — GENERATE
    # ======================
    if pptx_file and st.button("Generate Narration"):

        with st.spinner("Processing text and generating narration... please wait..."):

            timestamp = int(time.time())
            temp_ppt_path = os.path.join(tempfile.gettempdir(), f"{timestamp}.pptx")

            # Save PPT temporarily
            with open(temp_ppt_path, "wb") as f:
                f.write(pptx_file.getbuffer())

            # Extract text from slides
            slides = extract_text_from_pptx(temp_ppt_path)

            # Build final text string
            narration_text = ""
            for idx, slide_text in enumerate(slides, 1):
                clean_text = '\n'.join(slide_text) if isinstance(slide_text, list) else str(slide_text)
                narration_text += f"Slide {idx}.\n{clean_text}.\n\n"

            # Generate TTS audio
            output_audio = os.path.join(tempfile.gettempdir(), f"{timestamp}_narration.mp3")
            asyncio.run(edge_tts.Communicate(text=narration_text, voice=selected_voice).save(output_audio))

            # Success message
            st.success("Narration generated! 🎉")

            # DOWNLOAD BUTTON
            with open(output_audio, "rb") as audio:
                st.download_button(
                    label="Download Narration MP3",
                    data=audio,
                    file_name="narration.mp3",
                    mime="audio/mpeg"
                )

            # SHOW SLIDE TEXT
            st.write("### Slide Narration Script:")
            for idx, slide in enumerate(slides, 1):
                st.write(f"**Slide {idx}:**")
                st.write(slide)

# ======================
# FOOTER
# ======================
st.markdown("""
    <hr>
    <div style="text-align:center;color:#666;font-size:0.9rem;padding:1rem;">
    © 2025 Temasek Polytechnic | Educational Prototype
    </div>
""", unsafe_allow_html=True)
