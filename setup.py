#!/usr/bin/env python
"""
Script for installing, uploading, doing tests and so on.

This file is part of the physbiblio package.
"""

from setuptools import setup

import physbiblio

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='physbiblio',
		version=physbiblio.__version__,
		description='A bibliography manager in Python (using Sqlite and PySide)',
		long_description=readme(),
		author='Stefano Gariazzo',
		author_email='stefano.gariazzo@gmail.com',
		url='https://github.com/steog88/physBiblio',
		license="GPL-3.0",
		keywords="bibliography hep-ph high-energy-physics bibtex",

		packages=['physbiblio', 'physbiblio.gui', 'physbiblio.webimport',
			'physbiblio.tests', 'physbiblio.webimport.tests'],
		scripts=['PhysBiblio'],
		package_data={
			'': ['*.sh', '*.md', '*.png'],
			'physbiblio.gui': ['images/*.png'],
		},
		install_requires=[
			'appdirs',
			'argparse',
			'bibtexparser(>=1.0.1)',
			'dictdiffer',
			'feedparser',
			'matplotlib',
			'pymarc',
			'pyoai',
			'requests',
			'six',
			'mock;python_version<"3"',
			'unittest2;python_version<"3"',
			],
		provides=['physbiblio'],
		data_files = [("physbiblio", ["LICENSE", "CHANGELOG", 'physbiblio/gui/images/icon.png'])],
		test_loader = "physbiblio.testLoader:MyScanningLoader",
	)
