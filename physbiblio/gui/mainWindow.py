"""Module that contains the class for the main window of PhysBiblio.

This file is part of the physbiblio package.
"""
import sys
import traceback
import os
import six
import signal
import ast
import glob
import bibtexparser
if sys.version_info[0] < 3:
	from Queue import Queue
else:
	from queue import Queue

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import \
	QAction, QApplication, QDesktopWidget, QFrame, QMainWindow, \
	QMessageBox, QSplitter, QStatusBar

try:
	from physbiblio.errors import pBErrorManager, pBLogger
	from physbiblio.database import pBDB, dbStats
	from physbiblio.export import pBExport
	from physbiblio.webimport.webInterf import physBiblioWeb
	from physbiblio.config import pbConfig
	from physbiblio.pdf import pBPDF
	from physbiblio.view import pBView
	from physbiblio.bibtexWriter import pbWriter
	from physbiblio.inspireStats import pBStats
	from physbiblio.gui.errorManager import pBGUILogger
	from physbiblio.gui.basicDialogs import \
		askFileName, askFileNames, askGenericText, askSaveFileName, \
		askYesNo, infoMessage, LongInfoMessage
	from physbiblio.gui.commonClasses import \
		ObjectWithSignal, PBComboBox, WriteStream
	from physbiblio.gui.bibWindows import \
		AbstractFormulas, FieldsFromArxiv, SearchBibsWindow, editBibtex, \
		BibtexListWindow, BibtexInfo
	from physbiblio.gui.catWindows import CatsTreeWindow, editCategory
	from physbiblio.gui.dialogWindows import \
		ConfigWindow, LogFileContentDialog, PrintText, AdvancedImportDialog, \
		AdvancedImportSelect, DailyArxivDialog, DailyArxivSelect
	from physbiblio.gui.expWindows import \
		editExperiment, ExpsListWindow, EditExperimentDialog
	from physbiblio.gui.inspireStatsGUI import \
		AuthorStatsPlots, PaperStatsPlots
	from physbiblio.gui.profilesManager import SelectProfiles, editProfile
	from physbiblio.gui.threadElements import \
		Thread_authorStats, Thread_cleanSpare, Thread_cleanSparePDF, \
		Thread_updateAllBibtexs, Thread_exportTexBib, Thread_importFromBib, \
		Thread_updateInspireInfo, Thread_paperStats, Thread_loadAndInsert, \
		Thread_cleanAllBibtexs, Thread_findBadBibtexs, Thread_fieldsArxiv, \
		Thread_checkUpdated, Thread_replace, Thread_importDailyArxiv
except ImportError as e:
	print("Could not find physbiblio and its modules!", e)
	print(traceback.format_exc())
try:
	import physbiblio.gui.resourcesPyside2
except ImportError as e:
	print("Missing Resources_pyside2: run script update_resources.sh", e)


