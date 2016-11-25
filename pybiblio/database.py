import sqlite3
import os, re, traceback, datetime
import bibtexparser
import ast
import pybiblio.webimport.webInterf as webInt

try:
	from pybiblio.config import pbConfig
	import pybiblio.parse_accents as parse_accents
	import pybiblio.firstOpen as pbfo
	from pybiblio.webimport.webInterf import pyBiblioWeb
	import pybiblio.tablesDef
except ImportError:
    print("Could not find pybiblio and its contents: configure your PYTHONPATH!")

encoding_default = 'iso-8859-15'
parser = bibtexparser.bparser.BibTexParser()
parser.encoding = encoding_default
parser.customization = parse_accents.parse_accents_record
parser.alt_dict = {}

class pybiblioDB():
	"""
	Contains most of the basic DB functions
	"""
	def __init__(self, dbname = pbConfig.params['mainDatabaseName']):
		"""
		Initialize DB class
		"""
		#structure of the tables
		self.tableFields = pybiblio.tablesDef.tableFields
		#names of the columns
		self.tableCols = {}
		for q in self.tableFields.keys():
			self.tableCols[q] = [ a[0] for a in self.tableFields[q] ]
		
		self.conn = None
		self.curs = None
		self.dbname = dbname
		db_is_new = not os.path.exists(self.dbname)
		if db_is_new:
			print("-------New database. Creating tables!\n\n")
			pbfo.createTables(self)
		self.openDB()
		
		self.lastFetched = None
		self.catsHier = None

	def openDB(self):
		"""open the database"""
		self.conn = sqlite3.connect(self.dbname)
		self.conn.row_factory = sqlite3.Row
		self.curs = self.conn.cursor()

	def closeDB(self):
		"""close the database"""
		self.conn.close()

	def commit(self):
		"""commit the changes"""
		self.conn.commit()
		print("[DB] saved.")
		
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
			try:
				mainWin.setWindowTitle("PyBiblio*")
			except:
				pass
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

pBDB=pybiblioDB()

class pybiblioDBSub():
	"""
	Uses pybiblioDB instance 'pBDB' to act on the database.
	All the subcategories of pybiblioDB are defined starting from this one.
	"""
	def __init__(self):
		"""
		Initialize DB class
		"""
		#structure of the tables
		self.tableFields = pybiblio.tablesDef.tableFields
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

