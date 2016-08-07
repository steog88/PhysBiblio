#!/usr/bin/env python

import sys
from PySide.QtCore import *
from PySide.QtGui  import *
import signal

try:
	from pybiblio.database import *
	import pybiblio.export as bibexport
	import pybiblio.webimport.webInterf as webInt
except ImportError:
	print("Could not find pybiblio and its contents: configure your PYTHONPATH!")
try:
	import pybiblio.gui.Resources_pyside
except ImportError:
	print("Missing Resources_pyside.py: Run script update_resources.sh")

class MainWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self.setWindowTitle('PyBiblio')
		self.setGeometry(0,0,600,400)#x,y of topleft corner, width, height
		self.setMinimumHeight(400)
		self.setMinimumWidth(600)
		self.myStatusBar = QStatusBar()
		self.createActions()
		self.createMenus()
		self.createLayout()
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
		self.saveAct = QAction(QIcon(":/images/file_save.png"),
								"&Save database", self,
								shortcut="Ctrl+S",
								statusTip="Save the modifications",
								triggered=self.save)
								
		self.exportAct = QAction(QIcon(":/images/file_export.png"),
								"Ex&port last as *.bib", self,
								shortcut="Ctrl+P",
								statusTip="Export last query as *.bib",
								triggered=self.export)
								
		self.exportSelAct = QAction(QIcon(":/images/file_export.png"),
								"Export se&lection as *.bib", self,
								shortcut="Ctrl+L",
								statusTip="Export current selection as *.bib",
								triggered=self.exportSelection)
								
		self.exportAllAct = QAction(QIcon(":/images/file_export.png"),
								"Export &all as *.bib", self,
								shortcut="Ctrl+A",
								statusTip="Export complete bibliography as *.bib",
								triggered=self.exportAll)

		self.exitAct = QAction(QIcon(":/images/application_exit.png"),
								"E&xit", self,
								shortcut="Ctrl+Q",
								statusTip="Exit application",
								triggered=self.close)

		self.CatAct = QAction("&Categories", self,
								shortcut="Ctrl+C",
								statusTip="Manage Categories",
								triggered=self.categories)

		self.ExpAct = QAction("&Experiments", self,
								shortcut="Ctrl+E",
								statusTip="Manage Experiments",
								triggered=self.experiments)

		self.TagAct = QAction("&Tags", self,
								shortcut="Ctrl+T",
								statusTip="Manage tags",
								triggered=self.tags)

		self.biblioAct = QAction("&Bibliography", self,
								shortcut="Ctrl+B",
								statusTip="Manage bibliography",
								triggered=self.biblio)

		self.aboutAct = QAction(QIcon(":/images/help_about.png"),
								"&About", self,
								statusTip="Show About box",
								triggered=self.showAbout)

	def createMenus(self):
		"""
		Create Qt menus.
		"""
		self.fileMenu = self.menuBar().addMenu("&File")
		self.fileMenu.addAction(self.saveAct)
		self.separatorAct = self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exportAct)
		self.fileMenu.addAction(self.exportSelAct)
		self.fileMenu.addAction(self.exportAllAct)
		self.separatorAct = self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exitAct)

		self.menuBar().addSeparator()
		self.dataMenu = self.menuBar().addMenu("&Contents")
		self.dataMenu.addAction(self.CatAct)
		self.dataMenu.addAction(self.ExpAct)
		self.dataMenu.addAction(self.TagAct)
		self.dataMenu.addSeparator()
		self.dataMenu.addAction(self.biblioAct)

		#self.menuBar().addSeparator()
		#self.optionMenu = self.menuBar().addMenu("&Options")
		#self.optionMenu.addAction(self.optionsAct)
		#self.optionMenu.addAction(self.plotOptionsAct)
		#self.optionMenu.addAction(self.configOptionsAct)

		self.menuBar().addSeparator()
		self.helpMenu = self.menuBar().addMenu("&Help")
		self.helpMenu.addAction(self.aboutAct)
	
	def createLayout(self):
		pass

	
	
	
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
		
	def StatusBarMessage(self,message="abc",time=0):
		self.myStatusBar.showMessage(message, time)
		
	#def setStatusButton(self):
		#""" Function to set About Button
		#"""
		#self.StatusButton = QPushButton("Try", self)
		#self.StatusButton.move(0, 0)
		#self.StatusButton.clicked.connect(self.StatusBarMessage)
	
	def save(self):
		pyBiblioDB.commit()
		self.setWindowTitle("PyBiblio")
		self.StatusBarMessage("Changes saved")
		
	def export(self):
		#dialog to ask fname
		fname="temp.bib"
		bibexport.exportLast(fname)
		self.StatusBarMessage("Last fetched entries exported into %s"%fname)
	
	def exportSelection(self):
		#dialog to ask fname
		#retrieve selection
		bibexport.exportSelected(fname,rows)
		self.StatusBarMessage("Current selection exported into %s"%fname)
	
	def exportAll(self):
		#dialog to ask fname
		fname="all.bib"
		bibexport.exportAll(fname)
		self.StatusBarMessage("All entries saved into %s"%fname)
	
	def categories(self):
		rows=pyBiblioDB.extractParentcat(1)
		self.StatusBarMessage("categories triggered")
		#self.appLabel.setText(rows[0]['name'])
		#self.appLabel.show()
	
	def experiments(self):
		self.StatusBarMessage("experiments triggered")
	
	def tags(self):
		self.StatusBarMessage("tags triggered")
	
	def biblio(self):
		self.StatusBarMessage("biblio triggered")
		#abc=webInt.webInterf()
		#abc.loadInterfaces()
		#try:
			#tmp=abc.webSearch["inspire"].retrieveUrlFirst("Gariazzo:2015rra")
		#tmp=abc.webSearch["arxiv"].retrieveUrlFirst("1507.08204")
		#data=pyBiblioDB.prepareInsertEntry(tmp)
		#pyBiblioDB.insertEntry(data)
		#except:
			#print "errors occurred"
		#print pyBiblioDB.extractEntryByBibkey("1507.08204")
		#print abc.webSearch["inspire"].loadBibtexsForTex("/home/steog88/Dottorato/Latex/Articoli/1607_feature/")
		#print len(pyBiblioDB.extractEntries())
		self.StatusBarMessage("biblio done")

	
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
