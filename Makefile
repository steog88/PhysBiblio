PYTHON ?= python

default: sdist

sdist:
	$(PYTHON) setup.py sdist

test:
	$(PYTHON) setup.py test

changelog:
	$(PYTHON) dochangelog.py

uploadtest: changelog
	$(PYTHON) setup.py sdist
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload: changelog
	$(PYTHON) setup.py sdist
	twine upload dist/*

push:
	git push
	git push --tags
