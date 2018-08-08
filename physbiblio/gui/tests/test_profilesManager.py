#!/usr/bin/env python
"""
Test file for the physbiblio.gui.profilesManager module.

This file is part of the physbiblio package.
"""
import sys, traceback
import os
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest
from PySide2.QtGui import QIcon
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
	print("Could not find physbiblio and its modules!")
	raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestEditProf(GUITestCase):
	"""
	Test the editProf function
	"""
	@classmethod
	def setUpClass(self):
		"""set temporary pbConfig settings"""
		self.oldProfileOrder = pbConfig.profileOrder
		self.oldProfiles = pbConfig.profiles
		self.oldCurrentProfileName = pbConfig.currentProfileName
		self.oldCurrentProfile = pbConfig.currentProfile
		pbConfig.profileOrder = ["test1", "test2", "test3"]
		pbConfig.profiles = {
			"test1": {'db': u'test1.db', 'd': u'test1', 'n': u'test1'},
			"test2": {'db': u'test2.db', 'd': u'test2', 'n': u'test2'},
			"test3": {'db': u'test3.db', 'd': u'test3', 'n': u'test3'},
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

	def test_editProf(self):
		"""Test the editProf function"""
		# first tests
		p = QWidget()
		mw = MainWindow(True)
		ep = editProfile()
		ep.onCancel()
		with patch("physbiblio.gui.mainWindow.MainWindow.StatusBarMessage") \
				as _m:
			editProf(p, mw, ep)
			_m.assert_called_once_with("No modifications")
		with patch("physbiblio.gui.mainWindow.MainWindow.StatusBarMessage") \
				as _m:
			editProf(p, p, ep)
			_m.assert_not_called()

		# test switch lines and some description
		ep = editProfile()
		ep.switchLines(0)
		ep.elements[2]["d"].setText("descrip")
		ep.onOk()
		with patch("physbiblio.config.ConfigVars.loadProfiles") as _lp,\
				patch("physbiblio.config.globalDB.setDefaultProfile") as _sdp,\
				patch("physbiblio.config.globalDB.updateProfileField") as _upf,\
				patch("physbiblio.config.globalDB.deleteProfile") as _dp,\
				patch("physbiblio.config.globalDB.createProfile") as _cp,\
				patch("physbiblio.config.globalDB.setProfileOrder") as _spo,\
				patch("physbiblio.gui.mainWindow.MainWindow.StatusBarMessage") \
					as _m,\
				patch("shutil.copy2") as _copy:
			editProf(p, mw, ep)
			_lp.assert_called_once_with()
			_sdp.assert_not_called()
			_upf.assert_has_calls([
				call(u'test2', 'description', u'test2'),
				call(u'test1', 'description', u'test1'),
				call(u'test3', 'description', u'descrip'),
			])
			_dp.assert_not_called()
			_cp.assert_not_called()
			_spo.assert_called_once_with([u'test2', u'test1', u'test3'])
			_copy.assert_not_called()

		# test set new default
		ep = editProfile()
		ep.elements[1]["r"].setChecked(True)
		ep.onOk()
		with patch("physbiblio.config.ConfigVars.loadProfiles") as _lp,\
				patch("physbiblio.config.globalDB.setDefaultProfile") as _sdp,\
				patch("physbiblio.config.globalDB.updateProfileField") as _upf,\
				patch("physbiblio.config.globalDB.deleteProfile") as _dp,\
				patch("physbiblio.config.globalDB.createProfile") as _cp,\
				patch("physbiblio.config.globalDB.setProfileOrder") as _spo,\
				patch("physbiblio.gui.mainWindow.MainWindow.StatusBarMessage") \
					as _m,\
				patch("shutil.copy2") as _copy:
			editProf(p, mw, ep)
			_lp.assert_called_once_with()
			_sdp.assert_called_once_with("test2")
			_upf.assert_has_calls([
				call(u'test1', 'description', u'test1'),
				call(u'test2', 'description', u'test2'),
				call(u'test3', 'description', u'test3'),
			])
			_dp.assert_not_called()
			_cp.assert_not_called()
			_spo.assert_called_once_with([u'test1', u'test2', u'test3'])
			_copy.assert_not_called()

		# test delete
		ep = editProfile()
		ep.elements[1]["x"].setChecked(True)
		ep.onOk()
		with patch("physbiblio.config.ConfigVars.loadProfiles") as _lp,\
				patch("physbiblio.config.globalDB.setDefaultProfile") as _sdp,\
				patch("physbiblio.config.globalDB.updateProfileField") as _upf,\
				patch("physbiblio.config.globalDB.deleteProfile") as _dp,\
				patch("physbiblio.config.globalDB.createProfile") as _cp,\
				patch("physbiblio.config.globalDB.setProfileOrder") as _spo,\
				patch("physbiblio.gui.mainWindow.MainWindow.StatusBarMessage") \
					as _m,\
				patch("physbiblio.gui.profilesManager.askYesNo",
					return_value = True) as _ayn,\
				patch("shutil.copy2") as _copy:
			editProf(p, mw, ep)
			_lp.assert_called_once_with()
			_sdp.assert_not_called()
			_upf.assert_has_calls([
				call(u'test1', 'description', u'test1'),
				call(u'test2', 'description', u'test2'),
				call(u'test3', 'description', u'test3'),
			])
			_dp.assert_called_once_with("test2")
			_cp.assert_not_called()
			_spo.assert_called_once_with([u'test1', u'test3'])
			_ayn.assert_called_once_with("Do you really want to cancel the " +
				"profile 'test2'?\n" +
				"The action cannot be undone!\n" +
				"The corresponding database will not be erased.")
			_copy.assert_not_called()

		# test rename existing
		ep = editProfile()
		ep.elements[1]["n"].setText("testA")
		ep.onOk()
		with patch("physbiblio.config.ConfigVars.loadProfiles") as _lp,\
				patch("physbiblio.config.globalDB.setDefaultProfile") as _sdp,\
				patch("physbiblio.config.globalDB.updateProfileField") as _upf,\
				patch("physbiblio.config.globalDB.deleteProfile") as _dp,\
				patch("physbiblio.config.globalDB.createProfile") as _cp,\
				patch("physbiblio.config.globalDB.setProfileOrder") as _spo,\
				patch("physbiblio.gui.mainWindow.MainWindow.StatusBarMessage") \
					as _m,\
				patch("shutil.copy2") as _copy:
			editProf(p, mw, ep)
			_lp.assert_called_once_with()
			_sdp.assert_not_called()
			_upf.assert_has_calls([
				call(u'test1', 'description', u'test1'),
				call(os.path.join(pbConfig.dataPath, 'test2.db'),
					'name',
					'testA',
					identifierField = 'databasefile'),
				call(u'testA', 'description', u'test2'),
				call(u'test3', 'description', u'test3'),
			])
			_dp.assert_not_called()
			_cp.assert_not_called()
			_spo.assert_called_once_with([u'test1', u'testA', u'test3'])
			_copy.assert_not_called()

		# test rename existing and delete
		ep = editProfile()
		ep.elements[1]["n"].setText("testA")
		ep.elements[1]["x"].setChecked(True)
		ep.onOk()
		with patch("physbiblio.config.ConfigVars.loadProfiles") as _lp,\
				patch("physbiblio.config.globalDB.setDefaultProfile") as _sdp,\
				patch("physbiblio.config.globalDB.updateProfileField") as _upf,\
				patch("physbiblio.config.globalDB.deleteProfile") as _dp,\
				patch("physbiblio.config.globalDB.createProfile") as _cp,\
				patch("physbiblio.config.globalDB.setProfileOrder") as _spo,\
				patch("physbiblio.gui.profilesManager.askYesNo",
					return_value = True) as _ayn,\
				patch("physbiblio.gui.mainWindow.MainWindow.StatusBarMessage") \
					as _m,\
				patch("shutil.copy2") as _copy:
			editProf(p, mw, ep)
			_lp.assert_called_once_with()
			_sdp.assert_not_called()
			_upf.assert_has_calls([
				call(u'test1', 'description', u'test1'),
				call(os.path.join(pbConfig.dataPath, 'test2.db'),
					'name',
					'testA',
					identifierField = 'databasefile'),
				call(u'testA', 'description', u'test2'),
				call(u'test3', 'description', u'test3'),
			])
			_dp.assert_called_once_with("testA")
			_cp.assert_not_called()
			_spo.assert_called_once_with([u'test1', u'test3'])
			_ayn.assert_called_once_with("Do you really want to cancel the " +
				"profile 'testA'?\n" +
				"The action cannot be undone!\n" +
				"The corresponding database will not be erased.")
			_copy.assert_not_called()

		# test rename existing and reject delete
		ep = editProfile()
		ep.elements[1]["n"].setText("testA")
		ep.elements[1]["x"].setChecked(True)
		ep.onOk()
		with patch("physbiblio.config.ConfigVars.loadProfiles") as _lp,\
				patch("physbiblio.config.globalDB.setDefaultProfile") as _sdp,\
				patch("physbiblio.config.globalDB.updateProfileField") as _upf,\
				patch("physbiblio.config.globalDB.deleteProfile") as _dp,\
				patch("physbiblio.config.globalDB.createProfile") as _cp,\
				patch("physbiblio.config.globalDB.setProfileOrder") as _spo,\
				patch("physbiblio.gui.profilesManager.askYesNo",
					return_value = False) as _ayn,\
				patch("physbiblio.gui.mainWindow.MainWindow.StatusBarMessage") \
					as _m,\
				patch("shutil.copy2") as _copy:
			editProf(p, mw, ep)
			_lp.assert_called_once_with()
			_sdp.assert_not_called()
			_upf.assert_has_calls([
				call(u'test1', 'description', u'test1'),
				call(os.path.join(pbConfig.dataPath, 'test2.db'),
					'name',
					'testA',
					identifierField = 'databasefile'),
				call(u'testA', 'description', u'test2'),
				call(u'test3', 'description', u'test3'),
			])
			_dp.assert_not_called()
			_cp.assert_not_called()
			_spo.assert_called_once_with([u'test1', u'testA', u'test3'])
			_ayn.assert_called_once_with("Do you really want to cancel the " +
				"profile 'testA'?\n" +
				"The action cannot be undone!\n" +
				"The corresponding database will not be erased.")
			_copy.assert_not_called()

		# test creation of new profile
		ep = editProfile()
		ep.elements[-1]["n"].setText("testNew")
		ep.elements[-1]["f"].setCurrentText("testNew.db")
		ep.onOk()
		with patch("physbiblio.config.ConfigVars.loadProfiles") as _lp,\
				patch("physbiblio.config.globalDB.setDefaultProfile") as _sdp,\
				patch("physbiblio.config.globalDB.updateProfileField") as _upf,\
				patch("physbiblio.config.globalDB.deleteProfile") as _dp,\
				patch("physbiblio.config.globalDB.createProfile") as _cp,\
				patch("physbiblio.config.globalDB.setProfileOrder") as _spo,\
				patch("physbiblio.gui.errorManager.ErrorStream.write") as _w,\
				patch("physbiblio.gui.mainWindow.MainWindow.StatusBarMessage") \
					as _m,\
				patch("shutil.copy2") as _copy:
			editProf(p, mw, ep)
			_lp.assert_called_once_with()
			_sdp.assert_not_called()
			_upf.assert_has_calls([
				call(u'test1', 'description', u'test1'),
				call(u'test2', 'description', u'test2'),
				call(u'test3', 'description', u'test3'),
			])
			_dp.assert_not_called()
			_cp.assert_called_once_with(
				databasefile = os.path.join(pbConfig.dataPath, 'testNew.db'),
				description = '',
				name = 'testNew')
			_spo.assert_called_once_with(
				['test1', 'test2', 'test3', "testNew"])
			_w.assert_called_with('New profile created.\n')
			_copy.assert_not_called()

		# test creation of new profile as copy of existing one
		ep = editProfile()
		ep.elements[-1]["n"].setText("testNew")
		ep.elements[-1]["f"].setCurrentText("testNew.db")
		ep.elements[-1]["c"].setCurrentText("test1.db")
		ep.onOk()
		with patch("physbiblio.config.ConfigVars.loadProfiles") as _lp,\
				patch("physbiblio.config.globalDB.setDefaultProfile") as _sdp,\
				patch("physbiblio.config.globalDB.updateProfileField") as _upf,\
				patch("physbiblio.config.globalDB.deleteProfile") as _dp,\
				patch("physbiblio.config.globalDB.createProfile") as _cp,\
				patch("physbiblio.config.globalDB.setProfileOrder") as _spo,\
				patch("physbiblio.gui.errorManager.ErrorStream.write") as _w,\
				patch("physbiblio.gui.mainWindow.MainWindow.StatusBarMessage") \
					as _m,\
				patch("shutil.copy2") as _copy:
			editProf(p, mw, ep)
			_lp.assert_called_once_with()
			_sdp.assert_not_called()
			_upf.assert_has_calls([
				call(u'test1', 'description', u'test1'),
				call(u'test2', 'description', u'test2'),
				call(u'test3', 'description', u'test3'),
			])
			_dp.assert_not_called()
			_cp.assert_called_once_with(
				databasefile = os.path.join(pbConfig.dataPath, 'testNew.db'),
				description = '',
				name = 'testNew')
			_spo.assert_called_once_with(
				['test1', 'test2', 'test3', "testNew"])
			_w.assert_called_with('New profile created.\n')
			_copy.assert_called_once_with(
				os.path.join(pbConfig.dataPath, 'test1.db'),
				os.path.join(pbConfig.dataPath, 'testNew.db'))

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
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
		with patch("physbiblio.gui.profilesManager.selectProfiles.initUI") \
				as _iu:
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
		with patch("physbiblio.gui.profilesManager.selectProfiles.initUI") \
				as _iu,\
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
				patch("physbiblio.gui.mainWindow.MainWindow.reloadConfig") \
					as _rc,\
				patch("physbiblio.gui.mainWindow.MainWindow." +
					"reloadMainContent") as _rm,\
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
				patch("physbiblio.gui.mainWindow.MainWindow.reloadConfig") \
					as _rc,\
				patch("physbiblio.gui.mainWindow.MainWindow." +
					"reloadMainContent") as _rm,\
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

		with patch("physbiblio.gui.profilesManager.selectProfiles.onCancel") \
				as _f:
			QTest.mouseClick(sp.cancelButton, Qt.LeftButton)
			_f.assert_called_once_with()
		with patch("physbiblio.gui.profilesManager.selectProfiles.onLoad") \
				as _f:
			QTest.mouseClick(sp.loadButton, Qt.LeftButton)
			_f.assert_called_once_with()

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestmyOrderPushButton(GUITestCase):
	"""
	Test the myOrderPushButton class
	"""
	def test_init(self):
		"""test init"""
		self.max_diff = None
		qi = QIcon(":/images/arrow-down.png")
		p = editProfile(QWidget())
		opb = myOrderPushButton(p, 1, qi, "txt")
		self.assertIsInstance(opb, QPushButton)
		self.assertEqual(opb.text(), "txt")
		self.assertEqual(opb.qicon, qi)
		self.assertEqual(opb.parent(), p)
		self.assertEqual(opb.parentObj, p)
		with patch("physbiblio.gui.profilesManager.editProfile.switchLines") \
				as _s:
			opb.onClick()
			_s.assert_called_once_with(1)
			_s.reset_mock()
			QTest.mouseClick(opb, Qt.LeftButton)
			_s.assert_called_once_with(1)
		with patch("physbiblio.gui.profilesManager.QPushButton.__init__",
				return_value = QPushButton()) as _i:
			opb = myOrderPushButton(p, 1, qi, "txt", True)
			_i.assert_called_once_with(qi, "txt")

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestEditProfile(GUITestCase):
	"""Test the editProfile class"""
	@classmethod
	def setUpClass(self):
		"""set temporary pbConfig settings"""
		self.oldProfileOrder = pbConfig.profileOrder
		self.oldProfiles = pbConfig.profiles
		self.oldCurrentProfileName = pbConfig.currentProfileName
		self.oldCurrentProfile = pbConfig.currentProfile
		self.olddefaultProfileName = pbConfig.defaultProfileName
		pbConfig.profileOrder = ["test1", "test2", "test3"]
		pbConfig.profiles = {
			"test1": {'db': u'test1.db', 'd': u'test1', 'n': u'test1'},
			"test2": {'db': u'test2.db', 'd': u'test2', 'n': u'test2'},
			"test3": {'db': u'test3.db', 'd': u'test3', 'n': u'test3'},
		}
		pbConfig.currentProfileName = "test1"
		pbConfig.defaultProfileName = "test1"
		pbConfig.currentProfile = pbConfig.profiles["test1"]

	@classmethod
	def tearDownClass(self):
		"""restore previous pbConfig settings"""
		pbConfig.profileOrder = self.oldProfileOrder
		pbConfig.profiles = self.oldProfiles
		pbConfig.currentProfileName = self.oldCurrentProfileName
		pbConfig.currentProfile = self.oldCurrentProfile
		pbConfig.defaultProfileName = self.olddefaultProfileName

	def test_init(self):
		"""test init"""
		p = QWidget()
		with patch("physbiblio.gui.profilesManager.editProfile.createForm") \
				as _s:
			ep = editProfile(p)
			self.assertIsInstance(ep, editObjectWindow)
			self.assertEqual(ep.parent(), p)
			_s.assert_called_once_with()

	def test_onOk(self):
		"""test onOk"""
		p = QWidget()
		ep = editProfile(p)
		with patch("physbiblio.gui.profilesManager.QDialog.close") as _c,\
				patch("logging.Logger.info") as _i:
			ep.onOk()
			_c.assert_called_once_with()
			_i.assert_not_called()
			self.assertTrue(ep.result)
		for n, f in [
				["", "testA.db"],
				["testA", ""],
				]:
			ep.elements[-1]["n"].setText(n)
			ep.elements[-1]["f"].setCurrentText(f)
			with patch("physbiblio.gui.profilesManager.QDialog.close") as _c,\
					patch("logging.Logger.info") as _i:
				ep.onOk()
				_c.assert_not_called()
				_i.assert_called_once_with(
					"Cannot create a new profile if 'name' or 'filename' " +
					"is empty.")
		ep.elements[-1]["n"].setText("test1")
		ep.elements[-1]["f"].setCurrentText("testA.db")
		with patch("physbiblio.gui.profilesManager.QDialog.close") as _c,\
				patch("logging.Logger.info") as _i:
			ep.onOk()
			_c.assert_not_called()
			_i.assert_called_once_with(
				"Cannot create new profile: 'name' already in use.")
		ep.elements[-1]["n"].setText("testA")
		ep.elements[-1]["f"].setCurrentText("test1.db")
		with patch("physbiblio.gui.profilesManager.QDialog.close") as _c,\
				patch("logging.Logger.info") as _i:
			ep.onOk()
			_c.assert_not_called()
			_i.assert_called_once_with(
				"Cannot create new profile: 'filename' already in use.")

	def test_addButtons(self):
		"""test addButtons"""
		p = QWidget()
		with patch("physbiblio.gui.profilesManager.editProfile.createForm") \
				as _s:
			ep = editProfile(p)
		ep.addButtons()
		self.assertIsInstance(ep.def_group, QButtonGroup)
		self.assertIsInstance(ep.elements, list)
		self.assertIsInstance(ep.arrows, list)
		self.assertEqual(len(ep.elements), 3)
		self.assertEqual(len(ep.def_group.buttons()), 3)
		self.assertEqual(len(ep.arrows), 2)

		for i, k in enumerate(pbConfig.profileOrder):
			w0 = ep.layout().itemAtPosition(i + 1, 0).widget()
			self.assertIsInstance(w0, QRadioButton)
			if pbConfig.defaultProfileName == k:
				self.assertTrue(w0.isChecked())
			else:
				self.assertFalse(w0.isChecked())
			self.assertIn(w0, ep.def_group.buttons())

			w1 = ep.layout().itemAtPosition(i + 1, 1).widget()
			self.assertIsInstance(w1, QLineEdit)
			self.assertEqual(w1.text(), k)
			w2 = ep.layout().itemAtPosition(i + 1, 2).widget()
			self.assertIsInstance(w2, QLineEdit)
			self.assertEqual(w2.text(),
				pbConfig.profiles[k]["db"].split(os.sep)[-1])
			self.assertTrue(w2.isReadOnly())
			w3 = ep.layout().itemAtPosition(i + 1, 3).widget()
			self.assertIsInstance(w3, QLineEdit)
			self.assertEqual(w3.text(), pbConfig.profiles[k]["d"])

			if i > 1:
				ad = ep.layout().itemAtPosition(i, 5).widget()
				self.assertIsInstance(ad, myOrderPushButton)
				self.assertEqual(ad.data, i - 1)
				self.assertEqual(ep.arrows[i - 1][0], ad)
			if i < 2:
				au = ep.layout().itemAtPosition(i + 2, 4).widget()
				self.assertIsInstance(au, myOrderPushButton)
				self.assertEqual(au.data, i)
				self.assertEqual(ep.arrows[i][1], au)

			w6 = ep.layout().itemAtPosition(i + 1, 6).widget()
			self.assertIsInstance(w6, QCheckBox)
			self.assertFalse(w6.isChecked())
			self.assertEqual(ep.elements[i],
				{
				"r": w0,
				"n": w1,
				"f": w2,
				"d": w3,
				"x": w6
				})

		#test custom arguments A
		pdata = {
			"test1": {
				'db': u'test1.db',
				'd': u'new test1',
				'n': u'test1',
				'x': True,
				},
			"test2": {
				'db': u'test2.db',
				'd': u'test2',
				'n': u'test2',
				'x': False,
				},
			"test3A": {
				'db': u'test3a.db',
				'd': u'test3',
				'n': u'test3A',
				'x': False,
				},
		}
		porder = ["test2", "test1", "test3A"]
		pdefault = "test3A"
		ep.cleanLayout()
		ep.addButtons(pdata, porder, pdefault)
		self.assertIsInstance(ep.def_group, QButtonGroup)
		self.assertIsInstance(ep.elements, list)
		self.assertIsInstance(ep.arrows, list)
		self.assertEqual(len(ep.elements), 3)
		self.assertEqual(len(ep.def_group.buttons()), 3)
		self.assertEqual(len(ep.arrows), 2)

		for i, k in enumerate(porder):
			w0 = ep.layout().itemAtPosition(i + 1, 0).widget()
			self.assertIsInstance(w0, QRadioButton)
			self.assertEqual(w0.isChecked(), pdefault == k)
			self.assertIn(w0, ep.def_group.buttons())

			w1 = ep.layout().itemAtPosition(i + 1, 1).widget()
			self.assertIsInstance(w1, QLineEdit)
			self.assertEqual(w1.text(), k)
			w2 = ep.layout().itemAtPosition(i + 1, 2).widget()
			self.assertIsInstance(w2, QLineEdit)
			self.assertEqual(w2.text(),
				pdata[k]["db"].split(os.sep)[-1])
			self.assertTrue(w2.isReadOnly())
			w3 = ep.layout().itemAtPosition(i + 1, 3).widget()
			self.assertIsInstance(w3, QLineEdit)
			self.assertEqual(w3.text(), pdata[k]["d"])

			if i > 1:
				ad = ep.layout().itemAtPosition(i, 5).widget()
				self.assertIsInstance(ad, myOrderPushButton)
				self.assertEqual(ad.data, i - 1)
				self.assertEqual(ep.arrows[i - 1][0], ad)
			if i < 2:
				au = ep.layout().itemAtPosition(i + 2, 4).widget()
				self.assertIsInstance(au, myOrderPushButton)
				self.assertEqual(au.data, i)
				self.assertEqual(ep.arrows[i][1], au)

			w6 = ep.layout().itemAtPosition(i + 1, 6).widget()
			self.assertIsInstance(w6, QCheckBox)
			self.assertEqual(w6.isChecked(), pdata[k]["x"])
			self.assertEqual(ep.elements[i],
				{
				"r": w0,
				"n": w1,
				"f": w2,
				"d": w3,
				"x": w6
				})

		#test custom arguments B
		pdata = {
			"test1": {
				'db': u'test1.db',
				'n': u'test1',
				'x': True,
				'r': True,
				},
			"test2": {
				'db': u'test2.db',
				'd': u'',
				'n': u'test2',
				'x': False,
				'r': False,
				},
			"test3A": {
				'db': u'test3a.db',
				'd': u'test3',
				'n': u'test3A',
				'x': True,
				'r': False,
				},
		}
		porder = ["test2", "test1", "test3A", "test4"]
		pdefault = "test3A"
		ep.cleanLayout()
		with patch("logging.Logger.warning") as _w:
			ep.addButtons(pdata, porder, pdefault)
			_w.assert_has_calls([
				call("Missing info: 'd' in ['x', 'r', 'db', 'n']." +
					" Default to empty."),
				call("Missing profile: 'test4' in " +
					"['test1', 'test3A', 'test2']"),
				])
		self.assertIsInstance(ep.def_group, QButtonGroup)
		self.assertIsInstance(ep.elements, list)
		self.assertIsInstance(ep.arrows, list)
		self.assertEqual(len(ep.elements), 3)
		self.assertEqual(len(ep.def_group.buttons()), 3)
		self.assertEqual(len(ep.arrows), 2)

		for i, k in enumerate(["test2", "test1", "test3A"]):
			w0 = ep.layout().itemAtPosition(i + 1, 0).widget()
			self.assertIsInstance(w0, QRadioButton)
			self.assertEqual(w0.isChecked(), "test1" == k)
			self.assertIn(w0, ep.def_group.buttons())

			w1 = ep.layout().itemAtPosition(i + 1, 1).widget()
			self.assertIsInstance(w1, QLineEdit)
			self.assertEqual(w1.text(), k)
			w2 = ep.layout().itemAtPosition(i + 1, 2).widget()
			self.assertIsInstance(w2, QLineEdit)
			self.assertEqual(w2.text(),
				pdata[k]["db"].split(os.sep)[-1])
			self.assertTrue(w2.isReadOnly())
			w3 = ep.layout().itemAtPosition(i + 1, 3).widget()
			self.assertIsInstance(w3, QLineEdit)
			self.assertEqual(w3.text(), pdata[k]["d"])

			if i > 1:
				ad = ep.layout().itemAtPosition(i, 5).widget()
				self.assertIsInstance(ad, myOrderPushButton)
				self.assertEqual(ad.data, i - 1)
				self.assertEqual(ep.arrows[i - 1][0], ad)
			if i < 2:
				au = ep.layout().itemAtPosition(i + 2, 4).widget()
				self.assertIsInstance(au, myOrderPushButton)
				self.assertEqual(au.data, i)
				self.assertEqual(ep.arrows[i][1], au)

			w6 = ep.layout().itemAtPosition(i + 1, 6).widget()
			self.assertIsInstance(w6, QCheckBox)
			self.assertEqual(w6.isChecked(), pdata[k]["x"])
			self.assertEqual(ep.elements[i],
				{
				"r": w0,
				"n": w1,
				"f": w2,
				"d": w3,
				"x": w6
				})

	def test_createForm(self):
		"""test createForm"""
		p = QWidget()
		with patch("physbiblio.gui.profilesManager.editProfile.createForm") \
				as _c:
			ep = editProfile(p)
		ep.addButtons()
		with patch("physbiblio.gui.profilesManager.editProfile.addButtons") \
				as _a,\
				patch("glob.iglob",
					return_value = ["old1.db", "test1.db"]) as _g:
			ep.createForm()
			_a.assert_called_once_with(
				pbConfig.profiles,
				pbConfig.profileOrder)
			_g.assert_called_once_with(os.path.join(pbConfig.dataPath, "*.db"))

		# test labels and accept/cancel buttons
		self.assertEqual(ep.windowTitle(), 'Edit profile')
		labels = [
			[0, "Default"],
			[1, "Short name"],
			[2, "Filename"],
			[3, "Description"],
			[4, "Order"],
			[6, "Delete?"],
			]
		for i, l in labels:
			self.assertIsInstance(
				ep.layout().itemAtPosition(0, i).widget(),
				QLabel)
			self.assertEqual(
				ep.layout().itemAtPosition(0, i).widget().text(),
				l)
		i = len(pbConfig.profiles) + 3
		self.assertIsInstance(
			ep.layout().itemAtPosition(i - 2, 0).widget(),
			QLabel)
		self.assertEqual(
			ep.layout().itemAtPosition(i - 2, 0).widget().text(),
			"")
		self.assertIsInstance(
			ep.layout().itemAtPosition(i - 1, 0).widget(),
			QLabel)
		self.assertEqual(
			ep.layout().itemAtPosition(i - 1, 0).widget().text(),
			"Add new?")
		self.assertIsInstance(
			ep.layout().itemAtPosition(i + 1, 0).widget(),
			QLabel)
		self.assertEqual(
			ep.layout().itemAtPosition(i + 1, 0).widget().text(),
			"")
		self.assertIsInstance(
			ep.layout().itemAtPosition(i + 2, 1).widget(),
			QPushButton)
		self.assertEqual(
			ep.layout().itemAtPosition(i + 2, 1).widget(),
			ep.acceptButton)
		self.assertEqual(
			ep.acceptButton.text(),
			"OK")
		self.assertIsInstance(
			ep.layout().itemAtPosition(i + 2, 2).widget(),
			QPushButton)
		self.assertEqual(
			ep.layout().itemAtPosition(i + 2, 2).widget(),
			ep.cancelButton)
		self.assertEqual(
			ep.cancelButton.text(),
			"Cancel")
		self.assertTrue(ep.cancelButton.autoDefault())
		with patch("physbiblio.gui.profilesManager.editProfile.onOk") as _o:
			QTest.mouseClick(ep.acceptButton, Qt.LeftButton)
			_o.assert_called_once_with()
		with patch("physbiblio.gui.profilesManager.editProfile.onCancel") \
				as _o:
			QTest.mouseClick(ep.cancelButton, Qt.LeftButton)
			_o.assert_called_once_with()

		w0 = ep.layout().itemAtPosition(i, 0).widget()
		w1 = ep.layout().itemAtPosition(i, 1).widget()
		w2 = ep.layout().itemAtPosition(i, 2).widget()
		w3 = ep.layout().itemAtPosition(i, 3).widget()
		w6 = ep.layout().itemAtPosition(i, 6).widget()
		self.assertIsInstance(w0, QRadioButton)
		self.assertFalse(w0.isChecked())
		self.assertIn(w0, ep.def_group.buttons())
		self.assertIsInstance(w1, QLineEdit)
		self.assertEqual(w1.text(), "")
		self.assertIsInstance(w2, QComboBox)
		self.assertTrue(w2.isEditable())
		self.assertEqual(w2.currentText(), "")
		self.assertEqual(w2.count(), 2)
		self.assertEqual(w2.itemText(1), "old1.db")
		self.assertIsInstance(w3, QLineEdit)
		self.assertEqual(w3.text(), "")
		self.assertIsInstance(
			ep.layout().itemAtPosition(i, 4).widget(),
			QLabel)
		self.assertEqual(
			ep.layout().itemAtPosition(i, 4).widget().text(),
			"Copy from:")
		self.assertIsInstance(w6, QComboBox)
		self.assertEqual(w6.count(), 4)
		self.assertEqual(w6.currentText(), "None")
		self.assertEqual(w6.itemText(0), "None")
		self.assertEqual(w6.itemText(1), "test1.db")
		self.assertEqual(w6.itemText(2), "test2.db")
		self.assertEqual(w6.itemText(3), "test3.db")
		self.assertEqual(ep.elements[-1],
			{
			"r": w0,
			"n": w1,
			"f": w2,
			"d": w3,
			"c": w6,
			})

		#test custom arguments
		pdata = {
			"test1": {
				'db': u'test1.db',
				'd': u'new test1',
				'n': u'test1',
				'x': True,
				},
			"test2": {
				'db': u'test2.db',
				'd': u'test2',
				'n': u'test2',
				'x': False,
				},
			"test3A": {
				'db': u'test3.db',
				'd': u'test3',
				'n': u'test3A',
				'x': False,
				},
		}
		porder = ["test2", "test1", "test3A"]
		pdefault = "test3A"
		pnew = {
				'db': u'new.db',
				'n': u'testNew',
				'r': True,
				'c': "test1.db",
				}
		ep.cleanLayout()
		with patch("physbiblio.gui.profilesManager.editProfile.addButtons") \
				as _a,\
				patch("glob.iglob",
					return_value = ["old1.db", "test1.db"]) as _g,\
				patch("logging.Logger.warning") as _w:
			ep.createForm(pdata, porder, pdefault, pnew)
			_a.assert_called_once_with(pdata, porder)
			_w.assert_called_with("Missing field: 'd' in " +
				"['c', 'r', 'db', 'n']" +
				". Default to empty.")
		ep.cleanLayout()
		with patch("glob.iglob", return_value = ["old1.db", "test1.db"]) as _g:
			ep.createForm(pdata, porder, pdefault, pnew)

		w0 = ep.layout().itemAtPosition(i, 0).widget()
		w1 = ep.layout().itemAtPosition(i, 1).widget()
		w2 = ep.layout().itemAtPosition(i, 2).widget()
		w3 = ep.layout().itemAtPosition(i, 3).widget()
		w6 = ep.layout().itemAtPosition(i, 6).widget()
		self.assertIsInstance(w0, QRadioButton)
		self.assertTrue(w0.isChecked())
		self.assertIn(w0, ep.def_group.buttons())
		self.assertIsInstance(w1, QLineEdit)
		self.assertEqual(w1.text(), pnew["n"])
		self.assertIsInstance(w2, QComboBox)
		self.assertTrue(w2.isEditable())
		self.assertEqual(w2.currentText(), pnew["db"])
		self.assertEqual(w2.count(), 2)
		self.assertEqual(w2.itemText(0), pnew["db"])
		self.assertEqual(w2.itemText(1), "old1.db")
		self.assertIsInstance(w3, QLineEdit)
		self.assertEqual(w3.text(), "")
		self.assertIsInstance(
			ep.layout().itemAtPosition(i, 4).widget(),
			QLabel)
		self.assertEqual(
			ep.layout().itemAtPosition(i, 4).widget().text(),
			"Copy from:")
		self.assertIsInstance(w6, QComboBox)
		self.assertEqual(w6.count(), 4)
		self.assertEqual(w6.currentText(), pnew["c"])
		self.assertEqual(w6.itemText(0), "None")
		self.assertEqual(w6.itemText(1), "test1.db")
		self.assertEqual(w6.itemText(2), "test2.db")
		self.assertEqual(w6.itemText(3), "test3.db")
		self.assertEqual(ep.elements[-1],
			{
			"r": w0,
			"n": w1,
			"f": w2,
			"d": w3,
			"c": w6,
			})

	def test_switchLines(self):
		"""Test switchLines"""
		p = QWidget()
		ep = editProfile(p)
		with patch("physbiblio.gui.profilesManager.editProfile.createForm") \
				as _cf,\
				patch("physbiblio.gui.profilesManager."+
					"editProfile.cleanLayout") as _cl:
			self.assertTrue(ep.switchLines(0))
			_cl.assert_called_once_with()
			_cf.assert_called_once_with({
				u'test1':
					{'x': False, 'r': True, 'db': u'test1.db', 'd': u'test1'},
				u'test2':
					{'x': False, 'r': False, 'db': u'test2.db', 'd': u'test2'},
				u'test3':
					{'x': False, 'r': False, 'db': u'test3.db', 'd': u'test3'},
				},
				[u'test2', u'test1', u'test3'],
				{'r': False, 'db': u'', 'd': u'', 'n': u''})
		ep.elements[-1]["n"].setText("testA")
		ep.elements[-1]["f"].setCurrentText("testA.db")
		with patch("physbiblio.gui.profilesManager.editProfile.createForm") \
				as _cf,\
				patch("physbiblio.gui.profilesManager." +
					"editProfile.cleanLayout") as _cl:
			self.assertTrue(ep.switchLines(1))
			_cl.assert_called_once_with()
			_cf.assert_called_once_with({
				u'test1':
					{'x': False, 'r': True, 'db': u'test1.db', 'd': u'test1'},
				u'test2':
					{'x': False, 'r': False, 'db': u'test2.db', 'd': u'test2'},
				u'test3':
					{'x': False, 'r': False, 'db': u'test3.db', 'd': u'test3'},
				},
				[u'test1', u'test3', u'test2'],
				{'r': False, 'db': u'testA.db', 'd': u'', 'n': u'testA'})
		with patch("physbiblio.gui.profilesManager.editProfile.createForm") \
				as _cf,\
				patch("physbiblio.gui.profilesManager." +
					"editProfile.cleanLayout") as _cl,\
				patch("logging.Logger.warning") as _i:
			self.assertFalse(ep.switchLines(2))
			_i.assert_called_once_with("Impossible to switch lines: " +
				"index out of range")
			_cl.assert_not_called()
			_cf.assert_not_called()

	def test_cleanLayout(self):
		"""test cleanLayout"""
		p = QWidget()
		ep = editProfile(p)
		self.assertEqual(ep.layout().count(), 36)
		ep.cleanLayout()
		self.assertEqual(ep.layout().count(), 0)

if __name__=='__main__':
	unittest.main()
