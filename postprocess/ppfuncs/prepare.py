import re
from spellchecker import SpellChecker
from itertools import chain
from word2number import w2n


number_words = ["one", "two", "three", "four", "five", 
                "six", "seven", "eight", "nine", "ten"]

def _is_number_word(word):
    return word in number_words

def _create_spell_checker():
    sc = SpellChecker()
    keep_words_frequency ="postprocess/keep_words.txt"
    sc.word_frequency.load_text_file(keep_words_frequency)
    return sc

spell_checker = _create_spell_checker()

def _flatmap(func, iterable):
    return list(chain.from_iterable(map(func, iterable)))

def _autocorrect(di):
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
    words = sentence.split()
    output_words = []
    for word in words:
        if _is_number_word(word):
            output_words.append(str(w2n.word_to_num(word)))
        else:
            output_words.append(word)
    return ' '.join(output_words)

def _convert_fract_to_num(sentence):
    def is_frac(_word):
        nums = _word.split('/')
        return len(nums) == 2 and '/' in _word and nums[0].isdigit() and nums[1].isdigit()
    words = sentence.split()
    output_words = []
    for word in words:
        if is_frac(word):
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
    di = _convert_words_to_numbers(di)
    return _convert_fract_to_num(di)


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

