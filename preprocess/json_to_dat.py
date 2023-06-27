"""
Loads .json files from preprocess/tagged/ and crosschecks each tagging instance.
Outputs 2 .dat files:
    processed/crosschecked_data.dat     tagged dose instructions which don't conflict
    processed/conflicting_data.dat      tagged dose instructions which conflict
"""
from os import listdir
import json

# Get all .json files in filepath
filepath = "preprocess/tagged/"
files = [f for f in listdir(filepath) if f.endswith(".json")]

def load_data(file, filepath=filepath):
    with open(f"{filepath}/{file}", "r", encoding="utf-8") as f:
        data = json.load(f)
    return (data["annotations"])

# Load data into one flat list
alldata = [load_data(file) for file in files]
alldata = sorted([item for sublist in alldata for item in sublist if item is not None], key=lambda x: x[0], reverse=True)

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
    crosschecked_data = [dat for i, dat in enumerate(alldata) if dat[0] in crosschecked_dis and dat not in alldata[:i]]
    # All conflicting entries go into conflicting data
    conflicting_data = [dat for dat in alldata if dat[0] in conflicting_dis]
    return (crosschecked_data, conflicting_data)
            
crosschecked_data, conflicting_data = get_crosschecked_dis(alldata)

# Save out 
with open("preprocess/processed/crosschecked_data.dat", "w") as f:
    for line in crosschecked_data:
        f.write(line[0] + " | " + str(line[1]) +"\n")

with open("preprocess/processed/conflicting_data.dat", "w") as f:
    for line in conflicting_data:
        f.write(line[0] + " | " + str(line[1]) +"\n")
