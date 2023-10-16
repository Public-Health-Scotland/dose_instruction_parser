
import postprocess.ppfuncs.frequency as ppfrequency

def _get_duration_string(di):
    words = di.split()
    for i in range(len(words)):
        if words[i] == 'for':
            return ' '.join(words[i:])
    return None

def _get_duration_info(text):
    print("DURATION: " + text)
    durtype = ppfrequency._get_frequency_type(text)
    # TODO: min and max
    duration = ppfrequency._get_number_of_times(text)
    min = duration
    max = duration 
    return min, max, durtype

