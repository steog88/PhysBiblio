#!/usr/bin/env python
"""
Test file for the physbiblio.gui.profilesManager module.

This file is part of the physbiblio package.
"""
import sys, traceback
import os
from PySide2.QtCore import Qt, QPoint
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QWidget

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch, call
else:
	import unittest
	from unittest.mock import patch, call

try:
	from physbiblio.setuptests import *
	from physbiblio.gui.setuptests import *
	from physbiblio.gui.profilesManager import *
	from physbiblio.gui.mainWindow import MainWindow
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
	raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestEditProf(GUITestCase):
	"""
	Test the editProf function
	"""
	def test_editProf(self):
		"""Test the editProf function"""
		pass

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestSelectProfiles(GUITestCase):
	"""Test the selectProfiles class"""
	@classmethod
	def setUpClass(self):
		"""set temporary pbConfig settings"""
		self.oldProfileOrder = pbConfig.profileOrder
		self.oldProfiles = pbConfig.profiles
		self.oldCurrentProfileName = pbConfig.currentProfileName
		self.oldCurrentProfile = pbConfig.currentProfile
		pbConfig.profileOrder = ["test1", "test2"]
		pbConfig.profiles = {
			"test1": {'db': u'test1.db', 'd': u'test1', 'n': u'test1'},
			"test2": {'db': u'test2.db', 'd': u'test2', 'n': u'test2'},
		}
		pbConfig.currentProfileName = "test1"
		pbConfig.currentProfile = pbConfig.profiles["test1"]

	@classmethod
	def tearDownClass(self):
		"""restore previous pbConfig settings"""
		pbConfig.profileOrder = self.oldProfileOrder
		pbConfig.profiles = self.oldProfiles
		pbConfig.currentProfileName = self.oldCurrentProfileName
		pbConfig.currentProfile = self.oldCurrentProfile

	def test_init(self):
		"""test init"""
		p = MainWindow(True)
		with patch("physbiblio.gui.profilesManager.selectProfiles.initUI") as _iu:
			self.assertRaises(Exception,
				lambda: selectProfiles(None))
			sp = selectProfiles(p)
			self.assertIsInstance(sp, QDialog)
			self.assertEqual(sp.parent(), p)
			self.assertEqual(sp.message, None)
			sp = selectProfiles(p, "message")
			self.assertEqual(sp.message, "message")
			_iu.assert_has_calls([call(), call()])

	def test_onCancel(self):
		"""test onCancel"""
		with patch("physbiblio.gui.profilesManager.selectProfiles.initUI") as _iu,\
				patch("physbiblio.gui.profilesManager.QDialog.close") as _c:
			sp = selectProfiles(MainWindow(True))
			sp.onCancel()
			_c.assert_called_once_with()
			self.assertFalse(sp.result)

	def test_onLoad(self):
		"""test onLoad"""
		p = MainWindow(True)
		sp = selectProfiles(p)
		with patch("physbiblio.gui.profilesManager.QDialog.close") as _c,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadConfig") as _rc,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent") as _rm,\
				patch("physbiblio.config.ConfigVars.reInit") as _ri,\
				patch("physbiblio.database.physbiblioDB.reOpenDB") as _ro:
			sp.onLoad()
			_ri.assert_not_called()
			_ro.assert_not_called()
			_rc.assert_not_called()
			_rm.assert_called_once_with()
			_c.assert_called_once_with()
		sp = selectProfiles(p)
		sp.combo.setCurrentIndex(1)
		pbConfig.currentDatabase = "test2.db"
		with patch("physbiblio.gui.profilesManager.QDialog.close") as _c,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadConfig") as _rc,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent") as _rm,\
				patch("physbiblio.config.ConfigVars.reInit") as _ri,\
				patch("physbiblio.database.physbiblioDB.reOpenDB") as _ro:
			sp.onLoad()
			_ri.assert_called_once_with('test2',
				{'db': 'test2.db', 'd': 'test2', 'n': 'test2'})
			_ro.assert_called_once_with("test2.db")
			_rc.assert_called_once_with()
			_rm.assert_called_once_with()
			_c.assert_called_once_with()

	def test_initUI(self):
		"""Test initUI"""
		p = MainWindow(True)
		sp = selectProfiles(p, "message")
		self.assertEqual(sp.windowTitle(), 'Select profile')
		self.assertIsInstance(sp.layout(), QGridLayout)
		self.assertEqual(sp.layout().spacing(), 10)
		self.assertIsInstance(sp.layout().itemAtPosition(0, 0).widget(),
			QLabel)
		self.assertEqual(sp.layout().itemAtPosition(0, 0).widget().text(),
			"message")
		self.assertIsInstance(sp.layout().itemAtPosition(1, 0).widget(),
			QLabel)
		self.assertEqual(sp.layout().itemAtPosition(1, 0).widget().text(),
			"Available profiles: ")
		mcb = sp.layout().itemAtPosition(1, 1).widget()
		self.assertIsInstance(mcb, MyComboBox)
		self.assertEqual(mcb.count(), 2)
		self.assertEqual(mcb.itemText(0), "test1 -- test1")
		self.assertEqual(mcb.itemText(1), "test2 -- test2")
		self.assertEqual(mcb.currentText(), "test1 -- test1")
		self.assertIsInstance(sp.layout().itemAtPosition(2, 0).widget(),
			QPushButton)
		self.assertEqual(sp.layout().itemAtPosition(2, 0).widget(),
			sp.loadButton)
		self.assertIsInstance(sp.layout().itemAtPosition(2, 1).widget(),
			QPushButton)
		self.assertEqual(sp.layout().itemAtPosition(2, 1).widget(),
			sp.cancelButton)
		self.assertTrue(sp.cancelButton.autoDefault())

		sp = selectProfiles(p)
		self.assertIsInstance(sp.layout().itemAtPosition(0, 0).widget(),
			QLabel)
		self.assertEqual(sp.layout().itemAtPosition(0, 0).widget().text(),
			"Available profiles: ")
		self.assertIsInstance(sp.layout().itemAtPosition(0, 1).widget(),
			MyComboBox)
		self.assertEqual(sp.layout().itemAtPosition(1, 0).widget(),
			sp.loadButton)
		self.assertEqual(sp.layout().itemAtPosition(1, 1).widget(),
			sp.cancelButton)

		with patch("physbiblio.gui.profilesManager.selectProfiles.onCancel") as _f:
			QTest.mouseClick(sp.cancelButton, Qt.LeftButton)
			_f.assert_called_once_with()
		with patch("physbiblio.gui.profilesManager.selectProfiles.onLoad") as _f:
			QTest.mouseClick(sp.loadButton, Qt.LeftButton)
			_f.assert_called_once_with()

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestmyOrderPushButton(GUITestCase):
	"""
	Test the myOrderPushButton class
	"""
	def test_init(self):
		"""test init"""
		self.max_diff = None
		qi = QIcon(":/images/arrow-down.png")
		qp = QPushButton()
		p = editProfile(QWidget())
		opb = myOrderPushButton(p, 1, qi, "txt")
		self.assertIsInstance(opb, QPushButton)
		self.assertEqual(opb.text(), "txt")
		self.assertEqual(opb.parent(), p)
		self.assertEqual(opb.parentObj, p)
		with patch("physbiblio.gui.profilesManager.editProfile.switchLines") as _s:
			opb.onClick()
			_s.assert_called_once_with(1)
			_s.reset_mock()
			QTest.mouseClick(opb, Qt.LeftButton)
			_s.assert_called_once_with(1)
		with patch("physbiblio.gui.profilesManager.QPushButton.__init__",
				return_value = qp) as _i:
			opb = myOrderPushButton(p, 1, qi, "txt", True)
			_i.assert_called_once_with(opb, qi, "txt")

@unittest.skipIf(skipGuiTests, "GUI tests")
class TestEditProfile(GUITestCase):
	"""
	"""
	def test_init(self):
		"""test init"""
		p = QWidget()
		with patch("physbiblio.gui.profilesManager.editProfile.createForm") as _s:
			ep = editProfile(p)
			self.assertIsInstance(ep, editObjectWindow)
			self.assertEqual(ep.parent(), p)
			_s.assert_called_once_with()

	def test_onOk(self):
		pass

	def test_addButtons(self):
		pass

	def test_createForm(self):
		pass

	def test_switchLines(self):
		pass

	def test_cleanLayout(self):
		pass

if __name__=='__main__':
	unittest.main()
