"""Module with many classes that are further extended
in the other physbiblio.gui modules.

This file is part of the physbiblio package.
"""
import traceback
import time
from PySide2.QtCore import Qt, Signal, \
	QAbstractItemModel, QAbstractTableModel, QModelIndex, \
	QObject, QSortFilterProxyModel, QThread, QUrl
from PySide2.QtGui import QDesktopServices, QPainter, QPixmap
from PySide2.QtWidgets import \
	QAbstractItemView, QAction, QComboBox, QDesktopWidget, QDialog, \
	QGridLayout, QLabel, QLineEdit, QMenu, QStyle, QTableView, \
	QTableWidget, QTableWidgetItem, QVBoxLayout

try:
	from physbiblio.errors import PBErrorManagerClass, pBLogger
	from physbiblio.view import ViewEntry
	from physbiblio.pdf import pBPDF
	from physbiblio.database import pBDB, catString
	import physbiblio.gui.resourcesPyside2
except ImportError:
	print("Could not find physbiblio and its modules!")
	print(traceback.format_exc())


class PBDialog(QDialog):
	"""Extend QDialog with centerWindow"""

	def centerWindow(self):
		"""Use the `QDesktopWidget` to get the relevant information
		and center the dialog in the screen.
		"""
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())


class PBLabel(QLabel):
	"""Extension of `QLabel` with text interaction flags
	which enable text selection with the mouse
	"""

	def __init__(self, *args, **kwargs):
		"""Extend `QLabel.__init__` and call `setTextInteractionFlags`
		to allow text selection with the mouse
		"""
		QLabel.__init__(self, *args, **kwargs)
		self.setTextFormat(Qt.RichText)
		self.setOpenExternalLinks(True)
		self.setTextInteractionFlags(
			Qt.LinksAccessibleByMouse | Qt.TextSelectableByMouse)


class PBLabelRight(PBLabel):
	"""Class that creates a right-aligned QLabel"""

	def __init__(self, label):
		"""The constructor.

		Parameter:
			label: the text label to be passed to QLabel
		"""
		super(PBLabelRight, self).__init__(label)
		self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)


class PBLabelCenter(PBLabel):
	"""Class that creates a center-aligned QLabel"""

	def __init__(self, label):
		"""The constructor.

		Parameter:
			label: the text label to be passed to QLabel
		"""
		super(PBLabelCenter, self).__init__(label)
		self.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)


class PBComboBox(QComboBox):
	"""Personalize QComboBox for faster construction"""

	def __init__(self, parent, fields, current=None):
		"""Constructor.

		Parameters:
			parent: the parent widget
			fields: the list of (string or printable) contents
				to be added to the QComboBox
			current (default None): the value to be set as the initial value
		"""
		super(PBComboBox, self).__init__(parent)
		for f in fields:
			self.addItem("%s"%f)
		if current is not None:
			try:
				self.setCurrentIndex(fields.index(current))
			except ValueError:
				pass


class PBAndOrCombo(PBComboBox):
	"""Shortcut for generating a QComboBox with and/or"""

	def __init__(self, parent, current=None):
		"""Constructor.

		Parameters:
			parent: the parent widget
			current (default None): the value to be set
				as selected at the beginning
		"""
		super(PBAndOrCombo, self).__init__(parent,
			["AND", "OR"], current=current)


class PBTrueFalseCombo(PBComboBox):
	"""Shortcut for generating a QComboBox with true/false"""

	def __init__(self, parent, current=None):
		"""Constructor.

		Parameters:
			parent: the parent widget
			current (default None): the value to be set as selected
				at the beginning
		"""
		super(PBTrueFalseCombo, self).__init__(parent,
			["True", "False"], current=current)


