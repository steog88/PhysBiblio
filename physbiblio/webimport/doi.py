"""Module that deals with importing info from the DOI.org API.

This file is part of the physbiblio package.
"""
import traceback

try:
    from physbiblio.config import pbConfig
    from physbiblio.errors import pBLogger
    from physbiblio.parseAccents import parse_accents_str
    from physbiblio.strings.webimport import DOIStrings
    from physbiblio.webimport.webInterf import WebInterf
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise


class WebSearch(WebInterf, DOIStrings):
    """Subclass of WebInterf that can connect
    to doi.org to perform searches
    """

    name = "doi"
    description = "DOI fetcher"
    url = pbConfig.doiUrl
    headers = {"accept": "application/x-bibtex"}

    def createUrl(self, doi):
        """Joins the base url and the search string to get the full url.

        (DOI.org url Behaves differently than other APIs
        in the modules of this subpackage)
        """
        return self.url + doi

    def retrieveUrlFirst(self, string):
        """Retrieves the first (only) result from the content
        of the given web page.

        Parameters:
            string: the search string (the DOI)

        Output:
            returns the bibtex string
        """
        url = self.createUrl(string)
        pBLogger.info(self.searchInfo % (string, url))
        text = self.textFromUrl(url, self.headers)
        if "<title>Error: DOI Not Found</title>" in text:
            return ""
        try:
            return parse_accents_str(text[:])
        except Exception:
            pBLogger.exception(self.genericError)
            return ""

    def retrieveUrlAll(self, string):
        """Alias for retrieveUrlFirst
        (no more than one object should match a doi)
        """
        return self.retrieveUrlFirst(string)
