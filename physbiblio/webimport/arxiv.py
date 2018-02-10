import sys,re,os
from urllib2 import Request
import urllib2
import feedparser, traceback
try:
	from physbiblio.errors import pBErrorManager
except ImportError:
	print("Could not find physbiblio.errors and its contents: configure your PYTHONPATH!")
	print(traceback.format_exc())
from bibtexparser.bibdatabase import BibDatabase
from physbiblio.webimport.webInterf import *
from physbiblio.parse_accents import *
from physbiblio.bibtexwriter import pbWriter

class webSearch(webInterf):
	"""arxiv.org search"""
	def __init__(self):
		"""constants"""
		webInterf.__init__(self)
		self.name = "arXiv"
		self.description = "arXiv fetcher"
		self.url = "http://export.arxiv.org/api/query"
		self.urlArgs = {
			"start":"0"}
		
	def retrieveUrlFirst(self, string, searchType = "all", **kwargs):
		return self.arxivRetriever(string, searchType, additionalArgs = {"max_results":"1"}, **kwargs)
	def retrieveUrlAll(self, string, searchType = "all", **kwargs):
		return self.arxivRetriever(string, searchType, **kwargs)

	def arxivRetriever(self, string, searchType = "all", additionalArgs = None, fullDict = False):
		"""reads the feed content into a dictionary, used to return a bibtex"""
		if additionalArgs:
			for k, v in additionalArgs.iteritems():
				self.urlArgs[k] = v
		self.urlArgs["search_query"] = searchType + ":" + string
		url = self.createUrl()
		print("[arxiv] search %s:%s -> %s"%(searchType, string, url))
		text = parse_accents_str(self.textFromUrl(url))
		try:
			data = feedparser.parse(text)
			db = BibDatabase()
			db.entries = []
			for entry in data['entries']:
				tmp = {}
				idArx = entry['id'].replace("http://arxiv.org/abs/", "")
				pos = idArx.find("v")
				if pos >= 0:
					idArx = idArx[0:pos]
				tmp["ENTRYTYPE"] = "article"
				tmp["ID"] = idArx
				tmp["archiveprefix"] = "arXiv"
				tmp["title"] = entry['title']
				tmp["arxiv"] = idArx
				try:
					tmp["doi"] = entry['arxiv_doi']
				except KeyError, e:
					print("[arXiv] -> KeyError: ", e)
				tmp["abstract"] = entry['summary']
				tmp["authors"] = " and ".join([ au["name"] for au in entry['authors']])
				tmp["primaryclass"] = entry['arxiv_primary_category']['term']
				identif = re.compile("([0-9]{4}.[0-9]{4,5}|[0-9]{7})*")
				try:
					for t in identif.finditer(tmp["arxiv"]):
						if len(t.group()) > 0:
							e = t.group()
							a = e[0:2]
							if int(a) > 80:
								tmp["year"] = "19" + a
							else:
								tmp["year"] = "20" + a
				except:
					print("[DB] -> Error in converting year")
				db.entries.append(tmp)
			if fullDict:
				return pbWriter.write(db), tmp
			else:
				return pbWriter.write(db)
		except:
			pBErrorManager("[arXiv] -> ERROR: impossible to get results", traceback)
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
