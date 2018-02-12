import sqlite3
import os, re, traceback, datetime
import bibtexparser
import ast
import physbiblio.webimport.webInterf as webInt
import time

try:
	from physbiblio.config import pbConfig
	from physbiblio.bibtexwriter import pbWriter
	from physbiblio.errors import pBErrorManager
	import physbiblio.parse_accents as parse_accents
	import physbiblio.firstOpen as pbfo
	from physbiblio.webimport.webInterf import physBiblioWeb
	import physbiblio.tablesDef
	from physbiblio.parse_accents import *
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")

encoding_default = 'iso-8859-15'
parser = bibtexparser.bparser.BibTexParser()
parser.encoding = encoding_default
parser.customization = parse_accents.parse_accents_record
parser.alt_dict = {}

class physbiblioDB():
	"""
	Contains most of the basic DB functions
	"""
	def __init__(self, dbname = pbConfig.params['mainDatabaseName']):
		"""
		Initialize DB class
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
		db_is_new = not os.path.exists(self.dbname)
		self.openDB()
		if db_is_new:
			print("-------New database. Creating tables!\n\n")
			pbfo.createTables(self)
		
		# self.cursExec("ALTER TABLE entries ADD COLUMN abstract TEXT")

		self.lastFetched = None
		self.catsHier = None

	def reOpenDB(self, newDB = None):
		if newDB is not None:
			self.closeDB()
			del self.conn
			del self.curs
			self.dbname = newDB
			db_is_new = not os.path.exists(self.dbname)
			#time.sleep(2)
			self.openDB()
			if db_is_new:
				print("-------New database. Creating tables!\n\n")
				pbfo.createTables(self)

			self.lastFetched = None
			self.catsHier = None
			self.loadSubClasses()

	def checkUncommitted(self):
		#return self.conn.in_transaction() #works only with sqlite > 3.2...
		return self.dbChanged

	def openDB(self):
		"""open the database"""
		print("[DB] Opening database: %s"%self.dbname)
		self.conn = sqlite3.connect(self.dbname, check_same_thread=False)
		self.conn.row_factory = sqlite3.Row
		self.curs = self.conn.cursor()

	def closeDB(self):
		"""close the database"""
		print("[DB] Closing database...")
		self.conn.close()

	def commit(self):
		"""commit the changes"""
		self.conn.commit()
		self.dbChanged = False
		print("[DB] saved.")

	def undo(self):
		"""undo the uncommitted changes"""
		self.conn.rollback()
		print("[DB] rolled back to last commit.")
		
	def connExec(self,query,data=None):
		"""execute connection"""
		try:
			if data:
				self.conn.execute(query,data)
			else:
				self.conn.execute(query)
		except Exception, err:
			print('[connExec] ERROR: %s'%err)
			print(traceback.format_exc())
			self.conn.rollback()
			return False
		else:
			self.dbChanged = True
			return True

	def cursExec(self,query,data=None):
		"""execute cursor"""
		try:
			if data:
				self.curs.execute(query,data)
			else:
				self.curs.execute(query)
		except Exception, err:
			print('[cursExec] ERROR: %s'%err)
			return False
		else:
			return True
	
	def loadSubClasses(self):
		try:
			del self.bibs
			del self.cats
			del self.exps
			del self.bibExp
			del self.catBib
			del self.catExp
			del self.utils
		except:
			pass
		self.utils = utilities()
		self.bibs = entries()
		self.cats = categories()
		self.exps = experiments()
		self.bibExp = entryExps()
		self.catBib = catsEntries()
		self.catExp = catsExps()

pBDB=physbiblioDB()

class physbiblioDBSub():
	"""
	Uses physbiblioDB instance 'pBDB' to act on the database.
	All the subcategories of physbiblioDB are defined starting from this one.
	"""
	def __init__(self):
		"""
		Initialize DB class
		"""
		#structure of the tables
		self.tableFields = physbiblio.tablesDef.tableFields
		#names of the columns
		self.tableCols = {}
		for q in self.tableFields.keys():
			self.tableCols[q] = [ a[0] for a in self.tableFields[q] ]

		self.conn = pBDB.conn
		self.curs = pBDB.curs
		self.dbname = pBDB.dbname

		self.lastFetched = None
		self.catsHier = None

	def closeDB(self):
		"""close the database"""
		pBDB.closeDB()

	def commit(self):
		"""commit the changes"""
		pBDB.commit()

	def connExec(self,query,data=None):
		"""execute connection"""
		return pBDB.connExec(query, data = data)

	def cursExec(self,query,data=None):
		"""execute cursor"""
		return pBDB.cursExec(query, data = data)

class categories(physbiblioDBSub):
	"""functions for categories"""
	def insert(self, data):
		"""new category"""
		self.cursExec("""
			select * from categories where name=? and parentCat=?
			""", (data["name"], data["parentCat"]))
		if self.curs.fetchall():
			print("An entry with the same name is already present in the same category!")
			return False
		else:
			return self.connExec("""
				INSERT into categories (name, description, parentCat, comments, ord)
					values (:name, :description, :parentCat, :comments, :ord)
				""", data)

	def update(self, data, idCat):
		"""update"""
		data["idCat"] = idCat
		print(data)
		query = "replace into categories (" +\
					", ".join(data.keys()) + ") values (:" + \
					", :".join(data.keys()) + ")\n"
		return self.connExec(query, data)

	def updateField(self, idCat, field, value):
		"""update only a field"""
		print("[DB] updating '%s' for entry '%s'"%(field, key))
		if field in self.tableCols["categories"] and field is not "idCat" \
				and value is not "" and value is not None:
			query = "update categories set " + field + "=:field where idCat=:idCat\n"
			return self.connExec(query, {"field": value, "idCat": idCat})
		else:
			return False

	def getAll(self):
		"""get all the categories"""
		self.cursExec("""
		select * from categories
		""")
		return self.curs.fetchall()

	def getByID(self, idCat):
		"""get category matching the idCat"""
		self.cursExec("""
			select * from categories where idCat=?
			""", (idCat, ))
		return self.curs.fetchall()

	def getDictByID(self, idCat):
		"""get category matching the idCat, return a dictionary"""
		self.cursExec("""
			select * from categories where idCat=?
			""", (idCat, ))
		try:
			entry = self.curs.fetchall()[0]
			catDict = {}
			for i,k in enumerate(self.tableCols["categories"]):
				catDict[k] = entry[i]
		except:
			print("[DB] Error in extracting category by idCat")
			catDict = None
		return catDict

	def getByName(self,name):
		self.cursExec("""
		select * from categories where name=?
		""", (name,))
		return self.curs.fetchall()

	def getChild(self, parent):
		"""get subdirectories of a given one"""
		self.cursExec("""
		select cats1.*
		from categories as cats
		join categories as cats1 on cats.idCat=cats1.parentCat
		where cats.idCat=?
		""", (parent, ))
		return self.curs.fetchall()

	def getParent(self, child):
		"""get parent directory of a given one"""
		self.cursExec("""
		select cats.*
		from categories as cats
		join categories as cats1 on cats.idCat=cats1.parentCat
		where cats1.idCat=?
		""", (child, ))
		return self.curs.fetchall()

	def getHier(self, cats = None, startFrom = 0, replace = True):
		"""get categories and subcategories in a tree-like structure"""
		if self.catsHier is not None and not replace:
			return self.catsHier
		if cats is None:
			cats = self.getAll()
		def addSubCats(idC):
			tmp = {}
			for c in [ a for a in cats if a["parentCat"] == idC and a["idCat"] != 0 ]:
				tmp[c["idCat"]] = addSubCats(c["idCat"])
			return tmp
		catsHier = {}
		catsHier[startFrom] = addSubCats(startFrom)
		self.catsHier = catsHier
		return catsHier

	def printHier(self, startFrom = 0, sp = 5*" ", withDesc = False, depth = 10, replace = False):
		"""print categories and subcategories in a tree-like form"""
		cats = self.getAll()
		if depth < 2:
			print("[DB] invalid depth in printCatHier (must be greater than 2)")
			depth = 10
		catsHier = self.getHier(cats, startFrom=startFrom, replace = replace)
		def printSubGroup(tree, indent = "", startDepth = 0):
			if startDepth <= depth:
				for l in cats_alphabetical(tree.keys()):
					print(indent + catString(l))
					printSubGroup(tree[l], (startDepth + 1) * sp, startDepth + 1)
		printSubGroup(catsHier)

	def delete(self, idCat, name = None):
		"""delete a category, its subcategories and all their connections"""
		if type(idCat) is list:
			for c in idCat:
				self.delete(c)
		else:
			if idCat < 2 and name:
				result = self.extractCatByName(name)
				idCat = result[0]["idCat"]
			if idCat < 2:
				print("[DB] Error: should not delete the category with id: %d%s.)"%(idCat, " (name: %s)"%name if name else ""))
				return false
			print("[DB] using idCat=%d"%idCat)
			self.cursExec("""
			delete from categories where idCat=?
			""", (idCat, ))
			self.cursExec("""
			delete from expCats where idCat=?
			""", (idCat, ))
			self.cursExec("""
			delete from entryCats where idCat=?
			""", (idCat, ))
			print("[DB] looking for child categories")
			for row in self.getChild(idCat):
				self.deleteCat(row["idCat"])

	def getByEntry(self, key):
		"""find all the categories for a given entry"""
		self.cursExec("""
				select * from categories
				join entryCats on categories.idCat=entryCats.idCat
				where entryCats.bibkey=?
				""", (key,))
		return self.curs.fetchall()

	def getByExp(self, idExp):
		"""find all the categories for a given experiment"""
		self.cursExec("""
				select * from categories
				join expCats on categories.idCat=expCats.idCat
				where expCats.idExp=?
				""", (idExp,))
		return self.curs.fetchall()

pBDB.cats = categories()

class catsEntries(physbiblioDBSub):
	"""functions for connecting categories and entries"""
	def getOne(self, idCat, key):
		"""fine connection"""
		self.cursExec("""
				select * from entryCats where bibkey=:bibkey and idCat=:idCat
				""",
				{"bibkey": key, "idCat": idCat})
		return self.curs.fetchall()

	def getAll(self):
		"""get all the connections"""
		self.cursExec("""
				select * from entryCats
				""")
		return self.curs.fetchall()

	def insert(self, idCat, key):
		"""create a new connection"""
		if type(idCat) is list:
			for q in idCat:
				self.insert(q, key)
		elif type(key) is list:
			for q in key:
				self.insert(idCat, q)
		else:
			if len(self.getOne(idCat, key))==0:
				return self.connExec("""
						INSERT into entryCats (bibkey, idCat) values (:bibkey, :idCat)
						""",
						{"bibkey": key, "idCat": idCat})
			else:
				print("[DB] entryCat already present: (%d, %s)"%(idCat, key))
				return False

	def delete(self, idCat, key):
		"""delete connection"""
		if type(idCat) is list:
			for q in idCat:
				self.delete(q, key)
		elif type(key) is list:
			for q in key:
				self.delete(idCat, q)
		else:
			return self.connExec("""
					delete from entryCats where bibkey=:bibkey and idCat=:idCat
					""",
					{"bibkey": key, "idCat": idCat})

	def updateBibkey(self, new, old):
		"""update if there is a bibkey change"""
		print("[DB] updating entryCats for bibkey change, from '%s' to '%s'"%(old, new))
		query = "update entryCats set bibkey=:new where bibkey=:old\n"
		return self.connExec(query, {"new": new, "old": old})

	def askCats(self, keys):
		"""loop over given keys and ask for the cats to be saved"""
		if type(keys) is not list:
			keys = [keys]
		for k in keys:
			string = raw_input("categories for '%s': "%k)
			try:
				cats = ast.literal_eval("["+string.strip()+"]")
				self.insert(cats, k)
			except:
				print("[DB] something failed in reading your input")

	def askKeys(self, cats):
		"""loop over given cats and ask for the entries to be saved"""
		if type(cats) is not list:
			cats = [cats]
		for c in cats:
			string = raw_input("entries for '%d': "%c)
			try:
				keys = ast.literal_eval("["+string.strip()+"]")
				self.insert(c, keys)
			except:
				print("[DB] something failed in reading your input")

pBDB.catBib = catsEntries()

class catsExps(physbiblioDBSub):
	"""functions for connecting categories and entries"""
	def getOne(self, idCat, idExp):
		"""get one connection"""
		self.cursExec("""
				select * from expCats where idExp=:idExp and idCat=:idCat
				""",
				{"idExp": idExp, "idCat": idCat})
		return self.curs.fetchall()

	def getAll(self):
		"""find all the connections"""
		self.cursExec("""
				select * from expCats
				""")
		return self.curs.fetchall()

	def insert(self, idCat, idExp):
		"""insert a new connection"""
		if type(idCat) is list:
			for q in idCat:
				self.insert(q, idExp)
		elif type(idExp) is list:
			for q in idExp:
				self.insert(idCat, q)
		else:
			if len(self.getOne(idCat, idExp))==0:
				return self.connExec("""
						INSERT into expCats (idExp, idCat) values (:idExp, :idCat)
						""",
						{"idExp": idExp, "idCat": idCat})
			else:
				print("[DB] expCat already present: (%d, %d)"%(idCat, idExp))
				return False

	def delete(self, idCat, idExp):
		"""delete one connection"""
		if type(idCat) is list:
			for q in idCat:
				self.delete(q, idExp)
		elif type(idExp) is list:
			for q in idExp:
				self.delete(idCat, q)
		else:
			return self.connExec("""
					delete from expCats where idExp=:idExp and idCat=:idCat
					""",
					{"idExp": idExp, "idCat": idCat})

	def askCats(self, exps):
		"""loop over given exps and ask for the cats to be saved"""
		if type(exps) is not list:
			exps = [exps]
		for e in exps:
			string = raw_input("categories for '%d': "%e)
			try:
				cats = ast.literal_eval("["+string.strip()+"]")
				self.insert(cats, e)
			except:
				print("[DB] something failed in reading your input")

	def askExps(self, cats):
		"""loop over given cats and ask for the experiments to be saved"""
		if type(cats) is not list:
			cats = [cats]
		for c in cats:
			string = raw_input("entries for '%d': "%c)
			try:
				exps = ast.literal_eval("["+string.strip()+"]")
				self.insert(c, exps)
			except:
				print("[DB] something failed in reading your input")

pBDB.catExp = catsExps()

class entryExps(physbiblioDBSub):
	"""functions for connecting entries and experiments"""
	def getOne(self, key, idExp):
		"""find one connection"""
		self.cursExec("""
				select * from entryExps where idExp=:idExp and bibkey=:bibkey
				""",
				{"idExp": idExp, "bibkey": key})
		return self.curs.fetchall()

	def getAll(self):
		"""find all the connections"""
		self.cursExec("""
				select * from entryExps
				""")
		return self.curs.fetchall()

	def insert(self, key, idExp):
		"""insert a new connection"""
		if type(key) is list:
			for q in key:
				self.insert(q, idExp)
		elif type(idExp) is list:
			for q in idExp:
				self.insert(key, q)
		else:
			if len(self.getOne(key, idExp))==0:
				if self.connExec("""
						INSERT into entryExps (idExp, bibkey) values (:idExp, :bibkey)
						""",
						{"idExp": idExp, "bibkey": key}):
					for c in pBDB.cats.getByExp(idExp):
						pBDB.catBib.insert(c["idCat"],key)
			else:
				print("[DB] entryExp already present: (%d, %s)"%(idExp, key))
				return False

	def delete(self, key, idExp):
		"""delete one connection"""
		if type(key) is list:
			for q in key:
				self.delete(q, idExp)
		elif type(idExp) is list:
			for q in idExp:
				self.delete(key, q)
		else:
			return self.connExec("""
					delete from entryExps where idExp=:idExp and bibkey=:bibkey
					""",
					{"idExp": idExp, "bibkey": key})

	def updateBibkey(self, new, old):
		"""update if there is a bibkey change"""
		print("[DB] updating entryCats for bibkey change, from '%s' to '%s'"%(old, new))
		query = "update entryExps set bibkey=:new where bibkey=:old\n"
		return self.connExec(query, {"new": new, "old": old})

	def askExps(self, keys):
		"""loop over given keys and ask for the exps to be saved"""
		if type(keys) is not list:
			keys = [keys]
		for k in keys:
			string = raw_input("experiments for '%s': "%k)
			try:
				exps = ast.literal_eval("["+string.strip()+"]")
				self.insert(k, exps)
			except:
				print("[DB] something failed in reading your input")

	def askKeys(self, exps):
		"""loop over given exps and ask for the entries to be saved"""
		if type(exps) is not list:
			exps = [exps]
		for e in exps:
			string = raw_input("entries for '%d': "%e)
			try:
				keys = ast.literal_eval("["+string.strip()+"]")
				self.insert(keys, e)
			except:
				print("[DB] something failed in reading your input")

pBDB.bibExp = entryExps()

class experiments(physbiblioDBSub):
	"""functions for experiments"""
	def insert(self,data):
		"""insert a new experiment"""
		return self.connExec("""
				INSERT into experiments (name, comments, homepage, inspire)
					values (:name, :comments, :homepage, :inspire)
				""", data)

	def update(self, data, idExp):
		"""update an existing experiment"""
		data["idExp"] = idExp
		print(data)
		query = "replace into experiments (" +\
					", ".join(data.keys()) + ") values (:" + \
					", :".join(data.keys()) + ")\n"
		return self.connExec(query, data)

	def updateField(self, idExp, field, value):
		"""update a field"""
		print("[DB] updating '%s' for entry '%s'"%(field, idExp))
		if field in self.tableCols["experiments"] and field is not "idExp" \
				and value is not "" and value is not None:
			query = "update experiments set " + field + "=:field where idExp=:idExp\n"
			return self.connExec(query, {"field": value, "idExp": idExp})
		else:
			return False

	def getByID(self, idExp):
		"""get experiments matching the idExp"""
		self.cursExec("""
			select * from experiments where idExp=?
			""", (idExp, ))
		return self.curs.fetchall()

	def getDictByID(self, idExp):
		"""get experiments matching the idExp, return a dictionary"""
		self.cursExec("""
			select * from experiments where idExp=?
			""", (idExp, ))
		try:
			entry = self.curs.fetchall()[0]
			expDict = {}
			for i,k in enumerate(self.tableCols["experiments"]):
				expDict[k] = entry[i]
		except:
			print("[DB] Error in extracting experiment by idExp")
			expDict = None
		return expDict

	def getAll(self, orderBy = "name", order = "ASC"):
		"""get all the experiments from the DB"""
		self.cursExec("""
			select * from experiments
			order by %s %s
			"""%(orderBy, order))
		return self.curs.fetchall()

	def getByName(self, name):
		"""get experiments matching a name"""
		self.cursExec("""
			select * from experiments where name=?
			""", (name, ))
		return self.curs.fetchall()

	def filterAll(self, string):
		"""get experiments matching a string"""
		string = "%" + string + "%"
		self.cursExec("""
			select * from experiments where name LIKE ? OR comments LIKE ? OR homepage LIKE ? OR inspire LIKE ?
			""", (string, string, string, string))
		return self.curs.fetchall()

	def printInCats(self, startFrom = 0, sp = 5 * " ", withDesc = False):
		"""prints the experiments under the corresponding categories"""
		cats = pBDB.cats.getAll()
		exps = self.getAll()
		catsHier = pBDB.cats.getHier(cats, startFrom = startFrom)
		showCat = {}
		for c in cats:
			showCat[c["idCat"]] = False
		def expString(idExp):
			exp = [ e for e in exps if e["idExp"] == idExp ][0]
			if withDesc:
				return sp + '-> %s (%d) - %s'%(exp['name'], exp['idExp'], exp['comments'])
			else:
				return sp + '-> %s (%d)'%(exp['name'], exp['idExp'])
		def alphabetExp(listId):
			listIn = [ e for e in exps if e["idExp"] in listId ]
			decorated = [ (x["name"], x) for x in listIn ]
			decorated.sort()
			return [ x[1]["idExp"] for x in decorated ]
		expCats = {}
		for (a, idE, idC) in pBDB.catExp.getAll():
			if idC not in expCats.keys():
				expCats[idC] = []
				showCat[idC] = True
			expCats[idC].append(idE)
		def printExpCats(ix, lev):
			try:
				for e in alphabetExp(expCats[ix]):
					print(lev * sp + expString(e))
			except:
				pass
		for l0 in cats_alphabetical(catsHier.keys()):
			for l1 in cats_alphabetical(catsHier[l0].keys()):
				if showCat[l1]:
					showCat[l0] = True
				for l2 in cats_alphabetical(catsHier[l0][l1].keys()):
					if showCat[l2]:
						showCat[l0] = True
						showCat[l1] = True
					for l3 in cats_alphabetical(catsHier[l0][l1][l2].keys()):
						if showCat[l3]:
							showCat[l0] = True
							showCat[l1] = True
							showCat[l2] = True
						for l4 in cats_alphabetical(catsHier[l0][l1][l2][l3].keys()):
							if showCat[l4]:
								showCat[l0] = True
								showCat[l1] = True
								showCat[l2] = True
								showCat[l2] = True
		for l0 in cats_alphabetical(catsHier.keys()):
			if showCat[l0]:
				print(catString(l0))
				printExpCats(l0, 1)
			for l1 in cats_alphabetical(catsHier[l0].keys()):
				if showCat[l1]:
					print(sp + catString(l1))
					printExpCats(l1, 2)
				for l2 in cats_alphabetical(catsHier[l0][l1].keys()):
					if showCat[l2]:
						print(2*sp + catString(l2))
						printExpCats(l2, 3)
					for l3 in cats_alphabetical(catsHier[l0][l1][l2].keys()):
						if showCat[l3]:
							print(3*sp + catString(l3))
							printExpCats(l3, 4)
						for l4 in cats_alphabetical(catsHier[l0][l1][l2][l3].keys()):
							if showCat[l4]:
								print(4*sp + catString(l4))
								printExpCats(l4, 5)

	def delete(self, idExp, name = None):
		"""delete an experiment and its connections"""
		if type(idExp) is list:
			for e in idExp:
				self.delete(e)
		else:
			print("[DB] using idExp=%d"%idExp)
			self.cursExec("""
			delete from experiments where idExp=?
			""", (idExp, ))
			self.cursExec("""
			delete from expCats where idExp=?
			""", (idExp, ))
			self.cursExec("""
			delete from entryExps where idExp=?
			""", (idExp, ))

	def to_str(self, q):
		"""convert the experiment row in a string"""
		return "%3d: %-20s [%-40s] [%s]"%(q["idExp"], q["name"], q["homepage"], q["inspire"])

	def printAll(self, exps = None, orderBy = "name", order = "ASC"):
		"""print all the experiments"""
		if exps is None:
			exps = self.getAll(orderBy = orderBy, order = order)
		for q in exps:
			print(self.to_str(q))

	def getByCat(self, idCat):
		"""find all the experiments under a given category"""
		query = """
				select * from experiments
				join expCats on experiments.idExp=expCats.idExp
				where expCats.idCat=?
				"""
		self.cursExec(query, (idCat,))
		return self.curs.fetchall()

	def getByEntry(self, key):
		"""find all the experiments for a given entry"""
		self.cursExec("""
				select * from experiments
				join entryExps on experiments.idExp=entryExps.idExp
				where entryExps.bibkey=?
				""", (key, ))
		return self.curs.fetchall()

pBDB.exps = experiments()

class entries(physbiblioDBSub):
	"""functions for the entries"""
	def __init__(self): #need to create lastFetched
		physbiblioDBSub.__init__(self)
		self.lastFetched = "select * from entries limit 10"
		self.lastInserted = []

	def delete(self, key):
		"""delete an entry and its connections"""
		if type(key) is list:
			for k in key:
				self.delete(k)
		else:
			print("[DB] delete entry, using key = '%s'"%key)
			self.cursExec("""
			delete from entries where bibkey=?
			""", (key,))
			self.cursExec("""
			delete from entryCats where bibkey=?
			""", (key,))
			self.cursExec("""
			delete from entryExps where bibkey=?
			""", (key,))

	def completeFetched(self, fetched_in):
		fetched_out = []
		for el in fetched_in:
			tmp = {}
			for k in el.keys():
				tmp[k] = el[k]
			try:
				tmp["bibtexDict"] = bibtexparser.loads(el["bibtex"]).entries[0]
			except IndexError:
				tmp["bibtexDict"] = {}
			for fi in ["title", "journal", "volume", "number", "pages"]:
				try:
					tmp[fi] = tmp["bibtexDict"][fi]
				except KeyError:
					tmp[fi] = ""
			try:
				tmp["published"] = " ".join([tmp["journal"], tmp["volume"], "(%s)"%tmp["year"], tmp["pages"]])
			except IndexError:
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

	def fetchFromLast(self):
		"""fetch entries using the last query"""
		try:
			if len(self.lastVals) > 0:
				self.cursExec(self.lastQuery, self.lastVals)
			else:
				self.cursExec(self.lastQuery)
		except:
			print("[DB] query failed: %s"%self.lastQuery)
			print(self.lastVals)
		fetched_in = self.curs.fetchall()
		self.lastFetched = self.completeFetched(fetched_in)
		return self

	def fetchFromDict(self, queryDict = {}, catExpOperator = "and", defaultConnection = "and",
			orderBy = "firstdate", orderType = "ASC", limitTo = None, limitOffset = None, saveQuery = True):
		"""fetch entries reading the information from a dictionary. can be used for complex queries"""
		def getQueryStr(di):
			return "%%%s%%"%di["str"] if di["operator"] == "like" else di["str"]
		first = True
		vals = ()
		query = """select * from entries """
		prependTab = ""
		jC,wC,vC,jE,wE,vE = ["","","","","",""]
		if "catExpOperator" in queryDict.keys():
			catExpOperator = queryDict["catExpOperator"]
			del queryDict["catExpOperator"]
		def catExpStrings(tp, tabName, fieldName):
			joinStr = ""
			whereStr = ""
			valsTmp = tuple()
			if type(queryDict[tp]["id"]) is list:
				if queryDict[tp]["operator"] == "or":
					joinStr += " left join %s on entries.bibkey=%s.bibkey"%(tabName, tabName)
					whereStr += "(%s)"%queryDict[tp]["operator"].join(
						[" %s.%s=? "%(tabName,fieldName) for q in queryDict[tp]["id"]])
					valsTmp = tuple(queryDict[tp]["id"])
				elif queryDict[tp]["operator"] == "and":
					joinStr += " ".join(
						[" left join %s %s%d on entries.bibkey=%s%d.bibkey"%(tabName,tabName,iC,tabName,iC) for iC,q in enumerate(queryDict[tp]["id"])])
					whereStr += "(" + " and ".join(
						["%s%d.%s=?"%(tabName, iC, fieldName) for iC,q in enumerate(queryDict[tp]["id"])]) + ")"
					valsTmp = tuple(queryDict[tp]["id"])
				else:
					pBErrorManager("[DB] invalid operator for joining cats!")
					return joinStr, whereStr, valsTmp
			else:
				joinStr += "left join %s on entries.bibkey=%s.bibkey"%(tabName, tabName)
				whereStr += "%s.%s=? "%(tabName, fieldName)
				valsTmp = tuple(str(queryDict["cats"]["id"]))
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
				query += " %s "%queryDict[k]["connection"] if "connection" in queryDict[k].keys() else defaultConnection
			s = k.split("#")[0]
			if s in self.tableCols["entries"]:
				query += " %s%s %s ?"%(prependTab, s, queryDict[k]["operator"])
				vals += (getQueryStr(queryDict[k]), )
		query += " order by " + prependTab + orderBy + " " + orderType if orderBy else ""
		if limitTo is not None:
			query += " LIMIT %s"%(str(limitTo))
		if limitOffset is not None:
			if limitTo is None:
				query += " LIMIT 100000"
			query += " OFFSET %s"%(str(limitOffset))
		if saveQuery:
			self.lastQuery = query
			self.lastVals  = vals
		print("[DB] using query:\n%s"%query)
		print(vals)
		try:
			if len(vals) > 0:
				self.cursExec(query, vals)
			else:
				self.cursExec(query)
		except:
			print("[DB] query failed: %s"%query)
			print(vals)
		fetched_in = self.curs.fetchall()
		self.lastFetched = self.completeFetched(fetched_in)
		return self

	def fetchAll(self, params = None, connection = "and", operator = "=",
			orderBy = "firstdate", orderType = "ASC", limitTo = None, limitOffset = None, saveQuery = True):
		"""save entries fetched from the database"""
		query = """select * from entries """
		vals = ()
		if params and len(params) > 0:
			query += " where "
			first = True
			for k, v in params.iteritems():
				if type(v) is list:
					for v1 in v:
						if first:
							first = False
						else:
							query += " %s "%connection
						query += k + operator + " ? "
						vals += (v1,)
				else:
					if first:
						first = False
					else:
						query += " %s "%connection
					query += k + operator + "? "
					vals += (v,)
		query += " order by " + orderBy + " " + orderType if orderBy else ""
		if limitTo is not None:
			query += " LIMIT %s"%(str(limitTo))
		if limitOffset is not None:
			query += " OFFSET %s"%(str(limitOffset))
		if saveQuery:
			self.lastQuery = query
			self.lastVals  = vals
		try:
			if len(vals) > 0:
				self.cursExec(query, vals)
			else:
				self.cursExec(query)
		except:
			print("[DB] query failed: %s"%query)
			print(vals)
		fetched_in = self.curs.fetchall()
		self.lastFetched = self.completeFetched(fetched_in)
		return self
	
	def getAll(self, params = None, connection = "and ", operator = "=", orderBy = "firstdate", orderType = "ASC", limitTo = None, limitOffset = None, saveQuery = True):
		"""get entries from the database"""
		return self.fetchAll(params = params, connection = connection, operator = operator, orderBy = orderBy, orderType = orderType, limitTo = limitTo, limitOffset = limitOffset, saveQuery = saveQuery).lastFetched

	def fetchByBibkey(self, bibkey, saveQuery = True):
		"""shortcut for selecting entries by their bibtek key"""
		if type(bibkey) is list:
			return self.fetchAll(params = {"bibkey": bibkey},
				connection = "or ", saveQuery = saveQuery)
		else:
			return self.fetchAll(params = {"bibkey": bibkey}, saveQuery = saveQuery)
		
	def getByBibkey(self, bibkey, saveQuery = True):
		"""shortcut for selecting entries by their bibtek key"""
		return self.fetchByBibkey(bibkey, saveQuery = saveQuery).lastFetched

	def fetchByKey(self, key, saveQuery = True):
		"""shortcut for selecting entries based on a current or old key, or searching the bibtex entry"""
		if type(key) is list:
			strings = ["%%%s%%"%q for q in key]
			return self.fetchAll(
				params = {"bibkey": strings, "old_keys": strings, "bibtex": strings},
				connection = "or ",
				operator = " like ",
				saveQuery = saveQuery)
		else:
			return self.fetchAll(
				params = {"bibkey": "%%%s%%"%key, "old_keys": "%%%s%%"%key, "bibtex": "%%%s%%"%key},
				connection = "or ",
				operator = " like ",
				saveQuery = saveQuery)

	def getByKey(self, key, saveQuery = True):
		"""shortcut for selecting entries based on a current or old key, or searching the bibtex entry"""
		return self.fetchByKey(key, saveQuery = saveQuery).lastFetched

	def fetchByBibtex(self, string, saveQuery = True):
		"""shortcut for selecting entries with a search in the bibtex field"""
		if type(string) is list:
			return self.fetchAll(
				params = {"bibtex":["%%%s%%"%q for q in string]},
				connection = "or",
				operator = " like ",
				saveQuery = saveQuery)
		else:
			return self.fetchAll(
				params = {"bibtex":"%%%s%%"%string},
				operator = " like ",
				saveQuery = saveQuery)

	def getByBibtex(self, string, saveQuery = True):
		"""shortcut for selecting entries with a search in the bibtex field"""
		return self.fetchByBibtex(string, saveQuery = saveQuery).lastFetched

	def getField(self, key, field):
		"""extract the content of one field from a entry in the database, searched by bibtex key"""
		try:
			return self.getByBibkey(key, saveQuery = False)[0][field]
		except IndexError:
			print("[DB] ERROR in getEntryField('%s', '%s'): no element found?"%(key, field))
			return False

	def toDataDict(self, key):
		"""convert the entry bibtex into a dictionary"""
		return self.prepareInsertEntry(self.getField(key, "bibtex"))

	def getDoiUrl(self, key):
		"""get doi url"""
		url = pbConfig.doiUrl + self.getField(key, "doi")
		return url

	def getArxivUrl(self, key, urlType = "abs"):
		"""get doi url"""
		url = pbConfig.arxivUrl + urlType + "/" + self.getField(key, "arxiv")
		return url
			
	def insert(self, data):
		"""insert entry"""
		return self.connExec("INSERT into entries (" +
					", ".join(self.tableCols["entries"]) + ") values (:" +
					", :".join(self.tableCols["entries"]) + ")\n",
					data)

	def replaceInBibtex(self, old, new):
		"""replace a string with a new one, in all the bibtex entries of the table"""
		self.lastQuery = "SELECT * FROM entries WHERE bibtex LIKE :match"
		self.lastVals  = {"match": "%"+old+"%"}
		self.cursExec(self.lastQuery, self.lastVals)
		self.lastFetched = self.completeFetched(self.curs.fetchall())
		keys = [k["bibkey"] for k in self.lastFetched]
		print "[DB] Replacing text in entries: ", keys
		if self.connExec("UPDATE entries SET bibtex = replace( bibtex, :old, :new ) WHERE bibtex LIKE :match", {"old": old, "new": new, "match": "%"+old+"%"}):
			return keys

	def replace(self, fiOld, fiNews, old, news, entries = None, regex = False):
		"""replace a string with a new one, in the given field of the (previously) selected bibtex entries"""
		def myReplace(line, new, previous = None):
			if regex:
				reg = re.compile(old)
				if reg.match(line):
					line = reg.sub(new, line)
				else:
					line = previous
			else:
				line = line.replace(old, new)
			return line
		success = []
		changed = []
		failed = []
		for entry in entries:
			try:
				if not fiOld in entry["bibtexDict"].keys() and not fiOld in entry.keys():
					raise KeyError("Field %s not found in entry %s"%(fiOld, entry["bibkey"]))
				if fiOld in entry["bibtexDict"].keys():
					before = entry["bibtexDict"][fiOld]
				elif fiOld in entry.keys():
					before = entry[fiOld]
				bef = []
				aft = []
				for fiNew, new in zip(fiNews, news):
					if not fiNew in entry["bibtexDict"].keys() and not fiNew in entry.keys():
						raise KeyError("Field %s not found in entry %s"%(fiNew, entry["bibkey"]))
					if fiNew in entry["bibtexDict"].keys():
						bef.append(entry["bibtexDict"][fiNew])
						after  = myReplace(before, new, previous = entry["bibtexDict"][fiNew])
						aft.append(after)
						entry["bibtexDict"][fiNew] = after
						db = bibtexparser.bibdatabase.BibDatabase()
						db.entries = []
						db.entries.append(entry["bibtexDict"])
						entry["bibtex"] = self.rmBibtexComments(self.rmBibtexACapo(pbWriter.write(db).strip()))
						self.updateField(entry["bibkey"], "bibtex", entry["bibtex"], verbose = 0)
					if fiNew in entry.keys():
						bef.append(entry[fiNew])
						after  = myReplace(before, new, previous = entry[fiNew])
						aft.append(after)
						self.updateField(entry["bibkey"], fiNew, after, verbose = 0)
			except KeyError:
				pBErrorManager("[DB] something wrong in replace", traceback)
				failed.append(entry["bibkey"])
			else:
				success.append(entry["bibkey"])
				if any(b != a for a,b in zip(aft, bef)):
					changed.append(entry["bibkey"])
		return success, changed, failed

	def update(self, data, oldkey):
		"""update entry"""
		data["bibkey"] = oldkey
		query = "replace into entries (" +\
					", ".join(data.keys()) + ") values (:" + \
					", :".join(data.keys()) + ")\n"
		return self.connExec(query, data)

	def rmBibtexComments(self, bibtex):
		"""remove comments and empty lines from bibtex"""
		output = ""
		for l in bibtex.splitlines():
			lx = l.strip()
			if len(lx) > 0 and lx[0] != "%":
				output += l + "\n"
		return output.strip()

	def rmBibtexACapo(self, bibtex):
		"""remove returns from bibtex"""
		output = ""
		db = bibtexparser.bibdatabase.BibDatabase()
		tmp = {}
		for k,v in bibtexparser.loads(bibtex).entries[0].items():
			tmp[k] = v.replace("\n", " ")
		db.entries = [tmp]
		return pbWriter.write(db)

	def prepareInsert(self,
			bibtex, bibkey = None, inspire = None, arxiv = None, ads = None, scholar = None, doi = None, isbn = None,
			year = None, link = None, comments = None, old_keys = None, crossref = None,
			exp_paper = None, lecture = None, phd_thesis = None, review = None, proceeding = None, book = None,
			marks = None, firstdate = None, pubdate = None, noUpd = None, abstract = None, number = None):
		"""convert a bibtex into a dictionary, eventually using also additional info"""
		data = {}
		if number is None:
			number = 0
		try:
			element = bibtexparser.loads(bibtex).entries[number]
			data["bibkey"] = bibkey if bibkey else element["ID"]	
		except KeyError:
			print("[DB] ERROR: impossible to parse bibtex!")
			data["bibkey"] = ""
			return data
		db = bibtexparser.bibdatabase.BibDatabase()
		db.entries = []
		db.entries.append(element)
		data["bibtex"]  = self.rmBibtexComments(self.rmBibtexACapo(pbWriter.write(db).strip()))
		data["inspire"] = inspire if inspire else None
		if arxiv:
			data["arxiv"] = arxiv
		else:
			try:
				data["arxiv"] = element["arxiv"]
			except KeyError:
				try:
					data["arxiv"] = element["eprint"]
				except KeyError:
					data["arxiv"] = ""
		data["ads"] = ads if ads else None
		data["scholar"] = scholar if scholar else None
		if doi:
			data["doi"] = doi
		else:
			try:
				data["doi"] = element["doi"]
			except KeyError:
				data["doi"] = None
		if isbn:
			data["isbn"] = isbn
		else:
			try:
				data["isbn"] = element["isbn"]
			except KeyError:
				data["isbn"] = None
		if year:
			data["year"] = year
		else:
			try:
				data["year"] = element["year"]
			except KeyError:
				try:
					identif = re.compile("([0-9]{4}.[0-9]{4,5}|[0-9]{7})*")
					for t in identif.finditer(data["arxiv"]):
						if len(t.group()) > 0:
							e = t.group()
							a = e[0:2]
							if int(a) > 80:
								data["year"] = "19"+a
							else:
								data["year"] = "20"+a
				except KeyError:
					data["year"]=None
		if link:
			data["link"] = link
		else:
			try:
				data["link"] = pbConfig.arxivUrl + "abs/" + data["arxiv"]
			except KeyError:
				try:
					data["link"] = pbConfig.doiUrl + data["doi"]
				except KeyError:
					data["link"] = None
		data["comments"] = comments if comments else None
		data["old_keys"] = old_keys if old_keys else None
		if crossref:
			data["crossref"] = crossref
		else:
			try:
				data["crossref"] = element["crossref"]
			except KeyError:
				data["crossref"] = None
		data["exp_paper"] = 1 if exp_paper else 0
		data["lecture"] = 1 if lecture else 0
		data["phd_thesis"] = 1 if phd_thesis else 0
		data["review"] = 1 if review else 0
		data["proceeding"] = 1 if proceeding else 0
		data["book"] = 1 if book else 0
		data["noUpdate"] = 1 if noUpd else 0
		data["marks"] = marks if marks else ""
		if not abstract:
			try:
				abstract = element["abstract"]
			except KeyError:
				pass
		data["abstract"] = abstract if abstract else None
		data["firstdate"] = firstdate if firstdate else datetime.date.today().strftime("%Y-%m-%d")
		data["pubdate"] = pubdate if pubdate else ""
		return data
		
	def prepareUpdateByKey(self, key_old, key_new):
		"""get an entry bibtex and prepare an update using the new bibtex from another database entry"""
		u = self.prepareUpdate(self.getField(key_old, "bibtex"), self.getField(key_new, "bibtex"))
		return self.prepareInsert(u)
	
	def prepareUpdateByBibtex(self, key_old, bibtex_new):
		"""get an entry bibtex and prepare an update using the new given bibtex"""
		u = self.prepareUpdate(self.getEntryField(key_old, "bibtex"), bibtex_new)
		return self.prepareInsert(u)
		
	def prepareUpdate(self, bibtexOld, bibtexNew):
		"""prepare the update of an entry, comparing two bibtexs"""
		elementOld = bibtexparser.loads(bibtexOld).entries[0]
		elementNew = bibtexparser.loads(bibtexNew).entries[0]
		db = bibtexparser.bibdatabase.BibDatabase()
		db.entries = []
		keep = elementOld
		for k in elementNew.keys():
			if k not in elementOld.keys():
				keep[k] = elementNew[k]
			elif elementNew[k] and elementNew[k] != elementOld[k] and k != "bibtex" and k != "ID":
				keep[k] = elementNew[k]
		db.entries.append(keep)
		return pbWriter.write(db)
		
	def updateInspireID(self, string, key = None, number = None):
		"""use inspire websearch module to get and update the inspireID"""
		newid = physBiblioWeb.webSearch["inspire"].retrieveInspireID(string, number = number)
		if key is None:
			key = string
		if newid is not "":
			query = "update entries set inspire=:inspire where bibkey=:bibkey\n"
			if self.connExec(query, {"inspire": newid, "bibkey": key}):
				return newid
		else:
			return False
	
	def updateField(self, key, field, value, verbose = 1):
		"""update a single field of an entry"""
		if verbose > 0:
			print("[DB] updating '%s' for entry '%s'"%(field, key))
		if field in self.tableCols["entries"] and field != "bibkey" \
				and value is not "" and value is not None:
			query = "update entries set " + field + "=:field where bibkey=:bibkey\n"
			if verbose > 1:
				print query, field, value
			return self.connExec(query, {"field": value, "bibkey": key})
		else:
			if verbose > 1:
				print("[DB] non-existing field or unappropriated value: (%s, %s, %s)"%(key, field, value))
			return False
	
	def updateBibkey(self, oldKey, newKey):
		"""update the bibkey of an entry"""
		print("[DB] updating bibkey for entry '%s' into '%s'"%(oldKey, newKey))
		try:
			query = "update entries set bibkey=:new where bibkey=:old\n"
			if self.connExec(query, {"new": newKey, "old": oldKey}):
				query = "update entryCats set bibkey=:new where bibkey=:old\n"
				if self.connExec(query, {"new": newKey, "old": oldKey}):
					query = "update entryExps set bibkey=:new where bibkey=:old\n"
					return self.connExec(query, {"new": newKey, "old": oldKey})
				else:
					return False
			else:
				return False
		except:
			print traceback.format_exc()
			return False
			
	def getDailyInfoFromOAI(self, date1 = None, date2 = None):
		"""use inspire OAI webinterface to get updated entries between two dates"""
		if date1 is None or not re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", date1):
			date1 = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
		if date2 is None or not re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", date2):
			date2 = datetime.date.today().strftime("%Y-%m-%d")
		yren, monen, dayen = date1.split('-')
		yrst, monst, dayst = date2.split('-')
		print("[DB] calling INSPIRE-HEP OAI harvester between dates %s and %s"%(date1, date2))
		date1 = datetime.datetime(int(yren), int(monen), int(dayen))
		date2 = datetime.datetime(int(yrst), int(monst), int(dayst))
		entries = physBiblioWeb.webSearch["inspireoai"].retrieveOAIUpdates(date1, date2)
		for e in entries:
			try:
				key = e["bibkey"]
				print(key)
				old = self.extractEntryByBibkey(key)
				if len(old) > 0:
					for [o, d] in physBiblioWeb.webSearch["inspireoai"].correspondences:
						if e[o] != old[0][d]:
							self.updateEntryField(key, d, e[o], 0)
			except:
				print("[DB][oai] something missing in entry %s"%e["id"])
		print("[DB] inspire OAI harvesting done!")

	def updateInfoFromOAI(self, inspireID, bibtex = None, verbose = 0):
		"""use inspire OAI to retrieve the info for a single entry"""
		if not inspireID.isdigit(): #assume it's a key instead of the inspireID
			inspireID = self.getField(inspireID, "inspire")
			try:
				inspireID.isdigit()
			except AttributeError:
				pBErrorManager("[DB] wrong value/format in inspireID: %s"%inspireID)
				return False
		result = physBiblioWeb.webSearch["inspireoai"].retrieveOAIData(inspireID, bibtex = bibtex, verbose = verbose)
		if verbose > 1:
			print(result)
		if result is False:
			pBErrorManager("[DB][oai] empty record looking for recid:%s!"%inspireID)
			return False
		try:
			key = result["bibkey"]
			old = self.getByBibkey(key, saveQuery = False)
			if verbose > 1:
				print("%s, %s"%(key, old))
			if len(old) > 0:
				for [o, d] in physBiblioWeb.webSearch["inspireoai"].correspondences:
					try:
						if verbose > 0:
							print("%s = %s (%s)"%(d, result[o], old[0][d]))
						if result[o] != old[0][d]:
							if o == "bibtex" and result[o] is not None:
								self.updateField(key, d, self.rmBibtexComments(self.rmBibtexACapo(result[o].strip())), verbose = 0)
							else:
								self.updateField(key, d, result[o], verbose = 0)
					except:
						print("[DB][oai] key error: (%s, %s)"%(o,d))
			if verbose > 0:
				print("[DB] inspire OAI info for %s saved."%inspireID)
		except:
			pBErrorManager("[DB][oai] something missing in entry %s"%inspireID, traceback)
			return False
		return True
	
	def updateFromOAI(self, entry, verbose = 0):
		"""update entry from inspire OAI. If inspireID is missing, look for it"""
		if type(entry) is list:
			for e in entry:
				self.updateFromOAI(e, verbose = verbose)
		elif entry.isdigit():
			return self.updateInfoFromOAI(entry, verbose = verbose)
		else:
			inspireID = self.getField(entry, "inspire")
			if inspireID is not None:
				return self.updateInfoFromOAI(inspireID, verbose = verbose)
			else:
				inspireID = self.updateInspireID(entry, entry)
				return self.updateInfoFromOAI(inspireID, verbose = verbose)
	
	def searchOAIUpdates(self, startFrom = 0, entries = None, force = False):
		"""select unpublished papers and look for updates using inspireOAI"""
		if entries is None:
			try:
				entries = self.getAll(saveQuery = False)[startFrom:]
			except TypeError:
				pBErrorManager("[DB] invalid startFrom in searchOAIUpdates", traceback)
				return 0, 0, []
		num = 0
		err = []
		changed = []
		tot = len(entries)
		self.runningOAIUpdates = True
		print("[DB] searchOAIUpdates will process %d total entries"%tot)
		for ix,e in enumerate(entries):
			if self.runningOAIUpdates \
				and e["proceeding"] == 0 \
				and e["book"] == 0 \
				and e["lecture"] == 0 \
				and e["phd_thesis"] == 0 \
				and e["noUpdate"] == 0 \
				and e["inspire"] is not None \
				and e["inspire"] != "" \
				and (force or ( e["doi"] is None or "journal" not in e["bibtexDict"].keys() ) ):
					num += 1
					print("[DB] %5d / %d (%5.2f%%) - looking for update: '%s'"%(ix+1, tot, 100.*(ix+1)/tot, e["bibkey"]))
					if not self.updateInfoFromOAI(e["inspire"], bibtex = e["bibtex"], verbose = 0):
						err.append(e["bibkey"])
					elif e != self.getByBibkey(e["bibkey"], saveQuery = False)[0]:
						print("[DB] -- element changed!")
						changed.append(e["bibkey"])
					print("")
		print("\n[DB] %d entries processed"%num)
		print("\n[DB] %d errors occurred"%len(err))
		if len(err)>0:
			print(err)
		print("\n[DB] %d entries changed"%len(changed))
		if len(changed)>0:
			print(changed)
		return num, err, changed
		
	def loadAndInsert(self, entry, method = "inspire", imposeKey = None, number = None, returnBibtex = False, childProcess = False):
		"""read a list of keywords and look for inspire contents, then load in the database all the info"""
		requireAll = False
		def printExisting(entry, existing):
			print("[DB] Already existing: %s\n"%entry)
			if returnBibtex:
				return existing[0]["bibtex"]
			else:
				return True
		if not childProcess:
			self.lastInserted = []
		if entry is not None and not type(entry) is list:
			existing = self.getByBibkey(entry, saveQuery = False)
			if existing:
				return printExisting(entry, existing)
			if method == "bibtex":
				e = entry
			else:
				e = physBiblioWeb.webSearch[method].retrieveUrlAll(entry)
				if e.count('@') > 1:
					if number is not None:
						requireAll = True
					else:
						print(e)
						print("[DB] WARNING: possible mismatch. Specify the number of element to select with 'number'\n")
						return False
			if requireAll:
				data = self.prepareInsert(e, number = number)
			else:
				data = self.prepareInsert(e)
			key = data["bibkey"]
			if pbConfig.params["fetchAbstract"] and data["arxiv"] is not None:
				arxivBibtex, arxivDict = physBiblioWeb.webSearch["arxiv"].retrieveUrlAll(data["arxiv"], fullDict = True)
				data["abstract"] = arxivDict["abstract"]
			if imposeKey is not None:
				data["bibkey"] = imposeKey
				data["bibtex"] = data["bibtex"].replace(key, imposeKey)
				key = imposeKey
			if key.strip() == "":
				pBErrorManager("[DB] ERROR: impossible to insert an entry with empty bibkey!\n%s\n"%entry)
				return False
			existing = self.getByBibkey(key, saveQuery = False)
			if existing:
				return printExisting(key, existing)
			print("[DB] entry will have key\n'%s'"%key)
			try:
				self.insert(data)
			except:
				pBErrorManager("[DB] loadAndInsert(%s) failed in inserting entry\n"%entry)
				return False
			try:
				if method == "inspire":
					if not requireAll:
						eid = self.updateInspireID(entry, key)
					else:
						eid = self.updateInspireID(entry, key, number = number)
					self.updateInfoFromOAI(eid)
				elif method == "isbn":
					self.setBook(key)
				print("[DB] element successfully inserted.\n")
				self.lastInserted.append(key)
				if returnBibtex:
					return e
				else:
					return True
			except:
				pBErrorManager("[DB] loadAndInsertEntries(%s) failed in completing info\n"%entry)
				return False
		elif entry is not None and type(entry) is list:
			failed = []
			def returnListIfSub(a, out):
				if type(a) is list:
					for el in a:
						out = returnListIfSub(el, out)
					return out
				else:
					out += [a]
					return out
			entry = returnListIfSub(entry, [])
			self.runningLoadAndInsert = True
			tot = len(entry)
			print("[DB] loadAndInsert will process %d total entries"%tot)
			ix = 0
			for e in entry:
				if type(e) is float:
					e = str(e)
				if self.runningLoadAndInsert:
					print("[DB] %5d / %d (%5.2f%%) - looking for string: '%s'\n"%(ix+1, tot, 100.*(ix+1)/tot, e))
					if not self.loadAndInsert(e, childProcess = True):
						failed.append(e)
					ix += 1
			if len(self.lastInserted) > 0:
				print("[DB] imported entries:\n%s"%", ".join(self.lastInserted))
			if len(failed) > 0:
				pBErrorManager("[DB] ERRORS!\nFailed to load and import entries:\n%s"%", ".join(failed))
		else:
			print("[DB] ERROR: invalid arguments to loadAndInsertEntries!")
			return False
			
	def loadAndInsertWithCats(self, entry, method = "inspire", imposeKey = None, number = None, returnBibtex = False, childProcess = False):
		"""load the entries, then ask for their categories"""
		self.loadAndInsert(entry, method = method, imposeKey = imposeKey, number = number, returnBibtex = returnBibtex, childProcess = childProcess)
		pBDB.catBib.askCats(self.lastInserted)

	def setBook(self, key, value = 1):
		"""set (or unset) an entry as a book"""
		if type(key) is list:
			for q in key:
				self.setBook(q, value)
		else:
			return self.updateField(key, "book", value, 0)

	def setLecture(self, key, value = 1):
		"""set (or unset) an entry as a lecture"""
		if type(key) is list:
			for q in key:
				self.setLecture(q, value)
		else:
			return self.updateField(key, "lecture", value, 0)

	def setPhdThesis(self, key, value = 1):
		"""set (or unset) an entry as a PhD thesis"""
		if type(key) is list:
			for q in key:
				self.setPhdThesis(q, value)
		else:
			return self.updateField(key, "phd_thesis", value, 0)

	def setProceeding(self, key, value = 1):
		"""set (or unset) an entry as a proceeding"""
		if type(key) is list:
			for q in key:
				self.setProceeding(q, value)
		else:
			return self.updateField(key, "proceeding", value, 0)

	def setReview(self, key, value = 1):
		"""set (or unset) an entry as a review"""
		if type(key) is list:
			for q in key:
				self.setReview(q, value)
		else:
			return self.updateField(key, "review", value, 0)

	def setNoUpdate(self, key, value = 1):
		"""set (or unset) an entry as a review"""
		if type(key) is list:
			for q in key:
				self.setNoUpdate(q, value)
		else:
			return self.updateField(key, "noUpdate", value, 0)
			
	def printAllBibtexs(self, entriesIn = None):
		"""print the bibtex codes for all the entries (or for a given subset)"""
		if entriesIn is not None:
			entries = entriesIn
		elif self.lastFetched is not None:
			entries = self.lastFetched
		else:
			entries = self.getAll(orderBy = "firstdate")
		for i, e in enumerate(entries):
			print("%4d - %s\n"%(i, e["bibtex"]))
		print("[DB] %d elements found"%len(entries))
			
	def printAllBibkeys(self, entriesIn = None):
		"""print the bibtex keys for all the entries (or for a given subset)"""
		if entriesIn is not None:
			entries = entriesIn
		elif self.lastFetched is not None:
			entries = self.lastFetched
		else:
			entries = self.getAll(orderBy = "firstdate")
		for i, e in enumerate(entries):
			print("%4d %s"%(i, e["bibkey"]))
		print("[DB] %d elements found"%len(entries))
			
	def printAllInfo(self, entriesIn = None, orderBy = "firstdate", addFields = None):
		"""print the short info for all the entries (or for a given subset)"""
		if entriesIn is not None:
			entries = entriesIn
		elif self.lastFetched is not None:
			entries = self.lastFetched
		else:
			entries = self.getAll(orderBy = orderBy)
		for i, e in enumerate(entries):
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
				moreStr = "%-20s"%(e["arxiv"] if e["arxiv"] is not None else "-")
			elif e["proceeding"] == 1:
				typeStr = "(proc)"
			print(orderDate + "%7s "%typeStr + bibKeyStr + moreStr)
			if addFields is not None:
				try:
					if type(addFields) is list:
						for f in addFields:
							try:
								print("   %s: %s"%(f, e[f]))
							except:
								print("   %s: %s"%(f, e["bibtexDict"][f]))
					else:
						try:
							print("   %s: %s"%(addFields, e[addFields]))
						except:
							print("   %s: %s"%(addFields, e["bibtexDict"][addFields]))
				except:
					pass
		print("[DB] %d elements found"%len(entries))

	def fetchByCat(self, idCat, orderBy = "entries.firstdate", orderType = "ASC"):
		"""find all the entries in a given category"""
		query = """
				select * from entries
				join entryCats on entries.bibkey=entryCats.bibkey
				where entryCats.idCat=?
				"""
		query += " order by " + orderBy + " " + orderType if orderBy else ""
		self.cursExec(query, (idCat,))
		fetched_in = self.curs.fetchall()
		fetched_out = []
		for el in fetched_in:
			tmp = {}
			for k in el.keys():
				tmp[k] = el[k]
			tmp["bibtexDict"] = bibtexparser.loads(el["bibtex"]).entries[0]
			fetched_out.append(tmp)
		self.lastFetched = fetched_out
		return self

	def getByCat(self, idCat, orderBy = "entries.firstdate", orderType = "ASC"):
		return self.fetchByCat(idCat, orderBy = orderBy, orderType = orderType).lastFetched

	def fetchByExp(self, idExp, orderBy = "entries.firstdate", orderType = "ASC"):
		"""find all the entries for a given experiment"""
		query = """
				select * from entries
				join entryExps on entries.bibkey=entryExps.bibkey
				where entryExps.idExp=?
				"""
		query += " order by " + orderBy + " " + orderType if orderBy else ""
		self.cursExec(query, (idExp,))
		fetched_in = self.curs.fetchall()
		fetched_out = []
		for el in fetched_in:
			tmp = {}
			for k in el.keys():
				tmp[k] = el[k]
			tmp["bibtexDict"] = bibtexparser.loads(el["bibtex"]).entries[0]
			fetched_out.append(tmp)
		self.lastFetched = fetched_out
		return self

	def getByExp(self, idExp, orderBy = "entries.firstdate", orderType = "ASC"):
		return self.fetchByExp(idExp, orderBy = orderBy, orderType = orderType).lastFetched

	def cleanBibtexs(self, startFrom = 0, entries = None):
		"""clean and reformat the bibtexs"""
		if entries is None:
			try:
				entries = self.getAll(saveQuery = False)[startFrom:]
			except TypeError:
				pBErrorManager("[DB] invalid startFrom in cleanBibtexs", traceback)
				return 0, 0, []
		num = 0
		err = 0
		changed = []
		tot = len(entries)
		self.runningCleanBibtexs = True
		print("[DB] cleanBibtexs will process %d total entries"%tot)
		db = bibtexparser.bibdatabase.BibDatabase()
		for ix,e in enumerate(entries):
			if self.runningCleanBibtexs:
				num += 1
				print("[DB] %5d / %d (%5.2f%%) - cleaning: '%s'\n"%(ix+1, tot, 100.*(ix+1)/tot, e["bibkey"]))
				try:
					element = bibtexparser.loads(e["bibtex"]).entries[0]
					db.entries = []
					db.entries.append(element)
					newbibtex  = self.rmBibtexComments(self.rmBibtexACapo(pbWriter.write(db).strip()))
					if e["bibtex"] != newbibtex and self.updateField(e["bibkey"], "bibtex", newbibtex):
						print("[DB] -- element changed!")
						changed.append(e["bibkey"])
				except ValueError:
					err += 1
		print("\n[DB] %d entries processed"%num)
		print("\n[DB] %d errors occurred"%err)
		print("\n[DB] %d entries changed"%len(changed))
		return num, err, changed

pBDB.bibs = entries()

class utilities(physbiblioDBSub):
	"""various useful functions"""
	def cleanSpareEntries(self):
		"""finds and deletes connections where one of the parts is missing"""
		def deletePresent(ix1, ix2, join, func):
			for e in join:
				if e[0] not in ix1 or e[1] not in ix2:
					print("[DB] cleaning (%s, %s)"%(e[0], e[1]))
					func(e[0], e[1])

		bibkeys = [ e["bibkey"] for e in pBDB.bibs.getAll(saveQuery = False) ]
		idCats  = [ e["idCat"]  for e in pBDB.cats.getAll() ]
		idExps  = [ e["idExp"]  for e in pBDB.exps.getAll() ]
		
		deletePresent(bibkeys, idExps, [ [e["bibkey"], e["idExp"]] for e in pBDB.bibExp.getAll()], pBDB.bibExp.delete)
		deletePresent(idCats, bibkeys, [ [e["idCat"], e["bibkey"]] for e in pBDB.catBib.getAll()], pBDB.catBib.delete)
		deletePresent(idCats, idExps,  [ [e["idCat"], e["idExp"]]  for e in pBDB.catExp.getAll()], pBDB.catExp.delete)
	
	def cleanAllBibtexs(self, verbose = 0):
		"""remove newlines, non-standard characters and comments from the bibtex of all the entries"""
		b = pBDB.bibs
		for e in b.getAll():
			t = e["bibtex"]
			t = b.rmBibtexComments(t)
			t = parse_accents_str(t)
			t = b.rmBibtexACapo(t)
			b.updateField(e["bibkey"], "bibtex", t, verbose = verbose)

pBDB.utils = utilities()

def catString(idCat, withDesc = False):
	cat = pBDB.cats.getByID(idCat)[0]
	if withDesc:
		return '%4d: %s - <i>%s</i>'%(cat['idCat'], cat['name'], cat['description'])
	else:
		return '%4d: %s'%(cat['idCat'], cat['name'])

def cats_alphabetical(listId):
	listIn = [ pBDB.cats.getByID(i)[0] for i in listId ]
	decorated = [ (x["name"].lower(), x) for x in listIn ]
	decorated.sort()
	return [ x[1]["idCat"] for x in decorated ]

def dbStats():
	pBDB.stats={}
	pBDB.stats["bibs"] = len(pBDB.bibs.getAll())
	pBDB.stats["cats"] = len(pBDB.cats.getAll())
	pBDB.stats["exps"] = len(pBDB.exps.getAll())
	pBDB.stats["catBib"] = len(pBDB.catBib.getAll())
	pBDB.stats["catExp"] = len(pBDB.catExp.getAll())
	pBDB.stats["bibExp"] = len(pBDB.bibExp.getAll())
