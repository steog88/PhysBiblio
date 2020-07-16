"""Module that creates a command line interface to manually run
the PhysBiblio internal commands.

This file is part of the physbiblio package.
"""
import code
import readline  # optional, will allow Up/Down/History in the console
import sys
import traceback

try:
    import physbiblio.webimport.webInterf as webInt
    from physbiblio.config import pbConfig
    from physbiblio.database import pBDB
    from physbiblio.errors import pBLogger
    from physbiblio.export import pBExport
    from physbiblio.inspireStats import pBStats
    from physbiblio.pdf import pBPDF
    from physbiblio.strings.main import CLIStrings as clistr
    from physbiblio.view import pBView
    from physbiblio.webimport.webInterf import physBiblioWeb
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise


def cli():
    """Open a command line interface.

    Many initial imports allow the user
    to automatically access the useful classes.
    """
    vars = globals().copy()
    vars.update(locals())
    shell = code.InteractiveConsole(vars)
    shell.interact(clistr.activate)
    pBDB.closeDB()
    pBLogger.info(clistr.close)
