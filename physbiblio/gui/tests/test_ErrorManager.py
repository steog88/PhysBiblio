#!/usr/bin/env python
"""
Test file for the physbiblio.gui.DialogWindows module.

This file is part of the physbiblio package.
"""
import sys, traceback
import os
import logging
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QMessageBox

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch
else:
	import unittest
	from unittest.mock import patch

try:
	from physbiblio.setuptests import *
	from physbiblio.gui.setuptests import *
	from physbiblio.errors import pBErrorManagerClass
	from physbiblio.gui.ErrorManager import *
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestGUIErrorManager(GUITestCase):
	"""
	Test the functions in ErrorManager
	"""
	def test_ErrorStream(self):
		"""Test functions in ErrorStream"""
		es = ErrorStream()
		self.assertIsInstance(es, StringIO)
		self.assertEqual(es.lastMBox, None)
		self.assertEqual(es.priority, 1)
		es.setPriority(2)
		self.assertEqual(es.priority, 2)
		mb = es.write("sometext", testing = True)
		self.assertEqual(es.priority, 1)
		self.assertIsInstance(mb, QMessageBox)
		self.assertEqual(mb.text(), "sometext")
		self.assertEqual(mb.windowTitle(), "Error")
		self.assertEqual(mb.icon(), QMessageBox.Critical)
		es.setPriority(0)
		mb = es.write("some\ntext", testing = True)
		self.assertIsInstance(mb, QMessageBox)
		self.assertEqual(mb.text(), "some<br>text")
		self.assertEqual(mb.windowTitle(), "Information")
		self.assertEqual(mb.icon(), QMessageBox.Information)
		mb = es.write("some new text", testing = True)
		self.assertIsInstance(mb, QMessageBox)
		self.assertEqual(mb.text(), "some new text")
		self.assertEqual(mb.windowTitle(), "Warning")
		self.assertEqual(mb.icon(), QMessageBox.Warning)
		self.assertEqual(es.write(" ", testing = True), None)

	def test_pBErrorManagerClassGui(self):
		"""Test functions in ErrorStream"""
		el = pBErrorManagerClassGui()
		self.assertIsInstance(el, pBErrorManagerClass)
		self.assertIsInstance(el.guiStream, ErrorStream)
		l = el.loggerPriority(25)
		self.assertEqual(el.guiStream.priority, 25)
		self.assertIsInstance(l, logging.Logger)

if __name__=='__main__':
	unittest.main()
