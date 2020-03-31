"""The package that contains all the modules used by the PhysBiblio,
including the `gui` subpackage.

This file is part of the physbiblio package.
"""
__author__ = "Stefano Gariazzo"
__email__ = "stefano.gariazzo@gmail.com"

__version__ = "1.5.2"
__version_date__ = "31/03/2020"

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
<b>1.5.1</b>:<br>
* updates for working with INSPIRE after the old API has been temporarily moved to old.inspirehep.net;<br>
* buttons to delete lines in search form (when more than one line exists);<br>
* improved INSPIRE ID retrieve function;<br>
* all open tabs and category/experiment windows are closed when changing profile;<br>
* now requiring PySide2>=5.14 for python3.8 compatibility;<br>
* fixing problem with log file (the custom file name was not used);<br>
* fixing problem when saving invalid replaceFields in a non-replace record;<br>
* language fixes to address few SyntaxWarnings;<br>
* fixes to tests.<br>
<br>
<b>1.5.2</b>: fixing a new change from INSPIRE (OAI url - yesterday it was working!)<br>
"""
