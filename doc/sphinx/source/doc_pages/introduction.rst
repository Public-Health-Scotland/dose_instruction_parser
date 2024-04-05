Introduction
============

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

1. Pre-process the dose instruction to clean up the free text
2. Use a machine learning Named Entity Recogniser (NER) model to associate key phrases
   in the text with "entities" of interest such as "DOSAGE" and "DURATION"
3. Apply rules to each key phrase to extract structured information

As an example, consider the dose instruction "one/two tabs bid prn". 

===============     ========================
Stage               Output
===============     ========================
(1) Pre-process     1 / 2 tablets bid prn
(2) NER             DOSAGE: "1 / 2", FORM: "tablets", FREQUENCY: "bid", AS_REQUIRED: "prn"    
(3) Rules           StructuredDI(text='one/two tabs bid prn', form='tablet', dosageMin=1.0, dosageMax=2.0, frequencyMin=2.0, frequencyMax=2.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=True, asDirected=False)   
===============     ========================

The whole process is carried out by the :mod:`di_parser` package, available on `PyPI <https://pypi.org/>`_.
See Installation_, Quickstart_ and `Parsing dose instructions`_ for information on how to get going.


Pre-processing
~~~~~~~~~~~~~~

Pre-processing functions can be found in the :mod:`di_parser.di_prepare` module.
Several operations are performed on the input text to get it ready for 
the NER model:

