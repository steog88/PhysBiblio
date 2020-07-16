"""Module that deals with importing info from the ISBN2Bibtex API.

This file is part of the physbiblio package.
"""
import traceback

try:
    from physbiblio.errors import pBLogger
    from physbiblio.parseAccents import parse_accents_str
    from physbiblio.strings.webimport import ISBNStrings
    from physbiblio.webimport.webInterf import WebInterf
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise


class WebSearch(WebInterf, ISBNStrings):
    """Subclass of WebInterf that can connect to ISBN2Bibtex
    to perform searches
    """

    name = "isbn"
    description = "ISBN to bibtex"
    url = "http://www.ebook.de/de/tools/isbn2bibtex"

    def __init__(self):
        """Initializes the class variables
        using the WebInterf constructor.

        Define additional specific parameters for the ISBN2Bibtex API.
        """
        WebInterf.__init__(self)
        self.urlArgs = {}

    def retrieveUrlFirst(self, string):
        """Retrieves the first (only) result from the content
        of the given web page.

        Parameters:
            string: the search string (the ISBN)

        Output:
            returns the bibtex string
        """
        self.urlArgs["isbn"] = string
        url = self.createUrl()
        pBLogger.info(self.searchInfo % (string, url))
        text = self.textFromUrl(url)
        if "Not found" in text:
            return ""
        try:
            return parse_accents_str(text[:])
        except Exception:
            pBLogger.exception(self.genericError)
            return ""

    def retrieveUrlAll(self, string):
        """Alias for retrieveUrlFirst"""
        return self.retrieveUrlFirst(string)
