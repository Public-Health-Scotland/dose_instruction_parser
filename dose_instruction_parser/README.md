# Dose instructions free text parser for Public Health Scotland

Current version: "2023.1001-alpha"

* This repository contains code for parsing free text dose instructions which accompany NHS prescriptions.
* It draws upon the [parsigs](https://github.com/royashcenazi/parsigs) package, adapting and expanding the code to the context of data held by Public Health Scotland.
* The parser works by first applying a named entity recogniser (NER) model to identify parts of the text corresponding to different entities, and then using rules to extract structured output. 
* The default model for dose instructions is provisionally named **edris9**. This is an extension of the [med7](https://www.sciencedirect.com/science/article/abs/pii/S0933365721000798) model, which has the following named entities: form, dosage, frequency, duration, strength, route, drug. **edris9** has the additional entities as_directed and as_required, and has been further trained on approximately 10,000 gold standard examples of NHS data which were manually tagged twice over and double-checked.
* **edris9** is not currently publicly available. For interested internal NHS users please contact the eDRIS team at Public Health Scotland. For other users, code to train your own model is available [here]().

## Contents

1. [File layout](#file-layout)
1. [Setup](#setup)
1. [Usage](#usage)
1. [Development](#development)

## File layout

* **data**
    * **keep_words.txt**: words to be ignored by spellchecker when pre-processing dose instructions
    * **replace_words.csv**: mapping of words to substitue during pre-processing
* **docs**: documentation of the package
* **src/di_parser**: source code for the package
    * **__main__.py**: script for command line interface to package
    * **parser.py**: module containing primary parser function
    * **di_dosage.py**: module containing functions to do with dosage rules
    * **di_duration.py**: module containing functions to do with duration rules
    * **di_frequency.py**: module containing functions to do with frequency rules
    * **di_prepare.py**: module containing functions to do with pre-processing rules
* **tests**: tests 

## Setup

### Basic setup

#TODO: Upload package to PyPI so that this actually works!

1. Create new conda environment: `conda create -n di`
1. Activate environment: `conda activate di`
1. Install package: `python -m pip install dose_instruction_parser`
1. Run `parse_dose_instructions -h` on command line and/or get developing

### Development setup

1. Clone repository
1. Create new conda environment: `conda create -n di-dev`
1. Activate environment: `conda activate di-dev`
1. Install package using editable pip install and development dependencies: `python -m pip install -e dose_instruction_parser[dev]`
1. Install the **edris9** model or alternative
1. Run `parse_dose_instructions -h` on command line and/or get developing


## Usage

1. Follow [setup instructions](#setup)
1. Run `parse_dose_instructions -h` on command line to see help for command line functionality

### Example usage

In the following examples we assume the model "en_edris9" is installed. You can provide your own path to an alternative model with the same nine entities.

#### Command line interface

The simplest way to get started is to use the in-built command line interface. This can be accessed by running `parse_dose_instructions` on the command line.

##### A single instruction

A single dose instruction can be supplied using the **-di** argument.

```bash
(di-dev)$ parse_dose_instructions -di "take one tablet daily" -mod en_edris9 

StructuredDI(text='take one tablet daily', form='tablet', dosageMin=1.0, dosageMax=1.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)
```

##### Multiple instructions

Multiple dose instructions can be supplied from file using the **-f** argument, where each line in the text file supplied is a dose instruction. For example, if the file **multiple_dis.txt** contains the following:

```
daily 2 tabs
once daily when required
```

then you will get the corresponding output:

```bash
(di-dev)$ parse_dose_instructions -f "multiple_dis.txt" -mod en_edris9

StructuredDI(text='daily 2 tabs', form='tablet', dosageMin=2.0, dosageMax=2.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)
StructuredDI(text='once daily when required', form=None, dosageMin=1.0, dosageMax=1.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=True, asDirected=False)
```

Where you have a lot of examples to parse you may want to send the output to a file rather than the command line. To do this, specify the output file location with the **-o** argument. If this has **.txt** extension the results will be presented line by line like they would on the command line. If this has **.csv** extension the results will be cast to a data frame with one entry per row.

```bash
(di-dev)$ parse_dose_instructions -f "multiple_dis.txt" -mod en_edris9 -o "out_dis.csv"
```

The contents of **out_dis.csv** is as follows:

```
,text,form,dosageMin,dosageMax,frequencyMin,frequencyMax,frequencyType,durationMin,durationMax,durationType,asRequired,asDirected
0,daily 2 tabs,tablet,2.0,2.0,1.0,1.0,Day,,,,False,False
1,once daily when required,,,,1.0,1.0,Day,,,,True,False
```

### Usage from Python 

For more bespoke usage you can load the package into Python and use it within a script. The script **docs/example.py** is an example of this, pasted below:

```python
import pandas as pd
from di_parser import parser

# Create parser
p = parser.DIParser("en_edris9")

# Parse one dose instruction
p.parse("Take 2 tablets morning and night")

# Parse many dose instructions
parsed_dis = p.parse_many([
    "take one tablet daily",
    "two puffs prn",
    "one cap after meals for three weeks",
    "4 caplets tid"
])

print(parsed_dis)

# Convert output to pandas dataframe
di_df = pd.DataFrame(parsed_dis)

print(di_df)
```

Output:

```
[StructuredDI(text='take one tablet daily', form='tablet', dosageMin=1.0, dosageMax=1.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False), StructuredDI(text='two puffs prn', form='puff', dosageMin=2.0, dosageMax=2.0, frequencyMin=None, frequencyMax=None, frequencyType=None, durationMin=None, durationMax=None, durationType=None, asRequired=True, asDirected=False), StructuredDI(text='one cap after meals for three weeks', form='capsule', dosageMin=1.0, dosageMax=1.0, frequencyMin=3.0, frequencyMax=3.0, frequencyType='Day', durationMin=3.0, durationMax=3.0, durationType='Week', asRequired=False, asDirected=False), StructuredDI(text='4 caplets tid', form='carpet', dosageMin=4.0, dosageMax=4.0, frequencyMin=3.0, frequencyMax=3.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)]

text     form  dosageMin  dosageMax  frequencyMin  frequencyMax frequencyType  durationMin  durationMax durationType  asRequired  asDirected
0                take one tablet daily   tablet        1.0        1.0           1.0           1.0           Day          NaN          NaN         None       False       False
1                        two puffs prn     puff        2.0        2.0           NaN           NaN          None          NaN          NaN         None        True       False
2  one cap after meals for three weeks  capsule        1.0        1.0           3.0           3.0           Day          3.0          3.0         Week       False       False
3                        4 caplets tid   carpet        4.0        4.0           3.0           3.0           Day          NaN          NaN         None       False       False
```

## Development

1. Please open a new branch for any change and submit a pull request for merging to main
1. If you have ideas for an improvement, or spot a bug, please open an issue
1. Remember to include tests for any changes you might make, where appropriate