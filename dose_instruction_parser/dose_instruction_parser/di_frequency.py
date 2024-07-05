from dataclasses import dataclass
from itertools import compress
import re
import warnings

# Regex expression to search for numbers in text
re_digit = r"\d*\.?\d+"

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
                        "bid": _Frequency("Day", 2.0), "b/d": _Frequency("Day", 2.0),
                        "bd": _Frequency("Day", 2.0), "tid": _Frequency("Day", 3.0), 
                        "qid": _Frequency("Day", 4.0), "tds": _Frequency("Day", 3.0)}

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

frequency_numbers = {"second": 2, "third": 3, "fourth": 4, "fifth": 5,
                    "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9}

freqtype_conversion = {"7 Day": "Week", "24 Hour": "Day", "48 Hour": "2 Day",
                        "14 Day": "2 Week", "4 Week" : "Month"}

def get_frequency_type(frequency):
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
    freq_type = None
    if frequency is None:
        return None
    if any(x in frequency for x in ("hour", "hr")) | \
        (re.search(r"\dh$", frequency) is not None):
        freq_type = "Hour"
    elif any(x in frequency for x in ("week", "wk", "monday",
                                        "tuesday", "wednesday", "thursday",
                                        "friday", "saturday", "sunday", 
                                        "tue", "wed", "thu", "fri", "sat", "sun")):
        freq_type = "Week"
    elif "fortnight" in frequency:
        freq_type = "2 Week"
    elif any(x in frequency for x in ("month", "mnth", "mon ")):
        freq_type = "Month"
    elif any(x in frequency for x in ("year", "yr")):
        freq_type = "Year"
    elif any(x in frequency for x in
            ("day", "daily", "b/d", "bd", "night", "morning", "evening", "noon", "bedtime", "bed",
            "breakfast", "tea", "lunch", "dinner", "meal", "nocte", "mane", "feed", "am", "pm",
            "tds", "qds")):
        freq_type = "Day"
    latin_freq = _get_latin_frequency(frequency)
    if latin_freq:
        freq_type = latin_freq.frequencyType
    # Check for multiple units of frequency type e.g. every 2 days
    freq_type = _add_frequency_multiple_units(frequency, freq_type)
    # Convert e.g. "24 Hour" -> "Day"
    if freq_type in freqtype_conversion.keys():
        freq_type = freqtype_conversion[freq_type]
    return freq_type

def _add_frequency_multiple_units(frequency, freq_type):
    """
    Checks if frequency type is for multiples of frequency unit
    e.g. "every 2 hours" or "alternate days"

    Inputs:
    -------
        frequency: str
            Frequency NER text
            e.g. "every 6 hours", "alternate days"
        freq_type: str (None)
            Current frequency type identified
            e.g. "Hour", "Day"
    Outputs:
        freq_type with multiples added
        e.g. "6 Hour", "2 Day"
    """
    if any(x in frequency for x in ("alternate", "every other")):
        freq_type = "2 " + freq_type 
    if any(x in frequency for x in ("every", "hrly", "hourly")):
        nums = re.findall(re_digit, frequency)
        # Deal with words like third, fifth etc.
        for word in frequency.split():
            if word in frequency_numbers.keys():
                nums.append(str(frequency_numbers[word]))
        if len(nums) == 0:
            return freq_type
        if len(nums) != 1:
            warnings.warn("More than one number for every x time unit. Using lowest unit.")
        try:
            freq_type = min(nums) + " " + freq_type
        except TypeError:
            pass
    return freq_type

def _get_number_of_times(frequency, default=None):
    """
    Gets the number of times a dose must be taken per frequencyType
    Only use if no range of times is present

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
        words = frequency.split()
        if any(x in frequency for x in ("am", "pm")):
            indexes = [i for i in range(len(words)) if words[i] in ("am", "pm")]
            # Removing the time e.g. for "8 am" -> "am" so the 8 doesn't get
            # picked up as 8 times a day
            try:
                for index in indexes:
                    del words[index-1]
            except:
                pass
        for word in words:
            if word.isdigit():
                return float(word)
        latin_freq = _get_latin_frequency(frequency)
        if latin_freq:
            return latin_freq.frequency
        if any(x in frequency for x in ("meals", "feed", "food")):
            return 3.0
        if any(x in frequency for x in ("bed", "morning", "daily", "night", "evening",
            "noon", "breakfast","tea", "lunch", "dinner", "mane", "nocte", "day")):
            return 1.0
        else:
            return default

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
        if bound_type == "min":
            bound = min(nums)
            return float(bound), None
        elif bound_type == "max":
            bound = max(nums)
            return 0.0, float(bound)

def _check_min_max_amount(text, nums):
    """
    Checks whether can find a range of values using the pattern
    of "at least x" or "up to x" etc.

    Input:
    ------
        text: str
            text to look for pattern in 
            e.g. "max 4"
        nums: list of floats
            numbers identified from text
    Output:
    -------
        _min: float (None)
            minimum of range
        _max: float (None)
            maximum of range
        range_found: bool
            whether range successfully found
    """
    if any(x in text for x in ("max", "upto", "up to", "Maximum")):
        _min, _max = _get_bounding_num(nums, "max")
        if _max is None:
            if " a " in text:
                _max = 1.0
                _min = 0.0
                range_found = True
            else:
                range_found = False
        if _max is not None:
            range_found = True
    elif any(x in text for x in ("at least", "min")):
        if len(nums) == 0:
            range_found = True
            if (" a " in text) or text.endswith(" a"):
                _min = 1.0
                _max = None
            else:
                _min = None
                _max = None
        else:
            _min, _max = _get_bounding_num(nums, "min")
            range_found = True
    else:
        _min = None
        _max = None
        range_found = False
    return _min, _max, range_found

def _check_explicit_range(text, nums):
    """
    Checks whether a range of numbers can be found by looking
    for an explicitly stated range using "to", "-" or "or",
    e.g. "3-4 tablets", "1 to 2 days"

    Input:
    ------
        text: str
            text to look for pattern in 
            e.g. "2 to 4"
        nums: list of floats
            numbers identified from text
    Output:
    -------
        _min: float (None)
            minimum of range
        _max: float (None)
            maximum of range
        range_found: bool
            whether range successfully found
    """
    if any(x in text for x in (" to ", "-", " or ")):
        words = text.split()
        indexes = [i for i in range(len(words)) if words[i] in ("to", "-", "or")]
        try:
            assert len(indexes) == 1,\
                 "More than one instance of ('to', '-', 'or') in phrase"
            index = indexes[0]
            _min = float(words[index-1])
            _max = float(words[index+1])
            range_found = True
        except:
            min_nums = min(nums, default=None)
            max_nums = max(nums, default=None)
            _min = float(min_nums) if min_nums is not None else min_nums
            _max = float(max_nums) if max_nums is not None else max_nums
            range_found = True
        # If there is a third number e.g. 2 to 4 5ml spoonfuls
        # need to multiply 2 and 4 by 5 to get total ml
        if len(nums) > 2 and len(indexes) == 1:
            mindexes = [i for i in range(len(words)) if words[i] in ("ml", "mg")]
            if len(mindexes) != 0:
                if len(mindexes) != 1:
                    warnings.warn("More than one instance of ('ml', 'mg') in phrase")
                mindex = mindexes[0]
                try:
                    multiplier = float(words[mindex-1])
                    _min *= multiplier
                    _max *= multiplier
                    range_found = True
                except:
                    pass
    else:
        _min = None
        _max = None
        range_found = False
    return _min, _max, range_found

def _check_range_from_list(text):
    """
    Checks whether a range of numbers can be found by looking
    for a list of times
    e.g. "8am and 6pm"

    Input:
    ------
        text: str
            text to look for pattern in 
            e.g. "8 am and 6pm" -> (2.0, 2.0, True) as this is 2 times a day
    Output:
    -------
        _min: float (None)
            minimum of range
        _max: float (None)
            maximum of range
        range_found: bool
            whether range successfully found
    """
    if any(x in text for x in ("and", " / ", " ; ")):
        # Remove "/ day" or "/ d"
        text = text.replace("/ day", " ").replace("/ d", " ")
        substrs = re.split(r"and|,|\/|;", text)
        nums = [float(_get_number_of_times(s, default=0.0)) for s in substrs]
        if any(x in text for x in ("am", "pm")):
            _min = float(len(nums))
            _max = float(len(nums))
            range_found = True
        else:
            num = float(sum([num for num in nums if num is not None]))
            _min = num
            _max = num
            range_found = True
    else:
        _min = None
        _max = None
        range_found = False
    return _min, _max, range_found

def _get_range(text, default=None):
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
    for word in re.split(r"[ :;\-,]", text):
        if word in latin_frequency_types.keys():
            nums.append(latin_frequency_types[word].frequency)
    nums = [float(item) for item in nums]
    # Initially we have not found a range to return
    # Searching for valid range using multiple rules
    range_found = False
    _min, _max, range_found = _check_min_max_amount(text, nums)
    if not range_found:
        _min, _max, range_found = _check_explicit_range(text, nums)
    if not range_found:
        _min, _max, range_found = _check_range_from_list(text)
    if not range_found:
        if len(nums) >=2 and not any(x in text for x in (" x ", " ml ", " mg ")):
            _min = min(nums)
            _max = max(nums)
            range_found = True
    # Found no range
    if not range_found:
        _min = default
        _max = default
    return _min, _max

def _get_hourly_adjusted_frequency(text):
    """
    Gets frequency min, max and type where instruction specifies
    "x hourly" or "x hrly".

    Adjusts min and max to avoid double counting e.g. "six hourly"
    - > 1.0, 1.0, '6 Hour' rather than 6.0, 6.0, '6 Hour'.

    Input:
    ------
        text (str)
            NER frequency tag to extract information from
            e.g. "6 hourly"
    Output:
    -------
        _min: float
            The minimum number of times per freqtype
            e.g. 1.0
        _max: float
            The maximum number of times per freqtype
            e.g. 1.0
        freqtype: str
            The frequency type
            e.g. '6 Hour'
    """
    match = re.findall("hourly|hrly", text)
    if len(match) != 1:
        warnings.warn("More than one use of hourly/hrly, taking first instance.")
    match = match[0]
    freqtype = get_frequency_type(text)
    words = text.split()
    number_words = [word.replace(".","").isnumeric() for word in words]
    # Find number words immediately preceeding "hourly/hrly" and remove
    remove = [1]*len(words)
    try:
        for i in range(words.index(match), -1, -1):
            if number_words[i] or (words[i] in ("/","-","\\",";", "times", match)):
                remove[i] = 0
            else:
                break
    except:
        warnings.warn(f"Not in list: {words}")
    words = list(compress(words, remove))
    _min, _max = _get_range(" ".join(words), default=1.0)
    return _min, _max, freqtype

def get_frequency_info(text):
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
    # Consider "2-5 times every 4 weeks"
    # The part before "every" is used to determine frequency e.g. min 2, max 5
    # The part after is used to determine freq type e.g. "month"
    if "every" in text:
        # Split on every
        before, after = text.split("every", 1)
        # Get all numbers
        freqtype = get_frequency_type("every" + after)
        _min, _max = _get_range(before)
        # Replacing "text" with "before" as now we only want to 
        # consider 1st half of expression
        text = before
    # e.g. take 2 tablets 6 hrly
    elif any(x in text for x in ("hrly", "hourly")):
        _min, _max, freqtype = _get_hourly_adjusted_frequency(text)
    else:
        freqtype = get_frequency_type(text)
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
    if _min is None:
        _min = 1.0
        _max = 1.0
    return _min, _max, freqtype

