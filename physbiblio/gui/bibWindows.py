"""Module with the classes and functions that manage
the entries windows and panels.

This file is part of the physbiblio package.
"""
import traceback
import os
import matplotlib
import ast
matplotlib.use('Qt5Agg')
os.environ["QT_API"] = 'pyside2'
from matplotlib.backends.backend_agg import FigureCanvasAgg
import bibtexparser
import re
from pyparsing import ParseException
from pylatexenc.latex2text import LatexNodes2Text
from PySide2.QtCore import Qt, QEvent, QUrl
from PySide2.QtGui import QCursor, QFont, QIcon, QImage, QTextDocument
from PySide2.QtWidgets import \
	QAction, QApplication, QCheckBox, QComboBox, QDialog, QFrame, QGroupBox, \
	QHBoxLayout, QLineEdit, QPlainTextEdit, QPushButton, \
	QRadioButton, QTextEdit, QToolBar, QVBoxLayout, QWidget

try:
	from physbiblio.errors import pBLogger
	from physbiblio.database import pBDB
	from physbiblio.config import pbConfig
	from physbiblio.pdf import pBPDF
	from physbiblio.parseAccents import texToHtml
	from physbiblio.webimport.webInterf import physBiblioWeb
	from physbiblio.gui.errorManager import pBGUILogger
	from physbiblio.gui.marks import pBMarks
	from physbiblio.gui.basicDialogs import \
		askDirName, askFileName, askYesNo, infoMessage
	from physbiblio.gui.commonClasses import \
		editObjectWindow, MyAndOrCombo, MyComboBox, MyLabel, \
		MyLabelCenter, MyLabelRight, MyMenu, MyTableModel, \
		objListWindow, pBGuiView
	from physbiblio.gui.threadElements import \
		thread_downloadArxiv, thread_processLatex
	from physbiblio.gui.catWindows import catsTreeWindow
	from physbiblio.gui.expWindows import ExpsListWindow
	import physbiblio.gui.resourcesPyside2
except ImportError:
	print("Could not find physbiblio and its modules!")
	print(traceback.format_exc())

convertType = {
	"review": "Review",
	"proceeding": "Proceeding",
	"book": "Book",
	"phd_thesis": "PhD thesis",
	"lecture": "Lecture",
	"exp_paper": "Experimental paper",
}


def copyToClipboard(text):
	"""Copy the given text to the clipboard

	Parameter:
		text: the string to be copied to clipboard
	"""
	pBLogger.info("Copying to clipboard: '%s'"%text)
	clipboard = QApplication.clipboard()
	clipboard.setText(text)


def writeBibtexInfo(entry):
	"""Use the database information in order to write a short text
	that contains some relevant info on the bibtex entry,
	such as type, title, authors, journal and identification info.

	Parameter:
		entry: the database record from which to extract the info

	Output:
		a string
	"""
	infoText = ""
	for t in convertType.keys():
		try:
			if entry[t] == 1:
				infoText += "(%s) "%convertType[t]
		except KeyError:
			pBLogger.debug("KeyError: '%s' not in %s"%(
				t, sorted(entry.keys())))
	infoText += "<u>%s</u> (use with '<u>\cite{%s}</u>')<br/>\n"%(
		entry["bibkey"], entry["bibkey"])
	latexToText = LatexNodes2Text(
		keep_inline_math=True, keep_comments=False)
	try:
		infoText += "<b>%s</b><br/>\n"%(
			latexToText.latex_to_text(entry["bibtexDict"]["author"]))
	except KeyError:
		pBLogger.debug(
			"KeyError: 'author' not in %s"%(
				sorted(entry["bibtexDict"].keys())))
	try:
		infoText += "%s<br/>\n"%(
			latexToText.latex_to_text(entry["bibtexDict"]["title"]))
	except KeyError:
		pBLogger.debug(
			"KeyError: 'title' not in %s"%(
				sorted(entry["bibtexDict"].keys())))
	try:
		infoText += "<i>%s %s (%s) %s</i><br/>\n"%(
			entry["bibtexDict"]["journal"],
			entry["bibtexDict"]["volume"],
			entry["bibtexDict"]["year"],
			entry["bibtexDict"]["pages"])
	except KeyError:
		pBLogger.debug(
			"KeyError: 'journal', 'volume', 'year' or 'pages' not in %s"%(
				sorted(entry["bibtexDict"].keys())))
	infoText += "<br/>"
	for k in ["isbn", "doi", "arxiv", "ads", "inspire"]:
		try:
			infoText += "%s: <u>%s</u><br/>"%(
				pBDB.descriptions["entries"][k], entry[k]) \
					if (entry[k] is not None and entry[k] != "") else ""
		except KeyError:
			pBLogger.debug("KeyError: '%s' not in %s"%(k,
				sorted(entry.keys())))
	cats = pBDB.cats.getByEntry(entry["bibkey"])
	infoText += "\n<br/>Categories: <i>%s</i>"%(
		", ".join([c["name"] for c in cats]) if len(cats) > 0 else "None")
	exps = pBDB.exps.getByEntry(entry["bibkey"])
	infoText += "\n<br/>Experiments: <i>%s</i>"%(
		", ".join([e["name"] for e in exps]) if len(exps) > 0 else "None")
	return infoText


def writeAbstract(mainWin, entry):
	"""Process and write the abstract to the dedicated mainWindow panel

	Parameters:
		mainWin: the `mainWindow` instance where to write the abstract
		entry: the database record of the entry
	"""
	a = AbstractFormulas(mainWin, entry["abstract"])
	a.doText()


def editBibtex(parentObject, editKey=None, testing=False):
	"""Open a dialog (`EditBibtexDialog`) to edit a bibtex entry
	and process the output.

	Parameters:
		parentObject: the parent widget
		editKey: the key of the entry to be edited,
			or `None` to create a new one
		testing (default False): when doing tests,
			interrupt the execution before `exec_` and
			replace `newBibWin` with the passed object.
	"""
	if editKey is not None:
		edit = pBDB.bibs.getByKey(editKey, saveQuery=False)[0]
	else:
		edit = None
	newBibWin = EditBibtexDialog(parentObject, bib=edit)
	if testing:
		newBibWin = testing
	else:
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
		if data["bibtex"].strip() != "":
			if "bibkey" not in data.keys() or data["bibkey"].strip() == "":
				data = pBDB.bibs.prepareInsert(data["bibtex"].strip())
			if data["bibkey"].strip() != "":
				if editKey is not None:
					if data["bibkey"].strip() != editKey:
						if data["bibkey"].strip() != "not valid bibtex!":
							pBLogger.info(
								"New bibtex key (%s) for element '%s'..."%(
									data["bibkey"], editKey))
							if editKey not in data["old_keys"]:
								data["old_keys"] += " " + editKey
								data["old_keys"] = data["old_keys"].strip()
							if pBDB.bibs.updateBibkey(
									editKey, data["bibkey"].strip()):
								pBPDF.renameFolder(editKey,
									data["bibkey"].strip())
							else:
								pBGUILogger.warning(
									"Cannot update bibtex key: "
									+ "already present. "
									+ "Restoring previous one.")
								data["bibtex"] = data["bibtex"].replace(
									data["bibkey"], editKey)
								data["bibkey"] = editKey
						else:
							data["bibkey"] = editKey
					pBLogger.info(
						"Updating bibtex '%s'..."%data["bibkey"])
					pBDB.bibs.update(data, data["bibkey"])
				else:
					pBDB.bibs.insert(data)
				message = "Bibtex entry saved"
				try:
					parentObject.mainWindowTitle("PhysBiblio*")
				except AttributeError:
					pBLogger.debug(
						"parentObject has no attribute 'mainWindowTitle'",
						exc_info=True)
				pBDB.bibs.fetchFromLast()
				try:
					parentObject.reloadMainContent(
						pBDB.bibs.lastFetched)
				except AttributeError:
					pBLogger.debug(
						"parentObject has no attribute 'reloadMainContent'",
						exc_info=True)
			else:
				message = "ERROR: empty bibkey!"
				infoMessage(message)
		else:
			message = "ERROR: empty bibtex!"
			infoMessage(message)
	else:
		message = "No modifications to bibtex entry"
	try:
		parentObject.statusBarMessage(message)
	except AttributeError:
		pBLogger.debug("parentObject has no attribute 'statusBarMessage'",
			exc_info=True)


def deleteBibtex(parentObject, bibkey):
	"""Ask confirmation and eventually delete the selected bibtex entry

	Parameters:
		parentObject: the parent object, which has
			the `statusBarMessage` and `setWindowTitle` methods
			and a `bibtexListWindow` attribute
		bibkey: the bibtex key of the entry to be deleted
	"""
	if askYesNo("Do you really want to delete this bibtex entry "
			+ "(bibkey = '%s')?"%(bibkey)):
		pBDB.bibs.delete(bibkey)
		parentObject.setWindowTitle("PhysBiblio*")
		message = "Bibtex entry deleted"
		try:
			parentObject.bibtexListWindow.recreateTable()
		except AttributeError:
			pBLogger.debug("parentObject has no attribute 'recreateTable'",
				exc_info=True)
	else:
		message = "Nothing changed"
	try:
		parentObject.statusBarMessage(message)
	except AttributeError:
		pBLogger.debug("parentObject has no attribute 'statusBarMessage'",
			exc_info=True)


