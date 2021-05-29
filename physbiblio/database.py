"""Module that manages the actions on the database (and few more).

This file is part of the physbiblio package.
"""
import ast
import datetime
import os
import re
import traceback
from sqlite3 import DatabaseError, InterfaceError, OperationalError, ProgrammingError

import bibtexparser
import dictdiffer
import six
from pyparsing import ParseException

try:
    from physbiblio.bibtexWriter import pbWriter
    from physbiblio.config import ConfigurationDB, pbConfig
    from physbiblio.databaseCore import PhysBiblioDBCore, PhysBiblioDBSub
    from physbiblio.errors import pBLogger
    from physbiblio.parseAccents import parse_accents_str
    from physbiblio.strings.main import DatabaseStrings as dstr
    from physbiblio.webimport.webInterf import physBiblioWeb
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise


class PhysBiblioDB(PhysBiblioDBCore):
    """Subclassing PhysBiblioDBCore to add reOpenDB
    and loadSubClasses implementations.
    """

    def reOpenDB(self, newDB=None):
        """Close the currently open database and
        open a new one (the same if newDB is None).

        Parameters:
            newDB: None (default) or the name of the new database

        Output:
            True if successfull
        """
        self.utils = None
        self.bibs = None
        self.cats = None
        self.exps = None
        self.bibExp = None
        self.catBib = None
        self.catExp = None
        self.config = None
        if newDB is not None:
            self.closeDB()
            del self.conn
            del self.curs
            self.dbname = newDB
            db_is_new = not os.path.exists(self.dbname)
            self.openDB()
            if db_is_new or self.checkExistingTables():
                self.logger.info(dstr.newDbCreate)
                self.createTables()
            self.checkDatabaseUpdates()
            self.lastFetched = None
            self.catsHier = None
        else:
            self.closeDB()
            self.openDB()
            if self.checkExistingTables():
                self.logger.info(dstr.newDbCreate)
                self.createTables()
            self.checkDatabaseUpdates()
            self.lastFetched = None
            self.catsHier = None
        return True

    def loadSubClasses(self):
        """Load the subclasses that manage the content
        in the various tables in the database.

        Output:
            True
        """
        for q in [
            "bibs",
            "cats",
            "exps",
            "bibExp",
            "catBib",
            "catExp",
            "utils",
            "config",
        ]:
            try:
                delattr(self, q)
            except AttributeError:
                pass
        self.utils = Utilities(self)
        self.bibs = Entries(self)
        self.cats = Categories(self)
        self.exps = Experiments(self)
        self.bibExp = EntryExps(self)
        self.catBib = CatsEntries(self)
        self.catExp = CatsExps(self)
        self.config = ConfigurationDB(self)
        return True

    def checkDatabaseUpdates(self):
        """Run when new columns are added to the database with respect
        to previous versions of the software
        Check if bibdict column is present in entries table
        """
        PhysBiblioDBCore.checkDatabaseUpdates(self)
        self.convertSearchFormat()
        self.checkCaseInsensitiveBibkey()

    def checkCaseInsensitiveBibkey(self):
        """Check if the 'bibkey' field in the 'entries' table
        is case insensitive or not.
        If not, update the table structure
        """
        testQ = (
            "SELECT sql FROM sqlite_master WHERE type='table' "
            + "AND tbl_name='entries'"
        )
        self.cursExec(testQ)
        try:
            createQ = self.curs.fetchall()[0][0]
        except IndexError:
            pBLogger.exception("Impossible to read create table for 'entries'")
            return
        if "bibkey text primary key not null," in createQ:
            pBLogger.info(
                "Performing conversion of 'entries' table to case-insensitive key"
            )
            for fixQ in [
                "BEGIN TRANSACTION;",
                "ALTER TABLE entries RENAME TO tmp_entries;",
            ]:
                if not self.connExec(fixQ):
                    pBLogger.exception("Impossible to rename table 'entries'")
                    self.undo()
                    return
            self.createTable("entries", self.tableFields["entries"])
            for fixQ in [
                "INSERT INTO entries SELECT * FROM tmp_entries;",
                "DROP TABLE tmp_entries;",
            ]:
                if not self.connExec(fixQ):
                    pBLogger.exception("Impossible to read create table for 'entries'")
                    self.undo()
                    return
            self.commit()
        else:
            pBLogger.debug(
                "'bibkey' was not created without 'collate nocase'."
                + " Nothing to do here."
            )

    def convertSearchFormat(self):
        """Read the old saved searches/replaces and convert them
        to the new format for future use"""
        defSeF = [
            {
                "type": "Text",
                "logical": None,
                "field": "bibtex",
                "operator": "contains",
                "content": "",
            }
        ]
        defReF = {
            "regex": False,
            "fieOld": "author",
            "fieNew": "author",
            "old": "",
            "new": "",
            "fieNew1": "author",
            "new1": "",
            "double": False,
        }
        for sr in pbConfig.globalDb.getAllSearches():
            try:
                searchFields = ast.literal_eval(sr["searchDict"])
            except (ValueError, SyntaxError):
                pBLogger.error(
                    "Something went wrong when processing "
                    + "the search fields: '%s'" % sr["searchDict"]
                )
                pbConfig.globalDb.updateSearchField(sr["idS"], "searchDict", defSeF)
                searchFields = defSeF
            if not isinstance(searchFields, list) and isinstance(searchFields, dict):
                newContent = []
                first = True
                if "cats" in searchFields.keys():
                    first = False
                    newContent.append(
                        {
                            "type": "Categories",
                            "logical": None,
                            "field": "",
                            "operator": "all the following"
                            if searchFields["cats"]["operator"] == "and"
                            else "at least one among",
                            "content": searchFields["cats"]["id"],
                        }
                    )
                    del searchFields["cats"]
                if not first:
                    try:
                        ceop = searchFields["catExpOperator"]
                    except KeyError:
                        ceop = None
                else:
                    ceop = None
                try:
                    del searchFields["catExpOperator"]
                except KeyError:
                    pass
                if "exps" in searchFields.keys():
                    newContent.append(
                        {
                            "type": "Experiments",
                            "logical": ceop,
                            "field": "",
                            "operator": "all the following"
                            if searchFields["exps"]["operator"] == "and"
                            else "at least one among",
                            "content": searchFields["exps"]["id"],
                        }
                    )
                    del searchFields["exps"]
                if "marks" in searchFields.keys():
                    newContent.append(
                        {
                            "type": "Marks",
                            "logical": searchFields["marks"]["connection"],
                            "field": None,
                            "operator": None,
                            "content": ["any"]
                            if searchFields["marks"]["operator"] == "!="
                            else [searchFields["marks"]["str"]],
                        }
                    )
                    del searchFields["marks"]
                for t in self.bibs.searchPossibleTypes:
                    if t in searchFields.keys():
                        newContent.append(
                            {
                                "type": "Type",
                                "logical": searchFields[t]["connection"],
                                "field": None,
                                "operator": None,
                                "content": [t],
                            }
                        )
                        del searchFields[t]
                for fi in sorted(searchFields.keys()):
                    f, i = fi.split("#")
                    newContent.append(
                        {
                            "type": "Text",
                            "logical": searchFields[fi]["connection"],
                            "field": f,
                            "operator": searchFields[fi]["operator"],
                            "content": searchFields[fi]["str"],
                        }
                    )
                pbConfig.globalDb.updateSearchField(sr["idS"], "searchDict", newContent)

            if sr["replaceFields"] == "[]":
                pbConfig.globalDb.updateSearchField(
                    sr["idS"], "replaceFields", "{}", isReplace=False
                )
            if sr["isReplace"]:
                newContent = sr["replaceFields"]
                try:
                    replaceFields = ast.literal_eval(sr["replaceFields"])
                except (ValueError, SyntaxError):
                    pBLogger.error(
                        "Something went wrong when processing "
                        + "the saved replace: '%s'" % sr["replaceFields"]
                    )
                    replaceFields = {}
                    newContent = defReF
                if isinstance(replaceFields, list):
                    newContent = {}
                    if sr["isReplace"]:
                        try:
                            newContent["regex"] = replaceFields[4]
                            newContent["fieOld"] = replaceFields[0]
                            newContent["fieNew"] = replaceFields[1][0]
                            newContent["old"] = replaceFields[2]
                            newContent["new"] = replaceFields[3][0]
                        except IndexError:
                            pBLogger.error(
                                "Not enough elements for conversion: "
                                + sr["replaceFields"]
                            )
                            newContent = defReF
                        try:
                            newContent["fieNew1"] = replaceFields[1][1]
                            newContent["new1"] = replaceFields[3][1]
                            newContent["double"] = True
                        except IndexError:
                            newContent["fieNew1"] = defReF["fieNew1"]
                            newContent["new1"] = defReF["new1"]
                            newContent["double"] = defReF["double"]
                if "%s" % newContent != sr["replaceFields"]:
                    pbConfig.globalDb.updateSearchField(
                        sr["idS"], "replaceFields", newContent
                    )
            pbConfig.globalDb.commit(verbose=False)


class Categories(PhysBiblioDBSub):
    """Subclass that manages the functions for the categories."""

    def count(self):
        """Obtain the number of categories in the table"""
        self.cursExec("SELECT Count(*) FROM categories")
        return self.curs.fetchall()[0][0]

    def insert(self, data):
        """Insert a new category

        Parameters:
            data: the dictionary containing the category field values

        Output:
            False if another category with the same name and
                parent is present, the output of self.connExec otherwise
        """
        try:
            self.cursExec(
                "select * from categories where name=? and parentCat=?\n",
                (data["name"], data["parentCat"]),
            )
        except KeyError:
            pBLogger.exception(dstr.Cats.missingField)
            return False
        if self.curs.fetchall():
            pBLogger.info(dstr.Cats.alreadyPresent)
            return False
        else:
            return self.connExec(
                "INSERT into categories (name, description, parentCat, "
                + "comments, ord) values (:name, :description, :parentCat, "
                + ":comments, :ord)\n",
                data,
            )

    def update(self, data, idCat):
        """Update all the fields of an existing category

        Parameters:
            data: the dictionary containing the category field values
            idCat: the id of the category in the database

        Output:
            the output of self.connExec
        """
        data["idCat"] = idCat
        query = (
            "replace into categories ("
            + ", ".join(data.keys())
            + ") values (:"
            + ", :".join(data.keys())
            + ")\n"
        )
        return self.connExec(query, data)

    def updateField(self, idCat, field, value):
        """Update a field of an existing category

        Parameters:
            idCat: the id of the category in the database
            field: the name of the field
            value: the value of the field

        Output:
            False if the field or the value is not valid,
                the output of self.connExec otherwise
        """
        pBLogger.info(dstr.Cats.updateField % (field, idCat))
        if (
            field in self.tableCols["categories"]
            and field != "idCat"
            and value != ""
            and value is not None
        ):
            query = "update categories set " + field + "=:field where idCat=:idCat\n"
            return self.connExec(query, {"field": value, "idCat": idCat})
        else:
            return False

    def delete(self, idCat, name=None):
        """Delete a category, its subcategories and all their connections.
        Cannot delete categories with id ==0 or ==1
        (Main and Tags, the default categories).

        Parameters:
            idCat: the id of the category (or a list)
            name (optional): if id is smaller than 2,
                the name is used instead.

        Output:
            False if id ==0 or ==1, True otherwise
        """
        if isinstance(idCat, list):
            for c in idCat:
                self.delete(c)
        else:
            if idCat < 2 and name:
                result = self.extractCatByName(name)
                idCat = result[0]["idCat"]
            if idCat < 2:
                pBLogger.info(
                    dstr.Cats.cannotDelete
                    % (idCat, " (name: %s)" % name if name else "")
                )
                return False
            pBLogger.info(dstr.Cats.useCat % idCat)
            pBLogger.info(dstr.Cats.lookChild)
            for row in self.getChild(idCat):
                self.delete(row["idCat"])
            self.cursExec("delete from categories where idCat=?\n", (idCat,))
            self.cursExec("delete from expCats where idCat=?\n", (idCat,))
            self.cursExec("delete from entryCats where idCat=?\n", (idCat,))
            return True

    def getAll(self):
        """Get all the categories

        Output:
            the list of `sqlite3.Row` objects with all
                the categories in the database
        """
        self.cursExec("select * from categories\n")
        return self.curs.fetchall()

    def getByID(self, idCat):
        """Get a category given its id

        Parameters:
            idCat: the id of the required category

        Output:
            the list (len = 1) of `sqlite3.Row` objects
                with all the matching categories
        """
        self.cursExec("select * from categories where idCat=?\n", (idCat,))
        return self.curs.fetchall()

    def getDictByID(self, idCat):
        """Get a category given its id, returns a standard dictionary

        Parameters:
            idCat: the id of the required category

        Output:
            a dictionary with all field values for the required category
        """
        self.cursExec("select * from categories where idCat=?\n", (idCat,))
        try:
            entry = self.curs.fetchall()[0]
            catDict = {}
            for i, k in enumerate(self.tableCols["categories"]):
                catDict[k] = entry[i]
        except:
            pBLogger.info(dstr.Cats.errorExtract)
            catDict = None
        return catDict

    def getByName(self, name):
        """Get categories given the name

        Parameters:
            name: the name of the required category

        Output:
            the list of `sqlite3.Row` objects
                with all the matching categories
        """
        self.cursExec("select * from categories where name=?\n", (name,))
        return self.curs.fetchall()

    def getChild(self, parent):
        """Get the subcategories that have as a parent the given one

        Parameters:
            parent: the id of the parent category

        Output:
            the list of `sqlite3.Row` objects
                with all the matching categories
        """
        self.cursExec(
            "select cats1.* from categories as cats "
            + "join categories as cats1 on cats.idCat=cats1.parentCat "
            + "where cats.idCat=?\n",
            (parent,),
        )
        return self.curs.fetchall()

    def getAllCatsInTree(self, parent):
        """Get a list of all the subcategories that are in the tree
        starting with the given one

        Parameters:
            parent: the `idCat` of the parent category

        Output:
            the list of `idCat`s of the categories
        """
        try:
            [a for a in parent]
        except TypeError:
            parent = [parent]
        result = []
        for c in parent:
            if len(self.getByID(c)) == 0:
                continue
            r = self.getChild(c)
            result += [c] + [a["idCat"] for a in r]
        unique = set(result)
        result = [a for a in unique]
        for a in unique - set(parent):
            result += self.getAllCatsInTree(a)
        return list(set(result))

    def getParent(self, child):
        """Get the category that is the parent of the given one

        Parameters:
            child: the id of the child category

        Output:
            the list (len = 1) of `sqlite3.Row` objects
                with all the matching categories
        """
        self.cursExec(
            "select cats.* from categories as cats "
            + "join categories as cats1 on cats.idCat=cats1.parentCat "
            + "where cats1.idCat=?\n",
            (child,),
        )
        return self.curs.fetchall()

    def getHier(self, cats=None, startFrom=0, replace=True):
        """Builds a tree with the parent/child structure of the categories

        Parameters:
            cats: the list of `sqlite3.Row` objects of the categories
                to be considered or None
                (in this case the list is taken from self.getAll)
            startFrom (default 0, the main category):
                the parent category starting from which
                the tree should be built
            replace (boolean, default True): if True,
                rebuild the structure again,
                if False return the previously calculated one

        Output:
            the dictionary defining the tree of subcategories
                of the initial one
        """
        if self.catsHier is not None and not replace:
            return self.catsHier
        if cats is None:
            cats = self.getAll()

        def addSubCats(idC):
            """The subfunction that recursively builds
            the list of child categories

            Parameters:
                idC: the id of the parent category
            """
            tmp = {}
            for c in [a for a in cats if a["parentCat"] == idC and a["idCat"] != 0]:
                tmp[c["idCat"]] = addSubCats(c["idCat"])
            return tmp

        catsHier = {}
        catsHier[startFrom] = addSubCats(startFrom)
        self.catsHier = catsHier
        return catsHier

    def printHier(
        self, startFrom=0, sp=5 * " ", withDesc=False, depth=10, replace=False
    ):
        """Print categories and subcategories in a tree-like form

        Parameters:
            startFrom (default 0, the main category):
                the starting parent category
            sp (default 5*" "): the spacing to use while
                indenting inner levels
            withDesc (boolean, default False): if True,
                print also the category description
            depth (default 10): the maximum number of levels to print
            replace (boolean, default True):
                if True, rebuild the structure again,
                if False return the previously calculated one
        """
        cats = self.getAll()
        if depth < 2:
            pBLogger.warning(dstr.Cats.invalidDepth)
            depth = 10
        catsHier = self.getHier(cats, startFrom=startFrom, replace=replace)

        def printSubGroup(tree, indent="", startDepth=0):
            """The subfunction that recursively builds
            the list of child categories

            Parameters:
                tree (dictionary): the tree structure to use
                indent (default ""): the indentation level
                    from which to start
                startDepth (default 0): the depth from which to start
            """
            if startDepth <= depth:
                for l in cats_alphabetical(tree.keys(), self.mainDB):
                    print(indent + catString(l, self.mainDB, withDesc=withDesc))
                    printSubGroup(tree[l], (startDepth + 1) * sp, startDepth + 1)

        printSubGroup(catsHier)

    def getByEntry(self, key):
        """Find all the categories associated to a given entry

        Parameters:
            key: the bibtex key of the entry

        Output:
            the list of `sqlite3.Row` objects
                with all the matching categories
        """
        self.cursExec(
            "select * from categories "
            + "join entryCats on categories.idCat=entryCats.idCat "
            + "where entryCats.bibkey=?\n",
            (key,),
        )
        return self.curs.fetchall()

    def getByEntries(self, keys):
        """Find all the categories associated to a list of entries

        Parameters:
            keys: the list of bibtex keys of the entries

        Output:
            the list of `sqlite3.Row` objects
                with all the matching categories
        """
        self.cursExec(
            "select * from categories "
            + "join entryCats on categories.idCat=entryCats.idCat "
            + "where "
            + " or ".join(["entryCats.bibkey=?" for k in keys])
            + "\n",
            keys,
        )
        return self.curs.fetchall()

    def getByExp(self, idExp):
        """Find all the categories associated to a given experiment

        Parameters:
            idExp: the id of the experiment

        Output:
            the list of `sqlite3.Row` objects
                with all the matching categories
        """
        self.cursExec(
            "select * from categories "
            + "join expCats on categories.idCat=expCats.idCat "
            + "where expCats.idExp=?\n",
            (idExp,),
        )
        return self.curs.fetchall()


