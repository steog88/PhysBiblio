"""Module with the classes and functions
that manage the some dialog windows.

This file is part of the physbiblio package.
"""
import traceback
import ast
import six
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import \
	QCheckBox, QComboBox, QDesktopWidget, QGridLayout, \
	QLineEdit, QPlainTextEdit, QProgressBar, QPushButton, QTableWidgetItem, \
	QTextEdit, QVBoxLayout

try:
	from physbiblio.config import pbConfig
	from physbiblio.errors import pBLogger
	from physbiblio.database import pBDB
	from physbiblio.webimport.webInterf import physBiblioWeb
	from physbiblio.gui.errorManager import pBGUILogger
	from physbiblio.gui.basicDialogs import \
		askDirName, askSaveFileName, askYesNo, infoMessage
	from physbiblio.gui.commonClasses import \
		PBComboBox, PBDDTableWidget, PBDialog, PBImportedTableModel, \
		PBLabel, PBTableView, PBTrueFalseCombo, ObjListWindow
	from physbiblio.gui.catWindows import CatsTreeWindow
	import physbiblio.gui.resourcesPyside2
except ImportError:
	print("Could not find physbiblio and its modules!")
	print(traceback.format_exc())


class ConfigEditColumns(PBDialog):
	"""Extend `PBDialog` to ask the columns
	that must appear in the main table
	"""

	def __init__(self, parent=None, previous=None):
		"""Extend `PBDialog.__init__` and create the form structure

		Parameters:
			parent: teh parent widget
			previous: list of columns which must appear
				as selected at the beginning
		"""
		super(ConfigEditColumns, self).__init__(parent)
		self.excludeCols = [
			"crossref", "bibtex", "exp_paper", "lecture",
			"phd_thesis", "review", "proceeding", "book", "noUpdate",
			"bibdict", "abstract"]
		self.moreCols = [
			"title", "author", "journal", "volume", "pages",
			"primaryclass", "booktitle", "reportnumber"]
		self.previousSelected = previous \
			if previous is not None \
			else pbConfig.params["bibtexListColumns"]
		self.selected = self.previousSelected
		self.initUI()

	def onCancel(self):
		"""Reject the output (set self.result to False and close)"""
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
		"""Initialize the `PBDDTableWidget`s and their content,
		plus the buttons and labels
		"""
		self.gridlayout = QGridLayout()
		self.setLayout(self.gridlayout)

		self.items = []
		self.listAll = PBDDTableWidget(self, "Available columns")
		self.listSel = PBDDTableWidget(self, "Selected columns")
		self.gridlayout.addWidget(
			PBLabel("Drag and drop items to order visible columns"),
			0, 0, 1, 2)
		self.gridlayout.addWidget(self.listAll, 1, 0)
		self.gridlayout.addWidget(self.listSel, 1, 1)

		self.allItems = list(pBDB.descriptions["entries"]) + self.moreCols
		self.selItems = self.previousSelected
		isel = 0
		iall = 0
		for col in self.selItems \
				+ [i for i in self.allItems if i not in self.selItems]:
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


