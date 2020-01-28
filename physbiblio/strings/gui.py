from .common import CommonStrings
from .main import InspireStatsStrings


class CommonGUIStrings:
    """Some strings used in more than class of this module"""

    cats = "Categories"
    catsAssociated = "Associated categories: {ca}"
    catsInserted = "Categories for '%s' successfully inserted"
    clickMissingIndex = "Click on missing index"
    config = "Configuration"
    entriesCorrespondent = "Corresponding entries: {en}\n"
    entryNotInDb = "The entry '%s' is not in the database!"
    expNotInDb = "The experiment ID %s is not in the database!"
    expsAssociated = "Associated experiments: {ex}"
    featureNYI = "This feature is not implemented"
    filterEntries = "Filter entries"
    noAttribute = "%s has no attribute '%s'"
    nothingChanged = "Nothing changed"
    openEntryList = "Open list of corresponding entries"
    openLinkFailed = "Opening link '%s' failed!"
    winTitle = "PhysBiblio"
    winTitleModified = "PhysBiblio*"


class BasicDialogsStrings(CommonStrings):
    """Strings for the physbiblio.gui.basicDialogs module"""

    dir2Use = "Directory to use:"
    fn2Use = "Filename to use:"


class BibWindowsStrings:
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


class MainWindowStrings:
    """Strings for the physbiblio.gui.mainWindows module"""


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
        "Do you really want to cancel the "
        + "profile '%s'?\n"
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


class ThreadElementsStrings(CommonStrings):
    """Strings for the physbiblio.gui.threadElements module"""

    outdatedError = (
        "Error when executing check_outdated. "
        + "Maybe you are using a developing version"
    )
    outdatedWarning = "Error when trying to check new versions. Are you offline?"
    elementFailed = "Failed in inserting entry %s\n"
    elementImported = "Entries successfully imported:\n%s"
    elementInfoFailed = "Failed in completing info for entry %s\n"
    elementInserted = "Element '%s' successfully inserted.\n"
    errorsEntries = "Errors for entries:\n%s"
