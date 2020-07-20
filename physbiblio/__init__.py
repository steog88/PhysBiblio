"""The package that contains all the modules used by the PhysBiblio,
including the `gui` subpackage.

This file is part of the physbiblio package.
"""
__author__ = "Stefano Gariazzo"
__email__ = "stefano.gariazzo@gmail.com"

__version__ = "1.6.1"
__version_date__ = "20/07/2020"

__all__ = [
    "bibtexWriter",
    "cli",
    "config",
    "databaseCore",
    "database",
    "errors",
    "export",
    "inspireStats",
    "parseAccents",
    "pdf",
    "strings",
    "tablesDef",
    "view",
    "tests",
    "gui",
    "webimport",
]

__recent_changes__ = """<br>
<b>1.6.0</b>:<br>
* changed most of the code to use the new INSPIRE API<br>
* double click links point to new INSPIRE<br>
* bug when importing from arxiv daily listing<br>
* python2 support dropped! The code may still work, but it is not tested.<br>
* isort for ordering imports<br>
* pre-commit hooks to check code formatting and stuff<br>
<br>
<b>1.6.1</b>: I forgot to update the CHANGELOG!<br>
"""
