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

setup:
	# uvとnpmの準備
	command -v uv >/dev/null || pip install uv --break-system-packages
	. $${HOME}/.nvm/nvm.sh || command -v npm >/dev/null || curl -L https://www.npmjs.com/install.sh | sh


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile setup
	set -e; \
	. $${HOME}/.nvm/nvm.sh; \
	PATH=$${HOME}/.local/bin:$$PATH; \
	PATH=/opt/texlive/bin/$$(uname -m)-$$(uname -s | tr '[:upper:]' '[:lower:]'):$$PATH; \
	npm install --verbose; \
	echo "====="; echo "PATH: $$PATH"; echo "====="; \
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
