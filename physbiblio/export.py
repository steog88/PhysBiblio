import os, sys, numpy, codecs, re
import bibtexparser
import shutil
try:
	from physbiblio.errors import pBErrorManager
	from physbiblio.database import pBDB
	from physbiblio.bibtexwriter import pbWriter
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")

class pbExport():
	def __init__(self):
		self.exportForTexFlag = True
		self.backupextension = ".bck"

	def backupCopy(self, fname):
		if os.path.isfile(fname):
			shutil.copy2(fname, fname + self.backupextension)

	def restoreBackupCopy(self, fname):
		if os.path.isfile(fname + self.backupextension):
			shutil.copy2(fname + self.backupextension, fname)

	def rmBackupCopy(self, fname):
		if os.path.isfile(fname + self.backupextension):
			os.remove(fname + self.backupextension)

	def exportLast(self, fname):
		"""export the last selection of entries into a .bib file"""
		self.backupCopy(fname)
		if pBDB.bibs.lastFetched:
			txt = ""
			for q in pBDB.bibs.lastFetched:
				txt += q["bibtex"] + "\n"
			try:
				with codecs.open(fname, 'w', 'utf-8') as bibfile:
					bibfile.write(txt)
			except Exception:
				pBErrorManager("[export] problems in exporting .bib file!", traceback)
				self.restoreBackupCopy(fname)
		else:
			print("[export] No last selection to export!")
		self.rmBackupCopy(fname)

	def exportAll(self, fname):
		"""export all the entries in the database in a .bib file"""
		self.backupCopy(fname)
		rows = pBDB.bibs.getAll(saveQuery = False)
		if len(rows) > 0:
			txt = ""
			for q in rows:
				txt += q["bibtex"] + "\n"
			try:
				with codecs.open(fname, 'w', 'utf-8') as bibfile:
					bibfile.write(txt)
			except Exception:
				pBErrorManager("[export] problems in exporting .bib file!", traceback)
				self.restoreBackupCopy(fname)
		else:
			print("[export] No elements to export!")
		self.rmBackupCopy(fname)

	def exportSelected(self, fname, rows):
		"""export all the selected entries in the database in a .bib file"""
		self.backupCopy(fname)
		if len(rows) > 0:
			txt = ""
			for q in rows:
				txt += q["bibtex"] + "\n"
			try:
				with codecs.open(fname, 'w', 'utf-8') as bibfile:
					bibfile.write(txt)
			except Exception:
				pBErrorManager("[export] problems in exporting .bib file!", traceback)
				self.restoreBackupCopy(fname)
		else:
			print("[export] No elements to export!")
		self.rmBackupCopy(fname)

	def exportForTexFile(self, texFile, outFName, overwrite = False, autosave = True):
		"""
		export only the bibtexs required to compile a given .tex file (or a list of).
		If missing, it tries to download them
		"""
		self.exportForTexFlag = True
		print("[export] reading keys from '%s'"%texFile)
		print("[export] saving in '%s'"%outFName)
		if autosave:
			print("[export] I will automatically save the changes at the end!")

		if overwrite:
			with open(outFName, "w") as o:
				o.write("%file written by PhysBiblio\n")

		existingBib = open(outFName, "r").read()

		if type(texFile) is list:
			if len(texFile) == 0:
				return False
			for t in texFile:
				self.exportForTexFile(t, outFName, overwrite = False, autosave = autosave)
			print("[export] done for all the texFiles. See previous errors (if any)")
			return True

		allBibEntries = pBDB.bibs.getAll(saveQuery = False)
		allbib = [ e["bibkey"] for e in allBibEntries ]

		cite = re.compile('\\\\(cite|citep|citet)\{([A-Za-z\']*:[0-9]*[a-z]*[,]?[\n ]*|[A-Za-z0-9\-][,]?[\n ]*|[A-Za-z0-9_\-][,]?[\n ]*)*\}', re.MULTILINE)	#find \cite{...}
		unw1 = re.compile('[ ]*(Owner|Timestamp|__markedentry|File)+[ ]*=.*?,[\n]*')	#remove unwanted fields
		unw2 = re.compile('[ ]*(Owner|Timestamp|__markedentry|File)+[ ]*=.*?[\n ]*\}')	#remove unwanted fields
		unw3 = re.compile('[ ]*Abstract[ ]*=[ ]*[{]+(.*?)[}]+,', re.MULTILINE)		#remove Abstract field
		bibel = re.compile('@[a-zA-Z]*\{([A-Za-z]*:[0-9]*[a-z]*)?,', re.MULTILINE | re.DOTALL)	#find the @Article(or other)...}, entry for the key "m"
		bibty = re.compile('@[a-zA-Z]*\{', re.MULTILINE | re.DOTALL)	#find the @Article(or other) entry for the key "m"

		unexpected = []
		def saveEntryOutBib(a):
			bib = '@' + a.replace('@', '')
			for u in unw1.finditer(bib):
				bib = bib.replace(u.group(), '')
			for u in unw2.finditer(bib):
				bib = bib.replace(u.group(), '')
			for u in unw3.finditer(bib):
				bib = bib.replace(u.group(), '')
			bibf = '\n'.join([line for line in bib.split('\n') if line.strip() ])
			try:
				with open(outFName, "a") as o:
					o.write(bibf + "\n")
					print("[export] %s inserted in output file"%m)
			except:
				print("[export] ERROR: impossible to write file '%s'"%outFName)

		keyscont=""
		with open(texFile) as r:
			keyscont += r.read()

		citaz = [ m for m in cite.finditer(keyscont) if m != "" ]

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
		print("[export] %d new keys found"%len(requiredBibkeys))

		missing = []
		retrieved = []
		newKeys = {}
		notFound = []
		warnings = 0
		for s in requiredBibkeys:
			if s not in allbib and s.strip() != "":
				missing.append(s)

		for m in requiredBibkeys:
			if m in missing and self.exportForTexFlag:
				print("[export] key '%s' missing, trying to import it from Web"%m)
				newWeb = pBDB.bibs.loadAndInsert(m, returnBibtex = True)
				newCheck = pBDB.bibs.getByBibkey(m, saveQuery = False)

				if len(newCheck) > 0:
					pBDB.catBib.insert(pbConfig.params["defaultCategories"], m)
					retrieved.append(m)
					try:
						saveEntryOutBib(pBDB.bibs.getField(m, "bibtex"))
					except:
						unexpected.append(m)
						print("[export] unexpected error in saving entry '%s' into the output file"%m)
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
				print("\n")
			else:
				try:
					saveEntryOutBib(pBDB.bibs.getField(m, "bibtex"))
				except:
					unexpected.append(m)
					print("[export] unexpected error in extracting entry '%s' to the output file"%m)

		if autosave:
			pBDB.commit()
		print("\n[export] RESUME")
		print("[export] %d new keys found in .tex file"%len(requiredBibkeys))
		if len(missing) > 0:
			print("\n[export] %d required entries were missing in database"%len(missing))
		if len(retrieved) > 0:
			print("\n[export] retrieved %d new entries:"%len(retrieved))
			print(" - ".join(retrieved))
		if len(notFound) > 0:
			print("\n[export] impossible to find %d entries:"%len(notFound))
			print(" - ".join(notFound))
		if len(unexpected) > 0:
			print("\n[export] unexpected errors for %d entries:"%len(unexpected))
			print(" - ".join(unexpected))
		if len(newKeys.keys()) > 0:
			print("\n[export] possible non-matching keys in %d entries"%len(newKeys.keys()))
			print("\n".join(["'%s' => %s"%(k, ", ".join(n) ) for k, n in newKeys.items() ] ) )
		print("[export] -->     " + str(warnings) + " warning(s) occurred!")

	def updateExportedBib(self, fname, overwrite = False):
		self.backupCopy(fname)
		bibfile=""
		with open(fname) as r:
			bibfile += r.read()
		try:
			biblist = bibtexparser.loads(bibfile)
		except IndexError:
			pBErrorManager("[export] problems in loading the .bib file!", traceback)
			return "[export] problems in loading the .bib file!"
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
			with codecs.open(fname, 'w', 'utf-8') as outfile:
				outfile.write(txt)
		except Exception:
			pBErrorManager("[export] problems in exporting .bib file!", traceback)
			self.restoreBackupCopy(fname)
		if overwrite:
			self.rmBackupCopy(fname)
		return True

pBExport = pbExport()
