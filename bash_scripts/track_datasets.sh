#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <remote> <dataset_path>"
    exit 1
fi

# Assign arguments to variables
remote=$1
dataset_path=$2

# Add the dataset to DVC
dvc add "$dataset_path"
git add "$dataset_path.dvc"
# Push the dataset to the specified remote
git commit -m "Data update for '$bucket'"
git push
dvc push -r "$remote"

echo "Dataset '$dataset_path' tracked and pushed to remote '$bucket' successfully."