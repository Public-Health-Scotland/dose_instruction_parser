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

# Naming log file with today's time and date and model name
today=`date '+%m_%d__%H_%M_%S'`;
filename="logs/evaluate_${1//\//_}_$today.log"
touch $filename
echo $1 >> $filename

python -m spacy evaluate $1 data/test.spacy >> $filename