class ObjListWindow(PBDialog):
	"""Create a window managing a list (of bibtexs or of experiments)"""

	def __init__(self, parent=None, gridLayout=False):
		"""Init using parent class and create common definitions

		Parameters:
			parent: the parent object
			gridLayout (boolean, default False):
				if True, use a QGridLayout, otherwise a QVBoxLayout
		"""
		super(ObjListWindow, self).__init__(parent)
		self.tableWidth = None
		self.proxyModel = None
		self.gridLayout = gridLayout
		if gridLayout:
			self.currLayout = QGridLayout()
		else:
			self.currLayout = QVBoxLayout()
		self.setLayout(self.currLayout)

	def triggeredContextMenuEvent(self, row, col, event):
		"""Not implemented: requires a subclass"""
		raise NotImplementedError()

	def handleItemEntered(self, index):
		"""Not implemented: requires a subclass"""
		raise NotImplementedError()

	def cellClick(self, index):
		"""Not implemented: requires a subclass"""
		raise NotImplementedError()

	def cellDoubleClick(self, index):
		"""Not implemented: requires a subclass"""
		raise NotImplementedError()

	def createTable(self, *args, **kwargs):
		"""Not implemented: requires a subclass"""
		raise NotImplementedError()

	def changeFilter(self, string):
		"""Change the filter of the current view.

		Parameter:
			string: the filter string to be matched
		"""
		self.proxyModel.setFilterRegExp(str(string))

	def addFilterInput(self, placeholderText, gridPos=(1, 0)):
		"""Add a `QLineEdit` to change the filter of the list.

		Parameter:
			placeholderText: the text to be shown
				when no filter is present
			gridPos (tuple): if gridLayout is active,
				the position of the `QLineEdit` in the `QGridLayout`
		"""
		self.filterInput = QLineEdit("", self)
		self.filterInput.setPlaceholderText(placeholderText)
		self.filterInput.textChanged.connect(self.changeFilter)

		if self.gridLayout:
			self.currLayout.addWidget(self.filterInput, *gridPos)
		else:
			self.currLayout.addWidget(self.filterInput)
		self.filterInput.setFocus()

	def setProxyStuff(self, sortColumn, sortOrder):
		"""Prepare the proxy model to filter and sort the view.

		Parameter:
			sortColumn: the index of the column to use
				for sorting at the beginning
			sortOrder: the order for sorting
				(`Qt.AscendingOrder` or `Qt.DescendingOrder`)
		"""
		self.proxyModel = QSortFilterProxyModel(self)
		self.proxyModel.setSourceModel(self.tableModel)
		self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
		self.proxyModel.setSortCaseSensitivity(Qt.CaseInsensitive)
		self.proxyModel.setFilterKeyColumn(-1)

		self.tableview = PBTableView(self)
		self.tableview.setModel(self.proxyModel)
		self.tableview.setSortingEnabled(True)
		self.tableview.setMouseTracking(True)
		self.proxyModel.sort(sortColumn, sortOrder)
		self.currLayout.addWidget(self.tableview)

	def finalizeTable(self, gridPos=(1, 0)):
		"""Resize the table to fit the contents,
		connect functions, add to layout

		Parameter:
			gridPos (tuple): if gridLayout is active,
			the position of the `QLineEdit` in the `QGridLayout`
		"""
		self.tableview.resizeColumnsToContents()

		maxh = QDesktopWidget().availableGeometry().height()
		maxw = QDesktopWidget().availableGeometry().width()
		self.setMaximumHeight(maxh)
		self.setMaximumWidth(maxw)

		hwidth = self.tableview.horizontalHeader().length()
		swidth = self.tableview.style().pixelMetric(QStyle.PM_ScrollBarExtent)
		fwidth = self.tableview.frameWidth() * 2

		if self.tableWidth is None:
			if hwidth > maxw - (swidth + fwidth):
				self.tableWidth = maxw - (swidth + fwidth)
			else:
				self.tableWidth = hwidth + swidth + fwidth
		self.tableview.setFixedWidth(self.tableWidth)

		self.setMinimumHeight(600)

		self.tableview.resizeColumnsToContents()
		self.tableview.resizeRowsToContents()

		self.tableview.entered.connect(self.handleItemEntered)
		self.tableview.clicked.connect(self.cellClick)
		self.tableview.doubleClicked.connect(self.cellDoubleClick)

		if self.gridLayout:
			self.currLayout.addWidget(self.tableview, *gridPos)
		else:
			self.currLayout.addWidget(self.tableview)

	def cleanLayout(self):
		"""Delete the previous table widget and other layout items"""
		while True:
			o = self.layout().takeAt(0)
			if o is None: break
			o.widget().deleteLater()

	def recreateTable(self):
		"""Delete the previous table widget and other layout items,
		then create new ones
		"""
		self.cleanLayout()
		self.createTable()


