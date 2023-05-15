import spacy
from spacy.tokens import DocBin

nlp = spacy.load("en_core_med7_lg")
training_data = [
  ("one patch to be applied each day as directed", 
    [(0, 3, "DOSAGE"),
     (4, 9, "FORM"),
     (24, 32, "FREQUENCY"),
     (33, 44, "FREQUENCY")
    ]),
]
# the DocBin will store the example documents
db = DocBin()
for text, annotations in training_data:
    doc = nlp(text)
    ents = []
    for start, end, label in annotations:
        span = doc.char_span(start, end, label=label)
        ents.append(span)
    doc.ents = ents
    db.add(doc)
db.to_disk("./preprocess/train.spacy")