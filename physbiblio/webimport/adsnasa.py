"""Module that deals with importing info from the ADS API.

This file is part of the physbiblio package.
"""
import traceback

import ads

try:
    from physbiblio.config import pbConfig
    from physbiblio.errors import pBLogger
    from physbiblio.strings.webimport import ADSNasaStrings
    from physbiblio.webimport.webInterf import WebInterf
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise


class WebSearch(WebInterf, ADSNasaStrings):
    """Subclass of WebInterf that can connect to ADS to perform searches"""

    name = "ADS-NASA fetcher"
    description = "fetcher for ADS from NASA"
    url = "https://ui.adsabs.harvard.edu/"
    loadFields = [
        "abstract",
        "arxiv_class",
        "author",
        "bibcode",
        "citation_count",
        "doi",
        "first_author",
        "pubdate",
        "title",
        "year",
    ]
    fewFields = ["author", "first_author", "bibcode", "id", "year", "title"]

    def getGenericInfo(
        self, string, fields, rows=pbConfig.params["maxExternalAPIResults"]
    ):
        """Use the unofficial python client for the ADS API to obtain
        a list of results from a given search string

        Parameters:
            string: the search string
            fields: a list with the names of the required fields
            rows: the number of rows to obtain

        Output:
            a list of ads objects with the obtained entries
        """
        ads.config.token = pbConfig.params["ADSToken"]
        try:
            self.q = ads.SearchQuery(q=string, fl=fields, rows=rows)
            l = list(self.q)
        except ads.exceptions.APIResponseError:
            pBLogger.exception(self.unauthorized)
        except Exception:
            pBLogger.exception(self.genericFetchError, exc_info=True)
        else:
            pBLogger.info(self.getLimitInfo())
            return l
        return []

    def getBibtexs(self, bibcodes):
        """Obtain a string containing the bibtex entries for all the
        requested bibcodes

        Parameter:
            bibcodes: a single bibcode
                (string containing the ADS identifier of a given entry)
                or a list of bibcodes

        Output:
            a string with all the bibtex entries
        """
        ads.config.token = pbConfig.params["ADSToken"]
        try:
            self.q = ads.ExportQuery(bibcodes=bibcodes, format="bibtex")
            export = self.q.execute()
        except ads.exceptions.APIResponseError:
            pBLogger.exception(self.unauthorized)
        except Exception:
            pBLogger.exception(self.genericExportError, exc_info=True)
        else:
            pBLogger.info(self.getLimitInfo())
            return export
        return ""

    def retrieveUrlFirst(self, string):
        """Retrieves the first result from the given search.

        Parameters:
            string: the search string

        Output:
            returns a bibtex string with the first obtained bibtex entry
        """
        a = self.getGenericInfo(string, self.fewFields)
        if len(a) > 0:
            return self.getBibtexs(a[0].bibcode)
        else:
            return ""

    def retrieveUrlAll(self, string):
        """Retrieves all the results from the given search.

        Parameters:
            string: the search string

        Output:
            returns a string with all the bibtex entries
        """
        a = self.getGenericInfo(string, self.fewFields)
        return self.getBibtexs([p.bibcode for p in a])

    def getField(self, string, field):
        """Perform a search and return the value of a specific field
        as given by the ADS API

        Parameters:
            string: the search string
            field: the field name (must be in self.loadFields)

        Output:
            a list with the field values for all the obtained entries
        """
        if not field in self.loadFields:
            pBLogger.warning(self.invalidField % field)
            return []
        a = self.getGenericInfo(string, self.loadFields)
        return [getattr(p, field) for p in a]

    def getLimitInfo(self):
        """Return a dictionary with the information on the query limits"""
        lims = self.q.response.get_ratelimits()
        return self.remainingQueries % (lims["remaining"], lims["limit"])
