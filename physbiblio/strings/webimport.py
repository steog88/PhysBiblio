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

    cannotFindEntriesInFeed = "Key 'entries' not found in processed feed:\n%s"
    cannotParseRSS = "Cannot parse arxiv RSS feed:\n%s"
    cannotReadDict = "Something went wrong when reading the dictionary"
    cannotReadEntryId = "Cannot read the arXiv ID of this entry: %s"
    cannotReadItem = "Something went wrong when reading the feed item"
    emptyUrl = "Url is empty!"
    errorYearConversion = "Error in converting year from '%s'"
    mainCatNotFound = "Main category not found: %s"
    searchInfo = "Search '%s:%s' -> %s"
    subCatNotFound = "Sub category not found: %s"


class DOIStrings(GenericStrings):
    """Strings for the doi module"""


class InspireStrings(GenericStrings):
    """Strings for the inspire module"""

    apiResponseError = (
        "An error occurred. The API returned the following message: %s - %s"
    )
    endString = "END --- %s \n\n"
    errorEmptyText = "An error occurred. Empty text obtained"
    errorEmptySearch = "An error occurred. No search results obtained"
    errorInvalidBibtex = "Invalid bibtex!\n%s"
    errorReadRecord = "Error in readRecord! id:%s"
    errorUpdateBibtex = "Cannot update bibtex!"
    exceptionFormat = "%s, %s\n%s"
    foundID = "Found: %s"
    jsonError = "Cannot load JSON content"
    numberOfEntriesChanged = "The number of records changed from %s to %s during the execution of the INSPIRE API query"
    processed = "Processed %d elements"
    readData = "Reading data --- "
    searchIDInfo = "Search ID of %s -> %s"
    searchResultsFrom = "Search info from %s"
    startString = "\nSTARTING INSPIRE API harvester --- %s \n\n"
    warningJournal = "'journal' from OAI is missing or not a string (recid:%s)"
    warningMissingField = "Field '%s' from OAI is missing (recid:%s)"


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
