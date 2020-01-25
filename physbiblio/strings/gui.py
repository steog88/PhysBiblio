from .common import CommonStrings


class BasicDialogsStrings(CommonStrings):
    """Strings for the basicDialogs module"""

    dir2Use = "Directory to use:"
    fn2Use = "Filename to use:"


class BibWindowsStrings:
    """Strings for the bibWindows module"""


class ProfilesManagerStrings(CommonStrings):
    """Strings for the profileManager module"""

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
    """Strings for the threadElements module"""

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
