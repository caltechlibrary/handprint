# =============================================================================
# @file    Makefile
# @brief   Makefile for some steps in creating new releases on GitHub
# @author  Michael Hucka
# @date    2020-08-11
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/handprint
# =============================================================================

.ONESHELL: 				# Run all commands in the same shell.
.SHELLFLAGS += -e			# Exit at the first error.

# Before we go any further, test if certain programs are available.
# The following is based on the approach posted by Jonathan Ben-Avraham to
# Stack Overflow in 2014 at https://stackoverflow.com/a/25668869

PROGRAMS_NEEDED = curl gh git jq sed
TEST := $(foreach p,$(PROGRAMS_NEEDED),\
	  $(if $(shell which $(p)),_,$(error Cannot find program "$(p)")))


# Gather values that we need ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

$(info Gathering data ... Done.)


# make release ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

release: | test-branch release-on-github print-instructions

test-branch:
ifneq ($(branch),main)
	$(error Current git branch != main. Merge changes into main first)
endif

update-init:;
	@sed -i .bak -e "s|^\(__version__ *=\).*|\1 '$(version)'|"  $(init_file)
	@sed -i .bak -e "s|^\(__description__ *=\).*|\1 '$(desc)'|" $(init_file)
	@sed -i .bak -e "s|^\(__url__ *=\).*|\1 '$(url)'|"	    $(init_file)
	@sed -i .bak -e "s|^\(__author__ *=\).*|\1 '$(author)'|"    $(init_file)
	@sed -i .bak -e "s|^\(__email__ *=\).*|\1 '$(email)'|"	    $(init_file)
	@sed -i .bak -e "s|^\(__license__ *=\).*|\1 '$(license)'|"  $(init_file)

update-codemeta:;
	@sed -i .bak -e "/version/ s/[0-9].[0-9][0-9]*.[0-9][0-9]*/$(version)/" codemeta.json

update-citation:;
	$(eval date  := $(shell date "+%F"))
	@sed -i .bak -e "/^date-released/ s/[0-9][0-9-]*/$(date)/" CITATION.cff
	@sed -i .bak -e "/^version/ s/[0-9].[0-9][0-9]*.[0-9][0-9]*/$(version)/" CITATION.cff

edited := codemeta.json $(init_file) CITATION.cff

commit-updates:;
	git add $(edited)
	git diff-index --quiet HEAD $(edited) || \
	    git commit -m"Update stored version number" $(edited)

release-on-github: | update-init update-codemeta commit-updates
	$(eval tmp_file  := $(shell mktemp /tmp/release-notes-$(name).XXXX))
	git push -v --all
	git push -v --tags
	$(info ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓)
	$(info ┃ Write release notes in the file that gets opened in your  ┃)
	$(info ┃ editor. Close the editor to complete the release process. ┃)
	$(info ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛)
	sleep 2
	$(EDITOR) $(tmp_file)
	gh release create v$(version) -t "Release $(version)" -F $(tmp_file)

print-instructions:;
	$(info ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓)
	$(info ┃ Next steps:                                             ┃)
	$(info ┃ 1. Visit https://github.com/$(repo)/releases )
	$(info ┃ 2. Check the release                                    ┃)
	$(info ┃ 3. Wait a few seconds to let web services do their work ┃)
	$(info ┃ 4. Run "make update-doi" to update the DOI in README.md ┃)
	$(info ┃ 5. Run "make packages" & check the results              ┃)
	$(info ┃ 6. Run "make test-pypi" to push to test.pypi.org        ┃)
	$(info ┃ 7. Check https://test.pypi.org/$(repo) )
	$(info ┃ 8. Run "make pypi" to push to pypi for real             ┃)
	$(info ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛)
	@echo ""

update-doi: 
	sed -i .bak -e 's|/api/record/[0-9]\{1,\}|/api/record/$(doi_tail)|' README.md
	sed -i .bak -e 's|edu/records/[0-9]\{1,\}|edu/records/$(doi_tail)|' README.md
	sed -i .bak -e '/doi:/ s|10.22002/[0-9]\{1,\}|10.22002/$(doi_tail)|' CITATION.cff
	git add README.md CITATION.cff
	git diff-index --quiet HEAD README.md || \
	    (git commit -m"Update DOI" README.md && git push -v --all)
	git diff-index --quiet HEAD CITATION.cff || \
	    (git commit -m"Update DOI" CITATION.cff && git push -v --all)

packages: clean
	python3 setup.py sdist bdist_wheel
	python3 -m twine check dist/*

test-pypi: packages
	python3 -m twine upload --repository testpypi dist/$(name)-$(version)*.{whl,gz}

pypi: packages
	python3 -m twine upload dist/*


# make executables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

binaries binary: 
	mkdir -p dist/binary
	dev/scripts/create-pyz dist/binary 3.8.2
	dev/scripts/create-pyz dist/binary 3.9.2
	dev/scripts/create-pyz dist/binary 3.10.0


# Cleanup and miscellaneous directives ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

clean: clean-dist clean-build clean-release clean-other

clean-dist:;
	-rm -fr dist/$(name) dist/$(name)-$(version).tar.gz \
	    dist/$(name)-$(version)-py3-none-any.whl dist/binary \
            __pycache__ .eggs

clean-build:;
	-rm -rf build

clean-release:;
	-rm -rf $(name).egg-info codemeta.json.bak $(init_file).bak README.md.bak

clean-other:;
	-rm -fr $(name)/__pycache__

.PHONY: release release-on-github update-init update-codemeta \
	print-instructions packages clean test-pypi pypi
