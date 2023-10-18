import inflect
import re
import warnings
from functools import reduce

import di_parser.parserfuncs.frequency as pfrequency

def _is_str_float(s):
    """
    Whether a string can be cast to a float

    Input:
        s: str
            A string to test
    Output:
        bool    
            Whether string can be cast to float 
    """
    try:
        float(s)
        return True
    except ValueError:
        return False

# Not v sophisticated - just takes e.g. "2 tabs" and gets 2nd word "tabs"
def _get_form_from_dosage_tag(text):
    """
    Gets the form from dose entity text

    Input:
        text: str
            Dose entity text
            e.g. "2 tablets", "30ml spoonful", "1 puff"
    Output:
        str, None
            The form extracted from the text
            e.g. "tablets", "spoonful", "puff"
    """
    splitted = text.split(' ')
    if len(splitted) == 2:
        if _is_str_float(splitted[1]):
            return None
        else:
            return splitted[1]

# Words that preface a dosage
dose_words = ['take', 'inhale', 'instill', 'apply', 'spray', 'swallow']

# Not sure how useful this is given most dose texts don't have a dose word in them
def _get_single_dose(text):
    """
    Gets dose if it's of the form 
        dose word + number + ...
    e.g. "take 3 tablets", "inhale 1 puff", "apply 2 patches"

    Input:
        text: str
            Dose entity text
            e.g. "take 3 tablets", "inhale 1 puff", "drink 100ml"
    Output:
        str, None
            Dose
            e.g. 3.0, 1.0, None
    """
    def is_followed_by_number(word):
        return word in dose_words
    words = text.split()
    if is_followed_by_number(words[0]) and len(words) > 1 and _is_str_float(words[1]):
        return float(words[1])
    return None

inflect_engine = inflect.engine()

def _to_singular(word):
    """
    Converts word to singular if it's plural, else keeps as is

    Input:  
        word: str  
            A form word
            e.g. "tablets", "pill", "puffs", "octopodes"
    Output:
        str
            Singular version of word if available
            e.g. "tablet", "pill", "puff", "octopus"
    """
    singular = inflect_engine.singular_noun(word)
    return singular if singular else word

def _get_continuous_dose(text):
    """
    Gets dose information for a dosage of mg or ml (continuous)

    Input:
        text: str
            Dose entity text
            e.g. "3 5ml spoonfuls", "1 tablet", "10-20mg"
    Output:
        min: float
            Minimum dose if continuous, else None
            e.g. 15.0, None, 10.0
        max: float
            Maximum dose if continuous, else None
            e.g. 15.0, None, 20.0
        form: str
            Form if continuous, else None
            e.g. "ml", None, "mg"
    """
    measures = [ele for ele in ["mg", "ml"] if(ele in text)]
    if bool(measures):
        if len(measures) > 1:
            warnings.warn("More than one type of dosage continuous measure: " + str(measures) + 
            ". Using " + str(measures[0]) + ".")
        form = measures[0]
        min, max = pfrequency._get_range(text.replace(measures[0], ""))
        if min is None:
            dose_nums = re.findall(pfrequency.re_digit, re.sub(",", "", text))
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
    """ 
    Get information about dosage given a dosage entity text

    Input:
        text: str
            A dosage entity text 
            e.g. "2x10ml", "2-3", "max 4"
    Output:
        min: float
            The minimum dosage 
            e.g. 20.0, 2.0, 0.0
        max: float
            The maximum dosage 
            e.g. 20.0, 3.0, 4.0
        form: str
            The form of dosage if present
            e.g. "ml", None, None
    """
    print("DOSAGE: " + text)
    form = None
    # Check for e.g. "mg", "ml"
    min, max, form = _get_continuous_dose(text)
    if min is None:
        # Check for range of doses
        min, max = pfrequency._get_range(text)   
    # Where there is no dose range min and max are the same
    if min is None:
        # If first part of tag is a number this is the dosage
        if text.split()[0].replace('.','',1).isdigit():
            dosage = float(text.split()[0])
            min = dosage
            max = dosage
            form_from_dosage = _get_form_from_dosage_tag(text)
            if form_from_dosage is not None:
                form = _to_singular(form_from_dosage)
            # Otherwise extract first number to use as dosage
        else:
            nums = re.findall(pfrequency.re_digit, re.sub(",", "", text))
            if len(nums) > 0:
                dosage = nums[0]
                min = dosage
                max = dosage
            else:
                min = None
                max = None
    return min, max, form