class categories(pybiblioDBSub):
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
		print("-----\n", data, "\n------\n")
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

	def getHier(self, cats = None, startFrom = 0, replace = False):
		"""get categories and subcategories in a tree-like structure"""
		if self.catsHier is not None and not replace:
			return self.catsHier
		if cats is None:
			cats = self.getAll()
		def addSubCats(idC):
			tmp = {}
			for c in [ a for a in cats if a["parentCat"] == idC and a["idCat"] != 0 ]:
				tmp[c["idCat"]] = {}
			return tmp
		catsHier = {}
		new = addSubCats(startFrom)
		catsHier[startFrom] = new
		if len(new.keys()) == 0:
			return catsHier
		for l0 in catsHier.keys():
			for l1 in catsHier[l0].keys():
				new = addSubCats(l1)
				if len(new.keys()) > 0:
					catsHier[l0][l1] = new
		for l0 in catsHier.keys():
			for l1 in catsHier[l0].keys():
				for l2 in catsHier[l0][l1].keys():
					new = addSubCats(l2)
					if len(new.keys()) > 0:
						catsHier[l0][l1][l2] = new
		for l0 in catsHier.keys():
			for l1 in catsHier[l0].keys():
				for l2 in catsHier[l0][l1].keys():
					for l3 in catsHier[l0][l1][l2].keys():
						new = addSubCats(l3)
						if len(new.keys()) > 0:
							catsHier[l0][l1][l2][l3] = new
		self.catsHier = catsHier
		return catsHier

	def printHier(self, startFrom = 0, sp = 5*" ", withDesc = False, depth = 5, replace = False):
		"""print categories and subcategories in a tree-like form"""
		cats = self.getAll()
		if depth < 2 or depth > 5:
			print("[DB] invalid depth in printCatHier (use between 2 and 5)")
			depth = 5
		catsHier = self.getHier(cats, startFrom=startFrom, replace = replace)
		def catString(idCat):
			cat = cats[idCat]
			if withDesc:
				return '%4d: %s - %s'%(cat['idCat'], cat['name'], cat['description'])
			else:
				return '%4d: %s'%(cat['idCat'], cat['name'])
		def alphabetical(listId):
			listIn = [ cats[i] for i in listId ]
			decorated = [ (x["name"], x) for x in listIn ]
			decorated.sort()
			return [ x[1]["idCat"] for x in decorated ]
		for l0 in alphabetical(catsHier.keys()):
			print(catString(l0))
			if depth > 1:
				for l1 in alphabetical(catsHier[l0].keys()):
					print(sp + catString(l1))
					if depth > 2:
						for l2 in alphabetical(catsHier[l0][l1].keys()):
							print(2*sp + catString(l2))
							if depth > 3:
								for l3 in alphabetical(catsHier[l0][l1][l2].keys()):
									print(3*sp + catString(l3))
									if depth > 4:
										for l4 in alphabetical(catsHier[l0][l1][l2][l3].keys()):
											print(4*sp + catString(l4))

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
			for row in self.extractSubcats(idCat):
				self.deleteCat(row["idCat"])

	def findByEntry(self, key):
		"""find all the categories for a given entry"""
		self.cursExec("""
				select * from categories
				join entryCats on categories.idCat=entryCats.idCat
				where entryCats.bibkey=?
				""", (key,))
		return self.curs.fetchall()

	def findByExp(self, idExp):
		"""find all the categories for a given experiment"""
		self.cursExec("""
				select * from categories
				join expCats on categories.idCat=expCats.idCat
				where expCats.idExp=?
				""", (idExp,))
		return self.curs.fetchall()

pBDB.cats = categories()

class catsEntries(pybiblioDBSub):
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

	def askCats(self, keys):
		"""loop over given keys and ask for the cats to be saved"""
		if type(keys) is not list:
			keys = [keys]
		for k in keys:
			string = raw_input("categories for '%s': "%k)
			try:
				cats = ast.literal_eval(string.strip())
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
				keys = ast.literal_eval(string.strip())
				self.insert(c, keys)
			except:
				print("[DB] something failed in reading your input")

pBDB.catBib = catsEntries()

class catsExps(pybiblioDBSub):
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
				cats = ast.literal_eval(string.strip())
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
				exps = ast.literal_eval(string.strip())
				self.insert(c, exps)
			except:
				print("[DB] something failed in reading your input")

pBDB.catExp = catsExps()

class entryExps(pybiblioDBSub):
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
					for c in pBDB.cats.findByExp(idExp):
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

	def askExps(self, keys):
		"""loop over given keys and ask for the exps to be saved"""
		if type(keys) is not list:
			keys = [keys]
		for k in keys:
			string = raw_input("experiments for '%s': "%k)
			try:
				exps = ast.literal_eval(string.strip())
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
				keys = ast.literal_eval(string.strip())
				self.insert(keys, e)
			except:
				print("[DB] something failed in reading your input")

pBDB.bibExp = entryExps()

