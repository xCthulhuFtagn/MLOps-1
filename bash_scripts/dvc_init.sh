#!/bin/bash
# Run the dvc commands
dvc init --subdir
git add .
git commit -m "dvc init"
dvc config core.autostage true