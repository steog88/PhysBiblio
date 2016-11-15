import sys, traceback
import readline # optional, will allow Up/Down/History in the console
import code

try:
	import pybiblio.export as bibexport
	import pybiblio.webimport.webInterf as webInt
	from pybiblio.config import pbConfig
	from pybiblio.database import pBDB
	from pybiblio.pdf import pBPDF
	from pybiblio.view import pBView
	from pybiblio.webimport.webInterf import pyBiblioWeb
except ImportError:
	print("[CLI] Could not find pybiblio and its contents: configure your PYTHONPATH!")
	print traceback.format_exc()

def cli():
	"""open a command line interface"""
	vars = globals().copy()
	vars.update(locals())
	shell = code.InteractiveConsole(vars)
	shell.interact("""[CLI] Activating CommandLineInterface
Write a command and press Enter ('Ctrl+D' or 'exit()' to exit).""")
	print("[CLI] CommandLineInterface closed.")
