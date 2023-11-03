""" 
Benchmarking against the prolog test examples

Step 1: Read in prolog test examples and reformat for di_parser
Step 2: Run di_parser on all the examples 
Step 3: Calculate test score
"""
import pandas as pd
import re
import warnings
import di_parser.di_parser as dip

## Step 1: Read in prolog test examples and reformat for di_parser

with open("di_parser/tests/prolog_test.pl", "r") as lex:
    lines = lex.readlines()

# Keeping only the test lines
lines = [line for line in lines if line.startswith("test(")]

def check_nonetype(inp):
    if (inp is None) or (inp == "None") or (inp == ""):
            return None
    else:
        return inp

def check_nonetypes(inplist):
    outlist = [check_nonetype(inp) for inp in inplist]
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
  outinfo = inphrase_out[1].replace(")", "").replace("[","").replace("]", "").replace(",,", ",None,")
  try:
    dosmin, dosmax, form, fmin, fmax, ftype, \
        durmin, durmax, durtype, asreq, asdir = check_nonetypes(outinfo.split(","))
  except ValueError:
      print(ValueError)
      return inphrase, None
  out = dip.StructuredDI(form=form, dosageMin=convert_to_float(dosmin), dosageMax=convert_to_float(dosmax),
                            frequencyMin=convert_to_float(fmin), frequencyMax=convert_to_float(fmax), 
                            frequencyType=ftype, durationMin=convert_to_float(durmin), 
                            durationMax=convert_to_float(durmax), durationType=durtype,
                            asRequired=bool(asreq), asDirected=bool(asdir))
  return inphrase, out

parsed_lines = [parse_lex_line(line) for line in lines]
parsed_lines_df = pd.DataFrame(parsed_lines, columns = ["input", "desired_output"])

## Step 2: Run di_parser on all the examples
model_path = "***REMOVED***models/"
di_parser = dip.DIParser(model_name=f"{model_path}/original/model-best")

def apply_di_parser(x):
    try:
        return di_parser.parse(x)
    except:
        return None
    
parsed_lines_df["di_parser_output"] = parsed_lines_df["input"]\
    .transform(apply_di_parser)

def compare_numbers(left, right):
    if (left is None) and (right is None):
        return True
    elif (left is None) or (right is None):
        return False
    try:
        return (float(left) == float(right))
    except ValueError:
        return  (left == right)

# Step 3: Calculate test score
def compare_dataclass_attrs(di_1, di_2, attr):
    attr_1 = getattr(di_1, attr)
    attr_2 = getattr(di_2, attr)
    if attr == "form":
        return 0
    elif attr in ("frequencyType", "durationType"):
        if str(attr_1).lower() == str(attr_2).lower():
            match = True
        else:
            match = False
    elif attr in ("asRequired", "asDirected"):
        if bool(attr_1) == bool(attr_2):
            match = True
        else:
            match = False
    else:
        match = compare_numbers(attr_1, attr_2)
    # Now check whether match detected    
    if not match:
        warnings.warn(f"Mismatch in {attr}: want {attr_1}, got {attr_2}.")
        return 1
    else:
        return 0
    
def compare_structured_dis(input, di_1, di_2):
    if (di_1 is None) or (di_2 is None):
        warnings.warn("Some inputs are None")
        return 0
    if len(di_2) != 1:
        warnings.warn(f"Multiple dose instructions detected for di: {input}. Skipping instance.")
        return 0
    # Output from di_parser is stored in a list
    di_2 = di_2[0]
    # Form
    attrs = di_1.__annotations__.keys()
    mismatch = 0
    for attr in attrs:
        attr_mismatch = compare_dataclass_attrs(di_1, di_2, attr) 
        if attr_mismatch is not None:
            mismatch = mismatch + attr_mismatch
        else:
            mismatch = mismatch
    return mismatch

#parsed_lines_df = parsed_lines_df.query('desired_output != None')

parsed_lines_df["mismatch"] = parsed_lines_df.apply( 
    lambda x: compare_structured_dis(input = x["input"], 
                                    di_1 = x["desired_output"],
                                    di_2 = x["di_parser_output"]), axis=1
                                    )

percentage_match = 100*parsed_lines_df["mismatch"].value_counts()[0]/\
    parsed_lines_df["mismatch"].value_counts().sum()

print(f"Percentage match: {round(percentage_match)}%")
print("Prolog test match: 96%")

for index, row in parsed_lines_df[parsed_lines_df["mismatch"]!=0].iterrows():
    print(row["input"])
    print(row["desired_output"])
    print("\n")
