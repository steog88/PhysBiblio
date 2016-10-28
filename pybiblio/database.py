import sqlite3
import os,re, traceback
import bibtexparser
import pybiblio.webimport.webInterf as webInt

encoding_default='iso-8859-15'
parser = bibtexparser.bparser.BibTexParser()
parser.encoding=encoding_default
parser.customization = parse_accents.parse_accents_record
parser.alt_dict = {}

try:
	from pybiblio.gui.MainWindow import *
	from pybiblio.config import pbConfig
except ImportError:
    print("Could not find pybiblio and its contents: configure your PYTHONPATH!")

class pybiblioDB():
	"""
	Contains most of the DB functions
	"""
	def __init__(self,dbname=pbConfig.params['mainDatabaseName']):
		"""
		Initialize DB class
		"""
		#structure of the tables
		self.tableFields={}
		self.tableFields["entries"]=[
			["bibkey","text","primary key not null"],
			["inspire","text",""],
			["arxiv","text",""],
			["ads","text",""],
			["scholar","text",""],
			["doi","text",""],
			["isbn","text",""],
			["year","int",""],
			["link","text",""],
			["comments","text",""],
			["old_keys","text",""],
			["crossref","text",""],
			["bibtex","text","not null"],
			["exp_paper",	"int","default 0"],
			["lecture",		"int","default 0"],
			["phd_thesis",	"int","default 0"],
			["review",		"int","default 0"],
			["proceeding",	"int","default 0"],
			["book",		"int","default 0"],
			["marks","text",""]];
		self.tableFields["categories"]=[
			["idCat","integer","primary key"],
			["name","text","not null"],
			["description","text","not null"],
			["parentCat","int","default 0"],
			["comments","text","default ''"],
			["ord","int","default 0"]];
		self.tableFields["experiments"]=[
			["idExp","integer","primary key"],
			["name","text","not null"],
			["comments","text","not null"],
			["homepage","text",""],
			["inspire","text",""],
			["project",		"int","default 0"],
			["future",		"int","default 0"],
			["expired",		"int","default 0"],
			["website","text",""]];
		self.tableFields["expCats"]=[
			["idExC","integer","primary key"],
			["idExp","int","not null"],
			["idCat","int","not null"]];
		self.tableFields["entryCats"]=[
			["idEnC","integer","primary key"],
			["bibkey","text","not null"],
			["idCat","int","not null"]];
		self.tableFields["entryExps"]=[
			["idEnEx","integer","primary key"],
			["bibkey","text","not null"],
			["idExp","int","not null"]];
		#names of the columns
		self.tableCols={}
		for q in self.tableFields.keys():
			self.tableCols[q]=[ a[0] for a in self.tableFields[q]]
		
		self.conn=None
		self.curs=None
		self.dbname=dbname
		self.openDB()
		
		self.lastFetchedEntries=None

	#open DB
	def openDB(self):
		db_is_new = not os.path.exists(self.dbname)
		self.conn=sqlite3.connect(self.dbname)
		self.conn.row_factory = sqlite3.Row
		if db_is_new:
			print "-------New database. Creating tables!\n\n"
			self.createTables()
		self.curs=self.conn.cursor()

	def closeDB(self):
		self.conn.close()

	def commit(self):
		self.conn.commit()
		
	def connExec(self,query,data=None):
		try:
			if data:
				self.conn.execute(query,data)
			else:
				self.conn.execute(query)
		except Exception, err:
			print '[connExec] ERROR:', err
			print traceback.format_exc()
			self.conn.rollback()
			return False
		else:
			try:
				mainWin.setWindowTitle("PyBiblio*")
			except:
				pass
			#self.commit()
			return True
	def cursExec(self,query,data=None):
		try:
			if data:
				self.curs.execute(query,data)
			else:
				self.curs.execute(query)
		except Exception, err:
			print '[cursExec] ERROR:', err
			return False
		else:
			return True

	def createTables(self):
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
			print command+"\n"
			if not self.connExec(command):
				print "[DB] error: create %s failed"%q
		command="""
		INSERT into categories (idCat, name, description, parentCat, ord)
			values (0,"Main","This is the main category. All the other ones are subcategories of this one",0,0),
			(1,"Tags","Use this category to store tags (such as: ongoing projects, temporary cats,...)",0,0)
			"""
		print command+"\n"
		if not self.connExec(command):
			print "[DB] error: insert main categories failed"

	#functions for categories
	def insertCat(self,data):
		return self.connExec("""
				INSERT into categories (name, description, parentCat, comments, ord)
					values (:name,:description,:parentCat,:comments,:ord)
				""",data)
	def extractCats(self):
		self.cursExec("""
		select * from categories
		""")
		return self.curs.fetchall()
	def extractCatByName(self,name):
		self.cursExec("""
		select * from categories where name=?
		""",(name,))
		return self.curs.fetchall()
	def extractSubcats(self,parent):
		self.cursExec("""
		select cats1.*
		from categories as cats
		join categories as cats1 on cats.idCat=cats1.parentCat
		where cats.idCat=?
		""",(parent,))
		return self.curs.fetchall()
	def extractParentcat(self,child):
		self.cursExec("""
		select cats.*
		from categories as cats
		join categories as cats1 on cats.idCat=cats1.parentCat
		where cats1.idCat=?
		""",(child,))
		return self.curs.fetchall()
	def deleteCat(self,idCat,name=None):
		if idCat<2 and name:
			result=self.extractCatByName(name)
			idCat=result[0]["idCat"]
		if idCat<2:
			print "[DB] Error: should not delete the category with id: %d%s.)"%(idCat, " (name: %s)"%name if name else "")
			return false
		print "[DB] using idCat=%d"%idCat
		self.cursExec("""
		delete from categories where idCat=?
		""",(idCat,))
		self.cursExec("""
		delete from expCats where idCat=?
		""",(idCat,))
		self.cursExec("""
		delete from entryCats where idCat=?
		""",(idCat,))
		print "[DB] looking for child categories"
		for row in self.extractSubcats(idCat):
			self.deleteCat(row["idCat"])
			
	#functions for entryCat
	def findEntryCat(self, idCat, key):
		return self.connExec("""
				select * from entryCats where bibkey=:bibkey and idCat=:idCat
				""",
				{"bibkey": key, "idCat": idCat)
	def assignEntryCat(self, idCat, key):
		if len(self.findEntryCat(idCat, key))==0:
			return self.connExec("""
					INSERT into entryCats (bibkey, idCat) values (:bibkey, :idCat)
					""",
					{"bibkey": key, "idCat": idCat)
		else:
			print "[DB] entryCat already present"
			return False
	def deleteEntryCat(self, idCat, key):
		return self.connExec("""
				delete from entryCats where bibkey=:bibkey and idCat=:idCat
				""",
				{"bibkey": key, "idCat": idCat)
			
	#functions for expCats
	def findExpCat(self, idCat, idExp):
		return self.connExec("""
				select * from expCats where idExp=:idExp and idCat=:idCat
				""",
				{"idExp": idExp, "idCat": idCat)
	def assignExpCat(self, idCat, idExp):
		if len(self.findExpCat(idCat, idExp))==0:
			return self.connExec("""
					INSERT into expCats (idExp, idCat) values (:idExp, :idCat)
					""",
					{"idExp": idExp, "idCat": idCat)
		else:
			print "[DB] expCat already present"
			return False
	def deleteExpCat(self, idCat, idExp):
		return self.connExec("""
				delete from expCats where idExp=:idExp and idCat=:idCat
				""",
				{"idExp": idExp, "idCat": idCat)
	
	#functions for expCats
	def findEntryExp(self, key, idExp):
		return self.connExec("""
				select * from entryExps where idExp=:idExp and bibkey=:bibkey
				""",
				{"idExp": idExp, "bibkey": key)
	def assignEntryExp(self, key, idExp):
		if len(self.findEntryExp(key, idExp))==0:
			return self.connExec("""
					INSERT into entryExps (idExp, bibkey) values (:idExp, :bibkey)
					""",
					{"idExp": idExp, "bibkey": key)
		else:
			print "[DB] entryExp already present"
			return False
	def deleteEntryExp(self, key, idExp):
		return self.connExec("""
				delete from entryExps where idExp=:idExp and bibkey=:bibkey
				""",
				{"idExp": idExp, "bibkey": key)
	
	#for the entries
	#delete
	def deleteEntries(self, key_list):
		for k in key_list:
			self.deleteEntry(k)
	def deleteEntry(self,key):
		print "[DB] using key=%s"%key
		self.cursExec("""
		delete from entries where bibkey=?
		""",(key,))self.cursExec("""
		delete from entryCats where bibkey=?
		""",(key,))self.cursExec("""
		delete from entryExps where bibkey=?
		""",(key,))

	#extraction
	def extractEntries(self,params=None,connection="and ",operator="=",save=True):
		query="""
		select * from entries
		"""
		if params and len(params)>0:
			query+=" where "
			first=True
			vals=()
			for k,v in params.iteritems():
				if first:
					first=False
				else:
					query+=connection
				query+=k+operator+"? "
				vals+=(v,)
			try:
				self.cursExec(query,vals)
			except:
				print "[DB] query failed: %s"%query
				print vals
		else:
			try:
				self.cursExec(query)
			except:
				print "[DB] query failed: %s"%query
		if save:
			self.lastFetchedEntries=self.curs.fetchall()
			return self.lastFetchedEntries
		else:
			return self.curs.fetchall()
	def extractEntryByBibkey(self,bibkey):
		return self.extractEntries(params={"bibkey":bibkey})
	def extractEntryByKeyword(self,key):
		return self.extractEntries(
			params={"bibkey":"%%%s%%"%key,"old_keys":"%%%s%%"%key,"bibtex":"%%%s%%"%key},
			connection="or ",
			operator=" like ")
	def getEntryField(self, key, field):
		return self.extractEntryByBibkey(key)[0][field]
	def dbEntryToDataDict(self, key):
		return self.prepareInsertEntry(self.getEntryField(key,"bibtex"))
			
	#insertion and update
	def insertEntry(self,data):
		return self.connExec("INSERT into entries ("+
					", ".join(self.tableCols["entries"])+") values (:"+
					", :".join(self.tableCols["entries"])+")\n",
					data)
	def updateEntry(self,data, oldkey):
		data["bibkey"]=oldkey
		print "-----\n",data,"\n------\n"
		query= "replace into entries ("+\
					", ".join(data.keys())+") values (:"+\
					", :".join(data.keys())+")\n"
		return self.connExec(query, data)
	def prepareInsertEntry(self,
			bibtex,bibkey=None,inspire=None,arxiv=None,ads=None,scholar=None,doi=None,isbn=None,
			year=None,link=None,comments=None,old_keys=None,crossref=None,
			exp_paper=None,lecture=None,phd_thesis=None,review=None,proceeding=None,book=None,
			marks=None):
		data={}
		data["bibtex"]=bibtex
		element=bibtexparser.loads(bibtex).entries[0]
		data["bibkey"]=bibkey if bibkey else element["ID"]	
		data["inspire"]=inspire if inspire else None
		if arxiv:
			data["arxiv"]=arxiv
		else:
			if "arxiv" in element.keys():
				data["arxiv"]=element["arxiv"]
			else:
				data["arxiv"]=None
		data["ads"]=ads if ads else None
		data["scholar"]=scholar if scholar else None
		if doi:
			data["doi"]=doi
		else:
			if "doi" in element.keys():
				data["doi"]=element["doi"]
			else:
				data["doi"]=None
		if isbn:
			data["isbn"]=isbn
		else:
			if "isbn" in element.keys():
				data["isbn"]=element["isbn"]
			else:
				data["isbn"]=None
		if year:
			data["year"]=year
		else:
			if "year" in element.keys():
				data["year"]=element["year"]
			else:
				if "arxiv" in data.keys():
					identif=re.compile("([0-9]{4}.[0-9]{4,5}|[0-9]{7})*")
					try:
						for t in identif.finditer(data["arxiv"]):
							if len(t.group())>0:
								e=t.group()
								a=e[0:2]
								if int(a) > 80:
									data["year"]="19"+a
								else:
									data["year"]="20"+a
					except:
						print "[DB] -> Error in converting year"
						data["year"]=None
				else:
					data["year"]=None
		if link:
			data["link"]=link
		else:
			if arxiv in data.keys():
				data["link"]= "http://arxiv.org/abs/"+data["arxiv"]
			elif doi in data.keys():
				data["link"]= "http://www.doi.org/"+data["doi"]
			else:
				data["link"]=None
		data["comments"]=comments if comments else None
		data["old_keys"]=old_keys if old_keys else None
		if crossref:
			data["crossref"]=crossref
		else:
			if crossref in element.keys():
				data["crossref"]=element["crossref"]
			else:
				data["crossref"]=None
		data["exp_paper"]=1 if exp_paper else 0
		data["lecture"]=1 if lecture else 0
		data["phd_thesis"]=1 if phd_thesis else 0
		data["review"]=1 if review else 0
		data["proceeding"]=1 if proceeding else 0
		data["book"]=1 if book else 0
		data["marks"]=marks if marks else None
		return data
		
	def prepareUpdateEntriesByKey(self, key_old, key_new):
		u=pyBiblioDB.prepareUpdateEntry(self.getEntryField(key_old,"bibtex"), self.getEntryField(key_new,"bibtex"))
		return pyBiblioDB.prepareInsertEntry(u)
	
	def prepareUpdateEntryByBibtex(self, key_old, bibtex_new):
		u=pyBiblioDB.prepareUpdateEntry(self.getEntryField(key_old,"bibtex"),bibtex_new)
		return pyBiblioDB.prepareInsertEntry(u)
		
	def prepareUpdateEntry(self, bibtexOld, bibtexNew):
		elementOld=bibtexparser.loads(bibtexOld).entries[0]
		elementNew=bibtexparser.loads(bibtexNew).entries[0]
		db=bibtexparser.bibdatabase.BibDatabase()
		db.entries=[]
		keep=elementOld
		for k in elementNew.keys():
			if k not in elementOld.keys():
				keep[k]=elementNew[k]
			elif elementNew[k] and elementNew[k] != elementOld[k] and k!="bibtex" and k!="ID":
				keep[k] = elementNew[k]
		db.entries.append(keep)
		writer = bibtexparser.bwriter.BibTexWriter()
		writer.indent = ' '
		writer.comma_first = False
		return writer.write(db)
		
	def entryUpdateInspireID(self, key):
		newid=pyBiblioWeb.webSearch["inspire"].retrieveInspireID(key)
		if newid is not "":
			query= "update entries set inspire=:inspire where bibkey=:bibkey\n"
			return self.connExec(query, {"inspire":newid, "bibkey":key})
		else
			return False
	
	def entryUpdateField(self, key, field, value):
		if field in self.tableCols["entries"] and field is not "bibkey" \
				and value is not "" and value is not None:
			query= "update entries set %s=:field where bibkey=:bibkey\n"%field
			return self.connExec(query, {"field":value, "bibkey":key})
		else:
			return False

pyBiblioDB=pybiblioDB()

