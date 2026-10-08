"""The package that contains all the modules used by the PhysBiblio,
including the `gui` subpackage.

This file is part of the physbiblio package.
"""

from .version import __recent_changes__, __version__, __version_date__

__author__ = "Stefano Gariazzo"
__email__ = "stefano.gariazzo@gmail.com"

__all__ = [
    "__recent_changes__",
    "__version__",
    "__version_date__",
    "bibtexWriter",
    "cli",
    "config",
    "database",
    "databaseCore",
    "errors",
    "export",
    "gui",
    "inspireStats",
    "parseAccents",
    "pdf",
    "strings",
    "tablesDef",
    "tests",
    "view",
    "webimport",
]
