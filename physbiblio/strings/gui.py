from .common import CommonStrings
from .main import ErrorsStrings, InspireStatsStrings


class CommonGUIStrings:
    """Some strings used in more than class of this module"""

    attentionE = "Attention!"
    cats = "Categories"
    catsAssociated = "Associated categories: {ca}"
    catsInserted = "Categories for '%s' successfully inserted"
    clickMissingIndex = "Click on missing index"
    config = "Configuration"
    elementFailed = "Failed in inserting entry '%s'\n"
    elementImported = "Entries successfully imported: %s"
    elementInserted = "Element '%s' successfully inserted.\n"
    entriesCorrespondent = "Corresponding entries: {en}\n"
    entryNotInDb = "The entry '%s' is not in the database!"
    expNotInDb = "The experiment ID %s is not in the database!"
    expsAssociated = "Associated experiments: {ex}"
    featureNYI = "This feature is not implemented"
    filterEntries = "Filter entries"
    noAttribute = "%s has no attribute '%s'"
    nothingChanged = "Nothing changed"
    nothingToDo = "Nothing to do..."
    openEntryList = "Open list of corresponding entries"
    openLinkFailed = "Opening link '%s' failed!"
    winTitle = "PhysBiblio"
    winTitleModified = "PhysBiblio*"


class BasicDialogsStrings(CommonStrings):
    """Strings for the physbiblio.gui.basicDialogs module"""

    dir2Use = "Directory to use:"
    fn2Use = "Filename to use:"


class BibWindowsStrings(CommonStrings, CommonGUIStrings):
    """Strings for the physbiblio.gui.bibWindows module"""


class CatWindowsStrings(CommonStrings, CommonGUIStrings):
    """Strings for the physbiblio.gui.catWindows module"""

    addNew = "Add new category"
    addSub = "Add subcategory"
    askDelete = "Do you really want to delete this category (ID = '%s', name = '%s')?"
    askExp = "Ask experiments"
    catDeleted = "Category deleted"
    catDescr = "--Category: %s--"
    catEdit = "Edit category"
    catId = "{idC}: {cat}\n"
    catSaved = "Category saved"
    emptyName = "ERROR: empty category name"
    failedFind = "Failed in finding category"
    filterCat = "Filter categories"
    invalidCat = "Invalid idCat in previous selection: %s"
    markCatBibK = "Mark categories for the following entry:<br><b>key</b>:<br>%s<br>"
    markCatBibKAT = (
        "Mark categories for the following "
        + "entry:<br><b>key</b>:<br>%s<br>"
        + "<b>author(s)</b>:<br>%s<br>"
        + "<b>title</b>:<br>%s<br>"
    )
    markCatExpI = (
        "Mark categories for the following experiment:<br><b>id</b>:<br>%s<br>"
    )
    markCatExpINC = (
        "Mark categories for the following "
        + "experiment:<br><b>id</b>:<br>%s<br>"
        + "<b>name</b>:<br>%s<br>"
        + "<b>comments</b>:<br>%s<br>"
    )
    noModifications = "No modifications to categories"
    selectCat = "Select the desired category (only the first one will be considered):"
    selectCats = "Select the desired categories:"
    selectParent = "Select parent"
    updateCat = "Updating category %s..."


class CommonClassesStrings(CommonStrings):
    """Strings for the physbiblio.gui.commonClasses module"""

    alreadyExisting = " - already existing"
    dataListNotDef = "dataList is not defined!"
    invalidIdentif = "Invalid identifier in previous selection: %s"
    invalidIndexTMP = "Invalid index '%s' in TreeModel.parent"
    invalidParentTM = "Invalid parent '%s' in TreeModel.%s"
    missElement = "Missing element"
    openFailed = "Opening link for '%s' failed!"
    openSuccess = "Opening link '%s' for entry '%s' successful!"


