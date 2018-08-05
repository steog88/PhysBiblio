"""
Module with the classes and functions that enter the profiles management.

This file is part of the physbiblio package.
"""
import sys, time
import os
import glob
import shutil
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QButtonGroup, QCheckBox, QComboBox, QDesktopWidget, QDialog, QGridLayout, QLabel, QLineEdit, QPushButton, QRadioButton

try:
	from physbiblio.config import pbConfig
	from physbiblio.database import *
	from physbiblio.gui.errorManager import pBGUIErrorManager, pBGUILogger
	from physbiblio.gui.basicDialogs import *
	from physbiblio.gui.commonClasses import *
except ImportError:
	print("Could not find physbiblio and its modules!")
	print(traceback.format_exc())

def editProf(parent, statusBarObject, testing = False):
	"""
	Use `editProfile` and process the form output

	Parameters:
		parent: the parent object
		statusBarObject: the object which has the function `StatusBarMessage`
			(a `MainWindow` instance)
		testing: if False, create the `editProfile` instance normally,
			otherwise, use the passed object
	"""
	oldOrder = pbConfig.profileOrder
	if testing is False:
		newProfWin = editProfile(parent)
		newProfWin.exec_()
	else:
		newProfWin = testing
	data = {}
	if newProfWin.result:
		newProfiles = {}
		deleted = []
		for currEl in newProfWin.elements:
			name = currEl["n"].text()
			try:
				fileName = currEl["f"].text()
			except AttributeError:
				fileName = currEl["f"].currentText()
			if currEl["r"].isChecked() and name != "":
				pbConfig.globalDb.setDefaultProfile(name)
			if name in pbConfig.profiles.keys():
				pbConfig.globalDb.updateProfileField(
					name,
					"description",
					currEl["d"].text())
				if currEl["x"].isChecked() and \
						askYesNo("Do you really want to cancel the" +
							" profile '%s'?\n"%name +
							"The action cannot be undone!\n" +
							"The corresponding database will not be erased."):
					pbConfig.globalDb.deleteProfile(name)
					deleted.append(name)
			elif fileName in [pbConfig.profiles[k]["db"].split(os.sep)[-1] \
					for k in pbConfig.profiles.keys()]:
				pbConfig.globalDb.updateProfileField(
					os.path.join(pbConfig.dataPath, fileName),
					"name",
					name,
					identifierField = "databasefile")
				pbConfig.globalDb.updateProfileField(name,
					"description",
					currEl["d"].text())
				if currEl["x"].isChecked() and \
						askYesNo("Do you really want to cancel the " +
							"profile '%s'?\n"%name +
							"The action cannot be undone!\n" +
							"The corresponding database will not be erased."):
					pbConfig.globalDb.deleteProfile(name)
					deleted.append(name)
			else:
				if name.strip() != "":
					newFileName = os.path.join(pbConfig.dataPath,
						(fileName.split(os.sep)[-1] + ".db").replace(
							".db.db", ".db"))
					pbConfig.globalDb.createProfile(
						name = name,
						description = currEl["d"].text(),
						databasefile = newFileName,
						)
					if currEl["c"].currentText() != "None":
						shutil.copy2(os.path.join(pbConfig.dataPath,
							currEl["c"].currentText()), newFileName)
					pBGUIErrorManager.loggerPriority(0).info(
						"New profile created.")
		pbConfig.globalDb.setProfileOrder([e["n"].text() \
			for e in newProfWin.elements \
			if e["n"].text() != "" and e["n"].text() not in deleted])
		pbConfig.loadProfiles()
		message = "Profile management completed"
	else:
		pbConfig.profileOrder = oldOrder
		message = "No modifications"
	try:
		statusBarObject.StatusBarMessage(message)
	except AttributeError:
		pass

