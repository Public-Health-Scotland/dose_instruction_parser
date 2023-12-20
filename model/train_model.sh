#!/bin/bash

usage="$(basename "$0") [-h] -- script to train model

The model is trained on the data in data/train.spacy and data/dev.spacy
Output is in output/model-best and output/model-last
Logs are found in logs with train prefix and current timestamp.

"
if [ "$1" == "-h" ]; then
  echo "Usage: $usage"
  exit 0
fi

# Get DI_FILEPATH from hidden secrets.env file
source ./secrets.env

# Get today's time and date
today=`date '+%m_%d__%H_%M_%S'`;

# Set output location and logfile
read -p "Name for model output folder ['$today']: " outputname
outputname=${outputname:-'$today'}
modelloc="$DI_FILEPATH/models/$outputname"
if [ -d "$modelloc" ]; then
  echo "Model output folder already exists. Please pick a different name."
  exit 0
fi
mkdir "$modelloc"
filename="$modelloc/logs/train_$outputname.log"

# Write out config file to log
touch "$filename"
cat ./model/config/config.cfg >> "$filename"

# Write out training output to log
python -m spacy train ./model/config/config.cfg --output "$modelloc" --paths.train ./data/train.spacy --paths.dev ./data/dev.spacy >> "$filename"