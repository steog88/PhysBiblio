#!/usr/bin/env python
"""
Test file for the physbiblio.gui.commonClasses module.

This file is part of the physbiblio package.
"""
import sys, traceback
import os
import time
from PySide2.QtCore import Qt, QModelIndex, QPoint, QRect
from PySide2.QtGui import QContextMenuEvent
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QAction, QDesktopWidget, QInputDialog, QLineEdit, QWidget

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch, call
	from Queue import Queue
else:
	import unittest
	from unittest.mock import patch, call
	from queue import Queue

try:
	from physbiblio.setuptests import *
	from physbiblio.database import pBDB
	from physbiblio.gui.setuptests import *
	from physbiblio.gui.commonClasses import *
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

def fakeExec_writeStream_mys(x, text):
	"""simulate WriteStream.run and set running=False"""
	x.running = False
	x.text = text
def fakeExec_writeStream_fin(x):
	"""probe that finished has been emitted"""
	x.running = False
	x.fin = True
def fakeExec_dataChanged(x, y):
	"""probe that dataChanged has been emitted"""
	assert x == y

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

class emptyTreeModel(TreeModel):
	"""Used to do tests when a tree model is needed"""
	def __init__(self, elements, *args):
		self.rootElements = elements
		TreeModel.__init__(self, *args)

	def _getRootNodes(self):
		return [NamedNode(elem, None, index)
			for index, elem in enumerate(self.rootElements)]

	def rowCount(self, a = None):
		return 2

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
		with patch("PySide2.QtWidgets.QTableView.resizeColumnsToContents") as _rc, \
				patch("PySide2.QtWidgets.QTableView.resizeRowsToContents") as _rr:
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
		with patch("physbiblio.gui.commonClasses.objListWindow.cleanLayout") as _cl, \
				patch("physbiblio.gui.commonClasses.objListWindow.createTable") as _ct:
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
		with patch("PySide2.QtWidgets.QDialog.frameGeometry",
					autospec = True, return_value = QRect()) as _fg,\
				patch("PySide2.QtCore.QRect.center",
					autospec = True, return_value = QPoint()) as _ce,\
				patch("PySide2.QtCore.QRect.moveCenter",
					autospec = True) as _mc,\
				patch("PySide2.QtCore.QRect.topLeft",
					autospec = True, return_value = QPoint()) as _tl,\
				patch("PySide2.QtWidgets.QDialog.move",
					autospec = True) as _mo:
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
		with patch("time.sleep", autospec = True) as _sl,\
				patch("PySide2.QtCore.QThread.start", autospec = True) as _st:
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
		"""
		Test __init__, write, run methods
		"""
		queue = Queue()
		ws = WriteStream(queue)
		self.assertIsInstance(ws, MyThread)
		self.assertEqual(ws.queue, queue)
		self.assertTrue(ws.running)
		self.assertEqual(ws.parent(), None)
		self.assertIsInstance(ws.mysignal, Signal)
		self.assertIsInstance(ws.finished, Signal)
		ew = QWidget()
		ws = WriteStream(queue, parent = ew)
		self.assertEqual(ws.parent(), ew)
		ws.finished.connect(lambda: fakeExec_writeStream_fin(ws))
		if sys.version_info[0] < 3:
			with patch("Queue.Queue.put") as _put:
				ws.write("abc")
				_put.assert_called_once_with("abc")
			with patch("Queue.Queue.get", return_value = "abc") as _get:
				ws.mysignal.connect(lambda x: fakeExec_writeStream_mys(ws, x))
				ws.run()
				_get.assert_called_once()
				self.assertEqual(ws.text, "abc")
				self.assertTrue(ws.fin)
		else:
			with patch("queue.Queue.put") as _put:
				ws.write("abc")
				_put.assert_called_once_with("abc")
			with patch("queue.Queue.get", return_value = "abc") as _get:
				ws.mysignal.connect(lambda x: fakeExec_writeStream_mys(ws, x))
				ws.run()
				_get.assert_called_once()
				self.assertEqual(ws.text, "abc")
				self.assertTrue(ws.fin)

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestMyTableWidget(GUITestCase):
	"""
	Test the MyTableWidget class
	"""
	def test_methods(self):
		"""
		Test __init__, contextMenuEvent methods
		"""
		p = objListWindow()
		with patch("PySide2.QtWidgets.QTableWidget.__init__") as _i:
			MyTableWidget(2, 2, p)
			_i.assert_called_once_with(2, 2, p)
		mtw = MyTableWidget(2, 2, p)
		self.assertIsInstance(mtw, QTableWidget)
		self.assertEqual(mtw.parent, p)
		e = QContextMenuEvent(QContextMenuEvent.Mouse, QPoint())
		with patch("PySide2.QtGui.QContextMenuEvent.x",
					return_value = 12) as _x,\
				patch("PySide2.QtGui.QContextMenuEvent.y",
					return_value = 24) as _y,\
				patch("PySide2.QtWidgets.QTableWidget.rowAt",
					return_value = 0) as _r,\
				patch("PySide2.QtWidgets.QTableWidget.columnAt",
					return_value = 1) as _c,\
				patch("physbiblio.gui.commonClasses.objListWindow.triggeredContextMenuEvent") as _t:
			mtw.contextMenuEvent(e)
			_x.assert_called_once_with()
			_y.assert_called_once_with()
			_r.assert_called_once_with(24)
			_c.assert_called_once_with(12)
			_t.assert_called_once_with(0, 1, e)

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestMyTableView(GUITestCase):
	"""
	Test the MyTableView class
	"""
	def test_methods(self):
		"""
		Test __init__, contextMenuEvent methods
		"""
		p = objListWindow()
		with patch("PySide2.QtWidgets.QTableView.__init__") as _i:
			MyTableView(p)
			_i.assert_called_once_with(p)
		mtw = MyTableView(p)
		self.assertIsInstance(mtw, QTableView)
		self.assertEqual(mtw.parent, p)
		e = QContextMenuEvent(QContextMenuEvent.Mouse, QPoint())
		with patch("PySide2.QtGui.QContextMenuEvent.x",
					return_value = 12) as _x,\
				patch("PySide2.QtGui.QContextMenuEvent.y",
					return_value = 24) as _y,\
				patch("PySide2.QtWidgets.QTableView.rowAt",
					return_value = 0) as _r,\
				patch("PySide2.QtWidgets.QTableView.columnAt",
					return_value = 1) as _c,\
				patch("physbiblio.gui.commonClasses.objListWindow.triggeredContextMenuEvent") as _t:
			mtw.contextMenuEvent(e)
			_x.assert_called_once_with()
			_y.assert_called_once_with()
			_r.assert_called_once_with(24)
			_c.assert_called_once_with(12)
			_t.assert_called_once_with(0, 1, e)

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestMyTableModel(GUITestCase):
	"""
	Test the MyTableModel class
	"""
	@patch('sys.stdout', new_callable=StringIO)
	def assert_in_stdout(self, function, expected_output, mock_stdout):
		"""Catch and if test stdout of the function contains a string"""
		pBErrorManager.tempHandler(sys.stdout, format = '%(message)s')
		function()
		pBErrorManager.rmTempHandler()
		self.assertIn(expected_output, mock_stdout.getvalue())

	def test_init(self):
		"""test constructor"""
		p = objListWindow()
		mtm = MyTableModel(p, ["a", "b"])
		self.assertIsInstance(mtm, QAbstractTableModel)
		self.assertEqual(mtm.header, ["a", "b"])
		self.assertEqual(mtm.parentObj, p)
		self.assertEqual(mtm.previous, [])
		self.assertFalse(mtm.ask)
		mtm = MyTableModel(p, ["a", "b"], ask = True, previous = [1])
		self.assertEqual(mtm.previous, [1])
		self.assertTrue(mtm.ask)

	def test_changeAsk(self):
		"""Test changeAsk"""
		def setAbout(cl):
			cl.about = True
		def setChanged(cl):
			cl.changed = True
		p = objListWindow()
		mtm = MyTableModel(p, ["a", "b"])
		mtm.about = False
		mtm.changed = False
		mtm.layoutAboutToBeChanged.connect(lambda: setAbout(mtm))
		mtm.layoutChanged.connect(lambda: setChanged(mtm))
		self.assertFalse(mtm.about)
		self.assertFalse(mtm.changed)
		mtm.changeAsk()
		self.assertTrue(mtm.about)
		self.assertTrue(mtm.changed)
		self.assertTrue(mtm.ask)
		mtm.changeAsk()
		self.assertFalse(mtm.ask)
		mtm.changeAsk(False)
		self.assertFalse(mtm.ask)
		mtm.changeAsk(True)
		self.assertTrue(mtm.ask)
		mtm.changeAsk("a")#does nothing
		self.assertTrue(mtm.ask)

	def test_getIdentifier(self):
		"""Test that getIdentifier is not implemented"""
		p = objListWindow()
		mtm = MyTableModel(p, ["a", "b"])
		self.assertRaises(NotImplementedError, lambda: mtm.getIdentifier("a"))

	def test_prepareSelected(self):
		"""test prepareSelected"""
		def setAbout(cl):
			cl.about = True
		def setChanged(cl):
			cl.changed = True
		p = objListWindow()
		mtm = MyTableModel(p, ["a", "b"])
		mtm.dataList = [{"a": 1, "b": 3}, {"a": 2, "b": 2}, {"a": 3, "b": 1}]
		mtm.about = False
		mtm.changed = False
		mtm.layoutAboutToBeChanged.connect(lambda: setAbout(mtm))
		mtm.layoutChanged.connect(lambda: setChanged(mtm))
		self.assertFalse(mtm.about)
		self.assertFalse(mtm.changed)
		with patch("physbiblio.gui.commonClasses.MyTableModel.getIdentifier", side_effect = [0, 1, 2]) as _gi:
			mtm.prepareSelected()
			_gi.assert_has_calls([call({"a": 1, "b": 3}), call({"a": 2, "b": 2}), call({"a": 3, "b": 1})])
		self.assertEqual(mtm.selectedElements, {0: False, 1: False, 2: False})
		mtm = MyTableModel(p, ["a", "b"], previous = [2])
		mtm.dataList = [{"a": 1, "b": 3}, {"a": 2, "b": 2}, {"a": 3, "b": 1}]
		with patch("physbiblio.gui.commonClasses.MyTableModel.getIdentifier", side_effect = [0, 1, 2]) as _gi:
			mtm.prepareSelected()
			_gi.assert_has_calls([call({"a": 1, "b": 3}), call({"a": 2, "b": 2}), call({"a": 3, "b": 1})])
		self.assertEqual(mtm.selectedElements, {0: False, 1: False, 2: True})
		mtm = MyTableModel(p, ["a", "b"], previous = [1, 5])
		mtm.dataList = [{"a": 1, "b": 3}, {"a": 2, "b": 2}, {"a": 3, "b": 1}]
		with patch("physbiblio.gui.commonClasses.MyTableModel.getIdentifier", side_effect = [0, 1, 2]) as _gi:
			self.assert_in_stdout(mtm.prepareSelected, "Invalid identifier in previous selection: 5")
			_gi.assert_has_calls([call({"a": 1, "b": 3}), call({"a": 2, "b": 2}), call({"a": 3, "b": 1})])
		self.assertEqual(mtm.selectedElements, {0: False, 1: True, 2: False})
		mtm = MyTableModel(p, ["a", "b"])
		with patch("physbiblio.gui.commonClasses.MyTableModel.getIdentifier", side_effect = [0, 1, 2]) as _gi:
			self.assert_in_stdout(mtm.prepareSelected, "dataList is not defined!")
			_gi.assert_not_called()
		self.assertEqual(mtm.selectedElements, {})

	def test_un_selectAll(self):
		"""test selectAll and unselectAll"""
		def setAbout(cl):
			cl.about = True
		def setChanged(cl):
			cl.changed = True
		p = objListWindow()
		mtm = MyTableModel(p, ["a", "b"])
		dl = [{"a": 1, "b": 3}, {"a": 2, "b": 2}, {"a": 3, "b": 1}]
		mtm.dataList = dl
		mtm.about = False
		mtm.changed = False
		mtm.layoutAboutToBeChanged.connect(lambda: setAbout(mtm))
		mtm.layoutChanged.connect(lambda: setChanged(mtm))
		self.assertFalse(mtm.about)
		self.assertFalse(mtm.changed)
		mtm.selectedElements = {0: False, 1: False, 2: False}
		mtm.selectAll()
		self.assertTrue(mtm.about)
		self.assertTrue(mtm.changed)
		self.assertEqual(mtm.selectedElements, {0: True, 1: True, 2: True})
		mtm.about = False
		mtm.changed = False
		mtm.unselectAll()
		self.assertTrue(mtm.about)
		self.assertTrue(mtm.changed)
		self.assertEqual(mtm.selectedElements, {0: False, 1: False, 2: False})

	def test_addImage(self):
		"""Test addImage"""
		p = objListWindow()
		mtm = MyTableModel(p, ["a", "b"])
		img = mtm.addImage(":/images/edit.png", 51)
		self.assertIsInstance(img, QPixmap)
		self.assertEqual(img.height(), 51)
		img = mtm.addImage(":/images/nonexistent", 51)
		self.assertTrue(img.isNull())

	def test_addImages(self):
		"""Test addImages"""
		p = objListWindow()
		mtm = MyTableModel(p, ["a", "b"])
		qp = mtm.addImages([":/images/edit.png", ":/images/find.png"], 31)
		self.assertIsInstance(qp, QPixmap)
		self.assertEqual(qp.height(), 31)
		basepixm = QPixmap(96, 48)
		qpixm = QPixmap(":/images/edit.png")
		painter = QPainter(basepixm)
		with patch("physbiblio.gui.commonClasses.QPixmap",
					side_effect = [basepixm, qpixm, qpixm]) as _qpm,\
				patch("PySide2.QtGui.QPixmap.fill") as _fi,\
				patch("physbiblio.gui.commonClasses.QPainter",
					return_value = painter) as _qpai,\
				patch("PySide2.QtGui.QPainter.drawPixmap") as _drp:
			qp = mtm.addImages([":/images/edit.png", ":/images/find.png"], 31)
			_qpm.assert_has_calls([call(96, 48), call(":/images/edit.png"), call(":/images/find.png")])
			_fi.assert_called_once_with(Qt.transparent)
			_qpai.assert_called_once_with(basepixm)
			_drp.assert_has_calls([call(0, 0, qpixm), call(48, 0, qpixm)])
		self.assertFalse(mtm.painter.isActive())

	def test_rowCount(self):
		"""Test columnCount"""
		p = objListWindow()
		mtm = MyTableModel(p, ["a", "b"])
		self.assertEqual(mtm.rowCount(), 0)
		mtm.dataList = [{"a": 1, "b": 3}, {"a": 2, "b": 2}, {"a": 3, "b": 1}]
		self.assertEqual(mtm.rowCount(), 3)
		mtm = MyTableModel(p, 1)
		self.assertEqual(mtm.rowCount(), 0)

	def test_columnCount(self):
		"""Test columnCount"""
		p = objListWindow()
		mtm = MyTableModel(p, ["a", "b"])
		self.assertEqual(mtm.columnCount(), 2)
		self.assertEqual(mtm.columnCount(p), 2)
		mtm = MyTableModel(p, 1)
		self.assertEqual(mtm.columnCount(), 0)

	def test_data(self):
		"""Test that data is not implemented"""
		p = objListWindow()
		mtm = MyTableModel(p, ["a", "b"])
		self.assertRaises(NotImplementedError, lambda: mtm.data(1, 1))

	def test_flags(self):
		"""test flags"""
		idx = QModelIndex()
		p = objListWindow()
		mtm = MyTableModel(p, ["a", "b"])
		self.assertEqual(mtm.flags(idx), None)
		with patch("PySide2.QtCore.QModelIndex.isValid", return_value = True) as _iv:
			with patch("PySide2.QtCore.QModelIndex.column", return_value = 1) as _c:
				self.assertEqual(mtm.flags(idx), Qt.ItemIsEnabled | Qt.ItemIsSelectable)
			with patch("PySide2.QtCore.QModelIndex.column", return_value = 0) as _c:
				self.assertEqual(mtm.flags(idx), Qt.ItemIsEnabled | Qt.ItemIsSelectable)
			mtm.ask = True
			with patch("PySide2.QtCore.QModelIndex.column", return_value = 0) as _c:
				self.assertEqual(mtm.flags(idx), Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)

	def test_headerData(self):
		"""test headerData"""
		p = objListWindow()
		mtm = MyTableModel(p, ["a", "b"])
		self.assertEqual(mtm.headerData(0, Qt.Vertical, Qt.DisplayRole), None)
		self.assertEqual(mtm.headerData(0, Qt.Horizontal, Qt.EditRole), None)
		self.assertEqual(mtm.headerData(0, Qt.Horizontal, Qt.DisplayRole), "a")

	def test_setData(self):
		"""Test that setData is not implemented"""
		p = objListWindow()
		mtm = MyTableModel(p, ["a", "b"])
		self.assertRaises(NotImplementedError, lambda: mtm.setData(1, 1, 1))

	def test_sort(self):
		"""test sort function"""
		def setAbout(cl):
			cl.about = True
		def setChanged(cl):
			cl.changed = True
		p = objListWindow()
		mtm = MyTableModel(p, ["a", "b"])
		dl = [{"a": 1, "b": 3}, {"a": 2, "b": 2}, {"a": 3, "b": 1}]
		mtm.dataList = dl
		mtm.about = False
		mtm.changed = False
		mtm.layoutAboutToBeChanged.connect(lambda: setAbout(mtm))
		mtm.layoutChanged.connect(lambda: setChanged(mtm))
		self.assertFalse(mtm.about)
		self.assertFalse(mtm.changed)
		self.assert_in_stdout(mtm.sort, "Wrong column name in `sort`: '1'!")
		self.assertTrue(mtm.about)
		self.assertTrue(mtm.changed)
		self.assertEqual(mtm.dataList, dl)
		mtm.sort("b")
		self.assertEqual(mtm.dataList, [{"a": 3, "b": 1}, {"a": 2, "b": 2}, {"a": 1, "b": 3}])
		mtm.sort("b", Qt.DescendingOrder)
		self.assertEqual(mtm.dataList, dl)
		mtm.sort("a")
		self.assertEqual(mtm.dataList, dl)

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
		"""test the constructor"""
		with patch("physbiblio.gui.commonClasses.TreeModel._getRootNodes",
				return_value = "empty") as _gr:
			tm = TreeModel()
			_gr.assert_called_once()
		self.assertIsInstance(tm, QAbstractItemModel)
		self.assertEqual(tm.rootNodes, "empty")

	def test_getRootNodes(self):
		"""test the non implemented _getRootNodes"""
		self.assertRaises(NotImplementedError, lambda: TreeModel())
		with patch("physbiblio.gui.commonClasses.TreeModel._getRootNodes",
				return_value = "empty") as _gr:
			tm = TreeModel()
		self.assertRaises(NotImplementedError, lambda: tm._getRootNodes())

	def test_index(self):
		"""Test the function that returns the object index"""
		raise NotImplementedError()

	def test_parent(self):
		"""Test the function that returns the parent object"""
		raise NotImplementedError()

	def test_rowCount(self):
		"""test the counting of rows"""
		raise NotImplementedError()

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestNamedElement(GUITestCase):
	"""
	Test the NamedElement class
	"""
	def test_init(self):
		"""test the constructor"""
		with patch("physbiblio.gui.commonClasses.catString",
				return_value = "abcde") as _cs:
			ne = NamedElement(0, "main", ["a", "b"])
			_cs.assert_called_once_with(0, pBDB)
		self.assertEqual(ne.idCat, 0)
		self.assertEqual(ne.name, "main")
		self.assertEqual(ne.text, "abcde")
		self.assertEqual(ne.subelements, ["a", "b"])

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestNamedNode(GUITestCase):
	"""
	Test the NamedNode class
	"""
	def test_methods(self):
		"""test __init__ and _getChildren"""
		el = NamedElement(1, "tags", [])
		main = NamedElement(0, "main", [el])
		nn = NamedNode(main, None, 0)
		self.assertIsInstance(nn, TreeNode)
		with patch("physbiblio.gui.commonClasses.TreeNode.__init__", return_value = None) as _in:
			nn = NamedNode(main, None, 0)
			_in.assert_called_once_with(nn, None, 0)
		self.assertEqual(nn.element, main)
		with patch("physbiblio.gui.commonClasses.NamedNode.__init__", return_value = None) as _in:
			nn._getChildren()
			_in.assert_called_once_with(el, nn, 0)
		self.assertIsInstance(nn._getChildren(), list)
		self.assertEqual(len(nn._getChildren()), 1)
		self.assertIsInstance(nn._getChildren()[0], NamedNode)

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestLeafFilterProxyModel(GUITestCase):
	"""
	Test the LeafFilterProxyModel class
	"""
	def test_init(self):
		"""just check that the created object is an instance of parent class"""
		lf = LeafFilterProxyModel()
		self.assertIsInstance(lf, QSortFilterProxyModel)

	def test_filterAcceptsRow(self):
		"""Test filterAcceptsRow with all possible combinations"""
		lf = LeafFilterProxyModel()
		with patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.filterAcceptsRowItself",
					return_value = True) as _its, \
				patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.filterAcceptsAnyParent") as _par, \
				patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.hasAcceptedChildren") as _chi:
			self.assertTrue(lf.filterAcceptsRow(0, None))
			_its.assert_called_once_with(0, None)
			_par.assert_not_called()
			_chi.assert_not_called()
		with patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.filterAcceptsRowItself",
					return_value = False) as _its, \
				patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.filterAcceptsAnyParent",
					return_value = True) as _par, \
				patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.hasAcceptedChildren") as _chi:
			self.assertTrue(lf.filterAcceptsRow(0, None))
			_its.assert_called_once_with(0, None)
			_par.assert_called_once_with(None)
			_chi.assert_not_called()
		with patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.filterAcceptsRowItself",
					return_value = False) as _its, \
				patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.filterAcceptsAnyParent",
					return_value = False) as _par, \
				patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.hasAcceptedChildren",
					return_value = True) as _chi:
			self.assertTrue(lf.filterAcceptsRow(0, None))
			_its.assert_called_once_with(0, None)
			_par.assert_called_once_with(None)
			_chi.assert_called_once_with(0, None)
		with patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.filterAcceptsRowItself",
					return_value = False) as _its, \
				patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.filterAcceptsAnyParent",
					return_value = False) as _par, \
				patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.hasAcceptedChildren",
					return_value = False) as _chi:
			self.assertFalse(lf.filterAcceptsRow(0, None))
			_its.assert_called_once_with(0, None)
			_par.assert_called_once_with(None)
			_chi.assert_called_once_with(0, None)

	def test_filterAcceptRowItself(self):
		"""test filterAcceptRowItself"""
		lf = LeafFilterProxyModel()
		with patch("PySide2.QtCore.QSortFilterProxyModel.filterAcceptsRow",
				return_value = "testval") as _far:
			self.assertEqual(lf.filterAcceptsRowItself(0, "par"), "testval")
			_far.assert_called_once_with(0, "par")

	def test_filterAcceptsAnyParent(self):
		"""test filterAcceptsAnyParent"""
		el = NamedElement(1, "tags", [])
		main = NamedElement(0, "main", [el])
		lf = LeafFilterProxyModel()
		tm = emptyTreeModel([main])
		lf.setSourceModel(tm)
		self.assertTrue(lf.filterAcceptsAnyParent(lf.index(0,0,QModelIndex())))
		self.assertTrue(lf.filterAcceptsAnyParent(lf.index(1,0,QModelIndex())))
		self.assertFalse(lf.filterAcceptsAnyParent(lf.index(2,0,QModelIndex())))
		with patch("PySide2.QtCore.QModelIndex.isValid", side_effect=[True, True, False]) as _iv,\
				patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.filterAcceptsRowItself",
					return_value = False) as _its:
			self.assertFalse(lf.filterAcceptsAnyParent(lf.index(0,0,QModelIndex())))
			self.assertEqual(_iv.call_count, 3)
			self.assertEqual(_its.call_count, 2)
		with patch("PySide2.QtCore.QModelIndex.isValid", side_effect=[True, True, False]) as _iv,\
				patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.filterAcceptsRowItself",
					return_value = False) as _its,\
				patch("physbiblio.gui.commonClasses.QModelIndex.parent",
					return_value = QModelIndex()) as _pa:
			self.assertFalse(lf.filterAcceptsAnyParent(lf.index(0,0,QModelIndex())))
			self.assertEqual(_iv.call_count, 3)
			self.assertEqual(_its.call_count, 2)
			self.assertEqual(_pa.call_count, 4)
		with patch("PySide2.QtCore.QModelIndex.isValid", side_effect=[True, True, False]) as _iv,\
				patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.filterAcceptsRowItself",
					return_value = True) as _its:
			self.assertTrue(lf.filterAcceptsAnyParent(lf.index(0,0,QModelIndex())))
			self.assertEqual(_iv.call_count, 1)
			self.assertEqual(_its.call_count, 1)
		with patch("PySide2.QtCore.QModelIndex.isValid", side_effect=[True, True, False]) as _iv,\
				patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.filterAcceptsRowItself",
					return_value = True) as _its,\
				patch("physbiblio.gui.commonClasses.QModelIndex.parent") as _pa:
			self.assertTrue(lf.filterAcceptsAnyParent(lf.index(0,0,QModelIndex())))
			self.assertEqual(_iv.call_count, 1)
			self.assertEqual(_its.call_count, 1)
			self.assertEqual(_pa.call_count, 1)

	def test_hasAcceptedChildren(self):#probably could be improved a bit
		"""test hasAcceptedChildren"""
		el = NamedElement(1, "tags", [])
		main = NamedElement(0, "main", [el])
		lf = LeafFilterProxyModel()
		tm = emptyTreeModel([main])
		lf.setSourceModel(tm)
		self.assertTrue(lf.hasAcceptedChildren(0, QModelIndex()))
		with patch("physbiblio.gui.tests.test_commonClasses.emptyTreeModel.rowCount",
				return_value = 1) as _rc:
			self.assertTrue(lf.hasAcceptedChildren(1, QModelIndex()))
		with patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.filterAcceptsRow",
				return_value = True) as _acc:
			self.assertTrue(lf.hasAcceptedChildren(5, QModelIndex()))
			self.assertEqual(_acc.call_count, 1)
		with patch("physbiblio.gui.commonClasses.LeafFilterProxyModel.filterAcceptsRow",
				return_value = False) as _acc,\
				patch("physbiblio.gui.tests.test_commonClasses.emptyTreeModel.rowCount",
				return_value = 1) as _rc:
			self.assertFalse(lf.hasAcceptedChildren(1, QModelIndex()))

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestMyDDTableWidget(GUITestCase):
	"""
	Test the MyDDTableWidget class
	"""
	def test_init(self):
		"""test init"""
		mddtw = MyDDTableWidget("head")
		self.assertIsInstance(mddtw, QTableWidget)
		self.assertEqual(mddtw.columnCount(), 1)
		self.assertTrue(mddtw.dragEnabled())
		self.assertTrue(mddtw.acceptDrops())
		self.assertFalse(mddtw.dragDropOverwriteMode())
		self.assertEqual(mddtw.selectionBehavior(), QAbstractItemView.SelectRows)
		with patch("physbiblio.gui.commonClasses.QTableWidget.setHorizontalHeaderLabels") as _shl:
			mddtw = MyDDTableWidget("head")
			_shl.assert_called_once_with(["head"])

	def test_dropMimeData(self):
		"""test dropMimeData"""
		mddtw = MyDDTableWidget("head")
		self.assertTrue(mddtw.dropMimeData(12, 0, None, None))
		self.assertEqual(mddtw.last_drop_row, 12)

	def test_dropEvent(self):
		raise NotImplementedError()

	def test_getselectedRowsFast(self):
		"""test getselectedRowsFast"""
		mddtw = MyDDTableWidget("head")
		a = mddtw.getselectedRowsFast()
		self.assertEqual(a, [])
		with patch("PySide2.QtWidgets.QTableWidget.selectedItems",
					return_value = [QTableWidgetItem() for i in range(5)]) as _si,\
				patch("PySide2.QtWidgets.QTableWidgetItem.row",
					side_effect = [1, 8, 3, 1, 2]) as _r,\
				patch("PySide2.QtWidgets.QTableWidgetItem.text",
					side_effect = ["de", "fg", "ab", "hi", "bibkey"]) as _t:
			a = mddtw.getselectedRowsFast()
			self.assertEqual(a, [1, 3, 8])

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestMyMenu(GUITestCase):
	"""
	Test the MyMenu class
	"""
	def test_init(self):
		"""Test init"""
		mm = MyMenu()
		self.assertIsInstance(mm, QMenu)
		self.assertEqual(mm.possibleActions, [])
		self.assertFalse(mm.result)
		with patch("physbiblio.gui.commonClasses.QMenu.__init__") as _in:
			mm = MyMenu("abc")
			_in.assert_called_once_with("abc")

	def test_fillMenu(self):
		"""test fillMenu"""
		mm = MyMenu()
		acts = [
			QAction("test1"),
			"abc",
			QAction("test2"),
			None,
			["submenu", [
				QAction("Sub1"),
				QAction("Sub2"),
				["subsub", [
					QAction("nest")
					]
				],
				None
				]
			]
		]
		mm.possibleActions = acts
		mm.fillMenu()
		macts = mm.actions()
		self.assertEqual(acts[0], macts[0])
		self.assertEqual(acts[2], macts[1])
		self.assertTrue(macts[2].isSeparator())
		self.assertEqual(macts[0].menu(), None)
		self.assertEqual(macts[1].menu(), None)
		self.assertEqual(macts[2].menu(), None)
		self.assertIsInstance(macts[3].menu(), QMenu)
		subm = macts[3].menu()
		self.assertEqual(subm.title(), acts[4][0])
		sacts = subm.actions()
		self.assertEqual(acts[4][1][0], sacts[0])
		self.assertEqual(acts[4][1][1], sacts[1])
		self.assertIsInstance(sacts[2].menu(), QMenu)
		subsub = sacts[2].menu()
		self.assertEqual(subsub.title(), acts[4][1][2][0])
		self.assertEqual(subsub.actions()[0], acts[4][1][2][1][0])
		self.assertTrue(sacts[3].isSeparator())

	def test_keyPressEvent(self):
		"""test keyPressEvent"""
		mm = MyMenu()
		with patch("physbiblio.gui.commonClasses.QMenu.close") as _oc:
			QTest.keyPress(mm, "a")
			_oc.assert_not_called()
			QTest.keyPress(mm, Qt.Key_Enter)
			_oc.assert_not_called()
			QTest.keyPress(mm, Qt.Key_Escape)
			_oc.assert_called_once()

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestGuiViewEntry(GUITestCase):
	"""
	Test the GuiViewEntry class
	"""
	def test_methods(self):
		"""test that the object is instance of `viewEntry` and that openLink works"""
		gve = guiViewEntry()
		self.assertIsInstance(gve, viewEntry)
		self.assertIsInstance(pBGuiView, guiViewEntry)

		with patch("PySide2.QtGui.QDesktopServices.openUrl", return_value = True) as _ou,\
				patch("logging.Logger.debug") as _db:
			gve.openLink(["abc", "def"], "link")
			_db.assert_has_calls([
				call("Opening link 'abc' for entry 'abc' successful!"),
				call("Opening link 'def' for entry 'def' successful!"),
				])
			_ou.assert_has_calls([
				call(QUrl("abc")),
				call(QUrl("def"))
				])
		with patch("PySide2.QtGui.QDesktopServices.openUrl", return_value = False) as _ou,\
				patch("logging.Logger.warning") as _db:
			gve.openLink(["abc", "def"], "link")
			_db.assert_has_calls([
				call("Opening link for 'abc' failed!"),
				call("Opening link for 'def' failed!"),
				])
			_ou.assert_has_calls([
				call(QUrl("abc")),
				call(QUrl("def"))
				])
		with patch("PySide2.QtGui.QDesktopServices.openUrl", return_value = True) as _ou,\
				patch("physbiblio.view.viewEntry.getLink", return_value = "mylink") as _gl:
			gve.openLink("abc", arg = "somearg", fileArg = "somefilearg")
			_gl.assert_called_once_with("abc", arg = "somearg", fileArg = "somefilearg")
			_ou.assert_called_once_with(QUrl("mylink"))
		with patch("PySide2.QtGui.QDesktopServices.openUrl", return_value = True) as _ou,\
				patch("physbiblio.gui.commonClasses.QUrl.fromLocalFile",
					return_value = QUrl("mylink")) as _fl:
			gve.openLink("abc", arg = "file", fileArg = "/a/b/c")
			_fl.assert_called_once_with("/a/b/c")
			_ou.assert_called_once_with(QUrl("mylink"))

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestMyImportedTableModel(GUITestCase):
	"""
	Test the MyImportedTableModel class
	"""
	def test_init(self):
		"""test init"""
		with patch("physbiblio.gui.commonClasses.MyTableModel.prepareSelected") as _ps:
			mitm = MyImportedTableModel(QWidget(),
				{
				"a": {"exist": False, "bibpars": {"ID": "a"}},
				"b": {"exist": False, "bibpars": {"ID": "b"}},
				},
				["key", "id"],
				"bibkey")
			_ps.assert_called_once()
		self.assertIsInstance(mitm, MyTableModel)
		self.assertEqual(mitm.typeClass, "imports")
		self.assertEqual(mitm.idName, "bibkey")
		self.assertEqual(mitm.bibsOrder, ["a", "b"])
		self.assertEqual(mitm.dataList, [{"ID": "a"}, {"ID": "b"}])
		self.assertEqual(mitm.existList, [False, False])

	def test_getIdentifier(self):
		"""test getIdentifier"""
		mitm = MyImportedTableModel(QWidget(),
			{
			"a": {"exist": False, "bibpars": {"ID": "a"}},
			"b": {"exist": False, "bibpars": {"ID": "b"}},
			},
			["key", "id"])
		self.assertEqual(mitm.getIdentifier(
			{"id": "a", "bibkey": "b", "ID": "i"}),
			"i")

	def test_data(self):
		"""test data"""
		mitm = MyImportedTableModel(QWidget(),
			{
			"a": {"exist": False, "bibpars": {"ID": "a", "key": "a"}},
			"b": {"exist": False, "bibpars": {"ID": "b", "key": "b"}},
			},
			["key", "ID"])
		with patch("PySide2.QtCore.QModelIndex.isValid",
				return_value = False) as _iv:
			self.assertEqual(mitm.data(QModelIndex(), Qt.DisplayRole), None)
		with patch("PySide2.QtCore.QModelIndex.isValid",
				return_value = True) as _iv:
			with patch("PySide2.QtCore.QModelIndex.column",
						return_value = 10) as _c,\
					patch("PySide2.QtCore.QModelIndex.row",
						return_value = 10) as _r:
				self.assertEqual(mitm.data(QModelIndex(), Qt.DisplayRole), None)
			with patch("PySide2.QtCore.QModelIndex.column",
						return_value = 0) as _c,\
					patch("PySide2.QtCore.QModelIndex.row",
						return_value = 0) as _r:
				self.assertEqual(mitm.data(QModelIndex(), Qt.CheckStateRole),
					Qt.Unchecked)
				self.assertTrue(mitm.setData(QModelIndex(), Qt.Checked, Qt.CheckStateRole))
				self.assertEqual(mitm.data(QModelIndex(), Qt.CheckStateRole),
					Qt.Checked)
			with patch("PySide2.QtCore.QModelIndex.column",
						return_value = 0) as _c,\
					patch("PySide2.QtCore.QModelIndex.row",
						return_value = 0) as _r:
				mitm.existList[0] = True
				self.assertEqual(mitm.data(QModelIndex(), Qt.EditRole),
					"a - already existing")
				self.assertEqual(mitm.data(QModelIndex(), Qt.DisplayRole),
					"a - already existing")
				self.assertEqual(mitm.data(QModelIndex(), Qt.CheckStateRole),
					None)
			with patch("PySide2.QtCore.QModelIndex.column",
						return_value = 1) as _c,\
					patch("PySide2.QtCore.QModelIndex.row",
						return_value = 0) as _r:
				self.assertEqual(mitm.data(QModelIndex(), Qt.EditRole),
					"a")
				self.assertEqual(mitm.data(QModelIndex(), Qt.DisplayRole),
					"a")
				self.assertEqual(mitm.data(QModelIndex(), Qt.CheckStateRole),
					None)

	def test_setData(self):
		"""test setData"""
		mitm = MyImportedTableModel(QWidget(),
			{
			"a": {"exist": False, "bibpars": {"ID": "a"}},
			"b": {"exist": False, "bibpars": {"ID": "b"}},
			},
			["key", "id"])
		mitm.dataChanged.connect(fakeExec_dataChanged)
		ids = {"a": False, "b": False}
		with patch("PySide2.QtCore.QModelIndex.isValid",
				return_value = True) as _iv:
			self.assertTrue(mitm.setData(QModelIndex(), "abc", Qt.DisplayRole))
			self.assertEqual(ids, mitm.selectedElements)
			with patch("PySide2.QtCore.QModelIndex.column",
					return_value = 1) as _c:
				self.assertTrue(mitm.setData(QModelIndex(), "abc", Qt.CheckStateRole))
				self.assertEqual(ids, mitm.selectedElements)
			with patch("PySide2.QtCore.QModelIndex.column",
						return_value = 0) as _c,\
					patch("PySide2.QtCore.QModelIndex.row",
						return_value = 0) as _r:
				self.assertTrue(mitm.setData(QModelIndex(), Qt.Checked, Qt.CheckStateRole))
				self.assertEqual({"a": True, "b": False}, mitm.selectedElements)
				self.assertTrue(mitm.setData(QModelIndex(), Qt.Unchecked, Qt.CheckStateRole))
				self.assertEqual({"a": False, "b": False}, mitm.selectedElements)
				self.assertTrue(mitm.setData(QModelIndex(), Qt.Checked, Qt.CheckStateRole))
				self.assertEqual({"a": True, "b": False}, mitm.selectedElements)
				self.assertTrue(mitm.setData(QModelIndex(), "abc", Qt.CheckStateRole))
				self.assertEqual({"a": False, "b": False}, mitm.selectedElements)
		with patch("PySide2.QtCore.QModelIndex.isValid",
				return_value = False) as _iv:
			self.assertFalse(mitm.setData(QModelIndex(), Qt.Checked, Qt.DisplayRole))

	def test_flags(self):
		"""test flags"""
		mitm = MyImportedTableModel(QWidget(),
			{
			"a": {"exist": False, "bibpars": {"ID": "a"}},
			"b": {"exist": True, "bibpars": {"ID": "b"}},
			},
			["key", "id"])
		with patch("PySide2.QtCore.QModelIndex.isValid",
				return_value = False) as _iv:
			self.assertEqual(mitm.flags(QModelIndex()), None)
		with patch("PySide2.QtCore.QModelIndex.isValid",
				return_value = True) as _iv,\
				patch("PySide2.QtCore.QModelIndex.column",
					return_value = 1) as _c,\
				patch("PySide2.QtCore.QModelIndex.row",
					side_effect = [0, 1]) as _r:
			self.assertEqual(mitm.flags(QModelIndex()),
				Qt.ItemIsEnabled | Qt.ItemIsSelectable)
			self.assertEqual(mitm.flags(QModelIndex()),
				Qt.ItemIsEnabled | Qt.ItemIsSelectable)
		with patch("PySide2.QtCore.QModelIndex.isValid",
				return_value = True) as _iv,\
				patch("PySide2.QtCore.QModelIndex.column",
					return_value = 0) as _c,\
				patch("PySide2.QtCore.QModelIndex.row",
					side_effect = [0, 1]) as _r:
			self.assertEqual(mitm.flags(QModelIndex()),
				Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
			self.assertEqual(mitm.flags(QModelIndex()),
				Qt.ItemIsEnabled | Qt.ItemIsSelectable)

if __name__=='__main__':
	unittest.main()