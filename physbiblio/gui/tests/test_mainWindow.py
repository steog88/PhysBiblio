#!/usr/bin/env python
"""Test file for the physbiblio.gui.mainWindow module.

This file is part of the physbiblio package.
"""
import sys
import traceback
import os
from PySide2.QtCore import Qt, QEvent
from PySide2.QtGui import QImage
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QMenu, QToolBar

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
		e = QEvent(QEvent.Close)
		with patch("physbiblio.databaseCore.physbiblioDBCore."
					+ "checkUncommitted", return_value=True) as _c,\
				patch(self.modName + ".askYesNo",
					side_effect=[True, False]) as _a,\
				patch("PySide2.QtCore.QEvent.accept") as _ea,\
				patch("PySide2.QtCore.QEvent.ignore") as _ei:
			self.mainW.closeEvent(e)
			_c.assert_called_once_with()
			_a.assert_called_once_with(
				"There may be unsaved changes to the database.\n"
				+ "Do you really want to exit?")
			_ea.assert_called_once_with()
			self.mainW.closeEvent(e)
			_ei.assert_called_once_with()
		oldcfg = pbConfig.params["askBeforeExit"]
		pbConfig.params["askBeforeExit"] = False
		with patch("physbiblio.databaseCore.physbiblioDBCore."
					+ "checkUncommitted", return_value=False) as _c,\
				patch(self.modName + ".askYesNo",
					side_effect=[True, False]) as _a,\
				patch("PySide2.QtCore.QEvent.accept") as _ea,\
				patch("PySide2.QtCore.QEvent.ignore") as _ei:
			self.mainW.closeEvent(e)
			_c.assert_called_once_with()
			_ea.assert_called_once_with()
			_ea.reset_mock()
			pbConfig.params["askBeforeExit"] = True
			self.mainW.closeEvent(e)
			_a.assert_called_once_with(
				"Do you really want to exit?")
			_ea.assert_called_once_with()
			self.mainW.closeEvent(e)
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
		def assertAction(act, t, tip, trig, s=None, i=None, p=None):
			"""test the properties of a single action

			Parameters:
				act: the QAction to be tested
				t: the title/text
				tip: the status tip
				trig: the name of the triggered function
					(must be a MainWindow method)
				s (default None): the shortcut, if any, or None
				i (default None): the icon filename, if any, or None
				p (default None): the mocked triggered function or None
			"""
			self.assertIsInstance(act, QAction)
			self.assertEqual(act.text(), t)
			if s is not None:
				self.assertEqual(act.shortcut(), s)
			if i is not None:
				img = QImage(i).convertToFormat(
					QImage.Format_ARGB32_Premultiplied)
				self.assertEqual(img,
					act.icon().pixmap(img.size()).toImage())
			self.assertEqual(act.statusTip(), tip)
			if p is None:
				with patch("%s.%s"%(self.clsName, trig)) as _f:
					act.trigger()
					_f.assert_called_once_with()
			else:
				act.trigger()
				p.assert_called_once_with()

		with patch("PySide2.QtWidgets.QMainWindow.close") as _f:
			mw = MainWindow(testing=True)
			mw.createActions()
			assertAction(mw.exitAct,
				"E&xit",
				"Exit application",
				"close",
				s="Ctrl+Q",
				i=":/images/application-exit.png",
				p=_f)

		assertAction(self.mainW.profilesAct,
			"&Profiles",
			"Manage profiles",
			"manageProfiles",
			s="Ctrl+P",
			i=":/images/profiles.png")

		assertAction(self.mainW.editProfileWindowsAct,
			"&Edit profiles",
			"Edit profiles",
			"editProfile",
			s="Ctrl+Alt+P")

		assertAction(self.mainW.undoAct,
			"&Undo",
			"Rollback to last saved database state",
			"undoDB",
			s="Ctrl+Z",
			i=":/images/edit-undo.png")

		assertAction(self.mainW.saveAct,
			"&Save database",
			"Save the modifications",
			"save",
			s="Ctrl+S",
			i=":/images/file-save.png")

		assertAction(self.mainW.importBibAct,
			"&Import from *.bib",
			"Import the entries from a *.bib file",
			"importFromBib",
			s="Ctrl+B")

		assertAction(self.mainW.exportAct,
			"Ex&port last as *.bib",
			"Export last query as *.bib",
			"export",
			i=":/images/export.png")

		assertAction(self.mainW.exportAllAct,
			"Export &all as *.bib",
			"Export complete bibliography as *.bib",
			"exportAll",
			s="Ctrl+A",
			i=":/images/export-table.png")

		assertAction(self.mainW.exportFileAct,
			"Export for a *.&tex",
			"Export as *.bib the bibliography needed "
				+ "to compile a .tex file",
			"exportFile",
			s="Ctrl+X")

		assertAction(self.mainW.exportUpdateAct,
			"Update an existing *.&bib file",
			"Read a *.bib file and update "
				+ "the existing elements inside it",
			"exportUpdate",
			s="Ctrl+Shift+X")

		assertAction(self.mainW.catAct,
			"&Categories",
			"Manage Categories",
			"categories",
			s="Ctrl+T")

		assertAction(self.mainW.newCatAct,
			"Ne&w Category",
			"New Category",
			"newCategory",
			s="Ctrl+Shift+T")

		assertAction(self.mainW.expAct,
			"&Experiments",
			"List of Experiments",
			"experiments",
			s="Ctrl+E")

		assertAction(self.mainW.newExpAct,
			"&New Experiment",
			"New Experiment",
			"newExperiment",
			s="Ctrl+Shift+E")

		assertAction(self.mainW.searchBibAct,
			"&Find Bibtex entries",
			"Open the search dialog to filter the bibtex list",
			"searchBiblio",
			s="Ctrl+F",
			i=":/images/find.png")

		assertAction(self.mainW.searchReplaceAct,
			"&Search and replace bibtexs",
			"Open the search&replace dialog",
			"searchAndReplace",
			s="Ctrl+H")

		assertAction(self.mainW.newBibAct,
			"New &Bib item",
			"New bibliographic item",
			"newBibtex",
			s="Ctrl+N",
			i=":/images/file-add.png")

		assertAction(self.mainW.inspireLoadAndInsertAct,
			"&Load from INSPIRE-HEP",
			"Use INSPIRE-HEP to load and insert bibtex entries",
			"inspireLoadAndInsert",
			s="Ctrl+Shift+I")

		assertAction(self.mainW.inspireLoadAndInsertWithCatsAct,
			"&Load from INSPIRE-HEP (ask categories)",
			"Use INSPIRE-HEP to load and insert bibtex entries, "
				+ "then ask the categories for each",
			"inspireLoadAndInsertWithCats",
			s="Ctrl+I")

		assertAction(self.mainW.advImportAct,
			"&Advanced Import",
			"Open the advanced import window",
			"advancedImport",
			s="Ctrl+Alt+I")

		assertAction(self.mainW.updateAllBibtexsAct,
			"&Update bibtexs",
			"Update all the journal info of bibtexs",
			"updateAllBibtexs",
			s="Ctrl+U")

		assertAction(self.mainW.updateAllBibtexsAskAct,
			"Update bibtexs (&personalized)",
			"Update all the journal info of bibtexs, "
				+ "but with non-standard options (start from, force, ...)",
			"updateAllBibtexsAsk",
			s="Ctrl+Shift+U")

		assertAction(self.mainW.cleanAllBibtexsAct,
			"&Clean bibtexs",
			"Clean all the bibtexs",
			"cleanAllBibtexs",
			s="Ctrl+L")

		assertAction(self.mainW.findBadBibtexsAct,
			"&Find corrupted bibtexs",
			"Find all the bibtexs which contain syntax errors "
				+ "and are not readable",
			"findBadBibtexs",
			s="Ctrl+Shift+B")

		assertAction(self.mainW.infoFromArxivAct,
			"Info from ar&Xiv",
			"Get info from arXiv",
			"infoFromArxiv",
			s="Ctrl+V")

		assertAction(self.mainW.dailyArxivAct,
			"Browse last ar&Xiv listings",
			"Browse most recent arXiv listings",
			"browseDailyArxiv",
			s="Ctrl+D")

		assertAction(self.mainW.cleanAllBibtexsAskAct,
			"C&lean bibtexs (from ...)",
			"Clean all the bibtexs, starting from a given one",
			"cleanAllBibtexsAsk",
			s="Ctrl+Shift+L")

		assertAction(self.mainW.authorStatsAct,
			"&AuthorStats",
			"Search publication and citation stats "
				+ "of an author from INSPIRES",
			"authorStats",
			s="Ctrl+Shift+A")

		assertAction(self.mainW.configAct,
			"Settin&gs",
			"Save the settings",
			"config",
			s="Ctrl+Shift+S",
			i=":/images/settings.png")

		assertAction(self.mainW.refreshAct,
			"&Refresh current entries list",
			"Refresh the current list of entries",
			"refreshMainContent",
			s="F5",
			i=":/images/refresh2.png")

		assertAction(self.mainW.reloadAct,
			"&Reload (reset) main table",
			"Reload the list of bibtex entries",
			"reloadMainContent",
			s="Shift+F5",
			i=":/images/refresh.png")

		assertAction(self.mainW.aboutAct,
			"&About",
			"Show About box",
			"showAbout",
			i=":/images/help-about.png")

		assertAction(self.mainW.logfileAct,
			"Log file",
			"Show the content of the logfile",
			"logfile",
			s="Ctrl+G")

		assertAction(self.mainW.dbstatsAct,
			"&Database info",
			"Show some statistics about the current database",
			"showDBStats",
			i=":/images/stats.png")

		assertAction(self.mainW.cleanSpareAct,
			"&Clean spare entries",
			"Remove spare entries from the connection tables.",
			"cleanSpare")

		assertAction(self.mainW.cleanSparePDFAct,
			"&Clean spare PDF folders",
			"Remove spare PDF folders.",
			"cleanSparePDF")

	def test_createMenusAndToolBar(self):
		"""test createMenusAndToolBar"""
		def assertMenu(menu, title, acts):
			self.assertIsInstance(menu, QMenu)
			self.assertEqual(menu.title(), title)
			macts = menu.actions()
			self.assertEqual(len(macts), len(acts))
			for i, a in enumerate(acts):
				if a is None:
					self.assertTrue(macts[i].isSeparator())
				else:
					self.assertEqual(macts[i], a)

		assertMenu(self.mainW.fileMenu, "&File",
			[self.mainW.undoAct,
			self.mainW.saveAct,
			None,
			self.mainW.exportAct,
			self.mainW.exportFileAct,
			self.mainW.exportAllAct,
			self.mainW.exportUpdateAct,
			None,
			self.mainW.profilesAct,
			self.mainW.editProfileWindowsAct,
			self.mainW.configAct,
			None,
			self.mainW.exitAct])

		assertMenu(self.mainW.bibMenu, "&Bibliography",
			[self.mainW.newBibAct,
			self.mainW.importBibAct,
			self.mainW.inspireLoadAndInsertWithCatsAct,
			self.mainW.inspireLoadAndInsertAct,
			self.mainW.advImportAct,
			None,
			self.mainW.cleanAllBibtexsAct,
			self.mainW.cleanAllBibtexsAskAct,
			self.mainW.findBadBibtexsAct,
			None,
			self.mainW.infoFromArxivAct,
			self.mainW.updateAllBibtexsAct,
			self.mainW.updateAllBibtexsAskAct,
			None,
			self.mainW.searchBibAct,
			self.mainW.searchReplaceAct,
			None,
			self.mainW.refreshAct,
			self.mainW.reloadAct])

		assertMenu(self.mainW.catMenu, "&Categories",
			[self.mainW.catAct,
			self.mainW.newCatAct])

		assertMenu(self.mainW.expMenu, "&Experiments",
			[self.mainW.expAct,
			self.mainW.newExpAct])

		assertMenu(self.mainW.toolMenu, "&Tools",
			[self.mainW.dailyArxivAct,
			None,
			self.mainW.cleanSpareAct,
			self.mainW.cleanSparePDFAct,
			None,
			self.mainW.authorStatsAct])

		assertMenu(self.mainW.helpMenu, "&Help",
			[self.mainW.dbstatsAct,
			self.mainW.logfileAct,
			None,
			self.mainW.aboutAct])

		tb = self.mainW.mainToolBar
		self.assertIsInstance(tb, QToolBar)
		macts = tb.actions()
		acts = [self.mainW.undoAct,
			self.mainW.saveAct,
			None,
			self.mainW.newBibAct,
			self.mainW.searchBibAct,
			self.mainW.searchReplaceAct,
			self.mainW.exportAct,
			self.mainW.exportAllAct,
			None,
			self.mainW.refreshAct,
			self.mainW.reloadAct,
			None,
			self.mainW.configAct,
			self.mainW.dbstatsAct,
			self.mainW.aboutAct,
			None,
			self.mainW.exitAct]
		self.assertEqual(len(macts), len(acts))
		for i, a in enumerate(acts):
			if a is None:
				self.assertTrue(macts[i].isSeparator())
			else:
				self.assertEqual(macts[i], a)
		# self.assertEqual(tb.title(), "Toolbar")

		#test empty search/replace menu
		with patch("physbiblio.config.globalDB.getSearchList",
				side_effect=[[], []]) as _gs:
			self.mainW.createMenusAndToolBar()
			self.assertEqual(self.mainW.searchMenu, None)
			self.assertEqual(self.mainW.replaceMenu, None)

		#create with mock getSearchList for searches and replaces
		with patch("physbiblio.config.globalDB.getSearchList",
				side_effect=[
					[{"idS": 0, "name": "s1", "searchDict": "{'n': 'abc'}",
						"limitNum": 101, "offsetNum": 99},
					{"idS": 1, "name": "s2", "searchDict": "{'n': 'def'}",
						"limitNum": 102, "offsetNum": 100}],
					[{"idS": 2, "name": "s3", "searchDict": "{'n': 'ghi'}",
						"replaceFields": "['a', 'b']", "offsetNum": 1},
					{"idS": 3, "name": "s4", "searchDict": "{'n': 'jkl'}",
						"replaceFields": "['c', 'd']", "offsetNum": 2}]
					]) as _gs:
			self.mainW.createMenusAndToolBar()
			self.assertIsInstance(self.mainW.searchMenu, QMenu)
			self.assertEqual(self.mainW.searchMenu.title(),
				"Frequent &searches")
			macts = self.mainW.searchMenu.actions()
			acts = [
				["s1", self.clsName + ".runSearchBiblio",
					[{'n': 'abc'}, 101, 99]],
				["s2", self.clsName + ".runSearchBiblio",
					[{'n': 'def'}, 102, 100]],
				None,
				["Delete 's1'", self.clsName + ".delSearchBiblio", [0, "s1"]],
				["Delete 's2'", self.clsName + ".delSearchBiblio", [1, "s2"]]
				]
			for i, a in enumerate(acts):
				if a is None:
					self.assertTrue(macts[i].isSeparator())
				else:
					self.assertEqual(macts[i].text(), a[0])
					with patch(a[1]) as _f:
						macts[i].trigger()
						_f.assert_called_once_with(*a[2])
			self.assertIsInstance(self.mainW.replaceMenu, QMenu)
			self.assertEqual(self.mainW.replaceMenu.title(),
				"Frequent &replaces")
			macts = self.mainW.replaceMenu.actions()
			acts = [
				["s3", self.clsName + ".runSearchReplaceBiblio",
					[{'n': 'ghi'}, ['a', 'b'], 1]],
				["s4", self.clsName + ".runSearchReplaceBiblio",
					[{'n': 'jkl'}, ['c', 'd'], 2]],
				None,
				["Delete 's3'", self.clsName + ".delSearchBiblio", [2, "s3"]],
				["Delete 's4'", self.clsName + ".delSearchBiblio", [3, "s4"]]
				]
			for i, a in enumerate(acts):
				if a is None:
					self.assertTrue(macts[i].isSeparator())
				else:
					self.assertEqual(macts[i].text(), a[0])
					with patch(a[1]) as _f:
						macts[i].trigger()
						_f.assert_called_once_with(*a[2])

		raise NotImplementedError
		#test order of menus with and without s&r
		print [self.mainW.menuBar().widgetForAction(a)
			for a in self.mainW.menuBar().actions()]

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
