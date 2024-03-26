import argparse
from textwrap import dedent
from os import path
import pandas as pd

def main():
    """Parse dose instructions"""
    # Get command line arguments
    args = get_args()

    # Check input and output files
    single_di, ifext, ofext = check_setup(
        args.infile, args.outfile
    )

    # Set up parser
    from .parser import DIParser
    dip = DIParser(model_name=args.model)

    # Check if single di provided
    if single_di:
        parsed_di = dip.parse(args.doseinstruction)
        write_out(args.doseinstruction, parsed_di, args.outfile)
    else:
        if ifext == ".txt":
            with open(args.infile, "r") as file:
                    dis = [l.strip() for l in file.readlines()]
            if args.parallel == 'True':
                out = dip.parse_many_mp(dis)
            else:  
                out = dip.parse_many(dis)
        elif ifext == ".csv":
            di_info = pd.read_csv(args.infile)
            dis = di_info["di"].to_list()
            if args.parallel == 'True':
                out = dip.parse_many_mp(dis, di_info["rowid"].to_list())
            elif args.parallel == 'False':  
                out = dip.parse_many(dis, di_info["rowid"].to_list())
            elif args.parallel == 'async':
                out = dip.parse_many_async(dis, di_info["rowid"].to_list())
        else: 
            raise OSError(f"Input file {args.infile} must be .txt or .csv")        
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
    ap.add_argument("-mod", "--model", 
                    required=False, 
                    default="en_edris9",
                    help="Name of installed model or path to model")
    ap.add_argument("-o", "--outfile", 
                    help=".txt or .csv file to write output to")
    ap.add_argument("-p", "--parallel", 
                    choices=['True', 'False', 'async'], 
                    default='False',
                    help="Whether to use parallel processing")
    return ap.parse_args()

def check_setup(infile, outfile):
    # Input
    if infile is None:
        single_di = True
        ifext = None
    else:
        single_di = False
        if not path.exists(infile):
            raise OSError(f"Input file {infile} does not exist.")  
        ifname, ifext = path.splitext(infile)
        assert ifext in [".txt", ".csv"], \
            "Input file must be either .txt or .csv"
        if ifext == ".csv":
            # Check col names are correct
            cols = pd.read_csv(infile, nrows=1).columns.tolist()
            assert set(cols) == set(["rowid", "di"]), \
                f"Input .csv file must have columns 'rowid' and 'di'. Detected columns: {cols}."
    # Output
    if outfile is None:
        ofext = None
    else:
        ofname, ofext = path.splitext(outfile)
        assert ofext in [".txt", ".csv"], \
            "Out file must be either .txt or .csv"
    return single_di, ifext, ofext
    
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
   
if __name__ == "__main__":
    main()