class ConfigWindow(PBDialog):
	"""Create a window for editing the configuration settings"""

	def __init__(self, parent=None):
		"""Simple extension of `PBDialog.__init__`"""
		super(ConfigWindow, self).__init__(parent)
		self.textValues = []
		self.initUI()

	def onCancel(self):
		"""Reject the output (set self.result to False and close)"""
		self.result	= False
		self.close()

	def onOk(self):
		"""Accept the output (set self.result to True and close)"""
		self.result	= True
		self.close()

	def editPDFFolder(self):
		"""Open a dialog to select a new folder name
		for the PDF path, and save the result
		in the `ConfigWindow` interface
		"""
		ix = pbConfig.paramOrder.index("pdfFolder")
		folder = askDirName(
			parent=None,
			dir=self.textValues[ix][1].text(),
			title="Directory for saving PDF files:")
		if folder.strip() != "":
			self.textValues[ix][1].setText(str(folder))

	def editFile(self,
			paramkey="logFileName",
			text="Name for the log file",
			filter="*.log"):
		"""Open a dialog to select a new file name
		for a configuration parameter, and save the result
		in the `ConfigWindow` interface

		Parameters:
			paramkey: the parameter name in the configuration dictionary
			text: description in the file dialog
			filter: filter the folder content in the file dialog
		"""
		if paramkey not in pbConfig.paramOrder:
			pBLogger.warning("Invalid paramkey: '%s'"%paramkey)
			return
		ix = pbConfig.paramOrder.index(paramkey)
		fname = askSaveFileName(
			parent=None,
			title=text,
			dir=self.textValues[ix][1].text(),
			filter=filter)
		if fname.strip() != "":
			self.textValues[ix][1].setText(str(fname))

	def editColumns(self):
		"""Open a dialog to select and/or reorder the list of columns
		to show in the entries list, and save the result
		in the `ConfigWindow` interface
		"""
		ix = pbConfig.paramOrder.index("bibtexListColumns")
		window = ConfigEditColumns(self,
			ast.literal_eval(self.textValues[ix][1].text().strip()))
		window.exec_()
		if window.result:
			columns = window.selected
			self.textValues[ix][1].setText(str(columns))

	def editDefCats(self):
		"""Open a dialog to select a the default categories
		for the imported entries, and save the result
		in the `ConfigWindow` interface
		"""
		ix = pbConfig.paramOrder.index("defaultCategories")
		selectCats = CatsTreeWindow(
			parent=self,
			askCats=True,
			expButton=False,
			previous=ast.literal_eval(self.textValues[ix][1].text().strip()))
		selectCats.exec_()
		if selectCats.result == "Ok":
			self.textValues[ix][1].setText(str(self.selectedCats))

	def initUI(self):
		"""Create and fill the `QGridLayout`"""
		self.setWindowTitle('Configuration')

		grid = QGridLayout()
		self.grid = grid
		grid.setSpacing(1)

		i = 0
		for k in pbConfig.paramOrder:
			i += 1
			val = pbConfig.params[k] \
				if isinstance(pbConfig.params[k], six.string_types) \
				else str(pbConfig.params[k])
			grid.addWidget(
				PBLabel("%s (<i>%s</i>)"%(pbConfig.descriptions[k], k)),
				i-1, 0, 1, 2)
			if k == "bibtexListColumns":
				self.textValues.append([k, QPushButton(val)])
				self.textValues[-1][1].clicked.connect(self.editColumns)
			elif k == "pdfFolder":
				self.textValues.append([k, QPushButton(val)])
				self.textValues[-1][1].clicked.connect(self.editPDFFolder)
			elif k == "loggingLevel":
				try:
					self.textValues.append([k, PBComboBox(self,
						pbConfig.loggingLevels,
						pbConfig.loggingLevels[int(val)])
						])
				except (IndexError, ValueError):
					pBGUILogger.warning("Invalid string for 'loggingLevel' "
						+ "param. Reset to default")
					self.textValues.append([k,
						PBComboBox(self,
							pbConfig.loggingLevels,
							pbConfig.loggingLevels[
								int(pbConfig.defaultsParams["loggingLevel"])]
							)])
			elif k == "logFileName":
				self.textValues.append([k, QPushButton(val)])
				self.textValues[-1][1].clicked.connect(self.editFile)
			elif k == "defaultCategories":
				self.textValues.append([k, QPushButton(val)])
				self.textValues[-1][1].clicked.connect(self.editDefCats)
			elif pbConfig.specialTypes[k] == "boolean":
				self.textValues.append([k, PBTrueFalseCombo(self, val)])
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

		self.setGeometry(100, 100, 1000, 30*i)
		self.setLayout(grid)


