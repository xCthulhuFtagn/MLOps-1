import subprocess
import os
import shutil
import boto3
from botocore.client import Config
import git

from io import BytesIO
import pandas as pd
from typing import List
from pathlib import Path

def run_script(script_path: str, script_args: List):
    print(f"running {script_path}")
    os.chmod(script_path, 0o755)
    subprocess.run(
        [script_path] + script_args,
        check=True
    )

class DataVersionTrackerService:
    def __init__(self, repo_path, endpoint_url, access_key, secret_key):
        self.repo_path = repo_path
        self.repo_dir = "/".join(self.repo_path.split("/")[:-1])

        # Check if the repository is already initialized
        if not os.path.exists(self.repo_path):
            self._init_dvc()
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        print("creating s3 client")
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4')
        )

    def _init_dvc(self):
        print("init dvc")
        script_path = os.path.join(self.repo_dir, "bash_scripts/dvc_init.sh")
        os.chmod(script_path, 0o755)
        subprocess.run([script_path], cwd=self.repo_dir, check=True)

    def try_add_remote(self, bucket: str):
        script_path = os.path.join(self.repo_dir, "bash_scripts/add_remote.sh")
        run_script(script_path, [self.repo_path, bucket, self.endpoint_url, self.access_key, self.secret_key])

    def add_dataset(self, file_obj, bucket: str, object_name: str):
        # Create a temporary directory within the DVC repository
        datasets_dir = os.path.join(self.repo_dir, "rest-server/datasets")

        # Define the temporary file path
        temp_path = os.path.join(datasets_dir, object_name)
        # Check if the bucket exists, create it if it doesn't

        # Upload the file to Minio
        file_data = BytesIO(file_obj.read())
        df = pd.read_csv(file_data)
        print("adding dataset")
        df.to_csv(temp_path)

        if  not self.bucket_exists(bucket):
            self.create_bucket(bucket)

        self.try_add_remote(bucket)

        # Add the dataset to DVC
        script_path = os.path.join(self.repo_dir, "bash_scripts/track_datasets.sh")
        run_script(script_path, [bucket, temp_path])

        print("file added, deleting file")
        dir_path = Path(os.path.join(self.repo_dir, "rest-server/datasets"))
        for item in dir_path.iterdir():
            if item.is_file():
                item.unlink()

    def create_bucket(self, bucket_name: str):
        print("creating bucket")
        self.s3_client.create_bucket(Bucket=bucket_name)

    def bucket_exists(self, bucket_name: str) -> bool:
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
            print("Bucket found")
            return True
        except self.s3_client.exceptions.ClientError:
            print("No bucket")
            return False

    def get_dataset(self, bucket: str, file: str):
        print("getting dataset")
        remote = "s3://" + bucket
        subprocess.run(
            ['dvc', 'get', '-r', remote, file],
            check=True
        )