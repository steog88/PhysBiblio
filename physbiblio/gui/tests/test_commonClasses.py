#!/usr/bin/env python
"""Test file for the physbiblio.gui.commonClasses module.

This file is part of the physbiblio package.
"""
import os
import sys
import time
import traceback

from PySide2.QtCore import (
    QByteArray,
    QItemSelectionModel,
    QMimeData,
    QModelIndex,
    QPoint,
    QPointF,
    QRect,
    Qt,
)
from PySide2.QtGui import QContextMenuEvent, QDropEvent
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QAction, QInputDialog, QLineEdit, QWidget

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import call, patch
    from Queue import Queue
else:
    import unittest
    from queue import Queue
    from unittest.mock import call, patch

try:
    from physbiblio.database import pBDB
    from physbiblio.gui.commonClasses import *
    from physbiblio.gui.setuptests import *
    from physbiblio.setuptests import *
except ImportError:
    print("Could not find physbiblio and its modules!")
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


class EmptyTableModel(QAbstractTableModel):
    """Used to do tests when a table model is needed"""

    def __init__(self, *args):
        QAbstractTableModel.__init__(self, *args)
        self.header = []

    def rowCount(self, a=None):
        return 1

    def columnCount(self, a=None):
        return 1

    def data(self, index, role):
        return None


