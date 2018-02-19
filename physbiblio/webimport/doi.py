"""
Module that deals with importing info from the DOI.org API.
"""
import traceback
try:
	from physbiblio.errors import pBErrorManager
except ImportError:
	print("Could not find physbiblio.errors and its contents: configure your PYTHONPATH!")
	print(traceback.format_exc())
from physbiblio.webimport.webInterf import *
from physbiblio.parse_accents import *

class webSearch(webInterf):
	"""Subclass of webInterf that can connect to doi.org to perform searches"""
	def __init__(self):
		"""
		Initializes the class variables using the webInterf constructor.

		Define additional specific parameters for the DOI.org API.
		"""
		webInterf.__init__(self)
		self.name = "doi"
		self.description = "Doi fetcher"
		self.url = "http://dx.doi.org/"
		self.headers = {'accept': 'application/x-bibtex'}
		
	def createUrl(self, doi):
		"""
		Joins the base url and the search string to get the full url.

		(DOI.org url Behaves differently than other APIs in the modules of this subpackage)
		"""
		return self.url + doi
		
	def retrieveUrlFirst(self,string):
		"""
		Retrieves the first (only) result from the content of the given web page.

		Parameters:
			string: the search string (the DOI)

		Output:
			returns the bibtex string
		"""
		url = self.createUrl(string)
		print("[doi] search %s -> %s"%(string, url))
		text = self.textFromUrl(url, self.headers)
		try:
			return text[:]
		except Exception:
			pBErrorManager("[doi] -> ERROR: impossible to get results", traceback)
			return ""
		
	def retrieveUrlAll(self,string):
		"""
		Alias for retrieveUrlFirst
		"""
		return self.retrieveUrlFirst(string)