class CatsEntries(PhysBiblioDBSub):
    """Functions for connecting categories and entries"""

    def count(self):
        """obtain the number of rows in entryCats"""
        self.cursExec("SELECT Count(*) FROM entryCats")
        return self.curs.fetchall()[0][0]

    def countByCat(self, idCat):
        """Obtain the number of rows in entryCats
        which are associated with a given category

        Parameters:
            idCat: the id of the category

        Output:
            the number of matching records
        """
        self.cursExec(
            "SELECT Count(*) FROM entryCats WHERE idCat = :idCat", {"idCat": idCat}
        )
        return self.curs.fetchall()[0][0]

    def getOne(self, idCat, key):
        """Find connections between a category and an entry

        Parameters:
            idCat: the category id
            key: the bibtex key

        Output:
            the list of `sqlite3.Row` objects
                with all the matching connections
        """
        self.cursExec(
            "select * from entryCats where bibkey=:bibkey and idCat=:idCat\n",
            {"bibkey": key, "idCat": idCat},
        )
        return self.curs.fetchall()

    def getAll(self):
        """Get all the connections

        Output:
            the list of `sqlite3.Row` objects
        """
        self.cursExec("select * from entryCats")
        return self.curs.fetchall()

    def insert(self, idCat, key):
        """Create a new connection between a category and a bibtex entry

        Parameters:
            idCat: the category id (or a list)
            key: the bibtex key (or a list)

        Output:
            False if the connection is already present,
                the output of self.connExec otherwise
        """
        if isinstance(idCat, list):
            for q in idCat:
                self.insert(q, key)
        elif isinstance(key, list):
            for q in key:
                self.insert(idCat, q)
        else:
            if len(self.getOne(idCat, key)) == 0:
                pBLogger.debug(dstr.BibsCats.insert % (idCat, key))
                return self.connExec(
                    "INSERT into entryCats (bibkey, idCat) "
                    + "values (:bibkey, :idCat)",
                    {"bibkey": key, "idCat": idCat},
                )
            else:
                pBLogger.info(dstr.BibsCats.alreadyPresent % (idCat, key))
                return False

    def delete(self, idCat, key):
        """Delete a connection between a category and a bibtex entry

        Parameters:
            idCat: the category id (or a list)
            key: the bibtex key (or a list)

        Output:
            the output of self.connExec
        """
        if isinstance(idCat, list):
            for q in idCat:
                self.delete(q, key)
        elif isinstance(key, list):
            for q in key:
                self.delete(idCat, q)
        else:
            return self.connExec(
                "delete from entryCats where bibkey=:bibkey and idCat=:idCat",
                {"bibkey": key, "idCat": idCat},
            )

    def updateBibkey(self, new, old):
        """Update the connections affected by a bibkey change

        Parameters:
            new: the new bibtex key
            old: the old bibtex key

        Output:
            the output of self.connExec
        """
        pBLogger.info(dstr.BibsCats.updateKey % (old, new))
        query = "update entryCats set bibkey=:new where bibkey=:old\n"
        return self.connExec(query, {"new": new, "old": old})

    def askCats(self, keys):
        """Loop over the given bibtex keys and
        ask for the categories to be associated with them

        Parameters:
            keys: a single key or a list of bibtex keys
        """
        if not isinstance(keys, list):
            keys = [keys]
        for k in keys:
            string = six.moves.input(dstr.BibsCats.askInputCat % k)
            try:
                cats = self.literal_eval(string)
                self.insert(cats, k)
            except:
                pBLogger.warning(dstr.errorReadInput % string)

    def askKeys(self, cats):
        """Loop over the given categories and ask for
        the bibtex keys to be associated with them

        Parameters:
            cats: a single id or a list of categories
        """
        if not isinstance(cats, list):
            cats = [cats]
        for c in cats:
            string = six.moves.input(dstr.BibsCats.askInputBib % c)
            try:
                keys = self.literal_eval(string)
                self.insert(c, keys)
            except:
                pBLogger.warning(dstr.errorReadInput % string)


class CatsExps(PhysBiblioDBSub):
    """Functions for connecting categories and experiments"""

    def count(self):
        """obtain the number of rows in expCats"""
        self.cursExec("SELECT Count(*) FROM expCats")
        return self.curs.fetchall()[0][0]

    def countByExp(self, idExp):
        """Obtain the number of rows in expCats
        which are associated with a given experiment

        Parameters:
            idExp: the id of the experiment

        Output:
            the number of matching records
        """
        self.cursExec(
            "SELECT Count(*) FROM expCats WHERE idExp = :idExp", {"idExp": idExp}
        )
        return self.curs.fetchall()[0][0]

    def countByCat(self, idCat):
        """Obtain the number of rows in expCats
        which are associated with a given category

        Parameters:
            idCat: the id of the category

        Output:
            the number of matching records
        """
        self.cursExec(
            "SELECT Count(*) FROM expCats WHERE idCat = :idCat", {"idCat": idCat}
        )
        return self.curs.fetchall()[0][0]

    def getOne(self, idCat, idExp):
        """Find connections between a category and an experiment

        Parameters:
            idCat: the category id
            idExp: the experiment id

        Output:
            the list of `sqlite3.Row` objects
                with all the matching connections
        """
        self.cursExec(
            "select * from expCats where idExp=:idExp and idCat=:idCat",
            {"idExp": idExp, "idCat": idCat},
        )
        return self.curs.fetchall()

    def getAll(self):
        """Get all the connections

        Output:
            the list of `sqlite3.Row` objects
        """
        self.cursExec("select * from expCats")
        return self.curs.fetchall()

    def insert(self, idCat, idExp):
        """Create a new connection between a category and an experiment

        Parameters:
            idCat: the category id (or a list)
            idExp: the experiment id (or a list)

        Output:
            False if the connection is already present,
                the output of self.connExec otherwise
        """
        if isinstance(idCat, list):
            for q in idCat:
                self.insert(q, idExp)
        elif isinstance(idExp, list):
            for q in idExp:
                self.insert(idCat, q)
        else:
            if len(self.getOne(idCat, idExp)) == 0:
                pBLogger.debug(dstr.CatsExps.insert % (idCat, idExp))
                return self.connExec(
                    "INSERT into expCats (idExp, idCat) values (:idExp, :idCat)",
                    {"idExp": idExp, "idCat": idCat},
                )
            else:
                pBLogger.info(dstr.CatsExps.alreadyPresent % (idCat, idExp))
                return False

    def delete(self, idCat, idExp):
        """Delete a connection between a category and an experiment

        Parameters:
            idCat: the category id (or a list)
            idExp: the experiment id (or a list)

        Output:
            the output of self.connExec
        """
        if isinstance(idCat, list):
            for q in idCat:
                self.delete(q, idExp)
        elif isinstance(idExp, list):
            for q in idExp:
                self.delete(idCat, q)
        else:
            return self.connExec(
                "delete from expCats where idExp=:idExp and idCat=:idCat",
                {"idExp": idExp, "idCat": idCat},
            )

    def askCats(self, exps):
        """Loop over the given experiment ids and
        ask for the categories to be associated with them

        Parameters:
            exps: a single id or a list of experiment ids
        """
        if not isinstance(exps, list):
            exps = [exps]
        for e in exps:
            string = six.moves.input(dstr.CatsExps.askInputCat % e)
            try:
                cats = self.literal_eval(string)
                self.insert(cats, e)
            except:
                pBLogger.warning(dstr.errorReadInput % string)

    def askExps(self, cats):
        """Loop over the given category ids and
        ask for the experiments to be associated with them

        Parameters:
            cats: a single id or a list of category ids
        """
        if not isinstance(cats, list):
            cats = [cats]
        for c in cats:
            string = six.moves.input(dstr.CatsExps.askInputExp % c)
            try:
                exps = self.literal_eval(string)
                self.insert(c, exps)
            except:
                pBLogger.warning(dstr.errorReadInput % string)


class EntryExps(PhysBiblioDBSub):
    """Functions for connecting entries and experiments"""

    def count(self):
        """obtain the number of rows in EntryExps"""
        self.cursExec("SELECT Count(*) FROM entryExps")
        return self.curs.fetchall()[0][0]

    def countByExp(self, idExp):
        """Obtain the number of rows in EntryExps
        which are associated with a given experiment

        Parameters:
            idExp: the id of the experiment

        Output:
            the number of matching records
        """
        self.cursExec(
            "SELECT Count(*) FROM entryExps WHERE idExp = :idExp", {"idExp": idExp}
        )
        return self.curs.fetchall()[0][0]

    def getOne(self, key, idExp):
        """Find connections between an entry and an experiment

        Parameters:
            key: the bibtex key
            idExp: the experiment id

        Output:
            the list of `sqlite3.Row` objects
                with all the matching connections
        """
        self.cursExec(
            "select * from entryExps where idExp=:idExp and bibkey=:bibkey",
            {"idExp": idExp, "bibkey": key},
        )
        return self.curs.fetchall()

    def getAll(self):
        """Get all the connections

        Output:
            the list of `sqlite3.Row` objects
        """
        self.cursExec("select * from entryExps")
        return self.curs.fetchall()

    def insert(self, key, idExp):
        """Create a new connection between a bibtex entry and an experiment

        Parameters:
            key: the bibtex key (or a list)
            idExp: the experiment id (or a list)

        Output:
            False if the connection is already present,
                the output of self.connExec otherwise
        """
        if isinstance(key, list):
            for q in key:
                self.insert(q, idExp)
        elif isinstance(idExp, list):
            for q in idExp:
                self.insert(key, q)
        else:
            if len(self.getOne(key, idExp)) == 0:
                pBLogger.debug(dstr.BibsExps.insert % (key, idExp))
                if self.connExec(
                    "INSERT into entryExps (idExp, bibkey) "
                    + "values (:idExp, :bibkey)",
                    {"idExp": idExp, "bibkey": key},
                ):
                    for c in self.mainDB.cats.getByExp(idExp):
                        self.mainDB.catBib.insert(c["idCat"], key)
                    return True
            else:
                pBLogger.info(dstr.BibsExps.alreadyPresent % (key, idExp))
                return False

    def delete(self, key, idExp):
        """Delete a connection between a bibtex entry and an experiment

        Parameters:
            key: the bibtex key (or a list)
            idExp: the experiment id (or a list)

        Output:
            the output of self.connExec
        """
        if isinstance(key, list):
            for q in key:
                self.delete(q, idExp)
        elif isinstance(idExp, list):
            for q in idExp:
                self.delete(key, q)
        else:
            return self.connExec(
                "delete from entryExps where idExp=:idExp and bibkey=:bibkey",
                {"idExp": idExp, "bibkey": key},
            )

    def updateBibkey(self, new, old):
        """Update the connections affected by a bibkey change

        Parameters:
            new: the new bibtex key
            old: the old bibtex key

        Output:
            the output of self.connExec
        """
        pBLogger.info(dstr.BibsExps.updateKey % (old, new))
        query = "update entryExps set bibkey=:new where bibkey=:old\n"
        return self.connExec(query, {"new": new, "old": old})

    def askExps(self, keys):
        """Loop over the given bibtex keys and ask
        for the experiments to be associated with them

        Parameters:
            keys: a single key or a list of bibtex keys
        """
        if not isinstance(keys, list):
            keys = [keys]
        for k in keys:
            string = six.moves.input(dstr.BibsExps.askInputExp % k)
            try:
                exps = self.literal_eval(string)
                self.insert(k, exps)
            except:
                pBLogger.warning(dstr.errorReadInput % string)

    def askKeys(self, exps):
        """Loop over the given experiment ids
        and ask for the bibtexs to be associated with them

        Parameters:
            exps: a single id or a list of experiment ids
        """
        if not isinstance(exps, list):
            exps = [exps]
        for e in exps:
            string = six.moves.input(dstr.BibsExps.askInputBib % e)
            try:
                keys = self.literal_eval(string)
                self.insert(keys, e)
            except:
                pBLogger.warning(dstr.errorReadInput % string)