class LogFileContentDialog(PBDialog):
	"""Create a window for showing the logFile content"""

	def __init__(self, parent=None):
		"""Instantiate class and create its widgets

		Parameter:
			parent: the parent widget
		"""
		PBDialog.__init__(self, parent)
		self.title = "Log File Content"
		self.initUI()

	def clearLog(self):
		"""Ask confirmation, then eventually clear
		the content of the log file
		"""
		if askYesNo("Are you sure you want to clear the log file?"):
			try:
				open(pbConfig.params["logFileName"], "w").close()
			except IOError:
				pBGUILogger.exception("Impossible to clear log file!")
			else:
				infoMessage("Log file cleared.")
				self.close()

	def initUI(self):
		"""Create window layout and buttons,
		read log file content and print it in the `QPlainTextEdit`
		"""
		self.setWindowTitle(self.title)

		grid = QVBoxLayout()
		grid.setSpacing(1)

		grid.addWidget(PBLabel("Reading %s"%pbConfig.params["logFileName"]))
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


class PrintText(PBDialog):
	"""Create a window for printing text of command line output"""

	stopped = Signal()

	def __init__(self,
			parent=None,
			title="",
			progressBar=True,
			totStr=None,
			progrStr=None,
			noStopButton=False,
			message=None):
		"""Constructor.
		Set some properties and create the GUI of the dialog

		Parameters:
			parent: the parent widget
			title: the window title. If an empty string,
				"Redirect print" will be used
			progressBar: True (default) if the widget must have a progress bar
			totStr: string to be searched in the printed text in order to
				obtain the number of total iterations to be processed.
				Used to set the progress bar value appropriately.
			progrStr: string to be searched in the printed text in order
				to obtain the iteration number.
				Used to set the progress bar value appropriately.
			noStopButton (default False): True if the widget must have
				a "stop" button to stop the iterations
			message: a text to be inserted as a `PBLabel` in the dialog
		"""
		super(PrintText, self).__init__(parent)
		self._wantToClose = False
		if title != "":
			self.title = title
		else:
			self.title = "Redirect print"
		self.setProgressBar = progressBar
		self.totString = totStr if totStr is not None else "emptyString"
		self.progressString = progrStr if progrStr is not None \
			else "emptyString"
		self.noStopButton = noStopButton
		self.message = message
		self.initUI()

	def keyPressEvent(self, e):
		"""Intercept press keys and only exit if escape is pressed
		when closing is enabled

		Parameters:
			e: the `PySide2.QtGui.QKeyEvent`
		"""
		if e.key() == Qt.Key_Escape and self._wantToClose:
			self.close()

	def closeEvent(self, event):
		"""Manage the `closeEvent` of the dialog.
		Reject unless `self._wantToClose` is True

		Parameter:
			event: a `QEvent`
		"""
		if self._wantToClose:
			super(PrintText, self).closeEvent(event)
		else:
			event.ignore()

	def initUI(self):
		"""Create the main `QTextEdit`, the buttons and the `QProgressBar`"""
		self.setWindowTitle(self.title)

		grid = QGridLayout()
		self.grid = grid
		grid.setSpacing(1)

		if self.message is not None and self.message.strip() != "":
			grid.addWidget(PBLabel("%s"%self.message))

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
		self.closeButton.clicked.connect(
			lambda: self.reject())
		self.closeButton.setDisabled(True)
		grid.addWidget(self.closeButton)

		self.setGeometry(100, 100, 600, 600)
		self.setLayout(grid)
		self.centerWindow()

	def appendText(self, text):
		"""Add the given text to the end of the `self.textEdit` content.
		If a `self.progressBar` is set, try to obtain
		the maximum and the current value,
		looking for the expected `self.totString` and `self.progressString`

		Parameter:
			text: the string to be appended
		"""
		if self.setProgressBar:
			try:
				if self.totString in text:
					tot = [int(s) for s in text.split() if s.isdigit()][0]
					self.progressBarMax(tot)
				elif self.progressString in text:
					curr = [int(s) for s in text.split() if s.isdigit()][0]
					self.progressBar.setValue(curr)
			except IndexError:
				pBLogger.warning(
					"PrintText.progressBar cannot work with float numbers")
		self.textEdit.moveCursor(QTextCursor.End)
		self.textEdit.insertPlainText(text)

	def progressBarMin(self, minimum):
		"""Set the minimum value for the progress bar

		Parameter:
			minimum (int or float): the value
		"""
		if self.setProgressBar:
			self.progressBar.setMinimum(minimum)

	def progressBarMax(self, maximum):
		"""Set the maximum value for the progress bar

		Parameter:
			maximum (int or float): the value
		"""
		if self.setProgressBar:
			self.progressBar.setMaximum(maximum)

	def stopExec(self):
		"""Stop the iterations through the `stopped` Signal
		and disable the `cancelButton`
		"""
		self.cancelButton.setDisabled(True)
		self.stopped.emit()

	def enableClose(self):
		"""Enable the close button and set `self._wantToClose` to True"""
		self._wantToClose = True
		self.closeButton.setEnabled(True)


