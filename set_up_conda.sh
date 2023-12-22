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

# Get DI_FILEPATH from hidden secrets.env file
source ./secrets.env

# The name of the conda environment
read -p "Name for conda environment [di]: " conda_name
conda_name=${conda_name:-di}

# Initialise terminal for conda
conda init bash > /dev/null
source ~/.bashrc > /dev/null

# Remove old environment
conda deactivate
conda remove -n "$conda_name" --all || echo "No old $conda_name environment to remove"

# Create new environment 
conda env create --name "$conda_name" --file environment.yaml && echo "New $conda_name environment created"
conda activate "$conda_name" && echo "New $conda_name environment activated"

# Get current conda environment from conda prefix
current_env=(${CONDA_PREFIX//\// })
current_env=${current_env[-1]}

# If in correct environment get med7 model
if [ "$current_env" = "$conda_name" ]; then

    printf '\e[32m%s\e[0m' "Conda environment successfully created. Activate it using 'conda activate $conda_name'."
    echo ""

    yes_or_no "Do you wish to install the edris9 model? Y/n"
    python -m pip install "$DI_FILEPATH/models/en_edris9-1.0.0/dist/en_edris9-1.0.0-py3-none-any.whl" || printf '\e[31m%s\e[0m' "Failed to get edris9 model   " 

    yes_or_no "Do you wish to install the med7 model? Y/n"
    python -m pip install "$DI_FILEPATH/models/en_core_med7_lg-any-py3-none-any.whl" || printf '\e[31m%s\e[0m' "Failed to get med7 model   " 

else
    printf '\e[31m%s\e[0m' "Did not successfully activate $conda_name environment"; echo ""
fi