import sys
import spacy
from dataclasses import dataclass
from itertools import compress
import re
from spacy import Language
import copy
import os
import warnings

# Local import of postprocess functions
import di_parser.parserfuncs.prepare as pprepare
import di_parser.parserfuncs.dosage as pdosage
import di_parser.parserfuncs.frequency as pfrequency
import di_parser.parserfuncs.duration as pduration

@dataclass
class StructuredDI:
    """
    A structured dose instruction
    Attributes:
    -----------
    form: str
        The form of drug (e.g. "tablet", "patch", "injection")
    dosageMin: float
        The minimum dosage 
    dosageMax: floata
        The maximum dosage 
    frequencyMin: float
        The minimum frequency 
    frequencyMax: float
        The maximum frequency 
    frequencyType : str
        The type of frequency for the dosage (e.g. Hour, Day, Week, Month).
    durationMin: float
        The minimum duration of treatment 
    durationMax: float
        The maximum duration of treatment
    durationType: str
        The type of duration for dosage (e.g. Day, Week, Month)
    asRequired : bool
        Whether to take as required / as needed
    asDirected: bool
        Whether to take as directed
    """
    form: str
    dosageMin: float
    dosageMax: float
    frequencyMin: float
    frequencyMax: float
    frequencyType: str
    durationMin: float
    durationMax: float
    durationType: str
    asRequired: bool
    asDirected: bool

def _get_model_entities(model_output):
    """
    Retrieve the entities from model output.
    Create model output by:
        model = spacy.load("my_model")
        model_output = model("my dose instruction")
    """
    entities = model_output.ents
    return entities

def _get_model_entities_from_text(text, model):
    """
    Retrieve the entities from text
    """
    di_preprocessed = pprepare._pre_process(text)
    model_output = model(di_preprocessed)
    entities = model_output.ents 
    return entities

def _parse_di(di: str, model: Language):
    """
    1. Preprocesses dose instruction
    2. Applies model to retrieve entities
    3. Creates structured dose instruction from entities using static rules
    """
    di_preprocessed = pprepare._pre_process(di)
    model_output = model(di_preprocessed)
    return _create_structured_dis(model_output)

def _parse_dis(di_lst, model: Language):
    """
    Parses multiple dose instructions at once
    """
    return pprepare._flatmap(lambda di: _parse_di(di, model), di_lst)

blank_di_dict = {"DOSAGE": None, "FREQUENCY": None, "FORM": None, 
                    "DURATION": None, "AS_REQUIRED": None, "AS_DIRECTED": None}

def _keep_entity(entity, seen_labels):
    """
    Determine whether to pay attention to an entity when splitting labels
    up into multiple dose instructions

    Input:
        entity: spacy model entity
            entity to determine whether to ignore
        seen_labels: list of spacy model entity labels
            list of labels already seen by parser, e.g. which entities
            the parser has already seen
    Output:
        bool
            Whether to keep the entity or not
    """
    # Don't pay attention to any of these entities
    if entity.label_ in ["DRUG", "STRENGTH", "ROUTE"]:
            return False
    elif entity.label_ in seen_labels:
        if entity.label_ == "DOSAGE":
            if any(x in entity.text.split() for x in ("max", "maximum")):
                return False
            else:
                return True    
        elif entity.label_ == "FREQUENCY":
            if any(x in entity.text.split() for x in ("24", "maximum")):
                return False
            else:
                return True    
        else:
            return True
        # If we've not already seen it we pay attention
    else:
        return True

def _combine_split_dis(result):
    """
    Checks split dose instructions and re-combines into single dose instructions
    where necessary.

    In particular:
        1. Dose instructions with the same dosage are combined with the 
          corresponding frequencies joined by "and"
        2. Dose instructions with the same frequency type and null duration 
          are combined by adding the dosages together
    """
    # 1.
    print(result)
    keep_mask = [True]*len(result)
    add_index = None
    for i in range(len(result[:-1])):
        if result[i]["DOSAGE"] == result[i+1]["DOSAGE"]:
            print("hi")
            if add_index == None:
                add_index = i
            if result[i+1]["FREQUENCY"] is not None:
                result[add_index]["FREQUENCY"] = result[add_index]["FREQUENCY"] + " and " + result[i+1]["FREQUENCY"]
            keep_mask[i+1] = False
        else:
            add_index = None
    result = list(compress(result, keep_mask))
    # 2. 
    return result
    

