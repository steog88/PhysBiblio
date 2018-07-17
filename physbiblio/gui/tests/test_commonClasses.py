#!/usr/bin/env python
"""
Test file for the physbiblio.gui.commonClasses module.

This file is part of the physbiblio package.
"""
import sys, traceback
import os
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QInputDialog

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch
else:
	import unittest
	from unittest.mock import patch

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
class TestObjListWindow(GUITestCase):
	"""
	Test the MyLabelRight and MyLabelCenter classes
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
		pass
	def test_setProxyStuff(self):
		pass
	def test_finalizeTable(self):
		pass

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

if __name__=='__main__':
	unittest.main()
