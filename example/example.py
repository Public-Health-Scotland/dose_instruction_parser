import spacy
import pandas as pd
import random

med7 = spacy.load("en_core_med7_lg")
model_best = spacy.load("***REMOVED***models/original/model-best")
model_last = spacy.load("***REMOVED***models/original/model-last")

# create distinct colours for labels
col_dict = {}
seven_colours = ['#e6194B', '#3cb44b', '#ffe119', '#ffd8b1', '#f58231', '#f032e6', '#42d4f4', '#C5CAC8', '#8BC34A']
for label, colour in zip(model_best.pipe_labels['ner'], seven_colours):
    col_dict[label] = colour

options = {'ents': model_best.pipe_labels['ner'], 'colors': col_dict}


def apply_model(text, model):
    doc = model(text)
    spacy.displacy.render(doc, style='ent', jupyter=True, options=options)
    ents = [(ent.text, ent.label_) for ent in doc.ents]
    print(ents)
    return ents


def compare_models(text):
    print("Applying med7")
    apply_model(text, med7)
    print("Applying best model")
    apply_model(text, model_best)
    print("Applying last model")
    apply_model(text, model_last)
    return "Done"

# Comparing models for a specific example
text = 'A patient was prescribed Magnesium hydroxide 400mg/5ml suspension PO of total 30ml bid for the next 5 days.'
compare_models(text)

# Sampling from prolog data
test_data = pd.read_csv("preprocess/for_tagging/for_processing/parsed_unit_test_data.csv",
                        index_col = 0 )

test_data_short = test_data.sample(n=10)
for t in test_data_short.input:
    compare_models(t)

# Sampling from diabetes test data
with open("preprocess/for_testing/sample_diabetes_study_test.txt") as f:
    diabetes_test_data = f.readlines()

for i in range(10):
    text = random.choice(diabetes_test_data)
    print(text)
    compare_models(text)


