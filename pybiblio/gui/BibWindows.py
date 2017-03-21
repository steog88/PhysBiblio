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

def editExperiment(parent, statusBarObject, editIdExp = None):
	#if editIdExp is not None:
		#edit = pBDB.exps.getDictByID(editIdExp)
	#else:
		#edit = None
	#newExpWin = editExp(parent, exp = edit)
	#newExpWin.exec_()
	#data = {}
	#if newExpWin.result:
		#for k, v in newExpWin.textValues.items():
			#s = "%s"%v.text()
			#data[k] = s
		#if data["bibkey"].strip() != "" and data["bibtex"].strip() != "":
			#if "bibkey" in data.keys():
				#print("[GUI] Updating experiment %s..."%data["bibkey"])
				#pBDB.exps.update(data, data["idExp"])
			#else:
				#pBDB.exps.insert(data)
			#message = "Experiment saved"
			#statusBarObject.setWindowTitle("PyBiblio*")
			#try:
				#parent.recreateTable()
			#except:
				#pass
		#else:
			#message = "ERROR: empty experiment name"
	#else:
		#message = "No modifications to bibtex entry"
	#try:
		#statusBarObject.StatusBarMessage(message)
	#except:
		pass

def deleteBibtex(parent, statusBarObject, bibkey):
	if askYesNo("Do you really want to delete this bibtex entry (bibkey = '%s')?"%(bibkey)):
		pBDB.exps.delete(bibkey)
		statusBarObject.setWindowTitle("PyBiblio*")
		message = "Bibtex entry deleted"
		try:
			parent.recreateTable()
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
		self.tablewidget.setHorizontalHeaderLabels(self.columns + ["Modify", "Delete"])

		#table content
		for i in range(rowcnt):
			for j in range(self.colcnt):
				if self.bibs[i][self.columns[j]] is not None:
					string = str(self.bibs[i][self.columns[j]])
				else:
					string = ""
				item = QTableWidgetItem(string)
				item.setFlags(Qt.ItemIsEnabled)
				self.tablewidget.setItem(i, j, item)
			self.addPdfCell(i, self.colcnt, self.bibs[i]["bibkey"])
			self.addEditDeleteCells(i, self.colcnt+1)

		self.finalizeTable()

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
		#if self.colContents[col] == "modify":
			#editExperiment(self, self.parent, bibkey)
		#elif self.colContents[col] == "delete":
			#deleteExperiment(self, self.parent, bibkey)

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
				pBPDF.downloadArxiv(bibkey)
				self.parent.StatusBarMessage("...done!")
			elif ask.result == "delArxiv":
				if askYesNo("Do you really want to delete the arxiv PDF file for entry %s?"%bibkey):
					self.parent.StatusBarMessage("deleting arxiv PDF file...")
					pBPDF.removeFile(bibkey, "arxiv")
			elif ask.result == "delDoi":
				if askYesNo("Do you really want to delete the DOI PDF file for entry %s?"%bibkey):
					self.parent.StatusBarMessage("deleting DOI PDF file...")
					pBPDF.removeFile(bibkey, "doi")
			elif ask.result == "addDoi":
				print "NYI"
			elif ask.result == False:
				self.parent.StatusBarMessage("Nothing to do...")

	def setTableSize(self, rows, cols):
		"""set number of rows and columns"""
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

	def recreateTable(self):
		"""delete previous table widget and create a new one"""
		self.bibs = pBDB.bibs.getAll()
		o = self.layout().takeAt(0)
		o.widget().deleteLater()
		self.createTable()

class editBibtexEntry(editObjectWindow):
	"""create a window for editing or creating an experiment"""
	def __init__(self, parent = None, exp = None):
		super(editBibtexEntry, self).__init__(parent)
		#if exp is None:
			#self.data = {}
			#for k in pBDB.tableCols["experiments"]:
				#self.data[k] = ""
		#else:
			#self.data = exp
		#self.createForm()

	#def createForm(self):
		#self.setWindowTitle('Edit experiment')

		#i = 0
		#for k in pBDB.tableCols["experiments"]:
			#val = self.data[k]
			#if k != "idExp" or (k == "idExp" and self.data[k] != ""):
				#i += 1
				#self.currGrid.addWidget(QLabel(k), i*2-1, 0)
				#self.currGrid.addWidget(QLabel("(%s)"%pBDB.descriptions["experiments"][k]), i*2-1, 1)
				#self.textValues[k] = QLineEdit(str(val))
				#if k == "idExp":
					#self.textValues[k].setEnabled(False)
				#self.currGrid.addWidget(self.textValues[k], i*2, 0, 1, 2)

		## OK button
		#self.acceptButton = QPushButton('OK', self)
		#self.acceptButton.clicked.connect(self.onOk)
		#self.currGrid.addWidget(self.acceptButton, i*2+1, 0)

		## cancel button
		#self.cancelButton = QPushButton('Cancel', self)
		#self.cancelButton.clicked.connect(self.onCancel)
		#self.cancelButton.setAutoDefault(True)
		#self.currGrid.addWidget(self.cancelButton, i*2+1, 1)

		#self.setGeometry(100,100,400, 50*i)
		#self.centerWindow()

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
