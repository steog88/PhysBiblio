#!/usr/bin/env python
import sys
from PySide.QtCore import *
from PySide.QtGui  import *
import subprocess

try:
	#from pybiblio.database import *
	#from pybiblio.export import pBExport
	#import pybiblio.webimport.webInterf as webInt
	#from pybiblio.cli import cli as pyBiblioCLI
	from pybiblio.config import pbConfig
	from pybiblio.gui.CommonClasses import *
except ImportError:
	print("Could not find pybiblio and its contents: configure your PYTHONPATH!")
try:
	import pybiblio.gui.Resources_pyside
except ImportError:
	print("Missing Resources_pyside.py: Run script update_resources.sh")

def askYesNo(message, title = "Question"):
	reply = QMessageBox.question(None, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
	if reply == QMessageBox.Yes:
		return True
	if reply == QMessageBox.No:
		return False

def askFileName(parent = None, title = "Filename to use:", filter = ""):
	reply = QFileDialog.getOpenFileName(parent, title, "", filter)
	return reply[0]

def askSaveFileName(parent = None, title = "Filename to use:", filter = ""):
	reply = QFileDialog.getSaveFileName(parent, title, "", filter, options = QFileDialog.DontConfirmOverwrite)
	return reply[0]

def askDirName(parent = None, title = "Directory to use:", filter = ""):
	reply = QFileDialog.getExistingDirectory(parent, title, "", filter, options=QFileDialog.ShowDirsOnly)
	return reply

def askGenericText(message, title, parent = None):
	reply = QInputDialog.getText(parent, title, message)
	return reply[0]

def infoMessage(message, title = "Information"):
	reply = QMessageBox.information(None, title, message)

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

class askAction(QDialog):
	"""create a window for asking an action: modify, delete, view...?"""
	def __init__(self, parent = None):
		super(askAction, self).__init__(parent)
		self.message = None
		self.possibleActions = [
			["Modify", self.onModify],
			["Delete", self.onDelete]
			]

	def keyPressEvent(self, e):		
		if e.key() == Qt.Key_Escape:
			self.close()

	def onCancel(self):
		self.result	= False
		self.close()

	def onModify(self):
		self.result = "modify"
		self.close()

	def onDelete(self):
		self.result = "delete"
		self.close()

	def initUI(self):
		self.setWindowTitle('Select action')

		grid = QGridLayout()
		grid.setSpacing(1)

		i = 0
		if self.message is not None:
			grid.addWidget(QLabel("%s"%self.message), 0, 0)
			i += 1

		for act in self.possibleActions:
			i += 1
			button = QPushButton(act[0], self)
			button.clicked.connect(act[1])
			grid.addWidget(button, i, 0)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		grid.addWidget(self.cancelButton, i+1, 0)

		self.setGeometry(100,100,300, 30*i)
		self.setLayout(grid)

		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

class printText(QDialog):
	"""create a window for printing text of command line output"""
	stopped = Signal()

	def __init__(self, parent = None, title = "", progressBar = True, totStr = "[DB] searchOAIUpdates will process ", progrStr = "%) - looking for update: "):
		super(printText, self).__init__(parent)
		self.message = None
		if title != "":
			self.title = title
		else:
			self.title = "Redirect print"
		self.setProgressBar = progressBar
		self._want_to_close = False
		self.totString = totStr
		self.progressString = progrStr
		self.initUI()

	def closeEvent(self, evnt):
		if self._want_to_close:
			super(printText, self).closeEvent(evnt)
		else:
			evnt.ignore()
			#self.setWindowState(QtCore.Qt.WindowMinimized)

	def initUI(self):
		self.setWindowTitle(self.title)

		grid = QGridLayout()
		grid.setSpacing(1)

		i = 0
		if self.message is not None:
			grid.addWidget(QLabel("%s"%self.message), 0, 0)
			i += 1

		#main text
		self.textEdit = QTextEdit()
		grid.addWidget(self.textEdit)

		if self.setProgressBar:
			self.progressBar = QProgressBar(self)
			grid.addWidget(self.progressBar)

		# cancel button...should learn how to connect it with a thread kill
		self.cancelButton = QPushButton('Stop', self)
		self.cancelButton.clicked.connect(self.stopExec)
		self.cancelButton.setAutoDefault(True)
		grid.addWidget(self.cancelButton)
		self.closeButton = QPushButton('Close', self)
		self.closeButton.clicked.connect(self.reject)
		self.closeButton.setDisabled(True)
		grid.addWidget(self.closeButton)

		self.setGeometry(100,100,600, 600)
		self.setLayout(grid)

		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def append_text(self,text):
		if self.setProgressBar:
			if self.totString in text:
				tot = [int(s) for s in text.split() if s.isdigit()][0]
				self.progressBarMax(tot)
			elif self.progressString in text:
				curr = [int(s) for s in text.split() if s.isdigit()][0]
				self.progressBar.setValue(curr)
		self.textEdit.moveCursor(QTextCursor.End)
		self.textEdit.insertPlainText( text )

	def progressBarMin(self, minimum):
		if self.setProgressBar:
			self.progressBar.setMinimum(minimum)

	def progressBarMax(self, maximum):
		if self.setProgressBar:
			self.progressBar.setMaximum(maximum)

	def stopExec(self):
		self.cancelButton.setDisabled(True)
		self.stopped.emit()

	def enableClose(self):
		self._want_to_close = True
		self.closeButton.setEnabled(True)

class searchReplaceDialog(QDialog):
	"""create a window for search and replace"""
	def __init__(self, parent = None):
		super(searchReplaceDialog, self).__init__(parent)
		self.initUI()

	def onCancel(self):
		self.result	= False
		self.close()

	def onOk(self):
		self.result	= True
		self.close()

	def initUI(self):
		self.setWindowTitle('Search and replace')

		grid = QGridLayout()
		grid.setSpacing(1)

		#search
		grid.addWidget(QLabel("Search: "), 0, 0)
		self.searchEdit = QLineEdit("")
		grid.addWidget(self.searchEdit, 0, 1)

		#replace
		grid.addWidget(QLabel("Replace with: "), 1, 0)
		self.replaceEdit = QLineEdit("")
		grid.addWidget(self.replaceEdit, 1, 1)

		# OK button
		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		grid.addWidget(self.acceptButton, 2, 0)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		grid.addWidget(self.cancelButton, 2, 1)

		self.setGeometry(100,100,400, 100)
		self.setLayout(grid)

		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

class advImportDialog(QDialog):
	"""create a window for the advanced import"""
	def __init__(self, parent = None):
		super(advImportDialog, self).__init__(parent)
		self.initUI()

	def onCancel(self):
		self.result	= False
		self.close()

	def onOk(self):
		self.result	= True
		self.close()

	def initUI(self):
		self.setWindowTitle('Advanced import')

		grid = QGridLayout()
		grid.setSpacing(1)

		##search
		grid.addWidget(QLabel("Select method: "), 0, 0)
		self.comboMethod = MyComboBox(self,
			["Inspire", "arXiv", "DOI", "ISBN"],
			current = "Inspire")
		grid.addWidget(self.comboMethod, 0, 1)

		grid.addWidget(QLabel("Search string: "), 1, 0)
		self.searchStr = QLineEdit("")
		grid.addWidget(self.searchStr, 1, 1)

		# OK button
		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		grid.addWidget(self.acceptButton, 2, 0)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		grid.addWidget(self.cancelButton, 2, 1)

		self.setGeometry(100,100,400, 100)
		self.setLayout(grid)
		self.searchStr.setFocus()

		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

class advImportSelect(QDialog):
	"""create a window for the advanced import"""
	def __init__(self, bibs=[], parent = None):
		super(advImportSelect, self).__init__(parent)
		self.bibs = bibs
		self.oneNew = False
		self.checkBoxes = []
		self.initUI()

	def onCancel(self):
		self.result	= False
		self.close()

	def onOk(self):
		self.result	= True
		self.close()

	def initUI(self):
		self.setWindowTitle('Advanced import - results')

		grid = QGridLayout()
		grid.setSpacing(1)

		grid.addWidget(QLabel("This is the list of elements found.\nSelect the ones that you want to import:\n"), 0, 0, 1, 2)
		##search
		i = 0
		for bk, elDic in self.bibs.items():
			el = elDic["bibpars"]
			if elDic["exist"] is False:
				self.checkBoxes.append(QCheckBox(bk, self))
				self.checkBoxes[i].toggle()
				grid.addWidget(self.checkBoxes[i], i+1, 0)
				try:
					title = el["title"]
				except:
					title = "Title not found"
				try:
					authors = el["author"]
				except:
					authors = "Authors not found"
				try:
					arxiv = el["arxiv"]
				except:
					try:
						arxiv = el["eprint"]
					except:
						arxiv = "arXiv number not found"
				grid.addWidget(QLabel("%s\n%s\n%s"%(title, authors, arxiv)), i+1, 1)
				self.oneNew = True
			else:
				self.checkBoxes.append(QCheckBox(bk, self))
				self.checkBoxes[i].setDisabled(True)
				grid.addWidget(self.checkBoxes[i], i+1, 0)
				grid.addWidget(QLabel("Already existing"), i+1, 1)
			i += 1

		i += 2
		grid.addWidget(QLabel("\n"), i-1, 1)
		if self.oneNew:
			grid.addWidget(QLabel("Ask categories at the end?"), i, 1)
			self.askCats = QCheckBox("", self)
			self.askCats.toggle()
			grid.addWidget(self.askCats, i, 0)

			# OK button
			self.acceptButton = QPushButton('OK', self)
			self.acceptButton.clicked.connect(self.onOk)
			grid.addWidget(self.acceptButton, i+1, 0)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		grid.addWidget(self.cancelButton, i+1, 1)

		self.setGeometry(100,100,400, 100)
		self.setLayout(grid)

		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())