class EditObjectWindow(PBDialog):
	"""Create a window for editing or creating an experiment"""

	def __init__(self, parent=None):
		"""Constructor.

		Parameter:
			parent: the parent object
		"""
		super(EditObjectWindow, self).__init__(parent)
		self.textValues = {}
		self.initUI()

	def keyPressEvent(self, e):
		"""Intercept press keys and exit if escape is pressed

		Parameters:
			e: the `PySide2.QtGui.QKeyEvent`
		"""
		if e.key() == Qt.Key_Escape:
			self.onCancel()

	def onCancel(self):
		"""Set that the result should not be considered and exit"""
		self.result	= False
		self.close()

	def onOk(self):
		"""Set that the result should be considered and exit"""
		self.result	= True
		self.close()

	def initUI(self):
		"""Instantiate the `QGridLayout`"""
		self.currGrid = QGridLayout()
		self.currGrid.setSpacing(1)
		self.setLayout(self.currGrid)


class PBThread(QThread):
	"""Extend `QThread`, but further extension is needed"""

	finished = Signal()

	def __init__(self, parent=None):
		"""Construct the class using `QThread.__init__`

		Parameters:
			parent: the parent object (default None)
		"""
		QThread.__init__(self, parent)

	def run(self):
		"""Not implemented: requires a subclass"""
		raise NotImplementedError()

	def setStopFlag(self):
		"""Not implemented: requires a subclass"""
		raise NotImplementedError()

	def start(self, *args, **kwargs):
		"""Wait 0.3s and then call `QThread.start`
		(pass all the arguments)
		"""
		time.sleep(0.3)
		QThread.start(self, *args, **kwargs)


class WriteStream(PBThread):
	"""Class used to redirect prints to a window"""

	newText = Signal(str)

	finished = Signal()

	def __init__(self, queue, parent=None, *args, **kwargs):
		"""Constructor

		Parameters:
			queue: a Queue instance
			parent (optional): the parent widget
		"""
		super(WriteStream, self).__init__(parent, *args, **kwargs)
		self.queue = queue
		self.running = True

	def write(self, text):
		"""Write the given text

		Parameters:
			text: the text to send to the output stream
		"""
		self.queue.put(text)

	def run(self):
		"""Run the thread"""
		while self.running:
			text = self.queue.get()
			self.newText.emit(text)
		self.finished.emit()


class PBTableView(QTableView):
	"""Extension of `QTableView`, used to define the contextMenuEvent"""

	def contextMenuEvent(self, event):
		"""Connect the context menu event to the parent function

		Parameter:
			event: the `PySide2.QtGui.QContextMenuEvent`
		"""
		self.parent().triggeredContextMenuEvent(
			self.rowAt(event.y()),
			self.columnAt(event.x()),
			event)


