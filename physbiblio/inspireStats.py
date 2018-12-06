"""Module that uses INSPIRE-HEP to get author
(number of papers, h index, citations) and paper statistics (citations).

Uses matplotlib to do plots.

This file is part of the physbiblio package.
"""
import time
import os
import traceback
import os.path as osp
import json
import requests
import dateutil
import datetime
import matplotlib
matplotlib.use('Qt5Agg')
os.environ["QT_API"] = 'pyside2'
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages

try:
	from physbiblio.errors import pBLogger
	from physbiblio.config import pbConfig
except ImportError:
	print("Could not find physbiblio and its modules!")
	print(traceback.format_exc())
	raise


class InspireStatsLoader():
	"""Class that contains the methods
	to collect information from INSPIRE-HEP
	"""

	def __init__(self):
		"""The class constructor,
		defines some constants and search options
		"""
		self.urlBase = pbConfig.inspireSearchBase
		self.timeout = float(pbConfig.params["timeoutWebSearch"])
		self.authorStatsOpts = "&of=recjson&ot=recid,creation_date&so=a&rg=250"
		self.paperStatsOpts = "&of=recjson&ot=recid,creation_date&so=a&rg=250"
		self.skipPageOpt = "&jrec="
		self.maxPerPage = 250
		self.authorPlotInfo = None
		self.paperPlotInfo = None

	def changeBackend(self, wantBackend):
		"""Changes the matplotlib backend currently in use.

		Parameters:
			wantBackend: a string that defines the wanted backend
		"""
		if wantBackend != matplotlib.get_backend():
			matplotlib.use(wantBackend, warn=False, force=True)
			from matplotlib import pyplot as plt
			pBLogger.info("Changed backend to %s"%matplotlib.get_backend())

	def JsonFromUrl(self, url):
		"""Function that downloads the url content
		and returns a Json object

		Parameters:
			url: string containing the url to be opened

		Output:
			the json object generated from the url content
		"""
		def getSeries(url):
			response = requests.get(url, timeout=self.timeout)
			try:
				return json.loads(response.content.decode("utf-8"))
			except ValueError:
				pBLogger.warning("Empty response!")
				return []
			except:
				pBLogger.exception("Cannot read the page content!")
				return []
		ser = 0
		complete = []
		while True:
			temp = getSeries(url + self.skipPageOpt + "%d"%(
				ser * self.maxPerPage + 1))
			if len(temp) < self.maxPerPage:
				return complete + temp
			else:
				complete += temp
				ser += 1

	def authorStats(self, authorName, plot=False, reset=True):
		"""Function that gets the data and
		constructs the statistics for a given author.

		Parameters:
			authorName: the author name as identified into INSPIRE-HEP,
				or a list of author names
				(it calls itself recursively for all the list elements)
			plot (boolean, default False): True to call self.plotStats
			reset (boolean, default False): True to delete
				all previous existing data
				(used as False when processing a list of authors)

		Output:
			a dictionary containing all the statistic information.
			For a single author, the structure is the following:
			{
				"name": the author name,
				"aI": The complete information,
					including the dictionaries with the single papers info
					(see self.paperStats), the citations
					and the corresponding dates,
				"paLi": a list of [id, date] of the papers
					associated with the author,
				"allLi": the complete list of [date, total citations]
					with all the citations to the papers,
				"meanLi": the complete list of
					[date, total citations/number of papers]
					computed at each point from "allLi" content,
				"h": the h-index,
				"figs" (only if `plot` is True): contains the figures.
					See self.plotStats
			}
		"""
		if reset:
			self.allInfoA = {}
			self.authorPapersList = [[],[]]
			self.allCitations = []
		if isinstance(authorName, list):
			for a in authorName:
				self.authorStats(a, reset=False)
			self.authorPlotInfo["name"] = authorName
			return self.authorPlotInfo
		pBLogger.info("Stats for author '%s'"%authorName)
		url = pbConfig.inspireSearchBase + "?p=author:" \
			+ authorName + self.authorStatsOpts
		data = self.JsonFromUrl(url)
		recid_authorPapers = [ "%d"%a["recid"] for a in data ]
		tot = len(recid_authorPapers)
		pBLogger.info("AuthorStats will process %d "%tot
			+ "total papers to retrieve citations")
		self.runningAuthorStats = True
		for i, p in enumerate(recid_authorPapers):
			if not self.runningAuthorStats:
				pBLogger.info("Received 'stop' signal. "
					+ "Interrupting download of information. "
					+ "Processing and exiting...")
				break
			if tot > 20:
				time.sleep(1)
			if p in self.allInfoA.keys(): continue
			self.allInfoA[p] = {}
			self.allInfoA[p]["date"] = dateutil.parser.parse(
				data[i]["creation_date"])
			self.authorPapersList[0].append(self.allInfoA[p]["date"])
			pBLogger.info("%5d / %d (%5.2f%%) - looking for paper: '%s'"%(
				i+1, tot, 100.*(i+1)/tot, p))
			paperInfo = self.paperStats(p,
				verbose=0, paperDate=self.allInfoA[p]["date"])
			self.allInfoA[p]["infoDict"] = paperInfo["aI"]
			self.allInfoA[p]["citingPapersList"] = paperInfo["citList"]
			for c,v in self.allInfoA[p]["infoDict"].items():
				self.allCitations.append(v["date"])
			pBLogger.info("")
		self.authorPapersList[1] = []
		for i,p in enumerate(sorted(self.authorPapersList[0])):
			self.authorPapersList[0][i] = p
			self.authorPapersList[1].append(i + 1)
		pBLogger.info("Saving citation counts...")
		allCitList = [[],[]]
		meanCitList = [[],[]]
		currPaper = 0
		for i,d in enumerate(sorted(self.allCitations)):
			if currPaper < len(self.authorPapersList[0])-1 \
					and d >= self.authorPapersList[0][currPaper+1]:
				currPaper += 1
			allCitList[0].append(d)
			allCitList[1].append(i+1)
			meanCitList[0].append(d)
			meanCitList[1].append((i+1.)/self.authorPapersList[1][currPaper])
		hind = 0
		citations = [len(self.allInfoA[k]["citingPapersList"][0]) - 2 \
			for k in self.allInfoA.keys()]
		for h in range(len(citations)):
			if len([a for a in citations if a >= h]) >= h:
				hind = h
		self.authorPlotInfo = {
			"name": authorName,
			"aI": self.allInfoA,
			"paLi": self.authorPapersList,
			"allLi": allCitList,
			"meanLi": meanCitList,
			"h": hind}
		if plot:
			self.authorPlotInfo["figs"] = self.plotStats(author=True)
		pBLogger.info("Stats for author '%s' completed!"%authorName)
		return self.authorPlotInfo

	def paperStats(self, paperID,
			plot=False, verbose=1, paperDate=None, reset=True):
		"""Function that gets the data and
		constructs the statistics for a given paper.

		Parameters:
			paperID (string): the INSPIRE-HEP id of the paper (a number)
			plot (boolean): whether or not the citations
				should be plotted (default False)
			verbose (int, default 1): increase the verbosity level
			paperDate (datetime, optional): the date of at which
				the paper was published
			reset (boolean, default False): True to delete
				all previous existing data
				(used as False when processing a list of IDs)

		Output:
			a dictionary containing all the desired information.
			The structure is the following:
			{
				"id": the paper ID,
				"aI": the list of creation date for all the papers,
					in INSPIRE-HEP order,
				"citList": the ordered list of citing papers,
				"fig" (only if `plot` is True): contains the figure.
					See self.plotStats
			}
		"""
		if reset:
			self.allInfoP = {}
			self.citingPapersList = [[],[]]
		if isinstance(paperID, list):
			for a in paperID:
				self.paperStats(a, reset=False)
			self.paperPlotInfo["id"] = paperID
			return self.paperPlotInfo
		if verbose > 0:
			pBLogger.info("Stats for paper '%s'"%paperID)
		url = pbConfig.inspireSearchBase + "?p=refersto:recid:" \
			+ paperID + self.paperStatsOpts
		data = self.JsonFromUrl(url)
		recid_citingPapers = [ a["recid"] for a in data ]
		if paperDate is not None:
			self.citingPapersList[0].append(paperDate)
		for i,p in enumerate(recid_citingPapers):
			self.allInfoP[p] = {}
			self.allInfoP[p]["date"] = dateutil.parser.parse(
				data[i]["creation_date"])
			self.citingPapersList[0].append(self.allInfoP[p]["date"])
		for i,p in enumerate(sorted(self.citingPapersList[0])):
			self.citingPapersList[0][i] = p
			self.citingPapersList[1].append(i+1)
		self.citingPapersList[0].append(
			datetime.datetime.fromordinal(datetime.date.today().toordinal()))
		try:
			self.citingPapersList[1].append(self.citingPapersList[1][-1])
		except IndexError:
			self.citingPapersList[1].append(0)
		self.paperPlotInfo = {
			"id": paperID,
			"aI": self.allInfoP,
			"citList": self.citingPapersList}
		if plot:
			self.paperPlotInfo["fig"] = self.plotStats(paper=True)
		if verbose > 0:
			pBLogger.info("Done!")
		return self.paperPlotInfo

	def plotStats(self,
			paper=False,
			author=False,
			show=False,
			save=False,
			path=".",
			markPapers=False,
			pickVal=6):
		"""Plot the collected information, using matplotlib.pyplot.

		Parameters:
			paper (boolean, default False): plot statistics
				for the last analyzed paper
			author (boolean, default False): plot statistics
				for the last analyzed author
			show (boolean, default False): True to show the plots
				in a separate window (with matplotlib.pyplot.show())
			save (boolean, default False): True to save the plots into files.
			path (string): where to save the plots
			markPapers (boolean, default False): True to draw
				a vertical lines at the dates
				corresponding to a paper appearing
			pickVal (float, default 6): the picker tolerance

		Output:
			False if paper==False and author==False,
			the matplotlib.pyplot figure containing
				the citation plot if paper==True,
			a list of matplotlib.pyplot figures containing
				the various plots if author==True
		"""
		if paper and self.paperPlotInfo is not None:
			if len(self.paperPlotInfo["citList"][0]) > 0:
				pBLogger.info(
					"Plotting for paper '%s'..."%self.paperPlotInfo["id"])
				fig, ax = plt.subplots()
				plt.plot(self.paperPlotInfo["citList"][0],
					self.paperPlotInfo["citList"][1], picker=pickVal)
				fig.autofmt_xdate()
				if save:
					pdf = PdfPages(
						osp.join(path, self.paperPlotInfo["id"]+'.pdf'))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
				return fig
		elif author and self.authorPlotInfo is not None:
			pBLogger.info(
				"Plotting for author '%s'..."%self.authorPlotInfo["name"])
			try:
				ymin = min(
					int(self.authorPlotInfo["allLi"][0][0].strftime("%Y"))-2,
					int(self.authorPlotInfo["paLi"][0][0].strftime("%Y"))-2)
				ymax = max(
					int(self.authorPlotInfo["allLi"][0][-1].strftime("%Y"))+2,
					int(self.authorPlotInfo["paLi"][0][-1].strftime("%Y"))+2)
			except:
				try:
					ymin = int(
						self.authorPlotInfo["paLi"][0][0].strftime("%Y"))-2
					ymax = int(
						self.authorPlotInfo["paLi"][0][-1].strftime("%Y"))+2
				except:
					pBLogger.warning("No publications for this author?")
					return False
			figs = []
			if len(self.authorPlotInfo["paLi"][0]) > 0:
				fig, ax = plt.subplots()
				plt.title("Paper number")
				plt.plot(self.authorPlotInfo["paLi"][0],
					self.authorPlotInfo["paLi"][1],
					picker=pickVal)
				fig.autofmt_xdate()
				if save:
					pdf = PdfPages(osp.join(
						path, self.authorPlotInfo["name"]+'_papers.pdf'))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
				figs.append(fig)

			if len(self.authorPlotInfo["paLi"][0]) > 0:
				fig, ax = plt.subplots()
				plt.title("Papers per year")
				ax.hist([int(q.strftime("%Y")) \
					for q in self.authorPlotInfo["paLi"][0]],
					bins=range(ymin, ymax), picker=True)
				ax.get_xaxis().get_major_formatter().set_useOffset(False)
				plt.xlim([ymin, ymax])
				if save:
					pdf = PdfPages(osp.join(path,
						self.authorPlotInfo["name"]+'_yearPapers.pdf'))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
				figs.append(fig)

			if len(self.authorPlotInfo["allLi"][0]) > 0:
				fig, ax = plt.subplots()
				plt.title("Total citations")
				plt.plot(self.authorPlotInfo["allLi"][0],
					self.authorPlotInfo["allLi"][1], picker=pickVal)
				fig.autofmt_xdate()
				if save:
					pdf = PdfPages(osp.join(path,
						self.authorPlotInfo["name"]+'_allCit.pdf'))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
				figs.append(fig)

			if len(self.authorPlotInfo["allLi"][0]) > 0:
				fig, ax = plt.subplots()
				plt.title("Citations per year")
				ax.hist([int(q.strftime("%Y")) \
					for q in self.authorPlotInfo["allLi"][0]],
					bins=range(ymin, ymax), picker=True)
				ax.get_xaxis().get_major_formatter().set_useOffset(False)
				plt.xlim([ymin, ymax])
				if save:
					pdf = PdfPages(osp.join(path,
						self.authorPlotInfo["name"]+'_yearCit.pdf'))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
				figs.append(fig)

			if len(self.authorPlotInfo["meanLi"][0]) > 0:
				fig, ax = plt.subplots()
				plt.title("Mean citations")
				plt.plot(self.authorPlotInfo["meanLi"][0],
					self.authorPlotInfo["meanLi"][1], picker=pickVal)
				fig.autofmt_xdate()
				if markPapers:
					for q in self.authorPlotInfo["paLi"][0]:
						plt.axvline(datetime.datetime(int(q.strftime("%Y")),
							int(q.strftime("%m")),
							int(q.strftime("%d"))),
							color='k',
							ls='--')
				if save:
					pdf = PdfPages(osp.join(path,
						self.authorPlotInfo["name"]+'_meanCit.pdf'))
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
						plt.plot(
							self.authorPlotInfo["aI"][p][
								"citingPapersList"][0],
							self.authorPlotInfo["aI"][p][
								"citingPapersList"][1])
					except:
						pBLogger.exception(
							"Something went wrong while plotting...")
				fig.autofmt_xdate()
				if save:
					pdf = PdfPages(osp.join(path,
						self.authorPlotInfo["name"]+'_paperCit.pdf'))
					pdf.savefig()
					pdf.close()
				if show:
					plt.show()
				plt.close()
				figs.append(fig)
			return figs
		else:
			pBLogger.info("Nothing to plot...")
			return False


pBStats = InspireStatsLoader()
