#!/usr/bin/env python

import sys, time
from PySide.QtCore import *
from PySide.QtGui  import *

try:
	from pybiblio.config import pbConfig
	from pybiblio.database import *
	from pybiblio.gui.DialogWindows import *
	from pybiblio.gui.CommonClasses import *
except ImportError:
	print("Could not find pybiblio and its contents: configure your PYTHONPATH!")

class selectProfiles(QDialog):
	def __init__(self, parent = None, message = None):
		super(selectProfiles, self).__init__(parent)
		self.parent = parent
		self.message = message
		self.initUI()
	
	def onCancel(self):
		self.result	= False
		self.close()

	def onLoad(self):
		newProfile = "data/%s"%self.combo.currentText()
		if newProfile != pbConfig.configMainFile:
			pbConfig.reInit(newProfile)
			pBDB.reOpenDB(pbConfig.params['mainDatabaseName'])
		self.parent.reloadMainContent()
		self.close()

	def initUI(self):
		self.setWindowTitle('Select profile')

		grid = QGridLayout()
		grid.setSpacing(1)

		i = 0
		if self.message is not None:
			grid.addWidget(QLabel("%s"%self.message), 0, 0)
			i += 1

		grid.addWidget(QLabel("Available profiles: "), i, 0)
		self.combo = MyComboBox(self,
			[p.replace("data/", "") for p in pbConfig.profiles],
			current = pbConfig.configMainFile)
		grid.addWidget(self.combo, i, 1)
		i += 1
		
		# cancel button
		self.loadButton = QPushButton('Load', self)
		self.loadButton.clicked.connect(self.onLoad)
		grid.addWidget(self.loadButton, i+1, 0)
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		grid.addWidget(self.cancelButton, i+1, 1)

		#self.setGeometry(100,100,300, 30*i)
		self.setLayout(grid)

		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

class editProfile():
	def __init__(self):
		pass
