#!/bin/bash

printf '\e[36m%s\e[0m' "Setting up folder structure and conda environment for dose instructions NER"; echo ""

function yes_or_no {
    while true; do
        read -p "$* [y/n]: " yn
        case $yn in
            [Yy]*) return 0  ;;  
            [Nn]*) echo "Aborted" ; exit  1 ;;
        esac
    done
}

yes_or_no "Do you wish to continue? Y/n" 

# The name of the conda environment
read -p "Name for conda environment [med7]: " conda_name
conda_name=${conda_name:-pythondoc}

# Initialise terminal for conda
conda init bash > /dev/null
source ~/.bashrc > /dev/null

# Remove old environment
conda deactivate
yes | conda remove -n "$conda_name" --all || echo "No old $conda_name environment to remove"

# Create new environment 
yes | conda create -n "$conda_name" python=3.9 && echo "New $conda_name environment created"
conda activate "$conda_name" && echo "New $conda_name environment activated"

# Get current conda environment from conda prefix
current_env=(${CONDA_PREFIX//\// })
current_env=${current_env[-1]}

# If in correct environment do installs
if [ "$current_env" = "$conda_name" ]; then
    # Install packages
    yes | conda install spacy && echo "spacy installed"
    yes | conda install pandas && echo "pandas installed"
    yes | conda install jupyter && echo "jupyter installed"
    yes | conda install scikit-learn && echo "scikit-learn installed"

    printf '\e[32m%s\e[0m' "Conda environment successfully created. Activate it using 'conda activate $conda_name'."
    echo ""

    # Get med7 model
    pip install med7/en_core_med7_lg-any-py3-none-any.whl || printf '\e[31m%s\e[0m' "Failed to get med7 model   " 
else
     printf '\e[31m%s\e[0m' "Did not successfully activate $conda_name environment"; echo ""
fi