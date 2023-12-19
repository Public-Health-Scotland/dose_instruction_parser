from dose_instruction_parser import di_parser

def main():
    """Parse dose instructions"""
    # Arguments given
    # 0: dose instruction
    # 1: model path 
    di = sys.argv[0]
    model_path = sys.argv[1]

    di_parser = di_parser.DIParser(model_name=model_path)
    parsed_di = di_parser.parse(di)

    return parsed_di
    