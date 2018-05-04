#!/usr/bin/env python

import sys, time
import os
from PySide.QtCore import *
from PySide.QtGui  import *

try:
	from physbiblio.config import pbConfig
	from physbiblio.database import *
	from physbiblio.gui.ErrorManager import pBGUILogger
	from physbiblio.gui.DialogWindows import *
	from physbiblio.gui.CommonClasses import *
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")

def editProf(parent, statusBarObject):
	oldOrder = pbConfig.profileOrder
	newProfWin = editProfile(parent)
	newProfWin.exec_()
	data = {}
	if newProfWin.result:
		newProfiles = {}
		for currEl in newProfWin.elements:
			name = currEl["n"].text()
			fileName = currEl["f"].text()
			if currEl["r"].isChecked() and name != "":
				pbConfig.profilesDb.setDefaultProfile(name)
			if name in pbConfig.profiles.keys():
				pbConfig.profilesDb.updateProfileField(name, "description", currEl["d"].text())
				if currEl["x"].isChecked() and \
						askYesNo("Do you really want to cancel the profile '%s'?\nThe action cannot be undone!\nThe corresponding database will not be erased."%name):
					pbConfig.profilesDb.deleteProfile(name)
			elif fileName in [pbConfig.profiles[k]["db"].split(os.sep)[-1] for k in pbConfig.profiles.keys()]:
				pbConfig.profilesDb.updateProfileField(fileName, "name", name, identifier = "databasefile")
				pbConfig.profilesDb.updateProfileField(name, "description", currEl["d"].text())
				if currEl["x"].isChecked() and \
						askYesNo("Do you really want to cancel the profile '%s'?\nThe action cannot be undone!\nThe corresponding database will not be erased."%name):
					pbConfig.profilesDb.deleteProfile(name)
			else:
				if name.strip() != "":
					pbConfig.profilesDb.createProfile(
						name = name,
						description = currEl["d"].text(),
						databasefile = (currEl["f"].text().split(os.sep)[-1] + ".db").replace(".db.db", ".db"),
						)
					pBGUILogger.info("New profile created.")
		pbConfig.profilesDb.setProfileOrder([e["n"].text() for e in newProfWin.elements if e["n"].text() != ""])
		pbConfig.loadProfiles()
	else:
		pbConfig.profileOrder = oldOrder
		message = "No modifications"
	try:
		statusBarObject.StatusBarMessage(message)
	except:
		pass

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
		prof, desc = self.combo.currentText().split(" -- ")
		newProfile = pbConfig.profiles[prof]
		if newProfile != pbConfig.defaultProfileName:
			print("[config] Changing profile...")
			pbConfig.reInit(prof, newProfile)
			pBDB.reOpenDB(pbConfig.currentDatabase)

		self.parent.reloadConfig()
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
			["%s -- %s"%(p, pbConfig.profiles[p]["d"]) for p in pbConfig.profileOrder],
			current = "%s -- %s"%(pbConfig.currentProfileName, pbConfig.currentProfile["d"]))
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

		self.setLayout(grid)

		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

class myOrderPushButton(QPushButton):
	def __init__(self, parent, data, icon, text):
		QPushButton.__init__(self, icon, text)
		self.data = data
		self.parent = parent
		self.clicked.connect(self.onClick)

	def onClick(self):
		self.parent.switchLines(self.data)

