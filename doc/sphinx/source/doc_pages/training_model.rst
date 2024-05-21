.. _TrainingModel:

Training a new named entity recogniser model 
============================================


Configuration
-------------

The relevant folder is 'model'.

Setup according to README.md and check that installation part of docs has been done (see heading 'Installation' under CONTENTS).

Remember to use 'secrets.env' file as this is required to define the filepath.


Creating training data
----------------------

In order to train the model we need to create some data.

The first step in this process is to create tagged data in .json format. For this process we
recommend using spacy NER annotator.

Examples of the type of instructions could be "take 2 tablets" or "apply cream to area daily",
ensuring that there is only one (unique) example of each instruction.

A lookup table for how many there are of each example is then created.


Preprocess data
---------------

## Setup

### Model development set up

- Clone repository
- Obtain **secrets.env** file from colleagues which defines environment variable **DI_FILEPATH**. If you are working outwith Public Health Scotland you can define your own filepath and start the process from scratch.
- Run  `./set_up_conda.sh` to set up the conda environment (default name **di**)
- Activate environment with e.g. `conda activate di`

## How to train a model

Follow [model development setup](#model-development-set-up)
- Go to **model** folder
- Tag data using desktop [NER annotator tool](https://tecoholic.github.io/ner-annotator/) 
- Copy output to **preprocess/tagged** as .json. Only put files here which you want to train the model on.
- Run **preprocess/1-json_to_dat.py**. This takes the tagged data and crosschecks all unique dose instructions against the different tags which were given to them. Any where all tags agree are outputted to **preprocess/processed/crosschecked_data.dat**. Those where tags conflict are outputted to **preprocess/processed/conflicting_data.dat**
- Make a copy of **conflicting_data.dat** and save as **resolved_data.dat**. Remove the instances of tags you don't want.
- Run **preprocess/2-dat_to_spacy.py**. This loads in the crosschecked data and resolved data and converts to spacy format. Output is saved in **model/data**
- Check the config file: **config/config.cfg** (this file gives all of the parameters for what the model is actually going to be, so if changes are required this is where the changes are made).
    - an example from the config file is: -
        [components.ner]
        # Name of trained pipeline to copy components from
        source = "en_core_med7_lg"
        (note: so we can see this has come from med7. Wherever med7 appears in the config file it is because it is the base model that we are starting from, i.e. not starting from scratch. If a new model is created in the future to replace this then replace with name of new model throughout to give new starting point)
        see detailed explanation at https://spacy.io/usage/training/#config
- Train model using `./train_model.sh`. Takes about 3 hours to run ~2k (training) examples
- Model results are saved at the **DI_FILEPATH**. There is a best fit model (model-best) and also the last model tested (model-last).
    - If not specifically named then a folder will be created based upon date and time run.
    - There will also be information (file named 'train_' followed by date and time) saved in the logs folder. Within this we can see a table containing information relating to how good the score is (as a percentage e.g. 0.60, 0.93, etc.) as the model is trained.
- Evaluate your model results based on precision, recall and F-score using `./evalute_model.sh`. Output at **DI_FILEPATH** in **logs**.
    - There will be information (file named 'evaluate_' followed by date and time) saved in the logs folder. Within this we can see a table of results 'NER per type' (entity e.g. dosage, frequency, etc.) detailing precision, recall and F-score as required.
- You can compare and visualise model results by adapting the python script **compare_models.py**
- Convert your model to a package by running `./package_model.sh`
    - This is a script to help convert the model into a package that can be installed. This is only done once we are satisfied that the model is ready to be used. File is created in 'dist' with an extension of .whl and can be distributed to other individuals or teams for installation in order to share the model.
- Install your model using pip and specifying the path to the model
    - e.g. python -m pip install "$DI_FILEPATH/models/en_edris9-1.0.0/dist/en_edris9-1.0.0-py3-none-any.whl"