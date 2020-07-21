"""The package that contains all the modules used by the PhysBiblio,
including the `gui` subpackage.

This file is part of the physbiblio package.
"""
__author__ = "Stefano Gariazzo"
__email__ = "stefano.gariazzo@gmail.com"

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

from .version import __recent_changes__, __version__, __version_date__