class DialogWindowsStrings(CommonStrings, CommonGUIStrings):
    """Strings for the physbiblio.gui.dialogWindows module"""

    advImpMethod = "Select method: "
    advImpResults = "Advanced import - results"
    advImpSearch = "Search string: "
    advImpTitle = "Advanced import"
    arxCat = "Select category: "
    arxDailyTitle = "Browse arxiv daily"
    arxResTitle = "ArXiv daily listing - results"
    arxSub = "Subcategory: "
    askCats = "Ask categories at the end?"
    bibName = "Bib file name:"
    clearLogAsk = "Are you sure you want to clear the log file?"
    clearLogDone = "Log file cleared."
    clearLogFailClear = "Impossible to clear log file!"
    clearLogFailRead = "Impossible to read log file!"
    clearLogTitle = "Clear log file"
    colsAvailable = "Available columns"
    colsDragAndDrop = "Drag and drop items to order visible columns"
    colsSelected = "Selected columns"
    dirPDFSave = "Directory for saving PDF files:"
    errorAF = "self.abstractFormulas not present in DailyArxivSelect. Eprint: %s"
    exportAddTex = "Add more tex files"
    exportRemove = "Remove unused bibtexs?"
    exportReorder = "Reorder existing bibtexs? (includes removing unused ones)"
    exportTexFile = "Export for tex file"
    exportUpdate = "Update existing bibtexs?"
    globalSett = "global setting"
    importSelRes = (
        "This is the list of elements found.\nSelect the ones that you want to import:"
    )
    invalidData = "Data not valid"
    invalidLoggingLevel = "Invalid string for 'loggingLevel' param. Reset to default"
    invalidParamkey = "Invalid paramkey: '%s'"
    invalidText = "Invalid text: %s"
    logFileContent = "Log File Content"
    logFileName = "Name for the log file"
    logFileRead = "Reading %s"
    redirectPrint = "Redirect print"
    selFile = "Select file"
    texNames = "Tex file name(s):"
    whereExportBibs = "Where do you want to export the entries?"
    whichTexFiles = "Which is/are the *.tex file(s) you want to compile?"


class ExpWindowsStrings(CommonStrings, CommonGUIStrings):
    """Strings for the physbiblio.gui.expWindows module"""

    addNew = "Add new experiment"
    askDelete = "Do you really want to delete this experiment (ID = '%s', name = '%s')?"
    emptyName = "ERROR: empty experiment name"
    expDeleted = "Experiment deleted"
    expDescr = "--Experiment: %s--"
    expEdit = "Edit experiment"
    expId = "{idE}: {exp}\n"
    expSaved = "Experiment saved"
    failedFind = "Failed in finding experiment"
    filterExp = "Filter experiment"
    listTitle = "List of experiments"
    markExpK = "Mark experiments for the following entry:<br><b>key</b>:<br>%s<br>"
    markExpKAT = (
        "Mark experiments for the following entry:<br>"
        + "<b>key</b>:<br>%s<br>"
        + "<b>author(s)</b>:<br>%s<br>"
        + "<b>title</b>:<br>%s<br>"
    )
    noModifications = "No modifications to experiments"
    selectDesired = "Select the desired experiments:"
    updateExp = "Updating experiment %s..."


class InspireStatsGUIStrings(InspireStatsStrings):
    """Strings for the physbiblio.gui.inspireStatsGUI module"""

    citations = "Citations"
    citationsPaper = "Citations for each paper"
    citationsYear = "Citations per year"
    datefmt = "%d/%m/%Y"
    hIndexE = "ND"
    hIndexV = "Author h index: %s"
    lineMoreInfo = "Click on the line to have more information:"
    linesMoreInfo = "Click on the lines to have more information:"
    meanCitations = "Mean citations"
    paperNumber = "Paper number"
    paperYear = "Papers per year"
    plotSaved = "Plot saved."
    plotsSaved = "Plots saved."
    totalCitations = "Total citations"
    xInDateIsD = "%s in date %s is %d"
    xInDateIsF = "%s in date %s is %.2f"
    xInYearIs = "%s in year %d is: %d"
    whereSavePlot = "Where do you want to save the plot of the stats?"
    whereSavePlots = "Where do you want to save the plots of the stats?"


