#!/usr/bin/env python
import sys
from PySide.QtCore import *
from PySide.QtGui  import *

try:
	from pybiblio.errors import pBErrorManager
	import pybiblio.gui.Resources_pyside
	from pybiblio.gui.DialogWindows import *
	from pybiblio.database import catString
except ImportError:
	print("Missing Resources_pyside.py: Run script update_resources.sh")

class pBGUIErrorManager():
	def __init__(self, message, trcbk = None):
		message += "\n"
		infoMessage(message)
		pBErrorManager(message, trcbk)

class objListWindow(QDialog):
	"""create a window for printing the list of experiments"""
	def __init__(self, parent = None):
		"""init using parent class and create common definitions"""
		super(objListWindow, self).__init__(parent)
		self.tableWidth = None
		self.proxyModel = None
		self.currLayout = QVBoxLayout()
		self.setLayout(self.currLayout)

	def triggeredContextMenuEvent(self, row, col, event):
		raise NotImplementedError()

	def cellClick(self, index):
		raise NotImplementedError()

	def cellDoubleClick(self, index):
		raise NotImplementedError()

	def changeFilter(self, string):
		self.proxyModel.setFilterRegExp(str(string))

	def setProxyStuff(self, placeholderText, sortColumn, sortOrder):
		self.filterInput = QLineEdit("",  self)
		self.filterInput.setPlaceholderText(placeholderText)
		self.filterInput.textChanged.connect(self.changeFilter)
		self.currLayout.addWidget(self.filterInput)
		self.filterInput.setFocus()

		self.proxyModel = QSortFilterProxyModel(self)
		self.proxyModel.setSourceModel(self.table_model)
		self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
		self.proxyModel.setSortCaseSensitivity(Qt.CaseInsensitive)
		self.proxyModel.setFilterKeyColumn(-1)

		self.tablewidget = MyTableView(self)
		self.tablewidget.setModel(self.proxyModel)
		self.tablewidget.setSortingEnabled(True)
		self.proxyModel.sort(sortColumn, sortOrder)
		self.currLayout.addWidget(self.tablewidget)

	def finalizeTable(self):
		"""resize the table to fit the contents, connect click and doubleclick functions, add layout"""
		self.tablewidget.resizeColumnsToContents()

		vwidth = self.tablewidget.verticalHeader().width()
		hwidth = self.tablewidget.horizontalHeader().length()
		swidth = self.tablewidget.style().pixelMetric(QStyle.PM_ScrollBarExtent)
		fwidth = self.tablewidget.frameWidth() * 2

		if self.tableWidth is None:
			self.tableWidth = hwidth + swidth + fwidth + 40
		self.tablewidget.setFixedWidth(self.tableWidth)

		self.setMinimumHeight(600)

		self.tablewidget.clicked.connect(self.cellClick)
		self.tablewidget.doubleClicked.connect(self.cellDoubleClick)

		self.currLayout.addWidget(self.tablewidget)

	def cleanLayout(self):
		"""delete previous table widget"""
		while True:
			o = self.layout().takeAt(0)
			if o is None: break
			o.widget().deleteLater()

	def recreateTable(self):
		"""delete previous table widget and create a new one"""
		self.cleanLayout()
		self.createTable()