class experiments(pybiblioDBSub):
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
		print("-----\n", data, "\n------\n")
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

	def printInCats(self, startFrom = 0, sp = 5 * " ", withDesc = False):
		"""prints the experiments under the corresponding categories"""
		cats = pBDB.cats.getAll()
		exps = self.getAll()
		catsHier = pBDB.cats.getHier(cats, startFrom = startFrom)
		showCat = {}
		for c in cats:
			showCat[c["idCat"]] = False
		def catString(idCat):
			"""a format for printing the category"""
			cat = cats[idCat]
			if withDesc:
				return '%4d: %s - %s'%(cat['idCat'], cat['name'], cat['description'])
			else:
				return '%4d: %s'%(cat['idCat'], cat['name'])
		def expString(idExp):
			exp = [ e for e in exps if e["idExp"] == idExp ][0]
			if withDesc:
				return sp + '-> %s (%d) - %s'%(exp['name'], exp['idExp'], exp['comments'])
			else:
				return sp + '-> %s (%d)'%(exp['name'], exp['idExp'])
		def alphabetical(listId):
			listIn = [ cats[i] for i in listId ]
			decorated = [ (x["name"], x) for x in listIn ]
			decorated.sort()
			return [ x[1]["idCat"] for x in decorated ]
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
		for l0 in alphabetical(catsHier.keys()):
			for l1 in alphabetical(catsHier[l0].keys()):
				if showCat[l1]:
					showCat[l0] = True
				for l2 in alphabetical(catsHier[l0][l1].keys()):
					if showCat[l2]:
						showCat[l0] = True
						showCat[l1] = True
					for l3 in alphabetical(catsHier[l0][l1][l2].keys()):
						if showCat[l3]:
							showCat[l0] = True
							showCat[l1] = True
							showCat[l2] = True
						for l4 in alphabetical(catsHier[l0][l1][l2][l3].keys()):
							if showCat[l4]:
								showCat[l0] = True
								showCat[l1] = True
								showCat[l2] = True
								showCat[l2] = True
		for l0 in alphabetical(catsHier.keys()):
			if showCat[l0]:
				print(catString(l0))
				printExpCats(l0, 1)
			for l1 in alphabetical(catsHier[l0].keys()):
				if showCat[l1]:
					print(sp + catString(l1))
					printExpCats(l1, 2)
				for l2 in alphabetical(catsHier[l0][l1].keys()):
					if showCat[l2]:
						print(2*sp + catString(l2))
						printExpCats(l2, 3)
					for l3 in alphabetical(catsHier[l0][l1][l2].keys()):
						if showCat[l3]:
							print(3*sp + catString(l3))
							printExpCats(l3, 4)
						for l4 in alphabetical(catsHier[l0][l1][l2][l3].keys()):
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

	def findByCat(self, idCat):
		"""find all the experiments under a given category"""
		query = """
				select * from experiments
				join expCats on experiments.idExp=expCats.idExp
				where expCats.idCat=?
				"""
		self.cursExec(query, (idCat,))
		return self.curs.fetchall()

	def findByEntry(self, key):
		"""find all the experiments for a given entry"""
		self.cursExec("""
				select * from experiments
				join entryExps on experiments.idExp=entryExps.idExp
				where entryExps.bibkey=?
				""", (key, ))
		return self.curs.fetchall()

pBDB.exps = experiments()

