# Sphinx & Node.js ドキュメントビルド用 Makefile

# --- 変数定義 ---
SPHINXOPTS    ?=
SPHINXBUILD   ?= uv run sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# --- ユーティリティ関数 ---
define nvm_setup
	if [ -f "$${HOME}/.nvm/nvm.sh" ]; then \
		echo "nvm は既にインストールされています。"; \
	else \
		echo "nvm をインストールします..."; \
		curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash; \
	fi; \
	[ -f "$${HOME}/.nvm/nvm.sh" ] && . "$${HOME}/.nvm/nvm.sh"; \
	command -v nvm >/dev/null || exit 1; \
	nvm install --lts; \
	nvm use --lts
endef

# --- ターゲット定義 ---

.PHONY: help clean distclean serve setup

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -vfr $(BUILDDIR)

distclean: clean
	rm -fr .venv node_modules
	# エディタやOSの一時ファイルも削除
	find . -type f \( -name ".DS_Store" -or -name ".*.swp" -or -name "*~" -or -name "*.bak" -or -name "*.orig" \) -delete

serve: setup
	uv run sphinx-autobuild -b html --host 0.0.0.0 --port 8000 \
		--watch $(SOURCEDIR) --ignore "*.pyc" \
		$(SOURCEDIR) $(BUILDDIR)/html

setup: node_modules/.ok
	# uv のインストール確認
	command -v uv >/dev/null || pip install uv || pip install uv --break-system-packages

node_modules/.ok:
	$(call nvm_setup)
	npm install --verbose
	touch node_modules/.ok

# Sphinx の make mode 用キャッチオールターゲット
%: Makefile
	export PATH=$${HOME}/.local/bin:/opt/texlive/bin/$$(uname -m)-$$(uname -s | tr A-Z a-z):$$PATH; \
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
