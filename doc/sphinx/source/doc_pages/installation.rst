.. _Installation:

Installation
============

Basic install
-------------

.. warning::

    This package is 🚧 not yet available 🚧 on PyPI. This functionality is coming soon!

.. code:: bash

    conda create -n di                        # setup new conda env
    conda activate di                         # activate
    pip install dose_instruction_parser       # install dose_instruction_parser from PyPI
    parse_dose_instructions -h                # get help on parsing dose instructions


(Optional) Install the :program:`en_edris9` model. Contact `phs.edris@phs.scot <mailto:phs.edris@phs.scot>`_ for access.

Development install
-------------------

#.  Clone this repository
#.  Add a file called called :file:`secrets.env` in the top level of the cloned repository with the following contents:
    
    .. code:: bash

        export DI_FILEPATH="</path/to/model/folder>"

    This sets the environment variable :program:`DI_FILEPATH` where the code will read/write models. If you are working within Public Health Scotland please contact
    `phs.edris@phs.scot <mailto:phs.edris@phs.scot>`_ to receive the filepath. 
#. Create new conda environment and activate: 
    
    .. code:: bash

        conda create -n di-dev
        conda activate di-dev
    
#. Install package using editable pip install and development dependencies: 
    
    .. code:: bash

        python -m pip install -e dose_instruction_parser[dev]
    
    .. important::
        Make sure you run this from the top directory of the repository
#. (Optional) Install the :program:`en_edris9` model. Contact `phs.edris@phs.scot <mailto:phs.edris@phs.scot>`_ for access.