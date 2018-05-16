#!/usr/bin/env python
import sys
import os
import matplotlib as mpl
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PySide.QtCore import *
from PySide.QtGui  import *
import re
from pyparsing import ParseException
from pylatexenc.latex2text import LatexNodes2Text

try:
	from physbiblio.errors import pBLogger
	from physbiblio.database import pBDB
	from physbiblio.config import pbConfig
	from physbiblio.pdf import pBPDF
	from physbiblio.parse_accents import *
	from physbiblio.gui.ErrorManager import pBGUILogger
	from physbiblio.gui.DialogWindows import *
	from physbiblio.gui.CommonClasses import *
	from physbiblio.gui.ThreadElements import *
	from physbiblio.gui.CatWindows import *
	from physbiblio.gui.ExpWindows import *
	from physbiblio.gui.marks import *
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
try:
	if sys.version_info[0] < 3:
		import physbiblio.gui.Resources_pyside
	else:
		import physbiblio.gui.Resources_pyside3
except ImportError:
	print("Missing Resources_pyside: Run script update_resources.sh")

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
	latexToText = LatexNodes2Text(keep_inline_math = True, keep_comments = False)
	try:
		infoText += "<b>%s</b><br/>%s<br/>"%(latexToText.latex_to_text(entry["bibtexDict"]["author"]), latexToText.latex_to_text(entry["bibtexDict"]["title"]))
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

class abstractFormulas():
	def __init__(self, mainWin, text, fontsize = pbConfig.params["bibListFontSize"], abstractTitle = "<b>Abstract:</b><br/>"):
		self.fontsize = fontsize
		self.mainWin = mainWin
		self.editor = self.mainWin.bottomCenter.text
		self.document = QTextDocument()
		self.editor.setDocument(self.document)
		self.abstractTitle = abstractTitle
		text = str(text)
		self.text = abstractTitle + texToHtml(text).replace("\n", " ")

	def hasLatex(self):
		return "$" in self.text

	def doText(self):
		if "$" in self.text:
			self.editor.insertHtml("%sProcessing LaTeX formulas..."%self.abstractTitle)
			self.thr = thread_processLatex(self.prepareText, self.mainWin)
			self.thr.passData.connect(self.submitText)
			self.thr.start()
		else:
			self.editor.insertHtml(self.text)

	def mathTex_to_QPixmap(self, mathTex):
		fig = mpl.figure.Figure()
		fig.patch.set_facecolor('none')
		fig.set_canvas(FigureCanvasAgg(fig))
		renderer = fig.canvas.get_renderer()

		ax = fig.add_axes([0, 0, 1, 1])
		ax.axis('off')
		ax.patch.set_facecolor('none')
		t = ax.text(0, 0, mathTex, ha='left', va='bottom', fontsize = self.fontsize)

		fwidth, fheight = fig.get_size_inches()
		fig_bbox = fig.get_window_extent(renderer)

		try:
			text_bbox = t.get_window_extent(renderer)
		except ValueError:
			pBLogger.exception("Error when converting latex to image")
			return None

		tight_fwidth = text_bbox.width * fwidth / fig_bbox.width
		tight_fheight = text_bbox.height * fheight / fig_bbox.height

		fig.set_size_inches(tight_fwidth, tight_fheight)

		buf, size = fig.canvas.print_to_buffer()
		qimage = QImage.rgbSwapped(QImage(buf, size[0], size[1], QImage.Format_ARGB32))
		return qimage

	def prepareText(self):
		textList = self.text.split("$")
		matchFormula = re.compile('\$.*?\$', re.MULTILINE)
		mathTexts = [ q.group() for q in matchFormula.finditer(self.text) ]

		images = []
		text = self.text
		for i, t in enumerate(mathTexts):
			images.append(self.mathTex_to_QPixmap(t))
			text = text.replace(t, "<img src=\"mydata://image%d.png\" />"%i)
		return images, text

	def submitText(self, imgs, text):
		self.document = QTextDocument()
		self.editor.setDocument(self.document)
		for i, image in enumerate(imgs):
			self.document.addResource(QTextDocument.ImageResource,
				QUrl("mydata://image%d.png"%i), image)
		self.editor.insertHtml(text)
		self.mainWin.StatusBarMessage("Latex processing done!")

def writeAbstract(mainWin, entry):
	a = abstractFormulas(mainWin, entry["abstract"])
	if a.hasLatex():
		mainWin.StatusBarMessage("Parsing LaTeX...")
	a.doText()

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
		data["marks"] = ""
		for m, ckb in newBibWin.markValues.items():
			if ckb.isChecked():
				data["marks"] += "'%s',"%m
		if data["bibkey"].strip() == "" and data["bibtex"].strip() != "":
			data = pBDB.bibs.prepareInsert(data["bibtex"].strip())
		if data["bibkey"].strip() != "" and data["bibtex"].strip() != "":
			if "bibkey" in data.keys():
				if editKey is not None and data["bibkey"].strip() != editKey:
					print("[GUI] New bibtex key (%s) for element '%s'..."%(data["bibkey"], editKey))
					if editKey not in data["old_keys"]:
						data["old_keys"] += " " + editKey
						data["old_keys"] = data["old_keys"].strip()
					pBDB.bibs.updateBibkey(editKey, data["bibkey"].strip())
					pBPDF.renameFolder(editKey, data["bibkey"].strip())
				print("[GUI] Updating bibtex '%s'..."%data["bibkey"])
				pBDB.bibs.update(data, data["bibkey"])
			else:
				pBDB.bibs.insert(data)
			message = "Bibtex entry saved"
			statusBarObject.setWindowTitle("PhysBiblio*")
			try:
				parent.reloadMainContent(pBDB.bibs.fetchFromLast().lastFetched)
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
		statusBarObject.setWindowTitle("PhysBiblio*")
		message = "Bibtex entry deleted"
		try:
			parent.bibtexList.recreateTable()
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

