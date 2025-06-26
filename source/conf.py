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

extensions = ['myst_parser', 'sphinx_rtd_theme',
            'sphinxcontrib.mermaid', 'sphinx.ext.todo',]

todo_include_todos = True


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
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
    'preamble': r"""
        \usepackage{hyperref}
        \hypersetup{
            colorlinks=true,
            linkcolor=blue,
            filecolor=magenta,
            urlcolor=blue,
            pdftitle={\@title},
            pdfpagemode=FullScreen,
            }
    """
}
latex_show_urls = 'footnote'
latex_show_pagerefs = True
latex_use_latex_multicolumn = True
# 出力されるファイル名(LaTeX -> PDF)
master_doc = 'index'
latex_documents = [
    (master_doc, 'network2025.tex', 'ネットワーク(2025)関連資料', author, 'manual'),
]
# 図表の配置を可能な限り同じページで中央寄せにする
latex_elements['figure_align'] = 'H'
