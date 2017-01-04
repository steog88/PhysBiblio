#!/usr/bin/env python
import sys
from PySide.QtCore import *
from PySide.QtGui  import *
import subprocess

try:
	from pybiblio.database import pBDB, cats_alphabetical, catString
	#import pybiblio.export as bibexport
	#import pybiblio.webimport.webInterf as webInt
	#from pybiblio.cli import cli as pyBiblioCLI
	from pybiblio.config import pbConfig
except ImportError:
	print("Could not find pybiblio and its contents: configure your PYTHONPATH!")
try:
	import pybiblio.gui.Resources_pyside
except ImportError:
	print("Missing Resources_pyside.py: Run script update_resources.sh")

class catsWindowList(QDialog):
	def __init__(self, parent = None):
		super(catsWindowList, self).__init__(parent)
		self.parent = parent

		tree = pBDB.cats.getHier()
		self.cats = pBDB.cats.getAll()

		self.setMinimumWidth(400)
		self.setMinimumHeight(600)

		self.tree = QTreeView(self)
		layout = QHBoxLayout(self)
		layout.addWidget(self.tree)

		root_model = QStandardItemModel()
		self.tree.setModel(root_model)
		self._populateTree(tree, root_model.invisibleRootItem())
		self.tree.expandAll()

		#hheader = QHeaderView(Qt.Orientation.Horizontal)
		self.tree.setHeaderHidden(True)
		#self.tree.setHorizontalHeaderLabels(["Categories"])

		#folderTree.itemClicked.connect( lambda : printer( folderTree.currentItem() ) )

	def _populateTree(self, children, parent):
		for child in cats_alphabetical(self.cats, children):
			child_item = QStandardItem(catString(self.cats, child))
			parent.appendRow(child_item)
			self._populateTree(children[child], child_item)
