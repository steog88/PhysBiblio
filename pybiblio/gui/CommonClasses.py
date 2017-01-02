#!/usr/bin/env python
import sys
from PySide.QtCore import *
from PySide.QtGui  import *

try:
	import pybiblio.gui.Resources_pyside
except ImportError:
	print("Missing Resources_pyside.py: Run script update_resources.sh")

class objListWindow(QDialog):
	"""create a window for printing the list of experiments"""
	def __init__(self, parent = None):
		"""init using parent class and create common definitions"""
		super(objListWindow, self).__init__(parent)
		self.tableWidth = None
		self.currLayout = QHBoxLayout()
		self.setLayout(self.currLayout)

	def setTableSize(self, rows, cols):
		"""set number of rows and columns"""
		self.tablewidget = QTableWidget(rows, cols)
		vheader = QHeaderView(Qt.Orientation.Vertical)
		vheader.setResizeMode(QHeaderView.Interactive)
		self.tablewidget.setVerticalHeader(vheader)
		hheader = QHeaderView(Qt.Orientation.Horizontal)
		hheader.setResizeMode(QHeaderView.Interactive)
		self.tablewidget.setHorizontalHeader(hheader)

	def addEditDeleteCells(self, row, col):
		"""create icons for edit and delete"""
		pic = QPixmap(":/images/edit.png")
		img = QLabel(self)
		img.setPixmap(pic)
		self.tablewidget.setCellWidget(row, col, img)
		pic = QPixmap(":/images/delete.png")
		img = QLabel(self)
		img.setPixmap(pic)
		self.tablewidget.setCellWidget(row, col + 1, img)

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

		self.tablewidget.cellClicked.connect(self.cellClick)
		self.tablewidget.cellDoubleClicked.connect(self.cellDoubleClick)

		self.currLayout.addWidget(self.tablewidget)

	def recreateTable(self):
		"""delete previous table widget and create a new one"""
		o = self.layout().takeAt(0)
		o.widget().deleteLater()
		self.createTable()

class editObjectWindow(QDialog):
	"""create a window for editing or creating an experiment"""
	def __init__(self, parent = None):
		super(editObjectWindow, self).__init__(parent)
		self.textValues = {}
		self.initUI()

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
