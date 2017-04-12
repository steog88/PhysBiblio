#!/usr/bin/env python
import sys
from PySide.QtCore import *
from PySide.QtGui  import *
import subprocess

try:
	from pybiblio.database import pBDB
	#import pybiblio.export as bibexport
	#import pybiblio.webimport.webInterf as webInt
	#from pybiblio.cli import cli as pyBiblioCLI
	from pybiblio.config import pbConfig
	from pybiblio.gui.DialogWindows import *
	from pybiblio.gui.CommonClasses import *
	from pybiblio.pdf import pBPDF
	from pybiblio.view import pBView
	from pybiblio.gui.ThreadElements import *
except ImportError:
	print("Could not find pybiblio and its contents: configure your PYTHONPATH!")
try:
	import pybiblio.gui.Resources_pyside
except ImportError:
	print("Missing Resources_pyside.py: Run script update_resources.sh")

def writeBibtexInfo(entry):
	infoText = ""
	infoText += "<u>%s</u>  (use with '<u>\cite{%s}</u>')<br/>"%(entry["bibkey"], entry["bibkey"])
	try:
		infoText += "<b>%s</b><br/>%s<br/>"%(entry["bibtexDict"]["author"], entry["bibtexDict"]["title"])
	except KeyError:
		pass
	try:
		infoText +=  "<i>%s %s (%s) %s</i><br/>"%(
			entry["bibtexDict"]["journal"],
			entry["bibtexDict"]["volume"],
			entry["bibtexDict"]["year"],
			entry["bibtexDict"]["pages"])
	except KeyError:
		pass
	infoText += "<br/>"
	for k in ["isbn", "doi", "arxiv", "ads", "inspire"]:
		try:
			infoText += "%s: <u>%s</u><br/>"%(pBDB.descriptions["entries"][k], entry[k]) if entry[k] is not None else ""
		except KeyError:
			pass
	return infoText

def editBibtex(parent, statusBarObject, editKey = None):
	if editKey is not None:
		edit = pBDB.bibs.getByKey(editKey)[0]
	else:
		edit = None
	newBibWin = editBibtexEntry(parent, bib = edit)
	newBibWin.exec_()
	data = {}
	if newBibWin.result is True:
		for k, v in newBibWin.textValues.items():
			try:
				s = "%s"%v.text()
			except AttributeError:
				s = "%s"%v.toPlainText()
			data[k] = s
		for k, v in newBibWin.checkValues.items():
			if v.isChecked():
				data[k] = 1
			else:
				data[k] = 0
		if data["bibkey"].strip() != "" and data["bibtex"].strip() != "":
			if "bibkey" in data.keys():
				print("[GUI] Updating bibtex %s..."%data["bibkey"])
				pBDB.bibs.update(data, data["bibkey"])
			else:
				pBDB.bibs.insert(data)
			message = "Bibtex entry saved"
			statusBarObject.setWindowTitle("PyBiblio*")
			try:
				parent.top.recreateTable()
			except:
				pass
		else:
			infoMessage("ERROR: empty bibtex and/or bibkey!")
	else:
		message = "No modifications to bibtex entry"
	try:
		statusBarObject.StatusBarMessage(message)
	except:
		pass

def deleteBibtex(parent, statusBarObject, bibkey):
	if askYesNo("Do you really want to delete this bibtex entry (bibkey = '%s')?"%(bibkey)):
		pBDB.bibs.delete(bibkey)
		statusBarObject.setWindowTitle("PyBiblio*")
		message = "Bibtex entry deleted"
		try:
			parent.top.recreateTable()
		except:
			pass
	else:
		message = "Nothing changed"
	try:
		statusBarObject.StatusBarMessage(message)
	except:
		pass

class bibtexWindow(QFrame):
	def __init__(self, parent = None):
		super(bibtexWindow, self).__init__(parent)
		self.parent = parent

		self.currLayout = QHBoxLayout()
		self.setLayout(self.currLayout)

		self.text = QTextEdit("")
		font = QFont()
		font.setPointSize(pbConfig.params["bibListFontSize"])
		self.text.setFont(font)

		self.currLayout.addWidget(self.text)