1. All parentheses are replaced with a blank space
2. Hyphens ("-") and slashes ("/" and "\") and replaced with a blank space
3. Certain keywords are replaced with alternatives e.g. "qad" -> "every other day". 
   These combinations are listed in :mod:`di_parser.data.replace_words`
4. Spelling is corrected using the `pyspellchecker <https://pypi.org/project/pyspellchecker/>`_ package.
   Certain keywords are not corrected. These are listed in :mod:`di_parser.data.keep_words`
5. Number-words are converted to numbers using the `word2number <https://pypi.org/project/word2number/>`_ package,
   e.g. "two" -> "2"; "half" -> "0.5".
6. Blank spaces are added around numbers 
   e.g. "2x30ml" -> " 2 x 30 ml"
7. Extra spaces between words are removed
8. Leading and trailing whitespace is removed

For example, pre-processing would have the following results:

===============================  ================================
Input                            Output
===============================  ================================
take two tabs MORNING and nghit  take 2 tablets morning and night
half cap qh                      0.5 capsule every hour
two puff(s)                      2 puff
one/two with meals               1 / 2 with meals
===============================  ================================

Named Entity Recognition (NER)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The next step in processing is to identify parts of the instruction
associated with each named entity. This is done using a neural network, 
which is a type of machine learning
model. The neural network is implemented via the `spacy <https://spacy.io/>`_ package.

At Public Health Scotland we have trained a model called **edris9** to do NER. Due to data 
protection concerns the model is not currently publicly available. Please contact the eDRIS team 
on `phs.edris@phs.scot <mailto:phs.edris@phs.scot>`_ to enquire about access.

In the **edris9** model there are nine named entities:

* DOSAGE
* FORM 
* ROUTE
* DRUG 
* STRENGTH
* FREQUENCY
* DURATION
* AS_REQUIRED
* AS_DIRECTED

**edris9** was based on the `med 7 <https://github.com/kormilitzin/med7>`_ model with the addition of
two entities: "AS_REQUIRED" and "AS_DIRECTED".

Preparing for training
^^^^^^^^^^^^^^^^^^^^^^

The code used to prepare and train the model can be found in the **model** folder. To generate **edris9**,
the **med7** model was further trained on approximately 7,000 gold-standard tagged dose instructions. 
Each instruction was separately tagged by two eDRIS analysts, and any tagged instructions which didn't match
identically were manually resolved by the team. This was to ensure high quality input data. 

There are three steps to prepare raw examples of dose instructions for training:

1. Tag entities by hand 
2. Optional: cross check tagging if each example has been tagged twice by different people
3. Convert tagged examples to .spacy format

Tag entities by hand
''''''''''''''''''''

The tagging process was carried out using the desktop version of `NER Annotator for Spacy <https://github.com/tecoholic/ner-annotator>`_,
which outputs tagged dose instructions in .json format. An example of a .json file with just two tagged dose instructions is:

.. code:: 

   {"classes":["DOSE","FORM","FREQUENCY","DURATION","ROUTE","DRUG","STRENGTH","AS_DIRECTED","AS_REQUIRED"],
   "annotations":[
      ["1 tab in the morning",{"entities":[[0,1,"DOSE"],[2,5,"FORM"],[6,20,"FREQUENCY"]]}],
      ["1 cap 4 times daily",{"entities":[[0,1,"DOSE"],[2,5,"FORM"],[6,19,"FREQUENCY"]]}]
      ]
   }

For more information see TrainingModel_.

Cross check tagging
'''''''''''''''''''

Cross-checking tagging is done using the **1-json_to_dat.py** script in **model/preprocess/**. Tagged examples
must first be copied to **model/preprocess/tagged/**, and must be in .json format. The script
outputs two **.dat** files to **model/preprocess/processed**:

* **crosschecked_data\{time\}.dat** are examples where both taggers agree on all tags
* **conflicting_data_\{time\}.dat** are examples where taggers disagree on one or more tags

You must then manually open up **conflicting_data_\{time\}.dat** and resolve any conflicts, before
saving out as **resolved_data_\{time\}.dat**.

Convert tagged examples to .spacy format
''''''''''''''''''''''''''''''''''''''''

The crosschecked and resolved data are converted to **.spacy** format by **2-dat_to_spacy.py**.
The instances are shuffled and split into train; test; dev data with a 8:1:1 split. This can be changed
by editing the file. Data are saved out to **model/data** in **.spacy** format.

Training
^^^^^^^^

Before training the model you need to define a **DI_FILEPATH** environment variable, which is the 
file path you will save and load models from. You should save this variable in a **secrets.env** file
in the **dose_instructions_ner** folder. The contents of **secrets.env** should be:

.. code::

   export DI_FILEPATH="/path/to/folder/"

You can train the model by opening a Terminal and running:

.. code::
   
   cd model
   ./train_model.sh

You will be taken through interactive steps in the Terminal to set the model name.
The model parameters are defined in **model/config/config.cfg**, which is a `spacy 
configuration file <https://spacy.io/usage/training/#config>`_. There are a few important
things to note about the contents:

* The path to the training data is set under **\[paths\]**
* The **med7** model is used as a starting point for training. This is set
  using the **source** parameters under **\[components\]** and also in **\[initialize.before_init\]**.
* The hyperparameters for the neural network are set under **\[training.optimizer\]**.
  The `Adam <https://arxiv.org/abs/1412.6980>`_ optimiser is the default.
* **\[training.score_weights\]** details the relative importance of different measure
  in evaluating training performance. Available measures are precision, recall and 
  `F-score <https://en.wikipedia.org/wiki/F-score>`_ (the harmonic mean of precision and recall). 

Model training logs will be saved to a **logs** folder within your **DI_FILEPATH**. Training typically
takes a few hours.  

Model performance
^^^^^^^^^^^^^^^^^

You can evaluate the performance of a model by running the **evaluate_model.sh** script 
in a Terminal from within the **model** folder. You can either provide the name of the model
you with to evaluate or the location

.. code::

   ./evaluate_model.sh

This will produce a log in the **logs** folder within **DI_FILEPATH**. 

Adapting the model or training your own
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can adapt the model by training it again using additional training examples. To do this you need to install the **edris9** model and amend the configuration file 
so that the starting model is **edris9** rather than **med7**.

To train your own model you can follow similar steps, starting from any of **med7**, **edris9** or a standard language model like **en_core_web_sm**. Refer to `spacy <https://spacy.io/usage>`_ 
documentation for more information.

Rules
~~~~~

To convert named entities to the desired structured output we take a rule-based approach. The infrastructure was based on the open source `parsigs <https://github.com/royashcenazi/parsigs>`_ package
for parsing dose instructions.

There are different modules in the **dose_instruction_parser** package which deal with different entities. Some of the named entities (ROUTE, DRUG, STRENGTH) are not processed here because this
is information which is separately stored for prescriptions so we don't need to extract it from the dose instructions. The **DIParser** class in :mod:`di_parser.parser` 
is the culmination of all the pre-processing, NER and rule-based post-processing.

Workflow
--------

This is a summary of the overall workflow for different processes. More information can
be found in dedicated sections of this documentation.

Parsing dose instructions
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Create a new conda environment
2. Install `mod:dose_instruction_parser` package 
3. Install `en_edris9` model 
4. Run `parse_dose_instructions -h` on the command line to get help on parsing dose instructions

Improving/modifying the existing rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Create a new conda environment (keep it separate from the one for parsing instructions)
2. Clone the `Github repository <https://github.io>`_ 
3. Check out a new Git branch
4. Do the development setup as outlined in the Github README.md 
5. Edit the contents of the **dose_instructions_parser** folder 
6. Check the outcome using `parse_dose_instructions` on the command line, or by importing 
   the local **di_parser** package and running from python 
7. Make sure you update any tests in **parse_dose_instructions/di_parser/tests**
8. Commit the changes and push to Github
9. Open a new pull request to merge the changes into the main branch

Project layout
--------------