class entries(pybiblioDBSub):
	"""functions for the entries"""
	def __init__(self): #need to create lastFetched
		pybiblioDBSub.__init__(self)
		self.lastFetched = None

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

	def fetchAll(self, params = None, connection = "and", operator = "=",
			orderBy = "firstdate", orderType = "ASC"):
		"""save entries fetched from the database"""
		query = """
		select * from entries
		"""
		if params and len(params) > 0:
			query += " where "
			first = True
			vals = ()
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
			try:
				self.cursExec(query, vals)
			except:
				print("[DB] query failed: %s"%query)
				print(vals)
		else:
			query += " order by " + orderBy + " " + orderType if orderBy else ""
			try:
				self.cursExec(query)
			except:
				print("[DB] query failed: %s"%query)
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
	
	def getAll(self, params = None, connection = "and ", operator = "=", orderBy = "firstdate", orderType = "ASC"):
		"""get entries from the database"""
		return self.fetchAll(params = params, connection = connection, operator = operator, orderBy = orderBy, orderType = orderType).lastFetched

	def fetchByBibkey(self, bibkey):
		"""shortcut for selecting entries by their bibtek key"""
		if type(bibkey) is list:
			return self.fetchAll(params = {"bibkey": bibkey},
				connection = "or ")
		else:
			return self.fetchAll(params = {"bibkey": bibkey})
		
	def getByBibkey(self, bibkey):
		"""shortcut for selecting entries by their bibtek key"""
		return self.fetchByBibkey(bibkey).lastFetched

	def fetchByKey(self, key):
		"""shortcut for selecting entries based on a current or old key, or searching the bibtex entry"""
		if type(key) is list:
			strings = ["%%%s%%"%q for q in key]
			return self.fetchAll(
				params = {"bibkey": strings, "old_keys": strings, "bibtex": strings},
				connection = "or ",
				operator = " like ")
		else:
			return self.fetchAll(
				params = {"bibkey": "%%%s%%"%key, "old_keys": "%%%s%%"%key, "bibtex": "%%%s%%"%key},
				connection = "or ",
				operator = " like ")

	def getByKey(self, key):
		"""shortcut for selecting entries based on a current or old key, or searching the bibtex entry"""
		return self.fetchByKey(key).lastFetched

	def fetchByBibtex(self, string):
		"""shortcut for selecting entries with a search in the bibtex field"""
		if type(string) is list:
			return self.fetchAll(
				params = {"bibtex":["%%%s%%"%q for q in string]},
				connection = "or",
				operator = " like ")
		else:
			return self.fetchAll(
				params = {"bibtex":"%%%s%%"%string},
				operator = " like ")

	def getByBibtex(self, string):
		"""shortcut for selecting entries with a search in the bibtex field"""
		return self.fetchByBibtex(string).lastFetched

	def getField(self, key, field):
		"""extract the content of one field from a entry in the database, searched by bibtex key"""
		try:
			return self.getByBibkey(key)[0][field]
		except:
			print("[DB] ERROR in getEntryField('%s', '%s')"%(key, field))
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

	def update(self, data, oldkey):
		"""update entry"""
		data["bibkey"] = oldkey
		print("-----\n", data, "\n------\n")
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

	def prepareInsert(self,
			bibtex, bibkey = None, inspire = None, arxiv = None, ads = None, scholar = None, doi = None, isbn = None,
			year = None, link = None, comments = None, old_keys = None, crossref = None,
			exp_paper = None, lecture = None, phd_thesis = None, review = None, proceeding = None, book = None,
			marks = None, firstdate = None, pubdate = None, number = None):
		"""convert a bibtex into a dictionary, eventually using also additional info"""
		data = {}
		if number is None:
			number = 0
		try:
			element = bibtexparser.loads(bibtex).entries[number]
			data["bibkey"] = bibkey if bibkey else element["ID"]	
		except:
			print("[DB] ERROR: impossible to parse bibtex!")
			data["bibkey"] = ""
			return data
		data["bibtex"]  = self.rmBibtexComments(bibtex.strip())
		data["inspire"] = inspire if inspire else None
		if arxiv:
			data["arxiv"] = arxiv
		else:
			try:
				data["arxiv"] = element["arxiv"]
			except:
				try:
					data["arxiv"] = element["eprint"]
				except:
					data["arxiv"] = None
		data["ads"] = ads if ads else None
		data["scholar"] = scholar if scholar else None
		if doi:
			data["doi"] = doi
		else:
			try:
				data["doi"] = element["doi"]
			except:
				data["doi"] = None
		if isbn:
			data["isbn"] = isbn
		else:
			try:
				data["isbn"] = element["isbn"]
			except:
				data["isbn"] = None
		if year:
			data["year"] = year
		else:
			try:
				data["year"] = element["year"]
			except:
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
				except:
					data["year"]=None
		if link:
			data["link"] = link
		else:
			try:
				data["link"] = pbConfig.arxivUrl + "abs/" + data["arxiv"]
			except:
				try:
					data["link"] = pbConfig.doiUrl + data["doi"]
				except:
					data["link"] = None
		data["comments"] = comments if comments else None
		data["old_keys"] = old_keys if old_keys else None
		if crossref:
			data["crossref"] = crossref
		else:
			try:
				data["crossref"] = element["crossref"]
			except:
				data["crossref"] = None
		data["exp_paper"] = 1 if exp_paper else 0
		data["lecture"] = 1 if lecture else 0
		data["phd_thesis"] = 1 if phd_thesis else 0
		data["review"] = 1 if review else 0
		data["proceeding"] = 1 if proceeding else 0
		data["book"] = 1 if book else 0
		data["marks"] = marks if marks else None
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
		writer = bibtexparser.bwriter.BibTexWriter()
		writer.indent = ' '
		writer.comma_first = False
		return writer.write(db)
		
	def updateInspireID(self, string, key = None, number = None):
		"""use inspire websearch module to get and update the inspireID"""
		newid = pyBiblioWeb.webSearch["inspire"].retrieveInspireID(string, number = number)
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
			return self.connExec(query, {"field": value, "bibkey": key})
		else:
			if verbose > 1:
				print("[DB] non-existing field or unappropriated value: (%s, %s, %s)"%(key, field, value))
			return False
	
	def updateBibkey(self, oldKey, newKey):
		"""update the bibkey of an entry"""
		print("[DB] updating bibkey into '%s' for entry '%s'"%(oldKey, newKey))
		try:
			query = "update entries set bibkey=:new where bibkey=:old\n"
			return self.connExec(query, {"new": newKey, "old": oldKey})
		except:
			return False
			
	def getDailyInfoFromOAI(self, date1 = None, date2 = None):
		"""use inspire OAI webinterface to get updated entries between two dates"""
		if date1 is None or not re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", date1):
			date1 = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
		if date2 is None or not re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", date2):
			date2 = datetime.date.today().strftime("%Y-%m-%d")
		yren, monen, dayen = date1.split('-')
		yrst, monst, dayst = date2.split('-')
		print("[DB] calling Inspire OAI harvester between dates %s and %s"%(date1, date2))
		date1 = datetime.datetime(int(yren), int(monen), int(dayen))
		date2 = datetime.datetime(int(yrst), int(monst), int(dayst))
		entries = pyBiblioWeb.webSearch["inspireoai"].retrieveOAIUpdates(date1, date2)
		for e in entries:
			try:
				key = e["bibkey"]
				print(key)
				old = self.extractEntryByBibkey(key)
				if len(old) > 0:
					for [o, d] in pyBiblioWeb.webSearch["inspireoai"].correspondences:
						if e[o] != old[0][d]:
							self.updateEntryField(key, d, e[o], 0)
			except:
				print("[DB][oai] something missing in entry %s"%e["id"])
		print("[DB] inspire OAI harvesting done!")

	def updateInfoFromOAI(self, inspireID, verbose = 0):
		"""use inspire OAI to retrieve the info for a single entry"""
		if not inspireID.isdigit(): #assume it's a key instead of the inspireID
			inspireID = self.getField(inspireID, "inspire")
		result = pyBiblioWeb.webSearch["inspireoai"].retrieveOAIData(inspireID, verbose = verbose)
		if verbose > 1:
			print(result)
		try:
			key = result["bibkey"]
			old = self.getByBibkey(key)
			if verbose > 1:
				print("%s, %s"%(key, old))
			if len(old) > 0:
				for [o, d] in pyBiblioWeb.webSearch["inspireoai"].correspondences:
					try:
						if verbose > 0:
							print("%s = %s (%s)"%(d, result[o], old[0][d]))
						if result[o] != old[0][d]:
							self.updateField(key, d, result[o], 0)
					except:
						print("[DB][oai] key error: (%s, %s)"%(o,d))
			print("[DB] inspire OAI info for %s saved."%inspireID)
		except:
			print("[DB][oai] something missing in entry %s"%result["id"])
			print(traceback.format_exc())
	
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
	
	def searchOAIUpdates(self):
		"""select unpublished papers and look for updates using inspireOAI"""
		entries = self.extractEntries()
		num = 0
		for e in entries:
			if ( e["doi"] is None or "journal" not in e["bibtexDict"].keys() ) \
				and e["proceeding"] == 0 \
				and e["book"] == 0 \
				and e["lecture"] == 0 \
				and e["phd_thesis"] == 0 \
				and e["inspire"] is not None:
					num += 1
					print("\n[DB] looking for update: '%s'"%e["bibkey"])
					self.updateInfoFromOAI(e["inspire"], verbose = 0)
		print("\n[DB] %d entries processed"%num)
		
	def loadAndInsert(self, entry, method = "inspire", imposeKey = None, number = None, returnBibtex = False):
		"""read a list of keywords and look for inspire contents, then load in the database all the info"""
		requireAll = False
		if entry is not None and not type(entry) is list:
			existing = self.getByBibkey(entry)
			if existing:
				print("[DB] Already existing: %s\n"%entry)
				if returnBibtex:
					return existing
				else:
					return True
			if method == "bibtex":
				e = entry
			else:
				e = pyBiblioWeb.webSearch[method].retrieveUrlAll(entry)
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
			if imposeKey is not None:
				data["bibkey"] = imposeKey
				data["bibtex"] = data["bibtex"].replace(key, imposeKey)
				key = imposeKey
			if key.strip() == "":
				print("[DB] ERROR: impossible to insert an entry with empty bibkey!\n%s\n"%entry)
				return False
			print("[DB] entry will have key\n'%s'"%key)
			try:
				self.insert(data)
			except:
				print("[DB] loadAndInsert(%s) failed in inserting entry\n"%entry)
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
				if returnBibtex:
					return e
				else:
					return True
			except:
				print("[DB] loadAndInsertEntries(%s) failed in completing info\n"%entry)
				return False
		elif entry is not None and type(entry) is list:
			failed = []
			for e in entry:
				if not self.loadAndInsert(e):
					failed.append(e)
			if len(failed) > 0:
				print("[DB] ERRORS!\nFailed to load and import entries:\n%s"%", ".join(failed))
		else:
			print("[DB] ERROR: invalid arguments to loadAndInsertEntries!")
			return False

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
			
	def printAllInfo(self, entriesIn = None, orderBy = "firstdate"):
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
		print("[DB] %d elements found"%len(entries))

	def findByCat(self, idCat, orderBy = "entries.firstdate", orderType = "ASC"):
		"""find all the entries in a given category"""
		query = """
				select * from entries
				join entryCats on entries.bibkey=entryCats.bibkey
				where entryCats.idCat=?
				"""
		query += " order by " + orderBy + " " + orderType if orderBy else ""
		self.cursExec(query, (idCat,))
		return self.curs.fetchall()

	def findByExp(self, idExp, orderBy = "entries.firstdate", orderType = "ASC"):
		"""find all the entries for a given experiment"""
		query = """
				select * from entries
				join entryExps on entries.bibkey=entryExps.bibkey
				where entryExps.idExp=?
				"""
		query += " order by " + orderBy + " " + orderType if orderBy else ""
		self.cursExec(query, (idExp,))
		return self.curs.fetchall()

pBDB.bibs = entries()

class utilities(pybiblioDBSub):
	"""various useful functions"""
	def cleanSpareEntries(self):
		"""finds and deletes connections where one of the parts is missing"""
		def deletePresent(ix1, ix2, join, func):
			for e in join:
				if e[0] not in ix1 or e[1] not in ix2:
					print("[DB] cleaning (%s, %s)"%(e[0], e[1]))
					func(e[0], e[1])

		bibkeys = [ e["bibkey"] for e in pBDB.bibs.getAll() ]
		idCats  = [ e["idCat"]  for e in pBDB.cats.getAll() ]
		idExps  = [ e["idExp"]  for e in pBDB.exps.getAll() ]
		
		deletePresent(bibkeys, idExps, [ [e["bibkey"], e["idExp"]] for e in pBDB.bibExp.getAll()], pBDB.bibExp.delete)
		deletePresent(idCats, bibkeys, [ [e["idCat"], e["bibkey"]] for e in pBDB.catBib.getAll()], pBDB.catBib.delete)
		deletePresent(idCats, idExps,  [ [e["idCat"], e["idExp"]]  for e in pBDB.catExp.getAll()], pBDB.catExp.delete)

pBDB.utils = utilities()
