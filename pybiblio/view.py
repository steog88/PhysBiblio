import subprocess, traceback
try:
	import pybiblio.errors as pBDBErrors
except ImportError:
	print("Could not find pybiblio.errors and its contents: configure your PYTHONPATH!")
	print(traceback.format_exc())

try:
	from pybiblio.config import pbConfig
	from pybiblio.database import pBDB
	from pybiblio.pdf import pBPDF
except ImportError:
	pBDBErrors("[CLI] Could not find pybiblio and its contents: configure your PYTHONPATH!", traceback)
	
class viewEntry():
	"""Contains methods to print or open a web link to the entry"""
	def __init__(self):
		"""init link base names and application name"""
		self.webApp = pbConfig.params["webApplication"]

		self.inspireRecord = pbConfig.inspireRecord
		self.inspireSearch = pbConfig.inspireSearchBase + "?p=find+"
		
	def printLink(self, key, arg = "arxiv", fileArg = None):
		"""uses database information to compute and print the web link, or the pdf module to open a pdf"""
		arxiv = pBDB.bibs.getField(key, "arxiv")
		doi = pBDB.bibs.getField(key, "doi")
		inspire = pBDB.bibs.getField(key, "inspire")
		if arg is "arxiv" and arxiv:
			link = pBDB.bibs.getArxivUrl(key, "abs")
		elif arg is "doi" and doi:
			link = pBDB.bibs.getDoiUrl(key)
		elif arg is "inspire" and inspire:
			link = self.inspireRecord + inspire
		elif arg is "inspire" and arxiv:
			link = self.inspireSearch + arxiv
		elif arg is "inspire":
			link = self.inspireSearch + key
		elif arg is "file":
			pBPDF.openFile(key, fileArg)
		else:
			pBDBErrors("[viewEntry] ERROR: invalid selection or missing information.\nUse one of (arxiv|doi|inspire|file) and check that all the information is available for entry '%s'."%key)
			return False

		return link
		
	def openLink(self, key, arg = "arxiv", fileArg = None):
		"""uses the printLink method to compute the web link and opens it"""
		if type(key) is list:
			for k in key:
				self.openLink(k, arg, fileArg)
		else:
			link = self.printLink(key, arg = arg, fileArg = fileArg)
			if link:
				try:
					print("[viewEntry] opening '%s'..."%link)
					subprocess.Popen([self.webApp, link], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
				except OSError:
					pBDBErrors("[viewEntry] opening link for '%s' failed!"%key)
			else:
				pBDBErrors("[viewEntry] impossible to get the '%s' link for entry '%s'"%(arg, key))

pBView = viewEntry()
