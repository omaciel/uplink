TEST_OPTIONS=-m unittest discover --start-directory tests --top-level-directory .
CPU_COUNT=$(shell python3 -c "from multiprocessing import cpu_count; print(cpu_count())")

help:
	@echo "Please use \`make <target>' where <target> is one of:"
	@echo "  help           to show this message"
	@echo "  all            to to execute all following targets (except \`test')"
	@echo "  docs-html      to generate HTML documentation"
	@echo "  docs-clean     to remove documentation"
	@echo "  lint           to run all linters"
	@echo "  lint-flake8    to run the flake8 linter"
	@echo "  lint-pylint    to run the pylint linter"
	@echo "  test           to run unit tests"
	@echo "  test-coverage  to run unit tests and measure test coverage"
	@echo "  package        to generate installable Python packages"
	@echo "  package-clean  to remove generated Python packages"
	@echo "  publish        to upload dist/* to PyPi"

# Edit with caution! Travis CI uses this target. ¶ We run docs-clean before
# docs-html to ensure a complete build. (Warnings are emitted only when a file
# is compiled, and Sphinx does not needlessly recompile.) More broadly, we
# order dependencies by execution time and (anecdotal) likelihood of finding
# issues. ¶ `test-coverage` is a functional superset of `test`. Why keep both?
all: test-coverage lint docs-clean docs-html package-clean package

docs-html:
	@cd docs; $(MAKE) html

docs-clean:
	@cd docs; $(MAKE) clean

lint-flake8:
	flake8 . --ignore D203

lint-pylint:
	pylint -j $(CPU_COUNT) --reports=n --disable=I \
		docs/conf.py \
		scripts/run_functional_tests.py \
		setup.py \
		tests \
		uplink/__init__.py \
		uplink/config.py \
		uplink/exceptions.py \
		uplink/uplink_cli.py \
	pylint -j $(CPU_COUNT) --reports=n --disable=I,duplicate-code uplink/tests/

lint: lint-flake8 lint-pylint

test:
	python3 $(TEST_OPTIONS)

test-coverage:
	coverage run --source uplink.config,uplink.exceptions,uplink.uplink_cli \
	$(TEST_OPTIONS)

package:
	./setup.py --quiet sdist bdist_wheel --universal

package-clean:
	rm -rf build dist uplink.egg-info

publish: package
	twine upload dist/*

.PHONY: help all docs-html docs-clean lint-flake8 lint-pylint lint test \
    test-coverage package package-clean publish
