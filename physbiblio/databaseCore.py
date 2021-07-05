"""Module that manages the actions on the database (and few more).

This file is part of the physbiblio package.
"""
import ast
import os
import sqlite3
import sys
import traceback
from sqlite3 import (
    DatabaseError,
    IntegrityError,
    InterfaceError,
    OperationalError,
    ProgrammingError,
)

try:
    import physbiblio.tablesDef
    from physbiblio.strings.main import DatabaseCoreStrings as dbcstr
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise

encoding_default = "iso-8859-15"


class PhysBiblioDBCore:
    """Contains most of the basic functions on the database.
    Will be subclassed to do everything else.
    """

    def __init__(self, dbname, logger, noOpen=False, info=True):
        """Initialize database class (column names, descriptions)
        and opens the database.

        Parameters:
            dbname: the name of the database to be opened
            logger: the logger used for messages
            noOpen (boolean, default False): open the database or not
            info (boolean, default True): show some output when opening DB
        """
        # structure of the tables
        self.tableFields = physbiblio.tablesDef.tableFields
        self.descriptions = physbiblio.tablesDef.fieldsDescriptions
        # names of the columns
        self.tableCols = {}
        for q in self.tableFields.keys():
            self.tableCols[q] = [a[0] for a in self.tableFields[q]]

        self.dbChanged = False
        self.conn = None
        self.curs = None
        self.onIsLocked = None
        self.dbname = dbname
        self.logger = logger
        db_is_new = not os.path.exists(self.dbname)

        if not noOpen:
            self.openDB(info=info)
            if db_is_new or self.checkExistingTables():
                self.logger.info(dbcstr.noDatabaseCreate)
                self.createTables()
            self.checkDatabaseUpdates()

        self.lastFetched = None
        self.catsHier = None

        self.loadSubClasses()

    def openDB(self, info=True):
        """Open the database and creates the self.conn (connection)
        and self.curs (cursor) objects.

        Parameters:
            info (boolean, default True): show some output when opening DB

        Output:
            True
        """
        if info:
            self.logger.info(dbcstr.openDb % self.dbname)
        else:
            self.logger.debug(dbcstr.openDb % self.dbname)
        self.conn = sqlite3.connect(self.dbname, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.curs = self.conn.cursor()
        self.loadSubClasses()
        return True

    def reOpenDB(self):
        """Not defined at this stage. Present in subclass PhysBiblioDB"""
        pass

    def closeDB(self, info=True):
        """Close the database.

        Parameters:
            info (boolean, default True): show some output when opening DB
        """
        if info:
            self.logger.info(dbcstr.closeDb)
        else:
            self.logger.debug(dbcstr.closeDb)
        self.conn.close()
        return True

    def sendDBIsLocked(self):
        """If the database is open in another instance
        and no writing operation are allowed,
        try to emit a signal to the main GUI
        """
        if self.onIsLocked is not None:
            try:
                self.onIsLocked.emit()
            except AttributeError:
                self.logger.exception(dbcstr.invalidIsLocked)
                return False
            else:
                return True
        return False

    def checkUncommitted(self):
        """Check if there are uncommitted changes.

        Output:
            True/False
        """
        if sys.version_info[0] == 3 and sys.version_info[1] > 2:
            return self.conn.in_transaction
        else:
            return self.dbChanged

    def commit(self, verbose=True):
        """Commit the changes.

        Parameters:
            verbose (boolean, default True):
                show some output when opening DB

        Output:
            True if successfull, False if an exception occurred
        """
        try:
            self.conn.commit()
        except Exception:
            self.logger.exception(dbcstr.errorCannotCommit)
            return False
        else:
            self.dbChanged = False
            if verbose:
                self.logger.info(dbcstr.savedDb)
            return True

    def undo(self, verbose=True):
        """Undo the uncommitted changes
        and roll back to the last commit.

        Parameters:
            verbose (boolean, default True):
                show some output when opening DB

        Output:
            True if successfull, False if an exception occurred
        """
        try:
            self.conn.rollback()
        except Exception:
            self.logger.exception(dbcstr.errorCannotRollback)
            return False
        else:
            self.dbChanged = False
            if verbose:
                self.logger.info(dbcstr.rollbackDb)
            return True

    def connExec(self, query, data=None):
        """Execute connection.

        Parameters:
            query (string): the query to be executed
            data (dictionary or list):
                the values of the parameters in the query

        Output:
            True if successfull, False if an exception occurred
        """
        try:
            if data:
                self.conn.execute(query, data)
            else:
                self.conn.execute(query)
        except OperationalError as err:
            if str(err) == "database is locked":
                if not self.sendDBIsLocked():
                    self.logger.error(dbcstr.opErDbOpen % query)
            else:
                self.logger.exception(dbcstr.errorConnection % (err, query))
            return False
        except IntegrityError as err:
            self.logger.exception(dbcstr.errorInsUpd % (err, query))
            return False
        except (ProgrammingError, DatabaseError, InterfaceError) as err:
            self.logger.exception(dbcstr.errorConnection % (err, query))
            return False
        else:
            self.dbChanged = True
            return True

    def cursExec(self, query, data=None):
        """Execute cursor.

        Parameters:
            query (string): the query to be executed
            data (dictionary or list):
                the values of the parameters in the query

        Output:
            True if successfull, False if an exception occurred
        """
        try:
            if data:
                self.curs.execute(query, data)
            else:
                self.curs.execute(query)
        except Exception as err:
            self.logger.exception(
                dbcstr.errorCursor
                % (
                    err,
                    query,
                    data,
                )
            )
            return False
        else:
            return True

    def cursor(self):
        """Function wrapper that returns the default cursor"""
        return self.curs

    def loadSubClasses(self):
        """Not defined at this stage. Present in subclass PhysBiblioDB"""
        pass

    def checkExistingTables(
        self,
        wantedTables=[
            "categories",
            "entries",
            "entryCats",
            "entryExps",
            "expCats",
            "experiments",
            "settings",
        ],
    ):
        """Check that all the required tables
        are present in the database
        """
        self.cursExec("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [name[0] for name in self.curs]
        return not all(t in tables for t in wantedTables)

    def createTable(self, q, fields, critical=False):
        """Create the table 'q'

        Parameters:
            q: the table name
            fieldsDict: the list containing the column information
                for the table
        """
        command = "CREATE TABLE %s (\n" % q
        first = True
        for el in fields:
            if first:
                first = False
            else:
                command += ",\n"
            command += " ".join(el)
        command += ");"
        self.logger.info(command + "\n")
        if not self.connExec(command):
            self.logger.critical(dbcstr.errorCreateTable % q)
            if critical:
                sys.exit(1)
        else:
            if critical:
                self.commit()

    def createTables(self, fieldsDict=None):
        """Create tables for the database
        (and insert the default categories), if it is missing.

        Parameters:
            fieldsDict (default None):
                the structure of the tables (see physbiblio.tablesDef)
        """
        if fieldsDict is None:
            fieldsDict = self.tableFields
        self.cursExec("SELECT name FROM sqlite_master WHERE type='table';")
        existingTables = [name[0] for name in self.curs]
        for q in fieldsDict.keys():
            if q in existingTables:
                continue
            self.createTable(q, fieldsDict[q])
        self.cursExec("select * from categories where idCat = 0 or idCat = 1\n")
        cats = self.curs.fetchall()
        if len(cats) < 2:
            command = (
                "INSERT into categories "
                + "(idCat, name, description, parentCat, ord) values "
                + '(0,"Main","This is the main category. '
                + 'All the other ones are subcategories of this one",0,0), '
                + '(1,"Tags","Use this category to store tags '
                + '(such as: ongoing projects, temporary cats,...)",0,0)\n'
            )
            self.logger.info(command + "\n")
            if not self.connExec(command):
                self.logger.error(dbcstr.errorInsMainCats)
        self.commit()

    def checkDatabaseUpdates(self):
        """Run when new columns are added to the database with respect
        to previous versions of the software
        Check if bibdict column is present in entries table
        """
        entryFields = self.cursExec("PRAGMA table_info(entries);")
        entriesCols = [name[1] for name in self.curs]
        if "bibdict" not in entriesCols:
            if self.connExec("ALTER TABLE entries ADD COLUMN bibdict text;"):
                self.logger.info(dbcstr.newColEntries % ("bibdict", "text"))
                self.commit()
            else:
                self.logger.error(dbcstr.errorAlterEntries)
                self.undo()
        if "citations" not in entriesCols:
            if self.connExec(
                "ALTER TABLE entries ADD COLUMN citations integer default 0;"
            ):
                self.logger.info(dbcstr.newColEntries % ("citations", "integer"))
                self.commit()
            else:
                self.logger.error(dbcstr.errorAlterEntries)
                self.undo()
            if self.connExec(
                "ALTER TABLE entries ADD COLUMN citations_no_self integer default 0;"
            ):
                self.logger.info(
                    dbcstr.newColEntries % ("citations_no_self", "integer")
                )
                self.commit()
            else:
                self.logger.error(dbcstr.errorAlterEntries)
                self.undo()


class PhysBiblioDBSub:
    """Uses PhysBiblioDB instance 'self.mainDB = parent'
    to act on the database.
    All the subcategories of PhysBiblioDB are defined
    starting from this one.
    """

    def __init__(self, parent):
        """Initialize DB class, connecting to
        the main PhysBiblioDB instance (parent).
        """
        self.mainDB = parent

        self.tableFields = self.mainDB.tableFields
        self.tableCols = self.mainDB.tableCols

        self.conn = self.mainDB.conn
        self.curs = self.mainDB.curs
        self.dbname = self.mainDB.dbname

        self.lastFetched = None
        self.catsHier = None

    def sendDBIsLocked(self):
        """Call corresponding PhysBiblioDBCore function"""
        return self.mainDB.sendDBIsLocked()

    def literal_eval(self, string):
        """Wrapper for ast.literal_eval

        Parameters:
            string: the string to evaluate

        Output:
            a string or None
        """
        try:
            if "[" in string and "]" in string:
                return ast.literal_eval(string.strip())
            elif "," in string:
                return ast.literal_eval("[%s]" % string.strip())
            else:
                return string.strip()
        except SyntaxError:
            self.mainDB.logger.warning(dbcstr.errorLiteralEval % string)
            return None

    def closeDB(self):
        """Close the database (using PhysBiblioDB.close)"""
        self.mainDB.closeDB()

    def commit(self):
        """Commit the changes (using PhysBiblioDB.commit)"""
        self.mainDB.commit()

    def connExec(self, query, data=None):
        """Execute connection (see PhysBiblioDB.connExec)"""
        return self.mainDB.connExec(query, data=data)

    def cursExec(self, query, data=None):
        """Execute cursor (see PhysBiblioDB.cursExec)"""
        return self.mainDB.cursExec(query, data=data)

    def cursor(self):
        """Return the cursor"""
        return self.mainDB.cursor()
