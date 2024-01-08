"""
Loads .json files from preprocess/tagged/ and crosschecks each tagging instance.

Outputs 2 .dat files:
    processed/crosschecked_data.dat     tagged dose instructions which don't conflict
    processed/conflicting_data.dat      tagged dose instructions which conflict
"""
from os import listdir
import json
import time

from colorama import init as colorama_init
from colorama import Fore, Style

colorama_init()

print(Fore.YELLOW + "Reading tagged .json files from preprocess/tagged." + Style.RESET_ALL)

# Get all .json files in filepath
filepath = "model/preprocess/tagged/"
files = [f for f in listdir(filepath) if f.endswith(".json")]

def load_data(file, filepath=filepath):
    with open(f"{filepath}/{file}", "r", encoding="utf-8") as f:
        data = json.load(f)
    return (data["annotations"])

# Load data into one flat list
alldata = [load_data(file) for file in files]
alldata = sorted([item for sublist in alldata for item in sublist if item is not None], key=lambda x: x[0], reverse=True)
# Replacing all instances of "DOSE" with "DOSAGE" 
# Original tag is DOSAGE but some tagging was done using DOSE instead
for item in alldata:
    item[1]["entities"] = [[ent[0], ent[1], ent[2].replace("DOSE", "DOSAGE")] \
        for ent in item[1]["entities"]]

def get_crosschecked_dis(data):
    """ 
    Checks sets of tags for each unique dose instruction 
    """
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
    crosschecked_data = [dat for i, dat in enumerate(alldata) \
        if dat[0] in crosschecked_dis and dat not in alldata[:i]]
    # All conflicting entries go into conflicting data
    conflicting_data = [dat for dat in alldata if dat[0] in conflicting_dis]
    return (crosschecked_data, conflicting_data)
            
crosschecked_data, conflicting_data = get_crosschecked_dis(alldata)

# Save out 
def save_out(dat, filename):
    with open(f"model/preprocess/processed/{filename}", "w") as f:
        for line in dat:
            # Get entity text 
            ents = line[1]["entities"]
            selections = []
            for ent in ents:
                start, end, tag = ent
                ent_text = line[0][start:end]
                selection = [ent_text, tag]
                selections.append(selection)
            f.write(str(selections) + " | " + line[0] + " | " + str(line[1]) + "\n")

# Appending timestamp so data are not overwritten
time_out = time.strftime('%b-%d-%Y-%H%M', time.localtime())
save_out(crosschecked_data, f"crosschecked_data_{time_out}.dat")
# Backup copy
save_out(conflicting_data, f"conflicting_data_{time_out}.dat")
save_out(conflicting_data, f"resolved_data_{time_out}.dat")

print(Fore.GREEN + "Data saved to model/preprocess/processed" + "\n" + 
     Fore.YELLOW + "There are " + Fore.RED + str(len(conflicting_data)) + Fore.YELLOW + 
     f" entries to check in model/preprocess/processed/resolved_data_{time_out}.dat" + "\n" + 
     "Remove the duplicate entries which are unwanted, " + "\n" +
     "then run model/preprocess/2-dat_to_spacy.py" + Style.RESET_ALL)
