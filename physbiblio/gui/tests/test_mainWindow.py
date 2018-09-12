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
	from mock import patch, call
else:
	import unittest
	from unittest.mock import patch, call

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
	"""test"""

	@classmethod
	def setUpClass(self):
		"""define common parameters for test use"""
		super(TestMainWindow, self).setUpClass()
		self.mw = MainWindow()

	def test_init(self):
		"""test"""
		pass

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
			self.mw.undoDB()
			_u.assert_called_once_with()
			_swt.assert_called_once_with('PhysBiblio')
			_rmc.assert_called_once_with()

	def test_refreshMainContent(self):
		"""test refreshMainContent"""
		pBDB.bibs.lastFetched = []
		with patch("physbiblio.gui.mainWindow.MainWindow.done") as _d,\
				patch("physbiblio.gui.bibWindows.bibtexListWindow."
					+ "recreateTable") as _rt,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _fl:
			self.mw.refreshMainContent("anything")
			_d.assert_called_once_with()
			_sbm.assert_called_once_with("Reloading main table...")
			_fl.assert_called_once_with()
			_rt.assert_called_once_with([])

	def test_reloadMainContent(self):
		"""test reloadMainContent"""
		with patch("physbiblio.gui.mainWindow.MainWindow.done") as _d,\
				patch("physbiblio.gui.bibWindows.bibtexListWindow."
					+ "recreateTable") as _rt,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm:
			self.mw.reloadMainContent(bibs="fake")
			_d.assert_called_once_with()
			_sbm.assert_called_once_with("Reloading main table...")
			_rt.assert_called_once_with("fake")
			_rt.reset_mock()
			self.mw.reloadMainContent()
			_rt.assert_called_once_with(None)

	def test_manageProfiles(self):
		"""test manageProfiles"""
		with patch("physbiblio.gui.profilesManager.selectProfiles.__init__",
				return_value=None) as _i,\
				self.assertRaises(RuntimeError):
			self.mw.manageProfiles()
			_i.assert_called_once_with(self.mw)

	def test_editProfile(self):
		"""test editProfile"""
		with patch("physbiblio.gui.mainWindow.editProfile") as _e:
			self.mw.editProfile()
			_e.assert_called_once_with(self.mw)

	def test_config(self):
		"""test"""
		pass

	def test_logfile(self):
		"""test logfile"""
		with patch("physbiblio.gui.dialogWindows.LogFileContentDialog"
				+ ".__init__", return_value=None) as _i,\
				self.assertRaises(RuntimeError):
			self.mw.logfile()
			_i.assert_called_once_with(self.mw)

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
			self.mw.cleanSpare()
			_rit.assert_called_once_with(
				thread_cleanSpare, "Clean spare entries")

	def test_cleanSparePDF(self):
		"""test cleanSparePDF"""
		with patch("physbiblio.gui.mainWindow.MainWindow._runInThread"
				) as _rit,\
				patch("physbiblio.gui.mainWindow.askYesNo",
					return_value=True):
			self.mw.cleanSparePDF()
			_rit.assert_called_once_with(
				thread_cleanSparePDF, "Clean spare PDF folders")
		with patch("physbiblio.gui.mainWindow.MainWindow._runInThread"
				) as _rit,\
				patch("physbiblio.gui.mainWindow.askYesNo",
					return_value=False):
			self.mw.cleanSparePDF()
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
			self.mw.categories()
			_sm.assert_called_once_with("categories triggered")
			_i.assert_called_once_with(self.mw)

	def test_newCategory(self):
		"""test newCategory"""
		with patch("physbiblio.gui.mainWindow.editCategory"
				) as _f:
			self.mw.newCategory()
			_f.assert_called_once_with(self.mw, self.mw)

	def test_experiments(self):
		"""test experiments"""
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _sm,\
				patch("physbiblio.gui.expWindows.ExpsListWindow.__init__",
					return_value=None) as _i,\
				self.assertRaises(RuntimeError):
			self.mw.experiments()
			_sm.assert_called_once_with("experiments triggered")
			_i.assert_called_once_with(self.mw)

	def test_newExperiment(self):
		"""test newExperiment"""
		with patch("physbiblio.gui.mainWindow.editExperiment"
				) as _f:
			self.mw.newExperiment()
			_f.assert_called_once_with(self.mw, self.mw)

	def test_newBibtex(self):
		"""test newBibtex"""
		with patch("physbiblio.gui.mainWindow.editBibtex"
				) as _f:
			self.mw.newBibtex()
			_f.assert_called_once_with(self.mw)

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
			self.mw.sendMessage("mytext")
			_i.assert_called_once_with("mytext")

	def test_done(self):
		"""test done"""
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _sm:
			self.mw.done()
			_sm.assert_called_once_with("...done!")


if __name__=='__main__':
	unittest.main()
