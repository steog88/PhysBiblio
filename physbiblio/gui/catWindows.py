"""
Module with the classes and functions that manage the categories windows and panels.

This file is part of the physbiblio package.
"""
import sys
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QTreeView, QVBoxLayout, QToolTip

try:
	from physbiblio.errors import pBLogger
	from physbiblio.database import pBDB, cats_alphabetical
	from physbiblio.config import pbConfig
	from physbiblio.gui.errorManager import pBGUILogger
	from physbiblio.gui.basicDialogs import *
	from physbiblio.gui.commonClasses import *
	import physbiblio.gui.resourcesPyside2
except ImportError:
	print("Could not find physbiblio and its modules!")
	print(traceback.format_exc())

def editCategory(parent, statusBarObject, editIdCat = None, useParent = None):
	if editIdCat is not None:
		edit = pBDB.cats.getDictByID(editIdCat)
	else:
		edit = None
	newCatWin = editCat(parent, cat = edit, useParent = useParent)
	newCatWin.exec_()
	data = {}
	if newCatWin.result:
		for k, v in newCatWin.textValues.items():
			if k == "parentCat":
				try:
					s = str(newCatWin.selectedCats[0])
				except IndexError:
					s = "0"
			else:
				s = "%s"%v.text()
			data[k] = s
		if data["name"].strip() != "":
			if "idCat" in data.keys():
				print("[GUI] Updating category %s..."%data["idCat"])
				pBDB.cats.update(data, data["idCat"])
			else:
				pBDB.cats.insert(data)
			message = "Category saved"
			statusBarObject.setWindowTitle("PhysBiblio*")
			try:
				parent.recreateTable()
			except:
				pass
		else:
			message = "ERROR: empty category name"
	else:
		message = "No modifications to categories"
	try:
		statusBarObject.StatusBarMessage(message)
	except:
		pass

def deleteCategory(parent, statusBarObject, idCat, name):
	if askYesNo("Do you really want to delete this category (ID = '%s', name = '%s')?"%(idCat, name)):
		pBDB.cats.delete(int(idCat))
		statusBarObject.setWindowTitle("PhysBiblio*")
		message = "Category deleted"
		parent.recreateTable()
	else:
		message = "Nothing changed"
	try:
		statusBarObject.StatusBarMessage(message)
	except:
		pass