class AdvancedImportDialog(PBDialog):
	"""create a window for the advanced import"""

	def __init__(self, parent=None):
		"""Simple extension of `PBDialog.__init__`"""
		super(AdvancedImportDialog, self).__init__(parent)
		self.initUI()

	def onCancel(self):
		"""Reject the output (set self.result to False and close)"""
		self.result	= False
		self.close()

	def onOk(self):
		"""Accept the output (set self.result to True and close)"""
		self.result	= True
		self.close()

	def initUI(self):
		"""Create and fill the `QGridLayout`"""
		self.setWindowTitle('Advanced import')

		grid = QGridLayout()
		self.grid = grid
		grid.setSpacing(1)

		##search
		grid.addWidget(PBLabel("Search string: "), 0, 0)
		self.searchStr = QLineEdit("")
		grid.addWidget(self.searchStr, 0, 1)

		grid.addWidget(PBLabel("Select method: "), 1, 0)
		self.comboMethod = PBComboBox(self,
			["INSPIRE-HEP", "arXiv", "DOI", "ISBN"],
			current="INSPIRE-HEP")
		grid.addWidget(self.comboMethod, 1, 1)

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
		self.centerWindow()


class AdvancedImportSelect(ObjListWindow):
	"""create a window for the advanced import"""

	def __init__(self, bibs={}, parent=None):
		"""Set some properties and call `initUI`

		Parameters:
			bibs: a dictionary containing the imported bibtex entries.
				Each element should be a dictionary containing at least
				a "bibpars" item, a dictionary with at least the keys
				["ID", "title", "author", "eprint", "doi"],
				and a boolean "exist" item.
			parent: the parent widget
		"""
		self.bibs = bibs
		super(AdvancedImportSelect, self).__init__(parent, gridLayout=True)
		self.checkBoxes = []
		self.initUI()

	def onCancel(self):
		"""Reject the output (set self.result to False and close)"""
		self.result	= False
		self.close()

	def onOk(self):
		"""Accept the output (set self.result to True and close)"""
		self.selected = self.tableModel.selectedElements
		self.result	= True
		self.close()

	def keyPressEvent(self, e):
		"""Intercept press keys and exit if escape is pressed

		Parameters:
			e: the `PySide2.QtGui.QKeyEvent`
		"""
		if e.key() == Qt.Key_Escape:
			self.result	= False
			self.close()

	def initUI(self):
		"""Create and fill the `QGridLayout`"""
		self.setWindowTitle('Advanced import - results')

		self.currLayout.setSpacing(1)

		self.currLayout.addWidget(PBLabel("This is the list of elements found."
			+ "\nSelect the ones that you want to import:"))

		headers = ["ID", "title", "author", "eprint", "doi"]
		for k in self.bibs.keys():
			try:
				self.bibs[k]['bibpars']["eprint"] = \
					self.bibs[k]['bibpars']["arxiv"]
			except KeyError:
				pass
			try:
				self.bibs[k]['bibpars']["author"] = \
					self.bibs[k]['bibpars']["authors"]
			except KeyError:
				pass
			for f in headers:
				try:
					self.bibs[k]['bibpars'][f] = \
						self.bibs[k]['bibpars'][f].replace("\n", " ")
				except KeyError:
					pass
		self.tableModel = PBImportedTableModel(self, self.bibs, headers)
		self.addFilterInput("Filter entries", gridPos=(1, 0))
		self.setProxyStuff(0, Qt.AscendingOrder)
		self.finalizeTable(gridPos=(2, 0, 1, 2))

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
		"""Does nothing"""
		pass

	def handleItemEntered(self, index):
		"""Does nothing"""
		pass

	def cellClick(self, index):
		"""Does nothing"""
		pass

	def cellDoubleClick(self, index):
		"""Does nothing"""
		pass


