default: sdist

sdist:
	python setup.py sdist

test:
	python physbiblio_test.py

uploadtest:
	python setup.py sdist upload -r pypitest

upload:
	python setup.py sdist upload

push:
	git push
	git push --tags
