import boto3
import os

def create_boto3_client(service_name, endpoint_url=None, region_name='us-east-1', aws_access_key_id=None, aws_secret_access_key=None):
    if endpoint_url:
        return boto3.client(
            service_name,
            region_name=region_name,
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
    else:
        return boto3.client(
            service_name,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

def get_queue_url(sqs_client, queue_name):
    response = sqs_client.get_queue_url(QueueName=queue_name)
    return response['QueueUrl']

def download_file_from_s3(s3_client, bucket_name, bucket_key, download_path):
    s3_client.download_file(bucket_name, bucket_key, download_path)
    print(f"Downloaded {bucket_key} from bucket {bucket_name} to {download_path}")

def get_aws_clients(provider, region, access_key, secret_key):
    endpoint_url = 'http://localhost:4566' if provider == 'localstack' else None

    sqs_client = create_boto3_client(
        'sqs',
        endpoint_url=endpoint_url,
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    s3_client = create_boto3_client(
        's3',
        endpoint_url=endpoint_url,
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    return sqs_client, s3_client

def upload_to_s3(s3_client, file_path, bucket_name, bucket_key):
    s3_client.upload_file(file_path, bucket_name, bucket_key)
    print(f"Uploaded {file_path} to s3://{bucket_name}/{bucket_key}")

def generate_presigned_url(s3_client, bucket_name, bucket_key, expiration=3600):
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': bucket_key},
        ExpiresIn=expiration
    )
    return url
