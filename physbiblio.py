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

# GUI application
if __name__=='__main__':
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
