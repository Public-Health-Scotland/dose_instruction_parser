from dataclasses import dataclass

@dataclass(frozen=True, eq=True)
class _Frequency:
    frequencyType: str
    interval: int

# TODO add qXd support
latin_frequency_types = {"qd": _Frequency("Day", 1), "bid": _Frequency("Day", 2), "tid": _Frequency("Day", 3),
                         "qid": _Frequency("Day", 4)}


def _get_frequency_type(frequency):
    if frequency is not None:
        if "hour" in frequency:
            return "Hour"
        if "week" in frequency:
            return "Week"
        if "month" in frequency:
            return "Month"
        if "year" in frequency:
            return "Year"
        if any(daily_instruction in frequency for daily_instruction in
               ("day", "daily", "night", "morning", "evening", "noon", "bedtime")):
            return "Day"
        latin_freq = _get_latin_frequency(frequency)
        if latin_freq:
            return latin_freq.frequencyType

def _get_interval(frequency):
    if frequency is not None:
        for word in frequency.split():
            if word.isdigit():
                return int(word)
        # every other TIME_UNIT means every 2 days,weeks etc
        if "other" in frequency:
            return 2
        latin_freq = _get_latin_frequency(frequency)
        if latin_freq:
            return latin_freq.interval

def _get_latin_frequency(frequency):
    for latin_freq in latin_frequency_types.keys():
        if latin_freq in frequency:
            return latin_frequency_types[latin_freq]


