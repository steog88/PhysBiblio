import os, sys, numpy, codecs
try:
	from pybiblio.database import *
except ImportError:
	print("Could not find pybiblio and its contents: configure your PYTHONPATH!")

def exportLast(fname):
	if pybiblioDB.lastFetchedEntries:
		txt=""
		for q in pybiblioDB.lastFetchedEntries:
			txt+=q["bibtex"]+"\n"
		
		try:
			with codecs.open(fname, 'w','utf-8') as bibfile:
				bibfile.write(txt)
		except Exception, e:
			print e
			print traceback.format_exc()
			sys.stderr.write("error: "+readfilebib)
			os.rename(readfilebib+backupextension+".old", readfilebib+backupextension)

def exportAll(fname):
	rows=pybiblio.extractEntries()
	if len(rows>0):
		txt=""
		for q in pybiblioDB.lastFetchedEntries:
			txt+=q["bibtex"]+"\n"
		
		try:
			with codecs.open(fname, 'w','utf-8') as bibfile:
				bibfile.write(txt)
		except Exception, e:
			print e
			print traceback.format_exc()
			sys.stderr.write("error: "+readfilebib)
			os.rename(readfilebib+backupextension+".old", readfilebib+backupextension)
