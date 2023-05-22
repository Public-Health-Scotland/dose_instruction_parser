# Parse lex unit test data
import pandas as pd

lex = open("preprocess/for_tagging/for_processing/lex_unit_test_data_15593.pl", "r")
lines = lex.readlines()
# Keeping only the test lines
lines = [line for line in lines if line.startswith("test_big(")]

def parse_lex_line(line):
  # Strip beginning and end
  line = line.replace("test_big(", "").replace(".\n", "")
  # Split on first instance of ],
  inphrase_out = line.split("],", 1)
  assert len(inphrase_out) == 2, f"Length equal to {len(inphrase_out)}"
  inphrase = inphrase_out[0].replace("[", "").replace(","," ").replace("'", "").replace(" . ", ".")
  out = inphrase_out[1].replace(")", "").replace(",","")
  return inphrase, out

parsed_lines = [parse_lex_line(line) for line in lines]
parsed_lines_df = pd.DataFrame(parsed_lines, columns = ["input", "output"])

parsed_lines_df.to_csv("preprocess/for_tagging/parsed_unit_test_data.csv")

