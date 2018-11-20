"""Module that creates the base class WebInterf,
which will be used by other modules in this package.

Uses urllib to download url content.

This file is part of the physbiblio package.
"""
import sys
import os
import socket
import pkgutil
import traceback
import ssl
if sys.version_info[0] < 3:
	from urllib2 import Request, urlopen, URLError, HTTPError
else:
	from urllib.request import Request, urlopen, URLError, HTTPError

try:
	from physbiblio.errors import pBLogger
	import physbiblio.webimport as wi
	from physbiblio.config import pbConfig
except ImportError:
	print("Could not find physbiblio and its modules!")
	print(traceback.format_exc())
	raise

#scan package content to load list of available modules, to be imported later
pkgpath = os.path.dirname(wi.__file__)
webInterfaces = [name for _, name, _ in pkgutil.iter_modules([pkgpath])]


class WebInterf():
	"""This is the main class for the web search methods.

	It contains a constructor, a function to create an appropriate url
	and to retrieve text from the url,
	a function to load other webinterfaces
	"""

	def __init__(self):
		"""Initializes the class variables."""
		self.url = None
		self.urlArgs = None
		self.urlTimeout = float(pbConfig.params["timeoutWebSearch"])
		#save the names of the available web search interfaces
		self.interfaces = [ a for a in webInterfaces if a != "webInterf" \
			and a != "tests" ]
		self.webSearch = {}
		self.loaded = False

	def createUrl(self):
		"""Joins the arguments of the GET query to get the full url.

		Uses the self.urlArgs dictionary to generate the list
		of HTTP GET parameters.
		"""
		return self.url + "?" + "&".join(
			["%s=%s"%(a, b) for a, b in self.urlArgs.items()])

	def textFromUrl(self, url, headers=None):
		"""Use urllib to get the html content of the given url.

		Parameters:
			url: the url to be opened
			headers (default None): the additional headers
				to be passed to urllib.Request

		Output:
			text: the content of the url
		"""
		try:
			if headers is not None:
				req = Request(url, headers=headers)
			else:
				req = Request(url)
			response = urlopen(req, timeout=self.urlTimeout)
			data = response.read()
		except URLError:
			pBLogger.warning(
				"[%s] -> Error in retrieving data from url"%self.name)
			return ""
		except HTTPError:
			pBLogger.warning("[%s] -> %s not found"%url)
			return ""
		except (ssl.SSLError, socket.timeout):
			pBLogger.warning("[%s] -> Timed out"%self.name)
			return ""
		try:
			text = data.decode('utf-8')
		except Exception:
			pBLogger.warning(
				"[%s] -> Bad codification, utf-8 decode failed"%self.name)
			return ""
		return text

	def retrieveUrlFirst(self, search):
		"""Retrieves the first bibtexs that the search gives,
		using the subclass specific instructions.

		Parameter:
			search: the string to be searched

		Output:
			returns None in the default implementation
				(must be subclassed)
		"""
		return None

	def retrieveUrlAll(self, search):
		"""Retrieves all the bibtexs that the search gives,
		using the subclass specific instructions

		Parameter:
			search: the string to be searched

		Output:
			returns None in the default implementation
				(must be subclassed)
		"""
		return None

	def loadInterfaces(self):
		"""Load the subclasses that will interface
		with the main websites to search bibtex info
		and saves them into a dictionary (`self.webSearch`).

		The subclasses are read scanning the package directory.
		"""
		if self.loaded:
			return
		for method in self.interfaces:
			try:
				_temp = __import__("physbiblio.webimport." + method,
					globals(), locals(), ["WebSearch"])
				self.webSearch[method] = getattr(_temp, "WebSearch")()
			except Exception:
				pBLogger.exception(
					"Error importing physbiblio.webimport.%s"%method)
		self.loaded = True

	def retrieveUrlFirstFrom(self, search, method):
		"""Calls the function retrieveUrlFirst
		given the subclass method.

		Parameters:
			search: the search string
			method: the key of the method in `self.webSearch`

		Output:
			None in the default implementation (must be subclassed)
		"""
		try:
			return getattr(self.webSearch[method], retrieveUrlFirst)(search)
		except KeyError:
			pBLogger.warning("The method '%s' is not available!"%method)
			return ""

	def retrieveUrlAllFrom(self, search, method):
		"""Calls the function retrieveUrlAll given the subclass method.

		Parameters:
			search: the search string
			method: the key of the method in `self.webSearch`

		Output:
			None in the default implementation (must be subclassed)
		"""
		try:
			return getattr(self.webSearch[method], retrieveUrlAll)(search)
		except KeyError:
			pBLogger.warning("The method '%s' is not available!"%method)
			return ""


physBiblioWeb = WebInterf()
physBiblioWeb.loadInterfaces()
