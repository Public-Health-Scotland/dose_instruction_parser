Developing the `di_parser` package
==================================

If you find a bug or would like to request an enhancement to the code, please open
an issue on GitHub. If you would like to contribute, please fork this repository
and open a pull request.

Best practice workflow
----------------------

* Follow the Installation_ instructions for a development install
* Checkout a new branch
* Update the code locally
* Add comments for other developers
* Add docstrings for code users
* Write tests to cover your updates
* Consider updating the documentation
* Commit and push changes
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
