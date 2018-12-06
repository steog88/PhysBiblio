"""Module that manages the actions on the database (and few more).

This file is part of the physbiblio package.
"""
from sqlite3 import \
	OperationalError, ProgrammingError, DatabaseError, InterfaceError
import os
import re
import traceback
import ast
import datetime
import bibtexparser
import six
from pyparsing import ParseException
import dictdiffer

try:
	from physbiblio.databaseCore import PhysBiblioDBCore, PhysBiblioDBSub
	from physbiblio.config import pbConfig, ConfigurationDB
	from physbiblio.bibtexWriter import pbWriter
	from physbiblio.errors import pBLogger
	from physbiblio.webimport.webInterf import physBiblioWeb
	from physbiblio.webimport.arxiv import getYear
	from physbiblio.parseAccents import parse_accents_str
except ImportError:
	print("Could not find physbiblio and its modules!")
	print(traceback.format_exc())
	raise


class PhysBiblioDB(PhysBiblioDBCore):
	"""Subclassing PhysBiblioDBCore to add reOpenDB
	and loadSubClasses implementations.
	"""

	def __init__(self, *args, **kwargs):
		"""Wrapper for PhysBiblioDBCore.__init__"""
		PhysBiblioDBCore.__init__(self, *args, **kwargs)

	def reOpenDB(self, newDB=None):
		"""Close the currently open database and
		open a new one (the same if newDB is None).

		Parameters:
			newDB: None (default) or the name of the new database

		Output:
			True if successfull
		"""
		if newDB is not None:
			self.closeDB()
			del self.conn
			del self.curs
			self.dbname = newDB
			db_is_new = not os.path.exists(self.dbname)
			self.openDB()
			if db_is_new or self.checkExistingTables():
				self.logger.info("-------New database. Creating tables!\n\n")
				self.createTables()
			self.checkCols()

			self.lastFetched = None
			self.catsHier = None
		else:
			self.closeDB()
			self.openDB()
			if self.checkExistingTables():
				self.logger.info("-------New database. Creating tables!\n\n")
				self.createTables()
			self.checkCols()
			self.lastFetched = None
			self.catsHier = None
		return True

	def loadSubClasses(self):
		"""Load the subclasses that manage the content
		in the various tables in the database.

		Output:
			True
		"""
		for q in ["bibs", "cats", "exps", "bibExp", "catBib",
				"catExp", "utils", "config"]:
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
				(data["name"], data["parentCat"]))
		except KeyError:
			pBLogger.exception("Missing field when inserting category")
			return False
		if self.curs.fetchall():
			pBLogger.info(
				"An entry with the same name is already present "
				+ "in the same category!")
			return False
		else:
			return self.connExec(
				"INSERT into categories (name, description, parentCat, "
				+ "comments, ord) values (:name, :description, :parentCat, "
				+ ":comments, :ord)\n", data)

	def update(self, data, idCat):
		"""Update all the fields of an existing category

		Parameters:
			data: the dictionary containing the category field values
			idCat: the id of the category in the database

		Output:
			the output of self.connExec
		"""
		data["idCat"] = idCat
		query = "replace into categories (" \
			+ ", ".join(data.keys()) + ") values (:" \
			+ ", :".join(data.keys()) + ")\n"
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
		pBLogger.info("Updating '%s' for entry '%s'"%(field, idCat))
		if field in self.tableCols["categories"] and field is not "idCat" \
				and value is not "" and value is not None:
			query = "update categories set " + field \
				+ "=:field where idCat=:idCat\n"
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
					"You should not delete the category with id: %d%s."%(
					idCat, " (name: %s)"%name if name else ""))
				return False
			pBLogger.info("Using idCat=%d"%idCat)
			pBLogger.info("Looking for child categories")
			for row in self.getChild(idCat):
				self.delete(row["idCat"])
			self.cursExec("delete from categories where idCat=?\n",
				(idCat, ))
			self.cursExec("delete from expCats where idCat=?\n", (idCat, ))
			self.cursExec("delete from entryCats where idCat=?\n", (idCat, ))
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
		self.cursExec("select * from categories where idCat=?\n", (idCat, ))
		return self.curs.fetchall()

	def getDictByID(self, idCat):
		"""Get a category given its id, returns a standard dictionary

		Parameters:
			idCat: the id of the required category

		Output:
			a dictionary with all field values for the required category
		"""
		self.cursExec("select * from categories where idCat=?\n", (idCat, ))
		try:
			entry = self.curs.fetchall()[0]
			catDict = {}
			for i,k in enumerate(self.tableCols["categories"]):
				catDict[k] = entry[i]
		except:
			pBLogger.info("Error in extracting category by idCat")
			catDict = None
		return catDict

	def getByName(self,name):
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
		self.cursExec("select cats1.* from categories as cats "
			+ "join categories as cats1 on cats.idCat=cats1.parentCat "
			+ "where cats.idCat=?\n", (parent, ))
		return self.curs.fetchall()

	def getParent(self, child):
		"""Get the category that is the parent of the given one

		Parameters:
			child: the id of the child category

		Output:
			the list (len = 1) of `sqlite3.Row` objects
				with all the matching categories
		"""
		self.cursExec("select cats.* from categories as cats "
			+ "join categories as cats1 on cats.idCat=cats1.parentCat "
			+ "where cats1.idCat=?\n", (child, ))
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
			for c in [ a for a in cats if a["parentCat"] == idC \
					and a["idCat"] != 0 ]:
				tmp[c["idCat"]] = addSubCats(c["idCat"])
			return tmp
		catsHier = {}
		catsHier[startFrom] = addSubCats(startFrom)
		self.catsHier = catsHier
		return catsHier

	def printHier(self,
			startFrom=0,
			sp=5*" ",
			withDesc=False,
			depth=10,
			replace=False):
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
			pBLogger.warning(
				"Invalid depth in printCatHier (must be greater than 2)")
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
					print(indent
						+ catString(l, self.mainDB, withDesc=withDesc))
					printSubGroup(tree[l],
						(startDepth + 1) * sp,
						startDepth + 1)
		printSubGroup(catsHier)

	def getByEntry(self, key):
		"""Find all the categories associated to a given entry

		Parameters:
			key: the bibtex key of the entry

		Output:
			the list of `sqlite3.Row` objects
				with all the matching categories
		"""
		self.cursExec("select * from categories "
			+ "join entryCats on categories.idCat=entryCats.idCat "
			+ "where entryCats.bibkey=?\n", (key,))
		return self.curs.fetchall()

	def getByEntries(self, keys):
		"""Find all the categories associated to a list of entries

		Parameters:
			keys: the list of bibtex keys of the entries

		Output:
			the list of `sqlite3.Row` objects
				with all the matching categories
		"""
		self.cursExec("select * from categories "
			+ "join entryCats on categories.idCat=entryCats.idCat "
			+ "where " + " or ".join(
				["entryCats.bibkey=?" for k in keys])
			+ "\n",
			keys)
		return self.curs.fetchall()

	def getByExp(self, idExp):
		"""Find all the categories associated to a given experiment

		Parameters:
			idExp: the id of the experiment

		Output:
			the list of `sqlite3.Row` objects
				with all the matching categories
		"""
		self.cursExec("select * from categories "
			+ "join expCats on categories.idCat=expCats.idCat "
			+ "where expCats.idExp=?\n", (idExp,))
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
		self.cursExec("SELECT Count(*) FROM entryCats WHERE idCat = :idCat",
			{"idCat": idCat, })
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
			{"bibkey": key, "idCat": idCat})
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
			if len(self.getOne(idCat, key))==0:
				pBLogger.debug("inserting (idCat=%s and key=%s)"%(idCat, key))
				return self.connExec(
					"INSERT into entryCats (bibkey, idCat) "
					+ "values (:bibkey, :idCat)",
					{"bibkey": key, "idCat": idCat})
			else:
				pBLogger.info("EntryCat already present: (%d, %s)"%(
					idCat, key))
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
				{"bibkey": key, "idCat": idCat})

	def updateBibkey(self, new, old):
		"""Update the connections affected by a bibkey change

		Parameters:
			new: the new bibtex key
			old: the old bibtex key

		Output:
			the output of self.connExec
		"""
		pBLogger.info(
			"Updating entryCats for bibkey change, from '%s' to '%s'"%(
			old, new))
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
			string = six.moves.input("categories for '%s': "%k)
			try:
				cats = self.literal_eval(string)
				self.insert(cats, k)
			except:
				pBLogger.warning(
					"Something failed in reading your input '%s'"%string)

	def askKeys(self, cats):
		"""Loop over the given categories and ask for
		the bibtex keys to be associated with them

		Parameters:
			cats: a single id or a list of categories
		"""
		if not isinstance(cats, list):
			cats = [cats]
		for c in cats:
			string = six.moves.input("entries for '%d': "%c)
			try:
				keys = self.literal_eval(string)
				self.insert(c, keys)
			except:
				pBLogger.warning(
					"Something failed in reading your input '%s'"%string)


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
			"SELECT Count(*) FROM expCats WHERE idExp = :idExp",
			{"idExp": idExp, })
		return self.curs.fetchall()[0][0]

	def countByCat(self, idCat):
		"""Obtain the number of rows in expCats
		which are associated with a given category

		Parameters:
			idCat: the id of the category

		Output:
			the number of matching records
		"""
		self.cursExec("SELECT Count(*) FROM expCats WHERE idCat = :idCat",
			{"idCat": idCat, })
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
			{"idExp": idExp, "idCat": idCat})
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
			if len(self.getOne(idCat, idExp))==0:
				pBLogger.debug(
					"inserting (idCat=%s and idExp=%s)"%(idCat, idExp))
				return self.connExec(
					"INSERT into expCats (idExp, idCat) "
					+ "values (:idExp, :idCat)",
					{"idExp": idExp, "idCat": idCat})
			else:
				pBLogger.info(
					"ExpCat already present: (%d, %d)"%(idCat, idExp))
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
				{"idExp": idExp, "idCat": idCat})

	def askCats(self, exps):
		"""Loop over the given experiment ids and
		ask for the categories to be associated with them

		Parameters:
			exps: a single id or a list of experiment ids
		"""
		if not isinstance(exps, list):
			exps = [exps]
		for e in exps:
			string = six.moves.input("categories for '%d': "%e)
			try:
				cats = self.literal_eval(string)
				self.insert(cats, e)
			except:
				pBLogger.warning(
					"Something failed in reading your input '%s'"%string)

	def askExps(self, cats):
		"""Loop over the given category ids and
		ask for the experiments to be associated with them

		Parameters:
			cats: a single id or a list of category ids
		"""
		if not isinstance(cats, list):
			cats = [cats]
		for c in cats:
			string = six.moves.input("experiments for '%d': "%c)
			try:
				exps = self.literal_eval(string)
				self.insert(c, exps)
			except:
				pBLogger.warning(
					"Something failed in reading your input '%s'"%string)


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
		self.cursExec("SELECT Count(*) FROM entryExps WHERE idExp = :idExp",
			{"idExp": idExp, })
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
			{"idExp": idExp, "bibkey": key})
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
			if len(self.getOne(key, idExp))==0:
				pBLogger.debug("inserting (key=%s and idExp=%s)"%(key, idExp))
				if self.connExec(
						"INSERT into entryExps (idExp, bibkey) "
						+ "values (:idExp, :bibkey)",
						{"idExp": idExp, "bibkey": key}):
					for c in self.mainDB.cats.getByExp(idExp):
						self.mainDB.catBib.insert(c["idCat"],key)
					return True
			else:
				pBLogger.info(
					"EntryExp already present: (%s, %d)"%(key, idExp))
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
				{"idExp": idExp, "bibkey": key})

	def updateBibkey(self, new, old):
		"""Update the connections affected by a bibkey change

		Parameters:
			new: the new bibtex key
			old: the old bibtex key

		Output:
			the output of self.connExec
		"""
		pBLogger.info("Updating entryCats for bibkey change, "
			+ "from '%s' to '%s'"%(old, new))
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
			string = six.moves.input("experiments for '%s': "%k)
			try:
				exps = self.literal_eval(string)
				self.insert(k, exps)
			except:
				pBLogger.warning(
					"Something failed in reading your input '%s'"%string)

	def askKeys(self, exps):
		"""Loop over the given experiment ids
		and ask for the bibtexs to be associated with them

		Parameters:
			exps: a single id or a list of experiment ids
		"""
		if not isinstance(exps, list):
			exps = [exps]
		for e in exps:
			string = six.moves.input("entries for '%d': "%e)
			try:
				keys = self.literal_eval(string)
				self.insert(keys, e)
			except:
				pBLogger.warning(
					"Something failed in reading your input '%s'"%string)


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
			data)

	def update(self, data, idExp):
		"""Update an existing experiment

		Parameters:
			data: the dictionary with the experiment fields
			idExp: the experiment id

		Output:
			the output of self.connExec
		"""
		data["idExp"] = idExp
		query = "replace into experiments (" \
			+ ", ".join(data.keys()) + ") values (:" \
			+ ", :".join(data.keys()) + ")\n"
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
		pBLogger.info("Updating '%s' for entry '%s'"%(field, idExp))
		if field in self.tableCols["experiments"] and field is not "idExp" \
				and value is not "" and value is not None:
			query = "update experiments set " + field \
				+ "=:field where idExp=:idExp\n"
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
			pBLogger.info("Using idExp=%d"%idExp)
			self.cursExec("delete from experiments where idExp=?", (idExp, ))
			self.cursExec("delete from expCats where idExp=?", (idExp, ))
			self.cursExec("delete from entryExps where idExp=?", (idExp, ))

	def getAll(self, orderBy="name", order="ASC"):
		"""Get all the experiments

		Parameters:
			orderBy: the field used to order the output
			order: "ASC" or "DESC"

		Output:
			the list of `sqlite3.Row` objects
				with all the experiments in the database
		"""
		self.cursExec("select * from experiments order by %s %s"%(
			orderBy, order))
		return self.curs.fetchall()

	def getByID(self, idExp):
		"""Get experiment matching the given id

		Parameters:
			idExp: the experiment id

		Output:
			the list (len = 1) of `sqlite3.Row` objects
				with all the matching experiments
		"""
		self.cursExec("select * from experiments where idExp=?", (idExp, ))
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
		self.cursExec("select * from experiments where idExp=?", (idExp, ))
		try:
			entry = self.curs.fetchall()[0]
			expDict = {}
			for i,k in enumerate(self.tableCols["experiments"]):
				expDict[k] = entry[i]
		except:
			pBLogger.info("Error in extracting experiment by idExp")
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
		self.cursExec("select * from experiments where name=?", (name, ))
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
			(string, string, string, string))
		return self.curs.fetchall()

	def to_str(self, q):
		"""Convert the experiment row in a string

		Parameters:
			q: the experiment record (sqlite3.Row or dict)
		"""
		return "%3d: %-20s [%-40s] [%s]"%(
			q["idExp"], q["name"], q["homepage"], q["inspire"])

	def printInCats(self, startFrom=0, sp=5*" ", withDesc=False):
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
			exp = [ e for e in exps if e["idExp"] == idExp ][0]
			if withDesc:
				return sp + '-> %s (%d) - %s'%(
					exp['name'], exp['idExp'], exp['comments'])
			else:
				return sp + '-> %s (%d)'%(exp['name'], exp['idExp'])

		def alphabetExp(listId):
			"""Order experiments within a list in alphabetical order

			Parameters:
				listId: the list of experiment ids

			Output:
				the ordered list of id
			"""
			listIn = [ e for e in exps if e["idExp"] in listId ]
			decorated = [ (x["name"], x) for x in listIn ]
			decorated.sort()
			return [ x[1]["idExp"] for x in decorated ]

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
				pBLogger.exception("Error printing experiments!")

		for l0 in cats_alphabetical(catsHier.keys(), self.mainDB):
			for l1 in cats_alphabetical(catsHier[l0].keys(), self.mainDB):
				if showCat[l1]:
					showCat[l0] = True
				for l2 in cats_alphabetical(
						catsHier[l0][l1].keys(), self.mainDB):
					if showCat[l2]:
						showCat[l0] = True
						showCat[l1] = True
					for l3 in cats_alphabetical(
							catsHier[l0][l1][l2].keys(), self.mainDB):
						if showCat[l3]:
							showCat[l0] = True
							showCat[l1] = True
							showCat[l2] = True
						for l4 in cats_alphabetical(
								catsHier[l0][l1][l2][l3].keys(), self.mainDB):
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
				for l2 in cats_alphabetical(
						catsHier[l0][l1].keys(), self.mainDB):
					if showCat[l2]:
						print(2*sp + catString(l2, self.mainDB))
						printExpCats(l2, 3)
					for l3 in cats_alphabetical(
							catsHier[l0][l1][l2].keys(), self.mainDB):
						if showCat[l3]:
							print(3*sp + catString(l3, self.mainDB))
							printExpCats(l3, 4)
						for l4 in cats_alphabetical(
								catsHier[l0][l1][l2][l3].keys(), self.mainDB):
							if showCat[l4]:
								print(4*sp + catString(l4, self.mainDB))
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
		self.cursExec("select * from experiments " \
			+ "join expCats on experiments.idExp=expCats.idExp " \
			+ "where expCats.idCat=?", (idCat,))
		return self.curs.fetchall()

	def getByEntry(self, key):
		"""Get all the experiments matching a given bibtex entry

		Parameters:
			key: the key of the bibtex to be matched

		Output:
			the list of `sqlite3.Row` objects
				with all the matching experiments
		"""
		self.cursExec("select * from experiments " \
			+ "join entryExps on experiments.idExp=entryExps.idExp "
			+ "where entryExps.bibkey=?", (key, ))
		return self.curs.fetchall()

	def getByEntries(self, keys):
		"""Get all the experiments matching a list of given bibtex entries

		Parameters:
			keys: the keys of the bibtex to be matched

		Output:
			the list of `sqlite3.Row` objects
				with all the matching experiments
		"""
		self.cursExec("select * from experiments " \
			+ "join entryExps on experiments.idExp=entryExps.idExp " \
			+ "where " + " or ".join(["entryExps.bibkey=?" for k in keys]) \
			+ "\n", keys)
		return self.curs.fetchall()


