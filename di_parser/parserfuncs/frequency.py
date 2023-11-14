from dataclasses import dataclass
import re
import warnings

# Regex expression to search for numbers in text
re_digit = "\d*\.?\d+"

@dataclass(frozen=True, eq=True)
class _Frequency:
    """
    A structured frequency 
    Attributes:
    -----------
    frequencyType: str
        The type of frequency for the dosage (e.g. Hour, Day, Week, Month)
    frequency: int
        The number of times per frequencyType that the dose is taken
    """
    frequencyType: str
    frequency: int

latin_frequency_types = {"qd": _Frequency("Day", 4.0), "qds": _Frequency("Day", 4.0),
                        "bid": _Frequency("Day", 2.0), 
                        "bd": _Frequency("Day", 2.0), "tid": _Frequency("Day", 3.0), 
                        "qid": _Frequency("Day", 4.0)}

def _get_latin_frequency(frequency):
    """
    Inputs:
        frequency: str
            A string for dose instruction frequency
    Outputs:
        None
            If frequency doesn't contain a latin frequency type from 
            latin_frequency_types, e.g. "qid"
        _Frequency object
            If frequency does contain a latin frequency type
    """
    for latin_freq in latin_frequency_types.keys():
        if latin_freq in frequency:
            return latin_frequency_types[latin_freq]

def _get_frequency_type(frequency):
    """
    Gets the frequency type from a frequency string
    
    Inputs:
        frequency: str
            A string for dose instruction frequency
            e.g. "daily"
    Outputs:
        frequency type: str
            The type of frequency associated with the dose instruction
            e.g. "Day"
    """
    if frequency is not None:
        if any(x in frequency for x in ("hour", "hr")) | (re.search("\d?h$", frequency) is not None):
            return "Hour"
        if any(x in frequency for x in ("week", "wk")):
            return "Week"
        if any(x in frequency for x in ("month", "mnth", "mon ")):
            return "Month"
        if any(x in frequency for x in ("year", "yr")):
            return "Year"
        if any(daily_instruction in frequency for daily_instruction in
               ("day", "daily", "night", "morning", "evening", "noon", "bedtime", "bed",
               "breakfast", "tea", "lunch", "dinner", "meal", "nocte", "mane", "feed")):
            return "Day"
        latin_freq = _get_latin_frequency(frequency)
        if latin_freq:
            return latin_freq.frequencyType

def _get_number_of_times(frequency):
    """
    Gets the number of times a dose must be taken per frequencyType

    Inputs:
        frequency: str
            A string for dose instruction frequency
            e.g. "daily"
    Outputs:
        number of times: float   
            The number of times per frequencyType the dose is taken
            e.g. 1.0
    """
    if frequency is not None:
        for word in frequency.split():
            if word.isdigit():
                return int(word)
        # every other TIME_UNIT means every 2 days, weeks etc
        if "other" in frequency:
            return 0.5
        latin_freq = _get_latin_frequency(frequency)
        if latin_freq:
            return latin_freq.frequency
        if any(x in frequency for x in ("meals", "feed", "food")):
            return 3.0
        if any(x in frequency for x in ("bed", "morning", "daily", "night", 
            "noon", "breakfast","tea", "lunch", "dinner", "mane", "nocte")):
            return 1.0

def _get_bounding_num(nums, bound_type):
    """
    Gets the min or max from a list of numbers. Fills in the other
    bound accordingly; if you're trying to get the minimum then the max
    will be None e.g. "at least 2 tablets" the max is unknown. If you're
    trying to get the maximum then the min will be zero e.g. "up to 3 puffs"
    the min is 0 here.

    Input:
        nums: list(str)
            List of strings of numbers extracted from text
            e.g. ["2", "3", "0.5"]
        bound_type: str; ("min", "max")
            Whether to extract the min or max number

    Output:
        _min: float
            The value for minimum dose or frequency
        _max: float
            The value for maximum dose or frequency
    """
    if bound_type not in ("min", "max"):
        raise ValueError("bound_type must be one of: ('min', 'max')")
    elif len(nums) == 0:
        return None, None
    else:
        if len(nums) > 1:
            warnings.warn("More than one number found for bounding number")
            print(nums)
        if bound_type == "min":
            bound = min(nums)
            return float(bound), None
        elif bound_type == "max":
            bound = max(nums)
            return 0.0, float(bound)

# TODO: standardise output types
def _get_range(text):
    """
    Gets a range of max and min numbers given some text including numbers

    Input:
        text: str
            A dose instruction entity text 
            e.g. "daily", "3 to 5 tablets", "max 6 weeks"
    Output:
        If there is no range (1 value only) returns None

        _min: float or None
            The minimum number of times
            e.g. None, 3.0, 0.0
        _max: float or None
            The maximum number of times
            e.g. None 5.0, 6.0
    """
    nums = re.findall(re_digit, text)
    # Check for latin frequencies
    for word in text.split():
        if word in latin_frequency_types.keys():
            nums.append(latin_frequency_types[word].frequency)
    nums = [float(item) for item in nums]
    if any(x in text for x in ("max", "upto", "up to")):
        _min, _max = _get_bounding_num(nums, "max")
    elif any(x in text for x in ("at least", "min")):
        if len(nums) == 0:
            if " a " in text:
                _min = 1.0
            else:
                _max = None
        else:
            _min, _max = _get_bounding_num(nums, "min")
    elif any(x in text for x in (" to ", "-", " or ")):
        if len(nums) == 0:
            _min = None
            _max = None
        else:
            _min = min(nums)
            _max = max(nums)
    elif "and" in text:
        substrs = re.split("and|,", text)
        nums = [float(_get_number_of_times(s)) for s in substrs]
        num = sum([num for num in nums if num is not None])
        _min = num
        _max = num
    else:
        _min = None
        _max = None
    return _min, _max

def _get_frequency_info(text):
    """ 
    Get information about frequency given a frequency entity text

    Input:
        text: str
            A frequency entity text 
            e.g. "daily", "with meals and at bedtime", "2 to 5 times a week"
    Output:
        _min: float
            The minimum number of times per freqtype
            e.g. 1.0, 4.0, 2.0 
        _max: float
            The maximum number of times per freqtype
            e.g. 1.0, 4.0, 5.0
        freqtype: str
            The frequency type
            e.g. "Day", "Day", "Week"

    """
    freqtype = _get_frequency_type(text)
    _min, _max = _get_range(text)
    if _min is None:
        freq = _get_number_of_times(text)
        _min = freq
        _max = freq
    if _min is None:
        nums = re.findall(re_digit, re.sub(",", "", text))
        if len(nums) == 1:
            _min = float(nums[0])
            _max = float(nums[0])
        elif len(nums) == 2:
            _min = float(nums[0])
            _max = float(nums[1])
        else:
            _min = None
            _max = None
    # Default added only if there is a frequency tag in the di
    # handles cases such as "Every TIME_UNIT"
    if _min is None:
        _min = 1.0
        _max = 1.0
    return _min, _max, freqtype