class PBTableModel(QAbstractTableModel):
	"""Extension of `QAbstractTableModel`,
	used for experiments and bibtex entries
	"""

	def __init__(self, parent, header, ask=False, previous=[], *args):
		"""Constructor, based on `QAbstractTableModel.__init__`

		Parameters:
			parent: the parent widget
			header: the list of column names which constitute the table
			ask (boolean, default False):
				when True, allow to select the lines with a checkbox
			previous: the list of lines which must be selected at the beginning
		"""
		QAbstractTableModel.__init__(self, parent, *args)
		self.header = header
		self.parentObj = parent
		self.previous = previous
		self.ask = ask

	def parent(self):
		"""Return the parent object"""
		return self.parentObj

	def changeAsk(self, new=None):
		"""Change the value of `self.ask` to show/hide checkboxes

		Parameters:
			new: `None` to just swap the current value of `self.ask`,
				`True` or `False` to set it to the desired value
		"""
		self.layoutAboutToBeChanged.emit()
		if new is None:
			self.ask = not self.ask
		elif new == True or new == False:
			self.ask = new
		self.layoutChanged.emit()

	def getIdentifier(self, element):
		"""Not implemented: requires a subclass"""
		raise NotImplementedError()

	def prepareSelected(self):
		"""Fill the dictionary `self.selectedElements`
		according to previous selection
		"""
		self.layoutAboutToBeChanged.emit()
		self.selectedElements = {}
		try:
			for bib in self.dataList:
				self.selectedElements[self.getIdentifier(bib)] = False
		except AttributeError:
			pBLogger.exception("dataList is not defined!")
		for prevK in self.previous:
			try:
				if self.selectedElements[prevK] == False:
					self.selectedElements[prevK] = True
			except (KeyError,IndexError):
				pBLogger.exception(
					"Invalid identifier in previous selection: %s"%(prevK))
		self.layoutChanged.emit()

	def selectAll(self):
		"""Select all the available rows"""
		self.layoutAboutToBeChanged.emit()
		for key in self.selectedElements.keys():
			self.selectedElements[key] = True
		self.layoutChanged.emit()

	def unselectAll(self):
		"""Unselect all the available rows"""
		self.layoutAboutToBeChanged.emit()
		for key in self.selectedElements.keys():
			self.selectedElements[key] = False
		self.layoutChanged.emit()

	def addImage(self, imagePath, height):
		"""Create a cell containing an image

		Parameters:
			imagePath: the path of the image
			height: the height to give to the image

		Output:
			a QPixmap
		"""
		return QPixmap(imagePath).scaledToHeight(height)

	def addImages(self, imagePaths, outHeight, height = 48):
		"""Create a cell containing multiple images, using a `QPainter`

		Parameters:
			imagePaths: a list of image paths
				for creating the single `QPixmap`s
			outHeight: the final height for rescaling the image
			height (default 48): the height and width
				to be used when painting

		Output:
			a `QPixmap`
		"""
		width = len(imagePaths) * height
		pm = QPixmap(width, height)
		pm.fill(Qt.transparent)
		self.painter = QPainter(pm)
		for i, img in enumerate(imagePaths):
			self.painter.drawPixmap(i * height, 0, QPixmap(img))
		self.painter.end()
		return pm.scaledToHeight(outHeight)

	def rowCount(self, parent = None):
		"""Count the rows of the given model based on the header

		Parameter:
			parent: `QModelIndex` (required by the parent signature)

		Output:
			the number od rows or zero (if error occurred)
		"""
		try:
			return len(self.dataList)
		except (TypeError, AttributeError):
			return 0

	def columnCount(self, parent = None):
		"""Count the columns of the given model based on the header

		Parameter:
			parent: `QModelIndex` (required by the parent signature)

		Output:
			the number of columns or zero (if error occurred)
		"""
		try:
			return len(self.header)
		except TypeError:
			return 0

	def data(self, index, role):
		"""Not implemented: requires a subclass"""
		raise NotImplementedError()

	def flags(self, index):
		"""Determine the flags of a given item

		Parameter:
			index: a `QModelIndex`

		Output:
			None if the index is not valid
			if `self.ask` and first column, show checkboxes:
			Qt.ItemIsUserCheckable | Qt.ItemIsEditable |
				Qt.ItemIsEnabled | Qt.ItemIsSelectable
			all the other cases: Qt.ItemIsEnabled | Qt.ItemIsSelectable
		"""
		if not index.isValid():
			return None
		if index.column() == 0 and self.ask:
			return Qt.ItemIsUserCheckable | Qt.ItemIsEditable | \
				Qt.ItemIsEnabled | Qt.ItemIsSelectable
		else:
			return Qt.ItemIsEnabled | Qt.ItemIsSelectable

	def headerData(self, col, orientation, role):
		"""Obtain column name if correctly asked

		Parameters:
			col: the column index in `self.header`
			orientation: int from `Qt.Orientation`
			role: int from `Qt.ItemDataRole`

		Output:
			the column name or `None`
		"""
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return self.header[col]
		return None

	def setData(self, index, value, role):
		"""Not implemented: requires a subclass"""
		raise NotImplementedError()

	def sort(self, col=1, order=Qt.AscendingOrder):
		"""Sort table by the given column, number `col`

		Parameters:
			col: the column name
			order: int from `Qt.SortOrder`
		"""
		self.layoutAboutToBeChanged.emit()
		try:
			self.dataList = sorted(self.dataList, key = lambda x: x[col] )
			if order == Qt.DescendingOrder:
				self.dataList.reverse()
		except KeyError:
			pBLogger.warning("Wrong column name in `sort`: '%s'!"%col)
		self.layoutChanged.emit()


