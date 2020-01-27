from .common import CommonStrings
from .main import InspireStatsStrings


class BasicDialogsStrings(CommonStrings):
    """Strings for the physbiblio.gui.basicDialogs module"""

    dir2Use = "Directory to use:"
    fn2Use = "Filename to use:"


class BibWindowsStrings:
    """Strings for the physbiblio.gui.bibWindows module"""


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