class AbstractFormulas():
	"""Class that manages the transformation of the math formulas
	which appear in the abstract into images"""

	def __init__(self,
			mainWin,
			text,
			fontsize=pbConfig.params["bibListFontSize"],
			abstractTitle="<b>Abstract:</b><br/>",
			customEditor=None,
			statusMessages=True):
		"""Prepare the settings and the given text

		Parameters:
			mainWin: the main window object
			text: the text to be processed
			fontsize: the size of the font used to write the text
				(default: taken from the configuration parameters)
			abstractTitle: a title which will be written before
				the processed abstract
				(default: "<b>Abstract:</b><br/>")
			customEditor: the place where to save the text
				(default: `mainWin.bottomCenter.text`)
			statusMessages: if True (default), write messages
				in the statusbar
		"""
		self.fontsize = fontsize
		self.mainWin = mainWin
		self.statusMessages = statusMessages
		self.editor = self.mainWin.bottomCenter.text \
			if customEditor is None else customEditor
		self.document = QTextDocument()
		self.editor.setDocument(self.document)
		self.abstractTitle = abstractTitle
		text = str(text)
		self.text = abstractTitle + texToHtml(text).replace("\n", " ")

	def hasLatex(self):
		"""Return a boolean which indicates if there is math
		in the abstract, based on the presence of "$" in the text

		Output:
			a boolean
		"""
		return "$" in self.text

	def doText(self):
		"""Convert the text using the `thread_processLatex` thread
		to perform the conversion without freezing the main process
		"""
		if self.hasLatex():
			self.mainWin.statusBarMessage("Parsing LaTeX...")
			self.editor.setHtml(
				"%sProcessing LaTeX formulas..."%self.abstractTitle)
			self.thr = thread_processLatex(self.prepareText, self.mainWin)
			self.thr.passData.connect(self.submitText)
			self.thr.start()
		else:
			self.editor.setHtml(self.text)

	def mathTex_to_QPixmap(self, mathTex):
		"""Create a `matplotlib` figure with the equation
		that is given as a parameter

		Parameter:
			mathTex: the text to be converted into an image

		Output:
			a `QImage`
		"""
		fig = matplotlib.figure.Figure()
		fig.patch.set_facecolor('none')
		fig.set_canvas(FigureCanvasAgg(fig))
		renderer = fig.canvas.get_renderer()

		ax = fig.add_axes([0, 0, 1, 1])
		ax.axis('off')
		ax.patch.set_facecolor('none')
		t = ax.text(0, 0, mathTex,
			ha='left', va='bottom', fontsize=self.fontsize)

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
		qimage = QImage.rgbSwapped(
			QImage(buf, size[0], size[1], QImage.Format_ARGB32))
		return qimage

	def prepareText(self):
		"""Split the text into regular text and formulas
		and prepare the the images which will be inserted
		in the `QTextEdit` instead of the formulas
		"""
		matchFormula = re.compile('\$.*?\$', re.MULTILINE)
		mathTexts = [ q.group() for q in matchFormula.finditer(self.text) ]

		images = []
		text = self.text
		for i, t in enumerate(mathTexts):
			images.append(self.mathTex_to_QPixmap(t))
			text = text.replace(t, "<img src=\"mydata://image%d.png\" />"%i)
		return images, text

	def submitText(self, imgs, text):
		"""Prepare the `QTextDocument` with all the processed images
		and insert them in the `QTextEdit`
		"""
		for i, image in enumerate(imgs):
			self.document.addResource(QTextDocument.ImageResource,
				QUrl("mydata://image%d.png"%i), image)
		self.editor.setHtml(text)
		if self.statusMessages:
			self.mainWin.statusBarMessage("Latex processing done!")


class BibtexInfo(QFrame):
	"""`QFrame` extension to create a panel where to write
	some info about the selected bibtex entry"""

	def __init__(self, parent=None):
		"""Extension of `QFrame.__init__`, also adds a layout
		and a QTextEdit to the frame

		Parameter:
			parent: the parent widget
		"""
		super(BibtexInfo, self).__init__(parent)

		self.currLayout = QHBoxLayout()
		self.setLayout(self.currLayout)

		self.text = QTextEdit("")
		font = QFont()
		font.setPointSize(pbConfig.params["bibListFontSize"])
		self.text.setFont(font)
		self.text.setReadOnly(True)

		self.currLayout.addWidget(self.text)


class MyBibTableModel(MyTableModel):
	"""The model (based on `MyTableModel`)
	which manages the list of bibtex entries
	"""

	def __init__(self,
			parent,
			bib_list,
			header,
			stdCols=[],
			addCols=[],
			askBibs=False,
			previous=[],
			mainWin=None,
			*args):
		"""Constructor of the model, defines some properties
		and uses `MyTableModel.__init__`

		Parameters:
			parent: the parent widget
			bib_list: the list of bibtex entries in the model
			header: the names of the columns to be used
			stdCols (default []): the list of standard columns
				(the ones that are also fields in the database table)
			addCols (default []): the list of non-standard columns
				(the ones that are not fields in the database table,
				as "Type" or "PDF")
			askBibs: if True (default False),
				enable the checkboxes for selection
			previous (default []): the list of initially selected items
			mainWin: None (default) or a MainWindow instance
		"""
		self.mainWin = mainWin
		self.latexToText = LatexNodes2Text(
			keep_inline_math=False, keep_comments=False)
		self.typeClass = "Bibs"
		self.dataList = bib_list
		MyTableModel.__init__(self,
			parent, header + ["bibtex"], askBibs, previous, *args)
		self.stdCols = stdCols
		self.addCols = addCols + ["bibtex"]
		self.lenStdCols = len(stdCols)
		self.prepareSelected()

	def getIdentifier(self, element):
		"""Get the bibkey that uniquely identifies an element

		Parameter:
			element: the database record of the bibtex entry

		Output:
			the bibtex key
		"""
		return element["bibkey"]

	def addTypeCell(self, data):
		"""Create cell for describing the type of an entry

		Parameter:
			data: the database record of the entry

		Output:
			a string with the list of types
		"""
		someType = False
		string = ""
		for t in sorted(convertType.keys()):
			try:
				if data[t] == 1:
					if someType:
						string += ", "
					string += convertType[t]
					someType = True
			except KeyError:
				pBLogger.debug("Key not present: '%s'\nin %s"%(
					t, sorted(data.keys())))
		return string

	def addPDFCell(self, key):
		"""Create cell for the PDF file

		Parameter:
			key: the database key of the entry

		Output:
			a tuple, containing:
				True and an image
				or
				False and the string "no PDF"
		"""
		if len(pBPDF.getExisting(key))>0:
			return True, self.addImage(
				":/images/application-pdf.png",
				self.parentObj.tablewidget.rowHeight(0)*0.9)
		else:
			return False, "no PDF"

	def addMarksCell(self, marks):
		"""Create a cell for the marks

		Parameter:
			marks: the marks of the given entry

		Output:
			a tuple, containing:
				True and an image or a list of images
				or
				False and ""
		"""
		if marks is not None and (
				isinstance(marks, str) or isinstance(marks, unicode)):
			marks = [ k for k in pBMarks.marks.keys() if k in marks ]
			if len(marks)>1:
				return True, self.addImages(
					[pBMarks.marks[img]["icon"] for img in marks ],
					self.parentObj.tablewidget.rowHeight(0)*0.9)
			elif len(marks)>0:
				return True, self.addImage(
					pBMarks.marks[marks[0]]["icon"],
					self.parentObj.tablewidget.rowHeight(0)*0.9)
			else:
				return False, ""
		else:
			return False, ""

	def data(self, index, role):
		"""Return the cell data for the given index and role

		Parameters:
			index: the `QModelIndex` for which the data are required
			role: the desired Qt role for the data

		Output:
			None if the index or the role are not valid,
			the cell content or properties otherwise
		"""
		if not index.isValid():
			return None
		hasImg = False
		row = index.row()
		column = index.column()
		try:
			rowData = self.dataList[row]
		except IndexError:
			pBGUILogger.exception("MyBibTableModel.data(): invalid index")
			return None
		if "marks" in self.stdCols \
				and column == self.stdCols.index("marks"):
			hasImg, value = self.addMarksCell(rowData["marks"])
		elif column < self.lenStdCols:
			try:
				value = rowData[self.stdCols[column]]
				if self.stdCols[column] in ["title", "author"]:
					value = self.latexToText.latex_to_text(value)
			except KeyError:
				value = ""
		else:
			if self.addCols[column - self.lenStdCols] == "Type":
				value = self.addTypeCell(rowData)
			elif self.addCols[column - self.lenStdCols] == "PDF":
				hasImg, value = self.addPDFCell(rowData["bibkey"])
			else:
				value = rowData["bibtex"]

		if role == Qt.CheckStateRole and self.ask and column == 0:
			if self.selectedElements[rowData["bibkey"]] == True:
				return Qt.Checked
			else:
				return Qt.Unchecked
		if role == Qt.EditRole:
			return value
		if role == Qt.DecorationRole and hasImg:
			return value
		if role == Qt.DisplayRole and not hasImg:
			return value
		return None

	def setData(self, index, value, role):
		"""Set the cell data for the given index and role

		Parameters:
			index: the `QModelIndex` for which the data are required
			value: the new data value
			role: the desired Qt role for the data

		Output:
			True if correctly completed,
			False if the `index` is not valid
		"""
		if not index.isValid():
			return False
		if role == Qt.CheckStateRole and index.column() == 0:
			if value == Qt.Checked:
				self.selectedElements[
					self.dataList[index.row()]["bibkey"]] = True
			else:
				self.selectedElements[
					self.dataList[index.row()]["bibkey"]] = False

		self.dataChanged.emit(index, index)
		return True


