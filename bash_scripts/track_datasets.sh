#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <remote> <dataset_path>"
    exit 1
fi

# Assign arguments to variables
remote=$1
dataset_path=$2

# # Ensure the dataset path is within the DVC project
# if [[ ! "$dataset_path" =~ ^/home/owner/Documents/DEV/MLOps/HW1/ ]]; then
#     echo "Dataset path must be within the DVC project directory."
#     exit 1
# fi

# Add the dataset to DVC
dvc add "$dataset_path"
# git add ../.dvc
# Push the dataset to the specified remote
# git commit -m "Data update for '$bucket'"
# git push
dvc push -r "$remote"

echo "Dataset '$dataset_path' tracked and pushed to remote '$remote' successfully."
