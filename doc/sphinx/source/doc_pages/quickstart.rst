.. _Quickstart:

Quickstart
==========

The quickest way to start is by using the command line.

1.	Create new conda environment: ``conda create -n di``
2.	Activate environment: ``conda activate di``
3.	Install package: ``python -m pip install dose_instruction_parser``
4.	Run ``parse_dose_instructions -h`` to see help for command line functionality

A single dose instruction can be supplied using the **-di** argument.

.. code-block:: bash

    (di-dev)$ parse_dose_instructions -di "take one tablet daily" -mod en_edris9 

    StructuredDI(text='take one tablet daily', form='tablet', dosageMin=1.0, dosageMax=1.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)

Multiple dose instructions can be supplied from file using the **-f** argument, where each line in the text file supplied is a dose instruction. 
For example, if the file **multiple_dis.txt** contains the following:

.. code-block:: bash

    daily 2 tabs
    once daily when required

then you will get the corresponding output:

.. code-block:: bash

    (di-dev)$ parse_dose_instructions -f "multiple_dis.txt" -mod en_edris9  
    
    StructuredDI(text='daily 2 tabs', form='tablet', dosageMin=2.0, dosageMax=2.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)
    StructuredDI(text='once daily when required', form=None, dosageMin=1.0, dosageMax=1.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=True, asDirected=False)
