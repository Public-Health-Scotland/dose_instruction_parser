.. _Parsing dose instructions:

Parsing dose instructions
=========================

Follow the :ref:`Installation` instructions, then get started using the command line:

.. note::

    Run :program:`parse_dose_instructions -h` on the command line to get help on parsing dose instructions


In the following examples we assume the model :program:`en_edris9` is installed. You can provide your own path to an alternative model with the same nine entities.

A single instruction
--------------------

A single dose instruction can be supplied using the :program:`-di` argument.

.. code-block:: bash

    (di-dev)$ parse_dose_instructions -di "take one tablet daily" -mod en_edris9 

    Logging to command line. Use the --logfile argument to set a log file instead.
    2024-05-28 07:45:49,803 Checking input and output files
    2024-05-28 07:45:49,803 Setting up parser
    2024-05-28 07:46:34,205 Parsing single dose instruction

    StructuredDI(inputID=None, text='take one tablet daily', form='tablet', dosageMin=1.0, dosageMax=1.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)

Multiple dose instructions
--------------------------

Multiple dose instructions can be supplied from file using the :program:`-f` argument, where each line in the text file supplied is a dose instruction. 
For example, if the file :file:`multiple_dis.txt` contains the following:

.. code-block:: bash

    daily 2 tabs
    once daily when required

then you will get the corresponding output:

.. code-block:: bash

    Logging to command line. Use the --logfile argument to set a log file instead.
    2024-05-28 07:47:56,270 Checking input and output files
    2024-05-28 07:47:56,282 Setting up parser
    2024-05-28 07:48:18,003 Parsing multiple dose instructions
    Parsing dose instructions                                                                                               
    Parsed 100%|██████████████████████████████████████| 2/2 [00:00<00:00, 79.78 instructions/s]

    StructuredDI(inputID=0, text='daily 2 tabs', form='tablet', dosageMin=2.0, dosageMax=2.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)
    StructuredDI(inputID=1, text='once daily when required', form=None, dosageMin=None, dosageMax=None, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=True, asDirected=False)

Where you have a lot of examples to parse you may want to send the output to a file rather than 
the command line. To do this, specify the output file location with the :program:`-o` argument. 
If this has :file:`.txt` extension the results will be presented line by line like they 
would on the command line. If this has :file:`.csv` extension the results will be cast to a 
data frame with one entry per row.

.. code:: bash

    (di-dev)$ parse_dose_instructions -f "multiple_dis.txt" -mod en_edris9 -o "out_dis.csv"

The contents of :file:`out_dis.csv` is as follows:

.. csv-table:: Sample output
   :header-rows: 1

    ,inputID,text,form,dosageMin,dosageMax,frequencyMin,frequencyMax,frequencyType,durationMin,durationMax,durationType,asRequired,asDirected
    0,0,daily 2 tabs,tablet,2.0,2.0,1.0,1.0,Day,,,,False,False
    1,1,once daily when required,,,,1.0,1.0,Day,,,,True,False

.. note::

    Sometimes a dose instruction really contains more than one instruction within it. 
    In this case the output will be split into multiple outputs, one corresponding
    to each part of the instruction. For example,
    "Take two tablets twice daily for one week then one tablet once daily for two weeks"
    
    .. code::

        $ parse_dose_instructions -di "Take two tablets twice daily for one week then one tablet once daily for two weeks"
        
        Logging to command line. Use the --logfile argument to set a log file instead.
        2024-06-21 08:35:41,765 Checking input and output files
        2024-06-21 08:35:41,765 Setting up parser
        2024-06-21 08:35:59,572 Parsing single dose instruction
        
        StructuredDI(inputID=None, text='Take two tablets twice daily for one week then one tablet once daily for two weeks', form='tablet', dosageMin=2.0, dosageMax=2.0,  frequencyMin=2.0, frequencyMax=2.0, frequencyType='Day', durationMin=1.0, durationMax=1.0, durationType='Week', asRequired=False, asDirected=False)
        StructuredDI(inputID=None, text='Take two tablets twice daily for one week then one tablet once daily for two weeks', form='tablet', dosageMin=1.0, dosageMax=1.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=2.0, durationMax=2.0, durationType='Week', asRequired=False, asDirected=False)

