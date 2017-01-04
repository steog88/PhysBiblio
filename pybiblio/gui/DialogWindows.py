#!/usr/bin/env python
import sys
from PySide.QtCore import *
from PySide.QtGui  import *
import subprocess

try:
	#from pybiblio.database import *
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

def askYesNo(message, title = ""):
	reply = QMessageBox.question(None, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
	if reply == QMessageBox.Yes:
		return True
	if reply == QMessageBox.No:
		return False

def askFileName(message = "Filename to use:", title = "Enter filename"):
	reply = QInputDialog.getText(None, title, message)
	if reply[1]:
		# user clicked OK
		replyText = reply[0]
	else:
		# user clicked Cancel
		replyText = reply[0] # which will be "" if they clicked Cancel 
	return replyText

def infoMessage(message, title = ""):
	reply = QMessageBox.information(None, title, message)

class configWindow(QDialog):
	"""create a window for editing the configuration settings"""
	def __init__(self, parent = None):
		super(configWindow, self).__init__(parent)
		self.textValues = []
		self.initUI()

	def onCancel(self):
		self.result	= False
		self.close()

	def onOk(self):
		self.result	= True
		self.close()

	def initUI(self):
		self.setWindowTitle('Configuration')

		grid = QGridLayout()
		grid.setSpacing(1)

		i = 0
		for k in pbConfig.paramOrder:
			i += 1
			val = pbConfig.params[k] if type(pbConfig.params[k]) is str else str(pbConfig.params[k])
			grid.addWidget(QLabel("%s (<i>%s</i>)"%(pbConfig.descriptions[k], k)), i-1, 0, 1, 2)
			#grid.addWidget(QLabel("(%s)"%pbConfig.descriptions[k]), i-1, 1)
			self.textValues.append([k, QLineEdit(val)])
			grid.addWidget(self.textValues[i-1][1], i-1, 2, 1, 2)

		# OK button
		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		#width = self.acceptButton.fontMetrics().boundingRect('OK').width() + 7
		#self.acceptButton.setMaximumWidth(width)
		grid.addWidget(self.acceptButton, i, 0)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		#width = self.cancelButton.fontMetrics().boundingRect('Cancel').width() + 7
		#self.cancelButton.setMaximumWidth(width)
		grid.addWidget(self.cancelButton, i, 1)

		self.setGeometry(100,100,1000, 30*i)
		self.setLayout(grid)

		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

class askAction(QDialog):
	"""create a window for asking an action: modify, delete, view...?"""
	def __init__(self, parent = None):
		super(askAction, self).__init__(parent)
		self.message = None
		self.possibleActions = [
			["Modify", self.onModify],
			["Delete", self.onDelete]
			]

	def onCancel(self):
		self.result	= False
		self.close()

	def onModify(self):
		self.result = "modify"
		self.close()

	def onDelete(self):
		self.result = "delete"
		self.close()

	def initUI(self):
		self.setWindowTitle('Select action')

		grid = QGridLayout()
		grid.setSpacing(1)

		i = 0
		if self.message is not None:
			grid.addWidget(QLabel("%s"%self.message), 0, 0)
			i += 1

		for act in self.possibleActions:
			i += 1
			button = QPushButton(act[0], self)
			button.clicked.connect(act[1])
			grid.addWidget(button, i, 0)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		grid.addWidget(self.cancelButton, i+1, 0)

		self.setGeometry(100,100,300, 30*i)
		self.setLayout(grid)

		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())
