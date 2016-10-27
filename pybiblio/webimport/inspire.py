import sys,re,os
from urllib2 import Request
import urllib2
from pybiblio.webimport.webInterf import *

class webSearch(webInterf):
	def __init__(self):
		webInterf.__init__(self)
		self.name="inspire"
		self.description="INSPIRE fetcher"
		self.url="http://inspirehep.net/search"
		self.urlArgs={
			"action_search":"Search",
			"sf":"",
			"so":"d",
			"rm":"",
			"rg":"1000",
			"sc":"0",
			"of":"hx"#for bibtex format ---- hb for standard format, for retrieving inspireid
			}
		
	def retrieveUrlFirst(self,string):
		self.urlArgs["p"]=string
		url=self.createUrl()
		print "[inspire] search %s -> %s"%(string, url)
		text=self.textFromUrl(url)
		try:
			i1=text.find("<pre>")
			i2=text.find("</pre>")
			if i1>0 and i2>0:
				bibtex=text[i1+5:i2]
			else:
				bibtex=""
			return bibtex
		except:
			print "[inspire] -> ERROR: impossible to get results"
			return ""
		
	def retrieveUrlAll(self,string):
		self.urlArgs["p"]=string
		url=self.createUrl()
		print "[inspire] search %s -> %s"%(string,url)
		text=self.textFromUrl(url)
		try:
			i1=text.find("<pre>")
			i2=text.rfind("</pre>")
			if i1>0 and i2>0:
				bibtex=text[i1+5:i2]
			else:
				bibtex=""
			return bibtex.replace("<pre>","").replace("</pre>","")
		except:
			print "[inspire] -> ERROR: impossible to get results"
			return ""