class CommonBibActions():
	"""Class that contains actions and menu functions
	in use inside of other bibWindows classes
	"""

	def __init__(self, bibs, parent=None):
		"""Set basic properties

		Parameter:
			bibs: the list of bibtex entries to be managed
			parent (default None): the parent widget
		"""
		self.bibs = bibs
		self.keys = [e["bibkey"] for e in bibs]
		self.parentObj = parent

	def parent(self):
		"""Return the parent widget"""
		return self.parentObj

	def _createMenuArxiv(self, selection, arxiv):
		"""Create part of the right click menu,
		concerning the arXiv-related functions

		Parameters:
			selection: if the menu is for a multiple entries selection
				or for a right-click event on a single entry
			arxiv: the arxiv number of the bibtex record
		"""
		if selection or (
				not selection and (arxiv != "" and arxiv is not None)):
			menuA = []
			menuA.append(
				QAction("Load abstract", self.menu, triggered=self.onAbs))
			menuA.append(
				QAction("Get more fields", self.menu, triggered=self.onArx))
			self.menu.possibleActions.append(["arXiv", menuA])

	def _createMenuCopy(self, selection, initialRecord):
		"""Create part of the right click menu,
		concerning the copy to clipboard functions

		Parameters:
			selection: if the menu is for a multiple entries selection
				or for a right-click event on a single entry
			initialRecord: the bibtex record to be used
		"""
		menuC = [
			QAction("key(s)", self.menu, triggered=self.onCopyKeys),
			QAction("\cite{key(s)}", self.menu, triggered=self.onCopyCites),
			QAction("bibtex(s)", self.menu, triggered=self.onCopyBibtexs)
			]
		if not selection:
			abstract = initialRecord["abstract"]
			link = initialRecord["link"]
			if abstract is not None and abstract.strip() != "":
				menuC.append(
					QAction("abstract", self.menu,
						triggered=lambda t=abstract: copyToClipboard(t)))
			if link is not None and link.strip() != "":
				menuC.append(
					QAction("link", self.menu,
						triggered=lambda t=link: copyToClipboard(t)))
		self.menu.possibleActions.append(["Copy to clipboard", menuC])

	def _createMenuInspire(self, selection, inspireID):
		"""Create part of the right click menu,
		concerning the INSPIRE-HEP-related functions

		Parameters:
			selection: if the menu is for a multiple entries selection
				or for a right-click event on a single entry
			inspireID: the inspire ID of the bibtex record
		"""
		menuI = []
		menuI.append(
			QAction("Complete info (ID and auxiliary info)", self.menu,
			triggered=self.onComplete))
		if selection or (
				not selection and (inspireID != "" and inspireID is not None)):
			menuI.append(
				QAction("Update bibtex", self.menu,
				triggered=lambda r=True: self.onUpdate(force=r)))
			menuI.append(
				QAction("Reload bibtex", self.menu,
				triggered=lambda f=(not selection), r=True:
					self.onUpdate(force=f, reloadAll=r)))
			menuI.append(
				QAction("Citation statistics", self.menu,
				triggered=self.onCitations))
		self.menu.possibleActions.append(["INSPIRE-HEP", menuI])

	def _createMenuLinks(self, bibkey, arxiv, doi, inspireID):
		"""Create part of the right click menu,
		concerning the links-related functions

		Parameters:
			bibkey: the key of the bibtex record
			arxiv: the arXiv ID of the bibtex record
			doi: the DOI of the bibtex record
			inspireID: the inspire ID of the bibtex record
		"""
		menuL = []
		if arxiv is not None and arxiv != "":
			menuL.append(QAction("Open into arXiv", self.menu,
				triggered=lambda l=bibkey, t="arxiv":
					pBGuiView.openLink(l, t)))
		if doi is not None and doi != "":
			menuL.append(QAction("Open DOI link", self.menu,
				triggered=lambda l=bibkey, t="doi":
					pBGuiView.openLink(l, t)))
		if inspireID is not None and inspireID != "":
			menuL.append(QAction("Open into INSPIRE-HEP", self.menu,
				triggered=lambda l=bibkey, t="inspire":
					pBGuiView.openLink(l, t)))
		if len(menuL) > 0:
			self.menu.possibleActions.append(["Links", menuL])

	def _createMenuMarkType(self, initialRecord):
		"""Create part of the right click menu,
		concerning marks and types

		Parameter:
			initialRecord: the bibtex record to be used
		"""
		menuM = []
		for m in sorted(pBMarks.marks.keys()):
			if m in initialRecord["marks"]:
				menuM.append(QAction(
					"Unmark as '%s'"%pBMarks.marks[m]["desc"], self.menu,
					triggered=lambda m=m: self.onUpdateMark(m)))
			else:
				menuM.append(QAction(
					"Mark as '%s'"%pBMarks.marks[m]["desc"], self.menu,
					triggered=lambda m=m: self.onUpdateMark(m)))
		menuT = []
		for k, v in sorted(convertType.items()):
			if initialRecord[k]:
				menuT.append(QAction(
					"Unset '%s'"%v, self.menu,
					triggered=lambda t=k: self.onUpdateType(t)))
			else:
				menuT.append(QAction(
					"Set '%s'"%v, self.menu,
					triggered=lambda t=k: self.onUpdateType(t)))
		self.menu.possibleActions.append(["Marks", menuM])
		self.menu.possibleActions.append(["Type", menuT])
		self.menu.possibleActions.append(None)

	def _createMenuPDF(self, selection, initialRecord):
		"""Create part of the right click menu,
		concerning the PDF functions

		Parameters:
			selection: if the menu is for a multiple entries selection
				or for a right-click event on a single entry
			initialRecord: the bibtex record to be used
		"""
		if not selection:
			bibkey = initialRecord["bibkey"]
			arxiv = initialRecord["arxiv"]
			doi = initialRecord["doi"]
			menuP = []
			files = pBPDF.getExisting(bibkey, fullPath=True)
			arxivFile = pBPDF.getFilePath(bibkey, "arxiv")
			doiFile = pBPDF.getFilePath(bibkey, "doi")
			pdfDir = pBPDF.getFileDir(bibkey)
			menuP.append(
				QAction("Add generic PDF", self.menu,
					triggered=self.onAddPDF))
			if (len(files) > 0 and arxivFile in files) \
					or (arxiv is not None and arxiv != ""):
				menuP.append(None)
			if arxivFile in files:
				files.remove(arxivFile)
				menuP.append(QAction("Open arXiv PDF", self.menu,
					triggered=lambda k=bibkey, t="file", f=arxivFile:
						pBGuiView.openLink(k, t, fileArg = f)))
				menuP.append(QAction("Delete arXiv PDF", self.menu,
					triggered=lambda k=bibkey, a="arxiv", t="arxiv PDF":
						self.onDeletePDFFile(k, a, t)))
				menuP.append(QAction("Copy arXiv PDF", self.menu,
					triggered=lambda k=bibkey, a="arxiv":
						self.onCopyPDFFile(k, a)))
			elif arxiv is not None and arxiv != "":
				menuP.append(
					QAction("Download arXiv PDF", self.menu,
						triggered=self.onDown))
			if (len(files) > 0 and doiFile in files) \
					or (doi is not None and doi != ""):
				menuP.append(None)
			if doiFile in files:
				files.remove(doiFile)
				menuP.append(QAction("Open DOI PDF", self.menu,
					triggered=lambda k=bibkey, t="file", f=doiFile:
						pBGuiView.openLink(k, t, fileArg = f)))
				menuP.append(QAction("Delete DOI PDF", self.menu,
					triggered=lambda k=bibkey, a="doi", t="DOI PDF":
						self.onDeletePDFFile(k, a, t)))
				menuP.append(QAction("Copy DOI PDF", self.menu,
					triggered=lambda k=bibkey, a="doi":
						self.onCopyPDFFile(k, a)))
			elif doi is not None and doi != "":
				menuP.append(
					QAction("Assign DOI PDF", self.menu,
						triggered=lambda g="doi": self.onAddPDF(g)))
			if len(files) > 0:
				menuP.append(None)
			for i,f in enumerate(files):
				fn = f.replace(pdfDir+"/", "")
				menuP.append(QAction("Open %s"%fn, self.menu,
					triggered=lambda k=bibkey, t="file", f=fn:
						pBGuiView.openLink(k, t, fileArg = f)))
				menuP.append(QAction("Delete %s"%fn, self.menu,
					triggered=lambda k=bibkey, a=fn, t=f:
						self.onDeletePDFFile(k, a, a, t)))
				menuP.append(QAction("Copy %s"%fn, self.menu,
					triggered=lambda k=bibkey, a=fn, t=f:
						self.onCopyPDFFile(k, a, t)))
			self.menu.possibleActions.append(["PDF", menuP])
		else:
			self.menu.possibleActions.append(
				QAction("Download PDF from arXiv", self.menu,
				triggered=self.onDown))

	def createContextMenu(self, selection=False):
		"""Create a context menu event, for one or multiple entries

		Parameter:
			selection (default False): if True, the menu is for
				a selection of entries. If False, for a single entry
		"""
		menu = MyMenu(self.parent())
		self.menu = menu
		if len(self.keys) == 0 or len(self.bibs) == 0:
			return
		if not selection and (len(self.keys) > 1 or len(self.bibs) > 1):
			selection = True

		if not selection:
			self.bibs = [self.bibs[0]]
			self.keys = [self.keys[0]]
			initialRecord = self.bibs[0]
			bibkey = initialRecord["bibkey"]
			if initialRecord["marks"] is None:
				initialRecord["marks"] = ""
				pBDB.bibs.updateField(bibkey, "marks", "")
			arxiv = initialRecord["arxiv"]
			bibtex = initialRecord["bibtex"]
			doi = initialRecord["doi"]
			inspireID = initialRecord["inspire"]

			titAct = QAction("--Entry: %s--"%bibkey, menu)
			titAct.setDisabled(True)
			menu.possibleActions.append(titAct)
			menu.possibleActions.append(None)
			menu.possibleActions.append(
				QAction("Modify", menu, triggered=self.onModify))
		else:
			initialRecord = None
			arxiv = None
			inspireID = None
			if len(self.keys) == 2:
				menu.possibleActions.append(
					QAction("Merge", menu, triggered=self.onMerge))

		menu.possibleActions.append(
			QAction("Clean", menu, triggered=self.onClean))
		menu.possibleActions.append(
			QAction("Delete", menu, triggered=self.onDelete))
		menu.possibleActions.append(None)

		if not selection:
			self._createMenuMarkType(initialRecord)

		menuC = self._createMenuCopy(selection, initialRecord)

		self._createMenuPDF(selection, initialRecord)
		if not selection:
			self._createMenuLinks(bibkey, arxiv, doi, inspireID)
		menu.possibleActions.append(None)

		menu.possibleActions.append(
			QAction("Select categories", menu, triggered=self.onCat))
		menu.possibleActions.append(
			QAction("Select experiments", menu, triggered=self.onExp))
		menu.possibleActions.append(None)

		self._createMenuInspire(selection, inspireID)
		self._createMenuArxiv(selection, arxiv)
		menu.possibleActions.append(None)

		menu.possibleActions.append(
			QAction("Export entries in a .bib file", menu,
			triggered=self.onExport))
		menu.possibleActions.append(
			QAction("Copy all the (existing) PDF", menu,
			triggered=self.onCopyAllPDF))

		menu.fillMenu()
		return menu

	def onAddPDF(self, ftype="generic"):
		"""Ask and copy in the proper folder a new PDF

		Parameter:
			ftype (default "generic"): if "generic", add a generic PDF
				and keep its initial name.
				Otherwise, it may be e.g. "doi"
				(see `pdf.LocalPDF.copyNewFile:fileType`)
		"""
		bibkey = self.keys[0]
		newPdf = askFileName(self.parent(),
			"Where is the PDF located?", filter = "PDF (*.pdf)")
		if newPdf != "" and os.path.isfile(newPdf):
			if ftype == "generic":
				newName = newPdf.split("/")[-1]
				outcome = pBPDF.copyNewFile(bibkey, newPdf,
					customName = newName)
			else:
				outcome = pBPDF.copyNewFile(bibkey, newPdf, ftype)
			if outcome:
				infoMessage("PDF successfully copied!")
			else:
				pBGUILogger.error("Could not copy the new file!")

	def onAbs(self, message=True):
		"""Action performed when the download of
		the abstract is required

		Parameter:
			message (default True): if False, suppress some infoMessages
		"""
		self.parent().statusBarMessage(
			"Starting the abstract download process, please wait...")
		for e in self.bibs:
			arxiv = e["arxiv"]
			bibkey = e["bibkey"]
			if arxiv:
				bibtex, full = physBiblioWeb.webSearch["arxiv"].retrieveUrlAll(
					arxiv, searchType="id", fullDict=True)
				abstract = full["abstract"]
				pBDB.bibs.updateField(bibkey, "abstract", abstract)
				if message:
					infoMessage(abstract, title="Abstract of arxiv:%s"%arxiv)
			else:
				infoMessage("No arxiv number for entry '%s'!"%bibkey)
		self.parent().done()

	def onArx(self):
		"""Action to be performed when asking arXiv info.
		Call `gui.mainWindow.MainWindow.infoFromArxiv`
		"""
		self.parent().infoFromArxiv(self.bibs)

	def onCat(self, testing=False):
		"""Open a `catsTreeWindow` to ask the changes to the categories,
		then perform the database changes

		Parameter:
			testing (default False):
				if evaluates to True it must be
				a `catsTreeWindow` instance,
				the provided dialog will be used
				instead of running `exec_`
		"""
		previousAll = [e["idCat"] for e in pBDB.cats.getByEntries(self.keys)]
		if len(self.keys) == 1:
			bibkey = self.keys[0]
			selectCats = catsTreeWindow(parent=self.parent(),
				askCats=True,
				askForBib=bibkey,
				expButton=False,
				previous=previousAll)
		else:
			selectCats = catsTreeWindow(parent=self.parent(),
				askCats=True,
				expButton=False,
				previous=previousAll,
				multipleRecords=True)
		if testing:
			selectCats = testing
		else:
			selectCats.exec_()
		if selectCats.result == "Ok":
			if len(self.keys) == 1:
				cats = self.parent().selectedCats
				for p in previousAll:
					if p not in cats:
						pBDB.catBib.delete(p, bibkey)
				for c in cats:
					if c not in previousAll:
						pBDB.catBib.insert(c, bibkey)
				self.parent().statusBarMessage(
					"Categories for '%s' successfully inserted"%bibkey)
			else:
				prevAll = list(previousAll)
				for c in self.parent().previousUnchanged:
					if c in prevAll:
						del prevAll[prevAll.index(c)]
				for c in prevAll:
					if c not in self.parent().selectedCats:
						pBDB.catBib.delete(c, self.keys)
				pBDB.catBib.insert(self.parent().selectedCats, self.keys)
				self.parent().statusBarMessage(
					"Categories successfully inserted")

	def onCitations(self):
		"""Call `inspireStats.inspireStatsLoader.plotStats`
		to obtain the citation info of one or more papers
		"""
		self.parent().getInspireStats([e["inspire"] for e in self.bibs])

	def onClean(self):
		"""Action to be performed when cleaning bibtexs.
		Call `gui.mainWindow.MainWindow.cleanAllBibtexs`
		"""
		self.parent().cleanAllBibtexs(useEntries=self.bibs)

	def onComplete(self):
		"""Action to be performed when updating info from INSPIRE-HEP.
		Call `gui.mainWindow.MainWindow.updateInspireInfo`
		"""
		bibkey = self.bibs[0]["bibkey"]
		inspireID = self.bibs[0]["inspire"]
		self.parent().updateInspireInfo(bibkey, inspireID=inspireID)

	def onCopyBibtexs(self):
		"""Copy all the bibtexs to the keyboard"""
		copyToClipboard("\n\n".join([e["bibtex"] for e in self.bibs]))

	def onCopyCites(self):
		"""Copy '\cite{all the keys}' to the keyboard"""
		copyToClipboard("\cite{%s}"%",".join(
			[e["bibkey"] for e in self.bibs]))

	def onCopyKeys(self):
		"""Copy all the keys to the keyboard"""
		copyToClipboard(",".join([e["bibkey"] for e in self.bibs]))

	def onCopyPDFFile(self, bibkey, fileType, custom=None):
		"""Ask where and eventually copy a PDF file

		Parameters:
			bibkey: the key of the involved entry
			fileType: the file type or the filename of the custom PDF
			custom (default None): the full path of the custom PDF
		"""
		pdfName = os.path.join(pBPDF.getFileDir(bibkey), custom) \
			if custom is not None else pBPDF.getFilePath(bibkey, fileType)
		outFolder = askDirName(self.parent(),
			title="Where do you want to save the PDF %s?"%pdfName)
		if outFolder.strip() != "":
			pBPDF.copyToDir(outFolder, bibkey,
				fileType=fileType, customName=custom)

	def onCopyAllPDF(self):
		"""Ask the destination and copy there all the PDF files
		for the given entries
		"""
		outFolder = askDirName(self.parent(),
			title="Where do you want to save the PDF files?")
		if outFolder.strip() != "":
			for entry in self.bibs:
				key = entry["bibkey"]
				if pBPDF.checkFile(key, "doi"):
					pBPDF.copyToDir(outFolder, key, fileType="doi")
				elif pBPDF.checkFile(key, "arxiv"):
					pBPDF.copyToDir(outFolder, key, fileType="arxiv")
				else:
					existing = pBPDF.getExisting(key)
					if len(existing) > 0:
						for ex in existing:
							pBPDF.copyToDir(outFolder,
								key, "", customName=ex)

	def onDelete(self):
		"""Call `deleteBibtex` on all the entries"""
		deleteBibtex(self.parent(), self.keys)

	def onDeletePDFFile(self, bibkey, fileType, fdesc, custom=None):
		"""Ask and eventually delete a PDF file

		Parameters:
			bibkey: the key of the involved entry
			fileType: the file type or the filename of the custom PDF
			fdesc: a short description of the file type
			custom (default None): the full path of the custom PDF
		"""
		if askYesNo(
				"Do you really want to delete the %s file for entry %s?"%(
					fdesc, bibkey)):
			self.parent().statusBarMessage("deleting %s file..."%fdesc)
			if custom is not None:
				pBPDF.removeFile(bibkey, "", fileName=custom)
			else:
				pBPDF.removeFile(bibkey, fileType)
			self.parent().reloadMainContent(
				pBDB.bibs.fetchFromLast().lastFetched)

	def onDown(self):
		"""Download the arXiv PDF for each given entry"""
		self.downArxiv_thr = []
		for entry in self.bibs:
			if entry["arxiv"] is not None and entry["arxiv"] != "":
				self.parent().statusBarMessage(
					"downloading PDF for arxiv:%s..."%entry["arxiv"])
				self.downArxiv_thr.append(
					thread_downloadArxiv(entry["bibkey"], self.parent()))
				self.downArxiv_thr[-1].finished.connect(
					lambda a=entry["arxiv"]: self.onDownloadArxivDone(a))
				self.downArxiv_thr[-1].start()

	def onDownloadArxivDone(self, e):
		"""Send a message at the end of the arXiv PDF download

		Parameter:
			e: the arXiv identifier of the entry
		"""
		self.parent().sendMessage(
			"Download of PDF for arXiv:%s completed! "%e
			+ "Please check that it worked...")
		self.parent().done()
		self.parent().reloadMainContent(pBDB.bibs.fetchFromLast().lastFetched)

	def onExp(self, testing=False):
		"""Open a `ExpsListWindow` window to obtain the list of
		experiments to be added (also deleted, if for a single entry)
		and perform the database changes

		Parameter:
			testing (default False):
				if evaluates to True it must be
				a `ExpsListWindow` instance,
				the provided dialog will be used
				instead of running `exec_`
		"""
		if len(self.keys) == 1:
			bibkey = self.keys[0]
			previous = [a["idExp"] for a in pBDB.exps.getByEntry(bibkey)]
			selectExps = ExpsListWindow(parent=self.parent(),
				askExps=True,
				askForBib=bibkey,
				previous=previous)
			if testing:
				selectExps = testing
			else:
				selectExps.exec_()
			if selectExps.result == "Ok":
				exps = self.parent().selectedExps
				for p in previous:
					if p not in exps:
						pBDB.bibExp.delete(bibkey, p)
				for e in exps:
					if e not in previous:
						pBDB.bibExp.insert(bibkey, e)
				self.parent().statusBarMessage(
					"Experiments for '%s' successfully inserted"%bibkey)
		else:
			infoMessage("Warning: you can just add experiments "
				+ "to the selected entries, not delete!")
			selectExps = ExpsListWindow(parent=self.parent(),
				askExps=True, previous=[])
			if testing:
				selectExps = testing
			else:
				selectExps.exec_()
			if selectExps.result == "Ok":
				pBDB.bibExp.insert(self.keys, self.parent().selectedExps)
				self.parent().statusBarMessage(
					"Experiments successfully inserted")

	def onExport(self):
		"""Action to be performed when exporting bibtexs.
		Call `gui.mainWindow.MainWindow.exportSelection`
		"""
		self.parent().exportSelection(self.bibs)

	def onMerge(self, testing=False):
		"""Open a `MergeBibtexs` window to configure the merging,
		then perform the requested changes, merge the entries and
		delete the previous ones

		Parameter:
			testing (default False):
				if evaluates to True it must be
				a `MergeBibtexs` instance,
				the provided dialog will be used
				instead of running `exec_`
		"""
		mergewin = MergeBibtexs(
			self.bibs[0], self.bibs[1], self.parent())
		if testing:
			mergewin = testing
		else:
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
				data["old_keys"] = ", ".join(
					[data["old_keys"],
					self.entries[0]["bibkey"],
					self.entries[1]["bibkey"]])
			else:
				data["old_keys"] = ", ".join(
					[self.entries[0]["bibkey"],
					self.entries[1]["bibkey"]])
			data = pBDB.bibs.prepareInsert(**data)
			if data["bibkey"].strip() != "" and data["bibtex"].strip() != "":
				pBDB.commit()
				try:
					for key in [self.entries[0]["bibkey"],
							self.entries[1]["bibkey"]]:
						pBDB.bibs.delete(key)
				except:
					pBGUILogger.exception("Cannot delete old items!")
					pBDB.undo()
				else:
					if not pBDB.bibs.insert(data):
						pBGUILogger.error("Cannot insert new item!")
						pBDB.undo()
					else:
						self.parent().setWindowTitle("PhysBiblio*")
						try:
							self.parent().reloadMainContent(
								pBDB.bibs.fetchFromLast().lastFetched)
						except:
							pBLogger.warning("Impossible to reload content.")
			else:
				pBGUILogger.error("Empty bibtex and/or bibkey!")

	def onModify(self):
		"""Action to be performed when modifying bibtexs.
		Call `editBibtex`
		"""
		editBibtex(self.parent(), self.bibs[0]["bibkey"])

	def onUpdate(self, force=False, reloadAll=False):
		"""Action to be performed when updating bibtexs.
		Call `gui.mainWindow.MainWindow.updateAllBibtexs`

		Parameters:
			force (default False): if True, force update also when
				bibliographic information is already present
			reloadAll (default False): if True,
				completely reload the bibtexs
				instead of updating them
		"""
		self.parent().updateAllBibtexs(startFrom=0,
			useEntries=self.bibs,
			force=force,
			reloadAll=reloadAll)

	def onUpdateMark(self, mark):
		"""Update (set or unset) 'mark' for the given entries and
		reload the main table content

		Parameter:
			mark: one of the allowed marks
		"""
		if mark not in pBMarks.marks.keys():
			pBLogger.warning("Invalid mark: '%s'"%mark)
			return
		for e in self.bibs:
			marks = e["marks"].split(",")
			marks = [m for m in marks if m.strip() != ""]
			if mark in marks:
				marks.remove(mark)
			else:
				marks.append(mark)
			marks = sorted(marks)
			pBDB.bibs.updateField(e["bibkey"], "marks", ",".join(marks),
				verbose=0)
		self.parent().reloadMainContent(
			pBDB.bibs.fetchFromLast().lastFetched)

	def onUpdateType(self, type_):
		"""Toggle the field 'type_' for the given entries and
		reload the main table content

		Parameter:
			type_: one among "review", "proceeding", "book",
				"phd_thesis", "lecture", "exp_paper"
		"""
		if type_ not in convertType.keys():
			pBLogger.warning("Invalid type: '%s'"%type_)
			return
		for e in self.bibs:
			pBDB.bibs.updateField(
				e["bibkey"], type_, 0 if e[type_] else 1, verbose=0)
		self.parent().reloadMainContent(
			pBDB.bibs.fetchFromLast().lastFetched)


