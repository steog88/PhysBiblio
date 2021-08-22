#!/usr/bin/env python
"""Test file for the physbiblio.gui.expWindows module.

This file is part of the physbiblio package.
"""
import os
import sys
import traceback

from PySide2.QtCore import QEvent, QModelIndex, Qt
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
    from physbiblio.gui.commonClasses import PBTableView
    from physbiblio.gui.expWindows import *
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
    """Test the editExperiment and deleteExperiment functions"""

    def test_editExperiment(self):
        """test editExperiment"""
        p = QWidget()
        m = self.mainW
        ncw = EditExperimentDialog(p)
        ncw.exec_ = MagicMock()
        ncw.onCancel()
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.expWindows.EditExperimentDialog",
            return_value=ncw,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            editExperiment(p, m)
            _i.assert_called_once_with(p, experiment=None)
            _s.assert_called_once_with(m, "No modifications to experiments")

        with patch(
            "physbiblio.gui.expWindows.EditExperimentDialog",
            return_value=ncw,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i, patch("logging.Logger.debug") as _l:
            editExperiment(p, p)
            _i.assert_called_once_with(p, experiment=None)
            _l.assert_called_once_with(
                "mainWinObject has no attribute 'statusBarMessage'", exc_info=True
            )

        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.expWindows.EditExperimentDialog",
            return_value=ncw,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i, patch(
            "physbiblio.database.Experiments.getDictByID",
            return_value="abc",
            autospec=True,
        ) as _g:
            editExperiment(p, m, 9999)
            _i.assert_called_once_with(p, experiment="abc")
            _g.assert_called_once_with(pBDB.exps, 9999)
            _s.assert_called_once_with(m, "No modifications to experiments")

        ncw = EditExperimentDialog(p)
        ncw.selectedExps = [9999]
        ncw.textValues["homepage"].setText("www.some.thing.com")
        ncw.textValues["comments"].setText("comm")
        ncw.textValues["inspire"].setText("1234")
        ncw.exec_ = MagicMock()
        ncw.onOk()
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.expWindows.EditExperimentDialog",
            return_value=ncw,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i, patch(
            "physbiblio.database.Experiments.getDictByID",
            return_value="abc",
            autospec=True,
        ) as _g:
            editExperiment(p, m, editIdExp=9999)
            _i.assert_called_once_with(p, experiment="abc")
            _g.assert_called_once_with(pBDB.exps, 9999)
            _s.assert_called_once_with(m, "ERROR: empty experiment name")

        ncw.textValues["name"].setText("myexp")
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.expWindows.EditExperimentDialog",
            return_value=ncw,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i, patch(
            "physbiblio.database.Experiments.getDictByID",
            return_value="abc",
            autospec=True,
        ) as _g, patch(
            "physbiblio.database.Experiments.insert", return_value="abc", autospec=True
        ) as _n, patch(
            "logging.Logger.debug"
        ) as _l:
            editExperiment(p, m, 9999)
            _i.assert_called_once_with(p, experiment="abc")
            _g.assert_called_once_with(pBDB.exps, 9999)
            _n.assert_called_once_with(
                pBDB.exps,
                {
                    "name": u"myexp",
                    "inspire": u"1234",
                    "homepage": "www.some.thing.com",
                    "comments": u"comm",
                },
            )
            _s.assert_called_once_with(m, "Experiment saved")
            _l.assert_called_once_with(
                "parentObject has no attribute 'recreateTable'", exc_info=True
            )

        ncw.textValues["name"].setText("myexp")
        ctw = ExpsListWindow(p)
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.expWindows.EditExperimentDialog",
            return_value=ncw,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i, patch(
            "physbiblio.database.Experiments.getDictByID",
            return_value="abc",
            autospec=True,
        ) as _g, patch(
            "physbiblio.database.Experiments.insert", return_value="abc", autospec=True
        ) as _n, patch(
            "logging.Logger.debug"
        ) as _l, patch(
            "physbiblio.gui.expWindows.ExpsListWindow.recreateTable", autospec=True
        ) as _r:
            editExperiment(ctw, m, 9999)
            _i.assert_called_once_with(ctw, experiment="abc")
            _g.assert_called_once_with(pBDB.exps, 9999)
            _n.assert_called_once_with(
                pBDB.exps,
                {
                    "name": u"myexp",
                    "inspire": u"1234",
                    "homepage": "www.some.thing.com",
                    "comments": u"comm",
                },
            )
            _s.assert_called_once_with(m, "Experiment saved")
            _l.assert_not_called()
            _r.assert_called_once_with(ctw)

        exp = {
            "idExp": 9999,
            "homepage": "www.some.page.com",
            "comments": "no comment",
            "inspire": "1234",
            "name": "myexp",
        }
        ncw = EditExperimentDialog(p, exp)
        ncw.selectedCats = []
        ncw.textValues["inspire"].setText("4321")
        ncw.textValues["name"].setText("myexp1")
        ncw.textValues["comments"].setText("comm")
        ncw.textValues["homepage"].setText("www.page.com")
        ncw.exec_ = MagicMock()
        ncw.onOk()
        ctw = ExpsListWindow(p)
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.expWindows.EditExperimentDialog",
            return_value=ncw,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i, patch(
            "physbiblio.database.Experiments.getDictByID",
            return_value="abc",
            autospec=True,
        ) as _g, patch(
            "physbiblio.database.Experiments.update", return_value="abc", autospec=True
        ) as _n, patch(
            "logging.Logger.info"
        ) as _l, patch(
            "physbiblio.gui.expWindows.ExpsListWindow.recreateTable", autospec=True
        ) as _r:
            editExperiment(ctw, m, 9999)
            _i.assert_called_once_with(ctw, experiment="abc")
            _g.assert_called_once_with(pBDB.exps, 9999)
            _n.assert_called_once_with(
                pBDB.exps,
                {
                    "idExp": u"9999",
                    "name": u"myexp1",
                    "homepage": u"www.page.com",
                    "comments": u"comm",
                    "inspire": u"4321",
                },
                "9999",
            )
            _s.assert_called_once_with(m, "Experiment saved")
            _l.assert_called_once_with("Updating experiment 9999...")
            _r.assert_called_once_with(ctw)

    def test_deleteExperiment(self):
        """test deleteExperiment"""
        p = QWidget()
        m = self.mainW
        with patch(
            "physbiblio.gui.expWindows.askYesNo", return_value=False, autospec=True
        ) as _a, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s:
            deleteExperiment(p, m, 9999, "myexp")
            _a.assert_called_once_with(
                "Do you really want to delete this experiment "
                + "(ID = '9999', name = 'myexp')?"
            )
            _s.assert_called_once_with(m, "Nothing changed")

        with patch(
            "physbiblio.gui.expWindows.askYesNo", return_value=False, autospec=True
        ) as _a, patch("logging.Logger.debug") as _d:
            deleteExperiment(p, p, 9999, "myexp")
            _a.assert_called_once_with(
                "Do you really want to delete this experiment "
                + "(ID = '9999', name = 'myexp')?"
            )
            _d.assert_called_once_with(
                "mainWinObject has no attribute 'statusBarMessage'", exc_info=True
            )

        with patch(
            "physbiblio.gui.expWindows.askYesNo", return_value=True, autospec=True
        ) as _a, patch(
            "physbiblio.database.Experiments.delete", autospec=True
        ) as _c, patch(
            "PySide2.QtWidgets.QMainWindow.setWindowTitle", autospec=True
        ) as _t, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "logging.Logger.debug"
        ) as _d:
            deleteExperiment(p, m, 9999, "myexp")
            _a.assert_called_once_with(
                "Do you really want to delete this experiment "
                + "(ID = '9999', name = 'myexp')?"
            )
            _c.assert_called_once_with(pBDB.exps, 9999)
            _t.assert_called_once_with("PhysBiblio*")
            _s.assert_called_once_with(m, "Experiment deleted")
            _d.assert_called_once_with(
                "parentObject has no attribute 'recreateTable'", exc_info=True
            )

        elw = ExpsListWindow(p)
        with patch(
            "physbiblio.gui.expWindows.askYesNo", return_value=True, autospec=True
        ) as _a, patch(
            "physbiblio.database.Experiments.delete", autospec=True
        ) as _c, patch(
            "PySide2.QtWidgets.QMainWindow.setWindowTitle", autospec=True
        ) as _t, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.expWindows.ExpsListWindow.recreateTable", autospec=True
        ) as _r:
            deleteExperiment(elw, m, 9999, "myexp")
            _a.assert_called_once_with(
                "Do you really want to delete this experiment "
                + "(ID = '9999', name = 'myexp')?"
            )
            _c.assert_called_once_with(pBDB.exps, 9999)
            _t.assert_called_once_with("PhysBiblio*")
            _s.assert_called_once_with(m, "Experiment deleted")
            _r.assert_called_once_with(elw)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestExpTableModel(GUITestCase):
    """Test ExpTableModel"""

    def test_init(self):
        """test init"""
        p = QWidget()
        exp_list = [{"idExp": 0, "name": "no"}]
        header = ["id", "name"]
        em = ExpTableModel(p, exp_list, header, askExps=False, previous=[])
        self.assertIsInstance(em, PBTableModel)
        self.assertEqual(em.typeClass, "Exps")
        self.assertEqual(em.dataList, exp_list)
        with patch(
            "physbiblio.gui.commonClasses.PBTableModel.__init__", autospec=True
        ) as _i, patch(
            "physbiblio.gui.commonClasses.PBTableModel.prepareSelected", autospec=True
        ) as _s:
            em = ExpTableModel(p, exp_list, header, askExps=True, previous=[9999])
            _i.assert_called_once_with(em, p, ["id", "name"], True, [9999])
            _s.assert_called_once_with(em)

    def test_getIdentifier(self):
        """test getIdentifier"""
        p = QWidget()
        exp_list = [{"idExp": 0, "name": "no"}]
        header = ["id", "name"]
        em = ExpTableModel(p, exp_list, header, askExps=False, previous=[])
        self.assertEqual(em.getIdentifier({"idExp": 9999, "name": "no"}), 9999)

    def test_data(self):
        """test data"""
        p = QWidget()
        exp_list = [{"idExp": 0, "name": "myexp"}, {"idExp": 9999, "name": "exp"}]
        header = ["idExp", "name"]
        em = ExpTableModel(p, exp_list, header, askExps=False, previous=[])
        ix = em.index(10, 0)
        self.assertEqual(em.data(ix, Qt.CheckStateRole), None)
        ix = em.index(0, 0)
        self.assertEqual(em.data(ix, Qt.DisplayRole), 0)
        self.assertEqual(em.data(ix, Qt.EditRole), 0)
        self.assertEqual(em.data(ix, Qt.DecorationRole), None)
        ix = em.index(0, 1)
        self.assertEqual(em.data(ix, Qt.DisplayRole), "myexp")
        self.assertEqual(em.data(ix, Qt.EditRole), "myexp")
        self.assertEqual(em.data(ix, Qt.DecorationRole), None)

        ix = em.index(0, 0)
        self.assertEqual(em.data(ix, Qt.CheckStateRole), None)
        p = QWidget()
        p.askExps = False
        em = ExpTableModel(p, exp_list, header, askExps=False, previous=[])
        self.assertEqual(em.data(em.index(0, 0), Qt.CheckStateRole), None)
        em = ExpTableModel(p, exp_list, header, askExps=True, previous=[])
        self.assertEqual(em.data(em.index(0, 0), Qt.CheckStateRole), Qt.Unchecked)
        em = ExpTableModel(p, exp_list, header, askExps=True, previous=[0])
        self.assertEqual(em.data(em.index(0, 0), Qt.CheckStateRole), Qt.Checked)
        self.assertEqual(em.setData(ix, "abc", Qt.CheckStateRole), True)
        self.assertEqual(em.data(em.index(0, 0), Qt.CheckStateRole), Qt.Unchecked)
        self.assertEqual(em.setData(ix, Qt.Checked, Qt.CheckStateRole), True)
        self.assertEqual(em.data(em.index(0, 0), Qt.CheckStateRole), Qt.Checked)

    def test_setData(self):
        """test setData"""
        p = QWidget()

        def connectEmit(ix1, ix2):
            """used to test dataChanged.emit"""
            self.newEmit = ix1

        exp_list = [{"idExp": 0, "name": "no"}, {"idExp": 9999, "name": "yes"}]
        header = ["idExp", "name"]
        cm = ExpTableModel(p, exp_list, header)
        ix = cm.index(10, 0)
        self.newEmit = False
        cm.dataChanged.connect(connectEmit)
        self.assertEqual(cm.setData(ix, "abc", Qt.CheckStateRole), False)
        self.assertEqual(self.newEmit, False)
        ix = cm.index(0, 0)
        self.assertEqual(cm.setData(ix, Qt.Checked, Qt.CheckStateRole), True)
        self.assertEqual(cm.selectedElements[0], True)
        self.assertEqual(self.newEmit, ix)
        self.newEmit = False
        self.assertEqual(cm.setData(ix, "abc", Qt.CheckStateRole), True)
        self.assertEqual(cm.selectedElements[0], False)
        self.assertEqual(self.newEmit, ix)

        cm = ExpTableModel(p, exp_list, header)
        ix = cm.index(0, 0)
        self.assertEqual(cm.setData(ix, "abc", Qt.EditRole), True)
        self.assertEqual(cm.selectedElements[0], False)
        self.assertEqual(cm.setData(ix, "abc", Qt.CheckStateRole), True)
        self.assertEqual(cm.selectedElements[0], False)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestExpsListWindow(GUITestCase):
    """Test ExpsListWindow"""

    def setUp(self):
        """define common parameters for test use"""
        self.exps = [
            {
                "idExp": 0,
                "name": "test0",
                "homepage": "",
                "comments": "",
                "inspire": "",
            },
            {
                "idExp": 1,
                "name": "test1",
                "homepage": "",
                "comments": "",
                "inspire": "1234",
            },
            {
                "idExp": 2,
                "name": "test2",
                "homepage": "",
                "comments": "",
                "inspire": "",
            },
            {
                "idExp": 3,
                "name": "test3",
                "homepage": "",
                "comments": "",
                "inspire": "",
            },
        ]

    def test_init(self):
        """test init"""
        p = QWidget()
        with patch(
            "physbiblio.database.Experiments.getAll",
            return_value=self.exps,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.gui.expWindows.ExpsListWindow.createTable", autospec=True
        ) as _cf:
            elw = ExpsListWindow(p)
            _cf.assert_called_once_with(elw)
        self.assertIsInstance(elw, ObjListWindow)
        self.assertEqual(elw.parent(), p)
        self.assertEqual(elw.colcnt, 5)
        self.assertEqual(
            elw.colContents, ["idExp", "name", "comments", "homepage", "inspire"]
        )
        self.assertEqual(elw.askExps, False)
        self.assertEqual(elw.askForBib, None)
        self.assertEqual(elw.askForCat, None)
        self.assertEqual(elw.previous, [])
        self.assertEqual(elw.windowTitle(), "List of experiments")

        with patch(
            "physbiblio.database.Experiments.getAll",
            return_value=self.exps,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.gui.expWindows.ExpsListWindow.createTable", autospec=True
        ) as _cf:
            elw = ExpsListWindow(
                parent=p,
                askExps=True,
                askForBib="mybib",
                askForCat="mycat",
                previous=[9999],
            )
            _cf.assert_called_once_with(elw)
        self.assertIsInstance(elw, ObjListWindow)
        self.assertEqual(elw.parent(), p)
        self.assertEqual(elw.colcnt, 5)
        self.assertEqual(
            elw.colContents, ["idExp", "name", "comments", "homepage", "inspire"]
        )
        self.assertEqual(elw.askExps, True)
        self.assertEqual(elw.askForBib, "mybib")
        self.assertEqual(elw.askForCat, "mycat")
        self.assertEqual(elw.previous, [9999])
        self.assertEqual(elw.windowTitle(), "List of experiments")

    def test_populateAskExp(self):
        """test populateAskExp"""
        p = QWidget()
        with patch(
            "physbiblio.database.Experiments.getAll",
            return_value=self.exps,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.gui.expWindows.ExpsListWindow.createTable", autospec=True
        ) as _c:
            elw = ExpsListWindow(p)
        # test with askCats = False (nothing happens)
        self.assertTrue(elw.populateAskExp())
        self.assertEqual(elw.marked, [])
        self.assertFalse(hasattr(p, "selectedExps"))
        self.assertEqual(elw.currLayout.count(), 0)

        # test with askCats = True and askForBib
        with patch(
            "physbiblio.database.Experiments.getAll",
            return_value=self.exps,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.gui.expWindows.ExpsListWindow.createTable", autospec=True
        ) as _c:
            elw = ExpsListWindow(p, askExps=True, askForBib="bib")
        # bibkey not in db
        with patch(
            "physbiblio.database.Entries.getByBibkey", return_value=[], autospec=True
        ) as _gbb, patch("logging.Logger.warning") as _w:
            self.assertEqual(elw.populateAskExp(), None)
            _gbb.assert_called_once_with(pBDB.bibs, "bib", saveQuery=False)
            _w.assert_called_once_with(
                "The entry 'bib' is not in the database!", exc_info=True
            )
        self.assertEqual(elw.marked, [])
        self.assertFalse(hasattr(p, "selectedExps"))
        self.assertEqual(elw.currLayout.count(), 0)
        # dict has no "title" or "author"
        with patch(
            "physbiblio.database.Entries.getByBibkey",
            side_effect=[[{"inspire": None, "doi": None, "arxiv": None}]],
            autospec=True,
        ) as _gbb:
            self.assertEqual(elw.populateAskExp(), True)
            _gbb.assert_called_once_with(pBDB.bibs, "bib", saveQuery=False)
            self.assertEqual(elw.currLayout.count(), 1)
            self.assertIsInstance(elw.layout().itemAt(0).widget(), PBLabel)
            self.assertEqual(
                elw.layout().itemAt(0).widget().text(),
                "Mark experiments for the following "
                + "entry:<br><b>key</b>:<br>bib<br>",
            )
        self.assertEqual(elw.marked, [])
        self.assertTrue(hasattr(p, "selectedExps"))
        self.assertEqual(p.selectedExps, [])
        # no link exists
        elw.cleanLayout()
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
            self.assertEqual(elw.populateAskExp(), True)
            _gbb.assert_called_once_with(pBDB.bibs, "bib", saveQuery=False)
            self.assertEqual(elw.currLayout.count(), 1)
            self.assertIsInstance(elw.layout().itemAt(0).widget(), PBLabel)
            self.assertEqual(
                elw.layout().itemAt(0).widget().text(),
                "Mark experiments for the following "
                + "entry:<br><b>key</b>:<br>bib<br>"
                + "<b>author(s)</b>:<br>sg<br>"
                + "<b>title</b>:<br>title<br>",
            )
        # inspire exists
        elw.cleanLayout()
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
            self.assertEqual(elw.populateAskExp(), True)
            _gbb.assert_called_once_with(pBDB.bibs, "bib", saveQuery=False)
            _l.assert_called_once_with(pBView, "bib", "inspire")
            self.assertEqual(elw.currLayout.count(), 1)
            self.assertIsInstance(elw.layout().itemAt(0).widget(), PBLabel)
            self.assertEqual(
                elw.layout().itemAt(0).widget().text(),
                "Mark experiments for the following "
                + "entry:<br><b>key</b>:<br><a href='inspirelink'>bib</a><br>"
                + "<b>author(s)</b>:<br>sg<br>"
                + "<b>title</b>:<br>title<br>",
            )
        elw.cleanLayout()
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
            self.assertEqual(elw.populateAskExp(), True)
            _gbb.assert_called_once_with(pBDB.bibs, "bib", saveQuery=False)
            _l.assert_called_once_with(pBView, "bib", "arxiv")
            self.assertEqual(elw.currLayout.count(), 1)
            self.assertIsInstance(elw.layout().itemAt(0).widget(), PBLabel)
            self.assertEqual(
                elw.layout().itemAt(0).widget().text(),
                "Mark experiments for the following "
                + "entry:<br><b>key</b>:<br><a href='arxivlink'>bib</a><br>"
                + "<b>author(s)</b>:<br>sg<br>"
                + "<b>title</b>:<br>title<br>",
            )
        elw.cleanLayout()
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
            self.assertEqual(elw.populateAskExp(), True)
            _gbb.assert_called_once_with(pBDB.bibs, "bib", saveQuery=False)
            _l.assert_called_once_with(pBView, "bib", "doi")
            self.assertEqual(elw.currLayout.count(), 1)
            self.assertIsInstance(elw.layout().itemAt(0).widget(), PBLabel)
            self.assertEqual(
                elw.layout().itemAt(0).widget().text(),
                "Mark experiments for the following "
                + "entry:<br><b>key</b>:<br><a href='doilink'>bib</a><br>"
                + "<b>author(s)</b>:<br>sg<br>"
                + "<b>title</b>:<br>title<br>",
            )

        # test with askCats = True and askForExp
        p = QWidget()
        with patch(
            "physbiblio.database.Experiments.getAll",
            return_value=self.exps,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.gui.expWindows.ExpsListWindow.createTable", autospec=True
        ) as _c:
            elw = ExpsListWindow(p, askExps=True, askForCat="cat")
            with self.assertRaises(NotImplementedError):
                elw.populateAskExp()

        # #test with no askForBib, askForExp
        p = QWidget()
        with patch(
            "physbiblio.database.Experiments.getAll",
            return_value=self.exps,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.gui.expWindows.ExpsListWindow.createTable", autospec=True
        ) as _c:
            elw = ExpsListWindow(p, askExps=True)
        self.assertEqual(elw.populateAskExp(), True)
        self.assertEqual(elw.currLayout.count(), 1)
        self.assertIsInstance(elw.layout().itemAt(0).widget(), PBLabel)
        self.assertEqual(
            elw.layout().itemAt(0).widget().text(), "Select the desired experiments:"
        )

    def test_onCancel(self):
        """test onCancel"""
        elw = ExpsListWindow()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            elw.onCancel()
        self.assertFalse(elw.result)

    def test_onOk(self):
        """test onOk"""
        p = QWidget()
        with patch(
            "physbiblio.database.Experiments.getAll",
            return_value=self.exps,
            autospec=True,
        ) as _gh:
            elw = ExpsListWindow(p)
        self.assertFalse(hasattr(p, "selectedExps"))
        elw.tableModel.selectedElements[0] = True
        elw.tableModel.selectedElements[2] = False
        elw.tableModel.selectedElements[3] = True
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            elw.onOk()
            _c.assert_called_once_with()
        self.assertEqual(hasattr(p, "selectedExps"), True)
        self.assertEqual(p.selectedExps, [0, 3])
        self.assertEqual(elw.result, "Ok")

    def test_onNewExp(self):
        """test onNewExp"""
        p = QWidget()
        elw = ExpsListWindow(p)
        with patch("physbiblio.gui.expWindows.editExperiment", autospec=True) as _ec:
            elw.onNewExp()
            _ec.assert_called_once_with(elw, p)

    def test_keyPressEvent(self):
        """test keyPressEvent"""
        elw = ExpsListWindow()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _oc:
            QTest.keyPress(elw, "a")
            _oc.assert_not_called()
            QTest.keyPress(elw, Qt.Key_Enter)
            _oc.assert_not_called()
            QTest.keyPress(elw, Qt.Key_Escape)
            self.assertEqual(_oc.call_count, 1)

    def test_createTable(self):
        """test createTable"""
        p = QWidget()
        with patch(
            "physbiblio.gui.expWindows.ExpsListWindow.createTable", autospec=True
        ) as _c:
            elw = ExpsListWindow(p)
        with patch(
            "physbiblio.database.Experiments.getAll",
            return_value=self.exps,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.gui.expWindows.ExpsListWindow.populateAskExp", autospec=True
        ) as _pae, patch(
            "physbiblio.gui.expWindows.ExpTableModel.__init__",
            return_value=None,
            autospec=True,
        ) as _etm, patch(
            "physbiblio.gui.commonClasses.ObjListWindow.addFilterInput", autospec=True
        ) as _afi, patch(
            "physbiblio.gui.commonClasses.ObjListWindow.setProxyStuff", autospec=True
        ) as _sps, patch(
            "physbiblio.gui.commonClasses.ObjListWindow.finalizeTable", autospec=True
        ) as _ft:
            elw.createTable()
            _pae.assert_called_once_with(elw)
            _gh.assert_called_once_with(pBDB.exps)
            _afi.assert_called_once_with(elw, "Filter experiment")
            _sps.assert_called_once_with(elw, 1, Qt.AscendingOrder)
            _ft.assert_called_once_with(elw)
            _etm.assert_called_once_with(
                elw.tableModel,
                elw,
                self.exps,
                pBDB.tableCols["experiments"],
                askExps=False,
                previous=[],
            )
        elw.cleanLayout()
        with patch(
            "physbiblio.database.Experiments.getAll",
            return_value=self.exps,
            autospec=True,
        ) as _gh:
            elw.createTable()
        self.assertEqual(self.exps, elw.exps)
        self.assertIsInstance(elw.tableModel, ExpTableModel)
        self.assertEqual(elw.layout().count(), 3)
        self.assertIsInstance(elw.layout().itemAt(0).widget(), QLineEdit)
        self.assertEqual(elw.layout().itemAt(0).widget(), elw.filterInput)
        self.assertEqual(elw.filterInput.placeholderText(), "Filter experiment")
        with patch(
            "physbiblio.gui.expWindows.ExpsListWindow.changeFilter", autospec=True
        ) as _cf:
            elw.filterInput.textChanged.emit("a")
            _cf.assert_called_once_with(elw, "a")
        self.assertIsInstance(elw.layout().itemAt(1).widget(), PBTableView)
        self.assertEqual(elw.layout().itemAt(1).widget(), elw.tableview)
        self.assertIsInstance(elw.layout().itemAt(2).widget(), QPushButton)
        self.assertEqual(elw.layout().itemAt(2).widget(), elw.newExpButton)
        self.assertEqual(elw.newExpButton.text(), "Add new experiment")
        with patch(
            "physbiblio.gui.expWindows.ExpsListWindow.onNewExp", autospec=True
        ) as _f:
            QTest.mouseClick(elw.newExpButton, Qt.LeftButton)
            _f.assert_called_once_with(elw)

        # repeat with askExps=True, but ignore populateAskExp
        with patch(
            "physbiblio.gui.expWindows.ExpsListWindow.populateAskExp", autospec=True
        ) as _c:
            elw = ExpsListWindow(p, askExps=True)
        self.assertEqual(elw.layout().count(), 5)
        self.assertIsInstance(elw.layout().itemAt(0).widget(), QLineEdit)
        self.assertEqual(elw.layout().itemAt(0).widget(), elw.filterInput)
        self.assertEqual(elw.filterInput.placeholderText(), "Filter experiment")
        with patch(
            "physbiblio.gui.expWindows.ExpsListWindow.changeFilter", autospec=True
        ) as _cf:
            elw.filterInput.textChanged.emit("a")
            _cf.assert_called_once_with(elw, "a")
        self.assertIsInstance(elw.layout().itemAt(1).widget(), PBTableView)
        self.assertEqual(elw.layout().itemAt(1).widget(), elw.tableview)
        self.assertIsInstance(elw.layout().itemAt(2).widget(), QPushButton)
        self.assertEqual(elw.layout().itemAt(2).widget(), elw.newExpButton)
        self.assertEqual(elw.newExpButton.text(), "Add new experiment")
        with patch(
            "physbiblio.gui.expWindows.ExpsListWindow.onNewExp", autospec=True
        ) as _f:
            QTest.mouseClick(elw.newExpButton, Qt.LeftButton)
            _f.assert_called_once_with(elw)
        self.assertIsInstance(elw.layout().itemAt(3).widget(), QPushButton)
        self.assertEqual(elw.layout().itemAt(3).widget(), elw.acceptButton)
        self.assertEqual(elw.acceptButton.text(), "OK")
        with patch(
            "physbiblio.gui.expWindows.ExpsListWindow.onOk", autospec=True
        ) as _f:
            QTest.mouseClick(elw.acceptButton, Qt.LeftButton)
            _f.assert_called_once_with(elw)
        self.assertIsInstance(elw.layout().itemAt(4).widget(), QPushButton)
        self.assertEqual(elw.layout().itemAt(4).widget(), elw.cancelButton)
        self.assertEqual(elw.cancelButton.text(), "Cancel")
        self.assertTrue(elw.cancelButton.autoDefault())
        with patch(
            "physbiblio.gui.expWindows.ExpsListWindow.onCancel", autospec=True
        ) as _f:
            QTest.mouseClick(elw.cancelButton, Qt.LeftButton)
            _f.assert_called_once_with(elw)

    def test_triggeredContextMenuEvent(self):
        """test triggeredContextMenuEvent"""
        p = MainWindow(testing=True)
        position = QCursor.pos()
        ev = QMouseEvent(
            QEvent.MouseButtonPress,
            position,
            Qt.RightButton,
            Qt.NoButton,
            Qt.NoModifier,
        )
        mm = PBMenu()
        mm.exec_ = MagicMock()
        with patch(
            "physbiblio.database.Experiments.getAll",
            return_value=self.exps,
            autospec=True,
        ) as _gh, patch(
            "physbiblio.gui.expWindows.PBMenu",
            return_value=mm,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _mm:
            elw = ExpsListWindow(p)
        self.assertEqual(elw.triggeredContextMenuEvent(9999, 0, ev), None)
        self.assertEqual(elw.menu, None)
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rmc, patch(
            "physbiblio.gui.expWindows.PBMenu",
            return_value=mm,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _mm, patch(
            "physbiblio.gui.expWindows.editExperiment", autospec=True
        ) as _ec, patch(
            "physbiblio.gui.expWindows.deleteExperiment", autospec=True
        ) as _dc, patch(
            "physbiblio.gui.commonClasses.PBMenu.fillMenu", autospec=True
        ) as _f:
            self.assertEqual(elw.triggeredContextMenuEvent(0, 0, ev), True)
            _f.assert_called_once_with(elw.menu)
            _rmc.assert_not_called()
            _ec.assert_not_called()
            _dc.assert_not_called()

            self.assertIsInstance(elw.menu, PBMenu)
            self.assertIsInstance(elw.menu.possibleActions, list)
            self.assertEqual(len(elw.menu.possibleActions), 9)
            self.assertEqual(elw.menu.possibleActions[1], None)
            self.assertEqual(elw.menu.possibleActions[4], None)
            self.assertEqual(elw.menu.possibleActions[7], None)

            for ix, tit, en in [
                [0, "--Experiment: test0--", False],
                [2, "Open list of corresponding entries", True],
                [3, "Open in new tab", True],
                [5, "Modify", True],
                [6, "Delete", True],
                [8, "Categories", True],
            ]:
                act = elw.menu.possibleActions[ix]
                self.assertIsInstance(act, QAction)
                self.assertEqual(act.text(), tit)
                self.assertEqual(act.isEnabled(), en)

            mm.exec_ = lambda x, i=0: mm.possibleActions[i]
            self.assertEqual(elw.triggeredContextMenuEvent(0, 0, ev), True)
            _rmc.assert_not_called()
            _ec.assert_not_called()
            _dc.assert_not_called()

            mm.exec_ = lambda x, i=2: mm.possibleActions[i]
            with patch(
                "physbiblio.database.Entries.getByExp",
                return_value=["a"],
                autospec=True,
            ) as _ffd:
                self.assertEqual(elw.triggeredContextMenuEvent(0, 0, ev), True)
                _ffd.assert_called_once_with(pBDB.bibs, "0")
            _rmc.assert_called_once_with(p, ["a"])
            _ec.assert_not_called()
            _dc.assert_not_called()
            _rmc.reset_mock()

            mm.exec_ = lambda x, i=3: mm.possibleActions[i]
            with patch(
                "physbiblio.database.Entries.getByExp",
                return_value=["a"],
                autospec=True,
            ) as _ffd:
                self.assertEqual(elw.triggeredContextMenuEvent(0, 0, ev), True)
                _ffd.assert_called_once_with(pBDB.bibs, "0")
            _rmc.assert_called_once_with(p, ["a"], newTab="test0")
            _ec.assert_not_called()
            _dc.assert_not_called()
            _rmc.reset_mock()

            mm.exec_ = lambda x, i=5: mm.possibleActions[i]
            with patch(
                "physbiblio.database.Entries.getByExp",
                return_value=["a"],
                autospec=True,
            ) as _ffd:
                self.assertEqual(elw.triggeredContextMenuEvent(0, 0, ev), True)
            _rmc.assert_not_called()
            _ec.assert_called_once_with(elw, p, "0")
            _dc.assert_not_called()
            _ec.reset_mock()

            mm.exec_ = lambda x, i=6: mm.possibleActions[i]
            with patch(
                "physbiblio.database.Entries.getByExp",
                return_value=["a"],
                autospec=True,
            ) as _ffd:
                self.assertEqual(elw.triggeredContextMenuEvent(0, 0, ev), True)
            _rmc.assert_not_called()
            _ec.assert_not_called()
            _dc.assert_called_once_with(elw, p, "0", "test0")
            _dc.reset_mock()

            with patch(
                "physbiblio.database.Experiments.getByID",
                return_value=[self.exps[0]],
                autospec=True,
            ) as _gbi, patch(
                "physbiblio.gui.catWindows.CatsTreeWindow.createForm", autospec=True
            ) as _cf:
                sc = CatsTreeWindow(
                    parent=p,
                    askCats=True,
                    askForExp=0,
                    expButton=False,
                    previous=[0, 13],
                )
            sc.exec_ = MagicMock()
            sc.result = "Ok"
            p.selectedCats = [9, 13]
            mm.exec_ = lambda x, i=8: mm.possibleActions[i]
            with patch(
                "physbiblio.database.Entries.getByExp",
                return_value=["a"],
                autospec=True,
            ) as _ffd, patch(
                "physbiblio.gui.expWindows.CatsTreeWindow",
                return_value=sc,
                autospec=USE_AUTOSPEC_CLASS,
            ) as _i, patch(
                "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
            ) as _sbm, patch(
                "physbiblio.database.CatsExps.delete", autospec=True
            ) as _d, patch(
                "physbiblio.database.CatsExps.insert", autospec=True
            ) as _a, patch(
                "physbiblio.database.Categories.getByExp",
                return_value=[{"idCat": 0}, {"idCat": 13}],
                autospec=True,
            ) as _gbe:
                self.assertEqual(elw.triggeredContextMenuEvent(0, 0, ev), True)
                _ffd.assert_not_called()
                _gbe.assert_called_once_with(pBDB.cats, "0")
                _i.assert_called_once_with(
                    parent=p,
                    previous=[0, 13],
                    askCats=True,
                    askForExp="0",
                    expButton=False,
                )
                _d.assert_called_once_with(pBDB.catExp, 0, "0")
                _a.assert_called_once_with(pBDB.catExp, 9, "0")
                _sbm.assert_called_once_with(
                    p, "Categories for 'test0' successfully inserted"
                )
            _rmc.assert_not_called()
            _ec.assert_not_called()
            _dc.assert_not_called()

    def test_handleItemEntered(self):
        """test handleItemEntered"""
        p = QWidget()
        with patch(
            "physbiblio.database.Experiments.getAll",
            return_value=self.exps,
            autospec=True,
        ) as _gh:
            elw = ExpsListWindow(p)
        ix = elw.proxyModel.index(0, 0)
        with patch("logging.Logger.exception") as _l, patch(
            "PySide2.QtCore.QTimer.start", autospec=True
        ) as _st, patch(
            "PySide2.QtWidgets.QToolTip.showText", autospec=True
        ) as _sh, patch(
            "physbiblio.database.Experiments.getByID", return_value=[], autospec=True
        ) as _gbi:
            self.assertEqual(elw.handleItemEntered(ix), None)
            _l.assert_called_once_with("Failed in finding experiment")
            _gbi.assert_called_once_with(pBDB.exps, "0")
            _st.assert_not_called()
            _sh.assert_not_called()
        with patch("logging.Logger.exception") as _l, patch(
            "PySide2.QtCore.QTimer.start", autospec=True
        ) as _st, patch("PySide2.QtWidgets.QToolTip.showText") as _sh, patch(
            "physbiblio.database.Experiments.getByID",
            return_value=[self.exps[0]],
            autospec=True,
        ) as _gbi, patch(
            "physbiblio.database.EntryExps.countByExp", return_value=33, autospec=True
        ) as _cb, patch(
            "physbiblio.database.CatsExps.countByExp", return_value=12, autospec=True
        ) as _ce:
            position = QCursor.pos()
            self.assertEqual(elw.handleItemEntered(ix), None)
            _l.assert_not_called()
            self.assertIsInstance(elw.timer, QTimer)
            self.assertTrue(elw.timer.isSingleShot())
            _gbi.assert_called_once_with(pBDB.exps, "0")
            _st.assert_called_once_with(500)
            _sh.assert_not_called()
            elw.timer.timeout.emit()
            _sh.assert_called_once_with(
                position,
                "0: test0\nCorresponding entries: 33\nAssociated categories: 12",
                elw.tableview.viewport(),
                elw.tableview.visualRect(ix),
                3000,
            )
        with patch("logging.Logger.exception") as _l, patch(
            "PySide2.QtCore.QTimer.start", autospec=True
        ) as _st, patch("PySide2.QtWidgets.QToolTip.showText") as _sh, patch(
            "physbiblio.database.Experiments.getByID",
            return_value=[self.exps[0]],
            autospec=True,
        ) as _gbi, patch(
            "physbiblio.database.EntryExps.countByExp", return_value=33, autospec=True
        ) as _cb, patch(
            "physbiblio.database.CatsExps.countByExp", return_value=12, autospec=True
        ) as _ce:
            self.assertEqual(elw.handleItemEntered(ix), None)
            _sh.assert_called_once_with(QCursor.pos(), "", elw.tableview.viewport())

    def test_cellClick(self):
        """test cellClick"""
        p = QWidget()
        with patch(
            "physbiblio.database.Experiments.getAll",
            return_value=self.exps,
            autospec=True,
        ) as _gh:
            elw = ExpsListWindow(p)
        self.assertEqual(elw.cellClick(QModelIndex()), None)
        self.assertEqual(elw.cellClick(elw.tableModel.index(0, 0)), True)

    def test_cellDoubleClick(self):
        """test cellDoubleClick"""
        p = MainWindow(testing=True)
        exps = [
            {
                "idExp": 0,
                "name": "test0",
                "homepage": "",
                "comments": "",
                "inspire": "",
            },
            {
                "idExp": 1,
                "name": "test1",
                "homepage": "www.some.com",
                "comments": "",
                "inspire": "1234",
            },
        ]
        with patch(
            "physbiblio.database.Experiments.getAll", return_value=exps, autospec=True
        ) as _gh:
            elw = ExpsListWindow(p)
        self.assertEqual(elw.cellDoubleClick(QModelIndex()), None)
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rmc, patch(
            "physbiblio.database.Entries.getByExp", return_value=["a"], autospec=True
        ) as _ffd:
            self.assertEqual(elw.cellDoubleClick(elw.proxyModel.index(0, 0)), True)
            self.assertEqual(elw.cellDoubleClick(elw.proxyModel.index(0, 1)), True)
            self.assertEqual(elw.cellDoubleClick(elw.proxyModel.index(0, 2)), True)
            self.assertEqual(elw.cellDoubleClick(elw.proxyModel.index(0, 3)), None)
            self.assertEqual(elw.cellDoubleClick(elw.proxyModel.index(0, 4)), None)
            self.assertEqual(elw.cellDoubleClick(elw.proxyModel.index(1, 0)), True)
            self.assertEqual(elw.cellDoubleClick(elw.proxyModel.index(1, 1)), True)
            self.assertEqual(elw.cellDoubleClick(elw.proxyModel.index(1, 2)), True)
            self.assertEqual(_rmc.call_count, 8)
            _rmc.assert_has_calls([call(p, ["a"])])
        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch("logging.Logger.debug") as _l:
            self.assertEqual(elw.cellDoubleClick(elw.proxyModel.index(1, 3)), True)
            _ol.assert_called_once_with(pBGuiView, "www.some.com", "link")
            _l.assert_called_once_with("Opening 'www.some.com'...")
        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch("logging.Logger.debug") as _l:
            self.assertEqual(elw.cellDoubleClick(elw.proxyModel.index(1, 4)), True)
            _ol.assert_called_once_with(
                pBGuiView, pbConfig.inspireExperimentsLink + "1234", "link"
            )
            _l.assert_called_once_with(
                "Opening '%s'..." % (pbConfig.inspireExperimentsLink + "1234")
            )
        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink",
            side_effect=Exception("some error"),
            autospec=True,
        ) as _ol, patch("logging.Logger.debug") as _l, patch(
            "logging.Logger.warning"
        ) as _w:
            self.assertEqual(elw.cellDoubleClick(elw.proxyModel.index(1, 4)), True)
            _ol.assert_called_once_with(
                pBGuiView, pbConfig.inspireExperimentsLink + "1234", "link"
            )
            _l.assert_called_once_with(
                "Opening '%s'..." % (pbConfig.inspireExperimentsLink + "1234")
            )
            _w.assert_called_once_with(
                "Opening link '%s' failed!"
                % (pbConfig.inspireExperimentsLink + "1234"),
                exc_info=True,
            )


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestEditExperimentDialog(GUITestCase):
    """Test EditExperimentDialog"""

    def test_init(self):
        """test init"""
        p = QWidget()
        with patch(
            "physbiblio.gui.expWindows.EditExperimentDialog.createForm", autospec=True
        ) as _cf:
            eed = EditExperimentDialog(p)
            _cf.assert_called_once_with(eed)
        self.assertIsInstance(eed, EditObjectWindow)
        self.assertEqual(eed.parent(), p)
        self.assertIsInstance(eed.data, dict)
        self.assertEqual(
            eed.data,
            {"idExp": "", "name": "", "homepage": "", "inspire": "", "comments": ""},
        )
        exp = {
            "idExp": "9999",
            "name": "myexp",
            "homepage": "www.some.exp",
            "inspire": "1234",
            "comments": "no comments",
        }
        with patch(
            "physbiblio.gui.expWindows.EditExperimentDialog.createForm", autospec=True
        ) as _cf:
            eed = EditExperimentDialog(parent=p, experiment=exp)
            _cf.assert_called_once_with(eed)
        self.assertEqual(eed.data, exp)

    def test_createForm(self):
        """test createForm"""
        p = QWidget()
        eed = EditExperimentDialog(p)
        self.assertEqual(eed.windowTitle(), "Edit experiment")

        self.assertIsInstance(eed.layout().itemAtPosition(1, 0).widget(), PBLabel)
        self.assertEqual(eed.layout().itemAtPosition(1, 0).widget().text(), "name")
        self.assertIsInstance(eed.layout().itemAtPosition(1, 1).widget(), PBLabel)
        self.assertEqual(
            eed.layout().itemAtPosition(1, 1).widget().text(),
            "(Name of the experiment)",
        )
        self.assertIsInstance(eed.layout().itemAtPosition(2, 0).widget(), QLineEdit)
        self.assertEqual(
            eed.layout().itemAtPosition(2, 0).widget(), eed.textValues["name"]
        )
        self.assertEqual(eed.textValues["name"].text(), "")
        self.assertEqual(eed.textValues["name"].isEnabled(), True)

        self.assertIsInstance(eed.layout().itemAtPosition(3, 0).widget(), PBLabel)
        self.assertEqual(eed.layout().itemAtPosition(3, 0).widget().text(), "comments")
        self.assertIsInstance(eed.layout().itemAtPosition(3, 1).widget(), PBLabel)
        self.assertEqual(
            eed.layout().itemAtPosition(3, 1).widget().text(),
            "(Description or comments)",
        )
        self.assertIsInstance(eed.layout().itemAtPosition(4, 0).widget(), QLineEdit)
        self.assertEqual(
            eed.layout().itemAtPosition(4, 0).widget(), eed.textValues["comments"]
        )
        self.assertEqual(eed.textValues["comments"].text(), "")
        self.assertEqual(eed.textValues["comments"].isEnabled(), True)

        self.assertIsInstance(eed.layout().itemAtPosition(5, 0).widget(), PBLabel)
        self.assertEqual(eed.layout().itemAtPosition(5, 0).widget().text(), "homepage")
        self.assertIsInstance(eed.layout().itemAtPosition(5, 1).widget(), PBLabel)
        self.assertEqual(
            eed.layout().itemAtPosition(5, 1).widget().text(),
            "(Web link to the experiment homepage)",
        )
        self.assertIsInstance(eed.layout().itemAtPosition(6, 0).widget(), QLineEdit)
        self.assertEqual(
            eed.layout().itemAtPosition(6, 0).widget(), eed.textValues["homepage"]
        )
        self.assertEqual(eed.textValues["homepage"].text(), "")
        self.assertEqual(eed.textValues["homepage"].isEnabled(), True)

        self.assertIsInstance(eed.layout().itemAtPosition(7, 0).widget(), PBLabel)
        self.assertEqual(eed.layout().itemAtPosition(7, 0).widget().text(), "inspire")
        self.assertIsInstance(eed.layout().itemAtPosition(7, 1).widget(), PBLabel)
        self.assertEqual(
            eed.layout().itemAtPosition(7, 1).widget().text(),
            "(INSPIRE-HEP ID of the experiment record)",
        )
        self.assertIsInstance(eed.layout().itemAtPosition(8, 0).widget(), QLineEdit)
        self.assertEqual(
            eed.layout().itemAtPosition(8, 0).widget(), eed.textValues["inspire"]
        )
        self.assertEqual(eed.textValues["inspire"].text(), "")
        self.assertEqual(eed.textValues["inspire"].isEnabled(), True)

        self.assertIsInstance(eed.layout().itemAtPosition(9, 0).widget(), QPushButton)
        self.assertEqual(eed.layout().itemAtPosition(9, 0).widget(), eed.acceptButton)
        self.assertEqual(eed.acceptButton.text(), "OK")
        self.assertIsInstance(eed.layout().itemAtPosition(9, 1).widget(), QPushButton)
        self.assertEqual(eed.layout().itemAtPosition(9, 1).widget(), eed.cancelButton)
        self.assertEqual(eed.cancelButton.text(), "Cancel")
        self.assertTrue(eed.cancelButton.autoDefault())
        with patch(
            "physbiblio.gui.commonClasses.EditObjectWindow.onOk", autospec=True
        ) as _f:
            QTest.mouseClick(eed.acceptButton, Qt.LeftButton)
            _f.assert_called_once_with(eed)
        with patch(
            "physbiblio.gui.commonClasses.EditObjectWindow.onCancel", autospec=True
        ) as _f:
            QTest.mouseClick(eed.cancelButton, Qt.LeftButton)
            _f.assert_called_once_with(eed)

        exp = {
            "idExp": "9999",
            "name": "myexp",
            "homepage": "www.some.exp",
            "inspire": "1234",
            "comments": "no comments",
        }
        eed = EditExperimentDialog(parent=p, experiment=exp)

        self.assertIsInstance(eed.layout().itemAtPosition(1, 0).widget(), PBLabel)
        self.assertEqual(eed.layout().itemAtPosition(1, 0).widget().text(), "idExp")
        self.assertIsInstance(eed.layout().itemAtPosition(1, 1).widget(), PBLabel)
        self.assertEqual(
            eed.layout().itemAtPosition(1, 1).widget().text(),
            "(Unique ID that identifies the experiment)",
        )
        self.assertIsInstance(eed.layout().itemAtPosition(2, 0).widget(), QLineEdit)
        self.assertEqual(
            eed.layout().itemAtPosition(2, 0).widget(), eed.textValues["idExp"]
        )
        self.assertEqual(eed.textValues["idExp"].text(), "9999")
        self.assertEqual(eed.textValues["idExp"].isEnabled(), False)

        self.assertIsInstance(eed.layout().itemAtPosition(3, 0).widget(), PBLabel)
        self.assertEqual(eed.layout().itemAtPosition(3, 0).widget().text(), "name")
        self.assertIsInstance(eed.layout().itemAtPosition(3, 1).widget(), PBLabel)
        self.assertEqual(
            eed.layout().itemAtPosition(3, 1).widget().text(),
            "(Name of the experiment)",
        )
        self.assertIsInstance(eed.layout().itemAtPosition(4, 0).widget(), QLineEdit)
        self.assertEqual(
            eed.layout().itemAtPosition(4, 0).widget(), eed.textValues["name"]
        )
        self.assertEqual(eed.textValues["name"].text(), "myexp")
        self.assertEqual(eed.textValues["name"].isEnabled(), True)

        self.assertIsInstance(eed.layout().itemAtPosition(5, 0).widget(), PBLabel)
        self.assertEqual(eed.layout().itemAtPosition(5, 0).widget().text(), "comments")
        self.assertIsInstance(eed.layout().itemAtPosition(5, 1).widget(), PBLabel)
        self.assertEqual(
            eed.layout().itemAtPosition(5, 1).widget().text(),
            "(Description or comments)",
        )
        self.assertIsInstance(eed.layout().itemAtPosition(6, 0).widget(), QLineEdit)
        self.assertEqual(
            eed.layout().itemAtPosition(6, 0).widget(), eed.textValues["comments"]
        )
        self.assertEqual(eed.textValues["comments"].text(), "no comments")
        self.assertEqual(eed.textValues["comments"].isEnabled(), True)

        self.assertIsInstance(eed.layout().itemAtPosition(7, 0).widget(), PBLabel)
        self.assertEqual(eed.layout().itemAtPosition(7, 0).widget().text(), "homepage")
        self.assertIsInstance(eed.layout().itemAtPosition(7, 1).widget(), PBLabel)
        self.assertEqual(
            eed.layout().itemAtPosition(7, 1).widget().text(),
            "(Web link to the experiment homepage)",
        )
        self.assertIsInstance(eed.layout().itemAtPosition(8, 0).widget(), QLineEdit)
        self.assertEqual(
            eed.layout().itemAtPosition(8, 0).widget(), eed.textValues["homepage"]
        )
        self.assertEqual(eed.textValues["homepage"].text(), "www.some.exp")
        self.assertEqual(eed.textValues["homepage"].isEnabled(), True)

        self.assertIsInstance(eed.layout().itemAtPosition(9, 0).widget(), PBLabel)
        self.assertEqual(eed.layout().itemAtPosition(9, 0).widget().text(), "inspire")
        self.assertIsInstance(eed.layout().itemAtPosition(9, 1).widget(), PBLabel)
        self.assertEqual(
            eed.layout().itemAtPosition(9, 1).widget().text(),
            "(INSPIRE-HEP ID of the experiment record)",
        )
        self.assertIsInstance(eed.layout().itemAtPosition(10, 0).widget(), QLineEdit)
        self.assertEqual(
            eed.layout().itemAtPosition(10, 0).widget(), eed.textValues["inspire"]
        )
        self.assertEqual(eed.textValues["inspire"].text(), "1234")
        self.assertEqual(eed.textValues["inspire"].isEnabled(), True)
        self.assertEqual(eed.layout().itemAtPosition(11, 0).widget(), eed.acceptButton)
        self.assertEqual(eed.layout().itemAtPosition(11, 1).widget(), eed.cancelButton)


if __name__ == "__main__":
    unittest.main()
