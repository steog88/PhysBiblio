"""
Utilities for in the tests of the physbiblio modules.

This file is part of the physbiblio package.
"""
import sys, traceback, datetime, os
from PySide2.QtWidgets import QApplication, QFileDialog

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch
	from StringIO import StringIO
else:
	import unittest
	from unittest.mock import patch
	from io import StringIO

try:
	from physbiblio.setuptests import *
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
	print(traceback.format_exc())
	raise

skipGuiTests = False

globalQApp = QApplication()

def fakeExec(x, string, out):
	"""simulate the selection of some files and return True/False as if confirmed/canceled"""
	QFileDialog.selectFile(x, string)
	return out

class GUITestCase(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		self.maxDiff = None
		self.qapp = globalQApp

	@classmethod
	def tearDownClass(self):
		del self.qapp