Providing input IDs 
-------------------

The :program:`inputID` value helps to keep track of which outputs correspond to which inputs. The default behaviour is:

* For a single dose instruction, set :program:`inputID=None` 
* For multiple dose instructions, number each instruction starting from 0 by the order they appear in the input file

You may want to provide your own values for :program:`inputID`. To do this, provide input dose instructions as a :file:`.csv` file with columns 

* :program:`inputID` specifying the input ID
* :program:`di` specifying the dose instruction

For example, using :file:`test.csv` with the following contents:

.. csv-table:: Sample input
   :header-rows: 1
    
    inputID,di
    eDRIS/XXXX-XXXX/example/001,daily 2 caps
    eDRIS/XXXX-XXXX/example/002,daily 0.2ml
    eDRIS/XXXX-XXXX/example/003,two mane + two nocte
    eDRIS/XXXX-XXXX/example/004,2 tabs twice daily increased to 2 tabs three times daily during exacerbation chest symptoms
    eDRIS/XXXX-XXXX/example/005,take one in the morning and take two at night as directed
    eDRIS/XXXX-XXXX/example/006,1 tablet(s) three times daily for pain/inflammation
    eDRIS/XXXX-XXXX/example/007,two puffs at night
    eDRIS/XXXX-XXXX/example/008,0.6mls daily
    eDRIS/XXXX-XXXX/example/009,to be applied tds-qds
    eDRIS/XXXX-XXXX/example/010,take 1 tablet for 3 weeks then take 3 tablets for 4 weeks
    eDRIS/XXXX-XXXX/example/011,one to be taken twice a day  if sleepy do not drive/use machines. avoid alcohol. swallow whole.
    eDRIS/XXXX-XXXX/example/012,1 tab take as required
    eDRIS/XXXX-XXXX/example/013,take one daily for allergy
    eDRIS/XXXX-XXXX/example/014,one daily when required

yields the corresponding output

.. csv-table:: Sample output
   :header-rows: 1

    ,inputID,text,form,dosageMin,dosageMax,frequencyMin,frequencyMax,frequencyType,durationMin,durationMax,durationType,asRequired,asDirected
    0,eDRIS/XXXX-XXXX/example/001,daily 2 caps,capsule,2.0,2.0,1.0,1.0,Day,,,,False,False
    1,eDRIS/XXXX-XXXX/example/002,daily 0.2ml,ml,0.2,0.2,1.0,1.0,Day,,,,False,False
    2,eDRIS/XXXX-XXXX/example/003,two mane + two nocte,,2.0,2.0,2.0,2.0,Day,,,,False,False
    3,eDRIS/XXXX-XXXX/example/004,2 tabs twice daily increased to 2 tabs three times daily during exacerbation chest symptoms,tablet,2.0,2.0,5.0,5.0,Day,,,,False,False
    4,eDRIS/XXXX-XXXX/example/005,take one in the morning and take two at night as directed,,3.0,3.0,1.0,1.0,Day,,,,False,False
    5,eDRIS/XXXX-XXXX/example/006,1 tablet(s) three times daily for pain/inflammation,tablet,1.0,1.0,3.0,3.0,Day,,,,False,False
    6,eDRIS/XXXX-XXXX/example/007,two puffs at night,puff,2.0,2.0,1.0,1.0,Day,,,,False,False
    7,eDRIS/XXXX-XXXX/example/008,0.6mls daily,ml,0.6,0.6,1.0,1.0,Day,,,,False,False
    8,eDRIS/XXXX-XXXX/example/009,to be applied tds-qds,,,,3.0,3.0,Day,,,,False,False
    9,eDRIS/XXXX-XXXX/example/010,take 1 tablet for 3 weeks then take 3 tablets for 4 weeks,tablet,1.0,1.0,,,,3.0,3.0,Week,False,False
    10,eDRIS/XXXX-XXXX/example/010,take 1 tablet for 3 weeks then take 3 tablets for 4 weeks,tablet,3.0,3.0,,,,4.0,4.0,Week,False,False
    11,eDRIS/XXXX-XXXX/example/011,one to be taken twice a day  if sleepy do not drive/use machines. avoid alcohol. swallow whole.,,1.0,1.0,2.0,2.0,Day,,,,False,False
    12,eDRIS/XXXX-XXXX/example/012,1 tab take as required,tablet,1.0,1.0,,,,,,,True,False
    13,eDRIS/XXXX-XXXX/example/013,take one daily for allergy,,1.0,1.0,1.0,1.0,Day,,,,False,False
    14,eDRIS/XXXX-XXXX/example/014,one daily when required,,1.0,1.0,1.0,1.0,Day,,,,True,False

