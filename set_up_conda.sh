#!/bin/bash

# Remove old med7 environment
conda init bash
conda deactivate
yes | conda remove -n med7 --all || echo "No old med7 environment to remove"

# Create new med7 environment 
yes | conda create -n med7 python=3.9 && echo "New med7 environment created"
conda init bash
conda activate med7 && echo "New med7 environment activated"

# Get current conda environment from conda prefix
current_env=(${CONDA_PREFIX//\// })
current_env=${current_env[-1]}

# If in correct environment do installs
if [ "$current_env" = "med7" ]; then
    # Install packages
    yes | conda install -U spacy && echo "spacy installed"
    yes | conda install pandas && echo "pandas installed"
    yes | conda install jupyter && echo "jupyter installed"
    yes | conda install scikit-learn && echo "scikit-learn installed"

    # Get med7 model
    pip install med7/en_core_med7_lg-any-py3-none-any.whl || echo "Failed to get med7 model"
else
    echo "Did not successfully activate med7 environment"
fi