#!/usr/bin/env python
import sys
from PySide.QtCore import *
from PySide.QtGui  import *
import traceback

if sys.version_info[0] < 3:
	from StringIO import StringIO
else:
	from io import StringIO

try:
	#from physbiblio.database import *
	#from physbiblio.export import pBExport
	#import physbiblio.webimport.webInterf as webInt
	#from physbiblio.cli import cli as physBiblioCLI
	from physbiblio.config import pbConfig
	from physbiblio.gui.CommonClasses import *
	from physbiblio.errors import pBLogger, pBErrorManager
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

def askYesNo(message, title = "Question"):
	reply = QMessageBox.question(None, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
	if reply == QMessageBox.Yes:
		return True
	if reply == QMessageBox.No:
		return False

def askFileName(parent = None, title = "Filename to use:", filter = ""):
	reply = QFileDialog.getOpenFileName(parent, title, "", filter)
	return reply[0]

def askFileNames(parent = None, title = "Filename to use:", filter = ""):
	reply = QFileDialog.getOpenFileNames(parent, title, "", filter)
	return reply[0]

def askSaveFileName(parent = None, title = "Filename to use:", filter = "", dir = ""):
	reply = QFileDialog.getSaveFileName(parent, title, dir, filter, options = QFileDialog.DontConfirmOverwrite)
	return reply[0]

def askDirName(parent = None, title = "Directory to use:", dir = ""):
	reply = QFileDialog.getExistingDirectory(parent, title, dir, options = QFileDialog.ShowDirsOnly)
	return reply

def askGenericText(message, title, parent = None):
	reply = QInputDialog.getText(parent, title, message)
	return reply

def infoMessage(message, title = "Information"):
	reply = QMessageBox.information(None, title, message)

class configEditColumns(QDialog):
	def __init__(self, parent = None, previous = None):
		super(configEditColumns, self).__init__(parent)
		self.excludeCols = ["crossref", "bibtex", "exp_paper", "lecture", "phd_thesis", "review", "proceeding", "book", "noUpdate"]
		self.moreCols = ["title", "author", "journal", "volume", "pages", "primaryclass", "booktitle", "reportnumber"]
		self.previousSelected = previous if previous is not None else pbConfig.params["bibtexListColumns"]
		self.initUI()

	def onCancel(self):
		self.result	= False
		self.close()

	def onOk(self):
		self.result = True
		self.selected = []
		for row in range(self.listSel.rowCount()):
			self.selected.append(self.listSel.item(row, 0).text())
		self.close()

	def initUI(self):
		self.layout = QGridLayout()
		self.setLayout(self.layout)

		self.listAll = MyDDTableWidget("Available columns")
		self.listSel = MyDDTableWidget("Selected columns")
		self.layout.addWidget(QLabel("Drag and drop items to order visible columns"), 0, 0, 1, 2)
		self.layout.addWidget(self.listAll, 1, 0)
		self.layout.addWidget(self.listSel, 1, 1)

		self.allItems = pBDB.descriptions["entries"].keys() + self.moreCols
		self.selItems = self.previousSelected
		i=0
		for col in self.allItems:
			if col not in self.selItems and col not in self.excludeCols:
				item = QTableWidgetItem(col)
				self.listAll.insertRow(i)
				self.listAll.setItem(i, 0, item)
				i += 1
		for i, col in enumerate(self.selItems):
			item = QTableWidgetItem(col)
			self.listSel.insertRow(i)
			self.listSel.setItem(i, 0, item)

		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		self.layout.addWidget(self.acceptButton, 2, 0)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		self.layout.addWidget(self.cancelButton, 2, 1)

class printText(QDialog):
	"""create a window for printing text of command line output"""
	stopped = Signal()

	def __init__(self, parent = None, title = "", progressBar = True, totStr = None, progrStr = None, noStopButton = False):
		super(printText, self).__init__(parent)
		self.message = None
		if title != "":
			self.title = title
		else:
			self.title = "Redirect print"
		self.setProgressBar = progressBar
		self.noStopButton = noStopButton
		self._want_to_close = False
		self.totString = totStr if totStr is not None else "emptyString"
		self.progressString = progrStr if progrStr is not None else "emptyString"
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
		if self.noStopButton is not True:
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
			["INSPIRE-HEP", "arXiv", "DOI", "ISBN"],
			current = "INSPIRE-HEP")
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

class advImportSelect(objListWindow):
	"""create a window for the advanced import"""
	def __init__(self, bibs = [], parent = None):
		self.bibs = bibs
		super(advImportSelect, self).__init__(parent, gridLayout = True)
		self.checkBoxes = []
		self.initUI()

	def onCancel(self):
		self.result	= False
		self.close()

	def onOk(self):
		self.selected = self.table_model.selectedElements
		self.result	= True
		self.close()

	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Escape:
			self.result	= False
			self.close()

	def changeFilter(self, string):
		self.proxyModel.setFilterRegExp(str(string))

	def initUI(self):
		self.setWindowTitle('Advanced import - results')

		self.currLayout.setSpacing(1)

		self.currLayout.addWidget(QLabel("This is the list of elements found.\nSelect the ones that you want to import:\n"))

		headers = ["ID", "title", "author", "eprint", "doi"]
		for k in self.bibs.keys():
			try:
				self.bibs[k]['bibpars']["eprint"] = self.bibs[k]['bibpars']["arxiv"]
			except KeyError:
				pass
			try:
				self.bibs[k]['bibpars']["author"] = self.bibs[k]['bibpars']["authors"]
			except KeyError:
				pass
			for f in headers:
				try:
					self.bibs[k]['bibpars'][f] = self.bibs[k]['bibpars'][f].replace("\n", "")
				except KeyError:
					pass
		self.table_model = MyImportedTableModel(self, self.bibs, headers)
		self.addFilterInput("Filter entries")
		self.setProxyStuff(0, Qt.AscendingOrder)

		self.finalizeTable(gridPos = (1, 0, 1, 2))

		i = 2
		self.askCats = QCheckBox("Ask categories at the end?", self)
		self.askCats.toggle()
		self.currLayout.addWidget(self.askCats, i, 0)

		# OK button
		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		self.currLayout.addWidget(self.acceptButton, i + 1, 0)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		self.currLayout.addWidget(self.cancelButton, i + 2, 0)

	def triggeredContextMenuEvent(self, row, col, event):
		pass

	def cellClick(self, index):
		pass

	def cellDoubleClick(self, index):
		pass