class MyBibTableModel(MyTableModel):
	def __init__(self, parent, bib_list, header, stdCols = [], addCols = [], askBibs = False, previous = [], mainWin = None, *args):
		self.parent = parent
		self.mainWin = mainWin
		self.latexToText = LatexNodes2Text(keep_inline_math = False, keep_comments = False)
		self.typeClass = "Bibs"
		self.dataList = bib_list
		MyTableModel.__init__(self, parent, header + ["bibtex"], askBibs, previous, *args)
		self.stdCols = stdCols
		self.addCols = addCols + ["bibtex"]
		self.lenStdCols = len(stdCols)
		self.prepareSelected()

	def getIdentifier(self, element):
		return element["bibkey"]

	def addTypeCell(self, data):
		someType = False
		string = ""
		for t in convertType.keys():
			if data[t] == 1:
				if someType:
					string += ", "
				string += convertType[t]
		return string

	def addPdfCell(self, key):
		"""create cell for PDF file"""
		if len(pBPDF.getExisting(key))>0:
			return True, self.addImage(":/images/application-pdf.png", self.parentObj.tablewidget.rowHeight(0)*0.9)
		else:
			return False, "no PDF"

	def addMarksCell(self, marks):
		"""create cell for marks"""
		if marks is not None:
			marks = [ k for k in pBMarks.marks.keys() if k in marks ]
			if len(marks)>1:
				return True, self.addImages([pBMarks.marks[img]["icon"] for img in marks ], self.parentObj.tablewidget.rowHeight(0)*0.9)
			elif len(marks)>0:
				return True, self.addImage(pBMarks.marks[marks[0]]["icon"], self.parentObj.tablewidget.rowHeight(0)*0.9)
			else:
				return False, ("", "")
		else:
			return False, ("", "")

	def data(self, index, role):
		if not index.isValid():
			return None
		img = False
		row = index.row()
		column = index.column()
		try:
			if "marks" in self.stdCols and column == self.stdCols.index("marks"):
				img, value = self.addMarksCell(self.dataList[row]["marks"])
			elif column < self.lenStdCols:
				try:
					value = self.dataList[row][self.stdCols[column]]
					if self.stdCols[column] in ["title", "author"]:
						value = self.latexToText.latex_to_text(value)
				except KeyError:
					value = ""
			else:
				if self.addCols[column - self.lenStdCols] == "Type":
					value = self.addTypeCell(self.dataList[row])
				elif self.addCols[column - self.lenStdCols] == "PDF":
					img, value = self.addPdfCell(self.dataList[row]["bibkey"])
				else:
					value = self.dataList[row]["bibtex"]
		except IndexError:
			pBGUILogger.exception("MyBibTableModel.data(): invalid index")
			return None

		if role == Qt.CheckStateRole and self.ask and column == 0:
			if self.selectedElements[self.dataList[row]["bibkey"]] == True:
				return Qt.Checked
			else:
				return Qt.Unchecked
		if role == Qt.EditRole:
			return value
		if role == Qt.DecorationRole and img:
			return value
		if role == Qt.DisplayRole and not img:
			return value
		return None

	def setData(self, index, value, role):
		if role == Qt.CheckStateRole and index.column() == 0:
			if value == Qt.Checked:
				self.selectedElements[self.dataList[index.row()]["bibkey"]] = True
			else:
				self.selectedElements[self.dataList[index.row()]["bibkey"]] = False

		self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
		return True

