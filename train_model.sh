#!/bin/bash

python -m spacy train ./config/config.cfg --output ./output --paths.train ./data/train.spacy --paths.dev ./data/dev.spacy