#!/usr/bin/env python
"""
Test file for the physbiblio.gui.dialogWindows module.

This file is part of the physbiblio package.
"""
import sys, traceback
import os
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch, call
else:
	import unittest
	from unittest.mock import patch, call

try:
	from physbiblio.setuptests import *
	from physbiblio.gui.setuptests import *
	from physbiblio.gui.dialogWindows import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestConfigEditColumns(GUITestCase):
	"""
	Test configEditColumns
	"""
	@classmethod
	def setUpClass(self):
		"""set temporary settings"""
		pass

	@classmethod
	def tearDownClass(self):
		"""restore previous settings"""
		pass

	def test_init(self):
		"""Test __init__"""
		pass

	def test_onCancel(self):
		"""test"""
		pass

	def test_onOk(self):
		"""test"""
		pass

	def test_initUI(self):
		"""test"""
		pass

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestConfigWindow(GUITestCase):
	"""
	Test configWindow
	"""
	@classmethod
	def setUpClass(self):
		"""set temporary settings"""
		pass

	@classmethod
	def tearDownClass(self):
		"""restore previous settings"""
		pass

	def test_init(self):
		"""Test __init__"""
		pass

	def test_onCancel(self):
		"""test"""
		pass

	def test_onOk(self):
		"""test"""
		pass

	def test_editFolder(self):
		"""test"""
		pass

	def test_editFile(self):
		"""test"""
		pass

	def test_editColumns(self):
		"""test"""
		pass

	def test_editDefCats(self):
		"""test"""
		pass

	def test_initUI(self):
		"""test"""
		pass

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestLogFileContentDialog(GUITestCase):
	"""
	Test LogFileContentDialog
	"""
	def test_init(self):
		"""test"""
		pass

	def test_clearLog(self):
		"""test"""
		pass

	def test_initUI(self):
		"""test"""
		pass

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestPrintText(GUITestCase):
	"""
	Test printText
	"""
	def test_init(self):
		"""test"""
		pass

	def test_closeEvent(self):
		"""test"""
		pass

	def test_initUI(self):
		"""test"""
		pass

	def test_append_text(self):
		"""test"""
		pass

	def test_progressBarMin(self):
		"""test"""
		pass

	def test_progressBarMax(self):
		"""test"""
		pass

	def test_stopExec(self):
		"""test"""
		pass

	def test_enableClose(self):
		"""test"""
		pass

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestSearchReplaceDialog(GUITestCase):
	"""
	Test searchReplaceDialog
	"""
	def test_init(self):
		"""test"""
		pass

	def test_onCancel(self):
		"""test"""
		pass

	def test_onOk(self):
		"""test"""
		pass

	def test_initUI(self):
		"""test"""
		pass

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestAdvImportDialog(GUITestCase):
	"""
	Test advImportDialog
	"""
	def test_init(self):
		"""test"""
		pass

	def test_onCancel(self):
		"""test"""
		pass

	def test_onOK(self):
		"""test"""
		pass

	def test_initUI(self):
		"""test"""
		pass

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestAdvImportSelect(GUITestCase):
	"""
	Test advImportSelect
	"""
	def test_init(self):
		"""test"""
		pass

	def test_onCancel(self):
		"""test"""
		pass

	def test_onOk(self):
		"""test"""
		pass

	def test_keyPressEvent(self):
		"""test"""
		pass

	def test_changeFilter(self):
		"""test"""
		pass

	def test_initUI(self):
		"""test"""
		pass

	def test_triggeredContextMenuEvent(self):
		"""test"""
		pass

	def test_handleItemEntered(self):
		"""test"""
		pass

	def test_cellClick(self):
		"""test"""
		pass

	def test_cellDoubleClick(self):
		"""test"""
		pass

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestDailyArxivDialog(GUITestCase):
	"""
	Test dailyArxivDialog
	"""
	def test_init(self):
		"""test"""
		pass

	def test_onCancel(self):
		"""test"""
		pass

	def test_onOk(self):
		"""test"""
		pass

	def test_updateCat(self):
		"""test"""
		pass

	def test_initUI(self):
		"""test"""
		pass

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestDailyArxivSelect(GUITestCase):
	"""
	Test dailyArxivSelect
	"""
	def test_initUI(self):
		"""test"""
		pass

	def test_cellClick(self):
		"""test"""
		pass

if __name__=='__main__':
	unittest.main()
