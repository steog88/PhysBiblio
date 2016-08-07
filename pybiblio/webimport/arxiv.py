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
		self.name="arXiv fetcher"
		self.url="http://export.arxiv.org/api/query"
		self.urlArgs={
			"start":"0"}
		
	def retrieveUrlFirst(self,string,searchType="all"):
		return self.arxivRetriever(string,searchType,additionalArgs={"max_results":"1"})
	def retrieveUrlAll(self,string,searchType="all"):
		return self.arxivRetriever(string,searchType)

	def arxivRetriever(self,string,searchType="all",additionalArgs=None):
		if additionalArgs:
			for k,v in additionalArgs.iteritems():
				self.urlArgs[k]=v
		print "[arxiv] search "+searchType+":"+string+':'
		self.urlArgs["search_query"]=searchType+":"+string
		url=self.createUrl()
		print url
		text=self.textFromUrl(url)
		try:
			data=feedparser.parse(text)
			db=BibDatabase()
			db.entries=[]
			for entry in data['entries']:
				tmp={}
				idArx=entry['id'].replace("http://arxiv.org/abs/","")
				pos=idArx.find("v")
				if pos>=0:
					idArx=idArx[0:pos]
				tmp["ENTRYTYPE"]="article"
				tmp["ID"]=idArx
				tmp["archiveprefix"]="arXiv"
				tmp["title"]=entry['title']
				tmp["arxiv"]=idArx
				try:
					tmp["doi"]=entry['arxiv_doi']
				except KeyError,e:
					print "KeyError: ",e
					pass
				tmp["abstract"]=entry['summary']
				tmp["authors"]=" and ".join([ au["name"] for au in entry['authors']])
				tmp["primaryclass"]=entry['arxiv_primary_category']['term']
				db.entries.append(tmp)
			writer = BibTexWriter()
			writer.indent = ' '
			writer.comma_first = False
			return writer.write(db)
		except:
			print "error!"
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