class BibtexListWindow(QFrame, objListWindow):
	"""W"""

	def __init__(self,
			parent = None,
			bibs = None,
			askBibs = False,
			previous = []):
		#table dimensions
		self.columns = pbConfig.params["bibtexListColumns"]
		self.colcnt = len(self.columns)
		self.colContents = []
		self.previous = previous
		self.askBibs = askBibs
		self.additionalCols = ["Type", "PDF"]
		for j in range(self.colcnt):
			self.colContents.append(self.columns[j])
		self.colContents += [a.lower() for a in self.additionalCols]
		self.currentAbstractKey = None

		QFrame.__init__(self, parent)
		objListWindow.__init__(self, parent)
		self.mainWin = parent

		self.createActions()

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
		status = self.tableModel.ask
		self.clearAct.setEnabled(status)
		self.selAllAct.setEnabled(status)
		self.unselAllAct.setEnabled(status)
		self.okAct.setEnabled(status)

	def clearSelection(self):
		self.tableModel.previous = []
		self.tableModel.prepareSelected()
		self.tableModel.changeAsk(False)
		self.changeEnableActions()

	def createActions(self):
		self.selAct = QAction(QIcon(":/images/edit-node.png"),
			"&Select entries", self,
			statusTip="Select entries from the list",
			triggered=self.enableSelection)
		self.okAct = QAction(QIcon(":/images/dialog-ok-apply.png"),
			"Selection &completed", self,
			statusTip="Selection of elements completed",
			triggered=self.onOk)
		self.clearAct = QAction(QIcon(":/images/edit-clear.png"),
			"&Clear selection", self,
			statusTip="Discard the current selection and hide checkboxes",
			triggered=self.clearSelection)
		self.selAllAct = QAction(QIcon(":/images/edit-select-all.png"),
			"&Select all", self,
			statusTip="Select all the elements",
			triggered=self.selectAll)
		self.unselAllAct = QAction(QIcon(":/images/edit-unselect-all.png"),
			"&Unselect all", self,
			statusTip="Unselect all the elements",
			triggered=self.unselectAll)

	def enableSelection(self):
		self.tableModel.changeAsk()
		self.changeEnableActions()

	def selectAll(self):
		self.tableModel.selectAll()

	def unselectAll(self):
		self.tableModel.unselectAll()

	def onOk(self):
		position = QCursor.pos()
		self.mainWin.selectedBibs = [ \
			key for key in self.tableModel.selectedElements.keys() \
			if self.tableModel.selectedElements[key] == True]
		commonActions = CommonBibActions(
			[pBDB.bibs.getByKey(k)[0] for k in self.mainWin.selectedBibs],
			self.mainWin)
		ask = commonActions.createContextMenu(selection=True)
		ask.exec_(position)
		self.clearSelection()

	def createTable(self):
		if self.bibs is None:
			self.bibs = pBDB.bibs.getAll(orderType = "DESC",
				limitTo = pbConfig.params["defaultLimitBibtexs"])
		rowcnt = len(self.bibs)

		commentStr = "Last query to bibtex database: \t%s\t\t"%(
			pBDB.bibs.lastQuery)
		if len(pBDB.bibs.lastVals)>0 :
			commentStr += " - arguments:\t%s"%(pBDB.bibs.lastVals,)
		self.currLayout.addWidget(MyLabel(commentStr))

		self.selectToolBar = QToolBar('Bibs toolbar')
		self.selectToolBar.addAction(self.selAct)
		self.selectToolBar.addAction(self.clearAct)
		self.selectToolBar.addSeparator()
		self.selectToolBar.addAction(self.selAllAct)
		self.selectToolBar.addAction(self.unselAllAct)
		self.selectToolBar.addAction(self.okAct)
		self.selectToolBar.addWidget(MyLabel(
			"(Select exactly two entries to enable merging them)"))
		self.selectToolBar.addSeparator()

		self.filterInput = QLineEdit("",  self)
		self.filterInput.setPlaceholderText("Filter bibliography")
		self.filterInput.textChanged.connect(self.changeFilter)
		self.selectToolBar.addWidget(self.filterInput)
		self.filterInput.setFocus()

		self.currLayout.addWidget(self.selectToolBar)

		self.tableModel = MyBibTableModel(self,
			self.bibs,
			self.columns + self.additionalCols,
			self.columns,
			self.additionalCols,
			askBibs=self.askBibs,
			mainWin=self.mainWin,
			previous=self.previous)

		self.changeEnableActions()
		self.setProxyStuff(self.columns.index("firstdate"), Qt.DescendingOrder)
		self.tablewidget.hideColumn(
			len(self.columns) + len(self.additionalCols))

		self.finalizeTable()

	def updateInfo(self, entry):
		self.mainWin.bottomLeft.text.setText(entry["bibtex"])
		self.mainWin.bottomRight.text.setText(writeBibtexInfo(entry))
		if self.currentAbstractKey != entry["bibkey"]:
			self.currentAbstractKey = entry["bibkey"]
			writeAbstract(self.mainWin, entry)

	def getEventEntry(self, index):
		"""Use index to return bibkey and entry record"""
		if not index.isValid():
			return
		row = index.row()
		col = index.column()
		try:
			bibkey = str(self.proxyModel.sibling(
				row, self.columns.index("bibkey"), index).data())
		except AttributeError:
			pBLogger.debug("Error in reading table content")
			return
		if bibkey is None or bibkey is "":
			return
		try:
			entry = pBDB.bibs.getByBibkey(bibkey, saveQuery=False)[0]
		except IndexError:
			pBGUILogger.debug("The entry cannot be found!")
			return
		return row, col, bibkey, entry

	def triggeredContextMenuEvent(self, row, col, event):
		""""""
		index = self.tablewidget.model().index(row, col)
		try:
			row, col, bibkey, entry = self.getEventEntry(index)
		except TypeError:
			pBLogger.warning("The index is not valid!")
			return

		commonActions = CommonBibActions([entry], self.mainWin)
		menu = commonActions.createContextMenu()
		menu.exec_(event.globalPos())

	def handleItemEntered(self, index):
		pass

	def cellClick(self, index):
		try:
			row, col, bibkey, entry = self.getEventEntry(index)
		except TypeError:
			pBLogger.warning("The index is not valid!")
			return
		self.updateInfo(entry)

	def cellDoubleClick(self, index):
		try:
			row, col, bibkey, entry = self.getEventEntry(index)
		except TypeError:
			pBLogger.warning("The index is not valid!")
			return
		self.updateInfo(entry)
		if self.colContents[col] == "doi" \
				and entry["doi"] is not None \
				and entry["doi"] != "":
			pBGuiView.openLink(bibkey, "doi")
		elif self.colContents[col] == "arxiv" \
				and entry["arxiv"] is not None \
				and entry["arxiv"] != "":
			pBGuiView.openLink(bibkey, "arxiv")
		elif self.colContents[col] == "inspire" \
				and entry["inspire"] is not None \
				and entry["inspire"] != "":
			pBGuiView.openLink(bibkey, "inspire")
		elif self.colContents[col] == "pdf":
			pdfFiles = pBPDF.getExisting(bibkey, fullPath = True)
			if len(pdfFiles) == 1:
				self.mainWin.statusBarMessage("opening PDF...")
				pBGuiView.openLink(bibkey, "file", fileArg = pdfFiles[0])
			elif len(pdfFiles) > 1:
				ask = AskPDFAction(bibkey, self)
				ask.exec_(QCursor.pos())
				if ask.result == "openArxiv":
					self.mainWin.statusBarMessage("opening arxiv PDF...")
					pBGuiView.openLink(bibkey, "file",
						fileArg = pBPDF.getFilePath(bibkey, "arxiv"))
				elif ask.result == "openDoi":
					self.mainWin.statusBarMessage("opening doi PDF...")
					pBGuiView.openLink(bibkey, "file",
						fileArg = pBPDF.getFilePath(bibkey, "doi"))
				elif isinstance(ask.result, str) \
						and "openOther_" in ask.result:
					filename = ask.result.replace("openOther_", "")
					self.mainWin.statusBarMessage("opening %s..."%filename)
					pBGuiView.openLink(bibkey, "file",
						fileArg = os.path.join(
							pBPDF.getFileDir(bibkey), filename))

	def finalizeTable(self):
		"""resize the table to fit the contents, connect click
		and doubleclick functions, add layout
		"""
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
		QApplication.setOverrideCursor(Qt.WaitCursor)
		if bibs is not None:
			self.bibs = bibs
		else:
			self.bibs = pBDB.bibs.getAll(orderType = "DESC",
				limitTo = pbConfig.params["defaultLimitBibtexs"])
		self.cleanLayout()
		self.createTable()
		QApplication.restoreOverrideCursor()


