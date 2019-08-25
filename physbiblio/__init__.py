"""The package that contains all the modules used by the PhysBiblio,
including the `gui` subpackage.

This file is part of the physbiblio package.
"""
__author__ = "Stefano Gariazzo"
__email__ = "stefano.gariazzo@gmail.com"

__version__ = "1.3.0"
__version_date__ = "23/07/2019"

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
    "tablesDef",
    "view",
    "tests",
    "gui",
    "webimport",
]

__recent_changes__ = """<br>
* advance import connected with ADS by NASA;<br>
* can now copy full bibitem from the table;<br>
* exportForTexFile now recognizes also bibkeys with "&", "." and "+";<br>
* double click on corresponding column opens ADS page for the selected entry;<br>
* renamed configuration parameter 'maxArxivResults' to 'maxExternalAPIResults';<br>
* tests won't work in PySide2 5.12.4 and 5.13.0.<br>
"""
