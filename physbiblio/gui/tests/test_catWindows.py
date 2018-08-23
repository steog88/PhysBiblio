#!/usr/bin/env python
"""
Test file for the physbiblio.gui.catWindows module.

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
	from physbiblio.gui.catWindows import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestFunctions(GUITestCase):
	"""test editCategory and deleteCategory"""
	def test_editCategory(self):
		"""test"""
		pass

	def test_deleteCategory(self):
		"""test"""
		pass

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestCatsModel(GUITestCase):
	"""test the catsModel class"""
	def test_init(self):
		"""test init"""
		pass

	def test_getRootNodes(self):
		"""test"""
		pass

	def test_columnCount(self):
		"""test"""
		pass

	def test_data(self):
		"""test"""
		pass

	def test_flags(self):
		"""test"""
		pass

	def test_headerData(self):
		"""test"""
		pass

	def test_setData(self):
		"""test"""
		pass

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestCatsWindowList(GUITestCase):
	"""test the catsWindowList class"""
	def test_init(self):
		"""test init"""
		pass

	def test_populateAskCats(self):
		"""test"""
		pass

	def test_onCancel(self):
		"""test"""
		pass

	def test_onOk(self):
		"""test"""
		pass

	def test_change_filter(self):
		"""test"""
		pass

	def test_onAskExps(self):
		"""test"""
		pass

	def test_onNewCat(self):
		"""test"""
		pass

	def test_keyPressEvent(self):
		"""test"""
		pass

	def test_fillTree(self):
		"""test"""
		pass

	def test_populateTree(self):
		"""test"""
		pass

	def test_handleItemEntered(self):
		"""test"""
		pass

	def test_contextMenuEvent(self):
		"""test"""
		pass

	def test_cleanLayout(self):
		"""test"""
		pass

	def test_recreateTable(self):
		"""test"""
		pass

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestEditCategoryDialog(GUITestCase):
	"""test the editCategoryDialog class"""
	def test_init(self):
		"""test init"""
		pass

	def test_onAskParent(self):
		"""test"""
		pass

	def test_createForm(self):
		"""test"""
		pass

if __name__=='__main__':
	unittest.main()
