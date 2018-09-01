#!/usr/bin/env python
"""Test file for the physbiblio.gui.catWindows module.

This file is part of the physbiblio package.
"""
import sys, traceback
import os
from PySide2.QtCore import Qt, QModelIndex
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
	from physbiblio.gui.mainWindow import MainWindow
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestFunctions(GUITestCase):
	"""test editCategory and deleteCategory"""
	def test_editCategory(self):
		"""test editCategory"""
		raise NotImplementedError()

	def test_deleteCategory(self):
		"""test deleteCategory"""
		p = QWidget()
		m = MainWindow(testing = True)
		with patch("physbiblio.gui.catWindows.askYesNo",
				return_value = False) as _a, \
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _s:
			deleteCategory(p, m, 15, "mycat")
			_a.assert_called_once_with(
				"Do you really want to delete this category "
				+ "(ID = '15', name = 'mycat')?")
			_s.assert_called_once_with("Nothing changed")

		with patch("physbiblio.gui.catWindows.askYesNo",
				return_value = False) as _a, \
				patch("logging.Logger.debug") as _d:
			deleteCategory(p, p, 15, "mycat")
			_a.assert_called_once_with(
				"Do you really want to delete this category "
				+ "(ID = '15', name = 'mycat')?")
			_d.assert_called_once_with(
				"mainWinObject has no attribute 'statusBarMessage'",
				exc_info = True)

		with patch("physbiblio.gui.catWindows.askYesNo",
				return_value = True) as _a, \
				patch("physbiblio.database.categories.delete") as _c, \
				patch("PySide2.QtWidgets.QMainWindow.setWindowTitle") as _t, \
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _s, \
				patch("logging.Logger.debug") as _d:
			deleteCategory(p, m, 15, "mycat")
			_a.assert_called_once_with(
				"Do you really want to delete this category "
				+ "(ID = '15', name = 'mycat')?")
			_c.assert_called_once_with(15)
			_t.assert_called_once_with("PhysBiblio*")
			_s.assert_called_once_with("Category deleted")
			_d.assert_called_once_with(
				"parentObject has no attribute 'recreateTable'",
				exc_info = True)

		ctw = catsTreeWindow(p)
		with patch("physbiblio.gui.catWindows.askYesNo",
				return_value = True) as _a, \
				patch("physbiblio.database.categories.delete") as _c, \
				patch("PySide2.QtWidgets.QMainWindow.setWindowTitle") as _t, \
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _s, \
				patch("physbiblio.gui.catWindows.catsTreeWindow.recreateTable"
					) as _r:
			deleteCategory(ctw, m, 15, "mycat")
			_a.assert_called_once_with(
				"Do you really want to delete this category "
				+ "(ID = '15', name = 'mycat')?")
			_c.assert_called_once_with(15)
			_t.assert_called_once_with("PhysBiblio*")
			_s.assert_called_once_with("Category deleted")
			_r.assert_called_once_with()

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestCatsModel(GUITestCase):
	"""test the catsModel class"""
	def test_init(self):
		"""test init"""
		cm = catsModel([], [])
		# tm.rootElements = [
			# NamedElement(0, "main", [
				# NamedElement(1, "test1", [NamedElement(2, "test2", [])]),
				# NamedElement(3, "test3", []),
				# ])
			# ]
		raise NotImplementedError()

	def test_getRootNodes(self):
		"""test _getRootNodes"""
		raise NotImplementedError()

	def test_columnCount(self):
		"""test columnCount"""
		cm = catsModel([], [])
		self.assertEqual(cm.columnCount("a"), 1)

	def test_data(self):
		"""test data"""
		raise NotImplementedError()

	def test_flags(self):
		"""test flags"""
		cm = catsModel([], [])
		with patch("PySide2.QtCore.QModelIndex.isValid",
				return_value = False) as _iv:
			self.assertEqual(cm.flags(QModelIndex()), None)
			_iv.assert_called_once_with()

		with patch("PySide2.QtCore.QModelIndex.isValid",
				return_value = True) as _iv, \
				patch("PySide2.QtCore.QModelIndex.column",
					return_value = 1) as _c:
			self.assertEqual(cm.flags(QModelIndex()),
				Qt.ItemIsEnabled | Qt.ItemIsSelectable)
			_iv.assert_called_once_with()
			_c.assert_called_once_with()

		with patch("PySide2.QtCore.QModelIndex.isValid",
				return_value = True) as _iv, \
				patch("PySide2.QtCore.QModelIndex.column",
					return_value = 0) as _c:
			self.assertEqual(cm.flags(QModelIndex()),
				Qt.ItemIsEnabled | Qt.ItemIsSelectable)
			_iv.assert_called_once_with()
			_c.assert_called_once_with()

		p = QWidget()
		p.askCats = False
		cm = catsModel([], [], p)
		with patch("PySide2.QtCore.QModelIndex.isValid",
				return_value = True) as _iv, \
				patch("PySide2.QtCore.QModelIndex.column",
					return_value = 0) as _c:
			self.assertEqual(cm.flags(QModelIndex()),
				Qt.ItemIsEnabled | Qt.ItemIsSelectable)
			_iv.assert_called_once_with()
			_c.assert_called_once_with()

		p = QWidget()
		p.askCats = True
		cm = catsModel([], [], p)
		with patch("PySide2.QtCore.QModelIndex.isValid",
				return_value = True) as _iv, \
				patch("PySide2.QtCore.QModelIndex.column",
					return_value = 0) as _c:
			self.assertEqual(cm.flags(QModelIndex()),
				Qt.ItemIsUserCheckable | Qt.ItemIsEditable | \
				Qt.ItemIsEnabled | Qt.ItemIsSelectable)
			_iv.assert_called_once_with()
			_c.assert_called_once_with()

	def test_headerData(self):
		"""test headerData"""
		cm = catsModel([], [])
		self.assertEqual(cm.headerData(0, Qt.Horizontal, Qt.DisplayRole),
			"Name")
		self.assertEqual(cm.headerData(1, Qt.Horizontal, Qt.DisplayRole),
			None)
		self.assertEqual(cm.headerData(0, Qt.Vertical, Qt.DisplayRole),
			None)
		self.assertEqual(cm.headerData(0, Qt.Horizontal, Qt.EditRole),
			None)

	def test_setData(self):
		"""test setData"""
		raise NotImplementedError()

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestCategoriesTreeWindow(GUITestCase):
	"""test the catsTreeWindow class"""
	def test_init(self):
		"""test init"""
		p = QWidget()
		ctw = catsTreeWindow(p)
		raise NotImplementedError()

	def test_populateAskCats(self):
		"""test populateAskCats"""
		raise NotImplementedError()

	def test_onCancel(self):
		"""test onCancel"""
		ctw = catsTreeWindow()
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			ctw.onCancel()
		self.assertFalse(ctw.result)

	def test_onOk(self):
		"""test onOk"""
		raise NotImplementedError()

	def test_changeFilter(self):
		"""test changeFilter"""
		p = QWidget()
		ctw = catsTreeWindow(p)
		with patch("PySide2.QtWidgets.QTreeView.expandAll") as _e:
			ctw.changeFilter("abc")
			_e.assert_called_once_with()
		self.assertEqual(ctw.proxyModel.filterRegExp().pattern(), "abc")
		with patch("PySide2.QtWidgets.QTreeView.expandAll") as _e:
			ctw.changeFilter(123)
			_e.assert_called_once_with()
		self.assertEqual(ctw.proxyModel.filterRegExp().pattern(), "123")

	def test_onAskExps(self):
		"""test onAskExps"""
		p = QWidget()
		ctw = catsTreeWindow(p)
		with patch("physbiblio.gui.catWindows.catsTreeWindow.onOk"
				) as _oo:
			ctw.onAskExps()
			_oo.assert_called_once_with(exps = True)

	def test_onNewCat(self):
		"""test onNewCat"""
		p = QWidget()
		ctw = catsTreeWindow(p)
		with patch("physbiblio.gui.catWindows.editCategory") as _ec, \
				patch("physbiblio.gui.catWindows.catsTreeWindow.recreateTable"
					) as _rt:
			ctw.onNewCat()
			_ec.assert_called_once_with(p, p)
			_rt.assert_called_once()

	def test_keyPressEvent(self):
		"""test keyPressEvent"""
		ctw = catsTreeWindow()
		with patch("PySide2.QtWidgets.QDialog.close") as _oc:
			QTest.keyPress(ctw, "a")
			_oc.assert_not_called()
			QTest.keyPress(ctw, Qt.Key_Enter)
			_oc.assert_not_called()
			QTest.keyPress(ctw, Qt.Key_Escape)
			_oc.assert_called_once()

	def test_createForm(self):
		"""test createForm"""
		raise NotImplementedError()

	def test_populateTree(self):
		"""test _populateTree"""
		raise NotImplementedError()

	def test_handleItemEntered(self):
		"""test handleItemEntered"""
		raise NotImplementedError()

	def test_contextMenuEvent(self):
		"""test contextMenuEvent"""
		raise NotImplementedError()

	def test_cleanLayout(self):
		"""test cleanLayout"""
		ctw = catsTreeWindow()
		self.assertEqual(ctw.layout().count(), 3)
		ctw.cleanLayout()
		self.assertEqual(ctw.layout().count(), 0)

	def test_recreateTable(self):
		"""test recreateTable"""
		ctw = catsTreeWindow()
		with patch("physbiblio.gui.catWindows.catsTreeWindow.cleanLayout"
				) as _c1, \
				patch("physbiblio.gui.catWindows.catsTreeWindow.createForm"
					) as _c2:
			ctw.recreateTable()
			_c1.assert_called_once_with()
			_c2.assert_called_once_with()

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
		sc = catsTreeWindow(parent = ecd,
			askCats = True,
			expButton = False,
			single = True,
			previous = [0])
		sc.onCancel()
		txt = ecd.textValues["parentCat"].text()
		with patch("physbiblio.gui.catWindows.catsTreeWindow.__init__",
				return_value = None) as _i:
			ecd.onAskParent(sc)
			_i.assert_called_once_with(parent = ecd,
				askCats = True,
				expButton = False,
				single = True,
				previous = ecd.selectedCats)
		self.assertEqual(ecd.textValues["parentCat"].text(),
			"0 - Main")

		sc = catsTreeWindow(parent = ecd,
			askCats = True,
			expButton = False,
			single = True,
			previous = [1])
		sc.onOk()
		with patch("physbiblio.gui.catWindows.catsTreeWindow.__init__",
				return_value = None) as _i:
			ecd.onAskParent(sc)
			_i.assert_called_once_with(parent = ecd,
				askCats = True,
				expButton = False,
				single = True,
				previous = ecd.selectedCats)
		self.assertEqual(ecd.textValues["parentCat"].text(),
			"1 - Tags")

		sc = catsTreeWindow(parent = ecd,
			askCats = True,
			expButton = False,
			single = True,
			previous = [0, 1])
		sc.onOk()
		with patch("physbiblio.gui.catWindows.catsTreeWindow.__init__",
				return_value = None) as _i:
			ecd.onAskParent(sc)
			_i.assert_called_once_with(parent = ecd,
				askCats = True,
				expButton = False,
				single = True,
				previous = ecd.selectedCats)
		self.assertEqual(ecd.textValues["parentCat"].text(),
			"1 - Tags")

		sc = catsTreeWindow(parent = ecd,
			askCats = True,
			expButton = False,
			single = True,
			previous = [])
		sc.onOk()
		with patch("physbiblio.gui.catWindows.catsTreeWindow.__init__",
				return_value = None) as _i:
			ecd.onAskParent(sc)
			_i.assert_called_once_with(parent = ecd,
				askCats = True,
				expButton = False,
				single = True,
				previous = ecd.selectedCats)
		self.assertEqual(ecd.textValues["parentCat"].text(),
			"Select parent")

		sc = catsTreeWindow(parent = ecd,
			askCats = True,
			expButton = False,
			single = True,
			previous = [9999])
		sc.onOk()
		with patch("physbiblio.gui.catWindows.catsTreeWindow.__init__",
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
