.. di_parser documentation master file, created by
   sphinx-quickstart on Fri Mar  1 11:49:16 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Prescription dose instruction parser for Public Health Scotland
===============================================================

.. warning::
    This project is a work in progress. The documentation is not yet finished,
    and the code is preliminary. We do not advise using the code at this stage.
    Please contact **phs.edris@phs.scot** with any queries.

This is the documentation for the tool developed at Public Health Scotland to
parse prescription dose instruction free text into structured output.

This work is a collaboation between the Electronic Data Research Innovation Service
and Prescribing Team. The tool has drawn heavily upon the 
`med 7 <https://github.com/kormilitzin/med7>`_ and 
`parsigs <https://github.com/royashcenazi/parsigs>`_ projects, adapted and extended
to apply to the prescribing information free text held by Public Health Scotland.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   doc_pages/installation.rst
   doc_pages/quickstart.rst
   doc_pages/introduction.rst
   doc_pages/parsing_dis.rst
   doc_pages/developing_di_parser.rst
   doc_pages/training_model.rst
   doc_pages/adapting_code.rst
   modules/di_parser/modules.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
