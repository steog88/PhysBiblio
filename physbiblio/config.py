"""Manages the configuration of PhysBiblio, from saving to reading.

This file is part of the physbiblio package.
"""
import ast
import logging
import logging.handlers
import os
import sys
import traceback
from collections import OrderedDict

import six
from appdirs import AppDirs

try:
    from physbiblio.databaseCore import PhysBiblioDBCore, PhysBiblioDBSub
    from physbiblio.strings.main import ConfigStrings as cstr
    from physbiblio.tablesDef import profilesSettingsTable, searchesTable, tableFields
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise


globalLogName = "physbibliolog"
if six.PY2:
    FNFError = OSError
else:
    FNFError = FileNotFoundError


class ConfigParameter:
    """Instances contain some properties for configuration parameters,
    such as name, description, special type and default value
    """

    def __init__(self, name, default, description="", special=None, isGlobal=False):
        """Store the passed properties

        Parameters:
            name: the parameter name in the database
            default: the default value if not edited by the user
            description (default ""): a description
                for the configuration dialog
            special (default None): define a special type
                for the parameter (treat as list, int, float, bool, ...)
            isGlobal (default False): if True, the parameter is global
                and shared among all the databases.
                If False, it is relative to the current database only
        """
        self.name = name
        self.default = default
        self.description = description
        self.special = special
        self.isGlobal = isGlobal

    def __getitem__(self, key):
        """Extract attribute using a [...] syntax,
        for compatibility with previous code
        """
        try:
            item = getattr(self, key)
        except AttributeError:
            item = None
            logging.getLogger(globalLogName).warning(cstr.noAttribute % key)
        return item


class ConfigParametersList(OrderedDict):
    """Inherit from OrderedDict, but add a quick method to add
    `ConfigParameter`s to the list"""

    def add(self, cp):
        """Add a new value, corresponding to the key that is cp.name

        Parameters:
            cp: a ConfigParameter instance
        """
        if isinstance(cp, ConfigParameter):
            self[cp.name] = cp
        else:
            logging.getLogger(globalLogName).warning(cstr.invalidType % type(cp))


# these are the default parameter values, descriptions and types
configuration_params = ConfigParametersList()
configuration_params.add(
    ConfigParameter(
        "mainDatabaseName",
        "PBDATAphysbiblio.db",
        description=cstr.Desc.mainDBName,
    )
)
configuration_params.add(
    ConfigParameter(
        "loggingLevel",
        1,
        description=cstr.Desc.logLevel,
        special="int",
    )
)
configuration_params.add(
    ConfigParameter(
        "logFileName",
        "PBDATAparams.log",
        description=cstr.Desc.logFName,
        special=None,
    )
)
configuration_params.add(
    ConfigParameter(
        "pdfFolder",
        "PBDATApdf",
        description=cstr.Desc.PDFFolder,
        special=None,
    )
)
configuration_params.add(
    ConfigParameter(
        "pdfApplication",
        "",
        description=cstr.Desc.PDFApp,
        special=None,
    )
)
configuration_params.add(
    ConfigParameter(
        "webApplication",
        "",
        description=cstr.Desc.webApp,
        special=None,
    )
)
configuration_params.add(
    ConfigParameter(
        "timeoutWebSearch",
        20.0,
        description=cstr.Desc.timeout,
        special="float",
    )
)
configuration_params.add(
    ConfigParameter(
        "askBeforeExit", False, description=cstr.Desc.confirmExit, special="boolean"
    )
)
configuration_params.add(
    ConfigParameter(
        "defaultLimitBibtexs",
        100,
        description=cstr.Desc.limitBibtexs,
        special="int",
    )
)
configuration_params.add(
    ConfigParameter(
        "defaultUpdateFrom",
        0,
        description=cstr.Desc.updateFrom,
        special="int",
    )
)
configuration_params.add(
    ConfigParameter(
        "maxAuthorNames",
        3,
        description=cstr.Desc.maxAuthorsD,
        special="int",
    )
)
configuration_params.add(
    ConfigParameter(
        "maxAuthorSave",
        6,
        description=cstr.Desc.maxAuthorsS,
        special="int",
    )
)
configuration_params.add(
    ConfigParameter(
        "maxExternalAPIResults",
        10,
        description=cstr.Desc.maxAPIRes,
        special="int",
    )
)
configuration_params.add(
    ConfigParameter(
        "fetchAbstract",
        False,
        description=cstr.Desc.fetchAbstract,
        special="boolean",
    )
)
configuration_params.add(
    ConfigParameter(
        "defaultCategories",
        [],
        description=cstr.Desc.defaultCat,
        special="list",
    )
)
configuration_params.add(
    ConfigParameter(
        "bibListFontSize",
        9,
        description=cstr.Desc.fontSize,
        special="float",
    )
)
configuration_params.add(
    ConfigParameter(
        "bibtexListColumns",
        [
            "bibkey",
            "author",
            "title",
            "year",
            "firstdate",
            "pubdate",
            "doi",
            "arxiv",
            "isbn",
            "inspire",
        ],
        description=cstr.Desc.bibListCols,
        special="list",
    )
)
configuration_params.add(
    ConfigParameter(
        "resizeTable",
        True,
        description=cstr.Desc.autoResize,
        special="boolean",
    )
)
configuration_params.add(
    ConfigParameter(
        "maxSavedSearches",
        5,
        description=cstr.Desc.maxSavedSearches,
        special="int",
    )
)
configuration_params.add(
    ConfigParameter(
        "ADSToken",
        "",
        description=cstr.Desc.ADSToken,
        special=None,
    )
)
configuration_params.add(
    ConfigParameter(
        "openSinceLastUpdate",
        "0.0.0",
        description=cstr.Desc.sinceLastUpdate,
        isGlobal=True,
    )
)
configuration_params.add(
    ConfigParameter(
        "notifyUpdate",
        True,
        description=cstr.Desc.notifyUpdate,
        special="boolean",
        isGlobal=True,
    )
)
configuration_params.add(
    ConfigParameter(
        "batchSizeInspire",
        50,
        description=cstr.Desc.limitBibtexs,
        special="int",
    )
)

