.. _Installation:

Installation
============

To parse dose instructions from free text, you need to have the model 'edris9' installed. 
It is obtained by installing the :mod:`di_parser` package, available on `PyPI <https://pypi.org/>`_.
After this, if you are working at PHS, obtain **secrets.env** file from colleagues which defines environment variable **DI_FILEPATH** where the model results are saved. Alternatively, you can use your own path.

On the command line:
1. Create new conda environment: ``conda create -n di`` 
1. Activate environment: ``conda activate di``
1. Install package using editable pip install and development dependencies: ``python -m pip install -e dose_instruction_parser``
1. Run ``parse_dose_instructions -h`` on command line and/or get developing