class editObjectWindow(QDialog):
	"""create a window for editing or creating an experiment"""
	def __init__(self, parent = None):
		super(editObjectWindow, self).__init__(parent)
		self.parent = parent
		self.textValues = {}
		self.initUI()

	def keyPressEvent(self, e):		
		if e.key() == Qt.Key_Escape:
			self.onCancel()

	def onCancel(self):
		self.result	= False
		self.close()

	def onOk(self):
		self.result	= True
		self.close()

	def initUI(self):
		self.currGrid = QGridLayout()
		self.currGrid.setSpacing(1)
		self.setLayout(self.currGrid)

	def centerWindow(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

class MyThread(QThread):
	def __init__(self,  parent = None):
		QThread.__init__(self, parent)

	def run(self):
		pass

	finished = Signal()

class WriteStream(QObject):
    def __init__(self,queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)

class MyReceiver(MyThread):
	mysignal = Signal(str)
	finished = Signal()

	def __init__(self, queue, parent = None, *args, **kwargs):
		super(MyReceiver, self).__init__(parent, *args, **kwargs)
		self.queue = queue
		self.running = True
		self.parent = parent

	def run(self):
		while self.running:
			text = self.queue.get()
			self.mysignal.emit(text)
		self.finished.emit()

class MyComboBox(QComboBox):
	def __init__(self, parent, fields, current = None):
		super(MyComboBox, self).__init__(parent)
		for f in fields:
			self.addItem(f)
		if current is not None:
			try:
				self.setCurrentIndex(fields.index(current))
			except ValueError:
				pass

class MyAndOrCombo(MyComboBox):
	def __init__(self, parent, current = None):
		super(MyAndOrCombo, self).__init__(parent, ["AND", "OR"], current = current)

class MyTableWidget(QTableWidget):
	def __init__(self, rows, cols, parent):
		super(MyTableWidget, self).__init__(rows, cols, parent)
		self.parent = parent

	def contextMenuEvent(self, event):
		self.parent.triggeredContextMenuEvent(self.rowAt(event.y()), self.columnAt(event.x()), event)

class MyTableView(QTableView):
	def __init__(self, parent):
		super(MyTableView, self).__init__(parent)
		self.parent = parent

	def contextMenuEvent(self, event):
		self.parent.triggeredContextMenuEvent(self.rowAt(event.y()), self.columnAt(event.x()), event)

class MyTableModel(QAbstractTableModel):
	def __init__(self, parent, header, ask = False,  previous = [], *args):
		QAbstractTableModel.__init__(self, parent, *args)
		self.header = header
		self.parentObj = parent
		self.previous = previous
		self.ask = ask

	def getIdentifier(self, element):
		raise NotImplementedError()

	def prepareSelected(self):
		self.selectedElements = {}
		for bib in self.dataList:
			self.selectedElements[self.getIdentifier(bib)] = False
		for prevK in self.previous:
			try:
				self.selectedElements[prevK] = True
			except IndexError:
				pBErrorManager("[%s] Invalid identifier in previous selection: %s"%(self.typeClass, prevK))

	def addImage(self, imagePath, height):
		"""create a cell containing an image"""
		return QPixmap(imagePath).scaledToHeight(height)

	def rowCount(self, parent = None):
		return len(self.dataList)

	def columnCount(self, parent = None):
		try:
			return len(self.header)
		except IndexError:
			return 0

	def data(self, index, role):
		raise NotImplementedError()

	def flags(self, index):
		if not index.isValid():
			return None
		if index.column() == 0 and self.ask:
			return Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
		else:
			return Qt.ItemIsEnabled | Qt.ItemIsSelectable

	def headerData(self, col, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return self.header[col]
		return None

	def setData(self, index, value, role):
		raise NotImplementedError()

	def sort(self, col = 1, order = Qt.AscendingOrder):
		"""sort table by given column number col"""
		self.emit(SIGNAL("layoutAboutToBeChanged()"))
		self.dataList = sorted(self.dataList, key=operator.itemgetter(col) )
		if order == Qt.DescendingOrder:
			self.dataList.reverse()
		self.emit(SIGNAL("layoutChanged()"))

#https://www.hardcoded.net/articles/using_qtreeview_with_qabstractitemmodel
class TreeNode(object):
	def __init__(self, parent, row):
		self.parent = parent
		self.row = row
		self.subnodes = self._getChildren()

	def _getChildren(self):
		raise NotImplementedError()

class TreeModel(QAbstractItemModel):
	def __init__(self):
		QAbstractItemModel.__init__(self)
		self.rootNodes = self._getRootNodes()

	def _getRootNodes(self):
		raise NotImplementedError()

	def index(self, row, column, parent):
		if not parent.isValid():
			return self.createIndex(row, column, self.rootNodes[row])
		parentNode = parent.internalPointer()
		return self.createIndex(row, column, parentNode.subnodes[row])

	def parent(self, index):
		if not index.isValid():
			return QModelIndex()
		node = index.internalPointer()
		if node.parent is None:
			return QModelIndex()
		else:
			return self.createIndex(node.parent.row, 0, node.parent)

	def reset(self):
		self.rootNodes = self._getRootNodes()
		QAbstractItemModel.reset(self)

	def rowCount(self, parent):
		if not parent.isValid():
			return len(self.rootNodes)
		node = parent.internalPointer()
		return len(node.subnodes)

class NamedElement(object): # your internal structure
	def __init__(self, idCat, name, subelements):
		self.idCat = idCat
		self.name = name
		self.text = catString(idCat)
		self.subelements = subelements

class NamedNode(TreeNode):
	def __init__(self, ref, parent, row):
		self.ref = ref
		TreeNode.__init__(self, parent, row)

	def _getChildren(self):
		return [NamedNode(elem, self, index)
			for index, elem in enumerate(self.ref.subelements)]

#http://gaganpreet.in/blog/2013/07/04/qtreeview-and-custom-filter-models/
class LeafFilterProxyModel(QSortFilterProxyModel):
	''' Class to override the following behaviour:
			If a parent item doesn't match the filter,
			none of its children will be shown.

		This Model matches items which are descendants
		or ascendants of matching items.
	'''

	def filterAcceptsRow(self, row_num, source_parent):
		''' Overriding the parent function '''

		# Check if the current row matches
		if self.filter_accepts_row_itself(row_num, source_parent):
			return True

		# Traverse up all the way to root and check if any of them match
		if self.filter_accepts_any_parent(source_parent):
			return True

		# Finally, check if any of the children match
		return self.has_accepted_children(row_num, source_parent)

	def filter_accepts_row_itself(self, row_num, parent):
		return super(LeafFilterProxyModel, self).filterAcceptsRow(row_num, parent)

	def filter_accepts_any_parent(self, parent):
		''' Traverse to the root node and check if any of the
			ancestors match the filter
		'''
		while parent.isValid():
			if self.filter_accepts_row_itself(parent.row(), parent.parent()):
				return True
			parent = parent.parent()
		return False

	def has_accepted_children(self, row_num, parent):
		''' Starting from the current node as root, traverse all
			the descendants and test if any of the children match
		'''
		model = self.sourceModel()
		source_index = model.index(row_num, 0, parent)

		children_count =  model.rowCount(source_index)
		for i in xrange(children_count):
			if self.filterAcceptsRow(i, source_index):
				return True
		return False
