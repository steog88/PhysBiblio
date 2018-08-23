#!/usr/bin/env python
"""
Test file for the physbiblio.gui.expWindows module.

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
	from physbiblio.gui.expWindows import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestFunctions(GUITestCase):
	"""Test the editExperiment and deleteExperiment functions"""
	def test_editExperiment(self):
		"""test"""
		pass

	def test_deleteExperiment(self):
		"""test"""
		pass

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestMyExpTableModel(GUITestCase):
	"""Test MyExpTableModel"""
	def test_init(self):
		"""test"""
		pass

	def test_getIdentifier(self):
		"""test"""
		pass

	def test_data(self):
		"""test"""
		pass

	def test_setData(self):
		"""test"""
		pass

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestExpWindowList(GUITestCase):
	"""Test ExpWindowList"""
	def test_init(self):
		"""test"""
		pass

	def test_populateAskExp(self):
		"""test"""
		pass

	def test_onCancel(self):
		"""test"""
		pass

	def test_onOk(self):
		"""test"""
		pass

	def test_onNewExp(self):
		"""test"""
		pass

	def test_keyPressEvent(self):
		"""test"""
		pass

	def test_changeFilter(self):
		"""test"""
		pass

	def test_createTable(self):
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
class TestEditExp(GUITestCase):
	"""Test editExp"""
	def test_init(self):
		"""test"""
		pass

	def test_createForm(self):
		"""test"""
		pass

if __name__=='__main__':
	unittest.main()
