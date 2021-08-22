#!/usr/bin/env python
"""Test file for the physbiblio.gui.catWindows module.

This file is part of the physbiblio package.
"""
import os
import sys
import traceback

from PySide2.QtCore import QEvent, QModelIndex, QPoint, Qt
from PySide2.QtGui import QMouseEvent
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QWidget

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import MagicMock, call, patch
else:
    import unittest
    from unittest.mock import MagicMock, call, patch

try:
    from physbiblio.database import pBDB
    from physbiblio.gui.catWindows import *
    from physbiblio.gui.mainWindow import MainWindow
    from physbiblio.gui.setuptests import *
    from physbiblio.setuptests import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestFunctions(GUIwMainWTestCase):
    """test editCategory and deleteCategory"""

    def test_editCategory(self):
        """test editCategory"""
        p = QWidget()
        m = self.mainW
        ncw = EditCategoryDialog(p)
        ncw.exec_ = MagicMock()
        ncw.onCancel()
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.catWindows.EditCategoryDialog",
            return_value=ncw,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            editCategory(p, m)
            _i.assert_called_once_with(p, category=None, useParentCat=None)
            _s.assert_called_once_with(m, "No modifications to categories")

        with patch(
            "physbiblio.gui.catWindows.EditCategoryDialog",
            return_value=ncw,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i, patch("logging.Logger.debug") as _l:
            editCategory(p, p)
            _i.assert_called_once_with(p, category=None, useParentCat=None)
            _l.assert_called_once_with(
                "mainWinObject has no attribute 'statusBarMessage'", exc_info=True
            )

        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.catWindows.EditCategoryDialog",
            return_value=ncw,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i, patch(
            "physbiblio.database.Categories.getDictByID",
            return_value="abc",
            autospec=True,
        ) as _g:
            editCategory(p, m, 15)
            _i.assert_called_once_with(p, category="abc", useParentCat=None)
            _g.assert_called_once_with(pBDB.cats, 15)
            _s.assert_called_once_with(m, "No modifications to categories")

        ncw = EditCategoryDialog(p)
        ncw.selectedCats = [18]
        ncw.textValues["ord"].setText("0")
        ncw.textValues["comments"].setText("comm")
        ncw.textValues["description"].setText("desc")
        ncw.exec_ = MagicMock()
        ncw.onOk()
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.catWindows.EditCategoryDialog",
            return_value=ncw,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i, patch(
            "physbiblio.database.Categories.getDictByID",
            return_value="abc",
            autospec=True,
        ) as _g:
            editCategory(p, m, editIdCat=15)
            _i.assert_called_once_with(p, category="abc", useParentCat=None)
            _g.assert_called_once_with(pBDB.cats, 15)
            _s.assert_called_once_with(m, "ERROR: empty category name")

        ncw.textValues["name"].setText("mycat")
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.catWindows.EditCategoryDialog",
            return_value=ncw,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i, patch(
            "physbiblio.database.Categories.getDictByID",
            return_value="abc",
            autospec=True,
        ) as _g, patch(
            "physbiblio.database.Categories.insert", return_value="abc", autospec=True
        ) as _n, patch(
            "logging.Logger.debug"
        ) as _l:
            editCategory(p, m, 15)
            _i.assert_called_once_with(p, category="abc", useParentCat=None)
            _g.assert_called_once_with(pBDB.cats, 15)
            _n.assert_called_once_with(
                pBDB.cats,
                {
                    "ord": u"0",
                    "description": u"desc",
                    "parentCat": "18",
                    "comments": u"comm",
                    "name": u"mycat",
                },
            )
            _s.assert_called_once_with(m, "Category saved")
            _l.assert_called_once_with(
                "parentObject has no attribute 'recreateTable'", exc_info=True
            )

        ncw.textValues["name"].setText("mycat")
        ctw = CatsTreeWindow(p)
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.catWindows.EditCategoryDialog",
            return_value=ncw,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i, patch(
            "physbiblio.database.Categories.getDictByID",
            return_value="abc",
            autospec=True,
        ) as _g, patch(
            "physbiblio.database.Categories.insert", return_value="abc", autospec=True
        ) as _n, patch(
            "logging.Logger.debug"
        ) as _l, patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.recreateTable", autospec=True
        ) as _r:
            editCategory(ctw, m, 15)
            _i.assert_called_once_with(ctw, category="abc", useParentCat=None)
            _g.assert_called_once_with(pBDB.cats, 15)
            _n.assert_called_once_with(
                pBDB.cats,
                {
                    "ord": u"0",
                    "description": u"desc",
                    "parentCat": "18",
                    "comments": u"comm",
                    "name": u"mycat",
                },
            )
            _s.assert_called_once_with(m, "Category saved")
            _l.assert_not_called()
            _r.assert_called_once_with(ctw)

        cat = {
            "idCat": 15,
            "parentCat": 1,
            "description": "desc",
            "comments": "no comment",
            "ord": 0,
            "name": "mycat",
        }
        with patch(
            "physbiblio.database.Categories.getParent",
            return_value=[[1]],
            autospec=True,
        ) as _p:
            ncw = EditCategoryDialog(p, cat)
        ncw.selectedCats = []
        ncw.textValues["ord"].setText("0")
        ncw.textValues["name"].setText("mycat")
        ncw.textValues["comments"].setText("comm")
        ncw.textValues["description"].setText("desc")
        ncw.exec_ = MagicMock()
        ncw.onOk()
        ctw = CatsTreeWindow(p)
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.catWindows.EditCategoryDialog",
            return_value=ncw,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i, patch(
            "physbiblio.database.Categories.getDictByID",
            return_value="abc",
            autospec=True,
        ) as _g, patch(
            "physbiblio.database.Categories.update", return_value="abc", autospec=True
        ) as _n, patch(
            "logging.Logger.info"
        ) as _l, patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.recreateTable", autospec=True
        ) as _r:
            editCategory(ctw, m, 15, useParentCat=0)
            _i.assert_called_once_with(ctw, category="abc", useParentCat=0)
            _g.assert_called_once_with(pBDB.cats, 15)
            _n.assert_called_once_with(
                pBDB.cats,
                {
                    "idCat": u"15",
                    "ord": u"0",
                    "description": u"desc",
                    "parentCat": "0",
                    "comments": u"comm",
                    "name": u"mycat",
                },
                "15",
            )
            _s.assert_called_once_with(m, "Category saved")
            _l.assert_called_once_with("Updating category 15...")
            _r.assert_called_once_with(ctw)

    def test_deleteCategory(self):
        """test deleteCategory"""
        p = QWidget()
        m = self.mainW
        with patch(
            "physbiblio.gui.catWindows.askYesNo", return_value=False, autospec=True
        ) as _a, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s:
            deleteCategory(p, m, 15, "mycat")
            _a.assert_called_once_with(
                "Do you really want to delete this category "
                + "(ID = '15', name = 'mycat')?"
            )
            _s.assert_called_once_with(m, "Nothing changed")

        with patch(
            "physbiblio.gui.catWindows.askYesNo", return_value=False, autospec=True
        ) as _a, patch("logging.Logger.debug") as _d:
            deleteCategory(p, p, 15, "mycat")
            _a.assert_called_once_with(
                "Do you really want to delete this category "
                + "(ID = '15', name = 'mycat')?"
            )
            _d.assert_called_once_with(
                "mainWinObject has no attribute 'statusBarMessage'", exc_info=True
            )

        with patch(
            "physbiblio.gui.catWindows.askYesNo", return_value=True, autospec=True
        ) as _a, patch(
            "physbiblio.database.Categories.delete", autospec=True
        ) as _c, patch(
            "PySide2.QtWidgets.QMainWindow.setWindowTitle", autospec=True
        ) as _t, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "logging.Logger.debug"
        ) as _d:
            deleteCategory(p, m, 15, "mycat")
            _a.assert_called_once_with(
                "Do you really want to delete this category "
                + "(ID = '15', name = 'mycat')?"
            )
            _c.assert_called_once_with(pBDB.cats, 15)
            _t.assert_called_once_with("PhysBiblio*")
            _s.assert_called_once_with(m, "Category deleted")
            _d.assert_called_once_with(
                "parentObject has no attribute 'recreateTable'", exc_info=True
            )

        ctw = CatsTreeWindow(p)
        with patch(
            "physbiblio.gui.catWindows.askYesNo", return_value=True, autospec=True
        ) as _a, patch(
            "physbiblio.database.Categories.delete", autospec=True
        ) as _c, patch(
            "PySide2.QtWidgets.QMainWindow.setWindowTitle", autospec=True
        ) as _t, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.recreateTable", autospec=True
        ) as _r:
            deleteCategory(ctw, m, 15, "mycat")
            _a.assert_called_once_with(
                "Do you really want to delete this category "
                + "(ID = '15', name = 'mycat')?"
            )
            _c.assert_called_once_with(pBDB.cats, 15)
            _t.assert_called_once_with("PhysBiblio*")
            _s.assert_called_once_with(m, "Category deleted")
            _r.assert_called_once_with(ctw)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestCatsModel(GUITestCase):
    """test the CatsModel class"""

    def setUp(self):
        """define common parameters for test use"""
        self.cats = [
            {"idCat": 0, "name": "main"},
            {"idCat": 1, "name": "test1"},
            {"idCat": 2, "name": "test2"},
            {"idCat": 3, "name": "test3"},
        ]
        with patch(
            "physbiblio.gui.commonClasses.catString",
            side_effect=["test2S", "test1S", "test3S", "mainS"],
            autospec=True,
        ):
            self.rootElements = [
                NamedElement(
                    0,
                    "main",
                    [
                        NamedElement(1, "test1", [NamedElement(2, "test2", [])]),
                        NamedElement(3, "test3", []),
                    ],
                )
            ]

    def test_init(self):
        """test init"""
        p = QWidget()
        cm = CatsModel(self.cats, self.rootElements, p)
        self.assertIsInstance(cm, TreeModel)
        self.assertEqual(cm.cats, self.cats)
        self.assertEqual(cm.rootElements, self.rootElements)
        self.assertEqual(cm.parentObj, p)
        self.assertIsInstance(cm.selectedCats, dict)
        self.assertIsInstance(cm.previousSaved, dict)
        self.assertEqual(cm.selectedCats, {0: False, 1: False, 2: False, 3: False})
        self.assertEqual(cm.previousSaved, {0: False, 1: False, 2: False, 3: False})

        with patch("logging.Logger.warning") as _l:
            cm = CatsModel(self.cats, self.rootElements, p, [15])
            _l.assert_called_once_with("Invalid idCat in previous selection: 15")

        with patch("logging.Logger.warning") as _l:
            cm = CatsModel(self.cats, self.rootElements, p, [1, 3])
            _l.assert_not_called()
        self.assertEqual(cm.selectedCats, {0: False, 1: True, 2: False, 3: True})
        self.assertEqual(cm.previousSaved, {0: False, 1: False, 2: False, 3: False})

        cm = CatsModel(
            self.cats,
            self.rootElements,
            parent=p,
            previous=[1, 3],
            multipleRecords=True,
        )
        self.assertEqual(cm.previousSaved, {0: False, 1: True, 2: False, 3: True})
        self.assertEqual(cm.selectedCats, {0: False, 1: "p", 2: False, 3: "p"})

    def test_getRootNodes(self):
        """test _getRootNodes"""
        p = QWidget()
        cm = CatsModel(self.cats, self.rootElements, p)
        par = cm._getRootNodes()
        self.assertIsInstance(par, list)
        self.assertEqual(len(par), 1)
        self.assertIsInstance(par[0], NamedNode)
        self.assertEqual(par[0].element, self.rootElements[0])
        self.assertEqual(par[0].row, 0)
        self.assertEqual(par[0].parentObj, None)

    def test_columnCount(self):
        """test columnCount"""
        cm = CatsModel([], [])
        self.assertEqual(cm.columnCount("a"), 1)

    def test_data(self):
        """test data"""
        cm = CatsModel(self.cats, self.rootElements)
        ix = cm.index(10, 0)
        self.assertEqual(cm.data(ix, Qt.CheckStateRole), None)
        ix = cm.index(0, 0)
        self.assertEqual(cm.data(ix, Qt.DisplayRole), "mainS")
        self.assertEqual(cm.data(ix, Qt.EditRole), "mainS")
        self.assertEqual(cm.data(ix, Qt.DecorationRole), None)

        self.assertEqual(cm.data(ix, Qt.CheckStateRole), None)
        p = QWidget()
        p.askCats = False
        cm = CatsModel(self.cats, self.rootElements, p)
        ix = cm.index(0, 0)
        self.assertEqual(cm.data(ix, Qt.CheckStateRole), None)
        p.askCats = True
        cm = CatsModel(self.cats, self.rootElements, p)
        ix = cm.index(0, 0)
        self.assertEqual(cm.data(ix, Qt.CheckStateRole), Qt.Unchecked)
        cm = CatsModel(self.cats, self.rootElements, p, [0])
        ix = cm.index(0, 0)
        self.assertEqual(cm.data(ix, Qt.CheckStateRole), Qt.Checked)
        cm = CatsModel(self.cats, self.rootElements, p, [0], True)
        ix = cm.index(0, 0)
        self.assertEqual(cm.data(ix, Qt.CheckStateRole), Qt.PartiallyChecked)
        self.assertEqual(cm.setData(ix, "abc", Qt.CheckStateRole), True)
        self.assertEqual(cm.data(ix, Qt.CheckStateRole), Qt.Unchecked)
        self.assertEqual(cm.setData(ix, Qt.Checked, Qt.CheckStateRole), True)
        self.assertEqual(cm.data(ix, Qt.CheckStateRole), Qt.Checked)

    def test_flags(self):
        """test flags"""
        cm = CatsModel([], [])
        with patch(
            "PySide2.QtCore.QModelIndex.isValid", return_value=False, autospec=True
        ) as _iv:
            self.assertEqual(cm.flags(QModelIndex()), Qt.NoItemFlags)
            _iv.assert_called_once_with()

        with patch(
            "PySide2.QtCore.QModelIndex.isValid", return_value=True, autospec=True
        ) as _iv, patch(
            "PySide2.QtCore.QModelIndex.column", return_value=1, autospec=True
        ) as _c:
            self.assertEqual(
                cm.flags(QModelIndex()), Qt.ItemIsEnabled | Qt.ItemIsSelectable
            )
            _iv.assert_called_once_with()
            _c.assert_called_once_with()

        with patch(
            "PySide2.QtCore.QModelIndex.isValid", return_value=True, autospec=True
        ) as _iv, patch(
            "PySide2.QtCore.QModelIndex.column", return_value=0, autospec=True
        ) as _c:
            self.assertEqual(
                cm.flags(QModelIndex()), Qt.ItemIsEnabled | Qt.ItemIsSelectable
            )
            _iv.assert_called_once_with()
            _c.assert_called_once_with()

        p = QWidget()
        p.askCats = False
        cm = CatsModel([], [], p)
        with patch(
            "PySide2.QtCore.QModelIndex.isValid", return_value=True, autospec=True
        ) as _iv, patch(
            "PySide2.QtCore.QModelIndex.column", return_value=0, autospec=True
        ) as _c:
            self.assertEqual(
                cm.flags(QModelIndex()), Qt.ItemIsEnabled | Qt.ItemIsSelectable
            )
            _iv.assert_called_once_with()
            _c.assert_called_once_with()

        p = QWidget()
        p.askCats = True
        cm = CatsModel([], [], p)
        with patch(
            "PySide2.QtCore.QModelIndex.isValid", return_value=True, autospec=True
        ) as _iv, patch(
            "PySide2.QtCore.QModelIndex.column", return_value=0, autospec=True
        ) as _c:
            self.assertEqual(
                cm.flags(QModelIndex()),
                Qt.ItemIsUserCheckable
                | Qt.ItemIsEditable
                | Qt.ItemIsEnabled
                | Qt.ItemIsSelectable,
            )
            _iv.assert_called_once_with()
            _c.assert_called_once_with()

    def test_headerData(self):
        """test headerData"""
        cm = CatsModel([], [])
        self.assertEqual(cm.headerData(0, Qt.Horizontal, Qt.DisplayRole), "Name")
        self.assertEqual(cm.headerData(1, Qt.Horizontal, Qt.DisplayRole), None)
        self.assertEqual(cm.headerData(0, Qt.Vertical, Qt.DisplayRole), None)
        self.assertEqual(cm.headerData(0, Qt.Horizontal, Qt.EditRole), None)

    def test_setData(self):
        """test setData"""

        def connectEmit(ix1, ix2):
            """used to test dataChanged.emit"""
            self.newEmit = ix1

        cm = CatsModel(self.cats, self.rootElements)
        ix = cm.index(10, 0)
        self.newEmit = False
        cm.dataChanged.connect(connectEmit)
        self.assertEqual(cm.setData(ix, "abc", Qt.CheckStateRole), False)
        self.assertEqual(self.newEmit, False)
        ix = cm.index(0, 0)
        self.assertEqual(cm.setData(ix, Qt.Checked, Qt.CheckStateRole), True)
        self.assertEqual(cm.previousSaved[0], False)
        self.assertEqual(cm.selectedCats[0], True)
        self.assertEqual(self.newEmit, ix)
        self.newEmit = False
        self.assertEqual(cm.setData(ix, "abc", Qt.CheckStateRole), True)
        self.assertEqual(cm.previousSaved[0], False)
        self.assertEqual(cm.selectedCats[0], False)
        self.assertEqual(self.newEmit, ix)

        cm = CatsModel(self.cats, self.rootElements, None, [0], True)
        ix = cm.index(0, 0)
        self.assertEqual(cm.setData(ix, "abc", Qt.EditRole), True)
        self.assertEqual(cm.previousSaved[0], True)
        self.assertEqual(cm.selectedCats[0], "p")
        self.assertEqual(cm.setData(ix, "abc", Qt.CheckStateRole), True)
        self.assertEqual(cm.previousSaved[0], False)
        self.assertEqual(cm.selectedCats[0], False)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestCatsTreeWindow(GUITestCase):
    """test the CatsTreeWindow class"""

    def setUp(self):
        """define common parameters for test use"""
        self.cats = [
            {"idCat": 0, "name": "main"},
            {"idCat": 1, "name": "test1"},
            {"idCat": 2, "name": "test2"},
            {"idCat": 3, "name": "test3"},
        ]
        self.cathier = {0: {1: {2: {}}, 3: {}}}
        with patch(
            "physbiblio.gui.commonClasses.catString",
            side_effect=[" 2: test2S", " 1: test1S", " 3: test3S", " 0: mainS"],
            autospec=True,
        ):
            self.rootElements = [
                NamedElement(
                    0,
                    "main",
                    [
                        NamedElement(1, "test1", [NamedElement(2, "test2", [])]),
                        NamedElement(3, "test3", []),
                    ],
                )
            ]

    def test_init(self):
        """test init"""
        p = QWidget()
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.createForm", autospec=True
        ) as _c:
            ctw = CatsTreeWindow(p)
            _c.assert_called_once_with(ctw)
        self.assertIsInstance(ctw, PBDialog)
        self.assertEqual(ctw.windowTitle(), "Categories")
        self.assertIsInstance(ctw.layout(), QVBoxLayout)
        self.assertEqual(ctw.layout(), ctw.currLayout)
        self.assertEqual(ctw.askCats, False)
        self.assertEqual(ctw.askForBib, None)
        self.assertEqual(ctw.askForExp, None)
        self.assertEqual(ctw.expButton, True)
        self.assertEqual(ctw.previous, [])
        self.assertEqual(ctw.single, False)
        self.assertEqual(ctw.multipleRecords, False)
        self.assertEqual(ctw.minimumWidth(), 400)
        self.assertEqual(ctw.minimumHeight(), 600)

        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.createForm", autospec=True
        ) as _c:
            ctw = CatsTreeWindow(
                parent=p,
                askCats="ac",
                askForBib="bib",
                askForExp="exp",
                expButton="eb",
                previous="pr",
                single="s",
                multipleRecords="mr",
            )
            _c.assert_called_once_with(ctw)
        self.assertIsInstance(ctw, PBDialog)
        self.assertEqual(ctw.windowTitle(), "Categories")
        self.assertIsInstance(ctw.layout(), QVBoxLayout)
        self.assertEqual(ctw.layout(), ctw.currLayout)
        self.assertEqual(ctw.askCats, "ac")
        self.assertEqual(ctw.askForBib, "bib")
        self.assertEqual(ctw.askForExp, "exp")
        self.assertEqual(ctw.expButton, "eb")
        self.assertEqual(ctw.previous, "pr")
        self.assertEqual(ctw.single, "s")
        self.assertEqual(ctw.multipleRecords, "mr")
        self.assertEqual(ctw.minimumWidth(), 400)
        self.assertEqual(ctw.minimumHeight(), 600)

    def test_populateAskCats(self):
        """test populateAskCats"""
        p = QWidget()
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.createForm", autospec=True
        ) as _c:
            ctw = CatsTreeWindow(parent=p, askCats=False)

        # test with askCats = False (nothing happens)
        self.assertTrue(ctw.populateAskCat())
        self.assertEqual(ctw.marked, [])
        self.assertFalse(hasattr(p, "selectedCats"))
        self.assertEqual(ctw.currLayout.count(), 0)

        # test with askCats = True and askForBib
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.createForm", autospec=True
        ) as _c:
            ctw = CatsTreeWindow(parent=p, askCats=True, askForBib="bib")
        # bibkey not in db
        with patch(
            "physbiblio.database.Entries.getByBibkey", return_value=[], autospec=True
        ) as _gbb, patch("logging.Logger.warning") as _w:
            self.assertEqual(ctw.populateAskCat(), None)
            _gbb.assert_called_once_with(pBDB.bibs, "bib", saveQuery=False)
            _w.assert_called_once_with(
                "The entry 'bib' is not in the database!", exc_info=True
            )
        self.assertEqual(ctw.marked, [])
        self.assertFalse(hasattr(p, "selectedCats"))
        self.assertEqual(ctw.currLayout.count(), 0)
        # dict has no "title" or "author"
        with patch(
            "physbiblio.database.Entries.getByBibkey",
            side_effect=[[{"inspire": None, "doi": None, "arxiv": None}]],
            autospec=True,
        ) as _gbb:
            self.assertEqual(ctw.populateAskCat(), True)
            _gbb.assert_called_once_with(pBDB.bibs, "bib", saveQuery=False)
            self.assertEqual(ctw.currLayout.count(), 1)
            self.assertIsInstance(ctw.layout().itemAt(0).widget(), PBLabel)
            self.assertEqual(
                ctw.layout().itemAt(0).widget().text(),
                "Mark categories for the following "
                + "entry:<br><b>key</b>:<br>bib<br>",
            )
        self.assertTrue(hasattr(ctw, "marked"))
        self.assertEqual(ctw.marked, [])
        self.assertTrue(hasattr(p, "selectedCats"))
        self.assertEqual(p.selectedCats, [])
        # no link exists
        ctw.cleanLayout()
        with patch(
            "physbiblio.database.Entries.getByBibkey",
            side_effect=[
                [
                    {
                        "author": "sg",
                        "title": "title",
                        "inspire": None,
                        "doi": None,
                        "arxiv": None,
                    }
                ]
            ],
            autospec=True,
        ) as _gbb:
            self.assertEqual(ctw.populateAskCat(), True)
            _gbb.assert_called_once_with(pBDB.bibs, "bib", saveQuery=False)
            self.assertEqual(ctw.currLayout.count(), 1)
            self.assertIsInstance(ctw.layout().itemAt(0).widget(), PBLabel)
            self.assertEqual(
                ctw.layout().itemAt(0).widget().text(),
                "Mark categories for the following "
                + "entry:<br><b>key</b>:<br>bib<br>"
                + "<b>author(s)</b>:<br>sg<br>"
                + "<b>title</b>:<br>title<br>",
            )
        # inspire exists
        ctw.cleanLayout()
        with patch(
            "physbiblio.database.Entries.getByBibkey",
            side_effect=[
                [
                    {
                        "author": "sg",
                        "title": "title",
                        "inspire": "1234",
                        "doi": "1/2/3",
                        "arxiv": "123456",
                    }
                ]
            ],
            autospec=True,
        ) as _gbb, patch(
            "physbiblio.view.ViewEntry.getLink",
            return_value="inspirelink",
            autospec=True,
        ) as _l:
            self.assertEqual(ctw.populateAskCat(), True)
            _gbb.assert_called_once_with(pBDB.bibs, "bib", saveQuery=False)
            _l.assert_called_once_with(pBView, "bib", "inspire")
            self.assertEqual(ctw.currLayout.count(), 1)
            self.assertIsInstance(ctw.layout().itemAt(0).widget(), PBLabel)
            self.assertEqual(
                ctw.layout().itemAt(0).widget().text(),
                "Mark categories for the following "
                + "entry:<br><b>key</b>:<br><a href='inspirelink'>bib</a><br>"
                + "<b>author(s)</b>:<br>sg<br>"
                + "<b>title</b>:<br>title<br>",
            )
        ctw.cleanLayout()
        # arxiv exists
        with patch(
            "physbiblio.database.Entries.getByBibkey",
            side_effect=[
                [
                    {
                        "author": "sg",
                        "title": "title",
                        "inspire": None,
                        "doi": "1/2/3",
                        "arxiv": "123456",
                    }
                ]
            ],
            autospec=True,
        ) as _gbb, patch(
            "physbiblio.view.ViewEntry.getLink", return_value="arxivlink", autospec=True
        ) as _l:
            self.assertEqual(ctw.populateAskCat(), True)
            _gbb.assert_called_once_with(pBDB.bibs, "bib", saveQuery=False)
            _l.assert_called_once_with(pBView, "bib", "arxiv")
            self.assertEqual(ctw.currLayout.count(), 1)
            self.assertIsInstance(ctw.layout().itemAt(0).widget(), PBLabel)
            self.assertEqual(
                ctw.layout().itemAt(0).widget().text(),
                "Mark categories for the following "
                + "entry:<br><b>key</b>:<br><a href='arxivlink'>bib</a><br>"
                + "<b>author(s)</b>:<br>sg<br>"
                + "<b>title</b>:<br>title<br>",
            )
        ctw.cleanLayout()
        # doi exists
        with patch(
            "physbiblio.database.Entries.getByBibkey",
            side_effect=[
                [
                    {
                        "author": "sg",
                        "title": "title",
                        "inspire": None,
                        "doi": "1/2/3",
                        "arxiv": "",
                    }
                ]
            ],
            autospec=True,
        ) as _gbb, patch(
            "physbiblio.view.ViewEntry.getLink", return_value="doilink", autospec=True
        ) as _l:
            self.assertEqual(ctw.populateAskCat(), True)
            _gbb.assert_called_once_with(pBDB.bibs, "bib", saveQuery=False)
            _l.assert_called_once_with(pBView, "bib", "doi")
            self.assertEqual(ctw.currLayout.count(), 1)
            self.assertIsInstance(ctw.layout().itemAt(0).widget(), PBLabel)
            self.assertEqual(
                ctw.layout().itemAt(0).widget().text(),
                "Mark categories for the following "
                + "entry:<br><b>key</b>:<br><a href='doilink'>bib</a><br>"
                + "<b>author(s)</b>:<br>sg<br>"
                + "<b>title</b>:<br>title<br>",
            )

        # test with askCats = True and askForExp
        p = QWidget()
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.createForm", autospec=True
        ) as _c:
            ctw = CatsTreeWindow(parent=p, askCats=True, askForExp="exp")
        # idExp not in db
        with patch(
            "physbiblio.database.Experiments.getByID", return_value=[], autospec=True
        ) as _gbi, patch("logging.Logger.warning") as _w:
            self.assertEqual(ctw.populateAskCat(), None)
            _gbi.assert_called_once_with(pBDB.exps, "exp")
            _w.assert_called_once_with(
                "The experiment ID exp is not in the database!", exc_info=True
            )
        self.assertEqual(ctw.marked, [])
        self.assertFalse(hasattr(p, "selectedCats"))
        self.assertEqual(ctw.currLayout.count(), 0)
        # dict has no "name" or "comments"
        with patch(
            "physbiblio.database.Experiments.getByID",
            return_value=[{"name": "name", "idExp": 9999}],
            autospec=True,
        ) as _gbi:
            self.assertEqual(ctw.populateAskCat(), True)
            _gbi.assert_called_once_with(pBDB.exps, "exp")
            self.assertEqual(ctw.currLayout.count(), 1)
            self.assertIsInstance(ctw.layout().itemAt(0).widget(), PBLabel)
            self.assertEqual(
                ctw.layout().itemAt(0).widget().text(),
                "Mark categories for the following "
                + "experiment:<br><b>id</b>:<br>exp<br>",
            )
        self.assertEqual(ctw.marked, [])
        self.assertTrue(hasattr(p, "selectedCats"))
        self.assertEqual(p.selectedCats, [])
        # full string
        ctw.cleanLayout()
        with patch(
            "physbiblio.database.Experiments.getByID",
            return_value=[{"name": "name", "idExp": 9999, "comments": "comm"}],
            autospec=True,
        ) as _gbi:
            self.assertEqual(ctw.populateAskCat(), True)
            _gbi.assert_called_once_with(pBDB.exps, "exp")
            self.assertEqual(ctw.currLayout.count(), 1)
            self.assertIsInstance(ctw.layout().itemAt(0).widget(), PBLabel)
            self.assertEqual(
                ctw.layout().itemAt(0).widget().text(),
                "Mark categories for the following "
                + "experiment:<br><b>id</b>:<br>exp<br>"
                + "<b>name</b>:<br>name<br>"
                + "<b>comments</b>:<br>comm<br>",
            )

        # test with no askForBib, askForExp
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.createForm", autospec=True
        ) as _c:
            ctw = CatsTreeWindow(parent=p, askCats=True, single=True)
        self.assertEqual(ctw.populateAskCat(), True)
        self.assertEqual(ctw.currLayout.count(), 1)
        self.assertIsInstance(ctw.layout().itemAt(0).widget(), PBLabel)
        self.assertEqual(
            ctw.layout().itemAt(0).widget().text(),
            "Select the desired category (only the first one will be considered):",
        )

        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.createForm", autospec=True
        ) as _c:
            ctw = CatsTreeWindow(parent=p, askCats=True, single=False)
        self.assertEqual(ctw.populateAskCat(), True)
        self.assertEqual(ctw.currLayout.count(), 1)
        self.assertIsInstance(ctw.layout().itemAt(0).widget(), PBLabel)
        self.assertEqual(
            ctw.layout().itemAt(0).widget().text(), "Select the desired categories:"
        )

    def test_onCancel(self):
        """test onCancel"""
        ctw = CatsTreeWindow()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            ctw.onCancel()
        self.assertFalse(ctw.result)

    def test_onOk(self):
        """test onOk"""
        p = QWidget()
        with patch(
            "physbiblio.database.Categories.getHier",
            return_value=self.cathier,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.database.Categories.getAll",
            return_value=self.cats,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.gui.catWindows.CatsTreeWindow._populateTree",
            return_value=self.rootElements[0],
            autospec=True,
        ) as _pt:
            ctw = CatsTreeWindow(p)
        self.assertFalse(hasattr(p, "selectedCats"))
        self.assertFalse(hasattr(p, "previousUnchanged"))
        ctw.root_model.selectedCats[0] = True
        ctw.root_model.selectedCats[3] = True
        ctw.root_model.previousSaved[0] = True
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            ctw.onOk()
            _c.assert_called_once_with()
        self.assertEqual(hasattr(p, "selectedCats"), True)
        self.assertEqual(p.selectedCats, [0, 3])
        self.assertEqual(p.previousUnchanged, [0])
        self.assertEqual(ctw.result, "Ok")

        p = QWidget()
        with patch(
            "physbiblio.database.Categories.getHier",
            return_value=self.cathier,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.database.Categories.getAll",
            return_value=self.cats,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.gui.catWindows.CatsTreeWindow._populateTree",
            return_value=self.rootElements[0],
            autospec=True,
        ) as _pt:
            ctw = CatsTreeWindow(p, single=True)
        self.assertFalse(hasattr(p, "selectedCats"))
        self.assertFalse(hasattr(p, "previousUnchanged"))
        ctw.root_model.selectedCats[0] = True
        ctw.root_model.selectedCats[1] = False
        ctw.root_model.selectedCats[2] = False
        ctw.root_model.previousSaved[1] = False
        ctw.root_model.previousSaved[2] = False
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            ctw.onOk(exps=True)
            _c.assert_called_once_with()
        self.assertEqual(hasattr(p, "selectedCats"), True)
        self.assertEqual(p.selectedCats, [0])
        self.assertEqual(p.previousUnchanged, [])
        self.assertEqual(ctw.result, "Exps")

    def test_changeFilter(self):
        """test changeFilter"""
        p = QWidget()
        ctw = CatsTreeWindow(p)
        with patch("PySide2.QtWidgets.QTreeView.expandAll", autospec=True) as _e:
            ctw.changeFilter("abc")
            _e.assert_called_once_with()
        self.assertEqual(ctw.proxyModel.filterRegExp().pattern(), "abc")
        with patch("PySide2.QtWidgets.QTreeView.expandAll", autospec=True) as _e:
            ctw.changeFilter(123)
            _e.assert_called_once_with()
        self.assertEqual(ctw.proxyModel.filterRegExp().pattern(), "123")

    def test_onAskExps(self):
        """test onAskExps"""
        p = QWidget()
        ctw = CatsTreeWindow(p)
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.onOk", autospec=True
        ) as _oo:
            ctw.onAskExps()
            _oo.assert_called_once_with(ctw, exps=True)

    def test_onNewCat(self):
        """test onNewCat"""
        p = QWidget()
        ctw = CatsTreeWindow(p)
        with patch("physbiblio.gui.catWindows.editCategory", autospec=True) as _ec:
            ctw.onNewCat()
            _ec.assert_called_once_with(ctw, p)

    def test_keyPressEvent(self):
        """test keyPressEvent"""
        ctw = CatsTreeWindow()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _oc:
            QTest.keyPress(ctw, "a")
            _oc.assert_not_called()
            QTest.keyPress(ctw, Qt.Key_Enter)
            _oc.assert_not_called()
            QTest.keyPress(ctw, Qt.Key_Escape)
            self.assertEqual(_oc.call_count, 1)

    def test_createForm(self):
        """test createForm"""
        p = QWidget()
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.createForm", autospec=True
        ):
            ctw = CatsTreeWindow(p)
        with patch(
            "physbiblio.database.Categories.getHier",
            return_value=self.cathier,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.database.Categories.getAll",
            return_value=self.cats,
            autospec=True,
        ) as _ga, patch(
            "physbiblio.gui.catWindows.CatsTreeWindow._populateTree",
            return_value=self.rootElements[0],
            autospec=True,
        ) as _pt, patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.populateAskCat", autospec=True
        ) as _pac, patch(
            "PySide2.QtWidgets.QTreeView.expandAll", autospec=True
        ) as _ea:
            ctw.createForm()
            _pac.assert_called_once_with(ctw)
            _gh.assert_called_once_with(pBDB.cats)
            _ga.assert_called_once_with(pBDB.cats)
            _pt.assert_called_once_with(ctw, {1: {2: {}}, 3: {}}, 0)
            _ea.assert_called_once_with()
        self.assertIsInstance(ctw.layout().itemAt(0).widget(), QLineEdit)
        self.assertEqual(ctw.layout().count(), 3)
        self.assertEqual(ctw.filterInput, ctw.layout().itemAt(0).widget())
        self.assertEqual(ctw.filterInput.placeholderText(), "Filter categories")
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.changeFilter", autospec=True
        ) as _cf:
            ctw.filterInput.textChanged.emit("a")
            _cf.assert_called_once_with(ctw, "a")

        self.assertIsInstance(ctw.tree, QTreeView)
        self.assertIsInstance(ctw.layout().itemAt(1).widget(), QTreeView)
        self.assertEqual(ctw.tree, ctw.layout().itemAt(1).widget())
        self.assertTrue(ctw.tree.hasMouseTracking())
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.handleItemEntered", autospec=True
        ) as _f:
            ctw.tree.entered.emit(QModelIndex())
            _f.assert_called_once_with(ctw, QModelIndex())
        self.assertFalse(ctw.tree.expandsOnDoubleClick())
        qmi = QModelIndex()
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.cellDoubleClick", autospec=True
        ) as _dc:
            ctw.tree.doubleClicked.emit(qmi)
            _dc.assert_called_once_with(ctw, qmi)

        self.assertIsInstance(ctw.root_model, CatsModel)
        self.assertEqual(ctw.root_model.cats, self.cats)
        self.assertEqual(ctw.root_model.rootElements, self.rootElements)
        self.assertEqual(ctw.root_model.parentObj, ctw)
        self.assertEqual(
            ctw.root_model.selectedCats, {0: False, 1: False, 2: False, 3: False}
        )
        self.assertIsInstance(ctw.proxyModel, LeafFilterProxyModel)
        self.assertEqual(ctw.proxyModel.sourceModel(), ctw.root_model)
        self.assertEqual(ctw.proxyModel.filterCaseSensitivity(), Qt.CaseInsensitive)
        self.assertEqual(ctw.proxyModel.sortCaseSensitivity(), Qt.CaseInsensitive)
        self.assertEqual(ctw.proxyModel.filterKeyColumn(), -1)
        self.assertEqual(ctw.tree.model(), ctw.proxyModel)
        self.assertEqual(ctw.tree.isHeaderHidden(), True)
        self.assertIsInstance(ctw.layout().itemAt(2).widget(), QPushButton)
        self.assertEqual(ctw.layout().itemAt(2).widget(), ctw.newCatButton)
        self.assertEqual(ctw.newCatButton.text(), "Add new category")
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.onNewCat", autospec=True
        ) as _f:
            QTest.mouseClick(ctw.newCatButton, Qt.LeftButton)
            _f.assert_called_once_with(ctw)

        # repeat with askCats
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.createForm", autospec=True
        ):
            ctw = CatsTreeWindow(p, askCats=True)
        with patch(
            "physbiblio.database.Categories.getHier",
            return_value=self.cathier,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.database.Categories.getAll",
            return_value=self.cats,
            autospec=True,
        ) as _ga, patch(
            "physbiblio.gui.catWindows.CatsTreeWindow._populateTree",
            return_value=self.rootElements[0],
            autospec=True,
        ) as _pt, patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.populateAskCat", autospec=True
        ) as _pac, patch(
            "PySide2.QtWidgets.QTreeView.expandAll", autospec=True
        ) as _ea:
            ctw.createForm()
            _pac.assert_called_once_with(ctw)
            _gh.assert_called_once_with(pBDB.cats)
            _ga.assert_called_once_with(pBDB.cats)
            _pt.assert_called_once_with(ctw, {1: {2: {}}, 3: {}}, 0)
            _ea.assert_called_once_with()
        self.assertIsInstance(ctw.layout().itemAt(0).widget(), QLineEdit)
        self.assertEqual(ctw.layout().count(), 6)
        self.assertEqual(ctw.layout().itemAt(0).widget(), ctw.filterInput)
        self.assertIsInstance(ctw.layout().itemAt(1).widget(), QTreeView)
        self.assertEqual(ctw.layout().itemAt(1).widget(), ctw.tree)
        self.assertIsInstance(ctw.layout().itemAt(2).widget(), QPushButton)
        self.assertEqual(ctw.layout().itemAt(2).widget(), ctw.newCatButton)
        self.assertIsInstance(ctw.layout().itemAt(3).widget(), QPushButton)
        self.assertEqual(ctw.layout().itemAt(3).widget(), ctw.acceptButton)
        self.assertEqual(ctw.acceptButton.text(), "OK")
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.onOk", autospec=True
        ) as _f:
            QTest.mouseClick(ctw.acceptButton, Qt.LeftButton)
            _f.assert_called_once_with(ctw, False)
        self.assertIsInstance(ctw.layout().itemAt(4).widget(), QPushButton)
        self.assertEqual(ctw.layout().itemAt(4).widget(), ctw.expsButton)
        self.assertEqual(ctw.expsButton.text(), "Ask experiments")
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.onAskExps", autospec=True
        ) as _f:
            QTest.mouseClick(ctw.expsButton, Qt.LeftButton)
            _f.assert_called_once_with(ctw)
        self.assertIsInstance(ctw.layout().itemAt(5).widget(), QPushButton)
        self.assertEqual(ctw.layout().itemAt(5).widget(), ctw.cancelButton)
        self.assertEqual(ctw.cancelButton.text(), "Cancel")
        self.assertTrue(ctw.cancelButton.autoDefault())
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.onCancel", autospec=True
        ) as _f:
            QTest.mouseClick(ctw.cancelButton, Qt.LeftButton)
            _f.assert_called_once_with(ctw)

        # repeat without expButton
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.createForm", autospec=True
        ):
            ctw = CatsTreeWindow(p, askCats=True, expButton=False)
        with patch(
            "physbiblio.database.Categories.getHier",
            return_value=self.cathier,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.database.Categories.getAll",
            return_value=self.cats,
            autospec=True,
        ) as _ga, patch(
            "physbiblio.gui.catWindows.CatsTreeWindow._populateTree",
            return_value=self.rootElements[0],
            autospec=True,
        ) as _pt, patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.populateAskCat", autospec=True
        ) as _pac, patch(
            "PySide2.QtWidgets.QTreeView.expandAll", autospec=True
        ) as _ea:
            ctw.createForm()
            _pac.assert_called_once_with(ctw)
            _gh.assert_called_once_with(pBDB.cats)
            _ga.assert_called_once_with(pBDB.cats)
            _pt.assert_called_once_with(ctw, {1: {2: {}}, 3: {}}, 0)
            _ea.assert_called_once_with()
        self.assertEqual(ctw.layout().count(), 5)
        self.assertIsInstance(ctw.layout().itemAt(0).widget(), QLineEdit)
        self.assertEqual(ctw.layout().itemAt(0).widget(), ctw.filterInput)
        self.assertIsInstance(ctw.layout().itemAt(1).widget(), QTreeView)
        self.assertEqual(ctw.layout().itemAt(1).widget(), ctw.tree)
        self.assertIsInstance(ctw.layout().itemAt(2).widget(), QPushButton)
        self.assertEqual(ctw.layout().itemAt(2).widget(), ctw.newCatButton)
        self.assertIsInstance(ctw.layout().itemAt(3).widget(), QPushButton)
        self.assertEqual(ctw.layout().itemAt(3).widget(), ctw.acceptButton)
        self.assertIsInstance(ctw.layout().itemAt(4).widget(), QPushButton)
        self.assertEqual(ctw.layout().itemAt(4).widget(), ctw.cancelButton)

        # repeat with previous and multipleRecords
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.createForm", autospec=True
        ):
            ctw = CatsTreeWindow(
                p, askCats=True, expButton=False, previous=[1, 2], multipleRecords=True
            )
        with patch(
            "physbiblio.database.Categories.getHier",
            return_value=self.cathier,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.database.Categories.getAll",
            return_value=self.cats,
            autospec=True,
        ) as _ga, patch(
            "physbiblio.gui.catWindows.CatsTreeWindow._populateTree",
            return_value=self.rootElements[0],
            autospec=True,
        ) as _pt, patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.populateAskCat", autospec=True
        ) as _pac, patch(
            "PySide2.QtWidgets.QTreeView.expandAll", autospec=True
        ) as _ea:
            ctw.createForm()
            _pac.assert_called_once_with(ctw)
            _gh.assert_called_once_with(pBDB.cats)
            _ga.assert_called_once_with(pBDB.cats)
            _pt.assert_called_once_with(ctw, {1: {2: {}}, 3: {}}, 0)
            _ea.assert_called_once_with()
        self.assertEqual(
            ctw.root_model.selectedCats, {0: False, 1: "p", 2: "p", 3: False}
        )
        self.assertEqual(
            ctw.root_model.previousSaved, {0: False, 1: True, 2: True, 3: False}
        )
        self.assertEqual(ctw.layout().count(), 5)
        self.assertIsInstance(ctw.layout().itemAt(0).widget(), QLineEdit)
        self.assertEqual(ctw.layout().itemAt(0).widget(), ctw.filterInput)
        self.assertIsInstance(ctw.layout().itemAt(1).widget(), QTreeView)
        self.assertEqual(ctw.layout().itemAt(1).widget(), ctw.tree)
        self.assertIsInstance(ctw.layout().itemAt(2).widget(), QPushButton)
        self.assertEqual(ctw.layout().itemAt(2).widget(), ctw.newCatButton)
        self.assertIsInstance(ctw.layout().itemAt(3).widget(), QPushButton)
        self.assertEqual(ctw.layout().itemAt(3).widget(), ctw.acceptButton)
        self.assertIsInstance(ctw.layout().itemAt(4).widget(), QPushButton)
        self.assertEqual(ctw.layout().itemAt(4).widget(), ctw.cancelButton)

    def test_populateTree(self):
        """test _populateTree"""
        p = QWidget()
        ctw = CatsTreeWindow(p)
        with patch(
            "physbiblio.database.Categories.getByID",
            side_effect=[
                [{"idCat": 0, "name": "main"}],
                [{"idCat": 1, "name": "test1"}],
                [{"idCat": 3, "name": "test3"}],
                [{"idCat": 1, "name": "test1"}],
                [{"idCat": 2, "name": "test2"}],
                [{"idCat": 2, "name": "test2"}],
                [{"idCat": 2, "name": "test2"}],
                [{"idCat": 1, "name": "test1"}],
                [{"idCat": 3, "name": "test3"}],
                [{"idCat": 3, "name": "test3"}],
                [{"idCat": 0, "name": "test0"}],
                [{"idCat": 0, "name": "test0"}],
            ],
            autospec=True,
        ):
            pt = ctw._populateTree(self.cathier[0], 0)
        self.assertIsInstance(pt, NamedElement)
        self.assertEqual(pt.name, "main")
        self.assertEqual(pt.idCat, 0)
        self.assertIsInstance(pt.subelements, list)
        self.assertEqual(len(pt.subelements), 2)
        self.assertIsInstance(pt.subelements[0], NamedElement)
        self.assertEqual(pt.subelements[0].name, "test1")
        self.assertEqual(pt.subelements[0].idCat, 1)
        self.assertIsInstance(pt.subelements[0].subelements, list)
        self.assertEqual(len(pt.subelements[0].subelements), 1)
        self.assertIsInstance(pt.subelements[1], NamedElement)
        self.assertEqual(pt.subelements[1].name, "test3")
        self.assertEqual(pt.subelements[1].idCat, 3)
        self.assertIsInstance(pt.subelements[1].subelements, list)
        self.assertEqual(len(pt.subelements[1].subelements), 0)
        self.assertIsInstance(pt.subelements[0].subelements[0], NamedElement)
        self.assertEqual(pt.subelements[0].subelements[0].name, "test2")
        self.assertEqual(pt.subelements[0].subelements[0].idCat, 2)
        self.assertIsInstance(pt.subelements[0].subelements[0].subelements, list)
        self.assertEqual(len(pt.subelements[0].subelements[0].subelements), 0)

    def test_handleItemEntered(self):
        """test handleItemEntered"""
        p = QWidget()
        with patch(
            "physbiblio.database.Categories.getHier",
            return_value=self.cathier,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.database.Categories.getAll",
            return_value=self.cats,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.gui.catWindows.CatsTreeWindow._populateTree",
            return_value=self.rootElements[0],
            autospec=True,
        ) as _pt:
            ctw = CatsTreeWindow(p)
        ix = ctw.proxyModel.index(0, 0)
        with patch("logging.Logger.exception") as _l, patch(
            "PySide2.QtCore.QTimer.start", autospec=True
        ) as _st, patch("PySide2.QtWidgets.QToolTip.showText") as _sh, patch(
            "physbiblio.database.Categories.getByID", return_value=[], autospec=True
        ) as _gbi:
            self.assertEqual(ctw.handleItemEntered(ix), None)
            _l.assert_called_once_with("Failed in finding category")
            _gbi.assert_called_once_with(pBDB.cats, "0")
            _st.assert_not_called()
            _sh.assert_not_called()
        with patch("logging.Logger.exception") as _l, patch(
            "PySide2.QtCore.QTimer.start", autospec=True
        ) as _st, patch("PySide2.QtWidgets.QToolTip.showText") as _sh, patch(
            "physbiblio.database.Categories.getByID",
            return_value=[{"idCat": 0, "name": "main"}],
            autospec=True,
        ) as _gbi, patch(
            "physbiblio.database.CatsEntries.countByCat", return_value=33, autospec=True
        ) as _cb, patch(
            "physbiblio.database.CatsExps.countByCat", return_value=12, autospec=True
        ) as _ce:
            position = QCursor.pos()
            self.assertEqual(ctw.handleItemEntered(ix), None)
            _l.assert_not_called()
            self.assertIsInstance(ctw.timer, QTimer)
            self.assertTrue(ctw.timer.isSingleShot())
            _gbi.assert_called_once_with(pBDB.cats, "0")
            _st.assert_called_once_with(500)
            _sh.assert_not_called()
            ctw.timer.timeout.emit()
            _sh.assert_called_once_with(
                position,
                "0: main\nCorresponding entries: 33\nAssociated experiments: 12",
                ctw.tree.viewport(),
                ctw.tree.visualRect(ix),
                3000,
            )
        with patch("logging.Logger.exception") as _l, patch(
            "PySide2.QtCore.QTimer.start", autospec=True
        ) as _st, patch("PySide2.QtWidgets.QToolTip.showText") as _sh, patch(
            "physbiblio.database.Categories.getByID",
            return_value=[{"idCat": 0, "name": "main"}],
            autospec=True,
        ) as _gbi, patch(
            "physbiblio.database.CatsEntries.countByCat", return_value=33, autospec=True
        ) as _cb, patch(
            "physbiblio.database.CatsExps.countByCat", return_value=12, autospec=True
        ) as _ce:
            self.assertEqual(ctw.handleItemEntered(ix), None)
            _sh.assert_called_once_with(QCursor.pos(), "", ctw.tree.viewport())

    def test_contextMenuEvent(self):
        """test contextMenuEvent"""
        p = MainWindow(testing=True)
        position = QCursor.pos()
        ev = QMouseEvent(
            QEvent.MouseButtonPress,
            position,
            Qt.RightButton,
            Qt.NoButton,
            Qt.NoModifier,
        )
        with patch(
            "physbiblio.database.Categories.getHier",
            return_value=self.cathier,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.database.Categories.getAll",
            return_value=self.cats,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.gui.catWindows.CatsTreeWindow._populateTree",
            return_value=self.rootElements[0],
            autospec=True,
        ) as _pt:
            ctw = CatsTreeWindow(p)
        mm = PBMenu()
        mm.exec_ = MagicMock()
        with patch(
            "PySide2.QtWidgets.QTreeView.selectedIndexes",
            return_value=[QModelIndex()],
            autospec=True,
        ) as _si, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rmc, patch(
            "physbiblio.gui.catWindows.PBMenu",
            return_value=mm,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _mm, patch(
            "physbiblio.gui.catWindows.editCategory", autospec=True
        ) as _ec, patch(
            "physbiblio.gui.catWindows.deleteCategory", autospec=True
        ) as _dc:
            ctw.contextMenuEvent(ev)
        self.assertEqual(ctw.menu, None)
        with patch(
            "PySide2.QtWidgets.QTreeView.selectedIndexes",
            return_value=[ctw.tree.indexAt(QPoint(0, 0))],
            autospec=True,
        ) as _si, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rmc, patch(
            "physbiblio.gui.catWindows.PBMenu",
            return_value=mm,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _mm, patch(
            "physbiblio.gui.catWindows.editCategory", autospec=True
        ) as _ec, patch(
            "physbiblio.gui.catWindows.deleteCategory", autospec=True
        ) as _dc, patch(
            "physbiblio.gui.commonClasses.PBMenu.fillMenu", autospec=True
        ) as _f:
            ctw.contextMenuEvent(ev)
            _f.assert_called_once_with(ctw.menu)
            _rmc.assert_not_called()
            _ec.assert_not_called()
            _dc.assert_not_called()

            self.assertIsInstance(ctw.menu, PBMenu)
            self.assertIsInstance(ctw.menu.possibleActions, list)
            self.assertEqual(len(ctw.menu.possibleActions), 9)
            self.assertEqual(ctw.menu.possibleActions[1], None)
            self.assertEqual(ctw.menu.possibleActions[4], None)
            self.assertEqual(ctw.menu.possibleActions[7], None)

            for ix, tit, en in [
                [0, "--Category: mainS--", False],
                [2, "Open list of corresponding entries", True],
                [3, "Open in new tab", True],
                [5, "Modify", True],
                [6, "Delete", True],
                [8, "Add subcategory", True],
            ]:
                act = ctw.menu.possibleActions[ix]
                self.assertIsInstance(act, QAction)
                self.assertEqual(act.text(), tit)
                self.assertEqual(act.isEnabled(), en)

            mm.exec_ = lambda x, i=0: mm.possibleActions[i]
            ctw.contextMenuEvent(ev)
            _rmc.assert_not_called()
            _ec.assert_not_called()
            _dc.assert_not_called()

            mm.exec_ = lambda x, i=2: mm.possibleActions[i]
            with patch(
                "physbiblio.database.Entries.getByCat",
                return_value=["a"],
                autospec=True,
            ) as _ffd:
                ctw.contextMenuEvent(ev)
                _ffd.assert_called_once_with(pBDB.bibs, "0")
            _rmc.assert_called_once_with(p, ["a"])
            _ec.assert_not_called()
            _dc.assert_not_called()
            _rmc.reset_mock()

            mm.exec_ = lambda x, i=3: mm.possibleActions[i]
            with patch(
                "physbiblio.database.Entries.getByCat",
                return_value=["a"],
                autospec=True,
            ) as _ffd:
                ctw.contextMenuEvent(ev)
                _ffd.assert_called_once_with(pBDB.bibs, "0")
            _rmc.assert_called_once_with(p, ["a"], newTab="mainS")
            _ec.assert_not_called()
            _dc.assert_not_called()
            _rmc.reset_mock()

            mm.exec_ = lambda x, i=5: mm.possibleActions[i]
            with patch(
                "physbiblio.database.Entries.getByCat",
                return_value=["a"],
                autospec=True,
            ) as _ffd:
                ctw.contextMenuEvent(ev)
            _rmc.assert_not_called()
            _ec.assert_called_once_with(ctw, p, "0")
            _dc.assert_not_called()
            _ec.reset_mock()

            mm.exec_ = lambda x, i=6: mm.possibleActions[i]
            with patch(
                "physbiblio.database.Entries.getByCat",
                return_value=["a"],
                autospec=True,
            ) as _ffd:
                ctw.contextMenuEvent(ev)
            _rmc.assert_not_called()
            _ec.assert_not_called()
            _dc.assert_called_once_with(ctw, p, "0", "mainS")
            _dc.reset_mock()

            mm.exec_ = lambda x, i=8: mm.possibleActions[i]
            with patch(
                "physbiblio.database.Entries.getByCat",
                return_value=["a"],
                autospec=True,
            ) as _ffd:
                ctw.contextMenuEvent(ev)
            _rmc.assert_not_called()
            _ec.assert_called_once_with(ctw, p, useParentCat="0")
            _dc.assert_not_called()

        with patch(
            "PySide2.QtWidgets.QTreeView.selectedIndexes",
            return_value=[],
            autospec=True,
        ) as _si, patch("logging.Logger.debug") as _d, patch(
            "PySide2.QtCore.QModelIndex.isValid", return_value=False, autospec=True
        ) as _iv:
            ctw.contextMenuEvent(ev)
            _si.assert_called_once_with()
            _d.assert_called_once_with("Click on missing index")
            _iv.assert_not_called()

    def test_cellDoubleClick(self):
        """test cellDoubleClick"""
        p = MainWindow(testing=True)
        ctw = CatsTreeWindow(p)
        ix = ctw.proxyModel.index(0, 0)
        with patch(
            "PySide2.QtCore.QModelIndex.isValid", return_value=False, autospec=True
        ) as _iv, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rmc:
            self.assertEqual(ctw.cellDoubleClick(ix), None)
            _iv.assert_called_once_with()
            _rmc.assert_not_called()
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rmc, patch(
            "physbiblio.database.Entries.getByCat", return_value=["a"], autospec=True
        ) as _ffd:
            self.assertEqual(ctw.cellDoubleClick(ix), None)
            _rmc.assert_called_once_with(ctw.parent(), ["a"])
            _ffd.assert_called_once_with(pBDB.bibs, "0")

    def test_recreateTable(self):
        """test recreateTable"""
        ctw = CatsTreeWindow()
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.cleanLayout", autospec=True
        ) as _c1, patch(
            "physbiblio.gui.catWindows.CatsTreeWindow.createForm", autospec=True
        ) as _c2:
            ctw.recreateTable()
            _c1.assert_called_once_with(ctw)
            _c2.assert_called_once_with(ctw)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestEditCategoryDialog(GUITestCase):
    """test the EditCategoryDialog class"""

    def test_init(self):
        """test init"""
        p = QWidget()
        with patch(
            "physbiblio.gui.catWindows.EditObjectWindow.__init__",
            return_value=None,
            autospec=True,
        ) as _i, patch(
            "physbiblio.gui.catWindows.EditCategoryDialog.createForm", autospec=True
        ) as _c:
            ecd = EditCategoryDialog(p)
            _i.assert_called_once_with(ecd, p)
            _c.assert_called_once_with(ecd)
        ecd = EditCategoryDialog(p)
        self.assertIsInstance(ecd, EditObjectWindow)
        self.assertEqual(ecd.parent(), p)
        self.assertIsInstance(ecd.data, dict)
        for k in pBDB.tableCols["categories"]:
            self.assertEqual(ecd.data[k], "")
        self.assertIsInstance(ecd.selectedCats, list)
        self.assertEqual(ecd.selectedCats, [0])

        cat = {
            "idCat": 15,
            "parentCat": 1,
            "description": "desc",
            "comments": "no comment",
            "ord": 0,
            "name": "mycat",
        }
        with patch(
            "physbiblio.database.Categories.getParent",
            return_value=[[1]],
            autospec=True,
        ) as _p:
            ecd = EditCategoryDialog(p, cat)
            _p.assert_called_once_with(pBDB.cats, 15)
        for k in pBDB.tableCols["categories"]:
            self.assertEqual(ecd.data[k], cat[k])
        self.assertIsInstance(ecd.selectedCats, list)
        self.assertEqual(ecd.selectedCats, [1])
        with patch(
            "physbiblio.database.Categories.getParent", return_value=1, autospec=True
        ) as _p:
            ecd = EditCategoryDialog(parent=p, category=cat, useParentCat=14)
            _p.assert_not_called()
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
        ecd = EditCategoryDialog(p)
        sc = CatsTreeWindow(
            parent=ecd, askCats=True, expButton=False, single=True, previous=[0]
        )
        sc.exec_ = MagicMock()
        sc.onCancel()
        txt = ecd.textValues["parentCat"].text()
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow",
            return_value=sc,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            ecd.onAskParent()
            _i.assert_called_once_with(
                parent=ecd,
                askCats=True,
                expButton=False,
                single=True,
                previous=ecd.selectedCats,
            )
        self.assertEqual(ecd.textValues["parentCat"].text(), "0 - Main")

        sc = CatsTreeWindow(
            parent=ecd, askCats=True, expButton=False, single=True, previous=[1]
        )
        sc.exec_ = MagicMock()
        sc.onOk()
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow",
            return_value=sc,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            ecd.onAskParent()
            _i.assert_called_once_with(
                parent=ecd,
                askCats=True,
                expButton=False,
                single=True,
                previous=ecd.selectedCats,
            )
        self.assertEqual(ecd.textValues["parentCat"].text(), "1 - Tags")

        sc = CatsTreeWindow(
            parent=ecd, askCats=True, expButton=False, single=True, previous=[0, 1]
        )
        sc.exec_ = MagicMock()
        sc.onOk()
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow",
            return_value=sc,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            ecd.onAskParent()
            _i.assert_called_once_with(
                parent=ecd,
                askCats=True,
                expButton=False,
                single=True,
                previous=ecd.selectedCats,
            )
        self.assertEqual(ecd.textValues["parentCat"].text(), "1 - Tags")

        sc = CatsTreeWindow(
            parent=ecd, askCats=True, expButton=False, single=True, previous=[]
        )
        sc.exec_ = MagicMock()
        sc.onOk()
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow",
            return_value=sc,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            ecd.onAskParent()
            _i.assert_called_once_with(
                parent=ecd,
                askCats=True,
                expButton=False,
                single=True,
                previous=ecd.selectedCats,
            )
        self.assertEqual(ecd.textValues["parentCat"].text(), "Select parent")

        with patch("logging.Logger.warning") as _l:
            sc = CatsTreeWindow(
                parent=ecd, askCats=True, expButton=False, single=True, previous=[9999]
            )
            _l.assert_called_once_with("Invalid idCat in previous selection: 9999")
        sc.exec_ = MagicMock()
        sc.onOk()
        with patch(
            "physbiblio.gui.catWindows.CatsTreeWindow",
            return_value=sc,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i, patch("logging.Logger.warning") as _l:
            ecd.onAskParent()
            _i.assert_called_once_with(
                parent=ecd,
                askCats=True,
                expButton=False,
                single=True,
                previous=ecd.selectedCats,
            )
        self.assertEqual(ecd.textValues["parentCat"].text(), "Select parent")

    def test_createForm(self):
        """test createForm"""
        p = QWidget()
        ncf = (len(pBDB.tableCols["categories"]) - 1) * 2 + 1
        ecd = EditCategoryDialog(p)
        self.assertEqual(ecd.windowTitle(), "Edit category")
        self.assertEqual(ecd.layout().itemAtPosition(0, 0), None)
        self.assertEqual(ecd.layout().itemAtPosition(0, 1), None)

        self.assertIsInstance(ecd.layout().itemAtPosition(1, 0).widget(), PBLabel)
        self.assertEqual(
            ecd.layout().itemAtPosition(1, 0).widget().text(),
            pBDB.descriptions["categories"]["name"],
        )
        self.assertIsInstance(ecd.layout().itemAtPosition(1, 1).widget(), PBLabel)
        self.assertEqual(ecd.layout().itemAtPosition(1, 1).widget().text(), "(name)")
        self.assertIsInstance(ecd.textValues["name"], QLineEdit)
        self.assertEqual(
            ecd.textValues["name"], ecd.layout().itemAtPosition(2, 0).widget()
        )
        self.assertEqual(ecd.textValues["name"].text(), "")

        self.assertIsInstance(ecd.layout().itemAtPosition(3, 0).widget(), PBLabel)
        self.assertEqual(
            ecd.layout().itemAtPosition(3, 0).widget().text(),
            pBDB.descriptions["categories"]["description"],
        )
        self.assertIsInstance(ecd.layout().itemAtPosition(3, 1).widget(), PBLabel)
        self.assertEqual(
            ecd.layout().itemAtPosition(3, 1).widget().text(), "(description)"
        )
        self.assertIsInstance(ecd.textValues["description"], QLineEdit)
        self.assertEqual(
            ecd.textValues["description"], ecd.layout().itemAtPosition(4, 0).widget()
        )
        self.assertEqual(ecd.textValues["description"].text(), "")

        self.assertIsInstance(ecd.layout().itemAtPosition(5, 0).widget(), PBLabel)
        self.assertEqual(
            ecd.layout().itemAtPosition(5, 0).widget().text(),
            pBDB.descriptions["categories"]["parentCat"],
        )
        self.assertIsInstance(ecd.layout().itemAtPosition(5, 1).widget(), PBLabel)
        self.assertEqual(
            ecd.layout().itemAtPosition(5, 1).widget().text(), "(parentCat)"
        )
        self.assertIsInstance(ecd.textValues["parentCat"], QPushButton)
        self.assertEqual(
            ecd.textValues["parentCat"], ecd.layout().itemAtPosition(6, 0).widget()
        )
        self.assertEqual(ecd.textValues["parentCat"].text(), "0 - Main")
        with patch(
            "physbiblio.gui.catWindows.EditCategoryDialog.onAskParent", autospec=True
        ) as _f:
            QTest.mouseClick(ecd.textValues["parentCat"], Qt.LeftButton)
            _f.assert_called_once_with(ecd)

        self.assertIsInstance(ecd.layout().itemAtPosition(7, 0).widget(), PBLabel)
        self.assertEqual(
            ecd.layout().itemAtPosition(7, 0).widget().text(),
            pBDB.descriptions["categories"]["comments"],
        )
        self.assertIsInstance(ecd.layout().itemAtPosition(7, 1).widget(), PBLabel)
        self.assertEqual(
            ecd.layout().itemAtPosition(7, 1).widget().text(), "(comments)"
        )
        self.assertIsInstance(ecd.textValues["comments"], QLineEdit)
        self.assertEqual(
            ecd.textValues["comments"], ecd.layout().itemAtPosition(8, 0).widget()
        )
        self.assertEqual(ecd.textValues["comments"].text(), "")

        self.assertIsInstance(ecd.layout().itemAtPosition(9, 0).widget(), PBLabel)
        self.assertEqual(
            ecd.layout().itemAtPosition(9, 0).widget().text(),
            pBDB.descriptions["categories"]["ord"],
        )
        self.assertIsInstance(ecd.layout().itemAtPosition(9, 1).widget(), PBLabel)
        self.assertEqual(ecd.layout().itemAtPosition(9, 1).widget().text(), "(ord)")
        self.assertIsInstance(ecd.textValues["ord"], QLineEdit)
        self.assertEqual(
            ecd.textValues["ord"], ecd.layout().itemAtPosition(10, 0).widget()
        )
        self.assertEqual(ecd.textValues["ord"].text(), "")

        self.assertIsInstance(ecd.layout().itemAtPosition(ncf, 1).widget(), QPushButton)
        self.assertEqual(ecd.acceptButton, ecd.layout().itemAtPosition(ncf, 1).widget())
        self.assertEqual(ecd.acceptButton.text(), "OK")
        with patch(
            "physbiblio.gui.commonClasses.EditObjectWindow.onOk", autospec=True
        ) as _f:
            QTest.mouseClick(ecd.acceptButton, Qt.LeftButton)
            _f.assert_called_once_with(ecd)
        self.assertIsInstance(ecd.layout().itemAtPosition(ncf, 0).widget(), QPushButton)
        self.assertEqual(ecd.cancelButton, ecd.layout().itemAtPosition(ncf, 0).widget())
        self.assertEqual(ecd.cancelButton.text(), "Cancel")
        self.assertTrue(ecd.cancelButton.autoDefault())
        with patch(
            "physbiblio.gui.commonClasses.EditObjectWindow.onCancel", autospec=True
        ) as _f:
            QTest.mouseClick(ecd.cancelButton, Qt.LeftButton)
            _f.assert_called_once_with(ecd)

        cat = {
            "idCat": 15,
            "parentCat": 1,
            "description": "desc",
            "comments": "no comment",
            "ord": 0,
            "name": "mycat",
        }
        with patch(
            "physbiblio.database.Categories.getParent",
            return_value=[[1]],
            autospec=True,
        ) as _p, patch(
            "physbiblio.gui.catWindows.EditCategoryDialog.createForm", autospec=True
        ) as _c:
            ecd = EditCategoryDialog(p, cat)
            _p.assert_called_once_with(pBDB.cats, 15)
        ecd.selectedCats = []
        ecd.createForm()

        self.assertIsInstance(ecd.layout().itemAtPosition(1, 0).widget(), PBLabel)
        self.assertEqual(
            ecd.layout().itemAtPosition(1, 0).widget().text(),
            pBDB.descriptions["categories"]["idCat"],
        )
        self.assertIsInstance(ecd.layout().itemAtPosition(1, 1).widget(), PBLabel)
        self.assertEqual(ecd.layout().itemAtPosition(1, 1).widget().text(), "(idCat)")
        self.assertIn("idCat", ecd.textValues.keys())
        self.assertIsInstance(ecd.textValues["idCat"], QLineEdit)
        self.assertEqual(
            ecd.textValues["idCat"], ecd.layout().itemAtPosition(2, 0).widget()
        )
        self.assertEqual(ecd.textValues["idCat"].text(), "15")
        self.assertFalse(ecd.textValues["idCat"].isEnabled())

        self.assertIsInstance(ecd.layout().itemAtPosition(3, 0).widget(), PBLabel)
        self.assertEqual(
            ecd.layout().itemAtPosition(3, 0).widget().text(),
            pBDB.descriptions["categories"]["name"],
        )
        self.assertIsInstance(ecd.layout().itemAtPosition(3, 1).widget(), PBLabel)
        self.assertEqual(ecd.layout().itemAtPosition(3, 1).widget().text(), "(name)")

        self.assertEqual(ecd.textValues["name"].text(), "mycat")
        self.assertEqual(ecd.textValues["description"].text(), "desc")
        self.assertIsInstance(ecd.textValues["parentCat"], QPushButton)
        self.assertEqual(
            ecd.textValues["parentCat"], ecd.layout().itemAtPosition(8, 0).widget()
        )
        self.assertEqual(ecd.textValues["parentCat"].text(), "Select parent")
        self.assertEqual(ecd.textValues["comments"].text(), "no comment")
        self.assertEqual(ecd.textValues["ord"].text(), "0")


if __name__ == "__main__":
    unittest.main()
