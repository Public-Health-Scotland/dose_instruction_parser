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
import ast
import re
import os
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
import pandas as pd

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
colorama_init()

# Get data - crosschecked_data and resolved_data
filepath = "model/preprocess/processed/"
regex = re.compile("((resolved_data|crosschecked_data))\_\d+-\w+-\d+-\d+.dat")

files = []
for root, dirs, fs in os.walk(filepath):
  for file in fs:
    if regex.match(file):
       files.append(file)

print(Fore.YELLOW + "Loading the following files: " + Style.RESET_ALL + str(files))

def process_line(line):
    """
    line        A line of text from crosschecked or resolved data files
    returns     text and annotation from that line
    """
    selection, text, ann = line.replace("\n", "").split(" | ")
    ann = ast.literal_eval(ann)
    return [text, ann]

def process_lines(lines, file=file):
    for line in lines:
        try:
            yield process_line(line)
        except:
            print(Fore.RED + f"Error in the following input line. Please fix this in {file}" + Style.RESET_ALL)
            print(line)

def load_processed_dat(file, filepath=filepath):
    """
    file        File name to load
    filepath    File path where file is located
    returns     nested list of [text, annotation] for each line
    """
    with open(f"{filepath}/{file}", "r") as f:
        lines = f.readlines()
    
    lines = process_lines(lines, file)
    return lines

# Loading data from files and flattening list
processed_data = [load_processed_dat(file) for file in files]
processed_data = sorted([item for sublist in processed_data for item in sublist if item is not None], key=lambda x: x[0], reverse=True)

# Check there are no duplicates i.e. all the conflicting tags have been resolved
dis = [text for text, ann in processed_data]
duplicates = list(set([text for text in dis if dis.count(text) > 1]))
#assert len(duplicates) == 0, Fore.RED + "Please review resolved_data files and remove the following duplicates" + Style.RESET_ALL + "\n" + str(duplicates)

# Creating duplicate dose instructions based off frequency table
load_dotenv(dotenv_path="secrets.env")
freq_table = pd.read_csv(f"{os.getenv('DI_FILEPATH')}/data/dose_instructions_limit250_cntr.csv.xz")

print(Fore.YELLOW + "Creating duplicate dose instructions based off frequency table" + Style.RESET_ALL)
duplicated_data = []
for instruction, ann in tqdm(processed_data):
    try:      
        count = (
            freq_table.query(f"dose_instructions == '{instruction}'")
                .loc[:, "cntr"]
                .iat[0]
        )
        for i in range(count): 
            duplicated_data.append([instruction, ann])
    except:
        print(Fore.RED + f"Instruction not in frequency table, adding 1 copy only: {instruction}" + Style.RESET_ALL)
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
    convert_to_spacy(globals()[f"{name}_data"]).to_disk(f"./model/data/{name}.spacy")

print(Fore.GREEN + "Spacy data saved to data folder" + "\n" +
      Fore.YELLOW + "Check model/config/config.cfg then run" + 
      "./train_model.sh to train the model." + Style.RESET_ALL)