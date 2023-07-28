import spacy
from spacy.scorer import Scorer
from spacy.training import Example
from os import listdir
import json
import inspect
import pandas as pd

med7 = spacy.load("en_core_med7_lg")
model_best = spacy.load("output/model-best")
model_last = spacy.load("output/model-last")

# Get all .json files in filepath
filepath = "preprocess/tagged/"
files = [f for f in listdir(filepath) if f.endswith(".json")]

def load_data(file, filepath=filepath):
    with open(f"{filepath}/{file}", "r", encoding="utf-8") as f:
        data = json.load(f)
    return (data["annotations"])

# Load data into one flat list
alldata = [load_data(file) for file in files]
alldata = sorted([item for sublist in alldata for item in sublist if item is not None], key=lambda x: x[0], reverse=True)

def get_scores(ner_model, samples):
    scorer = Scorer(ner_model)
    example = []
    for sample in samples:
        pred = ner_model(sample[0])
        print(pred, sample[1]['entities'])
        temp_ex = Example.from_dict(pred, {'entities': sample[1]['entities']})
        example.append(temp_ex)
    scores = scorer.score(example)
    
    return scores

def retrieve_name(var):
        """
        Gets the name of var. Does it from the out most frame inner-wards.
        :param var: variable to get name from.
        :return: string
        """
        for fi in reversed(inspect.stack()):
            names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]
            if len(names) > 0:
                return names[0]

def compare_model_scores(models, samples):
    all_scores = []
    for model in models:
        scores = get_scores(model, samples)
        all_scores.append(scores)
    score_table = pd.json_normalize(all_scores)
    score_table.index = [retrieve_name(m) for m in models]
    return score_table.T

scores = compare_model_scores(models = [med7, model_best, model_last], samples = alldata)
print(scores)