#!/usr/bin/env python
"""
Main file for the PhysBiblio application, a bibliography manager written in Python.

This file is part of the PhysBiblio package.
"""

import sys, traceback

from PySide.QtGui import QApplication

try:
	from physbiblio.database import pBDB
	from physbiblio.gui.MainWindow import MainWindow
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

def TorF(s):
	"""Get a True or False value from a command line option"""
	if s.lower() == "t" or s == 1 or s.lower() == "true":
		return True
	elif s.lower() == "f" or s == 0 or s.lower() == "false":
		return True
	else:
		return None

# GUI application
if __name__=='__main__':
	command = None
	if len(sys.argv) > 1:
		command = sys.argv[1].lower()
	if command == "help":
		print("\nAvailable command line options:")
		print("* help: print this text;")
		print("* cli: open a command line where to directly run PhysBiblio functions;")
		print("* tex: read .tex file(s) and create a *.bib file with the cited bibtexs.")
		print("")
		exit()
	elif command == "cli":
		from physbiblio.cli import cli as physBiblioCLI
		physBiblioCLI()
		exit()
	elif command == "tex":
		from physbiblio.export import pBExport
		if len(sys.argv) < 4:
			print("\nWrong usage of command line command 'tex': mandatory arguments are missing. Please use:")
			print("`physbiblio.py tex '/folder/where/tex/files/are/' 'name_of_output.bib' [overwrite [autosave]]`")
			print("(the optional arguments overwrite and autosave may be 1,T,t,True,true for True or 0,F,f,False,false for False. Default: overwrite = False, autosave = True)\n")
		texFiles = sys.argv[2]
		bibFile = sys.argv[3]
		overwrite = TorF(sys.argv[4]) if len(sys.argv) > 4 else False
		autosave = TorF(sys.argv[5]) if len(sys.argv) > 5 else True
		if overwrite is None or autosave is None:
			print("\nInvalid value for overwrite or autosave. You may use 1,T,t,True,true for True or 0,F,f,False,false for False.\n")
		pBExport.exportForTexFile(texFiles, bibFile, overwrite = overwrite, autosave = autosave)
		exit()

	try:
		app = QApplication(sys.argv)
		mainWin = MainWindow()
		mainWin.show()
		mainWin.raise_()
		sys.exit(app.exec_())
	except NameError:
		print("NameError:",sys.exc_info()[1])
	except SystemExit:
		pBDB.closeDB()
		print("Closing main window...")
	except Exception:
		print(traceback.format_exc())
