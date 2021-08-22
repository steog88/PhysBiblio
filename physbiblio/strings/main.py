from .common import CommonStrings


class ArgParserStrings:
    """Strings for the physbiblio.argParser module"""

    citHelp = (
        "update citation counts for all entries using info from the INSPIRE database"
    )
    cleanHelp = "clean the entries in the database"
    cleanStartHelp = "the index from which the cleaning should start"
    cliHelp = "open the internal command line interface"
    closeMainW = "Closing main window..."
    dailyHelp = "fetch the daily updates from INSPIRE-HEP OAI"
    datesEndHelp = "the ending date (format as yyyy-mm-dd)"
    datesHelp = "fetch the updates from INSPIRE-HEP OAI between the given dates"
    datesStartHelp = "the starting date (format as yyyy-mm-dd)"
    exportFilenameHelp = "the filename where to save the entries"
    exportHelp = "export all the entries in the database in a file"
    guiHelp = "open the gui"
    profileHelp = "define the profile that must be used"
    subHelp = "sub-command help"
    testFailed = "Some error occurred during tests"
    testHelp = "run the test suite"
    testDbHelp = "do not perform database tests"
    testGuiHelp = "do not perform gui tests"
    testLongHelp = "do not perform long tests"
    testOAIHelp = "do not perform online tests with INSPIRE OAI"
    testOnlineHelp = "do not perform online tests"
    texHelp = "read .tex file(s) and create a *.bib file with the cited bibtexs"
    texBibHelp = "the filename of the bib file where to write"
    texOverwriteHelp = "overwrite the bib file, if existing"
    texRemoveHelp = (
        "remove from the .bib file those elements "
        + "that are not more used in the tex"
    )
    texReorderHelp = "reorder the elements in the .bib file and add new ones"
    texSaveHelp = "save the changes in the database"
    texTexsHelp = (
        "the filename of the tex file to read. A folder or wildcards are admitted"
    )
    texUpdateHelp = (
        "update the elements in the .bib file if they changed "
        + "in the database and remove duplicated entries"
    )
    updateHelp = "use INSPIRE to update the information in the database"
    updateForceHelp = "force the update"
    updateStartHelp = "the index from which the updating should start"
    weeklyHelp = "fetch the weekly updates from INSPIRE-HEP OAI"


class BibtexWriterStrings:
    """Strings for the physbiblio.bibtexWriter module"""

    errorNotString = u"The field %s in entry %s must be a string"


class CLIStrings:
    """Strings for the physbiblio.cli module"""

    activate = (
        "[CLI] Activating CommandLineInterface\n"
        + "Write a command and press Enter ('Ctrl+D' or 'exit()' to exit)."
    )
    close = "CommandLineInterface closed."