class EditBibtexDialog(editObjectWindow):
	"""create a window for editing or creating a bibtex entry"""

	def __init__(self, parent = None, bib = None):
		super(EditBibtexDialog, self).__init__(parent)
		self.bibtexEditLines = 8
		if bib is None:
			self.data = {}
			for k in pBDB.tableCols["entries"]:
				self.data[k] = ""
		else:
			self.data = bib
		self.checkValues = {}
		self.markValues = {}
		self.checkboxes = ["exp_paper", "lecture", "phd_thesis", "review",
			"proceeding", "book", "noUpdate"]
		self.createForm()

	def onOk(self):
		if self.textValues["bibtex"].toPlainText() == "":
			pBGUILogger.error("Invalid form contents: empty bibtex!")
			return False
		elif not self.textValues["bibkey"].isReadOnly() \
				and self.textValues["bibkey"].text() != "" \
				and self.textValues["bibtex"].toPlainText() != "":
			pBGUILogger.error(
				"Invalid form contents: bibtex key will be taken from bibtex!")
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
			if k != "bibtex" \
					and k != "marks" \
					and k != "abstract" \
					and k not in self.checkboxes:
				i += 1
				self.currGrid.addWidget(MyLabel(k),
					int((i+1-(i+i)%2)/2)*2-1, ((1+i)%2)*2)
				self.currGrid.addWidget(
					MyLabel("(%s)"%pBDB.descriptions["entries"][k]),
					int((i+1-(i+i)%2)/2)*2-1, ((1+i)%2)*2+1)
				self.textValues[k] = QLineEdit(str(val))
				if k == "bibkey" and val != "":
					self.textValues[k].setReadOnly(True)
				self.currGrid.addWidget(self.textValues[k],
					int((i+1-(i+i)%2)/2)*2, ((1+i)%2)*2, 1, 2)
			elif k == "marks":
				i += 1
				groupBox, markValues = pBMarks.getGroupbox(
					self.data["marks"],
					description = pBDB.descriptions["entries"]["marks"])
				self.markValues = markValues
				if ((1+i)%2)*2 != 0:
					i += 1
				self.currGrid.addWidget(groupBox,
					int((i+1-(i+i)%2)/2)*2, ((1+i)%2)*2, 1, 4)

		self.textValues["bibkey"].setReadOnly(True)

		#bibtex text editor
		i += 1 + i%2
		k = "bibtex"
		self.currGrid.addWidget(MyLabel(k),
			int((i+1-(i+i)%2)/2)*2-1, ((1+i)%2)*2)
		self.currGrid.addWidget(
			MyLabel("(%s)"%pBDB.descriptions["entries"][k]),
			int((i+1-(i+i)%2)/2)*2-1, ((1+i)%2)*2+1)
		self.textValues[k] = QPlainTextEdit(self.data[k])
		self.textValues["bibtex"].textChanged.connect(self.updateBibkey)
		self.currGrid.addWidget(self.textValues[k],
			int((i+1-(i+i)%2)/2)*2, 0, self.bibtexEditLines, 2)

		j = 0
		for k in pBDB.tableCols["entries"]:
			val = self.data[k]
			if k in self.checkboxes:
				j += 2
				self.currGrid.addWidget(MyLabel(k),
					int((i+1-(i+i)%2)/2)*2 + j - 2, 2)
				self.currGrid.addWidget(
					MyLabel("(%s)"%pBDB.descriptions["entries"][k]),
					int((i+1-(i+i)%2)/2)*2 + j - 1, 2, 1, 2)
				self.checkValues[k] = QCheckBox("", self)
				if val == 1:
					self.checkValues[k].toggle()
				self.currGrid.addWidget(self.checkValues[k],
					int((i+1-(i+i)%2)/2)*2 + j - 2, 3)

		self.currGrid.addWidget(self.textValues["bibtex"],
			int((i+1-(i+i)%2)/2)*2, 0, j, 2)

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


