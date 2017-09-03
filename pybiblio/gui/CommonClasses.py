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
		pass

	def setTableSize(self, rows, cols):
		"""set number of rows and columns"""
		self.tablewidget = MyTableWidget(rows, cols, self)
		vheader = QHeaderView(Qt.Orientation.Vertical)
		vheader.setResizeMode(QHeaderView.Interactive)
		self.tablewidget.setVerticalHeader(vheader)
		hheader = QHeaderView(Qt.Orientation.Horizontal)
		hheader.setResizeMode(QHeaderView.Interactive)
		self.tablewidget.setHorizontalHeader(hheader)

	def addImageCell(self, row, col, imagePath):
		"""create a cell containing an image"""
		pic = QPixmap(imagePath).scaledToHeight(self.tablewidget.rowHeight(row)*0.8)
		img = QLabel(self)
		img.setPixmap(pic)
		self.tablewidget.setCellWidget(row, col, img)

	def addEditDeleteCells(self, row, col):
		"""create icons for edit and delete"""
		self.addImageCell(row, col, ":/images/edit.png")
		self.addImageCell(row, col + 1, ":/images/delete.png")

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
