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
from config import get_config

def extract_audio(video_path, audio_path):
    """Extracts the complete audio from a video using FFmpeg."""
    if subprocess.run(["ffmpeg", "-version"]).returncode != 0:
        raise EnvironmentError("FFmpeg is not installed or not in the system PATH.")
    
    subprocess.run([
        "ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path,
        "-y"  # Overwrite output files without asking
    ])

def transcribe_audio(audio_path, language):
    """Transcribes audio using the Whisper model."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, language=language)
    
    # Build the text with dialogue separation
    segments = result['segments']
    transcribed_text = ""
    for segment in segments:
        transcribed_text += segment['text'] + "\n\n"

    return transcribed_text.strip()

def save_transcription(text, text_path):
    """Saves the transcribed text to a file."""
    with open(text_path, 'w', encoding='utf-8') as file:
        file.write(text)

def remove_file(file_path):
    """Removes the specified file."""
    if os.path.exists(file_path):
        os.remove(file_path)

def summarize_text(text, api_key, language):
    """Summarizes the text using the OpenAI API."""
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Summarize the following text in {language}:\n\n" + text,
            }
        ],
        model="gpt-4",
    )
    summary = response.choices[0].message.content

    return summary

def send_email(subject, body, to_email, files, config):
    """Sends an email with the attached files."""
    from_email = config['from_email']
    from_password = config['from_password']
    smtp_server = config['smtp_server']
    smtp_port = config['smtp_port']

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

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(from_email, from_password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

def main(video_filename, language):
    config = get_config()
    api_key = config['api_key']
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(script_dir, video_filename)
    
    base_name = os.path.splitext(video_filename)[0]
    unique_id = str(uuid.uuid4())
    output_subdir = os.path.join(script_dir, "files", f"{base_name}_{unique_id}")
    tmp_subdir = os.path.join(script_dir, "tmp", f"{base_name}_{unique_id}")
    os.makedirs(output_subdir, exist_ok=True)
    os.makedirs(tmp_subdir, exist_ok=True)
    
    audio_path = os.path.join(tmp_subdir, f"{base_name}.wav")
    
    # Extract the complete audio from the video
    extract_audio(video_path, audio_path)
    
    # Transcribe the complete audio
    transcribed_text = transcribe_audio(audio_path, language)
    
    # Path to save the complete transcription
    transcription_path = os.path.join(output_subdir, f"{base_name}.txt")
    save_transcription(transcribed_text, transcription_path)
    print(f"Complete transcription saved to: {transcription_path}")
    
    # Generate and save the summary of the transcribed text
    summary_text = summarize_text(transcribed_text, api_key, language)
    summary_path = os.path.join(output_subdir, f"{base_name}_summary.txt")
    save_transcription(summary_text, summary_path)
    print(f"Summary saved to: {summary_path}")

    # Send the email with the attached files
    send_email(
        subject="Transcription and Summary",
        body="Attached are the complete transcription and summary.",
        to_email="danilo.oficial@gmail.com",
        files=[transcription_path, summary_path],
        config=config
    )
    
    # Remove the temporary audio file and directory
    shutil.rmtree(tmp_subdir)
    print(f"Temporary directory {tmp_subdir} removed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe and summarize the audio from a video.")
    parser.add_argument("video_filename", help="Name of the video file")
    parser.add_argument("language", help="Language of the transcription and summary")
    args = parser.parse_args()
    main(args.video_filename, args.language)
