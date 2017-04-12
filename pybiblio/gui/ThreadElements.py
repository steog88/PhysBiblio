#!/usr/bin/env python

import sys, time
from PySide.QtCore import *
from PySide.QtGui  import *

try:
	from pybiblio.database import *
	from pybiblio.pdf import pBPDF
	from pybiblio.inspireStats import pBStats
	#import pybiblio.export as bibexport
	#import pybiblio.webimport.webInterf as webInt
	#from pybiblio.cli import cli as pyBiblioCLI
	#from pybiblio.config import pbConfig
	from pybiblio.gui.DialogWindows import *
	#from pybiblio.gui.BibWindows import *
	#from pybiblio.gui.CatWindows import *
	from pybiblio.gui.CommonClasses import *
except ImportError:
	print("Could not find pybiblio and its contents: configure your PYTHONPATH!")

class thread_updateAllBibtexs(MyThread):
	def __init__(self, startFrom, queue, myrec, parent = None):
		super(thread_updateAllBibtexs, self).__init__(parent)
		self.parent = parent
		self.startFrom = startFrom
		self.queue = queue
		self.my_receiver = myrec

	def run(self):
		self.my_receiver.start()
		pBDB.bibs.searchOAIUpdates(self.startFrom)
		time.sleep(0.1)
		self.my_receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBDB.bibs.runningOAIUpdates = False

class thread_downloadArxiv(MyThread):
	def __init__(self, bibkey):
		super(thread_downloadArxiv, self).__init__()
		self.bibkey = bibkey

	def run(self):
		pBPDF.downloadArxiv(self.bibkey)

class thread_authorStats(MyThread):
	def __init__(self, name, queue, myrec, parent = None):
		super(thread_authorStats, self).__init__(parent)
		self.parent = parent
		self.authorName = name
		self.queue = queue
		self.my_receiver = myrec

	def run(self):
		self.my_receiver.start()
		self.parent.lastAuthorStats = pBStats.authorStats(self.authorName)
		time.sleep(0.1)
		self.my_receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBStats.runningAuthorStats = False

class thread_loadAndInsert(MyThread):
	def __init__(self, content, queue, myrec, parent = None):
		super(thread_loadAndInsert, self).__init__(parent)
		self.parent = parent
		self.queue = queue
		self.content = content
		self.my_receiver = myrec

	def run(self):
		self.my_receiver.start()
		loadAndInsert = pBDB.bibs.loadAndInsert(self.content)
		if not loadAndInsert:
			self.parent.loadedAndInserted = []
		else:
			self.parent.loadedAndInserted = pBDB.bibs.lastInserted
		time.sleep(0.1)
		self.my_receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBDB.bibs.runningLoadAndInsert = False
