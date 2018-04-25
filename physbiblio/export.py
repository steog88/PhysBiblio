"""
Classes and functions that manage the export of the database entries into .bib files.

This file is part of the physbiblio package.
"""
import os, codecs, re
import bibtexparser
import shutil
import traceback

try:
	from physbiblio.errors import pBLogger
	from physbiblio.config import pbConfig
	from physbiblio.database import pBDB
	from physbiblio.bibtexwriter import pbWriter
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
	print(traceback.format_exc())
	raise

class pbExport():
	"""
	Class that contains the export functions and related.
	"""
	def __init__(self):
		"""
		Initialize the class instance and set some default variables.
		"""
		self.exportForTexFlag = True
		self.backupExtension = ".bck"

	def backupCopy(self, fileName):
		"""
		Creates a backup copy of the given file.

		Parameters:
			fileName: the name of the file to be backed up
		"""
		if os.path.isfile(fileName):
			try:
				shutil.copy2(fileName, fileName + self.backupExtension)
			except IOError:
				pBLogger.exception("Cannot write backup file.\nCheck the folder permissions.")
				return False
			else:
				return True
		return False

	def restoreBackupCopy(self, fileName):
		"""
		Restores the backup copy of the given file, if any.

		Parameters:
			fileName: the name of the file to be restore
		"""
		if os.path.isfile(fileName + self.backupExtension):
			try:
				shutil.copy2(fileName + self.backupExtension, fileName)
			except IOError:
				pBLogger.exception("Cannot restore backup file.\nCheck the file permissions.")
				return False
			else:
				return True
		return False

	def rmBackupCopy(self, fileName):
		"""
		Deletes the backup copy of the given file, if any.

		Parameters:
			fileName: the name of the file of which the backup should be deleted
		"""
		if os.path.isfile(fileName + self.backupExtension):
			try:
				os.remove(fileName + self.backupExtension)
			except IOError:
				pBLogger.exception("Cannot remove backup file.\nCheck the file permissions.")
				return False
			else:
				return True
		return True

	def exportLast(self, fileName):
		"""
		Export the last queried entries into a .bib file, if the list is not empty.

		Parameters:
			fileName: the name of the output bibtex file
		"""
		self.backupCopy(fileName)
		if pBDB.bibs.lastFetched:
			txt = ""
			for q in pBDB.bibs.lastFetched:
				txt += q["bibtex"] + "\n"
			try:
				with codecs.open(fileName, 'w', 'utf-8') as bibfile:
					bibfile.write(txt)
			except Exception:
				pBLogger.exception("Problems in exporting .bib file!")
				self.restoreBackupCopy(fileName)
		else:
			pBLogger.info("No last selection to export!")
		self.rmBackupCopy(fileName)

	def exportAll(self, fileName):
		"""
		Export all the entries in the database into a .bib file.

		Parameters:
			fileName: the name of the output bibtex file
		"""
		self.backupCopy(fileName)
		pBDB.bibs.fetchAll(saveQuery = False, doFetch = False)
		txt = ""
		for q in pBDB.bibs.fetchCursor():
			txt += q["bibtex"] + "\n"
		if txt != "":
			try:
				with codecs.open(fileName, 'w', 'utf-8') as bibfile:
					bibfile.write(txt)
			except Exception:
				pBLogger.exception("Problems in exporting .bib file!", traceback)
				self.restoreBackupCopy(fileName)
		else:
			pBLogger.info("No elements to export!")
		self.rmBackupCopy(fileName)

	def exportSelected(self, fileName, rows):
		"""
		Export the given entries into a .bib file.

		Parameters:
			fileName: the name of the output bibtex file
			rows: the list of entries to be exported
		"""
		self.backupCopy(fileName)
		if len(rows) > 0:
			txt = ""
			for q in rows:
				txt += q["bibtex"] + "\n"
			try:
				with codecs.open(fileName, 'w', 'utf-8') as bibfile:
					bibfile.write(txt)
			except Exception:
				pBLogger.exception("Problems in exporting .bib file!")
				self.restoreBackupCopy(fileName)
		else:
			pBLogger.info("No elements to export!")
		self.rmBackupCopy(fileName)

	def exportForTexFile(self, texFileName, outFileName, overwrite = False, autosave = True):
		"""
		Reads a .tex file looking for the \cite{} commands, collects the bibtex entries cited in the text and stores them in a bibtex file.
		The entries are taken from the database first, or from INSPIRE-HEP if possible.
		The downloaded entries are saved in the database.

		Parameters:
			texFileName: the name (or a list of names) of the considered .tex file(s)
			outFileName: the name of the output file, where the required entries will be added
			overwrite (boolean, default False): if True, the previous version of the file is replaced and no backup copy is created
			autosave (boolean, default True): if True, the changes to the database are automatically saved.

		Output:
			True if successful, False if errors occurred
		"""
		self.exportForTexFlag = True
		pBLogger.info("Reading keys from '%s'"%texFileName)
		pBLogger.info("Saving in '%s'"%outFileName)
		if autosave:
			pBLogger.info("Changes will be automatically saved at the end!")

		if overwrite:
			try:
				with open(outFileName, "w") as o:
					o.write("%file written by PhysBiblio\n")
			except IOError:
				pBLogger.exception("Cannot write on file.\nCheck the file permissions.")

		try:
			existingBib = open(outFileName, "r").read()
		except IOError:
			pBLogger.exception("Cannot read file %s."%outFileName)
			return False

		if type(texFileName) is list:
			if len(texFileName) == 0:
				return False
			for t in texFileName:
				self.exportForTexFile(t, outFileName, overwrite = False, autosave = autosave)
			pBLogger.info("Done for all the texFiles. See previous errors (if any)")
			return True

		cite = re.compile('\\\\(cite|citep|citet)\{([A-Za-z\']*:[0-9]*[a-z]*[,]?[\n ]*|[A-Za-z0-9\-][,]?[\n ]*|[A-Za-z0-9_\-][,]?[\n ]*)*\}', re.MULTILINE)	#find \cite{...}
		unw1 = re.compile('[ ]*(Owner|Timestamp|__markedentry|File)+[ ]*=.*?,[\n]*')	#remove unwanted fields
		unw2 = re.compile('[ ]*(Owner|Timestamp|__markedentry|File)+[ ]*=.*?[\n ]*\}')	#remove unwanted fields
		unw3 = re.compile('[ ]*Abstract[ ]*=[ ]*[{]+(.*?)[}]+,', re.MULTILINE)		#remove Abstract field
		bibel = re.compile('@[a-zA-Z]*\{([A-Za-z]*:[0-9]*[a-z]*)?,', re.MULTILINE | re.DOTALL)	#find the @Article(or other)...}, entry for the key "m"
		bibty = re.compile('@[a-zA-Z]*\{', re.MULTILINE | re.DOTALL)	#find the @Article(or other) entry for the key "m"

		unexpected = []
		def saveEntryOutBib(a):
			"""
			Remove unwanted fields and add the bibtex entry to the output file

			Parameters:
				a: the bibtex entry
			"""
			bib = '@' + a.replace('@', '')
			for u in unw1.finditer(bib):
				bib = bib.replace(u.group(), '')
			for u in unw2.finditer(bib):
				bib = bib.replace(u.group(), '')
			for u in unw3.finditer(bib):
				bib = bib.replace(u.group(), '')
			bibf = '\n'.join([line for line in bib.split('\n') if line.strip() ])
			try:
				with open(outFileName, "a") as o:
					o.write(bibf + "\n")
					pBLogger.info("%s inserted in output file"%m)
			except IOError:
				pBLogger.exception("Impossible to write file '%s'"%outFileName)

		keyscont=""
		try:
			with open(texFileName) as r:
				keyscont += r.read()
		except IOError:
			pBLogger.exception("The file %s does not exist."%texFileName)
			return False

		citaz = [ m for m in cite.finditer(keyscont) if m != "" ]
		pBLogger.info(r"%d \cite commands found in .tex file"%len(citaz))

		requiredBibkeys = []
		for c in citaz:
			b = c.group().replace(r'\cite{', '').replace(r'\citep{', '').replace(r'\citet{', '')
			d = b.replace(' ', '')
			b = d.replace('\n', '')
			d = b.replace(r'}', '')
			a = d.split(',')
			for e in a:
				if e not in requiredBibkeys and e not in existingBib and e.strip() != "":
					requiredBibkeys.append(e)
		pBLogger.info("%d new keys found"%len(requiredBibkeys))

		missing = []
		retrieved = []
		newKeys = {}
		notFound = []
		warnings = 0
		for s in requiredBibkeys:
			if not pBDB.bibs.getByBibtex(s) and s.strip() != "":
				missing.append(s)

		for m in requiredBibkeys:
			if m in missing and self.exportForTexFlag:
				pBLogger.info("Key '%s' missing, trying to import it from Web"%m)
				newWeb = pBDB.bibs.loadAndInsert(m, returnBibtex = True)
				newCheck = pBDB.bibs.getByBibkey(m, saveQuery = False)

				if len(newCheck) > 0:
					pBDB.catBib.insert(pbConfig.params["defaultCategories"], m)
					retrieved.append(m)
					try:
						saveEntryOutBib(pBDB.bibs.getField(m, "bibtex"))
					except:
						unexpected.append(m)
						pBLogger.exception("Unexpected error in saving entry '%s' into the output file"%m)
				else:
					if newWeb and not newWeb.find(m) > 0:
						warnings += 1
						t = [ j.group() for j in bibel.finditer(newWeb) ]
						t1 = []
						for s in t:
							for u in bibty.finditer(s):
								s = s.replace(u.group(), '')
							s = s.replace(',', '')
							t1.append(s)
						newKeys[m] = t1
					else:
						notFound.append(m)
						warnings += 1
				pBLogger.info("\n")
			else:
				try:
					saveEntryOutBib(pBDB.bibs.getField(m, "bibtex"))
				except:
					unexpected.append(m)
					pBLogger.exception("Unexpected error in extracting entry '%s' to the output file"%m)

		if autosave:
			pBDB.commit()
		pBLogger.info("\n\nRESUME")
		pBLogger.info("%d new keys found in .tex file"%len(requiredBibkeys))
		if len(missing) > 0:
			pBLogger.info("%d required entries were missing in database"%len(missing))
		if len(retrieved) > 0:
			pBLogger.info("%d new entries retrieved:"%len(retrieved))
			pBLogger.info(" - ".join(retrieved))
		if len(notFound) > 0:
			pBLogger.info("Impossible to find %d entries:"%len(notFound))
			pBLogger.info(" - ".join(notFound))
		if len(unexpected) > 0:
			pBLogger.info("Unexpected errors for %d entries:"%len(unexpected))
			pBLogger.info(" - ".join(unexpected))
		if len(newKeys.keys()) > 0:
			pBLogger.info("Possible non-matching keys in %d entries"%len(newKeys.keys()) + \
				"\n".join(["'%s' => %s"%(k, ", ".join(n) ) for k, n in newKeys.items() ] ) )
		pBLogger.info("     " + str(warnings) + " warning(s) occurred!")
		return True

	def updateExportedBib(self, fileName, overwrite = False):
		"""
		Reads a bibtex file and updates the entries that it contains, for example if the entry has been published.

		Parameters:
			fileName: the name of the considered bibtex file
			overwrite (boolean, default False): if True, the previous version of the file is replaced and no backup copy is created

		Output:
			True if successful, False if errors occurred
		"""
		self.backupCopy(fileName)
		bibfile=""
		try:
			with open(fileName) as r:
				bibfile += r.read()
		except IOError:
			pBLogger.exception("Cannot write on file.\nCheck the file permissions.")
			return False
		try:
			biblist = bibtexparser.loads(bibfile)
		except IndexError:
			pBLogger.exception("Problems in loading the .bib file!")
			return False
		db = bibtexparser.bibdatabase.BibDatabase()
		db.entries = []
		for b in biblist.entries:
			key = b["ID"]
			element = pBDB.bibs.getByBibkey(key, saveQuery = False)
			if len(element)>0:
				db.entries.append(element[0]["bibtexDict"])
			else:
				db.entries.append(b)
		txt = pbWriter.write(db).strip()
		try:
			with codecs.open(fileName, 'w', 'utf-8') as outfile:
				outfile.write(txt)
		except Exception:
			pBLogger.exception("Problems in exporting .bib file!")
			self.restoreBackupCopy(fileName)
			return False
		if overwrite:
			self.rmBackupCopy(fileName)
		return True

pBExport = pbExport()
