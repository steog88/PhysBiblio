import sqlite3
import os, re, traceback, datetime
import bibtexparser
import pybiblio.webimport.webInterf as webInt

try:
	from pybiblio.config import pbConfig
	import pybiblio.parse_accents as parse_accents
	from pybiblio.webimport.webInterf import pyBiblioWeb
except ImportError:
    print("Could not find pybiblio and its contents: configure your PYTHONPATH!")

encoding_default='iso-8859-15'
parser = bibtexparser.bparser.BibTexParser()
parser.encoding=encoding_default
parser.customization = parse_accents.parse_accents_record
parser.alt_dict = {}

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
			["firstdate","text","not null"],
			["pubdate","text",""],
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
			["inspire","text",""]];
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
		print "[database] saved."
		
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
		self.commit()

	#functions for categories
	def insertCat(self,data):
		self.cursExec("""
			select * from categories where name=? and parentCat=?
			""",(data["name"],data["parentCat"]))
		if self.curs.fetchall():
			print "An entry with the same name is already present in the same category!"
			return False
		else:
			return self.connExec("""
				INSERT into categories (name, description, parentCat, comments, ord)
					values (:name,:description,:parentCat,:comments,:ord)
				""",data)
	def extractCats(self):
		self.cursExec("""
		select * from categories
		""")
		return self.curs.fetchall()
	def extractCatsHierarchy(self, cats=None, startFrom=0):
		if cats is None:
			cats=self.extractCats()
		def addSubCats(idC):
			tmp={}
			for c in [ a for a in cats if a["parentCat"]==idC and a["idCat"] != 0 ]:
				tmp[c["idCat"]]={}
			return tmp
		catsHier={}
		new=addSubCats(startFrom)
		catsHier[startFrom]=new
		if len(new.keys())==0:
			return catsHier
		for l0 in catsHier.keys():
			for l1 in catsHier[l0].keys():
				new=addSubCats(l1)
				if len(new.keys())>0:
					catsHier[l0][l1]=new
		for l0 in catsHier.keys():
			for l1 in catsHier[l0].keys():
				for l2 in catsHier[l0][l1].keys():
					new=addSubCats(l2)
					if len(new.keys())>0:
						catsHier[l0][l1][l2]=new
		return catsHier
	def printCatHier(self, startFrom=0, sp="     ", withDesc=False, depth=4):
		cats=self.extractCats()
		if depth<2 or depth>4:
			print "[database] invalid depth in printCatHier (use between 2 and 4)"
		catsHier = self.extractCatsHierarchy(cats, startFrom=startFrom)
		def catString(idCat):
			cat=cats[idCat]
			if withDesc:
				return '%4d: %s - %s'%(cat['idCat'], cat['name'], cat['description'])
			else:
				return '%4d: %s'%(cat['idCat'], cat['name'])
		def alphabetical(listId):
			listIn=[ cats[i] for i in listId ]
			decorated = [(x["name"], x) for x in listIn]
			decorated.sort()
			return [x[1]["idCat"] for x in decorated]
		for l0 in alphabetical(catsHier.keys()):
			print catString(l0)
			if depth>1:
				for l1 in alphabetical(catsHier[l0].keys()):
					print sp+catString(l1)
					if depth>2:
						for l2 in alphabetical(catsHier[l0][l1].keys()):
							print sp+sp+catString(l2)
							if depth>3:
								for l3 in alphabetical(catsHier[l0][l1][l2].keys()):
									print sp+sp+sp+catString(l3)
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
			
	#functions for categories
	def insertExp(self,data):
		return self.connExec("""
				INSERT into experiments (name, comments, homepage, inspire)
					values (:name, :comments, :homepage, :inspire)
				""",data)
	def extractExps(self):
		self.cursExec("""
		select * from experiments
		""")
		return self.curs.fetchall()
	def extractExpByName(self,name):
		self.cursExec("""
		select * from experiments where name=?
		""",(name,))
		return self.curs.fetchall()
	def deleteExp(self,idExp,name=None):
		print "[DB] using idExp=%d"%idExp
		self.cursExec("""
		delete from experiments where idExp=?
		""",(idExp,))
		self.cursExec("""
		delete from expCats where idExp=?
		""",(idExp,))
		self.cursExec("""
		delete from entryExps where idExp=?
		""",(idExp,))
	def printExps(self,exps=None):
		if exps is None:
			exps=self.extractExps()
		for q in exps:
			print "%3d: %-20s [%-40s] [%s]"%(q["idExp"],q["name"],q["homepage"],q["inspire"])

	#functions for entryCat
	def findEntryCat(self, idCat, key):
		self.cursExec("""
				select * from entryCats where bibkey=:bibkey and idCat=:idCat
				""",
				{"bibkey": key, "idCat": idCat})
		return self.curs.fetchall()
	def assignEntryCat(self, idCat, key):
		if type(idCat) is list:
			for q in idCat:
				self.assignEntryCat(q,key)
		elif type(key) is list:
			for q in key:
				self.assignEntryCat(idCat,q)
		else:
			if len(self.findEntryCat(idCat, key))==0:
				return self.connExec("""
						INSERT into entryCats (bibkey, idCat) values (:bibkey, :idCat)
						""",
						{"bibkey": key, "idCat": idCat})
			else:
				print "[DB] entryCat already present:",idCat, key
				return False
	def deleteEntryCat(self, idCat, key):
		if type(idCat) is list:
			for q in idCat:
				self.deleteEntryCat(q,key)
		elif type(key) is list:
			for q in key:
				self.deleteEntryCat(idCat,q)
		else:
			return self.connExec("""
					delete from entryCats where bibkey=:bibkey and idCat=:idCat
					""",
					{"bibkey": key, "idCat": idCat})
			
	#functions for expCats
	def findExpCat(self, idCat, idExp):
		self.cursExec("""
				select * from expCats where idExp=:idExp and idCat=:idCat
				""",
				{"idExp": idExp, "idCat": idCat})
		return self.curs.fetchall()
	def assignExpCat(self, idCat, idExp):
		if type(idCat) is list:
			for q in idCat:
				self.assignExpCat(q,idExp)
		elif type(idExp) is list:
			for q in idExp:
				self.assignExpCat(idCat,q)
		else:
			if len(self.findExpCat(idCat, idExp))==0:
				return self.connExec("""
						INSERT into expCats (idExp, idCat) values (:idExp, :idCat)
						""",
						{"idExp": idExp, "idCat": idCat})
			else:
				print "[DB] expCat already present", idCat, idExp
				return False
	def deleteExpCat(self, idCat, idExp):
		if type(idCat) is list:
			for q in idCat:
				self.deleteExpCat(q,idExp)
		elif type(idExp) is list:
			for q in idExp:
				self.deleteExpCat(idCat,q)
		else:
			return self.connExec("""
					delete from expCats where idExp=:idExp and idCat=:idCat
					""",
					{"idExp": idExp, "idCat": idCat})
	
	#functions for expCats
	def findEntryExp(self, key, idExp):
		self.cursExec("""
				select * from entryExps where idExp=:idExp and bibkey=:bibkey
				""",
				{"idExp": idExp, "bibkey": key})
		return self.curs.fetchall()
	def assignEntryExp(self, key, idExp):
		if type(key) is list:
			for q in key:
				self.assignEntryExp(q,idExp)
		elif type(idExp) is list:
			for q in idExp:
				self.assignEntryExp(key,q)
		else:
			if len(self.findEntryExp(key, idExp))==0:
				if self.connExec("""
						INSERT into entryExps (idExp, bibkey) values (:idExp, :bibkey)
						""",
						{"idExp": idExp, "bibkey": key}):
					for c in self.findCatsForExp(idExp):
						self.assignEntryCat(c["idCat"],key)
			else:
				print "[DB] entryExp already present", idExp, key
				return False
	def deleteEntryExp(self, key, idExp):
		if type(key) is list:
			for q in key:
				self.deleteEntryExp(q,idExp)
		elif type(idExp) is list:
			for q in idExp:
				self.deleteEntryExp(key,q)
		else:
			return self.connExec("""
					delete from entryExps where idExp=:idExp and bibkey=:bibkey
					""",
					{"idExp": idExp, "bibkey": key})
	
	#various filtering
	def findExpsByCat(self, idCat):
		self.cursExec("""
				select * from experiments
				join expCats on experiments.idExp=expCats.idExp
				where expCats.idCat=?
				""", (idCat,))
		return self.curs.fetchall()
	def findEntriesByCat(self, idCat):
		self.cursExec("""
				select * from entries
				join entryCats on entries.bibkey=entryCats.bibkey
				where entryCats.idCat=?
				""", (idCat,))
		return self.curs.fetchall()
	def findEntriesByExp(self, idExp):
		self.cursExec("""
				select * from entries
				join entryExps on entries.bibkey=entryExps.bibkey
				where entryExps.idExp=?
				""", (idExp,))
		return self.curs.fetchall()
	def findCatsForExp(self, idExp):
		self.cursExec("""
				select * from categories
				join expCats on categories.idCat=expCats.idCat
				where expCats.idExp=?
				""", (idExp,))
		return self.curs.fetchall()
	def findCatsForEntry(self, key):
		self.cursExec("""
				select * from categories
				join entryCats on categories.idCat=entryCats.idCat
				where entryCats.bibkey=?
				""", (key,))
		return self.curs.fetchall()
	def findExpsForEntry(self, key):
		self.cursExec("""
				select * from experiments
				join entryExps on experiments.idExp=entryExps.idExp
				where entryExps.bibkey=?
				""", (key,))
		return self.curs.fetchall()
	
	#for the entries
	#delete
	def deleteEntries(self, key_list):
		for k in key_list:
			self.deleteEntry(k)
	def deleteEntry(self,key):
		print "[DB] using key=%s"%key
		self.cursExec("""
		delete from entries where bibkey=?
		""",(key,))
		self.cursExec("""
		delete from entryCats where bibkey=?
		""",(key,))
		self.cursExec("""
		delete from entryExps where bibkey=?
		""",(key,))

	#extraction
	def extractEntries(self,params=None,connection="and ",operator="=",save=True, orderBy=None, orderType="ASC"):
		query="""
		select * from entries
		"""
		query += " order by "+orderBy+" "+orderType if orderBy else ""
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
	def getDoiUrl(self, key):
		url = "http://dx.doi.org/" + self.getEntryField(key, "doi")
		return url
	def getArxivUrl(self, key, urlType = "abs"):
		url = "http://arxiv.org/"+ urlType + "/" + self.getEntryField(key, "arxiv")
		return url
			
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
	def rmBibtexComments(self, bibtex):
		output=""
		for l in bibtex.splitlines():
			lx=l.strip()
			if len(lx)>0 and lx[0]!="%":
				output+=l+"\n"
		return output.strip()
	def prepareInsertEntry(self,
			bibtex,bibkey=None,inspire=None,arxiv=None,ads=None,scholar=None,doi=None,isbn=None,
			year=None,link=None,comments=None,old_keys=None,crossref=None,
			exp_paper=None,lecture=None,phd_thesis=None,review=None,proceeding=None,book=None,
			marks=None, firstdate=None, pubdate=None):
		data={}
		data["bibtex"]=self.rmBibtexComments(bibtex.strip())
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
		data["firstdate"]=firstdate if firstdate else datetime.date.today().strftime("%Y-%m-%d")
		data["pubdate"]=pubdate if pubdate else ""
		return data
		
	def prepareUpdateEntriesByKey(self, key_old, key_new):
		u=self.prepareUpdateEntry(self.getEntryField(key_old,"bibtex"), self.getEntryField(key_new,"bibtex"))
		return self.prepareInsertEntry(u)
	
	def prepareUpdateEntryByBibtex(self, key_old, bibtex_new):
		u=self.prepareUpdateEntry(self.getEntryField(key_old,"bibtex"),bibtex_new)
		return self.prepareInsertEntry(u)
		
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
		
	def updateEntryInspireID(self, string, key=None):
		newid=pyBiblioWeb.webSearch["inspire"].retrieveInspireID(string)
		if key is None:
			key=string
		if newid is not "":
			query= "update entries set inspire=:inspire where bibkey=:bibkey\n"
			if self.connExec(query, {"inspire":newid, "bibkey":key}):
				return newid
		else:
			return False
	
	def updateEntryField(self, key, field, value):
		if field in self.tableCols["entries"] and field is not "bibkey" \
				and value is not "" and value is not None:
			query= "update entries set "+field+"=:field where bibkey=:bibkey\n"
			return self.connExec(query, {"field":value, "bibkey":key})
		else:
			return False
			
	def getUpdateInfoDaysFromOAI(self, date1=None, date2=None):
		if date1 is None or not re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", date1):
			date1 = (datetime.date.today()-datetime.timedelta(1)).strftime("%Y-%m-%d")
		if date2 is None or not re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", date2):
			date2 = datetime.date.today().strftime("%Y-%m-%d")
		yren,monen,dayen=date1.split('-')
		yrst,monst,dayst=date2.split('-')
		print "[database] calling Inspire OAI harvester between dates %s and %s"%(date1, date2)
		date1=datetime.datetime(int(yren), int(monen), int(dayen))
		date2=datetime.datetime(int(yrst), int(monst), int(dayst))
		entries=pyBiblioWeb.webSearch["inspireoai"].retrieveOAIUpdates(date1, date2)
		for e in entries:
			try:
				key=e["bibkey"]
				print key
				old=self.extractEntryByBibkey(key)
				if len(old)>0:
					for [o,d] in pyBiblioWeb.webSearch["inspireoai"].correspondences:
						if e[o] != old[0][d]:
							self.updateEntryField(key, d, e[o])
			except:
				print "[database][inspireoai] something missing in entry %s"%e["id"]
		print "[database] inspire OAI harvesting done!"

	def getUpdateInfoEntryFromOAI(self, inspireID):
		result=pyBiblioWeb.webSearch["inspireoai"].retrieveOAIData(inspireID)
		try:
			key=result["bibkey"]
			print key
			old=self.extractEntryByBibkey(key)
			if len(old)>0:
				for [o,d] in pyBiblioWeb.webSearch["inspireoai"].correspondences:
					try:
						if result[o] != old[0][d]:
							self.updateEntryField(key, d, result[o])
					except:
						print "[database][inspireoai] key error: (%s, %s)"%(o,d)
			print "[database] inspire OAI info for %s saved!"%inspireID
		except:
			print "[database][inspireoai] something missing in entry %s"%result["id"]
			print traceback.format_exc()
		
	def loadAndInsertEntries(self, entry):
		if entry is not None and not type(entry) is list:
			if self.extractEntryByBibkey(entry):
				print "[database] Already existing: %s"%entry
				return False
			e = pyBiblioWeb.webSearch["inspire"].retrieveUrlFirst(entry)
			data=self.prepareInsertEntry(e)
			key=data["bibkey"]
			if self.insertEntry(data):
				eid = self.updateEntryInspireID(entry,key)
				self.getUpdateInfoEntryFromOAI(eid)
				return True
			else:
				print "[database] loadAndInsertEntries(%s) failed"%entry
				return False
		elif entry is not None and type(entry) is list:
			for e in entry:
				self.loadAndInsertEntries(e)
		else:
			print "[database] ERROR: invalid arguments to loadAndInsertEntries"
			return False

	def setReview(self,key):
		if type(key) is list:
			for q in key:
				self.setReview(q)
		else:
			return self.updateEntryField(key,"review",1)
	def setProceeding(self,key):
		if type(key) is list:
			for q in key:
				self.setProceeding(q)
		else:
			return self.updateEntryField(key,"proceeding",1)
	def setBook(self,key):
		if type(key) is list:
			for q in key:
				self.setBook(q)
		else:
			return self.updateEntryField(key,"book",1)
	def setLecture(self,key):
		if type(key) is list:
			for q in key:
				self.setLecture(q)
		else:
			return self.updateEntryField(key,"lecture",1)
	def setPhdThesis(self,key):
		if type(key) is list:
			for q in key:
				self.setPhdThesis(q)
		else:
			return self.updateEntryField(key,"phd_thesis",1)
			
	def printAllBibtexs(self):
		entries = self.extractEntries(orderBy="firstdate")
		for i,e in enumerate(entries):
			print i,e["bibtex"]
			print "\n"
		print "[database] %d elements found"%len(entries)
			
	def printAllBibkeys(self):
		entries = self.extractEntries(orderBy="firstdate")
		for i,e in enumerate(entries):
			print i,e["bibkey"]
		print "[database] %d elements found"%len(entries)
		
pBDB=pybiblioDB()
