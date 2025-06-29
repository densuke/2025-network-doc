# SphinxプロジェクトでMermaid図をPDFに埋め込む方法

このドキュメントは、SphinxプロジェクトでMermaid図をHTML出力だけでなく、LaTeX経由でPDF出力にも含めるための手順をまとめたものです。

## 1. 問題の背景

SphinxのHTML出力では`sphinxcontrib.mermaid`拡張機能によりMermaid図が正しく表示されますが、PDF出力はLaTeXを介して行われるため、MermaidのJavaScriptレンダリングが直接適用されず、図が表示されません。

## 2. 解決策の概要

Mermaid図をPDFに含めるためには、以下の手順を踏みます。

1.  Mermaidの定義からPNG画像を生成します。
2.  生成されたPNG画像をSphinxが認識できるように設定します。
3.  Sphinxのビルドプロセスに、この画像生成と埋め込みを自動化するステップを組み込みます。

**重要な点:** このアプローチでは、元のMarkdownファイル内のMermaidコードブロックは変更されません。ビルド時に一時的に画像を生成し、Sphinxがそれを参照する形になります。これにより、Mermaid図の編集はMarkdownファイル内で直接行え、管理が容易になります。

PNG画像を使用することで、LaTeXが画像サイズを認識でき、図中のテキストも正しく表示されます。

## 3. 詳細な手順

### 3.1. 必要なツールのインストール

#### a. `mermaid.cli`のインストール

Mermaid図を画像に変換するために、`mermaid.cli`を使用します。プロジェクトのルートディレクトリで、`package.json`を作成し、ローカルにインストールします。

**`package.json`の作成:**

```json
{
  "name": "your-sphinx-project",
  "version": "1.0.0",
  "description": "Sphinx project with Mermaid diagrams for PDF output",
  "main": "index.js",
  "scripts": {
    "mermaid-single": "mmdc -i \"$MMD_FILE\" -o \"$PNG_FILE\""
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "mermaid.cli": "^0.5.1"
  }
}
```

**インストール:**

```bash
npm install
```

#### b. `rsvg-convert` (または同等のツール) のインストール

`mermaid.cli`がSVGを生成する際に、そのSVGをPNGに変換するために`rsvg-convert`を使用します。

-   **macOS (Homebrew):**
    ```bash
    brew install librsvg
    ```
-   **Linux (apt/yum):**
    ```bash
    sudo apt-get install librsvg2-bin  # Debian/Ubuntu
    sudo yum install librsvg2-tools   # CentOS/RHEL
    ```
-   **Windows:**
    WSL (Windows Subsystem for Linux) を使用するか、他のSVG-PNG変換ツールを検討してください。

### 3.2. Mermaid図の自動処理スクリプトの作成

Markdownファイル内のMermaidコードブロックを自動的にPNG画像に変換するPythonスクリプトを作成します。このスクリプトは元のMarkdownファイルを変更しません。

**`scripts/process_mermaid.py`の作成:**

```python
import os
import re
import hashlib
import subprocess

SOURCE_DIR = "source"
MERMAID_TEMP_DIR = os.path.join(SOURCE_DIR, ".mermaid_temp")
MERMAID_IMAGES_DIR = os.path.join(SOURCE_DIR, "_images")

def ensure_dirs():
    os.makedirs(MERMAID_TEMP_DIR, exist_ok=True)
    os.makedirs(MERMAID_IMAGES_DIR, exist_ok=True)

def process_mermaid_blocks():
    ensure_dirs()
    
    for root, _, files in os.walk(SOURCE_DIR):
        for file_name in files:
            if file_name.endswith(".md"):
                filepath = os.path.join(root, file_name)
                # Read the file content
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Find all mermaid blocks
                mermaid_blocks = re.findall(r"""```\{mermaid\}\n(.*?)\n```""", content, re.DOTALL)
                
                if not mermaid_blocks:
                    continue

                for i, block in enumerate(mermaid_blocks):
                    mermaid_hash = hashlib.md5(block.encode("utf-8")).hexdigest()
                    mmd_filepath = os.path.join(MERMAID_TEMP_DIR, f"{mermaid_hash}.mmd")
                    png_filename = f"mermaid_{mermaid_hash}.png"
                    png_filepath = os.path.join(MERMAID_IMAGES_DIR, png_filename)
                    
                    # Write mermaid code to a temporary .mmd file
                    with open(mmd_filepath, "w", encoding="utf-8") as f:
                        f.write(block)

                    # Generate PNG if it doesn't exist
                    if not os.path.exists(png_filepath):
                        print(f"Generating {png_filename}...")
                        try:
                            subprocess.run(
                                ["npm", "run", "mermaid-single"],
                                check=True,
                                capture_output=True,
                                text=True,
                                env={**os.environ, "MMD_FILE": mmd_filepath, "PNG_FILE": png_filepath}
                            )
                            print(f"Successfully generated {png_filename}")
                        except subprocess.CalledProcessError as e:
                            print(f"Error generating {png_filename}: {e.stderr}")
                            continue

# No longer modifying the markdown file content here.
# Sphinx will handle including the images from _images directory.

if __name__ == "__main__":
    process_mermaid_blocks()
```

