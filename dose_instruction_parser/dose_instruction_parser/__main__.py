import os
import argparse
from dotenv import load_dotenv
from dose_instruction_parser import di_parser

# TODO: arguments for outfile, parallelise
# Separate function for parsing 1 or many dis
def main():
    """Parse dose instructions"""
    # Arguments given
    # 1: dose instruction
    # 2: model path 
    ap = argparse.ArgumentParser()
    ap.add_argument("-di", "--doseinstruction", required=True)
    ap.add_argument("-mp", "--modelpath", required=True)
    args = ap.parse_args()

    dip = di_parser.DIParser(model_name=args.modelpath)

    # Check if valid filepath provided for dis
    if not os.path.exists(args.doseinstruction):
        parsed_di = dip.parse(args.doseinstruction)
        print(parsed_di)
        return parsed_di
    else:
        try:
            with open(args.doseinstruction, "r") as file:
                dis = file.readlines()
            out = [dip.parse(di) for di in dis]
            for line in out: print(line)
        except OSError:
            print(f"Could not open file: {args.doseinstruction}")


    
if __name__ == "__main__":
    main()