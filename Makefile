# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= uv run sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Update PATH to include ~/.local/bin during build
# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

clean:
	pwd
	ls -l
	rm -vfr build

distclean: clean
	rm -fr .venv node_modules
	# エディタの中間保存ファイルなども削除
	find . -type f -name ".DS_Store" -or -name ".*.swp" -or -name "*~" -or -name "*.bak" -or -name "*.orig" -delete

serve:
	uv run sphinx-autobuild -b html --host 0.0.0.0 --port 8000 \
		--watch source --ignore "*.pyc" \
		source build/html

setup: node_modules/.ok
	# uv
	command -v uv >/dev/null || pip install uv || pip install uv --break-system-packages
	uv venv
	uv sync

node_modules/.ok: package.json package-lock.json
	# node.jsまわり(nvm,npm)のセットアップ→必要となるモジュールのインストール
	. $${HOME}/.nvm/nvm.sh || command -v npm >/dev/null || curl -L https://www.npmjs.com/install.sh | sh
	[ -f "$${HOME}/.nvm/nvm.sh" ] && . "$${HOME}/.nvm/nvm.sh"
	if command -v nvm >/dev/null; then
		nvm install --lts
		nvm use --lts
		npm install --verbose
		touch node_modules/.ok
	else
		echo "警告: nvm コマンドが見つかりません。npm関連の処理が期待通りに動作しない可能性があります。" >&2
	fi

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile setup
	set -e; \
	. $${HOME}/.nvm/nvm.sh; \
	export PATH=$${HOME}/.local/bin:/opt/texlive/bin/$$(uname -m)-$$(uname -s | tr A-Z a-z):$$PATH; \
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
