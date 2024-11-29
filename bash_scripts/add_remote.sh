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

# Run the dvc commands
dvc remote add $bucket $remote --local
dvc remote modify $bucket endpointurl $endpoint_url
dvc remote modify --local $bucket access_key_id $access_key
dvc remote modify --local $bucket secret_access_key $secret_key