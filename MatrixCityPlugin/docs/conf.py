# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../Content/Python'))


# -- Project information -----------------------------------------------------

project = 'XRFeitoriaGear'
copyright = '2022, meihaiyi'
author = 'meihaiyi'

# The full version, including alpha/beta/rc tags
release = '0.1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # 'myst_parser',
    'recommonmark',
    'sphinx.ext.viewcode',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx', 
    'sphinx.ext.autosectionlabel',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'stencil_json.py']

master_doc = 'index'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_book_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_css_files = ['css/readthedocs.css']

html_theme_options = {
    "repo_type": "gitlab",
    "repository_url": "https://gitlab.bj.sensetime.com/openxrlab/xrfeitoria/xrfeitoria-gear",
    "use_repository_button": True,
    # "use_issues_button": True,
    # "use_edit_page_button": True,
}

# -- Extension -------------------------------------------------------------

# reference:
# https://github.com/tensorpack/tensorpack/blob/master/docs/conf.py

from sphinx.domains import Domain

class GithubURLDomain(Domain):
    """
    Resolve certain links in markdown files to github source.
    """

    name = "githuburl"
    ROOT = "https://gitlab.bj.sensetime.com/openxrlab/xrfeitoria/xrfeitoria-gear/-/tree/master/"

    def resolve_any_xref(self, env, fromdocname, builder, target, node, contnode):
        github_url = None
        print(f"target_: {target}")
        if ".html" not in target:
            if target.startswith("../"):
                # url = target.replace("../", "")
                url = target[3:]
                github_url = url
        
                print(f"github_url: {github_url}")
            
            # fix link of releases page
            if target.endswith("releases"):
                github_url = "../" + github_url

        if github_url is not None:
            if github_url.endswith("README"):
                github_url += ".md"
            print("Ref {} resolved to github:{}".format(target, github_url))
            contnode["refuri"] = self.ROOT + github_url
            return [("githuburl:any", contnode)]
        else:
            return []


def setup(app):
    print('setup app')
    from recommonmark.transform import AutoStructify
    app.add_domain(GithubURLDomain)
    app.add_config_value('recommonmark_config', {
        'auto_toc_tree_section': 'Contents',
        'enable_math': True,
        'enable_inline_math': True,
        'enable_eval_rst': True
        }, True)
    app.add_transform(AutoStructify)