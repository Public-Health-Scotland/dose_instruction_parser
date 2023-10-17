import inflect
import re
import warnings
from functools import reduce

import postprocess.ppfuncs.frequency as ppfrequency

dose_instructions = ['take', 'inhale', 'instill', 'apply', 'spray', 'swallow']

# Not v sophisticated - just takes e.g. "2 tabs" and gets 2nd word "tabs"
def _get_form_from_dosage_tag(text):
    splitted = text.split(' ')
    if len(splitted) == 2:
        return splitted[1]

def _get_single_dose(di):
    def is_followed_by_number(word):
        return word in dose_instructions
    words = di.split()
    if is_followed_by_number(words[0]) and len(words) > 1 and _is_str_float(words[1]):
        return float(words[1])
    return None

inflect_engine = inflect.engine()

def _to_singular(text):
    # turn to singular if plural else keep as is
    singular = inflect_engine.singular_noun(text)
    return singular if singular else text

def _get_continuous_dose(text):
    measures = [ele for ele in ["mg", "ml"] if(ele in text)]
    if bool(measures):
        if len(measures) > 1:
            warnings.warn("More than one type of dosage continuous measure: " + str(measures) + 
            ". Using " + str(measures[0]) + ".")
        form = measures[0]
        min, max = ppfrequency._get_range(text.replace(measures[0], ""))
        if min is None:
            dose_nums = re.findall("\d*\.?\d+", re.sub(",", "", text))
            print(dose_nums)
            if len(dose_nums) > 1:
                # e.g. 2 5ml spoonfuls becomes 10 ml
                dose = str(reduce(lambda x, y: x*y, [float(num) for num in dose_nums]))
            else:
                dose = dose_nums[0]
            min = dose
            max = dose
    else:
        min = None
        max = None
        form = None
    return min, max, form

def _get_dosage_info(text):
    print("DOSAGE: " + text)
    form = None
    freqtype = None
    # Check for e.g. "mg", "ml"
    min, max, form = _get_continuous_dose(text)
    if min is None:
        # Check for range of doses
        min, max = ppfrequency._get_range(text)   
    # Where there is no dose range min and max are the same
    if min is None:
        # If first part of tag is a number this is the dosage
        if text.split()[0].replace('.','',1).isdigit():
            dosage = float(text.split()[0])
            min = dosage
            max = dosage
            freqtype = ppfrequency._get_frequency_type(text)
            form_from_dosage = _get_form_from_dosage_tag(text)
            if form_from_dosage is not None:
                form = _to_singular(form_from_dosage)
            # Otherwise extract first number to use as dosage
        else:
            nums = re.findall("\d*\.?\d+", re.sub(",", "", text))
            # TODO: min and max
            dosage = nums[0]
            min = dosage
            max = dosage
    return min, max, form, freqtype