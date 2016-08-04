import sys,re,os
from urllib2 import Request
import urllib2
from pybiblio.webimport.webInterf import *

class webSearch(webInterf):
	def __init__(self):
		webInterf.__init__(self)
		self.url="http://www.ebook.de/de/tools/isbn2bibtex"
		self.urlArgs={}
		
	def retrieveUrlFirst(self,string):
		print "[isbnToBibtex] search "+string+':'
		self.urlArgs["isbn"]=string
		url=self.createUrl()
		print url
		text=self.textFromUrl(url)
		#i1=text.find("<pre>")
		#i2=text.find("</pre>")
		#if i1>0 and i2>0:
			#bibtex=text[i1+5:i2]
		#else:
			#bibtex=""
		#return bibtex
		return ""
		
	def retrieveUrlAll(self,string):
		print "[isbnToBibtex] search "+string+':'
		self.urlArgs["isbn"]=string
		url=self.createUrl()
		print url
		text=self.textFromUrl(url)
		#i1=text.find("<pre>")
		#i2=text.find("</pre>")
		#if i1>0 and i2>0:
			#bibtex=text[i1+5:i2]
		#else:
			#bibtex=""
		#return bibtex.replace("<pre>","").replace("</pre>","")
		return ""



        #try(InputStream source = url.openStream()) {
            #String bibtexString;
            #try(Scanner scan = new Scanner(source)) {
                #bibtexString = scan.useDelimiter("\\A").next();
            #}

            #BibEntry entry = BibtexParser.singleFromString(bibtexString);
            #if (entry != null) {
                #// Optionally add curly brackets around key words to keep the case
                #entry.getFieldOptional(FieldName.TITLE).ifPresent(title -> {
                    #// Unit formatting
                    #if (Globals.prefs.getBoolean(JabRefPreferences.USE_UNIT_FORMATTER_ON_SEARCH)) {
                        #title = unitsToLatexFormatter.format(title);
                    #}

                    #// Case keeping
                    #if (Globals.prefs.getBoolean(JabRefPreferences.USE_CASE_KEEPER_ON_SEARCH)) {
                        #title = protectTermsFormatter.format(title);
                    #}
                    #entry.setField(FieldName.TITLE, title);
                #});
                #inspector.addEntry(entry);
                #return true;
            #}
            #return false;
        }