class bibtexInfo(QFrame):
	def __init__(self, parent = None):
		super(bibtexInfo, self).__init__(parent)
		self.parent = parent

		self.currLayout = QHBoxLayout()
		self.setLayout(self.currLayout)

		self.text = QTextEdit("")
		font = QFont()
		font.setPointSize(pbConfig.params["bibListFontSize"])
		self.text.setFont(font)

		self.currLayout.addWidget(self.text)

class bibtexList(QFrame):
	def __init__(self, parent = None, bibs = None):
		#table dimensions
		self.columns = pbConfig.params["bibtexListColumns"]
		self.colcnt = len(self.columns)
		self.colContents = []
		for j in range(self.colcnt):
			self.colContents.append(self.columns[j])
		self.colContents.append("pdf")
		self.colContents.append("modify")
		self.colContents.append("delete")

		super(bibtexList, self).__init__(parent)
		self.parent = parent

		self.currLayout = QHBoxLayout()
		self.setLayout(self.currLayout)

		if bibs is not None:
			self.bibs = bibs
		else:
			self.bibs = None
		self.createTable()

	def createTable(self):
		if self.bibs is None:
			self.bibs = pBDB.bibs.getAll()
		rowcnt = len(self.bibs)

		#table settings and header
		self.setTableSize(rowcnt, self.colcnt+3)
		self.tablewidget.setHorizontalHeaderLabels(self.columns + ["PDF", "Modify", "Delete"])

		#table content
		for i in range(rowcnt):
			self.loadRow(i)

		self.finalizeTable()

	def refillTable(self, bibs = None):
		self.tablewidget.clearContents()
		if bibs is None:
			self.bibs = pBDB.bibs.getAll()
		else:
			self.bibs = bibs
		rowcnt = len(self.bibs)

		#table settings and header
		if self.rows > rowcnt:
			for i in range(rowcnt, self.rows+1):
				self.tablewidget.removeRow(i)
		elif self.rows < rowcnt:
			for i in range(self.rows, rowcnt+1):
				self.tablewidget.insertRow(q)

		#table content
		for i in range(rowcnt):
			self.loadRow(i)

		self.finalizeTable()
	
	def loadRow(self, r):
		for j in range(self.colcnt):
			if self.bibs[r][self.columns[j]] is not None:
				string = str(self.bibs[r][self.columns[j]])
			else:
				string = ""
			item = QTableWidgetItem(string)
			item.setFlags(Qt.ItemIsEnabled)
			self.tablewidget.setItem(r, j, item)
		self.addPdfCell(r, self.colcnt, self.bibs[r]["bibkey"])
		self.addEditDeleteCells(r, self.colcnt+1)

	def addImageCell(self, row, col, imagePath):
		"""create a cell containing an image"""
		pic = QPixmap(imagePath).scaledToHeight(self.tablewidget.rowHeight(row)*0.8)
		img = QLabel(self)
		img.setPixmap(pic)
		self.tablewidget.setCellWidget(row, col, img)

	def addPdfCell(self, row, col, key):
		"""create icons for edit and delete"""
		if len(pBPDF.getExisting(key))>0:
			self.addImageCell(row, col, ":/images/application-pdf.png")
		else:
			item = QTableWidgetItem("no PDF")
			item.setFlags(Qt.ItemIsEnabled)
			self.tablewidget.setItem(row, col, item)

	def addEditDeleteCells(self, row, col):
		"""create icons for edit and delete"""
		self.addImageCell(row, col, ":/images/edit.png")
		self.addImageCell(row, col + 1, ":/images/delete.png")

	def cellClick(self, row, col):
		bibkey = self.tablewidget.item(row, 0).text()
		entry = pBDB.bibs.getByBibkey(bibkey)[0]
		self.parent.bottomLeft.text.setText(entry["bibtex"])
		self.parent.bottomRight.text.setText(writeBibtexInfo(entry))
		if self.colContents[col] == "modify":
			editBibtex(self.parent, self.parent, bibkey)
		elif self.colContents[col] == "delete":
			deleteBibtex(self.parent, self.parent, bibkey)

	def cellDoubleClick(self, row, col):
		bibkey = self.tablewidget.item(row, 0).text()
		entry = pBDB.bibs.getByBibkey(bibkey)[0]
		self.parent.bottomLeft.text.setText(entry["bibtex"])
		self.parent.bottomRight.text.setText(writeBibtexInfo(entry))
		if self.colContents[col] == "doi" and entry["doi"] is not None and entry["doi"] != "":
			pBView.openLink(bibkey,"doi")
		elif self.colContents[col] == "arxiv" and entry["arxiv"] is not None and entry["arxiv"] != "":
			pBView.openLink(bibkey,"arxiv")
		elif self.colContents[col] == "pdf":
			ask = askPdfAction(self, bibkey, entry["arxiv"], entry["doi"])
			ask.exec_()
			if ask.result == "openArxiv":
				self.parent.StatusBarMessage("opening arxiv PDF...")
				pBPDF.openFile(bibkey, "arxiv")
			elif ask.result == "openDoi":
				self.parent.StatusBarMessage("opening doi PDF...")
				pBPDF.openFile(bibkey, "doi")
			elif ask.result == "downloadArxiv":
				self.parent.StatusBarMessage("downloading PDF from arxiv...")
				self.downArxiv_thr = thread_downloadArxiv(bibkey)
				self.connect(self.downArxiv_thr, SIGNAL("finished()"), self.downloadArxivDone)
				self.downArxiv_thr.start()
			elif ask.result == "delArxiv":
				if askYesNo("Do you really want to delete the arxiv PDF file for entry %s?"%bibkey):
					self.parent.StatusBarMessage("deleting arxiv PDF file...")
					pBPDF.removeFile(bibkey, "arxiv")
					self.parent.reloadMainContent()
			elif ask.result == "delDoi":
				if askYesNo("Do you really want to delete the DOI PDF file for entry %s?"%bibkey):
					self.parent.StatusBarMessage("deleting DOI PDF file...")
					pBPDF.removeFile(bibkey, "doi")
					self.parent.reloadMainContent()
			elif ask.result == "addDoi":
				newpdf = askFileName(self, "Where is the published PDF located?", "Select file")
				if newpdf != "" and os.path.isfile(newpdf):
					if pBPDF.copyNewFile(bibkey, newpdf, "doi"):
						infoMessage("PDF successfully copied!")
			elif ask.result == False:
				self.parent.StatusBarMessage("Nothing to do...")

	def downloadArxivDone(self):
		self.parent.sendMessage("Arxiv download completed!")
		self.parent.done()
		self.parent.reloadMainContent()

	def setTableSize(self, rows, cols):
		"""set number of rows and columns"""
		self.rows = rows
		self.cols = cols
		self.tablewidget = QTableWidget(rows, cols)
		vheader = QHeaderView(Qt.Orientation.Vertical)
		vheader.setResizeMode(QHeaderView.Interactive)
		self.tablewidget.setVerticalHeader(vheader)
		hheader = QHeaderView(Qt.Orientation.Horizontal)
		hheader.setResizeMode(QHeaderView.Interactive)
		self.tablewidget.setHorizontalHeader(hheader)

	def finalizeTable(self):
		"""resize the table to fit the contents, connect click and doubleclick functions, add layout"""
		font = QFont()
		font.setPointSize(pbConfig.params["bibListFontSize"])
		self.tablewidget.setFont(font)

		self.tablewidget.resizeColumnsToContents()
		self.tablewidget.resizeRowsToContents()

		self.tablewidget.cellClicked.connect(self.cellClick)
		self.tablewidget.cellDoubleClicked.connect(self.cellDoubleClick)

		self.currLayout.addWidget(self.tablewidget)

	def recreateTable(self, bibs = None):
		"""delete previous table widget and create a new one"""
		if bibs is not None:
			self.bibs = bibs
		else:
			self.bibs = pBDB.bibs.getAll()
		o = self.layout().takeAt(0)
		o.widget().deleteLater()
		self.createTable()

