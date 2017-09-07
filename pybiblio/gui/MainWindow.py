#!/usr/bin/env python

import sys
from Queue import Queue
from PySide.QtCore import *
from PySide.QtGui  import *
import signal
import ast

try:
	from pybiblio.errors import pBErrorManager
	from pybiblio.database import *
	from pybiblio.export import pBExport
	import pybiblio.webimport.webInterf as webInt
	from pybiblio.cli import cli as pyBiblioCLI
	from pybiblio.config import pbConfig
	from pybiblio.gui.DialogWindows import *
	from pybiblio.gui.BibWindows import *
	from pybiblio.gui.CatWindows import *
	from pybiblio.gui.ExpWindows import *
	from pybiblio.gui.inspireStatsGUI import *
	from pybiblio.gui.ProfilesManager import *
	from pybiblio.gui.ThreadElements import *
except ImportError:
	print("Could not find pybiblio and its contents: configure your PYTHONPATH!")
try:
	import pybiblio.gui.Resources_pyside
except ImportError:
	print("Missing Resources_pyside.py: Run script update_resources.sh")

class MainWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		availableWidth		= QDesktopWidget().availableGeometry().width()
		availableHeight		= QDesktopWidget().availableGeometry().height() 
		self.setWindowTitle('PyBiblio')
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

		#Catch Ctrl+C in shell
		signal.signal(signal.SIGINT, signal.SIG_DFL)
	
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

		self.saveAct = QAction(QIcon(":/images/file-save.png"),
								"&Save database", self,
								shortcut="Ctrl+S",
								statusTip="Save the modifications",
								triggered=self.save)
								
		self.exportAct = QAction(QIcon(":/images/export.png"),
								"Ex&port last as *.bib", self,
								#shortcut="Ctrl+P",
								statusTip="Export last query as *.bib",
								triggered=self.export)
								
		self.exportSelAct = QAction(QIcon(":/images/export.png"),
								"Export se&lection as *.bib", self,
								#shortcut="Ctrl+L",
								statusTip="Export current selection as *.bib",
								triggered=self.exportSelection)
								
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

		self.newBibAct = QAction(QIcon(":/images/file-add.png"),
								"New &Bib item", self,
								shortcut="Ctrl+N",
								statusTip="New bibliographic item",
								triggered=self.newBibtex)

		self.inspireLoadAndInsertAct = QAction("&Load from Inspires", self,
								shortcut="Ctrl+Shift+I",
								statusTip="Use Inspires to load and insert bibtex entries",
								triggered=self.inspireLoadAndInsert)

		self.inspireLoadAndInsertWithCatsAct = QAction("&Load from Inspires (ask categories)", self,
								shortcut="Ctrl+I",
								statusTip="Use Inspires to load and insert bibtex entries, then ask the categories for each",
								triggered=self.inspireLoadAndInsertWithCats)

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
								statusTip="Save the settings",
								triggered=self.config)

		self.refreshAct = QAction(QIcon(":/images/refresh2.png"),
								"&Refresh current entries list", self,
								shortcut="Ctrl+R",
								statusTip="Refresh the current list of entries",
								triggered=self.refreshMainContent)

		self.reloadAct = QAction(QIcon(":/images/refresh.png"),
								"&Reload (reset) main table", self,
								shortcut="Ctrl+Shift+R",
								statusTip="Reload the list of bibtex entries",
								triggered=self.reloadMainContent)

		self.aboutAct = QAction(QIcon(":/images/help-about.png"),
								"&About", self,
								statusTip="Show About box",
								triggered=self.showAbout)

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
		self.fileMenu.addAction(self.saveAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exportAct)
		self.fileMenu.addAction(self.exportSelAct)
		self.fileMenu.addAction(self.exportFileAct)
		self.fileMenu.addAction(self.exportAllAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.profilesAct)
		self.fileMenu.addAction(self.editProfilesAct)
		self.fileMenu.addAction(self.configAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exitAct)

		self.bibMenu = self.menuBar().addMenu("&Bibliography")
		self.bibMenu.addAction(self.newBibAct)
		self.bibMenu.addAction(self.inspireLoadAndInsertWithCatsAct)
		self.bibMenu.addAction(self.inspireLoadAndInsertAct)
		self.bibMenu.addSeparator()
		self.bibMenu.addAction(self.cleanAllBibtexsAct)
		self.bibMenu.addAction(self.cleanAllBibtexsAskAct)
		self.bibMenu.addSeparator()
		self.bibMenu.addAction(self.updateAllBibtexsAct)
		self.bibMenu.addAction(self.updateAllBibtexsAskAct)
		self.bibMenu.addSeparator()
		self.bibMenu.addAction(self.searchBibAct)
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
		self.toolMenu.addAction(self.authorStatsAct)
		self.toolMenu.addSeparator()
		self.toolMenu.addAction(self.cliAct)
		#self.optionMenu.addAction(self.optionsAct)
		#self.optionMenu.addAction(self.plotOptionsAct)
		#self.optionMenu.addAction(self.configOptionsAct)

		self.menuBar().addSeparator()
		self.helpMenu = self.menuBar().addMenu("&Help")
		self.helpMenu.addAction(self.aboutAct)
		
		self.mainToolBar = self.addToolBar('Toolbar')
		self.mainToolBar.addAction(self.saveAct)
		self.mainToolBar.addSeparator()
		self.mainToolBar.addAction(self.newBibAct)
		self.mainToolBar.addAction(self.searchBibAct)
		self.mainToolBar.addAction(self.exportAct)
		self.mainToolBar.addAction(self.exportAllAct)
		self.mainToolBar.addSeparator()
		self.mainToolBar.addAction(self.refreshAct)
		self.mainToolBar.addAction(self.reloadAct)
		self.mainToolBar.addAction(self.cliAct)
		self.mainToolBar.addSeparator()
		self.mainToolBar.addAction(self.configAct)
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

		#will contain other info on the bibtex entry:
		self.bottomRight = bibtexInfo(self)
		self.bottomRight.setFrameShape(QFrame.StyledPanel)

		splitter = QSplitter(Qt.Vertical)
		splitter.addWidget(self.bibtexList)
		splitterBottom = QSplitter(Qt.Horizontal)
		splitterBottom.addWidget(self.bottomLeft)
		splitterBottom.addWidget(self.bottomRight)
		splitter.addWidget(splitterBottom)
		splitter.setStretchFactor(0,3)
		splitter.setStretchFactor(1,1)

		availableWidth		= QDesktopWidget().availableGeometry().width()
		availableHeight		= QDesktopWidget().availableGeometry().height()
		#splitterBottom.setMinimumHeight(0.2*availableHeight)
		#splitterBottom.setMaximumHeight(0.4*availableHeight)
		#splitter.setMinimumHeight(0.8*availableHeight)
		#splitter.setMaximumHeight(0.8*availableHeight)
		splitter.setGeometry(0, 0, availableWidth, availableHeight)

		self.setCentralWidget(splitter)
		#self.setLayout(hbox)
		#QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))

		#self.setWindowTitle('QtGui.QSplitter')
		#self.show()

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
			for q in cfgWin.textValues:
				s = "%s"%q[1].text()
				if pbConfig.params[q[0]] != s:
					pbConfig.params[q[0]] = s
			pbConfig.saveConfigFile()
			pbConfig.readConfigFile()
			self.StatusBarMessage("Configuration saved")
		else:
			self.StatusBarMessage("Changes discarded")
	
	def showAbout(self):
		"""
		Function to show About Box
		"""
		QMessageBox.about(self, "About PyBiblio",
			"PyBiblio is a cross-platform tool for managing a LaTeX/BibTeX database. "+
			"It supports grouping, tagging and various different other functions.")

	def CreateStatusBar(self):
		"""
		Function to create Status Bar
		"""
		self.myStatusBar.showMessage('Ready', 0)
		self.setStatusBar(self.myStatusBar)
		
	def StatusBarMessage(self, message = "abc", time = 2000):
		print("[StatusBar] %s"%message)
		self.myStatusBar.showMessage(message, time)

	def save(self):
		if askYesNo("Do you really want to save?"):
			pBDB.commit()
			self.setWindowTitle("PyBiblio")
			self.StatusBarMessage("Changes saved")
		else:
			self.StatusBarMessage("Nothing saved")
		
	def export(self):
		filename = askSaveFileName(self, title = "Where do you want to export the entries?", filter = "Bibtex (*.bib)")
		if filename != "":
			pBExport.exportLast(filename)
			self.StatusBarMessage("Last fetched entries exported into %s"%filename)
		else:
			self.StatusBarMessage("Empty filename given!")
	
	def exportSelection(self):
		filename = askSaveFileName(self, title = "Where do you want to export the entries?", filter = "Bibtex (*.bib)")
		if filename != "":
			pBExport.exportSelected(filename)
			self.StatusBarMessage("Current selection exported into %s"%filename)
		else:
			self.StatusBarMessage("Empty filename given!")
	
	def exportFile(self):
		outFName = askSaveFileName(self, title = "Where do you want to export the entries?", filter = "Bibtex (*.bib)")
		if outFName != "":
			texFile = askFileName(self, title = "Which is the *.tex file you want to compile?", filter = "Latex (*.tex)")
			if texFile != "":
				app = printText(title = "Exporting...")
				app.progressBarMin(0)
				queue = Queue()
				self.exportTexBibReceiver = MyReceiver(queue, self)
				self.exportTexBibReceiver.mysignal.connect(app.append_text)
				self.exportTexBib_thr = thread_exportTexBib(texFile, outFName, queue, self.exportTexBibReceiver, self)

				self.connect(self.exportTexBibReceiver, SIGNAL("finished()"), self.exportTexBibReceiver.deleteLater)
				self.connect(self.exportTexBib_thr, SIGNAL("finished()"), app.enableClose)
				self.connect(self.exportTexBib_thr, SIGNAL("finished()"), self.exportTexBib_thr.deleteLater)
				self.connect(app, SIGNAL("stopped()"), self.exportTexBib_thr.setStopFlag)

				sys.stdout = WriteStream(queue)
				self.exportTexBib_thr.start()
				app.exec_()
				print("Closing...")
				sys.stdout = sys.__stdout__
				self.StatusBarMessage("All entries saved into %s"%outFName)
			else:
				self.StatusBarMessage("Empty input filename!")
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

	def searchBiblio(self):
		newSearchWin = searchBibsWindow(self)
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
			for i, dic in enumerate(newSearchWin.textValues):
				k="%s#%d"%(dic["field"].currentText(), i)
				s = "%s"%dic["content"].text()
				op = "like" if "%s"%dic["operator"].currentText() == "contains" else "="
				if s.strip() != "":
					searchDict[k] = {"str": s, "operator": op, "connection": dic["logical"].currentText()}
			self.reloadMainContent(pBDB.bibs.fetchFromDict(searchDict).lastFetched)

	def cli(self):
		self.StatusBarMessage("Activating CLI!")
		infoMessage("Command Line Interface activated: switch to the terminal, please.", "CLI")
		pyBiblioCLI()

	def updateAllBibtexsAsk(self):
		force = askYesNo("Do you want to force the update of already existing items?\n(Only regular articles not explicitely excluded will be considered)", "Force update:")
		text = askGenericText("Insert the ordinal number of the bibtex element from which you want to start the updates:", "Where do you want to start searchOAIUpdates from?", self)
		try:
			startFrom = int(text)
		except ValueError:
			if askYesNo("The text you inserted is not an integer. I will start from 0.\nDo you want to continue?", "Invalid entry"):
				startFrom = 0
			else:
				return False
		self.updateAllBibtexs(startFrom, force = force)

	def updateAllBibtexs(self, startFrom = 0, useEntries = None, force = False):
		self.StatusBarMessage("Starting update of bibtexs...")
		app = printText(title = "Update Bibtexs")
		app.progressBarMin(0)
		queue = Queue()
		self.uOAIReceiver = MyReceiver(queue, self)
		self.uOAIReceiver.mysignal.connect(app.append_text)
		self.updateOAI_thr = thread_updateAllBibtexs(startFrom, queue, self.uOAIReceiver, self, useEntries, force = force)

		self.connect(self.uOAIReceiver, SIGNAL("finished()"), self.uOAIReceiver.deleteLater)
		self.connect(self.updateOAI_thr, SIGNAL("finished()"), app.enableClose)
		self.connect(self.updateOAI_thr, SIGNAL("finished()"), self.updateOAI_thr.deleteLater)
		self.connect(app, SIGNAL("stopped()"), self.updateOAI_thr.setStopFlag)

		sys.stdout = WriteStream(queue)
		self.updateOAI_thr.start()
		app.exec_()
		print("Closing...")
		sys.stdout = sys.__stdout__
		self.done()

	def updateInspireInfo(self, bibkey):
		self.StatusBarMessage("Starting generic info update from Inspire...")
		app = printText(title = "Update Info")
		app.progressBarMin(0)
		queue = Queue()
		self.uIIReceiver = MyReceiver(queue, self)
		self.uIIReceiver.mysignal.connect(app.append_text)
		self.updateII_thr = thread_updateInspireInfo(bibkey, queue, self.uIIReceiver, self)

		self.connect(self.uIIReceiver, SIGNAL("finished()"), self.uIIReceiver.deleteLater)
		self.connect(self.updateII_thr, SIGNAL("finished()"), app.enableClose)
		self.connect(self.updateII_thr, SIGNAL("finished()"), self.updateII_thr.deleteLater)
		self.connect(app, SIGNAL("stopped()"), self.updateII_thr.setStopFlag)

		sys.stdout = WriteStream(queue)
		self.updateII_thr.start()
		app.exec_()
		print("Closing...")
		sys.stdout = sys.__stdout__
		self.done()

	def authorStats(self):
		authorName = askGenericText("Insert the INSPIRE name of the author of which you want the publication and citation statistics:", "Author name?", self)
		if authorName is "":
			pBGUIErrorManager("[authorStats] empty name inserted! cannot proceed.")
			return False
		self.StatusBarMessage("Starting computing author stats from INSPIRE...")
		app = printText(title = "Author Stats", totStr = "[inspireStats] authorStats will process ", progrStr = "%) - looking for paper: ")
		app.progressBarMin(0)
		queue = Queue()
		self.aSReceiver = MyReceiver(queue, self)
		self.aSReceiver.mysignal.connect(app.append_text)
		self.authorStats_thr = thread_authorStats(authorName, queue, self.aSReceiver, self)

		self.connect(self.aSReceiver, SIGNAL("finished()"), self.aSReceiver.deleteLater)
		self.connect(self.authorStats_thr, SIGNAL("finished()"), app.enableClose)
		self.connect(self.authorStats_thr, SIGNAL("finished()"), self.authorStats_thr.deleteLater)
		self.connect(app, SIGNAL("stopped()"), self.authorStats_thr.setStopFlag)

		sys.stdout = WriteStream(queue)
		self.authorStats_thr.start()
		app.exec_()
		print("Closing...")
		if self.lastAuthorStats is None:
			infoMessage("No results obtained. Maybe there was an error or you interrupted execution.")
			return False
		sys.stdout = sys.__stdout__
		self.lastAuthorStats["figs"] = pBStats.plotStats(author = True)
		aSP = authorStatsPlots(self.lastAuthorStats["figs"], title = "Statistics for %s"%authorName, parent = self)
		aSP.show()
		self.done()

	def inspireLoadAndInsert(self, doReload = True):
		queryStr = askGenericText("Insert the query string you want to use for importing from InspireHEP:\n(It will be interpreted as a list, if possible)", "Query string?", self)
		if queryStr == "":
			#pBGUIErrorManager("[inspireLoadAndInsert] empty string! cannot proceed.")
			return False
		self.loadedAndInserted = []
		self.StatusBarMessage("Starting import from INSPIRE...")
		app = printText(title = "Import from Inspire", totStr = "[DB] loadAndInsert will process ", progrStr = "%) - looking for string: ")
		app.progressBarMin(0)
		queue = Queue()
		self.iLAIReceiver = MyReceiver(queue, self)
		self.iLAIReceiver.mysignal.connect(app.append_text)
		if "," in queryStr:
			try:
				queryStr = ast.literal_eval("["+queryStr.strip()+"]")
			except SyntaxError:
				pBGUIErrorManager("[inspireLoadAndInsert] cannot recognize the list sintax. Missing quotes in the string?")
				return False
		print("[inspireLoadAndInsert] searching:")
		print(queryStr)
		self.inspireLoadAndInsert_thr = thread_loadAndInsert(queryStr, queue, self.iLAIReceiver, self)

		self.connect(self.iLAIReceiver, SIGNAL("finished()"), self.iLAIReceiver.deleteLater)
		self.connect(self.inspireLoadAndInsert_thr, SIGNAL("finished()"), app.enableClose)
		self.connect(self.inspireLoadAndInsert_thr, SIGNAL("finished()"), self.inspireLoadAndInsert_thr.deleteLater)
		self.connect(app, SIGNAL("stopped()"), self.inspireLoadAndInsert_thr.setStopFlag)

		sys.stdout = WriteStream(queue)
		self.inspireLoadAndInsert_thr.start()
		app.exec_()
		print("Closing...")
		if self.loadedAndInserted is []:
			infoMessage("No results obtained. Maybe there was an error or you interrupted execution.")
			return False
		sys.stdout = sys.__stdout__
		if doReload:
			self.reloadMainContent()
		return True

	def inspireLoadAndInsertWithCats(self):
		if self.inspireLoadAndInsert(doReload = False) and len(self.loadedAndInserted) > 0:
			for entry in self.loadedAndInserted:
				selectCats = catsWindowList(parent = self, askCats = True, askForBib = entry)
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
			self.reloadMainContent()

	def cleanAllBibtexsAsk(self):
		text = askGenericText("Insert the ordinal number of the bibtex element from which you want to start the cleaning:", "Where do you want to start cleanBibtexs from?", self)
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
		app = printText(title = "Clean Bibtexs", totStr = "[DB] cleanBibtexs will process ", progrStr = "%) - cleaning: ")
		app.progressBarMin(0)
		queue = Queue()
		self.cleanReceiver = MyReceiver(queue, self)
		self.cleanReceiver.mysignal.connect(app.append_text)
		self.cleanBibtexs_thr = thread_cleanAllBibtexs(startFrom, queue, self.cleanReceiver, self, useEntries)

		self.connect(self.cleanReceiver, SIGNAL("finished()"), self.cleanReceiver.deleteLater)
		self.connect(self.cleanBibtexs_thr, SIGNAL("finished()"), app.enableClose)
		self.connect(self.cleanBibtexs_thr, SIGNAL("finished()"), self.cleanBibtexs_thr.deleteLater)
		self.connect(app, SIGNAL("stopped()"), self.cleanBibtexs_thr.setStopFlag)

		sys.stdout = WriteStream(queue)
		self.cleanBibtexs_thr.start()
		app.exec_()
		print("Closing...")
		sys.stdout = sys.__stdout__
		self.done()

	def sendMessage(self, message):
		infoMessage(message)

	def done(self):
		self.StatusBarMessage("...done!")

if __name__=='__main__':
	try:
		myApp=QApplication(sys.argv)
		myWindow=MainWindow()
		myWindow.show()
		sys.exit(myApp.exec_())
	except NameError:
		print("NameError:",sys.exc_info()[1])
	except SystemExit:
		print("Closing main window...")
	except Exception:
		print(sys.exc_info()[1])