class editProfile(editObjectWindow):
	"""create a window for editing or creating a profile"""

	def __init__(self, parent = None):
		super(editProfile, self).__init__(parent)
		self.createForm()

	def addButtons(self, profilesData = pbConfig.profiles, profileOrder = pbConfig.profileOrder, defaultProfile = pbConfig.defaultProfileName):
		self.def_group = QButtonGroup(self.currGrid)
		self.elements = []
		self.arrows = []
		i = 0
		j = 0
		for k in profileOrder:
			prof = profilesData[k]
			i += 1
			tempEl = {}
			tempEl["r"] = QRadioButton("")
			self.def_group.addButton(tempEl["r"])
			if defaultProfile == k or ("r" in prof.keys() and prof["r"]):
				tempEl["r"].setChecked(True)
			else:
				tempEl["r"].setChecked(False)
			self.currGrid.addWidget(tempEl["r"], i, 0)

			tempEl["n"] = QLineEdit(k)
			tempEl["f"] = QLineEdit(prof["db"].split(os.sep)[-1])
			tempEl["f"].setReadOnly(True)
			tempEl["d"] = QLineEdit(prof["d"])
			self.currGrid.addWidget(tempEl["n"], i, 1)
			self.currGrid.addWidget(tempEl["f"], i, 2)
			self.currGrid.addWidget(tempEl["d"], i, 3)
			tempEl["x"] = QCheckBox("", self)
			if "x" in prof.keys() and prof["x"]:
				tempEl["x"].setChecked(True)
			self.currGrid.addWidget(tempEl["x"], i, 4)
			if i > 1:
				self.arrows.append([
					myOrderPushButton(self, j, QPixmap(":/images/arrow-down.png").scaledToHeight(48), ""),
					myOrderPushButton(self, j, QPixmap(":/images/arrow-up.png").scaledToHeight(48), "")])
				self.currGrid.addWidget(self.arrows[j][0], i-1, 6)
				self.currGrid.addWidget(self.arrows[j][1], i, 5)
				j += 1
			self.elements.append(tempEl)

	def createForm(self, profilesData = pbConfig.profiles, profileOrder = pbConfig.profileOrder, newLine = {"r": False, "n": "", "db": "", "d": ""}):
		self.setWindowTitle('Edit profile')

		labels = [ QLabel("Default"), QLabel("Short name"), QLabel("Filename"), QLabel("Description"), QLabel("Delete?") ]
		for i,e in enumerate(labels):
			self.currGrid.addWidget(e, 0, i)

		self.addButtons(profilesData, profileOrder)

		i = len(pbConfig.profiles) + 2
		tempEl = {}
		self.currGrid.addWidget(QLabel("Add new?"), i-1, 0)
		tempEl["r"] = QRadioButton("")
		self.def_group.addButton(tempEl["r"])
		if newLine["r"]:
			tempEl["r"].setChecked(True)
		else:
			tempEl["r"].setChecked(False)
		self.currGrid.addWidget(tempEl["r"], i, 0)

		tempEl["n"] = QLineEdit(newLine["n"])
		tempEl["f"] = QLineEdit(newLine["db"])
		tempEl["d"] = QLineEdit(newLine["d"])
		self.currGrid.addWidget(tempEl["n"], i, 1)
		self.currGrid.addWidget(tempEl["f"], i, 2)
		self.currGrid.addWidget(tempEl["d"], i, 3)
		self.elements.append(tempEl)

		# OK button
		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		self.currGrid.addWidget(self.acceptButton, i+1, 1)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		self.currGrid.addWidget(self.cancelButton, i+1, 0)

	def switchLines(self, ix):
		currentValues = {}
		currentOrder = []
		for el in self.elements[:len(pbConfig.profiles)]:
			tmp = {}
			tmp["f"] = el["db"].text()
			tmp["d"] = el["d"].text()
			tmp["r"] = el["r"].isChecked()
			tmp["x"] = el["x"].isChecked()
			currentValues[el["n"].text()] = tmp
			currentOrder.append(el["n"].text())
		newLine = {
			"r": self.elements[-1]["r"].isChecked(),
			"n": self.elements[-1]["n"].text(),
			"db": self.elements[-1]["f"].text(),
			"d": self.elements[-1]["d"].text(),
		}
		tempOrder = list(currentOrder)
		tempOrder[ix] = currentOrder[ix+1]
		tempOrder[ix+1] = currentOrder[ix]
		self.cleanLayout()
		self.createForm(currentValues, tempOrder, newLine)

	def cleanLayout(self):
		"""delete previous table widget"""
		while True:
			o = self.layout().takeAt(0)
			if o is None: break
			o.widget().deleteLater()
