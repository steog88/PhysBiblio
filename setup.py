#!/usr/bin/env python
"""Script for installing, uploading, doing tests and so on.

This file is part of the physbiblio package.
"""

from setuptools import setup

import physbiblio


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="physbiblio",
    version=physbiblio.__version__,
    description="A bibliography manager in Python (using Sqlite and PySide6)",
    long_description_content_type="text/markdown",
    long_description=readme(),
    author=physbiblio.__author__,
    author_email=physbiblio.__email__,
    url="https://github.com/steog88/PhysBiblio",
    license="GPL-3.0",
    keywords=["bibliography", "hep-ph", "high-energy-physics", "bibtex"],
    packages=[
        "physbiblio",
        "physbiblio.gui",
        "physbiblio.strings",
        "physbiblio.webimport",
        "physbiblio.tests",
        "physbiblio.gui.tests",
        "physbiblio.webimport.tests",
    ],
    scripts=["PhysBiblio.exe"],
    package_data={"": ["*.sh", "*.md", "*.png"], "physbiblio.gui": ["images/*.png"]},
    install_requires=[
        "ads",
        "appdirs",
        "argparse",
        "bibtexparser(>=1.1.0)",
        "dictdiffer",
        "feedparser",
        "matplotlib(>=3.6.2)",
        "outdated",
        "pylatexenc(>=2.0)",
        "pyparsing(>=2.4.0)",
        "pyside6(>=6.4.0)",
        "pytz",
        "requests(>=2.25)",
        "urllib3(>=1.26)",
    ],
    extras_require={"dev": ["black", "isort", "pre-commit", "pyyaml", "twine"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    provides=["physbiblio"],
    data_files=[
        ("physbiblio", ["LICENSE", "CHANGELOG", "physbiblio/gui/images/icon.png"])
    ],
    test_loader="physbiblio.testLoader:PBScanningLoader",
)
