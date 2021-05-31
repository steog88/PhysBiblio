from .common import CommonStrings


class GenericStrings(CommonStrings):
    """Generic strings that are used in the entire module"""

    genericError = "Impossible to get results"
    searchInfo = "Search '%s' -> %s"


class ADSNasaStrings:
    """Strings for the adsnasa module"""

    genericExportError = "Something went wrong while exporting ADS query"
    genericFetchError = "Something went wrong while fetching ADS"
    invalidField = "Invalid requested field in ADS query: %s"
    remainingQueries = "Remaining queries: %s/%s"
    unauthorized = "Unauthorized use of ADS API. Is your token valid?"


class ArxivStrings(GenericStrings):
    """Strings for the arxiv module"""

    cannotParseRSS = "Cannot parse arxiv RSS feed:\n%s"
    emptyUrl = "Url is empty!"
    errorYearConversion = "Error in converting year from '%s'"
    mainCatNotFound = "Main category not found: %s"
    searchInfo = "Search '%s:%s' -> %s"
    subCatNotFound = "Sub category not found: %s"


class DOIStrings(GenericStrings):
    """Strings for the doi module"""


class InspireStrings(GenericStrings):
    """Strings for the inspire module"""

    errorEmptyText = "An error occurred. Empty text obtained"
    foundID = "Found: %s"
    jsonError = "Cannot load JSON content"
    searchIDInfo = "Search ID of %s -> %s"


class InspireOAIStrings(InspireStrings):
    """Strings for the inspireoai module"""

    cannotSearch = "Inspireoai cannot search strings in the DB"
    emptyRecord = "Empty record!"
    endString = "END --- %s \n\n"
    errorInvalidBibtex = "Invalid bibtex!\n%s"
    errorReadRecord = "Error in readRecord!"
    errorMarcxml = "Impossible to get marcxml for entry %s"
    exceptionFormat = "%s, %s\n%s"
    processed = "Processed %d elements"
    readData = "Reading data --- "
    startString = "\nSTARTING OAI harvester --- %s \n\n"
    warningJournal = "'journal' from OAI is missing or not a string (recid:%s)"
    warningMissing = "Something from OAI is missing (recid:%s)"


class ISBNStrings(GenericStrings):
    """Strings for the isbn module"""


class WebInterfStrings:
    """Strings for the webInterf module"""

    errorBadCodification = "[%s] -> Bad codification, utf-8 decode failed"
    errorImportMethod = "Error importing physbiblio.webimport.%s"
    errorNotFound = "[%s] -> %s not found"
    errorRetrieve = "[%s] -> Error in retrieving data from url"
    errorTimedOut = "[%s] -> Timed out"
    methodNotAvailable = "The method '%s' is not available!"
