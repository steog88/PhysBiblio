#!/usr/bin/env python
"""Test file for the physbiblio.gui.errorManager module.

This file is part of the physbiblio package.
"""
import logging
import os
import traceback
import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QMessageBox

try:
    from physbiblio.errors import PBErrorManagerClass
    from physbiblio.gui.errorManager import *
    from physbiblio.gui.setuptests import *
    from physbiblio.setuptests import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestGUIErrorManager(GUITestCase):
    """Test the functions in ErrorManager"""

    def test_ErrorStream(self):
        """Test functions in ErrorStream"""
        es = ErrorStream()
        self.assertIsInstance(es, StringIO)
        self.assertEqual(es.lastMBox, None)
        self.assertEqual(es.priority, 1)
        es.setPriority(2)
        self.assertEqual(es.priority, 2)
        mb = MagicMock()
        with patch("physbiblio.gui.errorManager.QMessageBox", return_value=mb) as _mb:
            es.write("sometext")
            _mb.assert_called_once_with(_mb.Information, "Information", "")
        mb.setText.assert_called_once_with("sometext")
        mb.setWindowTitle.assert_called_once_with("Error")
        mb.setIcon.assert_called_once_with(_mb.Critical)
        mb.exec.assert_called_once_with()
        self.assertEqual(es.priority, 1)
        es.setPriority(0)
        mb = MagicMock()
        with patch("physbiblio.gui.errorManager.QMessageBox", return_value=mb) as _mb:
            es.write("some\ntext")
            _mb.assert_called_once_with(_mb.Information, "Information", "")
        mb.setText.assert_called_once_with("some<br>text")
        mb.setWindowTitle.assert_called_once_with("Information")
        mb.setIcon.assert_called_once_with(_mb.Information)
        mb.exec.assert_called_once_with()
        mb = MagicMock()
        with patch("physbiblio.gui.errorManager.QMessageBox", return_value=mb) as _mb:
            es.write("some new text")
            _mb.assert_called_once_with(_mb.Information, "Information", "")
        mb.setText.assert_called_once_with("some new text")
        mb.setWindowTitle.assert_called_once_with("Warning")
        mb.setIcon.assert_called_once_with(_mb.Warning)
        mb.exec.assert_called_once_with()
        with patch("physbiblio.gui.errorManager.QMessageBox", return_value=mb) as _mb:
            self.assertEqual(es.write(" "), None)
            _mb.assert_not_called()

    def test_PBErrorManagerClassGui(self):
        """Test functions in ErrorStream"""
        el = PBErrorManagerClassGui()
        self.assertIsInstance(el, PBErrorManagerClass)
        self.assertIsInstance(el.guiStream, ErrorStream)
        l = el.loggerPriority(25)
        self.assertEqual(el.guiStream.priority, 25)
        self.assertIsInstance(l, logging.Logger)

    def test_objects(self):
        """test that the module contains the appropriate objects"""
        import physbiblio.gui.errorManager as pgem

        self.assertIsInstance(pgem.pBGUIErrorManager, pgem.PBErrorManagerClassGui)
        self.assertIsInstance(pgem.pBGUIErrorManager, PBErrorManagerClass)
        self.assertIsInstance(pgem.pBGUILogger, logging.Logger)
        self.assertEqual(pgem.pBGUILogger, pgem.pBGUIErrorManager.logger)


if __name__ == "__main__":
    unittest.main()