class MainWindowStrings(CommonStrings, ErrorsStrings, CommonGUIStrings):
    """Strings for the physbiblio.gui.mainWindows module"""

    class Act:
        """Strings used in the definitions of the actions"""

        abD = "Show About box"
        abT = "&About"
        advImpD = "Open the advanced import window"
        advImpT = "&Advanced Import"
        arxBD = "Browse most recent arXiv listings"
        arxBT = "Browse last ar&Xiv listings"
        arxID = "Get info from arXiv"
        arxIT = "Info from ar&Xiv"
        autD = "Search publication and citation stats of an author from INSPIRES"
        autT = "&AuthorStats"
        bibM = "&Bibliography"
        bibND = "New bibliographic item"
        bibNT = "New &Bib item"
        catD = "Manage Categories"
        catM = "&Categories"
        catT = "&Categories"
        catND = "New Category"
        catNT = "Ne&w Category"
        chaD = "Show recent changes"
        chaT = "&Changelog"
        cleBD = "Clean all the bibtexs"
        cleBT = "&Clean bibtexs"
        cleED = "Remove spare entries from the connection tables."
        cleET = "&Clean spare entries"
        cleFD = "Clean all the bibtexs, starting from a given one"
        cleFT = "C&lean bibtexs (from ...)"
        clePD = "Remove spare PDF folders."
        clePT = "&Clean spare PDF folders"
        corrD = "Find all the bibtexs which contain syntax errors and are not readable"
        corrT = "&Find corrupted bibtexs"
        dbD = "Show some statistics about the current database"
        dbT = "&Database info"
        delete = "Delete '%s'"
        edit = "Edit '%s'"
        editProfD = "Edit profiles"
        editProfT = "&Edit profiles"
        exitD = "Exit application"
        exitT = "E&xit"
        expAD = "Export complete bibliography as *.bib"
        expAT = "Export &all as *.bib"
        expD = "List of Experiments"
        expM = "&Experiments"
        expLD = "Export last query as *.bib"
        expLT = "Ex&port last as *.bib"
        expND = "New Experiment"
        expNT = "&New Experiment"
        expT = "&Experiments"
        expTD = "Export as *.bib the bibliography needed to compile a .tex file"
        expTT = "Export for a *.&tex"
        fileM = "&File"
        findD = "Open the search dialog to filter the bibtex list"
        findT = "&Find Bibtex entries"
        freqRM = "Frequent &replaces"
        freqSM = "Frequent &searches"
        helpM = "&Help"
        impD = "Import the entries from a *.bib file"
        impT = "&Import from *.bib"
        loadInsCatD = (
            "Use INSPIRE-HEP to load and insert bibtex entries, "
            + "then ask the categories for each"
        )
        loadInsCatT = "&Load from INSPIRE-HEP (ask categories)"
        loadInsD = "Use INSPIRE-HEP to load and insert bibtex entries"
        loadInsT = "&Load from INSPIRE-HEP"
        logD = "Show the content of the logfile"
        logT = "Log file"
        manage = "Manage '%s'"
        profD = "Manage profiles"
        profT = "&Profiles"
        refD = "Refresh the current list of entries"
        refT = "&Refresh current entries list"
        rename = "Rename '%s'"
        resD = "Reload the list of bibtex entries"
        resT = "&Reload (reset) main table"
        saveD = "Save the modifications"
        saveT = "&Save database"
        settD = "Save the settings"
        settT = "Settin&gs"
        srD = "Open the search&replace dialog"
        srT = "&Search and replace bibtexs"
        toolbar = "Toolbar"
        toolsM = "&Tools"
        undoD = "Rollback to last saved database state"
        undoT = "&Undo"
        updBD = "Update all the journal info of bibtexs"
        updBT = "&Update bibtexs"
        updPD = (
            "Update all the journal info of bibtexs, "
            + "but with non-standard options (start from, force, ...)"
        )
        updPT = "Update bibtexs (&personalized)"
        updD = "Read a *.bib file and update the existing elements inside it"
        updT = "Update an existing *.&bib file"

    aboutText = (
        "PhysBiblio (<a href='https://github.com/steog88/physBiblio'>"
        + "https://github.com/steog88/physBiblio</a>) is "
        + "a cross-platform tool for managing a LaTeX/BibTeX database. "
        + "It is written in <code>python</code>, "
        + "using <code>sqlite3</code> for the database management "
        + "and <code>PySide</code> for the graphical part."
        + "<br>"
        + "It supports grouping, tagging, import/export, "
        + "automatic update and various different other functions."
        + "<br><br>"
        + "<b>Paths:</b><br>"
        + "<i>Configuration:</i> {cp:}<br>"
        + "<i>Data:</i> {dp:}<br>"
        + "<br>"
        + "<b>Author:</b> Stefano Gariazzo "
        + "<i>&lt;stefano.gariazzo@gmail.com&gt;</i><br>"
        + "<b>Version:</b> {ver:} ({vd:})<br>"
        + "<b>Python version</b>: {pyv:}"
    )
    aboutTitle = "About PhysBiblio"
    arxBrNoCat = "Non-existent category! %s"
    arxIm = "Import from arXiv"
    arxIn = "Get info from arXiv"
    arxInStart = "Starting importing info from arxiv..."
    askADSTokenText = (
        "Before using the ADS service by NASA, you need to obtain an API key:"
        + " the current value is empty.<br/>Sign up for the newest version of ADS search "
        + "at <a href='https://ui.adsabs.harvard.edu'>https://ui.adsabs.harvard.edu</a>,"
        + " visit 'Customize settings', 'API token' and 'Generate a new key'.<br/>"
        + "Then, enter it here and it will be stored in the configuration:"
    )
    askADSTokenTitle = "Token for ADS is missing"
    askOverwriteBib = "Do you want to overwrite the existing .bib file?"
    authorStEmptyName = "Empty name inserted! cannot proceed."
    authorStNameAsk = (
        "Insert the INSPIRE name of the author of which you want "
        + "the publication and citation statistics:"
    )
    authorStStart = "Starting computing author stats from INSPIRE..."
    authorStStats = "Statistics for '%s'"
    authorStNameTit = "Author name?"
    authorStatsTitle = "Author Stats"
    catInserted = "categories for '%s' successfully inserted"
    cheBib = "Check Bibtexs"
    cheBibFound = "%d bad records have been found. Do you want to fix them one by one?"
    cheBibNoInv = "No invalid records found!"
    cheBibStart = "Starting checking bibtexs..."
    cheBibSumNoAct = (
        "These are the bibtex keys corresponding to invalid records:\n%s"
        + "\n\nNo action will be performed."
    )
    cleBib = "Clean Bibtexs"
    cleBibStart = "Starting cleaning of bibtexs..."
    cleBibStartAsk = (
        "Insert the ordinal number of the bibtex element "
        + "from which you want to start the cleaning:"
    )
    cleBibStartTit = "Where do you want to start cleanBibtexs from?"
    cleanSpareT = "Clean spare entries"
    cleanPDFAsk = (
        "Do you really want to delete the unassociated PDF folders?\n"
        + "There may be some (unlikely) accidental deletion of files."
    )
    cleanPDFT = "Clean spare PDF folders"
    configDiscard = "Changes discarded"
    configNewVal = "New value for param %s = %s (old: '%s')"
    configNoChanges = "No changes requested"
    configReload = "Reloading configuration..."
    configSave = "Configuration saved"
    configUseVal = "Using configuration param %s = %s"
    dbLockedAskClose = (
        "The database is locked.\n"
        + "Probably another instance of the program is currently open "
        + "and you cannot save your changes.\n"
        + "For this reason, the current instance may not work properly.\n"
        + "Do you want to close this instance of PhysBiblio?"
    )
    dbStatsText = (
        "The PhysBiblio database currently contains "
        + "the following number of records:\n"
        + "- {bib:} bibtex entries\n"
        + "- {cat:} categories\n"
        + "- {exp:} experiments,\n"
        + "- {catbib:} bibtex entries to categories connections\n"
        + "- {catexp:} experiment to categories connections\n"
        + "- {bibexp:} bibtex entries to experiment connections.\n\n"
        + "The number of currently stored PDF files is {nf:}.\n"
        + "The size of the PDF folder is {pdfs:}."
    )
    dbStatsTitle = "PhysBiblio database statistics"
    emptyFN = "Empty filename given!"
    emptyInFNs = "Empty input filename(s)!"
    emptyOutFN = "Empty output filename!"
    emptyCantProceed = "Empty string! cannot proceed."
    expInserted = "experiments for '%s' successfully inserted"
    exporting = "Exporting..."
    exportAllSaved = "All entries saved into '%s'"
    exportLastDone = "Last fetched entries exported into '%s'"
    exportSelDone = "Current selection exported into '%s'"
    exportWhereG = "Where do you want to export the entries?"
    exportWhereS = "Where do you want to export the selected entries?"
    forceUpdText = (
        "Do you want to force the update of already "
        + "existing items?\n(Only regular articles not "
        + "explicitely excluded will be considered)"
    )
    forceUpdTitle = "Force update:"
    importAllDone = "All entries into '%s' have been imported"
    importFile = "File '%s' imported!"
    importFromWhere = "From where do you want to import?"
    importing = "Importing..."
    importInspAskStr = (
        "Insert the query string you want to use for importing from INSPIRE-HEP:\n"
        + "(It will be interpreted as a list, if possible)"
    )
    importInspire = "Do you want to use INSPIRE to find more information about the imported entries?"
    importInspNoRes = (
        "No results obtained. Maybe there was an error or you interrupted execution."
    )
    importInspStarting = "Starting import from INSPIRE..."
    importInspTit = "Import from INSPIRE-HEP"
    invalidEntry = "Invalid entry"
    invalidIntAsk = (
        "The text you inserted is not an integer. "
        + "I will start from 0.\nDo you want to continue?"
    )
    listSyntax = "Cannot recognize the list sintax. Missing quotes in the string?"
    mainTab = "Main tab"
    newTab = "New tab"
    newTabAsk = "Insert the new tab name"
    newTabName = "New tab name?"
    newVersion = (
        "New version available (%s)!\n"
        + "You can upgrade with `pip install -U physbiblio` "
        + "(with `sudo`, eventually)."
    )
    noNewVersion = "No new versions available!"
    noRes = "No results obtained."
    paperStats = "Paper Stats"
    paperStError = "No results obtained. Maybe there was an error."
    paperStStats = "Statistics for recid:%s"
    queryStr = "Query string?"
    recentCh = "Recent changes"
    recentNew = "New in this <b>version %s</b> (%s):<br>"
    reloadMain = "Reloading main table..."
    replaceAskName = (
        "Insert a name / short description to be able "
        + "to recognise this replace in the future:"
    )
    replaceCompl = (
        "Replace completed.<br><br>"
        + "{suc:} elements successfully processed "
        + "(of which {ncha:} changed), "
        + "{nfai:} failures (see below)."
        + "<br><br><b>Changed</b>: {cha:}"
        + "<br><br><b>Failed</b>: {fai:}"
    )
    replaceEmptyStr = "The string to substitute is empty!"
    replaceEmptyStrAsk = "Empty new string. Are you sure you want to continue?"
    replaceName = "Replace name"
    saveAsk = "Do you really want to save?"
    saveCh = "Changes saved"
    saveNoth = "Nothing saved"
    searchAskDelete = "Are you sure you want to delete the saved search '%s'?"
    searchAskName = (
        "Insert a name / short description to be able "
        + "to recognise this search in the future:"
    )
    searchCantFind = "Cannot find the requested search! id:%s"
    searching = "Searching:\n%s"
    searchName = "Search name"
    srMoreEntries = (
        "Warning: more entries match the current search, showing only the first %d of %d."
        + "\nChange 'Max number of results' in the search form to see more."
    )
    srAskNewName = (
        "Insert a new name / short description "
        + "to be able to recognise this search/replace in the future "
        + "(current name: '%s'):"
    )
    srNewName = "New name"
    trigCat = "categories triggered"
    trigExp = "experiments triggered"
    unsavedChanges = "There may be unsaved changes to the database."
    updateFileD = "File '%s' updated"
    updateFileQ = "File to update?"
    updateInfo = "Update Info"
    updateInfoStart = "Starting generic info update from INSPIRE-HEP..."
    updateStartFrom = "Starting update of bibtexs from %s..."
    updateTitle = "Update Bibtexs"
    updINumText = (
        "Insert the ordinal number of the bibtex element "
        + "from which you want to start the updates:"
    )
    updINumTitle = "Where do you want to start searchOAIUpdates from?"
    wantToExit = "Do you really want to exit?"