ignoreParameterOrder = ["mainDatabaseName", "openSinceLastUpdate"]
loggingLevels = ["0 - errors", "1 - warnings", "2 - info", "3 - all"]


class GlobalDB(PhysBiblioDBCore):
    """Class that manages the operations on the global DB:
    profiles and frequent searches/replaces
    """

    def __init__(self, dbname, logger, datapath, info=True):
        """Class constructor

        Parameters:
            dbname: the name of the database to open
            logger: the logger used for messages
            datapath: the path where to store database files
            info (boolean, default True): print some output messages
        """
        self.dataPath = datapath
        PhysBiblioDBCore.__init__(self, dbname, logger, noOpen=True)
        self.openDB(info=info)

        self.cursExec("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [name[0] for name in self.curs]
        if not all([a in tables for a in ["profiles", "searches", "settings"]]):
            self.createTables(tables)

        if self.countProfiles() == 0:
            self.createProfile()
        self.checkOnlyFilename()

        self.config = ConfigurationDB(self)

    def createTables(self, existing):
        """Create the profiles table"""
        if "profiles" not in existing:
            self.createTable("profiles", profilesSettingsTable, critical=True)
        if "searches" not in existing:
            self.createTable("searches", searchesTable, critical=True)
        if "settings" not in existing:
            self.createTable("settings", tableFields["settings"], critical=True)
        return True

    def countProfiles(self):
        """Obtain the number of profiles in the database

        Output:
            the number of profiles
        """
        self.cursExec("SELECT Count(*) FROM profiles")
        return self.curs.fetchall()[0][0]

    def createProfile(
        self, name="default", description="", databasefile=None, oldCfg=""
    ):
        """Create a new profile

        Parameters:
            name: the name of the profile
            description: a short description of the profile
            databasefile: the name of the database file
                which will contain data
            oldCfg: the name of the old .cfg file
                (backwards compatibility only)

        Output:
            True if successful, sys.exit(1) otherwise
        """
        if databasefile is None:
            databasefile = (
                configuration_params["mainDatabaseName"]
                .default.replace("PBDATA", "")
                .replace(self.dataPath, "")
            )
        command = (
            "INSERT into profiles "
            + "(name, description, databasefile, oldCfg, isDefault, ord) "
            + "values (:name, :description, :databasefile, "
            + ":oldCfg, :isDefault, :ord)"
        )
        data = {
            "name": name,
            "description": description,
            "databasefile": databasefile,
            "oldCfg": oldCfg,
            "isDefault": 1 if self.countProfiles() == 0 else 0,
            "ord": 100,
        }
        self.logger.info("%s\n%s" % (command, data))
        if not self.connExec(command, data):
            self.logger.exception(cstr.errorInsertProfile)
            sys.exit(1)
        self.commit(verbose=False)
        return True

    def updateProfileField(self, identifier, field, value, identifierField="name"):
        """Update a field of an existing profile

        Parameters:
            identifier: the identifier of the profile.
                It may be 1 if `identifierField` == "isDefault",
                the name of the profile or the database filename
                if `identifierField` == "name" or "databasefile",
                respectively.
            field: the name of the field to update.
            value: the new vallue of the field
            identifierField: "name", "databasefile" or "isDefault".
                It must be "databasefile" if you want to change
                the profile name and "name" if you want to change
                the databasefile (discouraged, however)

        Output:
            True if successful, False otherwise
        """
        if (
            (field == "databasefile" and identifierField != "name")
            or (field == "name" and identifierField != "databasefile")
            or (identifierField == "isDefault" and identifier != 1)
            or identifierField not in ["name", "databasefile", "isDefault"]
            or field not in [e[0] for e in profilesSettingsTable]
        ):
            self.logger.error(cstr.errorInvalidFieldI % (field, identifierField))
            return False
        command = (
            "update profiles set %s = :val " % field
            + " where %s = :iden\n" % identifierField
        )
        data = {"val": value, "iden": identifier}
        self.logger.debug("%s\n%s" % (command, data))
        if not self.connExec(command, data):
            self.logger.error(cstr.errorUpdateProfile)
            return False
        self.commit(verbose=False)
        return True

    def deleteProfile(self, name):
        """Delete a profile given the name

        Parameters:
            name: the profile name

        Output:
            True if successful, False otherwise
        """
        if name.strip() == "":
            self.logger.error(cstr.errorProfileName)
            return False
        isDefault = name == self.getDefaultProfile()
        command = "delete from profiles where name = :name\n"
        self.logger.debug("%s\n%s" % (command, {"name": name}))
        if not self.connExec(command, {"name": name}):
            self.logger.error(cstr.errorDeleteProfile)
            return False
        if isDefault:
            self.getDefaultProfile()
        self.commit(verbose=False)
        return True

    def getProfiles(self):
        """Get the list of profiles

        Output:
            the list of `sqlite3.Row` objects
        """
        self.cursExec("SELECT * FROM profiles order by ord ASC, name ASC\n")
        return self.curs.fetchall()

    def getProfile(self, name="", filename=""):
        """Get a profile given its name or the name of the database file.
        Note that only one of the two may be given

        Parameters:
            name: the name of the profile
            filename: the database filename of the profile

        Output:
            the `sqlite3.Row` object
        """
        if name.strip() == "" and filename.strip() == "":
            self.logger.warning(cstr.errorNameFilenameOne)
            return {}
        if name.strip() != "" and filename.strip() != "":
            self.logger.warning(cstr.errorNameFilenameOnly)
            return {}
        self.cursExec(
            "SELECT * FROM profiles WHERE name = :name or databasefile = :file\n",
            {"name": name, "file": filename},
        )
        return self.curs.fetchall()[0]

    def getProfileOrder(self):
        """Obtain the order of profiles

        Output:
            a list with the names of the ordered profiles
        """
        if self.countProfiles() == 0:
            self.createProfile()
            self.setDefaultProfile("default")
        self.cursExec("SELECT * FROM profiles order by ord ASC, name ASC\n")
        return [e["name"] for e in self.curs.fetchall()]

    def setProfileOrder(self, order=[]):
        """Set the new order of profiles

        Parameters:
            order: the ordered list of profile names

        Output:
            True if successful, False otherwise
        """
        if order == []:
            self.logger.warning(cstr.errorOrder)
            return False
        if sorted(order) != sorted([e["name"] for e in self.getProfiles()]):
            self.logger.info(sorted(order))
            self.logger.info(sorted([e["name"] for e in self.getProfiles()]))
            self.logger.warning(cstr.errorListProfilesMatch)
            return False
        failed = False
        for ix, profName in enumerate(order):
            if not self.connExec(
                "update profiles set ord=:ord where name=:name\n",
                {"name": profName, "ord": ix},
            ):
                failed = True
        if not failed:
            self.commit(verbose=False)
        else:
            self.logger.error(cstr.errorProfileOrdering)
            self.undo(verbose=False)
        return not failed

    def getDefaultProfile(self):
        """Obtain the name of the default profile

        Output:
            the `sqlite3.Row` objects
        """
        if self.countProfiles() == 0:
            self.createProfile()
            self.setDefaultProfile("default")
        self.cursExec("SELECT * FROM profiles WHERE isDefault = 1\n")
        try:
            defaultProfileName = [e["name"] for e in self.curs.fetchall()][0]
        except IndexError:
            self.cursExec("SELECT * FROM profiles\n")
            defaultProfileName = [e["name"] for e in self.curs.fetchall()][0]
            if self.setDefaultProfile(defaultProfileName):
                self.logger.info(cstr.defaultProfileChanged % defaultProfileName)
        return defaultProfileName

    def setDefaultProfile(self, name=None):
        """Set the new default profile

        Parameters:
            name: the profile name

        Output:
            True if successful, False otherwise
        """
        if name is None or name.strip() == "":
            self.logger.warning(cstr.errorName)
            return False
        self.cursExec("SELECT * FROM profiles WHERE name = :name\n", {"name": name})
        if len(self.curs.fetchall()) == 1:
            if self.connExec(
                "update profiles set isDefault=0 where 1\n"
            ) and self.connExec(
                "update profiles set isDefault=1 where name = :name\n", {"name": name}
            ):
                self.commit(verbose=False)
                return True
            else:
                self.logger.error(cstr.errorProfileDefault)
                self.undo(verbose=False)
                return False
        else:
            self.logger.warning(cstr.errorNoProfilesName)
            return False

    def checkOnlyFilename(self):
        """Convert previously stored profile names"""
        for q in self.getProfiles():
            if q["databasefile"].startswith(self.dataPath):
                self.updateProfileField(
                    q["name"],
                    "databasefile",
                    q["databasefile"].replace(self.dataPath, ""),
                )

    def countSearches(self):
        """Obtain the number of searches in the table

        Output:
            the number of searches
        """
        self.cursExec("SELECT Count(*) FROM searches")
        return self.curs.fetchall()[0][0]

    def insertSearch(
        self,
        name="",
        count=0,
        searchFields=[],
        replaceFields=[],
        manual=False,
        replacement=False,
        limit=0,
        offset=0,
    ):
        """Insert a new search/replace

        Parameters:
            name: the config name
            count: the order in the cronology or in the menu
            searchFields: the list of dictionaries which is meant
                to be passed to fetchByDict
            replaceFields: the replace fields used in searchAndReplace
            manual (boolean, default False): manually saved entry
            replacement (boolean, default False): replace or simple search
            limit: the number of requested entries
            offset: the offset

        Output:
            the output of self.connExec
        """
        if limit == 0:
            limit = pbConfig.params["defaultLimitBibtexs"]
        output = self.connExec(
            "INSERT into searches "
            + "(name, count, searchDict, limitNum, offsetNum, replaceFields,"
            + " manual, isReplace) values (:name, :count, :searchFields,"
            + " :limit, :offset, :replaceFields, :manual, :isReplace)\n",
            {
                "name": name,
                "count": count,
                "searchFields": "%s" % searchFields,
                "limit": limit,
                "offset": offset,
                "replaceFields": "%s" % replaceFields,
                "manual": 1 if manual else 0,
                "isReplace": 1 if replacement else 0,
            },
        )
        self.commit()
        return output

    def deleteSearch(self, idS):
        """Delete a search/replace given the id.

        Parameters:
            idS: the unique identifier

        Output:
            the output of cursExec
        """
        output = self.cursExec("delete from searches where idS=?\n", (idS,))
        self.commit()
        return output

    def getAllSearches(self):
        """Get all the searches

        Output:
            the list of `sqlite3.Row` objects
                with all the searches in the database
        """
        self.cursExec("select * from searches order by count asc\n")
        return self.curs.fetchall()

    def getSearchByID(self, idS):
        """Get a search given its name

        Parameters:
            idS: the name of the search/replace

        Output:
            the list (len = 1) of `sqlite3.Row` objects
                with all the matching searches
        """
        self.cursExec("select * from searches where idS=?\n", (idS,))
        return self.curs.fetchall()

    def getSearchByName(self, name):
        """Get a search given its name

        Parameters:
            name: the name of the search/replace

        Output:
            the list of `sqlite3.Row` objects with all the matching searches
        """
        self.cursExec("select * from searches where name=?\n", (name,))
        return self.curs.fetchall()

    def getSearchList(self, manual=False, replacement=False):
        """Get searches or replaces which were not manually saved

        Parameters:
            manual (boolean, default False): manually saved entry
            replacement (boolean, default False): replace or simple search

        Output:
            the list of `sqlite3.Row` objects with all the matching searches
        """
        self.cursExec(
            "select * from searches where manual=? "
            + "and isReplace=? order by count ASC\n",
            (1 if manual else 0, 1 if replacement else 0),
        )
        return self.curs.fetchall()

    def updateSearchOrder(self, replacement=False):
        """Update the cronology order for searches or replaces
        which were not manually saved

        Parameters:
            replacement (boolean, default False): replace or simple search

        Output:
            True if successfull, False if some sum failed
        """
        self.cursExec(
            "select * from searches where manual=? and isReplace=?\n",
            (0, 1 if replacement else 0),
        )
        for e in self.curs.fetchall():
            if e["count"] + 1 >= pbConfig.params["maxSavedSearches"]:
                self.deleteSearch(e["idS"])
            elif not self.connExec(
                "update searches set count = :count where idS=:idS\n",
                {"idS": e["idS"], "count": e["count"] + 1},
            ):
                self.undo()
                return False
        self.commit()
        return True

    def updateSearchField(self, idS, field, value, isReplace=True):
        """Update a single field of an entry

        Parameters:
            idS: the search ID
            field: the field name
            value: the new value of the field

        Output:
            the output of self.connExec or
                False (empty value or not valid field)
        """
        if (field == "replaceFields" and not isReplace) or (
            field in ["searchDict", "replaceFields", "name", "limitNum", "offsetNum"]
            and value is not None
            and ("%s" % value).strip() not in ["", "[]", "{}"]
        ):
            query = "update searches set " + field + "=:field where idS=:idS\n"
            return self.connExec(query, {"field": "%s" % value, "idS": idS})
        else:
            self.logger.warning(cstr.errorSearchField % (field, value))
            return False


class ConfigurationDB(PhysBiblioDBSub):
    """Subclass that manages the functions for the categories."""

    def count(self):
        """Obtain the number of settings in the table

        Output:
            the number of settings
        """
        self.cursExec("SELECT Count(*) FROM settings")
        return self.curs.fetchall()[0][0]

    def insert(self, name, value):
        """Insert a new setting. If already existing, update it

        Parameters:
            name: the config name
            value: the content of the setting

        Output:
            the output of self.connExec
        """
        self.cursExec("select * from settings where name=?\n", (name,))
        if len(self.curs.fetchall()) > 0:
            self.mainDB.logger.info(cstr.confEntryUpdate)
            return self.update(name, value)
        else:
            return self.connExec(
                "INSERT into settings (name, value) values (:name, :value)\n",
                {"name": name, "value": value},
            )

    def update(self, name, value):
        """Update an existing setting

        Parameters:
            name: the config name
            value: the content of the setting

        Output:
            the output of self.connExec
        """
        self.cursExec("select * from settings where name=?\n", (name,))
        if len(self.curs.fetchall()) == 0:
            self.mainDB.logger.info(cstr.confEntryInsert % name)
            return self.insert(name, value)
        else:
            return self.connExec(
                "update settings set value = :value where name = :name\n",
                {"name": name, "value": value},
            )

    def delete(self, name):
        """Delete a setting.

        Parameters:
            name: the setting name

        Output:
            the output of cursExec
        """
        return self.cursExec("delete from settings where name=?\n", (name,))

    def getAll(self):
        """Get all the settings

        Output:
            the list of `sqlite3.Row` objects with
                all the settings in the database
        """
        self.cursExec("select * from settings\n")
        return self.curs.fetchall()

    def getByName(self, name):
        """Get a setting given its name

        Parameters:
            name: the name of the setting

        Output:
            the list (len = 1) of `sqlite3.Row` objects
            with all the matching settings
        """
        self.cursExec("select * from settings where name=?\n", (name,))
        return self.curs.fetchall()


def getLogLevel(value):
    """Convert the numerical code saved in the configuration
    to a logging level code

    Parameter:
        value: an int, the logging level in the PhysBiblio scale

    Output:
        an int (may be among
            logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG
        )
    """
    if value == 0:
        return logging.ERROR
    elif value == 1:
        return logging.WARNING
    elif value == 2:
        return logging.INFO
    else:
        return logging.DEBUG


def replacePBDATA(path, var):
    """Replace the PBDATA placeholder in the given variable,
    if it is a string, or just return the variable otherwise

    Parameters:
        var: the input variable

    Output:
        the input variable or a string with replaced "PBDATA"
    """
    if isinstance(var, six.string_types) and "PBDATA" in var:
        var = os.path.join(path, var.replace("PBDATA", ""))
    return var


def addFileHandler(logger, logFileName, defaultPath=""):
    """Create and add a RotatingFileHandler to an existing Logger

    Parameters:
        logger: an existing instance of logging.Logger
        logFileName: the name of the log file
        defaultPath (default ""): used in case the logFileName is missing
            to point to the default log file name in the default folder
    """
    try:
        fh = logging.handlers.RotatingFileHandler(
            logFileName, maxBytes=5.0 * 2 ** 20, backupCount=5
        )
    except FNFError:
        logger.exception("")
        fh = logging.handlers.RotatingFileHandler(
            replacePBDATA(defaultPath, configuration_params["logFileName"].default),
            maxBytes=5.0 * 2 ** 20,
            backupCount=5,
        )
    fh.setLevel(getLogLevel(pbConfig.params["loggingLevel"]))
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)10s : [%(module)s.%(funcName)s] %(message)s"
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)