#https://www.hardcoded.net/articles/using_qtreeview_with_qabstractitemmodel
class TreeNode(object):
	"""Create an object that will work as a tree node"""

	def __init__(self, parent, row):
		"""Constructor, set basic properties

		Parameters:
			parent: the parent node
			row: the content of the data row
		"""
		self.parentObj = parent
		self.row = row
		self.subnodes = self._getChildren()

	def parent(self):
		"""Return the parent object"""
		return self.parentObj

	def _getChildren(self):
		"""Not implemented: requires a subclass"""
		raise NotImplementedError()


class TreeModel(QAbstractItemModel):
	"""Model for a tree structure."""

	def __init__(self):
		"""Class constructor. Calls `_getRootNodes`
		to build the tree structure
		"""
		QAbstractItemModel.__init__(self)
		self.rootNodes = self._getRootNodes()

	def _getRootNodes(self):
		"""Not implemented: requires a subclass"""
		raise NotImplementedError()

	def index(self, row, column, parent=QModelIndex()):
		"""Retrieve the `QModelIndex` of the requested object

		Parameters:
			row (int): the row index
			column (int): the column index
			parent: the parent `QModelIndex`

		Output:
			A `QModelIndex` instance
		"""
		if not isinstance(parent, QModelIndex):
			pBLogger.debug("Invalid parent '%s' in TreeModel.index"%parent,
				exc_info=True)
			return QModelIndex()
		if not parent.isValid():
			try:
				return self.createIndex(row, column, self.rootNodes[row])
			except IndexError:
				return QModelIndex()
		parentNode = parent.internalPointer()
		try:
			return self.createIndex(row, column, parentNode.subnodes[row])
		except IndexError:
			return QModelIndex()

	def parent(self, index):
		"""Retrieve the `QModelIndex` of the parent of
		the item with the given index, if it exists,
		or an invalid `QModelIndex` instead

		Parameters:
			index: the `QModelIndex` of the node

		Output:
			A `QModelIndex` instance
		"""
		if not isinstance(index, QModelIndex):
			pBLogger.debug("Invalid index '%s' in TreeModel.parent"%index,
				exc_info=True)
			return QModelIndex()
		if not index.isValid():
			return QModelIndex()
		nodeParent = index.internalPointer().parent()
		if nodeParent is None:
			return QModelIndex()
		else:
			return self.createIndex(nodeParent.row, 0, nodeParent)

	def rowCount(self, parent=QModelIndex()):
		"""Count the rows in a given tree branch

		Parameter:
			parent: the `QModelIndex` of the branch parent

		Output:
			the line number
		"""
		if not isinstance(parent, QModelIndex):
			pBLogger.debug("Invalid parent '%s' in TreeModel.rowCount"%parent,
				exc_info=True)
			return len(self.rootNodes)
		if not parent.isValid():
			return len(self.rootNodes)
		node = parent.internalPointer()
		return len(node.subnodes)


class NamedElement(object):
	"""Basic object for the tree structure of categories"""

	def __init__(self, idCat, name, subelements):
		"""Class constructor, set some element properties

		Parameters:
			idCat: the category id
			name: the name of the category
			subelements: the list of children elements
		"""
		self.idCat = idCat
		self.name = name
		self.text = catString(idCat, pBDB)
		self.subelements = subelements


class NamedNode(TreeNode):
	"""Extend `TreeNode` to work with `NamedElement`"""

	def __init__(self, element, parent, row):
		"""Define `self.element` and call `TreeNode.__init__`

		Parameters:
			element: the `NamedElement` of the object
			parent: the parent node
			row: the row index
		"""
		self.element = element
		TreeNode.__init__(self, parent, row)

	def _getChildren(self):
		"""Return a list of `NamedNode`s, containing the children nodes.
		Overrides `TreeNode._getChildren`
		"""
		return [NamedNode(elem, self, index)
			for index, elem in enumerate(self.element.subelements)]


