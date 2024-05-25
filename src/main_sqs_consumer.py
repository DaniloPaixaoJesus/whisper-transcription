import os
import json
from src.aws.aws_utils import create_boto3_client, get_queue_url, download_file_from_s3, get_aws_clients
from src.services.transcription_service import process_transcription

def handle_message(message, s3_client):
    body = message['Body']
    try:
        message_data_detail = json.loads(body)
        message_data = json.loads(message_data_detail['Message'])

        print(f'Receiving message: {message_data}')
        print('-------------------------------------')
        
        # Verificando todos os campos da mensagem
        for key in ['file-name', 'bucket-name', 'bucket-key', 'transaction-id']:
            if key not in message_data:
                print(f"Missing required field: {key} in message: {message_data}")
                return
        
        file_name = message_data['file-name']
        bucket_name = message_data['bucket-name']
        bucket_key = message_data['bucket-key']
        transaction_id = message_data['transaction-id']

        unique_file_name = f"{os.path.splitext(file_name)[0]}_{transaction_id}{os.path.splitext(file_name)[1]}"
        download_path = os.path.join('src', unique_file_name)
        
        download_file_from_s3(s3_client, bucket_name, bucket_key, download_path)
        
        try:
            process_transcription(unique_file_name, "portuguese")
        finally:
            # Ensure the local file is removed after processing
            if os.path.exists(download_path):
                os.remove(download_path)
                print(f"Deleted local file: {download_path}")
        
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON message: {e}")

def consume_messages(queue_url, sqs_client, s3_client):
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
            handle_message(message, s3_client)
            
            sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
            print("Message deleted.")

if __name__ == "__main__":
    provider = os.getenv('PROVIDER', 'localstack')
    queue_name = os.getenv('QUEUE_NAME', 'transcription-queue')
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID', None)
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY', None)
    aws_region = os.getenv('AWS_REGION', 'us-east-1')

    sqs_client, s3_client = get_aws_clients(provider, aws_region, aws_access_key_id, aws_secret_access_key)

    queue_url = get_queue_url(sqs_client, queue_name)
    
    print(f"Listening to queue: {queue_url}")

    consume_messages(queue_url, sqs_client, s3_client)
