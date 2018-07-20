#!/usr/bin/env python
"""
Test file for the physbiblio.gui.commonClasses module.

This file is part of the physbiblio package.
"""
import sys, traceback
import os
from PySide2.QtCore import Qt, QPoint, QRect
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QInputDialog, QDesktopWidget, QLineEdit, QWidget

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch, call
else:
	import unittest
	from unittest.mock import patch, call

try:
	from physbiblio.setuptests import *
	from physbiblio.gui.setuptests import *
	from physbiblio.gui.commonClasses import *
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

class emptyTableModel(QAbstractTableModel):
	"""Used to do tests when a table model is needed"""
	def __init__(self, *args):
		QAbstractTableModel.__init__(self, *args)

	def rowCount(self, a = None):
		return 1

	def columnCount(self, a = None):
		return 1

	def data(self, index, role):
		return None

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestLabels(GUITestCase):
	"""
	Test the MyLabelRight and MyLabelCenter classes
	"""
	def test_myLabelRight(self):
		"""Test MyLabelRight"""
		l = MyLabelRight("label")
		self.assertIsInstance(l, QLabel)
		self.assertEqual(l.text(), "label")
		self.assertEqual(l.alignment(), Qt.AlignRight | Qt.AlignVCenter)

	def test_myLabelCenter(self):
		"""Test MyLabelCenter"""
		l = MyLabelCenter("label")
		self.assertIsInstance(l, QLabel)
		self.assertEqual(l.text(), "label")
		self.assertEqual(l.alignment(), Qt.AlignCenter | Qt.AlignVCenter)

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestMyComboBox(GUITestCase):
	"""
	Test the MyComboBox class
	"""
	def test_init(self):
		"""test the constructor"""
		ew = QWidget()
		mb = MyComboBox(ew, [])
		self.assertIsInstance(mb, QComboBox)
		self.assertEqual(mb.parentWidget(), ew)
		self.assertEqual(mb.itemText(0), "")
		mb = MyComboBox(ew, ["1", "2"])
		self.assertEqual(mb.itemText(0), "1")
		self.assertEqual(mb.itemText(1), "2")
		self.assertEqual(mb.itemText(2), "")
		self.assertEqual(mb.currentText(), "1")
		mb = MyComboBox(ew, ["1", "2"],  "0")
		self.assertEqual(mb.currentText(), "1")
		mb = MyComboBox(ew, ["1", "2"],  "2")
		self.assertEqual(mb.currentText(), "2")
		mb = MyComboBox(ew, [1, 2])
		self.assertEqual(mb.itemText(0), "1")
		self.assertEqual(mb.itemText(1), "2")
		self.assertEqual(mb.itemText(2), "")

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestMyAndOrCombo(GUITestCase):
	"""
	Test the MyAndOrCombo class
	"""
	def test_init(self):
		"""test the constructor"""
		mb = MyAndOrCombo(None)
		self.assertIsInstance(mb, MyComboBox)
		self.assertIsInstance(mb, QComboBox)
		self.assertEqual(mb.parentWidget(), None)
		self.assertEqual(mb.itemText(0), "AND")
		self.assertEqual(mb.itemText(1), "OR")
		self.assertEqual(mb.itemText(2), "")
		self.assertEqual(mb.currentText(), "AND")
		mb = MyAndOrCombo(None, "or")
		self.assertEqual(mb.currentText(), "AND")
		ew = QWidget()
		mb = MyAndOrCombo(ew, "OR")
		self.assertEqual(mb.parentWidget(), ew)
		self.assertEqual(mb.currentText(), "OR")

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestMyTrueFalseCombo(GUITestCase):
	"""
	Test the MyTrueFalseCombo class
	"""
	def test_init(self):
		"""test the constructor"""
		mb = MyTrueFalseCombo(None)
		self.assertIsInstance(mb, MyComboBox)
		self.assertIsInstance(mb, QComboBox)
		self.assertEqual(mb.parentWidget(), None)
		self.assertEqual(mb.itemText(0), "True")
		self.assertEqual(mb.itemText(1), "False")
		self.assertEqual(mb.itemText(2), "")
		self.assertEqual(mb.currentText(), "True")
		mb = MyTrueFalseCombo(None, "abc")
		self.assertEqual(mb.currentText(), "True")
		ew = QWidget()
		mb = MyTrueFalseCombo(ew, "False")
		self.assertEqual(mb.parentWidget(), ew)
		self.assertEqual(mb.currentText(), "False")

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestObjListWindow(GUITestCase):
	"""
	Test the objListWindow class
	"""
	def test_init(self):
		"""test the __init__ function"""
		olw = objListWindow()
		self.assertIsInstance(olw, QDialog)
		self.assertEqual(olw.tableWidth, None)
		self.assertEqual(olw.proxyModel, None)
		self.assertFalse(olw.gridLayout)
		self.assertIsInstance(olw.currLayout, QVBoxLayout)
		self.assertEqual(olw.layout(), olw.currLayout)

		olw = objListWindow(gridLayout = True)
		self.assertTrue(olw.gridLayout)
		self.assertIsInstance(olw.currLayout, QGridLayout)
		self.assertEqual(olw.layout(), olw.currLayout)

	def test_NI(self):
		"""Test the non implemented functions (must be subclassed!)"""
		olw = objListWindow()
		ix = QModelIndex()
		self.assertRaises(NotImplementedError, lambda: olw.createTable())
		self.assertRaises(NotImplementedError, lambda: olw.cellClick(ix))
		self.assertRaises(NotImplementedError, lambda: olw.cellDoubleClick(ix))
		self.assertRaises(NotImplementedError, lambda: olw.handleItemEntered(ix))
		self.assertRaises(NotImplementedError, lambda: olw.triggeredContextMenuEvent(0, 0, ix))

	def test_changeFilter(self):
		"""test changeFilter"""
		olw = objListWindow()
		olw.table_model = emptyTableModel()
		olw.setProxyStuff(1, Qt.AscendingOrder)
		olw.changeFilter("abc")
		self.assertEqual(olw.proxyModel.filterRegExp().pattern(), "abc")
		olw.changeFilter(123)
		self.assertEqual(olw.proxyModel.filterRegExp().pattern(), "123")

	def test_addFilterInput(self):
		"""test addFilterInput"""
		olw = objListWindow()
		olw.addFilterInput("plch")
		self.assertIsInstance(olw.filterInput, QLineEdit)
		self.assertEqual(olw.filterInput.placeholderText(), "plch")
		with patch("physbiblio.gui.commonClasses.objListWindow.changeFilter") as _cf:
			olw.filterInput.textChanged.emit("sss")
			_cf.assert_called_once_with("sss")

		olw = objListWindow(gridLayout = True)
		olw.addFilterInput("plch", gridPos = (4, 1))
		self.assertEqual(olw.layout().itemAtPosition(4, 1).widget(), olw.filterInput)

	def test_setProxyStuff(self):
		"""test setProxyStuff"""
		olw = objListWindow()
		olw.table_model = emptyTableModel()
		with patch("PySide2.QtCore.QSortFilterProxyModel.sort") as _s:
			olw.setProxyStuff(1, Qt.AscendingOrder)
			_s.assert_called_once_with(1, Qt.AscendingOrder)
		self.assertIsInstance(olw.proxyModel, QSortFilterProxyModel)
		self.assertEqual(olw.proxyModel.filterCaseSensitivity(), Qt.CaseInsensitive)
		self.assertEqual(olw.proxyModel.sortCaseSensitivity(), Qt.CaseInsensitive)
		self.assertEqual(olw.proxyModel.filterKeyColumn(), -1)

		self.assertIsInstance(olw.tablewidget, MyTableView)
		self.assertEqual(olw.tablewidget.model(), olw.proxyModel)
		self.assertTrue(olw.tablewidget.isSortingEnabled())
		self.assertTrue(olw.tablewidget.hasMouseTracking())
		self.assertEqual(olw.layout().itemAt(0).widget(), olw.tablewidget)

	def test_finalizeTable(self):
		"""Test finalizeTable"""
		olw = objListWindow()
		olw.table_model = emptyTableModel()
		with patch("PySide2.QtCore.QSortFilterProxyModel.sort") as _s:
			olw.setProxyStuff(1, Qt.AscendingOrder)
		with patch("PySide2.QtWidgets.QTableView.resizeColumnsToContents") as _rc:
			with patch("PySide2.QtWidgets.QTableView.resizeRowsToContents") as _rr:
				olw.finalizeTable()
				_rc.assert_has_calls([call(), call()])
				_rr.assert_called_once()
		self.assertIsInstance(olw.tablewidget, MyTableView)
		maxw = QDesktopWidget().availableGeometry().width()
		self.assertEqual(olw.maximumHeight(), QDesktopWidget().availableGeometry().height())
		self.assertEqual(olw.maximumWidth(), maxw)
		hwidth = olw.tablewidget.horizontalHeader().length()
		swidth = olw.tablewidget.style().pixelMetric(QStyle.PM_ScrollBarExtent)
		fwidth = olw.tablewidget.frameWidth() * 2

		if hwidth > maxw - (swidth + fwidth):
			tW = maxw - (swidth + fwidth)
		else:
			tW = hwidth + swidth + fwidth
		self.assertEqual(olw.tablewidget.width(), tW)
		self.assertEqual(olw.minimumHeight(), 600)
		ix = QModelIndex()
		with patch("physbiblio.gui.commonClasses.objListWindow.handleItemEntered") as _f:
			olw.tablewidget.entered.emit(ix)
			_f.assert_called_once_with(ix)
		with patch("physbiblio.gui.commonClasses.objListWindow.cellClick") as _f:
			olw.tablewidget.clicked.emit(ix)
			_f.assert_called_once_with(ix)
		with patch("physbiblio.gui.commonClasses.objListWindow.cellDoubleClick") as _f:
			olw.tablewidget.doubleClicked.emit(ix)
			_f.assert_called_once_with(ix)
		self.assertEqual(olw.layout().itemAt(0).widget(), olw.tablewidget)

		olw = objListWindow(gridLayout = True)
		olw.table_model = emptyTableModel()
		with patch("PySide2.QtCore.QSortFilterProxyModel.sort") as _s:
			olw.setProxyStuff(1, Qt.AscendingOrder)
		olw.finalizeTable(gridPos = (4, 1))
		self.assertEqual(olw.layout().itemAtPosition(4, 1).widget(), olw.tablewidget)

	def test_cleanLayout(self):
		"""Test cleanLayout"""
		olw = objListWindow()
		olw.layout().addWidget(QLabel("empty"))
		olw.layout().addWidget(QLabel("empty1"))
		self.assertEqual(olw.layout().count(), 2)
		olw.cleanLayout()
		self.assertEqual(olw.layout().count(), 0)

	def test_recreateTable(self):
		"""Test recreateTable"""
		olw = objListWindow()
		with patch("physbiblio.gui.commonClasses.objListWindow.cleanLayout") as _cl:
			with patch("physbiblio.gui.commonClasses.objListWindow.createTable") as _ct:
				olw.recreateTable()
				_cl.assert_called_once()
				_ct.assert_called_once()

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestEditObjectWindow(GUITestCase):
	"""
	Test the editObjectWindow class
	"""
	def test_init(self):
		"""test constructor"""
		ew = QWidget()
		with patch("physbiblio.gui.commonClasses.editObjectWindow.initUI") as _iu:
			eow = editObjectWindow(ew)
			self.assertEqual(eow.parent, ew)
			self.assertEqual(eow.textValues, {})
			_iu.assert_called_once_with()

	def test_keyPressEvent(self):
		"""test keyPressEvent"""
		eow = editObjectWindow()
		w = QLineEdit()
		eow.currGrid.addWidget(w, 0, 0)
		with patch("physbiblio.gui.commonClasses.editObjectWindow.onCancel") as _oc:
			QTest.keyPress(w, "a")
			_oc.assert_not_called()
			QTest.keyPress(w, Qt.Key_Enter)
			_oc.assert_not_called()
			QTest.keyPress(w, Qt.Key_Escape)
			_oc.assert_called_once()

	def test_onCancel(self):
		"""test onCancel"""
		eow = editObjectWindow()
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			eow.onCancel()
			self.assertFalse(eow.result)
			_c.assert_called_once()

	def test_onOk(self):
		"""test onOk"""
		eow = editObjectWindow()
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			eow.onOk()
			self.assertTrue(eow.result)
			_c.assert_called_once()

	def test_initUI(self):
		"""test initUI"""
		with patch("physbiblio.gui.commonClasses.editObjectWindow.initUI") as _iu:
			eow = editObjectWindow()
		self.assertFalse(hasattr(eow, "currGrid"))
		eow = editObjectWindow()
		self.assertIsInstance(eow.currGrid, QGridLayout)
		self.assertEqual(eow.layout(), eow.currGrid)
		self.assertEqual(eow.currGrid.spacing(), 1)

	def test_centerWindow(self):
		"""test centerWindow"""
		eow = editObjectWindow()
		with patch("PySide2.QtWidgets.QDialog.frameGeometry", autospec = True, return_value = QRect()) as _fg:
			with patch("PySide2.QtCore.QRect.center", autospec = True, return_value = QPoint()) as _ce:
				with patch("PySide2.QtCore.QRect.moveCenter", autospec = True) as _mc:
					with patch("PySide2.QtCore.QRect.topLeft", autospec = True, return_value = QPoint()) as _tl:
						with patch("PySide2.QtWidgets.QDialog.move", autospec = True) as _mo:
							eow.centerWindow()
							_fg.assert_called_once()
							_ce.assert_called_once()
							_mc.assert_called_once()
							_tl.assert_called_once()
							_mo.assert_called_once()

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestMyThread(GUITestCase):
	"""
	Test the MyThread class
	"""
	def test_methods(self):
		"""test all the methods in the class"""
		with patch("PySide2.QtCore.QThread.__init__", autospec = True) as _in:
			MyThread()
			_in.assert_called_once()
		mt = MyThread()
		self.assertIsInstance(mt, QThread)
		self.assertRaises(NotImplementedError, lambda: mt.run())
		self.assertRaises(NotImplementedError, lambda: mt.setStopFlag())
		self.assertIsInstance(mt.finished, Signal)
		with patch("time.sleep", autospec = True) as _sl:
			with patch("PySide2.QtCore.QThread.start", autospec = True) as _st:
				mt.start()
				_sl.assert_called_once_with(0.3)
				_st.assert_called_once_with(mt)
				_st.reset_mock()
				mt.start(1, a = "try")
				_st.assert_called_once_with(mt, 1, a = "try")

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestWriteStream(GUITestCase):
	"""
	Test the WriteStream class
	"""
	def test_methods(self):
		pass

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestMyTableWidget(GUITestCase):
	"""
	Test the MyTableWidget class
	"""
	def test_methods(self):
		pass

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestMyTableView(GUITestCase):
	"""
	Test the MyTableView class
	"""
	def test_methods(self):
		pass

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestMyTableModel(GUITestCase):
	"""
	Test the MyTableModel class
	"""
	def test_init(self):
		pass
	def test_changeAsk(self):
		pass
	def test_getIdentifier(self):
		# self.assertRaises(NotImplementedError, lambda: ())
		pass
	def test_prepareSelected(self):
		pass
	def test_selectAll(self):
		pass
	def test_unselectAll(self):
		pass
	def test_addImage(self):
		pass
	def test_addImages(self):
		pass
	def test_rowCount(self):
		pass
	def test_columnCount(self):
		pass
	def test_data(self):
		# self.assertRaises(NotImplementedError, lambda: ())
		pass
	def test_flags(self):
		pass
	def test_headerData(self):
		pass
	def test_setData(self):
		# self.assertRaises(NotImplementedError, lambda: ())
		pass
	def test_sort(self):
		pass

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestTreeNode(GUITestCase):
	"""
	Test the TreeNode class
	"""
	def test_methods(self):
		"""test the __init__ and _getChildren methods"""
		ew = QWidget()
		with patch("physbiblio.gui.commonClasses.TreeNode._getChildren", return_value = "def") as _gc:
			tn = TreeNode(ew, "abc")
			self.assertEqual(tn.parent, ew)
			self.assertEqual(tn.row, "abc")
			self.assertEqual(tn.subnodes, "def")
			_gc.assert_called_once_with()
		self.assertRaises(NotImplementedError, lambda: tn._getChildren())

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestTreeModel(GUITestCase):
	"""
	Test the TreeModel class
	"""
	def test_init(self):
		pass
	def test_getRootNodes(self):
		# self.assertRaises(NotImplementedError, lambda: ())
		pass
	def test_index(self):
		pass
	def test_parent(self):
		pass
	def test_reset(self):
		pass
	def test_rowCount(self):
		pass

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestNamedElement(GUITestCase):
	"""
	Test the NamedElement class
	"""
	def test_init(self):
		pass

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestNamedNode(GUITestCase):
	"""
	Test the NamedNode class
	"""
	def test_methods(self):
		pass

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestLeafFilterProxyModel(GUITestCase):
	"""
	Test the LeafFilterProxyModel class
	"""
	def test_init(self):#just check if it is instance of parent class
		pass
	def test_filterAcceptsRow(self):
		pass
	def test_filter_accept_row_itself(self):
		pass
	def test_filter_accepts_any_parent(self):
		pass
	def test_has_accepted_children(self):
		pass

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestMyDDTableWidget(GUITestCase):
	"""
	Test the MyDDTableWidget class
	"""
	def test_init(self):
		pass
	def test_dropMimeData(self):
		pass
	def test_dropEvent(self):
		pass
	def test_getselectedRowsFast(self):
		pass

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestMyMenu(GUITestCase):
	"""
	Test the MyMenu class
	"""
	def test_init(self):
		pass
	def test_fillMenu(self):
		pass
	def test_keyPressEvent(self):
		pass

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestGuiViewEntry(GUITestCase):
	"""
	Test the GuiViewEntry class
	"""
	def test_init(self):
		pass
	def test_openLink(self):
		pass

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestMyImportedTableModel(GUITestCase):
	"""
	Test the MyImportedTableModel class
	"""
	def test_init(self):
		pass
	def test_getIdentifier(self):
		pass
	def test_data(self):
		pass
	def test_setData(self):
		pass
	def test_flags(self):
		pass

if __name__=='__main__':
	unittest.main()