class EmptyTreeModel(TreeModel):
    """Used to do tests when a tree model is needed"""

    def __init__(self, elements, *args):
        self.rootElements = elements
        TreeModel.__init__(self, *args)

    def _getRootNodes(self):
        return [
            NamedNode(elem, None, index) for index, elem in enumerate(self.rootElements)
        ]

    def columnCount(self, a=None):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole and index.column() == 0:
            return TreeNode.cast(index).element.text
        return None


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestPBDialog(GUITestCase):
    """Test the PBDialog class"""

    def test_centerWindow(self):
        """test centerWindow"""
        p = PBDialog()
        with patch(
            "PySide2.QtWidgets.QDialog.frameGeometry",
            autospec=True,
            return_value=QRect(),
        ) as _fg, patch(
            "PySide2.QtCore.QRect.center", autospec=True, return_value=QPoint()
        ) as _ce, patch(
            "PySide2.QtCore.QRect.moveCenter", autospec=True
        ) as _mc, patch(
            "PySide2.QtCore.QRect.topLeft", autospec=True, return_value=QPoint()
        ) as _tl, patch(
            "PySide2.QtWidgets.QDialog.move", autospec=True
        ) as _mo:
            p.centerWindow()
            self.assertEqual(_fg.call_count, 1)
            self.assertEqual(_ce.call_count, 1)
            self.assertEqual(_mc.call_count, 1)
            self.assertEqual(_tl.call_count, 1)
            self.assertEqual(_mo.call_count, 1)

    def test_cleanLayout(self):
        """Test cleanLayout"""
        p = PBDialog()
        p.currLayout = QGridLayout()
        p.setLayout(p.currLayout)
        p.layout().addWidget(QLabel("empty"))
        p.layout().addWidget(QLabel("empty1"))
        self.assertEqual(p.layout().count(), 2)
        p.cleanLayout()
        self.assertEqual(p.layout().count(), 0)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestLabels(GUITestCase):
    """Test the PBLabelRight and PBLabelCenter classes"""

    def test_myLabel(self):
        """Test PBLabel"""
        l = PBLabel("label")
        self.assertIsInstance(l, QLabel)
        self.assertEqual(l.text(), "label")
        self.assertEqual(
            l.textInteractionFlags(),
            Qt.LinksAccessibleByMouse | Qt.TextSelectableByMouse,
        )
        self.assertEqual(l.textFormat(), Qt.RichText)
        self.assertEqual(l.openExternalLinks(), True)

    def test_myLabelRight(self):
        """Test PBLabelRight"""
        l = PBLabelRight("label")
        self.assertIsInstance(l, QLabel)
        self.assertEqual(l.text(), "label")
        self.assertEqual(l.alignment(), Qt.AlignRight | Qt.AlignVCenter)

    def test_myLabelCenter(self):
        """Test PBLabelCenter"""
        l = PBLabelCenter("label")
        self.assertIsInstance(l, QLabel)
        self.assertEqual(l.text(), "label")
        self.assertEqual(l.alignment(), Qt.AlignCenter | Qt.AlignVCenter)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestPBComboBox(GUITestCase):
    """Test the PBComboBox class"""

    def test_init(self):
        """test the constructor"""
        ew = QWidget()
        mb = PBComboBox(ew, [])
        self.assertIsInstance(mb, QComboBox)
        self.assertEqual(mb.parentWidget(), ew)
        self.assertEqual(mb.itemText(0), "")
        mb = PBComboBox(ew, ["1", "2"])
        self.assertEqual(mb.itemText(0), "1")
        self.assertEqual(mb.itemText(1), "2")
        self.assertEqual(mb.itemText(2), "")
        self.assertEqual(mb.currentText(), "1")
        mb = PBComboBox(ew, ["1", "2"], "0")
        self.assertEqual(mb.currentText(), "1")
        mb = PBComboBox(ew, ["1", "2"], "2")
        self.assertEqual(mb.currentText(), "2")
        mb = PBComboBox(ew, [1, 2])
        self.assertEqual(mb.itemText(0), "1")
        self.assertEqual(mb.itemText(1), "2")
        self.assertEqual(mb.itemText(2), "")


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestPBAndOrCombo(GUITestCase):
    """Test the PBAndOrCombo class"""

    def test_init(self):
        """test the constructor"""
        mb = PBAndOrCombo(None)
        self.assertIsInstance(mb, PBComboBox)
        self.assertIsInstance(mb, QComboBox)
        self.assertEqual(mb.parentWidget(), None)
        self.assertEqual(mb.itemText(0), "AND")
        self.assertEqual(mb.itemText(1), "OR")
        self.assertEqual(mb.itemText(2), "")
        self.assertEqual(mb.currentText(), "AND")
        mb = PBAndOrCombo(None, "or")
        self.assertEqual(mb.currentText(), "AND")
        ew = QWidget()
        mb = PBAndOrCombo(ew, "OR")
        self.assertEqual(mb.parentWidget(), ew)
        self.assertEqual(mb.currentText(), "OR")


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestPBTrueFalseCombo(GUITestCase):
    """Test the PBTrueFalseCombo class"""

    def test_init(self):
        """test the constructor"""
        mb = PBTrueFalseCombo(None)
        self.assertIsInstance(mb, PBComboBox)
        self.assertIsInstance(mb, QComboBox)
        self.assertEqual(mb.parentWidget(), None)
        self.assertEqual(mb.itemText(0), "True")
        self.assertEqual(mb.itemText(1), "False")
        self.assertEqual(mb.itemText(2), "")
        self.assertEqual(mb.currentText(), "True")
        mb = PBTrueFalseCombo(None, "abc")
        self.assertEqual(mb.currentText(), "True")
        ew = QWidget()
        mb = PBTrueFalseCombo(ew, "False")
        self.assertEqual(mb.parentWidget(), ew)
        self.assertEqual(mb.currentText(), "False")


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestObjListWindow(GUITestCase):
    """Test the ObjListWindow class"""

    def test_init(self):
        """test the __init__ function"""
        olw = ObjListWindow()
        self.assertIsInstance(olw, QDialog)
        self.assertEqual(olw.tableWidth, None)
        self.assertEqual(olw.proxyModel, None)
        self.assertFalse(olw.gridLayout)
        self.assertIsInstance(olw.currLayout, QVBoxLayout)
        self.assertEqual(olw.layout(), olw.currLayout)

        olw = ObjListWindow(gridLayout=True)
        self.assertTrue(olw.gridLayout)
        self.assertIsInstance(olw.currLayout, QGridLayout)
        self.assertEqual(olw.layout(), olw.currLayout)

    def test_NI(self):
        """Test the non implemented functions (must be subclassed!)"""
        olw = ObjListWindow()
        ix = QModelIndex()
        self.assertRaises(NotImplementedError, lambda: olw.createTable())
        self.assertRaises(NotImplementedError, lambda: olw.cellClick(ix))
        self.assertRaises(NotImplementedError, lambda: olw.cellDoubleClick(ix))
        self.assertRaises(NotImplementedError, lambda: olw.handleItemEntered(ix))
        self.assertRaises(
            NotImplementedError, lambda: olw.triggeredContextMenuEvent(0, 0, ix)
        )

    def test_changeFilter(self):
        """test changeFilter"""
        olw = ObjListWindow()
        olw.tableModel = EmptyTableModel()
        olw.setProxyStuff(1, Qt.AscendingOrder)
        olw.changeFilter("abc")
        self.assertEqual(olw.proxyModel.filterRegExp().pattern(), "abc")
        olw.changeFilter(123)
        self.assertEqual(olw.proxyModel.filterRegExp().pattern(), "123")

    def test_addFilterInput(self):
        """test addFilterInput"""
        olw = ObjListWindow()
        olw.addFilterInput("plch")
        self.assertIsInstance(olw.filterInput, QLineEdit)
        self.assertEqual(olw.filterInput.placeholderText(), "plch")
        with patch(
            "physbiblio.gui.commonClasses.ObjListWindow.changeFilter", autospec=True
        ) as _cf:
            olw.filterInput.textChanged.emit("sss")
            _cf.assert_called_once_with(olw, "sss")

        olw = ObjListWindow(gridLayout=True)
        olw.addFilterInput("plch", gridPos=(4, 1))
        self.assertEqual(olw.layout().itemAtPosition(4, 1).widget(), olw.filterInput)

    def test_setProxyStuff(self):
        """test setProxyStuff"""
        olw = ObjListWindow()
        olw.tableModel = EmptyTableModel()
        with patch(
            "PySide2.QtWidgets.QTableView.sortByColumn", autospec=True
        ) as _st, patch(
            "PySide2.QtCore.QSortFilterProxyModel.sort", autospec=True
        ) as _sf:
            olw.setProxyStuff(1, Qt.AscendingOrder)
            _st.assert_called_once_with(1, Qt.AscendingOrder)
            _sf.assert_called_once_with(1, Qt.AscendingOrder)
        self.assertIsInstance(olw.proxyModel, QSortFilterProxyModel)
        self.assertEqual(olw.proxyModel.filterCaseSensitivity(), Qt.CaseInsensitive)
        self.assertEqual(olw.proxyModel.sortCaseSensitivity(), Qt.CaseInsensitive)
        self.assertEqual(olw.proxyModel.filterKeyColumn(), -1)

        self.assertIsInstance(olw.tableview, PBTableView)
        self.assertEqual(olw.tableview.model(), olw.proxyModel)
        self.assertTrue(olw.tableview.isSortingEnabled())
        self.assertTrue(olw.tableview.hasMouseTracking())
        self.assertTrue(olw.tableview.selectionBehavior(), QAbstractItemView.SelectRows)
        self.assertEqual(olw.layout().itemAt(0).widget(), olw.tableview)

    def test_finalizeTable(self):
        """Test finalizeTable"""
        olw = ObjListWindow()
        olw.tableModel = EmptyTableModel()
        with patch("PySide2.QtCore.QSortFilterProxyModel.sort", autospec=True) as _s:
            olw.setProxyStuff(1, Qt.AscendingOrder)
        with patch(
            "PySide2.QtWidgets.QTableView.resizeColumnsToContents", autospec=True
        ) as _rc, patch(
            "PySide2.QtWidgets.QTableView.resizeRowsToContents", autospec=True
        ) as _rr:
            olw.finalizeTable()
            _rc.assert_has_calls([call(), call()])
            self.assertEqual(_rr.call_count, 1)
        self.assertIsInstance(olw.tableview, PBTableView)
        maxw = QGuiApplication.primaryScreen().availableGeometry().width()
        self.assertEqual(
            olw.maximumHeight(),
            QGuiApplication.primaryScreen().availableGeometry().height(),
        )
        self.assertEqual(olw.maximumWidth(), maxw)
        hwidth = olw.tableview.horizontalHeader().length()
        swidth = olw.tableview.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        fwidth = olw.tableview.frameWidth() * 2

        if hwidth > maxw - (swidth + fwidth):
            tW = maxw - (swidth + fwidth)
        else:
            tW = hwidth + swidth + fwidth
        self.assertEqual(olw.tableview.width(), tW)
        self.assertEqual(olw.minimumHeight(), 600)
        ix = QModelIndex()
        with patch(
            "physbiblio.gui.commonClasses.ObjListWindow.handleItemEntered",
            autospec=True,
        ) as _f:
            olw.tableview.entered.emit(ix)
            _f.assert_called_once_with(olw, ix)
        with patch(
            "physbiblio.gui.commonClasses.ObjListWindow.cellClick", autospec=True
        ) as _f:
            olw.tableview.clicked.emit(ix)
            _f.assert_called_once_with(olw, ix)
        with patch(
            "physbiblio.gui.commonClasses.ObjListWindow.cellDoubleClick", autospec=True
        ) as _f:
            olw.tableview.doubleClicked.emit(ix)
            _f.assert_called_once_with(olw, ix)
        self.assertEqual(olw.layout().itemAt(0).widget(), olw.tableview)

        olw = ObjListWindow(gridLayout=True)
        olw.tableModel = EmptyTableModel()
        with patch("PySide2.QtCore.QSortFilterProxyModel.sort", autospec=True) as _s:
            olw.setProxyStuff(1, Qt.AscendingOrder)
        olw.finalizeTable(gridPos=(4, 1))
        self.assertEqual(olw.layout().itemAtPosition(4, 1).widget(), olw.tableview)

    def test_recreateTable(self):
        """Test recreateTable"""
        olw = ObjListWindow()
        with patch(
            "physbiblio.gui.commonClasses.ObjListWindow.cleanLayout", autospec=True
        ) as _cl, patch(
            "physbiblio.gui.commonClasses.ObjListWindow.createTable", autospec=True
        ) as _ct:
            olw.recreateTable()
            self.assertEqual(_cl.call_count, 1)
            self.assertEqual(_ct.call_count, 1)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestEditObjectWindow(GUITestCase):
    """Test the EditObjectWindow class"""

    def test_init(self):
        """test constructor"""
        ew = QWidget()
        with patch(
            "physbiblio.gui.commonClasses.EditObjectWindow.initUI", autospec=True
        ) as _iu:
            eow = EditObjectWindow(ew)
            self.assertEqual(eow.parent(), ew)
            self.assertEqual(eow.textValues, {})
            _iu.assert_called_once_with(eow)

    def test_keyPressEvent(self):
        """test keyPressEvent"""
        eow = EditObjectWindow()
        w = QLineEdit()
        eow.currGrid.addWidget(w, 0, 0)
        with patch(
            "physbiblio.gui.commonClasses.EditObjectWindow.onCancel", autospec=True
        ) as _oc:
            QTest.keyPress(w, "a")
            _oc.assert_not_called()
            QTest.keyPress(w, Qt.Key_Enter)
            _oc.assert_not_called()
            QTest.keyPress(w, Qt.Key_Escape)
            self.assertEqual(_oc.call_count, 1)

    def test_onCancel(self):
        """test onCancel"""
        eow = EditObjectWindow()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            eow.onCancel()
            self.assertFalse(eow.result)
            self.assertEqual(_c.call_count, 1)

    def test_onOk(self):
        """test onOk"""
        eow = EditObjectWindow()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            eow.onOk()
            self.assertTrue(eow.result)
            self.assertEqual(_c.call_count, 1)

    def test_initUI(self):
        """test initUI"""
        with patch(
            "physbiblio.gui.commonClasses.EditObjectWindow.initUI", autospec=True
        ) as _iu:
            eow = EditObjectWindow()
        self.assertEqual(eow.currGrid, None)
        eow = EditObjectWindow()
        self.assertIsInstance(eow.currGrid, QGridLayout)
        self.assertEqual(eow.layout(), eow.currGrid)
        self.assertEqual(eow.currGrid.spacing(), 1)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestPBThread(GUITestCase):
    """Test the PBThread class"""

    def test_methods(self):
        """test all the methods in the class"""
        with patch("PySide2.QtCore.QThread.__init__", autospec=True) as _in:
            PBThread()
            self.assertEqual(_in.call_count, 1)
        mt = PBThread()
        self.assertIsInstance(mt, QThread)
        self.assertRaises(NotImplementedError, lambda: mt.run())
        self.assertRaises(NotImplementedError, lambda: mt.setStopFlag())
        self.assertIsInstance(mt.finished, Signal)
        with patch("time.sleep", autospec=True) as _sl, patch(
            "PySide2.QtCore.QThread.start", autospec=True
        ) as _st:
            mt.start()
            _sl.assert_called_once_with(0.3)
            _st.assert_called_once_with(mt)
            _st.reset_mock()
            mt.start(1, a="try")
            _st.assert_called_once_with(mt, 1, a="try")


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestWriteStream(GUITestCase):
    """Test the WriteStream class"""

    def test_methods(self):
        """Test __init__, write, run methods"""
        queue = Queue()
        ws = WriteStream(queue)
        self.assertIsInstance(ws, PBThread)
        self.assertEqual(ws.queue, queue)
        self.assertTrue(ws.running)
        self.assertEqual(ws.parent(), None)
        self.assertIsInstance(ws.newText, Signal)
        self.assertIsInstance(ws.finished, Signal)
        ew = QWidget()
        ws = WriteStream(queue, parent=ew)
        self.assertEqual(ws.parent(), ew)
        ws.finished.connect(lambda: fakeExec_writeStream_fin(ws))
        if sys.version_info[0] < 3:
            package = "Queue"
        else:
            package = "queue"
        with patch(package + ".Queue.put", autospec=True) as _put:
            ws.write("abc")
            _put.assert_called_once_with(queue, "abc")
        with patch(package + ".Queue.get", return_value="abc", autospec=True) as _get:
            ws.newText.connect(lambda x: fakeExec_writeStream_mys(ws, x))
            ws.run()
            self.assertEqual(_get.call_count, 334)
            _get.assert_any_call(ws.queue, timeout=0.2)
            self.assertEqual(ws.text, "abc" * _get.call_count)
            self.assertTrue(ws.fin)

            _get.reset_mock()
            _get.return_value = "abcde" * 100
            ws.running = True
            ws.run()
            self.assertEqual(_get.call_count, 3)
            _get.assert_any_call(ws.queue, timeout=0.2)
            self.assertEqual(ws.text, "abcde" * 100 * _get.call_count)
            self.assertTrue(ws.fin)

            _get.reset_mock()
            _get.return_value = "abcde" * 201
            ws.running = True
            ws.run()
            self.assertEqual(_get.call_count, 1)
            _get.assert_any_call(ws.queue, timeout=0.2)
            self.assertEqual(ws.text, "abcde" * 201)

            _get.reset_mock()

            def getWait(x, timeout=0.2):
                time.sleep(timeout / 5.0)
                return "abcde"

            _get.side_effect = getWait
            ws.running = True
            ws.run()
            self.assertEqual(_get.call_count, 3)
            _get.assert_any_call(ws.queue, timeout=0.2)
            self.assertEqual(ws.text, "abcde" * 3)

            _get.reset_mock()
            self.a = 0

            def getWaitLong(ws, timeout=0.2):
                self.a += 1
                time.sleep(timeout)
                if self.a > 2:
                    return "abcde"
                else:
                    return ""

            _get.side_effect = getWaitLong
            ws.running = True
            ws.run()
            self.assertEqual(_get.call_count, 3)
            _get.assert_any_call(ws.queue, timeout=0.2)
            self.assertEqual(ws.text, "abcde")

            _get.reset_mock()
            self.a = 0

            def getWaitEmpty(q, timeout=0.2):
                self.a += 1
                time.sleep(timeout / 21.0)
                if self.a > 4:
                    ws.running = False
                    return ""
                else:
                    return "a"

            _get.side_effect = getWaitEmpty
            ws.running = True
            ws.run()
            self.assertEqual(_get.call_count, 5)
            _get.assert_any_call(ws.queue, timeout=0.2)
            self.assertEqual(ws.text, "aaaa")
        ws.running = False


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestPBTableView(GUITestCase):
    """Test the PBTableView class"""

    def test_methods(self):
        """Test __init__, contextMenuEvent methods"""
        p = ObjListWindow()
        mtw = PBTableView(p)
        self.assertIsInstance(mtw, QTableView)
        self.assertEqual(mtw.parent(), p)
        e = QContextMenuEvent(QContextMenuEvent.Mouse, QPoint())
        with patch(
            "PySide2.QtGui.QContextMenuEvent.x", return_value=12, autospec=True
        ) as _x, patch(
            "PySide2.QtGui.QContextMenuEvent.y", return_value=24, autospec=True
        ) as _y, patch(
            "PySide2.QtWidgets.QTableView.rowAt", return_value=0, autospec=True
        ) as _r, patch(
            "PySide2.QtWidgets.QTableView.columnAt", return_value=1, autospec=True
        ) as _c, patch(
            "physbiblio.gui.commonClasses.ObjListWindow.triggeredContextMenuEvent",
            autospec=True,
        ) as _t:
            mtw.contextMenuEvent(e)
            _x.assert_called_once_with()
            _y.assert_called_once_with()
            _r.assert_called_once_with(24)
            _c.assert_called_once_with(12)
            _t.assert_called_once_with(p, 0, 1, e)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestPBTableModel(GUITestCase):
    """Test the PBTableModel class"""

    def test_init(self):
        """test constructor"""
        p = ObjListWindow()
        mtm = PBTableModel(p, ["a", "b"])
        self.assertIsInstance(mtm, QAbstractTableModel)
        self.assertEqual(mtm.header, ["a", "b"])
        self.assertEqual(mtm.parentObj, p)
        self.assertEqual(mtm.previous, [])
        self.assertFalse(mtm.ask)
        mtm = PBTableModel(p, ["a", "b"], ask=True, previous=[1])
        self.assertEqual(mtm.previous, [1])
        self.assertTrue(mtm.ask)

    def test_changeAsk(self):
        """Test changeAsk"""

        def setAbout(cl):
            cl.about = True

        def setChanged(cl):
            cl.changed = True

        p = ObjListWindow()
        mtm = PBTableModel(p, ["a", "b"])
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
        mtm.changeAsk("a")  # does nothing
        self.assertTrue(mtm.ask)

    def test_getIdentifier(self):
        """Test that getIdentifier is not implemented"""
        p = ObjListWindow()
        mtm = PBTableModel(p, ["a", "b"])
        self.assertRaises(NotImplementedError, lambda: mtm.getIdentifier("a"))

    def test_prepareSelected(self):
        """test prepareSelected"""

        def setAbout(cl):
            cl.about = True

        def setChanged(cl):
            cl.changed = True

        p = ObjListWindow()
        mtm = PBTableModel(p, ["a", "b"])
        mtm.dataList = [{"a": 1, "b": 3}, {"a": 2, "b": 2}, {"a": 3, "b": 1}]
        mtm.about = False
        mtm.changed = False
        mtm.layoutAboutToBeChanged.connect(lambda: setAbout(mtm))
        mtm.layoutChanged.connect(lambda: setChanged(mtm))
        self.assertFalse(mtm.about)
        self.assertFalse(mtm.changed)
        with patch(
            "physbiblio.gui.commonClasses.PBTableModel.getIdentifier",
            side_effect=[0, 1, 2],
            autospec=True,
        ) as _gi:
            mtm.prepareSelected()
            _gi.assert_has_calls(
                [
                    call(mtm, {"a": 1, "b": 3}),
                    call(mtm, {"a": 2, "b": 2}),
                    call(mtm, {"a": 3, "b": 1}),
                ]
            )
        self.assertEqual(mtm.selectedElements, {0: False, 1: False, 2: False})
        mtm = PBTableModel(p, ["a", "b"], previous=[2])
        mtm.dataList = [{"a": 1, "b": 3}, {"a": 2, "b": 2}, {"a": 3, "b": 1}]
        with patch(
            "physbiblio.gui.commonClasses.PBTableModel.getIdentifier",
            side_effect=[0, 1, 2],
            autospec=True,
        ) as _gi:
            mtm.prepareSelected()
            _gi.assert_has_calls(
                [
                    call(mtm, {"a": 1, "b": 3}),
                    call(mtm, {"a": 2, "b": 2}),
                    call(mtm, {"a": 3, "b": 1}),
                ]
            )
        self.assertEqual(mtm.selectedElements, {0: False, 1: False, 2: True})
        mtm = PBTableModel(p, ["a", "b"], previous=[1, 5])
        mtm.dataList = [{"a": 1, "b": 3}, {"a": 2, "b": 2}, {"a": 3, "b": 1}]
        with patch(
            "physbiblio.gui.commonClasses.PBTableModel.getIdentifier",
            side_effect=[0, 1, 2],
            autospec=True,
        ) as _gi, patch("logging.Logger.exception") as _ex:
            mtm.prepareSelected()
            _ex.assert_called_once_with("Invalid identifier in previous selection: 5")
            _gi.assert_has_calls(
                [
                    call(mtm, {"a": 1, "b": 3}),
                    call(mtm, {"a": 2, "b": 2}),
                    call(mtm, {"a": 3, "b": 1}),
                ]
            )
        self.assertEqual(mtm.selectedElements, {0: False, 1: True, 2: False})
        mtm = PBTableModel(p, ["a", "b"])
        with patch(
            "physbiblio.gui.commonClasses.PBTableModel.getIdentifier",
            side_effect=[0, 1, 2],
            autospec=True,
        ) as _gi, patch("logging.Logger.exception") as _ex:
            mtm.prepareSelected()
            _ex.assert_called_once_with("dataList is not defined!")
            _gi.assert_not_called()
        self.assertEqual(mtm.selectedElements, {})

    def test_un_selectAll(self):
        """test selectAll and unselectAll"""

        def setAbout(cl):
            cl.about = True

        def setChanged(cl):
            cl.changed = True

        p = ObjListWindow()
        mtm = PBTableModel(p, ["a", "b"])
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
        p = ObjListWindow()
        mtm = PBTableModel(p, ["a", "b"])
        img = mtm.addImage(":/images/edit.png", 51)
        self.assertIsInstance(img, QPixmap)
        self.assertEqual(img.height(), 51)
        img = mtm.addImage(":/images/nonexistent", 51)
        self.assertTrue(img.isNull())

    def test_addImages(self):
        """Test addImages"""
        p = ObjListWindow()
        mtm = PBTableModel(p, ["a", "b"])
        qp = mtm.addImages([":/images/edit.png", ":/images/find.png"], 31)
        self.assertIsInstance(qp, QPixmap)
        self.assertEqual(qp.height(), 31)
        basepixm = QPixmap(96, 48)
        qpixm = QPixmap(":/images/edit.png")
        painter = QPainter(basepixm)
        with patch(
            "physbiblio.gui.commonClasses.QPixmap",
            side_effect=[basepixm, qpixm, qpixm],
            autospec=True,
        ) as _qpm, patch("PySide2.QtGui.QPixmap.fill", autospec=True) as _fi, patch(
            "physbiblio.gui.commonClasses.QPainter", return_value=painter, autospec=True
        ) as _qpai, patch(
            "PySide2.QtGui.QPainter.drawPixmap", autospec=True
        ) as _drp:
            qp = mtm.addImages([":/images/edit.png", ":/images/find.png"], 31)
            _qpm.assert_has_calls(
                [call(96, 48), call(":/images/edit.png"), call(":/images/find.png")]
            )
            _fi.assert_called_once_with(Qt.transparent)
            _qpai.assert_called_once_with(basepixm)
            _drp.assert_has_calls([call(0, 0, qpixm), call(48, 0, qpixm)])
        self.assertFalse(mtm.painter.isActive())

    def test_rowCount(self):
        """Test columnCount"""
        p = ObjListWindow()
        mtm = PBTableModel(p, ["a", "b"])
        self.assertEqual(mtm.rowCount(), 0)
        mtm.dataList = [{"a": 1, "b": 3}, {"a": 2, "b": 2}, {"a": 3, "b": 1}]
        self.assertEqual(mtm.rowCount(), 3)
        mtm = PBTableModel(p, 1)
        self.assertEqual(mtm.rowCount(), 0)

    def test_columnCount(self):
        """Test columnCount"""
        p = ObjListWindow()
        mtm = PBTableModel(p, ["a", "b"])
        self.assertEqual(mtm.columnCount(), 2)
        self.assertEqual(mtm.columnCount(p), 2)
        mtm = PBTableModel(p, 1)
        self.assertEqual(mtm.columnCount(), 0)

    def test_data(self):
        """Test that data is not implemented"""
        p = ObjListWindow()
        mtm = PBTableModel(p, ["a", "b"])
        self.assertRaises(NotImplementedError, lambda: mtm.data(1, 1))

    def test_flags(self):
        """test flags"""
        idx = QModelIndex()
        p = ObjListWindow()
        mtm = PBTableModel(p, ["a", "b"])
        self.assertEqual(mtm.flags(idx), Qt.NoItemFlags)
        with patch("PySide2.QtCore.QModelIndex.isValid", return_value=True) as _iv:
            with patch(
                "PySide2.QtCore.QModelIndex.column", return_value=1, autospec=True
            ) as _c:
                self.assertEqual(mtm.flags(idx), Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            with patch(
                "PySide2.QtCore.QModelIndex.column", return_value=0, autospec=True
            ) as _c:
                self.assertEqual(mtm.flags(idx), Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            mtm.ask = True
            with patch(
                "PySide2.QtCore.QModelIndex.column", return_value=0, autospec=True
            ) as _c:
                self.assertEqual(
                    mtm.flags(idx),
                    Qt.ItemIsUserCheckable
                    | Qt.ItemIsEditable
                    | Qt.ItemIsEnabled
                    | Qt.ItemIsSelectable,
                )

    def test_headerData(self):
        """test headerData"""
        p = ObjListWindow()
        mtm = PBTableModel(p, ["a", "b"])
        self.assertEqual(mtm.headerData(0, Qt.Vertical, Qt.DisplayRole), None)
        self.assertEqual(mtm.headerData(0, Qt.Horizontal, Qt.EditRole), None)
        self.assertEqual(mtm.headerData(0, Qt.Horizontal, Qt.DisplayRole), "a")

    def test_setData(self):
        """Test that setData is not implemented"""
        p = ObjListWindow()
        mtm = PBTableModel(p, ["a", "b"])
        self.assertRaises(NotImplementedError, lambda: mtm.setData(1, 1, 1))


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestTreeNode(GUITestCase):
    """Test the TreeNode class"""

    def test_methods(self):
        """test the __init__ and _getChildren methods"""
        ew = QWidget()
        with patch(
            "physbiblio.gui.commonClasses.TreeNode._getChildren",
            return_value="def",
            autospec=True,
        ) as _gc:
            tn = TreeNode(ew, "abc")
            self.assertEqual(tn.parent(), ew)
            self.assertEqual(tn.parentObj, ew)
            self.assertEqual(tn.row, "abc")
            self.assertEqual(tn.subnodes, "def")
            _gc.assert_called_once_with(tn)
        self.assertRaises(NotImplementedError, lambda: tn._getChildren())


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestTreeModel(GUITestCase):
    """Test the TreeModel class"""

    def createTm(self):
        """Create a model structure for tests"""
        with patch(
            "physbiblio.gui.commonClasses.TreeModel._getRootNodes", autospec=True
        ):
            tm = TreeModel()
        tm.rootElements = [
            NamedElement(
                0,
                "main",
                [
                    NamedElement(1, "test1", [NamedElement(2, "test2", [])]),
                    NamedElement(3, "test3", []),
                ],
            )
        ]
        tm.rootNodes = [NamedNode(tm.rootElements[0], None, 0)]
        return tm

    def test_init(self):
        """test the constructor"""
        with patch(
            "physbiblio.gui.commonClasses.TreeModel._getRootNodes",
            return_value="empty",
            autospec=True,
        ) as _gr:
            tm = TreeModel()
            self.assertEqual(_gr.call_count, 1)
        self.assertIsInstance(tm, QAbstractItemModel)
        self.assertEqual(tm.rootNodes, "empty")

    def test_getRootNodes(self):
        """test the non implemented _getRootNodes"""
        self.assertRaises(NotImplementedError, lambda: TreeModel())
        with patch(
            "physbiblio.gui.commonClasses.TreeModel._getRootNodes",
            return_value="empty",
            autospec=True,
        ) as _gr:
            tm = TreeModel()
        self.assertRaises(NotImplementedError, lambda: tm._getRootNodes())

    def test_index(self):
        """Test the function that returns the object index"""
        tm = self.createTm()
        with patch("logging.Logger.debug") as _d:
            qmi = tm.index(0, 0, None)
            self.assertIsInstance(qmi, QModelIndex)
            self.assertFalse(qmi.isValid())
            _d.assert_called_once_with(
                "Invalid parent 'None' in TreeModel.index", exc_info=True
            )
        qmi = tm.index(0, 0)
        self.assertIsInstance(qmi, QModelIndex)
        self.assertTrue(qmi.isValid())
        self.assertEqual(TreeNode.cast(qmi).element.name, "main")
        qmi = tm.index(1, 0)
        self.assertIsInstance(qmi, QModelIndex)
        self.assertFalse(qmi.isValid())
        p = tm.index(0, 0)
        qmi = tm.index(0, 0, parent=p)
        self.assertIsInstance(qmi, QModelIndex)
        self.assertTrue(qmi.isValid())
        self.assertEqual(TreeNode.cast(qmi).element.name, "test1")
        qmi = tm.index(1, 0, parent=p)
        self.assertIsInstance(qmi, QModelIndex)
        self.assertTrue(qmi.isValid())
        self.assertEqual(TreeNode.cast(qmi).element.name, "test3")
        qmi = tm.index(2, 0, parent=p)
        self.assertIsInstance(qmi, QModelIndex)
        self.assertFalse(qmi.isValid())
        qmi = tm.index(0, 0, parent=tm.index(1, 0, parent=p))
        self.assertIsInstance(qmi, QModelIndex)
        self.assertFalse(qmi.isValid())
        qmi = tm.index(0, 0, parent=tm.index(0, 0, parent=p))
        self.assertIsInstance(qmi, QModelIndex)
        self.assertTrue(qmi.isValid())
        self.assertEqual(TreeNode.cast(qmi).element.name, "test2")
        qmi = tm.index(0, 0, parent=tm.index(5, 0))
        self.assertIsInstance(qmi, QModelIndex)
        self.assertTrue(qmi.isValid())
        self.assertEqual(TreeNode.cast(qmi).element.name, "main")
        qmi = tm.index(3, 0, parent=tm.index(5, 0))
        self.assertIsInstance(qmi, QModelIndex)
        self.assertFalse(qmi.isValid())

    def test_parent(self):
        """Test the function that returns the parent object"""
        tm = self.createTm()
        mn = tm.index(0, 0)
        t1 = tm.index(0, 0, parent=mn)
        t2 = tm.index(0, 0, parent=t1)
        t3 = tm.index(1, 0, parent=mn)

        with patch("logging.Logger.debug") as _d:
            qmi = tm.parent(None)
            self.assertIsInstance(qmi, QModelIndex)
            self.assertFalse(qmi.isValid())
            _d.assert_called_once_with(
                "Invalid index 'None' in TreeModel.parent", exc_info=True
            )
        qmi = tm.parent(tm.index(3, 0))
        self.assertIsInstance(qmi, QModelIndex)
        self.assertFalse(qmi.isValid())

        qmi = tm.parent(mn)
        self.assertIsInstance(qmi, QModelIndex)
        self.assertFalse(qmi.isValid())
        qmi = tm.parent(t1)
        self.assertIsInstance(qmi, QModelIndex)
        self.assertTrue(qmi.isValid())
        self.assertEqual(TreeNode.cast(qmi).element.name, "main")
        qmi = tm.parent(t3)
        self.assertIsInstance(qmi, QModelIndex)
        self.assertTrue(qmi.isValid())
        self.assertEqual(TreeNode.cast(qmi).element.name, "main")
        qmi = tm.parent(t2)
        self.assertIsInstance(qmi, QModelIndex)
        self.assertTrue(qmi.isValid())
        self.assertEqual(TreeNode.cast(qmi).element.name, "test1")

    def test_rowCount(self):
        """test the counting of rows"""
        tm = self.createTm()
        mn = tm.index(0, 0)
        t1 = tm.index(0, 0, parent=mn)
        t2 = tm.index(0, 0, parent=t1)
        t3 = tm.index(1, 0, parent=mn)
        with patch("logging.Logger.debug") as _d:
            rc = tm.rowCount(None)
            self.assertEqual(rc, 1)
            _d.assert_called_once_with(
                "Invalid parent 'None' in TreeModel.rowCount", exc_info=True
            )
        self.assertEqual(tm.rowCount(), 1)
        self.assertEqual(tm.rowCount(tm.index(5, 0)), 1)
        self.assertEqual(tm.rowCount(mn), 2)
        self.assertEqual(tm.rowCount(t1), 1)
        self.assertEqual(tm.rowCount(t2), 0)
        self.assertEqual(tm.rowCount(t3), 0)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestNamedElement(GUITestCase):
    """Test the NamedElement class"""

    def test_init(self):
        """test the constructor"""
        with patch(
            "physbiblio.gui.commonClasses.catString",
            return_value="abcde",
            autospec=True,
        ) as _cs:
            ne = NamedElement(0, "main", ["a", "b"])
            _cs.assert_called_once_with(0, pBDB)
        self.assertEqual(ne.idCat, 0)
        self.assertEqual(ne.name, "main")
        self.assertEqual(ne.text, "abcde")
        self.assertEqual(ne.subelements, ["a", "b"])


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestNamedNode(GUITestCase):
    """Test the NamedNode class"""

    def test_methods(self):
        """test __init__ and _getChildren"""
        el = NamedElement(1, "tags", [])
        main = NamedElement(0, "main", [el])
        nn = NamedNode(main, None, 0)
        self.assertIsInstance(nn, TreeNode)
        with patch(
            "physbiblio.gui.commonClasses.TreeNode.__init__",
            return_value=None,
            autospec=True,
        ) as _in:
            nn = NamedNode(main, None, 0)
            _in.assert_called_once_with(nn, None, 0)
        self.assertEqual(nn.element, main)
        with patch(
            "physbiblio.gui.commonClasses.NamedNode.__init__",
            return_value=None,
            autospec=True,
        ) as _in:
            res = nn._getChildren()
            _in.assert_called_once_with(res[0], el, nn, 0)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertIsInstance(res[0], NamedNode)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestLeafFilterProxyModel(GUITestCase):
    """Test the LeafFilterProxyModel class"""

    def test_init(self):
        """just check that the created object is an instance of parent class"""
        lf = LeafFilterProxyModel()
        self.assertIsInstance(lf, QSortFilterProxyModel)

    def test_filterAcceptsRow(self):
        """Test filterAcceptsRow with all possible combinations"""
        lf = LeafFilterProxyModel()
        with patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel."
            + "filterAcceptsRowItself",
            return_value=True,
            autospec=True,
        ) as _its, patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel."
            + "filterAcceptsAnyParent",
            autospec=True,
        ) as _par, patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel."
            + "hasAcceptedChildren",
            autospec=True,
        ) as _chi:
            self.assertTrue(lf.filterAcceptsRow(0, None))
            _its.assert_called_once_with(lf, 0, None)
            _par.assert_not_called()
            _chi.assert_not_called()
        with patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel."
            + "filterAcceptsRowItself",
            return_value=False,
            autospec=True,
        ) as _its, patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel."
            + "filterAcceptsAnyParent",
            return_value=True,
            autospec=True,
        ) as _par, patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel."
            + "hasAcceptedChildren",
            autospec=True,
        ) as _chi:
            self.assertTrue(lf.filterAcceptsRow(0, None))
            _its.assert_called_once_with(lf, 0, None)
            _par.assert_called_once_with(lf, None)
            _chi.assert_not_called()
        with patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel."
            + "filterAcceptsRowItself",
            return_value=False,
            autospec=True,
        ) as _its, patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel."
            + "filterAcceptsAnyParent",
            return_value=False,
            autospec=True,
        ) as _par, patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel."
            + "hasAcceptedChildren",
            return_value=True,
            autospec=True,
        ) as _chi:
            self.assertTrue(lf.filterAcceptsRow(0, None))
            _its.assert_called_once_with(lf, 0, None)
            _par.assert_called_once_with(lf, None)
            _chi.assert_called_once_with(lf, 0, None)
        with patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel."
            + "filterAcceptsRowItself",
            return_value=False,
            autospec=True,
        ) as _its, patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel."
            + "filterAcceptsAnyParent",
            return_value=False,
            autospec=True,
        ) as _par, patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel."
            + "hasAcceptedChildren",
            return_value=False,
            autospec=True,
        ) as _chi:
            self.assertFalse(lf.filterAcceptsRow(0, None))
            _its.assert_called_once_with(lf, 0, None)
            _par.assert_called_once_with(lf, None)
            _chi.assert_called_once_with(lf, 0, None)

    def test_filterAcceptRowItself(self):
        """test filterAcceptRowItself"""
        lf = LeafFilterProxyModel()
        with patch(
            "PySide2.QtCore.QSortFilterProxyModel.filterAcceptsRow",
            return_value="testval",
            autospec=True,
        ) as _far:
            self.assertEqual(lf.filterAcceptsRowItself(0, "par"), "testval")
            _far.assert_called_once_with(0, "par")

    def test_filterAcceptsAnyParent(self):
        """test filterAcceptsAnyParent"""
        el = NamedElement(1, "tags", [])
        ot = NamedElement(2, "other", [])
        main = NamedElement(0, "main", [el])
        lf = LeafFilterProxyModel()
        tm = EmptyTreeModel([main, ot])
        lf.setSourceModel(tm)
        self.assertTrue(lf.filterAcceptsAnyParent(lf.index(0, 0, QModelIndex())))
        self.assertTrue(lf.filterAcceptsAnyParent(lf.index(1, 0, QModelIndex())))
        self.assertFalse(lf.filterAcceptsAnyParent(lf.index(2, 0, QModelIndex())))
        with patch(
            "PySide2.QtCore.QModelIndex.isValid",
            side_effect=[True, True, False],
            autospec=True,
        ) as _iv, patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel."
            + "filterAcceptsRowItself",
            return_value=False,
            autospec=True,
        ) as _its:
            self.assertFalse(lf.filterAcceptsAnyParent(lf.index(0, 0, QModelIndex())))
            self.assertEqual(_iv.call_count, 3)
            self.assertEqual(_its.call_count, 2)
        with patch(
            "PySide2.QtCore.QModelIndex.isValid",
            side_effect=[True, True, False],
            autospec=True,
        ) as _iv, patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel."
            + "filterAcceptsRowItself",
            return_value=False,
            autospec=True,
        ) as _its, patch(
            "physbiblio.gui.commonClasses.QModelIndex.parent",
            return_value=QModelIndex(),
            autospec=True,
        ) as _pa:
            self.assertFalse(lf.filterAcceptsAnyParent(lf.index(0, 0, QModelIndex())))
            self.assertEqual(_iv.call_count, 3)
            self.assertEqual(_its.call_count, 2)
            self.assertEqual(_pa.call_count, 4)
        with patch(
            "PySide2.QtCore.QModelIndex.isValid",
            side_effect=[True, True, False],
            autospec=True,
        ) as _iv, patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel."
            + "filterAcceptsRowItself",
            return_value=True,
            autospec=True,
        ) as _its:
            self.assertTrue(lf.filterAcceptsAnyParent(lf.index(0, 0, QModelIndex())))
            self.assertEqual(_iv.call_count, 1)
            self.assertEqual(_its.call_count, 1)
        with patch(
            "PySide2.QtCore.QModelIndex.isValid",
            side_effect=[True, True, False],
            autospec=True,
        ) as _iv, patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel."
            + "filterAcceptsRowItself",
            return_value=True,
            autospec=True,
        ) as _its, patch(
            "PySide2.QtCore.QModelIndex.parent", autospec=True
        ) as _pa:
            self.assertTrue(lf.filterAcceptsAnyParent(lf.index(0, 0, QModelIndex())))
            self.assertEqual(_iv.call_count, 1)
            self.assertEqual(_its.call_count, 1)
            self.assertEqual(_pa.call_count, 1)

    def test_hasAcceptedChildren(self):  # probably could be improved a bit
        """test hasAcceptedChildren"""
        el = NamedElement(1, "tags", [])
        main = NamedElement(0, "main", [el])
        lf = LeafFilterProxyModel()
        tm = EmptyTreeModel([main])
        lf.setSourceModel(tm)
        self.assertTrue(lf.hasAcceptedChildren(0, QModelIndex()))
        with patch(
            "physbiblio.gui.tests.test_commonClasses.EmptyTreeModel.rowCount",
            return_value=1,
            autospec=True,
        ) as _rc:
            self.assertTrue(lf.hasAcceptedChildren(1, QModelIndex()))
        with patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel.filterAcceptsRow",
            return_value=True,
            autospec=True,
        ) as _acc:
            self.assertTrue(lf.hasAcceptedChildren(5, QModelIndex()))
            self.assertEqual(_acc.call_count, 1)
        with patch(
            "physbiblio.gui.commonClasses.LeafFilterProxyModel.filterAcceptsRow",
            return_value=False,
            autospec=True,
        ) as _acc, patch(
            "physbiblio.gui.tests.test_commonClasses.EmptyTreeModel.rowCount",
            return_value=1,
            autospec=True,
        ) as _rc:
            self.assertFalse(lf.hasAcceptedChildren(1, QModelIndex()))


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestPBDDTableWidget(GUITestCase):
    """Test the PBDDTableWidget class"""

    def test_init(self):
        """test init"""
        p = QWidget()
        mddtw = PBDDTableWidget(p, "head")
        self.assertIsInstance(mddtw, QTableWidget)
        self.assertEqual(mddtw.parent(), p)
        self.assertEqual(mddtw.columnCount(), 1)
        self.assertTrue(mddtw.dragEnabled())
        self.assertTrue(mddtw.acceptDrops())
        self.assertFalse(mddtw.dragDropOverwriteMode())
        self.assertEqual(mddtw.selectionBehavior(), QAbstractItemView.SelectRows)
        with patch(
            "physbiblio.gui.commonClasses.QTableWidget.setHorizontalHeaderLabels",
            autospec=True,
        ) as _shl:
            mddtw = PBDDTableWidget(p, "head")
            _shl.assert_called_once_with(["head"])

    def test_dropMimeData(self):
        """test dropMimeData"""
        p = QWidget()
        mddtw = PBDDTableWidget(p, "head")
        self.assertTrue(mddtw.dropMimeData(12, 0, None, None))
        self.assertEqual(mddtw.lastDropRow, 12)

    def test_dropEvent(self):
        """test dropEvent"""
        p = QWidget()
        sender = PBDDTableWidget(p, "head")
        item = QTableWidgetItem("source1")
        sender.insertRow(0)
        sender.setItem(0, 0, item)
        item = QTableWidgetItem("source2")
        sender.insertRow(1)
        sender.setItem(1, 0, item)
        sender.selectionModel().select(
            sender.model().index(0, 0), QItemSelectionModel.Select
        )

        mddtw = PBDDTableWidget(p, "head")
        item = QTableWidgetItem("test1")
        mddtw.insertRow(0)
        mddtw.setItem(0, 0, item)
        item = QTableWidgetItem("test2")
        mddtw.insertRow(1)
        mddtw.setItem(1, 0, item)

        mimedata = QMimeData()
        if sys.version_info[0] < 3:
            mimedata.setData(
                "application/x-qabstractitemmodeldatalist", QByteArray("source1")
            )
        else:
            mimedata.setData(
                "application/x-qabstractitemmodeldatalist", QByteArray(b"source1")
            )
        ev = QDropEvent(
            mddtw.pos(),
            Qt.DropActions(Qt.MoveAction),
            mimedata,
            Qt.MouseButtons(Qt.LeftButton),
            Qt.KeyboardModifiers(Qt.NoModifier),
        )
        with patch(
            "PySide2.QtGui.QDropEvent.source", return_value=sender, autospec=True
        ) as _s:
            mddtw.dropEvent(ev)
            _s.assert_called_once_with()
        self.assertEqual(sender.rowCount(), 1)
        self.assertEqual(mddtw.rowCount(), 3)
        self.assertEqual(sender.item(0, 0).text(), "source2")
        self.assertEqual(mddtw.item(0, 0).text(), "source1")
        self.assertEqual(mddtw.item(1, 0).text(), "test1")
        self.assertEqual(mddtw.item(2, 0).text(), "test2")

        mddtw.selectionModel().select(
            mddtw.model().index(1, 0), QItemSelectionModel.Select
        )
        if sys.version_info[0] < 3:
            mimedata.setData(
                "application/x-qabstractitemmodeldatalist", QByteArray("test1")
            )
        else:
            mimedata.setData(
                "application/x-qabstractitemmodeldatalist", QByteArray(b"test1")
            )
        ev = QDropEvent(
            mddtw.pos(),
            Qt.DropActions(Qt.MoveAction),
            mimedata,
            Qt.MouseButtons(Qt.LeftButton),
            Qt.KeyboardModifiers(Qt.NoModifier),
        )
        with patch(
            "PySide2.QtGui.QDropEvent.source", return_value=mddtw, autospec=True
        ) as _s:
            mddtw.dropEvent(ev)
            _s.assert_called_once_with()
        self.assertEqual(sender.rowCount(), 1)
        self.assertEqual(mddtw.rowCount(), 3)
        self.assertEqual(sender.item(0, 0).text(), "source2")
        self.assertEqual(mddtw.item(0, 0).text(), "test1")
        self.assertEqual(mddtw.item(1, 0).text(), "source1")
        self.assertEqual(mddtw.item(2, 0).text(), "test2")

    def test_getselectedRowsFast(self):
        """test getselectedRowsFast"""
        p = QWidget()
        mddtw = PBDDTableWidget(p, "head")
        a = mddtw.getselectedRowsFast()
        self.assertEqual(a, [])
        with patch(
            "PySide2.QtWidgets.QTableWidget.selectedItems",
            return_value=[QTableWidgetItem() for i in range(5)],
            autospec=True,
        ) as _si, patch(
            "PySide2.QtWidgets.QTableWidgetItem.row",
            side_effect=[1, 8, 3, 1, 2],
            autospec=True,
        ) as _r, patch(
            "PySide2.QtWidgets.QTableWidgetItem.text",
            side_effect=["de", "fg", "ab", "hi", "bibkey"],
            autospec=True,
        ) as _t:
            a = mddtw.getselectedRowsFast()
            self.assertEqual(a, [1, 3, 8])


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestPBMenu(GUITestCase):
    """Test the PBMenu class"""

    def test_init(self):
        """Test init"""
        mm = PBMenu()
        self.assertIsInstance(mm, QMenu)
        self.assertEqual(mm.possibleActions, [])
        self.assertFalse(mm.result)
        with patch("physbiblio.gui.commonClasses.QMenu.__init__", autospec=True) as _in:
            mm = PBMenu("abc")
            _in.assert_called_once_with("abc")

    def test_fillMenu(self):
        """test fillMenu"""
        mm = PBMenu()
        acts = [
            QAction("test1"),
            "abc",
            QAction("test2"),
            None,
            [
                "submenu",
                [QAction("Sub1"), QAction("Sub2"), ["subsub", [QAction("nest")]], None],
            ],
            {
                "title": "submenuDict",
                "actions": [QAction("Sub3"), QAction("Sub4")],
                "toolTipsVisible": True,
            },
            {
                "title": "submenuDictI",
                "actions": [QAction("Sub5"), QAction("Sub6")],
            },
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

        self.assertIsInstance(macts[4].menu(), QMenu)
        subm = macts[4].menu()
        self.assertEqual(subm.title(), acts[5]["title"])
        sacts = subm.actions()
        self.assertEqual(acts[5]["actions"][0], sacts[0])
        self.assertEqual(acts[5]["actions"][1], sacts[1])
        self.assertTrue(subm.toolTipsVisible())

        subm = macts[5].menu()
        self.assertIsInstance(macts[5].menu(), QMenu)
        self.assertEqual(subm.title(), acts[6]["title"])
        sacts = subm.actions()
        self.assertEqual(acts[6]["actions"][0], sacts[0])
        self.assertEqual(acts[6]["actions"][1], sacts[1])
        self.assertFalse(subm.toolTipsVisible())

    def test_keyPressEvent(self):
        """test keyPressEvent"""
        mm = PBMenu()
        with patch("physbiblio.gui.commonClasses.QMenu.close", autospec=True) as _oc:
            QTest.keyPress(mm, "a")
            _oc.assert_not_called()
            QTest.keyPress(mm, Qt.Key_Enter)
            _oc.assert_not_called()
            QTest.keyPress(mm, Qt.Key_Escape)
            self.assertEqual(_oc.call_count, 1)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestGuiViewEntry(GUITestCase):
    """Test the GuiViewEntry class"""

    def test_methods(self):
        """Test that the object is instance of `ViewEntry`
        and that openLink works
        """
        gve = GUIViewEntry()
        self.assertIsInstance(gve, ViewEntry)
        self.assertIsInstance(pBGuiView, GUIViewEntry)

        with patch(
            "PySide2.QtGui.QDesktopServices.openUrl", return_value=True
        ) as _ou, patch("logging.Logger.debug") as _db:
            gve.openLink(["abc", "def"], "link")
            _db.assert_has_calls(
                [
                    call("Opening link 'abc' for entry 'abc' successful!"),
                    call("Opening link 'def' for entry 'def' successful!"),
                ]
            )
            _ou.assert_has_calls([call(QUrl("abc")), call(QUrl("def"))])
        with patch(
            "PySide2.QtGui.QDesktopServices.openUrl", return_value=False
        ) as _ou, patch("logging.Logger.warning") as _db:
            gve.openLink(["abc", "def"], "link")
            _db.assert_has_calls(
                [
                    call("Opening link for 'abc' failed!"),
                    call("Opening link for 'def' failed!"),
                ]
            )
            _ou.assert_has_calls([call(QUrl("abc")), call(QUrl("def"))])
        with patch(
            "PySide2.QtGui.QDesktopServices.openUrl", return_value=True
        ) as _ou, patch(
            "physbiblio.view.ViewEntry.getLink", return_value="mylink", autospec=True
        ) as _gl:
            gve.openLink("abc", arg="somearg", fileArg="somefilearg")
            _gl.assert_called_once_with(
                gve, "abc", arg="somearg", fileArg="somefilearg"
            )
            _ou.assert_called_once_with(QUrl("mylink"))
        with patch(
            "PySide2.QtGui.QDesktopServices.openUrl", return_value=True
        ) as _ou, patch(
            "physbiblio.gui.commonClasses.QUrl.fromLocalFile",
            return_value=QUrl("mylink"),
        ) as _fl:
            gve.openLink("abc", arg="file", fileArg="/a/b/c")
            _fl.assert_called_once_with("/a/b/c")
            _ou.assert_called_once_with(QUrl("mylink"))


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestPBImportedTableModel(GUITestCase):
    """Test the PBImportedTableModel class"""

    def test_init(self):
        """test init"""
        with patch(
            "physbiblio.gui.commonClasses.PBTableModel.prepareSelected", autospec=True
        ) as _ps:
            mitm = PBImportedTableModel(
                QWidget(),
                {
                    "a": {"exist": False, "bibpars": {"ID": "a"}},
                    "b": {"exist": False, "bibpars": {"ID": "b"}},
                },
                ["key", "id"],
                "bibkey",
            )
            self.assertEqual(_ps.call_count, 1)
        self.assertIsInstance(mitm, PBTableModel)
        self.assertEqual(mitm.typeClass, "imports")
        self.assertEqual(mitm.idName, "bibkey")
        self.assertEqual(mitm.bibsOrder, ["a", "b"])
        self.assertEqual(mitm.dataList, [{"ID": "a"}, {"ID": "b"}])
        self.assertEqual(mitm.existList, [False, False])

    def test_getIdentifier(self):
        """test getIdentifier"""
        mitm = PBImportedTableModel(
            QWidget(),
            {
                "a": {"exist": False, "bibpars": {"ID": "a"}},
                "b": {"exist": False, "bibpars": {"ID": "b"}},
            },
            ["key", "id"],
        )
        self.assertEqual(mitm.getIdentifier({"id": "a", "bibkey": "b", "ID": "i"}), "i")

    def test_data(self):
        """test data"""
        mitm = PBImportedTableModel(
            QWidget(),
            {
                "a": {"exist": False, "bibpars": {"ID": "a", "key": "a"}},
                "b": {"exist": False, "bibpars": {"ID": "b", "key": "b"}},
            },
            ["key", "ID"],
        )
        with patch(
            "PySide2.QtCore.QModelIndex.isValid", return_value=False, autospec=True
        ) as _iv:
            self.assertEqual(mitm.data(QModelIndex(), Qt.DisplayRole), None)
        with patch(
            "PySide2.QtCore.QModelIndex.isValid", return_value=True, autospec=True
        ) as _iv:
            with patch(
                "PySide2.QtCore.QModelIndex.column", return_value=10, autospec=True
            ) as _c, patch(
                "PySide2.QtCore.QModelIndex.row", return_value=10, autospec=True
            ) as _r:
                self.assertEqual(mitm.data(QModelIndex(), Qt.DisplayRole), None)
            with patch(
                "PySide2.QtCore.QModelIndex.column", return_value=0, autospec=True
            ) as _c, patch(
                "PySide2.QtCore.QModelIndex.row", return_value=0, autospec=True
            ) as _r:
                self.assertEqual(
                    mitm.data(QModelIndex(), Qt.CheckStateRole), Qt.Unchecked
                )
                self.assertTrue(
                    mitm.setData(QModelIndex(), Qt.Checked, Qt.CheckStateRole)
                )
                self.assertEqual(
                    mitm.data(QModelIndex(), Qt.CheckStateRole), Qt.Checked
                )
            with patch(
                "PySide2.QtCore.QModelIndex.column", return_value=0, autospec=True
            ) as _c, patch(
                "PySide2.QtCore.QModelIndex.row", return_value=0, autospec=True
            ) as _r:
                mitm.existList[0] = True
                self.assertEqual(
                    mitm.data(QModelIndex(), Qt.EditRole), "a - already existing"
                )
                self.assertEqual(
                    mitm.data(QModelIndex(), Qt.DisplayRole), "a - already existing"
                )
                self.assertEqual(mitm.data(QModelIndex(), Qt.CheckStateRole), None)
            with patch(
                "PySide2.QtCore.QModelIndex.column", return_value=1, autospec=True
            ) as _c, patch(
                "PySide2.QtCore.QModelIndex.row", return_value=0, autospec=True
            ) as _r:
                self.assertEqual(mitm.data(QModelIndex(), Qt.EditRole), "a")
                self.assertEqual(mitm.data(QModelIndex(), Qt.DisplayRole), "a")
                self.assertEqual(mitm.data(QModelIndex(), Qt.CheckStateRole), None)

    def test_setData(self):
        """test setData"""
        mitm = PBImportedTableModel(
            QWidget(),
            {
                "a": {"exist": False, "bibpars": {"ID": "a"}},
                "b": {"exist": False, "bibpars": {"ID": "b"}},
            },
            ["key", "id"],
        )
        mitm.dataChanged.connect(fakeExec_dataChanged)
        ids = {"a": False, "b": False}
        with patch(
            "PySide2.QtCore.QModelIndex.isValid", return_value=True, autospec=True
        ) as _iv:
            self.assertTrue(mitm.setData(QModelIndex(), "abc", Qt.DisplayRole))
            self.assertEqual(ids, mitm.selectedElements)
            with patch(
                "PySide2.QtCore.QModelIndex.column", return_value=1, autospec=True
            ) as _c:
                self.assertTrue(mitm.setData(QModelIndex(), "abc", Qt.CheckStateRole))
                self.assertEqual(ids, mitm.selectedElements)
            with patch(
                "PySide2.QtCore.QModelIndex.column", return_value=0, autospec=True
            ) as _c, patch(
                "PySide2.QtCore.QModelIndex.row", return_value=0, autospec=True
            ) as _r:
                self.assertTrue(
                    mitm.setData(QModelIndex(), Qt.Checked, Qt.CheckStateRole)
                )
                self.assertEqual({"a": True, "b": False}, mitm.selectedElements)
                self.assertTrue(
                    mitm.setData(QModelIndex(), Qt.Unchecked, Qt.CheckStateRole)
                )
                self.assertEqual({"a": False, "b": False}, mitm.selectedElements)
                self.assertTrue(
                    mitm.setData(QModelIndex(), Qt.Checked, Qt.CheckStateRole)
                )
                self.assertEqual({"a": True, "b": False}, mitm.selectedElements)
                self.assertTrue(mitm.setData(QModelIndex(), "abc", Qt.CheckStateRole))
                self.assertEqual({"a": False, "b": False}, mitm.selectedElements)
        with patch(
            "PySide2.QtCore.QModelIndex.isValid", return_value=False, autospec=True
        ) as _iv:
            self.assertFalse(mitm.setData(QModelIndex(), Qt.Checked, Qt.DisplayRole))

    def test_flags(self):
        """test flags"""
        mitm = PBImportedTableModel(
            QWidget(),
            {
                "a": {"exist": False, "bibpars": {"ID": "a"}},
                "b": {"exist": True, "bibpars": {"ID": "b"}},
            },
            ["key", "id"],
        )
        with patch(
            "PySide2.QtCore.QModelIndex.isValid", return_value=False, autospec=True
        ) as _iv:
            self.assertEqual(mitm.flags(QModelIndex()), Qt.NoItemFlags)
        with patch(
            "PySide2.QtCore.QModelIndex.isValid", return_value=True, autospec=True
        ) as _iv, patch(
            "PySide2.QtCore.QModelIndex.column", return_value=1, autospec=True
        ) as _c, patch(
            "PySide2.QtCore.QModelIndex.row", side_effect=[0, 1], autospec=True
        ) as _r:
            self.assertEqual(
                mitm.flags(QModelIndex()), Qt.ItemIsEnabled | Qt.ItemIsSelectable
            )
            self.assertEqual(
                mitm.flags(QModelIndex()), Qt.ItemIsEnabled | Qt.ItemIsSelectable
            )
        with patch(
            "PySide2.QtCore.QModelIndex.isValid", return_value=True, autospec=True
        ) as _iv, patch(
            "PySide2.QtCore.QModelIndex.column", return_value=0, autospec=True
        ) as _c, patch(
            "PySide2.QtCore.QModelIndex.row", side_effect=[0, 1], autospec=True
        ) as _r:
            self.assertEqual(
                mitm.flags(QModelIndex()),
                Qt.ItemIsUserCheckable
                | Qt.ItemIsEditable
                | Qt.ItemIsEnabled
                | Qt.ItemIsSelectable,
            )
            self.assertEqual(
                mitm.flags(QModelIndex()), Qt.ItemIsEnabled | Qt.ItemIsSelectable
            )


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestObjectWithSignal(GUITestCase):
    """Test the ObjectWithSignal class"""

    def test_class(self):
        """test the class inheritance and signal existence"""
        o = ObjectWithSignal()
        self.assertIsInstance(o, QObject)
        self.assertIsInstance(o.customSignal, Signal)


if __name__ == "__main__":
    unittest.main()
