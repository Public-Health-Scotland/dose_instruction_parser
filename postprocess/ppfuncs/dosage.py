import inflect

dose_instructions = ['take', 'inhale', 'instill', 'apply', 'spray', 'swallow']

# Not v sophisticated - just takes e.g. "2 tabs" and gets 2nd word "tabs"
def _get_form_from_dosage_tag(text):
    splitted = text.split(' ')
    if len(splitted) == 2:
        return splitted[1]

def _get_single_dose(di):
    def is_followed_by_number(word):
        return word in dose_instructions
    words = di.split()
    if is_followed_by_number(words[0]) and len(words) > 1 and _is_str_float(words[1]):
        return float(words[1])
    return None

inflect_engine = inflect.engine()

def _to_singular(text):
    # turn to singular if plural else keep as is
    singular = inflect_engine.singular_noun(text)
    return singular if singular else text
