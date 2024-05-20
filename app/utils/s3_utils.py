"""
import os
import boto3
from botocore.exceptions import NoCredentialsError

def upload_to_s3(file_path, bucket_name, s3_file_name):
    # Uploads a file to an S3 bucket
    localstack_endpoint = os.getenv("LOCALSTACK_ENDPOINT")
    s3 = boto3.client('s3', endpoint_url=localstack_endpoint)
    
    try:
        s3.upload_file(file_path, bucket_name, s3_file_name)
        print(f"Upload Successful: {file_path} to bucket {bucket_name} as {s3_file_name}")
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")

def download_from_s3(bucket_name, s3_key, local_path):
    # Downloads a file from an S3 bucket
    localstack_endpoint = os.getenv("LOCALSTACK_ENDPOINT")
    s3 = boto3.client('s3', endpoint_url=localstack_endpoint)
    
    try:
        s3.download_file(bucket_name, s3_key, local_path)
        print(f"Download Successful: {s3_key} from bucket {bucket_name} to {local_path}")
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")
    except Exception as e:
        print(f"Error downloading file: {e}")
"""