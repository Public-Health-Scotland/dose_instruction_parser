# Dose instruction parser documentation <a name="top"></a>

This folder is for storing the documentation for the dose instructions parser project at Public Health Scotland.

## Sphinx Documentation

### Generating the Documentation

The documentation is produced by the
[sphinx](http://www.sphinx-doc.org/en/master/) resource. To generate the sphinx
documentation, navigate to the `sphinx/` directory and execute the command `make
html`. This produces the documentation in the `build/index/` directory. The
`index.html` can be viewed with any appropriate browser.

### Adding to the Documentation

Add new documentation in restructured text (`.rst` suffix) format. 
To add a new section to the documentation, create an appropriately named directory in the `sphinx/source/` directory.  Inside the new directory, add all relevant documentation in restructured text format. In addition to these files, create an
`index.rst` file containing:

```
Chapter Name
============

.. toctree::
   :maxdepth: 1

   ./file1.md
   ./file2.rst
```
ensuring that the number of `=` signs is the same as the number of characters in
`Chapter Name`.

The next step is to reference the newly made `index.rst` in the main
`sphinx/source/index.rst` file.