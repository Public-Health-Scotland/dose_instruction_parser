from dataclasses import dataclass
import re

re_digit = "\d*\.?\d+"

@dataclass(frozen=True, eq=True)
class _Frequency:
    frequencyType: str
    interval: int

# TODO add qXd support
latin_frequency_types = {"qd": _Frequency("Day", 1), "bid": _Frequency("Day", 2), 
                        "bd": _Frequency("Day", 2),"tid": _Frequency("Day", 3), 
                        "qid": _Frequency("Day", 4)}


def _get_frequency_type(frequency):
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
    if frequency is not None:
        for word in frequency.split():
            if word.isdigit():
                return int(word)
        # every other TIME_UNIT means every 2 days, weeks etc
        if "other" in frequency:
            return 0.5
        latin_freq = _get_latin_frequency(frequency)
        if latin_freq:
            return latin_freq.interval
        if any(x in frequency for x in ("meals", "feed", "food")):
            return 3
        if any(x in frequency for x in ("bed", "morning", "daily", "night", 
            "noon", "breakfast","tea", "lunch", "dinner", "mane", "nocte")):
            return 1

def _get_latin_frequency(frequency):
    for latin_freq in latin_frequency_types.keys():
        if latin_freq in frequency:
            return latin_frequency_types[latin_freq]

# TODO: standardise output types
def _get_range(text):
    if any(x in text for x in ("max", "upto", "up to")):
        min = 0
        nums = re.findall(re_digit, re.sub(",", "", text))
        if len(nums) != 1:
            warnings.warn("More than one number found for max")
            max = nums[-1]
        else:
            max = nums[0]   
    elif any(x in text for x in (" to ", "-", " or ")):
        substrs = re.split("to|-|or", text)
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
            min = float(re.findall(re_digit,substrs[0])[0])
            max = float(re.findall(re_digit,substrs[0])[0])
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
            min = nums[0]
            max = nums[0]
        elif len(nums) == 2:
            min = nums[0]
            max = nums[1]
        else:
            min = None
            max = None
    # Default added only if there is a frequency tag in the di
    # handles cases such as "Every TIME_UNIT"
    if min is None:
        min = 1
        max = 1
    return min, max, freqtype

