<div align="center">
  <img src="doc/sphinx/source/_static/phs-logo.png" height=100>
</div><br>

![Build status](https://github.com/Public-Health-Scotland/dose_instruction_parser/actions/workflows/tests.yml/badge.svg)
![Code Coverage](https://img.shields.io/badge/Code%20Coverage-94%25-success?style=flat)
[![GitHub issues](https://img.shields.io/github/issues/Public-Health-Scotland/dose_instruction_parser)](https://github.com/Public-Health-Scotland/dose_instruction_parser/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/Public-Health-Scotland/dose_instruction_parser)](https://github.com/Public-Health-Scotland/dose_instruction_parser/commits/main)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/Public-Health-Scotland/dose_instruction_parser)](https://github.com/Public-Health-Scotland/dose_instruction_parser/releases/latest)

# 💊📝 Dose instructions parser 💊📝

> [!WARNING]
> This project is a 🚧 work in progress 🚧, please use the code with caution. Please contact [phs.edris@phs.scot](mailto:phs.edris@phs.scot) with any queries. 

> [!NOTE]
> 📓 Documentation can be found at https://public-health-scotland.github.io/dose_instruction_parser/
> 
> 📦 `dose_instruction_parser` package is available on PyPI at https://pypi.org/project/dose-instruction-parser/


This repository contains code for parsing *dose instructions*. These are short pieces of 
free text written on prescriptions to tell patients how to use their medication. An example
prescription is shown to the below, with the dose instruction "**125mg three times daily**" highlighted.

<img alt="Example prescription with dose instruction '125mg three times daily' source: BNF" style="width: 400px; display: block; margin-left: auto; margin-right: auto" src="doc/sphinx/source/_static/bnf_prescription_example.png">
<br clear="left"/>

The code is written primarily in Python and consists of two main phases:

1. *Named entity recognition (NER)* using a model trained via the [`spacy`](https://spacy.io)  package to identify phrases linked to key information, e.g. 

<div style="width: 100%;">
  <img src="doc/sphinx/source/_static/tag_example.svg" style="width: 100%;" alt="Click to see the source">
</div>

2. Extract structured output from the recognised entities using a series of rules, e.g. 
   ```python
   ...
   form="mg"
   dosageMin=125.0
   dosageMax=125.0
   frequencyMin=3.0
   frequencyMax=3.0
   frequencyType='Day'
   ...
   ```

Code to create the model (**1.**) can be found in the **model** folder.
Code to parse dose instructions given a model (**2.**) can be found in the **dose_instruction_parser** folder.

When the code is installed, dose instructions can be parsed from the command line in the following way (for more information see the [documentation](https://public-health-scotland.github.io/dose_instruction_parser/)):


```py
$ parse_dose_instructions -di "125mg three times daily" -mod "en_edris9"

Logging to command line. Use the --logfile argument to set a log file instead.
2024-05-28 07:45:49,803 Checking input and output files
2024-05-28 07:45:49,803 Setting up parser
2024-05-28 07:46:34,205 Parsing single dose instruction

StructuredDI(inputID=None, text='125mg three times daily', form='mg', dosageMin=125.0, dosageMax=125.0, frequencyMin=3.0, frequencyMax=3.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)
```

> [!NOTE]
> Code in the `model` folder was used to generate a model for **1.** called `edris9`. This is based on the [med7](https://www.sciencedirect.com/science/article/abs/pii/S0933365721000798) [model](https://huggingface.co/kormilitzin/en_core_med7_lg/tree/main), further trained using examples specific to the prescribing information system data held by Public Health Scotland. Due to information governance, the `edris9` model is not public. Please contact [phs.edris@phs.scot](mailto:phs.edris@phs.scot) if you wish to use the model.

> [!IMPORTANT]
> The code for the `dose_instruction_parser` package is based on the [`parsigs`](https://github.com/royashcenazi/parsigs) package. We recommend you have a look at this package if you are not using NHS prescribing data and/or are interested in different structural output. 

## Contents

1. [📁 Folder structure](#-folder-structure)
1. [💿 Installation and Setup](#-installation-and-setup)
1. [🔍 Further information](#-further-information)

## 📁 Folder structure

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
 ┃ ┃ ┃ ┃ ┗ 📂dose_instruction_parser
 ┃ ┃ ┃ ┣ 📂_static
 ┣ 📂dose_instruction_parser   # package for parsing dose instructions
 ┃ ┣ 📂dose_instruction_parser
 ┃ ┃ ┣ 📂data
 ┃ ┃ ┣ 📂tests
 ┣ 📂model                     # code for creating NER model
 ┃ ┣ 📂config                  # -- model configuration 
 ┃ ┣ 📂data                    # -- processed .spacy data created here
 ┃ ┣ 📂preprocess              # -- code for pre-processing training     
 ┃ ┃ ┣ 📂processed             # ---- intermediate processing carried out here
 ┃ ┃ ┣ 📂tagged                # ---- put tagged .json training data here
 ┗ ┗ 📂setup                   # -- script for setting up conda for model development
```

## 💿 Installation and setup

There are several different ways to set up the project. Please choose the one which is right for you.

### 📈 I am a PHS analyst 

If you are a PHS analyst and just want to parse dose instructions you can do this directly using R. You will need to follow the internal dose instructions SOP, which you can obtain from colleagues in eDRIS.

If you are an analyst wishing to develop the model or code, see below.

### 💊 I just want to parse dose instructions

> [!IMPORTANT]
> This requires a model (e.g. `edris9`) to be installed

```bash
conda create -n di                                  # setup new conda env
conda activate di                                   # activate
python -m pip install dose_instruction_parser       # install dose_instruction_parser from PyPI
parse_dose_instructions -h                          # get help on parsing dose instructions
```

### ⏳ I want to develop a model

1.  Clone this repository
1.  Add a file called called `secrets.env` in the top level of the cloned    repository with the following contents:

    ```bash
    export DI_FILEPATH="</path/to/model/folder>"
    ```

    This sets the environment variable `DI_FILEPATH` where the code will read/write models. If you are working within Public Health Scotland please contact
    [phs.edris@phs.scot](mailto:phs.edris@phs.scot) to receive the filepath. 
1. Run  
    ```bash
    cd model/setup/
    source ./set_up_conda.sh
    ``` 
    to set up the conda environment specifically for model development (default name **model**)
1. Activate environment with e.g. 
    ```bash
    conda activate model
    ```

### 📦 I want to develop the `dose_instruction_parser` package 


1.  Clone this repository
2.  Add a file called called `secrets.env` in the top level of the cloned    repository with the following contents:

    ```bash
    export DI_FILEPATH="</path/to/model/folder>"
    ```

    This sets the environment variable `DI_FILEPATH` where the code will read/write models. If you are working within Public Health Scotland please contact
    [phs.edris@phs.scot](mailto:phs.edris@phs.scot) to receive the filepath. 
3. Create new conda environment and activate: 
    ```bash
    conda create -n di-dev
    conda activate di-dev
    ```
4. Install package in editable mode so that when you change the code the package updates accordingly:
    ```bash
    python -m pip install --editable dose_instruction_parser[dev]
    ```
  > [!IMPORTANT]
  > Make sure you run this from the top directory of the repository
5. Get developing! 

## 🔍 Further information

* 📓 Check out the documentation at https://public-health-scotland.github.io/dose_instruction_parser/ for more information on how to use and develop the code
* 💊 See the README in the `dose_instruction_parser` folder for information on the `dose_instruction_parser` package
* 🔧 See the README in the `doc/sphinx` folder for information on adding to the documentation
* 👷 See the README in the `.github/workflows` folder for information on GitHub workflows for this repository
* 📧 Contact [phs.edris@phs.scot](mailto:phs.edris@phs.scot) with any queries

