# -*- coding: utf-8 -*-

import os
import sys
from datetime import date
import yaml
import re
from docutils import nodes
from recommonmark.transform import AutoStructify
from recommonmark.parser import CommonMarkParser, splitext, urlparse
from sphinx_scylladb_theme.utils import multiversion_regex_builder
from redirects_cli import cli as redirects_cli

# -- General configuration ------------------------------------------------

# Build documentation for the following tags and branches
TAGS = []
BRANCHES = ['scylla-3.7.2.x', 'scylla-3.10.2.x', 'scylla-3.11.0.x', 'scylla-3.11.2.x', 'scylla-4.7.2.x', 'scylla-4.10.0.x', 'scylla-4.11.1.x', 'scylla-4.12.0.x', 'scylla-4.13.0.x', 'scylla-4.14.1.x', 'scylla-4.15.0.x']
# Set the latest version.
LATEST_VERSION = 'scylla-4.15.0.x'
# Set which versions are not released yet.
UNSTABLE_VERSIONS = []
# Set which versions are deprecated
DEPRECATED_VERSIONS = []

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinx.ext.githubpages',
    'sphinx.ext.extlinks',
    'sphinx_sitemap',
    'sphinx.ext.autosectionlabel',
    'sphinx_scylladb_theme',
    'sphinx_multiversion',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
autosectionlabel_prefix_document = True

# The master toctree document.
master_doc = 'contents'

# General information about the project.
project = 'Scylla Java Driver'
copyright = str(date.today().year) + ', ScyllaDB. All rights reserved.'
author = u'Scylla Project Contributors'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '_utils']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for not found extension -------------------------------------------

# Template used to render the 404.html generated by this extension.
notfound_template =  '404.html'

# Prefix added to all the URLs generated in the 404 page.
notfound_urls_prefix = ''

# -- Options for multiversion extension ----------------------------------

# Whitelist pattern for tags
smv_tag_whitelist = multiversion_regex_builder(TAGS)
# Whitelist pattern for branches
smv_branch_whitelist = multiversion_regex_builder(BRANCHES)
# Defines which version is considered to be the latest stable version.
# Must be listed in smv_tag_whitelist or smv_branch_whitelist.
smv_latest_version = LATEST_VERSION
smv_rename_latest_version = 'stable'
# Whitelist pattern for remotes (set to None to use local branches only)
smv_remote_whitelist = r'^origin$'
# Pattern for released versions
smv_released_pattern = r'^tags/.*$'
# Format for versioned output directories inside the build directory
smv_outputdir_format = '{ref.name}'

# -- Options for sitemap extension ---------------------------------------

sitemap_url_scheme = "/stable/{link}"

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_scylladb_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    'conf_py_path': 'docs/source/',
    'branch_substring_removed': 'scylla-',
    'github_repository': 'scylladb/java-driver',
    'github_issues_repository': 'scylladb/java-driver',
    'hide_edit_this_page_button': 'false',
    'hide_feedback_buttons': 'false',
    'versions_unstable': UNSTABLE_VERSIONS,
    'versions_deprecated': DEPRECATED_VERSIONS,
    'hide_version_dropdown': ['scylla-3.x'],
    'skip_warnings': 'document_has_underscores'
}

# If not None, a 'Last updated on:' timestamp is inserted at every page
# bottom, using the given strftime format.
# The empty string is equivalent to '%b %d, %Y'.
#
html_last_updated_fmt = '%d %B %Y'

# Custom sidebar templates, maps document names to template names.
#
html_sidebars = {'**': ['side-nav.html']}

# Output file base name for HTML help builder.
htmlhelp_basename = 'ScyllaDocumentationdoc'

# URL which points to the root of the HTML documentation. 
html_baseurl = 'https://java-driver.docs.scylladb.com'

# Dictionary of values to pass into the template engine’s context for all pages
html_context = {'html_baseurl': html_baseurl}

# -- Initialize Sphinx ----------------------------------------------

class CustomCommonMarkParser(CommonMarkParser):
    
    def visit_document(self, node):
        pass
    
    def visit_link(self, mdnode):
        # Override MarkDownParser to avoid checking if relative links exists
        ref_node = nodes.reference()
        destination = mdnode.destination
        _, ext = splitext(destination)

        url_check = urlparse(destination)
        scheme_known = bool(url_check.scheme)

        if not scheme_known and ext.replace('.', '') in self.supported:
            destination = destination.replace(ext, '')
        ref_node['refuri'] = destination
        ref_node.line = self._get_line(mdnode)
        if mdnode.title:
            ref_node['title'] = mdnode.title
        next_node = ref_node

        self.current_node.append(next_node)
        self.current_node = ref_node

def replace_relative_links(app, docname, source):
    result = source[0]
    for key in app.config.replacements:
        result = re.sub(key, app.config.replacements[key], result)
    source[0] = result


def build_finished(app, exception):
    version_name = os.getenv("SPHINX_MULTIVERSION_NAME", "")
    version_name = "/" + version_name if version_name else ""
    redirect_to = version_name +'/api/index.html'
    out_file = app.outdir +'/api.html'
    redirects_cli.create(redirect_to=redirect_to,out_file=out_file)

def setup(app):
    # Setup Markdown parser
    app.add_source_parser(CustomCommonMarkParser)
    app.add_config_value('recommonmark_config', {
        'enable_eval_rst': True,
        'enable_auto_toc_tree': False,
    }, True)
    app.add_transform(AutoStructify)

    # Replace DataStax links
    current_slug = os.getenv("SPHINX_MULTIVERSION_NAME", "stable")
    replacements = {
        r'docs.datastax.com/en/drivers/java\/(.*?)\/': "java-driver.docs.scylladb.com/" + current_slug + "/api/",
        r'java-driver.docs.scylladb.com\/(.*?)\/': "java-driver.docs.scylladb.com/" + current_slug + "/"
    }
    app.add_config_value('replacements', replacements, True)
    app.connect('source-read', replace_relative_links)

    # Create redirect to JavaDoc API
    app.connect('build-finished', build_finished)
    
