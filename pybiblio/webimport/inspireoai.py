import sys, re, os, time
from urllib2 import Request
import urllib2
from pybiblio.webimport.webInterf import *
from pybiblio.parse_accents import *
from bibtexparser.bibdatabase import BibDatabase
import bibtexparser
from pybiblio.bibtexwriter import pbWriter

import codecs
reload(sys)
sys.setdefaultencoding('utf-8')

import datetime, traceback

from oaipmh.client import Client
from oaipmh.error import ErrorBase
from oaipmh.metadata import MetadataRegistry
from lxml import etree

from cStringIO import StringIO
from lxml.etree import tostring
from pymarc import marcxml, MARCWriter, field
from oaipmh import metadata
import httplib

def safe_list_get(l, idx, default=""):
	"""
	Safely get an element from a list.
	No error if it doesn't exist...
	"""
	if l is not None:
		try:
			return l[idx]
		except IndexError:
			return default
	else:
		return default
		
def get_journal_ref_xml(marcxml):
	"""
	Read the marcxml record and write the info on the publication
	"""
	p = []
	y = []
	v = []
	c = []
	m = []
	x = []
	t = []
	if marcxml["773"] is not None:
		for q in marcxml.get_fields("773"):
			p.append(parse_accents_str(q["p"]))	#journal name (even if submitted to only)
			v.append(parse_accents_str(q["v"]))	#volume
			y.append(parse_accents_str(q["y"]))	#year
			c.append(parse_accents_str(q["c"]))	#pages
			
			m.append(parse_accents_str(q["m"]))	#Erratum, Addendum, Publisher note
			
			x.append(parse_accents_str(q["x"]))	#freetext journal/book info
			t.append(parse_accents_str(q["t"]))	#for conf papers: presented at etc, freetext or KB?
	return p, v, y, c, m, x, t

class MARCXMLReader(object):
    """Returns the PyMARC record from the OAI structure for MARC XML"""
    def __call__(self, element):
        handler = marcxml.XmlHandler()
        marcxml.parse_xml(StringIO(tostring(element[0], encoding='UTF-8')), handler)
        return handler.records[0]

marcxml_reader = MARCXMLReader()

registry = metadata.MetadataRegistry()
registry.registerReader('marcxml', marcxml_reader)