class ConfigStrings:
    """Strings for the physbiblio.config module"""

    class Desc:
        """Description of some parameters"""

        ADSToken = "Token for connecting to the ADS service by NASA"
        autoResize = "Automatically resize columns and rows in the main bibtex table"
        batchSizeInspire = (
            "Batch size for cumulative searches through the INSPIRE API "
            + "(it must be <= 1000)"
        )
        bibListCols = "The columns to be shown in the entries list"
        confirmExit = "Confirm before exiting"
        defaultCat = "Default categories for imported bibtexs"
        fetchAbstract = (
            "Automatically fetch the abstract from arXiv if an arxiv number is present"
        )
        fontSize = "Font size in the list of bibtex entries and companion boxes"
        limitBibtexs = "Number of bibtex entries in the initial view of the main table"
        logFName = "Name of the log file"
        logLevel = (
            "How many messages to save in the log file "
            + "(will have effects only after closing the application)"
        )
        mainDBName = "Name of the database file"
        maxAPIRes = "Max number of entries per page when reading external API results"
        maxAuthorsD = "Max number of authors to be displayed in the main list"
        maxAuthorsS = "Max number of authors to be saved when adding info from arXiv"
        maxSavedSearches = "Max number of automatically saved search/replace arguments"
        notifyUpdate = (
            "If configured to False, do not show the existence"
            + " of updates when opening the app"
        )
        PDFApp = "Application for opening PDF files (used only via command line)"
        PDFFolder = "Folder where to save the PDF files"
        sinceLastUpdate = (
            "Parameter that saves the number of the last used version"
            + " for showing the list of changes when a new one is opened"
        )
        timeout = "Timeout for the web queries"
        updateFrom = (
            "Index of bibtex entries (firstdate ASC) "
            + 'from which I should start when using "Update bibtexs"'
        )
        webApp = "Web browser (used only via command line)"

    confEntryInsert = "No settings found with this name (%s). Inserting it."
    confEntryUpdate = "An entry with the same name is already present. Updating it"
    confLoaded = "Configuration loaded.\n"
    defaultCfgPath = "Default configuration path: %s"
    defaultDataPath = "Default data path: %s"
    defaultProfileChanged = "Default profile changed to %s"

    errorDeleteProfile = "Cannot delete profile"
    errorInsertProfile = "Cannot insert profile"
    errorInvalidFieldI = "Invalid field or identifierField: %s, %s"
    errorListProfilesMatch = "List of profile names does not match existing profiles!"
    errorName = "No name given!"
    errorNameFilenameOne = (
        "You should specify the name or the filename associated with the profile"
    )
    errorNameFilenameOnly = (
        "You should specify only the name "
        + "or only the filename associated with the profile"
    )
    errorNoProfileUseDef = (
        "The profile '%s' does not exist! Back to the default one ('%s')"
    )
    errorNoProfilesName = "No profiles with the given name!"
    errorOrder = "No order given!"
    errorProfileDefault = (
        "Something went wrong when setting new default profile. Undoing..."
    )
    errorProfileName = "You must provide the profile name!"
    errorProfileNotFound = "Profile not found!"
    errorProfileOrdering = (
        "Something went wrong when setting new profile order. Undoing..."
    )
    errorReadConf = "ERROR: reading config from '%s' failed."
    errorReadParam = "Failed in reading parameter '%s'."
    errorSearchField = (
        "Empty value or field not in the following list: "
        + "[searchDict, replaceFields, name, limitNum, offsetNum].\n"
        + "Field: %s, value: %s"
    )
    errorUpdateProfile = "Cannot update profile"
    invalidType = "Invalid parameter type: %s"
    noAttribute = "Attribute does not exist for current ConfigParameter: %s"
    readConf = "Reading configuration.\n"
    restartWProfile = "Restarting with profile '%s', database: %s"
    startWProfile = "Starting with profile '%s', database: %s"


class DatabaseCoreStrings:
    """Strings for the physbiblio.databaseCore module"""

    closeDb = "Closing database..."
    errorAlterEntries = "Cannot alter table 'entries'!"
    errorCannotCommit = "Impossible to commit!"
    errorCannotRollback = "Impossible to rollback!"
    errorConnection = "Connection error: %s\nquery: %s"
    errorCreateTable = "Create table %s failed"
    errorCursor = 'Cursor error: %s\nThe query was: "%s"\nand the parameters: %s'
    errorInsMainCats = "Insert main categories failed"
    errorInsUpd = "Cannot insert/update: ID exists!\n%s\nquery: %s"
    errorLiteralEval = "Error in literal_eval with string '%s'"
    invalidIsLocked = "Invalid `self.onIsLocked`!"
    newColEntries = "New column in table 'entries': '%s' (%s)."
    noDatabaseCreate = "-------New database or missing tables.\nCreating them!\n\n"
    openDb = "Opening database: %s"
    opErDbOpen = (
        "OperationalError: the database is already open "
        + "in another instance of the application\n"
        + "query failed: %s"
    )
    rollbackDb = "Rolled back to last commit."
    savedDb = "Database saved."


