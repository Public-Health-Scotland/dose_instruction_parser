# `di_parser`: Dose instructions free text parser for Public Health Scotland

Current version: "2023.1001-alpha"

📓 Documentation can be found at https://public-health-scotland.github.io/dose_instruction_parser/

* Thie `di_parser` package is for parsing free text dose instructions which accompany NHS prescriptions.
* It draws upon the [`parsigs`](https://pypi.org/project/parsigs/) package, adapting and expanding the code to the context of data held by Public Health Scotland.
* `di_parser` works by first applying a named entity recogniser (NER) model to identify parts of the text corresponding to different entities, and then using rules to extract structured output. 
* The default NER model is named `edris9`. This is an extension of the [`med7`](https://www.sciencedirect.com/science/article/abs/pii/S0933365721000798) model, which has the following named entities: form; dosage; frequency; duration; strength; route; drug. `edris9` has the additional entities as_directed and as_required, and has been further trained on approximately 10,000 gold standard examples of NHS dose instructions which were manually tagged by analysts at Public Health Scotland.
* `edris9` is not currently publicly available. For interested researchers and colleagues in the NHS, please contact the eDRIS team at Public Health Scotland via [phs.edris@phs.scot](mailto:phs.edris@phs.scot). For other users, code to train your own model is available [on GitHub](https://github.com/Public-Health-Scotland/dose_instruction_parser/).

## Contents

1. [File layout](#file-layout)
1. [Setup](#setup)
1. [Usage](#usage)
1. [Development](#development)

## File layout

```
📦dose_instruction_parser
 ┣ 📂di_parser                  # source code
 ┃ ┣ 📂data                     
 ┃ ┃ ┣ 📜keep_words.txt         # key words which won't be spellchecked
 ┃ ┃ ┣ 📜replace_words.csv      # key words to replace 
 ┃ ┃ ┗ 📜__init__.py
 ┃ ┣ 📂tests                    
 ┃ ┃ ┣ 📜conftest.py
 ┃ ┃ ┣ 📜test_dosage.py         
 ┃ ┃ ┣ 📜test_duration.py
 ┃ ┃ ┣ 📜test_frequency.py
 ┃ ┃ ┣ 📜test_parser.py
 ┃ ┃ ┣ 📜test_prepare.py
 ┃ ┃ ┗ 📜__init__.py
 ┃ ┣ 📜di_dosage.py             # parsing dosage tags
 ┃ ┣ 📜di_duration.py           # parsing duration tags
 ┃ ┣ 📜di_frequency.py          # parsing frequency tags
 ┃ ┣ 📜di_prepare.py            # preprocessing 
 ┃ ┣ 📜parser.py                # dose instruction parser
 ┃ ┣ 📜__init__.py  
 ┃ ┗ 📜__main__.py              # parse_dose_instructions command line function
 ┣ 📜.coveragerc
 ┣ 📜LICENSE
 ┣ 📜MANIFEST.in
 ┣ 📜pyproject.toml
 ┗ 📜README.md
```

## Setup

### Basic setup

> [!WARNING]
> This package is 🚧 not yet available 🚧 on PyPI. This functionality is coming soon!

```bash
conda create -n di          # setup new conda env
conda activate di           # activate
pip install di_parser       # install di_parser from PyPI
parse_dose_instructions -h  # get help on parsing dose instructions
```

(Optional) Install the `en_edris9` model. Contact [phs.edris@phs.scot](mailto:phs.edris@phs.scot) for access.

### Development setup

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
5. (Optional) Install the `en_edris9` model. Contact [phs.edris@phs.scot](mailto:phs.edris@phs.scot) for access.

## Usage

> [!TIP]
>   Run `parse_dose_instructions -h` on the command line to get help on parsing dose instructions

In the following examples we assume the model "en_edris9" is installed. You can provide your own path to an alternative model with the same nine entities.

### Command line interface

The simplest way to get started is to use the in-built command line interface. This can be accessed by running `parse_dose_instructions` on the command line.

#### A single instruction

A single dose instruction can be supplied using the **-di** argument.

```bash
(di-dev)$ parse_dose_instructions -di "take one tablet daily" -mod en_edris9 

Logging to command line. Use the --logfile argument to set a log file instead.
2024-05-28 07:45:49,803 Checking input and output files
2024-05-28 07:45:49,803 Setting up parser
2024-05-28 07:46:34,205 Parsing single dose instruction

StructuredDI(inputID=None, text='take one tablet daily', form='tablet', dosageMin=1.0, dosageMax=1.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)
```

#### Multiple instructions

Multiple dose instructions can be supplied from file using the **-f** argument, where each line in the text file supplied is a dose instruction. For example, if the file `multiple_dis.txt` contains the following:

```
daily 2 tabs
once daily when required
```

then you will get the corresponding output:

```bash
(di-dev)$ parse_dose_instructions -f "multiple_dis.txt" -mod en_edris9

Logging to command line. Use the --logfile argument to set a log file instead.
2024-05-28 07:47:56,270 Checking input and output files
2024-05-28 07:47:56,282 Setting up parser
2024-05-28 07:48:18,003 Parsing multiple dose instructions
Parsing dose instructions                                                                                               
Parsed 100%|██████████████████████████████████████| 2/2 [00:00<00:00, 79.78 instructions/s]

StructuredDI(inputID=0, text='daily 2 tabs', form='tablet', dosageMin=2.0, dosageMax=2.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)
StructuredDI(inputID=1, text='once daily when required', form=None, dosageMin=None, dosageMax=None, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=True, asDirected=False)
```

Where you have a lot of examples to parse you may want to send the output to a file rather than the command line. To do this, specify the output file location with the **-o** argument. If this has **.txt** extension the results will be presented line by line like they would on the command line. If this has **.csv** extension the results will be cast to a data frame with one entry per row.

```bash
(di-dev)$ parse_dose_instructions -f "multiple_dis.txt" -mod en_edris9 -o "out_dis.csv"
```

The contents of `out_dis.csv` is as follows:

```
,inputID,text,form,dosageMin,dosageMax,frequencyMin,frequencyMax,frequencyType,durationMin,durationMax,durationType,asRequired,asDirected
0,0,daily 2 tabs,tablet,2.0,2.0,1.0,1.0,Day,,,,False,False
1,1,once daily when required,,,,1.0,1.0,Day,,,,True,False
```

### Usage from Python 

For more adaptable usage you can load the package into Python and use it within a script or on the Python prompt. For example:

```python
In [1]: import pandas as pd
   ...: from di_parser import parser

In [2]: # Create parser
   ...: p = parser.DIParser("en_edris9")

In [3]: # Parse one dose instruction
   ...: p.parse("Take 2 tablets morning and night")
Out[3]: [StructuredDI(inputID=None, text='Take 2 tablets morning and night', form='tablet', dosageMin=2.0, dosageMax=2.0, frequencyMin=2.0, frequencyMax=2.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)]

In [4]: # Parse many dose instructions
   ...: parsed_dis = p.parse_many([
   ...:     "take one tablet daily",
   ...:     "two puffs prn",
   ...:     "one cap after meals for three weeks",
   ...:     "4 caplets tid"
   ...: ])

In [5]: print(parsed_dis)
[StructuredDI(inputID=0, text='take one tablet daily', form='tablet', dosageMin=1.0, dosageMax=1.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False), StructuredDI(inputID=1, text='two puffs prn', form='puff', dosageMin=2.0, dosageMax=2.0, frequencyMin=None, frequencyMax=None, frequencyType=None, durationMin=None, durationMax=None, durationType=None, asRequired=True, asDirected=False), StructuredDI(inputID=2, text='one cap after meals for three weeks', form='capsule', dosageMin=1.0, dosageMax=1.0, frequencyMin=3.0, frequencyMax=3.0, frequencyType='Day', durationMin=3.0, durationMax=3.0, durationType='Week', asRequired=False, asDirected=False), StructuredDI(inputID=3, text='4 caplets tid', form='carpet', dosageMin=4.0, dosageMax=4.0, frequencyMin=3.0, frequencyMax=3.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)]

In [6]: # Convert output to pandas dataframe
   ...: di_df = pd.DataFrame(parsed_dis)

In [7]: print(di_df)
   inputID                                 text     form  dosageMin  dosageMax  frequencyMin  frequencyMax frequencyType  durationMin  durationMax durationType  asRequired  asDirected
0        0                take one tablet daily   tablet        1.0        1.0           1.0           1.0           Day          NaN          NaN         None       False       False
1        1                        two puffs prn     puff        2.0        2.0           NaN           NaN          None          NaN          NaN         None        True       False
2        2  one cap after meals for three weeks  capsule        1.0        1.0           3.0           3.0           Day          3.0          3.0         Week       False       False
3        3                        4 caplets tid   carpet        4.0        4.0           3.0           3.0           Day          NaN          NaN         None       False       False
```

## Development

1. Please open a new branch for any change and submit a pull request for merging to main
1. If you have ideas for an improvement, or spot a bug, please open an issue
1. Remember to include tests for any changes you might make, where appropriate
