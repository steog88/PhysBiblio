#!/usr/bin/env python

import sys, time
from PySide2.QtCore import Signal
from outdated import check_outdated
if sys.version_info[0] < 3:
	from urllib2 import URLError
else:
	from urllib.request import URLError

try:
	from physbiblio import __version__
	from physbiblio.database import *
	from physbiblio.pdf import pBPDF
	from physbiblio.inspireStats import pBStats
	from physbiblio.export import pBExport
	from physbiblio.gui.basicDialogs import *
	from physbiblio.gui.commonClasses import *
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")

class thread_checkUpdated(MyThread):
	"""
	Thread that checks if PhysBiblio is updated, using the `outdated` module
	"""
	result = Signal(bool, str)

	def __init__(self, parent = None):
		"""
		Init the class, extending `MyThread.__init__`

		Parameter:
			parent: the parent widget
		"""
		super(thread_checkUpdated, self).__init__(parent)
		self.parent = parent

	def run(self):
		"""
		Run the thread, using `outdated.check_outdated` and checking for errors
		"""
		try:
			outdated, newVersion = check_outdated('physbiblio', __version__)
			self.result.emit(outdated, newVersion)
		except ValueError:
			pBLogger.warning("Error when executing check_outdated. Maybe you are using a developing version", exc_info = True)
		except URLError:
			pBLogger.warning("Error when trying to check new versions. Are you offline?", exc_info = True)
		self.finished.emit()

class thread_updateAllBibtexs(MyThread):
	"""
	Thread that uses `pBDB.bibs.searchOAIUpdates`
	"""
	def __init__(self, myrec, startFrom,
			parent = None, useEntries = None, force = False, reloadAll = False):
		"""
		Initialize the thread and store the required settings

		Parameters:
			myrec: the receiver for the text (a `WriteStream` object)
			startFrom: the index where to start from the update
				(see `physbiblio.database.entries.searchOAIUpdates`)
			parent: the parent widget
			useEntries: the list of entries that must be updated
				(see `physbiblio.database.entries.searchOAIUpdates`)
			force: force the update of all entries
				(see `physbiblio.database.entries.searchOAIUpdates`)
			reloadAll:  reload the entry completely, without trying to simply update the existing one
				(see `physbiblio.database.entries.searchOAIUpdates`)
		"""
		super(thread_updateAllBibtexs, self).__init__(parent)
		self.parent = parent
		self.startFrom = startFrom
		self.receiver = myrec
		self.useEntries = useEntries
		self.force = force
		self.reloadAll = reloadAll

	def run(self):
		"""
		Start the receiver, run `pBDB.bibs.searchOAIUpdates` and finish
		"""
		self.receiver.start()
		pBDB.bibs.searchOAIUpdates(self.startFrom,
			entries = self.useEntries,
			force = self.force,
			reloadAll = self.reloadAll)
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBDB.bibs.runningOAIUpdates = False

class thread_updateInspireInfo(MyThread):
	def __init__(self, myrec, bibkey, inspireID = None, parent = None):
		super(thread_updateInspireInfo, self).__init__(parent)
		self.parent = parent
		self.bibkey = bibkey
		self.inspireID = inspireID
		self.receiver = myrec

	def run(self):
		self.receiver.start()
		if self.inspireID is None:
			eid = pBDB.bibs.updateInspireID(self.bibkey)
			originalKey = None
		else:
			eid = self.inspireID
			originalKey = self.bibkey
		pBDB.bibs.updateInfoFromOAI(eid, verbose = 1, originalKey = originalKey)
		time.sleep(0.1)
		self.receiver.running = False
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
	def __init__(self, myrec, name, parent = None):
		super(thread_authorStats, self).__init__(parent)
		self.parent = parent
		self.authorName = name
		self.receiver = myrec

	def run(self):
		self.receiver.start()
		self.parent.lastAuthorStats = pBStats.authorStats(self.authorName)
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBStats.runningAuthorStats = False

