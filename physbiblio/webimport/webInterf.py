"""Module that creates the base class WebInterf,
which will be used by other modules in this package.

Uses urllib to download url content.

This file is part of the physbiblio package.
"""
import os
import pkgutil
import socket
import ssl
import sys
import traceback

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

if sys.version_info[0] < 3:
    from urllib2 import HTTPError, Request, URLError, urlopen
else:
    from urllib.request import HTTPError, Request, URLError, urlopen

try:
    import physbiblio.webimport as wi
    from physbiblio.config import pbConfig
    from physbiblio.errors import pBLogger
    from physbiblio.strings.webimport import WebInterfStrings
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise

# scan package content to load list of available modules, to be imported later
pkgpath = os.path.dirname(wi.__file__)
webInterfaces = [name for _, name, _ in pkgutil.iter_modules([pkgpath])]


class PBSession(requests.Session):
    """Extends the Session class to include auto-retries"""

    def __init__(
        self,
        total_retries=5,
        backoff=1.0,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"],
        **kwargs
    ):
        """Extend the Session class.
        Input parameters are as from
        requests.packages.urllib3.util.retry.Retry or requests.Session.
        """
        retry_strategy = Retry(
            total=total_retries,
            backoff_factor=backoff,
            status_forcelist=status_forcelist,
            allowed_methods=method_whitelist,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        requests.Session.__init__(self, **kwargs)
        self.mount("https://", adapter)
        self.mount("http://", adapter)


class WebInterf(WebInterfStrings):
    """This is the main class for the web search methods.

    It contains a constructor, a function to create an appropriate url
    and to retrieve text from the url,
    a function to load other webinterfaces
    """

    url = None
    urlArgs = None
    urlTimeout = 1000.0
    interfaces = []

    def __init__(self):
        """Initializes the class variables."""
        self.urlTimeout = float(pbConfig.params["timeoutWebSearch"])
        # save the names of the available web search interfaces
        self.interfaces = [
            a for a in webInterfaces if a not in ["strings", "tests", "webInterf"]
        ]
        self.webSearch = {}
        self.loaded = False

    def createUrl(self, args=None, url=None):
        """Joins the arguments of the GET query to get the full url.

        Uses the self.urlArgs dictionary to generate the list
        of HTTP GET parameters, unless args is passed as an argument.

        Parameter:
            args (default None): a dictionary
            url (default None): a string

        Output:
            a string
        """
        if not isinstance(args, dict):
            args = self.urlArgs
        if not isinstance(url, str) or url == "":
            url = self.url
        return (
            url + "?" + "&".join(["%s=%s" % (a, b) for a, b in args.items()])
            if len(args) > 0
            else url
        )

    def textFromUrl(self, url, headers=None):
        """Use urllib to get the html content of the given url.

        Parameters:
            url: the url to be opened
            headers (default None): the additional headers
                to be passed to urllib.Request

        Output:
            text: the content of the url
        """
        http = PBSession()
        if not isinstance(headers, dict):
            headers = {}
        try:
            data = http.get(url, headers=headers, timeout=self.urlTimeout).content
        except URLError:
            pBLogger.warning(self.errorRetrieve % self.name)
            return ""
        except HTTPError:
            pBLogger.warning(self.errorNotFound % url)
            return ""
        except (ssl.SSLError, socket.timeout):
            pBLogger.warning(self.errorTimedOut % self.name)
            return ""
        try:
            text = data.decode("utf-8")
        except Exception:
            pBLogger.warning(self.errorBadCodification % self.name)
            return ""
        http.close()
        return text

    def retrieveUrlFirst(self, search):
        """Retrieves the first bibtexs that the search gives,
        using the subclass specific instructions.

        Parameter:
            search: the string to be searched

        Output:
            returns None in the default implementation
                (must be subclassed)
        """
        return None

    def retrieveUrlAll(self, search):
        """Retrieves all the bibtexs that the search gives,
        using the subclass specific instructions

        Parameter:
            search: the string to be searched

        Output:
            returns None in the default implementation
                (must be subclassed)
        """
        return None

    def loadInterfaces(self):
        """Load the subclasses that will interface
        with the main websites to search bibtex info
        and saves them into a dictionary (`self.webSearch`).

        The subclasses are read scanning the package directory.
        """
        if self.loaded:
            return
        for method in self.interfaces:
            try:
                _temp = __import__(
                    "physbiblio.webimport." + method, globals(), locals(), ["WebSearch"]
                )
                self.webSearch[method] = getattr(_temp, "WebSearch")()
            except Exception:
                pBLogger.exception(self.errorImportMethod % method)
        self.loaded = True

    def retrieveUrlFirstFrom(self, search, method):
        """Calls the function retrieveUrlFirst
        given the subclass method.

        Parameters:
            search: the search string
            method: the key of the method in `self.webSearch`

        Output:
            None in the default implementation (must be subclassed)
        """
        try:
            return getattr(self.webSearch[method], retrieveUrlFirst)(search)
        except KeyError:
            pBLogger.warning(self.methodNotAvailable % method)
            return ""

    def retrieveUrlAllFrom(self, search, method):
        """Calls the function retrieveUrlAll given the subclass method.

        Parameters:
            search: the search string
            method: the key of the method in `self.webSearch`

        Output:
            None in the default implementation (must be subclassed)
        """
        try:
            return getattr(self.webSearch[method], retrieveUrlAll)(search)
        except KeyError:
            pBLogger.warning(self.methodNotAvailable % method)
            return ""


physBiblioWeb = WebInterf()
physBiblioWeb.loadInterfaces()
