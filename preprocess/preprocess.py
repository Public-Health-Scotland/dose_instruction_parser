from spacy.tokens import DocBin
import spacy
import json
from tqdm import tqdm
from sklearn.model_selection import train_test_split

files = ['diabetes_first_806.json','diabetes_rest.json','first170.json']

nlp = spacy.load("en_core_med7_lg")

def load_data(file):
    with open(f"preprocess/tagged/{file}", "r", encoding="utf-8") as f:
        data = json.load(f)
    return (data["annotations"])

# Load data into one flat list
alldata = [load_data(file) for file in files]
alldata = [item for sublist in alldata for item in sublist if item is not None]

# Shuffle and split into tr/val
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