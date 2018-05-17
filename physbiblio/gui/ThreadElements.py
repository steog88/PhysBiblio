#!/usr/bin/env python

import sys, time
from PySide.QtCore import *
from PySide.QtGui  import *
from outdated import check_outdated

try:
	from physbiblio import __version__
	from physbiblio.database import *
	from physbiblio.pdf import pBPDF
	from physbiblio.inspireStats import pBStats
	from physbiblio.export import pBExport
	from physbiblio.gui.DialogWindows import *
	from physbiblio.gui.CommonClasses import *
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")

class thread_checkUpdated(MyThread):
	result = Signal(bool, str)

	def __init__(self, parent = None):
		super(thread_checkUpdated, self).__init__(parent)
		self.parent = parent

	def run(self):
		outdated, newVersion = check_outdated('physbiblio', __version__)
		self.result.emit(outdated, newVersion)
		self.finished.emit()

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
	def __init__(self, bibkey, parent = None):
		super(thread_downloadArxiv, self).__init__(parent)
		self.bibkey = bibkey

	def run(self):
		pBPDF.downloadArxiv(self.bibkey)

class thread_processLatex(MyThread):
	passData = Signal(list, str)
	def __init__(self, func, parent = None):
		super(thread_processLatex, self).__init__(parent)
		self.func = func

	def run(self):
		images, text = self.func()
		self.passData.emit(images, text)

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

class thread_paperStats(MyThread):
	def __init__(self, queue, myrec, inspireId, parent = None):
		super(thread_paperStats, self).__init__(parent)
		self.parent = parent
		self.inspireId = inspireId
		self.queue = queue
		self.my_receiver = myrec

	def run(self):
		self.my_receiver.start()
		self.parent.lastPaperStats = pBStats.paperStats(self.inspireId)
		time.sleep(0.1)
		self.my_receiver.running = False
		self.finished.emit()

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

class thread_importFromBib(MyThread):
	def __init__(self, queue, myrec, bibFile, complete, parent = None):
		super(thread_importFromBib, self).__init__(parent)
		self.parent = parent
		self.bibFile = bibFile
		self.complete = complete
		self.queue = queue
		self.my_receiver = myrec

	def run(self):
		self.my_receiver.start()
		pBDB.bibs.importFromBib(self.bibFile, self.complete)
		time.sleep(0.1)
		self.my_receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBDB.bibs.importFromBibFlag = False

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
		super(thread_cleanSpare, self).__init__(parent)
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
		super(thread_cleanSparePDF, self).__init__(parent)
		self.parent = parent
		self.queue = queue
		self.my_receiver = myrec

	def run(self):
		self.my_receiver.start()
		pBPDF.removeSparePDFFolders()
		self.my_receiver.running = False
		self.finished.emit()

class thread_fieldsArxiv(MyThread):
	def __init__(self, queue, myrec, entries, fields, parent = None):
		super(thread_fieldsArxiv, self).__init__(parent)
		self.parent = parent
		self.entries = entries
		self.fields = fields
		self.queue = queue
		self.my_receiver = myrec

	def run(self):
		self.my_receiver.start()
		pBDB.bibs.getFieldsFromArxiv(self.entries, self.fields)
		time.sleep(0.1)
		self.my_receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBDB.bibs.getArxivFieldsFlag = False
