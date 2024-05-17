import subprocess
import whisper
import os
import openai
import argparse

def extract_audio(video_path, audio_path):
    """Extrai o áudio completo de um vídeo usando FFmpeg."""
    # Verificar se o FFmpeg está no PATH
    if subprocess.run(["ffmpeg", "-version"]).returncode != 0:
        raise EnvironmentError("FFmpeg não está instalado ou não está no PATH do sistema.")
    
    # Comando FFmpeg para extrair o áudio completo do vídeo
    subprocess.run([
        "ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path,
        "-y"  # Overwrite output files without asking
    ])

def transcribe_audio(audio_path, language="portuguese"):
    """Transcreve o áudio usando o modelo Whisper."""
    # Carregar o modelo Whisper
    model = whisper.load_model("base")
    
    # Transcrever o áudio extraído
    result = model.transcribe(audio_path, language=language)
    
    # Extrair o texto transcrito
    return result['text']

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
    # Caminho do vídeo original
    video_path = "C:/py-projects/whisper-transcription/files/RationalTeamConcert_CCM.mp4"
    # Caminho para salvar o áudio extraído
    audio_path = "C:/py-projects/whisper-transcription/files/RationalTeamConcert_CCM_audio.wav"
    # Caminho para salvar o texto transcrito
    text_path = os.path.splitext(video_path)[0] + ".txt"
    # Caminho para salvar o texto resumido
    summary_path = os.path.splitext(video_path)[0] + "_summary.txt"
    
    # Extrair o áudio do vídeo
    extract_audio(video_path, audio_path)
    
    # Transcrever o áudio extraído
    transcribed_text = transcribe_audio(audio_path)
    
    # Salvar o texto transcrito em um arquivo
    save_transcription(transcribed_text, text_path)
    
    # Gerar e salvar o resumo do texto transcrito
    summary_text = summarize_text(transcribed_text, api_key)
    save_transcription(summary_text, summary_path)
    
    # Remover o arquivo de áudio temporário
    remove_file(audio_path)
    
    print(f"Transcrição salva em: {text_path}")
    print(f"Resumo salvo em: {summary_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcrever e resumir o áudio de um vídeo.")
    parser.add_argument("api_key", help="Chave da API do OpenAI")
    args = parser.parse_args()
    main(args.api_key)
