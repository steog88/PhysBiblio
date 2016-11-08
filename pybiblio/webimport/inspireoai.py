import sys, re, os, time
from urllib2 import Request
import urllib2
from pybiblio.webimport.webInterf import *
from pybiblio.parse_accents import *

import codecs
reload(sys)
sys.setdefaultencoding('utf-8')

import datetime, traceback

from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry
from lxml import etree

from cStringIO import StringIO
from lxml.etree import tostring
from pymarc import marcxml, MARCWriter, field
from oaipmh import metadata

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
	def __init__(self):
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
		]
		
	def retrieveUrlFirst(self,string):
		print("[inspireoai] -> ERROR: inspireoai cannot search strings in the DB")
		return ""
		
	def retrieveUrlAll(self,string):
		print("[inspireoai] -> ERROR: inspireoai cannot search strings in the DB")
		return ""
		
	def readRecord(self, record):
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
					if q["a"]:
						tmpDict["bibkey"] = q["a"]
					elif q["z"]:
						tmpOld.append(q["z"])
				if q["9"] == "ADS":
					if q["a"] is not None:
						tmpDict["ads"] = q["a"]
		except:
			pass
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
	
	def retrieveOAIData(self,inspireID):
		record = self.oai.getRecord(metadataPrefix = 'marcxml', identifier = "oai:inspirehep.net:" + inspireID)
		nhand = 0
		print("[inspireoai] reading data --- " + time.strftime("%c"))
		try:
			res = self.readRecord(record[1])
			res["id"] = inspireID
			print("[inspireoai] done.")
			return res
		except Exception:
			print("[inspireoai] ERROR: impossible to read marcxml for entry %s"%inspireID)
			return False
		
	def retrieveOAIUpdates(self, date1, date2):
		recs = self.oai.listRecords(metadataPrefix = 'marcxml', from_ = date1, until = date2, set = "INSPIRE:HEP")
		nhand = 0
		print("\n[inspireoai] STARTING OAI harvester --- " + time.strftime("%c") + "\n\n")
		foundObjects = []
		for count, rec in enumerate(recs):
			id = rec[0].identifier()
			if count % 500 == 0:
				print("[inspireoai] Processed %d elements"%count)
			record = rec[1] # Get pyMARC representation
			if not record:
				continue
			try:
				tmpDict = self.readRecord(record)
				id_ = id.replace("oai:inspirehep.net:", "")
				tmpDict["id"] = id_
				foundObjects.append(tmpDict)
			except Exception, e:
				print count, id
				print e
				print traceback.format_exc()
		print("[inspireoai] Processed %d elements"%count)
		print("[inspireoai] END --- " + time.strftime("%c") + "\n\n")
		return foundObjects
