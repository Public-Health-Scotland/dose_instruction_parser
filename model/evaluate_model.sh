#!/bin/bash

usage="$(basename "$0") [-h] -- script to evaluate performance of a given model on data/test.spacy

You must provide as an argument the model you want to test.
This can be by name or location 
For example:
./evaluate_model en_core_med7_lg
./evaluate_model output/model-best
"
if [ "$1" == "-h" ]; then
  echo "Usage: $usage"
  exit 0
fi

# Get DI_FILEPATH from hidden secrets.env file
source ../secrets.env

# Naming log file with today's time and date and model name
today=`date '+%m_%d__%H_%M_%S'`;
filename="$DI_FILEPATH/logs/evaluate_${1//\//_}_$today.log"
touch $filename
echo $1 >> $filename

# Check if valid filepath relative to DI_FILEPATH was provided

if [ -d "$DI_FILEPATH/models/$1" ]; then
  mod="$DI_FILEPATH/models/$1"
else
  mod="$1"
fi

python -m spacy evaluate $1 data/test.spacy >> $filename