import argparse
from textwrap import dedent
from os import path

# TODO: arguments for outfile, parallelise
# Separate function for parsing 1 or many dis
def main():
    """Parse dose instructions"""
    # Get command line arguments
    args = get_args()

    # Set up parser
    from dose_instruction_parser import di_parser
    dip = di_parser.DIParser(model_name=args.modelpath)

    # Check if valid filepath provided for dis.
    # If not, treat the input as a single dose instruction string.
    if not path.exists(args.doseinstruction):
        parsed_di = dip.parse(args.doseinstruction)
        write_out(args.doseinstruction, parsed_di, args.outfile)
    else:
        try:
            with open(args.doseinstruction, "r") as file:
                dis = [l.strip() for l in file.readlines()]
        except OSError:
            print(f"Could not open file: {args.doseinstruction}")
        if args.parallel == 'True':
            out = dip.parse_many_mp(dis)
        else:  
            out = dip.parse_many(dis)
        write_out(dis, out, args.outfile)

def get_args(): 
    ap = argparse.ArgumentParser(
        prog="Dose Instruction Parser",
        description=dedent('''\
            Parses prescription dose instruction free text into structured output of the form:

            * form:                                         the form of drug e.g. 'tablet'
            * dosageMin, dosageMax:                         the min and max dosage
            * frequencyMin, frequencyMax, frequencyType:    the min and max frequency and type e.g. 'Day'
            * durationMin, durationMax, durationType:       the min and max duration of treatment and type e.g. 'Week'
            * asRequired:                                   whether to take as required / as needed (bool)
            * asDirected:                                   whether to take as directed (bool)
            '''),
        epilog="Please contact the eDRIS team with any queries.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    ap.add_argument("-di", "--doseinstruction", 
                    required=True)
    ap.add_argument("-mp", "--modelpath", 
                    required=True)
    ap.add_argument("-o", "--outfile", 
                    required=False,
                    help=".txt or .csv file to write output to")
    ap.add_argument("-p", "--parallel", 
                    required=False,  
                    choices=['True', 'False'], 
                    default='True',
                    help="Whether to use parallel processing")
    ap.print_help()
    return ap.parse_args()

def write_out(dis, out, outfile):
    if outfile is None:
        # No outfile specified so just print to terminal
        for line in out: print(line)
    else:
        fname, fext = path.splitext(outfile)
        if fext == ".txt":
            # For text file print structured output line by line
            try:
                with open(outfile, "w+") as file:
                    file.write("\n".join(str(i) for i in out))    
            except OSError:
                print(f"Could not write to file: {outfile}")
        elif fext == ".csv":
            # For csv convert output to dataframe
            import pandas as pd
            df = pd.DataFrame(out)
            df.to_csv(outfile)
        else:
            raise ValueError("Out file must be either .txt or .csv")
   
if __name__ == "__main__":
    main()