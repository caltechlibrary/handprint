# =============================================================================
# @file    Makefile
# @brief   Makefile for generating a PDF version of a JOSS paper, to preview it
# @author  Michael Hucka <mhucka@caltech.edu>
# @license https://github.com/caltechlibrary/template/blob/main/LICENSE
# @website https://gist.github.com/mhucka/c0b82778417f38f7ae6ee7d051cec90a
#
# The procedure for using this is very simple:
#   1. Create a directory for your paper
#   2. Copy your paper's Markdown, bib, & other source files into the directory
#   3. Copy this Makefile into the directory
#   4. Update this Makefile's configuration variables (see below)
#   5. Run "make setup"
#   6. Run "make paper"
#
# To get an auto-refreshed preview while editing, open the PDF file in a PDF
# viewer that auto-refreshes when it detects changes to the PDF file (e.g.,
# Skim on macOS), and run "make auto" instead of "make paper".
# =============================================================================

# CONFIGURATION VARIABLES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# The output PDF file and the bibliography .bib file are based on this name.
basename  := paper

# Set the following to the actual DOI for the archive of your software.
archive_doi := http://dx.doi.org/00.00000/zenodo.0000000

# The values of the following are irrelevant for a preview, and you can just
# leave them as-is. If you want to (re)create the PDF using final published
# values, then go ahead and update these once you know the appropriate values.
volume	  := 0
issue	  := 0
pages	  := 0
year	  := $(shell date +'%Y')
submitted := 00 January $(year)
accepted  := 00 January $(year)

# End of configuration section. You shouldn't have to change anything below.

# DEFAULT ACTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

help:
	@printf 'Available commands:\n\n'
	@printf 'make\n'
	@printf 'make help\n'
	@printf '  Print this summary of available commands.\n\n'
	@printf 'make setup\n'
	@printf '  Download a copy of Whedon and do some other setup work.\n\n'
	@printf 'make paper\n'
	@printf '  Run pandoc to create a PDF file to preview the paper.\n\n'
	@printf 'make auto\n'
	@printf '  Watch input files for changes and auto-remake the paper.\n'

# MAIN CODE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

setup:
	git clone --recursive git@github.com:openjournals/whedon.git
	@which pandoc > /dev/null || echo \
	  "\n\033[31m*** Cannot find pandoc -- please install it ***\033[0m\n"

input   := $(basename).md
output  := $(basename).pdf
bib     := $(basename).bib
title	:= $(shell grep title: $(input) | sed 's/title: *//' | tr -d "'")
authors := $(shell sed -n '/authors:/,/affiliations:/p' $(input) | grep name: |\
	      sed 's/- name: *//' | paste -d, -s - | sed 's/,/, /g')
repo	:= $(shell git remote get-url origin |\
	      sed 's|git@github.com:|https://github.com/|' | sed 's/\.git//')

paper $(output): check-have-pandoc check-whedon-exists $(input) $(bib) Makefile
	pandoc -s $(input) --verbose \
	-V title="$(title)" \
	-V paper_title="$(title)" \
	-V citation_author="$(authors)" \
	-V formatted_doi="10.21105/joss.$(pages)" \
	-V review_issue_url="https://github.com/openjournals/joss-reviews/issues/$(issue)" \
	-V repository="$(repo)" \
	-V archive_doi="$(archive_doi)" \
	-V submitted="$(submitted)" \
	-V published="$(accepted)" \
	-V journal_name="Journal of Open Source Software" \
	-V issue="$(issue)" \
	-V volume="$(volume)" \
	-V year="$(year)" \
	-V page="$(pages)" \
	-V graphics="true" \
	-V logo_path="whedon/resources/joss/logo.png" \
	-V geometry:margin=1in \
	-o $(output) \
	--pdf-engine=xelatex \
	--citeproc \
	--csl "whedon/resources/apa.csl" \
	--template "whedon/resources/latex.template"

autorefresh auto: check-have-entr
	((ls $(input) $(bib) Makefile | entr make $(output)) &)

# MISCELLANEOUS DIRECTIVES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

check-have-pandoc:; @which python > /dev/null

check-have-entr:; @which entr > /dev/null

check-whedon-exists:; @if [ ! -d whedon ]; then echo \
	   "\n\033[31m*** Could not find whedon -- run 'make setup' ***\033[0m\n";\
	    exit 1; fi;

.PHONY: check-have-pandoc check-have-entr check-whedon-exists
