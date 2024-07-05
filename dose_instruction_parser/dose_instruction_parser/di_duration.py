import re
from . import di_frequency 

def get_duration_info(text):
    """ 
    Get information about duration given a duration entity text

    Input:
        text: str
            A duration entity text 
            e.g. "for 5 weeks", "for up to a year", "for 2 - 3 months"
    Output:
        _min: float
            The minimum duration
            e.g. 5.0, 0.0, 2.0
        _max: float
            The maximum duration
            e.g. 5.0, 1.0, 3.0
        durtype: str
            The duration type
            e.g. "Week", "Year", "Month"
    """
    durtype = di_frequency.get_frequency_type(text)
    _min, _max = di_frequency._get_range(text)
    if _min is None:
        dur = di_frequency._get_number_of_times(text)
        _min = dur
        _max = dur
    if _min is None:
        nums = re.findall(di_frequency.re_digit, re.sub(",", "", text))
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
    return _min, _max, durtype
