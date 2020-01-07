# =============================================================================
# @file    Makefile
# @brief   Makefile for some steps in creating Handprint releases
# @author  Michael Hucka
# @date    2020-01-07
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/handprint
# =============================================================================

version := $(shell grep 'version\s*=' setup.cfg | cut -f2 -d'=' | tr -d '[:blank:]')
branch  := $(shell git rev-parse --abbrev-ref HEAD)

release: | test-branch release-on-github print-reminder

test-branch:
ifneq ($(branch),master)
	$(error Current git branch != master. Merge changes into master first)
endif

release-on-github:;
	sed -i .bak -e "/version/ s/[0-9].[0-9].[0-9]/$(version)/" codemeta.json
	git add codemeta.json
	git diff-index --quiet HEAD || git commit -m"Update version number" codemeta.json
	git tag -a v$(version) -m "Release $(version)"
	git push -v --all
	git push -v --tags

print-reminder:;
	$(info ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓)
	$(info ┃ Next steps:                                                                                   ┃)
	$(info ┃ 1. Go to GitHub and fill out new release info                                                 ┃)
	$(info ┃ 2. Go to data.caltech.edu and get new Zenodo DOI                                              ┃)
	$(info ┃ 3. Update DOI in README.md file                                                               ┃)
	$(info ┃ 4. Push to GitHub again                                                                       ┃)
	$(info ┃ 5. Push to test.pypi.org as follows:                                                          ┃)
	$(info ┃    a. /bin/rm -rf build dist                                                                  ┃)
	$(info ┃    b. python3 setup.py sdist bdist_wheel                                                      ┃)
	$(info ┃    c. python3 -m twine check dist/*                                                           ┃)
	$(info ┃    d. python3 -m twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/* ┃)
	$(info ┃ 6. Test installing from pypi test location                                                    ┃)
	$(info ┃ 7. Double-check everything                                                                    ┃)
	$(info ┃ 8. Push to pypi for real:                                                                     ┃)
	$(info ┃    a. python3 -m twine upload --verbose dist/*                                                ┃)
	$(info ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛)

.PHONY: release release-on-github print-reminder
