import inflect
import re
import warnings
from functools import reduce

from . import di_frequency

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
        _min: float
            Minimum dose if continuous, else None
            e.g. 15.0, None, 10.0
        _max: float
            Maximum dose if continuous, else None
            e.g. 15.0, None, 20.0
        form: str
            Form if continuous, else None
            e.g. "ml", None, "mg"
    """
    measures = [ele for ele in ["mg", "ml"] if(ele in text)]
    if bool(measures):
        if len(measures) > 1:
            warnings.warn("More than one type of dosage continuous measure: " + \
                str(measures) + \
                    ". Using " + str(measures[0]) + ".")
        form = measures[0]
        _min, _max = di_frequency._get_range(text) 
        if _min is None:
            dose_nums = re.findall(di_frequency.re_digit, re.sub(",", "", text))
            if len(dose_nums) > 1:
                # e.g. 2 5ml spoonfuls becomes 10 ml
                dose = float(reduce(lambda x, y: x*y, [float(num) for num in dose_nums]))
            elif len(dose_nums) == 0:
                dose = None
            else:
                dose = float(dose_nums[0])
            _min = dose
            _max = dose
    else:
        _min = None
        _max = None
        form = None
    return _min, _max, form

def get_dosage_info(text):
    """ 
    Get information about dosage given a dosage entity text

    Input:
        text: str
            A dosage entity text 
            e.g. "2x10ml", "2-3", "max 4"
    Output:
        _min: float
            The minimum dosage 
            e.g. 20.0, 2.0, 0.0
        _max: float
            The maximum dosage 
            e.g. 20.0, 3.0, 4.0
        form: str
            The form of dosage if present
            e.g. "ml", None, None
    """
    form = None
    # Check for e.g. "mg", "ml"
    _min, _max, form = _get_continuous_dose(text)
    if _min is None:
        # Check for range of doses
        _min, _max = di_frequency._get_range(text)   
    # Where there is no dose range _min and max are the same
    if _min is None:
        # If first part of tag is a number this is the dosage
        if text.split()[0].replace('.','',1).isdigit():
            dosage = float(text.split()[0])
            _min = dosage
            _max = dosage
            form_from_dosage = _get_form_from_dosage_tag(text)
            if form_from_dosage is not None:
                form = _to_singular(form_from_dosage)
            # Otherwise extract first number to use as dosage
        else:
            nums = re.findall(di_frequency.re_digit, re.sub(",", "", text))
            if len(nums) > 0:
                dosage = float(nums[0])
                _min = dosage
                _max = dosage
            else:
                _min = None
                _max = None
    return _min, _max, form