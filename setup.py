#!/usr/bin/env python

from setuptools import setup

setup(name='PhysBiblio',
		version='0.1',
		description='A bibliography manager in Python (using Sqlite and PySide)',
		author='Stefano Gariazzo',
		author_email='stefano.gariazzo@gmail.com',
		url='https://github.com/steog88/physBiblio',
		license="GPL-3.0",
		keywords="bibliography hep-ph high-energy-physics bibtex",

		packages=['physbiblio', 'physbiblio.gui', 'physbiblio.webimport'],
		scripts=['physbiblio.py', 'physbiblio_test.py'],
		package_data={
			'': ['*.sh', '*.png'],
			'physbiblio.gui': ['images/*.png'],
		},
		install_requires=[
			'bibtexparser(>=1.0.1)',
			'pyoai',
			'feedparser',
			'pymarc',
			'matplotlib',
			'unittest2;python_version<"3"',
			'mock;python_version<"3"',
			],
		provides=['physbiblio', 'physbiblio.gui', 'physbiblio.webimport'],
	)