class DatabaseStrings(CommonStrings, DatabaseCoreStrings):
    """Strings for the physbiblio.database module"""

    catNotInDb = "Category '%s' not in database"
    cleaning = "Cleaning (%s, %s)"
    errorReadInput = "Something failed in reading your input '%s'"
    errorRename = "Cannot rename folder"
    newDbCreate = "-------New database. Creating tables!\n\n"
    noElsFound = "No elements found?"

    class Bibs:
        """Strings for the physbiblio.database. class"""

        alreadyExisting = "Already existing: %s\n"
        apiChanged = "%d changed entries:\n%s"
        apiDone = "Inspire OAI harvesting done!"
        apiInfoS = "-- %s, '%s' -> '%s'"
        apiInfoL = "-- %s"
        apiInfoP = "Processing: %s"
        apiNew = "new:\n%s"
        apiOld = "old:\n%s"
        book = "Book"
        callOAIDates = "Calling INSPIRE-HEP OAI harvester between dates %s and %s"
        cannotParse = "Cannot parse properly:\n%s"
        cbError = "Error while cleaning entry '%s'"
        cbInvalidStart = "Invalid startFrom in cleanBibtexs"
        cbProcessProgr = "%5d / %d (%5.2f%%) - cleaning: '%s'\n"
        cbProcessTot = "CleanBibtexs will process %d total entries"
        cbResChan = "%d bibtex entries changed"
        cbResEntr = "%d entries processed"
        cbResErr = "%d errors occurred"
        ccCannotReadId = (
            "Cannot read the INSPIRE ID from the recently retrieved record %s"
        )
        ccCannotUpdateFields = (
            "Cannot update citation fields for entry %s from record %s"
        )
        ccNoCorrespondence = "No correspondence in database for INSPIRE ID %s"
        ccProcessTot = "CitationCount will process %d total entries"
        ccProcessProgr = "%5d / %d (%5.2f%%) - citation count: '%s'"
        delete = "Delete entry, using key = '%s'"
        elementChanged = "-- element changed!"
        elementsFound = "%d elements found"
        emptyBibtex = "Empty bibtex?\n%s\n%s"
        errorField = "Non-existing field or unappropriated value: (%s, %s, %s)"
        errorGFNoElement = "Error in getField('%s', '%s'): no element found?"
        errorGFNoField = "Error in getField('%s', '%s'): the field is missing?"
        errorOAIEntryDet = "something wrong with entry %s\n%s"
        errorOAIEntryMisKey = "Key %s missing for entry:\n%s"
        errorOAIEntryG = "Something went wrong with this entry..."
        errorParseBibtex = "Problem in parsing the following bibtex code:\n%s"
        errorParseBib = "Impossible to parse bibtex!"
        errorReadBibdict = "Cannot read bibdict:\n'%s'"
        errorQueryFailed = "Query failed: %s\nvalues: %s"
        errorUIIDArxiv = "Something went wrong in updateInspireID with arxiv search"
        errorUIIDDOI = "Something went wrong in updateInspireID with doi search"
        errorUIIDGeneric = "Something went wrong in updateInspireID"
        errorUpdateBib = "Impossible to update bibkey"
        experimental = "Experimental paper"
        fcbBadEntries = "%d bad entries found:\n %s"
        fcbInvalidStart = "Invalid startFrom in findCorruptedBibtexs"
        fcbNotReadable = "%s is NOT readable!\n"
        fcbProcessProgr = "%5d / %d (%5.2f%%) - processing: '%s'"
        fcbProcessTot = "findCorruptedBibtexs will process %d total entries"
        fcbReadable = "%s is readable.\n"
        gffaDone = "\n\ngetFieldsFromArxiv has finished!"
        gffaFailed = "Cannot get and save info from arXiv!\n"
        gffaProcessProgr = "%5d / %d (%5.2f%%) - processing: arxiv:%s\n"
        gffaProcessTot = "getFieldsFromArxiv will process %d entries."
        gffaSummary = "%d entries processed, of which these %d generated errors:\n%s"
        ifbCompleteSummary = (
            "Import completed.\n"
            + "%d entries processed, of which %d existing, "
            + "%d successfully inserted and %d errors."
        )
        ifbEmptyKey = "Impossible to insert an entry with empty bibkey!\n"
        ifbExist = "Already existing: %s\n"
        ifbFailed = "Failed in inserting entry %s\n"
        ifbFromFile = "Importing from file bib: %s"
        ifbInserted = "Element successfully inserted.\n"
        ifbNewKey = "Entry will have key: '%s'"
        ifbProcessProgr = "%5d / %d (%5.2f%%), processing entry %s"
        ifbProcessTot = "Entries to be processed: %d"
        iidEmptyID = "InspireID is empty, cannot proceed."
        iidEmptyRecord = "Empty record looking for recid:%s!"
        iidKeyError = "Key error: (%s, %s)"
        iidSaved = "Inspire OAI info for %s saved."
        iidStMissing = "Something missing in entry %s"
        iidWrongType = "Wrong type in inspireID: %s"
        iidWrongVal = "Wrong value/format in inspireID: %s"
        invalidComparisonOp = (
            "Invalid comparison operator "
            + "('%s') in database operations!\n"
            + "Reverting to default '='."
        )
        invalidLogicalOp = (
            "Invalid logical connection operator "
            + "('%s') in database operations!\n"
            + "Reverting to default 'and'."
        )
        invalidOrdering = (
            "Invalid ordering "
            + "('%s') in database operations!\n"
            + "Reverting to default 'ASC'."
        )
        laiEmptyKey = "Impossible to insert an entry with empty bibkey!\n%s\n"
        laiErrors = "ERRORS!\nFailed to load and import entries:\n%s"
        laiFailed = "Failed in inserting entry %s\n"
        laiImported = "Imported entries:\n%s"
        laiInserted = "Element successfully inserted.\n"
        laiInvalidArgs = "Invalid arguments!"
        laiInvalidMethod = "Method not valid: %s"
        laiMismatch = (
            "Possible mismatch. Specify the number of element "
            + "to select with 'number'\n%s"
        )
        laiNewKey = "Entry will have key: '%s'"
        laiProcessProgr = "%5d / %d (%5.2f%%) - looking for string: '%s'\n"
        laiProcessTot = "LoadAndInsert will process %d total entries"
        laiReadError = "Error while reading the bibtex '%s'"
        lecture = "Lecture"
        noneType = "No type"
        pabFound = "%d bibtex entries found."
        pabProgr = "%4d - %s\n"
        pabRead = "Reading bibtex entry #%d"
        pabStart = "Start reading file content"
        parsingExcPU = "Parsing exception in prepareUpdate:\n%s\n%s"
        phdth = "PhD thesis"
        proceeding = "Proceeding"
        psbEmpty = "Impossible to parse empty text!"
        psbError = "Impossible to parse text:\n%s"
        psbProcess = "Processing:\n%s"
        replaceInvalidNew = "Invalid 'fiNews' or 'news' (they must be lists)"
        replaceMissingField = "Field %s not found in entry %s"
        replaceProcessProgr = "processing %5d / %d (%5.2f%%): entry %s"
        replaceProcessTot = "Replace will process %d entries"
        replaceText = "Replacing text in entries: "
        replaceError = "Something wrong in replace"
        review = "Review"
        souError = (
            "Something wrong here. "
            + "Possibly the bibtex key has been changed "
            + "while processing entry '%s'?"
        )
        souFirst = "Starting preliminary loop"
        souInvalidStart = "Invalid startFrom in searchOAIUpdates"
        souResChan = "%d entries changed"
        souResErr = "%d errors occurred"
        souResProc = "%d entries processed"
        souProcessProgr = "%5d / %d (%5.2f%%) - looking for update: '%s'"
        souProcessTot = "SearchOAIUpdates will process %d total entries"
        souSecond = "Starting main loop"
        updateBibkey = "Updating bibkey for entry '%s' into '%s'"
        updateField = "Updating '%s' for entry '%s'"
        useQueryVals = "Using query:\n%s\nvalues: %s"
        wrongTypeField = "Wrong type or value for field %s (%s)?"

        class Search:
            """Stuff used in searches"""

            invalidContent = "Invalid 'content' in search: '%s' (%s)"
            invalidField = "Invalid field: '%s'"
            invalidIds = "Invalid list of ids: '%s'"
            invalidOperator = "Invalid operator: '%s'"
            opCEAll = "all the following"
            opCENone = "none of the following"
            opCEOne = "at least one among"
            opCSub = "this or subcategories"
            opTContains = "contains"
            opTDifferent = "different from"
            opTExact = "exact match"
            opTNotCont = "does not contain"

    class BibsCats:
        """Strings for the physbiblio.database.CatsEntries class"""

        askInputBib = "entries for '%d': "
        askInputCat = "categories for '%s': "
        alreadyPresent = "EntryCat already present: (%d, %s)"
        insert = "inserting (idCat=%s and key=%s)"
        updateKey = "Updating entryCats for bibkey change, from '%s' to '%s'"

    class BibsExps:
        """Strings for the physbiblio.database.EntryExps class"""

        askInputBib = "entries for '%d': "
        askInputExp = "experiments for '%s': "
        alreadyPresent = "EntryExp already present: (%s, %d)"
        insert = "inserting (key=%s and idExp=%s)"
        updateKey = "Updating entryExps for bibkey change, from '%s' to '%s'"

    class Cats:
        """Strings for the physbiblio.database.Categories class"""

        alreadyPresent = (
            "An entry with the same name is already present in the same category!"
        )
        cannotDelete = "You should not delete the category with id: %d%s."
        errorExtract = "Error in extracting category by idCat"
        invalidDepth = "Invalid depth in printCatHier (must be greater than 2)"
        lookChild = "Looking for child categories"
        missingField = "Missing field when inserting category"
        updateField = "Updating '%s' for category '%s'"
        useCat = "Using idCat=%d"

    class CatsExps:
        """Strings for the physbiblio.database.CatsExps class"""

        askInputCat = "categories for '%s': "
        askInputExp = "experiments for '%d': "
        alreadyPresent = "ExpCat already present: (%d, %d)"
        insert = "inserting (idCat=%s and idExp=%s)"

    class Exps:
        """Strings for the physbiblio.database.Experiments class"""

        errorExtract = "Error in extracting experiment by idExp"
        errorPrint = "Error printing experiments!"
        updateField = "Updating '%s' for experiment '%s'"
        useExp = "Using idExp=%d"


