#!/usr/bin/env python

import sys
import logging

from PySide.QtGui import QApplication

try:
    from pybiblio.gui.MainWindow import *
    from pybiblio.database import *
    from pybiblio.webimport.webInterf import *
except ImportError:
    print("Could not find pybiblio and its contents: configure your PYTHONPATH!")
    raise

# GUI application
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
	print("closing window...")
except Exception:
	print(traceback.format_exc())
