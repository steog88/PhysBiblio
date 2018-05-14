#!/usr/bin/env python
import sys
from PySide.QtCore import *
from PySide.QtGui  import *
import traceback
import operator

try:
	from physbiblio.database import *
	from physbiblio.config import pbConfig
	from physbiblio.gui.DialogWindows import *
	from physbiblio.gui.CommonClasses import *
	from physbiblio.gui.CatWindows import *
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
try:
	if sys.version_info[0] < 3:
		import physbiblio.gui.Resources_pyside
	else:
		import physbiblio.gui.Resources_pyside3
except ImportError:
	print("Missing Resources_pyside: Run script update_resources.sh")

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
			statusBarObject.setWindowTitle("PhysBiblio*")
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
		statusBarObject.setWindowTitle("PhysBiblio*")
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

class MyExpTableModel(MyTableModel):
	def __init__(self, parent, exp_list, header, askExps = False, previous = [], *args):
		self.typeClass = "Exps"
		self.dataList = exp_list
		MyTableModel.__init__(self, parent, header, askExps, previous, *args)
		self.prepareSelected()

	def getIdentifier(self, element):
		return element["idExp"]

	def data(self, index, role):
		if not index.isValid():
			return None
		row = index.row()
		column = index.column()
		try:
			value = self.dataList[row][column]
		except IndexError:
			return None

		if role == Qt.CheckStateRole and self.ask and column == 0:
			if self.selectedElements[self.dataList[row][0]] == False:
				return Qt.Unchecked
			else:
				return Qt.Checked
		if role == Qt.EditRole:
			return value
		if role == Qt.DisplayRole:
			return value
		return None

	def setData(self, index, value, role):
		if role == Qt.CheckStateRole and index.column() == 0:
			if value == Qt.Checked:
				self.selectedElements[self.dataList[index.row()][0]] = True
			else:
				self.selectedElements[self.dataList[index.row()][0]] = False

		self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
		return True

class ExpWindowList(objListWindow):
	"""create a window for printing the list of experiments"""
	def __init__(self, parent = None, askExps = False, askForBib = None, askForCat = None, previous = []):

		#table dimensions
		self.colcnt = len(pBDB.tableCols["experiments"])
		self.colContents = []
		for j in range(self.colcnt):
			self.colContents.append(pBDB.tableCols["experiments"][j])
		self.askExps = askExps
		self.askForBib = askForBib
		self.askForCat = askForCat
		self.previous = previous

		super(ExpWindowList, self).__init__(parent)
		self.parent = parent
		self.setWindowTitle('List of experiments')

		self.createTable()

	def populateAskExp(self):
		if self.askExps:
			if self.askForBib is not None:
				bibitem = pBDB.bibs.getByBibkey(self.askForBib, saveQuery = False)[0]
				try:
					bibtext = QLabel("Mark categories for the following entry:\n    key:\n%s\n    author(s):\n%s\n    title:\n%s\n"%(self.askForBib, bibitem["author"], bibitem["title"]))
				except:
					bibtext = QLabel("Mark categories for the following entry:\n    key:\n%s\n"%(self.askForBib))
				self.currLayout.addWidget(bibtext)
			elif self.askForCat is not None:
				pass
			self.marked = []
			self.parent.selectedExps = []

	def onCancel(self):
		self.result	= False
		self.close()

	def onOk(self):
		self.parent.selectedExps = [idE for idE in self.table_model.selectedElements.keys() if self.table_model.selectedElements[idE] == True]
		self.result	= "Ok"
		self.close()

	def onNewExp(self):
		editExperiment(self.parent, self.parent)
		self.recreateTable()

	def keyPressEvent(self, e):		
		if e.key() == Qt.Key_Escape:
			self.close()

	def changeFilter(self, string):
		self.proxyModel.setFilterRegExp(str(string))

	def createTable(self):
		self.populateAskExp()

		self.exps = pBDB.exps.getAll()

		self.table_model = MyExpTableModel(self, self.exps, pBDB.tableCols["experiments"], askExps = self.askExps, previous = self.previous)
		self.addFilterInput("Filter experiment")
		self.setProxyStuff(1, Qt.AscendingOrder)

		self.finalizeTable()

		self.addExpButton = QPushButton('Add new experiment', self)
		self.addExpButton.clicked.connect(self.onNewExp)
		self.currLayout.addWidget(self.addExpButton)

		if self.askExps:
			self.acceptButton = QPushButton('OK', self)
			self.acceptButton.clicked.connect(self.onOk)
			self.currLayout.addWidget(self.acceptButton)
			
			# cancel button
			self.cancelButton = QPushButton('Cancel', self)
			self.cancelButton.clicked.connect(self.onCancel)
			self.cancelButton.setAutoDefault(True)
			self.currLayout.addWidget(self.cancelButton)

	def triggeredContextMenuEvent(self, row, col, event):
		index = self.tablewidget.model().index(row, col)
		try:
			idExp = str(self.proxyModel.sibling(row, 0, index).data())
			expName = str(self.proxyModel.sibling(row, 1, index).data())
		except AttributeError:
			return
		menu = QMenu()
		titAct = menu.addAction("--Experiment: %s--"%expName).setDisabled(True)
		menu.addSeparator()
		bibAction = menu.addAction("Open list of corresponding entries")
		menu.addSeparator()
		modAction = menu.addAction("Modify")
		delAction = menu.addAction("Delete")
		menu.addSeparator()
		catAction = menu.addAction("Categories")
		action = menu.exec_(event.globalPos())

		if action == bibAction:
			searchDict = {"exps": {"id": [idExp], "operator": "and"}}
			self.parent.reloadMainContent(pBDB.bibs.fetchFromDict(searchDict).lastFetched)
		elif action == modAction:
			editExperiment(self, self.parent, idExp)
		elif action == delAction:
			deleteExperiment(self, self.parent, idExp, expName)
		elif action == catAction:
			previous = [a[0] for a in pBDB.cats.getByExp(idExp)]
			selectCats = catsWindowList(parent = self.parent, askCats = True, askForExp = idExp, expButton = False, previous = previous)
			selectCats.exec_()
			if selectCats.result == "Ok":
				cats = self.parent.selectedCats
				for p in previous:
					if p not in cats:
						pBDB.catExp.delete(p, idExp)
				for c in cats:
					if c not in previous:
						pBDB.catExp.insert(c, idExp)
				self.parent.StatusBarMessage("categories for '%s' successfully inserted"%expName)
				
	def cellClick(self, index):
		if index.isValid():
			row = index.row()
		else:
			return
		idExp = str(self.proxyModel.sibling(row, 0, index).data())

	def cellDoubleClick(self, index):
		if index.isValid():
			row = index.row()
			col = index.column()
		else:
			return
		idExp = str(self.proxyModel.sibling(row, 0, index).data())
		if self.colContents[col] == "inspire" or self.colContents[col] == "homepage":
			link = self.proxyModel.sibling(row, col, index).data()
			if link == "":
				return
			if self.colContents[col] == "inspire":
				link = "http://inspirehep.net/record/" + link
			print("will open '%s' "%link)
			try:
				print("[GUI] opening '%s'..."%link)
				pBGuiView.openLink(link, "link")
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
