"""Module that deals with importing info from the arXiv API.

Uses feedparser module to read the page content.

This file is part of the physbiblio package.
"""
import re
import sys
import traceback

import feedparser

try:
    from bibtexparser.bibdatabase import BibDatabase

    from physbiblio.bibtexWriter import pbWriter
    from physbiblio.config import pbConfig
    from physbiblio.errors import pBLogger
    from physbiblio.parseAccents import parse_accents_str
    from physbiblio.strings.webimport import ArxivStrings
    from physbiblio.webimport.webInterf import WebInterf, physBiblioWeb
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise


arxivCategories = {
    "astro-ph": ["CO", "EP", "GA", "HE", "IM", "SR"],
    "cond-mat": [
        "dis-nn",
        "mes-hall",
        "mtrl-sci",
        "other",
        "quant-gas",
        "soft",
        "stat-mech",
        "str-el",
        "supr-con",
    ],
    "cs": [
        "AI",
        "AR",
        "CC",
        "CE",
        "CG",
        "CL",
        "CR",
        "CV",
        "CY",
        "DB",
        "DC",
        "DL",
        "DM",
        "DS",
        "ET",
        "FL",
        "GL",
        "GR",
        "GT",
        "HC",
        "IR",
        "IT",
        "LG",
        "LO",
        "MA",
        "MM",
        "MS",
        "NA",
        "NE",
        "NI",
        "OH",
        "OS",
        "PF",
        "PL",
        "RO",
        "SC",
        "SD",
        "SE",
        "SI",
        "SY",
    ],
    "econ": ["EM", "GN", "TH"],
    "eess": ["AS", "IV", "SP"],
    "gr-qc": [],
    "hep-ex": [],
    "hep-lat": [],
    "hep-ph": [],
    "hep-th": [],
    "math": [
        "AC",
        "AG",
        "AP",
        "AT",
        "CA",
        "CO",
        "CT",
        "CV",
        "DG",
        "DS",
        "FA",
        "GM",
        "GN",
        "GR",
        "GT",
        "HO",
        "IT",
        "KT",
        "LO",
        "MG",
        "MP",
        "NA",
        "NT",
        "OA",
        "OC",
        "PR",
        "QA",
        "RA",
        "RT",
        "SG",
        "SP",
        "ST",
    ],
    "math-ph": [],
    "nlin": ["AO", "CD", "CG", "PS", "SI"],
    "nucl-ex": [],
    "nucl-th": [],
    "physics": [
        "acc-ph",
        "ao-ph",
        "app-ph",
        "atm-clus",
        "atom-ph",
        "bio-ph",
        "chem-ph",
        "class-ph",
        "comp-ph",
        "data-an",
        "ed-ph",
        "flu-dyn",
        "gen-ph",
        "geo-ph",
        "hist-ph",
        "ins-det",
        "med-ph",
        "optics",
        "plasm-ph",
        "pop-ph",
        "soc-ph",
        "space-ph",
    ],
    "q-bio": ["BM", "CB", "GN", "MN", "NC", "OT", "PE", "QM", "SC", "TO"],
    "q-fin": ["CP", "EC", "GN", "MF", "PM", "PR", "RM", "ST", "TR"],
    "quant-ph": [],
    "stat": ["AP", "CO", "ME", "ML", "OT", "TH"],
}


def isValidArxiv(string):
    """Determine if the string is a valid arXiv identifier
    (this does not mean that it exists)

    Parameter:
        string: the string to test

    Output:
        boolean
    """
    if "arxiv:" in string:
        string = string.replace("arxiv:", "")
    if re.match(
        "^[0-9]{4}\.[0-9]{4,5}(v[0-9]+)?$",
        string,
    ):
        return True
    elif re.match(
        "^[a-zA-Z]+(\-[a-zA-Z]+)?(\.[a-zA-Z]+(\-[a-zA-Z]+)?)?/[0-9]{7}(v[0-9]+)?$",
        string,
    ):
        if "." in string:
            matchcat = re.compile(
                "([a-zA-Z]+(\-[a-zA-Z]+)?)\.([a-zA-Z]+(\-[a-zA-Z]+)?)/"
            )
            for t in matchcat.finditer(string):
                cat = t.group(1)
                sub = t.group(3)
            if cat in arxivCategories.keys() and sub in arxivCategories[cat]:
                return True
        else:
            matchcat = re.compile("([a-zA-Z]+(\-[a-zA-Z]+)?)/")
            for t in matchcat.finditer(string):
                cat = t.group(1)
            if cat in arxivCategories.keys():
                return True
        return False
    else:
        return False


