"""
Module that deals with importing info from the ISBN2Bibtex API.

This file is part of the PhysBiblio package.
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
	"""Subclass of webInterf that can connect to ISBN2Bibtex to perform searches"""
	def __init__(self):
		"""
		Initializes the class variables using the webInterf constructor.

		Define additional specific parameters for the ISBN2Bibtex API.
		"""
		webInterf.__init__(self)
		self.name = "isbn"
		self.description = "ISBN to bibtex"
		self.url = "http://www.ebook.de/de/tools/isbn2bibtex"
		self.urlArgs = {}
		
	def retrieveUrlFirst(self,string):
		"""
		Retrieves the first (only) result from the content of the given web page.

		Parameters:
			string: the search string (the ISBN)

		Output:
			returns the bibtex string
		"""
		self.urlArgs["isbn"] = string
		url = self.createUrl()
		print("[isbn] search %s -> %s"%(string, url))
		text = self.textFromUrl(url)
		try:
			return parse_accents_str(text[:])
		except Exception:
			pBErrorManager("[isbn] -> ERROR: impossible to get results", traceback)
			return ""
		
	def retrieveUrlAll(self,string):
		"""
		Alias for retrieveUrlFirst
		"""
		return self.retrieveUrlFirst(string)

