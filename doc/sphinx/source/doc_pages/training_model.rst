.. _Training a model:

Training a new named entity recogniser model 
============================================

Pre-processing
~~~~~~~~~~~~~~

Pre-processing functions can be found in the :mod:`di_parser.di_prepare` module.
Several operations are performed on the input text to get it ready for 
the NER model:

#. All parentheses are replaced with a blank space
#. Hyphens ("-") and slashes ("/" and "\") and replaced with a blank space
#. Certain keywords are replaced with alternatives e.g. "qad" -> "every other day". 
   These combinations are listed in :mod:`di_parser.data.replace_words`
#. Spelling is corrected using the `pyspellchecker <https://pypi.org/project/pyspellchecker/>`_ package.
   Certain keywords are not corrected. These are listed in :mod:`di_parser.data.keep_words`
#. Number-words are converted to numbers using the `word2number <https://pypi.org/project/word2number/>`_ package,
   e.g. "two" -> "2"; "half" -> "0.5".
#. Blank spaces are added around numbers 
   e.g. "2x30ml" -> " 2 x 30 ml"
#. Extra spaces between words are removed
#. Leading and trailing whitespace is removed

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

At Public Health Scotland we have trained a model called :program:`en_edris9` to do NER. Due to data 
protection concerns the model is not currently publicly available. Please contact the eDRIS team 
on `phs.edris@phs.scot <mailto:phs.edris@phs.scot>`_ to enquire about access.

In the :program:`en_edris9` model there are nine named entities:

* DOSAGE
* FORM 
* ROUTE
* DRUG 
* STRENGTH
* FREQUENCY
* DURATION
* AS_REQUIRED
* AS_DIRECTED

:program:`en_edris9` was based on the `med 7 <https://github.com/kormilitzin/med7>`_ model with the addition of
two entities: "AS_REQUIRED" and "AS_DIRECTED".

Preparing for training
^^^^^^^^^^^^^^^^^^^^^^

The code used to prepare and train the model can be found in the **model** folder. To generate :program:`en_edris9`,
the :program:`en_med7` model was further trained on approximately 7,000 gold-standard tagged dose instructions. 
Each instruction was separately tagged by two eDRIS analysts, and any tagged instructions which didn't match
identically were manually resolved by the team. This was to ensure high quality input data. 

There are three steps to prepare raw examples of dose instructions for training:

#. Tag entities by hand 
#. Optional: cross check tagging if each example has been tagged twice by different people
#. Convert tagged examples to :file:`.spacy` format

Tag entities by hand
''''''''''''''''''''

The tagging process was carried out using the desktop version of `NER Annotator for Spacy <https://github.com/tecoholic/ner-annotator>`_,
which outputs tagged dose instructions in :file:`.json` format. An example of a :file:`.json` file with just two tagged dose instructions is:

.. code:: 

   {"classes":["DOSE","FORM","FREQUENCY","DURATION","ROUTE","DRUG","STRENGTH","AS_DIRECTED","AS_REQUIRED"],
   "annotations":[
      ["1 tab in the morning",{"entities":[[0,1,"DOSE"],[2,5,"FORM"],[6,20,"FREQUENCY"]]}],
      ["1 cap 4 times daily",{"entities":[[0,1,"DOSE"],[2,5,"FORM"],[6,19,"FREQUENCY"]]}]
      ]
   }

Cross check tagging
'''''''''''''''''''

Cross-checking tagging is done using the :file:`1-json_to_dat.py` script in :file:`model/preprocess/`. Tagged examples
must first be copied to :file:`model/preprocess/tagged/`, and must be in .json format. The script
outputs two :file:`.dat` files to :file:`model/preprocess/processed`:

* :file:`crosschecked_data_\\{time\\}.dat` are examples where both taggers agree on all tags
* :file:`conflicting_data_\\{time\\}.dat` are examples where taggers disagree on one or more tags

You must then manually open up :file:`conflicting_data_\\{time\\}.dat` and resolve any conflicts, before
saving out as :file:`resolved_data_\\{time\\}.dat`.

Convert tagged examples to .spacy format
''''''''''''''''''''''''''''''''''''''''

The crosschecked and resolved data are converted to :file:`.spacy` format by :file:`2-dat_to_spacy.py`.
The instances are shuffled and split into train; test; dev data with a 8:1:1 split. This can be changed
by editing the file. Data are saved out to :file:`model/data` in :file:`.spacy` format.

Training
^^^^^^^^

Before training the model you need to define a :program:`DI_FILEPATH`` environment variable, which is the 
file path you will save and load models from. You should save this variable in a :file:`secrets.env` file
in the :file:`dose_instructions_ner` folder. The contents of :file:`secrets.env` should be:

.. code::

   export DI_FILEPATH="/path/to/folder/"

You can train the model by opening a Terminal and running:

.. code::
   
   cd model
   ./train_model.sh

You will be taken through interactive steps in the Terminal to set the model name.
The model parameters are defined in :file:`model/config/config.cfg`, which is a `spacy 
configuration file <https://spacy.io/usage/training/#config>`_. There are a few important
things to note about the contents:

* The path to the training data is set under **\[paths\]**
* The :program:`en_med7` model is used as a starting point for training. This is set
  using the **source** parameters under **\[components\]** and also in **\[initialize.before_init\]**.
* The hyperparameters for the neural network are set under **\[training.optimizer\]**.
  The `Adam <https://arxiv.org/abs/1412.6980>`_ optimiser is the default.
* **\[training.score_weights\]** details the relative importance of different measure
  in evaluating training performance. Available measures are precision, recall and 
  `F-score <https://en.wikipedia.org/wiki/F-score>`_ (the harmonic mean of precision and recall). 

Model training logs will be saved to a :file:`logs`` folder within your :program:`DI_FILEPATH`. Training typically
takes a few hours.  

Model performance
^^^^^^^^^^^^^^^^^

You can evaluate the performance of a model by running the :file:`evaluate_model.sh` script 
in a Terminal from within the :file:`model` folder. You can either provide the name of the model
you with to evaluate or the location

.. code::

   ./evaluate_model.sh

This will produce a log in the :file:`logs` folder within :program:`DI_FILEPATH`. 

Adapting the model or training your own
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can adapt the model by training it again using additional training examples. To do this you need to install the :program:`en_edris9` model and amend the configuration file 
so that the starting model is :program:`en_edris9` rather than :program:`en_med7`.

To train your own model you can follow similar steps, starting from any of :program:`en_med7`, :program:`en_edris9` or a standard language model like :program:`en_core_web_sm`. Refer to `spacy <https://spacy.io/usage>`_ 
documentation for more information.
