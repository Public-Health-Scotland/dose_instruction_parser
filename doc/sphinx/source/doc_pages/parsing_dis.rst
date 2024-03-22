.. _`Parsing dose instructions`:

Parsing dose instructions
=========================

Command line 
------------

*1. A single instruction*

A single dose instruction can be supplied using the **-di** argument.
 
 ``parse_dose_instructions -di "take one tablet daily" -mod en_edris9``

Output:
::
    StructuredDI(text='take one tablet daily', form='tablet', dosageMin=1.0, dosageMax=1.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)

*2. Multiple instructions*

Multiple dose instructions can be supplied from file using the **-f** argument, where each line in the text file supplied is a dose instruction. 
For example, if the file multiple_dis.txt contains the following:

    - daily 2 tabs
    - once daily when required

Running:
``parse_dose_instructions -f "multiple_dis.txt" -mod en_edris9``

will produce the corresponding output:
::
    StructuredDI(text='daily 2 tabs', form='tablet', dosageMin=2.0, dosageMax=2.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)
    StructuredDI(text='once daily when required', form=None, dosageMin=1.0, dosageMax=1.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=True, asDirected=False)

Where you have a lot of examples to parse you may want to send the output to a file rather than the command line. To do this, specify the output file location with the *-o* argument. If this has *.txt*
extension the results will be presented line by line like they would on the command line. If this has *.csv* extension the results will be cast to a data frame with one entry per row.

``parse_dose_instructions -f "multiple_dis.txt" -mod en_edris9 -o "out_dis.csv"``

Using Python
------------

An example of parsing dose instructions on Python is found in the repository: ``/doc/examples/example.py``.
If you are manually inputting individual dose instructions, include them in the list within square brackets as follows:

.. code-block:: python
    parsed_dis = p.parse_many([
    "take one tablet daily",
    "two puffs prn",
    "one cap after meals for three weeks",
    "4 caplets tid"])

If you have saved a file in .csv format with your free text (one dose instruction per row), include it as follows:   

.. code-block:: python
    dose_instructions = pd.read_csv(“(PATH)/dose_instructions.csv”)

    parsed_dis = p.parse_many([
    dose_instructions[“COLUMN”]
    ])
