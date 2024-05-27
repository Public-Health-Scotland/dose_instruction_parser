<div align="center">
  <img src="doc/sphinx/source/_static/phs-logo.png" height=100>
</div>

![Build status](https://github.com/Public-Health-Scotland/dose_instruction_parser/actions/workflows/tests.yml/badge.svg)
![Code Coverage](https://img.shields.io/badge/Code%20Coverage-94%25-success?style=flat)

# Dose instructions free text model and parser
> [!WARNING]
> This project is a work in progress. We do not recommend you use the code at this stage. Please contact [phs.edris@phs.scot](mailto:phs.edris@phs.scot) with any queries.

> [!TIP]
> Documentation can be found at https://public-health-scotland.github.io/dose_instruction_parser/

<img alt="Example prescription with dose instruction '125mg three times daily' source: BNF" align="left" style="width: 400px; margin:18px" src="doc/sphinx/source/_static/bnf_prescription_example.png">

This repository contains code for parsing *dose instructions*. These are short pieces of 
free text written on prescriptions to tell patients how to use their medication. An example
prescription is shown to the left, with the dose instruction "*125mg three times daily*" highlighted.

The code is written primarily in Python and consists of two main phases:

1. *Named entity recognition (NER)* using a model trained via the [spacy](https://spacy.io)  package to identify phrases linked to key information, e.g. "*three times daily*" is tagged as **FREQUENCY**
2. Rules to extract structured output from the recognised entities, e.g. 
   ```python
   frequencyMin=3.0
   frequencyMax=3.0
   frequencyType='Day'
   ```

Code to create the model (**1.**) can be found in the **model** folder.
Code to parse dose instructions given a model (**2.**) can be found in the **dose_instruction_parser** folder.

When the code is installed, dose instructions can be parsed from the command line in the following way:

<br clear="left"/>

```py
(di-dev)$ parse_dose_instructions -di "125mg three times daily" -mod "en_edris9"

StructuredDI(inputID=None, text='125mg three times daily', form='mg', dosageMin=125.0, dosageMax=125.0, frequencyMin=3.0, frequencyMax=3.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)
```

> [!NOTE]
> Code in the **model** folder was used to generate a model for **1.** called **edris9**. This is based on the [med7](https://www.sciencedirect.com/science/article/abs/pii/S0933365721000798) [model](https://huggingface.co/kormilitzin/en_core_med7_lg/tree/main), further trained using examples specific to the prescribing information system data held by Public Health Scotland. Due to information governance, the **edris9** model is not public. Please contact [phs.edris@phs.scot](mailto:phs.edris@phs.scot) if you wish to use the model.

## Contents

1. [File layout](#file-layout)
1. [Setup](#setup)
1. [How to train a model](#how-to-train-a-model)
1. [How to parse dose instructions](#how-to-parse-dose-instructions)

## File layout

```
📦dose_instructions_parser
 ┣ 📂.github
 ┃ ┣ 📂workflows                
 ┣ 📂coverage                  # code coverage information 
 ┣ 📂doc                       # documentation
 ┃ ┣ 📂examples                # -- example scripts
 ┃ ┗ 📂sphinx                  # -- source behind github pages docs
 ┃ ┃ ┣ 📂source
 ┃ ┃ ┃ ┣ 📂doc_pages
 ┃ ┃ ┃ ┣ 📂modules
 ┃ ┃ ┃ ┃ ┗ 📂di_parser
 ┃ ┃ ┃ ┣ 📂_static
 ┣ 📂dose_instruction_parser   # package for parsing dose instructions
 ┃ ┣ 📂di_parser
 ┃ ┃ ┣ 📂data
 ┃ ┃ ┣ 📂tests
 ┣ 📂model                     # code for creating NER model
 ┃ ┣ 📂config                  # -- model configuration 
 ┃ ┣ 📂data                    # -- processed .spacy data created here
 ┃ ┣ 📂preprocess              # -- code for pre-processing training data         
 ┃ ┃ ┣ 📂processed             # ---- intermediate processing carried out here
 ┗ ┗ ┗ 📂tagged                # ---- put tagged .json training data here
```

## Setup

### Model development set up

1. Clone repository
1. Obtain **secrets.env** file from colleagues which defines environment variable **DI_FILEPATH**. If you are working outwith Public Health Scotland you can define your own filepath and start the process from scratch.
1. Run  `./set_up_conda.sh` to set up the conda environment (default name **di**)
1. Activate environment with e.g. `conda activate di`

### Package development set up

1. Clone repository
1. Obtain **secrets.env** file from colleagues which defines environment variable **DI_FILEPATH**. If you are working outwith Public Health Scotland you can define your own filepath and start the process from scratch.
1. Create new conda environment: `conda create -n di-dev`
1. Activate environment: `conda activate di-dev`
1. Install package using editable pip install and development dependencies: `python -m pip install -e dose_instruction_parser[dev]`
1. Run `parse_dose_instructions` on command line and/or get developing

## How to train a model

1. Follow [model development setup](#model-development-set-up)
1. Go to **model** folder
1. Tag data using desktop [NER annotator tool](https://tecoholic.github.io/ner-annotator/) 
1. Copy output to **preprocess/tagged** as .json. Only put files here which you want to train the model on.
1. Run **preprocess/1-json_to_dat.py**. This takes the tagged data and crosschecks all unique dose instructions against the different tags which were given to them. Any where all tags agree are outputted to **preprocess/processed/crosschecked_data.dat**. Those where tags conflict are outputted to **preprocess/processed/conflicting_data.dat**
1. Make a copy of **conflicting_data.dat** and save as **resolved_data.dat**. Remove the instances of tags you don't want.
1. Run **preprocess/2-dat_to_spacy.py**. This loads in the crosschecked data and resolved data and converts to spacy format. Output is saved in **model/data**
1. Check the config file: **config/config.cfg**
1. Train model using `./train_model.sh`. Takes about 3 hours to run ~2k examples
1. Model results are saved at the **DI_FILEPATH**. There is a best fit model (model-best) and also the last model tested (model-last).
1. Evaluate your model results based on precision, recall and F-score using `./evalute_model.sh`. Output at **DI_FILEPATH** in **logs**.
1. You can compare and visualise model results by adapting the python script **compare_models.py**
1. Convert your model to a package by running `./package_model.sh`
1. Install your model using pip and specifying the path to the model

## How to parse dose instructions

See the **README.md** in **dose_instruction_parser** for information on parsing dose instructions and developing the parser code.
