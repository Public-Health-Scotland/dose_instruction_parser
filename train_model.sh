#!/bin/bash

# Naming log file with today's time and date
today=`date '+%m_%d__%H_%M_%S'`;
filename="logs/train_$today.log"

# Write out config file to log
cat ./config/config/cfg | $filename
cat "\n\n\n" | $filename

# Write out training output to log
python -m spacy train ./config/config.cfg --output ./output --paths.train ./data/train.spacy --paths.dev ./data/dev.spacy | tee $filename