class ErrorsStrings:
    """Strings for the physbiblio.errors module"""

    errorAddHandler = "Failed while trying to add a new handler"
    unhandled = "Unhandled exception"


class ExportStrings:
    """Strings for the physbiblio.export module"""

    autoSave = "Changes will be automatically saved at the end!"
    byPhysbiblio = "%file written by PhysBiblio\n"
    cannotCreate = "Cannot create file %s!"
    cannotRead = "Cannot read file %s.\nCreating one."
    cannotRemoveBackup = "Cannot remove backup file.\nCheck the file permissions."
    cannotRestoreBackup = "Cannot restore backup file.\nCheck the file permissions."
    cannotWriteBackup = "Cannot write backup file.\nCheck the folder permissions."
    cannotWrite = "Cannot write on file.\nCheck the file permissions."
    citeFound = r"%d \cite commands found in .tex file"
    doneAllTexs = "Done for all the texFiles.\n\n"
    errorCitation = "Cannot recognize citation list in '%s'!"
    errorExport = "Problems in exporting .bib file!"
    errorLoading = "Problems in loading the .bib file!"
    errorNoFile = "The file %s does not exist."
    errorWrite = "Impossible to write file '%s'"
    entriesNotFound = "Impossible to find %d entries:"
    entriesRemoved = "Output file updated. Removed entries:\n%s"
    entryInserted = "%s inserted in output file"
    keyMissing = "Key '%s' missing, trying to import it from Web"
    keysFound = "%d keys found in .tex file"
    missingEntries = "%d required entries were missing in database"
    newKeysFound = "%d new keys found in .tex file"
    newKeysTotal = "%d new keys found, %d in total."
    noElement = "No elements to export!"
    noLastSel = "No last selection to export!"
    nonMatchingEntries = "Possible non-matching keys in %d entries:\n"
    outputUpdated = "Output file updated"
    readFrom = "Reading keys from '%s'"
    resume = "\n\nRESUME"
    retrievedEntries = "%d new entries retrieved:"
    saveTo = "Saving in '%s'"
    startEFTF = "Starting exportForTexFile...\n\n"
    unexpectedEntry = "Unexpected error in extracting entry '%s' to the output file"
    unexpectedForEntries = "Unexpected errors for %d entries:"
    totalWarnings = "     %s warning(s) occurred!"


