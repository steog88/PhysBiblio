"""
Module with the classes and functions that manage the some dialog windows.

This file is part of the physbiblio package.
"""
import sys
from PySide2.QtCore import Qt
from PySide2.QtWidgets import \
	QDesktopWidget, QDialog, QGridLayout, QLabel, QLineEdit, \
	QPlainTextEdit, QPushButton, QVBoxLayout
import subprocess
import traceback
import ast

try:
	from physbiblio.config import pbConfig
	from physbiblio.gui.errorManager import pBGUILogger
	from physbiblio.gui.commonClasses import *
	from physbiblio.gui.basicDialogs import *
	from physbiblio.gui.catWindows import *
	from physbiblio.database import pBDB
	import physbiblio.gui.resourcesPyside2
except ImportError:
	print("Could not find physbiblio and its modules!")
	print(traceback.format_exc())

class configEditColumns(QDialog):
	"""Extend `QDialog` to ask the columns that must appear in the main table"""
	def __init__(self, parent = None, previous = None):
		"""
		Extend `QDialog.__init__` and create the form structure

		Parameters:
			parent: teh parent widget
			previous: list of columns which must appear
				as selected at the beginning
		"""
		super(configEditColumns, self).__init__(parent)
		self.excludeCols = [
			"crossref", "bibtex", "exp_paper", "lecture",
			"phd_thesis", "review", "proceeding", "book", "noUpdate"]
		self.moreCols = [
			"title", "author", "journal", "volume", "pages",
			"primaryclass", "booktitle", "reportnumber"]
		self.previousSelected = previous \
			if previous is not None \
			else pbConfig.params["bibtexListColumns"]
		self.initUI()

	def onCancel(self):
		"""Reject the output"""
		self.result	= False
		self.close()

	def onOk(self):
		"""Accept the output and prepare `self.selected`"""
		self.result = True
		self.selected = []
		for row in range(self.listSel.rowCount()):
			self.selected.append(self.listSel.item(row, 0).text())
		self.close()

	def initUI(self):
		"""
		Initialize the `MyDDTableWidget`s and their content,
		plus the buttons and labels
		"""
		self.gridlayout = QGridLayout()
		self.setLayout(self.gridlayout)

		self.items = []
		self.listAll = MyDDTableWidget(self, "Available columns")
		self.listSel = MyDDTableWidget(self, "Selected columns")
		self.gridlayout.addWidget(
			QLabel("Drag and drop items to order visible columns"),
			0, 0, 1, 2)
		self.gridlayout.addWidget(self.listAll, 1, 0)
		self.gridlayout.addWidget(self.listSel, 1, 1)

		self.allItems = pBDB.descriptions["entries"].keys() + self.moreCols
		self.selItems = self.previousSelected
		isel = 0
		iall = 0
		for col in self.selItems + \
				[i for i in self.allItems if i not in self.selItems]:
			if col in self.excludeCols:
				continue
			item = QTableWidgetItem(col)
			self.items.append(item)
			if col in self.selItems:
				self.listSel.insertRow(isel)
				self.listSel.setItem(isel, 0, item)
				isel += 1
			else:
				self.listAll.insertRow(iall)
				self.listAll.setItem(iall, 0, item)
				iall += 1

		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		self.gridlayout.addWidget(self.acceptButton, 2, 0)

		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		self.gridlayout.addWidget(self.cancelButton, 2, 1)

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
		folder = askDirName(parent = None, dir = self.textValues[ix][1].text(), title = "Directory for saving PDF files:")
		if folder.strip() != "":
			self.textValues[ix][1].setText(str(folder))

	def editFile(self, paramkey = "logFileName", text = "Name for the log file", filter = "*.log"):
		ix = pbConfig.paramOrder.index(paramkey)
		fname = askSaveFileName(parent = None, title = text, dir = self.textValues[ix][1].text(), filter = filter)
		if fname.strip() != "":
			self.textValues[ix][1].setText(str(fname))

	def editColumns(self):
		ix = pbConfig.paramOrder.index("bibtexListColumns")
		window = configEditColumns(self, ast.literal_eval(self.textValues[ix][1].text().strip()))
		window.exec_()
		if window.result:
			columns = window.selected
			self.textValues[ix][1].setText(str(columns))

	def editDefCats(self):
		ix = pbConfig.paramOrder.index("defaultCategories")
		selectCats = catsWindowList(parent = self, askCats = True, expButton = False, previous = ast.literal_eval(self.textValues[ix][1].text().strip()))
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
			if k == "bibtexListColumns":
				self.textValues.append([k, QPushButton(val)])
				self.textValues[-1][1].clicked.connect(self.editColumns)
			elif k == "pdfFolder":
				self.textValues.append([k, QPushButton(val)])
				self.textValues[-1][1].clicked.connect(self.editFolder)
			elif k == "loggingLevel":
				try:
					self.textValues.append([k, MyComboBox(self, pbConfig.loggingLevels, pbConfig.loggingLevels[int(val)])])
				except ValueError:
					pBGUILogger.warning("Invalid string for 'loggingLevel' param. Reset to default")
					self.textValues.append([k, MyComboBox(self, pbConfig.loggingLevels, pbConfig.loggingLevels[int(pbConfig.defaultsParams["loggingLevel"])])])
			elif k == "logFileName":
				self.textValues.append([k, QPushButton(val)])
				self.textValues[-1][1].clicked.connect(self.editFile)
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
				pBGUILogger.exception("Impossible to clear log file!")
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

		self.currLayout.addWidget(QLabel("This is the list of elements found.\nSelect the ones that you want to import:"))

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
					self.bibs[k]['bibpars'][f] = self.bibs[k]['bibpars'][f].replace("\n", " ")
				except KeyError:
					pass
		self.table_model = MyImportedTableModel(self, self.bibs, headers)
		self.addFilterInput("Filter entries", gridPos = (1, 0))
		self.setProxyStuff(0, Qt.AscendingOrder)

		self.finalizeTable(gridPos = (2, 0, 1, 2))

		i = 3
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

	def handleItemEntered(self, index):
		pass

	def cellClick(self, index):
		pass

	def cellDoubleClick(self, index):
		pass

