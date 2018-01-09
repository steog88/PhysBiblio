import sys,re,os
from urllib2 import Request
import urllib2
from physbiblio.webimport.webInterf import *

class webSearch(webInterf):
	def __init__(self):
		webInterf.__init__(self)
		self.name="ADS-NASA fetcher"
		self.url="http://adsabs.harvard.edu/doi/"
		self.urlArgs={
			"data_type":"BIBTEX"}
		
	def retrieveUrlFirst(self,string):
		#print "[inspire] search "+string+':'
		#self.urlArgs["p"]=string
		#url=self.createUrl()
		#print url
		#text=self.textFromUrl(url)
		#try:
			#i1=text.find("<pre>")
			#i2=text.find("</pre>")
			#if i1>0 and i2>0:
				#bibtex=text[i1+5:i2]
			#else:
				#bibtex=""
			#return bibtex
		#except:
			return ""
		
	def retrieveUrlAll(self,string):
		#print "[inspire] search "+string+':'
		#self.urlArgs["p"]=string
		#url=self.createUrl()
		#print url
		#text=self.textFromUrl(url)
		#try:
			#i1=text.find("<pre>")
			#i2=text.rfind("</pre>")
			#if i1>0 and i2>0:
				#bibtex=text[i1+5:i2]
			#else:
				#bibtex=""
			#return bibtex.replace("<pre>","").replace("</pre>","")
		#except:
			return ""