class InspireStatsStrings(CommonStrings):
    """Strings for the physbiblio.inspireStats module"""

    authorStats = "Stats for author '%s'"
    authorStatsCompleted = "Stats for author '%s' completed!"
    authorStatsLooking = "%5d / %d (%5.2f%%) - looking for paper: '%s'"
    authorStatsProcess = (
        "AuthorStats will process %d total papers to retrieve citations"
    )
    changeBackend = "Changed backend to %s"
    citationsPaper = "Citations for each paper"
    citationsYear = "Citations per year"
    emptyResponse = "Empty response!"
    errorPlotting = "Something went wrong while plotting..."
    errorReadPage = "Cannot read the page content!"
    meanCitations = "Mean citations"
    noPlot = "Nothing to plot..."
    noPublications = "No publications for this author?"
    paperNumber = "Paper number"
    paperStats = "Stats for paper '%s'"
    paperYear = "Papers per year"
    plotAuthor = "Plotting for author '%s'..."
    plotPaper = "Plotting for paper '%s'..."
    savingCitations = "Saving citation counts..."
    stopReceived = (
        "Received 'stop' signal. "
        + "Interrupting download of information. "
        + "Processing and exiting..."
    )
    totalCitations = "Total citations"


class ParseAccentsStrings:
    """Strings for the physbiblio.parseAccents module"""

    converting = "    -> Converting bad characters in entry %s: "
    infodashes = "         -- "


