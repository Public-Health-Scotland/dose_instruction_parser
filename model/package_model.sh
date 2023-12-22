#!/bin/bash

usage="$(basename "$0") [-h] -- script to package a given model

"
if [ "$1" == "-h" ]; then
  echo "Usage: $usage"
  exit 0
fi

# Get DI_FILEPATH from hidden secrets.env file
source ../secrets.env

# Get info from command line
read -p "Existing model output folder relative to $DI_FILEPATH/models/: " input_dir
input_dir="$DI_FILEPATH/models/$input_dir/model-best"

read -p "Name for model: " pname
read -p "Model version: " pversion

output_dir="$DI_FILEPATH/models"

python -m spacy package "$input_dir" "$output_dir" --build wheel --name "$pname" --version "$pversion"

