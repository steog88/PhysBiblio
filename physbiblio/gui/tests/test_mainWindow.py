#!/usr/bin/env python
"""Test file for the physbiblio.gui.mainWindow module.

This file is part of the physbiblio package.
"""
import sys
import traceback
import os
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch, call, MagicMock
else:
	import unittest
	from unittest.mock import patch, call, MagicMock

try:
	from physbiblio.setuptests import *
	from physbiblio.gui.setuptests import *
	from physbiblio.gui.mainWindow import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
	print(traceback.format_exc())


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestMainWindow(GUITestCase):
	"""test the MainWindow class"""

	@classmethod
	def setUpClass(self):
		"""define common parameters for test use"""
		super(TestMainWindow, self).setUpClass()
		self.clsName = "physbiblio.gui.mainWindow.MainWindow"
		self.mainW = MainWindow()

	def test_init(self):
		"""test __init__"""
		tcu = thread_checkUpdated()
		tcu.start = MagicMock()
		with patch(self.clsName + ".createActions") as _ca,\
				patch(self.clsName + ".createMenusAndToolBar") as _mt,\
				patch(self.clsName + ".createMainLayout") as _ml,\
				patch(self.clsName + ".setIcon") as _si,\
				patch(self.clsName + ".createStatusBar") as _sb,\
				patch("physbiblio.gui.mainWindow.thread_checkUpdated",
					return_value=tcu) as _cu:
			mw = MainWindow()
			_ca.assert_called_once_with()
			_mt.assert_called_once_with()
			_ml.assert_called_once_with()
			_si.assert_called_once_with()
			_sb.assert_called_once_with()
			_cu.assert_called_once_with(mw)
			tcu.start.assert_called_once_with()
			mw1 = MainWindow(testing=True)
			_ca.assert_called_once_with()
		with patch(self.clsName + ".printNewVersion") as _pnw:
			mw.checkUpdated.result.emit(True, "0.0.0")
			_pnw.assert_called_once_with(True, "0.0.0")
		self.assertIsInstance(mw, QMainWindow)
		self.assertEqual(mw.minimumWidth(), 600)
		self.assertEqual(mw.minimumHeight(), 400)
		self.assertIsInstance(mw.mainStatusBar, QStatusBar)
		self.assertEqual(mw.lastAuthorStats, None)
		self.assertEqual(mw.lastPaperStats, None)
		self.assertIsInstance(mw1, QMainWindow)
		self.assertEqual(mw1.lastPaperStats, None)

	def test_mainWindowTitle(self):
		"""test mainWindowTitle"""
		with patch("PySide2.QtWidgets.QMainWindow.setWindowTitle") as _t:
			self.mainW.mainWindowTitle("mytitle")
			_t.assert_called_once_with("mytitle")

	def test_printNewVersion(self):
		"""test"""
		pass

	def test_setIcon(self):
		"""test"""
		pass

	def test_createActions(self):
		"""test"""
		pass

	def test_closeEvent(self):
		"""test"""
		pass

	def test_createMenusAndToolBar(self):
		"""test"""
		pass

	def test_createMainLayout(self):
		"""test"""
		pass

	def test_undoDB(self):
		"""test undoDB"""
		with patch("physbiblio.databaseCore.physbiblioDBCore.undo") as _u,\
				patch("PySide2.QtWidgets.QMainWindow.setWindowTitle") as _swt,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent"
					) as _rmc:
			self.mainW.undoDB()
			_u.assert_called_once_with()
			_swt.assert_called_once_with('PhysBiblio')
			_rmc.assert_called_once_with()

	def test_refreshMainContent(self):
		"""test refreshMainContent"""
		pBDB.bibs.lastFetched = []
		with patch("physbiblio.gui.mainWindow.MainWindow.done") as _d,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "recreateTable") as _rt,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _fl:
			self.mainW.refreshMainContent()
			_d.assert_called_once_with()
			_sbm.assert_called_once_with("Reloading main table...")
			_fl.assert_called_once_with()
			_rt.assert_called_once_with([])

	def test_reloadMainContent(self):
		"""test reloadMainContent"""
		with patch("physbiblio.gui.mainWindow.MainWindow.done") as _d,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "recreateTable") as _rt,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm:
			self.mainW.reloadMainContent(bibs="fake")
			_d.assert_called_once_with()
			_sbm.assert_called_once_with("Reloading main table...")
			_rt.assert_called_once_with("fake")
			_rt.reset_mock()
			self.mainW.reloadMainContent()
			_rt.assert_called_once_with(None)

	def test_manageProfiles(self):
		"""test manageProfiles"""
		with patch("physbiblio.gui.profilesManager.selectProfiles.__init__",
				return_value=None) as _i,\
				self.assertRaises(RuntimeError):
			self.mainW.manageProfiles()
			_i.assert_called_once_with(self.mainW)

	def test_editProfile(self):
		"""test editProfile"""
		with patch("physbiblio.gui.mainWindow.editProfile") as _e:
			self.mainW.editProfile()
			_e.assert_called_once_with(self.mainW)

	def test_config(self):
		"""test"""
		pass

	def test_logfile(self):
		"""test logfile"""
		with patch("physbiblio.gui.dialogWindows.LogFileContentDialog"
				+ ".__init__", return_value=None) as _i,\
				self.assertRaises(RuntimeError):
			self.mainW.logfile()
			_i.assert_called_once_with(self.mainW)

	def test_reloadConfig(self):
		"""test"""
		pass

	def test_showAbout(self):
		"""test"""
		pass

	def test_showDBStats(self):
		"""test"""
		pass

	def test_runInThread(self):
		"""test"""
		pass

	def test_cleanSpare(self):
		"""test cleanSpare"""
		with patch("physbiblio.gui.mainWindow.MainWindow._runInThread"
				) as _rit:
			self.mainW.cleanSpare()
			_rit.assert_called_once_with(
				thread_cleanSpare, "Clean spare entries")

	def test_cleanSparePDF(self):
		"""test cleanSparePDF"""
		with patch("physbiblio.gui.mainWindow.MainWindow._runInThread"
				) as _rit,\
				patch("physbiblio.gui.mainWindow.askYesNo",
					return_value=True):
			self.mainW.cleanSparePDF()
			_rit.assert_called_once_with(
				thread_cleanSparePDF, "Clean spare PDF folders")
		with patch("physbiblio.gui.mainWindow.MainWindow._runInThread"
				) as _rit,\
				patch("physbiblio.gui.mainWindow.askYesNo",
					return_value=False):
			self.mainW.cleanSparePDF()
			_rit.assert_not_called()

	def test_createStatusBar(self):
		"""test"""
		pass

	def test_statusBarMessage(self):
		"""test"""
		pass

	def test_save(self):
		"""test"""
		pass

	def test_importFromBib(self):
		"""test"""
		pass

	def test_export(self):
		"""test"""
		pass

	def test_exportSelection(self):
		"""test"""
		pass

	def test_exportFile(self):
		"""test"""
		pass

	def test_exportUpdate(self):
		"""test"""
		pass

	def test_exportAll(self):
		"""test"""
		pass

	def test_categories(self):
		"""test categories"""
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _sm,\
				patch("physbiblio.gui.catWindows.catsTreeWindow.__init__",
					return_value=None) as _i,\
				self.assertRaises(RuntimeError):
			self.mainW.categories()
			_sm.assert_called_once_with("categories triggered")
			_i.assert_called_once_with(self.mainW)

	def test_newCategory(self):
		"""test newCategory"""
		with patch("physbiblio.gui.mainWindow.editCategory"
				) as _f:
			self.mainW.newCategory()
			_f.assert_called_once_with(self.mainW, self.mainW)

	def test_experiments(self):
		"""test experiments"""
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _sm,\
				patch("physbiblio.gui.expWindows.ExpsListWindow.__init__",
					return_value=None) as _i,\
				self.assertRaises(RuntimeError):
			self.mainW.experiments()
			_sm.assert_called_once_with("experiments triggered")
			_i.assert_called_once_with(self.mainW)

	def test_newExperiment(self):
		"""test newExperiment"""
		with patch("physbiblio.gui.mainWindow.editExperiment"
				) as _f:
			self.mainW.newExperiment()
			_f.assert_called_once_with(self.mainW, self.mainW)

	def test_newBibtex(self):
		"""test newBibtex"""
		with patch("physbiblio.gui.mainWindow.editBibtex"
				) as _f:
			self.mainW.newBibtex()
			_f.assert_called_once_with(self.mainW)

	def test_searchBiblio(self):
		"""test"""
		pass

	def test_runSearchBiblio(self):
		"""test"""
		pass

	def test_runSearchReplaceBiblio(self):
		"""test"""
		pass

	def test_delSearchBiblio(self):
		"""test"""
		pass

	def test_searchAndReplace(self):
		"""test"""
		pass

	def test_runReplace(self):
		"""test"""
		pass

	def test_updateAllBibtexsAsk(self):
		"""test"""
		pass

	def test_updateAllBibtexs(self):
		"""test"""
		pass

	def test_updateInspireInfo(self):
		"""test"""
		pass

	def test_authorStats(self):
		"""test"""
		pass

	def test_getInspireStats(self):
		"""test"""
		pass

	def test_inspireLoadAndInsert(self):
		"""test"""
		pass

	def test_askCatsForEntries(self):
		"""test"""
		pass

	def test_inspireLoadAndInsertWithCats(self):
		"""test"""
		pass

	def test_advancedImport(self):
		"""test"""
		pass

	def test_cleanAllBibtexsAsk(self):
		"""test"""
		pass

	def test_cleanAllBibtexs(self):
		"""test"""
		pass

	def test_findBadBibtexs(self):
		"""test"""
		pass

	def test_infoFromArxiv(self):
		"""test"""
		pass

	def test_browseDailyArxiv(self):
		"""test"""
		pass

	def test_sendMessage(self):
		"""test sendMessage"""
		with patch("physbiblio.gui.mainWindow.infoMessage"
				) as _i:
			self.mainW.sendMessage("mytext")
			_i.assert_called_once_with("mytext")

	def test_done(self):
		"""test done"""
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _sm:
			self.mainW.done()
			_sm.assert_called_once_with("...done!")


if __name__=='__main__':
	unittest.main()