class MarksStrings:
    """Strings for the physbiblio.gui.marks module"""

    anys = "Any"
    bad = "Bad"
    favorite = "Favorite"
    important = "Important"
    toBeRead = "To be read"
    unclear = "Unclear"
    marks = "Marks"


class ProfilesManagerStrings(CommonStrings):
    """Strings for the physbiblio.gui.profileManager module"""

    addNew = "Add new?"
    askCancel = (
        "Do you really want to cancel the profile '%s'?\n"
        + "The action cannot be undone!\n"
        + "The corresponding database will not be erased."
    )
    availableProfiles = "Available profiles: "
    cannotCreateEmpty = "Cannot create a new profile if 'name' or 'filename' is empty."
    cannotCreateFieldInUse = "Cannot create new profile: '%s' already in use."
    changingProfile = "Changing profile..."
    completed = "Profile management completed"
    copyFrom = "Copy from:"
    editProfile = "Edit profile"
    errorSwitchLines = "Impossible to switch lines: index out of range"
    missingField = "Missing field: '%s' in %s. Default to empty."
    missingInfo = "Missing info: '%s' in %s. Default to empty."
    missingProfile = "Missing profile: '%s' in %s"
    newCreated = "New profile created."
    noModifications = "No modifications"
    selectProfile = "Select profile"
    splitter = " -- "


class ThreadElementsStrings(CommonStrings, CommonGUIStrings):
    """Strings for the physbiblio.gui.threadElements module"""

    outdatedError = (
        "Error when executing check_outdated. "
        + "Maybe you are using a developing version"
    )
    outdatedWarning = "Error when trying to check new versions. Are you offline?"
    errorsEntries = "Errors for entries:\n%s"
