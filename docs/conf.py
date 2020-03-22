# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import sys
from pathlib import Path


# curr_file = Path(__file__).parent
# sys.path.append(curr_file.joinpath("..").resolve())
# sys.path.append(curr_file.joinpath("../..").resolve())


def get_version():
    import toml

    toml_path = Path(__file__).parent.joinpath("..", "pyproject.toml")

    with open(toml_path, "r") as file:
        pyproject = toml.load(file)

    return pyproject["tool"]["poetry"]["version"]


# -- Project information -----------------------------------------------------

project = "pyrh"
copyright = "2020, Unofficial Robinhood Python API"
author = "Unofficial Robinhood Python API"

# The full version, including alpha/beta/rc tags
release = get_version()


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx.ext.intersphinx"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# source_suffix = '.rst'
source_suffix = [".rst"]

# intersphinx
intersphinx_mapping = {
    "requests": ("https://requests.readthedocs.io/en/master/", None),
}