class ConfigVars:
    """Contains all the common settings, the information on the profiles
    and their configuration.
    """

    adsUrl = "https://ui.adsabs.harvard.edu/abs/"
    arxivUrl = "https://arxiv.org"
    doiUrl = "https://doi.org/"
    inspireAPI = "https://inspirehep.net/api/"
    inspireConferencesAPI = "https://inspirehep.net/api/conferences/"
    inspireExperimentsLink = "https://inspirehep.net/experiments/"
    inspireLiteratureAPI = "https://inspirehep.net/api/literature/"
    inspireLiteratureLink = "https://inspirehep.net/literature/"

    def __init__(self, profileFileName="profiles.db"):
        """Initialize the configuration.
        Check the profiles first, then load the default profile
        and its configuration.
        """
        self.defaultProfileName = None
        self.profiles = None
        self.profileOrder = None
        self.currentProfileName = None
        self.currentProfile = None
        self.currentDatabase = ""
        self.loggerString = None
        self.logger = None

        # needed because the main logger will be loaded later!
        logging.basicConfig(
            format="[%(module)s.%(funcName)s] %(message)s", level=logging.INFO
        )
        self.prepareLogger(globalLogName)
        self.defaultDirs = AppDirs("PhysBiblio")

        configPath = os.getenv(
            "PHYSBIBLIO_CONFIG", self.defaultDirs.user_config_dir + os.sep
        )
        self.configPath = (
            configPath
            if isinstance(configPath, six.string_types) and configPath.strip() != ""
            else self.defaultDirs.user_config_dir + os.sep
        )
        dataPath = os.getenv("PHYSBIBLIO_DATA", self.defaultDirs.user_data_dir + os.sep)
        self.dataPath = (
            dataPath
            if isinstance(dataPath, six.string_types) and dataPath.strip() != ""
            else self.defaultDirs.user_data_dir + os.sep
        )
        self.logger.info(cstr.defaultCfgPath % self.configPath)
        if not os.path.exists(self.configPath):
            os.makedirs(self.configPath)
        self.logger.info(cstr.defaultDataPath % self.dataPath)
        if not os.path.exists(self.dataPath):
            os.makedirs(self.dataPath)

        self.loggingLevels = loggingLevels
        self.paramOrder = [
            p.name
            for p in configuration_params.values()
            if p.name not in ignoreParameterOrder
        ]
        self.setDefaultParams()

        self.oldConfigProfilesFile = os.path.join(self.configPath, "profiles.dat")
        self.globalDbFile = os.path.join(self.configPath, profileFileName)
        self.globalDb = GlobalDB(
            self.globalDbFile, self.logger, self.dataPath, info=False
        )

        self.checkOldProfiles()
        self.loadProfiles()

    def loadProfiles(self):
        """Load the information from the profile database"""
        try:
            (
                self.defaultProfileName,
                self.profiles,
                self.profileOrder,
            ) = self.readProfiles()
        except (IOError, ValueError, SyntaxError) as e:
            self.logger.warning(e)
            self.globalDb.createProfile()

    def prepareLogger(self, string):
        """Replace the logger used by this module

        Parameters:
            string: the string used in getLogger
        """
        self.loggerString = string
        self.logger = logging.getLogger(self.loggerString)

    def readConfig(self):
        """Read the configuration from the current database.
        Single parameters are read by self.readParam
        """
        self.logger.debug(cstr.readConf)
        self.setDefaultParams()
        tempDb = PhysBiblioDBCore(self.currentDatabase, self.logger, info=False)
        configDb = ConfigurationDB(tempDb)
        try:
            for k in configuration_params.keys():
                self.readParam(k, configDb)
        except Exception:
            self.logger.exception(cstr.errorReadConf % (self.currentDatabase))
        tempDb.closeDB(info=False)
        rfhs = []
        for lh in self.logger.handlers:
            if isinstance(lh, logging.handlers.RotatingFileHandler):
                rfhs.append(lh)
        for lh in rfhs:
            self.logger.removeHandler(lh)
        addFileHandler(
            self.logger, self.params["logFileName"], defaultPath=self.dataPath
        )
        self.logger.debug(cstr.confLoaded)

    def readParam(self, key, configDb):
        """Read the value of a single parameter from the database,
        and process it according to the parameter type.
        The result is stored in `self.params[key]`

        Parameters:
            key: the parameter name
            configDb: the configuration database where to read from
        """
        if key == "mainDatabaseName":
            return
        if configuration_params[key].isGlobal:
            cont = self.globalDb.config.getByName(key)
        else:
            cont = configDb.getByName(key)
        if len(cont) == 0:
            self.params[key] = self.replacePBDATA(configuration_params[key].default)
            return
        v = cont[0]["value"]
        try:
            if configuration_params[key].special == "float":
                self.params[key] = float(v)
            elif configuration_params[key].special == "int":
                self.params[key] = int(v)
            elif configuration_params[key].special == "boolean":
                if v.lower() in ("true", "1", "yes", "on"):
                    self.params[key] = True
                elif v.lower() in ("false", "0", "no", "off"):
                    self.params[key] = False
                else:
                    raise ValueError
            elif configuration_params[key].special == "list":
                self.params[key] = ast.literal_eval(v.strip())
            else:
                self.params[key] = self.replacePBDATA(v)
        except Exception:
            self.logger.warning(cstr.errorReadParam % key, exc_info=True)
            self.params[key] = configuration_params[key].default

    def readProfiles(self):
        """Reads the list of profiles and the related parameters
        from the profiles database.

        Output:
            the name of the default profile, the dictionary
                with the profiles and the list of ordered profile names
        """
        allProf = self.globalDb.getProfiles()
        profiles = {}
        for e in allProf:
            profiles[e["name"]] = {
                "n": e["name"],
                "d": e["description"],
                "f": e["oldCfg"],
                "db": e["databasefile"]
                if os.sep in e["databasefile"]
                else os.path.join(self.dataPath, e["databasefile"]),
            }
        return (
            self.globalDb.getDefaultProfile(),
            profiles,
            self.globalDb.getProfileOrder(),
        )

    def reInit(self, newShort, newProfile=None):
        """Used when changing profile.
        Reload all the configuration given the new profile name.

        Parameters:
            newShort (str): short name for the new profile to be loaded
            newProfile (dict, optional): the profile file dictionary
        """
        if newProfile is None:
            try:
                newProfile = self.profiles[newShort]
            except KeyError:
                self.logger.error(cstr.errorProfileNotFound)
                return
        self.currentProfileName = newShort
        self.currentProfile = newProfile
        self.currentDatabase = (
            newProfile["db"]
            if os.sep in newProfile["db"]
            else os.path.join(self.dataPath, newProfile["db"])
        )
        self.setDefaultParams()
        self.logger.info(
            cstr.restartWProfile % (self.currentProfileName, self.currentDatabase)
        )
        self.readConfig()

    def reloadProfiles(self, useProfile=None):
        """Load the information from the profile database,
        reset the default and current profile and the settings

        Parameters:
            useProfile (optional): the name of the profile
                to be used instead of the default one
        """
        self.loadProfiles()

        self.currentProfileName = (
            self.defaultProfileName if useProfile is None else useProfile
        )
        try:
            self.currentProfile = self.profiles[self.currentProfileName]
        except KeyError:
            self.logger.critical(
                cstr.errorNoProfileUseDef % (useProfile, self.defaultProfileName)
            )
            self.currentProfileName = self.defaultProfileName
            self.currentProfile = self.profiles[self.currentProfileName]
        self.currentDatabase = (
            self.currentProfile["db"]
            if os.sep in self.currentProfile["db"]
            else os.path.join(self.dataPath, self.currentProfile["db"])
        )
        self.logger.info(
            cstr.startWProfile % (self.currentProfileName, self.currentDatabase)
        )

        self.readConfig()

    def replacePBDATA(self, var):
        """Replace the PBDATA placeholder in the given variable,
        if it is a string, or just return the variable otherwise

        Parameters:
            var: the input variable

        Output:
            the input variable or a string with replaced "PBDATA"
        """
        return replacePBDATA(self.dataPath, var)

    def setDefaultParams(self):
        """Reset the list of params,
        setting their value to the default
        as defined in configuration_params
        """
        self.params = {}
        for k, p in configuration_params.items():
            if k == "mainDatabaseName":
                continue
            self.params[k] = self.replacePBDATA(p.default)

    def checkOldProfiles(self):
        """Intended for backwards compatibility.
        Check if there is a profiles.dat file in the self.configPath folder.
        If yes, move it and the related information into the databases.
        """
        if os.path.isfile(self.oldConfigProfilesFile):
            self.logger.info("Moving info from profiles.dat into the profiles.db")
            for k in self.globalDb.getProfileOrder():
                self.globalDb.deleteProfile(k)
            defProf, profiles, profileOrder = self.oldReadProfiles()
            for k in profiles.keys():
                self.oldReInit(k, profiles[k])
                tempDb = PhysBiblioDBCore(self.params["mainDatabaseName"], self.logger)
                configDb = ConfigurationDB(tempDb)

                self.globalDb.createProfile(
                    name=k,
                    description=profiles[k]["d"],
                    databasefile=self.params["mainDatabaseName"],
                    oldCfg=profiles[k]["f"],
                )
                if k == defProf:
                    self.globalDb.setDefaultProfile(k)
                for p in self.paramOrder:
                    if self.params[p] != configuration_params[p].default:
                        configDb.insert(p, str(self.params[p]))
                tempDb.commit()
                tempDb.closeDB()
                oldfile = os.path.join(self.configPath, profiles[k]["f"])
                os.rename(oldfile, oldfile + "_bck")
                self.logger.info(
                    "Old '%s' renamed to '%s'." % (oldfile, oldfile + "_bck")
                )
            self.globalDb.setProfileOrder(profileOrder)
            self.logger.info([dict(e) for e in self.globalDb.getProfiles()])
            os.rename(self.oldConfigProfilesFile, self.oldConfigProfilesFile + "_bck")
            self.logger.info(
                "Old '%s' renamed to '%s'."
                % (self.oldConfigProfilesFile, self.configProfilesFile + "_bck")
            )

    def oldReadConfigFile(self):
        """Read the configuration from a file,
        whose name is stored in self.configMainFile.
        Parses the various parameters given their declared type.
        """
        for k, p in configuration_params.items():
            if isinstance(p.default, str) and "PBDATA" in p.default:
                p.default = os.path.join(self.dataPath, p.default.replace("PBDATA", ""))
            self.params[k] = p.default
        try:
            with open(self.configMainFile) as r:
                txt = r.readlines()
            for l in txt:
                k, v = l.replace("\n", "").split(" = ")
                try:
                    if configuration_params[k].special == "float":
                        self.params[k] = float(v)
                    elif configuration_params[k].special == "int":
                        self.params[k] = int(v)
                    elif configuration_params[k].special == "boolean":
                        if v.lower() in ("true", "1", "yes", "on"):
                            self.params[k] = True
                        elif v.lower() in ("false", "0", "no", "off"):
                            self.params[k] = False
                        else:
                            raise ValueError
                    elif configuration_params[k].special == "list":
                        self.params[k] = ast.literal_eval(v.strip())
                    else:
                        if isinstance(v, str) and "PBDATA" in v:
                            v = os.path.join(self.dataPath, v.replace("PBDATA", ""))
                        self.params[k] = v
                except Exception:
                    self.logger.warning("Failed in reading parameter", exc_info=True)
                    self.params[k] = v
        except IOError:
            self.logger.warning(
                "ERROR: config file %s do not exist." % self.configMainFile
            )
        except Exception:
            self.logger.error("ERROR: reading %s file failed." % self.configMainFile)

    def oldReadProfiles(self):
        """Reads the list of profiles and the related parameters
        from the profiles.dat file.
        """
        with open(self.oldConfigProfilesFile) as r:
            txtarr = r.readlines()
        txt = "".join(txtarr)
        parsed = ast.literal_eval(txt.replace("\n", ""))
        if len(parsed) < 3:
            parsed = parsed + tuple(sorted(parsed[1].keys()))
        return parsed

    def oldReInit(self, newShort, newProfile):
        """Old function used when changing profile.
        Reloads all the configuration from scratch given the new profile name.

        Parameters:
            newShort (str): short name for the new profile to be loaded
            newProfile (dict): the profile file dictionary
        """
        self.currentProfileName = newShort
        self.params = {}
        for k, p in configuration_params.items():
            self.params[k] = p.default
        self.currentProfile = newProfile
        self.logger.info(
            "Starting with configuration in '%s'" % self.currentProfile["f"]
        )
        self.configMainFile = os.path.join(self.configPath, self.currentProfile["f"])
        self.params = {}
        self.oldReadConfigFile()


pbConfig = ConfigVars()
