import sqlite3
import os

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
			print 'ERROR:', err
			self.conn.rollback()
		else:
			mainWin.setWindowTitle("PyBiblio*")
			#self.commit()
	def cursExec(self,query,data=None):
		try:
			if data:
				self.curs.execute(query,data)
			else:
				self.curs.execute(query)
		except Exception, err:
			print 'ERROR:', err

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
			self.connExec(command)
		command="""
		INSERT into categories (idCat, name, description, parentCat, ord)
			values (0,"Main","This is the main category. All the other ones are subcategories of this one",0,0)
			"""
		print command+"\n"
		self.connExec(command)

	def insertCat(self,data):
		self.connExec("""
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
	def extractEntries(self):
		self.cursExec("""
		select * from entries
		""")
		return self.curs.fetchall()

pyBiblioDB=pybiblioDB()
pyBiblioDB.extractParentcat(1)
