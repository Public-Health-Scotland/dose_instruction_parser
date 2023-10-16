import re
from spellchecker import SpellChecker
from itertools import chain
from word2number import w2n

import postprocess.ppfuncs.frequency as ppfrequency
def _create_spell_checker():
    """
    Wrapper function to create a spellchecker.SpellChecker()
    Words in the keep_words.txt file will not be spellchecked
    """
    sc = SpellChecker()
    keep_words_frequency ="postprocess/keep_words.txt"
    sc.word_frequency.load_text_file(keep_words_frequency)
    return sc

spell_checker = _create_spell_checker()

def _flatmap(func, iterable):
    return list(chain.from_iterable(map(func, iterable)))

def _autocorrect(di):
    """
    Function to autocorrect a dose instruction before sending it
    to the NER model for tagging. 
    """
    di = di.lower().strip()
    corrected_words = []
    for word in di.split():
        # checking if the word is only letters
        if not re.match(r"^[a-zA-Z]+$", word) or spell_checker.known([word]):
            corrected_words.append(word)
        else:
            corrected_word = spell_checker.correction(word)
            corrected_words.append(corrected_word)
    di = ' '.join(corrected_words)
    return di


def _convert_words_to_numbers(sentence):
    frac_dict = {"half": 0.5, "third": 0.3, "quarter": 0.25, "fifth": 0.2}
    words = sentence.split()
    output_words = []
    for word in words:
        try:
            output_words.append(str(w2n.word_to_num(word)))
        except:
            output_words.append(word)
    return ' '.join(output_words)

def _convert_fract_to_num(sentence):
    frac_dict = {"half": 0.5, "third": 0.3, "quarter": 0.25, "fifth": 0.2}
    def is_frac(_word):
        nums = _word.split('/')
        return len(nums) == 2 and '/' in _word and nums[0].isdigit() and nums[1].isdigit()
    words = sentence.split()
    output_words = []
    for word in words:
        if word in frac_dict.keys():
            output_words.append(str(frac_dict[word]))
        elif is_frac(word):
            num, denom = word.split('/')
            output_words.append(str(int(num) / int(denom)))
        else:
            output_words.append(word)
    return ' '.join(output_words)

def _pre_process(di):
    di = _autocorrect(di)
    di = di.replace('twice', '2 times').replace("once", '1 time').replace("nightly", "every night")
    di = _add_space_around_parentheses(di)
    # remove extra spaces between words
    di = re.sub(r'\s+', ' ', di)
    output_words = []
    words = di.split()
    for word in words:
        if word == 'tab':
            word = word.replace('tab', 'tablet')
        elif word == 'tabs':
            word = word.replace('tabs', 'tablets')
        output_words.append(word)
    di = ' '.join(output_words)
    di = _convert_words_to_numbers(_convert_fract_to_num(di))
    return di


def _add_space_around_parentheses(s):
    s = re.sub(r'(?<!\s)\(', r' (', s)
    s = re.sub(r'\)(?!\s)', r') ', s)
    return s

def _is_str_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

