from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Flask-Exts'
copyright = '2024, HuaDong'
author = 'HuaDong'
release, version = get_version("Flask-Exts")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.doctest',    
    'sphinx.ext.autosummary',    
    "pallets_sphinx_themes",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'flask'
html_static_path = ['_static']
html_title = f"Flask-Exts Documentation ({version})"
