.. _Development:

Developing the :program:`dose_instruction_parser` package
=========================================================

If you find a bug or would like to request an enhancement to the code, please open
an issue on `GitHub <https://github.com/Public-Health-Scotland/dose_instruction_parser/issues>`_. If you would like to contribute, please fork this repository
and open a pull request.

Improving/modifying the existing rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To convert named entities to the desired structured output we take a rule-based approach. The infrastructure was based on the open source `parsigs <https://github.com/royashcenazi/parsigs>`_ package
for parsing dose instructions.

There are different modules in the :mod:`dose_instruction_parser` package which deal with different entities. Some of the named entities (ROUTE, DRUG, STRENGTH) are not processed here because this
is information which is separately stored for prescriptions so we don't need to extract it from the dose instructions. The :program:`DIParser` class in :mod:`di_parser.parser` 
is the culmination of all the pre-processing, NER and rule-based post-processing.

Best practice workflow
----------------------

* Follow the :ref:`Installation` instructions for a development install
* Checkout a new branch
* Edit the contents of the :file:`dose_instructions_parser` folder 
* Check the outcome using :program:`parse_dose_instructions` on the command line, or by importing the local :mod:`dose_instruction_parser` package and running from python 
* Add comments for other developers
* Add docstrings for code users
* Make sure you update any tests in :file:`parse_dose_instructions/di_parser/tests`
* Consider updating the documentation
* Commit and push changes to Github
* Open a pull request for your branch
* Review tests and code coverage from GitHub actions

Tips and tricks
---------------

* Try using an IPython prompt to explore the code in its present state
  (type `ipython` in the Terminal to bring up the prompt). Then for example
  to test the :mod:`di_parser.di_frequency.get_frequency_info` function

  .. code:: python

    >>> from di_parser.di_frequency import get_frequency_info
    >>> get_frequency_info("twice daily")

    (2.0, 2.0, 'Day')

* If you edit the code with a prompt still open you may need to reload the
  relevant module in order to get the changes. You can use the `reload`
  function from `importlib` to do this:

  .. code:: python

    >>> from di_parser import parser
    >>> p = parser.DIParser("en_edris9")
    >>> # Make some changes to the parser module
    >>> p = parser.DIParser("en_edris9") # changes won't have loaded
    >>> from importlib import reload
    >>> reload(parser)
    >>> p = parser.DIParser("en_edris9") # changes will have loaded