class editBibtexEntry(editObjectWindow):
	"""create a window for editing or creating a bibtex entry"""
	def __init__(self, parent = None, bib = None):
		super(editBibtexEntry, self).__init__(parent)
		self.bibtexEditLines = 8
		if bib is None:
			self.data = {}
			for k in pBDB.tableCols["entries"]:
				self.data[k] = ""
		else:
			self.data = bib
		self.checkValues = {}
		self.checkboxes = ["exp_paper", "lecture", "phd_thesis", "review", "proceeding", "book", "toBeUpdated"]
		self.createForm()

	def createForm(self):
		self.setWindowTitle('Edit bibtex entry')

		i = 0
		for k in pBDB.tableCols["entries"]:
			val = self.data[k]
			if k != "bibtex" and k not in self.checkboxes:
				i += 1
				self.currGrid.addWidget(QLabel(k), int((i+1-(i+i)%2)/2)*2-1, ((1+i)%2)*2)
				self.currGrid.addWidget(QLabel("(%s)"%pBDB.descriptions["entries"][k]),  int((i+1-(i+i)%2)/2)*2-1, ((1+i)%2)*2+1)
				self.textValues[k] = QLineEdit(str(val))
				if k == "bibkey" and val != "":
					self.textValues[k].setEnabled(False)
				self.currGrid.addWidget(self.textValues[k], int((i+1-(i+i)%2)/2)*2, ((1+i)%2)*2, 1, 2)

		#bibtex text editor
		i += 1 + i%2
		k = "bibtex"
		self.currGrid.addWidget(QLabel(k), int((i+1-(i+i)%2)/2)*2-1, ((1+i)%2)*2)
		self.currGrid.addWidget(QLabel("(%s)"%pBDB.descriptions["entries"][k]),  int((i+1-(i+i)%2)/2)*2-1, ((1+i)%2)*2+1)
		self.textValues[k] = QPlainTextEdit(self.data[k])
		self.currGrid.addWidget(self.textValues[k], int((i+1-(i+i)%2)/2)*2, 0, self.bibtexEditLines, 2)

		j = 0
		for k in pBDB.tableCols["entries"]:
			val = self.data[k]
			if k in self.checkboxes:
				j += 2
				self.currGrid.addWidget(QLabel(k), int((i+1-(i+i)%2)/2)*2 + j - 2, 2)
				self.currGrid.addWidget(QLabel("(%s)"%pBDB.descriptions["entries"][k]),  int((i+1-(i+i)%2)/2)*2 + j - 1, 2, 1, 2)
				self.checkValues[k] = QCheckBox("", self)
				if val == 1:
					self.checkValues[k].toggle()
				self.currGrid.addWidget(self.checkValues[k], int((i+1-(i+i)%2)/2)*2 + j - 2, 3)
		
		self.currGrid.addWidget(self.textValues["bibtex"], int((i+1-(i+i)%2)/2)*2, 0, j, 2)

		# OK button
		i += j
		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		self.currGrid.addWidget(self.acceptButton, i*2+1, 0,1,2)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		self.currGrid.addWidget(self.cancelButton, i*2+1, 2,1,2)

		self.setGeometry(100,100,400, 25*i)
		self.centerWindow()

