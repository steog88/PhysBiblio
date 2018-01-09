import sys, traceback
import readline # optional, will allow Up/Down/History in the console
import code

try:
	from physbiblio.export import pBExport
	import physbiblio.webimport.webInterf as webInt
	from physbiblio.config import pbConfig
	from physbiblio.database import pBDB
	from physbiblio.pdf import pBPDF
	from physbiblio.view import pBView
	from physbiblio.inspireStats import pBStats
	from physbiblio.webimport.webInterf import physBiblioWeb
except ImportError:
	print("[CLI] Could not find physbiblio and its contents: configure your PYTHONPATH!")
	print(traceback.format_exc())

def cli():
	"""open a command line interface"""
	vars = globals().copy()
	vars.update(locals())
	shell = code.InteractiveConsole(vars)
	shell.interact("""[CLI] Activating CommandLineInterface
Write a command and press Enter ('Ctrl+D' or 'exit()' to exit).""")
	print("[CLI] CommandLineInterface closed.")
