#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <remote> <file>"
    exit 1
fi

remote=$1
file=$2

# Run the dvc commands
dvc add file
dvc push -r $remote