class bibtexList(QFrame, objListWindow):
	def __init__(self, parent = None, bibs = None, askBibs = False, previous = []):
		#table dimensions
		self.columns = pbConfig.params["bibtexListColumns"]
		self.colcnt = len(self.columns)
		self.colContents = []
		self.previous = previous
		self.parent = parent
		self.askBibs = askBibs
		self.additionalCols = ["Type", "PDF"]
		for j in range(self.colcnt):
			self.colContents.append(self.columns[j])
		self.colContents += [a.lower() for a in self.additionalCols]

		QFrame.__init__(self, parent)
		objListWindow.__init__(self, parent)

		self.selAct = QAction(QIcon(":/images/edit-node.png"),
						"&Select entries", self,
						#shortcut="Ctrl+S",
						statusTip="Select entries from the list",
						triggered=self.enableSelection)
		self.okAct = QAction(QIcon(":/images/dialog-ok-apply.png"),
						"Selection &completed", self,
						#shortcut="Ctrl+S",
						statusTip="Selection of elements completed",
						triggered=self.onOk)
		self.clearAct = QAction(QIcon(":/images/edit-clear.png"),
						"&Clear selection", self,
						#shortcut="Ctrl+S",
						statusTip="Discard the current selection and hide checkboxes",
						triggered=self.clearSelection)
		self.selAllAct = QAction(QIcon(":/images/edit-select-all.png"),
						"&Select all", self,
						#shortcut="Ctrl+S",
						statusTip="Select all the elements",
						triggered=self.selectAll)
		self.unselAllAct = QAction(QIcon(":/images/edit-unselect-all.png"),
						"&Unselect all", self,
						#shortcut="Ctrl+S",
						statusTip="Unselect all the elements",
						triggered=self.unselectAll)

		if bibs is not None:
			self.bibs = bibs
		else:
			self.bibs = None
		self.createTable()

	def reloadColumnContents(self):
		self.columns = pbConfig.params["bibtexListColumns"]
		self.colcnt = len(self.columns)
		self.colContents = []
		for j in range(self.colcnt):
			self.colContents.append(self.columns[j])
		self.colContents += [a.lower() for a in self.additionalCols]

	def changeEnableActions(self):
		status = self.table_model.ask
		self.clearAct.setEnabled(status)
		self.selAllAct.setEnabled(status)
		self.unselAllAct.setEnabled(status)
		self.okAct.setEnabled(status)

	def enableSelection(self):
		self.table_model.changeAsk()
		self.changeEnableActions()

	def clearSelection(self):
		self.table_model.previous = []
		self.table_model.prepareSelected()
		self.table_model.changeAsk(False)
		self.changeEnableActions()

	def selectAll(self):
		self.table_model.selectAll()

	def unselectAll(self):
		self.table_model.unselectAll()

	def onOk(self):
		self.parent.selectedBibs = [key for key in self.table_model.selectedElements.keys() if self.table_model.selectedElements[key] == True]
		ask = askSelBibAction(self.parent, self.parent.selectedBibs)
		ask.exec_(QCursor.pos())
		if ask.result == "done":
			self.clearSelection()

	def createTable(self):
		if self.bibs is None:
			self.bibs = pBDB.bibs.getAll(orderType = "DESC", limitTo = pbConfig.params["defaultLimitBibtexs"])
		rowcnt = len(self.bibs)

		commentStr = "Last query to bibtex database: \t%s\t\t"%(pBDB.bibs.lastQuery)
		if len(pBDB.bibs.lastVals)>0 :
			commentStr += " - arguments:\t%s"%(pBDB.bibs.lastVals,)
		self.currLayout.addWidget(QLabel(commentStr))

		self.selectToolBar = QToolBar('Bibs toolbar')
		self.selectToolBar.addAction(self.selAct)
		self.selectToolBar.addAction(self.clearAct)
		self.selectToolBar.addSeparator()
		self.selectToolBar.addAction(self.selAllAct)
		self.selectToolBar.addAction(self.unselAllAct)
		self.selectToolBar.addAction(self.okAct)
		self.selectToolBar.addWidget(QLabel("(Select exactly two entries to enable merging them)"))
		self.selectToolBar.addSeparator()

		self.filterInput = QLineEdit("",  self)
		self.filterInput.setPlaceholderText("Filter bibliography")
		self.filterInput.textChanged.connect(self.changeFilter)
		self.selectToolBar.addWidget(self.filterInput)
		self.filterInput.setFocus()

		self.currLayout.addWidget(self.selectToolBar)

		self.table_model = MyBibTableModel(self,
			self.bibs, self.columns + self.additionalCols,
			self.columns, self.additionalCols,
			askBibs = self.askBibs,
			mainWin = self.parent,
			previous = self.previous)

		self.changeEnableActions()
		self.setProxyStuff(self.columns.index("firstdate"), Qt.DescendingOrder)
		self.tablewidget.hideColumn(len(self.columns) + len(self.additionalCols))

		self.finalizeTable()

	def triggeredContextMenuEvent(self, row, col, event):
		def deletePdfFile(bibkey, fileType, fdesc, custom = None):
			if askYesNo("Do you really want to delete the %s file for entry %s?"%(fdesc, bibkey)):
				self.parent.StatusBarMessage("deleting %s file..."%fdesc)
				if custom is not None:
					pBPDF.removeFile(bibkey, "", fileName = custom)
				else:
					pBPDF.removeFile(bibkey, fileType)
				self.parent.reloadMainContent(pBDB.bibs.fetchFromLast().lastFetched)

		def copyPdfFile(bibkey, fileType, custom = None):
			pdfName = os.path.join(pBPDF.getFileDir(bibkey), custom) if custom is not None else pBPDF.getFilePath(bibkey, fileType)
			outFolder = askDirName(self, title = "Where do you want to save the PDF %s?"%pdfName)
			if outFolder.strip() != "":
				pBPDF.copyToDir(outFolder, bibkey, fileType = fileType, customName = custom)

		index = self.tablewidget.model().index(row, col)
		try:
			bibkey = self.proxyModel.sibling(row, self.columns.index("bibkey"), index).data()
			if bibkey is None or bibkey is "":
				return
			bibkey = str(bibkey)
		except AttributeError:
			pBLogger.exception("Error in reading table content")
			return
		menu = QMenu()
		titAct = menu.addAction("--Entry: %s--"%bibkey).setDisabled(True)
		menu.addSeparator()
		modAction = menu.addAction("Modify")
		cleAction = menu.addAction("Clean")
		delAction = menu.addAction("Delete")
		menu.addSeparator()

		copyMenu = menu.addMenu("Copy to clipboard")
		copyActions = {}
		copyActions["bibkey"] = copyMenu.addAction("Copy key")
		copyActions["cite"] = copyMenu.addAction(r"Copy \cite{key}")
		copyActions["bibtex"] = copyMenu.addAction("Copy bibtex")
		abstract = pBDB.bibs.getField(bibkey, "abstract")
		if abstract is not None and abstract.strip() != "":
			copyActions["abstract"] = copyMenu.addAction("Copy abstract")
		link = pBDB.bibs.getField(bibkey, "link")
		if link is not None and link.strip() != "":
			copyActions["link"] = copyMenu.addAction("Copy link")
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
			pdfActs["copyArx"] = pdfMenu.addAction("Copy arXiv PDF")
		elif arxiv is not None and arxiv != "":
			pdfActs["downArx"] = pdfMenu.addAction("Download arXiv PDF")
		pdfMenu.addSeparator()
		doiFile = pBPDF.getFilePath(bibkey, "doi")
		if doiFile in files:
			files.remove(doiFile)
			pdfActs["openDoi"] = pdfMenu.addAction("Open DOI PDF")
			pdfActs["delDoi"] = pdfMenu.addAction("Delete DOI PDF")
			pdfActs["copyDoi"] = pdfMenu.addAction("Copy DOI PDF")
		elif doi is not None and doi != "":
			pdfActs["addDoi"] = pdfMenu.addAction("Assign DOI PDF")
		pdfMenu.addSeparator()
		pdfActs["openOtherPDF"] = [None for i in range(len(files))]
		pdfActs["delOtherPDF"] = [None for i in range(len(files))]
		pdfActs["copyOtherPDF"] = [None for i in range(len(files))]
		for i,f in enumerate(files):
			pdfActs["openOtherPDF"][i] = pdfMenu.addAction("Open %s"%f.replace(pdfDir+"/", ""))
			pdfActs["delOtherPDF"][i] = pdfMenu.addAction("Delete %s"%f.replace(pdfDir+"/", ""))
			pdfActs["copyOtherPDF"][i] = pdfMenu.addAction("Copy %s"%f.replace(pdfDir+"/", ""))
		
		menu.addSeparator()
		catAction = menu.addAction("Manage categories")
		expAction = menu.addAction("Manage experiments")
		menu.addSeparator()
		opArxAct = menu.addAction("Open into arXiv")
		opDoiAct = menu.addAction("Open DOI link")
		opInsAct = menu.addAction("Open into INSPIRE-HEP")
		menu.addSeparator()
		insAction = menu.addAction("Complete info (from INSPIRE-HEP)")
		updAction = menu.addAction("Update (search INSPIRE-HEP)")
		staAction = menu.addAction("Citation statistics (from INSPIRE-HEP)")
		if arxiv is not None and arxiv != "":
			absAction = menu.addAction("Get abstract (from arXiv)")
			arxAction = menu.addAction("Get info (from arXiv)")
		else:
			absAction = "absAction"
			arxAction = "arxAction"
		menu.addSeparator()
		
		action = menu.exec_(event.globalPos())
		if action == delAction:
			deleteBibtex(self.parent, self.parent, bibkey)
		elif action == modAction:
			editBibtex(self.parent, self.parent, bibkey)
		elif action == cleAction:
			self.parent.cleanAllBibtexs(useEntries = pBDB.bibs.getByBibkey(bibkey, saveQuery = False))
		#copy functions
		elif "bibkey" in copyActions.keys() and action == copyActions["bibkey"]:
			self.copyToClipboard(bibkey)
		elif "cite" in copyActions.keys() and action == copyActions["cite"]:
			self.copyToClipboard(r"\cite{%s}"%bibkey)
		elif "bibtex" in copyActions.keys() and action == copyActions["bibtex"]:
			self.copyToClipboard(pBDB.bibs.getField(bibkey, "bibtex"))
		elif "abstract" in copyActions.keys() and action == copyActions["abstract"]:
			self.copyToClipboard(abstract)
		elif "link" in copyActions.keys() and action == copyActions["link"]:
			self.copyToClipboard(link)
		#categories
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
		#experiments
		elif action == expAction:
			previous = [a[0] for a in pBDB.exps.getByEntry(bibkey)]
			selectExps = ExpWindowList(parent = self.parent, askExps = True, askForBib = bibkey, previous = previous)
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
		#open functions
		elif action == opArxAct:
			pBGuiView.openLink(bibkey, "arxiv")
		elif action == opDoiAct:
			pBGuiView.openLink(bibkey, "doi")
		elif action == opInsAct:
			pBGuiView.openLink(bibkey, "inspire")
		#online information
		elif action == insAction:
			self.parent.updateInspireInfo(bibkey)
		elif action == updAction:
			self.parent.updateAllBibtexs(useEntries = pBDB.bibs.getByBibkey(bibkey, saveQuery = False), force = True)
		elif action == staAction:
			self.parent.getInspireStats(pBDB.bibs.getField(bibkey, "inspire"))
		elif action == absAction:
			self.arxivAbstract(arxiv, bibkey)
		elif action == arxAction:
			askFieldsWin = fieldsFromArxiv()
			askFieldsWin.exec_()
			if askFieldsWin.result:
				result = pBDB.bibs.getFieldsFromArxiv(bibkey, askFieldsWin.output)
				if result is True:
					infoMessage("Done!")
				else:
					#must be improved...the function only returns False
					pBGUILogger.warning("getFieldsFromArxiv failed")
		#actions for PDF
		elif "openArx" in pdfActs.keys() and action == pdfActs["openArx"]:
			self.parent.StatusBarMessage("opening arxiv PDF...")
			pBGuiView.openLink(bibkey, "file", fileArg = pBPDF.getFilePath(bibkey, "arxiv"))
		elif "openDoi" in pdfActs.keys() and action == pdfActs["openDoi"]:
			self.parent.StatusBarMessage("opening doi PDF...")
			pBGuiView.openLink(bibkey, "file", fileArg = pBPDF.getFilePath(bibkey, "doi"))
		elif "downArx" in pdfActs.keys() and action == pdfActs["downArx"]:
			self.parent.StatusBarMessage("downloading PDF from arxiv...")
			self.downArxiv_thr = thread_downloadArxiv(bibkey, self.parent)
			self.downArxiv_thr.finished.connect(self.downloadArxivDone)
			self.downArxiv_thr.start()
		elif "delArx" in pdfActs.keys() and action == pdfActs["delArx"]:
			deletePdfFile(bibkey, "arxiv", "arxiv PDF")
		elif "delDoi" in pdfActs.keys() and action == pdfActs["delDoi"]:
			deletePdfFile(bibkey, "doi", "DOI PDF")
		elif "copyArx" in pdfActs.keys() and action == pdfActs["copyArx"]:
			copyPdfFile(bibkey, "arxiv")
		elif "copyDoi" in pdfActs.keys() and action == pdfActs["copyDoi"]:
			copyPdfFile(bibkey, "doi")
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
					pBGuiView.openLink(bibkey, "file", fileArg = fn)
			for i, act in enumerate(pdfActs["delOtherPDF"]):
				if action == act:
					fn = files[i].replace(pdfDir+"/", "")
					deletePdfFile(bibkey, fn, fn, custom = files[i])
			for i, act in enumerate(pdfActs["copyOtherPDF"]):
				if action == act:
					fn = files[i].replace(pdfDir+"/", "")
					copyPdfFile(bibkey, fn, custom = files[i])

	def cellClick(self, index):
		row = index.row()
		col = index.column()
		try:
			bibkey = str(self.proxyModel.sibling(row, self.columns.index("bibkey"), index).data())
		except AttributeError:
			return
		entry = pBDB.bibs.getByBibkey(bibkey, saveQuery = False)[0]
		self.parent.bottomLeft.text.setText(entry["bibtex"])
		self.parent.bottomRight.text.setText(writeBibtexInfo(entry))
		writeAbstract(self.parent, entry)

	def cellDoubleClick(self, index):
		row = index.row()
		col = index.column()
		try:
			bibkey = str(self.proxyModel.sibling(row, self.columns.index("bibkey"), index).data())
		except AttributeError:
			return
		entry = pBDB.bibs.getByBibkey(bibkey, saveQuery = False)[0]
		self.parent.bottomLeft.text.setText(entry["bibtex"])
		self.parent.bottomRight.text.setText(writeBibtexInfo(entry))
		if self.colContents[col] == "doi" and entry["doi"] is not None and entry["doi"] != "":
			pBGuiView.openLink(bibkey, "doi")
		elif self.colContents[col] == "arxiv" and entry["arxiv"] is not None and entry["arxiv"] != "":
			pBGuiView.openLink(bibkey, "arxiv")
		elif self.colContents[col] == "inspire" and entry["inspire"] is not None and entry["inspire"] != "":
			pBGuiView.openLink(bibkey, "inspire")
		elif self.colContents[col] == "pdf":
			pdfFiles = pBPDF.getExisting(bibkey, fullPath = True)
			if len(pdfFiles) == 1:
				self.parent.StatusBarMessage("opening PDF...")
				pBGuiView.openLink(bibkey, "file", fileArg = pdfFiles[0])
			elif len(pdfFiles) > 1:
				ask = askPdfAction(self, bibkey, entry["arxiv"], entry["doi"])
				ask.exec_(QCursor.pos())
				if ask.result == "openArxiv":
					self.parent.StatusBarMessage("opening arxiv PDF...")
					pBGuiView.openLink(bibkey, "file", fileArg = pBPDF.getFilePath(bibkey, "arxiv"))
				elif ask.result == "openDoi":
					self.parent.StatusBarMessage("opening doi PDF...")
					pBGuiView.openLink(bibkey, "file", fileArg = pBPDF.getFilePath(bibkey, "doi"))
				elif type(ask.result) is str and "openOther_" in ask.result:
					filename = ask.result.replace("openOther_", "")
					self.parent.StatusBarMessage("opening %s..."%filename)
					pBGuiView.openLink(bibkey, "file", fileArg = os.path.join(pBPDF.getFileDir(bibkey), filename))

	def downloadArxivDone(self):
		self.parent.sendMessage("Arxiv download execution completed! Please check that it worked...")
		self.parent.done()
		self.parent.reloadMainContent(pBDB.bibs.fetchFromLast().lastFetched)

	def arxivAbstract(self, arxiv, bibkey, message = True):
		if arxiv:
			bibtex, full = physBiblioWeb.webSearch["arxiv"].retrieveUrlAll(arxiv, searchType = "id", fullDict = True)
			abstract = full["abstract"]
			pBDB.bibs.updateField(bibkey, "abstract", abstract)
			if message:
				infoMessage(abstract, title = "Abstract of arxiv:%s"%arxiv)
		else:
			infoMessage("No arxiv number for entry '%s'!"%bibkey)

	def copyToClipboard(self, text):
		"""copy the given text to the clipboard"""
		pBLogger.info("Copying to clipboard: '%s'"%text)
		clipboard = QApplication.clipboard()
		clipboard.setText(text)

	def finalizeTable(self):
		"""resize the table to fit the contents, connect click and doubleclick functions, add layout"""
		font = QFont()
		font.setPointSize(pbConfig.params["bibListFontSize"])
		self.tablewidget.setFont(font)

		self.tablewidget.resizeColumnsToContents()
		self.tablewidget.resizeRowsToContents()

		self.tablewidget.clicked.connect(self.cellClick)
		self.tablewidget.doubleClicked.connect(self.cellDoubleClick)

		self.currLayout.addWidget(self.tablewidget)

	def recreateTable(self, bibs = None):
		"""delete previous table widget and create a new one"""
		if bibs is not None:
			self.bibs = bibs
		else:
			self.bibs = pBDB.bibs.getAll(orderType = "DESC", limitTo = pbConfig.params["defaultLimitBibtexs"])
		self.cleanLayout()
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
		self.markValues = {}
		self.checkboxes = ["exp_paper", "lecture", "phd_thesis", "review", "proceeding", "book", "noUpdate"]
		self.createForm()

	def onOk(self):
		if self.textValues["bibtex"].toPlainText() == "":
			pBGUILogger.error("Invalid form contents: empty bibtex!")
			return False
		elif not self.textValues["bibkey"].isReadOnly() and self.textValues["bibkey"].text() != "" and self.textValues["bibtex"].toPlainText() != "":
			pBGUILogger.error("Invalid form contents: bibtex key will be taken from bibtex!")
			return False
		self.result	= True
		self.close()

	def updateBibkey(self):
		bibtex = self.textValues["bibtex"].toPlainText()
		try:
			element = bibtexparser.loads(bibtex).entries[0]
			bibkey = element["ID"]
		except (ValueError, IndexError, ParseException):
			bibkey = "not valid bibtex!"
		self.textValues["bibkey"].setText(bibkey)

	def createForm(self):
		self.setWindowTitle('Edit bibtex entry')

		i = 0
		for k in pBDB.tableCols["entries"]:
			val = self.data[k] if self.data[k] is not None else ""
			if k != "bibtex" and k != "marks" and k != "abstract" and k not in self.checkboxes:
				i += 1
				self.currGrid.addWidget(QLabel(k), int((i+1-(i+i)%2)/2)*2-1, ((1+i)%2)*2)
				self.currGrid.addWidget(QLabel("(%s)"%pBDB.descriptions["entries"][k]),  int((i+1-(i+i)%2)/2)*2-1, ((1+i)%2)*2+1)
				self.textValues[k] = QLineEdit(str(val))
				if k == "bibkey" and val != "":
					self.textValues[k].setReadOnly(True)
				self.currGrid.addWidget(self.textValues[k], int((i+1-(i+i)%2)/2)*2, ((1+i)%2)*2, 1, 2)
			elif k == "marks":
				i += 1
				groupBox, markValues = pBMarks.getGroupbox(self.data["marks"], description = pBDB.descriptions["entries"]["marks"])
				self.markValues = markValues
				if ((1+i)%2)*2 != 0:
					i += 1
				self.currGrid.addWidget(groupBox, int((i+1-(i+i)%2)/2)*2, ((1+i)%2)*2, 1, 4)

		self.textValues["bibkey"].setReadOnly(True)

		#bibtex text editor
		i += 1 + i%2
		k = "bibtex"
		self.currGrid.addWidget(QLabel(k), int((i+1-(i+i)%2)/2)*2-1, ((1+i)%2)*2)
		self.currGrid.addWidget(QLabel("(%s)"%pBDB.descriptions["entries"][k]),  int((i+1-(i+i)%2)/2)*2-1, ((1+i)%2)*2+1)
		self.textValues[k] = QPlainTextEdit(self.data[k])
		self.textValues["bibtex"].textChanged.connect(self.updateBibkey)
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

