"""Module that deals with importing info from the INSPIRE-HEP API.

This file is part of the physbiblio package.
"""
import json
import re
import traceback

try:
    from physbiblio.config import pbConfig
    from physbiblio.errors import pBLogger
    from physbiblio.parseAccents import parse_accents_str
    from physbiblio.strings.webimport import InspireStrings
    from physbiblio.webimport.webInterf import WebInterf, physBiblioWeb
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
    url = pbConfig.inspireLiteratureAPI
    urlRecord = pbConfig.inspireLiteratureLink

    def __init__(self):
        """Initializes the class variables
        using the WebInterf constructor.

        Define additional specific parameters for the INSPIRE-HEP API.
        """
        WebInterf.__init__(self)
        self.urlArgs = {
            "sort": "mostrecent",
            "size": "250",
            "page": "1",
        }

    def retrieveBibtex(self, string, size=250):
        """Retrieves a list of bibtexs

        Parameters:
            string: the search string

        Output:
            returns the bibtex string obtained from the API
        """
        args = self.urlArgs.copy()
        args["q"] = string.replace(" ", "%20")
        args["size"] = str(size)
        args["format"] = "bibtex"
        url = self.createUrl(args)
        pBLogger.info(self.searchInfo % (string, url))
        text = self.textFromUrl(url)
        try:
            return parse_accents_str(text)
        except Exception:
            pBLogger.exception(self.genericError)
            return ""

    def retrieveUrlFirst(self, string):
        """Retrieves the first result
        from the content of the given web page.

        Parameters:
            string: the search string

        Output:
            returns the bibtex string obtained from the API
        """
        return self.retrieveBibtex(string, size=1)

    def retrieveUrlAll(self, string):
        """Retrieves all the result
        from the content of the given web page.

        Parameters:
            string: the search string

        Output:
            returns the bibtex string obtained from the API
        """
        return self.retrieveBibtex(string, size=250)

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
        args = self.urlArgs.copy()
        args["q"] = string.replace(" ", "%20")
        args["size"] = "1"
        try:
            args["page"] = int(number)
        except (TypeError, ValueError):
            pass
        url = self.createUrl(args)
        pBLogger.info(self.searchIDInfo % (string, url))
        text = self.textFromUrl(url)
        if text is None:
            pBLogger.warning(self.errorEmptyText)
            return ""
        try:
            results = json.loads(text)
        except json.decoder.JSONDecodeError:
            pBLogger.exception(self.jsonError)
            return ""
        try:
            inspireID = results["hits"]["hits"][0]["id"]
        except (IndexError, KeyError):
            pBLogger.exception(self.genericError)
            return ""
        pBLogger.info(self.foundID % inspireID)
        return inspireID
