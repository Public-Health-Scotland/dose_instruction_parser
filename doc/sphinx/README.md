# Dose instruction parser documentation <a name="top"></a>

This folder is for storing the documentation for the dose instructions parser project at Public Health Scotland.

📓 The documentation can be found at https://public-health-scotland.github.io/dose_instruction_parser/

## Sphinx Documentation

### Generating the documentation locally

> [!IMPORTANT] 
> Follow the development setup instructions in the main README for `dose_instruction_parser`.

The documentation is produced by the
[`sphinx`](http://www.sphinx-doc.org/en/master/) resource. To generate the sphinx
documentation, navigate to the `sphinx/` directory and execute the command 
```bash
make html
```
This runs the `Makefile` and produces the documentation in the `build/index/html` directory. To view the local documentation, open up `build/index/index.html` using a web browser.

> [!IMPORTANT]
> Pay close attention to the output of `make html`, particularly any errors or warnings which need to be fixed

>[!TIP]
> If you are developing the documentation you can run `source ./autobuild_mode.sh` to start [autobuild](https://pypi.org/project/sphinx-autobuild/) mode. This means the documentation will be continually compiled as you edit the source code. You just need to refresh your browser to see the changes.

#### Notes on the Makefile

* The `Makefile` sets compilation options such as the source for the documentation (`SOURCEDIR`) and location to build to (`BUILDDIR`)
* Commands under "`clean`" are run when `make clean` is executed. Note this includes setting up the GitHub pages git worktree
* [`sphinx-apidoc`](https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html) is used to automatically generate documentation for public functions in the `di_parser` package

### Adding to the documentation

> [!IMPORTANT]
> Please follow the development instructions in the documentation

* Add new documentation in [restructured text](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html) (`.rst` suffix) format. 
* To add a new section to the documentation, create a new **.rst** file in `sphinx/source/doc_pages`
* Amend `source/index.rst` to include your new file in the table of contents at the correct location

   ```diff
   Chapter Name
   ============

   .. toctree::
      :maxdepth: 2
      :caption: Contents:

      doc_pages/installation.rst
      doc_pages/quickstart.rst
      doc_pages/overview.rst
  +  doc_pages/your_new_file.rst         # New file added here 
      doc_pages/parsing_dis.rst
      doc_pages/developing_di_parser.rst
      doc_pages/training_model.rst
      doc_pages/adapting_code.rst
   ```

* Submit a pull request to the main branch of the code. Once this pull request has been merged, documentation on [GitHub pages](https://public-health-scotland.github.io/dose_instruction_parser/) will be automatically updated by the GitHub workflow at `../.github/workflows/docs.yaml`. Double check that the docs have rendered correctly. 
