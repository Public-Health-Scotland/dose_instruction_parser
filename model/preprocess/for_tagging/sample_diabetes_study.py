from random import random
import re


def get_diabetes_sample(percent=2):

    # Divide by 2 as get 1/2 amount from each file
    sample_num = percent/(2*100)

    # Sampling from Diabetes study
    lines_edi = [line for line in \
            open("***REMOVED***2223-0181_edi_cleanRx/data/redacted_sid")\
            if random() <= sample_num]

    lines_epr = [line for line in \
            open("***REMOVED***2223-0181_epr_cleanRx/data/redacted_sid")\
            if random() <= sample_num]

    lines = lines_edi + lines_epr

    # Remove the line number tags (everything up to and including |)
    lines = [re.sub(r'^.*?\|', '', line) for line in lines]

    return lines

# Getting 2% sample for tagging
diabetes_for_tagging = get_diabetes_sample()
with open("preprocess/for_tagging/sample_diabetes_study.txt", "w") as outfile:
    outfile.writelines(diabetes_for_tagging)

# Getting testing 1% sample
diabetes_for_testing = get_diabetes_sample(1)
with open("preprocess/for_testing/sample_diabetes_study_test.txt", "w") as outfile:
    outfile.writelines(diabetes_for_testing)




