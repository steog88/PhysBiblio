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
		self.urlRss = "http://export.arxiv.org/rss/"
		self.urlArgs = {
			"start":"0"}
		self.categories = {
			"astro-ph": ["", "CO", "EP", "GA", "HE", "IM", "SR"],
			"cond-mat": ["dis-nn", "mes-hall", "mtrl-sci", "other", "quant-gas", "soft", "stat-mech", "str-el", "supr-con"],
			"cs": ["AI", "AR", "CC", "CE", "CG", "CL", "CR", "CV", "CY", "DB", "DC", "DL", "DM", "DS", "ET", "FL", "GL", "GR", "GT", "HC", "IR", "IT", "LG", "LO", "MA", "MM", "MS", "NA", "NE", "NI", "OH", "OS", "PF", "PL", "RO", "SC", "SD", "SE", "SI", "SY"],
			"econ": ["EM"],
			"eess": ["AS", "IV", "SP"],
			"gr-qc": [""],
			"hep-ex": [""],
			"hep-lat": [""],
			"hep-ph": [""],
			"hep-th": [""],
			"math": ["AC", "AG", "AP", "AT", "CA", "CO", "CT", "CV", "DG", "DS", "FA", "GM", "GN", "GR", "GT", "HO", "IT", "KT", "LO", "MG", "MP", "NA", "NT", "OA", "OC", "PR", "QA", "RA", "RT", "SG", "SP", "ST"],
			"math-ph": [""],
			"nlin": ["AO", "CD", "CG", "PS", "SI"],
			"nucl-ex": [""],
			"nucl-th": [""],
			"physics": ["acc-ph", "ao-ph", "app-ph", "atm-clus", "atom-ph", "bio-ph", "chem-ph", "class-ph", "comp-ph", "data-an", "ed-ph", "flu-dyn", "gen-ph", "geo-ph", "hist-ph", "ins-det", "med-ph", "optics", "plasm-ph", "pop-ph", "soc-ph", "space-ph"],
			"q-bio": ["BM", "CB", "GN", "MN", "NC", "OT", "PE", "QM", "SC", "TO"],
			"q-fin": ["CP", "EC", "GN", "MF", "PM", "PR", "RM", "ST", "TR"],
			"quant-ph": [""],
			"stat": ["AP", "CO", "ME", "ML", "OT", "TH"]
			}
		
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

	def arxivDaily(self, category):
		"""
		Read daily RSS feed for a given category
		"""
		if "." in category:
			main, sub = category.split(".")
		else:
			main = category
			sub = ""
		url = self.urlRss
		if main not in self.categories.keys():
			pBLogger.warning("Main category not found: %s"%main)
			return False
		else:
			url += main
		if sub != "" and sub not in self.categories[main]:
			pBLogger.warning("Sub category not found: %s"%sub)
			return False
		elif sub != "" and sub in self.categories[main]:
			url += "." + sub
		pBLogger.info(url)
		text = self.textFromUrl(url)
		if text is None:
			pBLogger.warning("Url is empty!")
			return False
		author = re.compile('(>|&gt;)([^/]*)(</a>|&lt;/a&gt;)')
		additionalInfo = re.compile(' \(arXiv:([0-9\.v]*) \[([\-\.a-zA-Z]*)\]([ A-Z]*)\)')
		try:
			data = feedparser.parse(parse_accents_str(text.decode("utf-8")))
			entries = []
			for element in data.entries:
				tmp = {}
				tmp["eprint"] = element["id"].split("/")[-1]
				tmp["abstract"] = element["summary"].replace("\n", " ").replace("<p>", "").replace("</p>", "")
				tmp["authors"] = [ m.group(2) for m in author.finditer(element["authors"][0]["name"]) if m != "" ]
				tmp["cross"] = "CROSS LISTED" in element["title"]
				tmp["replacement"] = "UPDATED" in element["title"]
				tmp["mainCat"] = [m.group(2) for m in additionalInfo.finditer(element["title"]) if m != ""][0]
				tmp["version"] = [m.group(1) for m in additionalInfo.finditer(element["title"]) if m != ""][0]
				parenthesis = [m.group() for m in additionalInfo.finditer(element["title"]) if m != ""][0]
				tmp["title"] = element["title"].replace(parenthesis, "")
				entries.append(tmp)
			return entries
		except Exception:
			pBLogger.error("Cannot parse arxiv RSS feed:\n%s"%text, exc_info = True)
			return False