class DailyArxivDialog(PBDialog):
	"""create a window for the advanced import"""

	def __init__(self, parent=None):
		"""Simple extension of `PBDialog.__init__`"""
		super(DailyArxivDialog, self).__init__(parent)
		self.initUI()

	def onCancel(self):
		"""Reject the output (set self.result to False and close)"""
		self.result	= False
		self.close()

	def onOk(self):
		"""Accept the output (set self.result to True and close)"""
		self.result	= True
		self.close()

	def updateCat(self, category):
		"""Replace the current content of the `self.comboSub` combobox
		with the new list of subcategories of the given category

		Parameter:
			category: the name of the category in the
				`physBiblioWeb.webSearch["arxiv"].categories` dictionary
		"""
		self.comboSub.clear()
		self.comboSub.addItems(["--"] \
			+ physBiblioWeb.webSearch["arxiv"].categories[category])

	def initUI(self):
		"""Create and fill the `QGridLayout`"""
		self.setWindowTitle('Browse arxiv daily')

		self.grid = QGridLayout()
		self.grid.setSpacing(1)

		##combo boxes
		self.grid.addWidget(PBLabel("Select category: "), 0, 0)
		self.comboCat = PBComboBox(self,
			[""] + sorted(physBiblioWeb.webSearch["arxiv"].categories.keys()))
		self.comboCat.currentIndexChanged[str].connect(self.updateCat)
		self.grid.addWidget(self.comboCat, 0, 1)

		self.grid.addWidget(PBLabel("Subcategory: "), 1, 0)
		self.comboSub = PBComboBox(self, [""])
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

		self.setLayout(self.grid)

		self.setGeometry(100, 100, 400, 100)
		self.centerWindow()


class DailyArxivSelect(AdvancedImportSelect):
	"""create a window for the advanced import"""

	def initUI(self):
		"""Initialize the widget content, with the buttons and labels"""
		self.setWindowTitle('ArXiv daily listing - results')

		self.currLayout.setSpacing(1)

		self.currLayout.addWidget(
			PBLabel("This is the list of elements found.\n"
				+ "Select the ones that you want to import:"))

		headers = ["eprint", "type", "title", "author", "primaryclass"]
		self.tableModel = PBImportedTableModel(self,
			self.bibs,
			headers + ["abstract"],
			idName="eprint")
		self.addFilterInput("Filter entries", gridPos=(1, 0))
		self.setProxyStuff(0, Qt.AscendingOrder)

		self.finalizeTable(gridPos=(2, 0, 1, 2))

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

		self.abstractArea = QTextEdit('Abstract', self)
		self.currLayout.addWidget(self.abstractArea, i + 3, 0, 4, 2)

	def cellClick(self, index):
		"""Click action

		Parameter:
			index: a `QModelIndex` instance
		"""
		if not index.isValid():
			return
		row = index.row()
		try:
			eprint = str(self.proxyModel.sibling(row, 0, index).data())
		except AttributeError:
			pBLogger.debug("Data not valid", exc_info=True)
			return
		if "already existing" in eprint:
			eprint = eprint.replace(" - already existing", "")
		if hasattr(self, "abstractFormulas") and \
				self.abstractFormulas is not None:
			a = self.abstractFormulas(self.parent(),
				self.bibs[eprint]["bibpars"]["abstract"],
				customEditor=self.abstractArea,
				statusMessages=False)
			a.doText()
		else:
			pBLogger.debug("self.abstractFormulas not present in "
				+ "DailyArxivSelect. Eprint: %s"%eprint)