class PDFStrings(CommonStrings):
    """Strings for the physbiblio.pdf module"""

    copied = "%s copied to %s"
    downloading = "Downloading arXiv PDF from %s"
    e404 = "(404 error on url: %s)"
    errorArxivUrl = "Invalid arXiv PDF url for '%s', probably the field is empty."
    errorCopy = "Impossible to copy %s to %s"
    errorField = "Required field does not exist or is not valid"
    errorFormat = "Invalid format. Using '%.2f'"
    errorGetType = "Impossible to get the type '%s' filename for entry %s"
    errorInvalidSel = (
        "Invalid selection. One among fileType, fileNum or fileName must be given!"
    )
    errorList = "Error in listing the files"
    errorMissingArg = "You should supply a fileType ('doi' or 'arxiv') or a customName!"
    errorRemove = "Impossible to remove file: %s"
    errorSave = "Impossible to save to '%s'"
    errorSize = "Invalid size. It must be a number!"
    errorUnits = "Invalid units. Changing to 'MB'."
    folderMissing = "PDF folder is missing: %s. Creating it."
    invalidCheckFileArg = "Invalid argument to checkFile!"
    listing = "Listing file for entry '%s', located in %s:"
    pdfNotFound = "ArXiv PDF for '%s' not found "
    pdfPresent = "There is already a pdf and overwrite not requested."
    rename = "Renaming %s to %s"
    removed = "File %s removed"
    saved = "File saved to %s"
    spareFound = "Spare PDF folders found: %d\n%s\nThey will be removed now."
    wrongType = "Wrong filename type! %s"


