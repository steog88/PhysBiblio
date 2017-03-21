#!/usr/bin/env python

import sys
from PySide.QtCore import *
from PySide.QtGui  import *
import signal

try:
	from pybiblio.database import *
	import pybiblio.export as bibexport
	import pybiblio.webimport.webInterf as webInt
	from pybiblio.cli import cli as pyBiblioCLI
	from pybiblio.config import pbConfig
	from pybiblio.gui.DialogWindows import *
	from pybiblio.gui.BibWindows import *
	from pybiblio.gui.CatWindows import *
	from pybiblio.gui.ExpWindows import *
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

		#Catch Ctrl+C in shell
		signal.signal(signal.SIGINT, signal.SIG_DFL)
	
	def setIcon(self):
		appIcon=QIcon(':/images/icon.png')
		self.setWindowIcon(appIcon)
		
	def createActions(self):
		"""
		Create Qt actions used in GUI.
		"""
		self.saveAct = QAction(QIcon(":/images/file-save.png"),
								"&Save database", self,
								shortcut="Ctrl+S",
								statusTip="Save the modifications",
								triggered=self.save)
								
		self.exportAct = QAction(QIcon(":/images/export.png"),
								"Ex&port last as *.bib", self,
								shortcut="Ctrl+P",
								statusTip="Export last query as *.bib",
								triggered=self.export)
								
		self.exportSelAct = QAction(QIcon(":/images/export.png"),
								"Export se&lection as *.bib", self,
								shortcut="Ctrl+L",
								statusTip="Export current selection as *.bib",
								triggered=self.exportSelection)
								
		self.exportAllAct = QAction(QIcon(":/images/export-table.png"),
								"Export &all as *.bib", self,
								shortcut="Ctrl+A",
								statusTip="Export complete bibliography as *.bib",
								triggered=self.exportAll)

		self.exportFileAct = QAction(#QIcon(":/images/export-table.png"),
								"Export for a *.&tex", self,
								#shortcut="Ctrl+A",
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
								statusTip="New Category",
								triggered=self.newCategory)

		self.ExpAct = QAction("&Experiments", self,
								shortcut="Ctrl+E",
								statusTip="List of Experiments",
								triggered=self.experimentList)

		self.newExpAct = QAction("&New Experiment", self,
								statusTip="New Experiment",
								triggered=self.newExperiment)
								
		self.biblioAct = QAction("Bibliogra&phy", self,
								statusTip="Manage bibliography",
								triggered=self.biblio)

		self.newBibAct = QAction(QIcon(":/images/file-add.png"),
								"New &Bib item", self,
								shortcut="Ctrl+N",
								statusTip="New bibliographic item",
								triggered=self.newBibtex)

		self.cliAct = QAction(QIcon(":/images/terminal.png"),
								"&CLI", self,
								shortcut="Ctrl+T",
								statusTip="CommandLine Interface",
								triggered=self.cli)

		self.configAct = QAction(QIcon(":/images/settings.png"),
								"Settin&gs", self,
								statusTip="Save the settings",
								triggered=self.config)

		self.reloadAct = QAction(QIcon(":/images/refresh.png"),
								"&Reload", self,
								shortcut="Ctrl+R",
								statusTip="Reload the list of bibtex entries",
								triggered=self.reloadMainContent)

		self.aboutAct = QAction(QIcon(":/images/help-about.png"),
								"&About", self,
								statusTip="Show About box",
								triggered=self.showAbout)

	def closeEvent(self, event):
		if pbConfig.params["askBeforeExit"] and not askYesNo("Do you really want to exit?"):
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
		self.fileMenu.addAction(self.configAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exitAct)

		self.menuBar().addSeparator()
		self.dataMenu = self.menuBar().addMenu("&Contents")
		self.dataMenu.addAction(self.CatAct)
		self.dataMenu.addAction(self.newCatAct)
		self.dataMenu.addSeparator()
		self.dataMenu.addAction(self.ExpAct)
		self.dataMenu.addAction(self.newExpAct)
		self.dataMenu.addSeparator()
		self.dataMenu.addAction(self.biblioAct)
		self.dataMenu.addAction(self.newBibAct)
		self.dataMenu.addAction(self.reloadAct)
		self.dataMenu.addSeparator()
		self.dataMenu.addAction(self.cliAct)

		#self.menuBar().addSeparator()
		#self.optionMenu = self.menuBar().addMenu("&Options")
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
		self.mainToolBar.addAction(self.exportAct)
		self.mainToolBar.addAction(self.exportAllAct)
		self.mainToolBar.addSeparator()
		self.mainToolBar.addAction(self.reloadAct)
		self.mainToolBar.addAction(self.cliAct)
		self.mainToolBar.addSeparator()
		self.mainToolBar.addAction(self.configAct)
		self.mainToolBar.addAction(self.aboutAct)
		self.mainToolBar.addSeparator()
		self.mainToolBar.addAction(self.exitAct)
		
        
	def createMainLayout(self):
		#will contain the list of bibtex entries
		self.top = bibtexList(self)
		self.top.setFrameShape(QFrame.StyledPanel)

		#will contain the bibtex code:
		self.bottomLeft = bibtexWindow(self)
		self.bottomLeft.setFrameShape(QFrame.StyledPanel)

		#will contain other info on the bibtex entry:
		self.bottomRight = bibtexInfo(self)
		self.bottomRight.setFrameShape(QFrame.StyledPanel)

		splitter = QSplitter(Qt.Vertical)
		splitter.addWidget(self.top)
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

	def reloadMainContent(self):
		"""delete previous table widget and create a new one"""
		#o = self.layout().takeAt(0)
		#o.widget().deleteLater()
		#self.createMainLayout()
		self.StatusBarMessage("Reloading main table...")
		self.top = bibtexList(self)
		self.top.setFrameShape(QFrame.StyledPanel)
	
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
		filename = askFileName(message = "Where do you want to export the entries?", title = "Enter filename")
		if filename != "":
			fname = filename
		else:
			fname = "temp.bib"
		bibexport.exportLast(fname)
		self.StatusBarMessage("Last fetched entries exported into %s"%fname)
	
	def exportSelection(self):
		filename = askFileName(message = "Where do you want to export the entries?", title = "Enter filename")
		if filename != "":
			fname = filename
		else:
			fname = "temp.bib"
		#retrieve selection
		bibexport.exportSelected(fname, rows)
		self.StatusBarMessage("Current selection exported into %s"%fname)
	
	def exportFile(self):
		filename = askFileName(message = "Where do you want to export the entries?", title = "Enter output filename")
		if filename != "":
			outFName = filename
		else:
			outFName = "bibtex.bib"

		filename = askFileName(message = "Which is the *.tex file you want to compile?", title = "Enter *.tex filename")
		if filename != "":
			texFile = filename
			bibexport.exportForTexFile(texFile, outFName)
			self.StatusBarMessage("All entries saved into %s"%outFName)
		else:
			self.StatusBarMessage("Error: empty input filename!")

	def exportAll(self):
		filename = askFileName(message = "Where do you want to export the entries?", title = "Enter filename")
		if filename != "":
			fname = filename
		else:
			fname = "all.bib"
		bibexport.exportAll(fname)
		self.StatusBarMessage("All entries saved into %s"%fname)
	
	def categories(self):
		#rows=pBDB.extractCatByName("Tags")
		self.StatusBarMessage("categories triggered")
		catListWin = catsWindowList(self)
		catListWin.show()

	def newCategory(self):
		editCategory(self, self)
	
	def experimentList(self):
		self.StatusBarMessage("experiments triggered")
		expListWin = ExpListWindow(self)
		expListWin.show()
		#window.cellClicked.connect(window.slotItemClicked)

	def newExperiment(self):
		editExperiment(self, self)

	def newBibtex(self):
		editBibtexEntry(self, self)

	def biblio(self):
		self.StatusBarMessage("biblio triggered")
		#abc=webInt.webInterf()
		#abc.loadInterfaces()
		#try:
			#tmp=abc.webSearch["inspire"].retrieveUrlFirst("Gariazzo:2015rra")
		#tmp=abc.webSearch["arxiv"].retrieveUrlFirst("1507.08204")
		#data=pBDB.bibs.prepareInsert("""@Article{Gariazzo:prova,
  #author        = {Gariazzo, S. and Giunti, C. and Laveder, M. and Li, Y. F. and Zavanin, E. M.},
  #title         = {{Light sterile neutrinos}},
  #journal       = {J. Phys.},
  #primaryclass  = {hep-ph},
  #year          = {2016},
  #slaccitation  = {%%CITATION = ARXIV:1507.08204;%%},
  #timestamp     = {2015.07.30},
