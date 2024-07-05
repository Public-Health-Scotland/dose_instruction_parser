import csv
import spacy
import logging
import os
from dotenv import load_dotenv

from dose_instruction_parser.dose_instruction_parser import dose_instruction_parser as dip

load_dotenv(dotenv_path="secrets.env")

logging.basicConfig(filename="benchmark/di_check.log", level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

checkfile = f"{os.getenv('DI_FILEPATH')}/data/for tagging/dose_instructions_3_rp.txt"
checklines = [line for line in open(checkfile)]

model_path = f"{os.getenv('DI_FILEPATH')}/models/"
dose_instruction_parser = dip.DIParser(model_name=f"{model_path}/original/model-best")
model = spacy.load(f"{model_path}/original/model-best")

with open("benchmark/di_checking.txt", "w+") as outfile:
    for line in checklines:
        try:
            di = dose_instruction_parser.parse(line)
            ents = dip._get_model_entities_from_text(line, model)
            outfile.write( line + "\n\t" + str(ents) + "\n\t" + str(di) + "\n\n")
        except Exception as e:
            logger.warning(f"Error in dose instruction: {line}")
            logger.error(e)




