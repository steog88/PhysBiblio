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
				pbConfig.defProf = name
			if name in pbConfig.profiles.keys():
				pbConfig.profiles[name]["d"] = currEl["d"].text()
				if currEl["x"].isChecked() and \
						askYesNo("Do you really want to cancel the profile '%s'?\nThe action cannot be undone!\nThe corresponding database will not be erased."%name):
					del pbConfig.profiles[name]
					try:
						os.remove(os.path.join(pbConfig.configPath, currEl["f"].text()))
					except OSError:
						pBGUILogger.warning("Impossible to cancel the profile file %s."%currEl["f"])
			elif fileName in [pbConfig.profiles[k]["f"].split(os.sep)[-1] for k in pbConfig.profiles.keys()]:
				pbConfig.renameProfile(name, fileName)
				pbConfig.profiles[name]["d"] = currEl["d"].text()
				if currEl["x"].isChecked() and \
						askYesNo("Do you really want to cancel the profile '%s'?\nThe action cannot be undone!\nThe corresponding database will not be erased."%name):
					del pbConfig.profiles[name]
					try:
						os.remove(os.path.join(pbConfig.configPath, fileName))
					except OSError:
						pBGUILogger.warning("Impossible to cancel the profile file %s."%fileName)
			else:
				if name.strip() != "":
					pbConfig.profiles[name] = {}
					pbConfig.profiles[name]["d"] = currEl["d"].text()
					fname = currEl["f"].text().split(os.sep)[-1] + ".cfg"
					fname = fname.replace(".cfg.cfg", ".cfg")
					pbConfig.profiles[name]["f"] = fname
					open(os.path.join(pbConfig.configPath, fname), "a").close()
					pBGUILogger.info("New profile created.\nYou should configure it properly before use!\n(switch to it and open the configuration)")
		pbConfig.writeProfiles()
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
		if newProfile != pbConfig.defaultProfile:
			print("[config] Changing profile...")
			pbConfig.reInit(prof, newProfile)
			if pbConfig.needFirstConfiguration:
				infoMessage("Missing configuration file.\nYou should verify the configuration now.")
				self.parent.config()
			pBDB.reOpenDB(pbConfig.params['mainDatabaseName'])

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
			["%s -- %s"%(p, pbConfig.profiles[p]["d"]) for p in pbConfig.profiles.keys()],
			current = "%s -- %s"%(pbConfig.defProf, pbConfig.defaultProfile["d"]))
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

	def addButtons(self, profilesData = pbConfig.profiles, profileOrder = pbConfig.profileOrder):
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
			if pbConfig.defProf == k or ("r" in prof.keys() and prof["r"]):
				tempEl["r"].setChecked(True)
			else:
				tempEl["r"].setChecked(False)
			self.currGrid.addWidget(tempEl["r"], i, 0)

			tempEl["n"] = QLineEdit(k)
			tempEl["f"] = QLineEdit(prof["f"].split(os.sep)[-1])
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

	def createForm(self, profilesData = pbConfig.profiles, profileOrder = pbConfig.profileOrder, newLine = {"r": False, "n": "", "f": "", "d": ""}):
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
		tempEl["f"] = QLineEdit(newLine["f"])
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
			tmp["f"] = el["f"].text()
			tmp["d"] = el["d"].text()
			tmp["r"] = el["r"].isChecked()
			tmp["x"] = el["x"].isChecked()
			currentValues[el["n"].text()] = tmp
			currentOrder.append(el["n"].text())
		newLine = {
			"r": self.elements[-1]["r"].isChecked(),
			"n": self.elements[-1]["n"].text(),
			"f": self.elements[-1]["f"].text(),
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
