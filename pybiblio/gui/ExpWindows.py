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
	from pybiblio.gui.DialogWindows import *
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
		self.setWindowTitle('List of experiments')
		self.parent = parent

		#table dimensions
		self.colcnt = len(pBDB.tableCols["experiments"])
		self.colContents = []
		for j in range(self.colcnt):
			self.colContents.append(pBDB.tableCols["experiments"][j])
		self.colContents.append("modify")
		self.colContents.append("delete")
		self.tableWidth = None

		self.currLayout = QHBoxLayout()
		self.setLayout(self.currLayout)

		self.createTable()

	def createTable(self):
		exps = pBDB.exps.getAll()
		rowcnt = len(exps)

		#table settings and header
		self.tablewidget = QTableWidget(rowcnt, self.colcnt+2)
		vheader = QHeaderView(Qt.Orientation.Vertical)
		vheader.setResizeMode(QHeaderView.Interactive)
		self.tablewidget.setVerticalHeader(vheader)
		hheader = QHeaderView(Qt.Orientation.Horizontal)
		hheader.setResizeMode(QHeaderView.Interactive)
		self.tablewidget.setHorizontalHeader(hheader)
		self.tablewidget.setHorizontalHeaderLabels(pBDB.tableCols["experiments"]+["Modify","Delete"])

		#table content
		for i in range(rowcnt):
			for j in range(self.colcnt):
				if j == self.colcnt-1:
					item = QTableWidgetItem(
						("http://inspirehep.net/record/" + str(exps[i][pBDB.tableCols["experiments"][j]]) \
						if exps[i][pBDB.tableCols["experiments"][j]] != "" else "") )
				else:
					item = QTableWidgetItem(str(exps[i][pBDB.tableCols["experiments"][j]]))
				self.tablewidget.setItem(i, j, item)
			pic = QPixmap(":/images/edit.png")
			img = QLabel(self)
			img.setPixmap(pic)
			self.tablewidget.setCellWidget(i, self.colcnt, img)
			pic = QPixmap(":/images/delete.png")
			img = QLabel(self)
			img.setPixmap(pic)
			self.tablewidget.setCellWidget(i, self.colcnt+1, img)

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

	def cellClick(self, row, col):
		idExp = self.tablewidget.item(row, 0).text()
		if self.colContents[col] == "modify":
			self.editExperiment(idExp)
		elif self.colContents[col] == "delete":
			name = self.tablewidget.item(row, 1).text()
			self.deleteExperiment(idExp, name)

	def cellDoubleClick(self, row, col):
		idExp = self.tablewidget.item(row, 0).text()
		if self.colContents[col] == "inspire" or self.colContents[col] == "homepage":
			print "will open '%s' "%idExp

	def editExperiment(self, editIdExp = None):
		if editIdExp is not None:
			edit = pBDB.exps.getDictByID(editIdExp)
		else:
			edit = None
		newExpWin = editExp(self, exp = edit)
		newExpWin.exec_()
		data = {}
		if newExpWin.result:
			for k, v in newExpWin.textValues.items():
				s = "%s"%v.text()
				data[k] = s
			print data
			if "idExp" in data.keys():
				print("Updating experiment %s"%data["idExp"])
				pBDB.exps.update(data, data["idExp"])
			else:
				pBDB.exps.insert(data)
			message = "Experiment saved"
			self.recreateTable()
		else:
			message = "No modifications to experiments"
		try:
			self.parent.StatusBarMessage(message)
		except:
			pass

	def deleteExperiment(self, idExp, name):
		if askYesNo("Do you really want to delete this experiment (ID = '%s', name = '%s')?"%(idExp, name)):
			pBDB.exps.delete(int(idExp))
			self.parent.setWindowTitle("PyBiblio*")
			message = "Experiment deleted"
			self.recreateTable()
		else:
			message = "Nothing changed"
		try:
			self.parent.StatusBarMessage(message)
		except:
			pass

	def recreateTable(self):
		o = self.layout().takeAt(0)
		o.widget().deleteLater()
		self.createTable()

class editExp(QDialog):
	"""create a window for editing or creating an experiment"""
	def __init__(self, parent = None, exp = None):
		super(editExp, self).__init__(parent)
		self.textValues = {}
		if exp is None:
			self.data = {}
			for k in pBDB.tableCols["experiments"]:
				self.data[k] = ""
		else:
			self.data = exp
		self.initUI()

	def onCancel(self):
		self.result	= False
		self.close()

	def onOk(self):
		self.result	= True
		self.close()

	def initUI(self):
		self.setWindowTitle('Edit experiment')

		grid = QGridLayout()
		grid.setSpacing(1)

		i = 0
		for k in pBDB.tableCols["experiments"]:
			val = self.data[k]
			if k != "idExp" or (k == "idExp" and self.data[k] != ""):
				i += 1
				grid.addWidget(QLabel(k), i*2-1, 0)
				grid.addWidget(QLabel("(%s)"%pBDB.descriptions["experiments"][k]), i*2-1, 1)
				self.textValues[k] = QLineEdit(str(val))
				if k == "idExp":
					self.textValues[k].setEnabled(False)
				grid.addWidget(self.textValues[k], i*2, 0, 1, 2)

		# OK button
		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		#width = self.acceptButton.fontMetrics().boundingRect('OK').width() + 7
		#self.acceptButton.setMaximumWidth(width)
		grid.addWidget(self.acceptButton, i*2+1, 0)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		#width = self.cancelButton.fontMetrics().boundingRect('Cancel').width() + 7
		#self.cancelButton.setMaximumWidth(width)
		grid.addWidget(self.cancelButton, i*2+1, 1)

		self.setGeometry(100,100,400, 50*i)
		self.setLayout(grid)

		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())
