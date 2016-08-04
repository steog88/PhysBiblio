import sys,re,os
from urllib2 import Request
import urllib2
import feedparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from pybiblio.webimport.webInterf import *

class webSearch(webInterf):
	def __init__(self):
		webInterf.__init__(self)
		self.url="http://export.arxiv.org/api/query"
		self.urlArgs={
			"start":"0"}
		
	def retrieveUrlFirst(self,string):
		print "[arxiv] search "+string+':'
		self.urlArgs["search_query"]=string
		self.urlArgs["max_results"]="1"
		url=self.createUrl()
		print url
		text=self.textFromUrl(url)
		try:
			data=feedparser.parse(text)
			print data['entries'][0].keys()
			tmp={}
			idArx=data['entries'][0]['id'].replace("http://arxiv.org/abs/","")
			pos=idArx.find("v")
			if pos>=0:
				idArx=idArx[0:pos]
			tmp["ENTRYTYPE"]="article"
			tmp["ID"]=idArx
			tmp["archiveprefix"]="arXiv"
			tmp["title"]=data['entries'][0]['title']
			tmp["arxiv"]=idArx
			tmp["doi"]=data['entries'][0]['arxiv_doi']
			tmp["abstract"]=data['entries'][0]['summary']
			tmp["authors"]=" and ".join([ au["name"] for au in data['entries'][0]['authors']])
			tmp["primaryclass"]=data['entries'][0]['arxiv_primary_category']['term']
			db=BibDatabase()
			db.entries = [tmp]
			writer = BibTexWriter()
			writer.indent = ' '
			writer.comma_first = False
			return writer.write(db)
		except KeyError,e:
			print "KeyError: "+e
			pass
		except:
			return ""
		
	def retrieveUrlAll(self,string):
		#print "[arxiv] search "+string+':'
		#self.urlArgs["search_query"]=string
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



#Table: search_query field prefixes
#ti	Title
#au	Author
#abs	Abstract
#co	Comment
#jr	Journal Reference
#cat	Subject Category
#rn	Report Number
#id	Id (use id_list instead)
#all	All of the above
