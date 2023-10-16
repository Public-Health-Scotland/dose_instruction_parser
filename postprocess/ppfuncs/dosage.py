import inflect
import re

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

def _get_dosage_info(text):
    print("DOSAGE: " + text)
    form = None
    freqtype = None
    if "max" in text:
        min = 0
        nums = re.findall('\d+', text)
        if len(nums) != 1:
            warnings.warn("More than one number found for max dosage")
            max = nums[-1]
        else:
            max = nums[0]   
    elif any(x in text for x in ("to", "-")):
        substrs = re.split("to|-", text)
        if len(substrs) == 2:
            if "up" in substrs[0]:
                min = 0
            else:
                min = float(substrs[0])
            max = float(substrs[1])
        else:
            min = float(substrs[0])
            max = float(substrs[0])
    elif text.split()[0].replace('.','',1).isdigit():
        dosage = float(text.split()[0])
        min = dosage
        max = dosage
        freqtype = ppfrequency._get_frequency_type(text)
        form_from_dosage = _get_form_from_dosage_tag(text)
        if form_from_dosage is not None:
            form = _to_singular(form_from_dosage)
    # Check for e.g. "mg", "ml"
    else:
        measures = [ele for ele in ["mg", "ml"] if(ele in text)]
        if bool(measures):
            form = measures[0]
            dosage = text.replace(measures[0],"")
            # TODO: min and max
            min = dosage
            max = dosage
        # Otherwise extract first number to use as dosage
        else:
            nums = re.findall('\d+', text)
            # TODO: min and max
            dosage = nums[0]
            min = dosage
            max = dosage

    return min, max, form, freqtype