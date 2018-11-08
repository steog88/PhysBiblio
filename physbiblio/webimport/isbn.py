"""Module that deals with importing info from the ISBN2Bibtex API.

This file is part of the physbiblio package.
"""
import traceback
try:
	from physbiblio.errors import pBLogger
	from physbiblio.webimport.webInterf import WebInterf
	from physbiblio.parseAccents import parse_accents_str
except ImportError:
	print("Could not find physbiblio and its modules!")
	print(traceback.format_exc())
	raise


class WebSearch(WebInterf):
	"""Subclass of WebInterf that can connect to ISBN2Bibtex
	to perform searches
	"""

	def __init__(self):
		"""Initializes the class variables
		using the WebInterf constructor.

		Define additional specific parameters for the ISBN2Bibtex API.
		"""
		WebInterf.__init__(self)
		self.name = "isbn"
		self.description = "ISBN to bibtex"
		self.url = "http://www.ebook.de/de/tools/isbn2bibtex"
		self.urlArgs = {}

	def retrieveUrlFirst(self,string):
		"""Retrieves the first (only) result from the content
		of the given web page.

		Parameters:
			string: the search string (the ISBN)

		Output:
			returns the bibtex string
		"""
		self.urlArgs["isbn"] = string
		url = self.createUrl()
		pBLogger.info("Search '%s' -> %s"%(string, url))
		text = self.textFromUrl(url)
		try:
			return parse_accents_str(text[:])
		except Exception:
			pBLogger.exception("Impossible to get results")
			return ""

	def retrieveUrlAll(self,string):
		"""Alias for retrieveUrlFirst"""
		return self.retrieveUrlFirst(string)

