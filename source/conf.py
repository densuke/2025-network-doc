# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ネットワーク(2025)関連資料'
copyright = '2025, 佐藤 大輔 <densuke@st.kobedenshi.ac.jp>'
author = '佐藤 大輔 <densuke@st.kobedenshi.ac.jp>'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['myst_parser', 'sphinx_rtd_theme']


templates_path = ['_templates']
exclude_patterns = []

language = 'ja'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Later in the file, change the html_theme line to:
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- LaTeX経由PDF出力の設定 ------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
latex_docclass = {'manual': 'jsbook'}
