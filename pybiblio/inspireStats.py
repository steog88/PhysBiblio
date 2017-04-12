import os, sys, numpy, codecs, re, time
import os.path as osp
import json
from urllib2 import Request, urlopen
import dateutil, datetime
import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
try:
	from pybiblio.config import pbConfig
	from pybiblio.database import pBDB
	from pybiblio.pdf import pBPDF
	from pybiblio.view import pBView
	from pybiblio.errors import pBErrorManager
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

	def changeBackend(self, wantBackend):
		if wantBackend != matplotlib.get_backend():
			matplotlib.use(wantBackend,warn=False, force=True)
			from matplotlib import pyplot as plt
			print("[inspireStats] changed backend to %s"%matplotlib.get_backend())

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
		tot = len(recid_authorPapers)
		print("[inspireStats] authorStats will process %d total papers to retrieve citations"%tot)
		self.runningAuthorStats = True
		for i, p in enumerate(recid_authorPapers):
			if not self.runningAuthorStats:
				print("[inspireStats] received 'stop' signal. Interrupting download of information. Processing and exiting...")
				break
			if tot > 20:
				time.sleep(1)
			allInfo[p] = {}
			allInfo[p]["date"] = dateutil.parser.parse(data[i]["creation_date"])
			authorPapersList[0].append(allInfo[p]["date"])
			print("\n[inspireStats] %5d / %d (%5.2f%%) - looking for paper: '%s'"%(i+1, tot, 100.*(i+1)/tot, p))
			paperInfo = self.paperStats(p, verbose = 0)
			allInfo[p]["infoDict"] = paperInfo["aI"]
			allInfo[p]["citingPapersList"] = paperInfo["citList"]
			for c,v in allInfo[p]["infoDict"].items():
				allCitations.append(v["date"])
		for i,p in enumerate(sorted(authorPapersList[0])):
			authorPapersList[0][i] = p
			authorPapersList[1].append(i + 1)
		print("[inspireStats] saving citation counts...")
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
		if plot:
			self.authorPlotInfo["figs"] = self.plotStats(author = True)
		print("[inspireStats] stats for author '%s' completed!"%authorName)
		return self.authorPlotInfo

	def paperStats(self, paperID, plot = False, verbose = 1):
		if verbose > 0:
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
		for i,p in enumerate(sorted(citingPapersList[0])):
			citingPapersList[0][i] = p
			citingPapersList[1].append(i+1)
		self.paperPlotInfo = { "id": paperID, "aI": allInfo, "citList": citingPapersList }
		if plot:
			self.paperPlotInfo["fig"] = self.plotStats(paper = True)
		return self.paperPlotInfo
	
	def plotStats(self, paper = False, author = False, show = False, save = False, path = ".", markPapers = False):
		if paper and self.paperPlotInfo is not None:
			if len(self.paperPlotInfo["citList"][0]) > 0:
				print("[inspireStats] plotting for paper '%s'..."%self.paperPlotInfo["id"])
				fig, ax = plt.subplots()
				plt.plot(self.paperPlotInfo["citList"][0], self.paperPlotInfo["citList"][1])
				fig.autofmt_xdate()
				if save:
					pdf = PdfPages(osp.join(path, self.paperPlotInfo["id"]+'.pdf'))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
				return fig
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
					pBErrorManager("[inspireStats] no publications for this author?")
					return False
			figs = []
			if len(self.authorPlotInfo["paLi"][0]) > 0:
				fig, ax = plt.subplots()
				plt.title("Paper number")
				plt.plot(self.authorPlotInfo["paLi"][0], self.authorPlotInfo["paLi"][1])
				fig.autofmt_xdate()
				if save:
					pdf = PdfPages(osp.join(path, self.authorPlotInfo["name"]+'_papers.pdf'))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
				figs.append(fig)
			
			if len(self.authorPlotInfo["paLi"][0]) > 0:
				fig, ax = plt.subplots()
				plt.title("Papers per year")
				ax.hist([int(q.strftime("%Y")) for q in self.authorPlotInfo["paLi"][0]],
					bins=range(ymin,  ymax))
				ax.get_xaxis().get_major_formatter().set_useOffset(False)
				plt.xlim([ymin, ymax])
				if save:
					pdf = PdfPages(osp.join(path, self.authorPlotInfo["name"]+'_yearPapers.pdf'))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
				figs.append(fig)
			
			if len(self.authorPlotInfo["allLi"][0]) > 0:
				fig, ax = plt.subplots()
				plt.title("Total citations")
				plt.plot(self.authorPlotInfo["allLi"][0], self.authorPlotInfo["allLi"][1])
				fig.autofmt_xdate()
				if save:
					pdf = PdfPages(osp.join(path, self.authorPlotInfo["name"]+'_allCit.pdf'))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
				figs.append(fig)
			
			if len(self.authorPlotInfo["allLi"][0]) > 0:
				fig, ax = plt.subplots()
				plt.title("Citations per year")
				ax.hist([int(q.strftime("%Y")) for q in self.authorPlotInfo["allLi"][0]],
					bins=range(ymin,  ymax))
				ax.get_xaxis().get_major_formatter().set_useOffset(False)
				plt.xlim([ymin, ymax])
				if save:
					pdf = PdfPages(osp.join(path, self.authorPlotInfo["name"]+'_yearCit.pdf'))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
				figs.append(fig)
			
			if len(self.authorPlotInfo["meanLi"][0]) > 0:
				fig, ax = plt.subplots()
				plt.title("Mean citations")
				plt.plot(self.authorPlotInfo["meanLi"][0], self.authorPlotInfo["meanLi"][1])
				fig.autofmt_xdate()
				if markPapers:
					for q in self.authorPlotInfo["paLi"][0]:
						plt.axvline(datetime.datetime(int(q.strftime("%Y")), int(q.strftime("%m")), int(q.strftime("%d"))), color = 'k', ls = '--')
				if save:
					pdf = PdfPages(osp.join(path, self.authorPlotInfo["name"]+'_meanCit.pdf'))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
				figs.append(fig)
			
			if len(self.authorPlotInfo["aI"].keys()) > 0:
				fig, ax = plt.subplots()
				plt.title("Citations for each paper")
				for i,p in enumerate(self.authorPlotInfo["aI"].keys()):
					try:
						plt.plot(self.authorPlotInfo["aI"][p]["citingPapersList"][0],self.authorPlotInfo["aI"][p]["citingPapersList"][1])
					except:
						pass
				fig.autofmt_xdate()
				if save:
					pdf = PdfPages(osp.join(path, self.authorPlotInfo["name"]+'_paperCit.pdf'))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
				figs.append(fig)
			return figs
		else:
			print("[inspireStats] nothing to plot...")
			return False

pBStats = inspireStatsLoader()