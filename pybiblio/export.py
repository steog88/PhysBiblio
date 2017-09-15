import os, sys, numpy, codecs, re
try:
	from pybiblio.database import pBDB
except ImportError:
	print("Could not find pybiblio and its contents: configure your PYTHONPATH!")

class pbExport():
	def __init__(self):
		self.exportForTexFlag = True

	def exportLast(self, fname):
		"""export the last selection of entries into a .bib file"""
		if pBDB.bibs.lastFetched:
			txt = ""
			for q in pBDB.bibs.lastFetched:
				txt += q["bibtex"] + "\n"
			try:
				with codecs.open(fname, 'w', 'utf-8') as bibfile:
					bibfile.write(txt)
			except Exception, e:
				print(e)
				print(traceback.format_exc())
				sys.stderr.write("error: " + readfilebib)
				os.rename(readfilebib + backupextension + ".old", readfilebib + backupextension)
		else:
			print("[export] No last selection to export!")

	def exportAll(self, fname):
		"""export all the entries in the database in a .bib file"""
		rows = pBDB.bibs.getAll(saveQuery = False)
		if len(rows) > 0:
			txt = ""
			for q in rows:
				txt += q["bibtex"] + "\n"
			try:
				with codecs.open(fname, 'w', 'utf-8') as bibfile:
					bibfile.write(txt)
			except Exception, e:
				print(e)
				print(traceback.format_exc())
				sys.stderr.write("error: " + readfilebib)
				os.rename(readfilebib + backupextension + ".old", readfilebib + backupextension)
		else:
			print("[export] No elements to export!")

	def exportSelected(self, fname, rows):
		"""export all the selected entries in the database in a .bib file"""
		if len(rows) > 0:
			txt = ""
			for q in rows:
				txt += q["bibtex"] + "\n"
			try:
				with codecs.open(fname, 'w', 'utf-8') as bibfile:
					bibfile.write(txt)
			except Exception, e:
				print(e)
				print(traceback.format_exc())
				sys.stderr.write("error: " + readfilebib)
				os.rename(readfilebib + backupextension + ".old", readfilebib + backupextension)
		else:
			print("[export] No elements to export!")

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
				o.write("%file written by PyBiblio\n")

		existingBib = open(outFName, "r").read()

		if type(texFile) is list:
			for t in texFile:
				self.exportForTexFile(t, outFName, overwrite = False, autosave = autosave)
			print("[export] done for all the texFiles. See previous errors (if any)")
			return True

		allBibEntries = pBDB.bibs.getAll(saveQuery = False)
		allbib = [ e["bibkey"] for e in allBibEntries ]

		cite = re.compile('\\\\(cite|citep|citet)\{([A-Za-z\']*:[0-9]*[a-z]*[,]?[\n ]*|[A-Za-z0-9\-][,]?[\n ]*)*\}', re.MULTILINE)	#find \cite{...}
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
		print("[export] %d keys found"%len(requiredBibkeys))

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
					retrieved.append(m)
					try:
						saveEntryOutBib(pBDB.bibs.getField(m, "bibtex"))
					except:
						unexpected.append(m)
						print("[export] unexpected error in extracting entry '%s' to the output file"%m)
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
		print("[export] %d keys found in .tex file"%len(requiredBibkeys))
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
			print("\n".join(["'%s' => %s"%(k, ", ".join(n) ) for k, n in newKeys.iteritems() ] ) )
		print("[export] -->     " + str(warnings) + " warning(s) occurred!")

pBExport = pbExport()
