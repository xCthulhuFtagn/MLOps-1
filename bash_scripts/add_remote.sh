#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 5 ]; then
    echo "Usage: $0 <repo_path> <bucket> <endpoint_url> <access_key> <secret_key>"
    exit 1
fi

# Assign arguments to variables
repo_path=$1
bucket=$2
endpoint_url=$3
access_key=$4
secret_key=$5


# Get the list of all DVC remotes
REMOTE_LIST=$(dvc remote list)

# Check if the specified remote exists in the list
if echo "$REMOTE_LIST" | grep -qw "$bucket"; then
    echo "The remote '$bucket' already exists."
else
    echo "The remote '$bucket' does not exist. Adding it now."

    # Run the dvc commands to add and configure the remote
    dvc remote add --local "$bucket" s3://"$bucket"
    dvc remote modify --local "$bucket" endpointurl "$endpoint_url"
    dvc remote modify --local "$bucket" access_key_id "$access_key"
    dvc remote modify --local "$bucket" secret_access_key "$secret_key"

    echo "dvc remote add --local '$bucket' s3://'$bucket'"
    echo "dvc remote modify --local '$bucket' endpointurl '$endpoint_url'"
    echo "remote modify --local "$bucket" access_key_id "$access_key""
    echo "remote modify --local "$bucket" secret_access_key "$secret_key""
    echo "Remote '$bucket' added and configured successfully."
fi
