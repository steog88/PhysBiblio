"""This module manages the saved PDF files and opens them if required.

This file is part of the physbiblio package.
"""
import os
import os.path as osp
import shutil
import subprocess
import sys
import traceback

import six

if sys.version_info[0] < 3:
    from urllib2 import HTTPError, URLError, urlopen
else:
    from urllib.request import HTTPError, URLError, urlopen


try:
    from physbiblio.config import pbConfig
    from physbiblio.database import pBDB
    from physbiblio.errors import pBLogger
    from physbiblio.strings.main import PDFStrings as pstr
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise


class LocalPDF:
    """Class with functions to manage the PDF folder content
    and the stored material
    """

    pdfDir = pbConfig.params["pdfFolder"]
    pdfApp = pbConfig.params["pdfApplication"]
    badFNameCharacters = r'\/:*?"<>|' + "'"

    def __init__(self):
        """Init the class and set some default variables"""
        self.checkFolderExists()
        self.pdfDir = pbConfig.params["pdfFolder"]
        self.pdfApp = pbConfig.params["pdfApplication"]

    def checkFolderExists(self):
        """Check if the PDF folder exists. If not, create it"""
        if not os.path.isdir(self.pdfDir):
            pBLogger.info(pstr.folderMissing % self.pdfDir)
            os.makedirs(self.pdfDir)

    def badFName(self, filename):
        """Clean the filename substituting the bad characters with '_'

        Parameters:
            filename (string): the string containing the file name

        Output:
            the cleaned filename
        """
        newFilename = ""
        if not isinstance(filename, six.string_types):
            pBLogger.warning(pstr.wrongType % filename)
            return ""
        for i in filename:
            if i not in self.badFNameCharacters:
                newFilename += i
            else:
                newFilename += "_"
        return newFilename

    def getFileDir(self, key):
        """Obtain the name of the directory for a given entry.
        The name is cleaned and the absolute path is generated.

        Parameters:
            key (string): the bibtex key of the entry

        Output:
            the (cleaned) absolute path for the PDF files
                associated with the entry
        """
        return osp.join(self.pdfDir, self.badFName(key))

    def getFilePath(self, key, fileType):
        """Obtain the file path for a given file type (arxiv, doi, ...)
        of a given entry.
        It reads the field from the database in order
        to generate the file name.

        Parameters:
            key (string): the bibtex key of the entry
            fileType (string in
                ["arxiv", "inspire", "isbn", "doi", "ads", "scholar"]):
                basically the field in the database
                from which the name must be taken

        Output:
            the (cleaned) absolute path for the PDF file
        """
        if fileType not in ["arxiv", "inspire", "isbn", "doi", "ads", "scholar"]:
            pBLogger.warning(pstr.errorField)
            return ""
        filename = pBDB.bibs.getField(key, fileType)
        if filename is None:
            pBLogger.warning(pstr.errorGetType % (fileType, key))
            return ""
        else:
            filename = self.badFName(filename)
            return osp.join(self.getFileDir(key), filename + ".pdf")

    def createFolder(self, key, noCheck=False):
        """Create the PDF folder for a given entry.

        Parameters:
            key (string): the bibtex key of the entry
            noCheck (bool): True to avoid checking
                if the directory exists. Default False
        """
        directory = self.getFileDir(key)
        if noCheck or not osp.exists(directory):
            os.makedirs(directory)

    def renameFolder(self, oldkey, newkey):
        """Rename the PDF folder for a given entry
        for which the bibtex key has been changed.

        Parameters:
            oldkey (string): the old bibtex key of the entry
            newkey (string): the new bibtex key of the entry
        """
        olddir = self.getFileDir(oldkey)
        if osp.exists(olddir):
            newdir = self.getFileDir(newkey)
            pBLogger.info(pstr.rename % (olddir, newdir))
            if shutil.copytree(olddir, newdir, dirs_exist_ok=True):
                return shutil.rmtree(olddir)
        return False

    def copyNewFile(self, key, origFileName, fileType=None, customName=None):
        """Copy a file in any place of the filesystem
        into the directory corresponding to the given entry

        Parameters:
            key (string): the bibtex key of the entry
            origFileName (string): the name of the file to be copied
            fileType (string in
                ["arxiv", "inspire", "isbn", "doi", "ads", "scholar"]):
                basically the field in the database
                from which the name must be taken.
                `customName` can be given instead.
            customName (string):
                a completely independent name for the file.
                It may be given instead of fileType.
        """
        if not osp.exists(self.getFileDir(key)):
            self.createFolder(key, True)
        if customName is not None:
            newFileName = osp.join(self.getFileDir(key), customName)
        elif fileType is not None:
            newFileName = self.getFilePath(key, fileType)
        else:
            pBLogger.warning(pstr.errorMissingArg)
            return False
        try:
            shutil.copy2(origFileName, newFileName)
            pBLogger.info(pstr.copied % (origFileName, newFileName))
            return True
        except:
            pBLogger.exception(pstr.errorCopy % (origFileName, newFileName))
            return False

    def copyToDir(self, outFolder, key, fileType=None, customName=None):
        """Copy a file from the directory corresponding
        to the given entry to the a directory in the filesystem.

        Parameters:
            outFolder (string): the name of the destination folder
            key (string): the bibtex key of the entry
            fileType (string in
                ["arxiv", "inspire", "isbn", "doi", "ads", "scholar"]):
                basically the field in the database from which
                the name must be taken. customName can be given instead.
            customName (string):
                a completely independent name for the file.
                It may be given instead of fileType.
        """
        if customName is not None:
            origFile = osp.join(self.getFileDir(key), customName)
        elif fileType is not None:
            origFile = self.getFilePath(key, fileType)
        else:
            pBLogger.warning(pstr.errorMissingArg)
            return False
        try:
            shutil.copy2(origFile, outFolder)
            pBLogger.info(pstr.copied % (origFile, outFolder))
            return True
        except:
            pBLogger.exception(pstr.errorCopy % (origFile, outFolder))
            return False

    def downloadArxiv(self, key, force=False):
        """Download the PDF file from arXiv for a given entry
        and save it in the proper folder.

        Parameters:
            key (string): the bibtex key of the entry
            force (boolean, optional, default False):
                force the replacement of the file if it already exists.
                If False and there is a PDF with the same name,
                no action is performed.
        """
        filename = self.getFilePath(key, "arxiv")
        if osp.exists(filename) and not force:
            pBLogger.info(pstr.pdfPresent)
            return True
        self.createFolder(key)
        url = pBDB.bibs.getArxivUrl(key, "pdf")
        if not url:
            pBLogger.warning(pstr.errorArxivUrl % key)
            return False
        pBLogger.info(pstr.downloading % url)
        try:
            response = urlopen(url)
        except (URLError, ConnectionError):
            pBLogger.exception(pstr.pdfNotFound % key + pstr.e404 % url)
            return False
        else:
            try:
                with open(filename, "wb") as newF:
                    newF.write(response.read())
            except OSError:
                pBLogger.exception(pstr.errorSave % filename)
            else:
                pBLogger.info(pstr.saved % filename)
                return os.path.exists(filename)

    def openFile(self, key, arg=None, fileType=None, fileNum=None, fileName=None):
        """Open a PDF file in an external application
        (if defined in the configuration).
        Does nothing if there is self.pdfApp is empty.

        Parameters:
            key (string): the bibtex key of the entry
            at least one of the following (they are considered in this order):
                arg: used to guess the fileType, fileNum or fileName
                fileType (string in
                    ["arxiv", "inspire", "isbn", "doi", "ads", "scholar"]):
                    basically the field in the database
                    from which the name must be taken
                fileNum: the number of the desired PDF
                    in the list of existing PDF files for the considered entry
                filaName: the specific file name
        """
        try:
            if arg == "arxiv" or arg == "doi":
                fileType = arg
            elif float(arg).is_integer():
                fileNum = int(arg)
        except:
            if arg is not None:
                fileName = arg
        try:
            if fileType is not None:
                fName = self.getFilePath(key, fileType)
            elif fileNum is not None:
                fName = self.getExisting(key, True)[fileNum]
            elif fileName is not None:
                fName = osp.join(self.getFileDir(key), fileName)
            else:
                pBLogger.warning(pstr.errorInvalidSel)
                return
            if self.pdfApp != "":
                pBLogger.info(pstr.opening % fName)
                subprocess.Popen(
                    [self.pdfApp, fName],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
        except:
            pBLogger.exception(pstr.openingFailed % ("PDF", key))

    def checkFile(self, key, fileType):
        """Check if a file of a given type (arxiv, doi, ...)
        and a given entry exists.

        Parameters:
            key (string): the bibtex key of the entry
            fileType (string in
                ["arxiv", "inspire", "isbn", "doi", "ads", "scholar"]):
                basically the field in the database
                from which the name must be taken

        Output:
            boolean (if the arguments are valid) or None (if fileType is bad)
        """
        if fileType not in ["arxiv", "inspire", "isbn", "doi", "ads", "scholar"]:
            pBLogger.warning(pstr.invalidCheckFileArg)
            return
        return os.path.isfile(self.getFilePath(key, fileType))

    def removeFile(self, key, fileType, fileName=None):
        """Delete a PDF file.

        Parameters:
            key (string): the bibtex key of the entry
            fileType (any string if fileName is not None or string in
                ["arxiv", "inspire", "isbn", "doi", "ads", "scholar"]):
                basically the field in the database
                from which the name must be taken
            fileName (default None): specify the file name instead
                of computing it from the database information

        Output:
            True if successful, False if exception occurred
        """
        if fileName is None:
            fileName = self.getFilePath(key, fileType)
        try:
            os.remove(fileName)
        except OSError:
            pBLogger.exception(pstr.errorRemove % fileName)
            return False
        pBLogger.info(pstr.removed % fileName)
        return True

    def getExisting(self, key, fullPath=False):
        """Obtain the list of existing files for a given entry.

        Parameters:
            key (string): the bibtex key of the entry
            fullPath (boolean, default False):
                return the list with absolute paths

        Output:
            a list, possibly empty
        """
        fileDir = self.getFileDir(key)
        try:
            dircontent = os.listdir(fileDir)
        except Exception:
            return []
        try:
            files = [e for e in dircontent if osp.isfile(osp.join(fileDir, e))]
        except (FileNotFoundError, IOError):
            pBLogger.exception(pstr.errorList)
            return []
        if fullPath:
            files = [osp.join(fileDir, e) for e in files]
        return files

    def printExisting(self, key, fullPath=False):
        """Print the list of existing files for a given entry,
        using self.getExisting to get it.
        Same parameters as self.getExisting.
        """
        pBLogger.info(pstr.listing % (key, self.getFileDir(key)))
        for i, e in enumerate(self.getExisting(key, fullPath=fullPath)):
            pBLogger.info("%2d: %s" % (i, e))

    def printAllExisting(self, entries=None, fullPath=False):
        """Print the complete list of all the existing PDF files
        in the PDF folder, given all the entries in the database
        or a specific subset

        Parameters:
            entries (list, optional): the list of bibtex keys to consider.
                If None, get all the database content
            fullPath (boolean, default False):
                print the list with absolute paths
        """
        iterator = entries
        if entries is None:
            pBDB.bibs.fetchAll(orderBy="firstdate", saveQuery=False, doFetch=False)
            iterator = pBDB.bibs.fetchCursor()
        for e in iterator:
            exist = self.getExisting(e["bibkey"], fullPath=fullPath)
            if len(exist) > 0:
                pBLogger.info("%30s: [%s]" % (e["bibkey"], "] [".join(exist)))

    def removeSparePDFFolders(self):
        """Scans the PDF folder in order to find single unassociated
        directories (their name is not matched by any database entry).
        The unassociated directories are removed without asking any
        additional confirmation. Be careful!
        """
        pBDB.bibs.fetchAll(doFetch=False)
        folders = os.listdir(self.pdfDir)
        for e in pBDB.bibs.fetchCursor():
            k = e["bibkey"]
            cleaned = self.badFName(k)
            if cleaned in folders:
                del folders[folders.index(cleaned)]
        if len(folders) > 0:
            pBLogger.info(pstr.spareFound % (len(folders), folders))
            for f in folders:
                shutil.rmtree(osp.join(self.pdfDir, f))
            pBLogger.info(pstr.doneE)
        else:
            pBLogger.warning(pstr.nothingFound)

    def mergePDFFolders(self, oldkey, newkey):
        """Copy the PDF files that exist in one folder to a new one

        Parameters:
            oldkey: the old bibtex key
            newkey: the new bibtex key
        """
        oldPDFs = self.getExisting(oldkey, fullPath=True)
        outFolder = self.getFileDir(newkey)
        self.createFolder(newkey)
        for o in oldPDFs:
            try:
                shutil.copy2(o, outFolder)
                pBLogger.info(pstr.copied % (o, outFolder))
            except:
                pBLogger.exception(pstr.errorCopy % (o, outFolder))

    def numberOfFiles(self, folder):
        """Get the total number of files inside the given folder

        Parameters:
            folder: the path of the folder to scan

        Output:
            the number of files
        """
        total_number = 0
        if six.PY2:
            error_class = OSError
        else:
            error_class = FileNotFoundError
        if sys.version_info[0] < 3:
            try:
                dirlist = os.listdir(folder)
            except error_class:
                dirlist = []
            for item in dirlist:
                itempath = os.path.join(folder, item)
                if os.path.isfile(itempath):
                    total_number += 1
                elif os.path.isdir(itempath):
                    total_number += self.numberOfFiles(itempath)
        else:
            for dirpath, dirnames, filenames in os.walk(folder):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.isfile(fp):
                        total_number += 1
        return total_number

    def dirSize(self, folder, dirs=True):
        """Get the size of a single directory and its content

        Parameters:
            folder: the path of the folder to scan
            dirs (default True): if True, include the size of folders

        Output:
            the size in bytes
        """
        if dirs:
            if six.PY2:
                error_class = OSError
            else:
                error_class = FileNotFoundError
            try:
                total_size = os.path.getsize(folder)
            except error_class:
                pBLogger.exception(pstr.folderMissing % folder)
                os.makedirs(folder)
                return os.path.getsize(folder)
        else:
            total_size = 0
        if sys.version_info[0] < 3:
            for item in os.listdir(folder):
                itempath = os.path.join(folder, item)
                if os.path.isfile(itempath):
                    total_size += os.path.getsize(itempath)
                elif os.path.isdir(itempath):
                    total_size += self.dirSize(itempath, dirs=dirs)
        else:
            for dirpath, dirnames, filenames in os.walk(folder):
                if dirs:
                    for d in dirnames:
                        total_size += os.path.getsize(os.path.join(dirpath, d))
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.isfile(fp):
                        total_size += os.path.getsize(fp)
        return total_size

    def getSizeWUnits(self, size, units="MB", fmt="%.2f"):
        """Print a size obtained with `self.dirSize`

        Parameters:
            size:
            units (default "MB"):
            format (default "%.2f"): the format

        Output:
            the string with the size in the appropriate units
        """
        allowedUnits = ["B", "KB", "MB", "GB", "TB", "PB"]
        try:
            exponent = allowedUnits.index(units.upper())
            unitsU = units.upper()
        except ValueError:
            pBLogger.warning(pstr.errorUnits)
            exponent = 2
            unitsU = "MB"
        try:
            sizeWUnits = size / 1024.0 ** (exponent)
        except TypeError:
            pBLogger.warning(pstr.errorSize)
            return "nan"
        try:
            return fmt % sizeWUnits + unitsU
        except (TypeError, ValueError):
            pBLogger.warning(pstr.errorFormat)
            return "%.2f" % sizeWUnits + unitsU


pBPDF = LocalPDF()
