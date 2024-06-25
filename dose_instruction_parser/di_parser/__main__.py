import argparse
import logging
import sys
from textwrap import dedent
from os import path
import pandas as pd

def main():
    """Parse dose instructions"""
    # Get command line arguments
    args = get_args()
    
    # Set up logfile
    logformat = "%(asctime)s %(message)s"
    if args.logfile is not None:
        # Initialise logfile
        print(f"Logging to {args.logfile}")
        logging.basicConfig(filename=args.logfile, level=logging.DEBUG,
          format=logformat)
        
        # Redirect warnings and errors to logger
        stdout_logger = logging.getLogger('STDOUT')
        sl = StreamToLogger(stdout_logger, logging.INFO)
        sys.stdout = sl
        stderr_logger = logging.getLogger('STDERR')
        sl = StreamToLogger(stderr_logger, logging.ERROR)
        sys.stderr = sl
        logging.info(f"Logging to {args.logfile}")

    else:
        # Log to command line
        logging.basicConfig(level=logging.DEBUG,
            format=logformat)
        print("Logging to command line.", 
        "Use the --logfile argument to set a log file instead.")

    # Check input and output files
    logging.info("Checking input and output files")
    single_di, ifext, ofext = check_setup(
        args.infile, args.outfile
    )

    # Set up parser
    logging.info("Setting up parser")
    from .parser import DIParser
    dip = DIParser(model_name=args.model)

    # Check if single di provided
    if single_di:
        logging.info("Parsing single dose instruction")
        parsed_di = dip.parse(args.doseinstruction)
        write_out(args.doseinstruction, parsed_di, args.outfile)
    else:
        logging.info("Parsing multiple dose instructions")
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
                logging.info("Using multiprocessing")
                out = dip.parse_many_mp(dis, di_info["inputID"].to_list())
            elif args.parallel == 'False':  
                out = dip.parse_many(dis, di_info["inputID"].to_list())
            elif args.parallel == 'async':
                logging.info("Using asynchronous processing")
                out = dip.parse_many_async(dis, di_info["inputID"].to_list())
        else: 
            logging.error(f"Input file {args.infile} must be .txt or .csv")    
            
        logging.info("Writing output")    
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
    ap.add_argument("-l", "--logfile",
                    default = None,
                    help="Path to logfile. Default behaviour is to log to terminal.")
    return ap.parse_args() 

def check_setup(infile, outfile):
    # Input
    if infile is None:
        single_di = True
        ifext = None
    else:
        single_di = False
        if not path.exists(infile):
            logging.error(f"Input file {infile} does not exist.")  
        ifname, ifext = path.splitext(infile)
        assert ifext in [".txt", ".csv"], \
            "Input file must be either .txt or .csv"
        if ifext == ".csv":
            # Check col names are correct
            cols = pd.read_csv(infile, nrows=1).columns.tolist()
            assert set(cols) == set(["inputID", "di"]), \
                f"Input .csv file must have columns 'inputID' and 'di'. Detected columns: {cols}."
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
                logging.warning(f"Could not write to file: {outfile}")
        elif fext == ".csv":
            # For csv convert output to dataframe
            logging.info("Converting output to dataframe")
            df = pd.DataFrame(out)
            logging.info(f"Saving out to {outfile}")
            df.to_csv(outfile, index=False)

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    https://stackoverflow.com/questions/19425736/how-to-redirect-stdout-and-stderr-to-logger-in-python
    """
    def __init__(self, logger, level):
       self.logger = logger
       self.level = level
       self.linebuf = ''

    def write(self, buf):
       for line in buf.rstrip().splitlines():
          self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass
   
if __name__ == "__main__":
    main()
