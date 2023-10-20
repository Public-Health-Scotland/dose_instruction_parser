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

latin_frequency_types = {"qd": _Frequency("Day", 1.0), "bid": _Frequency("Day", 2.0), 
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

        min: float or None
            The minimum number of times
            e.g. None, 3.0, 0.0
        max: float or None
            The maximum number of times
            e.g. None 5.0, 6.0
    """
    if any(x in text for x in ("max", "upto", "up to", "at least")):
        min = 0.0
        nums = re.findall(re_digit, re.sub(",", "", text))
        if len(nums) > 1:
            warnings.warn("More than one number found for max")
            print(nums)
            max = float(nums[-1])
        elif len(nums) == 0:
            if " a " in text:
                max = 1.0
            else:
                max = None
        else:
            max = float(nums[0])   
    elif any(x in text for x in (" to ", "-", " or ")):
        substrs = re.split(" to |-| or  ", text)
        if len(substrs) == 2:
            if "up" in substrs[0]:
                min = 0
            else:
                try:
                    min = float(re.findall(re_digit, substrs[0])[0])
                except: 
                    try:    
                        min = float(re.findall(re_digit, substrs[1])[0])
                    except:
                        min = None
            try:
                max = float(re.findall(re_digit,substrs[1])[0])
            except: 
                try:
                    max = float(re.findall(re_digit,substrs[0])[0])
                except:
                    max = None
        else:
            try:
                min = float(re.findall(re_digit,substrs[0])[0])
                max = float(re.findall(re_digit,substrs[0])[0])
            except:
                min = None
                max = None
    elif "and" in text:
        substrs = re.split("and|,", text)
        nums = [float(_get_number_of_times(s)) for s in substrs]
        num = sum([num for num in nums if num is not None])
        min = num
        max = num
    else:
        min = None
        max = None
    return min, max

def _get_frequency_info(text):
    """ 
    Get information about frequency given a frequency entity text

    Input:
        text: str
            A frequency entity text 
            e.g. "daily", "with meals and at bedtime", "2 to 5 times a week"
    Output:
        min: float
            The minimum number of times per freqtype
            e.g. 1.0, 4.0, 2.0 
        max: float
            The maximum number of times per freqtype
            e.g. 1.0, 4.0, 5.0
        freqtype: str
            The frequency type
            e.g. "Day", "Day", "Week"

    """
    print("FREQUENCY: " + text)
    freqtype = _get_frequency_type(text)
    min, max = _get_range(text)
    if min is None:
        freq = _get_number_of_times(text)
        min = freq
        max = freq
    if min is None:
        nums = re.findall(re_digit, re.sub(",", "", text))
        if len(nums) == 1:
            min = float(nums[0])
            max = float(nums[0])
        elif len(nums) == 2:
            min = float(nums[0])
            max = float(nums[1])
        else:
            min = None
            max = None
    # Default added only if there is a frequency tag in the di
    # handles cases such as "Every TIME_UNIT"
    if min is None:
        min = 1.0
        max = 1.0
    return min, max, freqtype

