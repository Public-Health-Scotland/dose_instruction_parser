import spacy
from spacy.scorer import Scorer
from spacy.training import Example
from os import listdir
from tqdm import tqdm
import json
import inspect
import ast
import pandas as pd

med7 = spacy.load("en_core_med7_lg")
model_best = spacy.load("output/model-best")
model_last = spacy.load("output/model-last")

# Get all .json files in filepath
filepath = "preprocess/processed/"
files = ["crosschecked_data.dat", "resolved_data.dat"]

def process_line(line):
    selection, text, ann = line.replace("\n", "").split(" | ")
    ann = ast.literal_eval(ann)
    return [text, ann]

def load_processed_dat(file, filepath=filepath):
    with open(f"{filepath}/{file}", "r") as f:
        lines = f.readlines()
    lines = [process_line(line) for line in lines]
    return lines

processed_data = [load_processed_dat(file) for file in files]
processed_data = sorted([item for sublist in processed_data for item in sublist if item is not None], key=lambda x: x[0], reverse=True)

def get_scores(ner_model, samples):
    scorer = Scorer(ner_model)
    example = []
    for sample in tqdm(samples):
        pred = ner_model(sample[0])
        #print(pred, sample[1]['entities'])
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

scores = compare_model_scores(models = [med7, model_best, model_last], samples = processed_data)
print(scores)