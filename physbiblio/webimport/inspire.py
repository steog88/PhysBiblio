"""Module that deals with importing info from the INSPIRE-HEP API.

This file is part of the physbiblio package.
"""
import traceback
import re

try:
    from physbiblio.errors import pBLogger
    from physbiblio.config import pbConfig
    from physbiblio.webimport.webInterf import WebInterf, physBiblioWeb
    from physbiblio.parseAccents import parse_accents_str
    from physbiblio.strings.webimport import InspireStrings
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise


class WebSearch(WebInterf, InspireStrings):
    """Subclass of WebInterf that can connect
    to INSPIRE-HEP to perform searches
    """

    name = "inspire"
    description = "INSPIRE fetcher"
    url = pbConfig.inspireSearchBase
    urlRecord = pbConfig.inspireRecord

    def __init__(self):
        """Initializes the class variables
        using the WebInterf constructor.

        Define additional specific parameters for the INSPIRE-HEP API.
        """
        WebInterf.__init__(self)
        self.urlArgs = {
            # "action_search": "Search",
            "sf": "year",
            "so": "a",
            "rg": "250",
            "sc": "0",
            "eb": "B",
            "of": "hx"
            # for bibtex format ---- hb for standard format,
            # for retrieving inspireid
        }

    def retrieveUrlFirst(self, string):
        """Retrieves the first result
        from the content of the given web page.

        Parameters:
            string: the search string

        Output:
            returns the bibtex string obtained from the API
        """
        self.urlArgs["p"] = string.replace(" ", "+")
        url = self.createUrl()
        pBLogger.info(self.searchInfo % (string, url))
        text = self.textFromUrl(url)
        try:
            i1 = text.find("<pre>")
            i2 = text.find("</pre>")
            if i1 > 0 and i2 > 0:
                bibtex = text[i1 + 5 : i2]
            else:
                bibtex = ""
            return parse_accents_str(bibtex)
        except Exception:
            pBLogger.exception(self.genericError)
            return ""

    def retrieveUrlAll(self, string):
        """Retrieves all the result
        from the content of the given web page.

        Parameters:
            string: the search string

        Output:
            returns the bibtex string obtained from the API
        """
        self.urlArgs["p"] = string.replace(" ", "+")
        url = self.createUrl()
        pBLogger.info(self.searchInfo % (string, url))
        text = self.textFromUrl(url)
        try:
            i1 = text.find("<pre>")
            i2 = text.rfind("</pre>")
            if i1 > 0 and i2 > 0:
                bibtex = text[i1 + 5 : i2]
            else:
                bibtex = ""
            return parse_accents_str(bibtex.replace("<pre>", "").replace("</pre>", ""))
        except Exception:
            pBLogger.exception(self.genericError)
            return ""

    def retrieveInspireID(self, string, number=None, isDoi=False, isArxiv=False):
        """Read the fetched content for a given entry
        to obtain its INSPIRE-HEP ID

        Parameters:
            string: the search string
            number (optional): the integer corresponding
                to the desired entry in the list,
                if more than one is present
            isDoi (default False): if the search string is a DOI,
                add the "doi" prefix in the url
            isArxiv (default False): if the search string is an arxiv id,
                add the "eprint" (and "arxiv:" if needed) prefix in the url
        """
        i = 0
        if isDoi:
            string = "doi+" + string
        elif isArxiv:
            if re.match("[0-9]{4}\.[0-9]{4,5}", string) and "arxiv:" not in string:
                string = "arxiv:" + string
            string = "eprint " + string
        self.urlArgs["p"] = string.replace(" ", "+")
        self.urlArgs["of"] = "hb"  # do not ask bibtex, but standard
        url = self.createUrl()
        self.urlArgs["of"] = "hx"  # restore
        pBLogger.info(self.searchIDInfo % (string, url))
        text = self.textFromUrl(url)
        if text is None:
            pBLogger.warning(self.errorEmptyText)
            return ""
        try:
            searchID = re.compile(
                'titlelink(.*)?(http|https)%s([0-9]*)?">'
                % (pbConfig.inspireRecord.replace("https", ""))
            )
            inspireID = ""
            for q in searchID.finditer(text):
                if len(q.group()) > 0:
                    if number is None or i == number:
                        inspireID = q.group(3)
                        break
                    else:
                        i += 1
            pBLogger.info(self.foundID % inspireID)
            return inspireID
        except Exception:
            pBLogger.exception(self.genericError)
            return ""
