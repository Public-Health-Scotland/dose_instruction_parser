# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
print(sys.executable)
sys.path.insert(0, os.path.abspath('../../dose_instruction_parser/di_parser'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'di_parser'
copyright = '2024, Rosalyn Pearson, Nathalie Thureau, Mark Macartney, John Reid, Johanna Jokio'
author = 'Rosalyn Pearson, Nathalie Thureau, Mark Macartney, John Reid, Johanna Jokio'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx_rtd_theme',
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.githubpages'   
]

templates_path = ['_templates']
exclude_patterns = []

autosectionlabel_prefix_document = True
master_doc = "index"
language = "en"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_theme_options = {'logo_only' : True,
                      'display_version' : False}

html_css_files = [
    'custom.css',
]

html_logo = "_static/phs-logo.png"

html_favicon = "_static/favicon_phs.ico"

# -- Options for autodoc ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

# Automatically extract typehints when specified and place them in
# descriptions of the relevant function/method.
autodoc_typehints = "description"

# Don't show class signature with the class' name.
autodoc_class_signature = "separated"
autodoc_mock_imports = ["spacy", "spellchecker", "word2number", "inflect", "pytest"]