class MyPDFAction(QAction):
	"""Action used when asking which file to open"""

	def __init__(self, filename, parentMenu, *args, **kwargs):
		"""Extend `QAction.__init__` with few default properties

		Parameters:
			filename: the name of the file corresponding to this action
			parentMenu: the menu of which this action is part
			additional *args, **kwargs as in `QAction.__init__`
		"""
		QAction.__init__(self,
			*args,
			triggered = self.returnFileName,
			**kwargs)
		self.filename = filename
		self.parentMenu = parentMenu

	def returnFileName(self):
		"""Define the result of the parentMenu
		to later open the file self.filename
		"""
		self.parentMenu.result = "openOther_%s"%self.filename
		self.parentMenu.close()


class AskPDFAction(MyMenu):
	"""Menu used to ask which PDF file must be opened"""

	def __init__(self, key, parent=None):
		"""Prepare the menu, reading the list of existing PDF files
		and creating an action for each of them

		Parameters:
			key: the bibtex key of the item to consider
			parent (default None): the parent widget
		"""
		super(AskPDFAction, self).__init__(parent)
		self.message = "What PDF of this entry (%s) do you want to open?"%(key)
		self.possibleActions = []
		files = pBPDF.getExisting(key, fullPath=True)
		doiFile = pBPDF.getFilePath(key, "doi")
		arxivFile = pBPDF.getFilePath(key, "arxiv")
		if doiFile != "" and doiFile in files:
			self.possibleActions.append(
				QAction("Open DOI PDF", self, triggered = self.onOpenDoi))
			files.remove(doiFile)
		if arxivFile != "" and arxivFile in files:
			self.possibleActions.append(
				QAction("Open arxiv PDF", self, triggered = self.onOpenArxiv))
			files.remove(arxivFile)
		for f in files:
			self.possibleActions.append(
				MyPDFAction(f, self, "Open %s"%f.split(os.sep)[-1],
					parent=self))
		self.fillMenu()

	def onOpenArxiv(self):
		"""Set the result for opening the arXiv PDF"""
		self.result	= "openArxiv"
		self.close()

	def onOpenDoi(self):
		"""Set the result for opening the DOI PDF"""
		self.result	= "openDoi"
		self.close()


