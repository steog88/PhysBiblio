import sys,re,os
from urllib2 import Request
import urllib2
from pybiblio.webimport.webInterf import *
from pybiblio.parse_accents import *

class webSearch(webInterf):
	def __init__(self):
		webInterf.__init__(self)
		self.name = "doi"
		self.description = "Doi fetcher"
		self.url = "http://dx.doi.org/"
		self.headers = {'accept': 'application/x-bibtex'}
		
	def createUrl(self, doi):
		return self.url + doi
		
	def retrieveUrlFirst(self,string):
		url = self.createUrl(string)
		print("[doi] search %s -> %s"%(string, url))
		text = self.textFromUrl(url, self.headers)
		try:
			return text[:]
		except:
			print("[doi] -> ERROR: impossible to get results")
			return ""
		
	def retrieveUrlAll(self,string):
		return self.retrieveUrlFirst(string)