class MyPdfAction(QAction):
	def __init__(self, filename, parentMenu, *args, **kwargs):
		QAction.__init__(self, *args, triggered = self.returnFileName, **kwargs)
		self.filename = filename
		self.parentMenu = parentMenu

	def returnFileName(self):
		self.parentMenu.result = "openOther_%s"%self.filename
		self.parentMenu.close()

class askPdfAction(MyMenu):
	def __init__(self, parent = None, key = "", arxiv = None, doi = None):
		super(askPdfAction, self).__init__(parent)
		self.message = "What PDF of this entry (%s) do you want to open?"%(key)
		self.possibleActions = []
		files = pBPDF.getExisting(key, fullPath = True)
		if pBPDF.getFilePath(key, "arxiv") in files:
			self.possibleActions.append(QAction("Open arxiv PDF", self, triggered = self.onOpenArxiv))
			files.remove(pBPDF.getFilePath(key, "arxiv"))
		if pBPDF.getFilePath(key, "doi") in files:
			self.possibleActions.append(QAction("Open DOI PDF", self, triggered = self.onOpenDoi))
			files.remove(pBPDF.getFilePath(key, "doi"))
		for f in files:
			self.possibleActions.append(MyPdfAction(f, self, "Open %s"%f.split(os.sep)[-1], self))

		self.fillMenu()

	def onOpenOther(self, filename):
		self.result = "openOther_%s"%filename
		self.close()

	def onOpenArxiv(self):
		self.result	= "openArxiv"
		self.close()

	def onOpenDoi(self):
		self.result	= "openDoi"
		self.close()

