# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import os

# カスタム拡張のパスを追加
sys.path.insert(0, os.path.abspath('extensions'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ネットワーク(2025)関連資料'
copyright = '2025, 佐藤 大輔 <densuke@st.kobedenshi.ac.jp>'
author = '佐藤 大輔 <densuke@st.kobedenshi.ac.jp>'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx.ext.mathjax',  # HTMLでの数式表示（MathJax）
    'sphinx_rtd_theme',
    'sphinx_mermaid_lightweight',
]

# MyST で $...$ / $$...$$ や \begin{align} ... \end{align} を有効化
myst_enable_extensions = [
    'dollarmath',  # $...$ / $$...$$ 記法
    'amsmath',     # {math} ディレクティブや環境
]

# （任意）MathJax v3 の数式番号付与などの設定
mathjax3_config = {
    'tex': {
        'tags': 'ams',          # \label と \eqref による式番号
        'useLabelIds': True,
    }
}


templates_path = ['_templates']
exclude_patterns = []

language = 'ja'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Later in the file, change the html_theme line to:
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Mermaid.js setup from node_modules ------------------
import shutil
from pathlib import Path

def copy_mermaid_assets(app, config):
    """Copy Mermaid.js from node_modules to _static"""
    static_dir = Path(app.outdir) / '_static'
    static_dir.mkdir(exist_ok=True)
    
    # node_modulesからMermaidファイルをコピー
    mermaid_source = Path('node_modules/mermaid/dist/mermaid.min.js')
    mermaid_dest = static_dir / 'mermaid.min.js'
    
    if mermaid_source.exists():
        shutil.copy2(mermaid_source, mermaid_dest)
        print(f"Copied Mermaid.js: {mermaid_source} -> {mermaid_dest}")
    else:
        print(f"Warning: Mermaid.js not found at {mermaid_source}")

def setup_mermaid(app):
    """Setup Mermaid.js for Sphinx"""
    app.connect('config-inited', copy_mermaid_assets)

# -- LaTeX経由PDF出力の設定 ------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
latex_docclass = {'manual': 'jsbook'}
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
    'preamble': r"""
        \usepackage{hyperref}
        \usepackage{float}
        \hypersetup{
            colorlinks=true,
            linkcolor=blue,
            filecolor=magenta,
            urlcolor=blue,
            pdftitle={\@title},
            pdfpagemode=FullScreen,
            }
        % 図表周りのスペーシング調整
        \setlength{\floatsep}{12pt plus 2pt minus 2pt}
        \setlength{\textfloatsep}{18pt plus 2pt minus 4pt}
        \setlength{\intextsep}{12pt plus 2pt minus 2pt}
        % 画像の最大サイズ制御（既存画像にも適用）
        \usepackage{adjustbox}
        \let\oldincludegraphics\includegraphics
        \renewcommand{\includegraphics}[2][]{\adjustbox{max width=0.9\textwidth,max height=0.7\textheight,center}{\oldincludegraphics[#1]{#2}}}
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
# 図表の配置制御を最適化（Mermaidは個別に[H]制御）
latex_elements['figure_align'] = 'htbp'

# -- Lightweight Mermaid設定 ------------------------------
# 軽量Mermaid拡張の設定
mermaid_use_ink = True      # mermaid.ink API使用 (プライマリ)
mermaid_use_kroki = True    # Kroki API使用 (セカンダリ)
mermaid_use_cli = True      # ローカルmermaid-cli使用 (フォールバック)
mermaid_kroki_url = 'https://kroki.io'  # Kroki APIエンドポイント

# LaTeX/PDF出力時の画像サイズ制御
mermaid_max_width = '0.6\\textwidth'     # 最大幅（ページ幅の60%に制限）
mermaid_max_height = '0.45\\textheight'  # 最大高さ（ページ高さの45%に制限）

# 余白問題対策設定
mermaid_latex_format = 'png'          # LaTeX出力フォーマット (pdf/png) - PNG推奨
mermaid_crop_pdf = True               # PDFクロッピング有効/無効

# -- Setup Mermaid.js from node_modules ------------------
# Sphinxアプリケーション初期化時にMermaid.jsをセットアップ
def setup(app):
    setup_mermaid(app)
