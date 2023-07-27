"""
Converts crosschecked and resolved dose instructions to .spacy train and dev data.

Loads the following files:
    preprocess/processed/crosschecked_data.dat
    preprocess/processed/resolved_data.dat

1. Checks that there are no duplicate dose instructions. If so throws an error.
2. Creates duplicates of tagged dose instructions based off frequency table.
3. Splits data into train/dev
4. Converts to spacy format

Saves out the following files:
    data/train.spacy
    data/dev.spacy
"""
from spacy.tokens import DocBin
import spacy
import ast
from tqdm import tqdm
from sklearn.model_selection import train_test_split

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

colorama_init()

# Get data - crosschecked_data and resolved_data
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

# Check there are no duplicates i.e. all the conflicting tags have been resolved
dis = [text for text, ann in processed_data]
assert len(dis) == len(set(dis)), "Please review resolved_data.dat and make sure all duplicate dose instructions are resolved"

####################################################################################################
# TODO: Here is where we will create duplicates of dose instructions based off the frequency table #
####################################################################################################

# Using med7 model as a base 
nlp = spacy.load("en_core_med7_lg")

# Shuffle and split into tr/dev
train_data, dev_data = train_test_split(processed_data, test_size=0.33, random_state=6)

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

print(Fore.GREEN + "Spacy data saved to data folder" + "\n" +
      Fore.YELLOW + "Check config/config.cfg then run ./train_model.sh to train the model." + Style.RESET_ALL)