#TODO: Improve splitting
# Get rid of tags with redundant information (clarification e.g. "new daily dose = 100mg")
# Combine tags which go together e.g. "2 in the morning" + "2 in the evening" = "2 in the morning and 2 in the evening"
def _split_entities_for_multiple_instructions(model_entities):
    """
    Automatically determines if multiple dose instructions are included
    within one input dose instruction. If so, splits up the dose instruction.
    """
    result = []
    seen_labels = set()
    current_info = blank_di_dict.copy()
    for entity in model_entities:
        # Ignore some entities 
        keep_entity = _keep_entity(entity, seen_labels)
        if not keep_entity:
            continue
        elif entity.label_ in seen_labels:
            result.append(current_info)
            current_info = blank_di_dict.copy()
            seen_labels.clear()
        current_info[entity.label_] = entity.text
        seen_labels.add(entity.label_)
    result.append(current_info)
    # Combine the split dose instructions if necessary
    result = _combine_split_dis(result)
    return result


def _create_structured_di(model_entities, form=None, asRequired=False, asDirected=False):
    """
    Creates a StructuredDI from model entities.
    """
    structured_di = StructuredDI(form, None, None, None, None, 
                                    None, None, None, None, asRequired, asDirected)
    for label, text in model_entities.items(): 
        if text is None:
            continue
        elif label == 'FORM':
            if structured_di.form is None:
                form = pdosage._to_singular(text)
                if form is not None:
                    structured_di.form = form
        elif label == 'DOSAGE':
            min, max, form, = pdosage._get_dosage_info(text)
            structured_di.dosageMin = min
            structured_di.dosageMax = max
            if form is not None:
                structured_di.form = form
        elif label == 'FREQUENCY':
            min, max, freqtype = pfrequency._get_frequency_info(text)
            structured_di.frequencyMin = min
            structured_di.frequencyMax = max
            if freqtype is not None:
                structured_di.frequencyType = freqtype
        elif label == 'DURATION':
            min, max, durtype = pduration._get_duration_info(text)
            structured_di.durationMin = min
            structured_di.durationMax = max
            structured_di.durationType = durtype
        elif label == "AS_REQUIRED":
            structured_di.asRequired = True
        elif label == "AS_DIRECTED":
            structured_di.asDirected = True
        else:
            continue
    return structured_di

def _create_structured_dis(model_output):
    """
    Creates StructuredDIs from a model output.
    1. Gets entities
    2. Determines whether multiple instructions present 
    3. Creates a StructuredDI for each instruction
    """
    entities = _get_model_entities(model_output)
    multiple_instructions = _split_entities_for_multiple_instructions(entities)
    first_di = _create_structured_di(multiple_instructions[0])
    # incase multiple instructions exist, they apply to the same drug and form
    other_dis = [_create_structured_di(instruction_entities, 
                                         first_di.form, first_di.asRequired,
                                         first_di.asDirected)
                  for instruction_entities in multiple_instructions[1:]]
    return [first_di] + other_dis


class DIParser:
    """
    Dose instruction parser class 

    Example
    -------
    >>> model_path = "***REMOVED***models/"
    >>> di_parser = DIParser(model_name=f"{model_path}/original/model-best")

    >>> di = "take 2 3ml spoonfuls with meals for 5-6 weeks as discussed"
    >>> parsed_di = di_parser.parse(di)
    >>> parsed_di
    [StructuredDI(form='ml', dosageMin=6.0, dosageMax=6.0, 
        frequencyMin=3.0, frequencyMax=3.0, frequencyType='Day',
         durationMin=5.0, durationMax=6.0, durationType='Week', 
         asRequired=False, asDirected=True)]
    """
    def __init__(self, model_name):
        self.__language = spacy.load(model_name)
    def parse(self, di: str):
        return _parse_di(di, self.__language)
    def parse_many(self, dis: list):
        return _parse_dis(dis, self.__language)


#model_path = "***REMOVED***models/"
#dip = DIParser(model_name=f"{model_path}/original/model-best")

#from importlib import reload 
#reload(pfrequency)
