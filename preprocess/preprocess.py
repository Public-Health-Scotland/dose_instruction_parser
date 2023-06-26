"""
Loads .udt.json files from preprocess/tagged/ and converts them to spacy
format for training 
"""
from os import listdir
from spacy.tokens import DocBin
import spacy
import json
from tqdm import tqdm
from sklearn.model_selection import train_test_split

# Get all .udt.json files in filepath
filepath = "preprocess/tagged/"
files = [f for f in listdir(filepath) if f.endswith(".json")]

# Using med7 model as a base 
nlp = spacy.load("en_core_med7_lg")

def load_data(file):
    with open(f"{filepath}/{file}", "r", encoding="utf-8") as f:
        data = json.load(f)
    return (data["annotations"])

# Load data into one flat list
alldata = [load_data(file) for file in files]
alldata = [item for sublist in alldata for item in sublist if item is not None]


def get_crosschecked_dis(data):
    unique_dis = list(set([text for text, ann in data]))
    crosschecked_dis = []
    conflicting_dis = []
    for i, di in enumerate(unique_dis):
        matching_tags = [ann for text, ann in alldata if text == di]
        if all(tag == matching_tags[0] for tag in matching_tags):
            crosschecked_dis.append(unique_dis[i])
        else:
            conflicting_dis.append(unique_dis[i])
    # Unique crosschecked entries go into crosschecked_data
    crosschecked_data = [dat for i, dat in enumerate(alldata) if dat[0] in crosschecked_dis and dat not in alldata[:i]]
    # All conflicting entries go into conflicting data
    conflicting_data = [dat for dat in alldata if dat[0] in conflicting_dis]
    return (crosschecked_data, conflicting_data)
            

# Shuffle and split into tr/dev
train_data, dev_data = train_test_split(alldata, test_size=0.33, random_state=6)

# Convert json to spacy format
def create_training(TRAIN_DATA):
    db = DocBin()
    for text, annot in tqdm(TRAIN_DATA):
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annot["entities"]:
            span = doc.char_span(start, end, label=label,
                                 alignment_mode="contract")
            if span is None:
                print("Skipping entity")
            else:
                ents.append(span)
        doc.ents = ents
        db.add(doc)
    return (db)


train_data = create_training(train_data)
train_data.to_disk("./data/train.spacy")
dev_data = create_training(dev_data)
dev_data.to_disk("./data/dev.spacy")