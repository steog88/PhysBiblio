#!/usr/bin/env python
"""
Test file for the physbiblio.gui.catWindows module.

This file is part of the physbiblio package.
"""
import sys, traceback
import os
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QWidget

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch, call
else:
	import unittest
	from unittest.mock import patch, call

try:
	from physbiblio.setuptests import *
	from physbiblio.database import pBDB
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
class TestCategoriesTreeWindow(GUITestCase):
	"""test the categoriesTreeWindow class"""
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
		p = QWidget()
		with patch("physbiblio.gui.catWindows.editObjectWindow.__init__",
				return_value = None) as _i,\
				patch("physbiblio.gui.catWindows.editCategoryDialog.createForm"
					) as _c:
			ecd = editCategoryDialog(p)
			_i.assert_called_once_with(p)
			_c.assert_called_once_with()
		ecd = editCategoryDialog(p)
		self.assertIsInstance(ecd, editObjectWindow)
		self.assertEqual(ecd.parent(), p)
		self.assertIsInstance(ecd.data, dict)
		for k in pBDB.tableCols["categories"]:
			self.assertEqual(ecd.data[k], "")
		self.assertIsInstance(ecd.selectedCats, list)
		self.assertEqual(ecd.selectedCats, [0])

		cat = {
			'idCat': 15,
			'parentCat': 1,
			'description': "desc",
			'comments': "no comment",
			'ord': 0,
			'name': "mycat"
		}
		with patch("physbiblio.database.categories.getParent",
				return_value = [[1]]) as _p:
			ecd = editCategoryDialog(p, cat)
			_p.assert_called_once_with(15)
		for k in pBDB.tableCols["categories"]:
			self.assertEqual(ecd.data[k], cat[k])
		self.assertIsInstance(ecd.selectedCats, list)
		self.assertEqual(ecd.selectedCats, [1])
		with patch("physbiblio.database.categories.getParent",
				return_value = 1) as _p:
			ecd = editCategoryDialog(p, cat, 14)
			_p._assert_not_called()
		for k in pBDB.tableCols["categories"]:
			if k != "parentCat":
				self.assertEqual(ecd.data[k], cat[k])
			else:
				self.assertEqual(ecd.data[k], 14)
		self.assertIsInstance(ecd.selectedCats, list)
		self.assertEqual(ecd.selectedCats, [14])

	def test_onAskParent(self):
		"""test"""
		pass

	def test_createForm(self):
		"""test"""
		pass

if __name__=='__main__':
	unittest.main()
