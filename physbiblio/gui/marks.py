from PySide.QtCore import *
from PySide.QtGui  import *
try:
	import physbiblio.gui.Resources_pyside
except ImportError:
	print("Missing Resources_pyside.py: Run script update_resources.sh")

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

pBMarks = marks()
