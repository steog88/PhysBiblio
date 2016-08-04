import sys,re,os
from urllib2 import Request
import urllib2
from pybiblio.webimport.webInterf import *

class webSearch(webInterf):
	def __init__(self):
		webInterf.__init__(self)
		self.url=""
		self.urlArgs={}
		
	def retrieveUrlFirst(self,string):
		#print "[doiToBibtex] search "+string+':'
		#self.urlArgs["p"]=string
		#url=self.createUrl()
		#print url
		#text=self.textFromUrl(url)
		#i1=text.find("<pre>")
		#i2=text.find("</pre>")
		#if i1>0 and i2>0:
			#bibtex=text[i1+5:i2]
		#else:
			#bibtex=""
		#return bibtex
		return ""
		
	def retrieveUrlAll(self,string):
		#print "[doiToBibtex] search "+string+':'
		#self.urlArgs["p"]=string
		#url=self.createUrl()
		#print url
		#text=self.textFromUrl(url)
		#i1=text.find("<pre>")
		#i2=text.rfind("</pre>")
		#if i1>0 and i2>0:
			#bibtex=text[i1+5:i2]
		#else:
			#bibtex=""
		#return bibtex.replace("<pre>","").replace("</pre>","")
		return ""






        #try {
            #URL doiURL = new URL(doi.get().getURIAsASCIIString());

            #// BibTeX data
            #URLDownload download = new URLDownload(doiURL);
            #download.addParameters("Accept", "application/x-bibtex");
            #String bibtexString = download.downloadToString(StandardCharsets.UTF_8);
            #bibtexString = cleanupEncoding(bibtexString);

            #// BibTeX entry
            #BibEntry entry = BibtexParser.singleFromString(bibtexString);

            #if (entry == null) {
                #return Optional.empty();
            #}
            #// Optionally re-format BibTeX entry
            #formatTitleField(entry);

            #return Optional.of(entry);
        }
