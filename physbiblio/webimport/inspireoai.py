"""Use INSPIRE-HEP OAI API to collect information on single papers
(given the identifier) or to harvest updates in a given time period.

This file is part of the physbiblio package.
"""
import sys
import time
import codecs
import re

if sys.version_info[0] < 3:
	#needed to set utf-8 as encoding
	reload(sys)
	sys.setdefaultencoding('utf-8')
	from httplib import IncompleteRead
	from urllib2 import URLError
else:
	from http.client import IncompleteRead
	from urllib.request import URLError

import datetime
import traceback

import bibtexparser
from oaipmh.client import Client
from oaipmh.error import ErrorBase
from oaipmh.metadata import MetadataRegistry

if sys.version_info[0] < 3:
	from StringIO import StringIO
else:
	from io import StringIO
from lxml.etree import tostring
from pymarc import marcxml, MARCWriter, field
from oaipmh import metadata
from socket import error as SocketError

try:
	from physbiblio.errors import pBLogger
	from physbiblio.config import pbConfig
	from physbiblio.webimport.webInterf import WebInterf
	from physbiblio.webimport.arxiv import getYear
	from physbiblio.parseAccents import parse_accents_str
	from bibtexparser.bibdatabase import BibDatabase
	from physbiblio.bibtexWriter import pbWriter
except ImportError:
	print("Could not find physbiblio and its modules!")
	print(traceback.format_exc())
	raise


def safe_list_get(l, idx, default=""):
	"""Safely get an element from a list.
	No error if it doesn't exist...

	Parameters:
		l: the list from which to get the element
		idx: the index
		default: the default return value if `l[idx]` does not exist
	"""
	if l is not None:
		try:
			return l[idx]
		except IndexError:
			return default
	else:
		return default


def get_journal_ref_xml(marcxml):
	"""Read the marcxml record and write the info on the publication

	Parameter:
		marcxml: the marcxml record to read
	"""
	p = []
	y = []
	v = []
	c = []
	m = []
	x = []
	t = []
	w = []
	if marcxml["773"] is not None:
		for q in marcxml.get_fields("773"):
			#journal name (even if submitted to only)
			p.append(parse_accents_str(q["p"]))
			v.append(parse_accents_str(q["v"]))	#volume
			y.append(parse_accents_str(q["y"]))	#year
			c.append(parse_accents_str(q["c"]))	#pages

			#Erratum, Addendum, Publisher note
			m.append(parse_accents_str(q["m"]))

			#freetext journal/book info
			x.append(parse_accents_str(q["x"]))
			#for conf papers: presented at etc, freetext or KB?
			t.append(parse_accents_str(q["t"]))
			#for conf papers: conference code
			w.append(parse_accents_str(q["w"]))
	return p, v, y, c, m, x, t, w


class MARCXMLReader(object):
	"""Returns the PyMARC record from the OAI structure for MARC XML"""

	def __call__(self, element):
		"""Call the xml parser and return the records

		Parameter:
			element: the xml text to read
		"""
		handler = marcxml.XmlHandler()
		if sys.version_info[0] < 3:
			marcxml.parse_xml(StringIO(tostring(element[0], encoding='UTF-8')),
				handler)
		else:
			marcxml.parse_xml(StringIO(tostring(element[0], encoding=str)),
				handler)
		return handler.records[0]


marcxml_reader = MARCXMLReader()

registry = metadata.MetadataRegistry()
registry.registerReader('marcxml', marcxml_reader)


