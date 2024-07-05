# `dose_instruction_parser`: Dose instructions free text parser for Public Health Scotland

Current version: "2024.1002-alpha"

📓 Documentation can be found at https://public-health-scotland.github.io/dose_instruction_parser/

* The `dose_instruction_parser` package is for parsing free text dose instructions which accompany NHS prescriptions.
* It draws upon the [`parsigs`](https://pypi.org/project/parsigs/) package, adapting and expanding the code to the context of data held by Public Health Scotland.
* `dose_instruction_parser` works by first applying a named entity recogniser (NER) model to identify parts of the text corresponding to different entities, and then using rules to extract structured output. 
* The default NER model is named `en_edris9`. This is an extension of the [`med7`](https://www.sciencedirect.com/science/article/abs/pii/S0933365721000798) model, which has the following named entities: form; dosage; frequency; duration; strength; route; drug. `en_edris9` has the additional entities as_directed and as_required, and has been further trained on approximately 7,000 gold standard examples of NHS dose instructions which were manually tagged by analysts at Public Health Scotland.
* `en_edris9` is not currently publicly available. For interested researchers and colleagues in the NHS, please contact the eDRIS team at Public Health Scotland via [phs.edris@phs.scot](mailto:phs.edris@phs.scot). For other users, code to train your own model is available [on GitHub](https://github.com/Public-Health-Scotland/dose_instruction_parser/).

## Contents

1. [File layout](#file-layout)
1. [Setup](#setup)
1. [Usage](#usage)
1. [Development](#development)

## File layout

```
📦dose_instruction_parser
 ┣ 📂dose_instruction_parser                  # source code
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
conda create -n di                        # setup new conda env
conda activate di                         # activate
pip install dose_instruction_parser       # install dose_instruction_parser from PyPI
parse_dose_instructions -h                # get help on parsing dose instructions
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

In the following examples we assume the model `en_edris9` is installed. You can provide your own path to an alternative model with the same nine entities.

### Command line interface

The simplest way to get started is to use the in-built command line interface. This can be accessed by running `parse_dose_instructions` on the command line.

#### A single instruction

A single dose instruction can be supplied using the `-di` argument.

```bash
(di-dev)$ parse_dose_instructions -di "take one tablet daily" -mod en_edris9 

Logging to command line. Use the --logfile argument to set a log file instead.
2024-05-28 07:45:49,803 Checking input and output files
2024-05-28 07:45:49,803 Setting up parser
2024-05-28 07:46:34,205 Parsing single dose instruction

StructuredDI(inputID=None, text='take one tablet daily', form='tablet', dosageMin=1.0, dosageMax=1.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)
```

#### Multiple instructions

Multiple dose instructions can be supplied from file using the `-f` argument, where each line in the text file supplied is a dose instruction. For example, if the file `multiple_dis.txt` contains the following:

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

Where you have a lot of examples to parse you may want to send the output to a file rather than the command line. To do this, specify the output file location with the `-o` argument. If this has **.txt** extension the results will be presented line by line like they would on the command line. If this has **.csv** extension the results will be cast to a data frame with one entry per row.

```bash
(di-dev)$ parse_dose_instructions -f "multiple_dis.txt" -mod en_edris9 -o "out_dis.csv"
```

The contents of `out_dis.csv` is as follows:

```
inputID,text,form,dosageMin,dosageMax,frequencyMin,frequencyMax,frequencyType,durationMin,durationMax,durationType,asRequired,asDirected
0,daily 2 tabs,tablet,2.0,2.0,1.0,1.0,Day,,,,False,False
1,once daily when required,,,,1.0,1.0,Day,,,,True,False
```
> [!NOTE]
> Sometimes a dose instruction really contains more than one instruction within it. 
> In this case the output will be split into multiple outputs, one corresponding
> to each part of the instruction. For example,
> "Take two tablets twice daily for one week then one tablet once daily for two weeks"
> ```python
> $ parse_dose_instructions -di "Take two tablets twice daily for one week then one tablet once daily for two weeks"
>
> Logging to command line. Use the --logfile argument to set a log file instead.
> 2024-06-21 08:35:41,765 Checking input and output files
> 2024-06-21 08:35:41,765 Setting up parser
> 2024-06-21 08:35:59,572 Parsing single dose instruction
>
> StructuredDI(inputID=None, text='Take two tablets twice daily for one week then one tablet once daily for two weeks', form='tablet', dosageMin=2.0, dosageMax=2.0,  frequencyMin=2.0, frequencyMax=2.0, frequencyType='Day', durationMin=1.0, durationMax=1.0, durationType='Week', asRequired=False, asDirected=False)
> StructuredDI(inputID=None, text='Take two tablets twice daily for one week then one tablet once daily for two weeks', form='tablet', dosageMin=1.0, dosageMax=1.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=2.0, durationMax=2.0, durationType='Week', asRequired=False, asDirected=False)
> ```
>


#### Providing input IDs

The `inputID` value helps to keep track of which outputs correspond to which inputs. The default behaviour is:

* For a single dose instruction, set `inputID=None` 
* For multiple dose instructions, number each instruction starting from 0 by the order they appear in the input file

You may want to provide your own values for `inputID`. To do this, provide input dose instructions as a **.csv** file with columns 

* `inputID` specifying the input ID
* `di` specifying the dose instruction

For example, using `test.csv` with the following contents:

```
inputID,di
eDRIS/XXXX-XXXX/example/001,daily 2 caps
eDRIS/XXXX-XXXX/example/002,daily 0.2ml
eDRIS/XXXX-XXXX/example/003,two mane + two nocte
eDRIS/XXXX-XXXX/example/004,2 tabs twice daily increased to 2 tabs three times daily during exacerbation chest symptoms
eDRIS/XXXX-XXXX/example/005,take one in the morning and take two at night as directed
eDRIS/XXXX-XXXX/example/006,1 tablet(s) three times daily for pain/inflammation
eDRIS/XXXX-XXXX/example/007,two puffs at night
eDRIS/XXXX-XXXX/example/008,0.6mls daily
eDRIS/XXXX-XXXX/example/009,to be applied tds-qds
eDRIS/XXXX-XXXX/example/010,take 1 tablet for 3 weeks then take 3 tablets for 4 weeks
eDRIS/XXXX-XXXX/example/011,one to be taken twice a day  if sleepy do not drive/use machines. avoid alcohol. swallow whole.
eDRIS/XXXX-XXXX/example/012,1 tab take as required
eDRIS/XXXX-XXXX/example/013,take one daily for allergy
eDRIS/XXXX-XXXX/example/014,2x5ml spoonfuls with meals
eDRIS/XXXX-XXXX/example/015,one per month
eDRIS/XXXX-XXXX/example/016,1 cappful every four weeks
eDRIS/XXXX-XXXX/example/017,take two every 4-6hrs for pain
eDRIS/XXXX-XXXX/example/018,up to qid prn
eDRIS/XXXX-XXXX/example/019,one or two tabs dissolved in a glass of water at night
eDRIS/XXXX-XXXX/example/020,bid-tid
eDRIS/XXXX-XXXX/example/021,change every 2 weeks
eDRIS/XXXX-XXXX/example/022,take every fortnight
```
yields the corresponding output
```python
inputID,text,form,dosageMin,dosageMax,frequencyMin,frequencyMax,frequencyType,durationMin,durationMax,durationType,asRequired,asDirected
eDRIS/XXXX-XXXX/example/001,daily 2 caps,capsule,2.0,2.0,1.0,1.0,Day,,,,False,False
eDRIS/XXXX-XXXX/example/002,daily 0.2ml,ml,0.2,0.2,1.0,1.0,Day,,,,False,False
eDRIS/XXXX-XXXX/example/003,two mane + two nocte,,2.0,2.0,2.0,2.0,Day,,,,False,False
eDRIS/XXXX-XXXX/example/004,2 tabs twice daily increased to 2 tabs three times daily during exacerbation chest symptoms,tablet,2.0,2.0,5.0,5.0,Day,,,,False,False
eDRIS/XXXX-XXXX/example/005,take one in the morning and take two at night as directed,,3.0,3.0,1.0,1.0,Day,,,,False,False
eDRIS/XXXX-XXXX/example/006,1 tablet(s) three times daily for pain/inflammation,tablet,1.0,1.0,3.0,3.0,Day,,,,False,False
eDRIS/XXXX-XXXX/example/007,two puffs at night,puff,2.0,2.0,1.0,1.0,Day,,,,False,False
eDRIS/XXXX-XXXX/example/008,0.6mls daily,ml,0.6,0.6,1.0,1.0,Day,,,,False,False
eDRIS/XXXX-XXXX/example/009,to be applied tds-qds,,,,3.0,3.0,Day,,,,False,False
eDRIS/XXXX-XXXX/example/010,take 1 tablet for 3 weeks then take 3 tablets for 4 weeks,tablet,1.0,1.0,,,,3.0,3.0,Week,False,False
eDRIS/XXXX-XXXX/example/010,take 1 tablet for 3 weeks then take 3 tablets for 4 weeks,tablet,3.0,3.0,,,,4.0,4.0,Week,False,False
eDRIS/XXXX-XXXX/example/011,one to be taken twice a day  if sleepy do not drive/use machines. avoid alcohol. swallow whole.,,1.0,1.0,2.0,2.0,Day,,,,False,False
eDRIS/XXXX-XXXX/example/012,1 tab take as required,tablet,1.0,1.0,,,,,,,True,False
eDRIS/XXXX-XXXX/example/013,take one daily for allergy,,1.0,1.0,1.0,1.0,Day,,,,False,False
eDRIS/XXXX-XXXX/example/014,2x5ml spoonfuls with meals,ml,10.0,10.0,3.0,3.0,Day,,,,False,False
eDRIS/XXXX-XXXX/example/015,one per month,,1.0,1.0,1.0,1.0,Month,,,,False,False
eDRIS/XXXX-XXXX/example/016,1 cappful every four weeks,capful,1.0,1.0,1.0,1.0,Month,,,,False,False
eDRIS/XXXX-XXXX/example/017,take two every 4-6hrs for pain,,2.0,2.0,1.0,1.0,4 Hour,,,,True,False
eDRIS/XXXX-XXXX/example/018,up to qid prn,,,,0.0,4.0,Day,,,,True,False
eDRIS/XXXX-XXXX/example/019,one or two tabs dissolved in a glass of water at night,tablet,1.0,2.0,1.0,1.0,Day,,,,False,False
eDRIS/XXXX-XXXX/example/020,bid-tid,,,,2.0,3.0,Day,,,,False,False
eDRIS/XXXX-XXXX/example/021,change every 2 weeks,,,,1.0,1.0,2 Week,,,,False,False
eDRIS/XXXX-XXXX/example/022,take every fortnight,,,,1.0,1.0,2 Week,,,,False,False
```

> [!NOTE]
> In this example, `eDRIS/XXXX-XXXX/example/010` has been split up into two
> dose instructions 

### Usage from Python 

For more adaptable usage you can load the package into Python and use it within a script or on the Python prompt. For example, using [iPython](https://pypi.org/project/ipython/):

```python
In [1]: import pandas as pd
   ...: from dose_instruction_parser import parser

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
      0                take one tablet daily   tablet        1.0        1.0           1.0           1.0           Day          NaN          NaN         None       False       False
      1                        two puffs prn     puff        2.0        2.0           NaN           NaN          None          NaN          NaN         None        True       False
      2  one cap after meals for three weeks  capsule        1.0        1.0           3.0           3.0           Day          3.0          3.0         Week       False       False
      3                        4 caplets tid   carpet        4.0        4.0           3.0           3.0           Day          NaN          NaN         None       False       False
```

## Development

1. Please open a new branch for any change and submit a pull request for merging to main
1. If you have ideas for an improvement, or spot a bug, please open an issue
1. Remember to include tests for any changes you might make, where appropriate
