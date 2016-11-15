import sys,re,os
from urllib2 import Request
import urllib2
from pybiblio.config import pbConfig
from pybiblio.webimport.webInterf import *
from pybiblio.parse_accents import *

class webSearch(webInterf):
	"""inspire methods"""
	def __init__(self):
		"""configurations"""
		webInterf.__init__(self)
		self.name = "inspire"
		self.description = "INSPIRE fetcher"
		self.url = pbConfig.inspireSearchBase
		self.urlRecord = pbConfig.inspireRecord
		self.urlArgs = {
			"action_search": "Search",
			"sf": "",
			"so": "d",
			"rm": "",
			"rg": "1000",
			"sc": "0",
			"of": "hx"#for bibtex format ---- hb for standard format, for retrieving inspireid
			}
		self.urlRecordExt = {
			"bibtex": "/export/hx",
		}
		
	def urlOfRecord(self, inspireID, extension = None):
		"""get url for a given record"""
		if extension and extension in self.urlRecordExt.keys():
			ext = self.urlRecordExt[extension]
		else:
			ext = ""
		return self.urlRecord + inspireID + ext
		
	def retrieveUrlFirst(self, string):
		"""retrieve the first entry from a html page"""
		self.urlArgs["p"] = "\"" + string + "\""
		url = self.createUrl()
		print "[inspire] search %s -> %s"%(string, url)
		text = self.textFromUrl(url)
		try:
			i1 = text.find("<pre>")
			i2 = text.find("</pre>")
			if i1 > 0 and i2 > 0:
				bibtex = text[i1 + 5 : i2]
			else:
				bibtex = ""
			return parse_accents_str(bibtex)
		except:
			print "[inspire] -> ERROR: impossible to get results"
			return ""
		
	def retrieveUrlAll(self, string):
		"""retrieve all the entries from a html page"""
		self.urlArgs["p"] = "\"" + string + "\""
		url = self.createUrl()
		print "[inspire] search %s -> %s"%(string, url)
		text = self.textFromUrl(url)
		try:
			i1 = text.find("<pre>")
			i2 = text.rfind("</pre>")
			if i1 > 0 and i2 > 0:
				bibtex = text[i1 + 5 : i2]
			else:
				bibtex = ""
			return parse_accents_str(bibtex.replace("<pre>", "").replace("</pre>", ""))
		except:
			print "[inspire] -> ERROR: impossible to get results"
			return ""
	
	def retrieveInspireID(self, string, number = None):
		"""read the inspire ID of a given entry from the html page"""
		i = 0
		self.urlArgs["p"] = "\"" + string + "\""
		self.urlArgs["of"] = "hb" #not bibtex but standard
		url = self.createUrl()
		self.urlArgs["of"] = "hx" #restore
		print "[inspire] search ID of %s -> %s"%(string, url)
		text = self.textFromUrl(url)
		try:
			searchID = re.compile('titlelink(.*)?(http|https)://inspirehep.net/record/([0-9]*)?">')
			for q in searchID.finditer(text):
				if len(q.group()) > 0:
					if number is None or i == number:
						inspireID = q.group(3)
						break
					else:
						i += 1
			print "[inspire] found: %s"%inspireID
			return inspireID
		except:
			print "[inspire] -> ERROR: impossible to get results"
			return ""