class askSelBibAction(MyMenu):
	def __init__(self, parent = None, keys = []):
		super(askSelBibAction, self).__init__(parent)
		self.keys = keys
		self.entries = []
		for k in keys:
			self.entries.append(pBDB.bibs.getByBibkey(k)[0])
		self.parent = parent
		self.result = "done"
		if len(keys) == 2:
			self.possibleActions.append(QAction("Merge entries", self, triggered = self.onMerge))
		self.possibleActions.append(QAction("Clean entries", self, triggered = self.onClean))
		self.possibleActions.append(QAction("Update entries", self, triggered = self.onUpdate))
		self.possibleActions.append(None)
		self.possibleActions.append(QAction("Load abstract from arXiv", self, triggered = self.onAbs))
		self.possibleActions.append(QAction("Get fields from arXiv", self, triggered = self.onArx))
		self.possibleActions.append(QAction("Download PDF from arXiv", self, triggered = self.onDown))
		self.possibleActions.append(None)
		self.possibleActions.append(QAction("Export entries in a .bib file", self, triggered = self.onExport))
		self.possibleActions.append(None)
		self.possibleActions.append(QAction("Copy all the (existing) PDF", self, triggered = self.copyAllPdf))
		self.possibleActions.append(None)
		self.possibleActions.append(QAction("Select categories", self, triggered = self.onCat))
		self.possibleActions.append(QAction("Select experiments", self, triggered = self.onExp))

		self.fillMenu()

	def onMerge(self):
		mergewin = mergeBibtexs(self.entries[0], self.entries[1], self.parent)
		mergewin.exec_()
		if mergewin.result is True:
			data = {}
			for k, v in mergewin.textValues.items():
				try:
					s = "%s"%v.text()
					data[k] = s
				except AttributeError:
					try:
						s = "%s"%v.toPlainText()
						data[k] = s
					except AttributeError:
						pass
			for k, v in mergewin.checkValues.items():
				if v.isChecked():
					data[k] = 1
				else:
					data[k] = 0
			data["marks"] = ""
			for m, ckb in mergewin.markValues.items():
				if ckb.isChecked():
					data["marks"] += "'%s',"%m
			if data["old_keys"].strip() != "":
				data["old_keys"] = ", ".join([data["old_keys"], self.entries[0]["bibkey"], self.entries[1]["bibkey"]])
			else:
				data["old_keys"] = ", ".join([self.entries[0]["bibkey"], self.entries[1]["bibkey"]])
			data = pBDB.bibs.prepareInsert(**data)
			if data["bibkey"].strip() != "" and data["bibtex"].strip() != "":
				pBDB.commit()
				try:
					for key in [self.entries[0]["bibkey"], self.entries[1]["bibkey"]]:
						pBDB.bibs.delete(key)
				except:
					pBGUILogger.exception("Cannot delete old items!")
					pBDB.undo()
				else:
					if not pBDB.bibs.insert(data):
						pBGUILogger.error("Cannot insert new item!")
						pBDB.undo()
					else:
						self.parent.setWindowTitle("PhysBiblio*")
						try:
							self.parent.reloadMainContent(pBDB.bibs.fetchFromLast().lastFetched)
						except:
							pBLogger.warning("Impossible to reload content.")
			else:
				pBGUILogger.error("Empty bibtex and/or bibkey!")
		self.close()

	def onClean(self):
		self.parent.cleanAllBibtexs(self, useEntries = self.entries)
		self.close()

	def onUpdate(self):
		self.parent.updateAllBibtexs(self, useEntries = self.entries)
		self.close()

	def onAbs(self):
		infoMessage("Starting the abstract download process, please wait...")
		for entry in self.entries:
			self.parent.bibtexList.arxivAbstract(entry["arxiv"], entry["bibkey"], message = False)
		infoMessage("Done!")
		self.close()

	def onArx(self):
		self.parent.infoFromArxiv(self.entries)
		self.close()

	def onDown(self):
		self.downArxiv_thr = []
		for entry in self.entries:
			if entry["arxiv"] is not None:
				self.parent.StatusBarMessage("downloading PDF for arxiv:%s..."%entry["arxiv"])
				self.downArxiv_thr.append(thread_downloadArxiv(entry["bibkey"], self.parent))
				self.downArxiv_thr[-1].finished.connect(self.parent.bibtexList.downloadArxivDone)
				self.downArxiv_thr[-1].start()
		self.close()

	def onExport(self):
		self.parent.exportSelection(self.entries)
		self.close()

	def copyAllPdf(self):
		outFolder = askDirName(self, title = "Where do you want to save the PDF files?")
		if outFolder.strip() != "":
			for entryDict in self.entries:
				entry = entryDict["bibkey"]
				if pBPDF.checkFile(entry, "doi"):
					pBPDF.copyToDir(outFolder, entry, fileType = "doi")
				elif pBPDF.checkFile(entry, "arxiv"):
					pBPDF.copyToDir(outFolder, entry, fileType = "arxiv")
				else:
					existing = pBPDF.getExisting(entry)
					if len(existing) > 0:
						for ex in existing:
							pBPDF.copyToDir(outFolder, entry, "", customName = ex)
		self.close()

	def onCat(self):
		previousAll = [e["idCat"] for e in pBDB.cats.getByEntries(self.keys)]
		selectCats = catsWindowList(parent = self.parent, askCats = True, expButton = False, previous = previousAll, multipleRecords = True)
		selectCats.exec_()
		if selectCats.result == "Ok":
			for c in self.parent.previousUnchanged:
				if c in previousAll:
					del previousAll[previousAll.index(c)]
			for c in previousAll:
				if c not in self.parent.selectedCats:
					pBDB.catBib.delete(c, self.keys)
			pBDB.catBib.insert(self.parent.selectedCats, self.keys)
			self.parent.StatusBarMessage("categories successfully inserted")
		self.close()

	def onExp(self):
		infoMessage("Warning: you can just add experiments to the selected entries, not delete!")
		selectExps = ExpWindowList(parent = self.parent, askExps = True, previous = [])
		selectExps.exec_()
		if selectExps.result == "Ok":
			pBDB.bibExp.insert(self.keys, self.parent.selectedExps)
			self.parent.StatusBarMessage("experiments successfully inserted")
		self.close()

