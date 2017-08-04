#!/usr/bin/env python
import sys
from PySide.QtCore import *
from PySide.QtGui  import *
import subprocess

try:
	from pybiblio.database import pBDB
	#from pybiblio.export import pBExport
	#import pybiblio.webimport.webInterf as webInt
	#from pybiblio.cli import cli as pyBiblioCLI
	from pybiblio.config import pbConfig
	from pybiblio.gui.DialogWindows import *
	from pybiblio.gui.CommonClasses import *
	from pybiblio.pdf import pBPDF
	from pybiblio.view import pBView
	from pybiblio.gui.ThreadElements import *
	from pybiblio.gui.CatWindows import *
	from pybiblio.gui.ExpWindows import *
except ImportError:
	print("Could not find pybiblio and its contents: configure your PYTHONPATH!")
try:
	import pybiblio.gui.Resources_pyside
except ImportError:
	print("Missing Resources_pyside.py: Run script update_resources.sh")

convertType = {
	"review":  "Review",
	"proceeding":  "Proceeding",
	"book": "Book",
	"phd_thesis": "PhD thesis",
	"lecture": "Lecture",
	"exp_paper": "Experimental paper",
}

def writeBibtexInfo(entry):
	infoText = ""
	for t in convertType.keys():
		if entry[t] == 1:
			infoText += "(%s) "%convertType[t]
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
	cats = pBDB.cats.getByEntry(entry["bibkey"])
	infoText += "<br/>Categories: <i>%s</i>"%(", ".join([c["name"] for c in cats]) if len(cats) > 0 else "None")
	exps = pBDB.exps.getByEntry(entry["bibkey"])
	infoText += "<br/>Experiments: <i>%s</i>"%(", ".join([e["name"] for e in exps]) if len(exps) > 0 else "None")
	return infoText