class TablesDefStrings:
    """Strings for the physbiblio.tablesDef module"""

    catsDescs = {
        "idCat": "Unique ID that identifies the category",
        "name": "Name of the category",
        "description": "Description of the category",
        "parentCat": "Parent category",
        "comments": "Comments",
        "ord": "Ordering when plotting (not yet implemented)",
    }
    entriesCatsDescs = {
        "idEnC": "Unique identifier",
        "bibkey": "Corresponding bibtex key",
        "idCat": "Corresponding category ID",
    }
    entriesDescs = {
        "bibkey": "Unique bibtex key that identifies the bibliographic element",
        "inspire": "INSPIRE-HEP ID of the record",
        "arxiv": "arXiv ID of the record",
        "ads": "NASA ADS ID of the record",
        "scholar": "Google Scholar ID of the record",
        "doi": "DOI of the record",
        "isbn": "ISBN code of the record",
        "year": "Year of publication",
        "link": "Web link to article or additional material",
        "comments": "Comments",
        "old_keys": "Previous bibtex keys of the record",
        "crossref": "Bibtex crossref reference",
        "bibtex": "Bibtex entry",
        "firstdate": "Date of first appearance",
        "pubdate": "Date of publication",
        "exp_paper": "(T/F) The entry is a collaboration paper of some experiment",
        "lecture": "(T/F) The entry is a lecture",
        "phd_thesis": "(T/F) The entry is a PhD thesis",
        "review": "(T/F) The entry is a review",
        "proceeding": "(T/F) The entry is a proceeding",
        "book": "(T/F) The entry is a book",
        "noUpdate": "(T/F) The entry has been created/modified by the user "
        + "and/or should not be updated",
        "marks": "Mark the record",
        "abstract": "Abstract of the record",
        "bibdict": "Dictionary with fields of the bibtex entry from bibtexparser",
        "citations": "Most recent number of citations from INSPIRE",
        "citations_no_self": "Most recent number of citations from INSPIRE, excluding self cites",
    }
    entriesExpsDescs = {
        "idEnEx": "Unique identifier",
        "bibkey": "Corresponding bibtex key",
        "idExp": "Corresponding experiment ID",
    }
    expsCatsDescs = {
        "idExC": "Unique identifier",
        "idExp": "Corresponding experiment ID",
        "idCat": "Corresponding category ID",
    }
    expsDescs = {
        "idExp": "Unique ID that identifies the experiment",
        "name": "Name of the experiment",
        "comments": "Description or comments",
        "homepage": "Web link to the experiment homepage",
        "inspire": "INSPIRE-HEP ID of the experiment record",
    }
    searchesDescs = {
        "idS": "Unique identifier",
        "name": "Custom name of the search/replace",
        "count": "Order of the entry in the cronology",
        "searchDict": "Dictionary of fields to be passed to fetchByDict",
        "limit": "The max number of results in the search",
        "offset": "The offset in the search",
        "replaceFields": "List of fields used in replacement",
        "manual": "Manually saved",
        "isReplace": "(T/F) A replacement or a simple search",
    }
    settingsDescs = {
        "id": "Unique identifier",
        "name": "name of the setting",
        "value": "value of the setting",
    }


class ViewStrings(CommonStrings):
    """Strings for the physbiblio.view module"""

    errorLink = "Impossible to get the '%s' link for entry '%s'"
    warningInvalidUse = (
        "Invalid selection or missing information.\n"
        + "Use one of (arxiv|doi|inspire|file) and "
        + "check that all the information is available "
        + "for entry '%s'."
    )
