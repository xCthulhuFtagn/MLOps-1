import subprocess
import dvc.repo
import os
import shutil
import boto3
from botocore.client import Config
import git
from git import InvalidGitRepositoryError

class DataVersionTrackerService:
    def __init__(self, repo_path, endpoint_url, access_key, secret_key):
        self.repo_path = repo_path

        # Check if the repository is already initialized
        if not os.path.exists(os.path.join(self.repo_path, '.dvc')):
            self._init_dvc()

        self.repo = dvc.repo.Repo(repo_path)
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')
        )

    def _init_dvc(self):
        subprocess.run(["dvc", "init", "--subdir"], cwd=self.repo_path, check=True)

    def add_remote(self, bucket: str):
        remote = bucket.replace("s3://", "")
        subprocess.run(["dvc", "remote", "add", "-d", bucket, remote], cwd=self.repo_path, check=True)

    def download_file(self, bucket, object_name, temp_path):
        self.s3_client.download_file(bucket, object_name, temp_path)

    def add_dataset(self, file_obj, bucket: str, object_name: str):
        # Create a temporary directory within the DVC repository
        temp_dir = os.path.join(self.repo_path, "tmp/dvc_temp")
        os.makedirs(temp_dir, exist_ok=True)

        # Define the temporary file path
        temp_path = os.path.join(temp_dir, object_name.split('/')[-1])

        # Check if the bucket exists, create it if it doesn't
        if not self.bucket_exists(bucket):
            self.create_bucket(bucket)

        # Upload the file to Minio
        self.s3_client.upload_fileobj(file_obj, bucket, object_name)

        # Check if the remote already exists
        remote = bucket.replace("s3://", "")
        try:
            result = subprocess.run(["dvc", "remote", "list"], cwd=self.repo_path, check=True, capture_output=True, text=True)
            if remote not in result.stdout:
                self.add_remote(bucket)
        except subprocess.CalledProcessError:
            self.add_remote(bucket)

        # Download the file from Minio to the temporary directory
        self.download_file(bucket, object_name, temp_path)

        # Add the dataset to DVC
        self.repo.add(temp_path)
        git_repo = git.Repo(self.repo_path)
        git_repo.git.add(f"{temp_path}.dvc")
        git_repo.git.commit(f"Update {temp_path} in DVC")
        self.repo.push()

        # Clean up the temporary file and directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def create_bucket(self, bucket_name: str):
        self.s3_client.create_bucket(Bucket=bucket_name)

    def bucket_exists(self, bucket_name: str) -> bool:
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
            return True
        except self.s3_client.exceptions.ClientError:
            return False

    def pull_dataset(self, object_name: str):
        self.repo.pull(object_name)