"""The package that contains all the modules used by the PhysBiblio,
including the `gui` subpackage.

This file is part of the physbiblio package.
"""
__author__ = "Stefano Gariazzo"
__email__ = "stefano.gariazzo@gmail.com"

__version__ = "1.4.1"
__version_date__ = "14/10/2019"

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
* disable already useless stop button when a thread is finished;<br>
* attempt to fix "QThread: Destroyed while thread is still running";<br>
* fixing bugs with progress reporting in GUI for threaded process (and some functions improved meanwhile).<br>
"""
