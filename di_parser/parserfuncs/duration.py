import re
import di_parser.parserfuncs.frequency as pfrequency


def _get_duration_info(text):
    """ 
    Get information about duration given a duration entity text

    Input:
        text: str
            A duration entity text 
            e.g. "for 5 weeks", "for up to a year", "for 2-3 months"
    Output:
        min: float
            The minimum duration
            e.g. 5.0, 0.0, 2.0
        max: float
            The maximum duration
            e.g. 5.0, 1.0, 3.0
        durtype: str
            The duration type
            e.g. "Week", "Year", "Month"
    """
    print("DURATION: " + text)
    durtype = pfrequency._get_frequency_type(text)
    min, max = pfrequency._get_range(text)
    if min is None:
        dur = pfrequency._get_number_of_times(text)
        min = dur
        max = dur
    if min is None:
        nums = re.findall(pfrequency.re_digit, re.sub(",", "", text))
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
    return min, max, durtype
