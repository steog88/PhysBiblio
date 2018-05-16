#!/usr/bin/env python
import sys
import os
from PySide.QtCore import *
from PySide.QtGui  import *

try:
	from physbiblio.errors import pBErrorManagerClass, pBLogger
	from physbiblio.view import viewEntry
	from physbiblio.pdf import pBPDF
	from physbiblio.gui.DialogWindows import *
	from physbiblio.database import pBDB, catString
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
try:
	if sys.version_info[0] < 3:
		import physbiblio.gui.Resources_pyside
	else:
		import physbiblio.gui.Resources_pyside3
except ImportError:
	print("Missing Resources_pyside.py: Run script update_resources.sh")

class MyLabelRight(QLabel):
	def __init__(self, label):
		super(MyLabelRight, self).__init__(label)
		self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

class MyLabelCenter(QLabel):
	def __init__(self, label):
		super(MyLabelCenter, self).__init__(label)
		self.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

class objListWindow(QDialog):
	"""create a window for printing the list of experiments"""
	def __init__(self, parent = None, gridLayout = False):
		"""init using parent class and create common definitions"""
		super(objListWindow, self).__init__(parent)
		self.tableWidth = None
		self.proxyModel = None
		self.gridLayout = gridLayout
		if gridLayout:
			self.currLayout = QGridLayout()
		else:
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

	def addFilterInput(self, placeholderText):
		self.filterInput = QLineEdit("",  self)
		self.filterInput.setPlaceholderText(placeholderText)
		self.filterInput.textChanged.connect(self.changeFilter)
		self.currLayout.addWidget(self.filterInput)
		self.filterInput.setFocus()

	def setProxyStuff(self, sortColumn, sortOrder):
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

	def finalizeTable(self, gridPos = (1, 0)):
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

		if self.gridLayout:
			self.currLayout.addWidget(self.tablewidget, *gridPos)
		else:
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

	def setStopFlag(self):
		pass

	finished = Signal()

class WriteStream(MyThread):
	mysignal = Signal(str)
	finished = Signal()
	"""class used to redirect the stdout prints to a window"""
	def __init__(self, queue, parent = None, *args, **kwargs):
		super(WriteStream, self).__init__(parent, *args, **kwargs)
		self.queue = queue
		self.running = True
		self.parent = parent

	def write(self, text):
		"""output is sent to window but also copied to real stdout"""
		self.queue.put(text)

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

class MyTrueFalseCombo(MyComboBox):
	def __init__(self, parent, current = None):
		super(MyTrueFalseCombo, self).__init__(parent, ["True", "False"], current = current)

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

	def changeAsk(self, new = None):
		self.emit(SIGNAL("layoutAboutToBeChanged()"))
		if new is None:
			self.ask = not self.ask
		elif new == True or new == False:
			self.ask = new
		self.emit(SIGNAL("layoutChanged()"))

	def getIdentifier(self, element):
		raise NotImplementedError()

	def prepareSelected(self):
		self.emit(SIGNAL("layoutAboutToBeChanged()"))
		self.selectedElements = {}
		for bib in self.dataList:
			self.selectedElements[self.getIdentifier(bib)] = False
		for prevK in self.previous:
			try:
				self.selectedElements[prevK] = True
			except IndexError:
				pBLogger.exception("[%s] Invalid identifier in previous selection: %s"%(self.typeClass, prevK))
		self.emit(SIGNAL("layoutChanged()"))

	def selectAll(self):
		self.emit(SIGNAL("layoutAboutToBeChanged()"))
		for key in self.selectedElements.keys():
			self.selectedElements[key] = True
		self.emit(SIGNAL("layoutChanged()"))

	def unselectAll(self):
		self.emit(SIGNAL("layoutAboutToBeChanged()"))
		for key in self.selectedElements.keys():
			self.selectedElements[key] = False
		self.emit(SIGNAL("layoutChanged()"))

	def addImage(self, imagePath, height):
		"""create a cell containing an image"""
		return QPixmap(imagePath).scaledToHeight(height)

	def addImages(self, imagePaths, outHeight, height = 48):
		"""create a cell containing multiple images"""
		width = len(imagePaths) * height
		pm = QPixmap(width, height)
		pm.fill(Qt.transparent)
		painter = QPainter(pm)
		for i, img in enumerate(imagePaths):
			painter.drawPixmap(i * height, 0, QPixmap(img))
		painter.end()
		return pm.scaledToHeight(outHeight)

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
		self.text = catString(idCat, pBDB)
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
		for i in range(children_count):
			if self.filterAcceptsRow(i, source_index):
				return True
		return False