class Entries(PhysBiblioDBSub):
	"""Functions to manage the bibtex entries"""

	def __init__(self, parent):
		"""Call parent __init__ and create an empty lastFetched & c."""
		PhysBiblioDBSub.__init__(self, parent)
		self.lastFetched = []
		self.lastQuery = "select * from entries limit 10"
		self.lastVals = ()
		self.lastInserted = []
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
			pBLogger.info("Delete entry, using key = '%s'"%key)
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
		for el in fetched_in:
			tmp = {}
			for k in el.keys():
				tmp[k] = el[k]
			if el["bibdict"] is not None:
				if isinstance(el["bibdict"], six.string_types) \
						and el["bibdict"].strip() != "" \
						and el["bibdict"].strip() != "{}":
					tmp["bibtexDict"] = ast.literal_eval(
						el["bibdict"].strip())
					tmp["bibdict"] = dict(tmp["bibtexDict"])
				elif isinstance(el["bibdict"], dict):
					tmp["bibtexDict"] = tmp["bibdict"]
			else:
				try:
					tmp["bibtexDict"] = bibtexparser.bparser.BibTexParser(
						common_strings=True).parse(el["bibtex"]).entries[0]
				except IndexError:
					tmp["bibtexDict"] = {}
					tmp["bibdict"] = {}
				except ParseException:
					pBLogger.warning("Problem in parsing the following "
						+ "bibtex code:\n%s"%el["bibtex"],
						exc_info=True)
					tmp["bibtexDict"] = {}
					tmp["bibdict"] = {}
				self.updateField(el["bibkey"], "bibdict",
					"%s"%tmp["bibtexDict"])
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
					[tmp["journal"], tmp["volume"],
					"(%s)"%tmp["year"], tmp["pages"]])
				if tmp["published"] == "  () ":
					tmp["published"] = ""
			except KeyError:
				tmp["published"] = ""
			try:
				author = tmp["bibtexDict"]["author"]
				if author.count("and") > pbConfig.params["maxAuthorNames"] - 1:
					author = author[:author.index("and")] + "et al."
				tmp["author"] = author
			except KeyError:
				tmp["author"] = ""
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
				"Query failed: %s\nvalues:"%(self.lastQuery, self.lastVals))
		if doFetch:
			fetched_in = cursor.fetchall()
			self.lastFetched = self.completeFetched(fetched_in)
		return self

	def fetchFromDict(self,
			queryDict={},
			catExpOperator="and",
			defaultConnection="and",
			orderBy="firstdate",
			orderType="ASC",
			limitTo=None,
			limitOffset=None,
			saveQuery=True,
			doFetch=True):
		"""Fetch entries using a number of criterions

		Parameters:
			queryDict: a dictionary containing mostly dictionaries
				for the fields used to filter and the criterion
				for each field.
				Possible fields:
					"cats" or "exps" > {"operator":
						the logical connection, "id": the id to match}
					"catExpOperator" > "and" or "or" (see below)
					Each other item (the key in the dictionary
						should be the name of a field in the entries table)
						should be a dictionary with the following fields:
					{"str": the string to match
					"operator": "like" if the field must only contain
						the string, "=" for exact match
					"connection" (optional): logical operator}
			catExpOperator: "and" (default) or "or",
				the logical operator that connects multiple
				category + experiment searches.
				May be overwritten by an item in queryDict
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
		def getQueryStr(di):
			return "%%%s%%"%di["str"] if di["operator"] == "like" \
				else di["str"]
		first = True
		vals = ()
		query = "select * from entries "
		prependTab = ""
		jC,wC,vC,jE,wE,vE = ["","","","","",""]
		if "catExpOperator" in queryDict.keys():
			catExpOperator = queryDict["catExpOperator"]
			del queryDict["catExpOperator"]
		catExpOperator = " %s "%catExpOperator
		def catExpStrings(tp, tabName, fieldName):
			"""Returns the string and the data needed
			to perform a search using categories and/or experiments

			Parameters:
				tp: the field of queryDict to consider
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
			if isinstance(queryDict[tp]["id"], list):
				if queryDict[tp]["operator"] == "or":
					joinStr += " left join %s on entries.bibkey=%s.bibkey"%(
						tabName, tabName)
					whereStr += "(%s)"%queryDict[tp]["operator"].join(
						[" %s.%s=? "%(tabName,fieldName) for q in \
							queryDict[tp]["id"]])
					valsTmp = tuple(queryDict[tp]["id"])
				elif queryDict[tp]["operator"] == "and":
					joinStr += " ".join(
						[" left join %s %s%d on entries.bibkey=%s%d.bibkey"%(
							tabName,tabName,iC,tabName,iC) for iC,q in \
							enumerate(queryDict[tp]["id"])])
					whereStr += "(" + " and ".join(
						["%s%d.%s=?"%(tabName, iC, fieldName) for iC,q in \
						enumerate(queryDict[tp]["id"])]) + ")"
					valsTmp = tuple(queryDict[tp]["id"])
				else:
					pBLogger.warning("Invalid operator for joining cats!")
					return joinStr, whereStr, valsTmp
			else:
				joinStr += " left join %s on entries.bibkey=%s.bibkey"%(
					tabName, tabName)
				whereStr += "%s.%s=? "%(tabName, fieldName)
				valsTmp = tuple(str(queryDict[tp]["id"]))
			return joinStr, whereStr, valsTmp
		if "cats" in queryDict.keys():
			jC,wC,vC = catExpStrings("cats", "entryCats", "idCat")
			del queryDict["cats"]
		else:
			jC, wC, vC = "", "", tuple()
		if "exps" in queryDict.keys():
			jE,wE,vE = catExpStrings("exps", "entryExps", "idExp")
			del queryDict["exps"]
		else:
			jE, wE, vE = "", "", tuple()
		if jC != "" or jE != "":
			prependTab = "entries."
			toJoin = []
			if wC != "":
				toJoin.append(wC)
			if wE != "":
				toJoin.append(wE)
			query += jC + jE + " where " + " %s "%(catExpOperator).join(toJoin)
			vals += vC + vE
			first = False
		for k in queryDict.keys():
			if first:
				query += " where "
				first = False
			else:
				query += " %s "%queryDict[k]["connection"] if "connection" \
					in queryDict[k].keys() else defaultConnection
			s = k.split("#")[0]
			if s in self.tableCols["entries"]:
				query += " %s%s %s ? "%(
					prependTab, s, queryDict[k]["operator"])
				vals += (getQueryStr(queryDict[k]), )
		query += " order by " + prependTab + orderBy + " " \
			+ orderType if orderBy else ""
		if limitTo is not None:
			query += " LIMIT %s"%(str(limitTo))
		if limitOffset is not None:
			if limitTo is None:
				query += " LIMIT 100000"
			query += " OFFSET %s"%(str(limitOffset))
		if saveQuery and doFetch:
			self.lastQuery = query
			self.lastVals = vals
		if doFetch:
			cursor = self.curs
		else:
			cursor = self.fetchCurs
		pBLogger.info("Using query:\n%s\nvalues: %s"%(query, vals))
		try:
			if len(vals) > 0:
				cursor.execute(query, vals)
			else:
				cursor.execute(query)
		except:
			pBLogger.exception("Query failed: %s\nvalues: %s"%(query, vals))
			return self
		if doFetch:
			fetched_in = self.curs.fetchall()
			self.lastFetched = self.completeFetched(fetched_in)
		return self

	def fetchAll(self,
			params=None,
			connection="and",
			operator="=",
			orderBy="firstdate",
			orderType="ASC",
			limitTo=None,
			limitOffset=None,
			saveQuery=True,
			doFetch=True):
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
			pBLogger.warning("Invalid logical connection operator "
				+ "('%s') in database operations!\n"%connection
				+ "Reverting to default 'and'.")
			connection = "and"
		if operator.strip() != "=" and operator.strip() != "like":
			pBLogger.warning("Invalid comparison operator "
				+ "('%s') in database operations!\n"%operator
				+ "Reverting to default '='.")
			operator = "="
		if orderType.strip() != "ASC" and orderType.strip() != "DESC":
			pBLogger.warning("Invalid ordering "
				+ "('%s') in database operations!\n"%orderType
				+ "Reverting to default 'ASC'.")
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
							query += " %s "%connection
						query += k + " %s "%operator + " ? "
						if operator.strip() == "like" and "%" not in v1:
							v1 = "%%%s%%"%v1
						vals += (v1,)
				else:
					if first:
						first = False
					else:
						query += " %s "%connection
					query += k + " %s "%operator + "? "
					if operator.strip() == "like" and "%" not in v:
						v = "%%%s%%"%v
					vals += (v,)
		query += " order by " + orderBy + " " + orderType if orderBy else ""
		if limitTo is not None:
			query += " LIMIT %s"%(str(limitTo))
			if limitOffset is not None:
				query += " OFFSET %s"%(str(limitOffset))
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
					pBLogger.exception(
						'Operational error: the database is open'
						+ ' in another instance of the application\n'
						+ 'query: %s'%query)
			else:
				pBLogger.exception(
					'Connection error: %s\nquery: %s'%(err, query))
		except (ProgrammingError, DatabaseError, InterfaceError) as err:
			pBLogger.exception("Query failed: %s\nvalues: %s"%(query, vals))
		if doFetch:
			fetched_in = self.curs.fetchall()
			self.lastFetched = self.completeFetched(fetched_in)
		return self

	def getAll(self,
			params=None,
			connection="and",
			operator="=",
			orderBy="firstdate",
			orderType="ASC",
			limitTo=None,
			limitOffset=None,
			saveQuery=True):
		"""Use self.fetchAll and returns the dictionary of fetched entries

		Parameters: see self.fetchAll

		Output:
			a dictionary
		"""
		return self.fetchAll(params=params,
			connection=connection,
			operator=operator,
			orderBy=orderBy,
			orderType=orderType,
			limitTo=limitTo,
			limitOffset=limitOffset,
			saveQuery=saveQuery,
			doFetch=True).lastFetched

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
			return self.fetchAll(params={"bibkey": bibkey},
				connection="or", saveQuery=saveQuery)
		else:
			return self.fetchAll(params={"bibkey": bibkey},
				saveQuery=saveQuery)

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
			strings = ["%%%s%%"%q for q in key]
			return self.fetchAll(
				params = {"bibkey": strings,
					"old_keys": strings,
					"bibtex": strings},
				connection="or ",
				operator=" like ",
				saveQuery=saveQuery)
		else:
			return self.fetchAll(
				params = {"bibkey": "%%%s%%"%key,
					"old_keys": "%%%s%%"%key,
					"bibtex": "%%%s%%"%key},
				connection="or ",
				operator=" like ",
				saveQuery=saveQuery)

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
				params={"bibtex":["%%%s%%"%q for q in string]},
				connection="or",
				operator=" like ",
				saveQuery=saveQuery)
		else:
			return self.fetchAll(
				params={"bibtex":"%%%s%%"%string},
				operator=" like ",
				saveQuery=saveQuery)

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
			pBLogger.warning(
				"Error in getField('%s', '%s'): no element found?"%(
				key, field))
			return False
		except KeyError:
			pBLogger.warning(
				"Error in getField('%s', '%s'): the field is missing?"%(
				key, field))
			return False
		if field == "bibdict" and isinstance(value, six.string_types):
			try:
				return ast.literal_eval(value)
			except SyntaxError:
				pBLogger.error("Cannot read bibdict:\n'%s'"%value)
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

	def getDoiUrl(self, key):
		"""Get the doi.org url for the entry,
		if it has something in the doi field

		Parameters:
			key: the bibtex key

		Output:
			a string
		"""
		url = self.getField(key, "doi")
		return pbConfig.doiUrl + url \
			if url != "" and url is not False and url is not None \
			else False

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
		return pbConfig.arxivUrl + "/" + urlType + "/" + url \
			if url != "" and url is not False \
				and url is not None \
				and url is not "" \
			else False

	def insert(self, data):
		"""Insert an entry

		Parameters:
			data: a dictionary with the data fields to be inserted

		Output:
			the output of self.connExec
		"""
		return self.connExec("INSERT into entries ("
			+ ", ".join(self.tableCols["entries"]) + ") values (:"
			+ ", :".join(self.tableCols["entries"]) + ")\n",
			data)

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
		return self.connExec("replace into entries (" \
			+ ", ".join(data.keys()) + ") values (:" \
			+ ", :".join(data.keys()) + ")\n", data)

	def prepareInsert(self,
			bibtex,
			bibkey=None, inspire=None, arxiv=None,
			ads=None, scholar=None, doi=None, isbn=None,
			year=None, link=None, comments=None,
			old_keys=None, crossref=None,
			exp_paper=None, lecture=None, phd_thesis=None,
			review=None, proceeding=None, book=None,
			marks=None, firstdate=None, pubdate=None,
			noUpdate=None, abstract=None, number=None):
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
		data = {}
		if number is None:
			number = 0
		try:
			element = bibtexparser.bparser.BibTexParser(common_strings=True
				).parse(bibtex).entries[number]
			if element["ID"] is None:
				element["ID"] = ""
			if bibkey:
				element["ID"] = bibkey
			data["bibkey"] = element["ID"]
		except IndexError:
			pBLogger.info("No elements found?")
			data["bibkey"] = ""
			return data
		except (KeyError, ParseException):
			pBLogger.info("Impossible to parse bibtex!")
			data["bibkey"] = ""
			return data
		db = bibtexparser.bibdatabase.BibDatabase()
		db.entries = []
		db.entries.append(element)
		data["bibtex"] = self.rmBibtexComments(self.rmBibtexACapo(
			pbWriter.write(db).strip()))
		#most of the fields have standard behaviour:
		for k in ["abstract", "crossref", "doi", "isbn"]:
			data[k] = locals()[k] if locals()[k] else element[k] \
				if k in element.keys() else None
		for k in ["ads", "comments", "inspire", "old_keys", "scholar"]:
			data[k] = locals()[k] if locals()[k] else None
		for k in ["book", "exp_paper", "lecture",
				"noUpdate", "phd_thesis", "proceeding", "review"]:
			data[k] = 1 if locals()[k] else 0
		for k in ["marks", "pubdate"]:
			data[k] = locals()[k] if locals()[k] else ""
		#arxiv
		data["arxiv"] = arxiv if arxiv else \
			element["arxiv"] if "arxiv" in element.keys() else \
			element["eprint"] if "eprint" in element.keys() else ""
		#year
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
					data["year"]=None
		#link
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
		#firstdate
		data["firstdate"] = firstdate if firstdate \
			else datetime.date.today().strftime("%Y-%m-%d")
		#bibtex dict
		try:
			tmpBibDict = bibtexparser.bparser.BibTexParser(common_strings=True
				).parse(data["bibtex"]).entries[0]
		except IndexError:
			tmpBibDict = {}
		except ParseException:
			pBLogger.warning("Problem in parsing the following "
				+ "bibtex code:\n%s"%data["bibtex"], exc_info=True)
			tmpBibDict = {}
		data["bibdict"] = "%s"%tmpBibDict
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
		u = self.prepareUpdate(self.getField(key_old, "bibtex"),
			self.getField(key_new, "bibtex"))
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
			elementOld = bibtexparser.bparser.BibTexParser(common_strings=True
				).parse(bibtexOld).entries[0]
			elementNew = bibtexparser.bparser.BibTexParser(common_strings=True
				).parse(bibtexNew).entries[0]
		except ParseException:
			pBLogger.warning("Parsing exception in prepareUpdate:\n%s\n%s"%(
				bibtexOld, bibtexNew))
			return ""
		except IndexError:
			pBLogger.warning("Empty bibtex?\n%s\n%s"%(bibtexOld, bibtexNew))
			return ""
		db = bibtexparser.bibdatabase.BibDatabase()
		db.entries = []
		keep = elementOld
		for k in elementNew.keys():
			if k not in elementOld.keys():
				keep[k] = elementNew[k]
			elif elementNew[k] and elementNew[k] != elementOld[k] \
					and k != "bibtex" and k != "ID":
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
			string, number=number)
		if key is None:
			key = string
		if newid is not "":
			if self.connExec("update entries set inspire=:inspire " \
					+ "where bibkey=:bibkey\n",
					{"inspire": newid, "bibkey": key}):
				return newid
			else:
				pBLogger.warning("Something went wrong in updateInspireID")
				return False
		else:
			arxiv = self.getField(key, "arxiv")
			if arxiv is not "" and arxiv is not None:
				newid = physBiblioWeb.webSearch["inspire"].retrieveInspireID(
					"eprint+%s"%arxiv, number=0)
				if newid is not "":
					if self.connExec("update entries set inspire=:inspire " \
							+ "where bibkey=:bibkey\n",
							{"inspire": newid, "bibkey": key}):
						return newid
					else:
						pBLogger.warning(
							"Something went wrong in updateInspireID")
						return False
			else:
				doi = self.getField(key, "doi")
				if doi is not "" and doi is not None:
					newid = physBiblioWeb.webSearch["inspire"]\
						.retrieveInspireID("doi+%s"%doi, number=0)
					if newid is not "":
						if self.connExec(
								"update entries set inspire=:inspire " \
								+ "where bibkey=:bibkey\n",
								{"inspire": newid, "bibkey": key}):
							return newid
						else:
							pBLogger.warning(
								"Something went wrong in updateInspireID")
							return False
				else:
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
			pBLogger.info("Updating '%s' for entry '%s'"%(field, key))
		if field == "bibtex" and value != "" and value is not None:
			try:
				tmpBibDict = bibtexparser.bparser.BibTexParser(
					common_strings=True).parse(value).entries[0]
			except IndexError:
				tmpBibDict = {}
			except ParseException:
				pBLogger.warning("Problem in parsing the following "
					+ "bibtex code:\n%s"%value, exc_info=True)
				tmpBibDict = {}
			self.updateField(key,
				"bibdict", "%s"%tmpBibDict, verbose=verbose)
		if field in self.tableCols["entries"] and field != "bibkey" \
				and value is not None:
			query = "update entries set " + field \
				+ "=:field where bibkey=:bibkey\n"
			if verbose > 1:
				pBLogger.info("%s"%((query, field, value)))
			return self.connExec(query, {"field": value, "bibkey": key})
		else:
			if verbose > 1:
				pBLogger.warning(
					"Non-existing field or unappropriated value: "
					+ "(%s, %s, %s)"%(key, field, value))
			return False

	def updateBibkey(self, oldKey, newKey):
		"""Update the bibtex key of an entry

		Parameters:
			oldKey: the old bibtex key
			newKey: the new bibtex key

		Output:
			the output of self.connExec or False if some errors occurred
		"""
		pBLogger.info("Updating bibkey for entry '%s' into '%s'"%(
			oldKey, newKey))
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
				self.updateField(newKey, "old_keys", ",".join(
					oldkeys + [oldKey]))
				try:
					from physbiblio.pdf import pBPDF
					pBPDF.renameFolder(oldKey, newKey)
				except Exception:
					pBLogger.exception("Cannot rename folder")
				query = "update entryCats set bibkey=:new where bibkey=:old\n"
				if self.connExec(query, {"new": newKey, "old": oldKey}):
					query = "update entryExps set bibkey=:new " \
						+ "where bibkey=:old\n"
					return self.connExec(query, {"new": newKey, "old": oldKey})
				else:
					return False
			else:
				return False
		except:
			pBLogger.warning("Impossible to update bibkey", exc_info=True)
			return False

	def getDailyInfoFromOAI(self, date1=None, date2=None):
		"""Use inspire OAI webinterface to get updated information
		on the entries between two dates

		Parameters:
			date1, date2: the two dates defining
				the time interval to consider
		"""
		if date1 is None or not re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", date1):
			date1 = (datetime.date.today() - datetime.timedelta(1)).strftime(
				"%Y-%m-%d")
		if date2 is None or not re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", date2):
			date2 = datetime.date.today().strftime("%Y-%m-%d")
		yren, monen, dayen = date1.split('-')
		yrst, monst, dayst = date2.split('-')
		pBLogger.info(
			"Calling INSPIRE-HEP OAI harvester between dates %s and %s"%(
			date1, date2))
		date1 = datetime.datetime(int(yren), int(monen), int(dayen))
		date2 = datetime.datetime(int(yrst), int(monst), int(dayst))
		entries = physBiblioWeb.webSearch["inspireoai"].retrieveOAIUpdates(
			date1, date2)
		changed = []
		for e in entries:
			try:
				key = e["bibkey"]
				pBLogger.info(key)
				old = self.getByBibkey(key, saveQuery=False)
				if len(old) > 0 and old[0]["noUpdate"] == 0:
					outcome, bibtex = physBiblioWeb.webSearch["inspireoai"]\
						.updateBibtex(e, old[0]["bibtex"])
					if not outcome:
						pBLogger.warning(
							"Something went wrong with this entry...")
						continue
					e["bibtex"] = self.rmBibtexComments(self.rmBibtexACapo(
						bibtex.strip()))
					for [o, d] in physBiblioWeb.webSearch["inspireoai"]\
							.correspondences:
						if e[o] != old[0][d] and e[o] != None:
							if o == "bibtex":
								pBLogger.info("-- %s"%d)
								pBLogger.info("old:\n%s"%old[0][d])
								pBLogger.info("new:\n%s"%e[o])
							else:
								pBLogger.info("-- %s, '%s' -> '%s'"%(
									d, old[0][d], e[o]))
							self.updateField(key, d, e[o], verbose=0)
							if len(changed) == 0 or changed[-1] != key:
								changed.append(key)
			except:
				pBLogger.exception("something wrong with entry %s\n%s"%(
					e["id"], e))
		pBLogger.info("%d changed entries:\n%s"%(len(changed), changed))
		pBLogger.info("Inspire OAI harvesting done!")

	def updateInfoFromOAI(self,
			inspireID,
			bibtex=None,
			verbose=0,
			readConferenceTitle=False,
			reloadAll=False,
			originalKey=None):
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
		if inspireID is False or inspireID is "" or inspireID is None:
			pBLogger.error("InspireID is empty, cannot proceed.")
			return False
		if not inspireID.isdigit(): #assume it's a key instead of the inspireID
			originalKey = inspireID
			inspireID = self.getField(inspireID, "inspire")
			try:
				inspireID.isdigit()
			except AttributeError:
				pBLogger.error("Wrong type in inspireID: %s"%inspireID)
				return False
			if not inspireID.isdigit():
				pBLogger.error("Wrong value/format in inspireID: %s"%inspireID)
				return False
		if not reloadAll:
			result = physBiblioWeb.webSearch["inspireoai"].retrieveOAIData(
				inspireID,
				bibtex=bibtex,
				verbose=verbose,
				readConferenceTitle=readConferenceTitle)
		else:
			result = physBiblioWeb.webSearch["inspireoai"].retrieveOAIData(
				inspireID,
				verbose=verbose,
				readConferenceTitle=readConferenceTitle)
		if verbose > 1:
			pBLogger.info(result)
		if result is False:
			pBLogger.error("Empty record looking for recid:%s!"%inspireID)
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
				old = [{k: "" for x, k in \
					physBiblioWeb.webSearch["inspireoai"].correspondences}]
			if verbose > 1:
				pBLogger.info("%s, %s"%(key, old))
			if len(old) > 0:
				for [o, d] in physBiblioWeb.webSearch["inspireoai"]\
						.correspondences:
					try:
						if verbose > 0:
							pBLogger.info("%s = %s (%s)"%(
								d, result[o], old[0][d]))
						if result[o] != old[0][d]:
							if o == "bibtex" and result[o] is not None:
								self.updateField(key, d,
									self.rmBibtexComments(
										self.rmBibtexACapo(result[o].strip())),
									verbose=0)
							else:
								self.updateField(key, d, result[o],
									verbose=0)
					except KeyError:
						pBLogger.exception("Key error: (%s, %s)"%(o,d))
			if verbose > 0:
				pBLogger.info("Inspire OAI info for %s saved."%inspireID)
		except KeyError:
			pBLogger.exception("Something missing in entry %s"%inspireID)
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
		match = "%"+"%s"%old+"%"
		self.lastVals = {"match": match}
		self.cursExec(self.lastQuery, self.lastVals)
		self.lastFetched = self.completeFetched(self.curs.fetchall())
		keys = [k["bibkey"] for k in self.lastFetched]
		pBLogger.info("Replacing text in entries: ", keys)
		if self.connExec(
			"UPDATE entries SET bibtex = replace( bibtex, :old, :new ) "
			+ "WHERE bibtex LIKE :match",
			{"old": old, "new": new, "match": match}):
			return keys
		else:
			return False

	def replace(self,
			fiOld, fiNews, old, news,
			entries=None, regex=False, lenEntries=1):
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
			pBLogger.warning("Invalid 'fiNews' or 'news' (they must be lists)")
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
		pBLogger.info("Replace will process %d entries"%tot)
		if tot < 1:
			tot = 1
		for ix, entry in enumerate(iterator):
			if not self.runningReplace:
				continue
			if not "bibtexDict" in entry.keys():
				entry = self.completeFetched([entry])[0]
			pBLogger.info("processing %5d / %d (%5.2f%%): entry %s"%(
				ix+1, tot, 100.*(ix+1)/tot, entry["bibkey"]))
			try:
				if not fiOld in entry["bibtexDict"].keys() \
						and not fiOld in entry.keys():
					raise KeyError("Field %s not found in entry %s"%(
						fiOld, entry["bibkey"]))
				if fiOld in entry["bibtexDict"].keys():
					before = entry["bibtexDict"][fiOld]
				elif fiOld in entry.keys():
					before = entry[fiOld]
				bef = []
				aft = []
				for fiNew, new in zip(fiNews, news):
					if not fiNew in entry["bibtexDict"].keys() \
							and not fiNew in entry.keys():
						raise KeyError("Field %s not found in entry %s"%(
							fiNew, entry["bibkey"]))
					if fiNew in entry["bibtexDict"].keys():
						bef.append(entry["bibtexDict"][fiNew])
						after = singleReplace(
							before, new, previous=entry["bibtexDict"][fiNew])
						aft.append(after)
						entry["bibtexDict"][fiNew] = after
						db = bibtexparser.bibdatabase.BibDatabase()
						db.entries = []
						db.entries.append(entry["bibtexDict"])
						entry["bibtex"] = self.rmBibtexComments(
							self.rmBibtexACapo(pbWriter.write(db).strip()))
						self.updateField(entry["bibkey"],
							"bibtex", entry["bibtex"], verbose=0)
					if fiNew in entry.keys():
						bef.append(entry[fiNew])
						after = singleReplace(before, new,
							previous=entry[fiNew])
						aft.append(after)
						self.updateField(entry["bibkey"],
							fiNew, after, verbose=0)
			except KeyError:
				pBLogger.exception("Something wrong in replace")
				failed.append(entry["bibkey"])
			else:
				success.append(entry["bibkey"])
				if any(b != a for a,b in zip(aft, bef)):
					changed.append(entry["bibkey"])
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
			element = bibtexparser.bparser.BibTexParser(common_strings=True
				).parse(bibtex).entries[0]
		except ParseException:
			pBLogger.warning("Cannot parse properly:\n%s"%bibtex)
			return ""
		except IndexError:
			pBLogger.warning("No entries found:\n%s"%bibtex)
			return ""
		for k,v in element.items():
			try:
				tmp[k] = v.replace("\n", " ")
			except AttributeError:
				pBLogger.warning(
					"Wrong type or value for field %s (%s)?"%(k, v))
				tmp[k] = v
		db.entries = [tmp]
		return pbWriter.write(db)

	def getFieldsFromArxiv(self, bibkey, fields):
		"""Use arxiv.org to retrieve more fields for the entry

		Parameters:
			bibkey: the bibtex key of the entry
			fields: the fields to be updated
				using information from arxiv.org

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
			pBLogger.info("getFieldsFromArxiv will process %d entries."%tot)
			for ix, k in enumerate(bibkey):
				arxiv = str(self.getField(k, "arxiv"))
				if self.getArxivFieldsFlag and arxiv.strip() != "":
					pBLogger.info(
						"%5d / %d (%5.2f%%) - processing: arxiv:%s\n"%(
						ix+1, tot, 100.*(ix+1)/tot, arxiv))
					result = self.getFieldsFromArxiv(k, fields)
					if result is True:
						success.append(k)
					else:
						fail.append(k)
			pBLogger.info("\n\ngetFieldsFromArxiv has finished!")
			pBLogger.info(
				"%d entries processed, "%len(success+fail)
				+ "of which these %d generated errors:\n%s"%(len(fail), fail))
			return success, fail
		if not isinstance(fields, list):
			fields = [fields]
		bibtex = self.getField(bibkey, "bibtex")
		arxiv = str(self.getField(bibkey, "arxiv"))
		if arxiv is "False" or arxiv is "None" or arxiv.strip() == "":
			return False
		try:
			arxivBibtex, arxivDict = physBiblioWeb.webSearch["arxiv"] \
				.retrieveUrlAll(arxiv, searchType="id", fullDict=True)
			tmp = bibtexparser.bparser.BibTexParser(common_strings=True
				).parse(bibtex).entries[0]
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
							authors[start : \
								start \
								+ pbConfig.params["maxAuthorSave"]] \
								+ ["others"])
				except KeyError:
					pass
			db = bibtexparser.bibdatabase.BibDatabase()
			db.entries = [tmp]
			bibtex = self.rmBibtexComments(self.rmBibtexACapo(
				pbWriter.write(db).strip()))
			self.updateField(bibkey, "bibtex", bibtex)
			return True
		except Exception:
			pBLogger.exception("Cannot get and save info from arXiv!\n")
			return False

	def loadAndInsert(self,
			entry,
			method="inspire",
			imposeKey=None,
			number=None,
			returnBibtex=False,
			childProcess=False):
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
			pBLogger.info("Already existing: %s\n"%entry)
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
			exist = (len(existing) > 0)
			for f in ["arxiv", "doi"]:
				try:
					temp = self.fetchAll(params={f: entry},
						saveQuery=False).lastFetched
					exist = (exist or (len(temp) > 0))
					existing += temp
				except KeyError:
					pBLogger.debug("Error", exc_info=True)
			if existing:
				return printExisting(entry, existing)
			if method == "bibtex":
				try:
					db = bibtexparser.bibdatabase.BibDatabase()
					db.entries = bibtexparser.bparser.BibTexParser(
						common_strings=True).parse(entry).entries
					e = self.rmBibtexComments(self.rmBibtexACapo(
						pbWriter.write(db).strip()))
				except ParseException:
					pBLogger.exception(
						"Error while reading the bibtex '%s'"%entry)
					return False
			else:
				try:
					e = physBiblioWeb.webSearch[method].retrieveUrlAll(entry)
				except KeyError:
					pBLogger.error("Method not valid: %s"%method)
					return False
			if e.count('@') > 1:
				if number is not None:
					requireAll = True
				else:
					pBLogger.warning(
						"Possible mismatch. Specify the number of element " \
						+ "to select with 'number'\n%s"%e)
					return False
			kwargs = {}
			if requireAll:
				kwargs["number"] = number
			if imposeKey is not None and imposeKey.strip() is not "":
				kwargs["bibkey"] = imposeKey
			data = self.prepareInsert(e, **kwargs)
			key = data["bibkey"]
			if key.strip() == "":
				pBLogger.error(
					"Impossible to insert an entry with empty bibkey!\n"
					+ "%s\n"%entry)
				return False
			existing = self.getByBibkey(key, saveQuery=False)
			exist = (len(existing) > 0)
			for f in ["arxiv", "doi"]:
				try:
					if data[f] is not None \
							and isinstance(data[f], six.string_types) \
							and data[f].strip() != "":
						temp = self.fetchAll(params={f: data[f]},
							saveQuery=False).lastFetched
						exist = (exist or (len(temp) > 0))
						existing += temp
				except (AttributeError, KeyError):
					pBLogger.debug("Error", exc_info=True)
			if existing:
				return printExisting(key, existing)
			pBLogger.info("Entry will have key: '%s'"%key)
			if pbConfig.params["fetchAbstract"] and data["arxiv"] is not "":
				arxivBibtex, arxivDict = physBiblioWeb.webSearch["arxiv"]\
					.retrieveUrlAll(data["arxiv"],
						searchType="id",
						fullDict=True)
				data["abstract"] = arxivDict["abstract"]
			try:
				self.insert(data)
			except:
				pBLogger.exception("Failed in inserting entry %s\n"%entry)
				return False
			try:
				self.mainDB.catBib.insert(
					pbConfig.params["defaultCategories"], key)
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
				pBLogger.info("Element successfully inserted.\n")
				self.lastInserted.append(key)
				if returnBibtex:
					return e
				else:
					return True
			except:
				pBLogger.warning(
					"Failed in completing info for entry %s\n"%entry)
				return False
		elif entry is not None and isinstance(entry, list):
			failed = []
			entry = returnListIfSub(entry, [])
			self.runningLoadAndInsert = True
			tot = len(entry)
			pBLogger.info("LoadAndInsert will process %d total entries"%tot)
			ix = 0
			for e in entry:
				if isinstance(e, float):
					e = str(e)
				if self.runningLoadAndInsert:
					pBLogger.info(
						"%5d / %d (%5.2f%%) - looking for string: '%s'\n"%(
						ix+1, tot, 100.*(ix+1)/tot, e))
					if not self.loadAndInsert(e, childProcess=True):
						failed.append(e)
					ix += 1
			if len(self.lastInserted) > 0:
				pBLogger.info(
					"Imported entries:\n%s"%", ".join(self.lastInserted))
			if len(failed) > 0:
				pBLogger.warning(
					"ERRORS!\nFailed to load and import entries:\n%s"%(
					", ".join(failed)))
			return True
		else:
			pBLogger.error("Invalid arguments!")
			return False

	def loadAndInsertWithCats(self,
			entry,
			method="inspire",
			imposeKey=None,
			number=None,
			returnBibtex=False,
			childProcess=False):
		"""Load the entries, then ask for their categories.
		Uses self.loadAndInsert and self.mainDB.catBib.askCats

		Parameters: see self.loadAndInsert
		"""
		self.loadAndInsert(entry,
			method=method,
			imposeKey=imposeKey,
			number=number,
			returnBibtex=returnBibtex,
			childProcess=childProcess)
		for key in self.lastInserted:
			self.mainDB.catBib.delete(
				pbConfig.params["defaultCategories"], key)
		self.mainDB.catBib.askCats(self.lastInserted)

	def importFromBib(self, filename, completeInfo=True):
		"""Read a .bib file and add the contained entries in the database

		Parameters:
			filename: the name of the .bib file
			completeInfo (boolean, default True): use the bibtex key
				and other fields to look for more information online
		"""
		def printExisting(entry):
			"""Print a message when the entry is
			already present in the database

			Parameters:
				entry: the entry key
			"""
			pBLogger.info("Already existing: %s\n"%entry)

		self.lastInserted = []
		exist = []
		errors = []

		def parseSingle(text):
			"""Parse the text corresponding to an entry and returns
			the list of parsed entries from `bibtexparser`.
			If an exception occurs, return an empty list

			Parameter:
				text: the text to be processed

			Output:
				a list
			"""
			pBLogger.debug("Processing:\n%s"%text)
			if text.strip() == "":
				pBLogger.warning("Impossible to parse empty text!")
				return []
			bp = bibtexparser.bparser.BibTexParser(common_strings=True)
			try:
				return bp.parse(text).entries
			except ParseException:
				errors.append(text)
				pBLogger.exception("Impossible to parse text:\n%s"%text)
				return []

		pBLogger.info("Importing from file bib: %s"%filename)
		with open(filename) as r:
			fullBibText = r.read()
		bibText = ""
		elements = []
		for line in fullBibText:
			if "@" in line:
				elements += parseSingle(bibText)
				bibText = line
			else:
				bibText += line
		elements += parseSingle(bibText)
		db = bibtexparser.bibdatabase.BibDatabase()
		self.importFromBibFlag = True
		pBLogger.info("Entries to be processed: %d"%len(elements))
		tot = len(elements)
		for ie, e in enumerate(elements):
			if self.importFromBibFlag and e != []:
				db.entries = [e]
				bibtex = self.rmBibtexComments(self.rmBibtexACapo(
					pbWriter.write(db).strip()))
				data = self.prepareInsert(bibtex)
				key = data["bibkey"]
				pBLogger.info("%5d / %d (%5.2f%%), processing entry %s"%(
					ie+1, tot, 100.*(ie+1.)/tot, key))
				existing = self.getByBibkey(key, saveQuery=False)
				if existing:
					printExisting(key)
					exist.append(key)
				elif key.strip() == "":
					pBLogger.warning(
						"Impossible to insert an entry with empty bibkey!\n")
					errors.append(key)
				else:
					if completeInfo and pbConfig.params["fetchAbstract"] \
							and data["arxiv"] is not "":
						arxivBibtex, arxivDict = physBiblioWeb\
							.webSearch["arxiv"].retrieveUrlAll(
							data["arxiv"], searchType="id", fullDict=True)
						data["abstract"] = arxivDict["abstract"]
					pBLogger.info("Entry will have key: '%s'"%key)
					if not self.insert(data):
						pBLogger.warning("Failed in inserting entry %s\n"%key)
						errors.append(key)
					else:
						self.mainDB.catBib.insert(
							pbConfig.params["defaultCategories"], key)
						try:
							if completeInfo:
								eid = self.updateInspireID(key)
								self.updateInfoFromOAI(eid)
							pBLogger.info("Element successfully inserted.\n")
							self.lastInserted.append(key)
						except Exception:
							pBLogger.exception(
								"Failed in completing info for entry %s\n"%key)
							errors.append(key)
		pBLogger.info("Import completed.\n"
			+ "%d entries processed, of which %d existing, "%(
				len(elements), len(exist))
			+ "%d successfully inserted and %d errors."%(
				len(self.lastInserted), len(errors)))

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
			print("%4d - %s\n"%(i, e["bibtex"]))
		if entriesIn is not None:
			for i, e in enumerate(entriesIn):
				_print(i, e)
				total += 1
		else:
			self.fetchAll(orderBy="firstdate", doFetch=False)
			for i, e in enumerate(self.fetchCursor()):
				_print(i, e)
				total += 1
		pBLogger.info("%d elements found"%total)

	def printAllBibkeys(self, entriesIn=None):
		"""Print the bibtex keys for all the entries
		(or for a given subset)

		Parameters:
			entriesIn: the list of entries to print.
				If None, use self.lastFetched or self.getAll.
		"""
		total = 0
		def _print(i, e):
			print("%4d %s"%(i, e["bibkey"]))
		if entriesIn is not None:
			for i, e in enumerate(entriesIn):
				_print(i, e)
				total += 1
		else:
			self.fetchAll(orderBy="firstdate", doFetch=False)
			for i, e in enumerate(self.fetchCursor()):
				_print(i, e)
				total += 1
		pBLogger.info("%d elements found"%total)

	def printAllInfo(self,
			entriesIn=None,
			orderBy="firstdate",
			addFields=None):
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
			orderDate = "[%4d - %-11s]"%(i, e["firstdate"])
			bibKeyStr = "%-30s "%e["bibkey"]
			typeStr = ""
			moreStr = "%-20s %-20s"%(
				e["arxiv"] if e["arxiv"] is not None else "-",
				e["doi"] if e["doi"] is not None else "-"
				)
			if e["book"] == 1:
				typeStr = "(book)"
				moreStr = "%-20s"%e["isbn"]
			elif e["review"] == 1:
				typeStr = "(rev)"
			elif e["lecture"] == 1:
				typeStr = "(lect)"
			elif e["phd_thesis"] == 1:
				typeStr = "(PhDTh)"
				moreStr = "%-20s"%(
					e["arxiv"] if e["arxiv"] is not None else "-")
			elif e["proceeding"] == 1:
				typeStr = "(proc)"
			print(orderDate + "%7s "%typeStr + bibKeyStr + moreStr)
			if addFields is not None:
				try:
					if isinstance(addFields, list):
						for f in addFields:
							try:
								print("   %s: %s"%(f, e[f]))
							except:
								print("   %s: %s"%(f, e["bibtexDict"][f]))
					else:
						try:
							print("   %s: %s"%(addFields, e[addFields]))
						except:
							print("   %s: %s"%(
								addFields, e["bibtexDict"][addFields]))
				except:
					pass
		pBLogger.info("%d elements found"%total)

	def fetchByCat(self,
			idCat,
			orderBy="entries.firstdate",
			orderType="ASC"):
		"""Fetch all the entries associated to a given category

		Parameters:
			idCat: the id of the category
			orderBy (default "entries.firstdate"):
				the "table.field" to use for ordering
			orderType: "ASC" (default) or "DESC"

		Output:
			self
		"""
		query = "select * from entries " \
			+ "join entryCats on entries.bibkey=entryCats.bibkey " \
			+ "where entryCats.idCat=?"
		query += " order by " + orderBy + " " + orderType if orderBy else ""
		self.cursExec(query, (idCat,))
		fetched_in = self.curs.fetchall()
		fetched_out = []
		for el in fetched_in:
			tmp = {}
			for k in el.keys():
				tmp[k] = el[k]
			tmp["bibtexDict"] = bibtexparser.bparser.BibTexParser(
				common_strings=True).parse(el["bibtex"]).entries[0]
			fetched_out.append(tmp)
		self.lastFetched = fetched_out
		return self

	def getByCat(self,
			idCat,
			orderBy="entries.firstdate",
			orderType="ASC"):
		"""Use self.fetchByCat and returns
		the dictionary of fetched entries

		Parameters: see self.fetchByCat

		Output:
			a dictionary
		"""
		return self.fetchByCat(idCat,
			orderBy=orderBy, orderType=orderType).lastFetched

	def fetchByExp(self,
			idExp,
			orderBy="entries.firstdate",
			orderType="ASC"):
		"""Fetch all the entries associated to a given experiment

		Parameters:
			idExp: the id of the experiment
			orderBy (default "entries.firstdate"):
				the "table.field" to use for ordering
			orderType: "ASC" (default) or "DESC"

		Output:
			self
		"""
		query = "select * from entries " \
			+ "join entryExps on entries.bibkey=entryExps.bibkey " \
			+ "where entryExps.idExp=?"
		query += " order by " + orderBy + " " + orderType if orderBy else ""
		self.cursExec(query, (idExp,))
		fetched_in = self.curs.fetchall()
		fetched_out = []
		for el in fetched_in:
			tmp = {}
			for k in el.keys():
				tmp[k] = el[k]
			tmp["bibtexDict"] = bibtexparser.bparser.BibTexParser(
				common_strings=True).parse(el["bibtex"]).entries[0]
			fetched_out.append(tmp)
		self.lastFetched = fetched_out
		return self

	def getByExp(self,
			idExp,
			orderBy="entries.firstdate",
			orderType="ASC"):
		"""Use self.fetchByExp and returns
		the dictionary of fetched entries

		Parameters: see self.fetchByExp

		Output:
			a dictionary
		"""
		return self.fetchByExp(idExp,
			orderBy=orderBy, orderType=orderType).lastFetched

	def cleanBibtexs(self, startFrom=0, entries=None):
		"""Clean (remove comments, unwanted fields, newlines, accents)
		and reformat the bibtexs

		Parameters:
			startFrom (default 0): the index where to start from
			entries: the list of entries to be considered.
				If None, the output of self.getAll

		Output:
			num, err, changed:
				the number of considered entries,
				the number of errors,
				the list of keys of changed entries
		"""
		if entries is None:
			try:
				tot = self.count() - startFrom
				self.fetchAll(saveQuery=False,
					limitTo=tot, limitOffset=startFrom, doFetch=False)
				iterator = self.fetchCursor()
			except TypeError:
				pBLogger.exception("Invalid startFrom in cleanBibtexs")
				return 0, 0, []
		else:
			iterator = entries
			tot = len(entries)
		num = 0
		err = 0
		changed = []
		self.runningCleanBibtexs = True
		pBLogger.info("CleanBibtexs will process %d total entries"%tot)
		db = bibtexparser.bibdatabase.BibDatabase()
		for ix, e in enumerate(iterator):
			if self.runningCleanBibtexs:
				num += 1
				pBLogger.info("%5d / %d (%5.2f%%) - cleaning: '%s'\n"%(
					ix+1, tot, 100.*(ix+1)/tot, e["bibkey"]))
				for field in ["marks", "old_keys"]:#convert None to "" for given fields
					if e[field] is None:
						self.updateField(e["bibkey"], field, "")
				if e["marks"] is not None and "'" in e["marks"]:
					marks = e["marks"].replace("'", "").split(",")
					newmarks = []
					for m in marks:
						if m not in newmarks:
							newmarks.append(m)
					self.updateField(e["bibkey"],
						"marks", ",".join(newmarks))
				try:
					element = bibtexparser.bparser.BibTexParser(
						common_strings=True).parse(e["bibtex"]).entries[0]
					db.entries = []
					db.entries.append(element)
					newbibtex = self.rmBibtexComments(self.rmBibtexACapo(
						parse_accents_str(pbWriter.write(db).strip())))
					if e["bibtex"] != newbibtex and self.updateField(
							e["bibkey"], "bibtex", newbibtex):
						pBLogger.info("-- element changed!")
						changed.append(e["bibkey"])
				except (ValueError, ParseException):
					pBLogger.warning(
						"Error while cleaning entry '%s'"%e["bibkey"],
						exc_info=True)
					err += 1
		pBLogger.info("%d entries processed"%num)
		pBLogger.info("%d errors occurred"%err)
		pBLogger.info("%d bibtex entries changed"%len(changed))
		return num, err, changed

	def findCorruptedBibtexs(self, startFrom=0, entries=None):
		"""Find bibtexs that cannot be read properly

		Parameters:
			startFrom (default 0): the index where to start from
			entries: the list of entries to be considered.
				If None, the output of self.getAll

		Output:
			bibtexs: the list of problematic entries
		"""
		if entries is None:
			try:
				tot = self.count() - startFrom
				self.fetchAll(saveQuery=False,
					limitTo=tot, limitOffset=startFrom, doFetch=False)
				iterator = self.fetchCursor()
			except TypeError:
				pBLogger.exception("Invalid startFrom in cleanBibtexs")
				return 0, 0, []
		else:
			iterator = entries
			tot = len(entries)
		bibtexs = []
		self.runningFindBadBibtexs = True
		pBLogger.info("findCorruptedBibtexs will process %d total entries"%tot)
		db = bibtexparser.bibdatabase.BibDatabase()
		for ix, e in enumerate(iterator):
			if self.runningFindBadBibtexs:
				pBLogger.info("%5d / %d (%5.2f%%) - processing: '%s'"%(
					ix+1, tot, 100.*(ix+1)/tot, e["bibkey"]))
				try:
					element = bibtexparser.bparser.BibTexParser(
						common_strings=True).parse(e["bibtex"]).entries[0]
					pBLogger.info("%s is readable.\n"%element["ID"])
				except:
					bibtexs.append(e["bibkey"])
					pBLogger.warning("%s is NOT readable!\n"%e["bibkey"])
		pBLogger.info("%d bad entries found:\n %s"%(len(bibtexs), bibtexs))
		return bibtexs

	def searchOAIUpdates(self,
			startFrom=0, entries=None, force=False, reloadAll=False):
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

		Output:
			num, err, changed:
				the number of processed entries,
				the list of errors and
				of changed entries
		"""
		if entries is None:
			try:
				tot = self.count() - startFrom
				self.fetchAll(saveQuery=False,
					limitTo=tot, limitOffset=startFrom, doFetch=False)
				iterator = self.fetchCursor()
			except TypeError:
				pBLogger.exception("Invalid startFrom in searchOAIUpdates")
				return 0, [], []
		else:
			iterator = entries
			tot = len(entries)
		num = 0
		err = []
		changed = []
		self.runningOAIUpdates = True
		pBLogger.info("SearchOAIUpdates will process %d total entries"%tot)
		for ix, e in enumerate(iterator):
			if not "bibtexDict" in e.keys():
				e = self.completeFetched([e])[0]
			if self.runningOAIUpdates \
					and ( e["proceeding"] == 0 or force ) \
					and e["book"] == 0 \
					and e["lecture"] == 0 \
					and e["phd_thesis"] == 0 \
					and e["noUpdate"] == 0 \
					and e["inspire"] is not None \
					and e["inspire"] != "" \
					and (force or ( e["doi"] is None \
						or "journal" not in e["bibtexDict"].keys() ) ):
				num += 1
				pBLogger.info(
					"%5d / %d (%5.2f%%) - looking for update: '%s'"%(
					ix+1, tot, 100.*(ix+1)/tot, e["bibkey"]))
				if not self.updateInfoFromOAI(e["inspire"],
						bibtex=e["bibtex"],
						verbose=0,
						readConferenceTitle=(e["proceeding"] == 1 and force),
						reloadAll=reloadAll,
						originalKey=e["bibkey"]):
					err.append(e["bibkey"])
				else:
					try:
						new = self.getByKey(e["bibkey"], saveQuery=False)[0]
					except IndexError:
						try:
							e["bibkey"] = self.newKey
							del self.newKey
							new = self.getByKey(e["bibkey"],
								saveQuery=False)[0]
						except (AttributeError, IndexError):
							pBLogger.exception(
								"Something wrong here. "
								+ "Possibly the bibtex key has been changed "
								+ "while processing entry '%s'?"%e["bibkey"])
							err.append(e["bibkey"])
							continue
					if e != new:
						pBLogger.info("-- element changed!")
						for diff in list(dictdiffer.diff(e, new)):
							pBLogger.info(diff)
						changed.append(e["bibkey"])
				pBLogger.info("")
		pBLogger.info("%d entries processed"%num)
		pBLogger.info("%d errors occurred"%len(err))
		if len(err)>0:
			pBLogger.info(err)
		pBLogger.info("%d entries changed"%len(changed))
		if len(changed)>0:
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
					pBLogger.info("Cleaning (%s, %s)"%(e[0], e[1]))
					func(e[0], e[1])

		self.mainDB.bibs.fetchAll(saveQuery=False, doFetch=False)
		bibkeys = [e["bibkey"] for e in self.mainDB.bibs.fetchCursor()]
		idCats = [e["idCat"] for e in self.mainDB.cats.getAll()]
		idExps = [e["idExp"] for e in self.mainDB.exps.getAll()]

		deletePresent(bibkeys, idExps,
			[[e["bibkey"], e["idExp"]] for e in self.mainDB.bibExp.getAll()],
			self.mainDB.bibExp.delete)
		deletePresent(idCats, bibkeys,
			[[e["idCat"], e["bibkey"]] for e in self.mainDB.catBib.getAll()],
			self.mainDB.catBib.delete)
		deletePresent(idCats, idExps,
			[[e["idCat"], e["idExp"]] for e in self.mainDB.catExp.getAll()],
			self.mainDB.catExp.delete)

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
		pBLogger.warning("Category '%s' not in database"%idCat)
		return ""
	if withDesc:
		return '%4d: %s - <i>%s</i>'%(
			cat['idCat'], cat['name'], cat['description'])
	else:
		return '%4d: %s'%(cat['idCat'], cat['name'])


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
			pBLogger.warning("Category '%s' not in database"%i)
	decorated = [ (x["name"].lower(), x) for x in listIn ]
	decorated.sort()
	return [ x[1]["idCat"] for x in decorated ]


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
