#!/usr/bin/env python
import sys
from PySide.QtCore import *
from PySide.QtGui  import *
import subprocess
import traceback

try:
	#from physbiblio.database import *
	#from physbiblio.export import pBExport
	#import physbiblio.webimport.webInterf as webInt
	#from physbiblio.cli import cli as physBiblioCLI
	from physbiblio.config import pbConfig
	from physbiblio.gui.CommonClasses import *
	from physbiblio.gui.DialogWindows import *
	from physbiblio.gui.CatWindows import *
	from physbiblio.database import pBDB
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
try:
	if sys.version_info[0] < 3:
		import physbiblio.gui.Resources_pyside
	else:
		import physbiblio.gui.Resources_pyside3
except ImportError:
	print("Missing Resources_pyside: Run script update_resources.sh")

class configWindow(QDialog):
	"""create a window for editing the configuration settings"""
	def __init__(self, parent = None):
		super(configWindow, self).__init__(parent)
		self.textValues = []
		self.initUI()

	def onCancel(self):
		self.result	= False
		self.close()

	def onOk(self):
		self.result	= True
		self.close()

	def editFolder(self, paramkey = "pdfFolder"):
		ix = pbConfig.paramOrder.index(paramkey)
		folder = askDirName(parent = None, dir = pbConfig.params[paramkey], title = "Directory for saving PDF files:")
		if folder.strip() != "":
			self.textValues[ix][1].setText(str(folder))

	def editFile(self, paramkey, text, filter = ""):
		ix = pbConfig.paramOrder.index(paramkey)
		fname = askSaveFileName(parent = None, title = text, dir = pbConfig.params[paramkey], filter = filter)
		if fname.strip() != "":
			self.textValues[ix][1].setText(str(fname))

	def editColumns(self):
		ix = pbConfig.paramOrder.index("bibtexListColumns")
		window = configEditColumns(self)
		window.exec_()
		if window.result:
			columns = window.selected
			self.textValues[ix][1].setText(str(columns))

	def editDefCats(self):
		ix = pbConfig.paramOrder.index("defaultCategories")
		selectCats = catsWindowList(parent = self, askCats = True, expButton = False, previous = pbConfig.params["defaultCategories"])
		selectCats.exec_()
		if selectCats.result == "Ok":
			self.textValues[ix][1].setText(str(self.selectedCats))

	def initUI(self):
		self.setWindowTitle('Configuration')

		grid = QGridLayout()
		grid.setSpacing(1)

		i = 0
		for k in pbConfig.paramOrder:
			i += 1
			val = pbConfig.params[k] if type(pbConfig.params[k]) is str else str(pbConfig.params[k])
			grid.addWidget(QLabel("%s (<i>%s</i>)"%(pbConfig.descriptions[k], k)), i-1, 0, 1, 2)
			#grid.addWidget(QLabel("(%s)"%pbConfig.descriptions[k]), i-1, 1)
			if k == "bibtexListColumns":
				self.textValues.append([k, QPushButton(val)])
				self.textValues[-1][1].clicked.connect(self.editColumns)
			elif k == "pdfFolder":
				self.textValues.append([k, QPushButton(val)])
				self.textValues[-1][1].clicked.connect(self.editFolder)
			elif k == "mainDatabaseName":
				self.textValues.append([k, QPushButton(val)])
				self.textValues[-1][1].clicked.connect(lambda: self.editFile(k, "Name for the database file", filter = "*.db"))
			elif k == "loggingLevel":
				self.textValues.append([k, MyComboBox(self, ["0", "1", "2", "3"], val)])
			elif k == "logFileName":
				self.textValues.append([k, QPushButton(val)])
				self.textValues[-1][1].clicked.connect(lambda: self.editFile(k, "Name for the log file", filter = "*.log"))
			elif k == "defaultCategories":
				self.textValues.append([k, QPushButton(val)])
				self.textValues[-1][1].clicked.connect(self.editDefCats)
			elif pbConfig.specialTypes[k] == "boolean":
				self.textValues.append([k, MyTrueFalseCombo(self, val)])
			else:
				self.textValues.append([k, QLineEdit(val)])
			grid.addWidget(self.textValues[i-1][1], i-1, 2, 1, 2)

		# OK button
		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		#width = self.acceptButton.fontMetrics().boundingRect('OK').width() + 7
		#self.acceptButton.setMaximumWidth(width)
		grid.addWidget(self.acceptButton, i, 0)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		#width = self.cancelButton.fontMetrics().boundingRect('Cancel').width() + 7
		#self.cancelButton.setMaximumWidth(width)
		grid.addWidget(self.cancelButton, i, 1)

		self.setGeometry(100,100,1000, 30*i)
		self.setLayout(grid)

		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

class LogFileContentDialog(QDialog):
	"""create a window for the logFile content"""
	def __init__(self, parent = None):
		super(LogFileContentDialog, self).__init__(parent)
		self.title = "Log File Content"
		self.initUI()

	def clearLog(self):
		if askYesNo("Are you sure you want to clear the log file?"):
			try:
				open(pbConfig.params["logFileName"], "w").close()
			except IOError:
				pBGUIErrorManager("Impossible to clear log file!", trcbk = traceback, priority = 1)
			else:
				infoMessage("Log file cleared.")
				self.close()

	def initUI(self):
		self.setWindowTitle(self.title)

		grid = QVBoxLayout()
		grid.setSpacing(1)

		grid.addWidget(QLabel("Reading %s"%pbConfig.params["logFileName"]))
		try:
			with open(pbConfig.params["logFileName"]) as r:
				text = r.read()
		except IOError:
			text = "Impossible to read log file!"
			pBLogger.exception(text)
		self.textEdit = QPlainTextEdit(text)
		self.textEdit.setReadOnly(True)
		grid.addWidget(self.textEdit)

		self.closeButton = QPushButton('Close', self)
		self.closeButton.setAutoDefault(True)
		self.closeButton.clicked.connect(self.close)
		grid.addWidget(self.closeButton)

		self.clearButton = QPushButton('Clear log file', self)
		self.clearButton.clicked.connect(self.clearLog)
		grid.addWidget(self.clearButton)

		self.setGeometry(100, 100, 800, 800)
		self.setLayout(grid)

		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())