class catsModel(TreeModel):
	def __init__(self, cats, rootElements, parent = None, previous = [], multipleRecords = False):
		self.cats = cats
		self.rootElements = rootElements
		TreeModel.__init__(self)
		self.parentObj = parent
		self.selectedCats = {}
		self.previousSaved = {}
		for cat in self.cats:
			self.selectedCats[cat["idCat"]] = False
			self.previousSaved[cat["idCat"]] = False
		for prevIx in previous:
			try:
				if multipleRecords:
					self.previousSaved[prevIx] = True
					self.selectedCats[prevIx] = "p"
				else:
					self.selectedCats[prevIx] = True
			except IndexError:
				pBLogger.warning("Invalid idCat in previous selection: %s"%prevIx)

	def _getRootNodes(self):
		return [NamedNode(elem, None, index)
			for index, elem in enumerate(self.rootElements)]

	def columnCount(self, parent):
		return 1

	def data(self, index, role):
		if not index.isValid():
			return None
		row = index.row()
		column = index.column()
		value = index.internalPointer().element.text
		idCat = index.internalPointer().element.idCat
		if role == Qt.DisplayRole and index.column() == 0:
			return value

		if role == Qt.CheckStateRole and self.parentObj.askCats and column == 0:
			if self.previousSaved[idCat] == True and self.selectedCats[idCat] == "p":
				return Qt.PartiallyChecked
			elif self.selectedCats[idCat] == False:
				return Qt.Unchecked
			else:
				return Qt.Checked
		if role == Qt.EditRole:
			return value
		if role == Qt.DisplayRole:
			return value
		return None

	def flags(self, index):
		if not index.isValid():
			return None
		if index.column() == 0 and self.parentObj.askCats:
			return Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
		else:
			return Qt.ItemIsEnabled | Qt.ItemIsSelectable

	def headerData(self, section, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole \
			and section == 0:
			return 'Name'
		return None

	def setData(self, index, value, role):
		idCat = index.internalPointer().element.idCat
		if role == Qt.CheckStateRole and index.column() == 0:
			self.previousSaved[idCat] = False
			if value == Qt.Checked:
				self.selectedCats[idCat] = True
			else:
				self.selectedCats[idCat] = False
		self.dataChanged.emit(index, index)
		return True

class catsWindowList(QDialog):
	def __init__(self, parent = None, askCats = False, askForBib = None, askForExp = None, expButton = True, previous = [], single = False, multipleRecords = False):
		super(catsWindowList, self).__init__(parent)
		self.parent = parent
		self.setWindowTitle("Categories")
		self.currLayout = QVBoxLayout(self)
		self.askCats = askCats
		self.askForBib = askForBib
		self.askForExp = askForExp
		self.expButton = expButton
		self.previous = previous
		self.single = single
		self.multipleRecords = multipleRecords

		self.setMinimumWidth(400)
		self.setMinimumHeight(600)

		self.fillTree()

	def populateAskCat(self):
		if self.askCats:
			if self.askForBib is not None:
				bibitem = pBDB.bibs.getByBibkey(self.askForBib, saveQuery = False)[0]
				try:
					bibtext = QLabel("Mark categories for the following entry:\n    key:\n%s\n    author(s):\n%s\n    title:\n%s\n"%(self.askForBib, bibitem["author"], bibitem["title"]))
				except:
					bibtext = QLabel("Mark categories for the following entry:\n    key:\n%s\n"%(self.askForBib))
				self.currLayout.addWidget(bibtext)
			elif self.askForExp is not None:
				pass
			else:
				if self.single:
					comment = QLabel("Select the desired category (only the first one will be considered):")
				else:
					comment = QLabel("Select the desired categories:")
				self.currLayout.addWidget(comment)
			self.marked = []
			self.parent.selectedCats = []

	def onCancel(self):
		self.result	= False
		self.close()

	def onOk(self, exps = False):
		self.parent.selectedCats = [idC for idC in self.root_model.selectedCats.keys() if self.root_model.selectedCats[idC] == True]
		self.parent.previousUnchanged = [idC for idC in self.root_model.previousSaved.keys() if self.root_model.previousSaved[idC] == True]

		if self.single and len(self.parent.selectedCats) > 1 and self.parent.selectedCats[0] == 0:
			self.parent.selectedCats.pop(0)
		if exps:
			self.result	= "Exps"
		else:
			self.result	= "Ok"
		self.close()

	def changeFilter(self, string):
		self.proxyModel.setFilterRegExp(str(string))
		self.tree.expandAll()

	def onAskExps(self):
		self.onOk(exps = True)

	def onNewCat(self):
		editCategory(self.parent, self.parent)
		self.recreateTable()

	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Escape:
			self.close()

	def fillTree(self):
		self.populateAskCat()

		catsTree = pBDB.cats.getHier()

		self.filterInput = QLineEdit("",  self)
		self.filterInput.setPlaceholderText("Filter cateogries")
		self.filterInput.textChanged.connect(self.changeFilter)
		self.currLayout.addWidget(self.filterInput)
		self.filterInput.setFocus()

		self.tree = QTreeView(self)
		self.currLayout.addWidget(self.tree)
		self.tree.setMouseTracking(True)
		self.tree.entered.connect(self.handleItemEntered)

		catsNamedTree = self._populateTree(catsTree[0], 0)

		self.root_model = catsModel(pBDB.cats.getAll(), [catsNamedTree], self, self.previous, multipleRecords = self.multipleRecords)
		self.proxyModel = LeafFilterProxyModel(self)
		self.proxyModel.setSourceModel(self.root_model)
		self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
		self.proxyModel.setSortCaseSensitivity(Qt.CaseInsensitive)
		self.proxyModel.setFilterKeyColumn(-1)
		self.tree.setModel(self.proxyModel)

		self.tree.expandAll()

		self.tree.setHeaderHidden(True)
		#self.tree.doubleClicked.connect(self.askAndPerformAction)

		self.newCatButton = QPushButton('Add new category', self)
		self.newCatButton.clicked.connect(self.onNewCat)
		self.currLayout.addWidget(self.newCatButton)
		
		if self.askCats:
			self.acceptButton = QPushButton('OK', self)
			self.acceptButton.clicked.connect(self.onOk)
			self.currLayout.addWidget(self.acceptButton)
			
			if self.expButton:
				self.expsButton = QPushButton('Ask experiments', self)
				self.expsButton.clicked.connect(self.onAskExps)
				self.currLayout.addWidget(self.expsButton)

			# cancel button
			self.cancelButton = QPushButton('Cancel', self)
			self.cancelButton.clicked.connect(self.onCancel)
			self.cancelButton.setAutoDefault(True)
			self.currLayout.addWidget(self.cancelButton)

	def _populateTree(self, children, idCat):
		name = pBDB.cats.getByID(idCat)[0]["name"]
		children_list = []
		for child in cats_alphabetical(children, pBDB):
			child_item = self._populateTree(children[child], child)
			children_list.append(child_item)
		return NamedElement(idCat, name, children_list)

	def handleItemEntered(self, index):
		if index.isValid():
			row = index.row()
		else:
			return
		idCat, catName = self.proxyModel.sibling(row, 0, index).data().split(": ")
		idCat = idCat.strip()
		try:
			self.timerA.stop()
			self.timerB.stop()
			QToolTip.showText(QCursor.pos(), "", self.tree.viewport())
		except AttributeError:
			pass
		try:
			catData = pBDB.cats.getByID(idCat)[0]
		except IndexError:
			pBGUILogger.exception("Failed in finding category")
			return
		self.timerA = QTimer(self)
		self.timerA.setSingleShot(True)
		self.timerA.timeout.connect(lambda: QToolTip.showText(
			QCursor.pos(),
			"{idC}: {cat}\nCorresponding entries: {en}\nAssociated experiments: {ex}".format(
				idC = idCat, cat = catData["name"], en = pBDB.catBib.countByCat(idCat), ex = pBDB.catExp.countByCat(idCat)),
			self.tree.viewport(),
			self.tree.visualRect(index)
		))
		self.timerA.start(500)
		self.timerB = QTimer(self)
		self.timerB.setSingleShot(True)
		self.timerB.timeout.connect(lambda: QToolTip.showText(QCursor.pos(), "", self.tree.viewport()))
		self.timerB.start(3500)

	def contextMenuEvent(self, event):
		index = self.tree.selectedIndexes()[0]
		row = index.row()
		idCat, catName = self.proxyModel.sibling(row, 0, index).data().split(": ")
		idCat = idCat.strip()
		
		menu = MyMenu()
		titAction = QAction("--Category: %s--"%catName)
		titAction.setDisabled(True)
		bibAction = QAction("Open list of corresponding entries")
		modAction = QAction("Modify")
		delAction = QAction("Delete")
		subAction = QAction("Add subcategory")
		menu.possibleActions = [
			titAction, None, bibAction, None, modAction, delAction, None, subAction
			]
		menu.fillMenu()

		action = menu.exec_(event.globalPos())
		if action == bibAction:
			searchDict = {"cats": {"id": [idCat], "operator": "and"}}
			self.parent.reloadMainContent(pBDB.bibs.fetchFromDict(searchDict).lastFetched)
		elif action == modAction:
			editCategory(self, self.parent, idCat)
		elif action == delAction:
			deleteCategory(self, self.parent, idCat, catName)
		elif action == subAction:
			editCategory(self, self.parent, useParent = idCat)

	def cleanLayout(self):
		"""delete previous widgets"""
		while True:
			o = self.layout().takeAt(0)
			if o is None: break
			o.widget().deleteLater()

	def recreateTable(self):
		"""delete previous widgets and create new ones"""
		self.cleanLayout()
		self.fillTree()

class editCat(editObjectWindow):
	"""create a window for editing or creating a category"""
	def __init__(self, parent = None, cat = None, useParent = None):
		super(editCat, self).__init__(parent)
		if cat is None:
			self.data = {}
			for k in pBDB.tableCols["categories"]:
				self.data[k] = ""
		else:
			self.data = cat
		if useParent is not None:
			self.data["parentCat"] = useParent
			self.selectedCats = [useParent]
		elif cat is not None:
			try:
				self.selectedCats = [pBDB.cats.getParent(cat["idCat"])[0][0]]
			except IndexError:
				self.selectedCats = [0]
		else:
			self.selectedCats = [0]
		self.createForm()

	def onAskParent(self):
		selectCats = catsWindowList(parent = self, askCats = True, expButton = False, single = True, previous = self.selectedCats)
		selectCats.exec_()
		if selectCats.result == "Ok":
			try:
				val = self.selectedCats[0]
				self.textValues["parentCat"].setText("%s - %s"%(str(val), pBDB.cats.getByID(val)[0]["name"]))
			except IndexError:
				self.textValues["parentCat"].setText("Select parent")

	def createForm(self):
		self.setWindowTitle('Edit category')

		i = 0
		for k in pBDB.tableCols["categories"]:
			val = self.data[k]
			if k != "idCat" or (k == "idCat" and self.data[k] != ""):
				i += 1
				self.currGrid.addWidget(QLabel(pBDB.descriptions["categories"][k]), i*2-1, 0)
				self.currGrid.addWidget(QLabel("(%s)"%k), i*2-1, 1)
				if k == "parentCat":
					try:
						val = self.selectedCats[0]
						self.textValues[k] = QPushButton("%s - %s"%(str(val), pBDB.cats.getByID(val)[0]["name"]), self)
					except IndexError:
						self.textValues[k] = QPushButton("Select parent", self)
					self.textValues[k].clicked.connect(self.onAskParent)
				else:
					self.textValues[k] = QLineEdit(str(val))
				if k == "idCat":
					self.textValues[k].setEnabled(False)
				self.currGrid.addWidget(self.textValues[k], i*2, 0, 1, 2)

		# OK button
		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		self.currGrid.addWidget(self.acceptButton, i*2+1, 1)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		self.currGrid.addWidget(self.cancelButton, i*2+1, 0)

		self.setGeometry(100,100,400, 50*i)
		self.centerWindow()
