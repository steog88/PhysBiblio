import sys, traceback
import readline # optional, will allow Up/Down/History in the console
import code

try:
	import pybiblio.export as bibexport
	import pybiblio.webimport.webInterf as webInt
	from pybiblio.config import pbConfig
	from pybiblio.database import pBDB
except ImportError:
	print("[CLI] Could not find pybiblio and its contents: configure your PYTHONPATH!")
	print traceback.format_exc()

def cli():
	print("[CLI] Activating CommandLineInterface")
	print("Write a command and press Enter (leave empty and press Enter to exit):")	
	vars = globals().copy()
	vars.update(locals())
	shell = code.InteractiveConsole(vars)
	shell.interact()
	print("[CLI] CommandLineInterface closed.")
