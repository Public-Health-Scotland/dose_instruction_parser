from random import random
import re

# Sampling 2% from Diabetes study
lines_edi = [line for line in \
         open("***REMOVED***2223-0181_edi_cleanRx/data/redacted_sid")\
         if random() <= .001]

lines_epr = [line for line in \
         open("***REMOVED***2223-0181_epr_cleanRx/data/redacted_sid")\
         if random() <= .001]

lines = lines_edi + lines_epr

# Remove the line number tags (everything up to and including |)
lines = [re.sub(r'^.*?\|', '', line) for line in lines]
# Strip newlines
#lines = [line.rstrip() for line in lines]

# Write to text file
outfile = open("preprocess/for_tagging/sample_diabetes_study.txt", "w")
outfile.writelines(lines)
outfile.close()



