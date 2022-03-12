# =============================================================================
# @file    Makefile
# @brief   Makefile for building docs using Sphinx and MyST
# @created 2021-01-25
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/handprint
# =============================================================================

# Before we go any further, test if certain programs are available.
# The following is based on the approach posted by Jonathan Ben-Avraham to
# Stack Overflow in 2014 at https://stackoverflow.com/a/25668869

PROGRAMS_NEEDED = sphinx-build
TEST := $(foreach p,$(PROGRAMS_NEEDED),\
	  $(if $(shell which $(p)),_,$(error Cannot find program "$(p)")))


# Gather values that we need ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# You can set the following variables from the command line, and also from
# the environment for the first two.

SPHINXOPTS  ?=
SPHINXBUILD ?= sphinx-build
SPHINXAUTO  = sphinx-autobuild
SOURCEDIR   = .
BUILDDIR    = _build

# Actions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

auto autobuild live livehtml:
	@$(SPHINXAUTO) "$(SOURCEDIR)" "$(BUILDDIR)"/html $(SPHINXOPTS) $(O)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)


# Cleanup and miscellaneous directives ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.PHONY: help auto autobuild livehtml Makefile
