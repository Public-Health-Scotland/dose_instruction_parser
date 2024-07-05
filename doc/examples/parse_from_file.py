import pandas as pd
from dose_instruction_parser import parser

# Create parser
p = parser.DIParser("en_edris9")

# Parse dose instructions from file
infile = 

print(parsed_dis)

# Convert output to pandas dataframe
di_df = pd.DataFrame(parsed_dis)

print(di_df)