#}""")
		##pBDB.bibs.insert(data)
		##except:
			##print "errors occurred"
		#pBDB.bibs.updateInspireID("Gariazzo:2015rra")
		#data=pBDB.bibs.prepareUpdateByKey("Gariazzo:prova", "Gariazzo:2015rra")
		#pBDB.bibs.update(data, "Gariazzo:prova")
		#print abc.webSearch["inspire"].loadBibtexsForTex("/home/steog88/Dottorato/Latex/Articoli/1607_feature/")
		#print pBDB.bibs.getByBibkey("Gariazzo:prova")
		#pBDB.bibs.getUpdateInfoFromOAI()
		#pyBiblioWeb.webSearch["inspireoai"].retrieveOAIData("1385583")
		#pBDB.bibs.loadAndInsert(["DiValentino:2015zta","Cadavid:2015iya"])
		#pBDB.bibs.printAllBibkeys()
		#entries = pBDB.bibs.getAll(orderBy="firstdate")
		#for e in entries:
			#b=pBDB.bibs.rmBibtexComments(e["bibtex"])
			#print pBDB.bibs.updateField(e["bibkey"], "bibtex", b)
		#pBDB.cats.insert({"name":"Really???","description":"","parentCat":0,"comments":"","ord":1})
		
		#pBDB.catBib.insert([58,64,65],"Ade:2015xua")
		#pBDB.bibExp.insert("Ade:2015xua",1)
		#print pBDB.cats.findByEntry("Ade:2015xua")
		
		#pBDB.exps.insert({"name":"DAMA", "comments":"", "homepage":"http://people.roma2.infn.it/~dama/web/home.html", "inspire":"1401121"})
		#pBDB.assignExpCat([58,64,65,66],6)
		
		#pBDB.exps.printAll()
		#pBDB.cats.printHier()

		self.StatusBarMessage("biblio done")

	def cli(self):
		self.StatusBarMessage("Activating CLI!")
		infoMessage("Command Line Interface activated: switch to the terminal, please.", "CLI")
		pyBiblioCLI()
			

	
if __name__=='__main__':
	try:
		myApp=QApplication(sys.argv)
		myWindow=MainWindow()
		myWindow.show()
		sys.exit(myApp.exec_())
	except NameError:
		print("NameError:",sys.exc_info()[1])
	except SystemExit:
		print("closing window...")
	except Exception:
		print(sys.exc_info()[1])
