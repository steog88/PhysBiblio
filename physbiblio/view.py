"""Module that opens the external links.

This file is part of the physbiblio package.
"""
import subprocess
import traceback

try:
    from physbiblio.config import pbConfig
    from physbiblio.database import pBDB
    from physbiblio.errors import pBLogger
    from physbiblio.pdf import pBPDF
    from physbiblio.strings.main import ViewStrings as vstr
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise


class ViewEntry:
    """Contains methods to print or open a web link to the entry"""

    def __init__(self):
        """Init the class, storing the name of
        the external web application
        and the base strings to build some links
        """
        self.webApp = pbConfig.params["webApplication"]
        self.inspireRecord = pbConfig.inspireLiteratureLink
        self.inspireSearch = pbConfig.inspireLiteratureLink + "?p="

    def getLink(self, key, arg="arxiv", fileArg=None):
        """Uses database information to construct and
        print the web link, or the pdf module to open a pdf

        Parameters:
            key: the bibtex identifier as stored in the database.
                It may be a list (calls recursively itself)
            arg: the string defining the type of link/action
                ("arxiv", "doi", "inspire", "file")
            fileArg: additional argument for the PDF module,
                used only if arg == "file"

        Output:
            link: the string of the web link
                if arg in ("arxiv", "doi", "inspire"),
                True if arg == "file",
                False if arg is invalid
        """
        if isinstance(key, list):
            links = []
            for k in key:
                if arg != "file":
                    links.append(self.getLink(k, arg, fileArg))
                else:
                    links.append(fileArg)
            return links
        ads = pBDB.bibs.getField(key, "ads")
        arxiv = pBDB.bibs.getField(key, "arxiv")
        doi = pBDB.bibs.getField(key, "doi")
        inspire = pBDB.bibs.getField(key, "inspire")
        if arg == "ads" and ads:
            link = pBDB.bibs.getAdsUrl(key)
        elif arg == "arxiv" and arxiv:
            link = pBDB.bibs.getArxivUrl(key, "abs")
        elif arg == "doi" and doi:
            link = pBDB.bibs.getDoiUrl(key)
        elif arg == "inspire" and inspire:
            link = self.inspireRecord + inspire
        elif arg == "inspire" and arxiv:
            link = self.inspireSearch + "arxiv:" + arxiv
        elif arg == "inspire":
            link = self.inspireSearch + key
        elif arg == "file":
            pBPDF.openFile(key, fileArg)
            return fileArg
        else:
            pBLogger.warning(vstr.warningInvalidUse % key)
            return False

        return link

    def openLink(self, key, arg="arxiv", fileArg=None):
        """Uses the getLink method to generate the web link
        and opens it in an external application

        Parameters:
            key, arg, fileArg as in the getLink method
        """
        if isinstance(key, list):
            for k in key:
                self.openLink(k, arg, fileArg)
        else:
            if arg == "file":
                self.getLink(key, arg=arg, fileArg=fileArg)
                return
            elif arg == "link":
                link = key
            else:
                link = self.getLink(key, arg=arg, fileArg=fileArg)
            if link:
                if self.webApp != "":
                    pBLogger.info(vstr.opening % link)
                    try:
                        subprocess.Popen(
                            [self.webApp, link],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                        )
                    except OSError:
                        pBLogger.warning(vstr.openingFailed % ("link", key))
            else:
                pBLogger.warning(vstr.errorLink % (arg, key))


pBView = ViewEntry()
