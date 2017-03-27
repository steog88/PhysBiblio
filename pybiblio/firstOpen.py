import os, traceback
try:
	import pybiblio.errors as pBErrorManager
except ImportError:
	print("Could not find pybiblio.errors and its contents: configure your PYTHONPATH!")
	print(traceback.format_exc())
try:
	from pybiblio.config import pbConfig
	import pybiblio.tablesDef
except ImportError:
    pBErrorManager("Could not find pybiblio and its contents: configure your PYTHONPATH!", traceback)

#write here the functions to define the user settings and create the database and config file. 

#db_is_new = not os.path.exists(pbConfig.params['mainDatabaseName'])
#if db_is_new:
	#print("-------New database. Creating tables!\n\n")
	#createTables(pBDB)

def createTables(database):
	"""create tables: useful only at first use"""
	for q in database.tableFields.keys():
		command="CREATE TABLE "+q+" (\n"
		first=True
		for el in database.tableFields[q]:
			if first:
				first=False
			else:
				command+=",\n"
			command+=" ".join(el)
		command+=");"
		print(command+"\n")
		if not database.connExec(command):
			pBErrorManager("[DB] error: create %s failed"%q)
	command="""
	INSERT into categories (idCat, name, description, parentCat, ord)
		values (0,"Main","This is the main category. All the other ones are subcategories of this one",0,0),
		(1,"Tags","Use this category to store tags (such as: ongoing projects, temporary cats,...)",0,0)
		"""
	print(command+"\n")
	if not database.connExec(command):
		pBErrorManager("[DB] error: insert main categories failed")
	database.commit()
		