class WebSearch(WebInterf):
	"""Subclass of WebInterf that can connect to INSPIRE-HEP
	to perform searches using the OAI API
	"""

	def __init__(self):
		"""Initializes the class variables using
		the WebInterf constructor.

		Define additional specific parameters
		for the INSPIRE-HEP OAI API.
		"""
		WebInterf.__init__(self)
		self.name = "inspireoai"
		self.description = "INSPIRE OAI interface"
		self.url = "https://inspirehep.net/oai2d"
		self.oai = Client(self.url, registry)
		self.correspondences = [
			["id", "inspire"],
			["year", "year"],
			["arxiv", "arxiv"],
			# ["oldkeys", "old_keys"],
			["firstdate", "firstdate"],
			["pubdate", "pubdate"],
			["doi", "doi"],
			["ads", "ads"],
			["isbn", "isbn"],
			["bibtex", "bibtex"],
			["link", "link"],
		]
		self.bibtexFields = [
			"author", "title",
			"journal", "volume", "year", "pages",
			"arxiv", "primaryclass", "archiveprefix", "eprint",
			"doi", "isbn",
			"school", "reportnumber", "booktitle", "collaboration"]

	def retrieveUrlFirst(self, string):
		"""The OAI interface is not for string searches:
		use the retrieveOAIData function if you have the INSPIRE ID
		of the desired record
		"""
		pBLogger.warning("Inspireoai cannot search strings in the DB")
		return ""

	def retrieveUrlAll(self, string):
		"""The OAI interface is not for string searches:
		use the retrieveOAIData function if you have the INSPIRE ID
		of the desired record
		"""
		pBLogger.warning("Inspireoai cannot search strings in the DB")
		return ""

	def readRecord(self, record, readConferenceTitle=False):
		"""Read the content of a marcxml record
		to return a bibtex string

		Parameters:
			record: the marcxml record to read
			readConferenceTitle (default False): if True, look for
				the proceedings info to get the title of the conference

		Output:
			a dictionary with the obtained fields
		"""
		tmpDict = {}
		record.to_unicode = True
		record.force_utf8 = True
		arxiv = ""
		tmpOld = []
		try:
			tmpDict["doi"] = None
			for q in record.get_fields('024'):
				if q["2"] == "DOI":
					tmpDict["doi"] = q["a"]
		except Exception as e:
			pBLogger.warning("Error in readRecord!", exc_info=True)
		try:
			tmpDict["arxiv"] = None
			tmpDict["bibkey"] = None
			tmpDict["ads"] = None
			for q in record.get_fields('035'):
				if q["9"] == "arXiv":
					tmp = q["a"]
					if tmp is not None:
						arxiv = tmp.replace("oai:arXiv.org:", "")
					else:
						arxiv = ""
					tmpDict["arxiv"] = arxiv
				if q["9"] == "SPIRESTeX" or q["9"] == "INSPIRETeX":
					if q["z"]:
						tmpDict["bibkey"] = q["z"]
					elif q["a"]:
						tmpOld.append(q["a"])
				if q["9"] == "ADS":
					if q["a"] is not None:
						tmpDict["ads"] = q["a"]
		except (IndexError, TypeError) as e:
			pBLogger.warning("Error in readRecord!", exc_info=True)
		if tmpDict["bibkey"] is None and len(tmpOld) > 0:
			tmpDict["bibkey"] = tmpOld[0]
			tmpOld = []
		try:
			j, v, y, p, m, x, t, w = get_journal_ref_xml(record)
			tmpDict["journal"] = j[0]
			tmpDict["volume"] = v[0]
			tmpDict["year"] = y[0]
			tmpDict["pages"] = p[0]
			if w[0] is not None:
				conferenceCode = w[0]
			else:
				conferenceCode = None
		except IndexError:
			tmpDict["journal"] = None
			tmpDict["volume"] = None
			tmpDict["year"] = None
			tmpDict["pages"] = None
			conferenceCode = None
		try:
			firstdate = record["269"]
			if firstdate is not None:
				firstdate = firstdate["c"]
			else:
				firstdate = record["961"]
				if firstdate is not None:
					firstdate = firstdate["x"]
			tmpDict["firstdate"] = firstdate
		except TypeError:
			tmpDict["firstdate"] = None
		try:
			tmpDict["pubdate"] = record["260"]["c"]
		except TypeError:
			tmpDict["pubdate"] = None
		try:
			tmpDict["author"] = record["100"]["a"]
		except TypeError:
			tmpDict["author"] = ""
		try:
			addAuthors = 0
			if (len(record.get_fields("700")) >
					pbConfig.params["maxAuthorSave"] - 1):
				tmpDict["author"] += " and others"
			else:
				for r in record.get_fields("700"):
					addAuthors += 1
					if addAuthors > pbConfig.params["maxAuthorSave"]:
						tmpDict["author"] += " and others"
						break
					tmpDict["author"] += " and %s"%r["a"]
		except:
			pass
		try:
			tmpDict["collaboration"] = record["710"]["g"]
		except TypeError:
			tmpDict["collaboration"] = None
		tmpDict["primaryclass"] = None
		tmpDict["archiveprefix"] = None
		tmpDict["eprint"] = None
		tmpDict["reportnumber"] = None
		try:
			for q in record.get_fields('037'):
				if "arXiv" in q["a"]:
					tmpDict["primaryclass"] = q["c"]
					tmpDict["archiveprefix"] = q["9"]
					tmpDict["eprint"] = q["a"].lower().replace("arxiv:", "")
				else:
					tmpDict["reportnumber"] = q["a"]
		except:
			pass
		if tmpDict["arxiv"] != tmpDict["eprint"] and \
				tmpDict["eprint"] is not None:
			tmpDict["arxiv"] = tmpDict["eprint"]
		if tmpDict["eprint"] is not None and \
				tmpDict["year"] is None:
			tmpDict["year"] = getYear(tmpDict["eprint"])
		try:
			tmpDict["title"] = record["245"]["a"]
		except TypeError:
			tmpDict["title"] = None
		try:
			tmpDict["isbn"] = record["020"]["a"]
		except TypeError:
			tmpDict["isbn"] = None
		if conferenceCode is not None and readConferenceTitle:
			url = pbConfig.inspireSearchBase \
				+ "?p=773__w%%3A%s+or+773__w%%3A%s+and+980__a%%3A"%(
					conferenceCode, conferenceCode.replace("-", "%2F")) \
				+ "Proceedings&of=xe"
			text = parse_accents_str(self.textFromUrl(url))
			title = re.compile('<title>(.*)</title>', re.MULTILINE)
			try:
				tmpDict["booktitle"] = [m.group(1) for m in title.finditer(
					text)][0]
			except IndexError:
				tmpDict["booktitle"] = None
		if tmpDict["isbn"] is not None:
			tmpDict["ENTRYTYPE"] = "book"
		else:
			try:
				collections = [r["a"].lower() for r in record.get_fields("980")]
			except:
				collections = []
			if "conferencepaper" in collections or conferenceCode is not None:
				tmpDict["ENTRYTYPE"] = "inproceedings"
			elif "thesis" in collections:
				tmpDict["ENTRYTYPE"] = "phdthesis"
				try:
					tmpDict["school"] = record["502"]["c"]
					tmpDict["year"] = record["502"]["d"]
				except:
					pass
			else:
				tmpDict["ENTRYTYPE"] = "article"
		tmpDict["oldkeys"] = ",".join(tmpOld)
		for k in tmpDict.keys():
			try:
				tmpDict[k] = parse_accents_str(tmpDict[k])
			except:
				pass
		tmpDict["link"] = None
		try:
			if tmpDict["arxiv"] is not None and tmpDict["arxiv"] != "":
				tmpDict["link"] = pbConfig.arxivUrl + "/abs/" + tmpDict["arxiv"]
		except KeyError:
			pass
		try:
			if tmpDict["doi"] is not None and tmpDict["doi"] != "":
				tmpDict["link"] = pbConfig.doiUrl + tmpDict["doi"]
		except KeyError:
			pass
		bibtexDict = {"ENTRYTYPE": tmpDict["ENTRYTYPE"],
			"ID": tmpDict["bibkey"]}
		for k in self.bibtexFields:
			if k in tmpDict.keys() and tmpDict[k] is not None and \
					tmpDict[k] is not "":
				bibtexDict[k] = tmpDict[k]
		try:
			if bibtexDict["arxiv"] == bibtexDict["eprint"] and \
					bibtexDict["eprint"] is not None:
				del bibtexDict["arxiv"]
		except:
			pass
		db = bibtexparser.bibdatabase.BibDatabase()
		db.entries = [bibtexDict]
		tmpDict["bibtex"] = pbWriter.write(db)
		return tmpDict

	def retrieveOAIData(self,
			inspireID,
			bibtex=None,
			verbose=0,
			readConferenceTitle=False):
		"""Get the marcxml entry for a given record

		Parameters:
			inspireID: the INSPIRE-HEP identifier (a number)
				of the desired entry
			bibtex (default None): whether the bibtex should be
				included in the output dictionary
			verbose (default 0): increase the output level
			readConferenceTitle (boolean, default False):
				try to read the conference title if dealing
				with a proceeding

		Output:
			the dictionary containing the bibtex information
		"""
		try:
			record = self.oai.getRecord(metadataPrefix='marcxml',
				identifier="oai:inspirehep.net:" + inspireID)
		except (URLError, ErrorBase, IncompleteRead, SocketError):
			pBLogger.exception(
				"Impossible to get marcxml for entry %s"%inspireID)
			return False
		nhand = 0
		if verbose > 0:
			pBLogger.info("Reading data --- " + time.strftime("%c"))
		try:
			if record[1] is None:
				raise ValueError("Empty record!")
			res = self.readRecord(record[1],
				readConferenceTitle=readConferenceTitle)
			res["id"] = inspireID
			if bibtex is not None and res["pages"] is not None:
				outcome, bibtex = self.updateBibtex(res, bibtex)
			if verbose > 0:
				pBLogger.info("Done.")
			return res
		except Exception:
			pBLogger.exception(
				"Impossible to read marcxml for entry %s"%inspireID)
			return False

	def updateBibtex(self, res, bibtex):
		"""use OAI data to update the (existing) bibtex information
		of an entry

		Parameters:
			res: the recent search results
			bibtex: the old bibtex to be updated

		Output:
			True/False and a string containing the bibtex of the entry
		"""
		try:
			element = bibtexparser.loads(bibtex).entries[0]
		except:
			pBLogger.warning("Invalid bibtex!\n%s"%bibtex)
			return False, bibtex
		if res["journal"] is None:
			pBLogger.warning(
				"'journal' from OAI is missing or not a string (recid:%s)"%(
					res["id"])
				)
			return False, bibtex
		try:
			for k in ["doi", "volume", "pages", "year", "journal"]:
				if res[k] != "" and res[k] is not None:
					element[k] = res[k]
		except KeyError:
			pBLogger.warning("Something from OAI is missing (recid:%s)"%(
				res["id"]))
			return False, bibtex
		db = BibDatabase()
		db.entries = [element]
		return True, pbWriter.write(db)

	def retrieveOAIUpdates(self, date1, date2):
		"""Harvest the OAI API to get all the updates
		and new occurrences between two dates

		Parameters:
			date1, date2: dates that define
				the time interval to be searched

		Output:
			a list of dictionaries containing the bibtex information
		"""
		recs = self.oai.listRecords(metadataPrefix='marcxml',
			from_=date1, until=date2, set="INSPIRE:HEP")
		nhand = 0
		pBLogger.info("\nSTARTING OAI harvester --- " \
			+ time.strftime("%c") + "\n\n")
		foundObjects = []
		for count, rec in enumerate(recs):
			id = rec[0].identifier()
			if count % 500 == 0:
				pBLogger.info("Processed %d elements"%count)
			record = rec[1] # Get pyMARC representation
			if not record:
				continue
			try:
				tmpDict = self.readRecord(record)
				id_ = id.replace("oai:inspirehep.net:", "")
				tmpDict["id"] = id_
				foundObjects.append(tmpDict)
			except Exception as e:
				pBLogger.exception("%s, %s\n%s"%(count, id, e))
		pBLogger.info("Processed %d elements"%count)
		pBLogger.info("END --- " + time.strftime("%c") + "\n\n")
		return foundObjects
