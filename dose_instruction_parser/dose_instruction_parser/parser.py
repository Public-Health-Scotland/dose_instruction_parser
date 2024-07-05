import spacy
from dataclasses import dataclass
from itertools import compress, chain
import enlighten
import asyncio

from . import di_prepare
from . import di_frequency
from . import di_dosage
from . import di_duration

@dataclass
class StructuredDI: # pragma: no cover
    """
    A structured dose instruction

    Attributes:
    -----------
    inputID: str
        ID corresponding to input dose instruction.
        Ensures multiple StructuredDIs coming from the same original
        dose instruction are linkable
    text: str
        The free text before parsing
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
    inputID: str
    text: str
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
    di_preprocessed = di_prepare.pre_process(text)
    model_output = model(di_preprocessed)
    entities = model_output.ents 
    return entities

def _parse_di(di: str, model: spacy.Language, input_id=None, pbar=None): 
    """
    1. Preprocesses dose instruction
    2. Applies model to retrieve entities
    3. Creates structured dose instruction from entities using static rules
    """
    if pbar is not None:
        pbar.update()
    try:
        di_preprocessed = di_prepare.pre_process(di)
        model_output = model(di_preprocessed)
        return _create_structured_dis(di, model_output, input_id)
    except Exception:
        print(f"Error when parsing {di}: {Exception}")
        return StructuredDI(inputID=input_id, text=di, 
                            form=None, dosageMin=None, dosageMax=None, 
                            frequencyMin=None, frequencyMax=None, frequencyType=None,
                            durationMin=None, durationMax=None, durationType=None,
                            asRequired=None, asDirected=None)

def _parse_dis(di_lst, model: spacy.Language, rowid_lst=None): # pragma: no cover
    """
    Parses multiple dose instructions at once
    """
    # Progress bar
    manager = enlighten.get_manager()
    status_bar = manager.status_bar('Parsing dose instructions',
                                color="white_on_blue",
                                justify=enlighten.Justify.CENTER)
    pbar = manager.counter(total=len(di_lst), desc="Parsed", unit="instructions")
    rowid_lst = range(len(di_lst)) if rowid_lst is None else rowid_lst
    parsed_dis = di_prepare._flatmap(lambda di, id: _parse_di(di, model, id, pbar), 
                                            *(di_lst, rowid_lst))
    status_bar.color = "white_on_green"
    status_bar.update("Parsing complete")
    return parsed_dis

def _parse_dis_mp(di_lst, model: spacy.Language, rowid_lst=None): # pragma: no cover
    """
    Parses multiple dose instructions at once in parallel (synchronous)
    """
    import multiprocessing as mp

    rowid_lst = range(len(di_lst)) if rowid_lst is None else rowid_lst

    with mp.Pool(mp.cpu_count()) as p:
        parsed_dis = p.starmap(_parse_di, [(di, model, id) for di, id in zip(di_lst, rowid_lst)])
    # Flatten
    parsed_dis = list(chain(*parsed_dis))
    return parsed_dis

def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)

    return wrapped

@background
def _parse_di_async(di, model: spacy.Language, id): # pragma: no cover
    """
    Parses multiple dose instructions at once in parallel (asynchronous)
    """
    return _parse_di(di, model, id)

def _split_entities_for_multiple_instructions(model_entities):
    """
    Automatically determines if multiple dose instructions are included
    within one input dose instruction. If so, splits up the dose instruction.
    """
    result = []
    seen_labels = set()
    current_info = blank_di_dict.copy()
    ignore_next_frequency = False
    for entity in model_entities:
        # Ignore some entities 
        keep_entity = _keep_entity(entity, seen_labels)
        if entity.label_ == "FREQUENCY" and ignore_next_frequency is True:
            keep_entity = False
            ignore_next_frequency = False
        # If ignoring a dosage, ignore the corresponding frequency
        ignore_next_frequency = (entity.label_ == "DOSAGE" and keep_entity is False)
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


blank_di_dict = {"DOSAGE": None, "FREQUENCY": None, "FORM": None, 
                    "DURATION": None, "AS_REQUIRED": None, "AS_DIRECTED": None} # pragma: no cover

def _keep_entity(entity, seen_labels): # pragma: no cover
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
        if entity.label_ == "FORM":
            return False
        if entity.label_ == "DOSAGE":
            if any(x in entity.text.split() for x in ("max", "maximum", "up", "upto", "8")):
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
          corresponding frequencies and durations joined by "and"
        2. Dose instructions with the same frequency type and duration None
          are combined by adding the dosages together
    """
    # 1.
    keep_mask = [True]*len(result)
    add_index = None
    for i in range(len(result[:-1])):
        if result[i]["DOSAGE"] == result[i+1]["DOSAGE"]:
            for ent in ["FREQUENCY", "DURATION"]:
                if add_index == None:
                    add_index = i
                if result[i+1][ent] is not None:
                    if result[i+1][ent] != result[add_index][ent]:
                        if result[add_index][ent] is None:
                            result[add_index][ent] = result[i+1][ent]
                        else:
                            result[add_index][ent] = result[add_index][ent] + \
                            " and " + result[i+1][ent]
                keep_mask[i+1] = False
                add_index = None
        else:
            add_index = None
    result = list(compress(result, keep_mask))
    # 2. 
    keep_mask = [True]*len(result)
    add_index = None
    for i in range(len(result[:-1])):
        freq1 = di_frequency.get_frequency_type(result[i]["FREQUENCY"])
        freq2 = di_frequency.get_frequency_type(result[i+1]["FREQUENCY"])
        if (freq1 == freq2) \
            and (result[i]["DURATION"] is None) and (result[i+1]["DURATION"] is None):
            if add_index == None:
                add_index = i
            if result[i+1]["DOSAGE"] is not None:
                if result[add_index]["DOSAGE"] is not None:
                    result[add_index]["DOSAGE"] = result[add_index]["DOSAGE"] + \
                        " and " + result[i+1]["DOSAGE"]
                else:
                    result[add_index]["DOSAGE"] = result[i+1]["DOSAGE"]
                try:
                    freq1 = freq1.lower()
                except:
                    pass
                result[add_index]["FREQUENCY"] = freq1
            keep_mask[i+1] = False
        else:
            add_index = None
    result = list(compress(result, keep_mask))
    return result
    