class MainWindow(QMainWindow):
	"""This is the class that manages the main window of the PhysBiblio
	graphical interface
	"""

	def __init__(self, testing=False):
		"""Main window constructor.
		Call many functions to set all the widgets and the properties

		Parameter:
			testing (default False): if True, return without
				executing all the creation of objects (used for tests)
		"""
		QMainWindow.__init__(self)
		availableWidth = QDesktopWidget().availableGeometry().width()
		availableHeight = QDesktopWidget().availableGeometry().height()
		self.setWindowTitle('PhysBiblio')
		#x,y of topleft corner, width, height
		self.setGeometry(0, 0, availableWidth, availableHeight)
		self.setMinimumHeight(400)
		self.setMinimumWidth(600)
		self.mainStatusBar = QStatusBar()
		self.lastAuthorStats = None
		self.lastPaperStats = None
		if testing:
			return
		self.createActions()
		self.createMenusAndToolBar()
		self.createMainLayout()
		self.setIcon()
		self.createStatusBar()

		# When the DB is locked, ask if the user wants to close the PB instance
		self.onIsLockedClass = ObjectWithSignal()
		pBDB.onIsLocked = self.onIsLockedClass.customSignal
		pBDB.onIsLocked.connect(self.lockedDatabase)

		# Catch Ctrl+C in shell
		signal.signal(signal.SIGINT, signal.SIG_DFL)

		self.checkUpdated = Thread_checkUpdated(self)
		self.checkUpdated.finished.connect(self.checkUpdated.deleteLater)
		self.checkUpdated.result.connect(self.printNewVersion)
		self.checkUpdated.start()

	def closeEvent(self, event):
		"""Intercept close events. If uncommitted changes exist,
		ask before closing the application

		Parameter:
			event: a QEvent
		"""
		if pBDB.checkUncommitted():
			if not askYesNo("There may be unsaved changes to the database.\n"
					+ "Do you really want to exit?"):
				event.ignore()
			else:
				event.accept()
		elif pbConfig.params["askBeforeExit"] and not askYesNo(
				"Do you really want to exit?"):
			event.ignore()
		else:
			event.accept()

	def mainWindowTitle(self, title):
		"""Set the window title

		Parameter:
			title: the window title
		"""
		self.setWindowTitle(title)

	def printNewVersion(self, outdated, newVersion):
		"""Open a warning notifying the existence of a new version,
		if present, or just save an info in the log

		Parameters:
			outdated: boolean, tells if there is a new version available
				in the PyPI repositories for update
			newVersion: the number of the new version or an empty string
		"""
		if outdated:
			pBGUILogger.warning("New version available (%s)!\n"%newVersion
				+ "You can upgrade with `pip install -U physbiblio` "
				+ "(with `sudo`, eventually).")
		else:
			pBLogger.info("No new versions available!")

	def lockedDatabase(self):
		"""Action to be performed when the database is locked
		by another instance of the program.
		Ask what to do and close the main window.
		"""
		if askYesNo("The database is locked.\n"
				+ "Probably another instance of the program is"
				+ " currently open and you cannot save your changes.\n"
				+ "For this reason, the current instance "
				+ "may not work properly.\n"
				+ "Do you want to close this instance of PhysBiblio?",
				title="Attention!"):
			raise SystemExit

	def setIcon(self):
		"""Set the icon of the main window"""
		appIcon = QIcon(':/images/icon.png')
		self.setWindowIcon(appIcon)

	def createActions(self):
		"""Create the QActions used in menu and in the toolbar."""
		self.exitAct = QAction(QIcon(":/images/application-exit.png"),
			"E&xit", self,
			shortcut="Ctrl+Q",
			statusTip="Exit application",
			triggered=self.close)

		self.profilesAct = QAction(QIcon(":/images/profiles.png"),
			"&Profiles", self,
			shortcut="Ctrl+P",
			statusTip="Manage profiles",
			triggered=self.manageProfiles)

		self.editProfileWindowsAct = QAction(
			"&Edit profiles", self,
			shortcut="Ctrl+Alt+P",
			statusTip="Edit profiles",
			triggered=self.editProfile)

		self.undoAct = QAction(QIcon(":/images/edit-undo.png"),
			"&Undo", self,
			shortcut="Ctrl+Z",
			statusTip="Rollback to last saved database state",
			triggered=self.undoDB)

		self.saveAct = QAction(QIcon(":/images/file-save.png"),
			"&Save database", self,
			shortcut="Ctrl+S",
			statusTip="Save the modifications",
			triggered=self.save)

		self.importBibAct = QAction("&Import from *.bib", self,
			shortcut="Ctrl+B",
			statusTip="Import the entries from a *.bib file",
			triggered=self.importFromBib)

		self.exportAct = QAction(QIcon(":/images/export.png"),
			"Ex&port last as *.bib", self,
			statusTip="Export last query as *.bib",
			triggered=self.export)
				
		self.exportAllAct = QAction(QIcon(":/images/export-table.png"),
			"Export &all as *.bib", self,
			shortcut="Ctrl+A",
			statusTip="Export complete bibliography as *.bib",
			triggered=self.exportAll)

		self.exportFileAct = QAction(
			"Export for a *.&tex", self,
			shortcut="Ctrl+X",
			statusTip="Export as *.bib the bibliography needed "
				+ "to compile a .tex file",
			triggered=self.exportFile)

		self.exportUpdateAct = QAction(
			"Update an existing *.&bib file", self,
			shortcut="Ctrl+Shift+X",
			statusTip="Read a *.bib file and update "
				+ "the existing elements inside it",
			triggered=self.exportUpdate)

		self.catAct = QAction("&Categories", self,
			shortcut="Ctrl+T",
			statusTip="Manage Categories",
			triggered=self.categories)

		self.newCatAct = QAction("Ne&w Category", self,
			shortcut="Ctrl+Shift+T",
			statusTip="New Category",
			triggered=self.newCategory)

		self.expAct = QAction("&Experiments", self,
			shortcut="Ctrl+E",
			statusTip="List of Experiments",
			triggered=self.experiments)

		self.newExpAct = QAction("&New Experiment", self,
			shortcut="Ctrl+Shift+E",
			statusTip="New Experiment",
			triggered=self.newExperiment)

		self.searchBibAct = QAction(QIcon(":/images/find.png"),
			"&Find Bibtex entries", self,
			shortcut="Ctrl+F",
			statusTip="Open the search dialog to filter the bibtex list",
			triggered=self.searchBiblio)

		self.searchReplaceAct = QAction(
			QIcon(":/images/edit-find-replace.png"),
			"&Search and replace bibtexs", self,
			shortcut="Ctrl+H",
			statusTip="Open the search&replace dialog",
			triggered=self.searchAndReplace)

		self.newBibAct = QAction(QIcon(":/images/file-add.png"),
			"New &Bib item", self,
			shortcut="Ctrl+N",
			statusTip="New bibliographic item",
			triggered=self.newBibtex)

		self.inspireLoadAndInsertAct = QAction("&Load from INSPIRE-HEP", self,
			shortcut="Ctrl+Shift+I",
			statusTip="Use INSPIRE-HEP to load and insert bibtex entries",
			triggered=self.inspireLoadAndInsert)

		self.inspireLoadAndInsertWithCatsAct = QAction(
			"&Load from INSPIRE-HEP (ask categories)", self,
			shortcut="Ctrl+I",
			statusTip="Use INSPIRE-HEP to load and insert bibtex entries, "
				+ "then ask the categories for each",
			triggered=self.inspireLoadAndInsertWithCats)

		self.advImportAct = QAction("&Advanced Import", self,
			shortcut="Ctrl+Alt+I",
			statusTip="Open the advanced import window",
			triggered=self.advancedImport)

		self.updateAllBibtexsAct = QAction("&Update bibtexs", self,
			shortcut="Ctrl+U",
			statusTip="Update all the journal info of bibtexs",
			triggered=self.updateAllBibtexs)

		self.updateAllBibtexsAskAct = QAction(
			"Update bibtexs (&personalized)", self,
			shortcut="Ctrl+Shift+U",
			statusTip="Update all the journal info of bibtexs, "
				+ "but with non-standard options (start from, force, ...)",
			triggered=self.updateAllBibtexsAsk)

		self.cleanAllBibtexsAct = QAction("&Clean bibtexs", self,
			shortcut="Ctrl+L",
			statusTip="Clean all the bibtexs",
			triggered=self.cleanAllBibtexs)

		self.findBadBibtexsAct = QAction("&Find corrupted bibtexs", self,
			shortcut="Ctrl+Shift+B",
			statusTip="Find all the bibtexs which contain syntax errors "
				+ "and are not readable",
			triggered=self.findBadBibtexs)

		self.infoFromArxivAct = QAction("Info from ar&Xiv", self,
			shortcut="Ctrl+V",
			statusTip="Get info from arXiv",
			triggered=self.infoFromArxiv)

		self.dailyArxivAct = QAction("Browse last ar&Xiv listings", self,
			shortcut="Ctrl+D",
			statusTip="Browse most recent arXiv listings",
			triggered=self.browseDailyArxiv)

		self.cleanAllBibtexsAskAct = QAction(
			"C&lean bibtexs (from ...)", self,
			shortcut="Ctrl+Shift+L",
			statusTip="Clean all the bibtexs, starting from a given one",
			triggered=self.cleanAllBibtexsAsk)

		self.authorStatsAct = QAction("&AuthorStats", self,
			shortcut="Ctrl+Shift+A",
			statusTip="Search publication and citation stats "
				+ "of an author from INSPIRES",
			triggered=self.authorStats)

		self.configAct = QAction(QIcon(":/images/settings.png"),
			"Settin&gs", self,
			shortcut="Ctrl+Shift+S",
			statusTip="Save the settings",
			triggered=self.config)

		self.refreshAct = QAction(QIcon(":/images/refresh2.png"),
			"&Refresh current entries list", self,
			shortcut="F5",
			statusTip="Refresh the current list of entries",
			triggered=self.refreshMainContent)

		self.reloadAct = QAction(QIcon(":/images/refresh.png"),
			"&Reload (reset) main table", self,
			shortcut="Shift+F5",
			statusTip="Reload the list of bibtex entries",
			triggered=self.reloadMainContent)

		self.aboutAct = QAction(QIcon(":/images/help-about.png"),
			"&About", self,
			statusTip="Show About box",
			triggered=self.showAbout)

		self.logfileAct = QAction(
			"Log file", self,
			shortcut="Ctrl+G",
			statusTip="Show the content of the logfile",
			triggered=self.logfile)

		self.dbstatsAct = QAction(QIcon(":/images/stats.png"),
			"&Database info", self,
			statusTip="Show some statistics about the current database",
			triggered=self.showDBStats)

		self.cleanSpareAct = QAction(
			"&Clean spare entries", self,
			statusTip="Remove spare entries from the connection tables.",
			triggered=self.cleanSpare)

		self.cleanSparePDFAct = QAction(
			"&Clean spare PDF folders", self,
			statusTip="Remove spare PDF folders.",
			triggered=self.cleanSparePDF)

	def createMenusAndToolBar(self):
		"""Set the content of the menus and of the toolbar."""
		self.fileMenu = self.menuBar().clear()
		self.fileMenu = self.menuBar().addMenu("&File")
		self.fileMenu.addAction(self.undoAct)
		self.fileMenu.addAction(self.saveAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exportAct)
		self.fileMenu.addAction(self.exportFileAct)
		self.fileMenu.addAction(self.exportAllAct)
		self.fileMenu.addAction(self.exportUpdateAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.profilesAct)
		self.fileMenu.addAction(self.editProfileWindowsAct)
		self.fileMenu.addAction(self.configAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exitAct)

		self.bibMenu = self.menuBar().addMenu("&Bibliography")
		self.bibMenu.addAction(self.newBibAct)
		self.bibMenu.addAction(self.importBibAct)
		self.bibMenu.addAction(self.inspireLoadAndInsertWithCatsAct)
		self.bibMenu.addAction(self.inspireLoadAndInsertAct)
		self.bibMenu.addAction(self.advImportAct)
		self.bibMenu.addSeparator()
		self.bibMenu.addAction(self.cleanAllBibtexsAct)
		self.bibMenu.addAction(self.cleanAllBibtexsAskAct)
		self.bibMenu.addAction(self.findBadBibtexsAct)
		self.bibMenu.addSeparator()
		self.bibMenu.addAction(self.infoFromArxivAct)
		self.bibMenu.addAction(self.updateAllBibtexsAct)
		self.bibMenu.addAction(self.updateAllBibtexsAskAct)
		self.bibMenu.addSeparator()
		self.bibMenu.addAction(self.searchBibAct)
		self.bibMenu.addAction(self.searchReplaceAct)
		self.bibMenu.addSeparator()
		self.bibMenu.addAction(self.refreshAct)
		self.bibMenu.addAction(self.reloadAct)

		self.catMenu = self.menuBar().addMenu("&Categories")
		self.catMenu.addAction(self.catAct)
		self.catMenu.addAction(self.newCatAct)

		self.expMenu = self.menuBar().addMenu("&Experiments")
		self.expMenu.addAction(self.expAct)
		self.expMenu.addAction(self.newExpAct)

		self.toolMenu = self.menuBar().addMenu("&Tools")
		self.toolMenu.addAction(self.dailyArxivAct)
		self.toolMenu.addSeparator()
		self.toolMenu.addAction(self.cleanSpareAct)
		self.toolMenu.addAction(self.cleanSparePDFAct)
		self.toolMenu.addSeparator()
		self.toolMenu.addAction(self.authorStatsAct)

		freqSearches = pbConfig.globalDb.getSearchList(
			manual=True, replacement=False)
		if len(freqSearches) > 0:
			self.searchMenu = self.menuBar().addMenu("Frequent &searches")
			for fs in freqSearches:
				self.searchMenu.addAction(QAction(
					fs["name"], self,
					triggered=\
						lambda sD=ast.literal_eval(fs["searchDict"]),
								l=fs["limitNum"],
								o=fs["offsetNum"]:
							self.runSearchBiblio(sD, l, o)
					))
			self.searchMenu.addSeparator()
			for fs in freqSearches:
				self.searchMenu.addAction(QAction(
					"Delete '%s'"%fs["name"], self,
					triggered=\
						lambda idS=fs["idS"], n=fs["name"]: \
							self.delSearchBiblio(idS, n)
					))
		else:
			self.searchMenu = None

		freqReplaces = pbConfig.globalDb.getSearchList(
			manual=True, replacement=True)
		if len(freqReplaces) > 0:
			self.replaceMenu = self.menuBar().addMenu("Frequent &replaces")
			for fs in freqReplaces:
				self.replaceMenu.addAction(QAction(
					fs["name"], self,
					triggered=\
						lambda sD=ast.literal_eval(fs["searchDict"]),
								r=ast.literal_eval(fs["replaceFields"]),
								o=fs["offsetNum"]:
							self.runSearchReplaceBiblio(sD, r, o)
					))
			self.replaceMenu.addSeparator()
			for fs in freqReplaces:
				self.replaceMenu.addAction(QAction(
					"Delete '%s'"%fs["name"], self,
					triggered=\
						lambda idS=fs["idS"], n=fs["name"]: \
							self.delSearchBiblio(idS, n)
					))
		else:
			self.replaceMenu = None

		self.helpMenu = self.menuBar().addMenu("&Help")
		self.helpMenu.addAction(self.dbstatsAct)
		self.helpMenu.addAction(self.logfileAct)
		self.helpMenu.addSeparator()
		self.helpMenu.addAction(self.aboutAct)

		try:
			self.removeToolBar(self.mainToolBar)
		except AttributeError:
			pass
		self.mainToolBar = self.addToolBar('Toolbar')
		self.mainToolBar.addAction(self.undoAct)
		self.mainToolBar.addAction(self.saveAct)
		self.mainToolBar.addSeparator()
		self.mainToolBar.addAction(self.newBibAct)
		self.mainToolBar.addAction(self.searchBibAct)
		self.mainToolBar.addAction(self.searchReplaceAct)
		self.mainToolBar.addAction(self.exportAct)
		self.mainToolBar.addAction(self.exportAllAct)
		self.mainToolBar.addSeparator()
		self.mainToolBar.addAction(self.refreshAct)
		self.mainToolBar.addAction(self.reloadAct)
		self.mainToolBar.addSeparator()
		self.mainToolBar.addAction(self.configAct)
		self.mainToolBar.addAction(self.dbstatsAct)
		self.mainToolBar.addAction(self.aboutAct)
		self.mainToolBar.addSeparator()
		self.mainToolBar.addAction(self.exitAct)

	def createMainLayout(self):
		"""Set the layout of the main window, i.e. create the splitters
		and locate the bibtex list widget and the info panels
		"""
		#will contain the list of bibtex entries
		self.bibtexListWindow = BibtexListWindow(parent=self)
		self.bibtexListWindow.setFrameShape(QFrame.StyledPanel)

		#will contain the bibtex code:
		self.bottomLeft = BibtexInfo(self)
		self.bottomLeft.setFrameShape(QFrame.StyledPanel)

		#will contain the abstract of the bibtex entry:
		self.bottomCenter = BibtexInfo(self)
		self.bottomCenter.setFrameShape(QFrame.StyledPanel)

		#will contain other info on the bibtex entry:
		self.bottomRight = BibtexInfo(self)
		self.bottomRight.setFrameShape(QFrame.StyledPanel)

		splitter = QSplitter(Qt.Vertical)
		splitter.addWidget(self.bibtexListWindow)
		splitterBottom = QSplitter(Qt.Horizontal)
		splitterBottom.addWidget(self.bottomLeft)
		splitterBottom.addWidget(self.bottomCenter)
		splitterBottom.addWidget(self.bottomRight)
		splitter.addWidget(splitterBottom)
		splitter.setStretchFactor(0, 3)
		splitter.setStretchFactor(1, 1)

		availableWidth		= QDesktopWidget().availableGeometry().width()
		availableHeight		= QDesktopWidget().availableGeometry().height()
		splitter.setGeometry(0, 0, availableWidth, availableHeight)

		self.setCentralWidget(splitter)

	def undoDB(self):
		"""Reset database changes, window title and table content"""
		pBDB.undo()
		self.mainWindowTitle('PhysBiblio')
		self.reloadMainContent()

	def refreshMainContent(self):
		"""Delete the previous table widget and create a new one,
		using last used query
		"""
		self.statusBarMessage("Reloading main table...")
		self.bibtexListWindow.recreateTable(
			pBDB.bibs.fetchFromLast().lastFetched)
		self.done()

	def reloadMainContent(self, bibs=None):
		"""Delete the previous table widget and create a new one,
		using the default query
		"""
		self.statusBarMessage("Reloading main table...")
		self.bibtexListWindow.recreateTable(bibs)
		self.done()

	def manageProfiles(self):
		"""Ask and change profile"""
		profilesWin = SelectProfiles(self)
		profilesWin.exec_()

	def editProfile(self):
		"""Wrapper for profilesManager.editProfile"""
		editProfile(self)

	def config(self):
		"""Open a window to manage the configuration of PhysBiblio,
		then read its output and save the results
		"""
		cfgWin = ConfigWindow(self)
		cfgWin.exec_()
		if cfgWin.result:
			changed = False
			for q in cfgWin.textValues:
				if isinstance(q[1], PBComboBox):
					s = "%s"%q[1].currentText()
				else:
					s = "%s"%q[1].text()
				if q[0] == "loggingLevel":
					s = s.split(" - ")[0]
				if str(pbConfig.params[q[0]]) != s:
					pBLogger.info(
						"New value for param %s = %s (old: '%s')"%(
						q[0], s, pbConfig.params[q[0]]))
					pbConfig.params[q[0]] = s
					pBDB.config.update(q[0], s)
					changed = True
				pBLogger.debug("Using configuration param %s = %s"%(q[0], s))
			if changed:
				pBDB.commit()
				pbConfig.readConfig()
				self.reloadConfig()
				self.refreshMainContent()
				self.statusBarMessage("Configuration saved")
			else:
				self.statusBarMessage("No changes requested")
		else:
			self.statusBarMessage("Changes discarded")

	def logfile(self):
		"""Open a dialog to see the content of the log file"""
		logfileWin = LogFileContentDialog(self)
		logfileWin.exec_()

	def reloadConfig(self):
		"""Reload the configuration from the database.
		Typically used when a new profile has been opened
		"""
		self.statusBarMessage("Reloading configuration...")
		pBView.webApp = pbConfig.params["webApplication"]
		pBPDF.pdfApp = pbConfig.params["pdfApplication"]
		if pbConfig.params["pdfFolder"][0] == "/":
			pBPDF.pdfDir = pbConfig.params["pdfFolder"]
		else:
			pBPDF.pdfDir = os.path.join(os.path.split(
				os.path.abspath(sys.argv[0]))[0],
				pbConfig.params["pdfFolder"])
		self.bibtexListWindow.reloadColumnContents()

	def showAbout(self, testing=False):
		"""Function to show the About dialog"""
		mbox = QMessageBox(QMessageBox.Information,
			"About PhysBiblio",
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
		mbox.setTextFormat(Qt.RichText)
		mbox.setIconPixmap(QPixmap(':/images/icon.png'))
		if testing:
			return mbox
		mbox.exec_()

	def showDBStats(self, testing=False):
		"""Function to show a dialog with the statistics
		of the database content and on the number of stored PDF files

		Parameter:
			testing (default False): if True, return the QMessageBox
				instead of running `show()` (used for testing)
		"""
		dbStats(pBDB)
		onlyfiles = len(list(glob.iglob("%s/*/*.pdf"%pBPDF.pdfDir)))
		mbox = QMessageBox(QMessageBox.Information,
			"PhysBiblio database statistics",
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
			+ "The number of currently stored PDF files is %d.\n"%onlyfiles
			+ "The size of the PDF folder is %s."%(
				pBPDF.getSizeWUnits(pBPDF.dirSize(pBPDF.pdfDir))),
			parent=self)
		mbox.setIconPixmap(QPixmap(':/images/icon.png'))
		if testing:
			return mbox
		mbox.show()

	def _runInThread(self, Thread_func, title, *args, **kwargs):
		"""Function which simplifies the creation of the objects which
		are needed to run a function in a thread

		Parameters:
			Thread_func: the thread class name
			title: the title of the window where the output is shown
			*args, **kwargs: all the other parameters which will
				be passed to the thread constructor
		"""
		def getDelKwargs(key):
			"""Extract a parameter from kwargs and delete it
			from the original dictionary
			"""
			if key in kwargs.keys():
				tmp = kwargs.get(key)
				del kwargs[key]
				return tmp
			else:
				return None
		totStr = getDelKwargs("totStr")
		progrStr = getDelKwargs("progrStr")
		addMessage = getDelKwargs("addMessage")
		stopFlag = getDelKwargs("stopFlag")
		app = PrintText(title=title, totStr=totStr, progrStr=progrStr,
			noStopButton=True if stopFlag is False else False)

		outMessage = getDelKwargs("outMessage")
		minProgress = getDelKwargs("minProgress")
		if minProgress:
			app.progressBarMin(minProgress)
		queue = Queue()
		ws = WriteStream(queue)
		ws.newText.connect(app.appendText)
		thr = Thread_func(ws, *args, parent=self, **kwargs)

		ws.finished.connect(ws.deleteLater)
		thr.finished.connect(app.enableClose)
		thr.finished.connect(thr.deleteLater)
		if stopFlag:
			app.stopped.connect(thr.setStopFlag)

		pBErrorManager.tempHandler(ws, format='%(message)s')
		if addMessage:
			pBLogger.info(addMessage)
		thr.start()
		app.exec_()
		pBLogger.info("Closing...")
		pBErrorManager.rmTempHandler()
		if outMessage:
			self.statusBarMessage(outMessage)
		else:
			self.done()

	def cleanSpare(self):
		"""Run a thread to clean the spare connections and records
		in the database (if something has not been properly deleted)
		"""
		self._runInThread(Thread_cleanSpare, "Clean spare entries")

	def cleanSparePDF(self):
		"""Ask and run a thread to remove the spare PDF files/folder
		in the database (if something has not been properly deleted)
		"""
		if askYesNo("Do you really want to delete the unassociated "
				+ "PDF folders?\nThere may be some (unlikely) "
				+ "accidental deletion of files."):
			self._runInThread(Thread_cleanSparePDF, "Clean spare PDF folders")

	def createStatusBar(self):
		"""Function to create Status Bar"""
		self.mainStatusBar.showMessage('Ready', 0)
		self.setStatusBar(self.mainStatusBar)

	def statusBarMessage(self, message, time=4000):
		"""Show a message in the status bar

		Parameters:
			message: the message text
			time (default 4000): how long (in ms) to display the message
		"""
		pBLogger.info(message)
		self.mainStatusBar.showMessage(message, time)

	def save(self):
		"""Ask and save the database changes"""
		if askYesNo("Do you really want to save?"):
			pBDB.commit()
			self.mainWindowTitle("PhysBiblio")
			self.statusBarMessage("Changes saved")
		else:
			self.statusBarMessage("Nothing saved")

	def importFromBib(self):
		"""Ask and import (from a thread) the entries in a .bib file"""
		filename = askFileName(self,
			title="From where do you want to import?",
			filter="Bibtex (*.bib)")
		if filename != "":
			self._runInThread(
				Thread_importFromBib,
				"Importing...",
				filename,
				askYesNo("Do you want to use INSPIRE "
					+ "to find more information about the imported entries?"),
				totStr="Entries to be processed: ",
				progrStr="%), processing entry ",
				minProgress=0,
				stopFlag=True,
				outMessage="All entries into '%s' have been imported"%filename)
			self.statusBarMessage("File '%s' imported!"%filename)
			self.reloadMainContent()
		else:
			self.statusBarMessage("Empty filename given!")

	def export(self):
		"""Ask and export the last database query result in a .bib file"""
		filename = askSaveFileName(self,
			title="Where do you want to export the entries?",
			filter="Bibtex (*.bib)")
		if filename != "":
			pBExport.exportLast(filename)
			self.statusBarMessage(
				"Last fetched entries exported into '%s'"%filename)
		else:
			self.statusBarMessage("Empty filename given!")

	def exportSelection(self, entries):
		"""Ask and export the last selected entries in a .bib file

		Parameter:
			entries: the list of entries to be exported
		"""
		filename = askSaveFileName(self,
			title="Where do you want to export the selected entries?",
			filter="Bibtex (*.bib)")
		if filename != "":
			pBExport.exportSelected(filename, entries)
			self.statusBarMessage(
				"Current selection exported into '%s'"%filename)
		else:
			self.statusBarMessage("Empty filename given!")

	def exportFile(self):
		"""Ask and export in a .bib file the bibtex entries
		which are needed to compile one or more tex files
		"""
		outFName = askSaveFileName(self,
			title="Where do you want to export the entries?",
			filter="Bibtex (*.bib)")
		if outFName != "":
			texFile = askFileNames(self,
				title="Which is/are the *.tex file(s) you want to compile?",
				filter="Latex (*.tex)")
			if (not isinstance(texFile, list) and texFile != "") \
					or (isinstance(texFile, list) and len(texFile)>0):
				self._runInThread(
					Thread_exportTexBib,
					"Exporting...",
					texFile,
					outFName,
					minProgress=0,
					stopFlag=True,
					outMessage="All entries saved into '%s'"%outFName)
			else:
				self.statusBarMessage("Empty input filename/folder!")
		else:
			self.statusBarMessage("Empty output filename!")

	def exportUpdate(self):
		"""Ask and update a .bib file
		which already contains bibtex entries
		with the newer information from the database
		"""
		filename = askSaveFileName(self,
			title="File to update?",
			filter="Bibtex (*.bib)")
		if filename != "":
			overwrite = askYesNo(
				"Do you want to overwrite the existing .bib file?",
				"Overwrite")
			pBExport.updateExportedBib(filename, overwrite=overwrite)
			self.statusBarMessage("File '%s' updated"%filename)
		else:
			self.statusBarMessage("Empty output filename!")

	def exportAll(self):
		"""Ask and export all the entries in a .bib file"""
		filename = askSaveFileName(self,
			title="Where do you want to export the entries?",
			filter="Bibtex (*.bib)")
		if filename != "":
			pBExport.exportAll(filename)
			self.statusBarMessage("All entries saved into '%s'"%filename)
		else:
			self.statusBarMessage("Empty output filename!")

	def categories(self):
		"""Open a window to show the list categories"""
		self.statusBarMessage("categories triggered")
		catListWin = CatsTreeWindow(self)
		catListWin.show()

	def newCategory(self):
		"""Wrapper for catWindows.editCategory"""
		editCategory(self, self)

	def experiments(self):
		"""Open a window to show the list experiments"""
		self.statusBarMessage("experiments triggered")
		expListWin = ExpsListWindow(self)
		expListWin.show()

	def newExperiment(self):
		"""Wrapper for expWindows.editExperiment"""
		editExperiment(self, self)

	def newBibtex(self):
		"""Wrapper for bibWindows.editBibtex"""
		editBibtex(self)

	def searchBiblio(self, replace=False):
		"""Open a dialog for performing searches in the database

		Parameter:
			replace (default False): to be passed to SearchBibsWindow,
				in order to show (or not) the replace field inputs
		"""
		# maybe part of this should be implemented
		# inside the SearchBibsWindow class?
		newSearchWin = SearchBibsWindow(self, replace=replace)
		newSearchWin.exec_()
		searchDict = {}
		if newSearchWin.result is True:
			searchDict["catExpOperator"] = \
				newSearchWin.values["catExpOperator"]
			if len(newSearchWin.values["cats"]) > 0:
				searchDict["cats"] = {
					"id": newSearchWin.values["cats"],
					"operator": newSearchWin.values["catsOperator"].lower(),
				}
			if len(newSearchWin.values["exps"]) > 0:
				searchDict["exps"] = {
					"id": newSearchWin.values["exps"],
					"operator": newSearchWin.values["expsOperator"].lower(),
				}
			newSearchWin.getMarksValues()
			if len(newSearchWin.values["marks"]) > 0:
				if "any" in newSearchWin.values["marks"]:
					searchDict["marks"] = {"str": "",
						"operator": "!=",
						"connection": newSearchWin.values["marksConn"]}
				else:
					searchDict["marks"] = {
						"str": ", ".join(newSearchWin.values["marks"]),
						"operator": "like",
						"connection": newSearchWin.values["marksConn"]}
			newSearchWin.getTypeValues()
			if len(newSearchWin.values["type"]) > 0:
				for k in newSearchWin.values["type"]:
					searchDict[k] = {"str": "1",
						"operator": "=",
						"connection": newSearchWin.values["typeConn"]}
					print(searchDict[k])
			for i, dic in enumerate(newSearchWin.textValues):
				k="%s#%d"%(dic["field"].currentText(), i)
				s = "%s"%dic["content"].text()
				op = "like" \
					if "%s"%dic["operator"].currentText() == "contains" \
					else "="
				if s.strip() != "":
					searchDict[k] = {"str": s,
						"operator": op,
						"connection": dic["logical"].currentText()}
			try:
				lim = int(newSearchWin.limitValue.text())
			except ValueError:
				lim = pbConfig.params["defaultLimitBibtexs"]
			try:
				offs = int(newSearchWin.limitOffs.text())
			except ValueError:
				offs = 0
			if replace:
				fieldsNew = [ newSearchWin.replNewField.currentText() ]
				replNew = [ newSearchWin.replNew.text() ]
				if newSearchWin.doubleEdit.isChecked():
					fieldsNew.append(newSearchWin.replNewField1.currentText())
					replNew.append(newSearchWin.replNew1.text())
				if newSearchWin.save:
					name = ""
					cancel = False
					while name.strip() == "":
						res = askGenericText(
							"Insert a name / short description "
							+ "to be able to recognise this replace "
							+ "in the future:", "Replace name", parent=self)
						if res[1]:
							name = res[0]
						else:
							cancel = True
							break
					if not cancel:
						pbConfig.globalDb.insertSearch(
							name=name,
							count=0,
							searchDict=searchDict,
							manual=True,
							replacement=True,
							limit=lim,
							offset=offs,
							replaceFields=[
								newSearchWin.replOldField.currentText(),
								fieldsNew,
								newSearchWin.replOld.text(),
								replNew,
								newSearchWin.replRegex.isChecked()])
						self.createMenusAndToolBar()
				else:
					pbConfig.globalDb.updateSearchOrder(replacement=True)
					pbConfig.globalDb.insertSearch(count=0,
						searchDict=searchDict,
						manual=False,
						replacement=True,
						limit=lim,
						offset=offs,
						replaceFields=[
							newSearchWin.replOldField.currentText(),
							fieldsNew,
							newSearchWin.replOld.text(),
							replNew, newSearchWin.replRegex.isChecked()])
				noLim = pBDB.bibs.fetchFromDict(
					searchDict.copy(),
					limitOffset=offs,
					doFetch=False)
				return (newSearchWin.replOldField.currentText(),
					fieldsNew,
					newSearchWin.replOld.text(),
					replNew,
					newSearchWin.replRegex.isChecked())
			if newSearchWin.save:
				name = ""
				cancel = False
				while name.strip() == "":
					res = askGenericText("Insert a name / short description "
						+ "to be able to recognise this search "
						+ "in the future:", "Search name", parent=self)
					if res[1]:
						name = res[0]
					else:
						cancel = True
						break
				if not cancel:
					pbConfig.globalDb.insertSearch(name=name,
						count=0,
						searchDict=searchDict,
						manual=True,
						replacement=False,
						limit=lim,
						offset=offs)
					self.createMenusAndToolBar()
			self.runSearchBiblio(searchDict, lim, offs)
		elif replace:
			return False

	def runSearchBiblio(self, searchDict, lim, offs):
		"""Run a search with some parameters

		Parameters:
			searchDict: the dictionary with the search parameters
				to be used in `database.Entries.fetchFromDict`
			lim: the maximum number of entries to fetch
			offs: the offset for the search
		"""
		QApplication.setOverrideCursor(Qt.WaitCursor)
		noLim = pBDB.bibs.fetchFromDict(
			searchDict.copy(), limitOffset=offs).lastFetched
		lastFetched = pBDB.bibs.fetchFromDict(searchDict,
			limitTo=lim, limitOffset=offs
			).lastFetched
		if len(noLim) > len(lastFetched):
			infoMessage("Warning: more entries match the current search, "
				+ "showing only the first %d of %d."%(
					len(lastFetched), len(noLim))
				+ "\nChange 'Max number of results' in the search "
				+ "form to see more.")
		self.reloadMainContent(lastFetched)
		QApplication.restoreOverrideCursor()

	def runSearchReplaceBiblio(self, searchDict, replaceFields, offs):
		"""Run a search&replace with some parameters

		Parameters:
			searchDict: the dictionary with the search parameters
				to be used in `database.Entries.fetchFromDict`
			replaceFields: a tuple/list of 5 elements,
				as in the output of `self.searchBiblio`
			offs: the offset for the search
		"""
		pBDB.bibs.fetchFromDict(searchDict.copy(), limitOffset=offs)
		self.runReplace(replaceFields)

	def delSearchBiblio(self, idS, name):
		"""Delete a saved search from the database

		Parameters:
			idS: the search id in the database
			name: the search name
		"""
		if askYesNo("Are you sure you want to delete "
				+ "the saved search '%s'?"%name):
			pbConfig.globalDb.deleteSearch(idS)
			self.createMenusAndToolBar()

	def searchAndReplace(self):
		"""Open a search+replace form,
		then use the result to run the replace function
		"""
		result = self.searchBiblio(replace=True)
		if result is False:
			return
		self.runReplace(result)

	def runReplace(self, replace):
		"""Run the `database.Entries.replace` function,
		then print some output in a dialog

		Parameter:
			replace: a tuple/list of 5 elements,
				as in the output of `self.searchBiblio`
		"""
		fiOld, fiNew, old, new, regex = replace
		if old == "":
			infoMessage("The string to substitute is empty!")
			return
		if any(n == "" for n in new):
			if not askYesNo("Empty new string. "
					+ "Are you sure you want to continue?"):
				return
		self._runInThread(
			Thread_replace,
			"Replace",
			fiOld, fiNew, old, new,
			regex=regex,
			totStr="Replace will process ",
			progrStr="%): entry ",
			minProgress=0.,
			stopFlag=True
			)
		success, changed, failed = self.replaceResults
		LongInfoMessage("Replace completed.<br><br>"
			+ "%d elements successfully processed "%len(success)
			+ "(of which %d changed), "%len(changed)
			+ "%d failures (see below)."%len(failed)
			+ "<br><br><b>Changed</b>: %s"%changed
			+ "<br><br><b>Failed</b>: %s"%failed)
		QApplication.setOverrideCursor(Qt.WaitCursor)
		self.reloadMainContent(pBDB.bibs.fetchFromLast().lastFetched)
		QApplication.restoreOverrideCursor()

	def updateAllBibtexsAsk(self):
		"""Same as updateAllBibtexs, but ask the values of
		`startFrom` and `force` before the execution
		"""
		force = askYesNo("Do you want to force the update of already "
			+ "existing items?\n(Only regular articles not "
			+ "explicitely excluded will be considered)",
			"Force update:")
		text, out = askGenericText(
			"Insert the ordinal number of the bibtex element "
			+ "from which you want to start the updates:",
			"Where do you want to start searchOAIUpdates from?",
			self)
		if not out:
			return
		try:
			startFrom = int(text)
		except ValueError:
			if askYesNo("The text you inserted is not an integer. "
					+ "I will start from 0.\nDo you want to continue?",
					"Invalid entry"):
				startFrom = 0
			else:
				return
		self.updateAllBibtexs(startFrom, force=force)

	def updateAllBibtexs(self,
			startFrom=pbConfig.params["defaultUpdateFrom"],
			useEntries=None,
			force=False,
			reloadAll=False):
		"""Use INSPIRE to obtain updated information of a list of papers
		and update their bibtex with the new data.
		Typically used to add journal information to arXiv papers.

		Parameters (see `physbiblio.database.Entries.searchOAIUpdates`):
			startFrom (default from the app settings): the index
				of the entry where to start from
			useEntries (default None): None (then use all)
				or a list of entries
			force (default False): if True, force the update
				also of entries which already have journal information
			reloadAll (default False): if True, completely reload
				the bibtex instead of updating it
				(may solve some format problems)
		"""
		self.statusBarMessage(
			"Starting update of bibtexs from %s..."%startFrom)
		self._runInThread(
			Thread_updateAllBibtexs,
			"Update Bibtexs",
			startFrom,
			useEntries=useEntries,
			force=force,
			reloadAll=reloadAll,
			totStr="SearchOAIUpdates will process ",
			progrStr="%) - looking for update: ",
			minProgress=0.,
			stopFlag=True)
		self.refreshMainContent()

	def updateInspireInfo(self, bibkey, inspireID=None):
		"""Use a thread to look for the INSPIRE ID of one or more papers
		and then use it to obtain more information
		(identifiers like DOI/arXiv, first appearance date, publication)

		Parameters:
			bibkey: the (list of) bibtex key of the entry
			inspireID (default None): the (list of) INSPIRE ID,
				if already known
		"""
		self.statusBarMessage(
			"Starting generic info update from INSPIRE-HEP...")
		self._runInThread(
			Thread_updateInspireInfo,
			"Update Info",
			bibkey,
			inspireID,
			minProgress=0.,
			stopFlag=False)
		self.refreshMainContent()

	def authorStats(self):
		"""Ask the author name(s) and then
		use a thread to obtain the citation statistics
		for one or more authors using the INSPIRE-HEP database
		"""
		authorName, out = askGenericText(
			"Insert the INSPIRE name of the author of which you want "
			+ "the publication and citation statistics:",
			"Author name?", self)
		if not out:
			return False
		else:
			authorName = str(authorName)
		if authorName is "":
			pBGUILogger.warning("Empty name inserted! cannot proceed.")
			return False
		if "[" in authorName:
			try:
				authorName = ast.literal_eval(authorName.strip())
			except (ValueError, SyntaxError):
				pBGUILogger.exception(
					"Cannot recognize the list sintax. "
					+ "Missing quotes in the string?")
				return False
		self.statusBarMessage(
			"Starting computing author stats from INSPIRE...")

		self._runInThread(
			Thread_authorStats, "Author Stats",
			authorName,
			totStr="AuthorStats will process ",
			progrStr="%) - looking for paper: ",
			minProgress=0., stopFlag=True)

		if self.lastAuthorStats is None or len(
				self.lastAuthorStats["paLi"][0]) == 0:
			infoMessage("No results obtained. "
				+ "Maybe there was an error or you interrupted execution.")
			return False
		self.lastAuthorStats["figs"] = pBStats.plotStats(author=True)
		aSP = AuthorStatsPlots(self.lastAuthorStats["figs"],
			title="Statistics for '%s'"%authorName,
			parent=self)
		aSP.show()
		self.done()
		return True

	def getInspireStats(self, inspireId):
		"""Use a thread to obtain the citation statistics
		of a paper using the INSPIRE-HEP database

		Parameter:
			inspireId: the ID of the paper in the INSPIRE database
		"""
		self._runInThread(
			Thread_paperStats, "Paper Stats",
			inspireId,
			totStr="PaperStats will process ",
			progrStr="%) - looking for paper: ",
			minProgress=0., stopFlag=False)
		if self.lastPaperStats is None:
			infoMessage("No results obtained. Maybe there was an error.")
			return False
		self.lastPaperStats["fig"] = pBStats.plotStats(paper=True)
		pSP = PaperStatsPlots(self.lastPaperStats["fig"],
			title="Statistics for recid:%s"%inspireId,
			parent=self)
		pSP.show()
		self.done()

	def inspireLoadAndInsert(self, doReload=True):
		"""Ask a search string, then use inspire to import the entries
		which correspond, if unique results are obtained

		Parameter:
			doReload (default True): if True, reload
				the main entries list at the end
		"""
		queryStr, out = askGenericText(
			"Insert the query string you want to use for importing "
			+ "from INSPIRE-HEP:\n(It will be interpreted as a list, "
			+ "if possible)", "Query string?", self)
		if not out:
			return False
		if queryStr == "":
			pBGUILogger.warning("Empty string! cannot proceed.")
			return False
		self.loadedAndInserted = []
		self.statusBarMessage("Starting import from INSPIRE...")
		if "," in queryStr:
			try:
				queryStr = ast.literal_eval("[" + queryStr.strip() + "]")
			except (ValueError, SyntaxError):
				pBGUILogger.exception(
					"Cannot recognize the list sintax. "
					+ "Missing quotes in the string?")
				return False

		self._runInThread(
			Thread_loadAndInsert, "Import from INSPIRE-HEP",
			queryStr,
			totStr="LoadAndInsert will process ",
			progrStr="%) - looking for string: ",
			minProgress=0., stopFlag=True,
			addMessage="Searching:\n%s"%queryStr)

		if self.loadedAndInserted == []:
			infoMessage("No results obtained. "
				+ "Maybe there was an error or you interrupted execution.")
			return False
		if doReload:
			self.reloadMainContent()
		return True

	def askCatsForEntries(self, entriesList):
		"""Open a selection dialog for asking the categories
		for a given list of entries

		Parameter:
			entriesList: the list of entries to be used
		"""
		for entry in entriesList:
			selectCats = CatsTreeWindow(parent=self,
				askCats=True,
				askForBib=entry,
				previous=[a[0] for a in pBDB.cats.getByEntry(entry)])
			selectCats.exec_()
			if selectCats.result in ["Ok", "Exps"]:
				pBDB.catBib.insert(self.selectedCats, entry)
				self.statusBarMessage(
					"categories for '%s' successfully inserted"%entry)
			if selectCats.result == "Exps":
				selectExps = ExpsListWindow(parent=self,
					askExps=True, askForBib=entry)
				selectExps.exec_()
				if selectExps.result == "Ok":
					pBDB.bibExp.insert(entry, self.selectedExps)
					self.statusBarMessage(
						"experiments for '%s' successfully inserted"%entry)

	def inspireLoadAndInsertWithCats(self):
		"""Extend `self.inspireLoadAndInsert` to ask the categories
		to associate the entry with, if the import was successful
		"""
		if self.inspireLoadAndInsert(doReload=False) and len(
				self.loadedAndInserted) > 0:
			for key in self.loadedAndInserted:
				pBDB.catBib.delete(pbConfig.params["defaultCategories"], key)
			self.askCatsForEntries(self.loadedAndInserted)
			self.reloadMainContent()

	def advancedImport(self):
		"""Advanced import dialog.
		Open a dialog where you can select which method to use
		and insert the search string,
		then import a selection among the obtained results
		"""
		adIm = AdvancedImportDialog()
		adIm.exec_()
		method = adIm.comboMethod.currentText().lower()
		if method == "inspire-hep":
			method = "inspire"
		string = adIm.searchStr.text().strip()
		db = bibtexparser.bibdatabase.BibDatabase()
		if adIm.result == True and string != "":
			QApplication.setOverrideCursor(Qt.WaitCursor)
			cont = physBiblioWeb.webSearch[method].retrieveUrlAll(string)
			if cont.strip() != "":
				elements = bibtexparser.bparser.BibTexParser(
					common_strings=True).parse(cont).entries
			else:
				elements = []
			found = {}
			for el in elements:
				if not isinstance(el["ID"], six.string_types) or \
						el["ID"].strip() == "":
					db.entries = [el]
					entry = pbWriter.write(db)
					pBLogger.warning("Impossible to insert an entry with "
						+ "empty bibkey!\n%s\n"%entry)
				else:
					try:
						el["arxiv"] = el["eprint"]
					except KeyError:
						pass
					exist = (len(pBDB.bibs.getByBibkey(
						el["ID"],
						saveQuery=False) ) > 0)
					for f in ["arxiv", "doi"]:
						try:
							exist = (exist
								or (el[f].strip() != "" and len(
									pBDB.bibs.getAll(
										params={f: el[f]},
										saveQuery=False)) > 0))
						except KeyError:
							pBLogger.debug("KeyError '%s', entry: %s"%(
								f, el["ID"]))
					found[el["ID"]] = {"bibpars": el, "exist": exist}
			if len(found) == 0:
				infoMessage("No results obtained.")
				return False

			QApplication.restoreOverrideCursor()
			selImpo = AdvancedImportSelect(found, self)
			selImpo.exec_()
			if selImpo.result == True:
				newFound = {}
				for ch in sorted(selImpo.selected):
					if selImpo.selected[ch]:
						newFound[ch] = found[ch]
				found = newFound
				inserted = []
				for key in sorted(found):
					el = found[key]
					db.entries = [el["bibpars"]]
					entry = pbWriter.write(db)
					data = pBDB.bibs.prepareInsert(entry)
					if not pBDB.bibs.insert(data):
						pBLogger.warning(
							"Failed in inserting entry '%s'\n"%key)
						continue
					try:
						if method == "inspire":
							eid = pBDB.bibs.updateInspireID(key)
							pBDB.bibs.updateInfoFromOAI(eid)
						elif method == "isbn":
							pBDB.bibs.setBook(key)
						pBLogger.info(
							"Element '%s' successfully inserted.\n"%key)
						inserted.append(key)
					except:
						pBLogger.warning(
							"Failed in completing info for entry '%s'\n"%key)
				self.statusBarMessage(
					"Entries successfully imported: %s"%(
						inserted))
				if selImpo.askCats.isChecked():
					for key in inserted:
						pBDB.catBib.delete(
							pbConfig.params["defaultCategories"], key)
					self.askCatsForEntries(inserted)
			self.reloadMainContent()
		else:
			return False

	def cleanAllBibtexsAsk(self):
		"""Use a thread to clean and reformat the bibtex entries.
		Ask the index of the entry where to start from,
		before proceeding
		"""
		text, out = askGenericText("Insert the ordinal number of "
			+ "the bibtex element from which you want to start "
			+ "the cleaning:",
			"Where do you want to start cleanBibtexs from?",
			self)
		if not out:
			return
		try:
			startFrom = int(text)
		except ValueError:
			if askYesNo("The text you inserted is not an integer. "
					+ "I will start from 0.\nDo you want to continue?",
					"Invalid entry"):
				startFrom = 0
			else:
				return
		self.cleanAllBibtexs(startFrom)

	def cleanAllBibtexs(self, startFrom=0, useEntries=None):
		"""Use a thread to clean and reformat the bibtex entries

		Parameters:
			startFrom (default 0): the list index of the entry
				where to start from
			useEntries (default None): if not None, it must be a list
				of entries to be processed, otherwise the full database
				content will be used
		"""
		self.statusBarMessage("Starting cleaning of bibtexs...")
		self._runInThread(
			Thread_cleanAllBibtexs, "Clean Bibtexs",
			startFrom, useEntries=useEntries,
			totStr="CleanBibtexs will process ",
			progrStr="%) - cleaning: ",
			minProgress=0., stopFlag=True)

	def findBadBibtexs(self, startFrom=0, useEntries=None):
		"""Use a thread to scan the database for bad bibtex entries.
		If the user wants, a dialog for fixing each of them one by one
		may appear at the end of the search

		Parameters:
			startFrom (default 0): the list index of the entry
				where to start from
			useEntries (default None): if not None, it must be a list
				of entries to be processed, otherwise the full database
				content will be used
		"""
		self.statusBarMessage("Starting checking bibtexs...")
		self.badBibtexs = []
		self._runInThread(
			Thread_findBadBibtexs,
			"Check Bibtexs",
			startFrom,
			useEntries=useEntries,
			totStr="findCorruptedBibtexs will process ",
			progrStr="%) - processing: ",
			minProgress=0.,
			stopFlag=True)
		if len(self.badBibtexs) > 0:
			if askYesNo("%d bad records have been found. "%len(
						self.badBibtexs)
					+ "Do you want to fix them one by one?"):
				for bibkey in self.badBibtexs:
					editBibtex(self, bibkey)
			else:
				infoMessage("These are the bibtex keys corresponding "
					+ "to invalid records:\n%s"%", ".join(self.badBibtexs)
					+ "\n\nNo action will be performed.")
		else:
			infoMessage("No invalid records found!")

	def infoFromArxiv(self, useEntries=None):
		"""Use arXiv to obtain more information
		on a specific selection of entries

		Parameter:
			useEntries (default None): if not None, it must be a list
				of entries to be completed, otherwise the full database
				content will be used
		"""
		iterator = useEntries
		if useEntries is None:
			pBDB.bibs.fetchAll(doFetch=False)
			iterator = pBDB.bibs.fetchCursor()
		askFieldsWin = FieldsFromArxiv()
		askFieldsWin.exec_()
		if askFieldsWin.result:
			self.statusBarMessage("Starting importing info from arxiv...")
			self._runInThread(
				Thread_fieldsArxiv,
				"Get info from arXiv",
				[e["bibkey"] for e in iterator],
				askFieldsWin.output,
				totStr="Thread_fieldsArxiv will process ",
				progrStr="%) - processing: arxiv:",
				minProgress=0.,
				stopFlag=True)

	def browseDailyArxiv(self):
		"""Browse daily news from arXiv after showing
		a dialog for asking the category,
		and import the selection of entries
		"""
		bDA = DailyArxivDialog()
		bDA.exec_()
		cat = bDA.comboCat.currentText().lower()
		if bDA.result and cat != "":
			sub = bDA.comboSub.currentText()
			try:
				physBiblioWeb.webSearch["arxiv"].categories[cat]
			except KeyError:
				pBGUILogger.warning("Non-existent category! %s"%cat)
				return False
			QApplication.setOverrideCursor(Qt.WaitCursor)
			content = physBiblioWeb.webSearch["arxiv"].arxivDaily(
				cat if sub == "--" else "%s.%s"%(cat, sub))
			found = {}
			for el in content:
				el["type"] = ""
				if el["replacement"]:
					el["type"] += "[replacement]"
				if el["cross"]:
					el["type"] += "[cross-listed]"
				found[el["eprint"]] = {"bibpars": el, "exist": len(
					pBDB.bibs.getByBibkey(el["eprint"],
						saveQuery=False) ) > 0}
			if len(found) == 0:
				infoMessage("No results obtained.")
				return False

			QApplication.restoreOverrideCursor()
			selImpo = DailyArxivSelect(found, self)
			selImpo.abstractFormulas = AbstractFormulas
			selImpo.exec_()
			if selImpo.result == True:
				newFound = {}
				for ch in sorted(selImpo.selected):
					if selImpo.selected[ch]:
						newFound[ch] = found[ch]
				found = newFound
				self._runInThread(
					Thread_importDailyArxiv,
					"Import from arXiv",
					found,
					stopFlag=True
					)
				inserted, failed = self.importArXivResults
				self.statusBarMessage(
					"Entries successfully imported: %s"%(
						inserted))
				if selImpo.askCats.isChecked():
					for key in inserted:
						pBDB.catBib.delete(
							pbConfig.params["defaultCategories"], key)
					self.askCatsForEntries(inserted)
			self.reloadMainContent()
		else:
			return False

	def sendMessage(self, message):
		"""Show a simple infoMessage

		Parameter:
			message: the message content
		"""
		infoMessage(message)

	def done(self):
		"""Send a "done" message to the status bar"""
		self.statusBarMessage("...done!")


if __name__=='__main__':
	try:
		myApp = QApplication(sys.argv)
		myApp.setAttribute(Qt.AA_X11InitThreads)
		myWindow = MainWindow()
		myWindow.show()
		sys.exit(myApp.exec_())
	except NameError:
		print("NameError:", sys.exc_info()[1])
	except SystemExit:
		print("Closing main window...")
	except Exception:
		print(sys.exc_info()[1])
