import sys
from PySide2.QtWidgets import QCheckBox, QGroupBox, QHBoxLayout, QRadioButton
try:
	import physbiblio.gui.Resources_pyside2
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")

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

	def getGroupbox(self, marksData, description = "Marks", radio = False, addAny = False):
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