class askPdfAction(askAction):
	def __init__(self, parent = None, key = "", arxiv = None, doi = None):
		super(askPdfAction, self).__init__(parent)
		self.message = "What to do with the PDF of this entry (%s)?"%(key)
		self.possibleActions = []
		if pBPDF.checkFile(key, "arxiv"):
			self.possibleActions.append(["Open arxiv PDF", self.onOpenArxiv])
			self.possibleActions.append(["Delete arxiv PDF", self.onDelArxiv])
		elif arxiv is not None and arxiv != "":
			self.possibleActions.append(["Download arxiv", self.onDownloadArxiv])
		if pBPDF.checkFile(key, "doi"):
			self.possibleActions.append(["Open DOI PDF", self.onOpenDoi])
			self.possibleActions.append(["Delete DOI PDF", self.onDelDoi])
		elif doi is not None and doi != "":
			self.possibleActions.append(["Assign DOI PDF", self.onAddDoi])
		self.initUI()

	def onOpenArxiv(self):
		self.result	= "openArxiv"
		self.close()

	def onDelArxiv(self):
		self.result	= "delArxiv"
		self.close()

	def onOpenDoi(self):
		self.result	= "openDoi"
		self.close()

	def onDelDoi(self):
		self.result	= "delDoi"
		self.close()

	def onDownloadArxiv(self):
		self.result	= "downloadArxiv"
		self.close()

	def onAddDoi(self):
		self.result	= "addDoi"
		self.close()
