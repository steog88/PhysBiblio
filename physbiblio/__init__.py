"""The package that contains all the modules used by the PhysBiblio,
including the `gui` subpackage.

This file is part of the physbiblio package.
"""
__author__ = "Stefano Gariazzo"
__email__ = "stefano.gariazzo@gmail.com"

__version__ = "1.5.0"
__version_date__ = "01/02/2020"

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
* tabs in the main window, in order to keep multiple searches available at each time<br>
* search in a category or its subcategories<br>
* option to reorder bibtexs without updating, in "tex" shell command and in GUI<br>
* fix progressBar in authorStats when a single name is requested<br>
* internal improvements<br>
"""