#http://gaganpreet.in/blog/2013/07/04/qtreeview-and-custom-filter-models/
class LeafFilterProxyModel(QSortFilterProxyModel):
	"""Class to override the following behaviour:
		If a parent item doesn't match the filter,
		none of its children will be shown.

	This Model matches items which are descendants
	or ascendants of matching items.
	"""

	def filterAcceptsRow(self, row_num, source_parent):
		"""Overriding the parent function

		Parameters:
			row_num: the row number
			source_parent: the parent node in the tree
		"""
		# Check if the current row matches
		if self.filterAcceptsRowItself(row_num, source_parent):
			return True

		# Traverse up all the way to root and check if any of them match
		if self.filterAcceptsAnyParent(source_parent):
			return True

		# Finally, check if any of the children match
		return self.hasAcceptedChildren(row_num, source_parent)

	def filterAcceptsRowItself(self, row_num, parent):
		"""New name for the original `filterAcceptsRow`,
		which has been overridden

		Parameters:
			row_num: the row number
			parent: the parent node in the tree
		"""
		return super(LeafFilterProxyModel, self).filterAcceptsRow(
			row_num, parent)

	def filterAcceptsAnyParent(self, parent):
		"""Traverse to the root node and check if any of the
		ancestors match the filter

		Parameter:
			parent: the parent node in the tree
		"""
		while parent.isValid():
			if self.filterAcceptsRowItself(parent.row(), parent.parent()):
				return True
			parent = parent.parent()
		return False

	def hasAcceptedChildren(self, row_num, parent):
		"""Starting from the current node as root, traverse all
		the descendants and test if any of the children match

		Parameters:
			row_num: the row number
			parent: the parent node in the tree
		"""
		model = self.sourceModel()
		source_index = model.index(row_num, 0, parent)

		children_count = model.rowCount(source_index)
		for i in range(children_count):
			if self.filterAcceptsRow(i, source_index):
				return True
		return False


class PBDDTableWidget(QTableWidget):
	"""Drag and drop extension of QTableWidget"""

	def __init__(self, parent, header):
		"""Set some properties and settings.

		Parameters:
			header: the title of the column
		"""
		super(PBDDTableWidget, self).__init__(parent)
		self.setColumnCount(1)
		self.setHorizontalHeaderLabels([header])
		self.setDragEnabled(True)
		self.setAcceptDrops(True)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setDragDropOverwriteMode(False)

	# Override this method to get the correct row index for insertion
	def dropMimeData(self, row, col, mimeData, action):
		"""Overridden method to get the row index for insertion

		Parameters:
			row: the index of the dropped row
			col, mimeData, action: not used params
				(see the signature of `QTableWidget.dropMimeData`)
		"""
		self.last_drop_row = row
		return True

	def dropEvent(self, event):
		"""Accept dropEvent and move the selected item
		to the new position

		Parameter:
			event: a `QDropEvent`
		"""
		# The QTableWidget from which selected rows will be moved
		sender = event.source()

		# Default dropEvent method fires dropMimeData
		# with appropriate parameters (we're interested in the row index).
		super(PBDDTableWidget, self).dropEvent(event)
		# Now we know where to insert selected row(s)
		dropRow = self.last_drop_row

		selectedRows = sender.getselectedRowsFast()

		# Allocate space for transfer
		for _ in selectedRows:
			self.insertRow(dropRow)

		# if sender == receiver (self),
		# after creating new empty rows selected rows might change
		# their locations
		sel_rows_offsets = [0 if self != sender or srow < dropRow \
			else len(selectedRows) for srow in selectedRows]
		selectedRows = [row + offset for row, offset \
			in zip(selectedRows, sel_rows_offsets)]

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
		"""Return the list of selected rows

		Output:
			a list with the row indexes of the selected rows
		"""
		selectedRows = []
		for item in self.selectedItems():
			row = item.row()
			text = item.text()
			if row not in selectedRows and text != "bibkey":
				selectedRows.append(row)
		selectedRows.sort()
		return selectedRows


class PBMenu(QMenu):
	"""Extend `QMenu` for faster menu build"""

	def __init__(self, parent=None):
		"""Construct the element defining some basic properties

		Parameter:
			parent: the parent widget
		"""
		super(PBMenu, self).__init__(parent)
		self.possibleActions = []
		self.result = False

	def fillMenu(self):
		"""Add actions, separators or submenus according to the content
		of `self.possibleActions` (recursively for submenus)
		"""
		for act in self.possibleActions:
			if act is None:
				self.addSeparator()
			elif isinstance(act, list):
				submenu = PBMenu()
				submenu.setTitle(act[0])
				submenu.possibleActions = act[1]
				submenu.fillMenu()
				self.addMenu(submenu)
			elif isinstance(act, QAction):
				self.addAction(act)

	def keyPressEvent(self, e):
		"""Intercept press keys and exit if escape is pressed

		Parameters:
			e: the `PySide2.QtGui.QKeyEvent`
		"""
		if e.key() == Qt.Key_Escape:
			self.close()


