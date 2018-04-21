"""
Functions that should run only when PhysBiblio is opened for the first time.

This file is part of the physbiblio package.
"""
import os, traceback
try:
	from physbiblio.errors import pBLogger
	from physbiblio.config import pbConfig
	import physbiblio.tablesDef
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
	print(traceback.format_exc())
	raise

def createTables(database):
	"""
	Create tables for the database (and insert the default categories), if it is missing.
	"""
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
		pBLogger.info(command+"\n")
		if not database.connExec(command):
			pBLogger.critical("Create %s failed"%q, exec_info = True)
	command="""
	INSERT into categories (idCat, name, description, parentCat, ord)
		values (0,"Main","This is the main category. All the other ones are subcategories of this one",0,0),
		(1,"Tags","Use this category to store tags (such as: ongoing projects, temporary cats,...)",0,0)
		"""
	pBLogger.info(command+"\n")
	if not database.connExec(command):
		pBLogger.exception("Insert main categories failed", exec_info = True)
	database.commit()
		
