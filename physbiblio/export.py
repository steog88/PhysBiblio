"""Classes and functions that manage the export
of the database entries into .bib files.

This file is part of the physbiblio package.
"""
import codecs
import os
import re
import shutil
import traceback

import bibtexparser
from requests.structures import CaseInsensitiveDict

try:
    from physbiblio.bibtexWriter import pbWriter
    from physbiblio.config import pbConfig
    from physbiblio.database import pBDB
    from physbiblio.errors import pBLogger
    from physbiblio.strings.main import ExportStrings as exstr
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise


class PBExport:
    """Class that contains the export functions and related."""

    exportForTexFlag = True
    backupExtension = ".bck"
    unwantedFields = ["owner", "timestamp", "__markedentry", "abstract"]

    def __init__(self):
        """Initialize the class instance and set some default variables."""
        self.exportForTexFlag = True
        self.existingBibsList = None
        self.allCitations = set([])

    def backupCopy(self, fileName):
        """Creates a backup copy of the given file.

        Parameters:
            fileName: the name of the file to be backed up
        """
        if os.path.isfile(fileName):
            try:
                shutil.copy2(fileName, fileName + self.backupExtension)
            except IOError:
                pBLogger.exception(exstr.cannotWriteBackup)
                return False
            else:
                return True
        return False

    def restoreBackupCopy(self, fileName):
        """Restores the backup copy of the given file, if any.

        Parameters:
            fileName: the name of the file to be restore
        """
        if os.path.isfile(fileName + self.backupExtension):
            try:
                shutil.copy2(fileName + self.backupExtension, fileName)
            except IOError:
                pBLogger.exception(exstr.cannotRestoreBackup)
                return False
            else:
                return True
        return False

    def rmBackupCopy(self, fileName):
        """Deletes the backup copy of the given file, if any.

        Parameters:
            fileName: the name of the file of which
                the backup should be deleted
        """
        if os.path.isfile(fileName + self.backupExtension):
            try:
                os.remove(fileName + self.backupExtension)
            except IOError:
                pBLogger.exception(exstr.cannotRemoveBackup)
                return False
            else:
                return True
        return True

    def exportLast(self, fileName):
        """Export the last queried entries into a .bib file,
        if the list is not empty.

        Parameters:
            fileName: the name of the output bibtex file
        """
        if pBDB.bibs.lastFetched:
            self.exportRows(fileName, pBDB.bibs.lastFetched)
        else:
            pBLogger.info(exstr.noLastSel)

    def exportAll(self, fileName):
        """Export all the entries in the database into a .bib file.

        Parameters:
            fileName: the name of the output bibtex file
        """
        pBDB.bibs.fetchAll(saveQuery=False, doFetch=False)
        self.exportRows(fileName, pBDB.bibs.fetchCursor())

    def exportSelected(self, fileName, rows):
        """An alias for exportRows"""
        self.exportRows(fileName, rows)

    def exportRows(self, fileName, rows):
        """Export the given entries into a .bib file.

        Parameters:
            fileName: the name of the output bibtex file
            rows: the list of entries to be exported
        """
        self.backupCopy(fileName)
        if rows != []:
            try:
                with codecs.open(fileName, "w", "utf-8") as bibfile:
                    for q in rows:
                        bibfile.write(q["bibtex"] + "\n")
            except Exception:
                pBLogger.exception(exstr.errorExport, traceback)
                self.restoreBackupCopy(fileName)
        else:
            pBLogger.info(exstr.noElement)
        self.rmBackupCopy(fileName)

    def exportForTexFile(
        self,
        texFileName,
        outFileName,
        overwrite=False,
        autosave=True,
        updateExisting=False,
        removeUnused=False,
        reorder=False,
        newOperation=True,
    ):
        """Reads a .tex file looking for the \cite{} commands,
        collects the bibtex entries cited in the text and
        stores them in a bibtex file.
        The entries are taken from the database first,
        or from INSPIRE-HEP if possible.
        The downloaded entries are saved in the database.

        Parameters:
            texFileName: the name (or a list of names)
                of the considered .tex file(s)
            outFileName: the name of the output file,
                where the required entries will be added
            overwrite (boolean, default False):
                if True, the previous version of the file is replaced
                and no backup copy is created
            autosave (boolean, default True):
                if True, the changes to the database are automatically saved.
            updateExisting (boolean, default False):
                if True, remove duplicates and update entries
                that have been chenged in the DB
            removeUnused (boolean, default False):
                if True, remove bibtex entries that are no more cited
                in the tex files
            reorder (boolean, default False):
                if True, reorder (not update!) the bibtex entries
                in the bib files before adding the new ones
            newOperation (boolean, default True):
                reset the self.existingBibsList and read file .bib content.
                Time consuming! better to just keep it updated
                when using multiple texs...

        Output:
            True if successful, False if errors occurred
        """
        db = bibtexparser.bibdatabase.BibDatabase()

        def printOutput(
            reqBibkeys, miss, retr, nFound, unexp, nKeys, warn, totalCites, full=False
        ):
            """Print information on the process"""
            pBLogger.info(exstr.resume)
            if totalCites is not None:
                pBLogger.info(exstr.keysFound % totalCites)
            pBLogger.info(exstr.newKeysFound % len(reqBibkeys))
            j = ", "
            if full:
                pBLogger.info(j.join(reqBibkeys))
            if len(miss) > 0:
                pBLogger.info(exstr.missingEntries % len(miss))
                if full:
                    pBLogger.info(j.join(miss))
            if len(retr) > 0:
                pBLogger.info(exstr.retrievedEntries % len(retr))
                pBLogger.info(j.join(retr))
            if len(nFound) > 0:
                pBLogger.info(exstr.entriesNotFound % len(nFound))
                pBLogger.info(j.join(nFound))
            if len(unexp) > 0:
                pBLogger.info(exstr.unexpectedForEntries % len(unexp))
                pBLogger.info(j.join(unexp))
            if len(nKeys.keys()) > 0:
                pBLogger.info(
                    exstr.nonMatchingEntries % len(nKeys.keys())
                    + "\n".join(["'%s' => '%s'" % (k, n) for k, n in nKeys.items()])
                )
            pBLogger.info(exstr.totalWarnings % warn)

        def saveEntryOutBib(a, m=None):
            """Remove unwanted fields and add the bibtex entry
            to the output file

            Parameters:
                a: the bibtex entry
                m: the ID (bibtex key) of the entry,
                    if it is not the default one
            """
            entry = pBDB.bibs.readEntry(a)
            for u in self.unwantedFields:
                try:
                    del entry[u]
                except KeyError:
                    pass
            if m is not None:
                m = m.strip()
                if m != entry["ID"].strip():
                    entry["ID"] = m
            db.entries = [entry]
            bibf = pbWriter.write(db)
            try:
                with open(outFileName, "a") as o:
                    o.write(bibf)
                    pBLogger.info(exstr.entryInserted % m)
            except IOError:
                pBLogger.exception(exstr.errorWrite % outFileName)
                return False

        def removeUnusedBibtexs(existingBibsDict):
            """Functions that reads the list of bibtex entries
            in the existing .bib file and removes
            the ones that are not inside \cite commands
            """
            newDict = {}
            notFound = []
            for k, v in existingBibsDict.items():
                if k in self.allCitations:
                    newDict[k] = existingBibsDict[k]
                else:
                    notFound.append(k)
            db.entries = [
                newDict[k]
                for k in sorted(
                    [e["ID"] for e in newDict.values()], key=lambda s: s.lower()
                )
            ]
            bibf = pbWriter.write(db)
            try:
                with open(outFileName, "w") as o:
                    o.write(exstr.byPhysbiblio + bibf)
                    pBLogger.info(exstr.entriesRemoved % notFound)
            except IOError:
                pBLogger.exception(exstr.errorWrite % outFileName)

        self.exportForTexFlag = True
        pBLogger.info(exstr.startEFTF)
        pBLogger.info(exstr.readFrom % texFileName)
        pBLogger.info(exstr.saveTo % outFileName)
        if autosave:
            pBLogger.info(exstr.autoSave)

        missing = []
        newKeys = {}
        notFound = []
        requiredBibkeys = []
        retrieved = []
        unexpected = []
        warnings = 0
        totalCites = 0

        # if overwrite, reset the output file
        if overwrite:
            updateExisting = False
            removeUnused = False
            reorder = False
            try:
                with open(outFileName, "w") as o:
                    o.write(exstr.byPhysbiblio)
            except IOError:
                pBLogger.exception(exstr.cannotWrite)
                return False

        # read previous content of output file, if any
        try:
            with open(outFileName, "r") as f:
                existingBibText = f.readlines()
        except IOError:
            pBLogger.exception(exstr.cannotRead % outFileName)
            try:
                open(outFileName, "w").close()
            except IOError:
                pBLogger.exception(exstr.cannotCreate % outFileName)
                return False
            existingBibText = ""

        # this is time consuming if there are many entries.
        # Do not load it every time for multiple texs!
        if newOperation:
            self.allCitations = set([])
            if existingBibText != "":
                self.existingBibsList = pBDB.bibs.parseAllBibtexs(
                    existingBibText, verbose=False
                )
            else:
                self.existingBibsList = []
        # work with dictionary, so that if there are repeated entries
        # (entries with same ID) they are automatically discarded
        existingBibsDict = CaseInsensitiveDict()
        for e in self.existingBibsList:
            existingBibsDict[e["ID"]] = e

        # if requested, do some cleaning
        if updateExisting or reorder:
            # update entry from DB if existing
            if updateExisting:
                for k, v in existingBibsDict.items():
                    e = pBDB.bibs.getByBibtex(k, saveQuery=False)
                    if len(e) > 0 and e[0]["bibtexDict"] != v:
                        existingBibsDict[k] = e[0]["bibtexDict"]
                        if existingBibsDict[k]["ID"].lower() != k.lower():
                            existingBibsDict[k]["ID"] = k

            # write new (updated) bib content
            # (so also repeated entries are removed)
            db.entries = [
                existingBibsDict[k]
                for k in sorted(
                    [e["ID"] for e in existingBibsDict.values()],
                    key=lambda s: s.lower(),
                )
            ]
            bibf = pbWriter.write(db)
            try:
                with open(outFileName, "w") as o:
                    o.write(exstr.byPhysbiblio + bibf)
                    pBLogger.info(exstr.outputUpdated)
            except IOError:
                pBLogger.exception(exstr.errorWrite % outFileName)

        # if there is a list of tex files, run this function
        # for each of them...no updateExisting and removeUnused!
        if isinstance(texFileName, list):
            if len(texFileName) == 0:
                return False
            elif len(texFileName) == 1:
                texFileName = texFileName[0]
            else:
                for t in texFileName:
                    req, m, ret, nF, un, nK, w, cits = self.exportForTexFile(
                        t,
                        outFileName,
                        overwrite=False,
                        autosave=autosave,
                        updateExisting=False,
                        removeUnused=False,
                        reorder=False,
                        newOperation=False,
                    )
                    requiredBibkeys += req
                    missing += m
                    retrieved += ret
                    notFound += nF
                    unexpected += un
                    for k, v in nK.items():
                        newKeys[k] = v
                    warnings += w
                pBLogger.info(exstr.doneAllTexs)
                if removeUnused:
                    removeUnusedBibtexs(existingBibsDict)
                printOutput(
                    requiredBibkeys,
                    missing,
                    retrieved,
                    notFound,
                    unexpected,
                    newKeys,
                    warnings,
                    len(self.allCitations),
                    full=True,
                )
                return (
                    requiredBibkeys,
                    missing,
                    retrieved,
                    notFound,
                    unexpected,
                    newKeys,
                    warnings,
                    len(self.allCitations),
                )

        # read the texFile
        keyscont = ""
        try:
            with open(texFileName) as r:
                keyscont += r.read()
        except IOError:
            pBLogger.exception(exstr.errorNoFile % texFileName)
            return False

        # extract \cite* commands
        matchKeys = "([0-9A-Za-z_\-':\+\.\&]+)"
        cite = re.compile(
            "\\\\(cite|citep|citet)\{([\n ]*" + matchKeys + "[,]?[\n ]*)*\}",
            re.MULTILINE,
        )  # find \cite{...}
        citeKeys = re.compile(
            matchKeys, re.MULTILINE
        )  # find the keys inside \cite{...}
        citaz = [m for m in cite.finditer(keyscont) if m != ""]
        pBLogger.info(exstr.citeFound % len(citaz))

        # extract required keys from \cite* commands
        for c in citaz:
            try:
                for e in [l.group(1) for l in citeKeys.finditer(c.group())]:
                    e = e.strip()
                    if e == "" or e in ["cite", "citep", "citet"]:
                        continue
                    self.allCitations.add(e)
                    if e not in requiredBibkeys:
                        try:
                            # this it's just to check if already present
                            tmp = existingBibsDict[e]
                        except KeyError:
                            requiredBibkeys.append(e)
            except (IndexError, AttributeError, TypeError):
                pBLogger.warning(exstr.errorCitation % c.group())
                a = []
        pBLogger.info(
            exstr.newKeysTotal % (len(requiredBibkeys), len(self.allCitations))
        )

        # if True, remove unused bibtex entries
        if removeUnused:
            removeUnusedBibtexs(existingBibsDict)

        # check what is missing in the database and insert/import
        # what is needed:
        for m in requiredBibkeys:
            if m.strip() == "":
                continue
            entry = pBDB.bibs.getByBibtex(m)
            entryMissing = len(entry) == 0
            if not self.exportForTexFlag:
                # if flag set, stop execution and
                # go to the end skipping everything
                continue
            elif not entryMissing:
                # if already in the database, just insert it as it is
                bibtex = entry[0]["bibtex"]
                bibtexDict = entry[0]["bibtexDict"]
            else:
                # if no entry is found, mark it as missing
                missing.append(m)
                # if not present, try INSPIRE import
                pBLogger.info(exstr.keyMissing % m)
                newWeb = pBDB.bibs.loadAndInsert(m, returnBibtex=True)
                newCheck = pBDB.bibs.getByBibtex(m, saveQuery=False)

                # if the import worked, insert the entry
                if len(newCheck) > 0:
                    # if key is not matching,
                    # just replace it in the exported bib and print a message
                    if m.strip().lower() != newCheck[0]["bibkey"].lower():
                        warnings += 1
                        newKeys[m] = newCheck[0]["bibkey"]
                    if newCheck[0]["bibkey"] not in retrieved:
                        retrieved.append(newCheck[0]["bibkey"])
                    pBDB.catBib.insert(
                        pbConfig.params["defaultCategories"], newCheck[0]["bibkey"]
                    )
                    bibtex = newCheck[0]["bibtex"]
                    bibtexDict = newCheck[0]["bibtexDict"]
                else:
                    # if nothing found, add a warning for the end
                    warnings += 1
                    notFound.append(m)
                    continue
                pBLogger.info("\n")
            # save in output file
            try:
                bibtexDict["ID"] = m
                self.existingBibsList.append(bibtexDict)
                saveEntryOutBib(bibtex, m)
            except:
                unexpected.append(m)
                pBLogger.exception(exstr.unexpectedEntry % m)

        if autosave:
            pBDB.commit()
        printOutput(
            requiredBibkeys,
            missing,
            retrieved,
            notFound,
            unexpected,
            newKeys,
            warnings,
            len(self.allCitations),
        )
        return (
            requiredBibkeys,
            missing,
            retrieved,
            notFound,
            unexpected,
            newKeys,
            warnings,
            len(self.allCitations),
        )

    def updateExportedBib(self, fileName, overwrite=False):
        """Reads a bibtex file and updates the entries that it contains,
        for example if the entry has been published.

        Parameters:
            fileName: the name of the considered bibtex file
            overwrite (boolean, default False): if True,
                the previous version of the file is replaced
                and no backup copy is created

        Output:
            True if successful, False if errors occurred
        """
        self.backupCopy(fileName)
        bibfile = ""
        try:
            with open(fileName) as r:
                bibfile += r.read()
        except IOError:
            pBLogger.exception(exstr.cannotWrite)
            return False
        try:
            entries = pBDB.bibs.readEntries(bibfile)
        except IndexError:
            pBLogger.exception(exstr.errorLoading)
            return False
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = []
        for b in entries:
            key = b["ID"]
            element = pBDB.bibs.getByBibkey(key, saveQuery=False)
            if len(element) > 0:
                db.entries.append(element[0]["bibtexDict"])
            else:
                db.entries.append(b)
        txt = pbWriter.write(db).strip()
        try:
            with codecs.open(fileName, "w", "utf-8") as outfile:
                outfile.write(txt)
        except Exception:
            pBLogger.exception(exstr.errorExport)
            self.restoreBackupCopy(fileName)
            return False
        if overwrite:
            self.rmBackupCopy(fileName)
        return True


pBExport = PBExport()
