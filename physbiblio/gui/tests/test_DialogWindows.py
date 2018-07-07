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
		"""Test _entry_to_bibtex"""
		win = QMessageBox(QMessageBox.Question, "title", "message")
		yesButton = win.addButton(QMessageBox.Yes)
		noButton = win.addButton(QMessageBox.No)
		win.setDefaultButton(noButton)
		QTest.mouseClick(win.defaultButton(), Qt.LeftButton)
		self.assertEqual(win.clickedButton(), noButton)
		QTest.mouseClick(yesButton, Qt.LeftButton)
		self.assertEqual(win.clickedButton(), yesButton)

if __name__=='__main__':
	unittest.main()
