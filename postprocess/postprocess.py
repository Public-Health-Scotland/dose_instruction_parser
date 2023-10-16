import sys
from pathlib import Path
import spacy
from dataclasses import dataclass
import re
from spacy import Language
from itertools import chain
import copy
import os
import warnings

# Local import of postprocess functions
import postprocess.ppfuncs.prepare as ppprepare
import postprocess.ppfuncs.dosage as ppdosage
import postprocess.ppfuncs.frequency as ppfrequency
import postprocess.ppfuncs.duration as ppduration

@dataclass
class StructuredDI:
    """
    Represents a structured dose instruction
    Attributes:
    -----------
    form: str
        The form of drug (e.g. "tablet", "patch", "injection")
    dosageMin: float
        The minimum dosage 
    dosageMax: float
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


default_model_name = "en_parsigs"

def _get_model_entities(model_output):
    """
    Retrieve the entities from model output.
    Create model output by:
        model = spacy.load_model("my_model")
        model_output = model("my dose instruction")
    """
    entities = model_output.ents
    return entities

def _parse_di(di: str, model: Language):
    """
    1. Preprocesses dose instruction
    2. Applies model to retrieve entities
    3. Creates structured dose instruction from entities using static rules
    """
    di_preprocessed = ppprepare._pre_process(di)
    model_output = model(di_preprocessed)
    return _create_structured_dis(model_output)

def _parse_dis(di_lst, model: Language):
    """
    Parses multiple dose instructions at once
    """
    return ppprepare._flatmap(lambda di: _parse_di(di, model), di_lst)

def _split_entities_for_multiple_instructions(model_entities):
    """
    Automatically determines if multiple dose instructions are included
    within one input dose instruction. If so, splits up the dose instruction.
    """
    result = []
    seen_labels = set()
    current_sublist = []
    for entity in model_entities:
        # Ignore DRUG and STRENGTH
        if entity.label_ in ["DRUG", "STRENGTH"]:
            continue
        elif entity.label_ in seen_labels:
            result.append(current_sublist)
            current_sublist = []
            seen_labels.clear()
        current_sublist.append(entity)
        seen_labels.add(entity.label_)
    result.append(current_sublist)
    return result


def _create_structured_di(model_entities, form=None, asRequired=False, asDirected=False):
    """
    Creates a StructuredDI from model entities.
    """
    structured_di = StructuredDI(form, None, None, None, None, 
                                    None, None, None, None, asRequired, asDirected)
    for entity in model_entities:
        text = entity.text
        label = entity.label_
        if label == 'DOSAGE':
            min, max, form, freqtype = ppdosage._get_dosage_min_max(text)
            structured_di.dosageMin = min
            structured_di.dosageMax = max
            structured_di.form = form
            structured_di.frequencyType = freqtype
        elif label == 'FORM':
            structured_di.form = ppdosage._to_singular(text)
        elif label == 'FREQUENCY':
            structured_di.frequencyType = ppfrequency._get_frequency_type(text)
            # TODO: min and max
            freq = ppfrequency._get_interval(text)
            structured_di.frequencyMin = freq
            structured_di.frequencyMax = freq
            # Default added only if there is a frequency tag in the di
            # handles cases such as "Every TIME_UNIT"
            if structured_di.frequencyMin is None:
                structured_di.frequencyMin = 1
                structured_di.frequencyMax = 1
        elif label == 'DURATION':
            structured_di.durationType = ppfrequency._get_frequency_type(text)
            # TODO: min and max
            duration = ppfrequency._get_interval(text)
            structured_di.durationMin = duration
            structured_di.durationMax = duration
        elif label == "AS_REQUIRED":
            structured_di.takeAsRequired = True
        elif label == "AS_DIRECTED":
            structured_di.takeAsDirected = True
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
    """
    def __init__(self, model_name="en_parsigs"):
        self.__language = spacy.load(model_name)
    def parse(self, di: str):
        return _parse_di(di, self.__language)
    def parse_many(self, dis: list):
        return _parse_dis(dis, self.__language)


# Example
di_parser = DIParser(model_name="output/model-best")

di = "use two puffs into each nostril twice daily for 3 weeks"
parsed_di = di_parser.parse(di)

