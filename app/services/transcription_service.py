import subprocess
import whisper
import os
import uuid
import shutil
from openai import OpenAI
from app.config.config import get_config
from app.utils.email_utils import send_email
from app.utils.download_utils import download_video
# from app.utils.s3_utils import upload_to_s3
# from app.utils.mongodb_utils import init_transcription, update_transcription_status

def extract_audio(video_path, audio_path):
    """Extracts the complete audio from a video using FFmpeg."""
    if subprocess.run(["ffmpeg", "-version"]).returncode != 0:
        raise EnvironmentError("FFmpeg is not installed or not in the system PATH.")
    
    subprocess.run([
        "ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path,
        "-y"  # Overwrite output files without asking
    ], check=True)

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

def process_transcription(video_filename, language):
    config = get_config()
    api_key = config['api_key']
    
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    video_path = os.path.join(script_dir, '', video_filename)
    
    base_name = os.path.splitext(video_filename)[0]
    unique_id = str(uuid.uuid4())
    transcription_filename = f"{base_name}.txt"
    summary_filename = f"{base_name}_summary.txt"
    output_subdir = os.path.join(script_dir, "", "files", f"{base_name}_{unique_id}")
    tmp_subdir = os.path.join(script_dir, "", "tmp", f"{base_name}_{unique_id}")
    os.makedirs(output_subdir, exist_ok=True)
    os.makedirs(tmp_subdir, exist_ok=True)
    
    audio_path = os.path.join(tmp_subdir, f"{base_name}.wav")
    
    # Initialize transcription record in MongoDB
    # init_transcription(unique_id, video_filename, transcription_filename, summary_filename)
    
    # Extract the complete audio from the video
    extract_audio(video_path, audio_path)
    
    # Transcribe the complete audio
    transcribed_text = transcribe_audio(audio_path, language)
    
    # Path to save the complete transcription
    transcription_path = os.path.join(output_subdir, transcription_filename)
    save_transcription(transcribed_text, transcription_path)
    print(f"Complete transcription saved to: {transcription_path}")
    
    # Upload transcription to S3
    # upload_to_s3(transcription_path, "full-transcriptions", transcription_filename)
    
    # Generate and save the summary of the transcribed text
    summary_text = summarize_text(transcribed_text, api_key, language)
    summary_path = os.path.join(output_subdir, summary_filename)
    save_transcription(summary_text, summary_path)
    print(f"Summary saved to: {summary_path}")

    # Upload summary to S3
    # upload_to_s3(summary_path, "summary-transcriptions", summary_filename)

    # Send the email with the attached files
    send_email(
        subject="Transcription and Summary",
        body="Attached are the complete transcription and summary.",
        to_email="danilo.oficial@gmail.com",
        files=[transcription_path, summary_path],
        config=config
    )
    
    # Update transcription status to FINISHED
    # update_transcription_status(unique_id, "FINISHED")
    
    # Remove the temporary audio file and directory
    shutil.rmtree(tmp_subdir)
    print(f"Temporary directory {tmp_subdir} removed.")










"""
def process_transcription_from_url(url, language):
    config = get_config()
    api_key = config['api_key']
    
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    unique_id = str(uuid.uuid4())
    video_filename = f"downloaded_{unique_id}.mp4"
    video_path = os.path.join(script_dir, "", video_filename)
    
    base_name = os.path.splitext(video_filename)[0]
    transcription_filename = f"{base_name}.txt"
    summary_filename = f"{base_name}_summary.txt"
    output_subdir = os.path.join(script_dir, "", "files", f"{base_name}_{unique_id}")
    tmp_subdir = os.path.join(script_dir, "", "tmp", f"{base_name}_{unique_id}")
    os.makedirs(output_subdir, exist_ok=True)
    os.makedirs(tmp_subdir, exist_ok=True)
    
    # Initialize transcription record in MongoDB
    # init_transcription(unique_id, video_filename, transcription_filename, summary_filename)
    
    # Download the video
    download_video(url, video_path)
    
    audio_path = os.path.join(tmp_subdir, f"{base_name}.wav")
    
    # Extract the complete audio from the video
    extract_audio(video_path, audio_path)
    
    # Transcribe the complete audio
    transcribed_text = transcribe_audio(audio_path, language)
    
    # Path to save the complete transcription
    transcription_path = os.path.join(output_subdir, transcription_filename)
    save_transcription(transcribed_text, transcription_path)
    print(f"Complete transcription saved to: {transcription_path}")
    
    # Upload transcription to S3
    # upload_to_s3(transcription_path, "full-transcriptions", transcription_filename)
    
    # Generate and save the summary of the transcribed text
    summary_text = summarize_text(transcribed_text, api_key, language)
    summary_path = os.path.join(output_subdir, summary_filename)
    save_transcription(summary_text, summary_path)
    print(f"Summary saved to: {summary_path}")

    # Upload summary to S3
    # upload_to_s3(summary_path, "summary-transcriptions", summary_filename)

    # Send the email with the attached files
    send_email(
        subject="Transcription and Summary",
        body="Attached are the complete transcription and summary.",
        to_email="danilo.oficial@gmail.com",
        files=[transcription_path, summary_path],
        config=config
    )
    
    # Update transcription status to FINISHED
    #update_transcription_status(unique_id, "FINISHED")
    
    # Remove the temporary audio file and directory
    shutil.rmtree(tmp_subdir)
    print(f"Temporary directory {tmp_subdir} removed.")
"""