class SearchBibsWindow(editObjectWindow):
	"""create a window for searching a bibtex entry"""

	def __init__(self, parent = None, bib = None, replace = False):
		super(SearchBibsWindow, self).__init__(parent)
		self.textValues = []
		self.result = False
		self.save = False
		self.replace = replace
		self.historic = [self.processHistoric(a) \
			for a in pbConfig.globalDb.getSearchList(
				manual = False, replacement = replace)]
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

	def processHistoric(self, record):
		limit = record["limitNum"]
		offset = record["offsetNum"]
		replace = record["replaceFields"] if record["isReplace"] == 1 else []
		try:
			searchDict = ast.literal_eval(record["searchDict"])
		except:
			pBLogger.warning("Something went wrong when processing "
				+ "the saved search dict:\n%s"%record["searchDict"])
			searchDict = {}
		try:
			replaceFields = ast.literal_eval(replace)
		except:
			pBLogger.warning("Something went wrong when processing "
				+ "the saved search/replace:\n%s"%replace,
				exc_info=True)
			replaceFields = []
		return (searchDict, replaceFields, limit, offset)

	def cleanLayout(self):
		"""delete previous table widget"""
		while True:
			o = self.layout().takeAt(0)
			if o is None: break
			o.widget().deleteLater()

	def changeCurrentContent(self, index):
		self.cleanLayout()
		self.createForm(index)

	def onSave(self):
		self.save = True
		self.onOk()

	def onAskCats(self):
		selectCats = catsTreeWindow(parent = self,
			askCats = True, expButton = False, previous = self.values["cats"])
		selectCats.exec_()
		if selectCats.result == "Ok":
			self.values["cats"] = self.selectedCats

	def onAskExps(self):
		selectExps = ExpsListWindow(parent = self.parent(),
			askExps = True, previous = self.values["exps"])
		selectExps.exec_()
		if selectExps.result == "Ok":
			self.values["exps"] = self.parent().selectedExps

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
				widget in [a["content"] for a in self.textValues] \
				+ [self.replOld, self.replNew,
				self.limitValue, self.limitOffs]):
			key = event.key()
			if key == Qt.Key_Return or key == Qt.Key_Enter:
				self.acceptButton.setFocus()
				return True
		return QWidget.eventFilter(self, widget, event)

	def createForm(self, defaultIndex = 0, spaceRowHeight = 25):
		if defaultIndex > len(self.historic):
			defaultIndex = 0
		self.setWindowTitle('Search bibtex entries')
		# tempEl["f"] = QComboBox(self)
		# tempEl["f"].setEditable(True)
		# dbFiles = [f.split(os.sep)[-1] for f in list(glob.iglob(os.path.join(pbConfig.dataPath, "*.db")))]
		# registeredDb = [a["db"].split(os.sep)[-1] for a in profilesData.values()]
		# tempEl["f"].addItems([newLine["db"]] + [f for f in dbFiles if f not in registeredDb])
		# self.currGrid.addWidget(tempEl["f"], i, 2)
		# tempEl["f"].currentIndexChanged[int].connect(changeCurrentContent)

		self.currGrid.addWidget(MyLabelRight(
			"Filter by categories, using the following operator:"),
			0, 0, 1, 3)
		self.catsButton = QPushButton('Categories', self)
		self.catsButton.clicked.connect(self.onAskCats)
		self.currGrid.addWidget(self.catsButton, 0, 3, 1, 2)
		self.comboCats = MyAndOrCombo(self)
		self.comboCats.activated[str].connect(self.onComboCatsChange)
		self.currGrid.addWidget(self.comboCats, 0, 5)

		self.currGrid.addWidget(MyLabelRight(
			"Filter by experiments, using the following operator:"),
			1, 0, 1, 3)
		self.expsButton = QPushButton('Experiments', self)
		self.expsButton.clicked.connect(self.onAskExps)
		self.currGrid.addWidget(self.expsButton, 1, 3, 1, 2)
		self.comboExps = MyAndOrCombo(self)
		self.comboExps.activated[str].connect(self.onComboExpsChange)
		self.currGrid.addWidget(self.comboExps, 1, 5)

		self.currGrid.addWidget(MyLabelRight(
			"If using both categories and experiments, "
			+ "which operator between them?"),
			2, 0, 1, 4)
		self.comboCE = MyAndOrCombo(self)
		self.comboCE.activated[str].connect(self.onComboCEChange)
		self.currGrid.addWidget(self.comboCE, 2, 5)

		self.currGrid.setRowMinimumHeight(3, spaceRowHeight)

		self.marksConn = MyAndOrCombo(self, current = self.values["marksConn"])
		self.currGrid.addWidget(self.marksConn, 4, 0)
		self.currGrid.addWidget(MyLabelRight("Filter by marks:"), 4, 1)
		groupBox, markValues = pBMarks.getGroupbox(
			self.values["marks"], description = "",
			radio = True, addAny = True)
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

		self.currGrid.addWidget(MyLabel(
			"Select more: the operator to use, the field to match, "
			+ "(exact match vs contains) and the content to match"),
			7, 0, 1, 7)
		firstFields = 8
		self.currGrid.setRowMinimumHeight(6, spaceRowHeight)

		for i in range(self.numberOfRows):
			try:
				previous = {
					"logical": "%s"%(
						self.textValues[i]["logical"].currentText()),
					"field": "%s"%self.textValues[i]["field"].currentText(),
					"operator": "%s"%(
						self.textValues[i]["operator"].currentText()),
					"content": "%s"%self.textValues[i]["content"].text()
				}
			except IndexError:
				previous = {"logical": None,
					"field": None,
					"operator": None,
					"content": ""}
				self.textValues.append({})

			self.textValues[i]["logical"] = MyAndOrCombo(self,
				current = previous["logical"])
			self.currGrid.addWidget(self.textValues[i]["logical"],
				i + firstFields, 0)

			self.textValues[i]["field"] = MyComboBox(self,
				["bibtex", "bibkey", "arxiv", "doi", "year",
				"firstdate", "pubdate", "comment"],
				current = previous["field"])
			self.currGrid.addWidget(
				self.textValues[i]["field"], i + firstFields, 1)

			self.textValues[i]["operator"] = MyComboBox(self,
				["contains", "exact match"],
				current = previous["operator"])
			self.currGrid.addWidget(self.textValues[i]["operator"],
				i + firstFields, 2)

			self.textValues[i]["content"] = QLineEdit(previous["content"])
			self.currGrid.addWidget(self.textValues[i]["content"],
				i + firstFields, 3, 1, 4)
			self.textValues[i]["content"].installEventFilter(self)

		self.textValues[-1]["content"].setFocus()

		i = self.numberOfRows + firstFields + 1
		self.currGrid.addWidget(MyLabelRight(
			"Click here if you want more fields:"), i-1, 0, 1, 2)
		self.addFieldButton = QPushButton("Add another line", self)
		self.addFieldButton.clicked.connect(self.onAddField)
		self.currGrid.addWidget(self.addFieldButton, i-1, 2, 1, 2)

		self.currGrid.setRowMinimumHeight(i, spaceRowHeight)

		i += 2
		if self.replace:
			self.currGrid.addWidget(MyLabel("Replace:"), i - 1, 0)
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
			self.replOldField = MyComboBox(self,
				["arxiv", "doi", "year", "author", "title",
				"journal", "number", "volume", "published"],
				current = fieNew)
			self.currGrid.addWidget(self.replOldField, i, 1, 1, 2)
			self.replOld = QLineEdit(old)
			self.currGrid.addWidget(self.replOld, i, 3, 1, 3)
			i += 1
			self.currGrid.addWidget(MyLabelRight("Into field:"), i, 0)
			self.replNewField = MyComboBox(self,
				["arxiv", "doi", "year", "author", "title",
				"journal", "number", "volume"], current = fieNew)
			self.currGrid.addWidget(self.replNewField, i, 1, 1, 2)
			self.replNew = QLineEdit(new)
			self.currGrid.addWidget(self.replNew, i, 3, 1, 3)
			i += 1
			self.doubleEdit = QCheckBox("and also:")
			self.currGrid.addWidget(self.doubleEdit, i, 0)
			self.replNewField1 = MyComboBox(self,
				["arxiv", "doi", "year", "author", "title",
				"journal", "number", "volume"], current = fieNew)
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
			self.currGrid.addWidget(MyLabelRight("Max number of results:"),
				i - 1, 0, 1, 2)
			self.limitValue = QLineEdit(lim)
			self.limitValue.setMaxLength(6)
			self.limitValue.setFixedWidth(75)
			self.currGrid.addWidget(self.limitValue, i - 1, 2)
			self.currGrid.addWidget(MyLabelRight("Start from:"),
				i - 1, 3, 1, 2)
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

		# save button
		self.saveButton = QPushButton('Run and save', self)
		self.saveButton.clicked.connect(self.onSave)
		self.currGrid.addWidget(self.saveButton, i, 5)
		self.saveButton.setFixedWidth(120)

		self.currGrid.setColumnStretch(6, 1)


