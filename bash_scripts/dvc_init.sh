#!/bin/bash
# Run the dvc commands
dvc init #--subdir
echo 'dvc init worked'
git add .dvc
git commit -m "dvc init"
git push
# dvc config core.autostage true