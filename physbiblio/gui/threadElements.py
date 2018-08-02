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
	Thread that checks if PhysBiblio is updated, using the `outdated` package
	"""
	result = Signal(bool, str)
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
			myrec: the receiver for the text output (a `WriteStream` object)
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
	"""
	Thread that uses `physbiblio.database.entries.updateInfoFromOAI`
	to update the entry record.
	If the inspireID is missing, use `physbiblio.database.entries.updateInspireID`
	to retrieve it.
	"""
	def __init__(self, myrec, bibkey, inspireID = None, parent = None):
		"""
		Initialize the thread and store the required settings

		Parameters:
			myrec: the receiver for the text output (a `WriteStream` object)
			bibkey: the key of the entry to process
			inspireID: the identifier of the entry in the INSPIRE database
			parent: the parent widget
		"""
		super(thread_updateInspireInfo, self).__init__(parent)
		self.bibkey = bibkey
		self.inspireID = inspireID
		self.receiver = myrec

	def run(self):
		"""
		Start the receiver, run `pBDB.bibs.searchOAIUpdates` and finish
		"""
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

class thread_downloadArxiv(MyThread):
	"""
	Use `physbiblio.pdf.localPDF.downloadArxiv`
	to download the article PDF from arXiv.
	A valid arXiv number must be present in the database record for the entry.
	"""
	def __init__(self, bibkey, parent = None):
		"""
		Initialize the object.

		Parameter:
			bibkey: the identifier of the entry in the database
		"""
		super(thread_downloadArxiv, self).__init__(parent)
		self.bibkey = bibkey

	def run(self):
		"""
		Run `physbiblio.pdf.localPDF.downloadArxiv`
		"""
		pBPDF.downloadArxiv(self.bibkey)
		self.finished.emit()

class thread_processLatex(MyThread):
	"""
	Thread the function that processes the presence of maths in the abstracts
	"""
	passData = Signal(list, str)
	def __init__(self, func, parent = None):
		"""
		Instantiate object.

		Parameters:
			func: the function that processes the maths and returns text and images.
				Must be passed as an argument due to the dependencies.
			parent: the parent widget
		"""
		super(thread_processLatex, self).__init__(parent)
		self.func = func

	def run(self):
		"""
		Run the given function, emit a signal passing the output and finish
		"""
		images, text = self.func()
		self.passData.emit(images, text)
		self.finished.emit()

class thread_authorStats(MyThread):
	"""
	Thread using `physbiblio.inspireStats.inspireStatsLoader.authorStats`
	for downloading the author citation statistics
	"""
	def __init__(self, myrec, name, parent):
		"""
		Initialize the object

		Parameters:
			myrec: the receiver for the text output (a `WriteStream` instance)
			name: the author identifier in INSPIRE
			parent: the parent widget. Cannot be None
		"""
		super(thread_authorStats, self).__init__(parent)
		try:
			self.parent().lastAuthorStats = False
		except AttributeError:
			raise Exception("Cannot run thread_authorStats: invalid parent")
		self.authorName = name
		self.receiver = myrec

	def run(self):
		"""
		Start the receiver, run `pBStats.authorStats` and finish
		"""
		self.receiver.start()
		self.parent().lastAuthorStats = pBStats.authorStats(self.authorName)
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBStats.runningAuthorStats = False

class thread_paperStats(MyThread):
	"""
	Thread using `physbiblio.inspireStats.inspireStatsLoader.paperStats`
	for downloading the paper citation statistics
	"""
	def __init__(self, myrec, inspireId, parent):
		"""
		Initialize the object

		Parameters:
			myrec: the receiver for the text output (a `WriteStream` instance)
			inspireId: the paper identifier in INSPIRE
			parent: the parent widget. Cannot be None
		"""
		super(thread_paperStats, self).__init__(parent)
		try:
			self.parent().lastPaperStats = False
		except AttributeError:
			raise Exception("Cannot run thread_paperStats: invalid parent")
		self.inspireId = inspireId
		self.receiver = myrec

	def run(self):
		"""
		Start the receiver, run `pBStats.paperStats` and finish
		"""
		self.receiver.start()
		self.parent().lastPaperStats = pBStats.paperStats(self.inspireId)
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

class thread_loadAndInsert(MyThread):
	"""
	Thread the execution of `pBDB.bibs.loadAndInsert`
	"""
	def __init__(self, myrec, content, parent):
		"""
		Instantiate object.

		Parameters:
			myrec: the receiver for the text output (a `WriteStream` object)
			content: the string to be searched in INSPIRE
			parent: the parent widget. Cannot be None
		"""
		super(thread_loadAndInsert, self).__init__(parent)
		try:
			self.parent().lastAuthorStats = False
		except AttributeError:
			raise Exception("Cannot run thread_loadAndInsert: invalid parent")
		self.content = content
		self.receiver = myrec

	def run(self):
		"""
		Start the receiver, run `pBDB.bibs.loadAndInsert` and finish
		"""
		self.receiver.start()
		loadAndInsert = pBDB.bibs.loadAndInsert(self.content)
		if loadAndInsert is False:
			self.parent().loadedAndInserted = []
		else:
			self.parent().loadedAndInserted = pBDB.bibs.lastInserted
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBDB.bibs.runningLoadAndInsert = False

class thread_cleanAllBibtexs(MyThread):
	"""
	Thread the execution of `physbiblio.database.entries.cleanBibtexs`
	"""
	def __init__(self, myrec, startFrom, parent = None, useEntries = None):
		"""
		Instantiate the object

		Parameters:
			myrec: the receiver for the text output (a `WriteStream` object)
			startFrom: the list index of the object where to start from
				(see `physbiblio.database.entries.cleanBibtexs`)
			parent: the parent widget
			useEntries (optional): the list of entries to be processed
				(see `physbiblio.database.entries.cleanBibtexs`)
		"""
		super(thread_cleanAllBibtexs, self).__init__(parent)
		self.startFrom = startFrom
		self.receiver = myrec
		self.useEntries = useEntries

	def run(self):
		"""
		Start the receiver, run `pBDB.bibs.cleanBibtexs` and finish
		"""
		self.receiver.start()
		pBDB.bibs.cleanBibtexs(self.startFrom, entries = self.useEntries)
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBDB.bibs.runningCleanBibtexs = False

class thread_findBadBibtexs(MyThread):
	"""
	Thread the execution of `physbiblio.database.entries.findCorruptedBibtexs`
	"""
	def __init__(self, myrec, startFrom, parent, useEntries = None):
		"""
		Instantiate the object

		Parameters:
			myrec: the receiver for the text output (a `WriteStream` object)
			startFrom: the list index of the object where to start from
				(see `physbiblio.database.entries.findCorruptedBibtexs`)
			parent: the parent widget. Cannot be None
			useEntries (optional): the list of entries to be processed
				(see `physbiblio.database.entries.findCorruptedBibtexs`)
		"""
		super(thread_findBadBibtexs, self).__init__(parent)
		try:
			self.parent().badBibtexs = False
		except AttributeError:
			raise Exception("Cannot run thread_findBadBibtexs: invalid parent")
		self.startFrom = startFrom
		self.receiver = myrec
		self.useEntries = useEntries

	def run(self):
		"""
		Start the receiver, run `pBDB.bibs.findCorruptedBibtexs` and finish
		"""
		self.receiver.start()
		self.parent().badBibtexs = pBDB.bibs.findCorruptedBibtexs(self.startFrom, entries = self.useEntries)
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBDB.bibs.runningFindBadBibtexs = False

class thread_importFromBib(MyThread):
	"""
	Thread the execution of `physbiblio.database.entries.importFromBib`
	"""
	def __init__(self, myrec, bibFile, complete, parent = None):
		"""
		Instantiate the object

		Parameters:
			myrec: the receiver for the text output (a `WriteStream` object)
			bibFile: the name of the file to import
			complete: complete info online, using INSPIRE
				(see `physbiblio.database.entries.importFromBib`)
			parent: the parent widget
		"""
		super(thread_importFromBib, self).__init__(parent)
		self.bibFile = bibFile
		self.complete = complete
		self.receiver = myrec

	def run(self):
		"""
		Start the receiver, run `pBDB.bibs.importFromBib` and finish
		"""
		self.receiver.start()
		pBDB.bibs.importFromBib(self.bibFile, self.complete)
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBDB.bibs.importFromBibFlag = False

class thread_exportTexBib(MyThread):
	"""
	Thread the execution of `physbiblio.export.pbExport.exportForTexFile`
	"""
	def __init__(self, myrec, texFiles, outFName, parent = None):
		"""
		Instantiate the object

		Parameters:
			myrec: the receiver for the text output (a `WriteStream` object)
			texFiles: a list of '.tex' file names or a single file name
			outFName: the file name of the output '.bib' file
			parent: the parent widget
		"""
		super(thread_exportTexBib, self).__init__(parent)
		self.texFiles = texFiles
		self.outFName = outFName
		self.receiver = myrec

	def run(self):
		"""
		Start the receiver, run `pBExport.exportForTexFile` and finish
		"""
		self.receiver.start()
		pBExport.exportForTexFile(self.texFiles, self.outFName)
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBExport.exportForTexFlag = False

class thread_cleanSpare(MyThread):
	"""
	Thread the execution of `physbiblio.database.utilities.cleanSpareEntries`
	"""
	def __init__(self, myrec, parent):
		"""
		Instantiate the object

		Parameters:
			myrec: the receiver for the text output (a `WriteStream` object)
			parent: the parent widget
		"""
		super(thread_cleanSpare, self).__init__(parent)
		self.receiver = myrec

	def run(self):
		"""
		Start the receiver, run `pBDB.utils.cleanSpareEntries` and finish
		"""
		self.receiver.start()
		pBDB.utils.cleanSpareEntries()
		self.receiver.running = False
		self.finished.emit()

class thread_cleanSparePDF(MyThread):
	"""
	Thread the execution of `physbiblio.pdf.localPDF.removeSparePDFFolders`
	"""
	def __init__(self, myrec, parent = None):
		"""
		Instantiate the object

		Parameters:
			myrec: the receiver for the text output (a `WriteStream` object)
			parent: the parent widget
		"""
		super(thread_cleanSparePDF, self).__init__(parent)
		self.receiver = myrec

	def run(self):
		"""
		Start the receiver, run `pBPDF.removeSparePDFFolders` and finish
		"""
		self.receiver.start()
		pBPDF.removeSparePDFFolders()
		self.receiver.running = False
		self.finished.emit()

class thread_fieldsArxiv(MyThread):
	"""
	Thread the execution of `physbiblio.database.entries.getFieldsFromArxiv`
	"""
	def __init__(self, myrec, entries, fields, parent = None):
		"""
		Instantiate the object

		Parameters:
			myrec: the receiver for the text output (a `WriteStream` object)
			entries: the list of entries or the single entry
				for which the new fields must be added
			fields: the list of fields to be updated from arXiv
			parent: the parent widget
		"""
		super(thread_fieldsArxiv, self).__init__(parent)
		self.entries = entries
		self.fields = fields
		self.receiver = myrec

	def run(self):
		"""
		Start the receiver, run `pBDB.bibs.getFieldsFromArxiv` and finish
		"""
		self.receiver.start()
		pBDB.bibs.getFieldsFromArxiv(self.entries, self.fields)
		time.sleep(0.1)
		self.receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBDB.bibs.getArxivFieldsFlag = False