class selectProfiles(QDialog):
	"""Widget to change the profile"""
	def __init__(self, parent, message = None):
		"""
		Instantiate the class

		Parameters:
			parent: the parent window (a `MainWindow` instance)
			message: a message used as a description
		"""
		if not hasattr(parent, "reloadConfig"):
			raise Exception("Cannot run selectProfiles: invalid parent")
		super(selectProfiles, self).__init__(parent)
		self.message = message
		self.initUI()
	
	def onCancel(self):
		"""Set result to False and close the window"""
		self.result	= False
		self.close()

	def onLoad(self):
		"""Get current selection and (eventually) load new profile"""
		prof, desc = self.combo.currentText().split(" -- ")
		newProfile = pbConfig.profiles[prof]
		if prof != pbConfig.currentProfileName:
			pBLogger.info("Changing profile...")
			pbConfig.reInit(prof, newProfile)
			pBDB.reOpenDB(pbConfig.currentDatabase)
			self.parent().reloadConfig()
		self.parent().reloadMainContent()
		self.close()

	def initUI(self):
		"""
		Create a `QGridLayout` with the `MyComboBox` and
		the two selection buttons
		"""
		self.setWindowTitle('Select profile')

		grid = QGridLayout()
		grid.setSpacing(10)

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

		# Load and Cancel button
		self.loadButton = QPushButton('Load', self)
		self.loadButton.clicked.connect(self.onLoad)
		grid.addWidget(self.loadButton, i, 0)
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		grid.addWidget(self.cancelButton, i, 1)

		self.setLayout(grid)

class myOrderPushButton(QPushButton):
	"""
	Define a button to switch two form lines
	"""
	def __init__(self, parent, data, icon, text, testing = False):
		"""
		Extend `QPushButton.__init__`

		Parameters:
			parent: the parent object (an `editProfile` instance)
			data: the index of the row that will be switched
			icon: the `QPushButton` icon
			text: the `QPushButton` text
			testing (boolean, default False):
				if True, do not connect the clicked signal
		"""
		QPushButton.__init__(self, icon, text)
		self.data = data
		self.parentObj = parent
		if not testing:
			self.clicked.connect(self.onClick)

	def onClick(self):
		"""Perform the switchLines action"""
		self.parentObj.switchLines(self.data)

	def parent(self):
		"""Return the parent"""
		return self.parentObj

