import re
import csv
from spellchecker import SpellChecker
from itertools import chain
from word2number import w2n
from os import path

def _create_spell_checker():
    """
    Wrapper function to create a spellchecker.SpellChecker()
    Words in the keep_words.txt file will not be spellchecked
    """
    sc = SpellChecker()
    keep_words_frequency = path.join(path.dirname(__file__), 
                                        "../../data/keep_words.txt")
    sc.word_frequency.load_text_file(keep_words_frequency)
    return sc

spell_checker = _create_spell_checker()

def _flatmap(func, iterable):
    """
    Helper function to map a given function onto an iterable and
    return the outputs in a list

    Input:
        func: 
            Function to map across iterable
        iterable:  
            Iterable to map func across
    Output:
        list:
            List of outputs generated by action of func on each iterable element
    """
    return list(chain.from_iterable(map(func, iterable)))

def _autocorrect(di):
    """
    Function to autocorrect a dose instruction before sending it
    to the NER model for tagging. 

    Input:
        di: str
            dose instruction for spellchecking
            e.g. "2 tabletts twice a dya"
    Output:
        str
            autocorrected dose instruction
            e.g. "2 tablets twice a day"
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

def _remove_parentheses(s):
    """
    Removes parentheses

    Input:
        s: str
            String to remove parentheses
            e.g. "tablet(s)"
    Output:
        str
            String with parentheses removed
            e.g. "tablet s "
    """
    s = re.sub(r'\(', r' ', s) 
    s = re.sub(r'\)', r' ', s) 
    return s

def _pad_hyphens_and_slashes(s):
    """
    Pads hyphens with spaces

    Input:
        s: str
            String to pad hyphens 
            e.g. "four-six"
    Output:
        str
            String with hyphens padded
            e.g. "four - six"
    """
    s = re.sub(r'\-', r' - ', s)
    s = re.sub(r'\\', ' \ ', s)
    s = re.sub(r'\/', ' / ', s)
    return s

def _pad_numbers(s):
    """
    Add spaces around numbers

    Input:
        s: str
            String to pad numbers
            e.g. "2x20ml or 3 tablets at 8am"
    Output:
        str
            String with numbers padded
            e.g. " 2 x 20 ml or  3  tablets at  8 am"
    """
    s = re.sub('(\d+(\.\d+)?)', r' \1 ', s)
    return s

def _convert_words_to_numbers(sentence):
    """
    Takes a sentence and converts any number words to numbers

    Input:
        sentence: str
            Sentence to convert
            e.g. "take half a tablet every two days"
    Output:
        str
            Converted sentence
            e.g. "take 0.5 a tablet every 2 days" 
    """
    words = sentence.split()
    output_words = []
    for word in words:
        word = _convert_fract_to_num(word)
        try:
            output_words.append(str(w2n.word_to_num(word)))
        except:
            output_words.append(word)
    return ' '.join(output_words)

def _convert_fract_to_num(word):
    """
    Takes a word and converts it to a numeric fraction if possible

    Input: 
        word: str
        e.g. "half"
    Output:
        str
            Converted word
            e.g. "0.5"
    """
    frac_dict = {"half": "0.5",  "quarter": "0.25"}
    def is_frac(_word):
        nums = _word.split('/')
        return len(nums) == 2 and '/' in _word and nums[0].isdigit() and nums[1].isdigit()
    if word in frac_dict.keys():
        out = frac_dict[word]
    elif is_frac(word):
        num, denom = word.split('/')
        out = str(round(int(num) / int(denom), 3))
    else:
        out = word
    return out

def pre_process(di):
    """
    Pre-processes a dose instruction before it is sent to the model 

    Input:
        di: str
            Dose instruction
            e.g. "take two tabs MORNING and nghit"
    Output:
        str
            Pre-processed dose instruction
            e.g. "take 2 tablets morning and night"
    """
    # get words to replace
    output_words = []
    words = di.split()
    replace_words = {}
    replace_words_path = path.join(path.dirname(__file__), 
                                    "../../data/replace_words.csv")
    with open(replace_words_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            replace_words[row["Before"]] = row["After"]
    # replace words        
    for word in words:
        if word in replace_words.keys():
            word = word.replace(word,replace_words[word])
        output_words.append(word)
    di = ' '.join(output_words)
    # rest of preprocessing
    di = _autocorrect(di)
    di = _remove_parentheses(di)
    di = _pad_hyphens_and_slashes(di)
    di = _convert_words_to_numbers(di)
    di = _pad_numbers(di)
    # remove extra spaces between words
    di = re.sub(r'\s+', ' ', di)
    return di



