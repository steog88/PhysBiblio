"""Module that deals with importing info from the INSPIRE-HEP API.

This file is part of the physbiblio package.
"""
import traceback
import re
try:
	from physbiblio.errors import pBLogger
	from physbiblio.config import pbConfig
	from physbiblio.webimport.webInterf import WebInterf, physBiblioWeb
	from physbiblio.parseAccents import parse_accents_str
except ImportError:
	print("Could not find physbiblio and its modules!")
	print(traceback.format_exc())
	raise


class WebSearch(WebInterf):
	"""Subclass of WebInterf that can connect
	to INSPIRE-HEP to perform searches
	"""

	def __init__(self):
		"""Initializes the class variables
		using the WebInterf constructor.

		Define additional specific parameters for the INSPIRE-HEP API.
		"""
		WebInterf.__init__(self)
		self.name = "inspire"
		self.description = "INSPIRE fetcher"
		self.url = pbConfig.inspireSearchBase
		self.urlRecord = pbConfig.inspireRecord
		self.urlArgs = {
			#"action_search": "Search",
			"sf": "year",
			"so": "a",
			"rg": "250",
			"sc": "0",
			"eb": "B",
			"of": "hx"
				# for bibtex format ---- hb for standard format,
				# for retrieving inspireid
			}

	def retrieveUrlFirst(self, string):
		"""Retrieves the first result
		from the content of the given web page.

		Parameters:
			string: the search string

		Output:
			returns the bibtex string obtained from the API
		"""
		self.urlArgs["p"] = string.replace(" ", "+")
		url = self.createUrl()
		pBLogger.info("Search '%s' -> %s"%(string, url))
		text = self.textFromUrl(url)
		try:
			i1 = text.find("<pre>")
			i2 = text.find("</pre>")
			if i1 > 0 and i2 > 0:
				bibtex = text[i1 + 5 : i2]
			else:
				bibtex = ""
			return parse_accents_str(bibtex)
		except Exception:
			pBLogger.exception("Impossible to get results")
			return ""

	def retrieveUrlAll(self, string):
		"""Retrieves all the result
		from the content of the given web page.

		Parameters:
			string: the search string

		Output:
			returns the bibtex string obtained from the API
		"""
		self.urlArgs["p"] = string.replace(" ", "+")
		url = self.createUrl()
		pBLogger.info("Search '%s' -> %s"%(string, url))
		text = self.textFromUrl(url)
		try:
			i1 = text.find("<pre>")
			i2 = text.rfind("</pre>")
			if i1 > 0 and i2 > 0:
				bibtex = text[i1 + 5 : i2]
			else:
				bibtex = ""
			return parse_accents_str(
				bibtex.replace("<pre>", "").replace("</pre>", ""))
		except Exception:
			pBLogger.exception("Impossible to get results")
			return ""

	def retrieveInspireID(self, string, number=None):
		"""Read the fetched content for a given entry
		to obtain its INSPIRE-HEP ID

		Parameters:
			string: the search string
			number (optional): the integer corresponding
				to the desired entry in the list,
				if more than one is present
		"""
		i = 0
		self.urlArgs["p"] = string.replace(" ", "+")
		self.urlArgs["of"] = "hb" #do not ask bibtex, but standard
		url = self.createUrl()
		self.urlArgs["of"] = "hx" #restore
		pBLogger.info("Search ID of %s -> %s"%(string, url))
		text = self.textFromUrl(url)
		if text is None:
			pBLogger.warning("An error occurred. Empty text obtained")
			return ""
		try:
			searchID = re.compile(
				'titlelink(.*)?(http|https)://inspirehep.net/record/([0-9]*)?">'
				)
			inspireID = ""
			for q in searchID.finditer(text):
				if len(q.group()) > 0:
					if number is None or i == number:
						inspireID = q.group(3)
						break
					else:
						i += 1
			pBLogger.info("Found: %s"%inspireID)
			return inspireID
		except Exception:
			pBLogger.exception("Impossible to get results")
			return ""