class webSearch(webInterf):
	"""inspire OAI methods"""
	def __init__(self):
		"""configuration"""
		webInterf.__init__(self)
		self.name = "inspireoai"
		self.description = "INSPIRE OAI interface"
		self.url = "http://inspirehep.net/oai2d"
		self.oai = Client(self.url, registry)
		self.correspondences = [
			["id", "inspire"],
			["year", "year"],
			["arxiv", "arxiv"],
			["oldkeys", "old_keys"],
			["firstdate", "firstdate"],
			["pubdate", "pubdate"],
			["doi", "doi"],
			["ads", "ads"],
			["isbn", "isbn"],
			["bibtex", "bibtex"],
		]
		
	def retrieveUrlFirst(self,string):
		"""not possible to search a single string"""
		print("[oai] -> ERROR: inspireoai cannot search strings in the DB")
		return ""
		
	def retrieveUrlAll(self,string):
		"""not possible to search a single string"""
		print("[oai] -> ERROR: inspireoai cannot search strings in the DB")
		return ""
		
	def readRecord(self, record):
		"""read the content of a record marcxml"""
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
		except:
			pass
		try:
			tmpDict["arxiv"]  = None
			tmpDict["bibkey"] = None
			tmpDict["ads"]    = None
			for q in record.get_fields('035'):
				if q["9"] == "arXiv":
					tmp = q["a"]
					if tmp is not None:
						arxiv = tmp.replace("oai:arXiv.org:", "")
					else:
						arxiv = ""
					tmpDict["arxiv"]=arxiv
				if q["9"] == "SPIRESTeX" or q["9"] == "INSPIRETeX":
					if q["z"]:
						tmpDict["bibkey"] = q["z"]
					elif q["a"]:
						tmpOld.append(q["a"])
				if q["9"] == "ADS":
					if q["a"] is not None:
						tmpDict["ads"] = q["a"]
		except:
			pass
		if tmpDict["bibkey"] is None and len(tmpOld) > 0:
			tmpDict["bibkey"] = tmpOld[0]
			tmpOld = []
		try:
			j, v, y, p, m, x, t = get_journal_ref_xml(record)
			tmpDict["journal"] = j[0]
			tmpDict["volume"]  = v[0]
			tmpDict["year"]    = y[0]
			tmpDict["pages"]   = p[0]
		except:
			tmpDict["journal"] = None
			tmpDict["volume"]  = None
			tmpDict["year"]    = None
			tmpDict["pages"]   = None
		try:
			firstdate = record["269"]
			if firstdate is not None:
				firstdate = firstdate["c"]
			else:
				firstdate = record["961"]
				if firstdate is not None:
					firstdate = firstdate["x"]
			tmpDict["firstdate"] = firstdate
		except:
			tmpDict["firstdate"] = None
		try:
			tmpDict["pubdate"] = record["260"]["c"]
		except:
			tmpDict["pubdate"] = None
		try:
			tmpDict["isbn"] = record["020"]["a"]
		except:
			tmpDict["isbn"] = None
		try:
			tmpDict["pubdate"] = record["260"]["c"]
		except:
			tmpDict["pubdate"] = None
		tmpDict["oldkeys"] = ",".join(tmpOld)
		return tmpDict
	
	def retrieveOAIData(self, inspireID, bibtex = None, verbose = 0):
		"""get the marcxml for a given record"""
		try:
			record = self.oai.getRecord(metadataPrefix = 'marcxml', identifier = "oai:inspirehep.net:" + inspireID)
		except ErrorBase, httplib.IncompleteRead:
			print("[oai] ERROR: impossible to get marcxml for entry %s"%inspireID)
			return False
		nhand = 0
		if verbose > 0:
			print("[oai] reading data --- " + time.strftime("%c"))
		try:
			res = self.readRecord(record[1])
			res["id"] = inspireID
			if bibtex is not None and res["pages"] is not None:
				element = bibtexparser.loads(bibtex).entries[0]
				try:
					res["journal"] = res["journal"].replace(".", ". ")
				except AttributeError:
					print("[DB] 'journal' from OAI is not a string (?)")
				for k in ["doi", "volume", "pages", "year", "journal"]:
					if res[k] != "" and res[k] is not None:
						element[k] = res[k]
				db = BibDatabase()
				db.entries = []
				db.entries.append(element)
				res["bibtex"] = pbWriter.write(db)
			else:
				res["bibtex"] = None
			if verbose > 0:
				print("[oai] done.")
			return res
		except Exception:
			print("[oai] ERROR: impossible to read marcxml for entry %s"%inspireID)
			print(traceback.format_exc())
			return False
		
	def retrieveOAIUpdates(self, date1, date2):
		"""get all the updates and new occurrences between two dates"""
		recs = self.oai.listRecords(metadataPrefix = 'marcxml', from_ = date1, until = date2, set = "INSPIRE:HEP")
		nhand = 0
		print("\n[oai] STARTING OAI harvester --- " + time.strftime("%c") + "\n\n")
		foundObjects = []
		for count, rec in enumerate(recs):
			id = rec[0].identifier()
			if count % 500 == 0:
				print("[oai] Processed %d elements"%count)
			record = rec[1] # Get pyMARC representation
			if not record:
				continue
			try:
				tmpDict = self.readRecord(record)
				id_ = id.replace("oai:inspirehep.net:", "")
				tmpDict["id"] = id_
				foundObjects.append(tmpDict)
			except Exception, e:
				print(count, id)
				print(e)
				print(traceback.format_exc())
		print("[oai] Processed %d elements"%count)
		print("[oai] END --- " + time.strftime("%c") + "\n\n")
		return foundObjects