class searchBibsWindow(editObjectWindow):
	"""create a window for editing or creating a bibtex entry"""
	def __init__(self, parent = None, bib = None, replace = False):
		super(searchBibsWindow, self).__init__(parent)
		self.textValues = []
		self.result = False
		self.replace = replace
		self.possibleTypes = {
			"exp_paper": {"desc": "Experimental"},
			"lecture": {"desc": "Lecture"},
			"phd_thesis": {"desc": "PhD thesis"},
			"review": {"desc": "Review"},
			"proceeding": {"desc": "Proceeding"},
			"book": {"desc": "Book"}
			}
		self.values = {}
		self.values["cats"] = []
		self.values["exps"] = []
		self.values["catsOperator"] = "AND"
		self.values["expsOperator"] = "AND"
		self.values["catExpOperator"] = "AND"
		self.values["marks"] = []
		self.values["marksConn"] = "AND"
		self.values["type"] = []
		self.values["typeConn"] = "AND"
		self.numberOfRows = 1
		self.replOld = None
		self.replNew = None
		self.replNew1 = None
		self.limitValue = None
		self.limitOffs = None
		self.createForm()

	def onAskCats(self):
		selectCats = catsWindowList(parent = self, askCats = True, expButton = False, previous = self.values["cats"])
		selectCats.exec_()
		if selectCats.result == "Ok":
			self.values["cats"] = self.selectedCats

	def onAskExps(self):
		selectExps = ExpWindowList(parent = self.parent, askExps = True, previous = self.values["exps"])
		selectExps.exec_()
		if selectExps.result == "Ok":
			self.values["exps"] = self.parent.selectedExps

	def onComboCatsChange(self, text):
		self.values["catsOperator"] = text

	def onComboExpsChange(self, text):
		self.values["expsOperator"] = text

	def onComboCEChange(self, text):
		self.values["CatExpOperator"] = text

	def getMarksValues(self):
		self.values["marksConn"] = self.marksConn.currentText()
		self.values["marks"] = []
		for m in self.markValues.keys():
			if self.markValues[m].isChecked():
				self.values["marks"].append(m)

	def getTypeValues(self):
		self.values["typeConn"] = self.typeConn.currentText()
		self.values["type"] = []
		for m in self.typeValues.keys():
			if self.typeValues[m].isChecked():
				self.values["type"].append(m)

	def onAddField(self):
		self.numberOfRows = self.numberOfRows + 1
		self.getMarksValues()
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
				widget in [a["content"] for a in self.textValues] + [self.replOld, self.replNew, self.limitValue, self.limitOffs]):
			key = event.key()
			if key == Qt.Key_Return or key == Qt.Key_Enter:
				self.acceptButton.setFocus()
				return True
		return QWidget.eventFilter(self, widget, event)

	def createForm(self, spaceRowHeight = 25):
		self.setWindowTitle('Search bibtex entries')

		self.currGrid.addWidget(MyLabelRight("Filter by categories, using the following operator:"), 0, 0, 1, 3)
		self.catsButton = QPushButton('Categories', self)
		self.catsButton.clicked.connect(self.onAskCats)
		self.currGrid.addWidget(self.catsButton, 0, 3, 1, 2)
		self.comboCats = MyAndOrCombo(self)
		self.comboCats.activated[str].connect(self.onComboCatsChange)
		self.currGrid.addWidget(self.comboCats, 0, 5)

		self.currGrid.addWidget(MyLabelRight("Filter by experiments, using the following operator:"), 1, 0, 1, 3)
		self.expsButton = QPushButton('Experiments', self)
		self.expsButton.clicked.connect(self.onAskExps)
		self.currGrid.addWidget(self.expsButton, 1, 3, 1, 2)
		self.comboExps = MyAndOrCombo(self)
		self.comboExps.activated[str].connect(self.onComboExpsChange)
		self.currGrid.addWidget(self.comboExps, 1, 5)

		self.currGrid.addWidget(MyLabelRight("If using both categories and experiments, which operator between them?"), 2, 0, 1, 4)
		self.comboCE = MyAndOrCombo(self)
		self.comboCE.activated[str].connect(self.onComboCEChange)
		self.currGrid.addWidget(self.comboCE, 2, 5)

		self.currGrid.setRowMinimumHeight(3, spaceRowHeight)

		self.marksConn = MyAndOrCombo(self, current = self.values["marksConn"])
		self.currGrid.addWidget(self.marksConn, 4, 0)
		self.currGrid.addWidget(MyLabelRight("Filter by marks:"), 4, 1)
		groupBox, markValues = pBMarks.getGroupbox(self.values["marks"], description = "", radio = True, addAny = True)
		self.markValues = markValues
		self.currGrid.addWidget(groupBox, 4, 2, 1, 5)

		self.typeConn = MyAndOrCombo(self, current = self.values["typeConn"])
		self.currGrid.addWidget(self.typeConn, 5, 0)
		self.currGrid.addWidget(MyLabelRight("Entry type:"), 5, 1)
		groupBox = QGroupBox()
		self.typeValues = {}
		groupBox.setFlat(True)
		vbox = QHBoxLayout()
		for m, cont in self.possibleTypes.items():
			self.typeValues[m] = QRadioButton(cont["desc"])
			if m in self.values["type"]:
				self.typeValues[m].setChecked(True)
			vbox.addWidget(self.typeValues[m])
		vbox.addStretch(1)
		groupBox.setLayout(vbox)
		self.currGrid.addWidget(groupBox, 5, 2, 1, 5)

		self.currGrid.addWidget(QLabel("Select more: the operator to use, the field to match, (exact match vs contains) and the content to match"), 7, 0, 1, 7)
		firstFields = 8
		self.currGrid.setRowMinimumHeight(6, spaceRowHeight)

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
			self.currGrid.addWidget(self.textValues[i]["content"], i + firstFields, 3, 1, 4)
			self.textValues[i]["content"].installEventFilter(self)

		self.textValues[-1]["content"].setFocus()

		i = self.numberOfRows + firstFields + 1
		self.currGrid.addWidget(MyLabelRight("Click here if you want more fields:"), i-1, 0, 1, 2)
		self.addFieldButton = QPushButton("Add another line", self)
		self.addFieldButton.clicked.connect(self.onAddField)
		self.currGrid.addWidget(self.addFieldButton, i-1, 2, 1, 2)

		self.currGrid.setRowMinimumHeight(i, spaceRowHeight)

		i += 2
		if self.replace:
			self.currGrid.addWidget(QLabel("Replace:"), i - 1, 0)
			self.currGrid.addWidget(MyLabelRight("regex:"), i - 1, 2)
			self.replRegex = QCheckBox("", self)
			self.currGrid.addWidget(self.replRegex, i - 1, 3)
			try:
				fieOld = self.replOldField.currentText()
				fieNew = self.replNewField.currentText()
				fieNew1 = self.replNewField1.currentText()
				double = self.doubleEdit.isChecked()
				old = self.replOld.text()
				new = self.replNew.text()
				new1 = self.replNew1.text()
			except AttributeError:
				fieOld = "author"
				fieNew = "author"
				fieNew1 = "author"
				double = False
				old = ""
				new = ""
				new1 = ""
			self.currGrid.addWidget(MyLabelRight("From field:"), i, 0)
			self.replOldField = MyComboBox(self, ["arxiv", "doi", "year", "author", "title", "journal", "number", "volume", "published"], current = fieNew)
			self.currGrid.addWidget(self.replOldField, i, 1, 1, 2)
			self.replOld = QLineEdit(old)
			self.currGrid.addWidget(self.replOld, i, 3, 1, 3)
			i += 1
			self.currGrid.addWidget(MyLabelRight("Into field:"), i, 0)
			self.replNewField = MyComboBox(self, ["arxiv", "doi", "year", "author", "title", "journal", "number", "volume"], current = fieNew)
			self.currGrid.addWidget(self.replNewField, i, 1, 1, 2)
			self.replNew = QLineEdit(new)
			self.currGrid.addWidget(self.replNew, i, 3, 1, 3)
			i += 1
			self.doubleEdit = QCheckBox("and also:")
			self.currGrid.addWidget(self.doubleEdit, i, 0)
			self.replNewField1 = MyComboBox(self, ["arxiv", "doi", "year", "author", "title", "journal", "number", "volume"], current = fieNew)
			self.currGrid.addWidget(self.replNewField1, i, 1, 1, 2)
			self.replNew1 = QLineEdit(new1)
			self.currGrid.addWidget(self.replNew1, i, 3, 1, 3)
			self.replOld.installEventFilter(self)
			self.replNew.installEventFilter(self)
			self.limitValue = QLineEdit("100000")
			self.limitOffs = QLineEdit("0")
			i += 1
		else:
			#limit to, limit offset
			try:
				lim = self.limitValue.text()
				offs = self.limitOffs.text()
			except AttributeError:
				lim = str(pbConfig.params["defaultLimitBibtexs"])
				offs = "0"
			self.currGrid.addWidget(MyLabelRight("Max number of results:"), i - 1, 0, 1, 2)
			self.limitValue = QLineEdit(lim)
			self.limitValue.setMaxLength(6)
			self.limitValue.setFixedWidth(75)
			self.currGrid.addWidget(self.limitValue, i - 1, 2)
			self.currGrid.addWidget(MyLabelRight("Start from:"), i - 1, 3, 1, 2)
			self.limitOffs = QLineEdit(offs)
			self.limitOffs.setMaxLength(6)
			self.limitOffs.setFixedWidth(75)
			self.currGrid.addWidget(self.limitOffs, i - 1, 5)
			self.limitValue.installEventFilter(self)
			self.limitOffs.installEventFilter(self)

		self.currGrid.setRowMinimumHeight(i, spaceRowHeight)
		i += 1

		# OK button
		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		self.currGrid.addWidget(self.acceptButton, i, 2)
		self.acceptButton.setFixedWidth(80)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		self.currGrid.addWidget(self.cancelButton, i, 3)
		self.cancelButton.setFixedWidth(80)

		self.currGrid.setColumnStretch(6, 1)

