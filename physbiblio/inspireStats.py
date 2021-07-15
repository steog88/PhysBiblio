"""Module that uses INSPIRE-HEP to get author
(number of papers, h index, citations) and paper statistics (citations).

Uses matplotlib to do plots.

This file is part of the physbiblio package.
"""
import datetime
import json
import os
import os.path as osp
import traceback

import dateutil
import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pytz
from matplotlib.backends.backend_pdf import PdfPages

plt.switch_backend("Qt5Agg")
os.environ["QT_API"] = "pyside2"

try:
    from physbiblio.config import pbConfig
    from physbiblio.errors import pBLogger
    from physbiblio.strings.main import InspireStatsStrings as isstr
    from physbiblio.webimport.webInterf import physBiblioWeb
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise


class InspireStatsLoader:
    """Class that contains the methods
    to collect information from INSPIRE-HEP
    """

    authorPlotInfo = {}
    paperPlotInfo = {}

    def __init__(self):
        """The class constructor,
        defines some constants and search options
        """
        self.authorPlotInfo = None
        self.paperPlotInfo = None
        self.allInfoA = {}
        self.authorPapersList = [[], []]
        self.allCitations = []
        self.runningAuthorStats = True
        self.runningPaperStats = True
        self.allInfoP = {}
        self.citingPapersList = [[], []]

    def changeBackend(self, wantBackend):
        """Changes the matplotlib backend currently in use.

        Parameters:
            wantBackend: a string that defines the wanted backend
        """
        if wantBackend != matplotlib.get_backend():
            matplotlib.use(wantBackend, warn=False, force=True)
            from matplotlib import pyplot as plt

            pBLogger.info(isstr.changeBackend % matplotlib.get_backend())

    def authorStats(self, authorName, plot=False, reset=True, pbMax=None, pbVal=None):
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
            pbMax (callable, optional): a function to set the maximum
                of a progress bar in the GUI, if possible
            pbVal (callable, optional): a function to set the value
                of a progress bar in the GUI, if possible

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
            self.authorPapersList = [[], []]
            self.allCitations = []
        if isinstance(authorName, list):
            try:
                pbMax(len(authorName))
            except TypeError:
                pass
            for ia, a in enumerate(authorName):
                try:
                    pbVal(ia + 1)
                except TypeError:
                    pass
                self.authorStats(a, reset=False)
            self.authorPlotInfo["name"] = authorName
            return self.authorPlotInfo
        pBLogger.info(isstr.authorStats % authorName)
        data, tot = physBiblioWeb.webSearch["inspire"].retrieveSearchResults(
            "author:%s" % authorName, fields=["control_number"]
        )
        recid_authorPapers = sorted(["%s" % a["id"] for a in data])
        tot = len(recid_authorPapers)
        pBLogger.info(isstr.authorStatsProcess % tot)
        self.runningAuthorStats = True
        try:
            pbMax(tot)
        except TypeError:
            pass
        batchSize = pbConfig.params["batchSizeInspire"]
        for i in range(0, tot, batchSize):
            entries, nume = physBiblioWeb.webSearch["inspire"].retrieveBatchQuery(
                recid_authorPapers[i : i + batchSize],
                searchFormat="recid:%s",
                fields=["control_number", "references.record"],
            )
            references, numr = physBiblioWeb.webSearch["inspire"].retrieveBatchQuery(
                recid_authorPapers[i : i + batchSize],
                searchFormat="refersto:recid:%s",
                fields=["control_number", "references.record"],
            )
            # fill here list of citations for each entry, use references->reference:record
            current = []
            for e in entries:
                eid = e["id"]
                refs = []
                for r in references:
                    if eid in [
                        a["record"]["$ref"].replace(
                            physBiblioWeb.webSearch["inspire"].url, ""
                        )
                        for a in r["metadata"]["references"]
                    ]:
                        refs.append(r)
                current.append([e, refs])

            for ix, (e, r) in enumerate(current):
                try:
                    pbVal(i + ix + 1)
                except TypeError:
                    pass
                if not self.runningAuthorStats:
                    pBLogger.info(isstr.stopReceived)
                    break
                p = e["id"]
                if p in self.allInfoA.keys():
                    continue
                self.allInfoA[p] = {}
                self.allInfoA[p]["date"] = dateutil.parser.parse(e["created"])
                self.authorPapersList[0].append(self.allInfoA[p]["date"])
                pBLogger.info(
                    isstr.authorStatsLooking
                    % (i + ix + 1, tot, 100.0 * (i + ix + 1) / tot, p)
                )
                paperInfo = self.paperStats(
                    p, verbose=0, paperDate=self.allInfoA[p]["date"], useData=r
                )
                self.allInfoA[p]["infoDict"] = paperInfo["aI"]
                self.allInfoA[p]["citingPapersList"] = paperInfo["citList"]
                for c, v in self.allInfoA[p]["infoDict"].items():
                    self.allCitations.append(v["date"])
                pBLogger.info("")

        self.authorPapersList[1] = []
        for i, p in enumerate(sorted(self.authorPapersList[0])):
            self.authorPapersList[0][i] = p
            self.authorPapersList[1].append(i + 1)
        pBLogger.info(isstr.savingCitations)
        allCitList = [[], []]
        meanCitList = [[], []]
        currPaper = 0
        for i, d in enumerate(sorted(self.allCitations)):
            if (
                currPaper < len(self.authorPapersList[0]) - 1
                and d >= self.authorPapersList[0][currPaper + 1]
            ):
                currPaper += 1
            allCitList[0].append(d)
            allCitList[1].append(i + 1)
            meanCitList[0].append(d)
            meanCitList[1].append((i + 1.0) / self.authorPapersList[1][currPaper])
        hind = 0
        citations = [
            len(self.allInfoA[k]["citingPapersList"][0]) - 2
            for k in self.allInfoA.keys()
        ]
        for h in range(len(citations)):
            if len([a for a in citations if a >= h]) >= h:
                hind = h
        self.authorPlotInfo = {
            "name": authorName,
            "aI": self.allInfoA,
            "paLi": self.authorPapersList,
            "allLi": allCitList,
            "meanLi": meanCitList,
            "h": hind,
        }
        if plot:
            self.authorPlotInfo["figs"] = self.plotStats(author=True)
        pBLogger.info(isstr.authorStatsCompleted % authorName)
        return self.authorPlotInfo

    def paperStats(
        self,
        paperID,
        plot=False,
        verbose=1,
        paperDate=None,
        reset=True,
        pbMax=None,
        pbVal=None,
        useData=None,
    ):
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
            pbMax (callable, optional): a function to set the maximum
                of a progress bar in the GUI, if possible
            pbVal (callable, optional): a function to set the value
                of a progress bar in the GUI, if possible
            useData (default None): if not None, the data to use
                instead of reading them from INSPIRE

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
            self.citingPapersList = [[], []]
        if isinstance(paperID, list):
            self.runningPaperStats = True
            try:
                pbMax(len(paperID))
            except TypeError:
                pass
            for ia, a in enumerate(paperID):
                try:
                    pbVal(ia + 1)
                except TypeError:
                    pass
                if self.runningPaperStats:
                    self.paperStats(a, reset=False)
            self.paperPlotInfo["id"] = paperID
            return self.paperPlotInfo
        if verbose > 0:
            pBLogger.info(isstr.paperStats % paperID)
        if useData is not None:
            data = useData
        else:
            data, tot = physBiblioWeb.webSearch["inspire"].retrieveSearchResults(
                "refersto:recid:%s" % paperID, fields=["control_number"]
            )
        self.readPaperStats(paperID, data, paperDate=paperDate)
        if plot:
            self.paperPlotInfo["fig"] = self.plotStats(paper=True)
        if verbose > 0:
            pBLogger.info(isstr.doneE)
        return self.paperPlotInfo

    def plotStats(
        self,
        paper=False,
        author=False,
        show=False,
        save=False,
        path=".",
        markPapers=False,
        pickVal=6,
    ):
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
                pBLogger.info(isstr.plotPaper % self.paperPlotInfo["id"])
                fig, ax = plt.subplots()
                plt.plot(
                    self.paperPlotInfo["citList"][0],
                    self.paperPlotInfo["citList"][1],
                    picker=True,
                    pickradius=pickVal,
                )
                fig.autofmt_xdate()
                if save:
                    pdf = PdfPages(osp.join(path, self.paperPlotInfo["id"] + ".pdf"))
                    pdf.savefig()
                    pdf.close()
                if show:
                    plt.show()
                plt.close()
                return fig
        elif author and self.authorPlotInfo is not None:
            pBLogger.info(isstr.plotAuthor % self.authorPlotInfo["name"])
            try:
                ymin = min(
                    int(self.authorPlotInfo["allLi"][0][0].strftime("%Y")) - 2,
                    int(self.authorPlotInfo["paLi"][0][0].strftime("%Y")) - 2,
                )
                ymax = max(
                    int(self.authorPlotInfo["allLi"][0][-1].strftime("%Y")) + 2,
                    int(self.authorPlotInfo["paLi"][0][-1].strftime("%Y")) + 2,
                )
            except:
                try:
                    ymin = int(self.authorPlotInfo["paLi"][0][0].strftime("%Y")) - 2
                    ymax = int(self.authorPlotInfo["paLi"][0][-1].strftime("%Y")) + 2
                except:
                    pBLogger.warning(isstr.noPublications)
                    return False
            figs = []
            if len(self.authorPlotInfo["paLi"][0]) > 0:
                fig, ax = plt.subplots()
                plt.title(isstr.paperNumber)
                plt.plot(
                    self.authorPlotInfo["paLi"][0],
                    self.authorPlotInfo["paLi"][1],
                    picker=True,
                    pickradius=pickVal,
                )
                fig.autofmt_xdate()
                if save:
                    pdf = PdfPages(
                        osp.join(path, self.authorPlotInfo["name"] + "_papers.pdf")
                    )
                    pdf.savefig()
                    pdf.close()
                if show:
                    plt.show()
                plt.close()
                figs.append(fig)

            if len(self.authorPlotInfo["paLi"][0]) > 0:
                fig, ax = plt.subplots()
                plt.title(isstr.paperYear)
                ax.hist(
                    [int(q.strftime("%Y")) for q in self.authorPlotInfo["paLi"][0]],
                    bins=range(ymin, ymax),
                    picker=True,
                )
                ax.get_xaxis().get_major_formatter().set_useOffset(False)
                plt.xlim([ymin, ymax])
                if save:
                    pdf = PdfPages(
                        osp.join(path, self.authorPlotInfo["name"] + "_yearPapers.pdf")
                    )
                    pdf.savefig()
                    pdf.close()
                if show:
                    plt.show()
                plt.close()
                figs.append(fig)

            if len(self.authorPlotInfo["allLi"][0]) > 0:
                fig, ax = plt.subplots()
                plt.title(isstr.totalCitations)
                plt.plot(
                    self.authorPlotInfo["allLi"][0],
                    self.authorPlotInfo["allLi"][1],
                    picker=True,
                    pickradius=pickVal,
                )
                fig.autofmt_xdate()
                if save:
                    pdf = PdfPages(
                        osp.join(path, self.authorPlotInfo["name"] + "_allCit.pdf")
                    )
                    pdf.savefig()
                    pdf.close()
                if show:
                    plt.show()
                plt.close()
                figs.append(fig)

            if len(self.authorPlotInfo["allLi"][0]) > 0:
                fig, ax = plt.subplots()
                plt.title(isstr.citationsYear)
                ax.hist(
                    [int(q.strftime("%Y")) for q in self.authorPlotInfo["allLi"][0]],
                    bins=range(ymin, ymax),
                    picker=True,
                )
                ax.get_xaxis().get_major_formatter().set_useOffset(False)
                plt.xlim([ymin, ymax])
                if save:
                    pdf = PdfPages(
                        osp.join(path, self.authorPlotInfo["name"] + "_yearCit.pdf")
                    )
                    pdf.savefig()
                    pdf.close()
                if show:
                    plt.show()
                plt.close()
                figs.append(fig)

            if len(self.authorPlotInfo["meanLi"][0]) > 0:
                fig, ax = plt.subplots()
                plt.title(isstr.meanCitations)
                plt.plot(
                    self.authorPlotInfo["meanLi"][0],
                    self.authorPlotInfo["meanLi"][1],
                    picker=True,
                    pickradius=pickVal,
                )
                fig.autofmt_xdate()
                if markPapers:
                    for q in self.authorPlotInfo["paLi"][0]:
                        plt.axvline(
                            datetime.datetime(
                                int(q.strftime("%Y")),
                                int(q.strftime("%m")),
                                int(q.strftime("%d")),
                            ),
                            color="k",
                            ls="--",
                        )
                if save:
                    pdf = PdfPages(
                        osp.join(path, self.authorPlotInfo["name"] + "_meanCit.pdf")
                    )
                    pdf.savefig()
                    pdf.close()
                if show:
                    plt.show()
                plt.close()
                figs.append(fig)

            if len(self.authorPlotInfo["aI"].keys()) > 0:
                fig, ax = plt.subplots()
                plt.title(isstr.citationsPaper)
                for i, p in enumerate(self.authorPlotInfo["aI"].keys()):
                    try:
                        plt.plot(
                            self.authorPlotInfo["aI"][p]["citingPapersList"][0],
                            self.authorPlotInfo["aI"][p]["citingPapersList"][1],
                        )
                    except:
                        pBLogger.exception(isstr.errorPlotting)
                fig.autofmt_xdate()
                if save:
                    pdf = PdfPages(
                        osp.join(path, self.authorPlotInfo["name"] + "_paperCit.pdf")
                    )
                    pdf.savefig()
                    pdf.close()
                if show:
                    plt.show()
                plt.close()
                figs.append(fig)
            return figs
        else:
            pBLogger.info(isstr.noPlot)
            return False

    def readPaperStats(
        self,
        paperID,
        data,
        paperDate=None,
    ):
        """Function that reads the data on a paper and
        constructs the corresponding statistics.

        Parameters:
            paperID (string): the INSPIRE-HEP id of the paper (a number)
            data (string): the INSPIRE-HEP id of the paper (a number)
            paperDate (datetime, optional): the date of at which
                the paper was published

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
        recid_citingPapers = [a["id"] for a in data]
        if paperDate is not None:
            self.citingPapersList[0].append(paperDate)
        for i, p in enumerate(recid_citingPapers):
            self.allInfoP[p] = {}
            self.allInfoP[p]["date"] = dateutil.parser.parse(data[i]["created"])
            self.citingPapersList[0].append(
                self.allInfoP[p]["date"].replace(tzinfo=pytz.UTC)
            )
        for i, p in enumerate(sorted(self.citingPapersList[0])):
            self.citingPapersList[0][i] = p
            self.citingPapersList[1].append(i + 1)
        self.citingPapersList[0].append(
            datetime.datetime.fromordinal(datetime.date.today().toordinal()).replace(
                tzinfo=pytz.UTC
            )
        )
        try:
            self.citingPapersList[1].append(self.citingPapersList[1][-1])
        except IndexError:
            self.citingPapersList[1].append(0)
        self.paperPlotInfo = {
            "id": paperID,
            "aI": self.allInfoP,
            "citList": self.citingPapersList,
        }


pBStats = InspireStatsLoader()
