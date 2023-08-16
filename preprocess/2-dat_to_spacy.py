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
import pandas as pd

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
colorama_init()

# Get data - crosschecked_data and resolved_data
filepath = "***REMOVED***preprocess/processed/"
files = ["crosschecked_data.dat", "resolved_data.dat"]

def process_line(line):
    """
    line        A line of text from crosschecked or resolved data files
    returns     text and annotation from that line
    """
    selection, text, ann = line.replace("\n", "").split(" | ")
    ann = ast.literal_eval(ann)
    return [text, ann]

def load_processed_dat(file, filepath=filepath):
    """
    file        File name to load
    filepath    File path where file is located
    returns     nested list of [text, annotation] for each line
    """
    with open(f"{filepath}/{file}", "r") as f:
        lines = f.readlines()
    lines = [process_line(line) for line in lines]
    return lines

# Loading data from files and flattening list
processed_data = [load_processed_dat(file) for file in files]
processed_data = sorted([item for sublist in processed_data for item in sublist if item is not None], key=lambda x: x[0], reverse=True)

# Check there are no duplicates i.e. all the conflicting tags have been resolved
dis = [text for text, ann in processed_data]
assert len(dis) == len(set(dis)), "Please review resolved_data.dat and make sure all duplicate dose instructions are resolved"

# Creating duplicate dose instructions based off frequency table
freq_table = pd.read_csv("***REMOVED***dose_instructions_limit250_cntr.csv.xz")
duplicated_data = []
for instruction, ann in processed_data:
    try:      
        count = (
            freq_table.query(f"dose_instructions == '{instruction}'")
                .loc[:, "cntr"]
                .iat[0]
        )
        for i in range(count): 
            duplicated_data.append([instruction, ann])
    except:
        print(f"Instruction not in frequency table, adding 1 copy only: {instruction}")
        duplicated_data.append([instruction, ann])
    

# Using med7 model as a base 
nlp = spacy.load("en_core_med7_lg")

# Shuffle and split into test/tr/dev
# N.B. can tweak the train/test/dev/split
use_data, test_data = train_test_split(processed_data, test_size=1/10, random_state=6)
train_data, dev_data = train_test_split(use_data, test_size=1/9, random_state=6)

# Convert json to spacy format
def convert_to_spacy(dat):
    """
    dat         list of [text, annotation] pairs to be converted
    returns     spacy DocBin() containing information from dat
    """
    db = DocBin()
    for text, ann in tqdm(dat):
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in ann["entities"]:
            span = doc.char_span(start, end, label=label,
                                 alignment_mode="contract")
            if span is None:
                print("Skipping entity")
            else:
                ents.append(span)
        doc.ents = ents
        db.add(doc)
    return (db)

# Save out test, train and dev data
for name in ["test", "train", "dev"]:
    convert_to_spacy(globals()[f"{name}_data"]).to_disk(f"./data/{name}.spacy")

print(Fore.GREEN + "Spacy data saved to data folder" + "\n" +
      Fore.YELLOW + "Check config/config.cfg then run ./train_model.sh to train the model." + Style.RESET_ALL)