.. note::

    In this example, `eDRIS/XXXX-XXXX/example/010` has been split up into two dose instructions

Usage from Python
-----------------

For more adaptable usage you can load the package into Python and use it within a script or on the Python prompt. For example, using `iPython <https://pypi.org/project/ipython/>`_:

.. code:: ipython 

    In [1]: import pandas as pd
   ...: from di_parser import parser

    In [2]: # Create parser
    ...: p = parser.DIParser("en_edris9")

    In [3]: # Parse one dose instruction
    ...: p.parse("Take 2 tablets morning and night")
    Out[3]: [StructuredDI(inputID=None, text='Take 2 tablets morning and night', form='tablet', dosageMin=2.0, dosageMax=2.0, frequencyMin=2.0, frequencyMax=2.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)]

    In [4]: # Parse many dose instructions
    ...: parsed_dis = p.parse_many([
    ...:     "take one tablet daily",
    ...:     "two puffs prn",
    ...:     "one cap after meals for three weeks",
    ...:     "4 caplets tid"
    ...: ])

    In [5]: print(parsed_dis)
    [StructuredDI(inputID=0, text='take one tablet daily', form='tablet', dosageMin=1.0, dosageMax=1.0, frequencyMin=1.0, frequencyMax=1.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False), StructuredDI(inputID=1, text='two puffs prn', form='puff', dosageMin=2.0, dosageMax=2.0, frequencyMin=None, frequencyMax=None, frequencyType=None, durationMin=None, durationMax=None, durationType=None, asRequired=True, asDirected=False), StructuredDI(inputID=2, text='one cap after meals for three weeks', form='capsule', dosageMin=1.0, dosageMax=1.0, frequencyMin=3.0, frequencyMax=3.0, frequencyType='Day', durationMin=3.0, durationMax=3.0, durationType='Week', asRequired=False, asDirected=False), StructuredDI(inputID=3, text='4 caplets tid', form='carpet', dosageMin=4.0, dosageMax=4.0, frequencyMin=3.0, frequencyMax=3.0, frequencyType='Day', durationMin=None, durationMax=None, durationType=None, asRequired=False, asDirected=False)]

    In [6]: # Convert output to pandas dataframe
    ...: di_df = pd.DataFrame(parsed_dis)

    In [7]: print(di_df)
    inputID                                 text     form  dosageMin  dosageMax  frequencyMin  frequencyMax frequencyType  durationMin  durationMax durationType  asRequired  asDirected
    0        0                take one tablet daily   tablet        1.0        1.0           1.0           1.0           Day          NaN          NaN         None       False       False
    1        1                        two puffs prn     puff        2.0        2.0           NaN           NaN          None          NaN          NaN         None        True       False
    2        2  one cap after meals for three weeks  capsule        1.0        1.0           3.0           3.0           Day          3.0          3.0         Week       False       False
    3        3                        4 caplets tid   carpet        4.0        4.0           3.0           3.0           Day          NaN          NaN         None       False       False
