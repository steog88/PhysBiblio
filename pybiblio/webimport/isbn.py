#import sys,re,os
#from urllib2 import Request
#import urllib2
from pybiblio.webimport.webInterf import *
from pybiblio.parse_accents import *

class webSearch(webInterf):
	def __init__(self):
		webInterf.__init__(self)
		self.name = "isbn"
		self.description = "ISBN to bibtex"
		self.url = "http://www.ebook.de/de/tools/isbn2bibtex"
		self.urlArgs = {}
		
	def retrieveUrlFirst(self,string):
		self.urlArgs["isbn"] = string
		url = self.createUrl()
		print("[isbn] search %s -> %s"%(string, url))
		text = self.textFromUrl(url)
		try:
			return parse_accents_str(text[:])
		except:
			print("[isbn] -> ERROR: impossible to get results")
			return ""
		
	def retrieveUrlAll(self,string):
		return self.retrieveUrlFirst(string)

