import os, sys, numpy, codecs, re
import json
from urllib2 import Request, urlopen
import dateutil, datetime
import matplotlib.pyplot as plt
try:
	from pybiblio.config import pbConfig
	from pybiblio.database import pBDB
	from pybiblio.pdf import pBPDF
	from pybiblio.view import pBView
except ImportError:
	print("Could not find pybiblio and its contents: configure your PYTHONPATH!")

class inspireStatsLoader():
	def __init__(self):
		self.urlBase = pbConfig.inspireSearchBase
		self.timeout = float(pbConfig.params["timeoutWebSearch"])
		self.authorStatsOpts = "&of=recjson&ot=recid,creation_date&so=a&rg=250"
		self.paperStatsOpts  = "&of=recjson&ot=recid,creation_date&so=a&rg=250"
		self.skipPageOpt = "&jrec="
		self.maxPerPage = 250

	def JsonFromUrl(self, url):
		def getSeries(url):
			response = urlopen(url, timeout = self.timeout)
			text = response.read()
			try:
				return json.loads(text)
			except:
				return []
		ser = 0
		complete = []
		while True:
			temp = getSeries(url + self.skipPageOpt + "%d"%(ser * self.maxPerPage + 1))
			if len(temp) < self.maxPerPage:
				return complete + temp
			else:
				complete += temp
				ser += 1

	def authorStats(self, authorName, plot = False):
		print("[inspireStats] stats for author '%s'"%authorName)
		url = pbConfig.inspireSearchBase + "?p=author:" + authorName + self.authorStatsOpts
		data = self.JsonFromUrl(url)
		recid_authorPapers = [ "%d"%a["recid"] for a in data ]
		allInfo = {}
		authorPapersList = [[],[]]
		allCitations = []
		for i, p in enumerate(recid_authorPapers):
			allInfo[p] = {}
			allInfo[p]["date"] = dateutil.parser.parse(data[i]["creation_date"])
			authorPapersList[0].append(allInfo[p]["date"])
			authorPapersList[1].append(i + 1)
			allInfo[p]["infoDict"], allInfo[p]["citingPapersList"] = self.paperStats(p)
			for c,v in allInfo[p]["infoDict"].items():
				allCitations.append(v["date"])
		allCitList = [[],[]]
		meanCitList = [[],[]]
		currPaper = 0
		for i,d in enumerate(sorted(allCitations)):
			if currPaper < len(authorPapersList[0])-1 and d >= authorPapersList[0][currPaper+1]:
				currPaper += 1
			allCitList[0].append(d)
			allCitList[1].append(i+1)
			meanCitList[0].append(d)
			meanCitList[1].append((i+1.)/authorPapersList[1][currPaper])
		if plot:
			plt.subplot(111)
			plt.title("Paper number")
			plt.plot(authorPapersList[0], authorPapersList[1])
			plt.show()
			plt.subplot(111)
			plt.title("Citations for each paper")
			for i,p in enumerate(recid_authorPapers):
				plt.plot(allInfo[p]["citingPapersList"][0],allInfo[p]["citingPapersList"][1])
			plt.show()
			plt.subplot(111)
			plt.title("Total citations")
			plt.plot(allCitList[0], allCitList[1])
			plt.show()
			plt.subplot(111)
			plt.title("Mean citations")
			plt.plot(meanCitList[0], meanCitList[1])
			for q in authorPapersList[0]:
				plt.axvline(datetime.datetime(int(q.strftime("%Y")), int(q.strftime("%m")), int(q.strftime("%d"))), color = 'k', ls = '--')
			plt.show()
		return allInfo, authorPapersList, allCitList,  meanCitList

	def paperStats(self, paperID, plot = False):
		print("[inspireStats] stats for paper '%s'"%paperID)
		url = pbConfig.inspireSearchBase + "?p=refersto:recid:" + paperID + self.paperStatsOpts
		data = self.JsonFromUrl(url)
		recid_citingPapers = [ a["recid"] for a in data ]
		allInfo = {}
		citingPapersList = [[],[]]
		for i,p in enumerate(recid_citingPapers):
			allInfo[p] = {}
			allInfo[p]["date"] = dateutil.parser.parse(data[i]["creation_date"])
			citingPapersList[0].append(allInfo[p]["date"])
			citingPapersList[1].append(i+1)
		if plot:
			plt.plot(citingPapersList[0], citingPapersList[1])
			plt.show()
		return allInfo, citingPapersList

pBStats = inspireStatsLoader()
