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
	def __init__(self, parent = None):
		super(catsWindowList, self).__init__(parent)
		self.parent = parent
		self.currLayout = QHBoxLayout(self)

		self.setMinimumWidth(400)
		self.setMinimumHeight(600)

		self.fillTree()

	def keyPressEvent(self, e):		
		if e.key() == Qt.Key_Escape:
			self.close()

	def fillTree(self):
		tree = pBDB.cats.getHier()

		self.tree = QTreeView(self)
		self.currLayout.addWidget(self.tree)

		root_model = QStandardItemModel()
		self.tree.setModel(root_model)
		self._populateTree(tree, root_model.invisibleRootItem())
		self.tree.expandAll()

		#hheader = QHeaderView(Qt.Orientation.Horizontal)
		self.tree.setHeaderHidden(True)
		#self.tree.setHorizontalHeaderLabels(["Categories"])

		self.tree.clicked.connect(self.askAndPerformAction)

	def _populateTree(self, children, parent):
		for child in cats_alphabetical(children):
			child_item = QStandardItem(catString(child))
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
		o = self.layout().takeAt(0)
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
		self.createForm()

	def createForm(self):
		self.setWindowTitle('Edit category')

		i = 0
		for k in pBDB.tableCols["categories"]:
			val = self.data[k]
			if k != "idCat" or (k == "idCat" and self.data[k] != ""):
				i += 1
				self.currGrid.addWidget(QLabel(pBDB.descriptions["categories"][k]), i*2-1, 0)
				self.currGrid.addWidget(QLabel("(%s)"%k), i*2-1, 1)
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
