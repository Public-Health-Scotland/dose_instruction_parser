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
    from . import parser
    dip = parser.DIParser(model_name=args.modelpath)

    # Check if single di provided
    if args.doseinstruction is not None:
        parsed_di = dip.parse(args.doseinstruction)
        write_out(args.doseinstruction, parsed_di, args.outfile)
    else:
        # Check if valid filepath provided for dis.
        if not path.exists(args.infile):
            raise OSError(f"Input file {args.infile} does not exist.")  
        with open(args.infile, "r") as file:
                dis = [l.strip() for l in file.readlines()]
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
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("-di", "--doseinstruction")
    group.add_argument("-f", "--infile")
    ap.add_argument("-mp", "--modelpath", required=True)
    ap.add_argument("-o", "--outfile", 
                    help=".txt or .csv file to write output to")
    ap.add_argument("-p", "--parallel", 
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
            except (OSError, RuntimeError):
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