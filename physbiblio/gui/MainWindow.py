#!/usr/bin/env python

import sys
if sys.version_info[0] < 3:
	from Queue import Queue
else:
	from queue import Queue

from PySide.QtCore import *
from PySide.QtGui  import *
import signal
import ast
import glob

try:
	from physbiblio.errors import pBErrorManager, pBLogger
	from physbiblio.database import *
	from physbiblio.export import pBExport
	import physbiblio.webimport.webInterf as webInt
	from physbiblio.cli import cli as physBiblioCLI
	from physbiblio.config import pbConfig
	from physbiblio.pdf import pBPDF
	from physbiblio.view import pBView
	from physbiblio.gui.ErrorManager import pBGUILogger
	from physbiblio.gui.DialogWindows import *
	from physbiblio.gui.BibWindows import *
	from physbiblio.gui.CatWindows import *
	from physbiblio.gui.UtilityWindows import *
	from physbiblio.gui.ExpWindows import *
	from physbiblio.gui.inspireStatsGUI import *
	from physbiblio.gui.ProfilesManager import *
	from physbiblio.gui.ThreadElements import *
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
try:
	if sys.version_info[0] < 3:
		import physbiblio.gui.Resources_pyside
	else:
		import physbiblio.gui.Resources_pyside3
except ImportError:
	print("Missing Resources_pyside: Run script update_resources.sh")

class MainWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		availableWidth		= QDesktopWidget().availableGeometry().width()
		availableHeight		= QDesktopWidget().availableGeometry().height() 
		self.setWindowTitle('PhysBiblio')
		self.setGeometry(0, 0, availableWidth, availableHeight)#x,y of topleft corner, width, height
		self.setMinimumHeight(400)
		self.setMinimumWidth(600)
		self.myStatusBar = QStatusBar()
		self.createActions()
		self.createMenusAndToolBar()
		self.createMainLayout()
		self.setIcon()
		self.CreateStatusBar()
		self.lastAuthorStats = None
		self.lastPaperStats = None

		#Catch Ctrl+C in shell
		signal.signal(signal.SIGINT, signal.SIG_DFL)

		self.checkUpdated = thread_checkUpdated(self)
		self.checkUpdated.finished.connect(self.checkUpdated.deleteLater)
		self.checkUpdated.result.connect(self.printNewVersion)
		self.checkUpdated.start()

	def printNewVersion(self, outdated, newVersion):
		if outdated:
			pBGUILogger.warning("New version available (%s)!\nYou can upgrade with `pip install -U physbiblio` (with `sudo`, eventually)."%newVersion)
		else:
			pBLogger.info("No new versions available!")

	def setIcon(self):
		appIcon=QIcon(':/images/icon.png')
		self.setWindowIcon(appIcon)
		
	def createActions(self):
		"""
		Create Qt actions used in GUI.
		"""
		self.profilesAct = QAction(QIcon(":/images/profiles.png"),
								"&Profiles", self,
								shortcut="Ctrl+P",
								statusTip="Manage profiles",
								triggered=self.manageProfiles)

		self.editProfilesAct = QAction(
								"&Edit profiles", self,
								shortcut="Ctrl+Alt+P",
								statusTip="Edit profiles",
								triggered=self.editProfiles)

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
								#shortcut="Ctrl+P",
								statusTip="Export last query as *.bib",
								triggered=self.export)
								
		self.exportAllAct = QAction(QIcon(":/images/export-table.png"),
								"Export &all as *.bib", self,
								shortcut="Ctrl+A",
								statusTip="Export complete bibliography as *.bib",
								triggered=self.exportAll)

		self.exportFileAct = QAction(#QIcon(":/images/export-table.png"),
								"Export for a *.&tex", self,
								shortcut="Ctrl+X",
								statusTip="Export as *.bib the bibliography needed to compile a .tex file",
								triggered=self.exportFile)

		self.exportUpdateAct = QAction(#QIcon(":/images/export-table.png"),
								"Update an existing *.&bib file", self,
								shortcut="Ctrl+Shift+X",
								statusTip="Read a *.bib file and update the existing elements inside it",
								triggered=self.exportUpdate)

		self.exitAct = QAction(QIcon(":/images/application-exit.png"),
								"E&xit", self,
								shortcut="Ctrl+Q",
								statusTip="Exit application",
								triggered=self.close)

		self.CatAct = QAction("&Categories", self,
								shortcut="Ctrl+C",
								statusTip="Manage Categories",
								triggered=self.categories)

		self.newCatAct = QAction("Ne&w Category", self,
								shortcut="Ctrl+Shift+C",
								statusTip="New Category",
								triggered=self.newCategory)

		self.ExpAct = QAction("&Experiments", self,
								shortcut="Ctrl+E",
								statusTip="List of Experiments",
								triggered=self.experimentList)

		self.newExpAct = QAction("&New Experiment", self,
								shortcut="Ctrl+Shift+E",
								statusTip="New Experiment",
								triggered=self.newExperiment)

		self.searchBibAct = QAction(QIcon(":/images/find.png"),
								"&Find Bibtex entries", self,
								shortcut="Ctrl+F",
								statusTip="Open the search dialog to filter the bibtex list",
								triggered=self.searchBiblio)

		self.searchReplaceAct = QAction(QIcon(":/images/edit-find-replace.png"),
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

		self.inspireLoadAndInsertWithCatsAct = QAction("&Load from INSPIRE-HEP (ask categories)", self,
								shortcut="Ctrl+I",
								statusTip="Use INSPIRE-HEP to load and insert bibtex entries, then ask the categories for each",
								triggered=self.inspireLoadAndInsertWithCats)

		self.advImportAct = QAction("&Advanced Import", self,
								shortcut="Ctrl+Alt+I",
								statusTip="Open the advanced import window",
								triggered=self.advancedImport)

		self.updateAllBibtexsAct = QAction("&Update bibtexs", self,
								shortcut="Ctrl+U",
								statusTip="Update all the journal info of bibtexs",
								triggered=self.updateAllBibtexs)

		self.updateAllBibtexsAskAct = QAction("Update bibtexs (&personalized)", self,
								shortcut="Ctrl+Shift+U",
								statusTip="Update all the journal info of bibtexs, but with non-standard options (start from, force, ...)",
								triggered=self.updateAllBibtexsAsk)

		self.cleanAllBibtexsAct = QAction("&Clean bibtexs", self,
								shortcut="Ctrl+L",
								statusTip="Clean all the bibtexs",
								triggered=self.cleanAllBibtexs)

		self.infoFromArxivAct = QAction("Info from ar&Xiv", self,
								shortcut="Ctrl+V",
								statusTip="Get info from arXiv",
								triggered=self.infoFromArxiv)

		self.cleanAllBibtexsAskAct = QAction("C&lean bibtexs (from ...)", self,
								shortcut="Ctrl+Shift+L",
								statusTip="Clean all the bibtexs, starting from a given one",
								triggered=self.cleanAllBibtexsAsk)

		self.authorStatsAct = QAction("&AuthorStats", self,
								shortcut="Ctrl+Shift+A",
								statusTip="Search publication and citation stats of an author from INSPIRES",
								triggered=self.authorStats)

		self.cliAct = QAction(QIcon(":/images/terminal.png"),
								"&CLI", self,
								shortcut="Ctrl+T",
								statusTip="CommandLine Interface",
								triggered=self.cli)

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

		self.logfileAct = QAction(#QIcon(":/images/settings.png"),
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

	def closeEvent(self, event):
		if pBDB.checkUncommitted():
			if askYesNo("There may be unsaved changes to the database.\nDo you really want to exit?"):
				event.accept()
			else:
				event.ignore()
		elif pbConfig.params["askBeforeExit"] and not askYesNo("Do you really want to exit?"):
			event.ignore()
		else:
			event.accept()

	def createMenusAndToolBar(self):
		"""
		Create Qt menus.
		"""
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
		self.fileMenu.addAction(self.editProfilesAct)
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

		self.menuBar().addSeparator()
		self.catMenu = self.menuBar().addMenu("&Categories")
		self.catMenu.addAction(self.CatAct)
		self.catMenu.addAction(self.newCatAct)
		
		self.menuBar().addSeparator()
		self.expMenu = self.menuBar().addMenu("&Experiments")
		self.expMenu.addAction(self.ExpAct)
		self.expMenu.addAction(self.newExpAct)
		
		self.menuBar().addSeparator()
		self.toolMenu = self.menuBar().addMenu("&Tools")
		self.toolMenu.addAction(self.cleanSpareAct)
		self.toolMenu.addAction(self.cleanSparePDFAct)
		self.toolMenu.addSeparator()
		self.toolMenu.addAction(self.authorStatsAct)
		# self.toolMenu.addSeparator()
		# self.toolMenu.addAction(self.cliAct)
		#self.optionMenu.addAction(self.optionsAct)
		#self.optionMenu.addAction(self.plotOptionsAct)
		#self.optionMenu.addAction(self.configOptionsAct)

		self.menuBar().addSeparator()
		self.helpMenu = self.menuBar().addMenu("&Help")
		self.helpMenu.addAction(self.dbstatsAct)
		self.helpMenu.addAction(self.logfileAct)
		self.helpMenu.addSeparator()
		self.helpMenu.addAction(self.aboutAct)
		
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
		# self.mainToolBar.addAction(self.cliAct)
		self.mainToolBar.addSeparator()
		self.mainToolBar.addAction(self.configAct)
		self.mainToolBar.addAction(self.dbstatsAct)
		self.mainToolBar.addAction(self.aboutAct)
		self.mainToolBar.addSeparator()
		self.mainToolBar.addAction(self.exitAct)

	def createMainLayout(self):
		#will contain the list of bibtex entries
		self.bibtexList = bibtexList(self)
		self.bibtexList.setFrameShape(QFrame.StyledPanel)

		#will contain the bibtex code:
		self.bottomLeft = bibtexWindow(self)
		self.bottomLeft.setFrameShape(QFrame.StyledPanel)

		#will contain the abstract of the bibtex entry:
		self.bottomCenter = bibtexInfo(self)
		self.bottomCenter.setFrameShape(QFrame.StyledPanel)

		#will contain other info on the bibtex entry:
		self.bottomRight = bibtexInfo(self)
		self.bottomRight.setFrameShape(QFrame.StyledPanel)

		splitter = QSplitter(Qt.Vertical)
		splitter.addWidget(self.bibtexList)
		splitterBottom = QSplitter(Qt.Horizontal)
		splitterBottom.addWidget(self.bottomLeft)
		splitterBottom.addWidget(self.bottomCenter)
		splitterBottom.addWidget(self.bottomRight)
		splitter.addWidget(splitterBottom)
		splitter.setStretchFactor(0,3)
		splitter.setStretchFactor(1,1)

		availableWidth		= QDesktopWidget().availableGeometry().width()
		availableHeight		= QDesktopWidget().availableGeometry().height()
		splitter.setGeometry(0, 0, availableWidth, availableHeight)

		self.setCentralWidget(splitter)

	def undoDB(self):
		pBDB.undo()
		self.reloadMainContent()

	def refreshMainContent(self, bibs = None):
		"""delete previous table widget and create a new one, using last used query"""
		self.StatusBarMessage("Reloading main table...")
		self.bibtexList.recreateTable(pBDB.bibs.fetchFromLast().lastFetched)
		self.done()

	def reloadMainContent(self, bibs = None):
		"""delete previous table widget and create a new one"""
		self.StatusBarMessage("Reloading main table...")
		self.bibtexList.recreateTable(bibs)
		self.done()

	def manageProfiles(self):
		"""change profile"""
		profilesWin = selectProfiles(self)
		profilesWin.exec_()

	def editProfiles(self):
		editProf(self, self)

	def config(self):
		cfgWin = configWindow(self)
		cfgWin.exec_()
		if cfgWin.result:
			changed = False
			for q in cfgWin.textValues:
				if isinstance(q[1], MyComboBox):
					s = "%s"%q[1].currentText()
				else:
					s = "%s"%q[1].text()
				if q[0] == "loggingLevel":
					s = s.split(" - ")[0]
				if str(pbConfig.params[q[0]]) != s:
					pBLogger.info("New value for param %s = %s (old: '%s')"%(q[0], s, pbConfig.params[q[0]]))
					pbConfig.params[q[0]] = s
					pBDB.config.update(q[0], s)
					changed = True
				if str(pbConfig.defaultsParams[q[0]]) == s:
					pBDB.config.delete(q[0])
					changed = True
				pBLogger.debug("Using configuration param %s = %s"%(q[0], s))
			if changed:
				pBDB.commit()
				pbConfig.readConfig()
				self.reloadConfig()
				self.refreshMainContent()
				self.StatusBarMessage("Configuration saved")
		else:
			self.StatusBarMessage("Changes discarded")

	def logfile(self):
		logfileWin = LogFileContentDialog(self)
		logfileWin.exec_()

	def reloadConfig(self):
		self.StatusBarMessage("Reloading configuration...")
		pBView.webApp = pbConfig.params["webApplication"]
		pBPDF.pdfApp = pbConfig.params["pdfApplication"]
		if pbConfig.params["pdfFolder"][0] == "/":
			pBPDF.pdfDir = pbConfig.params["pdfFolder"]
		else:
			pBPDF.pdfDir = os.path.join(os.path.split(os.path.abspath(sys.argv[0]))[0], pbConfig.params["pdfFolder"])
		self.bibtexList.reloadColumnContents()

	def showAbout(self):
		"""
		Function to show About Box
		"""
		mbox = QMessageBox(QMessageBox.Information,
			"About PhysBiblio",
			"PhysBiblio (<a href='https://github.com/steog88/physBiblio'>https://github.com/steog88/physBiblio</a>) is a cross-platform tool for managing a LaTeX/BibTeX database. "+
			"It is written in <code>python</code>, using <code>sqlite3</code> for the database management and <code>PySide</code> for the graphical part."+
			"<br>"+
			"It supports grouping, tagging, import/export, automatic update and various different other functions."+
			"<br><br>"+
			"<b>Paths:</b><br>"+
			"<i>Configuration:</i> %s<br>"%pbConfig.configPath+
			"<i>Data:</i> %s<br>"%pbConfig.dataPath+
			"<br>"+
			"<b>Author:</b> Stefano Gariazzo <i>&lt;stefano.gariazzo@gmail.com&gt;</i><br>"+
			"<b>Version:</b> %s (%s)"%(physbiblio.__version__, physbiblio.__version_date__))
		mbox.setTextFormat(Qt.RichText)
		mbox.setIconPixmap(QPixmap(':/images/icon.png'))
		mbox.exec_()

	def showDBStats(self):
		"""
		Function to show About Box
		"""
		dbStats(pBDB)
		onlyfiles = len(list(glob.iglob("%s/*/*.pdf"%pBPDF.pdfDir)))
		QMessageBox.about(self, "PhysBiblio database statistics",
			"The PhysBiblio database currently contains the following number of records:\n"+
			"- {bibs} bibtex entries\n- {cats} categories\n- {exps} experiments,\n".format(**pBDB.stats)+
			"- {catBib} bibtex entries to categories connections\n- {catExp} experiment to categories connections\n- {bibExp} bibtex entries to experiment connections.\n\n".format(**pBDB.stats)+
			"The number of currently stored PDF files is %d."%onlyfiles)

	def _runInThread(self, thread_func, title, *args, **kwargs):
		def getDelKwargs(key):
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
		app = printText(title = title, totStr = totStr, progrStr = progrStr,
			noStopButton = True if stopFlag is False else False)

		outMessage = getDelKwargs("outMessage")
		minProgress = getDelKwargs("minProgress")
		if minProgress:
			app.progressBarMin(minProgress)
		queue = Queue()
		ws = WriteStream(queue)
		ws.mysignal.connect(app.append_text)
		thr = thread_func(queue, ws, *args, parent = self, **kwargs)

		ws.finished.connect(ws.deleteLater)
		thr.finished.connect(app.enableClose)
		thr.finished.connect(thr.deleteLater)
		if stopFlag:
			app.stopped.connect(thr.setStopFlag)

		pBErrorManager.tempHandler(ws, format = '%(message)s')
		if addMessage:
			pBLogger.info(addMessage)
		thr.start()
		app.exec_()
		pBLogger.info("Closing...")
		pBErrorManager.rmTempHandler()
		if outMessage:
			self.StatusBarMessage(outMessage)
		else:
			self.done()

	def cleanSpare(self):
		self._runInThread(thread_cleanSpare, "Clean spare entries")

	def cleanSparePDF(self):
		if askYesNo("Do you really want to delete the unassociated PDF folders?\nThere may be some (unlikely) accidental deletion of files."):
			self._runInThread(thread_cleanSparePDF, "Clean spare PDF folders")

	def CreateStatusBar(self):
		"""
		Function to create Status Bar
		"""
		self.myStatusBar.showMessage('Ready', 0)
		self.setStatusBar(self.myStatusBar)
		
	def StatusBarMessage(self, message = "abc", time = 4000):
		pBLogger.info(message)
		self.myStatusBar.showMessage(message, time)

	def save(self):
		if askYesNo("Do you really want to save?"):
			pBDB.commit()
			self.setWindowTitle("PhysBiblio")
			self.StatusBarMessage("Changes saved")
		else:
			self.StatusBarMessage("Nothing saved")

	def importFromBib(self):
		filename = askFileName(self, title = "From where do you want to import?", filter = "Bibtex (*.bib)")
		if filename != "":
			self._runInThread(
				thread_importFromBib, "Importing...",
				filename, askYesNo("Do you want to use INSPIRE to find more information about the imported entries?"),
				totStr = "Entries to be processed: ", progrStr = "%), processing entry ",
				minProgress=0,  stopFlag = True, outMessage = "All entries into %s have been imported"%filename)
			self.StatusBarMessage("File %s imported!"%filename)
			self.reloadMainContent()
		else:
			self.StatusBarMessage("Empty filename given!")

	def export(self):
		filename = askSaveFileName(self, title = "Where do you want to export the entries?", filter = "Bibtex (*.bib)")
		if filename != "":
			pBExport.exportLast(filename)
			self.StatusBarMessage("Last fetched entries exported into %s"%filename)
		else:
			self.StatusBarMessage("Empty filename given!")

	def exportSelection(self, entries):
		filename = askSaveFileName(self, title = "Where do you want to export the selected entries?", filter = "Bibtex (*.bib)")
		if filename != "":
			pBExport.exportSelected(filename, entries)
			self.StatusBarMessage("Current selection exported into %s"%filename)
		else:
			self.StatusBarMessage("Empty filename given!")

	def exportFile(self):
		outFName = askSaveFileName(self, title = "Where do you want to export the entries?", filter = "Bibtex (*.bib)")
		if outFName != "":
			texFile = askFileNames(self, title = "Which is/are the *.tex file(s) you want to compile?", filter = "Latex (*.tex)")
			if (type(texFile) is not list and texFile != "") or (type(texFile) is list and len(texFile)>0):
				self._runInThread(
					thread_exportTexBib, "Exporting...",
					texFile, outFName,
					minProgress=0,  stopFlag = True, outMessage = "All entries saved into %s"%outFName)
			else:
				self.StatusBarMessage("Empty input filename/folder!")
		else:
			self.StatusBarMessage("Empty output filename!")

	def exportUpdate(self):
		filename = askSaveFileName(self, title = "File to update?", filter = "Bibtex (*.bib)")
		if filename != "":
			overwrite = askYesNo("Do you want to overwrite the existing .bib file?", "Overwrite")
			pBExport.updateExportedBib(filename, overwrite = overwrite)
			self.StatusBarMessage("File %s updated"%filename)
		else:
			self.StatusBarMessage("Empty output filename!")

	def exportAll(self):
		filename = askSaveFileName(self, title = "Where do you want to export the entries?", filter = "Bibtex (*.bib)")
		if filename != "":
			pBExport.exportAll(filename)
			self.StatusBarMessage("All entries saved into %s"%filename)
		else:
			self.StatusBarMessage("Empty output filename!")
	
	def categories(self):
		self.StatusBarMessage("categories triggered")
		catListWin = catsWindowList(self)
		catListWin.show()

	def newCategory(self):
		editCategory(self, self)
	
	def experimentList(self):
		self.StatusBarMessage("experiments triggered")
		expListWin = ExpWindowList(self)
		expListWin.show()

	def newExperiment(self):
		editExperiment(self, self)

	def newBibtex(self):
		editBibtex(self, self)

	def searchBiblio(self, replace = False):
		newSearchWin = searchBibsWindow(self, replace = replace)
		newSearchWin.exec_()
		searchDict = {}
		if newSearchWin.result is True:
			searchDict["catExpOperator"] = newSearchWin.values["catExpOperator"]
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
					searchDict["marks"] = {"str": "", "operator": "!=", "connection": newSearchWin.values["marksConn"]}
				else:
					searchDict["marks"] = {"str": ", ".join(newSearchWin.values["marks"]), "operator": "like", "connection": newSearchWin.values["marksConn"]}
			newSearchWin.getTypeValues()
			if len(newSearchWin.values["type"]) > 0:
				for k in newSearchWin.values["type"]:
					searchDict[k] = {"str": "1", "operator": "=", "connection": newSearchWin.values["typeConn"]}
					print(searchDict[k])
			for i, dic in enumerate(newSearchWin.textValues):
				k="%s#%d"%(dic["field"].currentText(), i)
				s = "%s"%dic["content"].text()
				op = "like" if "%s"%dic["operator"].currentText() == "contains" else "="
				if s.strip() != "":
					searchDict[k] = {"str": s, "operator": op, "connection": dic["logical"].currentText()}
			try:
				lim = int(newSearchWin.limitValue.text())
			except ValueError:
				lim = pbConfig.params["defaultLimitBibtexs"]
			try:
				offs = int(newSearchWin.limitOffs.text())
			except ValueError:
				offs = 0
			noLim = pBDB.bibs.fetchFromDict(searchDict.copy(), limitOffset = offs).lastFetched
			if replace:
				fieldsNew = [ newSearchWin.replNewField.currentText() ]
				replNew = [ newSearchWin.replNew.text() ]
				if newSearchWin.doubleEdit.isChecked():
					fieldsNew.append(newSearchWin.replNewField1.currentText())
					replNew.append(newSearchWin.replNew1.text())
				return (newSearchWin.replOldField.currentText(), fieldsNew,
					newSearchWin.replOld.text(), replNew, newSearchWin.replRegex.isChecked())
			lastFetched = pBDB.bibs.fetchFromDict(searchDict,
				limitTo = lim, limitOffset = offs
				).lastFetched
			if len(noLim) > len(lastFetched):
				infoMessage("Warning: more entries match the current search, showing only the first %d of %d.\nChange 'Max number of results' in the search form to see more."%(
					len(lastFetched), len(noLim)))
			self.reloadMainContent(lastFetched)
		elif replace:
			return False

	def searchAndReplace(self):
		result = self.searchBiblio(replace = True)
		if result is False:
			return False
		fiOld, fiNew, old, new, regex = result
		if old == "":
			infoMessage("The string to substitute is empty!")
			return
		if any(n == "" for n in new):
			if not askYesNo("Empty new string. Are you sure you want to continue?"):
				return
		success, changed, failed = pBDB.bibs.replace(fiOld, fiNew, old, new, entries = pBDB.bibs.lastFetched, regex = regex)
		infoMessage("Replace completed.\n" +
			"%d elements successfully processed (of which %d changed), %d failures (see below)."%(len(success), len(changed), len(failed)) +
			"\nChanged: %s\nFailed: %s"%(changed, failed))
		self.reloadMainContent(pBDB.bibs.fetchFromLast().lastFetched)

	def oldSearchAndReplace(self):
		dialog = searchReplaceDialog(self)
		dialog.exec_()
		if dialog.result == True:
			if dialog.searchEdit.text().strip() == "":
				infoMessage("Empty search string!\nDoing nothing.")
				return
			changed = pBDB.bibs.replaceInBibtex(dialog.searchEdit.text(), dialog.replaceEdit.text())
			if len(changed) > 0:
				infoMessage("Elements changed:\n%s"%changed)
			self.reloadMainContent(pBDB.bibs.lastFetched)

	def cli(self):
		self.StatusBarMessage("Activating CLI!")
		infoMessage("Command Line Interface activated: switch to the terminal, please.", "CLI")
		physBiblioCLI()

	def updateAllBibtexsAsk(self):
		force = askYesNo("Do you want to force the update of already existing items?\n(Only regular articles not explicitely excluded will be considered)", "Force update:")
		text, out = askGenericText("Insert the ordinal number of the bibtex element from which you want to start the updates:", "Where do you want to start searchOAIUpdates from?", self)
		if not out:
			return False
		try:
			startFrom = int(text)
		except ValueError:
			if askYesNo("The text you inserted is not an integer. I will start from 0.\nDo you want to continue?", "Invalid entry"):
				startFrom = 0
			else:
				return False
		self.updateAllBibtexs(startFrom, force = force)

	def updateAllBibtexs(self, startFrom = pbConfig.params["defaultUpdateFrom"], useEntries = None, force = False):
		self.StatusBarMessage("Starting update of bibtexs from %s..."%startFrom)
		self._runInThread(
			thread_updateAllBibtexs, "Update Bibtexs",
			startFrom, useEntries = useEntries, force = force,
			totStr = "SearchOAIUpdates will process ", progrStr = "%) - looking for update: ",
			minProgress = 0., stopFlag = True)

	def updateInspireInfo(self, bibkey):
		self.StatusBarMessage("Starting generic info update from INSPIRE-HEP...")
		self._runInThread(
			thread_updateInspireInfo, "Update Info",
			bibkey,
			minProgress = 0., stopFlag = True)

	def authorStats(self):
		authorName, out = askGenericText("Insert the INSPIRE name of the author of which you want the publication and citation statistics:", "Author name?", self)
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
			except SyntaxError:
				pBGUILogger.exception("Cannot recognize the list sintax. Missing quotes in the string?")
				return False
		self.StatusBarMessage("Starting computing author stats from INSPIRE...")

		self._runInThread(
			thread_authorStats, "Author Stats",
			authorName,
			totStr = "AuthorStats will process ", progrStr = "%) - looking for paper: ",
			minProgress = 0., stopFlag = True)

		if self.lastAuthorStats is None or len(self.lastAuthorStats["paLi"][0]) == 0:
			infoMessage("No results obtained. Maybe there was an error or you interrupted execution.")
			return False
		self.lastAuthorStats["figs"] = pBStats.plotStats(author = True)
		aSP = authorStatsPlots(self.lastAuthorStats["figs"], title = "Statistics for %s"%authorName, parent = self)
		aSP.show()
		self.done()

	def getInspireStats(self, inspireId):
		self._runInThread(
			thread_paperStats, "Paper Stats",
			inspireId,
			totStr = "PaperStats will process ", progrStr = "%) - looking for paper: ",
			minProgress = 0., stopFlag = False)
		if self.lastPaperStats is None:
			infoMessage("No results obtained. Maybe there was an error.")
			return False
		self.lastPaperStats["fig"] = pBStats.plotStats(paper = True)
		pSP = paperStatsPlots(self.lastPaperStats["fig"], title = "Statistics for recid:%s"%inspireId, parent = self)
		pSP.show()
		self.done()

	def inspireLoadAndInsert(self, doReload = True):
		queryStr, out = askGenericText("Insert the query string you want to use for importing from INSPIRE-HEP:\n(It will be interpreted as a list, if possible)", "Query string?", self)
		if not out:
			return False
		if queryStr == "":
			pBGUILogger.warning("Empty string! cannot proceed.")
			return False
		self.loadedAndInserted = []
		self.StatusBarMessage("Starting import from INSPIRE...")
		if "," in queryStr:
			try:
				queryStr = ast.literal_eval("[" + queryStr.strip() + "]")
			except (ValueError, SyntaxError):
				pBGUILogger.exception("Cannot recognize the list sintax. Missing quotes in the string?")
				return False

		self._runInThread(
			thread_loadAndInsert, "Import from INSPIRE-HEP",
			queryStr,
			totStr = "LoadAndInsert will process ", progrStr = "%) - looking for string: ",
			minProgress = 0., stopFlag = True,
			addMessage = "Searching:\n%s"%queryStr)

		if self.loadedAndInserted is []:
			infoMessage("No results obtained. Maybe there was an error or you interrupted execution.")
			return False
		if doReload:
			self.reloadMainContent()
		return True

	def askCatsForEntries(self, entriesList):
		for entry in entriesList:
			selectCats = catsWindowList(parent = self, askCats = True, askForBib = entry, previous = [a[0] for a in pBDB.cats.getByEntry(entry)])
			selectCats.exec_()
			if selectCats.result in ["Ok", "Exps"]:
				cats = self.selectedCats
				pBDB.catBib.insert(cats, entry)
				self.StatusBarMessage("categories for '%s' successfully inserted"%entry)
			if selectCats.result == "Exps":
				selectExps = ExpWindowList(parent = self, askExps = True, askForBib = entry)
				selectExps.exec_()
				if selectExps.result == "Ok":
					exps = self.selectedExps
					pBDB.bibExp.insert(entry, exps)
					self.StatusBarMessage("experiments for '%s' successfully inserted"%entry)

	def inspireLoadAndInsertWithCats(self):
		if self.inspireLoadAndInsert(doReload = False) and len(self.loadedAndInserted) > 0:
			for key in self.loadedAndInserted:
				pBDB.catBib.delete(pbConfig.params["defaultCategories"], key)
			self.askCatsForEntries(self.loadedAndInserted)
			self.reloadMainContent()

	def advancedImport(self):
		adIm = advImportDialog()
		adIm.exec_()
		method = adIm.comboMethod.currentText().lower()
		if method == "inspire-hep":
			method = "inspire"
		string = adIm.searchStr.text().strip()
		if adIm.result == True and string != "":
			cont = physBiblioWeb.webSearch[method].retrieveUrlAll(string)
			elements = bibtexparser.loads(cont).entries
			found = {}
			for el in elements:
				if el["ID"].strip() == "":
					pBLogger.warning("Impossible to insert an entry with empty bibkey!\n%s\n"%el["ID"])
				else:
					exist = (len(pBDB.bibs.getByBibkey(el["ID"], saveQuery = False) ) > 0)
					for f in ["arxiv", "doi"]:
						try:
							exist = (exist or
								(el[f].strip() != "" and len(pBDB.bibs.fetchAll(params = {f: el[f]}, saveQuery = False).lastFetched) > 0))
						except KeyError:
							pBLogger.debug("Error", exc_info = True)
					found[el["ID"]] = {"bibpars": el, "exist": exist}
			if len(found) == 0:
				infoMessage("No results obtained.")
				return False

			selImpo = advImportSelect(found, self)
			selImpo.exec_()
			if selImpo.result == True:
				newFound = {}
				for ch, val in selImpo.selected.items():
					if val:
						newFound[ch] = found[ch]
				found = newFound
				db = bibtexparser.bibdatabase.BibDatabase()
				inserted = []
				for key, el in found.items():
					db.entries = [el["bibpars"]]
					entry = pbWriter.write(db)
					data = pBDB.bibs.prepareInsert(entry)
					try:
						pBDB.bibs.insert(data)
					except:
						pBLogger.warning("Failed in inserting entry %s\n"%key)
						continue
					try:
						if method == "inspire":
							eid = pBDB.bibs.updateInspireID(key)
							pBDB.bibs.updateInfoFromOAI(eid)
						elif method == "isbn":
							pBDB.bibs.setBook(key)
						pBLogger.info("Element '%s' successfully inserted.\n"%key)
						inserted.append(key)
					except:
						pBLogger.warning("Failed in completing info for entry %s\n"%key)
				self.StatusBarMessage("[advancedImport] Entries successfully imported: %s"%inserted)
				if selImpo.askCats.isChecked():
					self.askCatsForEntries(inserted)
			self.reloadMainContent()
		else:
			return False

	def cleanAllBibtexsAsk(self):
		text, out = askGenericText("Insert the ordinal number of the bibtex element from which you want to start the cleaning:", "Where do you want to start cleanBibtexs from?", self)
		if not out:
			return False
		try:
			startFrom = int(text)
		except ValueError:
			if askYesNo("The text you inserted is not an integer. I will start from 0.\nDo you want to continue?", "Invalid entry"):
				startFrom = 0
			else:
				return False
		self.cleanAllBibtexs(startFrom)

	def cleanAllBibtexs(self, startFrom = 0, useEntries = None):
		self.StatusBarMessage("Starting cleaning of bibtexs...")
		self._runInThread(
			thread_cleanAllBibtexs, "Clean Bibtexs",
			startFrom, useEntries = useEntries,
			totStr = "CleanBibtexs will process ", progrStr = "%) - cleaning: ",
			minProgress = 0., stopFlag = True)

	def infoFromArxiv(self, useEntries = None):
		iterator = useEntries
		if useEntries is None:
			pBDB.bibs.fetchAll(doFetch = False)
			iterator = pBDB.bibs.fetchCursor()
		askFieldsWin = fieldsFromArxiv()
		askFieldsWin.exec_()
		if askFieldsWin.result:
			self.StatusBarMessage("Starting importing info from arxiv...")
			self._runInThread(
				thread_fieldsArxiv, "Get info from arXiv",
				[e["bibkey"] for e in iterator], askFieldsWin.output,
				totStr = "Thread_fieldsArxiv will process ", progrStr = "%) - processing: arxiv:",
				minProgress = 0., stopFlag = True)

	def sendMessage(self, message):
		infoMessage(message)

	def done(self):
		self.StatusBarMessage("...done!")

if __name__=='__main__':
	try:
		myApp=QApplication(sys.argv)
		myApp.setAttribute(Qt.AA_X11InitThreads)
		myWindow=MainWindow()
		myWindow.show()
		sys.exit(myApp.exec_())
	except NameError:
		print("NameError:",sys.exc_info()[1])
	except SystemExit:
		print("Closing main window...")
	except Exception:
		print(sys.exc_info()[1])
