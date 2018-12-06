"""Module with the classes that are used to run threads.

This file is part of the physbiblio package.
"""
import sys
import traceback
import time
from PySide2.QtCore import Signal
from outdated import check_outdated
if sys.version_info[0] < 3:
	from urllib2 import URLError
else:
	from urllib.request import URLError
import bibtexparser

try:
	from physbiblio import __version__
	from physbiblio.errors import pBLogger
	from physbiblio.bibtexWriter import pbWriter
	from physbiblio.database import pBDB
	from physbiblio.pdf import pBPDF
	from physbiblio.inspireStats import pBStats
	from physbiblio.export import pBExport
	from physbiblio.gui.commonClasses import \
		PBThread, WriteStream
except ImportError:
	print("Could not find physbiblio and its modules!")
	print(traceback.format_exc())


class Thread_checkUpdated(PBThread):
	"""Thread that checks if PhysBiblio is updated,
	using the `outdated` package
	"""

	result = Signal(bool, str)

	def run(self):
		"""Run the thread, using `outdated.check_outdated`
		and checking for errors
		"""
		try:
			outdated, newVersion = check_outdated('physbiblio', __version__)
			self.result.emit(outdated, newVersion)
		except ValueError:
			pBLogger.warning("Error when executing check_outdated. "
				+ "Maybe you are using a developing version", exc_info=True)
		except URLError:
			pBLogger.warning("Error when trying to check new versions. "
				+ "Are you offline?", exc_info=True)


class Thread_updateAllBibtexs(PBThread):
	"""Thread that uses `pBDB.bibs.searchOAIUpdates`"""

	def __init__(self,
			receiver,
			startFrom,
			parent=None,
			useEntries=None,
			force=False,
			reloadAll=False):
		"""Initialize the thread and store the required settings

		Parameters:
			receiver: the receiver for the text output (a `WriteStream` object)
			startFrom: the index where to start from the update
				(see `physbiblio.database.Entries.searchOAIUpdates`)
			parent: the parent widget
			useEntries: the list of entries that must be updated
				(see `physbiblio.database.Entries.searchOAIUpdates`)
			force: force the update of all entries
				(see `physbiblio.database.Entries.searchOAIUpdates`)
			reloadAll: reload the entry completely, without trying
				to simply update the existing one
				(see `physbiblio.database.Entries.searchOAIUpdates`)
		"""
		super(Thread_updateAllBibtexs, self).__init__(parent)
		self.startFrom = startFrom
		self.receiver = receiver
		self.useEntries = useEntries
		self.force = force
		self.reloadAll = reloadAll

	def run(self):
		"""Start the receiver,
		run `pBDB.bibs.searchOAIUpdates` and finish
		"""
		self.receiver.start()
		pBDB.bibs.searchOAIUpdates(self.startFrom,
			entries=self.useEntries,
			force=self.force,
			reloadAll=self.reloadAll)
		time.sleep(0.1)
		self.receiver.running = False

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBDB.bibs.runningOAIUpdates = False


class Thread_replace(PBThread):
	"""Thread that uses `pBDB.bibs.replace`"""

	def __init__(self,
			receiver,
			fiOld,
			fiNew,
			old,
			new,
			parent,
			regex=False):
		"""Initialize the thread and store the required settings

		Parameters:
			receiver: the receiver for the text output
				(a `WriteStream` object)
			fiOld: name of the field from where the content is taken
			fiNew (list): names of new fields where
				the replaced content must go
			old: content to replace or match string
			new (list): new content or regex instruction to extract it
			parent: the parent widget
			regex (default False): if True, use regular expressions.
				if False, just do normal string replacement
		"""
		super(Thread_replace, self).__init__(parent)
		self.fiOld = fiOld
		self.fiNew = fiNew
		self.old = old
		self.new = new
		self.receiver = receiver
		self.regex = regex

	def run(self):
		"""Start the receiver,
		run `pBDB.bibs.replace` and finish
		"""
		self.receiver.start()
		pBDB.bibs.fetchFromLast(doFetch=False)
		success, changed, failed = pBDB.bibs.replace(
			self.fiOld, self.fiNew, self.old, self.new,
			entries=pBDB.bibs.fetchCursor(), regex=self.regex,
			lenEntries=len(pBDB.bibs.fetchFromLast().lastFetched))
		self.parent().replaceResults = (success, changed, failed)
		time.sleep(0.1)
		self.receiver.running = False

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBDB.bibs.runningReplace = False


