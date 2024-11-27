import subprocess
import dvc.repo
import os
import shutil
import boto3
from botocore.client import Config

class DataVersionTrackerService:
    def __init__(self, repo_path, endpoint_url, access_key, secret_key):
        self.repo_path = repo_path
        self.repo = dvc.repo.Repo(repo_path)
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')
        )

    def init_dvc(self):
        subprocess.run(["dvc", "init"], cwd=self.repo_path, check=True)

    def add_remote(self, bucket: str):
        remote_name = bucket.replace("s3://", "")
        subprocess.run(["dvc", "remote", "add", "-d", remote_name, bucket], cwd=self.repo_path, check=True)


    def download_file(self, bucket, object_name, temp_path):
        self.s3_client.download_file(bucket, object_name, temp_path)

    def add_dataset(self, file_obj, bucket: str, object_name: str):
        # Create a temporary directory
        temp_dir = "/tmp/dvc_temp"
        os.makedirs(temp_dir, exist_ok=True)

        # Define the temporary file path
        temp_path = os.path.join(temp_dir, object_name.split('/')[-1])

        # Upload the file to Minio
        self.s3_client.upload_fileobj(file_obj, bucket, object_name)

        # Add the new remote to DVC
        self.add_remote(bucket)

        # Download the file from Minio to the temporary directory
        self.download_file(bucket, object_name, temp_path)

        # Add the dataset to DVC
        self.repo.add(temp_path)
        self.repo.git.add(f"{temp_path}.dvc")
        self.repo.git.commit(f"Add {temp_path} to DVC")
        self.repo.push()

        # Clean up the temporary file and directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def pull_dataset(self, object_name: str):
        self.repo.pull(object_name)

# Initialize the DataVersionTrackerService
data_version_tracker_service = DataVersionTrackerService(
    repo_path=".",
    endpoint_url='http://localhost:9000',
    access_key='your_access_key',
    secret_key='your_secret_key'
)
data_version_tracker_service.init_dvc()
