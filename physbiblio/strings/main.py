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
    """..."""


class DatabaseStrings:
    """..."""


class DatabaseCoreStrings:
    """..."""


class ErrorsStrings:
    """..."""


class ExportStrings:
    """..."""


class InspireStatsStrings:
    """..."""


class ParseAccentsStrings:
    """Strings for the physbiblio.parseAccents module"""

    converting = "    -> Converting bad characters in entry %s: "


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
    """..."""


class ViewStrings(CommonStrings):
    """Strings for the physbiblio.view module"""

    errorLink = "Impossible to get the '%s' link for entry '%s'"
    warningInvalidUse = (
        "Invalid selection or missing information.\n"
        + "Use one of (arxiv|doi|inspire|file) and "
        + "check that all the information is available "
        + "for entry '%s'."
    )
