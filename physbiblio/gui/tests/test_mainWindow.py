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

		assertAction(self.mainW.EditProfileWindowsAct,
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
			self.mainW.EditProfileWindowsAct,
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
		self.assertEqual(tb.windowTitle(), "Toolbar")

		#test empty search/replace menu
		with patch("physbiblio.config.globalDB.getSearchList",
				side_effect=[[], []]) as _gs:
			self.mainW.createMenusAndToolBar()
			self.assertEqual(self.mainW.searchMenu, None)
			self.assertEqual(self.mainW.replaceMenu, None)
		#test order of menus
		self.assertEqual([a.menu() for a in self.mainW.menuBar().actions()],
			[self.mainW.fileMenu,
			self.mainW.bibMenu,
			self.mainW.catMenu,
			self.mainW.expMenu,
			self.mainW.toolMenu,
			self.mainW.helpMenu])

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
		#test order of menus with and without s&r
		self.assertEqual([a.menu() for a in self.mainW.menuBar().actions()],
			[self.mainW.fileMenu,
			self.mainW.bibMenu,
			self.mainW.catMenu,
			self.mainW.expMenu,
			self.mainW.toolMenu,
			self.mainW.searchMenu,
			self.mainW.replaceMenu,
			self.mainW.helpMenu])

	def test_createMainLayout(self):
		"""test createMainLayout"""
		self.assertIsInstance(self.mainW.bibtexListWindow, BibtexListWindow)
		self.assertEqual(self.mainW.bibtexListWindow.frameShape(),
			QFrame.StyledPanel)
		self.assertIsInstance(self.mainW.bottomLeft, BibtexInfo)
		self.assertEqual(self.mainW.bottomLeft.frameShape(),
			QFrame.StyledPanel)
		self.assertIsInstance(self.mainW.bottomCenter, BibtexInfo)
		self.assertEqual(self.mainW.bottomCenter.frameShape(),
			QFrame.StyledPanel)
		self.assertIsInstance(self.mainW.bottomRight, BibtexInfo)
		self.assertEqual(self.mainW.bottomRight.frameShape(),
			QFrame.StyledPanel)

		spl = self.mainW.centralWidget()
		self.assertIsInstance(spl, QSplitter)
		self.assertEqual(spl.orientation(), Qt.Vertical)
		self.assertEqual(spl.widget(0), self.mainW.bibtexListWindow)
		self.assertEqual(spl.widget(0).sizePolicy().verticalStretch(), 3)
		self.assertIsInstance(spl.widget(1), QSplitter)
		self.assertEqual(spl.widget(1).sizePolicy().verticalStretch(), 1)
		spl1 = spl.widget(1)
		self.assertEqual(spl1.orientation(), Qt.Horizontal)
		self.assertEqual(spl1.widget(0), self.mainW.bottomLeft)
		self.assertEqual(spl1.widget(1), self.mainW.bottomCenter)
		self.assertEqual(spl1.widget(2), self.mainW.bottomRight)
		self.assertGeometry(spl, 0, 0,
			QDesktopWidget().availableGeometry().width(),
			QDesktopWidget().availableGeometry().height())

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
		cw = configWindow(self.mainW)
		cw.exec_ = MagicMock()
		raise NotImplementedError

	def test_logfile(self):
		"""test logfile"""
		with patch("logging.Logger.exception") as _e:
			ld = LogFileContentDialog(self.mainW)
		ld.exec_ = MagicMock()
		with patch(self.modName + ".LogFileContentDialog",
				return_value=ld) as _i:
			self.mainW.logfile()
			_i.assert_called_once_with(self.mainW)
			ld.exec_.assert_called_once_with()

	def test_reloadConfig(self):
		"""test reloadConfig"""
		oldWebA = pbConfig.params["webApplication"]
		oldPdfA = pbConfig.params["pdfApplication"]
		oldPdfF = pbConfig.params["pdfFolder"]
		oldPdfD = pBPDF.pdfDir
		pbConfig.params["webApplication"] = "webApp"
		pbConfig.params["pdfApplication"] = "pdfApp"
		pbConfig.params["pdfFolder"] = "pdf/folder"
		with patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "reloadColumnContents") as _rcc:
			self.mainW.reloadConfig()
			_sbm.assert_called_once_with("Reloading configuration...")
			_rcc.assert_called_once_with()
			self.assertEqual(pBView.webApp, "webApp")
			self.assertEqual(pBPDF.pdfApp, "pdfApp")
			self.assertEqual(pBPDF.pdfDir,
				os.path.join(os.path.split(
				os.path.abspath(sys.argv[0]))[0],
				"pdf/folder"))
		pbConfig.params["webApplication"] = "webApp"
		pbConfig.params["pdfApplication"] = "pdfApp"
		pbConfig.params["pdfFolder"] = "/pdf/folder"
		with patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "reloadColumnContents") as _rcc:
			self.mainW.reloadConfig()
			_sbm.assert_called_once_with("Reloading configuration...")
			_rcc.assert_called_once_with()
			self.assertEqual(pBView.webApp, "webApp")
			self.assertEqual(pBPDF.pdfApp, "pdfApp")
			self.assertEqual(pBPDF.pdfDir, "/pdf/folder")
		pbConfig.params["webApplication"] = oldWebA
		pbConfig.params["pdfApplication"] = oldPdfA
		pbConfig.params["pdfFolder"] = oldPdfF
		with patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "reloadColumnContents") as _rcc:
			self.mainW.reloadConfig()
		pBPDF.pdfDir = oldPdfD

	def test_showAbout(self):
		"""test showAbout"""
		mbox = self.mainW.showAbout(testing=True)
		self.assertEqual(mbox.windowTitle(), "About PhysBiblio")
		self.assertEqual(mbox.text(),
			"PhysBiblio (<a href='https://github.com/steog88/physBiblio'>"
			+ "https://github.com/steog88/physBiblio</a>) is "
			+ "a cross-platform tool for managing a LaTeX/BibTeX database. "
			+ "It is written in <code>python</code>, "
			+ "using <code>sqlite3</code> for the database management "
			+ "and <code>PySide</code> for the graphical part."
			+ "<br>"
			+ "It supports grouping, tagging, import/export, "
			+ "automatic update and various different other functions."
			+ "<br><br>"
			+ "<b>Paths:</b><br>"
			+ "<i>Configuration:</i> %s<br>"%pbConfig.configPath
			+ "<i>Data:</i> %s<br>"%pbConfig.dataPath
			+ "<br>"
			+ "<b>Author:</b> Stefano Gariazzo "
			+ "<i>&lt;stefano.gariazzo@gmail.com&gt;</i><br>"
			+ "<b>Version:</b> %s (%s)<br>"%(
				physbiblio.__version__, physbiblio.__version_date__)
			+ "<b>Python version</b>: %s"%sys.version)
		self.assertEqual(mbox.textFormat(), Qt.RichText)
		img = QImage(":/images/icon.png").convertToFormat(
			QImage.Format_ARGB32_Premultiplied)
		self.assertEqual(img, mbox.iconPixmap().toImage())

		mb = QMessageBox(QMessageBox.Information, "title", "PhysBiblio")
		mb.exec_ = MagicMock()
		with patch(self.modName + ".QMessageBox", return_value=mb) as _mb:
			self.mainW.showAbout()
			mb.exec_.assert_called_once_with()

	def test_showDBStats(self):
		"""test showDBStats"""
		dbStats(pBDB)
		with patch(self.modName + ".dbStats") as _dbs,\
				patch("glob.iglob", return_value=["a", "b"]) as _ig:
			mbox = self.mainW.showDBStats(testing=True)
			_dbs.assert_called_once_with(pBDB)
			_ig.assert_called_once_with("%s/*/*.pdf"%pBPDF.pdfDir)
		self.assertEqual(mbox.windowTitle(), "PhysBiblio database statistics")
		self.assertEqual(mbox.text(),
			"The PhysBiblio database currently contains "
			+ "the following number of records:\n"
			+ "- %d bibtex entries\n"%(pBDB.stats["bibs"])
			+ "- %d categories\n"%(pBDB.stats["cats"])
			+ "- %d experiments,\n"%(pBDB.stats["exps"])
			+ "- %d bibtex entries to categories connections\n"%(
				pBDB.stats["catBib"])
			+ "- %d experiment to categories connections\n"%(
				pBDB.stats["catExp"])
			+ "- %d bibtex entries to experiment connections.\n\n"%(
				pBDB.stats["bibExp"])
			+ "The number of currently stored PDF files is 2.")
		img = QImage(":/images/icon.png").convertToFormat(
			QImage.Format_ARGB32_Premultiplied)
		self.assertEqual(img, mbox.iconPixmap().toImage())
		self.assertEqual(mbox.parent(), self.mainW)

		mb = QMessageBox(QMessageBox.Information, "title", "PhysBiblio")
		mb.show = MagicMock()
		with patch(self.modName + ".QMessageBox", return_value=mb) as _mb:
			self.mainW.showDBStats()
			mb.show.assert_called_once_with()

	def test_runInThread(self):
		"""test _runInThread"""
		raise NotImplementedError

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
		"""test createStatusBar"""
		with patch(self.modName + ".QStatusBar.showMessage") as _sm:
			self.mainW.createStatusBar()
			_sm.assert_called_once_with('Ready', 0)
			self.assertEqual(self.mainW.statusBar(), self.mainW.mainStatusBar)

	def test_statusBarMessage(self):
		"""test statusBarMessage"""
		with patch(self.modName + ".QStatusBar.showMessage") as _sm,\
				patch("logging.Logger.info") as _i:
			self.mainW.statusBarMessage("abc")
			_i.assert_called_once_with("abc")
			_sm.assert_called_once_with("abc", 4000)
			_sm.reset_mock()
			self.mainW.statusBarMessage("abc", time=2000)
			_sm.assert_called_once_with("abc", 2000)

	def test_save(self):
		"""test save"""
		with patch(self.modName + ".askYesNo",
				side_effect=[True, False]) as _ayn,\
				patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch(self.clsName + ".mainWindowTitle") as _mwt,\
				patch("physbiblio.database.physbiblioDBCore.commit") as _c:
			self.mainW.save()
			_ayn.assert_called_once_with("Do you really want to save?")
			_sbm.assert_called_once_with("Changes saved")
			_mwt.assert_called_once_with("PhysBiblio")
			_c.assert_called_once_with()
			_ayn.reset_mock()
			_sbm.reset_mock()
			_mwt.reset_mock()
			_c.reset_mock()
			self.mainW.save()
			_ayn.assert_called_once_with("Do you really want to save?")
			_sbm.assert_called_once_with("Nothing saved")
			_mwt.assert_not_called()
			_c.assert_not_called()

	def test_importFromBib(self):
		"""test importFromBib"""
		with patch(self.modName + ".askFileName",
				side_effect=["a.bib", ""]) as _afn,\
				patch(self.modName + ".askYesNo", return_value=True) as _ayn,\
				patch(self.clsName + "._runInThread") as _rit,\
				patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch(self.clsName + ".reloadMainContent") as _rmc:
			self.mainW.importFromBib()
			_afn.assert_called_once_with(self.mainW,
				title="From where do you want to import?",
				filter="Bibtex (*.bib)")
			_rit.assert_called_once_with(
				thread_importFromBib,
				"Importing...", "a.bib", True,
				totStr="Entries to be processed: ",
				progrStr="%), processing entry ",
				minProgress=0, stopFlag=True,
				outMessage="All entries into 'a.bib' have been imported")
			_ayn.assert_called_once_with("Do you want to use INSPIRE "
				+ "to find more information about the imported entries?")
			_sbm.assert_called_once_with("File 'a.bib' imported!")
			_rmc.assert_called_once_with()
			_rit.reset_mock()
			_sbm.reset_mock()
			self.mainW.importFromBib()
			_rit.assert_not_called()
			_sbm.assert_called_once_with("Empty filename given!")

	def test_export(self):
		"""test export"""
		with patch(self.modName + ".askSaveFileName",
				side_effect=["a.bib", ""]) as _afn,\
				patch("physbiblio.export.pbExport.exportLast") as _ex,\
				patch(self.clsName + ".statusBarMessage") as _sbm:
			self.mainW.export()
			_afn.assert_called_once_with(self.mainW,
				title="Where do you want to export the entries?",
				filter="Bibtex (*.bib)")
			_ex.assert_called_once_with("a.bib")
			_sbm.assert_called_once_with(
				"Last fetched entries exported into 'a.bib'")
			_ex.reset_mock()
			_sbm.reset_mock()
			self.mainW.export()
			_ex.assert_not_called()
			_sbm.assert_called_once_with("Empty filename given!")

	def test_exportSelection(self):
		"""test exportSelection"""
		with patch(self.modName + ".askSaveFileName",
				side_effect=["a.bib", ""]) as _afn,\
				patch("physbiblio.export.pbExport.exportSelected") as _ex,\
				patch(self.clsName + ".statusBarMessage") as _sbm:
			self.mainW.exportSelection([{"bibkey": "k"}])
			_afn.assert_called_once_with(self.mainW,
				title="Where do you want to export the selected entries?",
				filter="Bibtex (*.bib)")
			_ex.assert_called_once_with("a.bib", [{"bibkey": "k"}])
			_sbm.assert_called_once_with(
				"Current selection exported into 'a.bib'")
			_ex.reset_mock()
			_sbm.reset_mock()
			self.mainW.exportSelection([{"bibkey": "k"}])
			_ex.assert_not_called()
			_sbm.assert_called_once_with("Empty filename given!")

	def test_exportFile(self):
		"""test exportFile"""
		with patch(self.modName + ".askSaveFileName",
				side_effect=["a.bib", "a.bib", ""]) as _asn,\
				patch(self.modName + ".askFileNames",
					side_effect=[["a.tex", "b.tex"], ""]) as _afn,\
				patch(self.clsName + "._runInThread") as _ex,\
				patch(self.clsName + ".statusBarMessage") as _sbm:
			self.mainW.exportFile()
			_asn.assert_called_once_with(self.mainW,
				title="Where do you want to export the entries?",
				filter="Bibtex (*.bib)"),
			_afn.assert_called_once_with(self.mainW,
				title="Which is/are the *.tex file(s) you want to compile?",
				filter="Latex (*.tex)")
			_ex.assert_called_once_with(
					thread_exportTexBib, "Exporting...",
					["a.tex", "b.tex"], "a.bib",
					minProgress=0, stopFlag=True,
					outMessage="All entries saved into 'a.bib'")
			_ex.reset_mock()
			self.mainW.exportFile()
			_ex.assert_not_called()
			_sbm.assert_called_once_with("Empty input filename/folder!")
			_ex.reset_mock()
			_sbm.reset_mock()
			self.mainW.exportFile()
			_ex.assert_not_called()
			_sbm.assert_called_once_with("Empty output filename!")

	def test_exportUpdate(self):
		"""test exportUpdate"""
		with patch(self.modName + ".askSaveFileName",
				side_effect=["a.bib", ""]) as _afn,\
				patch(self.modName + ".askYesNo", return_value="a") as _ayn,\
				patch("physbiblio.export.pbExport.updateExportedBib") as _ex,\
				patch(self.clsName + ".statusBarMessage") as _sbm:
			self.mainW.exportUpdate()
			_afn.assert_called_once_with(self.mainW,
				 title="File to update?",
				filter="Bibtex (*.bib)")
			_ayn.assert_called_once_with(
				"Do you want to overwrite the existing .bib file?",
				"Overwrite")
			_ex.assert_called_once_with("a.bib", overwrite="a")
			_sbm.assert_called_once_with(
				"File 'a.bib' updated")
			_ex.reset_mock()
			_sbm.reset_mock()
			self.mainW.exportUpdate()
			_ex.assert_not_called()
			_sbm.assert_called_once_with("Empty output filename!")

	def test_exportAll(self):
		"""test exportAll"""
		with patch(self.modName + ".askSaveFileName",
				side_effect=["a.bib", ""]) as _afn,\
				patch("physbiblio.export.pbExport.exportAll") as _ex,\
				patch(self.clsName + ".statusBarMessage") as _sbm:
			self.mainW.exportAll()
			_afn.assert_called_once_with(self.mainW,
				title="Where do you want to export the entries?",
				filter="Bibtex (*.bib)")
			_ex.assert_called_once_with("a.bib")
			_sbm.assert_called_once_with(
				"All entries saved into 'a.bib'")
			_ex.reset_mock()
			_sbm.reset_mock()
			self.mainW.exportAll()
			_ex.assert_not_called()
			_sbm.assert_called_once_with("Empty output filename!")

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
		"""test searchBiblio"""
		raise NotImplementedError

	def test_runSearchBiblio(self):
		"""test runSearchBiblio"""
		pBDB.lastFetched = []
		with patch("PySide2.QtWidgets.QApplication."
				+ "setOverrideCursor") as _soc,\
				patch("PySide2.QtWidgets.QApplication."
					+ "restoreOverrideCursor") as _roc,\
				patch("physbiblio.database.entries.fetchFromDict",
					return_value=pBDB) as _ffd,\
				patch(self.clsName + ".reloadMainContent") as _rmc:
			self.mainW.runSearchBiblio({"s": "a"}, 12, 34)
			_soc.assert_called_once_with(Qt.WaitCursor)
			_roc.assert_called_once_with()
			_ffd.assert_has_calls([
				call({"s": "a"}, limitOffset=34),
				call({"s": "a"}, limitOffset=34, limitTo=12)])
			_rmc.assert_called_once_with([])

		pBDB.lastFetched = ["a"]
		self.lastFetched = ["a", "b"]
		with patch("PySide2.QtWidgets.QApplication."
				+ "setOverrideCursor") as _soc,\
				patch("PySide2.QtWidgets.QApplication."
					+ "restoreOverrideCursor") as _roc,\
				patch("physbiblio.database.entries.fetchFromDict",
					side_effect=[self, pBDB]) as _ffd,\
				patch(self.clsName + ".reloadMainContent") as _rmc,\
				patch(self.modName + ".infoMessage") as _im:
			self.mainW.runSearchBiblio({"s": "a"}, 12, 34)
			_soc.assert_called_once_with(Qt.WaitCursor)
			_roc.assert_called_once_with()
			_ffd.assert_has_calls([
				call({"s": "a"}, limitOffset=34),
				call({"s": "a"}, limitOffset=34, limitTo=12)])
			_rmc.assert_called_once_with(["a"])
			_im.assert_called_once_with(
				"Warning: more entries match the current search, "
				+ "showing only the first 1 of 2.\nChange "
				+ "'Max number of results' in the search form to see more.")

	def test_runSearchReplaceBiblio(self):
		"""test runSearchReplaceBiblio"""
		pBDB.lastFetched = ["a"]
		with patch("physbiblio.database.entries.fetchFromDict",
					return_value=pBDB) as _ffd,\
				patch(self.clsName + ".runReplace") as _rr:
			self.mainW.runSearchReplaceBiblio({"s": "a"}, ["b"], 12)
			_ffd.assert_called_once_with({'s': 'a'}, limitOffset=12)
			_rr.assert_called_once_with(["b"])

	def test_delSearchBiblio(self):
		"""test delSearchBiblio"""
		pBDB.lastFetched = ["a"]
		with patch("physbiblio.config.globalDB.deleteSearch") as _ds,\
				patch(self.clsName + ".createMenusAndToolBar") as _cm,\
				patch(self.modName + ".askYesNo") as _ay:
			self.mainW.delSearchBiblio(999, "search")
			_ay.assert_called_once_with("Are you sure you want to delete "
				+ "the saved search 'search'?")
			_cm.assert_called_once_with()
			_ds.assert_called_once_with(999)

	def test_searchAndReplace(self):
		"""test searchAndReplace"""
		with patch(self.clsName + ".searchBiblio",
				side_effect=[False, "a"]) as _sb,\
				patch(self.clsName + ".runReplace") as _rr:
			self.mainW.searchAndReplace()
			_sb.assert_called_once_with(replace=True)
			_rr.assert_not_called()
			self.mainW.searchAndReplace()
			_rr.assert_called_once_with("a")

	def test_runReplace(self):
		"""test runReplace"""
		pBDB.lastFetched = ["z"]
		with patch("PySide2.QtWidgets.QApplication."
				+ "setOverrideCursor") as _soc,\
				patch("PySide2.QtWidgets.QApplication."
					+ "restoreOverrideCursor") as _roc,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB) as _ffl,\
				patch("physbiblio.database.entries.replace",
					return_value=[["d"], ["e", "f"], ["g", "h", "i"]]) as _r,\
				patch("physbiblio.database.entries.fetchCursor",
					return_value="c") as _fc,\
				patch(self.clsName + ".reloadMainContent") as _rmc,\
				patch(self.modName + ".infoMessage") as _im,\
				patch(self.modName + ".longInfoMessage") as _lim,\
				patch(self.modName + ".askYesNo",
					side_effect=[False, True]) as _ay:
			self.mainW.runReplace(("bibtex", "bibkey", "", ["a"], "r"))
			_soc.assert_not_called()
			_r.assert_not_called()
			_im.assert_called_once_with("The string to substitute is empty!")
			_im.reset_mock()

			self.mainW.runReplace(("bibtex", "bibkey", "o", ["a", ""], "r"))
			_soc.assert_not_called()
			_r.assert_not_called()
			_ay.assert_called_once_with("Empty new string. "
				+ "Are you sure you want to continue?")
			_ay.reset_mock()

			self.mainW.runReplace(("bibtex", "bibkey", "o", ["a", ""], "r"))
			_soc.assert_has_calls([call(Qt.WaitCursor), call(Qt.WaitCursor)])
			_roc.assert_has_calls([call(), call()])
			_ay.assert_called_once_with("Empty new string. "
				+ "Are you sure you want to continue?")
			_rmc.assert_called_once_with(["z"])
			_im.assert_not_called()
			_ay.assert_called_once_with("Empty new string. "
				+ "Are you sure you want to continue?")
			_r.assert_called_once_with(
				'bibtex', 'bibkey', 'o', ['a', ''], entries='c', regex='r')
			_fc.assert_called_once_with()
			_ffl.assert_called_once_with()
			_lim.assert_called_once_with(
				"Replace completed.<br><br>"
				+ "1 elements successfully processed"
				+ " (of which 2 changed), "
				+ "3 failures (see below).<br><br>"
				+ "<b>Changed</b>: ['e', 'f']<br><br>"
				+ "<b>Failed</b>: ['g', 'h', 'i']")

	def test_updateAllBibtexsAsk(self):
		"""test updateAllBibtexsAsk"""
		with patch(self.modName + ".askYesNo", return_value=False) as _ay,\
				patch(self.modName + ".askGenericText",
					return_value=["a", False]) as _agt,\
				patch(self.clsName + ".updateAllBibtexs") as _uab:
			self.assertEqual(self.mainW.updateAllBibtexsAsk(), None)
			_uab.assert_not_called()

		with patch(self.modName + ".askYesNo", return_value=False) as _ay,\
				patch(self.modName + ".askGenericText",
					return_value=["a", True]) as _agt,\
				patch(self.clsName + ".updateAllBibtexs") as _uab:
			self.assertEqual(self.mainW.updateAllBibtexsAsk(), None)
			_uab.assert_not_called()

		with patch(self.modName + ".askYesNo", return_value=True) as _ay,\
				patch(self.modName + ".askGenericText",
					return_value=["a", True]) as _agt,\
				patch(self.clsName + ".updateAllBibtexs") as _uab:
			self.assertEqual(self.mainW.updateAllBibtexsAsk(), None)
			_ay.assert_any_call("The text you inserted is not an integer. "
				+ "I will start from 0.\nDo you want to continue?",
				"Invalid entry")
			_uab.assert_called_once_with(0, force=True)

		with patch(self.modName + ".askYesNo", return_value=False) as _ay,\
				patch(self.modName + ".askGenericText",
					return_value=["12", True]) as _agt,\
				patch(self.clsName + ".updateAllBibtexs") as _uab:
			self.assertEqual(self.mainW.updateAllBibtexsAsk(), None)
			_ay.assert_called_once_with(
				"Do you want to force the update of already existing "
				+ "items?\n(Only regular articles not explicitely "
				+ "excluded will be considered)", 'Force update:')
			_agt.assert_called_once_with(
				"Insert the ordinal number of the bibtex element from "
				+ "which you want to start the updates:",
				'Where do you want to start searchOAIUpdates from?',
				self.mainW)
			_uab.assert_called_once_with(12, force=False)

	def test_updateAllBibtexs(self):
		"""test updateAllBibtexs"""
		with patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch(self.clsName + "._runInThread") as _rit,\
				patch(self.clsName + ".refreshMainContent") as _rmc:
			self.mainW.updateAllBibtexs()
			_sbm.assert_called_once_with(
				"Starting update of bibtexs from %s..."%(
					pbConfig.params["defaultUpdateFrom"]))
			_rit.assert_called_once_with(thread_updateAllBibtexs,
				'Update Bibtexs', pbConfig.params["defaultUpdateFrom"],
				force=False, minProgress=0.0,
				progrStr='%) - looking for update: ', reloadAll=False,
				stopFlag=True, totStr='SearchOAIUpdates will process ',
				useEntries=None)
			_rmc.assert_called_once_with()
		with patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch(self.clsName + "._runInThread") as _rit,\
				patch(self.clsName + ".refreshMainContent") as _rmc:
			self.mainW.updateAllBibtexs(startFrom=12,
				useEntries="abc",
				force=True,
				reloadAll=True)
			_sbm.assert_called_once_with(
				"Starting update of bibtexs from 12...")
			_rit.assert_called_once_with(thread_updateAllBibtexs,
				'Update Bibtexs', 12, force=True, minProgress=0.0,
				progrStr='%) - looking for update: ', reloadAll=True,
				stopFlag=True, totStr='SearchOAIUpdates will process ',
				useEntries="abc")
			_rmc.assert_called_once_with()

	def test_updateInspireInfo(self):
		"""test updateInspireInfo"""
		with patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch(self.clsName + "._runInThread") as _rit,\
				patch(self.clsName + ".refreshMainContent") as _rmc:
			self.mainW.updateInspireInfo("key")
			_sbm.assert_called_once_with(
				"Starting generic info update from INSPIRE-HEP...")
			_rit.assert_called_once_with(thread_updateInspireInfo,
				"Update Info", "key", None, minProgress=0., stopFlag=False)
			_rmc.assert_called_once_with()
		with patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch(self.clsName + "._runInThread") as _rit,\
				patch(self.clsName + ".refreshMainContent") as _rmc:
			self.mainW.updateInspireInfo("key", inspireID="1234")
			_sbm.assert_called_once_with(
				"Starting generic info update from INSPIRE-HEP...")
			_rit.assert_called_once_with(thread_updateInspireInfo,
				"Update Info", "key", "1234", minProgress=0., stopFlag=False)
			_rmc.assert_called_once_with()

	def test_authorStats(self):
		"""test authorStats"""
		raise NotImplementedError

	def test_getInspireStats(self):
		"""test getInspireStats"""
		raise NotImplementedError

	def test_inspireLoadAndInsert(self):
		"""test inspireLoadAndInsert"""
		raise NotImplementedError

	def test_askCatsForEntries(self):
		"""test askCatsForEntries"""
		raise NotImplementedError

	def test_inspireLoadAndInsertWithCats(self):
		"""test inspireLoadAndInsertWithCats"""
		self.mainW.loadedAndInserted = []
		with patch(self.clsName + ".inspireLoadAndInsert",
				return_value=False) as _ili,\
				patch(self.clsName + ".askCatsForEntries") as _ace,\
				patch(self.clsName + ".reloadMainContent") as _rmc,\
				patch("physbiblio.database.catsEntries.delete") as _d:
			self.mainW.inspireLoadAndInsertWithCats()
			_ili.assert_called_once_with(doReload=False)
			_d.assert_not_called()
			_ace.assert_not_called()
			_rmc.assert_not_called()
		with patch(self.clsName + ".inspireLoadAndInsert",
				return_value=True) as _ili,\
				patch(self.clsName + ".askCatsForEntries") as _ace,\
				patch(self.clsName + ".reloadMainContent") as _rmc,\
				patch("physbiblio.database.catsEntries.delete") as _d:
			self.mainW.inspireLoadAndInsertWithCats()
			_ili.assert_called_once_with(doReload=False)
			_d.assert_not_called()
			_ace.assert_not_called()
			_rmc.assert_not_called()

		self.mainW.loadedAndInserted = ["a", "b"]
		with patch(self.clsName + ".inspireLoadAndInsert",
				return_value=True) as _ili,\
				patch(self.clsName + ".askCatsForEntries") as _ace,\
				patch(self.clsName + ".reloadMainContent") as _rmc,\
				patch("physbiblio.database.catsEntries.delete") as _d:
			self.mainW.inspireLoadAndInsertWithCats()
			_ili.assert_called_once_with(doReload=False)
			_d.assert_has_calls([
				call(pbConfig.params["defaultCategories"], "a"),
				call(pbConfig.params["defaultCategories"], "b")])
			_ace.assert_called_once_with(["a", "b"])
			_rmc.assert_called_once_with()

	def test_advancedImport(self):
		"""test advancedImport"""
		raise NotImplementedError

	def test_cleanAllBibtexsAsk(self):
		"""test cleanAllBibtexsAsk"""
		with patch(self.modName + ".askGenericText",
					return_value=["a", False]) as _agt,\
				patch(self.clsName + ".cleanAllBibtexs") as _cab:
			self.assertEqual(self.mainW.cleanAllBibtexsAsk(), None)
			_agt.assert_called_once_with(
				"Insert the ordinal number of "
				+ "the bibtex element from which you want to start "
				+ "the cleaning:",
				"Where do you want to start cleanBibtexs from?",
				self.mainW)
			_cab.assert_not_called()

		with patch(self.modName + ".askYesNo", return_value=False) as _ay,\
				patch(self.modName + ".askGenericText",
					return_value=["a", True]) as _agt,\
				patch(self.clsName + ".cleanAllBibtexs") as _cab:
			self.assertEqual(self.mainW.cleanAllBibtexsAsk(), None)
			_agt.assert_called_once_with(
				"Insert the ordinal number of "
				+ "the bibtex element from which you want to start "
				+ "the cleaning:",
				"Where do you want to start cleanBibtexs from?",
				self.mainW)
			_ay.assert_called_once_with(
				"The text you inserted is not an integer. "
				+ "I will start from 0.\nDo you want to continue?",
				"Invalid entry")
			_cab.assert_not_called()

		with patch(self.modName + ".askYesNo", return_value=True) as _ay,\
				patch(self.modName + ".askGenericText",
					return_value=["a", True]) as _agt,\
				patch(self.clsName + ".cleanAllBibtexs") as _cab:
			self.assertEqual(self.mainW.cleanAllBibtexsAsk(), None)
			_agt.assert_called_once_with(
				"Insert the ordinal number of "
				+ "the bibtex element from which you want to start "
				+ "the cleaning:",
				"Where do you want to start cleanBibtexs from?",
				self.mainW)
			_ay.assert_called_once_with(
				"The text you inserted is not an integer. "
				+ "I will start from 0.\nDo you want to continue?",
				"Invalid entry")
			_cab.assert_called_once_with(0)

		with patch(self.modName + ".askYesNo", return_value=True) as _ay,\
				patch(self.modName + ".askGenericText",
					return_value=["12", True]) as _agt,\
				patch(self.clsName + ".cleanAllBibtexs") as _cab:
			self.assertEqual(self.mainW.cleanAllBibtexsAsk(), None)
			_agt.assert_called_once_with(
				"Insert the ordinal number of "
				+ "the bibtex element from which you want to start "
				+ "the cleaning:",
				"Where do you want to start cleanBibtexs from?",
				self.mainW)
			_ay.assert_not_called()
			_cab.assert_called_once_with(12)

	def test_cleanAllBibtexs(self):
		"""test cleanAllBibtexs"""
		with patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch(self.clsName + "._runInThread") as _rit:
			self.mainW.cleanAllBibtexs()
			_sbm.assert_called_once_with(
				"Starting cleaning of bibtexs...")
			_rit.assert_called_once_with(thread_cleanAllBibtexs,
				'Clean Bibtexs', 0, minProgress=0.0,
				progrStr='%) - cleaning: ', stopFlag=True,
				totStr='CleanBibtexs will process ', useEntries=None)
		with patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch(self.clsName + "._runInThread") as _rit,\
				patch(self.clsName + ".refreshMainContent") as _rmc:
			self.mainW.cleanAllBibtexs(startFrom=12, useEntries=["a"])
			_sbm.assert_called_once_with(
				"Starting cleaning of bibtexs...")
			_rit.assert_called_once_with(thread_cleanAllBibtexs,
				'Clean Bibtexs', 12, minProgress=0.0,
				progrStr='%) - cleaning: ', stopFlag=True,
				totStr='CleanBibtexs will process ', useEntries=["a"])

	def test_findBadBibtexs(self):
		"""test findBadBibtexs"""
		mainW = MainWindow(testing=True)
		def patcher(*args, **kwargs):
			mainW.badBibtexs = ["a", "b"]
		with patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch(self.clsName + "._runInThread") as _rit,\
				patch(self.modName + ".infoMessage") as _im:
			self.mainW.findBadBibtexs()
			_sbm.assert_called_once_with("Starting checking bibtexs...")
			_rit.assert_called_once_with(
				thread_findBadBibtexs, "Check Bibtexs",
				0, useEntries=None,
				totStr="findCorruptedBibtexs will process ",
				progrStr="%) - processing: ",
				minProgress=0., stopFlag=True)
			_im.assert_called_once_with("No invalid records found!")
		with patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch(self.clsName + "._runInThread") as _rit,\
				patch(self.modName + ".infoMessage") as _im:
			self.mainW.findBadBibtexs(startFrom=12, useEntries=["abc"])
			_sbm.assert_called_once_with("Starting checking bibtexs...")
			_rit.assert_called_once_with(
				thread_findBadBibtexs, "Check Bibtexs",
				12, useEntries=["abc"],
				totStr="findCorruptedBibtexs will process ",
				progrStr="%) - processing: ",
				minProgress=0., stopFlag=True)
			_im.assert_called_once_with("No invalid records found!")

		mainW._runInThread = patcher
		with patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch(self.modName + ".askYesNo", return_value=False) as _ay,\
				patch(self.modName + ".infoMessage") as _im,\
				patch(self.modName + ".editBibtex") as _eb:
			mainW.findBadBibtexs()
			_im.assert_called_once_with(
				"These are the bibtex keys corresponding to invalid"
				+ " records:\na, b\n\nNo action will be performed.")
			_eb.assert_not_called()
		with patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch(self.modName + ".askYesNo", return_value=True) as _ay,\
				patch(self.modName + ".editBibtex") as _eb:
			mainW.findBadBibtexs()
			_eb.assert_has_calls([call(mainW, "a"), call(mainW, "b")])

	def test_infoFromArxiv(self):
		"""test infoFromArxiv"""
		ffa = FieldsFromArxiv()
		ffa.output = ["title"]
		ffa.exec_ = MagicMock()
		ffa.result = False
		with patch(self.modName + ".FieldsFromArxiv",
				return_value=ffa) as _ffa,\
				patch("physbiblio.database.entries.fetchAll") as _fa,\
				patch("physbiblio.database.entries.fetchCursor",
					return_value=[{"bibkey": "a"}]) as _fc,\
				patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch(self.clsName + "._runInThread") as _rit:
			self.mainW.infoFromArxiv()
			_ffa.assert_called_once_with()
			ffa.exec_.assert_called_once_with()
			_fa.assert_called_once_with(doFetch=False)
			_fc.assert_called_once_with()
			_sbm.assert_not_called()
			_rit.assert_not_called()

		ffa.result = True
		with patch(self.modName + ".FieldsFromArxiv",
				return_value=ffa) as _ffa,\
				patch("physbiblio.database.entries.fetchAll") as _fa,\
				patch("physbiblio.database.entries.fetchCursor",
					return_value=[{"bibkey": "a"}]) as _fc,\
				patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch(self.clsName + "._runInThread") as _rit:
			self.mainW.infoFromArxiv()
			_ffa.assert_called_once_with()
			_fa.assert_called_once_with(doFetch=False)
			_fc.assert_called_once_with()
			_sbm.assert_called_once_with(
				"Starting importing info from arxiv...")
			_rit.assert_called_once_with(thread_fieldsArxiv,
				'Get info from arXiv', ['a'], ['title'], minProgress=0.0,
				progrStr='%) - processing: arxiv:', stopFlag=True,
				totStr='Thread_fieldsArxiv will process ')
		with patch(self.modName + ".FieldsFromArxiv",
				return_value=ffa) as _ffa,\
				patch("physbiblio.database.entries.fetchAll") as _fa,\
				patch("physbiblio.database.entries.fetchCursor",
					return_value=[{"bibkey": "a"}]) as _fc,\
				patch(self.clsName + ".statusBarMessage") as _sbm,\
				patch(self.clsName + "._runInThread") as _rit:
			self.mainW.infoFromArxiv(
				useEntries=[{"bibkey": "a"}, {"bibkey": "b"}])
			_ffa.assert_called_once_with()
			_fa.assert_not_called()
			_fc.assert_not_called()
			_sbm.assert_called_once_with(
				"Starting importing info from arxiv...")
			_rit.assert_called_once_with(thread_fieldsArxiv,
				'Get info from arXiv', ['a', 'b'], ['title'], minProgress=0.0,
				progrStr='%) - processing: arxiv:', stopFlag=True,
				totStr='Thread_fieldsArxiv will process ')

	def test_browseDailyArxiv(self):
		"""test browseDailyArxiv"""
		raise NotImplementedError

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