class Thread_updateInspireInfo(PBThread):
	"""Thread that uses `physbiblio.database.Entries.updateInfoFromOAI`
	to update the entry record.
	If the inspireID is missing,
	use `physbiblio.database.Entries.updateInspireID` to retrieve it.
	"""

	def __init__(self, receiver, bibkey, inspireID=None, parent=None):
		"""Initialize the thread and store the required settings

		Parameters:
			receiver: the receiver for the text output
				(a `WriteStream` object)
			bibkey: the key of the entry to process
			inspireID: the identifier of the entry
				in the INSPIRE database
			parent: the parent widget
		"""
		super(Thread_updateInspireInfo, self).__init__(parent)
		self.bibkey = bibkey
		self.inspireID = inspireID
		self.receiver = receiver

	def run(self):
		"""Start the receiver,
		run `pBDB.bibs.searchOAIUpdates` and finish
		"""
		self.receiver.start()
		if isinstance(self.bibkey, list):
			for i, k in enumerate(self.bibkey):
				inspireID = self.inspireID[i]
				if inspireID is None or inspireID == "":
					eid = pBDB.bibs.updateInspireID(k)
					originalKey = None
				else:
					eid = inspireID
					originalKey = k
				pBDB.bibs.updateInfoFromOAI(eid,
					verbose=1, originalKey=originalKey)
		else:
			if self.inspireID is None:
				eid = pBDB.bibs.updateInspireID(self.bibkey)
				originalKey = None
			else:
				eid = self.inspireID
				originalKey = self.bibkey
			pBDB.bibs.updateInfoFromOAI(eid,
				verbose=1, originalKey=originalKey)
		time.sleep(0.1)
		self.receiver.running = False


class Thread_downloadArxiv(PBThread):
	"""Use `physbiblio.pdf.LocalPDF.downloadArxiv`
	to download the article PDF from arXiv.
	A valid arXiv number must be present
	in the database record for the entry.
	"""

	def __init__(self, bibkey, parent=None):
		"""Initialize the object.

		Parameter:
			bibkey: the identifier of the entry in the database
		"""
		super(Thread_downloadArxiv, self).__init__(parent)
		self.bibkey = bibkey

	def run(self):
		"""Run `physbiblio.pdf.LocalPDF.downloadArxiv`"""
		pBPDF.downloadArxiv(self.bibkey)


class Thread_processLatex(PBThread):
	"""Thread the function that processes the presence
	of maths in the abstracts
	"""

	passData = Signal(list, str)

	def __init__(self, func, parent=None):
		"""Instantiate object.

		Parameters:
			func: the function that processes the maths
				and returns text and images.
				Must be passed as an argument due to the dependencies.
			parent: the parent widget
		"""
		super(Thread_processLatex, self).__init__(parent)
		self.func = func

	def run(self):
		"""Run the given function, emit a signal passing
		the output and finish
		"""
		images, text = self.func()
		self.passData.emit(images, text)


