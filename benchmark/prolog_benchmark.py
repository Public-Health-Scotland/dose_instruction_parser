""" 
Benchmarking against the prolog test examples

Step 1: Read in prolog test examples and reformat for dose_instruction_parser
Step 2: Run dose_instruction_parser on all the examples 
Step 3: Calculate test score
"""
import pandas as pd
import re
import warnings
from dose_instruction_parser.dose_instruction_parser import dose_instruction_parser as dip

from contextlib import contextmanager
from timeit import default_timer

@contextmanager
def elapsed_timer():
    start = default_timer()
    elapser = lambda: default_timer() - start
    yield lambda: elapser()
    end = default_timer()
    elapser = lambda: end-start

## Step 1: Read in prolog test examples and reformat for dose_instruction_parser

with open("benchmark/new_test.pl", "r") as lex:
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
    elif inp.strip() == '':
        return None 
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

## Step 2: Run dose_instruction_parser on all the examples
model_path = f"{os.getenv('DI_FILEPATH')}/models/"
dose_instruction_parser = dip.DIParser(model_name=f"{model_path}/original/model-best")

def apply_dose_instruction_parser(x):
    try:
        return dose_instruction_parser.parse(x)
    except:
        return None

with elapsed_timer() as elapsed:    
    parsed_lines_df["dose_instruction_parser_output"] = parsed_lines_df["input"]\
        .transform(apply_dose_instruction_parser)

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
    # Output from dose_instruction_parser is stored in a list
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
                                    di_2 = x["dose_instruction_parser_output"]), axis=1
                                    )

mismatch_counts = parsed_lines_df["mismatch"].value_counts()

percentage_total_match = 100*mismatch_counts[0]/\
    parsed_lines_df["mismatch"].value_counts().sum()

mismatch_df = pd.DataFrame({
    "mismatch" : mismatch_counts.index,
    "count" : mismatch_counts
})

mismatch_df["penalty"] = mismatch_df["mismatch"] * mismatch_df["count"]
total_penalty = mismatch_df["penalty"].sum()
total_possible_penalty = parsed_lines_df.shape[0] * 11
percentage_match = 100*(1-total_penalty/total_possible_penalty)

print(f"Percentage match: {round(percentage_total_match)}% with time {round(elapsed(), 2)}s")
print(f"Partial match: {round(percentage_match)}%")
print("Prolog test match: 66% with time 18s")

for index, row in parsed_lines_df[parsed_lines_df["mismatch"]!=0].iterrows():
    print(row["input"])
    print(row["desired_output"])
    print(row["dose_instruction_parser_output"])
    print("\n")
