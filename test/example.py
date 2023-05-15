import spacy
import pandas as pd

med7 = spacy.load("en_core_med7_lg")

# create distinct colours for labels
col_dict = {}
seven_colours = ['#e6194B', '#3cb44b', '#ffe119', '#ffd8b1', '#f58231', '#f032e6', '#42d4f4']
for label, colour in zip(med7.pipe_labels['ner'], seven_colours):
    col_dict[label] = colour

options = {'ents': med7.pipe_labels['ner'], 'colors':col_dict}


def apply_model(text):
    doc = med7(text)
    spacy.displacy.render(doc, style='ent', jupyter=True, options=options)
    return [(ent.text, ent.label_) for ent in doc.ents]

text = 'A patient was prescribed Magnesium hydroxide 400mg/5ml suspension PO of total 30ml bid for the next 5 days.'
apply_model(text)

# Loading test data
test_data = pd.read_csv("parsed_unit_test_data.csv",
                        index_col = 0 )

# Taking 10 random entries
test_data_short = test_data.sample(n=10)

for t in test_data_short.input:
    apply_model(t)