### 3.3. カスタムSphinx拡張機能の作成

SphinxがMarkdownファイル内の`mermaid`ディレクティブを画像として認識し、ビルドプロセス中に対応するPNG画像を参照できるように、カスタム拡張機能を作成します。

**`source/mermaid_pdf_extension.py`の作成:**

```python
import os
import hashlib
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

class MermaidDirective(SphinxDirective):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'alt': directives.unchanged,
        'align': directives.unchanged,
        'width': directives.unchanged,
        'height': directives.unchanged,
        'scale': directives.unchanged,
    }

    def run(self):
        # Get the mermaid code from the directive content
        mermaid_code = "\n".join(self.content)
        
        # Calculate hash for the mermaid code
        mermaid_hash = hashlib.md5(mermaid_code.encode("utf-8")).hexdigest()
        
        # Construct the image filename based on the hash
        png_filename = f"mermaid_{mermaid_hash}.png"
        
        # The path Sphinx will look for the image relative to the source directory
        # Since we put images in source/_images, the path is _images/mermaid_hash.png
        image_path = os.path.join("_images", png_filename)

        # Create an image node
        image_node = nodes.image(uri=image_path, **self.options)
        
        return [image_node]

def setup(app):
    app.add_directive("mermaid", MermaidDirective)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

### 3.4. `conf.py`の修正

Sphinxがカスタム拡張機能と生成された画像を認識できるように`conf.py`を修正します。

**`source/conf.py`の修正:**

```python
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'test'
copyright = '2025, test'
author = 'test'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'mermaid_pdf_extension',
]

templates_path = ['_templates']
exclude_patterns = []

language = 'ja'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static', '_images']
```

### 3.5. `Makefile`の修正

Sphinxのビルドコマンドが実行される前に、Mermaid図の自動処理スクリプトが実行されるように`Makefile`を修正します。また、`clean`コマンドで生成された一時ファイルや画像も削除されるようにします。

**`Makefile`の修正:**

```makefile
# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= uv run sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

.PHONY: help Makefile mermaid clean

mermaid:
	@python3 scripts/process_mermaid.py

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

html: mermaid
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

latexpdf: mermaid
	@$(SPHINXBUILD) -M latexpdf "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	@$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "Cleaning Mermaid generated files..."
	@rm -rf $(SOURCEDIR)/.mermaid_temp
	@rm -f $(SOURCEDIR)/_images/mermaid_*.png
	@echo "Mermaid generated files cleaned."

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
```

### 3.6. MarkdownファイルでのMermaid図の記述方法

Markdownファイルでは、通常通りMermaidコードブロックを記述します。ビルド時に`process_mermaid.py`スクリプトがこれを検出し、自動的にPNG画像を生成し、カスタム拡張機能がその画像をPDFに埋め込みます。

**例: `source/your_document.md`**

```markdown
# My Document

Here is a Mermaid diagram:

```{mermaid}
graph TD
    A[Start] --> B{Is it?};
    B -- Yes --> C[OK];
    C --> D[End];
    B -- No --> E[Error];
    E --> D;
```

別のMermaid図:

```{mermaid}
sequenceDiagram
    Alice->>Bob: Hello Bob, how are you?
    Bob-->>Alice: I am good thanks!
```

### 3.7. ビルドの実行

上記の設定が完了したら、通常通りSphinxのビルドコマンドを実行します。

```bash
make html
make latexpdf
```

`make latexpdf`を実行すると、`scripts/process_mermaid.py`が自動的に実行され、Mermaid図がPNG画像として生成され、PDFに埋め込まれます。

## 4. 注意事項

-   **一時ファイルと画像ディレクトリ:**
    -   `source/.mermaid_temp/`: Mermaidの定義を一時的に保存するディレクトリです。`.gitignore`に追加することを検討してください。
    -   `source/_images/`: 生成されたPNG画像が保存されるディレクトリです。`.gitignore`に追加することを検討してください。
-   **PNGの品質:** PNGはラスター画像のため、拡大するとSVGのような鮮明さは失われます。高解像度が必要な場合は、`mermaid.cli`のオプションで解像度を調整するか、SVGをPDFに変換する別の方法を検討する必要があります。
-   **Pythonのバージョン:** スクリプトはPython 3で動作します。

このガイドが、あなたのSphinxプロジェクトでMermaid図をPDFに埋め込む手助けとなることを願っています。