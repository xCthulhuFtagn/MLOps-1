import boto3
from botocore.client import Config

class MinioService:
    def __init__(self, endpoint_url, access_key, secret_key):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')
        )

    def upload_fileobj(self, file_obj, bucket, object_name):
        self.s3_client.upload_fileobj(file_obj, bucket, object_name)

    def download_file(self, bucket, object_name, file_path):
        self.s3_client.download_file(bucket, object_name, file_path)