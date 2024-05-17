import subprocess
import whisper
import os
import openai
import argparse
import uuid
import shutil

def extract_audio_segments(video_path, segment_duration=1200, tmp_dir="tmp"):
    """Extrai segmentos de áudio do vídeo usando FFmpeg."""
    if subprocess.run(["ffmpeg", "-version"]).returncode != 0:
        raise EnvironmentError("FFmpeg não está instalado ou não está no PATH do sistema.")
    
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    total_duration = float(result.stdout)
    
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    tmp_subdir = os.path.join(tmp_dir, f"{video_name}_{uuid.uuid4()}")
    os.makedirs(tmp_subdir, exist_ok=True)

    segments = []
    for start_time in range(0, int(total_duration), segment_duration):
        segment_path = os.path.join(tmp_subdir, f"{video_name}_{start_time // 60}min.wav")
        segments.append((start_time, segment_path))
        subprocess.run([
            "ffmpeg", "-i", video_path, "-ss", str(start_time), "-t", str(segment_duration),
            "-q:a", "0", "-map", "a", segment_path,
            "-y"
        ])
    return segments, tmp_subdir

def transcribe_audio_segment(audio_path, language="portuguese"):
    """Transcreve um segmento de áudio usando o modelo Whisper e adiciona quebras de linha para separar diálogos."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, language=language)
    
    segments = result['segments']
    transcribed_text = ""
    for segment in segments:
        transcribed_text += segment['text'] + "\n\n"

    return transcribed_text.strip()

def save_transcription(text, text_path):
    """Salva o texto transcrito em um arquivo."""
    with open(text_path, 'w', encoding='utf-8') as file:
        file.write(text)

def remove_file(file_path):
    """Remove o arquivo especificado."""
    if os.path.exists(file_path):
        os.remove(file_path)

def summarize_text(text, api_key):
    """Resume o texto usando a API do OpenAI."""
    openai.api_key = api_key
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Resuma o seguinte texto:\n\n{text}",
        max_tokens=150,
        temperature=0.7
    )
    summary = response.choices[0].text.strip()
    return summary

def main(api_key):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    video_filename = "RationalTeamConcert_CCM.mp4"
    video_path = os.path.join(script_dir, video_filename)
    
    base_name = os.path.splitext(video_filename)[0]
    unique_id = str(uuid.uuid4())
    output_subdir = os.path.join(script_dir, "files", f"{base_name}_{unique_id}")
    os.makedirs(output_subdir, exist_ok=True)
    
    segments, tmp_subdir = extract_audio_segments(video_path)
    
    all_transcriptions = ""
    for start_time, audio_path in segments:
        transcribed_text = transcribe_audio_segment(audio_path)
        
        text_path = os.path.join(output_subdir, f"{base_name}_{start_time // 60}min.txt")
        save_transcription(transcribed_text, text_path)
        
        all_transcriptions += transcribed_text + "\n\n"
        remove_file(audio_path)
        
        print(f"Transcrição do segmento começando em {start_time // 60} minutos salva em: {text_path}")
    
    concatenated_transcription_path = os.path.join(output_subdir, f"{base_name}.txt")
    save_transcription(all_transcriptions, concatenated_transcription_path)
    print(f"Transcrição completa salva em: {concatenated_transcription_path}")

    summary_text = summarize_text(all_transcriptions, api_key)
    summary_path = os.path.join(output_subdir, f"{base_name}_summary.txt")
    save_transcription(summary_text, summary_path)
    print(f"Resumo salvo em: {summary_path}")

    shutil.rmtree(tmp_subdir)
    print(f"Diretório temporário {tmp_subdir} removido.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcrever e resumir o áudio de um vídeo.")
    parser.add_argument("api_key", help="Chave da API do OpenAI")
    args = parser.parse_args()
    main(args.api_key)