def editBibtex(parent, statusBarObject, editKey = None):
	if editKey is not None:
		edit = pBDB.bibs.getByKey(editKey, saveQuery = False)[0]
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
		if data["bibkey"].strip() == "" and data["bibtex"].strip() != "":
			data = pBDB.bibs.prepareInsert(data["bibtex"].strip())
		if data["bibkey"].strip() != "" and data["bibtex"].strip() != "":
			if "bibkey" in data.keys():
				print("[GUI] Updating bibtex '%s'..."%data["bibkey"])
				pBDB.bibs.update(data, data["bibkey"])
			else:
				pBDB.bibs.insert(data)
			message = "Bibtex entry saved"
			statusBarObject.setWindowTitle("PyBiblio*")
			try:
				parent.top.recreateTable(parent.top.bibs)
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
		self.additionalCols = ["Type", "PDF"]
		for j in range(self.colcnt):
			self.colContents.append(self.columns[j])
		self.colContents += [a.lower() for a in self.additionalCols]

		super(bibtexList, self).__init__(parent)
		self.parent = parent

		self.currLayout = QVBoxLayout()
		self.setLayout(self.currLayout)

		if bibs is not None:
			self.bibs = bibs
		else:
			self.bibs = None
		self.createTable()

	def createTable(self):
		if self.bibs is None:
			self.bibs = pBDB.bibs.getAll(orderType = "DESC", limitTo = pbConfig.params["defaultLimitBibtexs"])
		rowcnt = len(self.bibs)

		commentStr = "Last query to bibtex database: \t%s\t\t"%(pBDB.bibs.lastQuery)
		if len(pBDB.bibs.lastVals)>0 :
			commentStr += " - arguments:\t%s"%(pBDB.bibs.lastVals,)
		self.currLayout.addWidget(QLabel(commentStr))

		#table settings and header
		self.setTableSize(rowcnt, self.colcnt + len(self.additionalCols))
		self.tablewidget.setHorizontalHeaderLabels(self.columns + self.additionalCols)

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
		self.addTypeCell(r, self.colcnt, self.bibs[r])
		self.addPdfCell(r, self.colcnt+1, self.bibs[r]["bibkey"])

	def addImageCell(self, row, col, imagePath):
		"""create a cell containing an image"""
		pic = QPixmap(imagePath).scaledToHeight(self.tablewidget.rowHeight(row)*0.8)
		img = QLabel(self)
		img.setPixmap(pic)
		self.tablewidget.setCellWidget(row, col, img)

	def addTypeCell(self, row, col, data):
		someType = False
		string = ""
		for t in convertType.keys():
			if data[t] == 1:
				if someType:
					string += ", "
				string += convertType[t]
		item = QTableWidgetItem(string)
		item.setFlags(Qt.ItemIsEnabled)
		self.tablewidget.setItem(row, col, item)

	def addPdfCell(self, row, col, key):
		"""create cell for PDF file"""
		if len(pBPDF.getExisting(key))>0:
			self.addImageCell(row, col, ":/images/application-pdf.png")
		else:
			item = QTableWidgetItem("no PDF")
			item.setFlags(Qt.ItemIsEnabled)
			self.tablewidget.setItem(row, col, item)

	def triggeredContextMenuEvent(self, row, col, event):
		def deletePdfFile(bibkey, ftype, fdesc, custom = None):
			if askYesNo("Do you really want to delete the %s file for entry %s?"%(fdesc, bibkey)):
				self.parent.StatusBarMessage("deleting %s file..."%fdesc)
				if custom is not None:
					pBPDF.removeFile(bibkey, "", fname = custom)
				else:
					pBPDF.removeFile(bibkey, ftype)
				self.parent.reloadMainContent(pBDB.bibs.fetchFromLast().lastFetched)
		
		try:
			bibkey = self.tablewidget.item(row, 0).text()
		except AttributeError:
			return
		menu = QMenu()
		titAct = menu.addAction("--Entry: %s--"%bibkey).setDisabled(True)
		menu.addSeparator()
		delAction = menu.addAction("Delete")
		modAction = menu.addAction("Modify")
		cleAction = menu.addAction("Clean")
		menu.addSeparator()

		pdfMenu = menu.addMenu("PDF")
		arxiv = pBDB.bibs.getField(bibkey, "arxiv")
		doi = pBDB.bibs.getField(bibkey, "doi")
		files = pBPDF.getExisting(bibkey, fullPath = True)
		arxivFile = pBPDF.getFilePath(bibkey, "arxiv")
		pdfDir = pBPDF.getFileDir(bibkey)
		pdfActs={}
		pdfActs["addPdf"] = pdfMenu.addAction("Add generic PDF")
		pdfMenu.addSeparator()
		if arxivFile in files:
			files.remove(arxivFile)
			pdfActs["openArx"] = pdfMenu.addAction("Open arXiv PDF")
			pdfActs["delArx"] = pdfMenu.addAction("Delete arXiv PDF")
		elif arxiv is not None and arxiv != "":
			pdfActs["downArx"] = pdfMenu.addAction("Download arXiv PDF")
		pdfMenu.addSeparator()
		doiFile = pBPDF.getFilePath(bibkey, "doi")
		if doiFile in files:
			files.remove(doiFile)
			pdfActs["openDoi"] = pdfMenu.addAction("Open DOI PDF")
			pdfActs["delDoi"] = pdfMenu.addAction("Delete DOI PDF")
		elif doi is not None and doi != "":
			pdfActs["addDoi"] = pdfMenu.addAction("Assign DOI PDF")
		pdfMenu.addSeparator()
		pdfActs["openOtherPDF"] = [None for i in xrange(len(files))]
		pdfActs["delOtherPDF"] = [None for i in xrange(len(files))]
		for i,f in enumerate(files):
			pdfActs["openOtherPDF"][i] = pdfMenu.addAction("Open %s"%f.replace(pdfDir+"/", ""))
			pdfActs["delOtherPDF"][i] = pdfMenu.addAction("Delete %s"%f.replace(pdfDir+"/", ""))
		
		menu.addSeparator()
		catAction = menu.addAction("Manage categories")
		expAction = menu.addAction("Manage experiments")
		menu.addSeparator()
		opArxAct = menu.addAction("Open into arXiv")
		opDoiAct = menu.addAction("Open DOI link")
		opInsAct = menu.addAction("Open into InspireHEP")
		menu.addSeparator()
		updAction = menu.addAction("Update (search Inspire)")
		menu.addSeparator()
		
		action = menu.exec_(event.globalPos())
		if action == delAction:
			deleteBibtex(self.parent, self.parent, bibkey)
		elif action == modAction:
			editBibtex(self.parent, self.parent, bibkey)
		elif action == catAction:
			previous = [a[0] for a in pBDB.cats.getByEntry(bibkey)]
			selectCats = catsWindowList(parent = self.parent, askCats = True, askForBib = bibkey, expButton = False, previous = previous)
			selectCats.exec_()
			if selectCats.result == "Ok":
				cats = self.parent.selectedCats
				for p in previous:
					if p not in cats:
						pBDB.catBib.delete(p, bibkey)
				for c in cats:
					if c not in previous:
						pBDB.catBib.insert(c, bibkey)
				self.parent.StatusBarMessage("categories for '%s' successfully inserted"%bibkey)
		elif action == expAction:
			previous = [a[0] for a in pBDB.exps.getByEntry(bibkey)]
			selectExps = ExpWindowList(parent = self, askExps = True, askForBib = bibkey, previous = previous)
			selectExps.exec_()
			if selectExps.result == "Ok":
				exps = self.parent.selectedExps
				for p in previous:
					if p not in exps:
						pBDB.bibExp.delete(bibkey, p)
				for e in exps:
					if e not in previous:
						pBDB.bibExp.insert(bibkey, e)
				self.parent.StatusBarMessage("experiments for '%s' successfully inserted"%bibkey)
		elif action == opArxAct:
			pBView.openLink(bibkey, "arxiv")
		elif action == opDoiAct:
			pBView.openLink(bibkey, "doi")
		elif action == opInsAct:
			pBView.openLink(bibkey, "inspire")
		elif action == cleAction:
			self.parent.cleanAllBibtexs(useEntries = pBDB.bibs.getByBibkey(bibkey))
		elif action == updAction:
			self.parent.updateAllBibtexs(useEntries = pBDB.bibs.getByBibkey(bibkey), force = True)
		#actions for PDF
		elif "openArx" in pdfActs.keys() and action == pdfActs["openArx"]:
			self.parent.StatusBarMessage("opening arxiv PDF...")
			pBPDF.openFile(bibkey, "arxiv")
		elif "openDoi" in pdfActs.keys() and action == pdfActs["openDoi"]:
			self.parent.StatusBarMessage("opening doi PDF...")
			pBPDF.openFile(bibkey, "doi")
		elif "downArx" in pdfActs.keys() and action == pdfActs["downArx"]:
			self.parent.StatusBarMessage("downloading PDF from arxiv...")
			self.downArxiv_thr = thread_downloadArxiv(bibkey)
			self.connect(self.downArxiv_thr, SIGNAL("finished()"), self.downloadArxivDone)
			self.downArxiv_thr.start()
		elif "delArx" in pdfActs.keys() and action == pdfActs["delArx"]:
			deletePdfFile(bibkey, "arxiv", "arxiv PDF")
		elif "delDoi" in pdfActs.keys() and action == pdfActs["delDoi"]:
			deletePdfFile(bibkey, "doi", "DOI PDF")
		elif "addDoi" in pdfActs.keys() and action == pdfActs["addDoi"]:
			newpdf = askFileName(self, "Where is the published PDF located?", filter = "PDF (*.pdf)")
			if newpdf != "" and os.path.isfile(newpdf):
				if pBPDF.copyNewFile(bibkey, newpdf, "doi"):
					infoMessage("PDF successfully copied!")
		elif "addPdf" in pdfActs.keys() and action == pdfActs["addPdf"]:
			newPdf = askFileName(self, "Where is the published PDF located?", filter = "PDF (*.pdf)")
			newName = newPdf.split("/")[-1]
			if newPdf != "" and os.path.isfile(newPdf):
				if pBPDF.copyNewFile(bibkey, newPdf, customName = newName):
					infoMessage("PDF successfully copied!")
		#warning: this elif must be the last one!
		elif len(pdfActs["openOtherPDF"]) > 0:
			for i, act in enumerate(pdfActs["openOtherPDF"]):
				if action == act:
					fn = files[i].replace(pdfDir+"/", "")
					self.parent.StatusBarMessage("opening %s..."%fn)
					pBPDF.openFile(bibkey, fileName = fn)
			for i, act in enumerate(pdfActs["delOtherPDF"]):
				if action == act:
					fn = files[i].replace(pdfDir+"/", "")
					deletePdfFile(bibkey, fn, fn, custom = files[i])

	def cellClick(self, row, col):
		self.tablewidget.selectRow(row)
		bibkey = self.tablewidget.item(row, 0).text()
		entry = pBDB.bibs.getByBibkey(bibkey, saveQuery = False)[0]
		self.parent.bottomLeft.text.setText(entry["bibtex"])
		self.parent.bottomRight.text.setText(writeBibtexInfo(entry))
		if self.colContents[col] == "modify":
			editBibtex(self.parent, self.parent, bibkey)
		elif self.colContents[col] == "delete":
			deleteBibtex(self.parent, self.parent, bibkey)

	def cellDoubleClick(self, row, col):
		self.tablewidget.selectRow(row)
		bibkey = self.tablewidget.item(row, 0).text()
		entry = pBDB.bibs.getByBibkey(bibkey, saveQuery = False)[0]
		self.parent.bottomLeft.text.setText(entry["bibtex"])
		self.parent.bottomRight.text.setText(writeBibtexInfo(entry))
		if self.colContents[col] == "doi" and entry["doi"] is not None and entry["doi"] != "":
			pBView.openLink(bibkey, "doi")
		elif self.colContents[col] == "arxiv" and entry["arxiv"] is not None and entry["arxiv"] != "":
			pBView.openLink(bibkey, "arxiv")
		elif self.colContents[col] == "inspire" and entry["inspire"] is not None and entry["inspire"] != "":
			pBView.openLink(bibkey, "inspire")
		elif self.colContents[col] == "pdf":
			pdfFiles = pBPDF.getExisting(bibkey)
			if len(pdfFiles) == 1:
				self.parent.StatusBarMessage("opening PDF...")
				pBPDF.openFile(bibkey, fileName = pdfFiles[0])
			elif len(pdfFiles) > 1:
				ask = askPdfAction(self, bibkey, entry["arxiv"], entry["doi"])
				ask.exec_()
				if ask.result == "openArxiv":
					self.parent.StatusBarMessage("opening arxiv PDF...")
					pBPDF.openFile(bibkey, "arxiv")
				elif ask.result == "openDoi":
					self.parent.StatusBarMessage("opening doi PDF...")
					pBPDF.openFile(bibkey, "doi")

	def downloadArxivDone(self):
		self.parent.sendMessage("Arxiv download execution completed! Please check that it worked...")
		self.parent.done()
		self.parent.reloadMainContent(pBDB.bibs.fetchFromLast().lastFetched)

	def setTableSize(self, rows, cols):
		"""set number of rows and columns"""
		self.rows = rows
		self.cols = cols
		self.tablewidget = MyTableWidget(rows, cols, self)
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
			self.bibs = pBDB.bibs.getAll(orderType = "DESC", limitTo = pbConfig.params["defaultLimitBibtexs"])
		while True:
			o = self.layout().takeAt(0)
			if o is None: break
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
		self.checkboxes = ["exp_paper", "lecture", "phd_thesis", "review", "proceeding", "book", "noUpdate"]
		self.createForm()

	def onOk(self):
		if self.textValues["bibtex"].toPlainText() == "":
			pBGUIErrorManager("Invalid form contents: empty bibtex!")
			return False
		elif not self.textValues["bibkey"].isReadOnly() and self.textValues["bibkey"].text() != "" and self.textValues["bibtex"].toPlainText() != "":
			pBGUIErrorManager("Invalid form contents: bibtex key will be taken from bibtex!")
			return False
		self.result	= True
		self.close()

	def createForm(self):
		self.setWindowTitle('Edit bibtex entry')

		i = 0
		for k in pBDB.tableCols["entries"]:
			val = self.data[k] if self.data[k] is not None else ""
			if k != "bibtex" and k not in self.checkboxes:
				i += 1
				self.currGrid.addWidget(QLabel(k), int((i+1-(i+i)%2)/2)*2-1, ((1+i)%2)*2)
				self.currGrid.addWidget(QLabel("(%s)"%pBDB.descriptions["entries"][k]),  int((i+1-(i+i)%2)/2)*2-1, ((1+i)%2)*2+1)
				self.textValues[k] = QLineEdit(str(val))
				if k == "bibkey" and val != "":
					self.textValues[k].setReadOnly(True)
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
		self.message = "What PDF of this entry (%s) do you want to open?"%(key)
		self.possibleActions = []
		files = pBPDF.getExisting(key, fullPath = True)
		if pBPDF.getFilePath(key, "arxiv") in files:
			self.possibleActions.append(["Open arxiv PDF", self.onOpenArxiv])
		if pBPDF.getFilePath(key, "doi") in files:
			self.possibleActions.append(["Open DOI PDF", self.onOpenDoi])
		self.initUI()

	def onOpenArxiv(self):
		self.result	= "openArxiv"
		self.close()

	def onOpenDoi(self):
		self.result	= "openDoi"
		self.close()