def _create_structured_di(free_text, model_entities, input_id=None, 
                            form=None, asRequired=False, asDirected=False):
    """
    Creates a StructuredDI from model entities.
    """
    structured_di = StructuredDI(input_id, free_text, form, None, None, None, None, 
                                    None, None, None, None, asRequired, asDirected)
    for label, text in model_entities.items(): 
        if text is None:
            continue
        elif label == 'FORM':
            if structured_di.form is None:
                form = di_dosage._to_singular(text)
                if form is not None:
                    structured_di.form = form
        elif label == 'DOSAGE':
            min, max, form, = di_dosage.get_dosage_info(text)
            structured_di.dosageMin = min
            structured_di.dosageMax = max
            if form is not None:
                structured_di.form = form
        elif label == 'FREQUENCY':
            min, max, freqtype = di_frequency.get_frequency_info(text)
            structured_di.frequencyMin = min
            structured_di.frequencyMax = max
            if freqtype is not None:
                structured_di.frequencyType = freqtype
        elif label == 'DURATION':
            min, max, durtype = di_duration.get_duration_info(text)
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

def _create_structured_dis(free_text, model_output, input_id=None):
    """
    Creates StructuredDIs from a model output.
    1. Gets entities
    2. Determines whether multiple instructions present 
    3. Creates a StructuredDI for each instruction
    """
    entities = _get_model_entities(model_output)
    multiple_instructions = _split_entities_for_multiple_instructions(entities)
    first_di = _create_structured_di(free_text, multiple_instructions[0], input_id)
    # incase multiple instructions exist, they apply to the same drug and form
    other_dis = [_create_structured_di(free_text, instruction_entities, 
                                        first_di.inputID, 
                                        first_di.form, first_di.asRequired,
                                        first_di.asDirected)
                  for instruction_entities in multiple_instructions[1:]]
    return [first_di] + other_dis


class DIParser:
    """
    Dose instruction parser class 
    """
    def __init__(self, model_name):
        self.__language = spacy.load(model_name)
    def parse(self, di: str):
        return _parse_di(di, self.__language)
    def parse_many(self, dis: list, rowids=None):
        return _parse_dis(dis, self.__language, rowids)
    def parse_many_mp(self, dis: list, rowids=None):
        return _parse_dis_mp(dis, self.__language, rowids)
    def parse_many_async(self, dis: list, rowids=None):
        rowids = range(len(dis)) if rowids is None else rowids
        loop = asyncio.get_event_loop()
        looper = asyncio.gather(*[_parse_di_async(di, self.__language, rowid) for di, rowid in zip(dis, rowids)],
                                    return_exceptions = False)
        results = loop.run_until_complete(looper)
        results = [r for sublist in results for r in sublist]
        loop.close()
        return results
