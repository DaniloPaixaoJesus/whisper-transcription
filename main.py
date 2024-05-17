import subprocess
import whisper
import os
from openai import OpenAI
import argparse
import uuid
import shutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def extract_audio(video_path, audio_path):
    """Extrai o áudio completo de um vídeo usando FFmpeg."""
    if subprocess.run(["ffmpeg", "-version"]).returncode != 0:
        raise EnvironmentError("FFmpeg não está instalado ou não está no PATH do sistema.")
    
    subprocess.run([
        "ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path,
        "-y"  # Overwrite output files without asking
    ])

def transcribe_audio(audio_path, language="portuguese"):
    """Transcreve o áudio usando o modelo Whisper."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, language=language)
    
    # Construir o texto com separação de diálogos
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
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Interpret the following text extracted from a video transcription:\n\n" + text,
            }
        ],
        model="gpt-3.5-turbo",
    )
    summary = response.choices[0].message.content

    return summary

def send_email(subject, body, to_email, files):
    """Envia um e-mail com os arquivos anexados."""
    from_email = "emaill@gmail.com"
    from_password = "password"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    for file in files:
        attachment = open(file, "rb")

        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= " + os.path.basename(file))

        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, from_password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

def main(api_key, video_filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(script_dir, video_filename)
    
    base_name = os.path.splitext(video_filename)[0]
    unique_id = str(uuid.uuid4())
    output_subdir = os.path.join(script_dir, "files", f"{base_name}_{unique_id}")
    tmp_subdir = os.path.join(script_dir, "tmp", f"{base_name}_{unique_id}")
    os.makedirs(output_subdir, exist_ok=True)
    os.makedirs(tmp_subdir, exist_ok=True)
    
    audio_path = os.path.join(tmp_subdir, f"{base_name}.wav")
    
    # Extrair o áudio completo do vídeo
    extract_audio(video_path, audio_path)
    
    # Transcrever o áudio completo
    transcribed_text = transcribe_audio(audio_path)
    
    # Caminho para salvar a transcrição completa
    transcription_path = os.path.join(output_subdir, f"{base_name}.txt")
    save_transcription(transcribed_text, transcription_path)
    print(f"Transcrição completa salva em: {transcription_path}")
    
    # Gerar e salvar o resumo do texto transcrito
    summary_text = summarize_text(transcribed_text, api_key)
    summary_path = os.path.join(output_subdir, f"{base_name}_summary.txt")
    save_transcription(summary_text, summary_path)
    print(f"Resumo salvo em: {summary_path}")

    # Enviar o e-mail com os arquivos anexados
    send_email(
        subject="Transcrição e Resumo",
        body="Segue em anexo a transcrição completa e o resumo.",
        to_email="contato.danilo.paixao@gmail.com",
        files=[transcription_path, summary_path]
    )
    
    # Remover o arquivo de áudio temporário e o diretório temporário
    shutil.rmtree(tmp_subdir)
    print(f"Diretório temporário {tmp_subdir} removido.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcrever e resumir o áudio de um vídeo.")
    parser.add_argument("api_key", help="Chave da API do OpenAI")
    parser.add_argument("video_filename", help="Nome do arquivo de vídeo")
    args = parser.parse_args()
    main(args.api_key, args.video_filename)