class Experiments(PhysBiblioDBSub):
    """Functions to manage the experiments"""

    def count(self):
        """obtain the number of experiments in the table"""
        self.cursExec("SELECT Count(*) FROM experiments")
        return self.curs.fetchall()[0][0]

    def insert(self, data):
        """Insert a new experiment

        Parameters:
            data: the dictionary with the experiment fields

        Output:
            the output of self.connExec
        """
        return self.connExec(
            "INSERT into experiments (name, comments, homepage, inspire)"
            + "values (:name, :comments, :homepage, :inspire)",
            data,
        )

    def update(self, data, idExp):
        """Update an existing experiment

        Parameters:
            data: the dictionary with the experiment fields
            idExp: the experiment id

        Output:
            the output of self.connExec
        """
        data["idExp"] = idExp
        query = (
            "replace into experiments ("
            + ", ".join(data.keys())
            + ") values (:"
            + ", :".join(data.keys())
            + ")\n"
        )
        return self.connExec(query, data)

    def updateField(self, idExp, field, value):
        """Update an existing experiment

        Parameters:
            idExp: the experiment id
            field: the field name
            value: the new field value

        Output:
            False if the field or the content is invalid,
                the output of self.connExec otherwise
        """
        pBLogger.info(dstr.Exps.updateField % (field, idExp))
        if (
            field in self.tableCols["experiments"]
            and field != "idExp"
            and value != ""
            and value is not None
        ):
            query = "update experiments set " + field + "=:field where idExp=:idExp\n"
            return self.connExec(query, {"field": value, "idExp": idExp})
        else:
            return False

    def delete(self, idExp):
        """Delete an experiment and all its connections

        Parameters:
            idExp: the experiment ID
        """
        if isinstance(idExp, list):
            for e in idExp:
                self.delete(e)
        else:
            pBLogger.info(dstr.Exps.useExp % idExp)
            self.cursExec("delete from experiments where idExp=?", (idExp,))
            self.cursExec("delete from expCats where idExp=?", (idExp,))
            self.cursExec("delete from entryExps where idExp=?", (idExp,))

    def getAll(self, orderBy="name", order="ASC"):
        """Get all the experiments

        Parameters:
            orderBy: the field used to order the output
            order: "ASC" or "DESC"

        Output:
            the list of `sqlite3.Row` objects
                with all the experiments in the database
        """
        self.cursExec("select * from experiments order by %s %s" % (orderBy, order))
        return self.curs.fetchall()

    def getByID(self, idExp):
        """Get experiment matching the given id

        Parameters:
            idExp: the experiment id

        Output:
            the list (len = 1) of `sqlite3.Row` objects
                with all the matching experiments
        """
        self.cursExec("select * from experiments where idExp=?", (idExp,))
        return self.curs.fetchall()

    def getDictByID(self, idExp):
        """Get experiment matching the given id,
        returns a standard dictionary

        Parameters:
            idExp: the experiment id

        Output:
            the list (len = 1) of `sqlite3.Row` objects
                with all the matching experiments
        """
        self.cursExec("select * from experiments where idExp=?", (idExp,))
        try:
            entry = self.curs.fetchall()[0]
            expDict = {}
            for i, k in enumerate(self.tableCols["experiments"]):
                expDict[k] = entry[i]
        except:
            pBLogger.info(dstr.Exps.errorExtract)
            expDict = None
        return expDict

    def getByName(self, name):
        """Get all the experiments matching a given name

        Parameters:
            name: the experiment name to be matched

        Output:
            the list of `sqlite3.Row` objects
                with all the matching experiments
        """
        self.cursExec("select * from experiments where name=?", (name,))
        return self.curs.fetchall()

    def filterAll(self, string):
        """Get all the experiments matching a given string

        Parameters:
            string: the string to be matched

        Output:
            the list of `sqlite3.Row` objects
                with all the matching experiments
        """
        string = "%" + string + "%"
        self.cursExec(
            "select * from experiments where name LIKE ? OR "
            + "comments LIKE ? OR homepage LIKE ? OR inspire LIKE ?",
            (string, string, string, string),
        )
        return self.curs.fetchall()

    def to_str(self, q):
        """Convert the experiment row in a string

        Parameters:
            q: the experiment record (sqlite3.Row or dict)
        """
        return "%3d: %-20s [%-40s] [%s]" % (
            q["idExp"],
            q["name"],
            q["homepage"],
            q["inspire"],
        )

    def printInCats(self, startFrom=0, sp=5 * " ", withDesc=False):
        """Prints the experiments under the corresponding categories

        Parameters:
            startFrom (int): where to start from
            sp (string): the spacing
            withDesc (boolean, default False):
                whether to print the description
        """
        cats = self.mainDB.cats.getAll()
        exps = self.getAll()
        catsHier = self.mainDB.cats.getHier(cats, startFrom=startFrom)
        showCat = {}
        for c in cats:
            showCat[c["idCat"]] = False

        def expString(idExp):
            """Get the string describing the experiment

            Parameters:
                idExp: the experiment id

            Output:
                the string
            """
            exp = [e for e in exps if e["idExp"] == idExp][0]
            if withDesc:
                return sp + "-> %s (%d) - %s" % (
                    exp["name"],
                    exp["idExp"],
                    exp["comments"],
                )
            else:
                return sp + "-> %s (%d)" % (exp["name"], exp["idExp"])

        def alphabetExp(listId):
            """Order experiments within a list in alphabetical order

            Parameters:
                listId: the list of experiment ids

            Output:
                the ordered list of id
            """
            listIn = [e for e in exps if e["idExp"] in listId]
            decorated = [(x["name"], x) for x in listIn]
            return [x[1]["idExp"] for x in sorted(decorated)]

        expCats = {}
        for (a, idE, idC) in self.mainDB.catExp.getAll():
            if idC not in expCats.keys():
                expCats[idC] = []
                showCat[idC] = True
            expCats[idC].append(idE)

        def printExpCats(ix, lev):
            """Prints the experiments in a given category

            Parameters:
                ix: the category id
                lev: the indentation level
            """
            try:
                for e in alphabetExp(expCats[ix]):
                    print(lev * sp + expString(e))
            except:
                pBLogger.exception(dstr.Exps.errorPrint)

        for l0 in cats_alphabetical(catsHier.keys(), self.mainDB):
            for l1 in cats_alphabetical(catsHier[l0].keys(), self.mainDB):
                if showCat[l1]:
                    showCat[l0] = True
                for l2 in cats_alphabetical(catsHier[l0][l1].keys(), self.mainDB):
                    if showCat[l2]:
                        showCat[l0] = True
                        showCat[l1] = True
                    for l3 in cats_alphabetical(
                        catsHier[l0][l1][l2].keys(), self.mainDB
                    ):
                        if showCat[l3]:
                            showCat[l0] = True
                            showCat[l1] = True
                            showCat[l2] = True
                        for l4 in cats_alphabetical(
                            catsHier[l0][l1][l2][l3].keys(), self.mainDB
                        ):
                            if showCat[l4]:
                                showCat[l0] = True
                                showCat[l1] = True
                                showCat[l2] = True
                                showCat[l2] = True
        for l0 in cats_alphabetical(catsHier.keys(), self.mainDB):
            if showCat[l0]:
                print(catString(l0, self.mainDB))
                printExpCats(l0, 1)
            for l1 in cats_alphabetical(catsHier[l0].keys(), self.mainDB):
                if showCat[l1]:
                    print(sp + catString(l1, self.mainDB))
                    printExpCats(l1, 2)
                for l2 in cats_alphabetical(catsHier[l0][l1].keys(), self.mainDB):
                    if showCat[l2]:
                        print(2 * sp + catString(l2, self.mainDB))
                        printExpCats(l2, 3)
                    for l3 in cats_alphabetical(
                        catsHier[l0][l1][l2].keys(), self.mainDB
                    ):
                        if showCat[l3]:
                            print(3 * sp + catString(l3, self.mainDB))
                            printExpCats(l3, 4)
                        for l4 in cats_alphabetical(
                            catsHier[l0][l1][l2][l3].keys(), self.mainDB
                        ):
                            if showCat[l4]:
                                print(4 * sp + catString(l4, self.mainDB))
                                printExpCats(l4, 5)

    def printAll(self, exps=None, orderBy="name", order="ASC"):
        """Print all the experiments

        Parameters:
            exps: the experiments (if None it gets
                all the experiments in the database)
            orderBy: the field to use for ordering the experiments,
                if they are not given
            order: which order, if exps is not given
        """
        if exps is None:
            exps = self.getAll(orderBy=orderBy, order=order)
        for q in exps:
            print(self.to_str(q))

    def getByCat(self, idCat):
        """Get all the experiments associated with a given category

        Parameters:
            idCat: the id of the category to be matched

        Output:
            the list of `sqlite3.Row` objects
                with all the matching experiments
        """
        self.cursExec(
            "select * from experiments "
            + "join expCats on experiments.idExp=expCats.idExp "
            + "where expCats.idCat=?",
            (idCat,),
        )
        return self.curs.fetchall()

    def getByEntry(self, key):
        """Get all the experiments matching a given bibtex entry

        Parameters:
            key: the key of the bibtex to be matched

        Output:
            the list of `sqlite3.Row` objects
                with all the matching experiments
        """
        self.cursExec(
            "select * from experiments "
            + "join entryExps on experiments.idExp=entryExps.idExp "
            + "where entryExps.bibkey=?",
            (key,),
        )
        return self.curs.fetchall()

    def getByEntries(self, keys):
        """Get all the experiments matching a list of given bibtex entries

        Parameters:
            keys: the keys of the bibtex to be matched

        Output:
            the list of `sqlite3.Row` objects
                with all the matching experiments
        """
        self.cursExec(
            "select * from experiments "
            + "join entryExps on experiments.idExp=entryExps.idExp "
            + "where "
            + " or ".join(["entryExps.bibkey=?" for k in keys])
            + "\n",
            keys,
        )
        return self.curs.fetchall()


