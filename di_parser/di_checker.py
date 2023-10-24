import csv
import spacy
import logging
import di_parser.di_parser as dip

logging.basicConfig(filename="di_parser/di_check.log", level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

checkfile = "***REMOVED***data/for tagging/dose_instructions_3_rp.txt"
checklines = [line for line in open(checkfile)]

model_path = "***REMOVED***models/"
di_parser = dip.DIParser(model_name=f"{model_path}/original/model-best")
model = spacy.load(f"{model_path}/original/model-best")

with open("di_parser/di_checking.txt", "w+") as outfile:
    for line in checklines:
        try:
            di = di_parser.parse(line)
            ents = dip._get_model_entities_from_text(line, model)
            outfile.write( line + "\n\t" + str(ents) + "\n\t" + str(di) + "\n\n")
        except Exception as e:
            logger.warning(f"Error in dose instruction: {line}")
            logger.error(e)




