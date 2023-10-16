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
class StructuredSig:
    """
    Represents a structured medication dosage instructions.
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
    entities = model_output.ents
    return entities

def _parse_sig(sig: str, model: Language):
    """
    Converts the preprocessed sig using static rules and the model outputs
    """
    sig_preprocessed = ppprepare._pre_process(sig)
    model_output = model(sig_preprocessed)
    return _create_structured_sigs(model_output)

def _parse_sigs(sig_lst, model: Language):
    """
    Converts a medication dosage instructions string to a StructuredSig object.
    The input string is pre processed, and than combining static rules and NER model outputs, a StructuredSig object is created.
    """
    return ppprepare._flatmap(lambda sig: _parse_sig(sig, model), sig_lst)

def _split_entities_for_multiple_instructions(model_entities):
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


def _create_structured_sig(model_entities, form=None, asRequired=False, asDirected=False):
    structured_sig = StructuredSig(form, None, None, None, None, 
                                    None, None, None, None, asRequired, asDirected)
    for entity in model_entities:
        text = entity.text
        label = entity.label_
        if label == 'DOSAGE':
            print("DOSAGE: " + text)
            if "max" in text:
                structured_sig.dosageMin = 0
                nums = re.findall('\d+', text)
                if len(nums) != 1:
                    warnings.warn("More than one number found for max dosage")
                structured_sig.dosageMax = nums[0]   
            elif any(x in text for x in ("to", "-")):
                substrs = re.split("to|-", text)
                if len(substrs) == 2:
                    if "up" in substrs[0]:
                        structured_sig.dosageMin = 0
                    else:
                        structured_sig.dosageMin = float(substrs[0])
                    structured_sig.dosageMax = float(substrs[1])
                else:
                    structured_sig.dosageMin = float(substrs[0])
                    structured_sig.dosageMax = float(substrs[0])
            elif text.split()[0].isnumeric():
                dosage = float(text.split()[0])
                structured_sig.dosageMin = dosage
                structured_sig.dosageMax = dosage
                structured_sig.frequencyType = ppfrequency._get_frequency_type(text)
                form_from_dosage = ppdosage._get_form_from_dosage_tag(text)
                if form_from_dosage is not None:
                    structured_sig.form = ppdosage._to_singular(form_from_dosage)
            # Check for e.g. "mg", "ml"
            else:
                measures = [ele for ele in ["mg", "ml"] if(ele in text)]
                if bool(measures):
                    structured_sig.form = measures[0]
                    dosage = text.replace(measures[0],"")
                    # TODO: min and max
                    structured_sig.dosageMin = dosage
                    structured_sig.dosageMax = dosage
                # Otherwise extract first number to use as dosage
                else:
                    nums = re.findall('\d+', text)
                    # TODO: min and max
                    dosage = nums[0]
                    structured_sig.dosageMin = dosage
                    structured_sig.dosageMax = dosage
        elif label == 'FORM':
            structured_sig.form = ppdosage._to_singular(text)
        elif label == 'FREQUENCY':
            structured_sig.frequencyType = ppfrequency._get_frequency_type(text)
            # TODO: min and max
            freq = ppfrequency._get_interval(text)
            structured_sig.frequencyMin = freq
            structured_sig.frequencyMax = freq
            # Default added only if there is a frequency tag in the sig
            # handles cases such as "Every TIME_UNIT"
            if structured_sig.frequencyMin is None:
                structured_sig.frequencyMin = 1
                structured_sig.frequencyMax = 1
        elif label == 'DURATION':
            structured_sig.durationType = ppfrequency._get_frequency_type(text)
            # TODO: min and max
            duration = ppfrequency._get_interval(text)
            structured_sig.durationMin = duration
            structured_sig.durationMax = duration
        elif label == "AS_REQUIRED":
            structured_sig.takeAsRequired = True
        elif label == "AS_DIRECTED":
            structured_sig.takeAsDirected = True
        else:
            continue
    return structured_sig

def _create_structured_sigs(model_output):
    entities = _get_model_entities(model_output)
    multiple_instructions = _split_entities_for_multiple_instructions(entities)
    first_sig = _create_structured_sig(multiple_instructions[0])
    # incase multiple instructions exist, they apply to the same drug and form
    other_sigs = [_create_structured_sig(instruction_entities, 
                                         first_sig.form, first_sig.asRequired,
                                         first_sig.asDirected)
                  for instruction_entities in multiple_instructions[1:]]
    return [first_sig] + other_sigs


class SigParser:
    def __init__(self, model_name="en_parsigs"):
        self.__language = spacy.load(model_name)
    def parse(self, sig: str):
        return _parse_sig(sig, self.__language)
    def parse_many(self, sigs: list):
        return _parse_sigs(sigs, self.__language)

sig_parser = SigParser(model_name="output/model-best")

sig = "use two puffs into each nostril twice daily for 3 weeks"
parsed_sig = sig_parser.parse(sig)

