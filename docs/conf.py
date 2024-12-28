# -*- coding: utf-8 -*-
#
# Sphinx documentation builder configuration file.
#
# Contains selected common configuration options.
# For complete options list, visit:
# http://www.sphinx-doc.org/en/stable/config

# -- Setup paths ----------------------------------------------------------

# For autodoc extensions or modules in different directories,
# add directory paths here. For relative paths to documentation root,
# convert to absolute using os.path.abspath as shown below.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../'))

# -- Basic project details ------------------------------------------------

project = 'GitAnalyzer'
copyright = '2024, Shawn'
author = 'Shawn'

# Version info
version = ''  # Short X.Y version
release = '1.0'  # Complete version including alpha/beta/rc tags

# -- Core configuration --------------------------------------------------

# Minimum required Sphinx version (uncomment if needed)
# needs_sphinx = '1.0'

# Sphinx extensions (both built-in and custom)
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest'
]

# Template directory location
templates_path = ['_templates']

# Source file extensions
source_suffix = '.rst'  # Can be list: ['.rst', '.md']

# Root document for the documentation
master_doc = 'index'

# Documentation language (None = default)
language = None

# Files/directories to ignore
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store'
]

# Syntax highlighting style
pygments_style = 'sphinx'

# -- HTML output settings ------------------------------------------------

# Selected HTML theme
html_theme = 'sphinx_rtd_theme'

# Theme-specific options
html_theme_options = {}

# Static files directory (CSS, JavaScript, images)
html_static_path = ['_static']

# Sidebar template configuration
# Default: ['localtoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html']
# html_sidebars = {}

# -- HTMLHelp settings --------------------------------------------------

htmlhelp_basename = 'GitAnalyzerdoc'

# -- LaTeX output configuration -----------------------------------------

latex_elements = {
    # Uncomment and modify as needed:
    # 'papersize': 'letterpaper',
    # 'pointsize': '10pt',
    # 'preamble': '',
    # 'figure_align': 'htbp',
}

# LaTeX document organization
latex_documents = [
    (
        master_doc,
        'GitAnalyzer.tex',
        'GitAnalyzer Documentation',
        'Shawn',
        'manual'
    ),
]

# -- Manual page configuration ------------------------------------------

man_pages = [
    (
        master_doc,
        'gitanalyzer',
        'GitAnalyzer Documentation',
        [author],
        1
    )
]

# -- Texinfo output configuration --------------------------------------

texinfo_documents = [
    (
        master_doc,
        'GitAnalyzer',
        'GitAnalyzer Documentation',
        author,
        'GitAnalyzer',
        'Advanced Git Repository Analysis Tool',
        'Miscellaneous'
    ),
]