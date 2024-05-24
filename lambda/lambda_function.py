import json
import os
import boto3
import uuid
from urllib.parse import unquote_plus

s3_client = boto3.client('s3', endpoint_url='http://localstack:4566')
sns_client = boto3.client('sns', endpoint_url='http://localstack:4566')
topic_arn = 'arn:aws:sns:us-east-1:000000000000:transcription-topic'

def lambda_handler(event, context):
    for record in event['Records']:
        
        bucket_name = record['s3']['bucket']['name']
        bucket_key = unquote_plus(record['s3']['object']['key'])
        object_size = record['s3']['object']['size']
        event_time = record['eventTime']
        
        # Create message to send to SNS
        message = {
            "bucket-name": bucket_name,
            "bucket-key": bucket_key,
            "size": object_size,
            "event-time": event_time,
            "uuid": str(uuid.uuid4())
        }
        
        message_json = json.dumps(message)
        
        # Publish the message to SNS
        try:
            response = sns_client.publish(
                TopicArn=topic_arn,
                Message=message_json
            )
        except Exception as e:
            print(f"Erro ao publicar mensagem no SNS: {e}")
            raise e
        
        print(f"Mensagem publicada com sucesso no SNS: {message}")

    return {
        'statusCode': 200,
        'body': json.dumps('Processamento concluído com sucesso.')
    }
