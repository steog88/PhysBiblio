#!/usr/bin/env python
import sys
from PySide.QtCore import *
from PySide.QtGui  import *
import subprocess, traceback
try:
	from pybiblio.errors import pBErrorManager
except ImportError:
	print("Could not find pybiblio.errors and its contents: configure your PYTHONPATH!")
	print(traceback.format_exc())

try:
	from pybiblio.database import *
	#import pybiblio.export as bibexport
	#import pybiblio.webimport.webInterf as webInt
	#from pybiblio.cli import cli as pyBiblioCLI
	from pybiblio.config import pbConfig
	from pybiblio.gui.DialogWindows import *
	from pybiblio.gui.CommonClasses import *
except ImportError:
	print("Could not find pybiblio and its contents: configure your PYTHONPATH!")
try:
	import pybiblio.gui.Resources_pyside
except ImportError:
	print("Missing Resources_pyside.py: Run script update_resources.sh")

def editExperiment(parent, statusBarObject, editIdExp = None):
	if editIdExp is not None:
		edit = pBDB.exps.getDictByID(editIdExp)
	else:
		edit = None
	newExpWin = editExp(parent, exp = edit)
	newExpWin.exec_()
	data = {}
	if newExpWin.result:
		for k, v in newExpWin.textValues.items():
			s = "%s"%v.text()
			data[k] = s
		if data["name"].strip() != "":
			if "idExp" in data.keys():
				print("[GUI] Updating experiment %s..."%data["idExp"])
				pBDB.exps.update(data, data["idExp"])
			else:
				pBDB.exps.insert(data)
			message = "Experiment saved"
			statusBarObject.setWindowTitle("PyBiblio*")
			try:
				parent.recreateTable()
			except:
				pass
		else:
			message = "ERROR: empty experiment name"
	else:
		message = "No modifications to experiments"
	try:
		statusBarObject.StatusBarMessage(message)
	except:
		pass

def deleteExperiment(parent, statusBarObject, idExp, name):
	if askYesNo("Do you really want to delete this experiment (ID = '%s', name = '%s')?"%(idExp, name)):
		pBDB.exps.delete(int(idExp))
		statusBarObject.setWindowTitle("PyBiblio*")
		message = "Experiment deleted"
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

class ExpWindowList(objListWindow):
	"""create a window for printing the list of experiments"""
	def __init__(self, parent = None, askExps = False, askForBib = None, askForCat = None):

		#table dimensions
		self.colcnt = len(pBDB.tableCols["experiments"])
		self.colContents = []
		for j in range(self.colcnt):
			self.colContents.append(pBDB.tableCols["experiments"][j])
		self.colContents.append("modify")
		self.colContents.append("delete")
		self.askExps = askExps

		super(ExpWindowList, self).__init__(parent)
		self.parent = parent
		self.setWindowTitle('List of experiments')

		if self.askExps:
			if askForBib is not None:
				bibitem = pBDB.bibs.getByBibkey(askForBib)[0]
				try:
					bibtext = QLabel("Mark categories for the following entry:\n    key:\n%s\n    author(s):\n%s\n    title:\n%s\n"%(askForBib, bibitem["author"], bibitem["title"]))
				except:
					bibtext = QLabel("Mark categories for the following entry:\n    key:\n%s\n"%(askForBib))
				self.currLayout.addWidget(bibtext)
			elif askForCat is not None:
				pass
			else:
				pBErrorManager("[askCats] asking categories for what? no Bib or Cat specified!")
				return
			self.marked = []
			self.parent.selectedCats = []
			
		self.createTable()

	def onCancel(self):
		self.result	= False
		self.close()

	def onOk(self):
		self.parent.selectedExps = []

		for i in range(self.tablewidget.rowCount()):
			item = self.tablewidget.item(i, 0)
			if item.checkState():
				idExp = item.text()
				self.parent.selectedExps.append(int(idExp))
			
		self.result	= "Ok"
		self.close()

	def keyPressEvent(self, e):		
		if e.key() == Qt.Key_Escape:
			self.close()

	def createTable(self):
		exps = pBDB.exps.getAll()
		rowcnt = len(exps)

		#table settings and header
		self.setTableSize(rowcnt, self.colcnt+2)
		self.tablewidget.setHorizontalHeaderLabels(pBDB.tableCols["experiments"]+["Modify","Delete"])

		#table content
		for i in range(rowcnt):
			for j in range(self.colcnt):
				if j == self.colcnt-1:
					item = QTableWidgetItem(
						("http://inspirehep.net/record/" + str(exps[i][pBDB.tableCols["experiments"][j]]) \
						if exps[i][pBDB.tableCols["experiments"][j]] != "" else "") )
				else:
					item = QTableWidgetItem(str(exps[i][pBDB.tableCols["experiments"][j]]))
				if j==0 and self.askExps:
					item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
					item.setCheckState(Qt.Unchecked)
				else:
					item.setFlags(Qt.ItemIsEnabled)
				self.tablewidget.setItem(i, j, item)
			self.addEditDeleteCells(i, self.colcnt)

		self.finalizeTable()

		if self.askExps:
			self.acceptButton = QPushButton('OK', self)
			self.acceptButton.clicked.connect(self.onOk)
			self.currLayout.addWidget(self.acceptButton)
			
			# cancel button
			self.cancelButton = QPushButton('Cancel', self)
			self.cancelButton.clicked.connect(self.onCancel)
			self.cancelButton.setAutoDefault(True)
			self.currLayout.addWidget(self.cancelButton)

	def cellClick(self, row, col):
		idExp = self.tablewidget.item(row, 0).text()
		if self.colContents[col] == "modify":
			editExperiment(self, self.parent, idExp)
		elif self.colContents[col] == "delete":
			name = self.tablewidget.item(row, 1).text()
			deleteExperiment(self, self.parent, idExp, name)

	def cellDoubleClick(self, row, col):
		idExp = self.tablewidget.item(row, 0).text()
		if self.colContents[col] == "inspire" or self.colContents[col] == "homepage":
			link = self.tablewidget.item(row, col).text()
			print "will open '%s' "%link
			try:
				print("[GUI] opening '%s'..."%link)
				subprocess.Popen([pbConfig.params["webApplication"], link], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
			except:
				print("[GUI] opening link '%s' failed!"%link)

class editExp(editObjectWindow):
	"""create a window for editing or creating an experiment"""
	def __init__(self, parent = None, exp = None):
		super(editExp, self).__init__(parent)
		if exp is None:
			self.data = {}
			for k in pBDB.tableCols["experiments"]:
				self.data[k] = ""
		else:
			self.data = exp
		self.createForm()

	def createForm(self):
		self.setWindowTitle('Edit experiment')

		i = 0
		for k in pBDB.tableCols["experiments"]:
			val = self.data[k]
			if k != "idExp" or (k == "idExp" and self.data[k] != ""):
				i += 1
				self.currGrid.addWidget(QLabel(k), i*2-1, 0)
				self.currGrid.addWidget(QLabel("(%s)"%pBDB.descriptions["experiments"][k]), i*2-1, 1)
				self.textValues[k] = QLineEdit(str(val))
				if k == "idExp":
					self.textValues[k].setEnabled(False)
				self.currGrid.addWidget(self.textValues[k], i*2, 0, 1, 2)

		# OK button
		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		self.currGrid.addWidget(self.acceptButton, i*2+1, 0)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		self.currGrid.addWidget(self.cancelButton, i*2+1, 1)

		self.setGeometry(100,100,400, 50*i)
		self.centerWindow()
