#!/usr/bin/env python

import sys, time
from PySide.QtCore import *
from PySide.QtGui  import *

try:
	from pybiblio.database import *
	from pybiblio.pdf import pBPDF
	from pybiblio.inspireStats import pBStats
	from pybiblio.export import pBExport
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
	def __init__(self, startFrom, queue, myrec, parent = None, useEntries = None, force = False):
		super(thread_updateAllBibtexs, self).__init__(parent)
		self.parent = parent
		self.startFrom = startFrom
		self.queue = queue
		self.my_receiver = myrec
		self.useEntries = useEntries
		self.force = force

	def run(self):
		self.my_receiver.start()
		pBDB.bibs.searchOAIUpdates(self.startFrom, entries = self.useEntries, force = self.force)
		time.sleep(0.1)
		self.my_receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBDB.bibs.runningOAIUpdates = False

class thread_updateInspireInfo(MyThread):
	def __init__(self, bibkey, queue, myrec, parent = None):
		super(thread_updateInspireInfo, self).__init__(parent)
		self.parent = parent
		self.bibkey = bibkey
		self.queue = queue
		self.my_receiver = myrec

	def run(self):
		self.my_receiver.start()
		eid = pBDB.bibs.updateInspireID(self.bibkey)
		pBDB.bibs.updateInfoFromOAI(eid, verbose = 1)
		time.sleep(0.1)
		self.my_receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pass

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
		if loadAndInsert is False:
			self.parent.loadedAndInserted = []
		else:
			self.parent.loadedAndInserted = pBDB.bibs.lastInserted
		time.sleep(0.1)
		self.my_receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBDB.bibs.runningLoadAndInsert = False

class thread_cleanAllBibtexs(MyThread):
	def __init__(self, startFrom, queue, myrec, parent = None, useEntries = None):
		super(thread_cleanAllBibtexs, self).__init__(parent)
		self.parent = parent
		self.startFrom = startFrom
		self.queue = queue
		self.my_receiver = myrec
		self.useEntries = useEntries

	def run(self):
		self.my_receiver.start()
		pBDB.bibs.cleanBibtexs(self.startFrom, entries = self.useEntries)
		time.sleep(0.1)
		self.my_receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBDB.bibs.runningCleanBibtexs = False

class thread_exportTexBib(MyThread):
	def __init__(self, texFile, outFName, queue, myrec, parent = None):
		super(thread_exportTexBib, self).__init__(parent)
		self.parent = parent
		self.texFile = texFile
		self.outFName = outFName
		self.queue = queue
		self.my_receiver = myrec

	def run(self):
		self.my_receiver.start()
		pBExport.exportForTexFile(self.texFile, self.outFName)
		time.sleep(0.1)
		self.my_receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBExport.exportForTexFlag = False