class GUIViewEntry(ViewEntry):
	"""Extends the ViewEntry class to work with QtGui.QDesktopServices"""

	def openLink(self, key, arg="", fileArg=None):
		"""Use `QDesktopServices` to open an url using
		the system default applications

		Parameters:
			key: the entry key or the link (if `arg` == "link")
			arg:
				if `arg` == "file", `fileArg` must be the file name
				if `arg` == "link", `key` must be the link to be opened
				for any other values, the link will be generated using
					the `physbiblio.view.viewWntry.getLink` method
			fileArg: the file name if `arg` == "file", or
				the argument passed to `physbiblio.view.viewWntry.getLink`
				if needed
		"""
		if isinstance(key, list):
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
				pBLogger.debug("Opening link '%s' for entry '%s' successful!"%(
					url.toString(), key))
			else:
				pBLogger.warning("Opening link for '%s' failed!"%key)


pBGuiView = GUIViewEntry()


class PBImportedTableModel(PBTableModel):
	"""Extend `PBTableModel` to manage the selection
	during the import of entries
	"""

	def __init__(self, parent, bibdict, header, idName="ID", *args):
		"""Set some properties and settings

		Parameters:
			parent: the parent widget (pass to `PBTableModel.__init__`)
			bibdict: a dictionary with the info
				of the imported bibtex entries.
				It should contain dictionaries with two items:
					"bibpars", "exist"
			header: the header names to be passed
				to `PBTableModel.__init__`
			idName: the key of the field representing
				the unique ID of the item
		"""
		self.typeClass = "imports"
		self.idName = idName
		self.bibsOrder = [k for k in bibdict.keys()]
		self.dataList = [bibdict[k]['bibpars'] for k in self.bibsOrder]
		self.existList = [bibdict[k]['exist'] for k in self.bibsOrder]
		PBTableModel.__init__(self, parent, header, *args)
		self.prepareSelected()

	def getIdentifier(self, element):
		"""Return the unique identifier of the given element

		Parameters:
			element: a dictionary
		"""
		return element[self.idName]

	def data(self, index, role):
		"""Return the data for the requested cell and role

		Parameters:
			index: a `QModelIndex`
			role: the requested role for the given cell
		"""
		if not index.isValid():
			return None
		row = index.row()
		column = index.column()
		try:
			value = self.dataList[row][self.header[column]]
		except (IndexError, KeyError):
			pBLogger.warning("Missing element", exc_info=True)
			return None

		if role == Qt.CheckStateRole and column == 0 and \
				self.existList[row] is False:
			if self.selectedElements[self.dataList[row][self.idName]] == False:
				return Qt.Unchecked
			else:
				return Qt.Checked
		if role in [Qt.EditRole, Qt.DisplayRole] and column == 0 \
				and self.existList[row] is True:
			return value + " - already existing"
		if role == Qt.EditRole:
			return value
		if role == Qt.DisplayRole:
			return value
		return None

	def setData(self, index, value, role):
		"""Set the selection data for a given index

		Parameters:
			index: a `QModelIndex`
			value: `Qt.Checked` to set the row as selected
			role: `Qt.CheckStateRole` for performing an action,
				or any other role
		"""
		if not index.isValid():
			return False
		if role == Qt.CheckStateRole and index.column() == 0:
			if value == Qt.Checked:
				self.selectedElements[self.dataList[index.row()][self.idName]] \
					= True
			else:
				self.selectedElements[self.dataList[index.row()][self.idName]] \
					= False
		self.dataChanged.emit(index, index)
		return True

	def flags(self, index):
		"""Return the flags for the requested row

		Parameters:
			index: a `QModelIndex`
		"""
		if not index.isValid():
			return None
		if index.column() == 0 and self.existList[index.row()] is False:
			return Qt.ItemIsUserCheckable | Qt.ItemIsEditable | \
				Qt.ItemIsEnabled | Qt.ItemIsSelectable
		else:
			return Qt.ItemIsEnabled | Qt.ItemIsSelectable


class ObjectWithSignal(QObject):
	"""Being a QObject is necessary to create a signal and use it"""

	customSignal = Signal()
