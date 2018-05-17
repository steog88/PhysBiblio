"""
Module that deals with importing info from the arXiv API.

Uses feedparser module to read the page content.

This file is part of the physbiblio package.
"""
import re, traceback
import feedparser
try:
	from physbiblio.errors import pBLogger
	from bibtexparser.bibdatabase import BibDatabase
	from physbiblio.webimport.webInterf import *
	from physbiblio.parse_accents import *
	from physbiblio.bibtexwriter import pbWriter
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
	print(traceback.format_exc())
	raise

class webSearch(webInterf):
	"""Subclass of webInterf that can connect to arxiv.org to perform searches"""
	def __init__(self):
		"""
		Initializes the class variables using the webInterf constructor.

		Define additional specific parameters for the arxiv.org API.
		"""
		webInterf.__init__(self)
		self.name = "arXiv"
		self.description = "arXiv fetcher"
		self.url = "http://export.arxiv.org/api/query"
		self.urlArgs = {
			"start":"0"}
		
	def retrieveUrlFirst(self, string, searchType = "all", **kwargs):
		"""
		Retrieves the first result from the content of the given web page.
		The function calls arxivRetriever which will do the job.

		Parameters:
			string: the search string
			searchType: the search method in arxiv API (default 'all')

		Output:
			returns the bibtex string built from arxivRetriever
		"""
		return self.arxivRetriever(string, searchType, additionalArgs = {"max_results":"1"}, **kwargs)

	def retrieveUrlAll(self, string, searchType = "all", **kwargs):
		"""
		Retrieves all the results from the content of the given web page.
		The function calls arxivRetriever which will do the job.

		Parameters:
			string: the search string
			searchType: the search method in arxiv API (default 'all')

		Output:
			returns the bibtex string built from arxivRetriever
		"""
		return self.arxivRetriever(string, searchType, additionalArgs = {"max_results": pbConfig.params["maxArxivResults"]}, **kwargs)

	def arxivRetriever(self, string, searchType = "all", additionalArgs = None, fullDict = False):
		"""
		Reads the feed content got from arxiv into a dictionary, used to return a bibtex.

		Parameters:
			string: the search string
			searchType: the search method in arxiv API (default 'all'). The possible values are:
				ti->	Title
				au	->	Author
				abs	->	Abstract
				co	->	Comment
				jr	->	Journal Reference
				cat	->	Subject Category
				rn	->	Report Number
				id	->	Id (use id_list instead)
				all	->	All of the above
			additionalArgs: a dictionary of additional arguments that can be passed to self.urlArgs (default None)
			fullDict (logical): return the bibtex dictionary in addition to the bibtex text (default False)

		Output:
			the bibtex text
			(optional, depending on fullDict): the bibtex Dictionary
		"""
		if additionalArgs:
			for k, v in additionalArgs.items():
				self.urlArgs[k] = v
		self.urlArgs["search_query"] = searchType + ":" + string
		url = self.createUrl()
		pBLogger.info("Search '%s:%s' -> %s"%(searchType, string, url))
		text = parse_accents_str(self.textFromUrl(url))
		try:
			data = feedparser.parse(text)
			db = BibDatabase()
			db.entries = []
			dictionaries = []
			for entry in data['entries']:
				dictionary = {}
				idArx = entry['id'].replace("http://arxiv.org/abs/", "")
				pos = idArx.find("v")
				if pos >= 0:
					idArx = idArx[0:pos]
				dictionary["ENTRYTYPE"] = "article"
				dictionary["ID"] = idArx
				dictionary["archiveprefix"] = "arXiv"
				dictionary["title"] = entry['title']
				dictionary["arxiv"] = idArx
				try:
					dictionary["doi"] = entry['arxiv_doi']
				except KeyError as e:
					pBLogger.debug("KeyError: %s"%e)
				dictionary["abstract"] = entry['summary'].replace("\n", " ")
				dictionary["authors"] = " and ".join([ au["name"] for au in entry['authors']])
				dictionary["primaryclass"] = entry['arxiv_primary_category']['term']
				identif = re.compile("([0-9]{4}.[0-9]{4,5}|[0-9]{7})*")
				try:
					for t in identif.finditer(dictionary["arxiv"]):
						if len(t.group()) > 0:
							e = t.group()
							a = e[0:2]
							if int(a) > 80:
								dictionary["year"] = "19" + a
							else:
								dictionary["year"] = "20" + a
				except Exception:
					pBLogger.warning("Error in converting year")
				db.entries.append(dictionary)
				dictionaries.append(dictionary)
			if fullDict:
				dictionary = dictionaries[0]
				for d in dictionaries:
					if string in d["arxiv"]:
						dictionary = d
				return pbWriter.write(db), dictionary
			else:
				return pbWriter.write(db)
		except Exception:#intercept all other possible errors
			pBLogger.exception("Impossible to get results")
			if fullDict:
				return "",  {}
			else:
				return ""
