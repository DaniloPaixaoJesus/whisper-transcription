import os
import uuid
import subprocess
import whisper

def extract_audio(video_path, audio_path):
    """Extrai o áudio de um vídeo usando FFmpeg."""
    if subprocess.run(["ffmpeg", "-version"]).returncode != 0:
        raise EnvironmentError("FFmpeg não está instalado ou não está no PATH.")

    subprocess.run([
        "ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path, "-y"
    ], check=True)

def transcribe_audio(audio_path, language):
    """Transcreve o áudio usando Whisper."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, language=language)
    return "\n\n".join(segment['text'] for segment in result['segments'])

def save_file(text, path):
    """Salva o texto da transcrição em arquivo."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

def process_transcription(video_path, language="portuguese"):
    print(f"Iniciando transcrição: {video_path}")
    
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    uid = str(uuid.uuid4())

    tmp_dir = os.path.join("src", "tmp")
    results_dir = os.path.join("src", "results")
    os.makedirs(tmp_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    audio_path = os.path.join(tmp_dir, f"{base_name}_{uid}.wav")
    transcription_path = os.path.join(results_dir, f"{base_name}_transcription_{uid}.txt")

    try:
        extract_audio(video_path, audio_path)
        transcription = transcribe_audio(audio_path, language)
        save_file(transcription, transcription_path)
        print(f"Transcrição salva em: {transcription_path}")
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"Áudio temporário removido: {audio_path}")
