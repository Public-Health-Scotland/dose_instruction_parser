import sys
from pathlib import Path

import spacy
from word2number import w2n
from dataclasses import dataclass
import re
from spacy import Language
from itertools import chain
import copy
import os
from spellchecker import SpellChecker
import warnings


import inflect
# TODO handle multiple instructions in one sentence
# TODO Create Pypi distribution

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


@dataclass
class StructuredSig:
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


dose_instructions = ['take', 'inhale', 'instill', 'apply', 'spray', 'swallow']
number_words = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]

default_model_name = "en_parsigs"

inflect_engine = inflect.engine()

def _create_spell_checker():
    sc = SpellChecker()
    keep_words_frequency ="example/keep_words.txt"
    #drug_words_frequency = 'example/drug_names.txt'
    sc.word_frequency.load_text_file(keep_words_frequency)
    #sc.word_frequency.remove_words(["talbot"])
    return sc


spell_checker = _create_spell_checker()


@dataclass(frozen=True, eq=True)
class _Frequency:
    frequencyType: str
    interval: int


# TODO add qXd support
latin_frequency_types = {"qd": _Frequency("Day", 1), "bid": _Frequency("Day", 2), "tid": _Frequency("Day", 3),
                         "qid": _Frequency("Day", 4)}


def _flatmap(func, iterable):
    return list(chain.from_iterable(map(func, iterable)))
"""
Converts a medication dosage instructions string to a StructuredSig object.
The input string is pre processed, and than combining static rules and NER model outputs, a StructuredSig object is created.
"""


def _parse_sigs(sig_lst, model: Language):
    return _flatmap(lambda sig: _parse_sig(sig, model), sig_lst)


def _parse_sig(sig: str, model: Language):
    sig_preprocessed = _pre_process(sig)
    model_output = model(sig_preprocessed)
    return _create_structured_sigs(model_output)


def _autocorrect(sig):
    sig = sig.lower().strip()
    corrected_words = []
    for word in sig.split():
        # checking if the word is only letters
        if not re.match(r"^[a-zA-Z]+$", word) or spell_checker.known([word]):
            corrected_words.append(word)
        else:
            corrected_word = spell_checker.correction(word)
            corrected_words.append(corrected_word)
    sig = ' '.join(corrected_words)
    return sig


def _pre_process(sig):
    sig = _autocorrect(sig)
    sig = sig.replace('twice', '2 times').replace("once", '1 time').replace("nightly", "every night")
    sig = _add_space_around_parentheses(sig)
    # remove extra spaces between words
    sig = re.sub(r'\s+', ' ', sig)
    output_words = []
    words = sig.split()
    for word in words:
        if word == 'tab':
            word = word.replace('tab', 'tablet')
        elif word == 'tabs':
            word = word.replace('tabs', 'tablets')
        output_words.append(word)
    sig = ' '.join(output_words)
    sig = _convert_words_to_numbers(sig)
    return _convert_fract_to_num(sig)


def _add_space_around_parentheses(s):
    s = re.sub(r'(?<!\s)\(', r' (', s)
    s = re.sub(r'\)(?!\s)', r') ', s)
    return s


"""
Converts the preprocessed sig using static rules and the model outputs
"""

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


# Not v sophisticated - just takes e.g. "2 tabs" and gets 2nd word "tabs"
def _get_form_from_dosage_tag(text):
    splitted = text.split(' ')
    if len(splitted) == 2:
        return splitted[1]

def _to_singular(text):
    # turn to singular if plural else keep as is
    singular = inflect_engine.singular_noun(text)
    return singular if singular else text

def _create_structured_sig(model_entities, form=None, asRequired=False, asDirected=False):
    structured_sig = StructuredSig(form, None, None, None, None, 
                                    None, None, None, None, asRequired, asDirected)
    for entity in model_entities:
        text = entity.text
        label = entity.label_
        if label == 'DOSAGE':
            print(text)
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
                # TODO: min and max here
                dosage = float(text.split()[0])
                structured_sig.dosageMin = dosage
                structured_sig.dosageMax = dosage
                structured_sig.frequencyType = _get_frequency_type(text)
                form_from_dosage = _get_form_from_dosage_tag(text)
                if form_from_dosage is not None:
                    structured_sig.form = _to_singular(form_from_dosage)
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
            structured_sig.form = _to_singular(text)
        elif label == 'FREQUENCY':
            structured_sig.frequencyType = _get_frequency_type(text)
            # TODO: min and max
            freq = _get_interval(text)
            structured_sig.frequencyMin = freq
            structured_sig.frequencyMax = freq
            # Default added only if there is a frequency tag in the sig
            # handles cases such as "Every TIME_UNIT"
            if structured_sig.frequencyMin is None:
                structured_sig.frequencyMin = 1
                structured_sig.frequencyMax = 1
        elif label == 'DURATION':
            structured_sig.durationType = _get_frequency_type(text)
            # TODO: min and max
            duration = _get_interval(text)
            structured_sig.durationMin = duration
            structured_sig.durationMax = duration
        elif label == "AS_REQUIRED":
            structured_sig.takeAsRequired = True
        elif label == "AS_DIRECTED":
            structured_sig.takeAsDirected = True
        else:
            continue
    return structured_sig


def _get_model_entities(model_output):
    entities = model_output.ents
    return entities


def _is_number_word(word):
    return word in number_words


def _get_duration_string(sig):
    words = sig.split()
    for i in range(len(words)):
        if words[i] == 'for':
            return ' '.join(words[i:])
    return None


def _convert_fract_to_num(sentence):
    def is_frac(_word):
        nums = _word.split('/')
        return len(nums) == 2 and '/' in _word and nums[0].isdigit() and nums[1].isdigit()
    words = sentence.split()
    output_words = []
    for word in words:
        if is_frac(word):
            num, denom = word.split('/')
            output_words.append(str(int(num) / int(denom)))
        else:
            output_words.append(word)
    return ' '.join(output_words)


def _convert_words_to_numbers(sentence):
    words = sentence.split()
    output_words = []
    for word in words:
        if _is_number_word(word):
            output_words.append(str(w2n.word_to_num(word)))
        else:
            output_words.append(word)
    return ' '.join(output_words)


def _get_single_dose(sig):
    def is_followed_by_number(word):
        return word in dose_instructions
    words = sig.split()
    if is_followed_by_number(words[0]) and len(words) > 1 and _is_str_float(words[1]):
        return float(words[1])
    return None


def _is_str_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def _get_frequency_type(frequency):
    if frequency is not None:
        if "hour" in frequency:
            return "Hour"
        if "week" in frequency:
            return "Week"
        if "month" in frequency:
            return "Month"
        if "year" in frequency:
            return "Year"
        if any(daily_instruction in frequency for daily_instruction in
               ("day", "daily", "night", "morning", "evening", "noon", "bedtime")):
            return "Day"
        latin_freq = _get_latin_frequency(frequency)
        if latin_freq:
            return latin_freq.frequencyType


def _get_interval(frequency):
    if frequency is not None:
        for word in frequency.split():
            if word.isdigit():
                return int(word)
        # every other TIME_UNIT means every 2 days,weeks etc
        if "other" in frequency:
            return 2
        latin_freq = _get_latin_frequency(frequency)
        if latin_freq:
            return latin_freq.interval


def _get_latin_frequency(frequency):
    for latin_freq in latin_frequency_types.keys():
        if latin_freq in frequency:
            return latin_frequency_types[latin_freq]


def _should_take_as_needed(frequency):
    return "as needed" in frequency


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