class MyDDTableWidget(QTableWidget):
	def __init__(self,  header):
		super(MyDDTableWidget, self).__init__()
		self.setColumnCount(1)
		self.setHorizontalHeaderLabels([header])
		self.setDragEnabled(True)
		self.setAcceptDrops(True)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setDragDropOverwriteMode(False)

	# Override this method to get the correct row index for insertion
	def dropMimeData(self, row, col, mimeData, action):
		self.last_drop_row = row
		return True

	def dropEvent(self, event):
		# The QTableWidget from which selected rows will be moved
		sender = event.source()

		# Default dropEvent method fires dropMimeData with appropriate parameters (we're interested in the row index).
		super(MyDDTableWidget, self).dropEvent(event)
		# Now we know where to insert selected row(s)
		dropRow = self.last_drop_row

		selectedRows = sender.getselectedRowsFast()

		# Allocate space for transfer
		for _ in selectedRows:
			self.insertRow(dropRow)

		# if sender == receiver (self), after creating new empty rows selected rows might change their locations
		sel_rows_offsets = [0 if self != sender or srow < dropRow else len(selectedRows) for srow in selectedRows]
		selectedRows = [row + offset for row, offset in zip(selectedRows, sel_rows_offsets)]

		# copy content of selected rows into empty ones
		for i, srow in enumerate(selectedRows):
			for j in range(self.columnCount()):
				item = sender.item(srow, j)
				if item:
					source = QTableWidgetItem(item)
					self.setItem(dropRow + i, j, source)

		# delete selected rows
		for srow in reversed(selectedRows):
			sender.removeRow(srow)

		event.accept()

	def getselectedRowsFast(self):
		selectedRows = []
		for item in self.selectedItems():
			if item.row() not in selectedRows and item.text() != "bibkey":
				selectedRows.append(item.row())
		selectedRows.sort()
		return selectedRows

class MyMenu(QMenu):
	def __init__(self, parent = None):
		super(MyMenu, self).__init__(parent)
		self.possibleActions = []
		self.result = False

	def fillMenu(self):
		for act in self.possibleActions:
			if act is None:
				self.addSeparator()
			else:
				self.addAction(act)

	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Escape:
			self.close()

class guiViewEntry(viewEntry):
	"""
	Extends viewEntry class to work with QtGui.QDesktopServices
	"""
	def __init__(self):
		"""
		Init the class, storing the name of the external web application
		and the base strings to build some links
		"""
		viewEntry.__init__(self)

	def openLink(self, key, arg = "", fileArg = None):
		if type(key) is list:
			for k in key:
				self.openLink(k, arg, fileArg)
		else:
			if arg is "file":
				url = QUrl.fromLocalFile(fileArg)
			elif arg is "link":
				url = QUrl(key)
			else:
				link = self.getLink(key, arg = arg, fileArg = fileArg)
				url = QUrl(link)
			if QDesktopServices.openUrl(url):
				pBLogger.debug("Opening link '%s' for entry '%s' successful!"%(url.toString(), key))
			else:
				pBLogger.warning("Opening link for '%s' failed!"%key)

pBGuiView = guiViewEntry()

class MyImportedTableModel(MyTableModel):
	def __init__(self, parent, biblist, header, *args):
		self.typeClass = "imports"
		self.bibsOrder = [k for k in biblist.keys()]
		self.dataList = [biblist[k]['bibpars'] for k in self.bibsOrder]
		self.existList = [biblist[k]['exist'] for k in self.bibsOrder]
		MyTableModel.__init__(self, parent, header, *args)
		self.prepareSelected()

	def getIdentifier(self, element):
		return element["ID"]

	def data(self, index, role):
		if not index.isValid():
			return None
		row = index.row()
		column = index.column()
		try:
			value = self.dataList[row][self.header[column]]
		except (IndexError, KeyError):
			return None

		if role == Qt.CheckStateRole and column == 0 and self.existList[row] is False:
			if self.selectedElements[self.dataList[row]["ID"]] == False:
				return Qt.Unchecked
			else:
				return Qt.Checked
		if role in [Qt.EditRole, Qt.DisplayRole] and column == 0 and self.existList[row] is True:
			return value + " - already existing"
		if role == Qt.EditRole:
			return value
		if role == Qt.DisplayRole:
			return value
		return None

	def setData(self, index, value, role):
		if role == Qt.CheckStateRole and index.column() == 0:
			if value == Qt.Checked:
				self.selectedElements[self.dataList[index.row()]["ID"]] = True
			else:
				self.selectedElements[self.dataList[index.row()]["ID"]] = False

		self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
		return True

	def flags(self, index):
		if not index.isValid():
			return None
		if index.column() == 0 and self.existList[index.row()] is False:
			return Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
		else:
			return Qt.ItemIsEnabled | Qt.ItemIsSelectable