class thread_paperStats(MyThread):
	def __init__(self, myrec, inspireId, parent = None):
		super(thread_paperStats, self).__init__(parent)
		self.parent = parent
		self.inspireId = inspireId
		self.receiver = myrec

	def run(self):
		self.receiver.start()
		self.parent.lastPaperStats = pBStats.paperStats(self.inspireId)
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

class thread_loadAndInsert(MyThread):
	def __init__(self, myrec, content, parent = None):
		super(thread_loadAndInsert, self).__init__(parent)
		self.parent = parent
		self.content = content
		self.receiver = myrec

	def run(self):
		self.receiver.start()
		loadAndInsert = pBDB.bibs.loadAndInsert(self.content)
		if loadAndInsert is False:
			self.parent.loadedAndInserted = []
		else:
			self.parent.loadedAndInserted = pBDB.bibs.lastInserted
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBDB.bibs.runningLoadAndInsert = False

class thread_cleanAllBibtexs(MyThread):
	def __init__(self, myrec, startFrom, parent = None, useEntries = None):
		super(thread_cleanAllBibtexs, self).__init__(parent)
		self.parent = parent
		self.startFrom = startFrom
		self.receiver = myrec
		self.useEntries = useEntries

	def run(self):
		self.receiver.start()
		pBDB.bibs.cleanBibtexs(self.startFrom, entries = self.useEntries)
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBDB.bibs.runningCleanBibtexs = False

class thread_findBadBibtexs(MyThread):
	def __init__(self, myrec, startFrom, parent = None, useEntries = None):
		super(thread_findBadBibtexs, self).__init__(parent)
		self.parent = parent
		self.startFrom = startFrom
		self.receiver = myrec
		self.useEntries = useEntries

	def run(self):
		self.receiver.start()
		self.parent.badBibtexs = pBDB.bibs.findCorruptedBibtexs(self.startFrom, entries = self.useEntries)
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBDB.bibs.runningFindBadBibtexs = False

class thread_importFromBib(MyThread):
	def __init__(self, myrec, bibFile, complete, parent = None):
		super(thread_importFromBib, self).__init__(parent)
		self.parent = parent
		self.bibFile = bibFile
		self.complete = complete
		self.receiver = myrec

	def run(self):
		self.receiver.start()
		pBDB.bibs.importFromBib(self.bibFile, self.complete)
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBDB.bibs.importFromBibFlag = False

class thread_exportTexBib(MyThread):
	def __init__(self, myrec, texFile, outFName, parent = None):
		super(thread_exportTexBib, self).__init__(parent)
		self.parent = parent
		self.texFile = texFile
		self.outFName = outFName
		self.receiver = myrec

	def run(self):
		self.receiver.start()
		pBExport.exportForTexFile(self.texFile, self.outFName)
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBExport.exportForTexFlag = False

class thread_cleanSpare(MyThread):
	def __init__(self, myrec, parent):
		super(thread_cleanSpare, self).__init__(parent)
		self.parent = parent
		self.receiver = myrec

	def run(self):
		self.receiver.start()
		pBDB.utils.cleanSpareEntries()
		self.receiver.running = False
		self.finished.emit()

class thread_cleanSparePDF(MyThread):
	def __init__(self, myrec, parent):
		super(thread_cleanSparePDF, self).__init__(parent)
		self.parent = parent
		self.receiver = myrec

	def run(self):
		self.receiver.start()
		pBPDF.removeSparePDFFolders()
		self.receiver.running = False
		self.finished.emit()

class thread_fieldsArxiv(MyThread):
	def __init__(self, myrec, entries, fields, parent = None):
		super(thread_fieldsArxiv, self).__init__(parent)
		self.parent = parent
		self.entries = entries
		self.fields = fields
		self.receiver = myrec

	def run(self):
		self.receiver.start()
		pBDB.bibs.getFieldsFromArxiv(self.entries, self.fields)
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBDB.bibs.getArxivFieldsFlag = False
