import subprocess
import whisper
import os
import uuid
import shutil
from openai import OpenAI
from src.config.config import get_config
from src.utils.email_utils import send_email
from src.utils.download_utils import download_video
from src.aws.aws_utils import upload_to_s3, generate_presigned_url, get_aws_clients

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

def save_file_transcription(text, text_path):
    """Saves the transcribed text to a file."""
    with open(text_path, 'w', encoding='utf-8') as file:
        file.write(text)
# CHECK
# https://platform.openai.com/docs/guides/speech-to-text/improving-reliability


def split_text(text, max_tokens):
    """Splits text into smaller chunks based on max_tokens limit."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > max_tokens:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word) + 1
        else:
            current_chunk.append(word)
            current_length += len(word) + 1

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def summarize_text_chunk(chunk, api_key, language):
    """Summarizes a chunk of text using the OpenAI API."""
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Summarize the following text in {language}:\n\n" + chunk,
            }
        ],
        model="gpt-4",
    )
    summary = response.choices[0].message.content
    return summary

def summarize_text(text, api_key, language):
    """Summarizes the text using the OpenAI API by splitting it into smaller chunks."""
    max_tokens = 9000  # Adjust this value based on the token limit
    chunks = split_text(text, max_tokens)
    summaries = []

    for chunk in chunks:
        summary = summarize_text_chunk(chunk, api_key, language)
        summaries.append(summary)

    final_summary = "\n\n".join(summaries)
    return final_summary

def process_transcription(video_filename, language):
    try:
        provider = os.getenv('PROVIDER', 'localstack')
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID', 'test')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        sqs_client, s3_client = get_aws_clients(provider, aws_region, aws_access_key_id, aws_secret_access_key)

        config = get_config()
        open_api_key = config['api_key']
        
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        video_path = os.path.join(app_dir, '', video_filename)
        
        base_name = os.path.splitext(video_filename)[0]
        unique_id = str(uuid.uuid4())

        transcription_filename = f"{base_name}_full_transcription_{unique_id}.txt"
        summary_filename = f"{base_name}_summary_{unique_id}.txt"

        output_transcriptions_dir = os.path.join(app_dir, "results", "transcriptions")
        output_summaries_dir = os.path.join(app_dir, "results", "summaries")
        tmp_dir = os.path.join(app_dir, "tmp")

        os.makedirs(output_transcriptions_dir, exist_ok=True)
        os.makedirs(output_summaries_dir, exist_ok=True)
        os.makedirs(tmp_dir, exist_ok=True)
        
        audio_path = os.path.join(tmp_dir, f"{base_name}_{unique_id}.wav")
        
        # Initialize transcription record in MongoDB
        # init_transcription(unique_id, video_filename, transcription_filename, summary_filename)
        
        # Extract the complete audio from the video
        extract_audio(video_path, audio_path)
        
        # Transcribe the complete audio
        transcribed_text = transcribe_audio(audio_path, language)
        
        # Path to save the complete transcription
        transcription_path = os.path.join(output_transcriptions_dir, transcription_filename)
        save_file_transcription(transcribed_text, transcription_path)
        print(f"Complete transcription saved to: {transcription_path}")
        
        # Generate and save the summary of the transcribed text
        summary_text = summarize_text(transcribed_text, open_api_key, language)
        summary_path = os.path.join(output_summaries_dir, summary_filename)
        save_file_transcription(summary_text, summary_path)
        print(f"Summary saved to: {summary_path}")

        # Upload transcription and summary to S3
        upload_to_s3(s3_client, transcription_path, "transcription-bucket", f"full-transcriptions/{transcription_filename}")
        upload_to_s3(s3_client, summary_path, "transcription-bucket", f"summary-transcriptions/{summary_filename}")

        # Generate pre-signed URLs
        transcription_url = generate_presigned_url(s3_client, "transcription-bucket", f"full-transcriptions/{transcription_filename}")
        summary_url = generate_presigned_url(s3_client, "transcription-bucket", f"summary-transcriptions/{summary_filename}")

       # Send the email with the pre-signed URLs
        email_body = f"Attached are the complete transcription and summary.\n\n" \
                     f"Transcription: {transcription_url}\n" \
                     f"Summary: {summary_url}"
        
        send_email(
            subject="Transcription and Summary",
            body=email_body,
            to_email="danilo.oficial@gmail.com",
            #files=[],
            files=[transcription_path, summary_path],
            config=config
        )
        
        # Update transcription status to FINISHED
        # update_transcription_status(unique_id, "FINISHED")
                
    finally:
        # Remove the temporary audio file
        print(f"Temporary audio file {audio_path} removed.")
        os.remove(transcription_path)
        os.remove(summary_path)
        os.remove(audio_path)
