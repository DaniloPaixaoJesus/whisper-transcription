"""
import boto3
import json
import os
from botocore.exceptions import NoCredentialsError
from app.services.transcription_service import process_transcription

sqs = boto3.client('sqs', endpoint_url=os.getenv("LOCALSTACK_ENDPOINT"))
s3 = boto3.client('s3', endpoint_url=os.getenv("LOCALSTACK_ENDPOINT"))

def download_video_from_s3(bucket_name, bucket_key, download_path):
    try:
        s3.download_file(bucket_name, bucket_key, download_path)
        print(f"Download Successful: {bucket_key} from bucket {bucket_name} to {download_path}")
    except NoCredentialsError:
        print("Credentials not available")
    except Exception as e:
        print(f"Error downloading file: {e}")

def process_messages():
    queue_url = os.getenv("SQS_QUEUE_URL")
    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )
        if 'Messages' in response:
            for message in response['Messages']:
                receipt_handle = message['ReceiptHandle']
                body = json.loads(message['Body'])
                bucket_name = body['bucket_name']
                bucket_key = body['bucket_key']
                language = body.get('language', 'english')

                unique_id = os.path.splitext(os.path.basename(bucket_key))[0]
                video_path = os.path.join('/tmp', f"{unique_id}.mp4")
                
                download_video_from_s3(bucket_name, bucket_key, video_path)
                
                # Process the transcription
                process_transcription(video_path, language)
                
                # Delete received message from queue
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt_handle
                )
                print(f"Processed and deleted message: {receipt_handle}")

if __name__ == "__main__":
    process_messages()
"""