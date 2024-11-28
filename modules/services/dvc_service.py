import subprocess
import dvc.repo
import os
import shutil

class DVCService:
    def __init__(self, repo_path, minio_service):
        self.repo_path = repo_path
        self.repo = dvc.repo.Repo(repo_path)
        self.minio_service = minio_service

    def init_dvc(self):
        subprocess.run(["dvc", "init"], cwd=self.repo_path, check=True)

    def add_remote(self, bucket: str, endpoint_url: str, access_key: str, secret_key: str):
        remote_name = bucket.replace("s3://", "")
        subprocess.run(["dvc", "remote", "add", "-d", remote_name, bucket], cwd=self.repo_path, check=True)
        subprocess.run(["dvc", "remote", "modify", remote_name, "endpointurl", endpoint_url], cwd=self.repo_path, check=True)
        subprocess.run(["dvc", "remote", "modify", remote_name, "access_key_id", access_key], cwd=self.repo_path, check=True)
        subprocess.run(["dvc", "remote", "modify", remote_name, "secret_access_key", secret_key], cwd=self.repo_path, check=True)

    def add_dataset(self, bucket: str, object_name: str, endpoint_url: str, access_key: str, secret_key: str):
        # Create a temporary directory
        temp_dir = "/tmp/dvc_temp"
        os.makedirs(temp_dir, exist_ok=True)

        # Download the file from Minio to the temporary directory
        temp_path = os.path.join(temp_dir, object_name.split('/')[-1])
        self.minio_service.download_file(bucket, object_name, temp_path)

        try:
            # Add the new remote to DVC
            self.add_remote(bucket, endpoint_url, access_key, secret_key)

            # Add the dataset to DVC
            self.repo.add(temp_path)
            self.repo.git.add(f"{temp_path}.dvc")
            self.repo.git.commit(f"Add {temp_path} to DVC")
            self.repo.push()
        finally:
            # Clean up the temporary file and directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def pull_dataset(self, object_name: str):
        self.repo.pull(object_name)