class Entries(PhysBiblioDBSub):
    """Functions to manage the bibtex entries"""

    searchPossibleTypes = {
        "exp_paper": {"desc": dstr.Bibs.experimental},
        "lecture": {"desc": dstr.Bibs.lecture},
        "phd_thesis": {"desc": dstr.Bibs.phdth},
        "review": {"desc": dstr.Bibs.review},
        "proceeding": {"desc": dstr.Bibs.proceeding},
        "book": {"desc": dstr.Bibs.book},
    }
    searchOperators = {
        "text": {
            dstr.Bibs.Search.opTContains: "like",
            dstr.Bibs.Search.opTExact: "=",
            dstr.Bibs.Search.opTNotCont: "not like",
            dstr.Bibs.Search.opTDifferent: "!=",
        },
        "catexp": {
            dstr.Bibs.Search.opCEAll: "",
            dstr.Bibs.Search.opCEOne: "",
            dstr.Bibs.Search.opCSub: "",
            # dstr.Bibs.Search.opCENone: "",
        },
    }
    searchFields = {
        "text": [
            "bibtex",
            "bibkey",
            "arxiv",
            "doi",
            "year",
            "firstdate",
            "pubdate",
            "comments",
            "abstract",
        ]
    }
    validReplaceFields = {
        "old": [
            "arxiv",
            "doi",
            "year",
            "author",
            "title",
            "journal",
            "number",
            "volume",
            "published",
        ],
        "new": [
            "arxiv",
            "doi",
            "year",
            "author",
            "title",
            "journal",
            "number",
            "volume",
        ],
    }

    def __init__(self, parent):
        """Call parent __init__ and create an empty lastFetched & c."""
        PhysBiblioDBSub.__init__(self, parent)
        self.lastFetched = []
        self.lastQuery = "select * from entries limit 10"
        self.lastVals = ()
        self.lastInserted = []
        self.runningReplace = False
        self.getArxivFieldsFlag = False
        self.runningLoadAndInsert = False
        self.runningCleanBibtexs = False
        self.runningOAIUpdates = False
        self.newKey = None
        try:
            self.fetchCurs = self.conn.cursor()
        except AttributeError:
            self.fetchCurs = None

    def fetchCursor(self):
        """Return the cursor"""
        return self.fetchCurs

    def count(self):
        """obtain the number of entries in the table"""
        self.cursExec("SELECT Count(*) FROM entries")
        return self.curs.fetchall()[0][0]

    def delete(self, key):
        """Delete an entry and all its connections

        Parameters:
            key: the bibtex key (or a list)
        """
        if isinstance(key, list):
            for k in key:
                self.delete(k)
        else:
            pBLogger.info(dstr.Bibs.delete % key)
            self.cursExec("delete from entries where bibkey=?", (key,))
            self.cursExec("delete from entryCats where bibkey=?", (key,))
            self.cursExec("delete from entryExps where bibkey=?", (key,))

    def completeFetched(self, fetched_in):
        """Use the database content to add additional fields
        ("bibtexDict", "published", "author", "title",
        "journal", "volume", "number", "pages") to the query results.

        Parameters:
            fetched_in: the list of `sqlite3.Row` objects
                returned by the last query

        Output:
            a dictionary with the original and the new fields
        """
        fetched_out = []
        fetched_keys = set([])
        for el in fetched_in:
            tmp = {}
            for k in el.keys():
                tmp[k] = el[k]
            if el["bibdict"] is not None:
                if (
                    isinstance(el["bibdict"], six.string_types)
                    and el["bibdict"].strip() != ""
                    and el["bibdict"].strip() != "{}"
                ):
                    tmp["bibtexDict"] = ast.literal_eval(el["bibdict"].strip())
                    tmp["bibdict"] = dict(tmp["bibtexDict"])
                elif isinstance(el["bibdict"], dict):
                    tmp["bibtexDict"] = tmp["bibdict"]
            else:
                try:
                    tmp["bibtexDict"] = (
                        bibtexparser.bparser.BibTexParser(common_strings=True)
                        .parse(el["bibtex"])
                        .entries[0]
                    )
                except IndexError:
                    tmp["bibtexDict"] = {}
                    tmp["bibdict"] = {}
                except ParseException:
                    pBLogger.warning(
                        dstr.Bibs.errorParseBibtex % el["bibtex"],
                        exc_info=True,
                    )
                    tmp["bibtexDict"] = {}
                    tmp["bibdict"] = {}
                self.updateField(el["bibkey"], "bibdict", "%s" % tmp["bibtexDict"])
            try:
                tmp["year"] = tmp["bibtexDict"]["year"]
            except KeyError:
                if tmp["year"] is None:
                    tmp["year"] = ""
            for fi in ["title", "journal", "volume", "number", "pages"]:
                try:
                    tmp[fi] = tmp["bibtexDict"][fi]
                except KeyError:
                    tmp[fi] = ""
            try:
                tmp["published"] = " ".join(
                    [tmp["journal"], tmp["volume"], "(%s)" % tmp["year"], tmp["pages"]]
                )
                if tmp["published"] == "  () ":
                    tmp["published"] = ""
            except KeyError:
                tmp["published"] = ""
            try:
                author = tmp["bibtexDict"]["author"]
                if author.count(" and ") > pbConfig.params["maxAuthorNames"] - 1:
                    author = author[: author.index(" and ")] + " et al."
                tmp["author"] = author
            except KeyError:
                tmp["author"] = ""
            if tmp["bibkey"] not in fetched_keys:
                fetched_keys.add(tmp["bibkey"])
                fetched_out.append(tmp)
        return fetched_out

    def fetchFromLast(self, doFetch=True):
        """Fetch entries using the last saved query

        Parameter:
            doFetch (boolean, default True):
                use self.curs.fetchall and store all the rows in a list.
                Set to False to directly use the iterator on self.curs.

        Output:
            self
        """
        if doFetch:
            cursor = self.curs
        else:
            cursor = self.fetchCurs
        try:
            if len(self.lastVals) > 0:
                cursor.execute(self.lastQuery, self.lastVals)
            else:
                cursor.execute(self.lastQuery)
        except:
            pBLogger.warning(
                dstr.bibs.errorQueryFailed % (self.lastQuery, self.lastVals)
            )
        if doFetch:
            fetched_in = cursor.fetchall()
            self.lastFetched = self.completeFetched(fetched_in)
        return self

    def fetchFromDict(
        self,
        queryFields=[],
        defaultConnection="and",
        orderBy="firstdate",
        orderType="ASC",
        limitTo=None,
        limitOffset=None,
        saveQuery=True,
        doFetch=True,
    ):
        """Fetch entries using a number of criterions

        Parameters:
            queryFields: a list of dictionaries containing
                the type, criterion and content
                for each search requirement.
                Each dictionary must have the following keys:
                    "type": either "Text", "Categories", "Experiments",
                        "Marks" or "Type"
                    "field": the sub-field to match.
                        Ignored for some types.
                    "logical": the logical operator connecting
                        to the previous requirements
                    "operator": depending on the type, different values
                        are allowed (e.g., "exact match" or "contains")
                    "content": the string match, or
                        the index of category/experiment,
                        or the list of types/marks
            defaultConnection: "and" (default) or "or",
                the default logical operator for multiple field matches
            orderBy: the name of the field according to which
                the results must be ordered
            orderType: "ASC" (default) or "DESC"
            limitTo (int or None): maximum number of results.
                If None, do not limit
            limitOffset (int or None): where to start in the ordered list.
                If None, use 0
            saveQuery (boolean, default True):
                if True, save the query for future reuse
            doFetch (boolean, default True):
                use self.curs.fetchall and store all the rows in a list.
                Set to False to directly use the iterator on self.curs.

        Output:
            self
        """

        def getQueryStr(txt, operator):
            """Return a match string, with trailing % if needed

            Parameters:
                txt: the text to match
                operator: the operator to use

            Output:
                a string
            """
            return "%%%s%%" % txt if "like" in operator else txt

        def catExpStrings(idxs, operator, tabName, fieldName):
            """Returns the string and the data needed
            to perform a search using categories and/or experiments

            Parameters:
                idxs: the list of indices
                operator: the operator to use
                tabName: the name of the table to consider
                fieldName: the name of the primary key in the considered table

            Output:
                joinStr, whereStr, valsTmp:
                    the string containing the `join` structure,
                    the one containing the `where` conditions
                    and a tuple with the values of the fields
            """
            joinStr = ""
            whereStr = ""
            valsTmp = tuple()
            if isinstance(idxs, list):
                idxs = [str(i) for i in idxs]
            else:
                idxs = [str(idxs)]
            if operator == dstr.Bibs.Search.opCSub and fieldName == "idCat":
                idxs = self.mainDB.cats.getAllCatsInTree(idxs)
                operator = dstr.Bibs.Search.opCEOne
            if len(idxs) > 1:
                if operator == dstr.Bibs.Search.opCEOne:
                    joinStr += " left join %s on entries.bibkey=%s.bibkey" % (
                        tabName,
                        tabName,
                    )
                    whereStr += "(%s)" % "or".join(
                        [" %s.%s = ? " % (tabName, fieldName) for q in idxs]
                    )
                    valsTmp = tuple(idxs)
                elif operator == dstr.Bibs.Search.opCEAll:
                    joinStr += " ".join(
                        [
                            " left join %s %s%d on entries.bibkey=%s%d.bibkey"
                            % (tabName, tabName, iC, tabName, iC)
                            for iC, q in enumerate(idxs)
                        ]
                    )
                    whereStr += (
                        "("
                        + " and ".join(
                            [
                                "%s%d.%s = ?" % (tabName, iC, fieldName)
                                for iC, q in enumerate(idxs)
                            ]
                        )
                        + ")"
                    )
                    valsTmp = tuple(idxs)
                # elif operator == "none of the following":
                # joinStr += " ".join(
                # [" left join %s %s%d on entries.bibkey=%s%d.bibkey"%(
                # tabName, tabName, iC, tabName, iC) for iC, q in \
                # enumerate(idxs)])
                # whereStr += "(" + " and ".join(
                # ["%s%d.%s != ?"%(tabName, iC, fieldName) for iC, q in \
                # enumerate(idxs)]) + ")"
                # valsTmp = tuple(idxs)
                else:
                    pBLogger.warning(dstr.Bibs.Search.invalidOperator % operator)
            elif len(idxs) == 1:
                joinStr += " left join %s on entries.bibkey=%s.bibkey" % (
                    tabName,
                    tabName,
                )
                whereStr += "%s.%s = ? " % (tabName, fieldName)
                valsTmp = tuple(idxs)
            else:
                pBLogger.warning(dstr.Bibs.Search.invalidIds % idxs)
            return joinStr, whereStr, valsTmp

        first = True
        vals = ()
        query = "select * from entries "
        joinQ = ""
        whereQ = ""
        prependTab = (
            "entries."
            if any([e["type"] in ["Categories", "Experiments"] for e in queryFields])
            else ""
        )
        jC, wC, vC, jE, wE, vE = ["", "", tuple(), "", "", tuple()]

        for di in queryFields:
            if di["logical"] is None or di["logical"].lower() not in ["and", "or"]:
                di["logical"] = defaultConnection
            if (
                (di["type"] in ["Categories", "Experiments"] and di["content"] == "")
                or (
                    di["type"] == "Text"
                    and (
                        di["content"] == ""
                        and di["operator"]
                        not in [
                            dstr.Bibs.Search.opTDifferent,
                            "!=",
                            dstr.Bibs.Search.opTExact,
                            "=",
                        ]
                    )
                )
                or (
                    di["type"] in ["Marks", "Type"]
                    and (not isinstance(di["content"], list) or len(di["content"]) != 1)
                )
            ):
                pBLogger.warning(
                    dstr.Bibs.Search.invalidContent % (di["content"], di["type"])
                )
                continue
            if first:
                first = False
                di["logical"] = ""
            if di["type"] == "Text":
                if di["operator"] in self.searchOperators["text"]:
                    di["operator"] = self.searchOperators["text"][di["operator"]]
                elif di["operator"] not in [
                    v for v in self.searchOperators["text"].values()
                ]:
                    pBLogger.warning(dstr.Bibs.Search.invalidOperator % di["operator"])
                    continue
                if di["field"] in self.tableCols["entries"]:
                    whereQ += "%s %s%s %s ? " % (
                        di["logical"],
                        prependTab,
                        di["field"],
                        di["operator"],
                    )
                    vals += (getQueryStr(di["content"], di["operator"]),)
                else:
                    pBLogger.warning(dstr.Bibs.Search.invalidField % di["field"])
                    continue
            elif di["type"] == "Categories":
                jC, wC, vC = catExpStrings(
                    di["content"], di["operator"], "entryCats", "idCat"
                )
                joinQ += jC if "join entryCats" not in joinQ else ""
                whereQ += "%s %s " % (di["logical"], wC)
                vals += vC
            elif di["type"] == "Experiments":
                jE, wE, vE = catExpStrings(
                    di["content"], di["operator"], "entryExps", "idExp"
                )
                joinQ += jE if "join entryExps" not in joinQ else ""
                whereQ += "%s %s " % (di["logical"], wE)
                vals += vE
            elif di["type"] == "Marks":
                if "any" in di["content"]:
                    di["operator"] = "!="
                    di["content"] = [""]
                if di["operator"] is None or di["operator"] not in ["=", "!=", "like"]:
                    di["operator"] = "like"
                whereQ += "%s %s%s %s ? " % (
                    di["logical"],
                    prependTab,
                    "marks",
                    di["operator"],
                )
                vals += (getQueryStr(di["content"][0], di["operator"]),)
            elif di["type"] == "Type":
                whereQ += "%s %s%s %s ? " % (
                    di["logical"],
                    prependTab,
                    di["content"][0],
                    "=",
                )
                vals += ("1",)

        query += joinQ if joinQ != "" else ""
        query += (" where %s" % whereQ) if whereQ != "" else ""
        query += " order by %s%s" % (prependTab, orderBy)
        query += (" %s" % orderType) if orderBy else ""
        if limitTo is not None:
            query += " LIMIT %s" % (str(limitTo))
        if limitOffset is not None:
            if limitTo is None:
                query += " LIMIT 100000"
            query += " OFFSET %s" % (str(limitOffset))
        if saveQuery and doFetch:
            self.lastQuery = query
            self.lastVals = vals
        if doFetch:
            cursor = self.curs
        else:
            cursor = self.fetchCurs
        pBLogger.info(dstr.Bibs.useQueryVals % (query, vals))
        try:
            if len(vals) > 0:
                cursor.execute(query, vals)
            else:
                cursor.execute(query)
        except:
            pBLogger.exception(dstr.Bibs.errorQueryFailed % (query, vals))
            return self
        if doFetch:
            fetched_in = self.curs.fetchall()
            self.lastFetched = self.completeFetched(fetched_in)
        return self

    def fetchAll(
        self,
        params=None,
        connection="and",
        operator="=",
        orderBy="firstdate",
        orderType="ASC",
        limitTo=None,
        limitOffset=None,
        saveQuery=True,
        doFetch=True,
    ):
        """Fetch entries using a number of criterions.
        Simpler than self.fetchFromDict.

        Parameters:
            params (a dictionary or None): if a dictionary,
                it must contain the structure "field": "value"
            connection: "and"/"or", default "and"
            operator: "=" for exact match (default),
                "like" for containing match
            orderBy: the name of the field according
                to which the results are ordered
            orderType: "ASC" (default) or "DESC"
            limitTo (int or None): maximum number of results.
                If None, do not limit
            limitOffset (int or None): where to start in the ordered list.
                If None, use 0
            saveQuery (boolean, default True):
                if True, save the query for future reuse
            doFetch (boolean, default True):
                use self.curs.fetchall and store all the rows in a list.
                Set to False to directly use the iterator on self.curs.

        Output:
            self
        """
        query = "select * from entries "
        vals = ()
        if connection.strip() != "and" and connection.strip() != "or":
            pBLogger.warning(dstr.Bibs.invalidLogicalOp % connection)
            connection = "and"
        if operator.strip() != "=" and operator.strip() != "like":
            pBLogger.warning(dstr.Bibs.invalidComparisonOp % operator)
            operator = "="
        if orderType.strip() != "ASC" and orderType.strip() != "DESC":
            pBLogger.warning(dstr.Bibs.invalidOrdering % orderType)
            orderType = "ASC"
        if params and len(params) > 0:
            query += " where "
            first = True
            for k, v in params.items():
                if isinstance(v, list):
                    for v1 in v:
                        if first:
                            first = False
                        else:
                            query += " %s " % connection
                        query += k + " %s " % operator + " ? "
                        if operator.strip() == "like" and "%" not in v1:
                            v1 = "%%%s%%" % v1
                        vals += (v1,)
                else:
                    if first:
                        first = False
                    else:
                        query += " %s " % connection
                    query += k + " %s " % operator + "? "
                    if operator.strip() == "like" and "%" not in v:
                        v = "%%%s%%" % v
                    vals += (v,)
        query += " order by " + orderBy + " " + orderType if orderBy else ""
        if limitTo is not None:
            query += " LIMIT %s" % (str(limitTo))
            if limitOffset is not None:
                query += " OFFSET %s" % (str(limitOffset))
        if saveQuery and doFetch:
            self.lastQuery = query
            self.lastVals = vals
        if doFetch:
            cursor = self.curs
        else:
            cursor = self.fetchCurs
        try:
            if len(vals) > 0:
                cursor.execute(query, vals)
            else:
                cursor.execute(query)
        except OperationalError as err:
            if str(err) == "database is locked":
                if not self.sendDBIsLocked():
                    pBLogger.exception(dstr.opErDbOpen)
            else:
                pBLogger.exception(dstr.errorConnection % (err, query))
        except (ProgrammingError, DatabaseError, InterfaceError) as err:
            pBLogger.exception(dstr.Bibs.errorQueryFailed % (query, vals))
        if doFetch:
            fetched_in = self.curs.fetchall()
            self.lastFetched = self.completeFetched(fetched_in)
        return self

    def getAll(
        self,
        params=None,
        connection="and",
        operator="=",
        orderBy="firstdate",
        orderType="ASC",
        limitTo=None,
        limitOffset=None,
        saveQuery=True,
    ):
        """Use self.fetchAll and returns the dictionary of fetched entries

        Parameters: see self.fetchAll

        Output:
            a dictionary
        """
        return self.fetchAll(
            params=params,
            connection=connection,
            operator=operator,
            orderBy=orderBy,
            orderType=orderType,
            limitTo=limitTo,
            limitOffset=limitOffset,
            saveQuery=saveQuery,
            doFetch=True,
        ).lastFetched

    def fetchByBibkey(self, bibkey, saveQuery=True):
        """Use self.fetchAll with a match on the bibtex key
        and returns the dictionary of fetched entries

        Parameters:
            bibkey: the bibtex key to match (or a list)
            saveQuery (boolean, default True):
                whether to save the query or not

        Output:
            self
        """
        if isinstance(bibkey, list):
            return self.fetchAll(
                params={"bibkey": bibkey}, connection="or", saveQuery=saveQuery
            )
        else:
            return self.fetchAll(params={"bibkey": bibkey}, saveQuery=saveQuery)

    def getByBibkey(self, bibkey, saveQuery=True):
        """Use self.fetchByBibkey and returns
        the dictionary of fetched entries

        Parameters: see self.fetchByBibkey

        Output:
            a dictionary
        """
        return self.fetchByBibkey(bibkey, saveQuery=saveQuery).lastFetched

    def fetchByKey(self, key, saveQuery=True):
        """Use self.fetchAll with a match
        on the bibtex key in the bibkey, bibtex or old_keys fields
        and returns the dictionary of fetched entries

        Parameters:
            key: the bibtex key to match (or a list)
            saveQuery (boolean, default True):
                whether to save the query or not

        Output:
            self
        """
        if isinstance(key, list):
            strings = ["%%%s%%" % q for q in key]
            return self.fetchAll(
                params={"bibkey": strings, "old_keys": strings},
                connection="or ",
                operator=" like ",
                saveQuery=saveQuery,
            )
        else:
            return self.fetchAll(
                params={"bibkey": "%%%s%%" % key, "old_keys": "%%%s%%" % key},
                connection="or ",
                operator=" like ",
                saveQuery=saveQuery,
            )

    def getByKey(self, key, saveQuery=True):
        """Use self.fetchByKey and returns
        the dictionary of fetched entries

        Parameters: see self.fetchByKey

        Output:
            a dictionary
        """
        return self.fetchByKey(key, saveQuery=saveQuery).lastFetched

    def fetchByBibtex(self, string, saveQuery=True):
        """Use self.fetchAll with a match on the bibtex content
        and returns the dictionary of fetched entries

        Parameters:
            string: the string to match in the bibtex (or a list)
            saveQuery (boolean, default True):
                whether to save the query or not

        Output:
            self
        """
        if isinstance(string, list):
            return self.fetchAll(
                params={"bibtex": ["%%%s%%" % q for q in string]},
                connection="or",
                operator=" like ",
                saveQuery=saveQuery,
            )
        else:
            return self.fetchAll(
                params={"bibtex": "%%%s%%" % string},
                operator=" like ",
                saveQuery=saveQuery,
            )

    def getByBibtex(self, string, saveQuery=True):
        """Use self.fetchByBibtex and returns
        the dictionary of fetched entries

        Parameters: see self.fetchByBibtex

        Output:
            a dictionary
        """
        return self.fetchByBibtex(string, saveQuery=saveQuery).lastFetched

    def getField(self, key, field):
        """Extract the content of one field
        from a entry in the database, searched by bibtex key

        Parameters:
            key: the bibtex key
            field: the field name

        Output:
            False if the search failed,
            the output of self.getByBibkey otherwise
        """
        try:
            value = self.getByBibkey(key, saveQuery=False)[0][field]
        except IndexError:
            pBLogger.warning(dstr.Bibs.errorGFNoElement % (key, field))
            return False
        except KeyError:
            pBLogger.warning(dstr.Bibs.errorGFNoField % (key, field))
            return False
        if field == "bibdict" and isinstance(value, six.string_types):
            try:
                return ast.literal_eval(value)
            except SyntaxError:
                pBLogger.error(dstr.Bibs.errorReadBibdict % value)
                return value
        else:
            return value

    def toDataDict(self, key):
        """Convert the entry bibtex into a dictionary

        Parameters:
            key: the bibtex key

        Output:
            the output of self.prepareInsert
        """
        return self.prepareInsert(self.getField(key, "bibtex"))

    def getAdsUrl(self, key):
        """Get the adsabs url for the entry,
        if it has something in the ads field

        Parameters:
            key: the bibtex key

        Output:
            a string
        """
        url = self.getField(key, "ads")
        return pbConfig.adsUrl + url if url != "" and url else False

    def getArxivUrl(self, key, urlType="abs"):
        """Get the arxiv.org url for the entry,
        if it has something in the arxiv field

        Parameters:
            key: the bibtex key
            urlType: "abs" or "pdf"

        Output:
            a string
        """
        url = self.getField(key, "arxiv")
        return (
            pbConfig.arxivUrl + "/" + urlType + "/" + url
            if (url != "" and url)
            else False
        )

    def getDoiUrl(self, key):
        """Get the doi.org url for the entry,
        if it has something in the doi field

        Parameters:
            key: the bibtex key

        Output:
            a string
        """
        url = self.getField(key, "doi")
        return pbConfig.doiUrl + url if url != "" and url else False

    def insert(self, data):
        """Insert an entry

        Parameters:
            data: a dictionary with the data fields to be inserted

        Output:
            the output of self.connExec
        """
        return self.connExec(
            "INSERT into entries ("
            + ", ".join(self.tableCols["entries"])
            + ") values (:"
            + ", :".join(self.tableCols["entries"])
            + ")\n",
            data,
        )

    def insertFromBibtex(self, bibtex):
        """A function that wraps self.insert(self.prepareInsert(bibtex))

        Parameters:
            bibtex: the string containing the bibtex code
                for the given element

        Output:
            the output of self.insert
        """
        return self.insert(self.prepareInsert(bibtex))

    def update(self, data, oldkey):
        """Update an entry

        Parameters:
            data: a dictionary with the new field contents
            oldKey: the bibtex key of the entry to be updated

        Output:
            the output of self.connExec
        """
        data["bibkey"] = oldkey
        return self.connExec(
            "replace into entries ("
            + ", ".join(data.keys())
            + ") values (:"
            + ", :".join(data.keys())
            + ")\n",
            data,
        )

    def prepareInsert(
        self,
        bibtex,
        bibkey=None,
        inspire=None,
        arxiv=None,
        ads=None,
        scholar=None,
        doi=None,
        isbn=None,
        year=None,
        link=None,
        comments=None,
        old_keys=None,
        crossref=None,
        exp_paper=None,
        lecture=None,
        phd_thesis=None,
        review=None,
        proceeding=None,
        book=None,
        marks=None,
        firstdate=None,
        pubdate=None,
        noUpdate=None,
        abstract=None,
        number=None,
    ):
        """Convert a bibtex into a dictionary,
        eventually using also additional info

        Mandatory parameter:
            bibtex: the bibtex string for the entry
                (more than one is allowed, only one will be considered,
                see Optional argument>number)

        Optional fields:
            number (default None, converted to 0):
                the index of the desired entry
                in the list of bibtex strings
            the value for the fields in the database table:
                bibkey, inspire, arxiv, ads, scholar, doi, isbn,
                year, link, comments, old_keys, crossref, exp_paper,
                lecture, phd_thesis, review, proceeding, book, marks,
                firstdate, pubdate, noUpdate, abstract

        Output:
            a dictionary with all the field values for self.insert
        """
        from physbiblio.webimport.arxiv import getYear

        data = {}
        if number is None:
            number = 0
        try:
            elements = (
                bibtexparser.bparser.BibTexParser(common_strings=True)
                .parse(bibtex)
                .entries
            )
        except ParseException:
            pBLogger.info(dstr.Bibs.errorParseBib)
            data["bibkey"] = ""
            return data
        if len(elements) == 0:
            pBLogger.info(dstr.noElsFound)
            data["bibkey"] = ""
            return data
        element = elements[number]
        try:
            if element["ID"] is None:
                element["ID"] = ""
            if bibkey:
                element["ID"] = bibkey
            data["bibkey"] = element["ID"]
        except KeyError:
            pBLogger.info(dstr.Bibs.errorParseBib)
            data["bibkey"] = ""
            return data
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = []
        db.entries.append(element)
        data["bibtex"] = self.rmBibtexComments(
            self.rmBibtexACapo(pbWriter.write(db).strip())
        )
        # most of the fields have standard behaviour:
        for k in ["abstract", "crossref", "doi", "isbn"]:
            data[k] = (
                locals()[k]
                if locals()[k]
                else element[k]
                if k in element.keys()
                else None
            )
        for k in ["ads", "comments", "inspire", "old_keys", "scholar"]:
            data[k] = locals()[k] if locals()[k] else None
        for k in [
            "book",
            "exp_paper",
            "lecture",
            "noUpdate",
            "phd_thesis",
            "proceeding",
            "review",
        ]:
            data[k] = 1 if locals()[k] else 0
        for k in ["marks", "pubdate"]:
            data[k] = locals()[k] if locals()[k] else ""
        # arxiv
        data["arxiv"] = (
            arxiv
            if arxiv
            else element["arxiv"]
            if "arxiv" in element.keys()
            else element["eprint"]
            if "eprint" in element.keys()
            else ""
        )
        # year
        data["year"] = None
        if year:
            data["year"] = year
        else:
            try:
                data["year"] = element["year"]
            except KeyError:
                try:
                    data["year"] = getYear(data["arxiv"])
                except KeyError:
                    data["year"] = None
        # link
        if link:
            data["link"] = link
        else:
            data["link"] = ""
            try:
                if data["arxiv"] is not None and data["arxiv"] != "":
                    data["link"] = pbConfig.arxivUrl + "/abs/" + data["arxiv"]
            except KeyError:
                pass
            try:
                if data["doi"] is not None and data["doi"] != "":
                    data["link"] = pbConfig.doiUrl + data["doi"]
            except KeyError:
                pass
        # firstdate
        data["firstdate"] = (
            firstdate if firstdate else datetime.date.today().strftime("%Y-%m-%d")
        )
        # bibtex dict
        try:
            tmpBibDict = (
                bibtexparser.bparser.BibTexParser(common_strings=True)
                .parse(data["bibtex"])
                .entries[0]
            )
        except IndexError:
            tmpBibDict = {}
        except ParseException:
            pBLogger.warning(
                dstr.Bibs.errorParseBibtex % data["bibtex"],
                exc_info=True,
            )
            tmpBibDict = {}
        data["bibdict"] = "%s" % tmpBibDict
        # if some fields are empty, use bibtex info
        if arxiv == "":
            if "arxiv" in tmpBibDict.keys() and tmpBibDict["arxiv"] != "":
                arxiv = tmpBibDict["arxiv"]
            elif "eprint" in tmpBibDict.keys() and tmpBibDict["eprint"] != "":
                arxiv = tmpBibDict["eprint"]
        for f in ["year", "doi", "isbn"]:
            if f in tmpBibDict.keys() and tmpBibDict[f] != "":
                data[f] = tmpBibDict[f]
        return data

    def prepareUpdateByKey(self, key_old, key_new):
        """Get an entry bibtex and prepare an update,
        using the new bibtex from another database entry

        Parameters:
            key_old: the key of the old entry
            key_new: the key of the new entry

        Output:
            the output of self.prepareInsert(u)
        """
        u = self.prepareUpdate(
            self.getField(key_old, "bibtex"), self.getField(key_new, "bibtex")
        )
        return self.prepareInsert(u)

    def prepareUpdateByBibtex(self, key_old, bibtex_new):
        """Get an entry bibtex and prepare an update,
        using the new bibtex passed as an argument

        Parameters:
            key_old: the key of the old entry
            bibtex_new: the new bibtex

        Output:
            the output of self.prepareInsert(u)
        """
        u = self.prepareUpdate(self.getField(key_old, "bibtex"), bibtex_new)
        return self.prepareInsert(u)

    def prepareUpdate(self, bibtexOld, bibtexNew):
        """Prepare the update of an entry, comparing two bibtexs.
        Uses the fields from the old bibtex,
        adds the ones in the new bibtex and updates the repeated ones

        Parameters:
            bibtexOld: the old bibtex
            bibtexNew: the new bibtex

        Output:
            the joined bibtex
        """
        try:
            elementOld = (
                bibtexparser.bparser.BibTexParser(common_strings=True)
                .parse(bibtexOld)
                .entries[0]
            )
            elementNew = (
                bibtexparser.bparser.BibTexParser(common_strings=True)
                .parse(bibtexNew)
                .entries[0]
            )
        except ParseException:
            pBLogger.warning(dstr.Bibs.parsingExcPU % (bibtexOld, bibtexNew))
            return ""
        except IndexError:
            pBLogger.warning(dstr.Bibs.emptyBibtex % (bibtexOld, bibtexNew))
            return ""
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = []
        keep = elementOld
        for k in elementNew.keys():
            if k not in elementOld.keys():
                keep[k] = elementNew[k]
            elif (
                elementNew[k]
                and elementNew[k] != elementOld[k]
                and k != "bibtex"
                and k != "ID"
            ):
                keep[k] = elementNew[k]
        db.entries.append(keep)
        return pbWriter.write(db)

    def updateInspireID(self, string, key=None, number=None):
        """Use inspire websearch module to get and
        update the inspire ID of an entry.
        If the given string is cannot be matched, uses arxiv and doi
        fields from the database (if the key is valid)

        Parameters:
            string: the string so be searched
            key (optional): the bibtex key of the database entry
            number (optional): the index of the desired element
                in the list of results

        Output:
            the id or False if empty
        """
        newid = physBiblioWeb.webSearch["inspire"].retrieveInspireID(
            string, number=number
        )
        if key is None:
            key = string
        if newid != "":
            if self.connExec(
                "update entries set inspire=:inspire where bibkey=:bibkey\n",
                {"inspire": newid, "bibkey": key},
            ):
                return newid
            else:
                pBLogger.warning(dstr.Bibs.errorUIIDGeneric)
                return False
        else:
            doi = self.getField(key, "doi")
            if isinstance(doi, six.string_types) and doi.strip() != "":
                newid = physBiblioWeb.webSearch["inspire"].retrieveInspireID(
                    doi,
                    number=0,
                    isDoi=True,
                )
                if newid != "":
                    if self.connExec(
                        "update entries set inspire=:inspire "
                        + "where bibkey=:bibkey\n",
                        {"inspire": newid, "bibkey": key},
                    ):
                        return newid
                    else:
                        pBLogger.warning(dstr.Bibs.errorUIIDDOI)
            arxiv = self.getField(key, "arxiv")
            if isinstance(arxiv, six.string_types) and arxiv.strip() != "":
                newid = physBiblioWeb.webSearch["inspire"].retrieveInspireID(
                    arxiv,
                    number=0,
                    isArxiv=True,
                )
                if newid != "":
                    if self.connExec(
                        "update entries set inspire=:inspire "
                        + "where bibkey=:bibkey\n",
                        {"inspire": newid, "bibkey": key},
                    ):
                        return newid
                    else:
                        pBLogger.warning(dstr.Bibs.errorUIIDArxiv)
            return False

    def updateField(self, key, field, value, verbose=1):
        """Update a single field of an entry

        Parameters:
            key: the bibtex key
            field: the field name
            value: the new value of the field
            verbose (int): increase output level

        Output:
            the output of self.connExec or False if the field is invalid
        """
        if verbose > 0:
            pBLogger.info(dstr.Bibs.updateField % (field, key))
        if field == "bibtex" and value != "" and value is not None:
            try:
                tmpBibDict = (
                    bibtexparser.bparser.BibTexParser(common_strings=True)
                    .parse(value)
                    .entries[0]
                )
            except IndexError:
                tmpBibDict = {}
            except ParseException:
                pBLogger.warning(
                    dstr.Bibs.errorParseBibtex % value,
                    exc_info=True,
                )
                tmpBibDict = {}
            self.updateField(key, "bibdict", "%s" % tmpBibDict, verbose=verbose)
        if (
            field in self.tableCols["entries"]
            and field != "bibkey"
            and value is not None
        ):
            query = "update entries set " + field + "=:field where bibkey=:bibkey\n"
            if verbose > 1:
                pBLogger.info("%s" % ((query, field, value)))
            return self.connExec(query, {"field": value, "bibkey": key})
        else:
            if verbose > 1:
                pBLogger.warning(dstr.Bibs.errorField % (key, field, value))
            return False

    def updateBibkey(self, oldKey, newKey):
        """Update the bibtex key of an entry

        Parameters:
            oldKey: the old bibtex key
            newKey: the new bibtex key

        Output:
            the output of self.connExec or False if some errors occurred
        """
        pBLogger.info(dstr.Bibs.updateBibkey % (oldKey, newKey))
        try:
            query = "update entries set bibkey=:new where bibkey=:old\n"
            if self.connExec(query, {"new": newKey, "old": oldKey}):
                entry = self.getByBibkey(newKey, saveQuery=False)[0]
                try:
                    oldkeys = entry["old_keys"].split(",")
                    if oldkeys == [""]:
                        oldkeys = []
                except AttributeError:
                    oldkeys = []
                self.updateField(newKey, "old_keys", ",".join(oldkeys + [oldKey]))
                try:
                    from physbiblio.pdf import pBPDF

                    pBPDF.renameFolder(oldKey, newKey)
                except Exception:
                    pBLogger.exception(dstr.errorRename)
                query = "update entryCats set bibkey=:new where bibkey=:old\n"
                if self.connExec(query, {"new": newKey, "old": oldKey}):
                    query = "update entryExps set bibkey=:new where bibkey=:old\n"
                    return self.connExec(query, {"new": newKey, "old": oldKey})
                else:
                    return False
            else:
                return False
        except:
            pBLogger.warning(dstr.Bibs.errorUpdateBib, exc_info=True)
            return False

    def getDailyInfoFromOAI(self, date1=None, date2=None):
        """Use inspire OAI webinterface to get updated information
        on the entries between two dates

        Parameters:
            date1, date2: the two dates defining
                the time interval to consider
        """
        if date1 is None or not re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", date1):
            date1 = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
        if date2 is None or not re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", date2):
            date2 = datetime.date.today().strftime("%Y-%m-%d")
        yren, monen, dayen = date1.split("-")
        yrst, monst, dayst = date2.split("-")
        pBLogger.info(dstr.Bibs.callOAIDates % (date1, date2))
        date1 = datetime.datetime(int(yren), int(monen), int(dayen))
        date2 = datetime.datetime(int(yrst), int(monst), int(dayst))
        entries = physBiblioWeb.webSearch["inspireoai"].retrieveOAIUpdates(date1, date2)
        changed = []
        for e in entries:
            try:
                key = e["bibkey"]
                pBLogger.info(key)
                old = self.getByBibkey(key, saveQuery=False)
                if len(old) > 0 and old[0]["noUpdate"] == 0:
                    outcome, bibtex = physBiblioWeb.webSearch[
                        "inspireoai"
                    ].updateBibtex(e, old[0]["bibtex"])
                    if not outcome:
                        pBLogger.warning(dstr.Bibs.errorOAIEntryG)
                        continue
                    e["bibtex"] = self.rmBibtexComments(
                        self.rmBibtexACapo(bibtex.strip())
                    )
                    for [o, d] in physBiblioWeb.webSearch["inspireoai"].correspondences:
                        if e[o] != old[0][d] and e[o] != None:
                            if o == "bibtex":
                                pBLogger.info(dstr.Bibs.oaiInfoL % d)
                                pBLogger.info(dstr.Bibs.oaiOld % old[0][d])
                                pBLogger.info(dstr.Bibs.oaiNew % e[o])
                            else:
                                pBLogger.info(dstr.Bibs.oaiInfoS % (d, old[0][d], e[o]))
                            self.updateField(key, d, e[o], verbose=0)
                            if len(changed) == 0 or changed[-1] != key:
                                changed.append(key)
            except:
                pBLogger.exception(dstr.Bibs.errorOAIEntryDet % (e["id"], e))
        pBLogger.info(dstr.Bibs.oaiChanged % (len(changed), changed))
        pBLogger.info(dstr.Bibs.oaiDone)

    def updateInfoFromOAI(
        self,
        inspireID,
        bibtex=None,
        verbose=0,
        readConferenceTitle=False,
        reloadAll=False,
        originalKey=None,
    ):
        """Use inspire OAI to retrieve the info for a single entry

        Parameters:
            inspireID (string): the id of the entry in inspires.
                If is not a number, assume it is the bibtex key
            bibtex: see physBiblio.webimport.inspireoai.retrieveOAIData
            verbose: increase level of verbosity
            reloadAll (boolean, default False):
                reload the entire content,
                without trying to simply update the existing one
            originalKey (optional): the previous key of the entry
                (useful when reloadAll is True)

        Output:
            True if successful, or False if there were errors
        """
        if inspireID == "" or not inspireID:
            pBLogger.error(dstr.Bibs.iidEmptyID)
            return False
        if not inspireID.isdigit():  # assume it's a key instead of the inspireID
            originalKey = inspireID
            inspireID = self.getField(inspireID, "inspire")
            try:
                inspireID.isdigit()
            except AttributeError:
                pBLogger.error(dstr.Bibs.iidWrongType % inspireID)
                return False
            if not inspireID.isdigit():
                pBLogger.error(dstr.Bibs.iidWrongVal % inspireID)
                return False
        if not reloadAll:
            result = physBiblioWeb.webSearch["inspireoai"].retrieveOAIData(
                inspireID,
                bibtex=bibtex,
                verbose=verbose,
                readConferenceTitle=readConferenceTitle,
            )
        else:
            result = physBiblioWeb.webSearch["inspireoai"].retrieveOAIData(
                inspireID, verbose=verbose, readConferenceTitle=readConferenceTitle
            )
        if verbose > 1:
            pBLogger.info(result)
        if not result:
            pBLogger.error(dstr.Bibs.iidEmptyRecord % inspireID)
            return False
        try:
            key = result["bibkey"] if originalKey is None else originalKey
            if key != result["bibkey"]:
                self.updateBibkey(key, result["bibkey"])
                key = result["bibkey"]
                self.newKey = result["bibkey"]
            if not reloadAll:
                old = self.getByBibkey(key, saveQuery=False)
            else:
                old = [
                    {
                        k: ""
                        for x, k in physBiblioWeb.webSearch[
                            "inspireoai"
                        ].correspondences
                    }
                ]
            if verbose > 1:
                pBLogger.info("%s, %s" % (key, old))
            if len(old) > 0:
                for [o, d] in physBiblioWeb.webSearch["inspireoai"].correspondences:
                    try:
                        if verbose > 0:
                            pBLogger.info("%s = %s (%s)" % (d, result[o], old[0][d]))
                        if result[o] != old[0][d]:
                            if o == "bibtex" and result[o] is not None:
                                self.updateField(
                                    key,
                                    d,
                                    self.rmBibtexComments(
                                        self.rmBibtexACapo(result[o].strip())
                                    ),
                                    verbose=0,
                                )
                            else:
                                self.updateField(key, d, result[o], verbose=0)
                    except KeyError:
                        pBLogger.exception(dstr.Bibs.iidKeyError % (o, d))
            if verbose > 0:
                pBLogger.info(dstr.Bibs.iidSaved % inspireID)
        except KeyError:
            pBLogger.exception(dstr.Bibs.iidStMissing % inspireID)
            return False
        return True

    def updateFromOAI(self, entry, verbose=0):
        """Update an entry from inspire OAI.
        If inspireID is missing, look for it before

        Parameters:
            entry (string): the inspire ID or an identifier
                of the entry to consider (also a list is accepted)
            verbose: increase level of verbosity

        Output:
            for a single entry, the output of self.updateInfoFromOAI
            for a list of entries, a list with the output
                of self.updateInfoFromOAI for each entry
        """
        if isinstance(entry, list):
            output = []
            for e in entry:
                output.append(self.updateFromOAI(e, verbose=verbose))
            return output
        elif entry.isdigit():
            return self.updateInfoFromOAI(entry, verbose=verbose)
        else:
            inspireID = self.getField(entry, "inspire")
            if inspireID is not None:
                return self.updateInfoFromOAI(inspireID, verbose=verbose)
            else:
                inspireID = self.updateInspireID(entry, entry)
                return self.updateInfoFromOAI(inspireID, verbose=verbose)

    def replaceInBibtex(self, old, new):
        """Replace a string with a new one,
        in all the matching bibtex entries of the table

        Parameters:
            old: the old string
            new: the new string

        Output:
            the list of keys of the matching bibtex entries
            or False if self.connExec failed
        """
        self.lastQuery = "SELECT * FROM entries WHERE bibtex LIKE :match"
        match = "%" + "%s" % old + "%"
        self.lastVals = {"match": match}
        self.cursExec(self.lastQuery, self.lastVals)
        self.lastFetched = self.completeFetched(self.curs.fetchall())
        keys = [k["bibkey"] for k in self.lastFetched]
        pBLogger.info(dstr.Bibs.replaceText, keys)
        if self.connExec(
            "UPDATE entries SET bibtex = replace( bibtex, :old, :new ) "
            + "WHERE bibtex LIKE :match",
            {"old": old, "new": new, "match": match},
        ):
            return keys
        else:
            return False

    def replace(
        self,
        fiOld,
        fiNews,
        old,
        news,
        entries=None,
        regex=False,
        lenEntries=1,
        pbMax=None,
        pbVal=None,
    ):
        """Replace a string with a new one, in the given field
        of the (previously) selected bibtex entries

        Parameters:
            fiOld: the field where the string to match is taken from
            fiNews: the list of new fields where to insert
                the replaced string
            old: the old string to replace
            news: the list of new strings
            entries (None or a list): the entries to consider.
                If None, use self.getAll
            regex (boolean, default False):
                whether to use regular expression
                for matching and replacing
            lenEntries (default 1): if `entries` is passed, this must be
                the length of `entries`
            pbMax (callable, optional): a function to set the maximum
                of a progress bar in the GUI, if possible
            pbVal (callable, optional): a function to set the value
                of a progress bar in the GUI, if possible

        Output:
            success, changed, failed:
                the lists of entries that were
                successfully processed, changed or produced errors
        """

        def singleReplace(line, new, previous=None):
            """Replace the old with the new string in the given line

            Parameters:
                line: the string where to match and replace
                new: the new string
                previous (default None): the previous content of the field
                    (useful when using regex and complex replaces)

            Output:
                the processed line or previous
                    (if regex and no matches are found)
            """
            if regex:
                reg = re.compile(old)
                if reg.match(line):
                    line = reg.sub(new, line)
                else:
                    line = previous
            else:
                line = line.replace(old, new)
            return line

        if not isinstance(fiNews, list) or not isinstance(news, list):
            pBLogger.warning(dstr.Bibs.replaceInvalidNew)
            return [], [], []
        if entries is None:
            tot = len(self.fetchAll(saveQuery=False).lastFetched)
            self.fetchAll(saveQuery=False, doFetch=False)
            iterator = self.fetchCursor()
        else:
            iterator = entries
            tot = lenEntries
        success = []
        changed = []
        failed = []
        self.runningReplace = True
        pBLogger.info(dstr.Bibs.replaceProcessTot % tot)
        if tot < 1:
            tot = 1
        try:
            pbMax(tot)
        except TypeError:
            pass
        for ix, entry in enumerate(iterator):
            try:
                pbVal(ix + 1)
            except TypeError:
                pass
            if not self.runningReplace:
                continue
            if not "bibtexDict" in entry.keys():
                entry = self.completeFetched([entry])[0]
            pBLogger.info(
                dstr.Bibs.replaceProcessProgr
                % (ix + 1, tot, 100.0 * (ix + 1) / tot, entry["bibkey"])
            )
            try:
                if (
                    not fiOld in entry["bibtexDict"].keys()
                    and not fiOld in entry.keys()
                ):
                    raise KeyError(
                        dstr.Bibs.replaceMissingField % (fiOld, entry["bibkey"])
                    )
                if fiOld in entry["bibtexDict"].keys():
                    before = entry["bibtexDict"][fiOld]
                elif fiOld in entry.keys():
                    before = entry[fiOld]
                bef = []
                aft = []
                for fiNew, new in zip(fiNews, news):
                    if (
                        not fiNew in entry["bibtexDict"].keys()
                        and not fiNew in entry.keys()
                    ):
                        raise KeyError(
                            dstr.Bibs.replaceMissingField % (fiNew, entry["bibkey"])
                        )
                    if fiNew in entry["bibtexDict"].keys():
                        bef.append(entry["bibtexDict"][fiNew])
                        after = singleReplace(
                            before, new, previous=entry["bibtexDict"][fiNew]
                        )
                        aft.append(after)
                        entry["bibtexDict"][fiNew] = after
                        db = bibtexparser.bibdatabase.BibDatabase()
                        db.entries = []
                        db.entries.append(entry["bibtexDict"])
                        entry["bibtex"] = self.rmBibtexComments(
                            self.rmBibtexACapo(pbWriter.write(db).strip())
                        )
                        self.updateField(
                            entry["bibkey"], "bibtex", entry["bibtex"], verbose=0
                        )
                    if fiNew in entry.keys():
                        bef.append(entry[fiNew])
                        after = singleReplace(before, new, previous=entry[fiNew])
                        aft.append(after)
                        self.updateField(entry["bibkey"], fiNew, after, verbose=0)
            except KeyError:
                pBLogger.exception(dstr.Bibs.replaceError)
                failed.append(entry["bibkey"])
            else:
                success.append(entry["bibkey"])
                if any(b != a for a, b in zip(aft, bef)):
                    changed.append(entry["bibkey"])
        pBLogger.info(dstr.doneE)
        return success, changed, failed

    def rmBibtexComments(self, bibtex):
        """Remove comments and empty lines from a bibtex

        Parameters:
            bibtex: the bibtex to process

        Output:
            the processed bibtex
        """
        output = ""
        for l in bibtex.splitlines():
            lx = l.strip()
            if len(lx) > 0 and lx[0] != "%":
                output += l + "\n"
        return output.strip()

    def rmBibtexACapo(self, bibtex):
        """Remove line breaks in the fields of a bibtex

        Parameters:
            bibtex: the bibtex to process

        Output:
            the processed bibtex
        """
        output = ""
        db = bibtexparser.bibdatabase.BibDatabase()
        tmp = {}
        try:
            element = (
                bibtexparser.bparser.BibTexParser(common_strings=True)
                .parse(bibtex)
                .entries[0]
            )
        except (IndexError, ParseException):
            pBLogger.warning(dstr.Bibs.cannotParse % bibtex)
            return ""
        for k, v in element.items():
            try:
                tmp[k] = v.replace("\n", " ")
            except AttributeError:
                pBLogger.warning(dstr.Bibs.wrongTypeField % (k, v))
                tmp[k] = v
        db.entries = [tmp]
        return pbWriter.write(db)

    def getFieldsFromArxiv(self, bibkey, fields, pbMax=None, pbVal=None):
        """Use arxiv.org to retrieve more fields for the entry

        Parameters:
            bibkey: the bibtex key of the entry
            fields: the fields to be updated
                using information from arxiv.org
            pbMax (callable, optional): a function to set the maximum
                of a progress bar in the GUI, if possible
            pbVal (callable, optional): a function to set the value
                of a progress bar in the GUI, if possible

        Output:
            False if some error occurred,
            True if a single entry has been successfully processed
            or
            the lists of successfully processed entryes
                and failures when considering a list
        """
        if isinstance(bibkey, list):
            tot = len(bibkey)
            self.getArxivFieldsFlag = True
            success = []
            fail = []
            pBLogger.info(dstr.Bibs.gffaProcessTot % tot)
            try:
                pbMax(tot)
            except TypeError:
                pass
            for ix, k in enumerate(bibkey):
                arxiv = str(self.getField(k, "arxiv"))
                try:
                    pbVal(ix + 1)
                except TypeError:
                    pass
                if self.getArxivFieldsFlag and arxiv.strip() != "":
                    pBLogger.info(
                        dstr.Bibs.gffaProcessProgr
                        % (ix + 1, tot, 100.0 * (ix + 1) / tot, arxiv)
                    )
                    result = self.getFieldsFromArxiv(k, fields)
                    if result:
                        success.append(k)
                    else:
                        fail.append(k)
            pBLogger.info(dstr.Bibs.gffaDone)
            pBLogger.info(
                dstr.Bibs.gffaSummary % (len(success + fail), len(fail), fail)
            )
            return success, fail
        if not isinstance(fields, list):
            fields = [fields]
        bibtex = self.getField(bibkey, "bibtex")
        arxiv = str(self.getField(bibkey, "arxiv"))
        if arxiv == "False" or arxiv == "None" or arxiv.strip() == "":
            return False
        try:
            arxivBibtex, arxivDict = physBiblioWeb.webSearch["arxiv"].retrieveUrlAll(
                arxiv, searchType="id", fullDict=True
            )
            tmp = (
                bibtexparser.bparser.BibTexParser(common_strings=True)
                .parse(bibtex)
                .entries[0]
            )
            for k in fields:
                try:
                    tmp[k] = arxivDict[k]
                except KeyError:
                    pass
            if "authors" in fields:
                try:
                    authors = tmp["authors"].split(" and ")
                    if len(authors) > pbConfig.params["maxAuthorSave"]:
                        start = 1 if "collaboration" in authors[0] else 0
                        tmp["author"] = " and ".join(
                            authors[start : start + pbConfig.params["maxAuthorSave"]]
                            + ["others"]
                        )
                except KeyError:
                    pass
            db = bibtexparser.bibdatabase.BibDatabase()
            db.entries = [tmp]
            bibtex = self.rmBibtexComments(
                self.rmBibtexACapo(pbWriter.write(db).strip())
            )
            self.updateField(bibkey, "bibtex", bibtex)
            return True
        except Exception:
            pBLogger.exception(dstr.Bibs.gffaFailed)
            return False

    def loadAndInsert(
        self,
        entry,
        method="inspire",
        imposeKey=None,
        number=None,
        returnBibtex=False,
        childProcess=False,
        pbMax=None,
        pbVal=None,
    ):
        """Read a list of keywords and look for inspire contents,
        then load in the database all the info

        Parameters:
            entry: the bibtex key or a list
            method: "inspire" (default) or any other supported method
                from the webimport subpackage or "bibtex"
            imposeKey (default None): if a string, the bibtex key
                to use with the imported entry
            number (default None): if not None, the index
                of the wanted entry in the list of results
            returnBibtex (boolean, default False): whether to return
                the bibtex of the entry
            childProcess (boolean, default False): if True, do not reset
                the self.lastInserted (used when recursively called)
            pbMax (callable, optional): a function to set the maximum
                of a progress bar in the GUI, if possible
            pbVal (callable, optional): a function to set the value
                of a progress bar in the GUI, if possible

        Output:
            False if some error occurred,
            True if successful but returnBibtex is False
                or entry is not a list,
            the bibtex field if entry is a single element
                and returnBibtex is True
        """
        requireAll = False

        def printExisting(entry, existing):
            """Print a message if the entry already exists,
            returns True or the bibtex field depending
            on the value of returnBibtex

            Parameters:
                entry: the entry key
                existing: the list of dictionaries returned
                    by self.getByBibkey

            Output:
                the bibtex field if returnBibtex is True, True otherwise
            """
            pBLogger.info(dstr.Bibs.alreadyExisting % entry)
            if returnBibtex:
                return existing[0]["bibtex"]
            else:
                return True

        def returnListIfSub(a, out):
            """If the original list contains sublists,
            return a list with all the elements in the list
            and each sublist

            Parameters:
                a: the original list
                out: the previous output,
                    which will be recursively increased

            Output:
                the output, increased with the new elements
            """
            if isinstance(a, list):
                for el in a:
                    out = returnListIfSub(el, out)
                return out
            else:
                out += [a]
                return out

        if not childProcess:
            self.lastInserted = []
        if entry is not None and not isinstance(entry, list):
            existing = self.getByBibkey(entry, saveQuery=False)
            exist = len(existing) > 0
            for f in ["arxiv", "doi"]:
                try:
                    temp = self.fetchAll(params={f: entry}, saveQuery=False).lastFetched
                    exist = exist or (len(temp) > 0)
                    existing += temp
                except KeyError:
                    pBLogger.debug("Error", exc_info=True)
            if existing:
                return printExisting(entry, existing)
            if method == "bibtex":
                try:
                    db = bibtexparser.bibdatabase.BibDatabase()
                    db.entries = (
                        bibtexparser.bparser.BibTexParser(common_strings=True)
                        .parse(entry)
                        .entries
                    )
                    e = self.rmBibtexComments(
                        self.rmBibtexACapo(pbWriter.write(db).strip())
                    )
                except ParseException:
                    pBLogger.exception(dstr.Bibs.laiReadError % entry)
                    return False
            else:
                try:
                    e = physBiblioWeb.webSearch[method].retrieveUrlAll(entry)
                except KeyError:
                    pBLogger.error(dstr.Bibs.laiInvalidMethod % method)
                    return False
            if [a.startswith("@") for a in e.split("\n")].count(True) > 1:
                if number is not None:
                    requireAll = True
                else:
                    pBLogger.warning(dstr.Bibs.laiMismatch % e)
                    return False
            kwargs = {}
            if requireAll:
                kwargs["number"] = number
            if imposeKey is not None and imposeKey.strip() != "":
                kwargs["bibkey"] = imposeKey
            data = self.prepareInsert(e, **kwargs)
            key = data["bibkey"]
            if key.strip() == "":
                pBLogger.error(dstr.Bibs.laiEmptyKey % entry)
                return False
            existing = self.getByBibkey(key, saveQuery=False)
            exist = len(existing) > 0
            for f in ["arxiv", "doi"]:
                try:
                    if (
                        data[f] is not None
                        and isinstance(data[f], six.string_types)
                        and data[f].strip() != ""
                    ):
                        temp = self.fetchAll(
                            params={f: data[f]}, saveQuery=False
                        ).lastFetched
                        exist = exist or (len(temp) > 0)
                        existing += temp
                except (AttributeError, KeyError):
                    pBLogger.debug("Error", exc_info=True)
            if existing:
                return printExisting(key, existing)
            pBLogger.info(dstr.Bibs.laiNewKey % key)
            if pbConfig.params["fetchAbstract"] and data["arxiv"] != "":
                arxivBibtex, arxivDict = physBiblioWeb.webSearch[
                    "arxiv"
                ].retrieveUrlAll(data["arxiv"], searchType="id", fullDict=True)
                data["abstract"] = arxivDict["abstract"]
            try:
                self.insert(data)
            except:
                pBLogger.exception(dstr.Bibs.laiFailed % entry)
                return False
            try:
                self.mainDB.catBib.insert(pbConfig.params["defaultCategories"], key)
                if method == "inspire":
                    if not requireAll:
                        eid = self.updateInspireID(entry, key)
                    else:
                        eid = self.updateInspireID(entry, key, number=number)
                    self.updateInfoFromOAI(eid)
                elif method == "isbn":
                    self.setBook(key)
                if "inproceeding" in data["bibtex"].lower():
                    self.setProceeding(key)
                if "phdthesis" in data["bibtex"].lower():
                    self.setPhdThesis(key)
                pBLogger.info(dstr.Bibs.laiInserted)
                self.lastInserted.append(key)
                if returnBibtex:
                    return e
                else:
                    return True
            except:
                pBLogger.warning(dstr.failedComplete % entry)
                return False
        elif entry is not None and isinstance(entry, list):
            failed = []
            entry = returnListIfSub(entry, [])
            self.runningLoadAndInsert = True
            tot = len(entry)
            pBLogger.info(dstr.Bibs.laiProcessTot % tot)
            try:
                pbMax(tot)
            except TypeError:
                pass
            for ie, e in enumerate(entry):
                try:
                    pbVal(ie + 1)
                except TypeError:
                    pass
                if isinstance(e, float):
                    e = str(e)
                if self.runningLoadAndInsert:
                    pBLogger.info(
                        dstr.Bibs.laiProcessProgr
                        % (ie + 1, tot, 100.0 * (ie + 1) / tot, e)
                    )
                    if not self.loadAndInsert(e, childProcess=True):
                        failed.append(e)
            if len(self.lastInserted) > 0:
                pBLogger.info(dstr.Bibs.laiImported % ", ".join(self.lastInserted))
            if len(failed) > 0:
                pBLogger.warning(dstr.Bibs.laiErrors % (", ".join(failed)))
            return True
        else:
            pBLogger.error(dstr.Bibs.laiInvalidArgs)
            return False

    def loadAndInsertWithCats(
        self,
        entry,
        method="inspire",
        imposeKey=None,
        number=None,
        returnBibtex=False,
        childProcess=False,
    ):
        """Load the entries, then ask for their categories.
        Uses self.loadAndInsert and self.mainDB.catBib.askCats

        Parameters: see self.loadAndInsert
        """
        self.loadAndInsert(
            entry,
            method=method,
            imposeKey=imposeKey,
            number=number,
            returnBibtex=returnBibtex,
            childProcess=childProcess,
        )
        for key in self.lastInserted:
            self.mainDB.catBib.delete(pbConfig.params["defaultCategories"], key)
        self.mainDB.catBib.askCats(self.lastInserted)

    def parseSingleBibtex(self, text, errors=[], verbose=False):
        """Parse the text corresponding to an entry and returns
        the list of parsed entries from `bibtexparser`.
        If an exception occurs, return an empty list

        Parameter:
            text: the text to be processed
            errors (default []): a list that contains the errors.
                It should add to the existing list if passed
            verbose (default False): if True, print some more messages

        Output:
            a list with the parsed entries
        """
        if verbose:
            pBLogger.debug(dstr.Bibs.psbProcess % text)
        if text.strip() == "":
            if verbose:
                pBLogger.warning(dstr.Bibs.psbEmpty)
            return []
        bp = bibtexparser.bparser.BibTexParser(common_strings=True)
        try:
            entries = bp.parse(text).entries
        except ParseException:
            errors.append(text)
            pBLogger.exception(dstr.Bibs.psbError % text)
            entries = []
        return entries

    def parseAllBibtexs(self, fullBibText, errors=[], verbose=False, messageEvery=100):
        """Parse the text containing several bibtex entries and return
        the list of parsed entries from `bibtexparser`.
        It should deal well with a number of errors

        Parameter:
            fullBibText: the text to be processed
            errors (default []): a list that contains the errors.
                It should add to the existing list if passed
            verbose (default False): if True, print some more messages
            messageEvery (default 100): print a message
                showing the reading progress every N found entries

        Output:
            a list of parsed entries
        """
        bibText = ""
        elements = []
        found = 0
        pBLogger.info(dstr.Bibs.pabStart)
        for il, line in enumerate(fullBibText):
            if line.startswith("@") and il > 0:
                elements += self.parseSingleBibtex(
                    bibText, errors=errors, verbose=verbose
                )
                found += 1
                if found % messageEvery == 0:
                    pBLogger.info(dstr.Bibs.pabRead % found)
                bibText = line
            else:
                bibText += line
        elements += self.parseSingleBibtex(bibText, errors=errors, verbose=verbose)
        pBLogger.info(dstr.Bibs.pabFound % len(elements))
        return elements

    def importFromBib(self, filename, completeInfo=True, pbMax=None, pbVal=None):
        """Read a .bib file and add the contained entries in the database

        Parameters:
            filename: the name of the .bib file
            completeInfo (boolean, default True): use the bibtex key
                and other fields to look for more information online
            pbMax (callable, optional): a function to set the maximum
                of a progress bar in the GUI, if possible
            pbVal (callable, optional): a function to set the value
                of a progress bar in the GUI, if possible
        """

        def printExisting(entry):
            """Print a message when the entry is
            already present in the database

            Parameters:
                entry: the entry key
            """
            pBLogger.info(dstr.Bibs.ifbExist % entry)

        self.lastInserted = []
        exist = []
        errors = []

        pBLogger.info(dstr.Bibs.ifbFromFile % filename)
        with open(filename) as r:
            fullBibText = r.readlines()
        elements = self.parseAllBibtexs(fullBibText, errors=errors, verbose=True)
        db = bibtexparser.bibdatabase.BibDatabase()
        self.importFromBibFlag = True
        tot = len(elements)
        pBLogger.info(dstr.Bibs.ifbProcessTot % tot)
        try:
            pbMax(tot)
        except TypeError:
            pass
        for ie, e in enumerate(elements):
            try:
                pbVal(ie + 1)
            except TypeError:
                pass
            if self.importFromBibFlag and e != []:
                db.entries = [e]
                bibtex = self.rmBibtexComments(
                    self.rmBibtexACapo(pbWriter.write(db).strip())
                )
                data = self.prepareInsert(bibtex)
                key = data["bibkey"]
                pBLogger.info(
                    dstr.Bibs.ifbProcessProgr
                    % (ie + 1, tot, 100.0 * (ie + 1.0) / tot, key)
                )
                existing = self.getByBibkey(key, saveQuery=False)
                if existing:
                    printExisting(key)
                    exist.append(key)
                elif key.strip() == "":
                    pBLogger.warning(dstr.Bibs.ifbEmptyKey)
                    errors.append(key)
                else:
                    if (
                        completeInfo
                        and pbConfig.params["fetchAbstract"]
                        and data["arxiv"] != ""
                    ):
                        arxivBibtex, arxivDict = physBiblioWeb.webSearch[
                            "arxiv"
                        ].retrieveUrlAll(data["arxiv"], searchType="id", fullDict=True)
                        data["abstract"] = arxivDict["abstract"]
                    pBLogger.info(dstr.Bibs.ifbNewKey % key)
                    if not self.insert(data):
                        pBLogger.warning(dstr.Bibs.ifbFailed % key)
                        errors.append(key)
                    else:
                        self.mainDB.catBib.insert(
                            pbConfig.params["defaultCategories"], key
                        )
                        try:
                            if completeInfo:
                                eid = self.updateInspireID(key)
                                self.updateInfoFromOAI(eid)
                            pBLogger.info(dstr.Bibs.ifbInserted)
                            self.lastInserted.append(key)
                        except Exception:
                            pBLogger.exception(dstr.failedComplete % key)
                            errors.append(key)
        pBLogger.info(
            dstr.Bibs.ifbCompleteSummary
            % (len(elements), len(exist), len(self.lastInserted), len(errors))
        )

    def setBook(self, key, value=1):
        """Set (or unset) the book field for an entry

        Parameters:
            key: the bibtex key
            value: 1 or 0

        Output:
            the output of self.updateField
        """
        if isinstance(key, list):
            for q in key:
                self.setBook(q, value)
        else:
            return self.updateField(key, "book", value, 0)

    def setLecture(self, key, value=1):
        """Set (or unset) the Lecture field for an entry

        Parameters:
            key: the bibtex key
            value: 1 or 0

        Output:
            the output of self.updateField
        """
        if isinstance(key, list):
            for q in key:
                self.setLecture(q, value)
        else:
            return self.updateField(key, "lecture", value, 0)

    def setPhdThesis(self, key, value=1):
        """Set (or unset) the PhD thesis field for an entry

        Parameters:
            key: the bibtex key
            value: 1 or 0

        Output:
            the output of self.updateField
        """
        if isinstance(key, list):
            for q in key:
                self.setPhdThesis(q, value)
        else:
            return self.updateField(key, "phd_thesis", value, 0)

    def setProceeding(self, key, value=1):
        """Set (or unset) the proceeding field for an entry

        Parameters:
            key: the bibtex key
            value: 1 or 0

        Output:
            the output of self.updateField
        """
        if isinstance(key, list):
            for q in key:
                self.setProceeding(q, value)
        else:
            return self.updateField(key, "proceeding", value, 0)

    def setReview(self, key, value=1):
        """Set (or unset) the review field for an entry

        Parameters:
            key: the bibtex key
            value: 1 or 0

        Output:
            the output of self.updateField
        """
        if isinstance(key, list):
            for q in key:
                self.setReview(q, value)
        else:
            return self.updateField(key, "review", value, 0)

    def setNoUpdate(self, key, value=1):
        """Set (or unset) the noUpdate field for an entry

        Parameters:
            key: the bibtex key
            value: 1 or 0

        Output:
            the output of self.updateField
        """
        if isinstance(key, list):
            for q in key:
                self.setNoUpdate(q, value)
        else:
            return self.updateField(key, "noUpdate", value, 0)

    def printAllBibtexs(self, entriesIn=None):
        """Print the bibtex codes for all the entries
        (or for a given subset)

        Parameters:
            entriesIn: the list of entries to print.
                If None, use self.lastFetched or self.getAll.
        """
        total = 0

        def _print(i, e):
            print(dstr.Bibs.pabProgr % (i, e["bibtex"]))

        if entriesIn is not None:
            for i, e in enumerate(entriesIn):
                _print(i, e)
                total += 1
        else:
            self.fetchAll(orderBy="firstdate", doFetch=False)
            for i, e in enumerate(self.fetchCursor()):
                _print(i, e)
                total += 1
        pBLogger.info(dstr.Bibs.elementsFound % total)

    def printAllBibkeys(self, entriesIn=None):
        """Print the bibtex keys for all the entries
        (or for a given subset)

        Parameters:
            entriesIn: the list of entries to print.
                If None, use self.lastFetched or self.getAll.
        """
        total = 0

        def _print(i, e):
            print(dstr.Bibs.pabProgr % (i, e["bibkey"]))

        if entriesIn is not None:
            for i, e in enumerate(entriesIn):
                _print(i, e)
                total += 1
        else:
            self.fetchAll(orderBy="firstdate", doFetch=False)
            for i, e in enumerate(self.fetchCursor()):
                _print(i, e)
                total += 1
        pBLogger.info(dstr.Bibs.elementsFound % total)

    def printAllInfo(self, entriesIn=None, orderBy="firstdate", addFields=None):
        """Print a short resume for all the bibtex entries
        (or for a given subset)

        Parameters:
            entriesIn: the list of entries to print.
                If None, use self.lastFetched or self.getAll.
            orderBy (default "firstdate"): field to consider
                for ordering the entries (if using self.getAll)
            addFields: print additional fields in addition
                to the minimal info, default None
        """
        if entriesIn is not None:
            iterator = entriesIn
        else:
            self.fetchAll(orderBy=orderBy, doFetch=False)
            iterator = self.fetchCursor()
        total = 0
        for i, e in enumerate(iterator):
            total += 1
            orderDate = "[%4d - %-11s]" % (i, e["firstdate"])
            bibKeyStr = "%-30s " % e["bibkey"]
            typeStr = ""
            moreStr = "%-20s %-20s" % (
                e["arxiv"] if e["arxiv"] is not None else "-",
                e["doi"] if e["doi"] is not None else "-",
            )
            if e["book"] == 1:
                typeStr = "(book)"
                moreStr = "%-20s" % e["isbn"]
            elif e["review"] == 1:
                typeStr = "(rev)"
            elif e["lecture"] == 1:
                typeStr = "(lect)"
            elif e["phd_thesis"] == 1:
                typeStr = "(PhDTh)"
                moreStr = "%-20s" % (e["arxiv"] if e["arxiv"] is not None else "-")
            elif e["proceeding"] == 1:
                typeStr = "(proc)"
            print(orderDate + "%7s " % typeStr + bibKeyStr + moreStr)
            if addFields is not None:
                try:
                    if isinstance(addFields, list):
                        for f in addFields:
                            try:
                                print("   %s: %s" % (f, e[f]))
                            except:
                                print("   %s: %s" % (f, e["bibtexDict"][f]))
                    else:
                        try:
                            print("   %s: %s" % (addFields, e[addFields]))
                        except:
                            print("   %s: %s" % (addFields, e["bibtexDict"][addFields]))
                except:
                    pass
        pBLogger.info(dstr.Bibs.elementsFound % total)

    def fetchByCat(self, idCat, orderBy="firstdate", orderType="ASC"):
        """Fetch all the entries associated to a given category

        Parameters:
            idCat: the id of the category
            orderBy (default "entries.firstdate"):
                the "table.field" to use for ordering
            orderType: "ASC" (default) or "DESC"

        Output:
            self
        """
        self.fetchFromDict(
            [
                {
                    "type": "Categories",
                    "content": idCat,
                    "field": "",
                    "operator": "",
                    "logical": "",
                }
            ],
            orderBy=orderBy,
            orderType=orderType,
        )
        return self

    def getByCat(self, idCat, orderBy="firstdate", orderType="ASC"):
        """Use self.fetchByCat and returns
        the dictionary of fetched entries

        Parameters: see self.fetchByCat

        Output:
            a dictionary
        """
        return self.fetchByCat(idCat, orderBy=orderBy, orderType=orderType).lastFetched

    def fetchByExp(self, idExp, orderBy="firstdate", orderType="ASC"):
        """Fetch all the entries associated to a given experiment

        Parameters:
            idExp: the id of the experiment
            orderBy (default "entries.firstdate"):
                the "table.field" to use for ordering
            orderType: "ASC" (default) or "DESC"

        Output:
            self
        """
        self.fetchFromDict(
            [
                {
                    "type": "Experiments",
                    "content": idExp,
                    "field": "",
                    "operator": "",
                    "logical": "",
                }
            ],
            orderBy=orderBy,
            orderType=orderType,
        )
        return self

    def getByExp(self, idExp, orderBy="firstdate", orderType="ASC"):
        """Use self.fetchByExp and returns
        the dictionary of fetched entries

        Parameters: see self.fetchByExp

        Output:
            a dictionary
        """
        return self.fetchByExp(idExp, orderBy=orderBy, orderType=orderType).lastFetched

    def cleanBibtexs(self, startFrom=0, entries=None, pbMax=None, pbVal=None):
        """Clean (remove comments, unwanted fields, newlines, accents)
        and reformat the bibtexs

        Parameters:
            startFrom (default 0): the index where to start from
            entries: the list of entries to be considered.
                If None, the output of self.getAll
            pbMax (callable, optional): a function to set the maximum
                of a progress bar in the GUI, if possible
            pbVal (callable, optional): a function to set the value
                of a progress bar in the GUI, if possible

        Output:
            num, err, changed:
                the number of considered entries,
                the number of errors,
                the list of keys of changed entries
        """
        if entries is None:
            try:
                tot = self.count() - startFrom
                self.fetchAll(
                    saveQuery=False, limitTo=tot, limitOffset=startFrom, doFetch=False
                )
                iterator = self.fetchCursor()
            except TypeError:
                pBLogger.exception(dstr.Bibs.cbInvalidStart)
                return 0, 0, []
        else:
            iterator = entries
            tot = len(entries)
        num = 0
        err = 0
        changed = []
        self.runningCleanBibtexs = True
        pBLogger.info(dstr.Bibs.cbProcessTot % tot)
        try:
            pbMax(tot)
        except TypeError:
            pass
        db = bibtexparser.bibdatabase.BibDatabase()
        for ix, e in enumerate(iterator):
            try:
                pbVal(ix + 1)
            except TypeError:
                pass
            if self.runningCleanBibtexs:
                num += 1
                pBLogger.info(
                    dstr.Bibs.cbProcessProgr
                    % (ix + 1, tot, 100.0 * (ix + 1) / tot, e["bibkey"])
                )
                for field in [
                    "marks",
                    "old_keys",
                ]:  # convert None to "" for given fields
                    if e[field] is None:
                        self.updateField(e["bibkey"], field, "")
                if e["marks"] is not None and "'" in e["marks"]:
                    marks = e["marks"].replace("'", "").split(",")
                    newmarks = []
                    for m in marks:
                        if m not in newmarks:
                            newmarks.append(m)
                    self.updateField(e["bibkey"], "marks", ",".join(newmarks))
                try:
                    element = (
                        bibtexparser.bparser.BibTexParser(common_strings=True)
                        .parse(e["bibtex"])
                        .entries[0]
                    )
                    db.entries = []
                    db.entries.append(element)
                    newbibtex = self.rmBibtexComments(
                        self.rmBibtexACapo(
                            parse_accents_str(pbWriter.write(db).strip())
                        )
                    )
                    if e["bibtex"] != newbibtex and self.updateField(
                        e["bibkey"], "bibtex", newbibtex
                    ):
                        pBLogger.info(dstr.Bibs.elementChanged)
                        changed.append(e["bibkey"])
                except (IndexError, ValueError, ParseException):
                    pBLogger.warning(dstr.Bibs.cbError % e["bibkey"], exc_info=True)
                    err += 1
        pBLogger.info(dstr.Bibs.cbResEntr % num)
        pBLogger.info(dstr.Bibs.cbResErr % err)
        pBLogger.info(dstr.Bibs.cbResChan % len(changed))
        return num, err, changed

    def findCorruptedBibtexs(self, startFrom=0, entries=None, pbMax=None, pbVal=None):
        """Find bibtexs that cannot be read properly

        Parameters:
            startFrom (default 0): the index where to start from
            entries: the list of entries to be considered.
                If None, the output of self.getAll
            pbMax (callable, optional): a function to set the maximum
                of a progress bar in the GUI, if possible
            pbVal (callable, optional): a function to set the value
                of a progress bar in the GUI, if possible

        Output:
            bibtexs: the list of problematic entries
        """
        if entries is None:
            try:
                tot = self.count() - startFrom
                self.fetchAll(
                    saveQuery=False, limitTo=tot, limitOffset=startFrom, doFetch=False
                )
                iterator = self.fetchCursor()
            except TypeError:
                pBLogger.exception(dstr.Bibs.fcbInvalidStart)
                return 0, 0, []
        else:
            iterator = entries
            tot = len(entries)
        bibtexs = []
        self.runningFindBadBibtexs = True
        pBLogger.info(dstr.Bibs.fcbProcessTot % tot)
        try:
            pbMax(tot)
        except TypeError:
            pass
        db = bibtexparser.bibdatabase.BibDatabase()
        for ix, e in enumerate(iterator):
            try:
                pbVal(ix + 1)
            except TypeError:
                pass
            if self.runningFindBadBibtexs:
                pBLogger.info(
                    dstr.Bibs.fcbProcessProgr
                    % (ix + 1, tot, 100.0 * (ix + 1) / tot, e["bibkey"])
                )
                try:
                    element = (
                        bibtexparser.bparser.BibTexParser(common_strings=True)
                        .parse(e["bibtex"])
                        .entries[0]
                    )
                    pBLogger.info(dstr.Bibs.fcbReadable % element["ID"])
                except Exception:
                    bibtexs.append(e["bibkey"])
                    pBLogger.warning(dstr.Bibs.fcbNotReadable % e["bibkey"])
        pBLogger.info(dstr.Bibs.fcbBadEntries % (len(bibtexs), bibtexs))
        return bibtexs

    def searchOAIUpdates(
        self,
        startFrom=0,
        entries=None,
        force=False,
        reloadAll=False,
        pbMax=None,
        pbVal=None,
    ):
        """Select unpublished papers and look for updates using inspireOAI

        Parameters:
            startFrom (default 0): the index in the list of entries
                where to start updating from
            entries: the list of entries to be considered or None
                (if None, use self.getAll)
            force (boolean, default False): force the update also
                of entries which already have journal information
            reloadAll (boolean, default False): reload the entire content,
                without trying to simply update the existing one
            pbMax (callable, optional): a function to set the maximum
                of a progress bar in the GUI, if possible
            pbVal (callable, optional): a function to set the value
                of a progress bar in the GUI, if possible

        Output:
            num, err, changed:
                the number of processed entries,
                the list of errors and
                of changed entries
        """
        if entries is None:
            try:
                tot = self.count() - startFrom
                self.fetchAll(
                    saveQuery=False, limitTo=tot, limitOffset=startFrom, doFetch=False
                )
                iterator = self.fetchCursor()
            except TypeError:
                pBLogger.exception(dstr.Bibs.souInvalidStart)
                return 0, [], []
        else:
            iterator = entries
            tot = len(entries)
        num = 0
        err = []
        changed = []
        self.runningOAIUpdates = True
        pBLogger.info(dstr.Bibs.souProcessTot % tot)
        try:
            pbMax(tot)
        except TypeError:
            pass
        for ix, e in enumerate(iterator):
            try:
                pbVal(ix + 1)
            except TypeError:
                pass
            if not "bibtexDict" in e.keys():
                e = self.completeFetched([e])[0]
            if (
                self.runningOAIUpdates
                and (e["proceeding"] == 0 or force)
                and e["book"] == 0
                and e["lecture"] == 0
                and e["phd_thesis"] == 0
                and e["noUpdate"] == 0
                and e["inspire"] is not None
                and e["inspire"] != ""
                and (
                    force
                    or (e["doi"] is None or "journal" not in e["bibtexDict"].keys())
                )
            ):
                num += 1
                pBLogger.info(
                    dstr.Bibs.souProcessProgr
                    % (ix + 1, tot, 100.0 * (ix + 1) / tot, e["bibkey"])
                )
                if not self.updateInfoFromOAI(
                    e["inspire"],
                    bibtex=e["bibtex"],
                    verbose=0,
                    readConferenceTitle=(e["proceeding"] == 1 and force),
                    reloadAll=reloadAll,
                    originalKey=e["bibkey"],
                ):
                    err.append(e["bibkey"])
                else:
                    try:
                        new = self.getByKey(e["bibkey"], saveQuery=False)[0]
                    except IndexError:
                        try:
                            e["bibkey"] = self.newKey
                            del self.newKey
                            new = self.getByKey(e["bibkey"], saveQuery=False)[0]
                        except (AttributeError, IndexError):
                            pBLogger.exception(dstr.Bibs.souError % e["bibkey"])
                            err.append(e["bibkey"])
                            continue
                    if e != new:
                        pBLogger.info(dstr.Bibs.elementChanged)
                        for diff in list(dictdiffer.diff(e, new)):
                            pBLogger.info(diff)
                        changed.append(e["bibkey"])
                pBLogger.info("")
        pBLogger.info(dstr.Bibs.souResProc % num)
        pBLogger.info(dstr.Bibs.souResErr % len(err))
        if len(err) > 0:
            pBLogger.info(err)
        pBLogger.info(dstr.Bibs.souResChan % len(changed))
        if len(changed) > 0:
            pBLogger.info(changed)
        return num, err, changed