class Thread_authorStats(PBThread):
	"""Thread using
	`physbiblio.inspireStats.InspireStatsLoader.authorStats`
	for downloading the author citation statistics
	"""

	def __init__(self, receiver, name, parent):
		"""Initialize the object

		Parameters:
			receiver: the receiver for the text output
				(a `WriteStream` instance)
			name: the author identifier in INSPIRE
			parent: the parent widget. Cannot be None
		"""
		super(Thread_authorStats, self).__init__(parent)
		try:
			self.parent().lastAuthorStats = False
		except AttributeError:
			raise Exception("Cannot run Thread_authorStats: invalid parent")
		self.authorName = name
		self.receiver = receiver

	def run(self):
		"""Start the receiver, run `pBStats.authorStats` and finish"""
		self.receiver.start()
		self.parent().lastAuthorStats = pBStats.authorStats(self.authorName)
		time.sleep(0.1)
		self.receiver.running = False

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBStats.runningAuthorStats = False


class Thread_paperStats(PBThread):
	"""Thread using `physbiblio.inspireStats.InspireStatsLoader.paperStats`
	for downloading the paper citation statistics
	"""

	def __init__(self, receiver, inspireId, parent):
		"""Initialize the object

		Parameters:
			receiver: the receiver for the text output (a `WriteStream` instance)
			inspireId: the paper identifier in INSPIRE
			parent: the parent widget. Cannot be None
		"""
		super(Thread_paperStats, self).__init__(parent)
		try:
			self.parent().lastPaperStats = False
		except AttributeError:
			raise Exception("Cannot run Thread_paperStats: invalid parent")
		self.inspireId = inspireId
		self.receiver = receiver

	def run(self):
		"""Start the receiver, run `pBStats.paperStats` and finish"""
		self.receiver.start()
		self.parent().lastPaperStats = pBStats.paperStats(self.inspireId)
		time.sleep(0.1)
		self.receiver.running = False


class Thread_loadAndInsert(PBThread):
	"""Thread the execution of `pBDB.bibs.loadAndInsert`"""

	def __init__(self, receiver, content, parent):
		"""Instantiate object.

		Parameters:
			receiver: the receiver for the text output (a `WriteStream` object)
			content: the string to be searched in INSPIRE
			parent: the parent widget. Cannot be None
		"""
		super(Thread_loadAndInsert, self).__init__(parent)
		try:
			self.parent().lastAuthorStats = False
		except AttributeError:
			raise Exception("Cannot run Thread_loadAndInsert: invalid parent")
		self.content = content
		self.receiver = receiver

	def run(self):
		"""Start the receiver, run `pBDB.bibs.loadAndInsert` and finish"""
		self.receiver.start()
		loadAndInsert = pBDB.bibs.loadAndInsert(self.content)
		if loadAndInsert is False:
			self.parent().loadedAndInserted = []
		else:
			self.parent().loadedAndInserted = pBDB.bibs.lastInserted
		time.sleep(0.1)
		self.receiver.running = False

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBDB.bibs.runningLoadAndInsert = False


class Thread_cleanAllBibtexs(PBThread):
	"""Thread the execution
	of `physbiblio.database.Entries.cleanBibtexs`
	"""

	def __init__(self, receiver, startFrom, parent=None, useEntries=None):
		"""Instantiate the object

		Parameters:
			receiver: the receiver for the text output
				(a `WriteStream` object)
			startFrom: the list index of the object where to start from
				(see `physbiblio.database.Entries.cleanBibtexs`)
			parent: the parent widget
			useEntries (optional): the list of entries to be processed
				(see `physbiblio.database.Entries.cleanBibtexs`)
		"""
		super(Thread_cleanAllBibtexs, self).__init__(parent)
		self.startFrom = startFrom
		self.receiver = receiver
		self.useEntries = useEntries

	def run(self):
		"""Start the receiver, run `pBDB.bibs.cleanBibtexs` and finish"""
		self.receiver.start()
		pBDB.bibs.cleanBibtexs(self.startFrom, entries=self.useEntries)
		time.sleep(0.1)
		self.receiver.running = False

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBDB.bibs.runningCleanBibtexs = False


