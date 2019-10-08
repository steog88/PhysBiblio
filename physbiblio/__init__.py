"""The package that contains all the modules used by the PhysBiblio,
including the `gui` subpackage.

This file is part of the physbiblio package.
"""
__author__ = "Stefano Gariazzo"
__email__ = "stefano.gariazzo@gmail.com"

__version__ = "1.4.0"
__version_date__ = "08/10/2019"

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
* function to show recent version changes from the GUI (shown when opening the program for the first time with a new version);<br>
* option to make the update notification less invasive (it will be shown in the status bar instead of as a message at startup);<br>
* solved bug affecting database.Entries.getByKey when simple keys are used;<br>
* some new tests for package properties and fixes to adsnasa offline tests;<br>
* several internal changes and test improvements.<br>
"""