def getYear(string):
    """Use the arxiv id to compute the year

    Parameter:
        string: the arxiv identifier

    Output:
        a string containing the year of the submission to arXiv
    """
    identif = re.compile("(([a-zA-Z\-]+/)([0-9]{7}))|([0-9]{4}\.[0-9]{4,5})")
    try:
        for t in identif.finditer(string):
            if len(t.group()) > 0:
                try:
                    a = t.group(3)[:2]  # match first type, e.g. hep-ex/0101001
                except (IndexError, TypeError):
                    a = t.group(4)[
                        :2
                    ]  # match second type, e.g. 1301.0123 or 1501.01234
                if int(a) > 90:
                    return "19" + a
                else:
                    return "20" + a
    except (IndexError, TypeError):
        pBLogger.warning(ArxivStrings.errorYearConversion % string)
        return None


class WebSearch(WebInterf, ArxivStrings):
    """Subclass of WebInterf that can connect to arxiv.org
    to perform searches
    """

    name = "arXiv"
    description = "arXiv fetcher"
    url = "https://export.arxiv.org/api/query"
    urlRss = "https://export.arxiv.org/rss/"
    categories = arxivCategories

    def __init__(self):
        """Initializes the class variables using
        the WebInterf constructor.

        Define additional specific parameters for the arxiv.org API.
        """
        WebInterf.__init__(self)
        self.urlArgs = {"start": "0"}

    def getYear(self, string):
        """Use the arxiv id to compute the year"""
        return getYear(string)

    def retrieveUrlFirst(self, string, searchType="all", **kwargs):
        """Retrieves the first result from the content
        of the given web page.
        The function calls arxivRetriever which will do the job.

        Parameters:
            string: the search string
            searchType: the search method in arxiv API (default 'all')

        Output:
            returns the bibtex string built from arxivRetriever
        """
        return self.arxivRetriever(
            string, searchType, additionalArgs={"max_results": "1"}, **kwargs
        )

    def retrieveUrlAll(self, string, searchType="all", **kwargs):
        """Retrieves all the results from the content
        of the given web page.
        The function calls arxivRetriever which will do the job.

        Parameters:
            string: the search string
            searchType: the search method in arxiv API (default 'all')

        Output:
            returns the bibtex string built from arxivRetriever
        """
        return self.arxivRetriever(
            string,
            searchType,
            additionalArgs={"max_results": pbConfig.params["maxExternalAPIResults"]},
            **kwargs
        )

    def arxivRetriever(
        self, string, searchType="all", additionalArgs=None, fullDict=False
    ):
        """Reads the feed content got from arxiv into a dictionary,
        used to return a bibtex.

        Parameters:
            string: the search string
            searchType: the search method in arxiv API (default 'all').
                The possible values are:
                    ti  -> Title
                    au  -> Author
                    abs -> Abstract
                    co  -> Comment
                    jr  -> Journal Reference
                    cat -> Subject Category
                    rn  -> Report Number
                    id  -> Id (use id_list instead)
                    all -> All of the above
            additionalArgs: a dictionary of additional arguments
                that can be passed to self.urlArgs (default None)
            fullDict (logical): return the bibtex dictionary in addition
                to the bibtex text (default False)

        Output:
            the bibtex text
            (optional, depending on fullDict): the bibtex Dictionary
        """

        def returnFailed():
            """Define output of the function when an error occurred"""
            if fullDict:
                return "", {}
            else:
                return ""

        urlArgs = self.urlArgs.copy()
        if additionalArgs:
            try:
                for k, v in additionalArgs.items():
                    urlArgs[k] = v
            except (AttributeError, TypeError):
                pass
        urlArgs["search_query"] = searchType + ":" + string
        url = self.createUrl(urlArgs)
        pBLogger.info(self.searchInfo % (searchType, string, url))
        text = parse_accents_str(self.textFromUrl(url))
        try:
            data = feedparser.parse(text)
        except Exception:  # intercept all possible errors
            pBLogger.exception(self.cannotParseRSS % text, exc_info=True)
            return returnFailed()
        if "entries" not in data.keys():
            pBLogger.exception(self.cannotFindEntriesInFeed % data)
            return returnFailed()
        db = BibDatabase()
        db.entries = []
        dictionaries = []
        for entry in data["entries"]:
            dictionary = {"ENTRYTYPE": "article", "archiveprefix": "arXiv"}
            try:
                idArx = (
                    entry["id"]
                    .replace("http://arxiv.org/abs/", "")
                    .replace("https://arxiv.org/abs/", "")
                )
            except (AttributeError, KeyError, TypeError):
                pBLogger.exception(self.cannotReadEntryId % entry)
                continue
            else:
                pos = idArx.find("v")
                if pos >= 0:
                    idArx = idArx[0:pos]
                dictionary["ID"] = idArx
                dictionary["arxiv"] = idArx
            for m, k in [["title", "title"], ["doi", "arxiv_doi"]]:
                try:
                    dictionary[m] = entry[k]
                except KeyError as e:
                    pBLogger.debug("KeyError: %s" % e)
            try:
                dictionary["abstract"] = entry["summary"].replace("\n", " ")
            except KeyError as e:
                pBLogger.debug("KeyError: %s" % e)
            try:
                dictionary["authors"] = " and ".join(
                    [au["name"] for au in entry["authors"]]
                )
            except KeyError as e:
                pBLogger.debug("KeyError: %s" % e)
            try:
                dictionary["primaryclass"] = entry["arxiv_primary_category"]["term"]
            except KeyError as e:
                pBLogger.debug("KeyError: %s" % e)
            try:
                year = self.getYear(dictionary["arxiv"])
            except KeyError as e:
                pBLogger.debug("KeyError: %s" % e)
            else:
                if year is not None:
                    dictionary["year"] = year
            db.entries.append(dictionary)
            dictionaries.append(dictionary)
        if fullDict:
            try:
                dictionary = dictionaries[0]
                for d in dictionaries:
                    if string in d["arxiv"]:
                        dictionary = d
            except (IndexError, TypeError):
                pBLogger.exception(self.cannotReadDict)
                return returnFailed()
            else:
                return pbWriter.write(db), dictionary
        else:
            return pbWriter.write(db)

    def arxivDaily(self, category):
        """Read daily RSS feed for a given category

        Parameter:
            category: the selected category (see `self.categories)
        """
        if "." in category:
            main, sub = category.split(".")
        else:
            main = category
            sub = ""
        url = self.urlRss
        if main not in self.categories.keys():
            pBLogger.warning(self.mainCatNotFound % main)
            return False
        else:
            url += main
        if sub != "" and sub not in self.categories[main]:
            pBLogger.warning(self.subCatNotFound % sub)
            return False
        elif sub != "" and sub in self.categories[main]:
            url += "." + sub
        pBLogger.info(url)
        text = self.textFromUrl(url)
        if text is None:
            pBLogger.warning(self.emptyUrl)
            return False
        author = re.compile("(>|&gt;)([^/]*)(</a>|&lt;/a&gt;)")
        additionalInfo = re.compile(
            " \(arXiv:([0-9\.v]*) \[([\-\.a-zA-Z]*)\]([ A-Z]*)\)"
        )
        if sys.version_info[0] < 3:
            text = text.decode("utf-8")
        text = parse_accents_str(text)
        try:
            data = feedparser.parse(text)
        except Exception:
            pBLogger.exception(self.cannotParseRSS % text)
            return False
        entries = []
        for element in data.entries:
            tmp = {}
            try:
                tmp["eprint"] = element["id"].split("/")[-1]
                tmp["abstract"] = (
                    element["summary"]
                    .replace("\n", " ")
                    .replace("<p>", "")
                    .replace("</p>", "")
                )
                tmp["authors"] = [
                    m.group(2)
                    for m in author.finditer(element["authors"][0]["name"])
                    if m != ""
                ]
                tmp["author"] = (
                    " and ".join(tmp["authors"])
                    if len(tmp["authors"]) < pbConfig.params["maxAuthorNames"]
                    else " and ".join(
                        tmp["authors"][0 : pbConfig.params["maxAuthorNames"]]
                        + ["others"]
                    )
                )
                tmp["replacement"] = "UPDATED" in element["title"]
                tmp["primaryclass"] = [
                    m.group(2)
                    for m in additionalInfo.finditer(element["title"])
                    if m != ""
                ][0]
                tmp["cross"] = (
                    "CROSS LISTED" in element["title"]
                    or category.lower() not in tmp["primaryclass"].lower()
                )
                tmp["version"] = [
                    m.group(1)
                    for m in additionalInfo.finditer(element["title"])
                    if m != ""
                ][0]
                parenthesis = [
                    m.group()
                    for m in additionalInfo.finditer(element["title"])
                    if m != ""
                ][0]
                tmp["title"] = element["title"].replace(parenthesis, "")
            except (IndexError, KeyError, TypeError):
                pBLogger.warning(self.cannotReadItem)
                continue
            else:
                entries.append(tmp)
        return entries