class MergeBibtexs(EditBibtexDialog):
	"""W"""

	def __init__(self, bib1, bib2, parent = None):
		super(EditBibtexDialog, self).__init__(parent)
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
		self.checkboxes = [
			"exp_paper", "lecture", "phd_thesis", "review",
			"proceeding", "book", "noUpdate"]
		self.generic = [
			"year", "doi", "arxiv", "inspire", "isbn", "firstdate",
			"pubdate", "ads", "scholar", "link", "comments",
			"old_keys", "crossref"]
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
			self.textValues[ix][k] = QLineEdit(
				str(self.dataOld[ix][k] if self.dataOld[ix][k] is not None  \
					else ""))
			self.textValues[ix][k].setReadOnly(True)
			self.currGrid.addWidget(self.textValues[ix][k], i, c)
		def addFieldNew(k, i, v):
			self.textValues[k] = QLineEdit(str(v))
			self.textValues[k].textEdited.connect(
				lambda x: self.textModified(k, x))
			self.currGrid.addWidget(self.textValues[k], i, 2)
		def addRadio(ix, k, i, c):
			self.radioButtons[ix][k] = QRadioButton("")
			self.radioButtons[ix][k].setAutoExclusive(False)
			self.radioButtons[ix][k].clicked.connect(
				lambda x = False: self.radioToggled(ix, k, x))
			self.currGrid.addWidget(self.radioButtons[ix][k], i, c)
		def addBibtexOld(ix, i, c):
			k = "bibtex"
			self.textValues[ix][k] = QPlainTextEdit(
				str(self.dataOld[ix][k] if self.dataOld[ix][k] is not None \
					else ""))
			self.textValues[ix][k].setReadOnly(True)
			self.textValues[ix][k].setMinimumWidth(self.bibtexWidth)
			self.currGrid.addWidget(self.textValues[ix][k],
				i, c, self.bibtexEditLines, 1)
		self.setWindowTitle('Merge bibtex entries')

		i = 0
		for k in self.generic:
			if self.dataOld["0"][k] == self.dataOld["1"][k]:
				self.textValues[k] = QLineEdit(str(self.dataOld["0"][k]))
				self.textValues[k].hide()
			else:
				self.currGrid.addWidget(MyLabelCenter(
					"%s (%s)"%(k, pBDB.descriptions["entries"][k])),
					i, 0, 1, 5)
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
		groupBox, markValues = pBMarks.getGroupbox(
			self.data["marks"],
			description = pBDB.descriptions["entries"]["marks"])
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
		self.currGrid.addWidget(MyLabelCenter(
			"%s (%s)"%(k, pBDB.descriptions["entries"][k])), i, 0, 1, 5)
		i += 1
		addFieldOld("0", k, i, 0)
		addFieldOld("1", k, i, 4)
		self.textValues[k] = QLineEdit("")
		self.textValues[k].setReadOnly(True)
		self.currGrid.addWidget(self.textValues[k], i, 2)
		i += 1
		k = "bibtex"
		self.currGrid.addWidget(MyLabelCenter(
			"%s (%s)"%(k, pBDB.descriptions["entries"][k])), i, 0, 1, 5)
		i += 1
		addBibtexOld("0", i, 0)
		addRadio("0", k, i, 1)
		addBibtexOld("1", i, 4)
		addRadio("1", k, i, 3)
		#radio and connection
		self.textValues[k] = QPlainTextEdit(
			str(self.data[k] if self.data[k] is not None else ""))
		self.textValues[k].textChanged.connect(self.updateBibkey)
		self.textValues[k].setMinimumWidth(self.bibtexWidth)
		self.textValues[k].textChanged.connect(
			lambda x = "": self.textModified("bibtex", str(x)))
		self.currGrid.addWidget(self.textValues[k],
			i, 2, self.bibtexEditLines, 1)
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


class FieldsFromArxiv(QDialog):
	"""Dialog windows used to ask which fields should be imported
	from the arXiv record of the field"""

	def __init__(self, parent = None):
		"""Initialize the properties and the layout of the widget

		Parameter:
			parent: the parent widget
		"""
		super(FieldsFromArxiv, self).__init__(parent)
		self.setWindowTitle("Import fields from arXiv")
		self.checkBoxes = {}
		self.arxivDict = [
			"authors", "title", "doi", "primaryclass", "archiveprefix"]
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
		"""Accept the dialog output and prepare self.output"""
		self.output = []
		for k in self.checkBoxes.keys():
			if self.checkBoxes[k].isChecked():
				self.output.append(k)
		self.result = True
		self.close()

	def onCancel(self):
		"""Reject the dialog output"""
		self.result = False
		self.close()
