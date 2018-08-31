#!/usr/bin/env python
"""Test file for the physbiblio.gui.catWindows module.

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
		"""test onAskParents"""
		p = QWidget()
		ecd = editCategoryDialog(p)
		sc = categoriesTreeWindow(parent = ecd,
			askCats = True,
			expButton = False,
			single = True,
			previous = [0])
		sc.onCancel()
		txt = ecd.textValues["parentCat"].text()
		with patch("physbiblio.gui.catWindows.categoriesTreeWindow.__init__",
				return_value = None) as _i:
			ecd.onAskParent(sc)
			_i.assert_called_once_with(parent = ecd,
				askCats = True,
				expButton = False,
				single = True,
				previous = ecd.selectedCats)
		self.assertEqual(ecd.textValues["parentCat"].text(),
			"0 - Main")

		sc = categoriesTreeWindow(parent = ecd,
			askCats = True,
			expButton = False,
			single = True,
			previous = [1])
		sc.onOk()
		with patch("physbiblio.gui.catWindows.categoriesTreeWindow.__init__",
				return_value = None) as _i:
			ecd.onAskParent(sc)
			_i.assert_called_once_with(parent = ecd,
				askCats = True,
				expButton = False,
				single = True,
				previous = ecd.selectedCats)
		self.assertEqual(ecd.textValues["parentCat"].text(),
			"1 - Tags")

		sc = categoriesTreeWindow(parent = ecd,
			askCats = True,
			expButton = False,
			single = True,
			previous = [0, 1])
		sc.onOk()
		with patch("physbiblio.gui.catWindows.categoriesTreeWindow.__init__",
				return_value = None) as _i:
			ecd.onAskParent(sc)
			_i.assert_called_once_with(parent = ecd,
				askCats = True,
				expButton = False,
				single = True,
				previous = ecd.selectedCats)
		self.assertEqual(ecd.textValues["parentCat"].text(),
			"1 - Tags")

		sc = categoriesTreeWindow(parent = ecd,
			askCats = True,
			expButton = False,
			single = True,
			previous = [])
		sc.onOk()
		with patch("physbiblio.gui.catWindows.categoriesTreeWindow.__init__",
				return_value = None) as _i:
			ecd.onAskParent(sc)
			_i.assert_called_once_with(parent = ecd,
				askCats = True,
				expButton = False,
				single = True,
				previous = ecd.selectedCats)
		self.assertEqual(ecd.textValues["parentCat"].text(),
			"Select parent")

		sc = categoriesTreeWindow(parent = ecd,
			askCats = True,
			expButton = False,
			single = True,
			previous = [9999])
		sc.onOk()
		with patch("physbiblio.gui.catWindows.categoriesTreeWindow.__init__",
				return_value = None) as _i:
			ecd.onAskParent(sc)
			_i.assert_called_once_with(parent = ecd,
				askCats = True,
				expButton = False,
				single = True,
				previous = ecd.selectedCats)
		self.assertEqual(ecd.textValues["parentCat"].text(),
			"Select parent")

	def test_createForm(self):
		"""test createForm"""
		p = QWidget()
		ncf = (len(pBDB.tableCols["categories"]) - 1) * 2 + 1
		ecd = editCategoryDialog(p)
		self.assertEqual(ecd.windowTitle(), 'Edit category')
		self.assertEqual(ecd.layout().itemAtPosition(0, 0), None)
		self.assertEqual(ecd.layout().itemAtPosition(0, 1), None)

		self.assertIsInstance(ecd.layout().itemAtPosition(1, 0).widget(),
			MyLabel)
		self.assertEqual(ecd.layout().itemAtPosition(1, 0).widget().text(),
			pBDB.descriptions["categories"]["name"])
		self.assertIsInstance(ecd.layout().itemAtPosition(1, 1).widget(),
			MyLabel)
		self.assertEqual(ecd.layout().itemAtPosition(1, 1).widget().text(),
			"(name)")
		self.assertIsInstance(ecd.textValues["name"], QLineEdit)
		self.assertEqual(ecd.textValues["name"],
			ecd.layout().itemAtPosition(2, 0).widget())
		self.assertEqual(ecd.textValues["name"].text(), "")

		self.assertIsInstance(ecd.layout().itemAtPosition(3, 0).widget(),
			MyLabel)
		self.assertEqual(ecd.layout().itemAtPosition(3, 0).widget().text(),
			pBDB.descriptions["categories"]["description"])
		self.assertIsInstance(ecd.layout().itemAtPosition(3, 1).widget(),
			MyLabel)
		self.assertEqual(ecd.layout().itemAtPosition(3, 1).widget().text(),
			"(description)")
		self.assertIsInstance(ecd.textValues["description"], QLineEdit)
		self.assertEqual(ecd.textValues["description"],
			ecd.layout().itemAtPosition(4, 0).widget())
		self.assertEqual(ecd.textValues["description"].text(), "")

		self.assertIsInstance(ecd.layout().itemAtPosition(5, 0).widget(),
			MyLabel)
		self.assertEqual(ecd.layout().itemAtPosition(5, 0).widget().text(),
			pBDB.descriptions["categories"]["parentCat"])
		self.assertIsInstance(ecd.layout().itemAtPosition(5, 1).widget(),
			MyLabel)
		self.assertEqual(ecd.layout().itemAtPosition(5, 1).widget().text(),
			"(parentCat)")
		self.assertIsInstance(ecd.textValues["parentCat"], QPushButton)
		self.assertEqual(ecd.textValues["parentCat"],
			ecd.layout().itemAtPosition(6, 0).widget())
		self.assertEqual(ecd.textValues["parentCat"].text(), "0 - Main")
		with patch("physbiblio.gui.catWindows.editCategoryDialog.onAskParent"
				) as _f:
			QTest.mouseClick(ecd.textValues["parentCat"], Qt.LeftButton)
			_f.assert_called_once_with(False)

		self.assertIsInstance(ecd.layout().itemAtPosition(7, 0).widget(),
			MyLabel)
		self.assertEqual(ecd.layout().itemAtPosition(7, 0).widget().text(),
			pBDB.descriptions["categories"]["comments"])
		self.assertIsInstance(ecd.layout().itemAtPosition(7, 1).widget(),
			MyLabel)
		self.assertEqual(ecd.layout().itemAtPosition(7, 1).widget().text(),
			"(comments)")
		self.assertIsInstance(ecd.textValues["comments"], QLineEdit)
		self.assertEqual(ecd.textValues["comments"],
			ecd.layout().itemAtPosition(8, 0).widget())
		self.assertEqual(ecd.textValues["comments"].text(), "")

		self.assertIsInstance(ecd.layout().itemAtPosition(9, 0).widget(),
			MyLabel)
		self.assertEqual(ecd.layout().itemAtPosition(9, 0).widget().text(),
			pBDB.descriptions["categories"]["ord"])
		self.assertIsInstance(ecd.layout().itemAtPosition(9, 1).widget(),
			MyLabel)
		self.assertEqual(ecd.layout().itemAtPosition(9, 1).widget().text(),
			"(ord)")
		self.assertIsInstance(ecd.textValues["ord"], QLineEdit)
		self.assertEqual(ecd.textValues["ord"],
			ecd.layout().itemAtPosition(10, 0).widget())
		self.assertEqual(ecd.textValues["ord"].text(), "")

		self.assertIsInstance(ecd.layout().itemAtPosition(ncf, 1).widget(),
			QPushButton)
		self.assertEqual(ecd.acceptButton,
			ecd.layout().itemAtPosition(ncf, 1).widget())
		self.assertEqual(ecd.acceptButton.text(), "OK")
		with patch("physbiblio.gui.commonClasses.editObjectWindow.onOk"
				) as _f:
			QTest.mouseClick(ecd.acceptButton, Qt.LeftButton)
			_f.assert_called_once_with()
		self.assertIsInstance(ecd.layout().itemAtPosition(ncf, 0).widget(),
			QPushButton)
		self.assertEqual(ecd.cancelButton,
			ecd.layout().itemAtPosition(ncf, 0).widget())
		self.assertEqual(ecd.cancelButton.text(), "Cancel")
		self.assertTrue(ecd.cancelButton.autoDefault())
		with patch("physbiblio.gui.commonClasses.editObjectWindow.onCancel"
				) as _f:
			QTest.mouseClick(ecd.cancelButton, Qt.LeftButton)
			_f.assert_called_once_with()

		cat = {
			'idCat': 15,
			'parentCat': 1,
			'description': "desc",
			'comments': "no comment",
			'ord': 0,
			'name': "mycat"
		}
		with patch("physbiblio.database.categories.getParent",
				return_value = [[1]]) as _p, \
				patch("physbiblio.gui.catWindows.editCategoryDialog.createForm"
					) as _c:
			ecd = editCategoryDialog(p, cat)
			_p.assert_called_once_with(15)
		ecd.selectedCats = []
		ecd.createForm()

		self.assertIsInstance(ecd.layout().itemAtPosition(1, 0).widget(),
			MyLabel)
		self.assertEqual(ecd.layout().itemAtPosition(1, 0).widget().text(),
			pBDB.descriptions["categories"]["idCat"])
		self.assertIsInstance(ecd.layout().itemAtPosition(1, 1).widget(),
			MyLabel)
		self.assertEqual(ecd.layout().itemAtPosition(1, 1).widget().text(),
			"(idCat)")
		self.assertIn("idCat", ecd.textValues.keys())
		self.assertIsInstance(ecd.textValues["idCat"], QLineEdit)
		self.assertEqual(ecd.textValues["idCat"],
			ecd.layout().itemAtPosition(2, 0).widget())
		self.assertEqual(ecd.textValues["idCat"].text(), "15")
		self.assertFalse(ecd.textValues["idCat"].isEnabled())

		self.assertIsInstance(ecd.layout().itemAtPosition(3, 0).widget(),
			MyLabel)
		self.assertEqual(ecd.layout().itemAtPosition(3, 0).widget().text(),
			pBDB.descriptions["categories"]["name"])
		self.assertIsInstance(ecd.layout().itemAtPosition(3, 1).widget(),
			MyLabel)
		self.assertEqual(ecd.layout().itemAtPosition(3, 1).widget().text(),
			"(name)")

		self.assertEqual(ecd.textValues["name"].text(), "mycat")
		self.assertEqual(ecd.textValues["description"].text(), "desc")
		self.assertIsInstance(ecd.textValues["parentCat"], QPushButton)
		self.assertEqual(ecd.textValues["parentCat"],
			ecd.layout().itemAtPosition(8, 0).widget())
		self.assertEqual(ecd.textValues["parentCat"].text(), "Select parent")
		self.assertEqual(ecd.textValues["comments"].text(), "no comment")
		self.assertEqual(ecd.textValues["ord"].text(), "0")

if __name__=='__main__':
	unittest.main()
