from .common import CommonStrings


class ArgParserStrings:
    """Strings for the physbiblio.argParser module"""

    testFailed = "Some error occurred during tests"


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

    confEntryInsert = "No settings found with this name (%s). Inserting it."
    confEntryUpdate = "An entry with the same name is already present. Updating it"
    confLoaded = "Configuration loaded.\n"
    defaultCfgPath = "Default configuration path: %s"
    defaultDataPath = "Default data path: %s"
    defaultProfileChanged = "Default profile changed to %s"

    descrADSToken = "Token for connecting to the ADS service by NASA"
    descrAutoResize = (
        "Automatically resize columns and rows " + "in the main bibtex table"
    )
    descrBibListCols = "The columns to be shown in the entries list"
    descrConfirmExit = "Confirm before exiting"
    descrDefaultCat = "Default categories for imported bibtexs"
    descrFetchAbstract = (
        "Automatically fetch the abstract " + "from arXiv if an arxiv number is present"
    )
    descrFontSize = "Font size in the list of bibtex entries and companion boxes"
    descrLimitBibtexs = (
        "Number of bibtex entries in the initial view " + "of the main table"
    )
    descrLogFName = "Name of the log file"
    descrLogLevel = (
        "How many messages to save in the log file "
        + "(will have effects only after closing the application)"
    )
    descrMainDBName = "Name of the database file"
    descrMaxAPIRes = (
        "Max number of entries per page " + "when reading external API results"
    )
    descrMaxAuthorsD = "Max number of authors to be displayed in the main list"
    descrMaxAuthorsS = (
        "Max number of authors to be saved " + "when adding info from arXiv"
    )
    descrMaxSavedSearches = "Max number of automatically saved search/replace arguments"
    descrNotifyUpdate = (
        "If configured to False, do not show the existence"
        + " of updates when opening the app"
    )
    descrPDFApp = "Application for opening PDF files " + "(used only via command line)"
    descrPDFFolder = "Folder where to save the PDF files"
    descrSinceLastUpdate = (
        "Parameter that saves the number of the last used version"
        + " for showing the list of changes when a new one is opened"
    )
    descrTimeout = "Timeout for the web queries"
    descrUpdateFrom = (
        "Index of bibtex entries (firstdate ASC) "
        + 'from which I should start when using "Update bibtexs"'
    )
    descrWebApp = "Web browser (used only via command line)"

    errorDeleteProfile = "Cannot delete profile"
    errorInsertProfile = "Cannot insert profile"
    errorInvalidFieldI = "Invalid field or identifierField: %s, %s"
    errorListProfilesMatch = "List of profile names does not match existing profiles!"
    errorName = "No name given!"
    errorNameFilenameOne = (
        "You should specify the name or the filename" + "associated with the profile"
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
        + "[searchDict, replaceFields, name, limitNum, offsetNum]"
    )
    errorUpdateProfile = "Cannot update profile"
    invalidType = "Invalid parameter type: %s"
    noAttribute = "Attribute does not exist for current ConfigParameter: %s"
    readConf = "Reading configuration.\n"
    restartWProfile = "Restarting with profile '%s', database: %s"
    startWProfile = "Starting with profile '%s', database: %s"


class DatabaseStrings:
    """Strings for the physbiblio.database module"""


class DatabaseCoreStrings:
    """Strings for the physbiblio.databaseCore module"""

    closeDb = "Closing database..."
    errorCannotCommit = "Impossible to commit!"
    errorCannotRollback = "Impossible to rollback!"
    invalidIsLocked= "Invalid `self.onIsLocked`!"
    noDatabaseCreate = "-------New database or missing tables.\nCreating them!\n\n"
    openDb = "Opening database: %s"
    rollbackDb = "Rolled back to last commit."
    savedDb = "Database saved."


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


class ViewStrings(CommonStrings):
    """Strings for the physbiblio.view module"""

    errorLink = "Impossible to get the '%s' link for entry '%s'"
    warningInvalidUse = (
        "Invalid selection or missing information.\n"
        + "Use one of (arxiv|doi|inspire|file) and "
        + "check that all the information is available "
        + "for entry '%s'."
    )
