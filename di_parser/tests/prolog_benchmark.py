""" 
Benchmarking against the prolog test examples

Step 1: Read in prolog test examples and reformat for di_parser
Step 2: Run di_parser on all the examples and check against desired output
Step 3: Calculate test score
"""
import pandas as pd
import re
import di_parser.di_parser as dip

## Step 1

with open("di_parser/tests/prolog_test.pl", "r") as lex:
    lines = lex.readlines()
# Keeping only the test lines
lines = [line for line in lines if line.startswith("test(")]

def check_nonetypes(inplist):
    outlist = []
    for inp in inplist:
        if (inp is None) or (inp == "None") or (inp == ""):
            outlist.append(None)
        else:
            outlist.append(inp)
    return outlist

def convert_to_float(inp):
    inp = check_nonetype(inp)
    if inp is None:
        return inp
    else:
        return float(inp)

def parse_lex_line(line):
  # Strip beginning and end
  line = re.sub(r"test\(\d+,", "", line).replace(".\n", "")
  # Split on first instance of ],
  inphrase_out = line.split("],", 1)
  assert len(inphrase_out) == 2, f"Length equal to {len(inphrase_out)}"
  inphrase = inphrase_out[0].replace("[", "").replace(","," ").replace("'", "").replace(" . ", ".")
  outinfo = inphrase_out[1].replace(")", "").replace("[","").replace("]", "").replace(".","").replace(",,", ",None,")
  dosmin, dosmax, form, fmin, fmax, ftype, \
      durmin, durmax, durtype, asreq, asdir = check_nonetypes(outinfo.split(","))
  out = dip.StructuredDI(form=form, dosageMin=convert_to_float(dosmin), dosageMax=convert_to_float(dosmax),
                            frequencyMin=convert_to_float(fmin), frequencyMax=convert_to_float(fmax), 
                            frequencyType=ftype, durationMin=convert_to_float(durmin), 
                            durationMax=convert_to_float(durmax), durationType=durtype,
                            asRequired=bool(asreq), asDirected=bool(asdir))
  return inphrase, out

parsed_lines = [parse_lex_line(line) for line in lines]
parsed_lines_df = pd.DataFrame(parsed_lines, columns = ["input", "desired_output"])

## Step 2


