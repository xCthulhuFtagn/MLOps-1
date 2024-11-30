#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 6 ]; then
    echo "Usage: $0 <repo_path> <bucket> <remote> <endpoint_url> <access_key> <secret_key>"
    exit 1
fi

# Assign arguments to variables
repo_path=$1
bucket=$2
remote=$3
endpoint_url=$4
access_key=$5
secret_key=$6

# Change to the repository directory
cd "$repo_path" || { echo "Failed to change directory to $repo_path"; exit 1; }

# Get the list of all DVC remotes
REMOTE_LIST=$(dvc remote list)

# Check if the specified remote exists in the list
if echo "$REMOTE_LIST" | grep -qw "$remote"; then
    echo "The remote '$remote' already exists."
else
    echo "The remote '$remote' does not exist. Adding it now."

    # Run the dvc commands to add and configure the remote
    dvc remote add --local "$remote" s3://"$bucket"
    dvc remote modify --local "$remote" endpointurl "$endpoint_url"
    dvc remote modify --local "$remote" access_key_id "$access_key"
    dvc remote modify --local "$remote" secret_access_key "$secret_key"

    echo "Remote '$remote' added and configured successfully."
fi
