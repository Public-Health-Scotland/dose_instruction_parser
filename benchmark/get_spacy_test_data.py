import spacy
from spacy.tokens import DocBin

db = DocBin().from_disk("data/test.spacy")

model_path = "***REMOVED***models/"
model = spacy.load(f"{model_path}/original/model-best")

test_examples = [doc.text for doc in list(db.get_docs(model.vocab))]

with open("di_parser/benchmark/test_dis.txt", "wt") as f:
    f.write("\n".join(test_examples))