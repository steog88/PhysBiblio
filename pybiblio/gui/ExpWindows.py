#!/usr/bin/env python

import sys
from PySide.QtCore import *
from PySide.QtGui  import *
import signal

try:
	from pybiblio.database import *
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

class ExpListWindow(QDialog):
	"""create a window for printing the list of experiments"""
	def __init__(self, parent = None):
		super(ExpListWindow, self).__init__(parent)

		#table dimensions
		colcnt = len(pBDB.tableCols["experiments"])
		exps = pBDB.exps.getAll()
		rowcnt = len(exps)
		
		#table settings and header
		self.tablewidget = QTableWidget(rowcnt, colcnt)
		vheader = QHeaderView(Qt.Orientation.Vertical)
		vheader.setResizeMode(QHeaderView.ResizeToContents)
		self.tablewidget.setVerticalHeader(vheader)
		hheader = QHeaderView(Qt.Orientation.Horizontal)
		hheader.setResizeMode(QHeaderView.ResizeToContents)
		self.tablewidget.setHorizontalHeader(hheader)
		self.tablewidget.setHorizontalHeaderLabels(pBDB.tableCols["experiments"])
		
		#table content
		for i in range(rowcnt):
			for j in range(colcnt):
				item = QTableWidgetItem(str(exps[i][pBDB.tableCols["experiments"][j]]))
				self.tablewidget.setItem(i, j, item)

		layout = QHBoxLayout()
		layout.addWidget(self.tablewidget)
		self.setLayout(layout)
		
		self.setWindowTitle('List of experiments')

		availableWidth		= QDesktopWidget().availableGeometry().width()
		availableHeight		= QDesktopWidget().availableGeometry().height() 
		self.setGeometry(0, 0, availableWidth, availableHeight)

		#qr = self.frameGeometry()
		#cp = QDesktopWidget().availableGeometry().center()
		#qr.moveCenter(cp)
		#self.move(qr.topLeft())
