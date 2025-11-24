from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from utils import extract_text_from_pptx
import os
import time
import edge_tts
import asyncio

app = Flask(__name__)
app.secret_key = 'super-secret'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['AUDIO_FOLDER'] = os.path.join('static', 'outputs')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)


# Async wrapper for Edge TTS
async def generate_tts(text, voice, output_path):
    tts = edge_tts.Communicate(text=text, voice=voice)
    await tts.save(output_path)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    try:
        pptx_file = request.files.get('pptx_file')
        selected_voice = request.form.get('voice')

        if not pptx_file or not pptx_file.filename.endswith('.pptx'):
            flash("Only .pptx files are supported.")
            return redirect(url_for('index'))

        filename = secure_filename(pptx_file.filename)
        timestamp = int(time.time())
        saved_name = f"{os.path.splitext(filename)[0]}_{timestamp}.pptx"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_name)
        pptx_file.save(file_path)

        slides = extract_text_from_pptx(file_path)

        # Compose narration text with spacing and breaks
        narration_text = ""
        for idx, slide_text in enumerate(slides, 1):
            if isinstance(slide_text, list):
                clean_text = '\n'.join(slide_text).strip()
            else:
                clean_text = str(slide_text).strip()
            narration_text += f"Slide {idx}.\n{clean_text}.\n\n"

        # Generate TTS audio using Edge TTS
        audio_filename = f"{timestamp}_narration.mp3"
        audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)
        asyncio.run(generate_tts(narration_text, selected_voice, audio_path))

        return render_template('result.html', notes=slides, download_link=audio_path)

    except Exception as e:
        return f"<h2>An error occurred:</h2><pre>{str(e)}</pre>", 500


@app.route('/download')
def download():
    path = request.args.get('file')
    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)