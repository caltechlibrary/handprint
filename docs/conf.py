# =============================================================================
# @file    conf.py
# @brief   COnfiguration file for Sphynx + MyST based documentation
# @created 2021-01-25
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/handprint
#
# This file only contains a selection of the most common options. For a full
# list, refer to https://www.sphinx-doc.org/en/master/usage/configuration.html
# =============================================================================

project = 'Handprint'
copyright = '2022, Caltech Library'
author = 'Michael Hucka @ Caltech Library'


# -- General configuration ----------------------------------------------------

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.napoleon',
    'sphinxcontrib.mermaid'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'README.md',
                    '**/README.md']


# -- Sphinx options for HTML output -------------------------------------------

html_title = 'Handprint'
html_short_title = "Home"

html_logo = "_static/media/handprint-icon-white.png"
html_favicon = "_static/media/favicon.ico"

# The theme to use for HTML and HTML Help pages.
html_theme = 'sphinx_material'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Our additional CSS.
html_css_files   = ['css/custom.css']

html_show_sourcelink = False
html_sidebars = {
    "**": ["globaltoc.html", "searchbox.html"]
}

# Show the last updated date in the footer using the default format.
html_last_updated_fmt = ""


# -- Options for the Material theme -------------------------------------------
# C.f. https://github.com/bashtage/sphinx-material/blob/master/docs/conf.py

# Material theme options (see theme.conf for more information)
html_theme_options = {

    # Set the name of the project to appear in the navigation.
    'nav_title': 'Handprint',

    # Set you GA account ID to enable tracking
    'google_analytics_account': '',

    # Specify a base_url used to generate sitemap.xml. If not
    # specified, then no sitemap will be built.
    'base_url': 'https://caltechlibrary.github.io/handprint',

    # Set the colors. I found a list here:
    # https://squidfunk.github.io/mkdocs-material/setup/changing-the-colors/
    "theme_color": 'blue-grey',
    'color_primary': 'deep-orange',
    'color_accent': 'teal',

    # Set the repo location to get a badge with stats
    'repo_url': 'https://github.com/caltechlibrary/handprint/',
    'repo_name': 'Handprint',

    # Visible levels of the global TOC; -1 means unlimited
    'globaltoc_depth': 2,
    # If False, expand all TOC entries
    'globaltoc_collapse': False,
    # If True, show hidden TOC entries
    'globaltoc_includehidden': False,

    "html_minify": False,
    "html_prettify": False,

    "version_dropdown": False,
    "version_json": "_static/versions.json",
    # "version_info": {
    #     "Release": "https://bashtage.github.io/sphinx-material/",
    #     "Development": "https://bashtage.github.io/sphinx-material/devel/",
    #     "Release (rel)": "/sphinx-material/",
    #     "Development (rel)": "/sphinx-material/devel/",
    # },
}


# -- Options for the MyST parser ----------------------------------------------

myst_enable_extensions = [
    "colon_fence",
    "html_image",
    "linkify",
    "smartquotes",
    "substitution"
]