class dailyArxivDialog(QDialog):
	"""create a window for the advanced import"""
	def __init__(self, parent = None):
		super(dailyArxivDialog, self).__init__(parent)
		self.initUI()

	def onCancel(self):
		self.result	= False
		self.close()

	def onOk(self):
		self.result	= True
		self.close()

	def updateCat(self, category):
		self.comboSub.clear()
		self.comboSub.addItems(["--"] + physBiblioWeb.webSearch["arxiv"].categories[category])

	def initUI(self):
		self.setWindowTitle('Browse arxiv daily')

		self.grid = QGridLayout()
		self.grid.setSpacing(1)

		##search
		self.grid.addWidget(QLabel("Select category: "), 0, 0)
		self.comboCat = MyComboBox(self,
			[""] + sorted(physBiblioWeb.webSearch["arxiv"].categories.keys()))
		self.comboCat.currentIndexChanged[str].connect(self.updateCat)
		self.grid.addWidget(self.comboCat, 0, 1)

		self.grid.addWidget(QLabel("Subcategory: "), 1, 0)
		self.comboSub = MyComboBox(self,
			[""])
		self.grid.addWidget(self.comboSub, 1, 1)

		# OK button
		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		self.grid.addWidget(self.acceptButton, 2, 0)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		self.grid.addWidget(self.cancelButton, 2, 1)

		self.setGeometry(100,100,400, 100)
		self.setLayout(self.grid)

		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

class dailyArxivSelect(advImportSelect):
	"""create a window for the advanced import"""
	def initUI(self):
		self.setWindowTitle('ArXiv daily listing - results')

		self.currLayout.setSpacing(1)

		self.currLayout.addWidget(QLabel("This is the list of elements found.\nSelect the ones that you want to import:"))

		headers = ["eprint", "type", "title", "author", "primaryclass"]
		self.table_model = MyImportedTableModel(self, self.bibs, headers, idName = "eprint")
		self.addFilterInput("Filter entries", gridPos = (1, 0))
		self.setProxyStuff(0, Qt.AscendingOrder)

		self.finalizeTable(gridPos = (2, 0, 1, 2))

		i = 3
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

		self.abstractArea = QTextEdit('Abastract', self)
		self.currLayout.addWidget(self.abstractArea, i + 3, 0, 4, 2)

	def cellClick(self, index):
		row = index.row()
		try:
			eprint = str(self.proxyModel.sibling(row, 0, index).data())
		except AttributeError:
			return
		if self.abstractFormulas is not None:
			a = self.abstractFormulas(self.parent(), self.bibs[eprint]["bibpars"]["abstract"], customEditor = self.abstractArea, statusMessages = False)
			a.doText()
