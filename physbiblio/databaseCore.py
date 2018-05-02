"""
Module that manages the actions on the database (and few more).

This file is part of the physbiblio package.
"""
import sqlite3
from sqlite3 import OperationalError, ProgrammingError, DatabaseError, InterfaceError
import os

try:
	import physbiblio.tablesDef
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
	print(traceback.format_exc())
	raise

encoding_default = 'iso-8859-15'

class physbiblioDBCore():
	"""
	Contains most of the basic functions on the database.
	Will be subclassed to do everything else.
	"""
	def __init__(self, dbname, logger, noOpen = False):
		"""
		Initialize database class (column names, descriptions) and opens the database.

		Parameters:
			dbname: the name of the database to be opened
		"""
		#structure of the tables
		self.tableFields = physbiblio.tablesDef.tableFields
		self.descriptions = physbiblio.tablesDef.fieldsDescriptions
		#names of the columns
		self.tableCols = {}
		for q in self.tableFields.keys():
			self.tableCols[q] = [ a[0] for a in self.tableFields[q] ]

		self.dbChanged = False
		self.conn = None
		self.curs = None
		self.dbname = dbname
		self.logger = logger
		db_is_new = not os.path.exists(self.dbname)

		if not noOpen:
			self.openDB()
			self.cursExec("SELECT name FROM sqlite_master WHERE type='table';")
			if db_is_new or sorted([name[0] for name in self.curs]) != ["categories", "entries", "entryCats", "entryExps", "expCats", "experiments"]:
				self.logger.info("-------New database. Creating tables!\n\n")
				self.createTables()

		# self.cursExec("ALTER TABLE entries ADD COLUMN abstract TEXT")

		self.lastFetched = None
		self.catsHier = None

		self.loadSubClasses()


	def openDB(self):
		"""
		Open the database and creates the self.conn (connection) and self.curs (cursor) objects.

		Output:
			True if successfull
		"""
		self.logger.info("Opening database: %s"%self.dbname)
		self.conn = sqlite3.connect(self.dbname, check_same_thread=False)
		self.conn.row_factory = sqlite3.Row
		self.curs = self.conn.cursor()
		self.loadSubClasses()
		return True

	def reOpenDB(self, newDB = None):
		"""
		Close the currently open database and open a new one (the same if newDB is None).

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
			self.cursExec("SELECT name FROM sqlite_master WHERE type='table';")
			if db_is_new or sorted([name[0] for name in self.curs]) != ["categories", "entries", "entryCats", "entryExps", "expCats", "experiments"]:
				self.logger.info("-------New database. Creating tables!\n\n")
				self.createTables()

			self.lastFetched = None
			self.catsHier = None
		else:
			self.closeDB()
			self.openDB()
			self.cursExec("SELECT name FROM sqlite_master WHERE type='table';")
			if sorted([name[0] for name in self.curs]) != ["categories", "entries", "entryCats", "entryExps", "expCats", "experiments"]:
				self.logger.info("-------New database. Creating tables!\n\n")
				self.createTables()
			self.lastFetched = None
			self.catsHier = None
		return True

	def closeDB(self):
		"""
		Close the database.
		"""
		self.logger.info("Closing database...")
		self.conn.close()
		return True

	def checkUncommitted(self):
		"""
		Check if there are uncommitted changes.

		Output:
			True/False
		"""
		#return self.conn.in_transaction() #works only with sqlite > 3.2...
		return self.dbChanged

	def commit(self, verbose = True):
		"""
		Commit the changes.

		Output:
			True if successfull, False if an exception occurred
		"""
		try:
			self.conn.commit()
			self.dbChanged = False
			if verbose:
				self.logger.info("Database saved.")
			return True
		except Exception:
			self.logger.exception("Impossible to commit!")
			return False

	def undo(self, verbose = True):
		"""
		Undo the uncommitted changes and roll back to the last commit.

		Output:
			True if successfull, False if an exception occurred
		"""
		try:
			self.conn.rollback()
			self.dbChanged = False
			if verbose:
				self.logger.info("Rolled back to last commit.")
			return True
		except Exception:
			self.logger.exception("Impossible to rollback!")
			return False
		
	def connExec(self, query, data = None):
		"""
		Execute connection.

		Parameters:
			query (string): the query to be executed
			data (dictionary or list): the values of the parameters in the query

		Output:
			True if successfull, False if an exception occurred
		"""
		try:
			if data:
				self.conn.execute(query,data)
			else:
				self.conn.execute(query)
		except (OperationalError, ProgrammingError, DatabaseError, InterfaceError) as err:
			self.logger.exception('Connection error: %s\nquery: %s'%(err, query))
			return False
		else:
			self.dbChanged = True
			return True

	def cursExec(self, query, data = None):
		"""
		Execute cursor.

		Parameters:
			query (string): the query to be executed
			data (dictionary or list): the values of the parameters in the query

		Output:
			True if successfull, False if an exception occurred
		"""
		try:
			if data:
				self.curs.execute(query,data)
			else:
				self.curs.execute(query)
		except Exception as err:
			self.logger.exception('Cursor error: %s\nThe query was: "%s"\n and the parameters: %s'%(err, query, data))
			return False
		else:
			return True

	def cursor(self):
		return self.curs

	def createTables(self):
		"""
		Create tables for the database (and insert the default categories), if it is missing.
		"""
		for q in self.tableFields.keys():
			command="CREATE TABLE "+q+" (\n"
			first=True
			for el in self.tableFields[q]:
				if first:
					first=False
				else:
					command+=",\n"
				command+=" ".join(el)
			command+=");"
			self.logger.info(command+"\n")
			if not self.connExec(command):
				self.logger.critical("Create %s failed"%q)
		command="""
		INSERT into categories (idCat, name, description, parentCat, ord)
			values (0,"Main","This is the main category. All the other ones are subcategories of this one",0,0),
			(1,"Tags","Use this category to store tags (such as: ongoing projects, temporary cats,...)",0,0)
			"""
		self.logger.info(command+"\n")
		if not self.connExec(command):
			self.logger.exception("Insert main categories failed")
		self.commit()
