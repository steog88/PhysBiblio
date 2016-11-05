import sys, traceback

try:
	import pybiblio.export as bibexport
	import pybiblio.webimport.webInterf as webInt
	from pybiblio.config import pbConfig
	from pybiblio.database import pyBiblioDB
except ImportError:
	print("[CLI] Could not find pybiblio and its contents: configure your PYTHONPATH!")
	print traceback.format_exc()

def cli():
	print("[CLI] Activating CommandLineInterface")
	print("Write a command and press Enter (leave empty and press Enter to exit):")
	line=raw_input()
	while line:
		try:
			exec(line)
		except:
			print traceback.format_exc()
		print("Write a command and press Enter (leave empty and press Enter to exit):")
		line=raw_input()
	print("[CLI] CommandLineInterface closed.")