class mergeBibtexs(editBibtexEntry):
	def __init__(self, bib1, bib2, parent = None):
		super(editBibtexEntry, self).__init__(parent)
		self.bibtexEditLines = 8
		self.bibtexWidth = 330
		self.dataOld = {"0": bib1, "1": bib2}
		self.data = {}
		for k in pBDB.tableCols["entries"]:
			self.data[k] = ""
		self.checkValues = {}
		self.markValues = {}
		self.radioButtons = {"0": {}, "1": {}}
		self.textValues["0"] = {}
		self.textValues["1"] = {}
		self.checkboxes = ["exp_paper", "lecture", "phd_thesis", "review", "proceeding", "book", "noUpdate"]
		self.generic = ["year", "doi", "arxiv", "inspire", "isbn", "firstdate", "pubdate", "ads", "scholar", "link", "comments", "old_keys", "crossref"]
		self.createForm()

	def radioToggled(self, ix, k, val):
		self.radioButtons[ix][k].setChecked(True)
		self.radioButtons[str((int(ix)+1)%2)][k].setChecked(False)
		if k == "bibtex":
			self.textValues[k].blockSignals(True)
			self.textValues[k].setPlainText(self.dataOld[ix][k])
			self.textValues[k].blockSignals(False)
			self.updateBibkey()
		else:
			self.textValues[k].setText(str(self.dataOld[ix][k]))

	def textModified(self, k, val):
		for ix in ["0", "1"]:
			self.radioButtons[ix][k].setChecked(False)

	def createForm(self):
		def addFieldOld(ix, k, i, c):
			self.textValues[ix][k] = QLineEdit(str(self.dataOld[ix][k] if self.dataOld[ix][k] is not None else ""))
			self.textValues[ix][k].setReadOnly(True)
			self.currGrid.addWidget(self.textValues[ix][k], i, c)
		def addFieldNew(k, i, v):
			self.textValues[k] = QLineEdit(str(v))
			self.textValues[k].textEdited.connect(lambda x: self.textModified(k, x))
			self.currGrid.addWidget(self.textValues[k], i, 2)
		def addRadio(ix, k, i, c):
			self.radioButtons[ix][k] = QRadioButton("")
			self.radioButtons[ix][k].setAutoExclusive(False)
			self.radioButtons[ix][k].clicked.connect(lambda x = False: self.radioToggled(ix, k, x))
			self.currGrid.addWidget(self.radioButtons[ix][k], i, c)
		def addBibtexOld(ix, i, c):
			k = "bibtex"
			self.textValues[ix][k] = QPlainTextEdit(str(self.dataOld[ix][k] if self.dataOld[ix][k] is not None else ""))
			self.textValues[ix][k].setReadOnly(True)
			self.textValues[ix][k].setMinimumWidth(self.bibtexWidth)
			self.currGrid.addWidget(self.textValues[ix][k], i, c, self.bibtexEditLines, 1)
		self.setWindowTitle('Merge bibtex entries')

		i = 0
		for k in self.generic:
			if self.dataOld["0"][k] == self.dataOld["1"][k]:
				self.textValues[k] = QLineEdit(str(self.dataOld["0"][k]))
				self.textValues[k].hide()
			else:
				self.currGrid.addWidget(MyLabelCenter("%s (%s)"%(k, pBDB.descriptions["entries"][k])), i, 0, 1, 5)
				i += 1
				addFieldOld("0", k, i, 0)
				addRadio("0", k, i, 1)
				addFieldOld("1", k, i, 4)
				addRadio("1", k, i, 3)

				#add radio
				if self.dataOld["0"][k] != "" and self.dataOld["1"][k] == "":
					self.radioButtons["0"][k].toggle()
					val = self.dataOld["0"][k]
				elif self.dataOld["0"][k] == "" and self.dataOld["1"][k] != "":
					self.radioButtons["1"][k].toggle()
					val = self.dataOld["1"][k]
				else:
					val = ""
				addFieldNew(k, i, val)
				i += 1

		i += 1
		groupBox, markValues = pBMarks.getGroupbox(self.data["marks"], description = pBDB.descriptions["entries"]["marks"])
		self.markValues = markValues
		self.currGrid.addWidget(groupBox, i, 0, 1, 5)
		i += 1
		groupBox = QGroupBox("Types")
		groupBox.setFlat(True)
		hbox = QHBoxLayout()
		for k in pBDB.tableCols["entries"]:
			if k in self.checkboxes:
				self.checkValues[k] = QCheckBox(k, self)
				hbox.addWidget(self.checkValues[k])
		groupBox.setLayout(hbox)
		self.currGrid.addWidget(groupBox, i, 0, 1, 5)

		#bibtex text editor
		i += 1
		k = "bibkey"
		self.currGrid.addWidget(MyLabelCenter("%s (%s)"%(k, pBDB.descriptions["entries"][k])), i, 0, 1, 5)
		i += 1
		addFieldOld("0", k, i, 0)
		addFieldOld("1", k, i, 4)
		self.textValues[k] = QLineEdit("")
		self.textValues[k].setReadOnly(True)
		self.currGrid.addWidget(self.textValues[k], i, 2)
		i += 1
		k = "bibtex"
		self.currGrid.addWidget(MyLabelCenter("%s (%s)"%(k, pBDB.descriptions["entries"][k])), i, 0, 1, 5)
		i += 1
		addBibtexOld("0", i, 0)
		addRadio("0", k, i, 1)
		addBibtexOld("1", i, 4)
		addRadio("1", k, i, 3)
		#radio and connection
		self.textValues[k] = QPlainTextEdit(str(self.data[k] if self.data[k] is not None else ""))
		self.textValues[k].textChanged.connect(self.updateBibkey)
		self.textValues[k].setMinimumWidth(self.bibtexWidth)
		self.textValues[k].textChanged.connect(lambda x = "": self.textModified("bibtex", str(x)))
		self.currGrid.addWidget(self.textValues[k], i, 2, self.bibtexEditLines, 1)
		i += self.bibtexEditLines

		# OK button
		i += 1
		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		self.currGrid.addWidget(self.acceptButton, i, 0, 1, 2)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		self.currGrid.addWidget(self.cancelButton, i, 3, 1, 2)

		self.setGeometry(100,100,3*self.bibtexWidth+50, 25*i)
		self.centerWindow()

class fieldsFromArxiv(QDialog):
	def __init__(self, parent = None):
		super(fieldsFromArxiv, self).__init__(parent)
		self.setWindowTitle("Import fields from arXiv")
		self.parent = parent
		self.checkBoxes = {}
		self.arxivDict = ["authors", "title", "doi", "primaryclass", "archiveprefix"]
		vbox = QVBoxLayout()
		for k in self.arxivDict:
			self.checkBoxes[k] = QCheckBox(k, self)
			self.checkBoxes[k].setChecked(True)
			vbox.addWidget(self.checkBoxes[k])
		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		vbox.addWidget(self.acceptButton)
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		vbox.addWidget(self.cancelButton)
		self.setLayout(vbox)

	def onOk(self):
		self.output = []
		for k in self.checkBoxes.keys():
			if self.checkBoxes[k].isChecked():
				self.output.append(k)
		self.result = True
		self.close()

	def onCancel(self):
		self.result = False
		self.close()
