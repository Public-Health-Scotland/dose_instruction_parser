import pandas as pd
from di_parser import parser

# Create parser
p = parser.DIParser("en_edris9")

# Parse one dose instruction
p.parse("Take 2 tablets morning and night")

# Parse many dose instructions
parsed_dis = p.parse_many([
    "take one tablet daily",
    "two puffs prn",
    "one cap after meals for three weeks",
    "4 caplets tid"
])

print(parsed_dis)

# Convert output to pandas dataframe
di_df = pd.DataFrame(parsed_dis)

print(di_df)