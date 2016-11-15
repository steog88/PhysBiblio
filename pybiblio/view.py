import subprocess

try:
	from pybiblio.config import pbConfig
	from pybiblio.database import pBDB
	from pybiblio.pdf import pBPDF
except ImportError:
	print("[CLI] Could not find pybiblio and its contents: configure your PYTHONPATH!")
	print traceback.format_exc()
	
class viewEntry():
	def __init__(self):
		self.webApp = pbConfig.params["webApplication"]
		self.arxivUrl = pbConfig.arxivUrl
		self.doiUrl = pbConfig.doiUrl
		self.inspireRecord = pbConfig.inspireRecord
		self.inspireSearch = pbConfig.inspireSearchBase + "p=find+"
		
	def openLink(self, key, arg = "arxiv", fileArg = None, printOnly = False):
		arxiv = pBDB.getEntryField(key, "arxiv")
		doi = pBDB.getEntryField(key, "doi")
		inspire = pBDB.getEntryField(key, "inspire")
		if arg is "arxiv" and arxiv:
			link = self.arxivUrl + arxiv
		elif arg is "doi" and doi:
			link = self.doiUrl + doi
		elif arg is "inspire" and inspire:
			link = self.inspireRecord + inspire
		elif arg is "inspire" and arxiv:
			link = self.inspireSearch + arxiv
		elif arg is "inspire":
			link = self.inspireSearch + key
		elif arg is "file":
			pBPDF.openFile(key, fileArg)
		else:
			print("[viewEntry] ERROR: invalid selection or missing information.\nUse one of (arxiv|doi|inspire|file) and check that all the information is available for entry '%s'."%key)
			return False
		
		if printOnly:
			print("[viewEntry] entry '%s' can be opened at '%s'"%(key, link))
		else:
			try:
				print("[viewEntry] opening '%s'..."%link)
				subprocess.Popen([self.webApp, link], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
			except:
				print("[viewEntry] opening link for '%s' failed!"%key)

pBView = viewEntry()