class editProfile(editObjectWindow):
	"""create a window for editing or creating a profile"""
	def __init__(self, parent = None):
		"""Prepare instance and create form"""
		super(editProfile, self).__init__(parent)
		self.createForm()

	def onOk(self):
		"""
		In case "Ok" is pressed, decide if the result is valid:
			* if the name or filename of the new profile are empty, reject;
			* if the name or filename of the new profile are already in use, reject;
			* in all the other cases, accept and close the dialog.
		"""
		if (self.elements[-1]["f"].currentText().strip() != "" and \
					self.elements[-1]["n"].text().strip() == "") \
				or (self.elements[-1]["f"].currentText().strip() == "" and \
					self.elements[-1]["n"].text().strip() != ""):
			pBGUILogger.info("Cannot create a new profile if 'name' or 'filename' is empty.")
			return
		if self.elements[-1]["n"].text().strip() in \
				[a["n"].text() for a in self.elements[:-1]]:
			pBGUILogger.info("Cannot create new profile: 'name' already in use.")
			return
		if (self.elements[-1]["f"].currentText().strip().split(os.sep)[-1] \
				+ ".db").replace(".db.db", ".db") in \
				[a["f"].text().split(os.sep)[-1] for a in self.elements[:-1]]:
			pBGUILogger.info("Cannot create new profile: 'filename' already in use.")
			return
		self.result	= True
		self.close()

	def addButtons(self,
			profilesData = None,
			profileOrder = None,
			defaultProfile = None):
		"""
		...
		"""
		if profilesData is None:
			profilesData = pbConfig.profiles
		if profileOrder is None:
			profileOrder = pbConfig.profileOrder
		if defaultProfile is None:
			defaultProfile = pbConfig.defaultProfileName
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
			if i > 1:
				self.arrows.append([
					myOrderPushButton(self, j, QPixmap(":/images/arrow-down.png").scaledToHeight(48), ""),
					myOrderPushButton(self, j, QPixmap(":/images/arrow-up.png").scaledToHeight(48), "")])
				self.currGrid.addWidget(self.arrows[j][0], i-1, 5)
				self.currGrid.addWidget(self.arrows[j][1], i, 4)
				j += 1
			tempEl["x"] = QCheckBox("", self)
			if "x" in prof.keys() and prof["x"]:
				tempEl["x"].setChecked(True)
			self.currGrid.addWidget(tempEl["x"], i, 6)
			self.elements.append(tempEl)

	def createForm(self,
			profilesData = None,
			profileOrder = None,
			defaultProfile = None,
			newLine = {"r": False, "n": "", "db": "", "d": ""}):
		"""
		...
		"""
		if profilesData is None:
			profilesData = pbConfig.profiles
		if profileOrder is None:
			profileOrder = pbConfig.profileOrder
		if defaultProfile is None:
			defaultProfile = pbConfig.defaultProfileName

		self.setWindowTitle('Edit profile')

		labels = [ QLabel("Default"), QLabel("Short name"), QLabel("Filename"), QLabel("Description") ]
		for i,e in enumerate(labels):
			self.currGrid.addWidget(e, 0, i)
		self.currGrid.addWidget(QLabel("Order"), 0, 4, 1, 2)
		self.currGrid.addWidget(QLabel("Delete?"), 0, 6)

		self.addButtons(profilesData, profileOrder)

		i = len(pbConfig.profiles) + 3
		self.currGrid.addWidget(QLabel(""), i-2, 0)
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
		self.currGrid.addWidget(tempEl["n"], i, 1)

		tempEl["f"] = QComboBox(self)
		tempEl["f"].setEditable(True)
		dbFiles = [f.split(os.sep)[-1] for f in list(glob.iglob(os.path.join(pbConfig.dataPath, "*.db")))]
		registeredDb = [a["db"].split(os.sep)[-1] for a in profilesData.values()]
		tempEl["f"].addItems([newLine["db"]] + [f for f in dbFiles if f not in registeredDb])
		self.currGrid.addWidget(tempEl["f"], i, 2)

		tempEl["d"] = QLineEdit(newLine["d"])
		self.currGrid.addWidget(tempEl["d"], i, 3)

		self.currGrid.addWidget(QLabel("Copy from:"), i, 4, 1, 2)
		tempEl["c"] = QComboBox(self)
		tempEl["c"].addItems(["None"] + registeredDb)
		self.currGrid.addWidget(tempEl["c"], i, 6)

		self.elements.append(tempEl)

		i += 1
		self.currGrid.addWidget(QLabel(""), i, 0)
		# OK button
		self.acceptButton = QPushButton('OK', self)
		self.acceptButton.clicked.connect(self.onOk)
		self.currGrid.addWidget(self.acceptButton, i+1, 1)

		# cancel button
		self.cancelButton = QPushButton('Cancel', self)
		self.cancelButton.clicked.connect(self.onCancel)
		self.cancelButton.setAutoDefault(True)
		self.currGrid.addWidget(self.cancelButton, i+1, 2)

	def switchLines(self, ix):
		"""
		Save the current form content,
		switch the order of the rows as required,
		create a new form with the new order.

		Parameter:
			ix: the index of the first of the two rows involved in the switch
				(e.g., to switch the first and second rows, use ix = 0)
		"""
		currentValues = {}
		currentOrder = []
		for el in self.elements[:len(pbConfig.profiles)]:
			tmp = {}
			tmp["db"] = el["f"].text()
			tmp["d"] = el["d"].text()
			tmp["r"] = el["r"].isChecked()
			tmp["x"] = el["x"].isChecked()
			currentValues[el["n"].text()] = tmp
			currentOrder.append(el["n"].text())
		newLine = {
			"r": self.elements[-1]["r"].isChecked(),
			"n": self.elements[-1]["n"].text(),
			"db": self.elements[-1]["f"].currentText(),
			"d": self.elements[-1]["d"].text(),
		}
		tempOrder = list(currentOrder)
		try:
			tempOrder[ix] = currentOrder[ix+1]
			tempOrder[ix+1] = currentOrder[ix]
		except IndexError:
			pBLogger.warning("Impossible to switch lines: index out of range")
			return False
		self.cleanLayout()
		self.createForm(currentValues, tempOrder, newLine)
		return True

	def cleanLayout(self):
		"""Delete all the existing items in the layout"""
		while True:
			o = self.layout().takeAt(0)
			if o is None: break
			o.widget().deleteLater()
