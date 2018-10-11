#!/usr/bin/env python
"""Test file for the physbiblio.gui.mainWindow module.

This file is part of the physbiblio package.
"""
import sys
import traceback
import os
from PySide2.QtCore import Qt, QEvent
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
		self.qmwName = "PySide2.QtWidgets.QMainWindow"
		self.modName = "physbiblio.gui.mainWindow"
		self.clsName = self.modName + ".MainWindow"
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
				patch(self.modName + ".thread_checkUpdated",
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
		self.assertGeometry(mw, 0, 0,
			QDesktopWidget().availableGeometry().width(),
			QDesktopWidget().availableGeometry().height())

	def test_closeEvent(self):
		"""test closeEvent"""
		with patch("physbiblio.databaseCore.physbiblioDBCore."
					+ "checkUncommitted", return_value=True) as _c,\
				patch(self.modName + ".askYesNo",
					side_effect=[True, False]) as _a,\
				patch("PySide2.QtCore.QEvent.accept") as _ea,\
				patch("PySide2.QtCore.QEvent.ignore") as _ei:
			self.mainW.closeEvent(QEvent)
			_c.assert_called_once_with()
			_a.assert_called_once_with(
				"There may be unsaved changes to the database.\n"
				+ "Do you really want to exit?")
			_ea.assert_called_once_with()
			self.mainW.closeEvent(QEvent)
			_ei.assert_called_once_with()
		oldcfg = pbConfig.params["askBeforeExit"]
		pbConfig.params["askBeforeExit"] = False
		with patch("physbiblio.databaseCore.physbiblioDBCore."
					+ "checkUncommitted", return_value=False) as _c,\
				patch(self.modName + ".askYesNo",
					side_effect=[True, False]) as _a,\
				patch("PySide2.QtCore.QEvent.accept") as _ea,\
				patch("PySide2.QtCore.QEvent.ignore") as _ei:
			self.mainW.closeEvent(QEvent)
			_c.assert_called_once_with()
			_ea.assert_called_once_with()
			_ea.reset_mock()
			pbConfig.params["askBeforeExit"] = True
			self.mainW.closeEvent(QEvent)
			_a.assert_called_once_with(
				"Do you really want to exit?")
			_ea.assert_called_once_with()
			self.mainW.closeEvent(QEvent)
			_ei.assert_called_once_with()
		pbConfig.params["askBeforeExit"] = oldcfg

	def test_mainWindowTitle(self):
		"""test mainWindowTitle"""
		with patch(self.qmwName + ".setWindowTitle") as _t:
			self.mainW.mainWindowTitle("mytitle")
			_t.assert_called_once_with("mytitle")

	def test_printNewVersion(self):
		"""test printNewVersion"""
		with patch("logging.Logger.info") as _i:
			self.mainW.printNewVersion(False, "")
			_i.assert_called_once_with("No new versions available!")
		with patch("logging.Logger.warning") as _w:
			self.mainW.printNewVersion(True, "0.0.0")
			_w.assert_called_once_with("New version available (0.0.0)!\n"
				+ "You can upgrade with `pip install -U physbiblio` "
				+ "(with `sudo`, eventually).")

	def test_setIcon(self):
		"""test setIcon"""
		qi = QIcon(':/images/icon.png')
		with patch(self.modName + ".QIcon", return_value=qi) as _qi,\
				patch(self.qmwName + ".setWindowIcon") as _swi:
			self.mainW.setIcon()
			_qi.assert_called_once_with(':/images/icon.png')
			_swi.assert_called_once_with(qi)

	def test_createActions(self):
		"""test createActions"""
		raise NotImplementedError

	def test_createMenusAndToolBar(self):
		"""test createMenusAndToolBar"""
		raise NotImplementedError

	def test_createMainLayout(self):
		"""test createMainLayout"""
		raise NotImplementedError

	def test_undoDB(self):
		"""test undoDB"""
		with patch("physbiblio.databaseCore.physbiblioDBCore.undo") as _u,\
				patch(self.qmwName + ".setWindowTitle") as _swt,\
				patch(self.clsName + ".reloadMainContent") as _rmc:
			self.mainW.undoDB()
			_u.assert_called_once_with()
			_swt.assert_called_once_with('PhysBiblio')
			_rmc.assert_called_once_with()

	def test_refreshMainContent(self):
		"""test refreshMainContent"""
		pBDB.bibs.lastFetched = []
		with patch(self.clsName + ".done") as _d,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "recreateTable") as _rt,\
				patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _fl:
			self.mainW.refreshMainContent()
			_d.assert_called_once_with()
			_sbm.assert_called_once_with("Reloading main table...")
			_fl.assert_called_once_with()
			_rt.assert_called_once_with([])

	def test_reloadMainContent(self):
		"""test reloadMainContent"""
		with patch(self.clsName + ".done") as _d,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "recreateTable") as _rt,\
				patch(self.clsName + ".statusBarMessage") as _sbm:
			self.mainW.reloadMainContent(bibs="fake")
			_d.assert_called_once_with()
			_sbm.assert_called_once_with("Reloading main table...")
			_rt.assert_called_once_with("fake")
			_rt.reset_mock()
			self.mainW.reloadMainContent()
			_rt.assert_called_once_with(None)

	def test_manageProfiles(self):
		"""test manageProfiles"""
		sp = selectProfiles(self.mainW)
		sp.exec_ = MagicMock()
		with patch(self.modName + ".selectProfiles",
				return_value=sp) as _i:
			self.mainW.manageProfiles()
			_i.assert_called_once_with(self.mainW)
			sp.exec_.assert_called_once_with()

	def test_editProfile(self):
		"""test editProfile"""
		with patch(self.modName + ".editProfile") as _e:
			self.mainW.editProfile()
			_e.assert_called_once_with(self.mainW)

	def test_config(self):
		"""test config"""
		raise NotImplementedError

	def test_logfile(self):
		"""test logfile"""
		ld = LogFileContentDialog(self.mainW)
		ld.exec_ = MagicMock()
		with patch(self.modName + ".LogFileContentDialog",
				return_value=ld) as _i:
			self.mainW.logfile()
			_i.assert_called_once_with(self.mainW)
			ld.exec_.assert_called_once_with()

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
		with patch(self.clsName + "._runInThread") as _rit:
			self.mainW.cleanSpare()
			_rit.assert_called_once_with(
				thread_cleanSpare, "Clean spare entries")

	def test_cleanSparePDF(self):
		"""test cleanSparePDF"""
		with patch(self.clsName + "._runInThread") as _rit,\
				patch(self.modName + ".askYesNo",
					return_value=True):
			self.mainW.cleanSparePDF()
			_rit.assert_called_once_with(
				thread_cleanSparePDF, "Clean spare PDF folders")
		with patch(self.clsName + "._runInThread") as _rit,\
				patch(self.modName + ".askYesNo",
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
		ca = catsTreeWindow(self.mainW)
		ca.show = MagicMock()
		with patch(self.clsName + ".statusBarMessage") as _sm,\
				patch(self.modName + ".catsTreeWindow",
					return_value=ca) as _i:
			self.mainW.categories()
			_sm.assert_called_once_with("categories triggered")
			_i.assert_called_once_with(self.mainW)
			ca.show.assert_called_once_with()

	def test_newCategory(self):
		"""test newCategory"""
		with patch(self.modName + ".editCategory") as _f:
			self.mainW.newCategory()
			_f.assert_called_once_with(self.mainW, self.mainW)

	def test_experiments(self):
		"""test experiments"""
		ex = ExpsListWindow(self.mainW)
		ex.show = MagicMock()
		with patch(self.clsName + ".statusBarMessage") as _sm,\
				patch(self.modName + ".ExpsListWindow",
					return_value=ex) as _i:
			self.mainW.experiments()
			_sm.assert_called_once_with("experiments triggered")
			_i.assert_called_once_with(self.mainW)
			ex.show.assert_called_once_with()

	def test_newExperiment(self):
		"""test newExperiment"""
		with patch(self.modName + ".editExperiment") as _f:
			self.mainW.newExperiment()
			_f.assert_called_once_with(self.mainW, self.mainW)

	def test_newBibtex(self):
		"""test newBibtex"""
		with patch(self.modName + ".editBibtex") as _f:
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
		with patch(self.modName + ".infoMessage") as _i:
			self.mainW.sendMessage("mytext")
			_i.assert_called_once_with("mytext")

	def test_done(self):
		"""test done"""
		with patch(self.clsName + ".statusBarMessage") as _sm:
			self.mainW.done()
			_sm.assert_called_once_with("...done!")


if __name__=='__main__':
	unittest.main()
