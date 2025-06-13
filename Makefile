# Sphinx & Node.js ドキュメントビルド用 Makefile

# --- 変数定義 ---
SPHINXOPTS    ?=
SPHINXBUILD   ?= uv run sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# --- nvmセットアップ関数 ---
define nvm_setup
	if [ ! -f "$${HOME}/.nvm/nvm.sh" ]; then \
		echo "nvm をインストールします..."; \
		curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash; \
	else \
		echo "nvm は既にインストールされています。"; \
	fi; \
	. "$${HOME}/.nvm/nvm.sh"; \
	nvm install --lts; \
	nvm use --lts
endef

# --- ターゲット定義 ---

.PHONY: help clean distclean serve setup-uv node_modules

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -vfr $(BUILDDIR)

distclean: clean
	rm -fr .venv node_modules
	find . -type f \( -name ".DS_Store" -or -name ".*.swp" -or -name "*~" -or -name "*.bak" -or -name "*.orig" \) -delete 
	rm -f .uv-installed

serve: setup-uv
	export PATH=$${HOME}/.local/bin:$$PATH; \
	uv run sphinx-autobuild -b html --host 0.0.0.0 --port 8000 \
		--watch $(SOURCEDIR) --ignore "*.pyc" \
		$(SOURCEDIR) $(BUILDDIR)/html

setup-uv: .uv-installed

.uv-installed:
	command -v uv >/dev/null || pip install uv --break-system-packages
	touch .uv-installed

node_modules: node_modules/.ok

node_modules/.ok: package.json package-lock.json
	$(call nvm_setup)
	npm install --verbose
	touch node_modules/.ok

html: setup-uv
	export PATH=$${HOME}/.local/bin:$$PATH; \
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Sphinx の make mode 用キャッチオールターゲット
%:
	make setup-uv node_modules
	export PATH=$${HOME}/.local/bin:$$(pwd)/node_modules/.bin:/opt/texlive/bin/$$(uname -m)-$$(uname -s | tr A-Z a-z):$$PATH; \
	. "$${HOME}/.nvm/nvm.sh"; \
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
