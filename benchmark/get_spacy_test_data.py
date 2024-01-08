import spacy
from spacy.tokens import DocBin
from dotenv import load_dotenv
import os

db = DocBin().from_disk("model/data/test.spacy")

load_dotenv(dotenv_path="secrets.env")

model_path = f"{os.getenv('DI_FILEPATH')}/models/"
model = spacy.load(f"{model_path}/original/model-best")

test_examples = [doc.text for doc in list(db.get_docs(model.vocab))]

with open("benchmark/test_dis.txt", "wt") as f:
    f.write("\n".join(test_examples))