<div align="center">
  <img src="doc/sphinx/source/_static/phs-logo.png" height=100>
</div>

![Build status](https://github.com/Public-Health-Scotland/dose_instruction_parser/actions/workflows/tests.yml/badge.svg)
![Code Coverage](https://img.shields.io/badge/Code%20Coverage-94%25-success?style=flat)
[![GitHub issues](https://img.shields.io/github/issues/Public-Health-Scotland/dose_instruction_parser)](https://github.com/Public-Health-Scotland/dose_instruction_parser/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/Public-Health-Scotland/dose_instruction_parser)](https://github.com/Public-Health-Scotland/dose_instruction_parser/commits/main)

# 💊📝 Dose instructions parser 💊📝

> [!WARNING]
> This project is a 🚧 work in progress 🚧. We do not recommend you use the code at this stage. Please contact [phs.edris@phs.scot](mailto:phs.edris@phs.scot) with any queries. 

> [!TIP]
> 📓 Documentation can be found at https://public-health-scotland.github.io/dose_instruction_parser/

<img alt="Example prescription with dose instruction '125mg three times daily' source: BNF" align="left" style="width: 400px; margin:18px" src="doc/sphinx/source/_static/bnf_prescription_example.png">

This repository contains code for parsing *dose instructions*. These are short pieces of 
free text written on prescriptions to tell patients how to use their medication. An example
prescription is shown to the left, with the dose instruction "*125mg three times daily*" highlighted.

The code is written primarily in Python and consists of two main phases:

1. *Named entity recognition (NER)* using a model trained via the [`spacy`](https://spacy.io)  package to identify phrases linked to key information, e.g. "*three times daily*" is tagged as `FREQUENCY`
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
> Code in the `model` folder was used to generate a model for **1.** called `edris9`. This is based on the [med7](https://www.sciencedirect.com/science/article/abs/pii/S0933365721000798) [model](https://huggingface.co/kormilitzin/en_core_med7_lg/tree/main), further trained using examples specific to the prescribing information system data held by Public Health Scotland. Due to information governance, the `edris9` model is not public. Please contact [phs.edris@phs.scot](mailto:phs.edris@phs.scot) if you wish to use the model.

> [!IMPORTANT]
> The code for the `di_parser` package is based on the [`parsigs`](https://github.com/royashcenazi/parsigs) package. We recommend you have a look at this package as it may be better suited to your needs.

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
 ┃ ┃ ┃ ┃ ┗ 📂di_parser
 ┃ ┃ ┃ ┣ 📂_static
 ┣ 📂dose_instruction_parser   # package for parsing dose instructions
 ┃ ┣ 📂di_parser
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

If you are a PHS analyst and just want to parse dose instructions you can do this directly using R. You will need to follow the dose instructions SOP, which you can obtain from colleagues in eDRIS.

If you are an analyst wishing to develop the model or code, see below.

### 💊 I just want to parse dose instructions
> [!WARNING]
> This package is 🚧 not yet available 🚧 on PyPI. This functionality is coming soon!

```bash
conda create -n di          # setup new conda env
conda activate di           # activate
pip install di_parser       # install di_parser from PyPI
parse_dose_instructions -h  # get help on parsing dose instructions
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
    to set up the conda environment (default name **model**)
1. Activate environment with e.g. 
    ```bash
    conda activate model
    ```

### 📦 I want to develop the `di_parser` package 

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
4. Install package using editable pip install and development dependencies: 
    ```bash
    python -m pip install -e dose_instruction_parser[dev]
    ```
  > [!IMPORTANT]
  > Make sure you run this from the top directory of the repository
5. Get developing! 

## 🔍 Further information

* 📓 Check out the documentation at https://public-health-scotland.github.io/dose_instruction_parser/ for more information on how to use and develop the code
* 💊 See the README in the `dose_instruction_parser` folder for information on the `di_parser` package
* 🔧 See the README in the `doc/sphinx` folder for information on adding to the documentation
* 👷 See the README in the `.github/workflows` folder for information on GitHub workflows for this repository
* 📧 Contact [phs.edris@phs.scot](mailto:phs.edris@phs.scot) with any queries

