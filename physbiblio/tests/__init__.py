"""The package that contains the tests for the physbiblio package.

This file is part of the physbiblio package.
"""
__author__ = 'Stefano Gariazzo'
__email__ = "stefano.gariazzo@gmail.com"

import physbiblio
__version__ = physbiblio.__version__
__version_date__ = physbiblio.__version_date__

__all__ = [
	"test_argParser",
	"test_bibtexWriter",
	"test_config",
	"test_database",
	"test_errors",
	"test_export",
	"test_inspireStats",
	"test_pdf",
	"test_view",
	]

