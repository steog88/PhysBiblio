import sys,re,os, time
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
	p=[]
	y=[]
	v=[]
	c=[]
	m=[]
	x=[]
	t=[]
	if marcxml["773"] is not None:
		for q in marcxml.get_fields("773"):
			p.append(parse_accents_str(q["p"]))	#journal name (even if submitted to only)
			v.append(parse_accents_str(q["v"]))	#volume
			y.append(parse_accents_str(q["y"]))	#year
			c.append(parse_accents_str(q["c"]))	#pages
			
			m.append(parse_accents_str(q["m"]))	#Erratum, Addendum, Publisher note
			
			x.append(parse_accents_str(q["x"]))	#freetext journal/book info
			t.append(parse_accents_str(q["t"]))	#for conf papers: presented at etc, freetext or KB?
	return p,v,y,c,m,x,t

class MARCXMLReader(object):
    """Returns the PyMARC record from the OAI structure for MARC XML"""
    def __call__(self, element):
        handler = marcxml.XmlHandler()
        marcxml.parse_xml(StringIO(tostring(element[0], encoding='UTF-8')), handler)
        return handler.records[0]

marcxml_reader = MARCXMLReader()

from oaipmh import metadata

registry = metadata.MetadataRegistry()
registry.registerReader('marcxml', marcxml_reader)

class webSearch(webInterf):
	def __init__(self):
		webInterf.__init__(self)
		self.name="inspireoai"
		self.description="INSPIRE OAI interface"
		self.url="http://inspirehep.net/oai2d"
		self.urlArgs={
			"action_search":"Search",
			"sf":"",
			"so":"d",
			"rm":"",
			"rg":"1000",
			"sc":"0",
			"of":"hx"#for bibtex format ---- hb for standard format, for retrieving inspireid
			}
		self.oai = Client(self.url, registry)
		
	def retrieveUrlFirst(self,string):
		print "[inspireoai] -> ERROR: inspireoai cannot search strings in the DB"
		return ""
		
	def retrieveUrlAll(self,string):
		print "[inspireoai] -> ERROR: inspireoai cannot search strings in the DB"
		return ""
	
	def retrieveOAIData(self,inspireID):
		pass
		
	def retrieveOAIUpdates(self, date1, date2):
		recs = self.oai.listRecords(metadataPrefix='marcxml',from_=date1,until=date2,set="INSPIRE:HEP")
		nhand=0
		print "\n[inspireoai] STARTING OAI harvester --- "+time.strftime("%c")+"\n\n"
		foundObjects=[]
		for count, rec in enumerate(recs):
			id = rec[0].identifier()
			if count % 500 == 0:
				print "[inspireoai] Processed %d elements"%count
			record = rec[1] # Get pyMARC representation
			if not record:
				continue
			try:
				tmp={}
				record.to_unicode = True
				record.force_utf8 = True
				arxiv=""
				oldkeys=[]
				id_=id.replace("oai:inspirehep.net:","")
				tmp["id"]=id_
				tmp["oldkeys"]=[]
				for q in record.get_fields('035'):
					if q["9"] == "arXiv":
						tmp=q["a"]
						if tmp is not None:
							arxiv = tmp.replace("oai:arXiv.org:","")
						else:
							arxiv=""
						tmp["arxiv"]=arxiv
					if q["9"] == "SPIRESTeX" or q["9"] == "INSPIRETeX":
						if q["a"]:
							tmp["bibkey"]=q["a"]
						elif q["z"]:
							tmp["oldkeys"].append(q["z"])
				tmp["journal"],tmp["volume"],tmp["year"],tmp["pages"],m,x,t=get_journal_ref_xml(record)
				firstdate=record["269"]
				if firstdate is not None:
					firstdate=firstdate["c"]
				else:
					firstdate=record["961"]
					if firstdate is not None:
						firstdate=firstdate["x"]
				tmp["firstdate"]=firstdate
				foundObjects.append(tmp)
			except Exception, e:
				print count, id
				print e
				print traceback.format_exc()
		print "[inspireoai] Processed %d elements"%count
		print "[inspireoai] END --- "+time.strftime("%c")+"\n\n"
		return foundObjects
