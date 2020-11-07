# =============================================================================
# @file    Makefile
# @brief   Makefile for some steps in creating new releases on GitHub
# @author  Michael Hucka
# @date    2020-08-11
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/handprint
# =============================================================================

# Before we go any further, test if certain programs are available.
# The following is based on the approach posted by Jonathan Ben-Avraham to
# Stack Overflow in 2014 at https://stackoverflow.com/a/25668869

PROGRAMS_NEEDED = curl gh git jq sed
TEST := $(foreach p,$(PROGRAMS_NEEDED),\
	  $(if $(shell which $(p)),_,$(error Cannot find program "$(p)")))

# Gather values that we need further below.

$(info Gathering data -- this takes a few moments ...)

name	:= $(strip $(shell grep -m 1 'name\s*=' setup.cfg	  | cut -f2 -d'='))
version	:= $(strip $(shell grep -m 1 'version\s*=' setup.cfg	  | cut -f2 -d'='))
url	:= $(strip $(shell grep -m 1 'url\s*=' setup.cfg	  | cut -f2 -d'='))
desc	:= $(strip $(shell grep -m 1 'description\s*=' setup.cfg  | cut -f2 -d'='))
author	:= $(strip $(shell grep -m 1 'author\s*=' setup.cfg	  | cut -f2 -d'='))
email	:= $(strip $(shell grep -m 1 'author_email\s*=' setup.cfg | cut -f2 -d'='))
license	:= $(strip $(shell grep -m 1 'license\s*=' setup.cfg      | cut -f2 -d'='))

branch	  := $(shell git rev-parse --abbrev-ref HEAD)
repo	  := $(strip $(shell gh repo view | head -1 | cut -f2 -d':'))
id	  := $(shell curl -s https://api.github.com/repos/$(repo) | jq '.id')
id_url	  := https://data.caltech.edu/badge/latestdoi/$(id)
doi_url	  := $(shell curl -sILk $(id_url) | grep Locat | cut -f2 -d' ')
doi	  := $(subst https://doi.org/,,$(doi_url))
doi_tail  := $(lastword $(subst ., ,$(doi)))
init_file := $(name)/__init__.py
tmp_file  := $(shell mktemp /tmp/release-notes-$(name).XXXXXX)

$(info Gathering data ... Done.)

# The main action is "make release".

release: | test-branch release-on-github print-instructions

test-branch:
ifneq ($(branch),main)
	$(error Current git branch != main. Merge changes into main first)
endif

update-init-file:;
	@sed -i .bak -e "s|^\(__version__ *=\).*|\1 '$(version)'|"  $(init_file)
	@sed -i .bak -e "s|^\(__description__ *=\).*|\1 '$(desc)'|" $(init_file)
	@sed -i .bak -e "s|^\(__url__ *=\).*|\1 '$(url)'|"	    $(init_file)
	@sed -i .bak -e "s|^\(__author__ *=\).*|\1 '$(author)'|"    $(init_file)
	@sed -i .bak -e "s|^\(__email__ *=\).*|\1 '$(email)'|"	    $(init_file)
	@sed -i .bak -e "s|^\(__license__ *=\).*|\1 '$(license)'|"  $(init_file)

update-codemeta-file:;
	@sed -i .bak -e "/version/ s/[0-9].[0-9][0-9]*.[0-9][0-9]*/$(version)/" codemeta.json

edited := codemeta.json $(init_file)

check-in-updated-files:;
	git add $(edited)
	git diff-index --quiet HEAD $(edited) || git commit -m"Update version" $(edited)

release-on-github: | update-init-file update-codemeta-file check-in-updated-files
	git push -v --all
	git push -v --tags
	$(info ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓)
	$(info ┃ Write release notes in the file that will be opened in your editor ┃)
	$(info ┃ then save and close the file to complete this release process.     ┃)
	$(info ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛)
	sleep 2
	$(EDITOR) $(tmp_file)
	gh release create v$(version) -t "Release $(version)" -F $(tmp_file)

print-instructions:;
	$(info ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓)
	$(info ┃ Next steps:                                                        ┃)
	$(info ┃ 1. Visit https://github.com/$(repo)/releases )
	$(info ┃ 2. Double-check the draft release, and click "Publish" if ready    ┃)
	$(info ┃ 3. Wait a few seconds to let web services do their work            ┃)
	$(info ┃ 4. Run "make update-doi" to update the DOI in README.md            ┃)
	$(info ┃ 5. Run "make create-dist" and check the distribution for problems  ┃)
	$(info ┃ 6. Run "make test-pypi" to push to test.pypi.org                   ┃)
	$(info ┃ 7. Double-check https://test.pypi.org/$(repo) )
	$(info ┃ 8. Run "make pypi" to push to pypi for real                        ┃)
	$(info ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛)
	@echo ""

update-doi: 
	sed -i .bak -e 's|DOI-.*-blue|DOI-$(doi)-blue|' README.md
	sed -i .bak -e 's|caltech.edu/records/[0-9]\{1,\}|caltech.edu/records/$(doi_tail)|' README.md
	git add README.md
	git diff-index --quiet HEAD README.md || git commit -m"Update DOI" README.md && git push -v --all

create-dist: clean
	python3 setup.py sdist bdist_wheel
	python3 -m twine check dist/*

test-pypi: create-dist
	python3 -m twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/*

pypi: create-dist
	python3 -m twine upload --verbose dist/*

clean:;
	-rm -rf dist build $(name).egg-info

.PHONY: release release-on-github update-init-file update-codemeta-file \
	print-instructions create-dist clean test-pypi pypi
