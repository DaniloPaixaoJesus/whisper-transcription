import os
import boto3
import time
import json
from src.services.transcription_service import process_transcription


def create_sqs_client(endpoint_url=None, region_name='us-east-1', aws_access_key_id=None, aws_secret_access_key=None):
    return boto3.client(
        'sqs',
        region_name=region_name,
        endpoint_url=endpoint_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

def get_queue_url(sqs_client, queue_name):
    response = sqs_client.get_queue_url(QueueName=queue_name)
    return response['QueueUrl']

def consume_messages(queue_url, sqs_client):
    while True:
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )
        messages = response.get('Messages', [])
        if not messages:
            print("No messages in the queue.")
            continue
        for message in messages:
            body = message['Body']
            try:
                message_data = json.loads(body)
                video_filename = message_data.get('video_filename')
                language = message_data.get('language')
                print(f"Received message: video_filename={video_filename}, language={language}")
                # Aqui você pode chamar a função process_transcription ou outra função para processar o vídeo
                # process_transcription(video_filename, language)
                # Process the transcription
                process_transcription(video_filename, language)
                
            except json.JSONDecodeError:
                print("Error decoding JSON message")
            
            sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
            print("Message deleted.")

if __name__ == "__main__":
    provider = os.getenv('PROVIDER', 'localstack')
    queue_name = os.getenv('QUEUE_NAME', 'transcription-queue')
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID', 'test')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')

    if provider == 'localstack':
        sqs_client = create_sqs_client(
            endpoint_url='http://localhost:4566',
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
    else:  # AWS
        sqs_client = create_sqs_client(
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    queue_url = get_queue_url(sqs_client, queue_name)
    print(f"Listening to queue: {queue_url}")
    consume_messages(queue_url, sqs_client)