class Thread_findBadBibtexs(PBThread):
	"""Thread the execution of
	`physbiblio.database.Entries.findCorruptedBibtexs`
	"""

	def __init__(self, receiver, startFrom, parent, useEntries=None):
		"""Instantiate the object

		Parameters:
			receiver: the receiver for the text output
				(a `WriteStream` object)
			startFrom: the list index of the object where to start from
				(see `physbiblio.database.Entries.findCorruptedBibtexs`)
			parent: the parent widget. Cannot be None
			useEntries (optional): the list of entries to be processed
				(see `physbiblio.database.Entries.findCorruptedBibtexs`)
		"""
		super(Thread_findBadBibtexs, self).__init__(parent)
		try:
			self.parent().badBibtexs = False
		except AttributeError:
			raise Exception(
				"Cannot run Thread_findBadBibtexs: invalid parent")
		self.startFrom = startFrom
		self.receiver = receiver
		self.useEntries = useEntries

	def run(self):
		"""Start the receiver,
		run `pBDB.bibs.findCorruptedBibtexs` and finish
		"""
		self.receiver.start()
		self.parent().badBibtexs = pBDB.bibs.findCorruptedBibtexs(
			self.startFrom, entries=self.useEntries)
		time.sleep(0.1)
		self.receiver.running = False

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBDB.bibs.runningFindBadBibtexs = False


class Thread_importFromBib(PBThread):
	"""Thread the execution of
	`physbiblio.database.Entries.importFromBib`
	"""

	def __init__(self, receiver, bibFile, complete, parent=None):
		"""Instantiate the object

		Parameters:
			receiver: the receiver for the text output
				(a `WriteStream` object)
			bibFile: the name of the file to import
			complete: complete info online, using INSPIRE
				(see `physbiblio.database.Entries.importFromBib`)
			parent: the parent widget
		"""
		super(Thread_importFromBib, self).__init__(parent)
		self.bibFile = bibFile
		self.complete = complete
		self.receiver = receiver

	def run(self):
		"""Start the receiver,
		run `pBDB.bibs.importFromBib` and finish
		"""
		self.receiver.start()
		pBDB.bibs.importFromBib(self.bibFile, self.complete)
		time.sleep(0.1)
		self.receiver.running = False

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBDB.bibs.importFromBibFlag = False


class Thread_exportTexBib(PBThread):
	"""Thread the execution of
	`physbiblio.export.PBExport.exportForTexFile`
	"""

	def __init__(self, receiver, texFiles, outFName, parent=None):
		"""Instantiate the object

		Parameters:
			receiver: the receiver for the text output
				(a `WriteStream` object)
			texFiles: a list of '.tex' file names or a single file name
			outFName: the file name of the output '.bib' file
			parent: the parent widget
		"""
		super(Thread_exportTexBib, self).__init__(parent)
		self.texFiles = texFiles
		self.outFName = outFName
		self.receiver = receiver

	def run(self):
		"""Start the receiver,
		run `pBExport.exportForTexFile` and finish
		"""
		self.receiver.start()
		pBExport.exportForTexFile(self.texFiles, self.outFName)
		time.sleep(0.1)
		self.receiver.running = False

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBExport.exportForTexFlag = False


class Thread_cleanSpare(PBThread):
	"""Thread the execution of
	`physbiblio.database.Utilities.cleanSpareEntries`
	"""

	def __init__(self, receiver, parent):
		"""Instantiate the object

		Parameters:
			receiver: the receiver for the text output
				(a `WriteStream` object)
			parent: the parent widget
		"""
		PBThread.__init__(self, parent)
		self.receiver = receiver

	def run(self):
		"""Start the receiver,
		run `pBDB.utils.cleanSpareEntries` and finish
		"""
		self.receiver.start()
		pBDB.utils.cleanSpareEntries()
		self.receiver.running = False


