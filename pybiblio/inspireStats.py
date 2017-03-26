import os, sys, numpy, codecs, re
import json
from urllib2 import Request, urlopen
import dateutil, datetime
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
try:
	from pybiblio.config import pbConfig
	from pybiblio.database import pBDB
	from pybiblio.pdf import pBPDF
	from pybiblio.view import pBView
	from pybiblio.errors import ErrorManager
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
		self.authorPlotInfo = None
		self.paperPlotInfo = None

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
			paperInfo = self.paperStats(p)
			allInfo[p]["infoDict"] = paperInfo["aI"]
			allInfo[p]["citingPapersList"] = paperInfo["citList"]
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
		self.authorPlotInfo = { "name": authorName, "aI": allInfo, "paLi": authorPapersList, "allLi": allCitList,  "meanLi": meanCitList }
		return self.authorPlotInfo

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
		self.paperPlotInfo = { "id": paperID, "aI": allInfo, "citList": citingPapersList }
		return self.paperPlotInfo
	
	def plotStats(self, paper = False, author = False, show = False, save = False, path = "."):
		if paper and self.paperPlotInfo is not None:
			if len(self.paperPlotInfo["citList"][0]) > 0:
				print("[inspireStats] plotting for paper '%s'..."%self.paperPlotInfo["id"])
				plt.plot(self.paperPlotInfo["citList"][0], self.paperPlotInfo["citList"][1])
				if save:
					pdf = PdfPages('%s/%s.pdf'%(path, self.paperPlotInfo["id"]))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
		elif author and self.authorPlotInfo is not None:
			print("[inspireStats] plotting for author '%s'..."%self.authorPlotInfo["name"])
			try:
				ymin = min(int(self.authorPlotInfo["allLi"][0][0].strftime("%Y"))-2, int(self.authorPlotInfo["paLi"][0][0].strftime("%Y"))-2)
				ymax = max(int(self.authorPlotInfo["allLi"][0][-1].strftime("%Y"))+2, int(self.authorPlotInfo["paLi"][0][-1].strftime("%Y"))+2)
			except:
				try:
					ymin = int(self.authorPlotInfo["paLi"][0][0].strftime("%Y"))-2
					ymax = int(self.authorPlotInfo["paLi"][0][-1].strftime("%Y"))+2
				except:
					ErrorManager("[inspireStats] no publications for this author?")
					return False
				
			
			if len(self.authorPlotInfo["paLi"][0]) > 0:
				fig, ax = plt.subplots()
				plt.title("Paper number")
				plt.plot(self.authorPlotInfo["paLi"][0], self.authorPlotInfo["paLi"][1])
				if save:
					pdf = PdfPages('%s/%s_papers.pdf'%(path, self.authorPlotInfo["name"]))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
			
			if len(self.authorPlotInfo["paLi"][0]) > 0:
				fig, ax = plt.subplots()
				plt.title("Papers per year")
				ax.hist([int(q.strftime("%Y")) for q in self.authorPlotInfo["paLi"][0]],
					bins=range(ymin,  ymax))
				ax.get_xaxis().get_major_formatter().set_useOffset(False)
				plt.xlim([ymin, ymax])
				plt.xticks(range(ymin,ymax+1))
				if save:
					pdf = PdfPages('%s/%s_yearPapers.pdf'%(path, self.authorPlotInfo["name"]))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
			
			if len(self.authorPlotInfo["aI"].keys()) > 0:
				fig, ax = plt.subplots()
				plt.title("Citations for each paper")
				for i,p in enumerate(self.authorPlotInfo["aI"].keys()):
					try:
						plt.plot(self.authorPlotInfo["aI"][p]["citingPapersList"][0],self.authorPlotInfo["aI"][p]["citingPapersList"][1])
					except:
						pass
				if save:
					pdf = PdfPages('%s/%s_paperCit.pdf'%(path, self.authorPlotInfo["name"]))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
			
			if len(self.authorPlotInfo["allLi"][0]) > 0:
				fig, ax = plt.subplots()
				plt.title("Total citations")
				plt.plot(self.authorPlotInfo["allLi"][0], self.authorPlotInfo["allLi"][1])
				if save:
					pdf = PdfPages('%s/%s_allCit.pdf'%(path, self.authorPlotInfo["name"]))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
			
			if len(self.authorPlotInfo["allLi"][0]) > 0:
				fig, ax = plt.subplots()
				plt.title("Citations per year")
				ax.hist([int(q.strftime("%Y")) for q in self.authorPlotInfo["allLi"][0]],
					bins=range(ymin,  ymax))
				ax.get_xaxis().get_major_formatter().set_useOffset(False)
				plt.xlim([ymin, ymax])
				plt.xticks(range(ymin,ymax+1))
				if save:
					pdf = PdfPages('%s/%s_yearCit.pdf'%(path, self.authorPlotInfo["name"]))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
			
			if len(self.authorPlotInfo["meanLi"][0]) > 0:
				fig, ax = plt.subplots()
				plt.title("Mean citations")
				plt.plot(self.authorPlotInfo["meanLi"][0], self.authorPlotInfo["meanLi"][1])
				for q in self.authorPlotInfo["paLi"][0]:
					plt.axvline(datetime.datetime(int(q.strftime("%Y")), int(q.strftime("%m")), int(q.strftime("%d"))), color = 'k', ls = '--')
				if save:
					pdf = PdfPages('%s/%s_meanCit.pdf'%(path, self.authorPlotInfo["name"]))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
		else:
			print("[inspireStats] nothing to plot...")

pBStats = inspireStatsLoader()
