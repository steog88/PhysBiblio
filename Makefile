PYTHON ?= python

default: sdist

sdist:
	$(PYTHON) setup.py sdist

test:
	$(PYTHON) setup.py test

uploadtest:
	$(PYTHON) setup.py sdist upload -r pypitest

upload:
	$(PYTHON) setup.py sdist upload

push:
	git push
	git push --tags
