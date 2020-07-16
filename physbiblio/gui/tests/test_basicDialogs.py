#!/usr/bin/env python
"""Test file for the physbiblio.gui.basicDialogs module.

This file is part of the physbiblio package.
"""
import os
import sys
import traceback

from PySide2.QtCore import Qt
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QInputDialog, QWidget

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import MagicMock, call, patch
else:
    import unittest
    from unittest.mock import MagicMock, call, patch

try:
    from physbiblio.gui.basicDialogs import *
    from physbiblio.gui.setuptests import *
    from physbiblio.setuptests import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestDialogWindows(GUITestCase):
    """Test the functions in DialogWindows"""

    def test_askYesNo(self):
        """Test askYesNo"""
        mb = MagicMock()
        mb.addButton.side_effect = ["yes", "no", "yes", "no"]
        mb.clickedButton.side_effect = ["yes", "no"]
        with patch(
            "physbiblio.gui.basicDialogs.QMessageBox", return_value=mb, autospec=True
        ) as _mb:
            self.assertTrue(askYesNo("mymessage"))
            _mb.assert_called_once_with(_mb.Question, "Question", "mymessage")
            mb.addButton.assert_has_calls([call(_mb.Yes), call(_mb.No)])
            mb.setDefaultButton.assert_called_once_with("no")
            mb.exec_.assert_called_once_with()
            mb.clickedButton.assert_called_once_with()
            _mb.reset_mock()
            self.assertFalse(askYesNo("mymessage", title="mytitle"))
            _mb.assert_called_once_with(_mb.Question, "mytitle", "mymessage")

    def test_infoMessage(self):
        """Test infoMessage"""
        mb = MagicMock()
        with patch(
            "physbiblio.gui.basicDialogs.QMessageBox", return_value=mb, autospec=True
        ) as _mb:
            infoMessage("mymessage")
            _mb.assert_called_once_with(_mb.Information, "Information", "mymessage")
            _mb.reset_mock()
            infoMessage("mymessage", title="mytitle")
            _mb.assert_called_once_with(_mb.Information, "mytitle", "mymessage")
            mb.exec_.assert_called_once_with()

    def test_LongInfoMessage(self):
        """Test LongInfoMessage"""
        with patch(
            "physbiblio.gui.basicDialogs.LongInfoMessage.exec_", autospec=True
        ) as _e:
            win = LongInfoMessage("mymessage")
            _e.assert_called_once_with()
        self.assertIsInstance(win, QDialog)
        self.assertEqual(win.windowTitle(), "Information")
        self.assertIsInstance(win.layout(), QGridLayout)
        self.assertEqual(win.layout(), win.gridlayout)
        self.assertIsInstance(win.layout().itemAtPosition(0, 0).widget(), QTextEdit)
        self.assertEqual(win.layout().itemAtPosition(0, 0).widget(), win.textarea)
        self.assertEqual(win.textarea.isReadOnly(), True)
        self.assertEqual(win.textarea.toPlainText(), "mymessage")
        self.assertIsInstance(win.layout().itemAtPosition(1, 1).widget(), QPushButton)
        self.assertEqual(win.layout().itemAtPosition(1, 1).widget(), win.okbutton)
        self.assertEqual(win.okbutton.text(), "OK")
        with patch("PySide2.QtWidgets.QDialog.close") as _c:
            QTest.mouseClick(win.okbutton, Qt.LeftButton)
            _c.assert_called_once_with(win)
        mb = MagicMock()
        with patch(
            "physbiblio.gui.basicDialogs.LongInfoMessage.exec_", autospec=True
        ) as _e:
            win = LongInfoMessage("mymessage", "mytitle")
        self.assertEqual(win.windowTitle(), "mytitle")

    def test_askGenericText(self):
        """Test askGenericText"""
        p = MagicMock()
        q = QWidget()
        qid = MagicMock()
        qid.exec_.side_effect = [True, False, True]
        qid.textValue.side_effect = ["abc", "def", "ghi"]
        with patch(
            "physbiblio.gui.basicDialogs.QInputDialog", return_value=qid, autospec=True
        ) as _qid:
            self.assertEqual(askGenericText("mymessage", "mytitle"), ("abc", True))
            qid.setInputMode.assert_called_once_with(_qid.TextInput)
            qid.setLabelText.assert_called_once_with("mymessage")
            qid.setTextValue.assert_called_once_with("")
            qid.setWindowTitle.assert_called_once_with("mytitle")
            qid.exec_.assert_called_once_with()
            qid.textValue.assert_called_once_with()
            self.assertEqual(
                askGenericText("mymessage", "mytitle", parent=p), ("def", False)
            )
        with patch(
            "physbiblio.gui.basicDialogs.QInputDialog", return_value=qid, autospec=True
        ) as _qid:
            self.assertEqual(
                askGenericText("mymessage", "mytitle", q, "ABC"), ("ghi", True)
            )
            qid.setTextValue.assert_any_call("ABC")

    def test_askFileName(self):
        """Test askFileName"""
        fd = MagicMock()
        fd.exec_.side_effect = [False, True, True]
        fd.selectedFiles.side_effect = [["abc", "def"], []]
        with patch(
            "physbiblio.gui.basicDialogs.QFileDialog", return_value=fd, autospec=True
        ) as _fd:
            self.assertEqual(
                askFileName(
                    parent=None, title="mytitle", dir="/tmp", filter="test: *.txt"
                ),
                "",
            )
            _fd.assert_called_once_with(None, "mytitle", "/tmp", "test: *.txt")
            fd.setFileMode.assert_called_once_with(_fd.ExistingFile)
            fd.exec_.assert_called_once_with()
            fd.selectedFiles.assert_not_called()
            _fd.reset_mock()
            self.assertEqual(askFileName(), "abc")
            _fd.assert_called_once_with(None, "Filename to use:", "", "")
            fd.selectedFiles.assert_called_once_with()
            self.assertEqual(askFileName(), "")

    def test_askFileNames(self):
        """Test askFileNames"""
        fd = MagicMock()
        fd.exec_.side_effect = [False, True]
        fd.selectedFiles.return_value = ["abc", "def"]
        with patch(
            "physbiblio.gui.basicDialogs.QFileDialog", return_value=fd, autospec=True
        ) as _fd:
            self.assertEqual(
                askFileNames(
                    parent=None, title="mytitle", dir="/tmp", filter="test: *.txt"
                ),
                [],
            )
            _fd.assert_called_once_with(None, "mytitle", "/tmp", "test: *.txt")
            fd.setFileMode.assert_called_once_with(_fd.ExistingFiles)
            fd.setOption.assert_called_once_with(_fd.DontConfirmOverwrite, True)
            fd.exec_.assert_called_once_with()
            fd.selectedFiles.assert_not_called()
            _fd.reset_mock()
            self.assertEqual(askFileNames(), ["abc", "def"])
            _fd.assert_called_once_with(None, "Filename to use:", "", "")
            fd.selectedFiles.assert_called_once_with()

    def test_askSaveFileName(self):
        """Test askSaveFileName"""
        fd = MagicMock()
        fd.exec_.side_effect = [False, True, True]
        fd.selectedFiles.side_effect = [["abc", "def"], []]
        with patch(
            "physbiblio.gui.basicDialogs.QFileDialog", return_value=fd, autospec=True
        ) as _fd:
            self.assertEqual(
                askSaveFileName(
                    parent=None, title="mytitle", dir="/tmp", filter="test: *.txt"
                ),
                "",
            )
            _fd.assert_called_once_with(None, "mytitle", "/tmp", "test: *.txt")
            fd.setFileMode.assert_called_once_with(_fd.AnyFile)
            fd.setOption.assert_called_once_with(_fd.DontConfirmOverwrite, True)
            fd.exec_.assert_called_once_with()
            fd.selectedFiles.assert_not_called()
            _fd.reset_mock()
            self.assertEqual(askSaveFileName(), "abc")
            _fd.assert_called_once_with(None, "Filename to use:", "", "")
            fd.selectedFiles.assert_called_once_with()
            self.assertEqual(askSaveFileName(), "")

    def test_askDirName(self):
        """Test askDirName"""
        fd = MagicMock()
        fd.exec_.side_effect = [False, True, True]
        fd.selectedFiles.side_effect = [["abc", "def"], []]
        with patch(
            "physbiblio.gui.basicDialogs.QFileDialog", return_value=fd, autospec=True
        ) as _fd:
            self.assertEqual(askDirName(parent=None, title="mytitle", dir="/tmp"), "")
            _fd.assert_called_once_with(None, "mytitle", "/tmp")
            fd.setFileMode.assert_called_once_with(_fd.Directory)
            fd.setOption.assert_called_once_with(_fd.ShowDirsOnly, True)
            fd.exec_.assert_called_once_with()
            fd.selectedFiles.assert_not_called()
            _fd.reset_mock()
            self.assertEqual(askDirName(), "abc")
            _fd.assert_called_once_with(None, "Directory to use:", "")
            fd.selectedFiles.assert_called_once_with()
            self.assertEqual(askDirName(), "")


if __name__ == "__main__":
    unittest.main()
