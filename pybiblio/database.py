import sqlite3
import os,re
import bibtexparser

try:
    from pybiblio.gui.MainWindow import *
except ImportError:
    print("Could not find pybiblio and its contents: configure your PYTHONPATH!")

class pybiblioDB():
	"""
	Contains most of the DB functions
	"""
	def __init__(self,dbname='data/pybiblio.db'):
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
		self.tableFields["tags"]=[
			["idTag","integer","primary key"],
			["name","text","not null"],
			["description","text","not null"],
			["comments","text",""],
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
		self.tableFields["expTags"]=[
			["idExT","integer","primary key"],
			["idExp","int","not null"],
			["idTag","int","not null"]];
		self.tableFields["entryCats"]=[
			["idEnC","integer","primary key"],
			["bibkey","text","not null"],
			["idCat","int","not null"]];
		self.tableFields["entryTags"]=[
			["idEnT","integer","primary key"],
			["bibkey","text","not null"],
			["idTag","int","not null"]];
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
			values (0,"Main","This is the main category. All the other ones are subcategories of this one",0,0)
			"""
		print command+"\n"
		if not self.connExec(command):
			print "[DB] error: insert main category failed"

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

	#for the entries
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
	def insertEntry(self,data):
		return self.connExec("INSERT into entries ("+
					", ".join(self.tableCols["entries"])+") values (:"+
					", :".join(self.tableCols["entries"])+")\n",
					data)
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

pyBiblioDB=pybiblioDB()

