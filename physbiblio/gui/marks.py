import sys
from PySide.QtCore import *
from PySide.QtGui  import *
try:
	if sys.version_info[0] < 3:
		import physbiblio.gui.Resources_pyside
	else:
		import physbiblio.gui.Resources_pyside3
except ImportError:
	print("Missing Resources_pyside: Run script update_resources.sh")

class marks():
	def __init__(self):
		self.marks = {}
		self.newMark("imp", "Important", "emblem-important-symbolic")
		self.newMark("fav", "Favorite", "emblem-favorite-symbolic")
		self.newMark("bad", "Bad", "emblem-remove")
		self.newMark("que", "Unclear", "emblem-question")
		self.newMark("new", "To be read", "unread-new")

	def newMark(self, key, desc, icon):
		self.marks[key] = {"desc": desc, "icon": ":/images/%s.png"%icon}

	def getGroupbox(self, marksData, description = "Marks", radio= False, addAny = False):
		groupBox = QGroupBox(description)
		markValues = {}
		groupBox.setFlat(True)
		vbox = QHBoxLayout()
		for m, cont in self.marks.items():
			if radio:
				markValues[m] = QRadioButton(cont["desc"])
			else:
				markValues[m] = QCheckBox(cont["desc"])
			if marksData is not None and m in marksData:
				markValues[m].setChecked(True)
			vbox.addWidget(markValues[m])
		if addAny:
			markValues["any"] = QRadioButton("Any")
			vbox.addWidget(markValues["any"])
		# vbox.addStretch(1)
		groupBox.setLayout(vbox)
		return groupBox, markValues

pBMarks = marks()
