#!/usr/bin/env python

import sys, time
from PySide.QtCore import *
from PySide.QtGui  import *

try:
	from physbiblio.database import *
	from physbiblio.pdf import pBPDF
	from physbiblio.inspireStats import pBStats
	from physbiblio.export import pBExport
	#import physbiblio.webimport.webInterf as webInt
	#from physbiblio.cli import cli as physBiblioCLI
	#from physbiblio.config import pbConfig
	from physbiblio.gui.DialogWindows import *
	#from physbiblio.gui.BibWindows import *
	#from physbiblio.gui.CatWindows import *
	from physbiblio.gui.CommonClasses import *
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")

class thread_updateAllBibtexs(MyThread):
	def __init__(self, queue, myrec, startFrom, parent = None, useEntries = None, force = False):
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
	def __init__(self, queue, myrec, bibkey, parent = None):
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
	def __init__(self, queue, myrec, name, parent = None):
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
	def __init__(self, queue, myrec, content, parent = None):
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
	def __init__(self, queue, myrec, startFrom, parent = None, useEntries = None):
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
	def __init__(self, queue, myrec, texFile, outFName, parent = None):
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

class thread_cleanSpare(MyThread):
	def __init__(self, queue, myrec, parent):
		super(thread_cleanSpare, self).__init__()
		self.parent = parent
		self.queue = queue
		self.my_receiver = myrec

	def run(self):
		self.my_receiver.start()
		pBDB.utils.cleanSpareEntries()
		self.my_receiver.running = False
		self.finished.emit()

class thread_cleanSparePDF(MyThread):
	def __init__(self, queue, myrec, parent):
		super(thread_cleanSparePDF, self).__init__()
		self.parent = parent
		self.queue = queue
		self.my_receiver = myrec

	def run(self):
		self.my_receiver.start()
		pBPDF.removeSparePDFFolders()
		self.my_receiver.running = False
		self.finished.emit()
