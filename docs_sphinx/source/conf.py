# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('../../..'))
sys.path.insert(0, os.path.abspath('../../dendrify'))

from version import __version__ as release

# -- Project information -------------------------------------------------------
project = 'Dendrify'
copyright = '2023-2025, Michalis Pagkalos. Licensed under the GPL-3.0 License.'
author = 'Michalis Pagkalos'


# -- General configuration -----------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autosummary',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel',
    'nbsphinx',
    'autodocsumm',
    'sphinx_copybutton',
]

templates_path = ['_templates']
exclude_patterns = ['_build', '**.ipynb_checkpoints']
autosummary_generate = True
nbsphinx_input_prompt = "%.0s"
nbsphinx_output_prompt = "%.0s"
autodoc_default_options = {
    'show-inheritance': True,
    'members': True,
    'inherited-members': True}
autodoc_typehints = "none"
intersphinx_mapping = {
    "brian2": ("https://brian2.readthedocs.io/en/stable/", None),
    "networkx": ("https://networkx.org/documentation/stable", None),
    "brian2cuda": ("https://brian2cuda.readthedocs.io/en/latest/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None)
}

myst_url_schemes = ["http", "https", ]

# -- HTML settings -------------------------------------------------------------
def setup(app):
    app.add_css_file("custom-nbsphinx.css")

mathjax3_config = {'chtml': {'displayAlign': 'left'}}
html_static_path = ['_static']
copybutton_prompt_text = r">>> (?!#)"
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = True
html_scaled_image_link = False
html_title = f"{project} {release}"
html_theme = 'furo'
pygments_style = "default"
pygments_dark_style = "material"
html_theme_options = {
    "sidebar_hide_name": True,
    "navigation_with_keys": True,
    "light_logo": "dendrify_logo_light.png",
    "dark_logo": "dendrify_logo_dark.png",
    "light_css_variables": {
        "color-brand-primary": "#052a91",
        "color-brand-content": "#052a91",
    },
    "dark_css_variables": {
        "color-brand-primary": "#78b2ff",
        "color-brand-content": "#78b2ff",
        "color-background-hover": "#ffffff33"
    },
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/Poirazi-Lab/dendrify",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
}
