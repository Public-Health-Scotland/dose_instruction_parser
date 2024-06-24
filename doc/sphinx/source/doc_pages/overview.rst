.. _Overview:

Overview
========

This is the documentation for a tool developed at Public Health Scotland to parse
prescription dose instructions.

Background
----------

Dose instructions are pieces of free text that
accompany a prescription, for example "Take 1 tablet every 3 hours" or 
"2 puffs daily via acuhaler".

Because the dose instructions are free text there are many ways of phrasing the 
same core information and this means it is difficult to use them for analysis when
there are a lot of different instructions to process. Additionally, free text can 
include patient-identifiable information like names, emails and addresses. 

By processing the dose instructions we can convert the free text into a structured
output - i.e. a series of columns with different information in them pulled from the 
text. This output is more suitable for analysis and also greatly reduces the chance
of patient-identifiable information being present.

This tool allows you to parse free text dose instructions to the following structured
fields:

===============     ==================================================================
Field               Description
===============     ==================================================================
inputID             ID passed in with dose instruction for bookkeeping 
text                The original free text dose instruction (can be later removed)
form                The form of drug e.g. "tablet", "patch", "injection"
dosageMin           The minimum dosage 
dosageMax           The maximum dosage
frequencyMin        The minimum frequency
frequencyMax        The maximum frequency 
frequencyType       The type of frequency for the dosage e.g. "Hour", "Day", "2 Week"
durationMin         The minimum duration of treatment 
durationMax         The maximum duration of treatment
durationType        The type of duration for dosage e.g. "Day", "Week"
asRequired          True/False: Whether to take as required / as needed
asDirected          True/False: Whether to take as directed
===============     ==================================================================

Here is a piece of sample output:

.. csv-table:: Sample output
   :header-rows: 1

    ,inputID,text,form,dosageMin,dosageMax,frequencyMin,frequencyMax,frequencyType,durationMin,durationMax,durationType,asRequired,asDirected
    0,eDRIS/XXXX-XXXX/example/001,daily 2 caps as directed,capsule,2.0,2.0,1.0,1.0,Day,,,,False,True
    1,eDRIS/XXXX-XXXX/example/002,daily 0.2ml,ml,0.2,0.2,1.0,1.0,Day,,,,False,False
    2,eDRIS/XXXX-XXXX/example/003,two mane + two nocte,,2.0,2.0,2.0,2.0,Day,,,,False,False
    3,eDRIS/XXXX-XXXX/example/004,2 tabs twice daily ,tablet,2.0,2.0,2.0,2.0,Day,,,,False,False
    4,eDRIS/XXXX-XXXX/example/005,take one in the morning and take two at night as directed,,3.0,3.0,1.0,1.0,Day,,,,False,False
    5,eDRIS/XXXX-XXXX/example/006,1 tablet(s) three times daily for pain/inflammation,tablet,1.0,1.0,3.0,3.0,Day,,,,False,False
    6,eDRIS/XXXX-XXXX/example/007,two puffs at night,puff,2.0,2.0,1.0,1.0,Day,,,,False,False
    7,eDRIS/XXXX-XXXX/example/008,0.6mls daily,ml,0.6,0.6,1.0,1.0,Day,,,,False,False
    8,eDRIS/XXXX-XXXX/example/009,to be applied tds prn,,,,3.0,3.0,Day,,,,True,False
    9,eDRIS/XXXX-XXXX/example/010,take 1 tablet for 3 weeks then take 3 tablets for 4 weeks,tablet,1.0,1.0,,,,3.0,3.0,Week,False,False
    10,eDRIS/XXXX-XXXX/example/010,take 1 tablet for 3 weeks then take 3 tablets for 4 weeks,tablet,3.0,3.0,,,,4.0,4.0,Week,False,False
    11,eDRIS/XXXX-XXXX/example/011,one to be taken twice a day  if sleepy do not drive/use machines. avoid alcohol. swallow whole.,,1.0,1.0,2.0,2.0,Day,,,,False,False
    12,eDRIS/XXXX-XXXX/example/012,1 tab take as required,tablet,1.0,1.0,,,,,,,True,False
    13,eDRIS/XXXX-XXXX/example/013,take one daily for allergy,,1.0,1.0,1.0,1.0,Day,,,,False,False
    14,eDRIS/XXXX-XXXX/example/014,one daily when required,,1.0,1.0,1.0,1.0,Day,,,,True,False

Methods
-------

The parsing process consists of three main stages:

#. Pre-process the dose instruction to clean up the free text
#. Use a machine learning Named Entity Recogniser (NER) model to associate key phrases
   in the text with "entities" of interest such as "DOSAGE" and "DURATION"
#. Apply rules to each key phrase to extract structured information

As an example, consider the dose instruction "one/two tabs bid prn". 

===============     ========================
Stage               Output
===============     ========================
(1) Pre-process     1 / 2 tablets bid prn
(2) NER             DOSAGE: "1 / 2", FORM: "tablets", FREQUENCY: "bid", AS_REQUIRED: "prn"    
(3) Rules           StructuredDI(text='one/two tabs bid prn', form='tablet', dosageMin=1.0, dosageMax=2.0, frequencyMin=2.0, frequencyMax=2.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=True, asDirected=False)   
===============     ========================

The whole process is carried out by the :mod:`dose_instruction_parser` package, available on `PyPI <https://pypi.org/>`_.
See :ref:`Installation` and :ref:`Parsing dose instructions` for information on how to get going.

Project layout
--------------

.. code::

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