class Utilities(PhysBiblioDBSub):
    """Adds some more useful functions to the database management"""

    def cleanSpareEntries(self):
        """Find and delete connections
        (bibtex-category, bibtex-experiment, category-experiment)
        where one of the parts is missing
        """

        def deletePresent(ix1, ix2, join, func):
            """Delete the connections if one of the two extremities
            are missing in the respective tables.

            Parameters:
                ix1, ix2: the lists of ids/bibkeys
                    where to look for the indexes
                join: the list of pairs of connected elements
                func: the function that must be used
                    to delete the connections
            """
            for e in join:
                if e[0] not in ix1 or e[1] not in ix2:
                    pBLogger.info(dstr.cleaning % (e[0], e[1]))
                    func(e[0], e[1])

        self.mainDB.bibs.fetchAll(saveQuery=False, doFetch=False)
        bibkeys = [e["bibkey"] for e in self.mainDB.bibs.fetchCursor()]
        idCats = [e["idCat"] for e in self.mainDB.cats.getAll()]
        idExps = [e["idExp"] for e in self.mainDB.exps.getAll()]

        deletePresent(
            bibkeys,
            idExps,
            [[e["bibkey"], e["idExp"]] for e in self.mainDB.bibExp.getAll()],
            self.mainDB.bibExp.delete,
        )
        deletePresent(
            idCats,
            bibkeys,
            [[e["idCat"], e["bibkey"]] for e in self.mainDB.catBib.getAll()],
            self.mainDB.catBib.delete,
        )
        deletePresent(
            idCats,
            idExps,
            [[e["idCat"], e["idExp"]] for e in self.mainDB.catExp.getAll()],
            self.mainDB.catExp.delete,
        )

    def cleanAllBibtexs(self, verbose=0):
        """Remove newlines, non-standard characters
        and comments from the bibtex of all the entries in the database

        Parameters:
            verbose: print more messages
        """
        b = self.mainDB.bibs
        b.fetchAll(doFetch=False)
        for e in b.fetchCursor():
            t = e["bibtex"]
            t = b.rmBibtexComments(t)
            t = parse_accents_str(t)
            t = b.rmBibtexACapo(t)
            b.updateField(e["bibkey"], "bibtex", t, verbose=verbose)


