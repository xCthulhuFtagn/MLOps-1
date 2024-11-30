import subprocess
import dvc.repo
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

        # Check if the repository is already initialized
        path = os.path.join("/".join(self.repo_path.split("/")[:-1]), '.dvc')
        print(path)
        if not os.path.exists(path):
            self._init_dvc()
        # print(f"creating DVC object at {self.repo_path}")
        # self.DVC = dvc.repo.Repo(self.repo_path)
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
        script_path = os.path.join("/".join(self.repo_path.split("/")[:-1]), "bash_scripts/dvc_init.sh")
        os.chmod(script_path, 0o755)
        subprocess.run([script_path], cwd="/".join(self.repo_path.split("/")[:-1]), check=True)

    def add_remote(self, bucket: str):
        print("adding remote")
        remote = bucket.replace("s3://", "")
        print(remote)
        script_path = os.path.join("/".join(self.repo_path.split("/")[:-1]), "bash_scripts/add_remote.sh")
        run_script(script_path, [self.repo_path, bucket, remote, self.endpoint_url, self.access_key, self.secret_key])

    def add_dataset(self, file_obj, bucket: str, object_name: str):
        # Create a temporary directory within the DVC repository
        temp_dir = os.path.join("/".join(self.repo_path.split("/")[:-1]), "datasets")

        # Define the temporary file path
        temp_path = os.path.join(temp_dir, object_name)
        # Check if the bucket exists, create it if it doesn't

        # Upload the file to Minio
        file_data = BytesIO(file_obj.read())
        df = pd.read_csv(file_data)
        print("adding dataset")
        df.to_csv(temp_path)

        if  not self.bucket_exists(bucket):
            self.create_bucket(bucket)

        # Check if the remote already exists
        remote = bucket.replace("s3://", "")
        try:
            result = subprocess.run(["dvc", "remote", "list"], cwd="/".join(self.repo_path.split("/")[:-1]), check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError:
            self.add_remote(bucket)
        else:
            if not any([remote == out for out in result.stdout]):
                self.add_remote(bucket)

        # Add the dataset to DVC
        script_path = os.path.join("/".join(self.repo_path.split("/")[:-1]), "bash_scripts/track_datasets.sh")
        run_script(script_path, [remote, temp_path])

        print("file added, deleting file")
        dir_path = Path(os.path.join("/".join(self.repo_path.split("/")[:-1]), "datasets"))
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
        remote = bucket.replace("s3://", "")
        subprocess.run(
            ['dvc', 'get', '-r', remote, file],
            check=True
        )