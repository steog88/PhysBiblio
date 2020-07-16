#!/usr/bin/env python
"""Test file for the physbiblio.gui.dialogWindows module.

This file is part of the physbiblio package.
"""
import os
import sys
import traceback

from PySide2.QtCore import QEvent, QModelIndex, QPoint, QRect, Qt
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QWidget

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import MagicMock, call, patch
else:
    import unittest
    from unittest.mock import MagicMock, call, patch

try:
    from physbiblio.config import configuration_params, pbConfig
    from physbiblio.database import pBDB
    from physbiblio.gui.bibWindows import AbstractFormulas
    from physbiblio.gui.dialogWindows import *
    from physbiblio.gui.setuptests import *
    from physbiblio.setuptests import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise


class Fake_abstractFormulas:
    """Used to test `DailyArxivSelect.cellClick`"""

    def __init__(self):
        """empty constructor"""
        return

    def __call__(self, p, abstract, customEditor=None, statusMessages=True):
        """Save some attributes and return self.el

        Parameters: (see also `physbiblio.gui.bibWindows.AbstractFormulas`)
            p: parent widget
            abstract: the abstract
            customEditor: widget where to store the processed text
            statusMessages: print status messages
        """
        self.par = p
        self.abstract = abstract
        self.ce = customEditor
        self.sm = statusMessages
        self.el = AbstractFormulas(
            p, abstract, customEditor=self.ce, statusMessages=self.sm
        )
        return self.el


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestConfigEditColumns(GUITestCase):
    """Test ConfigEditColumns"""

    @classmethod
    def setUpClass(self):
        """set temporary settings"""
        super(TestConfigEditColumns, self).setUpClass()
        self.defCols = [
            a["default"]
            for a in configuration_params.values()
            if a["name"] == "bibtexListColumns"
        ][0]

    @patch.dict(
        pbConfig.params,
        {
            "bibtexListColumns": [
                a["default"]
                for a in configuration_params.values()
                if a["name"] == "bibtexListColumns"
            ][0]
        },
        clear=False,
    )
    def test_init(self):
        """Test __init__"""
        p = QWidget()
        with patch(
            "physbiblio.gui.dialogWindows.ConfigEditColumns.initUI", autospec=True
        ) as _u:
            cec = ConfigEditColumns()
            self.assertIsInstance(cec, PBDialog)
            self.assertEqual(cec.parent(), None)
            _u.assert_called_once_with(cec)
            cec = ConfigEditColumns(p)
            self.assertIsInstance(cec, PBDialog)
            self.assertEqual(cec.parent(), p)
            self.assertEqual(
                cec.excludeCols,
                [
                    "crossref",
                    "bibtex",
                    "exp_paper",
                    "lecture",
                    "phd_thesis",
                    "review",
                    "proceeding",
                    "book",
                    "noUpdate",
                    "bibdict",
                    "abstract",
                ],
            )
            self.assertEqual(
                cec.moreCols,
                [
                    "title",
                    "author",
                    "journal",
                    "volume",
                    "pages",
                    "primaryclass",
                    "booktitle",
                    "reportnumber",
                ],
            )
            self.assertEqual(cec.previousSelected, self.defCols)
            self.assertEqual(cec.selected, self.defCols)
            cec = ConfigEditColumns(p, ["bibkey", "author", "title"])
            self.assertEqual(cec.previousSelected, ["bibkey", "author", "title"])

    @patch.dict(
        pbConfig.params,
        {
            "bibtexListColumns": [
                a["default"]
                for a in configuration_params.values()
                if a["name"] == "bibtexListColumns"
            ][0]
        },
        clear=False,
    )
    def test_onCancel(self):
        """test onCancel"""
        cec = ConfigEditColumns()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            cec.onCancel()
            self.assertFalse(cec.result)
            self.assertEqual(_c.call_count, 1)

    @patch.dict(
        pbConfig.params,
        {
            "bibtexListColumns": [
                a["default"]
                for a in configuration_params.values()
                if a["name"] == "bibtexListColumns"
            ][0]
        },
        clear=False,
    )
    def test_onOk(self):
        """test onOk"""
        p = QWidget()
        cec = ConfigEditColumns(p, ["bibkey", "author", "title"])
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            cec.onOk()
            self.assertTrue(cec.result)
            self.assertEqual(_c.call_count, 1)
        self.assertEqual(cec.selected, ["bibkey", "author", "title"])
        item = QTableWidgetItem("arxiv")
        cec.listSel.insertRow(3)
        cec.listSel.setItem(3, 0, item)
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            cec.onOk()
        self.assertEqual(cec.selected, ["bibkey", "author", "title", "arxiv"])

    @patch.dict(
        pbConfig.params,
        {
            "bibtexListColumns": [
                a["default"]
                for a in configuration_params.values()
                if a["name"] == "bibtexListColumns"
            ][0]
        },
        clear=False,
    )
    def test_initUI(self):
        """test initUI"""
        p = QWidget()
        cec = ConfigEditColumns(p, ["bibkey", "author", "title"])
        self.assertIsInstance(cec.layout(), QGridLayout)
        self.assertEqual(cec.layout(), cec.gridlayout)
        self.assertIsInstance(cec.items, list)
        self.assertIsInstance(cec.allItems, list)
        self.assertIsInstance(cec.selItems, list)
        self.assertIsInstance(cec.listAll, PBDDTableWidget)
        self.assertIsInstance(cec.listSel, PBDDTableWidget)
        self.assertIsInstance(cec.layout().itemAtPosition(0, 0).widget(), PBLabel)
        self.assertEqual(
            cec.layout().itemAtPosition(0, 0).widget().text(),
            "Drag and drop items to order visible columns",
        )
        self.assertEqual(cec.layout().itemAtPosition(1, 0).widget(), cec.listAll)
        self.assertEqual(cec.layout().itemAtPosition(1, 1).widget(), cec.listSel)
        self.assertEqual(
            cec.allItems, list(pBDB.descriptions["entries"]) + cec.moreCols
        )
        self.assertEqual(cec.selItems, cec.previousSelected)

        self.assertEqual(cec.listSel.rowCount(), 3)
        for ix, col in enumerate(["bibkey", "author", "title"]):
            item = cec.listSel.item(ix, 0)
            self.assertEqual(item.text(), col)
            self.assertIs(item, cec.items[ix])

        allCols = [
            i
            for i in cec.allItems
            if i not in cec.selItems and i not in cec.excludeCols
        ]
        self.assertEqual(cec.listAll.rowCount(), len(allCols))
        for ix, col in enumerate(allCols):
            item = cec.listAll.item(ix, 0)
            self.assertEqual(item.text(), col)
            self.assertIs(item, cec.items[ix + 3])

        self.assertIsInstance(cec.acceptButton, QPushButton)
        self.assertIsInstance(cec.cancelButton, QPushButton)
        self.assertEqual(cec.acceptButton.text(), "OK")
        self.assertEqual(cec.cancelButton.text(), "Cancel")
        self.assertTrue(cec.cancelButton.autoDefault())
        self.assertEqual(cec.layout().itemAtPosition(2, 0).widget(), cec.acceptButton)
        self.assertEqual(cec.layout().itemAtPosition(2, 1).widget(), cec.cancelButton)
        with patch(
            "physbiblio.gui.dialogWindows.ConfigEditColumns.onOk", autospec=True
        ) as _f:
            QTest.mouseClick(cec.acceptButton, Qt.LeftButton)
            _f.assert_called_once_with(cec)
        with patch(
            "physbiblio.gui.dialogWindows.ConfigEditColumns.onCancel", autospec=True
        ) as _f:
            QTest.mouseClick(cec.cancelButton, Qt.LeftButton)
            _f.assert_called_once_with(cec)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestConfigWindow(GUITestCase):
    """Test ConfigWindow"""

    def test_init(self):
        """Test __init__"""
        p = QWidget()
        with patch(
            "physbiblio.gui.dialogWindows.ConfigWindow.initUI", autospec=True
        ) as _iu:
            cw = ConfigWindow(p)
            self.assertIsInstance(cw, PBDialog)
            self.assertEqual(cw.parent(), p)
            self.assertEqual(cw.textValues, [])
            _iu.assert_called_once_with(cw)

    def test_onCancel(self):
        """test onCancel"""
        cw = ConfigWindow()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            cw.onCancel()
            self.assertFalse(cw.result)
            self.assertEqual(_c.call_count, 1)

    def test_onOk(self):
        """test onOk"""
        cw = ConfigWindow()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            cw.onOk()
            self.assertTrue(cw.result)
            self.assertEqual(_c.call_count, 1)

    def test_editPDFFolder(self):
        """test editPDFFolder"""
        cw = ConfigWindow()
        ix = pbConfig.paramOrder.index("pdfFolder")
        self.assertEqual(cw.textValues[ix][1].text(), pbConfig.params["pdfFolder"])
        with patch(
            "physbiblio.gui.dialogWindows.askDirName",
            return_value="/some/new/folder/",
            autospec=True,
        ) as _adn:
            cw.editPDFFolder()
            self.assertEqual(cw.textValues[ix][1].text(), "/some/new/folder/")
            _adn.assert_called_once_with(
                parent=None,
                dir=pbConfig.params["pdfFolder"],
                title="Directory for saving PDF files:",
            )
        with patch(
            "physbiblio.gui.dialogWindows.askDirName", return_value="", autospec=True
        ) as _adn:
            cw.editPDFFolder()
            self.assertEqual(cw.textValues[ix][1].text(), "/some/new/folder/")
            _adn.assert_called_once_with(
                parent=None,
                dir="/some/new/folder/",
                title="Directory for saving PDF files:",
            )

    def test_editFile(self):
        """test editFile"""
        cw = ConfigWindow()
        ix = pbConfig.paramOrder.index("logFileName")
        self.assertEqual(cw.textValues[ix][1].text(), pbConfig.params["logFileName"])
        with patch(
            "physbiblio.gui.dialogWindows.askSaveFileName",
            return_value="/some/new/folder/file.log",
            autospec=True,
        ) as _adn:
            cw.editFile()
            self.assertEqual(cw.textValues[ix][1].text(), "/some/new/folder/file.log")
            _adn.assert_called_once_with(
                parent=None,
                title="Name for the log file",
                dir=pbConfig.params["logFileName"],
                filter="*.log",
            )
        with patch(
            "physbiblio.gui.dialogWindows.askSaveFileName",
            return_value="  ",
            autospec=True,
        ) as _adn:
            cw.editFile(text="Name", filter="*.txt")
            self.assertEqual(cw.textValues[ix][1].text(), "/some/new/folder/file.log")
            _adn.assert_called_once_with(
                parent=None,
                title="Name",
                dir="/some/new/folder/file.log",
                filter="*.txt",
            )
        with patch("logging.Logger.warning") as _w:
            cw.editFile("someField")
            _w.assert_called_once_with("Invalid paramkey: 'someField'")

    def test_editColumns(self):
        """test editColumns"""
        cw = ConfigWindow()
        ix = pbConfig.paramOrder.index("bibtexListColumns")
        self.assertEqual(
            ast.literal_eval(cw.textValues[ix][1].text()),
            pbConfig.params["bibtexListColumns"],
        )
        cec = ConfigEditColumns(cw, ["bibkey", "author", "title"])
        cec.exec_ = MagicMock()
        cec.onCancel()
        with patch(
            "physbiblio.gui.dialogWindows.ConfigEditColumns",
            return_value=cec,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _cec:
            cw.editColumns()
            _cec.assert_called_once_with(cw, pbConfig.params["bibtexListColumns"])
        self.assertEqual(
            ast.literal_eval(cw.textValues[ix][1].text()),
            pbConfig.params["bibtexListColumns"],
        )
        cec = ConfigEditColumns(cw, ["bibkey", "author", "title"])
        cec.exec_ = MagicMock()
        cec.onOk()
        with patch(
            "physbiblio.gui.dialogWindows.ConfigEditColumns",
            return_value=cec,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _cec:
            cw.editColumns()
            _cec.assert_called_once_with(cw, pbConfig.params["bibtexListColumns"])
        self.assertEqual(
            ast.literal_eval(cw.textValues[ix][1].text()), ["bibkey", "author", "title"]
        )

    def test_editDefCats(self):
        """test editDefCats"""
        cw = ConfigWindow()
        ix = pbConfig.paramOrder.index("defaultCategories")
        self.assertEqual(
            ast.literal_eval(cw.textValues[ix][1].text()),
            pbConfig.params["defaultCategories"],
        )
        cwl = CatsTreeWindow(parent=cw, askCats=True, expButton=False, previous=["1"])
        cwl.exec_ = MagicMock()
        cwl.onCancel()
        with patch(
            "physbiblio.gui.dialogWindows.CatsTreeWindow",
            return_value=cwl,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _cwl:
            cw.editDefCats()
            _cwl.assert_called_once_with(
                parent=cw,
                askCats=True,
                expButton=False,
                previous=pbConfig.params["defaultCategories"],
            )
        self.assertEqual(
            ast.literal_eval(cw.textValues[ix][1].text()),
            pbConfig.params["defaultCategories"],
        )
        cwl = CatsTreeWindow(parent=cw, askCats=True, expButton=False, previous=["1"])
        cwl.exec_ = MagicMock()
        cwl.onOk()
        cw.selectedCats = ["1"]
        with patch(
            "physbiblio.gui.dialogWindows.CatsTreeWindow",
            return_value=cwl,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _cwl:
            cw.editDefCats()
            _cwl.assert_called_once_with(
                parent=cw,
                askCats=True,
                expButton=False,
                previous=pbConfig.params["defaultCategories"],
            )
        self.assertEqual(ast.literal_eval(cw.textValues[ix][1].text()), ["1"])

    def test_initUI(self):
        """test initUI"""
        cw = ConfigWindow()
        self.assertEqual(cw.windowTitle(), "Configuration")
        self.assertIsInstance(cw.layout(), QGridLayout)
        self.assertEqual(cw.layout(), cw.grid)
        self.assertEqual(cw.grid.spacing(), 1)

        for ix, k in enumerate(pbConfig.paramOrder):
            self.assertIsInstance(cw.layout().itemAtPosition(ix, 0).widget(), PBLabel)
            self.assertEqual(
                cw.layout().itemAtPosition(ix, 0).widget().text(),
                "%s (<i>%s</i>%s)"
                % (
                    configuration_params[k].description,
                    k,
                    " - global setting" if configuration_params[k].isGlobal else "",
                ),
            )
            if k == "bibtexListColumns":
                currClass = QPushButton
                currWidget = cw.textValues[ix][1]
                self.assertIsInstance(currWidget, currClass)
                self.assertEqual(currWidget.text(), "%s" % pbConfig.params[k])
                with patch(
                    "physbiblio.gui.dialogWindows.ConfigWindow.editColumns",
                    autospec=True,
                ) as _f:
                    QTest.mouseClick(currWidget, Qt.LeftButton)
                    _f.assert_called_once_with(cw)
            elif k == "pdfFolder":
                currClass = QPushButton
                currWidget = cw.textValues[ix][1]
                self.assertIsInstance(currWidget, currClass)
                self.assertEqual(currWidget.text(), "%s" % pbConfig.params[k])
                with patch(
                    "physbiblio.gui.dialogWindows.ConfigWindow.editPDFFolder",
                    autospec=True,
                ) as _f:
                    QTest.mouseClick(currWidget, Qt.LeftButton)
                    _f.assert_called_once_with(cw)
            elif k == "loggingLevel":
                currClass = PBComboBox
                currWidget = cw.textValues[ix][1]
                self.assertIsInstance(currWidget, currClass)
                self.assertEqual(
                    currWidget.currentText(),
                    pbConfig.loggingLevels[int(pbConfig.params[k])],
                )
                self.assertEqual(currWidget.count(), len(pbConfig.loggingLevels))
                for j, l in enumerate(pbConfig.loggingLevels):
                    self.assertEqual(currWidget.itemText(j), pbConfig.loggingLevels[j])
            elif k == "logFileName":
                currClass = QPushButton
                currWidget = cw.textValues[ix][1]
                self.assertIsInstance(currWidget, currClass)
                self.assertEqual(currWidget.text(), "%s" % pbConfig.params[k])
                with patch(
                    "physbiblio.gui.dialogWindows.ConfigWindow.editFile", autospec=True
                ) as _f:
                    QTest.mouseClick(currWidget, Qt.LeftButton)
                    _f.assert_called_once_with(cw)
            elif k == "defaultCategories":
                currClass = QPushButton
                currWidget = cw.textValues[ix][1]
                self.assertIsInstance(currWidget, currClass)
                self.assertEqual(currWidget.text(), "%s" % pbConfig.params[k])
                with patch(
                    "physbiblio.gui.dialogWindows.ConfigWindow.editDefCats",
                    autospec=True,
                ) as _f:
                    QTest.mouseClick(currWidget, Qt.LeftButton)
                    _f.assert_called_once_with(cw)
            elif configuration_params[k].special == "boolean":
                currClass = PBTrueFalseCombo
                currWidget = cw.textValues[ix][1]
                self.assertIsInstance(currWidget, currClass)
                self.assertEqual(currWidget.currentText(), "%s" % pbConfig.params[k])
            else:
                currClass = QLineEdit
                currWidget = cw.textValues[ix][1]
                self.assertIsInstance(currWidget, currClass)
                self.assertEqual(currWidget.text(), "%s" % pbConfig.params[k])
            self.assertIsInstance(cw.layout().itemAtPosition(ix, 2).widget(), currClass)
            self.assertEqual(cw.layout().itemAtPosition(ix, 2).widget(), currWidget)

        self.assertIsInstance(cw.acceptButton, QPushButton)
        self.assertIsInstance(cw.cancelButton, QPushButton)
        self.assertEqual(cw.acceptButton.text(), "OK")
        self.assertEqual(cw.cancelButton.text(), "Cancel")
        self.assertTrue(cw.cancelButton.autoDefault())
        ix = len(pbConfig.paramOrder)
        self.assertEqual(cw.layout().itemAtPosition(ix, 0).widget(), cw.acceptButton)
        self.assertEqual(cw.layout().itemAtPosition(ix, 1).widget(), cw.cancelButton)
        with patch(
            "physbiblio.gui.dialogWindows.ConfigWindow.onOk", autospec=True
        ) as _f:
            QTest.mouseClick(cw.acceptButton, Qt.LeftButton)
            _f.assert_called_once_with(cw)
        with patch(
            "physbiblio.gui.dialogWindows.ConfigWindow.onCancel", autospec=True
        ) as _f:
            QTest.mouseClick(cw.cancelButton, Qt.LeftButton)
            _f.assert_called_once_with(cw)

        # test non valid value for loggingLevel
        with patch("logging.Logger.warning") as _w, patch.dict(
            pbConfig.params, {"loggingLevel": "10"}, clear=False
        ):
            cw = ConfigWindow()
            _w.assert_called_once_with(
                "Invalid string for 'loggingLevel' param. Reset to default"
            )
        with patch("logging.Logger.warning") as _w, patch.dict(
            pbConfig.params, {"loggingLevel": "abc"}, clear=False
        ):
            cw = ConfigWindow()
            _w.assert_called_once_with(
                "Invalid string for 'loggingLevel' param. Reset to default"
            )
        for ix, k in enumerate(pbConfig.paramOrder):
            if k == "loggingLevel":
                currClass = PBComboBox
                currWidget = cw.textValues[ix][1]
                self.assertIsInstance(currWidget, currClass)
                self.assertEqual(
                    currWidget.currentText(),
                    pbConfig.loggingLevels[
                        int(configuration_params["loggingLevel"].default)
                    ],
                )
                self.assertEqual(currWidget.count(), len(pbConfig.loggingLevels))
                for j, l in enumerate(pbConfig.loggingLevels):
                    self.assertEqual(currWidget.itemText(j), pbConfig.loggingLevels[j])


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestLogFileContentDialog(GUITestCase):
    """Test LogFileContentDialog"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        with patch(
            "physbiblio.gui.dialogWindows.LogFileContentDialog.initUI", autospec=True
        ) as _u:
            lf = LogFileContentDialog(p)
            self.assertIsInstance(lf, PBDialog)
            self.assertEqual(lf.parent(), p)
            self.assertEqual(lf.title, "Log File Content")
            _u.assert_called_once_with(lf)
        if os.path.exists(pbConfig.params["logFileName"]):
            os.remove(pbConfig.params["logFileName"])

    def test_clearLog(self):
        """test clearLog"""
        p = QWidget()
        with open(pbConfig.params["logFileName"], "w") as _f:
            _f.write("test content")
        lf = LogFileContentDialog(p)
        ayn_str = "physbiblio.gui.dialogWindows.askYesNo"
        with patch(ayn_str, return_value=False, autospec=True) as _ayn:
            lf.clearLog()
            with open(pbConfig.params["logFileName"]) as _f:
                text = _f.read()
            self.assertEqual(text, "test content")
        with patch(ayn_str, return_value=True, autospec=True) as _ayn, patch(
            "physbiblio.gui.dialogWindows.infoMessage", autospec=True
        ) as _in, patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            lf.clearLog()
            with open(pbConfig.params["logFileName"]) as _f:
                text = _f.read()
            self.assertEqual(text, "")
            _in.assert_called_once_with("Log file cleared.")
            _c.assert_called_once_with()
        if os.path.exists(pbConfig.params["logFileName"]):
            os.remove(pbConfig.params["logFileName"])
        openModule = "__builtin__.open" if sys.version_info[0] < 3 else "builtins.open"
        with patch(ayn_str, return_value=True, autospec=True) as _ayn, patch(
            openModule, side_effect=IOError("fake"), autospec=True
        ) as _op, patch("logging.Logger.exception") as _ex, patch(
            "PySide2.QtWidgets.QDialog.close", autospec=True
        ) as _c:
            lf.clearLog()
            _ex.assert_called_once_with("Impossible to clear log file!")
            _c.assert_not_called()
        if os.path.exists(pbConfig.params["logFileName"]):
            os.remove(pbConfig.params["logFileName"])

    def test_initUI(self):
        """test initUI"""
        p = QWidget()
        if os.path.exists(pbConfig.params["logFileName"]):
            os.remove(pbConfig.params["logFileName"])
        with patch("logging.Logger.exception") as _ex:
            lf = LogFileContentDialog(p)
            _ex.assert_called_once_with("Impossible to read log file!")
            self.assertIsInstance(lf.textEdit, QPlainTextEdit)
            self.assertEqual(lf.textEdit.toPlainText(), "Impossible to read log file!")
        with open(pbConfig.params["logFileName"], "w") as _f:
            _f.write("test content")
        lf = LogFileContentDialog(p)
        self.assertEqual(lf.windowTitle(), lf.title)
        self.assertIsInstance(lf.layout(), QVBoxLayout)
        self.assertEqual(lf.layout().spacing(), 1)
        self.assertIsInstance(lf.layout().itemAt(0).widget(), PBLabel)
        self.assertEqual(
            lf.layout().itemAt(0).widget().text(),
            "Reading %s" % pbConfig.params["logFileName"],
        )
        self.assertIsInstance(lf.textEdit, QPlainTextEdit)
        self.assertTrue(lf.textEdit.isReadOnly())
        self.assertEqual(lf.textEdit.toPlainText(), "test content")
        self.assertIsInstance(lf.layout().itemAt(1).widget(), QPlainTextEdit)
        self.assertEqual(lf.textEdit, lf.layout().itemAt(1).widget())
        self.assertIsInstance(lf.layout().itemAt(2).widget(), QPushButton)
        self.assertEqual(lf.layout().itemAt(2).widget(), lf.closeButton)
        self.assertTrue(lf.closeButton.autoDefault())
        self.assertEqual(lf.closeButton.text(), "Close")
        self.assertIsInstance(lf.layout().itemAt(3).widget(), QPushButton)
        self.assertEqual(lf.layout().itemAt(3).widget(), lf.clearButton)
        self.assertEqual(lf.clearButton.text(), "Clear log file")
        if os.path.exists(pbConfig.params["logFileName"]):
            os.remove(pbConfig.params["logFileName"])


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestPrintText(GUITestCase):
    """Test PrintText"""

    def test_init(self):
        """test init"""
        with patch(
            "physbiblio.gui.dialogWindows.PrintText.initUI", autospec=True
        ) as _u:
            pt = PrintText()
            _u.assert_called_once_with(pt)
        self.assertIsInstance(pt, PBDialog)
        self.assertIsInstance(pt.stopped, Signal)
        self.assertIsInstance(pt.pbMax, Signal)
        self.assertIsInstance(pt.pbVal, Signal)
        self.assertEqual(pt._wantToClose, False)
        self.assertEqual(pt.parent(), None)
        self.assertEqual(pt.title, "Redirect print")
        self.assertEqual(pt.setProgressBar, True)
        self.assertEqual(pt.noStopButton, False)
        self.assertEqual(pt.message, None)
        with patch(
            "physbiblio.gui.dialogWindows.PrintText.progressBarMax", autospec=True
        ) as _m, patch(
            "physbiblio.gui.dialogWindows.PrintText.progressBarValue", autospec=True
        ) as _v, patch(
            "physbiblio.gui.dialogWindows.PrintText.initUI", autospec=True
        ) as _u:
            pt = PrintText()
            _u.assert_called_once_with(pt)
            pt.pbMax.emit(1)
            _m.assert_called_once_with(pt, 1)
            pt.pbVal.emit(2)
            _v.assert_called_once_with(pt, 2)

        p = QWidget()
        pt = PrintText(p, "title", False, True, "mymessage")
        self.assertEqual(pt.parent(), p)
        self.assertEqual(pt.title, "title")
        self.assertEqual(pt.setProgressBar, False)
        self.assertEqual(pt.noStopButton, True)
        self.assertEqual(pt.message, "mymessage")

    def test_keyPressEvent(self):
        """test keyPressEvent"""
        p = QWidget()
        pt = PrintText(p)
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _oc:
            QTest.keyPress(pt, "a")
            _oc.assert_not_called()
            QTest.keyPress(pt, Qt.Key_Enter)
            _oc.assert_not_called()
            QTest.keyPress(pt, Qt.Key_Escape)
            _oc.assert_not_called()
            pt.enableClose()
            QTest.keyPress(pt, Qt.Key_Escape)
            self.assertEqual(_oc.call_count, 1)

    def test_closeEvent(self):
        """test closeEvent"""
        p = QWidget()
        pt = PrintText(p)
        e = QEvent(QEvent.Close)
        with patch("PySide2.QtCore.QEvent.ignore", autospec=True) as _i:
            pt.closeEvent(e)
            _i.assert_called_once_with()
        pt._wantToClose = True
        with patch("PySide2.QtWidgets.QDialog.closeEvent", autospec=True) as _c:
            pt.closeEvent(e)
            _c.assert_called_once_with(e)

    def test_initUI(self):
        """test initUI"""
        p = QWidget()
        pt = PrintText(p, progressBar=False, noStopButton=True)
        self.assertEqual(pt.windowTitle(), "Redirect print")
        self.assertIsInstance(pt.layout(), QGridLayout)
        self.assertEqual(pt.layout(), pt.grid)
        self.assertEqual(pt.grid.spacing(), 1)
        self.assertIsInstance(pt.grid.itemAtPosition(0, 0).widget(), QTextEdit)
        self.assertEqual(pt.grid.itemAtPosition(0, 0).widget(), pt.textEdit)
        self.assertEqual(pt.textEdit.toPlainText(), "")
        self.assertIsInstance(pt.grid.itemAtPosition(1, 0).widget(), QPushButton)
        self.assertEqual(pt.grid.itemAtPosition(1, 0).widget(), pt.closeButton)
        self.assertEqual(pt.closeButton.text(), "Close")
        self.assertFalse(pt.closeButton.isEnabled())

        pt = PrintText(p, "title", True, False, "mymessage")
        self.assertIsInstance(pt.grid.itemAtPosition(0, 0).widget(), PBLabel)
        self.assertEqual(pt.grid.itemAtPosition(0, 0).widget().text(), pt.message)
        self.assertIsInstance(pt.grid.itemAtPosition(1, 0).widget(), QTextEdit)
        self.assertEqual(pt.grid.itemAtPosition(1, 0).widget(), pt.textEdit)
        self.assertEqual(pt.textEdit.toPlainText(), "")
        self.assertIsInstance(pt.grid.itemAtPosition(2, 0).widget(), QProgressBar)
        self.assertEqual(pt.grid.itemAtPosition(2, 0).widget(), pt.progressBar)
        self.assertEqual(pt.progressBar.value(), -1)
        self.assertEqual(pt.progressBar.minimum(), 0)
        self.assertEqual(pt.progressBar.maximum(), 100)
        self.assertIsInstance(pt.grid.itemAtPosition(3, 0).widget(), QPushButton)
        self.assertEqual(pt.grid.itemAtPosition(3, 0).widget(), pt.cancelButton)
        self.assertEqual(pt.cancelButton.text(), "Stop")
        self.assertTrue(pt.cancelButton.autoDefault())
        with patch(
            "physbiblio.gui.dialogWindows.PrintText.stopExec", autospec=True
        ) as _s:
            QTest.mouseClick(pt.cancelButton, Qt.LeftButton)
            _s.assert_called_once_with(pt)
        self.assertIsInstance(pt.grid.itemAtPosition(4, 0).widget(), QPushButton)
        self.assertEqual(pt.grid.itemAtPosition(4, 0).widget(), pt.closeButton)
        self.assertEqual(pt.closeButton.text(), "Close")
        self.assertFalse(pt.closeButton.isEnabled())
        with patch("PySide2.QtWidgets.QDialog.reject", autospec=True) as _s:
            QTest.mouseClick(pt.closeButton, Qt.LeftButton)
            _s.assert_not_called()
            pt.enableClose()
            self.assertTrue(pt.closeButton.isEnabled())

        with patch(
            "physbiblio.gui.dialogWindows.PrintText.centerWindow", autospec=True
        ) as _c:
            pt.initUI()
            _c.assert_called_once_with(pt)

    def test_appendText(self):
        """test appendText"""
        p = QWidget()
        pt = PrintText(p)
        self.assertEqual(pt.textEdit.toPlainText(), "")
        pt.appendText("abcd")
        self.assertEqual(pt.textEdit.toPlainText(), "abcd")
        pt.textEdit.moveCursor(QTextCursor.Start)
        pt.appendText("\nefgh")
        self.assertEqual(pt.textEdit.toPlainText(), "abcd\nefgh")

    def test_progressBarMin(self):
        """test progressBarMin"""
        pt = PrintText()
        self.assertIsInstance(pt.progressBar, QProgressBar)
        pt.progressBarMin(1234.0)
        self.assertEqual(pt.progressBar.minimum(), 1234.0)

    def test_progressBarMax(self):
        """test progressBarMax"""
        pt = PrintText()
        self.assertIsInstance(pt.progressBar, QProgressBar)
        pt.progressBarMax(1234)
        self.assertEqual(pt.progressBar.maximum(), 1234)

    def test_progressBarValue(self):
        """test progressBarValue"""
        pt = PrintText()
        self.assertIsInstance(pt.progressBar, QProgressBar)
        pt.progressBarMax(4321)
        pt.progressBarValue(1234.0)
        self.assertEqual(pt.progressBar.value(), 1234.0)

    def test_stopExec(self):
        """test stopExec"""
        self.stop = False

        def stoppedAct(a=self):
            a.stop = True

        pt = PrintText()
        pt.stopped.connect(stoppedAct)
        self.assertTrue(pt.cancelButton.isEnabled())
        self.assertFalse(self.stop)
        pt.stopExec()
        self.assertFalse(pt.cancelButton.isEnabled())
        self.assertTrue(self.stop)

    def test_enableClose(self):
        """test enableClose"""
        pt = PrintText()
        self.assertFalse(pt.closeButton.isEnabled())
        self.assertTrue(pt.cancelButton.isEnabled())
        self.assertFalse(pt._wantToClose)
        pt.enableClose()
        self.assertTrue(pt.closeButton.isEnabled())
        self.assertTrue(pt._wantToClose)
        self.assertFalse(pt.cancelButton.isEnabled())
        pt = PrintText(noStopButton=True)
        self.assertFalse(pt.closeButton.isEnabled())
        self.assertFalse(pt._wantToClose)
        pt.enableClose()
        self.assertTrue(pt.closeButton.isEnabled())
        self.assertTrue(pt._wantToClose)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestAdvImportDialog(GUITestCase):
    """Test AdvancedImportDialog"""

    def test_init(self):
        """Test __init__"""
        p = QWidget()
        with patch(
            "physbiblio.gui.dialogWindows.AdvancedImportDialog.initUI", autospec=True
        ) as _iu:
            aid = AdvancedImportDialog(p)
            self.assertIsInstance(aid, PBDialog)
            self.assertEqual(aid.parent(), p)
            _iu.assert_called_once_with(aid)

    def test_onCancel(self):
        """test onCancel"""
        aid = AdvancedImportDialog()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            aid.onCancel()
            self.assertFalse(aid.result)
            self.assertEqual(_c.call_count, 1)

    def test_onOk(self):
        """test onOk"""
        aid = AdvancedImportDialog()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            aid.onOk()
            self.assertTrue(aid.result)
            self.assertEqual(_c.call_count, 1)

    def test_initUI(self):
        """test initUI"""
        with patch(
            "physbiblio.gui.commonClasses.PBDialog.centerWindow", autospec=True
        ) as _cw:
            aid = AdvancedImportDialog()
            _cw.assert_called_once_with(aid)
        self.assertEqual(aid.windowTitle(), "Advanced import")
        self.assertIsInstance(aid.layout(), QGridLayout)
        self.assertEqual(aid.grid, aid.layout())
        self.assertEqual(aid.grid.spacing(), 1)

        self.assertIsInstance(aid.grid.itemAtPosition(0, 0).widget(), PBLabel)
        self.assertEqual(
            aid.grid.itemAtPosition(0, 0).widget().text(), "Search string: "
        )
        self.assertIsInstance(aid.grid.itemAtPosition(1, 0).widget(), PBLabel)
        self.assertEqual(
            aid.grid.itemAtPosition(1, 0).widget().text(), "Select method: "
        )

        le = aid.grid.itemAtPosition(0, 1).widget()
        self.assertIsInstance(le, QLineEdit)
        self.assertEqual(le, aid.searchStr)
        self.assertEqual(le.text(), "")
        cm = aid.grid.itemAtPosition(1, 1).widget()
        self.assertIsInstance(cm, PBComboBox)
        self.assertEqual(cm, aid.comboMethod)
        self.assertEqual(cm.count(), 5)
        self.assertEqual(cm.itemText(0), "INSPIRE-HEP")
        self.assertEqual(cm.currentText(), "INSPIRE-HEP")
        self.assertEqual(cm.itemText(1), "ADS-NASA")
        self.assertEqual(cm.itemText(2), "arXiv")
        self.assertEqual(cm.itemText(3), "DOI")
        self.assertEqual(cm.itemText(4), "ISBN")

        self.assertIsInstance(aid.grid.itemAtPosition(2, 0).widget(), QPushButton)
        self.assertEqual(aid.grid.itemAtPosition(2, 0).widget(), aid.acceptButton)
        self.assertEqual(aid.acceptButton.text(), "OK")
        with patch(
            "physbiblio.gui.dialogWindows.AdvancedImportDialog.onOk", autospec=True
        ) as _o:
            QTest.mouseClick(aid.acceptButton, Qt.LeftButton)
            _o.assert_called_once_with(aid)

        self.assertIsInstance(aid.grid.itemAtPosition(2, 1).widget(), QPushButton)
        self.assertEqual(aid.grid.itemAtPosition(2, 1).widget(), aid.cancelButton)
        self.assertEqual(aid.cancelButton.text(), "Cancel")
        self.assertTrue(aid.cancelButton.autoDefault())
        with patch(
            "physbiblio.gui.dialogWindows.AdvancedImportDialog.onCancel", autospec=True
        ) as _c:
            QTest.mouseClick(aid.cancelButton, Qt.LeftButton)
            _c.assert_called_once_with(aid)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestAdvImportSelect(GUITestCase):
    """Test AdvancedImportSelect"""

    def test_init(self):
        """test init"""
        p = QWidget()
        with patch(
            "physbiblio.gui.dialogWindows.AdvancedImportSelect.initUI", autospec=True
        ) as _i:
            ais = AdvancedImportSelect({"abc": "def"}, p)
            _i.assert_called_once_with(ais)
        self.assertIsInstance(ais, ObjListWindow)
        self.assertEqual(ais.bibs, {"abc": "def"})
        self.assertEqual(ais.parent(), p)
        self.assertEqual(ais.checkBoxes, [])

    def test_onCancel(self):
        """test onCancel"""
        ais = AdvancedImportSelect()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            ais.onCancel()
            self.assertFalse(ais.result)
            self.assertEqual(_c.call_count, 1)

    def test_onOk(self):
        """test onOk"""
        ais = AdvancedImportSelect()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            ais.onOk()
            self.assertTrue(ais.result)
            self.assertEqual(_c.call_count, 1)

    def test_keyPressEvent(self):
        """test keyPressEvent"""
        ais = AdvancedImportSelect()
        ais.result = True
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _oc:
            QTest.keyPress(ais, "a")
            _oc.assert_not_called()
            self.assertTrue(ais.result)
            QTest.keyPress(ais, Qt.Key_Enter)
            _oc.assert_not_called()
            self.assertTrue(ais.result)
            QTest.keyPress(ais, Qt.Key_Escape)
            self.assertEqual(_oc.call_count, 1)
            self.assertFalse(ais.result)

    def test_initUI(self):
        """test initUI"""
        p = QWidget()
        ais = AdvancedImportSelect(
            {
                "abc": {
                    "exist": True,
                    "bibpars": {
                        "ID": "abc",
                        "title": "Abc",
                        "authors": "s\ng",
                        "eprint": "1807.15000",
                        "doi": "1/2/3",
                    },
                },
                "def": {
                    "exist": False,
                    "bibpars": {
                        "ID": "def",
                        "title": "De\nf",
                        "author": "SG",
                        "arxiv": "1807.16000",
                        "doi": "3/2/1",
                    },
                },
            },
            p,
        )
        self.assertEqual(ais.windowTitle(), "Advanced import - results")
        self.assertEqual(ais.layout(), ais.currLayout)
        self.assertEqual(ais.currLayout.spacing(), 1)
        self.assertIsInstance(ais.layout().itemAtPosition(0, 0).widget(), PBLabel)
        self.assertEqual(
            ais.layout().itemAtPosition(0, 0).widget().text(),
            "This is the list of elements found."
            + "\nSelect the ones that you want to import:",
        )
        self.assertIsInstance(ais.tableModel, PBImportedTableModel)
        self.assertEqual(
            ais.tableModel.header, ["ID", "title", "author", "eprint", "doi"]
        )
        self.assertEqual(ais.tableModel.bibsOrder, ["abc", "def"])
        self.assertEqual(
            ais.tableModel.dataList,
            [
                {
                    "ID": "abc",
                    "title": "Abc",
                    "authors": "s\ng",
                    "author": "s g",
                    "eprint": "1807.15000",
                    "doi": "1/2/3",
                },
                {
                    "ID": "def",
                    "title": "De f",
                    "author": "SG",
                    "eprint": "1807.16000",
                    "arxiv": "1807.16000",
                    "doi": "3/2/1",
                },
            ],
        )
        self.assertEqual(ais.tableModel.existList, [True, False])

        self.assertIsInstance(ais.layout().itemAtPosition(3, 0).widget(), QCheckBox)
        self.assertEqual(
            ais.layout().itemAtPosition(3, 0).widget().text(),
            "Ask categories at the end?",
        )
        self.assertEqual(ais.layout().itemAtPosition(3, 0).widget(), ais.askCats)
        self.assertTrue(ais.layout().itemAtPosition(3, 0).widget().isChecked())
        self.assertIsInstance(ais.layout().itemAtPosition(4, 0).widget(), QPushButton)
        self.assertEqual(ais.layout().itemAtPosition(4, 0).widget(), ais.acceptButton)
        self.assertEqual(ais.acceptButton.text(), "OK")
        self.assertIsInstance(ais.layout().itemAtPosition(5, 0).widget(), QPushButton)
        self.assertEqual(ais.layout().itemAtPosition(5, 0).widget(), ais.cancelButton)
        self.assertEqual(ais.cancelButton.text(), "Cancel")
        self.assertTrue(ais.cancelButton.autoDefault())
        with patch(
            "physbiblio.gui.dialogWindows.AdvancedImportSelect.onOk", autospec=True
        ) as _o:
            QTest.mouseClick(ais.acceptButton, Qt.LeftButton)
            _o.assert_called_once_with(ais)
        with patch(
            "physbiblio.gui.dialogWindows.AdvancedImportSelect.onCancel", autospec=True
        ) as _o:
            QTest.mouseClick(ais.cancelButton, Qt.LeftButton)
            _o.assert_called_once_with(ais)

        with patch(
            "physbiblio.gui.commonClasses.ObjListWindow.addFilterInput", autospec=True
        ) as _afi, patch(
            "physbiblio.gui.commonClasses.ObjListWindow.setProxyStuff", autospec=True
        ) as _sps, patch(
            "physbiblio.gui.commonClasses.ObjListWindow.finalizeTable", autospec=True
        ) as _ft:
            ais.initUI()
            _afi.assert_called_once_with(ais, "Filter entries", gridPos=(1, 0))
            _sps.assert_called_once_with(ais, 0, Qt.AscendingOrder)
            _ft.assert_called_once_with(ais, gridPos=(2, 0, 1, 2))

    def test_more(self):
        """test some empty functions"""
        ais = AdvancedImportSelect()
        self.assertEqual(
            None, ais.triggeredContextMenuEvent(0, 0, QEvent(QEvent.ContextMenu))
        )
        self.assertEqual(None, ais.handleItemEntered(QModelIndex()))
        self.assertEqual(None, ais.cellClick(QModelIndex()))
        self.assertEqual(None, ais.cellDoubleClick(QModelIndex()))


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestDailyArxivDialog(GUITestCase):
    """Test DailyArxivDialog"""

    def test_init(self):
        """Test __init__"""
        p = QWidget()
        with patch(
            "physbiblio.gui.dialogWindows.DailyArxivDialog.initUI", autospec=True
        ) as _iu:
            dad = DailyArxivDialog(p)
            self.assertIsInstance(dad, PBDialog)
            self.assertEqual(dad.parent(), p)
            _iu.assert_called_once_with(dad)

    def test_onCancel(self):
        """test onCancel"""
        dad = DailyArxivDialog()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            dad.onCancel()
            self.assertFalse(dad.result)
            self.assertEqual(_c.call_count, 1)

    def test_onOk(self):
        """test onOk"""
        dad = DailyArxivDialog()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            dad.onOk()
            self.assertTrue(dad.result)
            self.assertEqual(_c.call_count, 1)

    def test_updateCat(self):
        """test updateCat"""
        dad = DailyArxivDialog()
        self.assertEqual(dad.comboSub.count(), 1)
        self.assertEqual(dad.comboSub.itemText(0), "")
        for c in physBiblioWeb.webSearch["arxiv"].categories.keys():
            dad.updateCat(c)
            self.assertEqual(
                dad.comboSub.count(),
                1 + len(physBiblioWeb.webSearch["arxiv"].categories[c]),
            )
            self.assertEqual(dad.comboSub.itemText(0), "--")
            for ix, sc in enumerate(physBiblioWeb.webSearch["arxiv"].categories[c]):
                self.assertEqual(dad.comboSub.itemText(ix + 1), sc)

    def test_initUI(self):
        """test initUI"""
        dad = DailyArxivDialog()
        self.assertEqual(dad.windowTitle(), "Browse arxiv daily")
        self.assertIsInstance(dad.layout(), QGridLayout)
        self.assertEqual(dad.grid, dad.layout())
        self.assertEqual(dad.grid.spacing(), 1)

        self.assertIsInstance(dad.grid.itemAtPosition(0, 0).widget(), PBLabel)
        self.assertEqual(
            dad.grid.itemAtPosition(0, 0).widget().text(), "Select category: "
        )
        self.assertIsInstance(dad.grid.itemAtPosition(1, 0).widget(), PBLabel)
        self.assertEqual(dad.grid.itemAtPosition(1, 0).widget().text(), "Subcategory: ")

        cc = dad.grid.itemAtPosition(0, 1).widget()
        self.assertIsInstance(cc, PBComboBox)
        self.assertEqual(cc, dad.comboCat)
        self.assertEqual(
            cc.count(), len(physBiblioWeb.webSearch["arxiv"].categories) + 1
        )
        self.assertEqual(cc.itemText(0), "")
        for ix, c in enumerate(
            sorted(physBiblioWeb.webSearch["arxiv"].categories.keys())
        ):
            self.assertEqual(cc.itemText(ix + 1), c)
        with patch(
            "physbiblio.gui.dialogWindows.DailyArxivDialog.updateCat", autospec=True
        ) as _cic:
            dad.comboCat.setCurrentText("hep-ph")
            _cic.assert_called_once_with(dad, "hep-ph")
        cs = dad.grid.itemAtPosition(1, 1).widget()
        self.assertIsInstance(cs, PBComboBox)
        self.assertEqual(cs, dad.comboSub)
        self.assertEqual(cs.count(), 1)
        self.assertEqual(cs.itemText(0), "")

        self.assertIsInstance(dad.grid.itemAtPosition(2, 0).widget(), QPushButton)
        self.assertEqual(dad.grid.itemAtPosition(2, 0).widget(), dad.acceptButton)
        self.assertEqual(dad.acceptButton.text(), "OK")
        with patch(
            "physbiblio.gui.dialogWindows.DailyArxivDialog.onOk", autospec=True
        ) as _o:
            QTest.mouseClick(dad.acceptButton, Qt.LeftButton)
            _o.assert_called_once_with(dad)

        self.assertIsInstance(dad.grid.itemAtPosition(2, 1).widget(), QPushButton)
        self.assertEqual(dad.grid.itemAtPosition(2, 1).widget(), dad.cancelButton)
        self.assertEqual(dad.cancelButton.text(), "Cancel")
        self.assertTrue(dad.cancelButton.autoDefault())
        with patch("physbiblio.gui.dialogWindows.DailyArxivDialog.onCancel") as _c:
            QTest.mouseClick(dad.cancelButton, Qt.LeftButton)
            _c.assert_called_once_with()

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
            dad.initUI()
            self.assertEqual(_fg.call_count, 1)
            self.assertEqual(_ce.call_count, 1)
            self.assertEqual(_mc.call_count, 1)
            self.assertEqual(_tl.call_count, 1)
            self.assertEqual(_mo.call_count, 1)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestDailyArxivSelect(GUITestCase):
    """Test DailyArxivSelect"""

    def test_init(self):
        """test init"""
        p = QWidget()
        das = DailyArxivSelect({}, p)
        self.assertIsInstance(das, AdvancedImportSelect)

    def test_initUI(self):
        """test initUI"""
        p = QWidget()
        with patch(
            "PySide2.QtWidgets.QTableView.sortByColumn", autospec=True
        ) as _s, patch(
            "physbiblio.gui.commonClasses.ObjListWindow.finalizeTable", autospec=True
        ) as _f:
            das = DailyArxivSelect({}, p)
            _s.assert_called_once_with(0, Qt.AscendingOrder)
            _f.assert_called_once_with(das, gridPos=(2, 0, 1, 2))
        das = DailyArxivSelect({}, p)
        self.assertEqual(das.windowTitle(), "ArXiv daily listing - results")
        self.assertEqual(das.layout().spacing(), 1)
        self.assertIsInstance(das.layout().itemAt(0).widget(), PBLabel)
        self.assertEqual(
            das.layout().itemAt(0).widget().text(),
            "This is the list of elements found.\n"
            + "Select the ones that you want to import:",
        )
        self.assertIsInstance(das.tableModel, PBImportedTableModel)
        self.assertEqual(
            das.tableModel.header,
            ["eprint", "type", "title", "author", "primaryclass", "abstract"],
        )
        self.assertEqual(das.tableModel.idName, "eprint")
        self.assertIsInstance(das.layout().itemAt(1).widget(), QLineEdit)
        self.assertEqual(das.layout().itemAt(1).widget(), das.filterInput)
        self.assertIsInstance(das.layout().itemAt(2).widget(), PBTableView)
        self.assertEqual(das.layout().itemAt(2).widget(), das.tableview)
        self.assertIsInstance(das.askCats, QCheckBox)
        self.assertEqual(das.askCats.text(), "Ask categories at the end?")
        self.assertTrue(das.askCats.isChecked())
        self.assertEqual(das.layout().itemAt(3).widget(), das.askCats)
        self.assertIsInstance(das.layout().itemAt(4).widget(), QPushButton)
        self.assertEqual(das.layout().itemAt(4).widget(), das.acceptButton)
        self.assertEqual(das.acceptButton.text(), "OK")
        self.assertIsInstance(das.layout().itemAt(5).widget(), QPushButton)
        self.assertEqual(das.layout().itemAt(5).widget(), das.cancelButton)
        self.assertEqual(das.cancelButton.text(), "Cancel")
        self.assertTrue(das.cancelButton.autoDefault())
        with patch(
            "physbiblio.gui.dialogWindows.AdvancedImportSelect.onOk", autospec=True
        ) as _o:
            QTest.mouseClick(das.acceptButton, Qt.LeftButton)
            _o.assert_called_once_with(das)
        with patch(
            "physbiblio.gui.dialogWindows.AdvancedImportSelect.onCancel", autospec=True
        ) as _o:
            QTest.mouseClick(das.cancelButton, Qt.LeftButton)
            _o.assert_called_once_with(das)
        self.assertIsInstance(das.layout().itemAt(6).widget(), QTextEdit)
        self.assertEqual(das.layout().itemAt(6).widget(), das.abstractArea)
        self.assertEqual(das.abstractArea.toPlainText(), "Abstract")

    def test_cellClick(self):
        """test cellClick"""
        p = QWidget()
        bibs = {
            "1808.00000": {
                "bibpars": {
                    "eprint": "1808.00000",
                    "type": "art",
                    "title": "empty",
                    "author": "me",
                    "primaryclass": "physics",
                    "abstract": "no text",
                },
                "exist": False,
            },
            "1507.08204": {
                "bibpars": {
                    "eprint": "1507.08204",
                    "type": "art",
                    "title": "Light sterile neutrinos",
                    "author": "SG",
                    "primaryclass": "hep-ph",
                    "abstract": "some text",
                },
                "exist": False,
            },
        }
        das = DailyArxivSelect(bibs, p)
        with patch(
            "PySide2.QtCore.QModelIndex.isValid", return_value=False, autospec=True
        ) as _iv:
            self.assertEqual(das.cellClick(QModelIndex()), None)
        self.assertFalse(hasattr(das, "abstractFormulas"))
        # the first row will contain the 1507.08204 entry,
        # as the order is Qt.AscendingOrder on the first column (eprint)
        ix = das.tableview.model().index(1, 0)
        with patch("logging.Logger.debug") as _d:
            das.cellClick(ix)
            _d.assert_called_once_with(
                "self.abstractFormulas not present "
                + "in DailyArxivSelect. Eprint: 1808.00000"
            )
        with patch(
            "PySide2.QtCore.QSortFilterProxyModel.sibling",
            return_value=None,
            autospec=True,
        ) as _s, patch("logging.Logger.debug") as _d:
            self.assertEqual(das.cellClick(ix), None)
            _d.assert_called_once_with("Data not valid", exc_info=True)
            _s.assert_called_once_with(1, 0, ix)
        ix = das.tableview.model().index(0, 0)
        das.abstractFormulas = Fake_abstractFormulas()
        with patch(
            "physbiblio.gui.bibWindows.AbstractFormulas.doText", autospec=True
        ) as _d:
            das.cellClick(ix)
            self.assertIsInstance(das.abstractFormulas.el, AbstractFormulas)
            self.assertEqual(das.abstractFormulas.par, p)
            self.assertEqual(das.abstractFormulas.abstract, "some text")
            self.assertEqual(das.abstractFormulas.ce, das.abstractArea)
            self.assertEqual(das.abstractFormulas.sm, False)
            _d.assert_called_once_with(das.abstractFormulas.el)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestExportForTexDialog(GUITestCase):
    """Test ExportForTexDialog"""

    def test_init(self):
        """test init"""
        with patch(
            "physbiblio.gui.dialogWindows.ExportForTexDialog.initUI", autospec=True
        ) as _iu:
            eft = ExportForTexDialog()
            _iu.assert_called_once_with(eft)
        self.assertIsInstance(eft, PBDialog)
        self.assertEqual(eft.numTexFields, 1)
        self.assertEqual(eft.bibName, "")
        self.assertEqual(eft.texFileNames, [""])
        self.assertEqual(eft.texNames, [])
        self.assertFalse(eft.update)
        self.assertFalse(eft.remove)
        self.assertFalse(eft.reorder)
        self.assertFalse(eft.result)
        self.assertIsInstance(eft.grid, QGridLayout)
        self.assertEqual(eft.layout(), eft.grid)

    def test_readForm(self):
        """test readForm"""
        eft = ExportForTexDialog()
        eft.onAddTex()
        eft.remove = "o"
        eft.bibButton.setText("file.bib")
        eft.updateCheck.setChecked(True)
        eft.removeCheck.setChecked(False)
        eft.reorderCheck.setChecked(True)
        eft.texButtons[0].setText("%s" % ["a.tex", "b.tex", "", "Select file"])
        eft.texButtons[1].setText("c.tex")
        eft.readForm()
        self.assertEqual(eft.update, True)
        self.assertEqual(eft.remove, False)
        self.assertEqual(eft.reorder, True)
        self.assertEqual(eft.bibName, "file.bib")
        self.assertEqual(
            eft.texFileNames, [["a.tex", "b.tex", "", "Select file"], "c.tex"]
        )
        self.assertEqual(eft.texNames, ["a.tex", "b.tex", "c.tex"])
        eft.bibButton.setText("Select file")
        eft.readForm()
        self.assertEqual(eft.bibName, "")

    def test_onAddTex(self):
        """test onAddTex"""
        eft = ExportForTexDialog()
        eft.numTexFields = 3
        with patch(
            "physbiblio.gui.dialogWindows.ExportForTexDialog.cleanLayout", autospec=True
        ) as _cl, patch(
            "physbiblio.gui.dialogWindows.ExportForTexDialog.initUI", autospec=True
        ) as _iu, patch(
            "physbiblio.gui.dialogWindows.ExportForTexDialog.readForm", autospec=True
        ) as _rf:
            eft.onAddTex()
            self.assertEqual(eft.numTexFields, 4)
            self.assertEqual(eft.texFileNames, ["", "", "", ""])
            _cl.assert_called_once_with(eft)
            _iu.assert_called_once_with(eft)
            _rf.assert_called_once_with(eft)

    def test_onCancel(self):
        """test onCancel"""
        eow = ExportForTexDialog()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            eow.onCancel()
            self.assertFalse(eow.result)
            self.assertEqual(_c.call_count, 1)

    def test_onOk(self):
        """test onOk"""
        eow = ExportForTexDialog()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c, patch(
            "physbiblio.gui.dialogWindows.ExportForTexDialog.readForm", autospec=True
        ) as _rf:
            eow.onOk()
            self.assertTrue(eow.result)
            _rf.assert_called_once_with(eow)
            self.assertEqual(_c.call_count, 1)

    def test_onAskBib(self):
        """test onAskBib"""
        eft = ExportForTexDialog()
        with patch(
            "physbiblio.gui.dialogWindows.askSaveFileName",
            return_value="",
            autospec=True,
        ) as _af:
            eft.onAskBib()
        self.assertEqual(eft.bibButton.text(), "Select file")
        with patch(
            "physbiblio.gui.dialogWindows.askSaveFileName",
            return_value="f.bib",
            autospec=True,
        ) as _af:
            eft.onAskBib()
        self.assertEqual(eft.bibButton.text(), "f.bib")

    def test_onAskTex(self):
        """test onAskTex"""
        eft = ExportForTexDialog()
        eft.onAddTex()
        with patch(
            "physbiblio.gui.dialogWindows.askFileNames", return_value="", autospec=True
        ) as _af:
            eft.onAskTex(0)
        self.assertEqual(eft.texButtons[0].text(), "Select file")
        with patch(
            "physbiblio.gui.dialogWindows.askFileNames", return_value=[], autospec=True
        ) as _af:
            eft.onAskTex(0)
        self.assertEqual(eft.texButtons[0].text(), "Select file")
        with patch(
            "physbiblio.gui.dialogWindows.askFileNames",
            return_value="a.tex",
            autospec=True,
        ) as _af:
            eft.onAskTex(0)
        self.assertEqual(eft.texButtons[0].text(), "a.tex")
        with patch(
            "physbiblio.gui.dialogWindows.askFileNames",
            return_value=["b.tex"],
            autospec=True,
        ) as _af:
            eft.onAskTex(1)
        self.assertEqual(eft.texButtons[1].text(), "['b.tex']")

    def test_initUI(self):
        """test initUI"""
        eft = ExportForTexDialog()
        self.assertEqual(eft.numTexFields, 1)
        self.assertEqual(eft.bibName, "")
        self.assertEqual(eft.texFileNames, [""])
        self.assertEqual(eft.windowTitle(), "Export for tex file")
        self.assertIsInstance(eft.grid.itemAtPosition(0, 0).widget(), PBLabelRight)
        self.assertEqual(
            eft.grid.itemAtPosition(0, 0).widget().text(), "Bib file name:"
        )
        self.assertIsInstance(eft.grid.itemAtPosition(0, 2).widget(), QPushButton)
        self.assertEqual(eft.grid.itemAtPosition(0, 2).widget(), eft.bibButton)
        self.assertEqual(eft.bibButton.text(), "Select file")
        with patch(
            "physbiblio.gui.dialogWindows.ExportForTexDialog.onAskBib", autospec=True
        ) as _f:
            QTest.mouseClick(eft.bibButton, Qt.LeftButton)
            _f.assert_called_once_with(eft)

        self.assertIsInstance(eft.grid.itemAtPosition(1, 0).widget(), PBLabelRight)
        self.assertEqual(
            eft.grid.itemAtPosition(1, 0).widget().text(), "Tex file name(s):"
        )
        self.assertIsInstance(eft.texButtons, list)
        self.assertEqual(len(eft.texButtons), eft.numTexFields)
        self.assertIsInstance(eft.grid.itemAtPosition(1, 2).widget(), QPushButton)
        self.assertEqual(eft.grid.itemAtPosition(1, 2).widget(), eft.texButtons[0])
        self.assertEqual(eft.texButtons[0].text(), "Select file")
        with patch(
            "physbiblio.gui.dialogWindows.ExportForTexDialog.onAskTex", autospec=True
        ) as _f:
            QTest.mouseClick(eft.texButtons[0], Qt.LeftButton)
            _f.assert_called_once_with(eft, 0)

        self.assertIsInstance(eft.grid.itemAtPosition(2, 2).widget(), QPushButton)
        self.assertEqual(eft.grid.itemAtPosition(2, 2).widget(), eft.addTexButton)
        self.assertEqual(eft.addTexButton.text(), "Add more tex files")
        with patch(
            "physbiblio.gui.dialogWindows.ExportForTexDialog.onAddTex", autospec=True
        ) as _f:
            QTest.mouseClick(eft.addTexButton, Qt.LeftButton)
            _f.assert_called_once_with(eft)

        self.assertIsInstance(eft.grid.itemAtPosition(3, 0).widget(), QCheckBox)
        self.assertEqual(eft.grid.itemAtPosition(3, 0).widget(), eft.removeCheck)
        self.assertEqual(eft.removeCheck.text(), "Remove unused bibtexs?")
        self.assertFalse(eft.removeCheck.isChecked())
        self.assertIsInstance(eft.grid.itemAtPosition(3, 2).widget(), QCheckBox)
        self.assertEqual(eft.grid.itemAtPosition(3, 2).widget(), eft.updateCheck)
        self.assertEqual(eft.updateCheck.text(), "Update existing bibtexs?")
        self.assertFalse(eft.updateCheck.isChecked())
        self.assertIsInstance(eft.grid.itemAtPosition(4, 0).widget(), QCheckBox)
        self.assertEqual(eft.grid.itemAtPosition(4, 0).widget(), eft.reorderCheck)
        self.assertEqual(
            eft.reorderCheck.text(),
            "Reorder existing bibtexs? (includes removing unused ones)",
        )
        self.assertFalse(eft.reorderCheck.isChecked())

        self.assertIsInstance(eft.grid.itemAtPosition(5, 1).widget(), QPushButton)
        self.assertEqual(eft.grid.itemAtPosition(5, 1).widget(), eft.acceptButton)
        self.assertEqual(eft.acceptButton.text(), "OK")
        with patch(
            "physbiblio.gui.dialogWindows.ExportForTexDialog.onOk", autospec=True
        ) as _f:
            QTest.mouseClick(eft.acceptButton, Qt.LeftButton)
            _f.assert_called_once_with(eft)

        self.assertIsInstance(eft.grid.itemAtPosition(5, 2).widget(), QPushButton)
        self.assertEqual(eft.grid.itemAtPosition(5, 2).widget(), eft.cancelButton)
        self.assertEqual(eft.cancelButton.text(), "Cancel")
        with patch(
            "physbiblio.gui.dialogWindows.ExportForTexDialog.onCancel", autospec=True
        ) as _f:
            QTest.mouseClick(eft.cancelButton, Qt.LeftButton)
            _f.assert_called_once_with(eft)

        with patch(
            "physbiblio.gui.dialogWindows.ExportForTexDialog.initUI", autospec=True
        ) as _iu:
            eft = ExportForTexDialog()
        eft.numTexFields = 2
        eft.bibName = "file.bib"
        eft.texFileNames = ["a.tex", ""]
        eft.update = True
        eft.remove = True
        eft.reorder = True
        with patch(
            "physbiblio.gui.dialogWindows.ExportForTexDialog.centerWindow",
            autospec=True,
        ) as _cw, patch(
            "physbiblio.gui.dialogWindows.ExportForTexDialog.setGeometry", autospec=True
        ) as _sg:
            eft.initUI()
            _cw.assert_called_once_with(eft)
            _sg.assert_called_once_with(100, 100, 400, 25 * (5 + 2))
        self.assertEqual(eft.bibButton.text(), "file.bib")

        self.assertIsInstance(eft.grid.itemAtPosition(1, 0).widget(), PBLabelRight)
        self.assertEqual(
            eft.grid.itemAtPosition(1, 0).widget().text(), "Tex file name(s):"
        )
        self.assertIsInstance(eft.texButtons, list)
        self.assertEqual(len(eft.texButtons), eft.numTexFields)
        self.assertIsInstance(eft.grid.itemAtPosition(1, 2).widget(), QPushButton)
        self.assertEqual(eft.grid.itemAtPosition(1, 2).widget(), eft.texButtons[0])
        self.assertEqual(eft.texButtons[0].text(), "a.tex")
        with patch(
            "physbiblio.gui.dialogWindows.ExportForTexDialog.onAskTex", autospec=True
        ) as _f:
            QTest.mouseClick(eft.texButtons[0], Qt.LeftButton)
            _f.assert_called_once_with(eft, 0)
        self.assertIsInstance(eft.grid.itemAtPosition(2, 0).widget(), PBLabelRight)
        self.assertEqual(
            eft.grid.itemAtPosition(2, 0).widget().text(), "Tex file name(s):"
        )
        self.assertIsInstance(eft.grid.itemAtPosition(2, 2).widget(), QPushButton)
        self.assertEqual(eft.grid.itemAtPosition(2, 2).widget(), eft.texButtons[1])
        self.assertEqual(eft.texButtons[1].text(), "Select file")
        with patch(
            "physbiblio.gui.dialogWindows.ExportForTexDialog.onAskTex", autospec=True
        ) as _f:
            QTest.mouseClick(eft.texButtons[1], Qt.LeftButton)
            _f.assert_called_once_with(eft, 1)
        self.assertEqual(eft.grid.itemAtPosition(3, 2).widget(), eft.addTexButton)
        self.assertEqual(eft.grid.itemAtPosition(4, 0).widget(), eft.removeCheck)
        self.assertTrue(eft.removeCheck.isChecked())
        self.assertEqual(eft.grid.itemAtPosition(4, 2).widget(), eft.updateCheck)
        self.assertTrue(eft.updateCheck.isChecked())
        self.assertEqual(eft.grid.itemAtPosition(5, 0).widget(), eft.reorderCheck)
        self.assertTrue(eft.reorderCheck.isChecked())
        self.assertEqual(eft.grid.itemAtPosition(6, 1).widget(), eft.acceptButton)
        self.assertEqual(eft.grid.itemAtPosition(6, 2).widget(), eft.cancelButton)


if __name__ == "__main__":
    unittest.main()
