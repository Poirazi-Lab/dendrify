# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('../../..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Dendrify'
copyright = '2022, Michalis Pagkalos'
author = 'Michalis Pagkalos'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autosummary',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'nbsphinx',
    'autodocsumm'
]

templates_path = ['_templates']
exclude_patterns = ['_build', '**.ipynb_checkpoints']
html_theme = 'furo'
html_static_path = ['_static']
autosummary_generate = True
pygments_style = 'sphinx'
html_title = "Dendrify"
autodoc_default_options = {'show-inheritance': True}
autodoc_typehints = "none"
