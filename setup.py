#!/usr/bin/env python
"""
Script for installing, uploading, doing tests and so on.

This file is part of the PhysBiblio package.
"""

from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='PhysBiblio',
		version='0.1.0',
		description='A bibliography manager in Python (using Sqlite and PySide)',
		long_description=readme(),
		author='Stefano Gariazzo',
		author_email='stefano.gariazzo@gmail.com',
		url='https://github.com/steog88/physBiblio',
		license="GPL-3.0",
		keywords="bibliography hep-ph high-energy-physics bibtex",

		packages=['physbiblio', 'physbiblio.gui', 'physbiblio.webimport',
			'physbiblio.tests', 'physbiblio.webimport.tests'],
		scripts=['physbiblio.py'],
		package_data={
			'': ['*.sh', '*.md', '*.png'],
			'physbiblio.gui': ['images/*.png'],
		},
		install_requires=[
			'six',
			'bibtexparser(>=1.0.1)',
			'pyoai',
			'feedparser',
			'pymarc',
			'matplotlib',
			'unittest2;python_version<"3"',
			'mock;python_version<"3"',
			],
		provides=['physbiblio'],
		data_files = [("", ["LICENSE"])],
		test_loader = "physbiblio.testLoader:MyScanningLoader",
	)
