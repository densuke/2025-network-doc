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

$(CURDIR)/node_modules/.bin:
	@echo "Installing dependencies..."
	@npm install

serve:
	uv run sphinx-autobuild -b html --host 0.0.0.0 --port 8000 \
		--watch source --ignore "*.pyc" \
		source build/html
# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile $(CURDIR)/node_modules/.bin
	PATH=$(CURDIR)/node_modules/.bin:~/.local/bin:$(PATH) \
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
