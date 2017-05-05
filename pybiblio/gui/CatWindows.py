#!/usr/bin/env python
import sys
from PySide.QtCore import *
from PySide.QtGui  import *
import subprocess

try:
	from pybiblio.database import pBDB, cats_alphabetical, catString
	from pybiblio.config import pbConfig
	from pybiblio.gui.DialogWindows import *
	from pybiblio.gui.CommonClasses import *
except ImportError:
	print("Could not find pybiblio and its contents: configure your PYTHONPATH!")
try:
	import pybiblio.gui.Resources_pyside
except ImportError:
	print("Missing Resources_pyside.py: Run script update_resources.sh")

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
			statusBarObject.setWindowTitle("PyBiblio*")
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
		statusBarObject.setWindowTitle("PyBiblio*")
		message = "Category deleted"
		#try:
		parent.recreateTable()
		#except:
			#pass
	else:
		message = "Nothing changed"
	try:
		statusBarObject.StatusBarMessage(message)
	except:
		pass

class catsWindowList(QDialog):
	def __init__(self, parent = None, askCats = False, askForBib = None, askForExp = None, expButton = True, previous = [], single = False):
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
		self.parent.selectedCats = []

		def getChecked(root):
			child_count = root.rowCount()
			for i in range(child_count):
				item = root.child(i)
				if item.checkState():
					idCat, name = item.text().split(": ")
					self.parent.selectedCats.append(int(idCat))
				getChecked(item)

		getChecked(self.tree.model().invisibleRootItem())
		if self.single and len(self.parent.selectedCats) > 1 and self.parent.selectedCats[0] == 0:
			self.parent.selectedCats.pop(0)
		if exps:
			self.result	= "Exps"
		else:
			self.result	= "Ok"
		self.close()

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

		tree = pBDB.cats.getHier()

		self.tree = QTreeView(self)
		self.currLayout.addWidget(self.tree)

		root_model = QStandardItemModel()
		self.tree.setModel(root_model)
		self._populateTree(tree, root_model.invisibleRootItem())
		self.tree.expandAll()

		self.tree.setHeaderHidden(True)
		self.tree.doubleClicked.connect(self.askAndPerformAction)

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

	def _populateTree(self, children, parent):
		for child in cats_alphabetical(children):
			child_item = QStandardItem(catString(child))
			if self.askCats:
				child_item.setCheckable(True)
				if child in self.previous:
					child_item.setCheckState(Qt.Checked)
			parent.appendRow(child_item)
			self._populateTree(children[child], child_item)

	def askAndPerformAction(self, index):
		item = self.tree.selectedIndexes()[0]
		idCat, name = item.model().itemFromIndex(index).text().split(": ")
		idCat = idCat.strip()
		ask = askCatAction(self, int(idCat), name)
		ask.exec_()
		if ask.result == "modify":
			editCategory(self, self.parent, idCat)
		elif ask.result == "delete":
			deleteCategory(self, self.parent, idCat, name)
		elif ask.result == "subcat":
			editCategory(self, self.parent, useParent = idCat)
		elif ask.result == False:
			self.parent.StatusBarMessage("Action cancelled")
		else:
			self.parent.StatusBarMessage("Invalid action")

	def recreateTable(self):
		"""delete previous table widget and create a new one"""
		while True:
			o = self.layout().takeAt(0)
			if o is None: break
			o.widget().deleteLater()
		self.fillTree()

class askCatAction(askAction):
	def __init__(self, parent = None, idCat = -1, name = ""):
		super(askCatAction, self).__init__(parent)
		self.message = "What to do with this category (%d - %s)?"%(idCat, name)
		self.possibleActions.append(["Add subcategory", self.onSubCat])
		self.initUI()

	def onSubCat(self):
		self.result	= "subcat"
		self.close()

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
