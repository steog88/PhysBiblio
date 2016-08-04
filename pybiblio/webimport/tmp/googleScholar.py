import sys,re,os
from urllib2 import Request
import urllib2
from pybiblio.webimport.webInterf import *

class webSearch(webInterf):
	def __init__(self):
		webInterf.__init__(self)
		self.url="https://scholar.google.com//scholar"
		self.urlArgs={
			"as_q":"",
			"as_occt":"title"}
		
	def retrieveUrlFirst(self,string):
		print "[google scholar] search "+string+':'
		self.urlArgs["as_epq"]=string
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
		print "[inspire] search "+string+':'
		self.urlArgs["p"]=string
		url=self.createUrl()
		print url
		text=self.textFromUrl(url)
		#i1=text.find("<pre>")
		#i2=text.rfind("</pre>")
		#if i1>0 and i2>0:
			#bibtex=text[i1+5:i2]
		#else:
			#bibtex=""
		#return bibtex.replace("<pre>","").replace("</pre>","")
		return ""






        #Document doc = Jsoup.connect(url)
                #.userAgent("Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0") // don't identify as a crawler
                #.get();
        #// Check results for PDF link
        #// TODO: link always on first result or none?
        #for (int i = 0; i < NUM_RESULTS; i++) {
            #Elements link = doc.select(String.format("#gs_ggsW%s a", i));

            #if (link.first() != null) {
                #String s = link.first().attr("href");
                #// link present?
                #if (!"".equals(s)) {
                    #// TODO: check title inside pdf + length?
                    #// TODO: report error function needed?! query -> result
                    #LOGGER.info("Fulltext PDF found @ Google: " + s);
                    #pdfLink = Optional.of(new URL(s));
                    #break;
                #}
            #}
        #}

        #return pdfLink;
    #}
#}
