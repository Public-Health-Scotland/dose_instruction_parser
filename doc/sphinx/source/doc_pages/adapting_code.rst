Adapting the code to similar tasks
==================================

The `en_edris9` model and `di_parser` package have been tailored to the problem of parsing free text dose instructions from prescriptions. 
However, the code can be used as a starting point to solve similar problems.

Parsing dose instructions for specific drugs or conditions
----------------------------------------------------------

The `en_edris9` model was trained on a balanced set of data covering the whole of national prescribing information. This makes the model a
good "all rounder" when it comes to performance. If you are interested in a specific subset of drugs or conditions, you should be able to boost
performance by further training the model on this subset of data. To do this, follow instructions in the TrainingModel_ section, taking care to: 

1. Create training data for the types of dose instruction you are interested in
1. Install the `en_edris9` model (if you don't have access you can use `en_core_med7_lg`, obtained following the instructions `here <https://github.com/kormilitzin/med7>`_)
1. Modify `model/config/config.cfg` to replace all instances of `en_core_med7_lg` with `en_edris9`
1. Evaluate the performance compared to `en_edris9` and/or `en_core_med7_lg`, using `model/compare_models.py` as a guide alongside output from `source model/evaluate_model.sh`

Extracting different structural information
-------------------------------------------

In `en_edris9` there are nine named entities extracted, which give rise to the following structured fields:

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

Changing this output requires three main steps:

1. Create new training data tagged with all the named entities you are interested in. You can add new entities here e.g. "AS_REQUIRED" and "AS_DIRECTED" were new entities surplus to those in `med7`
1. Make sure that `overwrite_ents = True` in the `\[components.ner\]` section of `model/config/config.cfg`, then train a new model following TrainingModel_
1. Modify `dose_instruction_parser/di_parser` code to process the new entities into the output you desire.
   This process is more or less involved depending on the complexity of the entities. You can use the existing
   entities as a guide.

.. warning::
    Note that you should include training data which is fully representative of the data you
    would like to use the model for. If you only train the model further on a certain type of example
    it will begin to "forget" what it already knows i.e. get worse at extracting entities which 
    it could do before but is now not being trained on.

General application to medical free text parsing
------------------------------------------------

This is a more involved version of the above. Broadly, you will need to

1. Create tagged training data with all the named entities you are interested in
1. Train a model following TrainingModel_
1. Heavily alter the `dose_instruction_parser/di_parser` code to process the output
   in the way you want.

.. note::
   In this case it would be best to create a totally new repository using this
   repository as a starting point

