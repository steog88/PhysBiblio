#!/usr/bin/env python
"""
Test file for the physbiblio.gui.DialogWindows module.

This file is part of the physbiblio package.
"""
import sys, traceback
import os
import logging
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QLabel, QLineEdit, QMessageBox, QWidget

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch
else:
	import unittest
	from unittest.mock import patch

try:
	from physbiblio.setuptests import *
	from physbiblio.gui.setuptests import *
	from physbiblio.gui.inspireStatsGUI import *
	from physbiblio.gui.DialogWindows import askDirName
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

class fakeParent(QWidget):
	"""used to substitute the parent in the inspireStatsGUI classes"""
	def __init__(self):
		QWidget.__init__(self)
		self.lastAuthorStats = {"h": 999}
		self.lastPaperStats = {}

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestAuthorStatsPlots(GUITestCase):
	"""
	Test the functions in authorStatsPlots
	"""
	def test_figTitles(self):
		"""test figTitles"""
		self.assertEqual(figTitles, [
		"Paper number",
		"Papers per year",
		"Total citations",
		"Citations per year",
		"Mean citations",
		"Citations for each paper"
		])

	def test_init(self):
		"""Test __init__"""
		parent = fakeParent()
		with patch("physbiblio.gui.inspireStatsGUI.authorStatsPlots.updatePlots") as _up:
			asp = authorStatsPlots(["a", "b", "c", "d", "e", "f"])
			_up.assert_called_once_with(["a", "b", "c", "d", "e", "f"])
			self.assertIsInstance(asp.layout(), QGridLayout)
			self.assertEqual(asp.layout().columnCount(), 2)
			self.assertEqual(asp.layout().rowCount(), 7)
			w40 = asp.layout().itemAtPosition(4, 0).widget()
			self.assertIsInstance(w40, QLabel)
			self.assertEqual(w40.text(), "Click on the lines to have more information:")
			self.assertIsInstance(asp.hIndex, QLabel)
			self.assertEqual(asp.hIndex.font(), QFont("Times", 15, QFont.Bold))
			self.assertEqual(asp.hIndex.text(), "Author h index: ND")
			self.assertEqual(asp.layout().itemAtPosition(4, 1).widget(), asp.hIndex)
			self.assertIsInstance(asp.textBox, QLineEdit)
			self.assertTrue(asp.textBox.isReadOnly())
			self.assertEqual(asp.layout().itemAtPosition(5, 0).widget(), asp.textBox)
			self.assertIsInstance(asp.saveButton, QPushButton)
			self.assertEqual(asp.saveButton.text(), "Save")
			self.assertEqual(asp.layout().itemAtPosition(6, 0).widget(), asp.saveButton)
			with patch("physbiblio.gui.inspireStatsGUI.authorStatsPlots.saveAction") as _sa:
				QTest.mouseClick(asp.saveButton, Qt.LeftButton)
				_sa.assert_called_once()
			self.assertIsInstance(asp.clButton, QPushButton)
			self.assertEqual(asp.clButton.text(), "Close")
			self.assertTrue(asp.clButton.autoDefault())
			self.assertEqual(asp.layout().itemAtPosition(6, 1).widget(), asp.clButton)
			with patch("physbiblio.gui.inspireStatsGUI.authorStatsPlots.onClose") as _cl:
				QTest.mouseClick(asp.clButton, Qt.LeftButton)
				_cl.assert_called_once()

			asp = authorStatsPlots(["a", "b", "c", "d", "e", "f"], parent = parent)
			self.assertEqual(asp.parent, parent)
			self.assertIsInstance(asp.hIndex, QLabel)
			self.assertEqual(asp.hIndex.text(), "Author h index: 999")
			self.assertEqual(asp.windowTitle(), "")

			asp = authorStatsPlots(["a", "b", "c", "d", "e", "f"], title = "abcdef", parent = parent)
			self.assertEqual(asp.windowTitle(), "abcdef")

	def test_saveAction(self):
		"""Test """
		fakepar = fakeParent()
		with patch("physbiblio.gui.inspireStatsGUI.authorStatsPlots.updatePlots") as _up:
			asp = authorStatsPlots(["a", "b", "c", "d", "e", "f"], parent = fakepar)
			self.assertTrue(asp.saveButton.isEnabled())
			with patch("physbiblio.inspireStats.inspireStatsLoader.plotStats", return_value = "fakeval") as _ps:
				with patch('PySide2.QtWidgets.QFileDialog.exec_', new=lambda x: fakeExec(x, "/tmp", False)):
					asp.saveAction()
					self.assertTrue(asp.saveButton.isEnabled())
					self.assertNotIn("figs", fakepar.lastAuthorStats.keys())
					_ps.assert_not_called()
				with patch('PySide2.QtWidgets.QFileDialog.exec_', new=lambda x: fakeExec(x, "/tmp", True)):
					with patch('PySide2.QtWidgets.QMessageBox.exec_'):
						asp.saveAction()
						self.assertFalse(asp.saveButton.isEnabled())
						_ps.assert_called_once_with(author = True, path = '/tmp', save = True)
						self.assertEqual(fakepar.lastAuthorStats["figs"], "fakeval")


	def test_pickEvent(self):
		"""Test """
		pass

	def test_updatePlots(self):
		"""Test """
		pass

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestPaperStatsPlots(GUITestCase):
	"""
	Test the functions in paperStatsPlots
	"""
	def test_init(self):
		"""Test """
		pass

	def test_saveAction(self):
		"""Test """
		pass

	def test_pickEvent(self):
		"""Test """
		pass

	def test_updatePlots(self):
		"""Test """
		pass

if __name__=='__main__':
	unittest.main()