def catString(idCat, db, withDesc=False):
    """Return the string describing the category
    (id, name, description if required)

    Parameters:
        idCat: the id of the category
        withDesc (boolean, default False):
            if True, add the category description

    Output:
        the output string
    """
    try:
        cat = db.cats.getByID(idCat)[0]
    except IndexError:
        pBLogger.warning(dstr.catNotInDb % idCat)
        return ""
    if withDesc:
        return "%4d: %s - <i>%s</i>" % (cat["idCat"], cat["name"], cat["description"])
    else:
        return "%4d: %s" % (cat["idCat"], cat["name"])


def cats_alphabetical(listId, db):
    """Sort the categories in the given list in alphabetical order

    Parameters:
        listId: the list of ids of the categories

    Output:
        the list of ids, ordered according to the category names.
    """
    listIn = []
    for i in listId:
        try:
            listIn.append(db.cats.getByID(i)[0])
        except IndexError:
            pBLogger.warning(dstr.catNotInDb % i)
    decorated = [(x["name"].lower(), x) for x in listIn]
    return [x[1]["idCat"] for x in sorted(decorated)]


def dbStats(db):
    """Get statistics on the number of entries
    in the various database tables

    Parameters:
        db: the database (instance of PhysBiblioDB)
    """
    db.stats = {}
    db.stats["bibs"] = db.bibs.count()
    db.stats["cats"] = db.cats.count()
    db.stats["exps"] = db.exps.count()
    db.stats["catBib"] = db.catBib.count()
    db.stats["catExp"] = db.catExp.count()
    db.stats["bibExp"] = db.bibExp.count()


pBDB = PhysBiblioDB(pbConfig.currentDatabase, pBLogger)
