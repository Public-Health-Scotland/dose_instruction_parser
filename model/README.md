# Training a new named entity recognition (NER) model

The purpose of the model is to identify parts of the instruction
associated with each named entity. This is done using a neural network, 
which is a type of machine learning
model. The neural network is implemented via the [spacy](https://spacy.io/) package.

At Public Health Scotland we have trained a model called `en_edris9` to do NER. Due to data protection concerns the model is not currently publicly available. Please contact the eDRIS team 
on [phs.edris@phs.scot](mailto:phs.edris@phs.scot) to enquire about access.

In the `en_edris9` model there are nine named entities:

* DOSAGE
* FORM 
* ROUTE
* DRUG 
* STRENGTH
* FREQUENCY
* DURATION
* AS_REQUIRED
* AS_DIRECTED

`en_edris9` was based on the [med 7](https://github.com/kormilitzin/med7) model with the addition of two entities: "AS_REQUIRED" and "AS_DIRECTED".

## Preparing for training

The code used to prepare and train the model can be found in the `model` folder. To generate `en_edris9`, the `en_med7` model was further trained on approximately 7,000 gold-standard tagged dose instructions. 
Each instruction was separately tagged by two eDRIS analysts, and any tagged instructions which didn't match
identically were manually resolved by the team. This was to ensure high quality input data. 

There are three steps to prepare raw examples of dose instructions for training:

1. Tag entities by hand 
1. Optional: cross check tagging if each example has been tagged twice by different people
1. Convert tagged examples to `.spacy` format

### Tag entities by hand

The tagging process was carried out using the desktop version of [NER Annotator for Spacy](https://github.com/tecoholic/ner-annotator),
which outputs tagged dose instructions in `.json` format. An example of a `.json` file with just two tagged dose instructions is:

```
{"classes":["DOSE","FORM","FREQUENCY","DURATION","ROUTE","DRUG","STRENGTH","AS_DIRECTED","AS_REQUIRED"],
"annotations":[
    ["1 tab in the morning",{"entities":[[0,1,"DOSE"],[2,5,"FORM"],[6,20,"FREQUENCY"]]}],
    ["1 cap 4 times daily",{"entities":[[0,1,"DOSE"],[2,5,"FORM"],[6,19,"FREQUENCY"]]}]
    ]
}
```

The numbers alongside each entity refer to the start and end positions of the entity in the text (where numbers start counting from 0). 
For example, for "1 tab in the morning", the the `FORM` entity is recorded as `[2,5,"FORM"]` which corresponds to the 2nd up to but not
including the 5th character in the text, e.g. "tab".

### Cross check tagging

Cross-checking tagging is done using the `1-json_to_dat.py` script in `model/preprocess/`. Tagged examples must first be copied to `model/preprocess/tagged/`, and must be in `.json` format. The script outputs two `.dat` files to `model/preprocess/processed`:

* `crosschecked_data_{time}.dat` are examples where both taggers agree on all tags
* `conflicting_data_{time}.dat` are examples where taggers disagree on one or more tags

You must then manually open up `conflicting_data_{time}.dat` and resolve any conflicts, before saving out as `resolved_data_{time}.dat`.

### Convert tagged examples to `.spacy` format

The crosschecked and resolved data are converted to `.spacy` format by `2-dat_to_spacy.py`.
The instances are shuffled and split into train; test; dev data with a 8:1:1 split. This can be changed by editing the file. Data are saved out to `model/data` in `.spacy` format.

## Training

Before training the model you need to define a `DI_FILEPATH` environment variable, which is the file path you will save and load models from. You should save this variable in a `secrets.env` file in the `dose_instructions_ner` folder. The contents of `secrets.env` should be:

```
export DI_FILEPATH="/path/to/folder/"
```

You can train the model by opening a Terminal and running:

```
cd model
./train_model.sh
```

You will be taken through interactive steps in the Terminal to set the model name.
The model parameters are defined in `model/config/config.cfg`, which is a [spacy 
configuration file](https://spacy.io/usage/training/#config). There are a few important
things to note about the contents:

* The path to the training data is set under **\[paths\]**
* The `en_med7` model is used as a starting point for training. This is set
  using the **source** parameters under **\[components\]** and also in **\[initialize.before_init\]**.
* The hyperparameters for the neural network are set under **\[training.optimizer\]**.
  The [Adam](https://arxiv.org/abs/1412.6980) optimiser is the default.
* **\[training.score_weights\]** details the relative importance of different measure
  in evaluating training performance. Available measures are precision, recall and 
  [F-score](https://en.wikipedia.org/wiki/F-score) (the harmonic mean of precision and recall). 

Model training logs will be saved to a `logs` folder within your `DI_FILEPATH`.

## Model performance

You can evaluate the performance of a model by running the `evaluate_model.sh` script 
in a Terminal from within the `model` folder. You can either provide the name of the model
you with to evaluate or the location

```
./evaluate_model.sh
```

This will produce a log in the `logs` folder within `DI_FILEPATH`. 

## Adapting the model or training your own

You can adapt the model by training it again using additional training examples. To do this you need to install the `en_edris9` model and amend the configuration file 
so that the starting model is `en_edris9` rather than `en_med7`.

To train your own model you can follow similar steps, starting from any of `en_med7`, `en_edris9` or a standard language model like `en_core_web_sm`. Refer to [spacy](https://spacy.io/usage) documentation for more information.


