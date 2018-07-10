#!/usr/bin/env python
"""
Test file for the physbiblio.gui.DialogWindows module.

This file is part of the physbiblio package.
"""
import sys, traceback
import os
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch
else:
	import unittest
	from unittest.mock import patch

try:
	from physbiblio.setuptests import *
	from physbiblio.gui.setuptests import *
	from physbiblio.gui.DialogWindows import *
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestDialogWindows(GUITestCase):
	"""
	Test the functions in DialogWindows
	"""
	def test_askYesNo(self):
		"""Test askYesNo"""
		win, yesButton, noButton = askYesNo("mymessage", "mytitle", True)
		self.assertEqual(win.text(), "mymessage")
		self.assertEqual(win.windowTitle(), "mytitle")
		self.assertEqual(win.defaultButton(), noButton)
		QTest.mouseClick(win.defaultButton(), Qt.LeftButton)
		self.assertEqual(win.clickedButton(), noButton)
		QTest.mouseClick(yesButton, Qt.LeftButton)
		self.assertEqual(win.clickedButton(), yesButton)

	def test_infoMessage(self):
		"""Test infoMessage"""
		win = infoMessage("mymessage", "mytitle", True)
		self.assertEqual(win.text(), "mymessage")
		self.assertEqual(win.windowTitle(), "mytitle")

	def test_askFileName(self):
		"""Test askFileName"""
		win = askFileName(None, title = "mytitle", dir = "/tmp", filter = "test: *.txt", testing = True)
		self.assertEqual(win.fileMode(), QFileDialog.ExistingFile)
		self.assertEqual(win.windowTitle(), "mytitle")
		self.assertEqual(win.nameFilters(), ["test: *.txt"])
		self.assertEqual(win.directory(), "/tmp")
		self.assertEqual(win.selectedFiles(), [])

	def test_askFileNames(self):
		"""Test askFileNames"""
		win = askFileNames(None, title = "mytitle", dir = "/tmp", filter = "test: *.txt", testing = True)
		self.assertEqual(win.fileMode(), QFileDialog.ExistingFiles)
		self.assertEqual(win.windowTitle(), "mytitle")
		self.assertEqual(win.nameFilters(), ["test: *.txt"])
		self.assertEqual(win.directory(), "/tmp")
		self.assertEqual(win.selectedFiles(), [])

	def test_askSaveFileName(self):
		"""Test askSaveFileName"""
		win = askSaveFileName(None, title = "mytitle", dir = "/tmp", filter = "test: *.txt", testing = True)
		self.assertEqual(win.fileMode(), QFileDialog.AnyFile)
		self.assertEqual(win.options(), QFileDialog.DontConfirmOverwrite)
		self.assertEqual(win.windowTitle(), "mytitle")
		self.assertEqual(win.nameFilters(), ["test: *.txt"])
		self.assertEqual(win.directory(), "/tmp")
		self.assertEqual(win.selectedFiles(), ["/tmp"])

	def test_askDirName(self):
		"""Test askDirName"""
		win = askDirName(None, title = "mytitle", dir = "/tmp", testing = True)
		self.assertEqual(win.fileMode(), QFileDialog.Directory)
		self.assertEqual(win.options(), QFileDialog.ShowDirsOnly)
		self.assertEqual(win.windowTitle(), "mytitle")
		self.assertEqual(win.directory(), "/tmp")
		self.assertEqual(win.selectedFiles(), ["/tmp"])

if __name__=='__main__':
	unittest.main()
