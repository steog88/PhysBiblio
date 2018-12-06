"""Utilities for in the tests of the physbiblio modules.

This file is part of the physbiblio package.
"""
import sys
import traceback
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
	from physbiblio.gui.mainWindow import MainWindow
except ImportError:
	print("Could not find physbiblio and its modules!")
	raise
except Exception:
	print(traceback.format_exc())

globalQApp = QApplication()


def fakeExec(x, string, out):
	"""Simulate the selection of some files and
	return True/False as if confirmed/canceled
	"""
	QFileDialog.selectFile(x, string)
	return out


class GUITestCase(unittest.TestCase):
	"""Class that manages GUI tests"""

	@classmethod
	def setUpClass(self):
		"""Assign a temporary QApplication to the class instance"""
		self.maxDiff = None
		self.qapp = globalQApp

	@classmethod
	def tearDownClass(self):
		"""Remove a temporary QApplication from the class instance"""
		del self.qapp

	def assertGeometry(self, obj, x, y, w, h):
		"""Test the geometry of an object

		Parameters:
			obj: the object to be tested
			x: the expected x position
			y: the expected y position
			w: the expected width
			h: the expected height
		"""
		geom = obj.geometry()
		self.assertEqual(geom.x(), x)
		self.assertEqual(geom.y(), y)
		self.assertEqual(geom.width(), w)
		self.assertEqual(geom.height(), h)


class GUIwMainWTestCase(unittest.TestCase):
	"""Class that manages GUI tests which need a testing instance
	of the MainWindow class
	"""

	@classmethod
	def setUpClass(self):
		"""Call the parent method and instantiate a testing MainWindow"""
		super(GUIwMainWTestCase, self).setUpClass()
		self.mainW = MainWindow(testing=True)