class searchBibsWindow(editObjectWindow):
	"""create a window for editing or creating a bibtex entry"""
	def __init__(self, parent = None, bib = None):
		super(searchBibsWindow, self).__init__(parent)
		self.textValues = []
		self.result = False
		self.values = {}
		self.values["cats"] = []
		self.values["exps"] = []
		self.values["catsOperator"] = "AND"
		self.values["expsOperator"] = "AND"
		self.values["catExpOperator"] = "AND"
		self.numberOfRows = 1
		self.createForm()
		#self.setGeometry(100,100,400, 25*i)
		#self.centerWindow()

	def onAskCats(self):
		selectCats = catsWindowList(parent = self, askCats = True, expButton = False, previous = self.values["cats"])
		selectCats.exec_()
		if selectCats.result == "Ok":
			self.values["cats"] = self.selectedCats

	def onAskExps(self):
		selectExps = ExpWindowList(parent = self, askExps = True, previous = self.values["exps"])
		selectExps.exec_()
		if selectExps.result == "Ok":
			self.values["exps"] = self.selectedExps

	def onComboCatsChange(self, text):
		self.values["catsOperator"] = text

	def onComboExpsChange(self, text):
		self.values["expsOperator"] = text

	def onComboCEChange(self, text):
		self.values["CatExpOperator"] = text

	def onAddField(self):
		self.numberOfRows = self.numberOfRows + 1
		while True:
			o = self.layout().takeAt(0)
			if o is None: break
			o.widget().deleteLater()
		self.createForm()

	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Escape:
			self.onCancel()

	def eventFilter(self, widget, event):
		if (event.type() == QEvent.KeyPress and
				widget in [a["content"] for a in self.textValues]):
			key = event.key()
			if key == Qt.Key_Return or key == Qt.Key_Enter:
				self.acceptButton.setFocus()
				return True
		return QWidget.eventFilter(self, widget, event)

	def createForm(self):
		self.setWindowTitle('Search bibtex entries')

		self.currGrid.addWidget(QLabel("Filter by categories, using the following operator:"), 0, 0, 1, 2)
		self.catsButton = QPushButton('Categories', self)
		self.catsButton.clicked.connect(self.onAskCats)
		self.currGrid.addWidget(self.catsButton, 0, 2)
		self.comboCats = MyAndOrCombo(self)
		self.comboCats.activated[str].connect(self.onComboCatsChange)
		self.currGrid.addWidget(self.comboCats, 0, 3)

		self.currGrid.addWidget(QLabel("Filter by experiments, using the following operator:"), 1, 0, 1, 2)
		self.expsButton = QPushButton('Experiments', self)
		self.expsButton.clicked.connect(self.onAskExps)
		self.currGrid.addWidget(self.expsButton, 1, 2)
		self.comboExps = MyAndOrCombo(self)
		self.comboExps.activated[str].connect(self.onComboExpsChange)
		self.currGrid.addWidget(self.comboExps, 1, 3)

		self.currGrid.addWidget(QLabel("If using both categories and experiments, which operator between them?"), 2, 0, 1, 3)
		self.comboCE = MyAndOrCombo(self)
		self.comboCE.activated[str].connect(self.onComboCEChange)
		self.currGrid.addWidget(self.comboCE, 2, 3)

		self.currGrid.addWidget(QLabel("Select more: the operator to use, the field to match, (exact match vs contains) and the content to match"), 3, 0, 1, 3)
		firstFields = 4

		for i in range(self.numberOfRows):
			try:
				previous = {
					"logical": "%s"%self.textValues[i]["logical"].currentText(),
					"field": "%s"%self.textValues[i]["field"].currentText(),
					"operator": "%s"%self.textValues[i]["operator"].currentText(),
					"content": "%s"%self.textValues[i]["content"].text()
				}
			except IndexError:
				previous = {"logical": None, "field": None, "operator": None, "content": ""}
				self.textValues.append({})

			self.textValues[i]["logical"] = MyAndOrCombo(self, current = previous["logical"])
			self.currGrid.addWidget(self.textValues[i]["logical"], i + firstFields, 0)

			self.textValues[i]["field"] = MyComboBox(self, ["bibtex", "bibkey", "arxiv", "doi", "year", "firstdate", "pubdate", "comment"], current = previous["field"])
			self.currGrid.addWidget(self.textValues[i]["field"], i + firstFields, 1)

			self.textValues[i]["operator"] = MyComboBox(self, ["contains", "exact match"], current = previous["operator"])
			self.currGrid.addWidget(self.textValues[i]["operator"], i + firstFields, 2)

			self.textValues[i]["content"] = QLineEdit(previous["content"])
			self.currGrid.addWidget(self.textValues[i]["content"], i + firstFields, 3)
			self.textValues[i]["content"].installEventFilter(self)

		self.textValues[-1]["content"].setFocus()

		i = self.numberOfRows + firstFields + 1
		self.currGrid.addWidget(QLabel("Click here if you want more fields:"), i-1, 0, 1, 3)
		self.addFieldButton = QPushButton("Add another field line", self)
		self.addFieldButton.clicked.connect(self.onAddField)
		self.currGrid.addWidget(self.addFieldButton, i-1, 3)

		# OK button
		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		self.currGrid.addWidget(self.acceptButton, i, 1)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		self.currGrid.addWidget(self.cancelButton, i, 2)
