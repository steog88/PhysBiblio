import sys,re,os
from urllib2 import Request
import urllib2, traceback
try:
	import pybiblio.errors as pBErrorManager
except ImportError:
	print("Could not find pybiblio.errors and its contents: configure your PYTHONPATH!")
	print(traceback.format_exc())
from pybiblio.webimport.webInterf import *
from pybiblio.parse_accents import *

class webSearch(webInterf):
	"""doi web interface"""
	def __init__(self):
		"""configuration"""
		webInterf.__init__(self)
		self.name = "doi"
		self.description = "Doi fetcher"
		self.url = "http://dx.doi.org/"
		self.headers = {'accept': 'application/x-bibtex'}
		
	def createUrl(self, doi):
		"""doi url behaves differently from other urls"""
		return self.url + doi
		
	def retrieveUrlFirst(self,string):
		"""first (and only) bibtex result for a given doi"""
		url = self.createUrl(string)
		print("[doi] search %s -> %s"%(string, url))
		text = self.textFromUrl(url, self.headers)
		try:
			return text[:]
		except:
			pBErrorManager("[doi] -> ERROR: impossible to get results")
			return ""
		
	def retrieveUrlAll(self,string):
		"""first (and only) bibtex result for a given doi (redirect to retrieveUrlFirst)"""
		return self.retrieveUrlFirst(string)