class Thread_cleanSparePDF(PBThread):
	"""Thread the execution of
	`physbiblio.pdf.LocalPDF.removeSparePDFFolders`
	"""

	def __init__(self, receiver, parent=None):
		"""Instantiate the object

		Parameters:
			receiver: the receiver for the text output
				(a `WriteStream` object)
			parent: the parent widget
		"""
		super(Thread_cleanSparePDF, self).__init__(parent)
		self.receiver = receiver

	def run(self):
		"""Start the receiver,
		run `pBPDF.removeSparePDFFolders` and finish
		"""
		self.receiver.start()
		pBPDF.removeSparePDFFolders()
		self.receiver.running = False


class Thread_fieldsArxiv(PBThread):
	"""Thread the execution of
	`physbiblio.database.Entries.getFieldsFromArxiv`
	"""

	def __init__(self, receiver, entries, fields, parent=None):
		"""Instantiate the object

		Parameters:
			receiver: the receiver for the text output
				(a `WriteStream` object)
			entries: the list of entries or the single entry
				for which the new fields must be added
			fields: the list of fields to be updated from arXiv
			parent: the parent widget
		"""
		super(Thread_fieldsArxiv, self).__init__(parent)
		self.entries = entries
		self.fields = fields
		self.receiver = receiver

	def run(self):
		"""Start the receiver,
		run `pBDB.bibs.getFieldsFromArxiv` and finish
		"""
		self.receiver.start()
		pBDB.bibs.getFieldsFromArxiv(self.entries, self.fields)
		time.sleep(0.1)
		self.receiver.running = False

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		pBDB.bibs.getArxivFieldsFlag = False


class Thread_importDailyArxiv(PBThread):
	"""Thread that uses `pBDB.bibs.replace`"""

	def __init__(self,
			receiver,
			found,
			parent):
		"""Initialize the thread and store the required settings

		Parameters:
			receiver: the receiver for the text output
				(a `WriteStream` object)
			found: the list of records to be imported
			parent: the parent widget
		"""
		super(Thread_importDailyArxiv, self).__init__(parent)
		self.found = found
		self.receiver = receiver
		self.runningImport = True

	def run(self):
		"""Start the receiver,
		import the required entries and finish
		"""
		self.receiver.start()
		db = bibtexparser.bibdatabase.BibDatabase()
		inserted = []
		failed = []
		for key in sorted(self.found):
			if not self.runningImport:
				continue
			el = self.found[key]
			if pBDB.bibs.loadAndInsert(el["bibpars"]["eprint"]):
				newKey = pBDB.bibs.getByKey(key)[0]["bibkey"]
				inserted.append(newKey)
			else:
				db.entries = [{
					"ID": el["bibpars"]["eprint"],
					"ENTRYTYPE": "article",
					"title": el["bibpars"]["title"],
					"author": el["bibpars"]["author"],
					"archiveprefix": "arXiv",
					"eprint": el["bibpars"]["eprint"],
					"primaryclass": el["bibpars"]["primaryclass"]}]
				entry = pbWriter.write(db)
				data = pBDB.bibs.prepareInsert(entry)
				if pBDB.bibs.insert(data):
					pBLogger.info("Element '%s' "%key
						+ "successfully inserted.\n")
					inserted.append(key)
				else:
					pBLogger.warning(
						"Failed in inserting entry %s\n"%key)
					failed.append(key)
					continue
				try:
					eid = pBDB.bibs.updateInspireID(key)
					pBDB.bibs.searchOAIUpdates(0,
						entries=pBDB.bibs.getByBibkey(key),
						force=True, reloadAll=True)
					newKey = pBDB.bibs.getByKey(key)[0]["bibkey"]
					if key != newKey:
						inserted[-1] = newKey
				except:
					pBLogger.warning(
						"Failed in completing info for entry %s\n"%(
							key))
					failed.append(key)
		pBLogger.info("Entries successfully imported:\n%s"%(inserted))
		pBLogger.info("Errors for entries:\n%s"%(failed))
		self.parent().importArXivResults = (inserted, failed)
		time.sleep(0.1)
		self.receiver.running = False

	def setStopFlag(self):
		"""Set the stop flag for the threaded process"""
		self.runningImport = False
