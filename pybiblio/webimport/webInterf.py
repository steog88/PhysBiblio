import sys,re,os
from urllib2 import Request
import urllib2
import pkgutil
try:
	import pybiblio.webimport as wi
	from pybiblio.database import *
	from pybiblio.config import pbConfig
except ImportError:
	print("Could not find pybiblio and its contents: configure your PYTHONPATH!")
pkgpath = os.path.dirname(wi.__file__)
webInterfaces=[name for _, name, _ in pkgutil.iter_modules([pkgpath])]

class webInterf():
	def __init__(self):
		self.url=None
		self.urlArgs=None
		self.urlTimeout=float(pbConfig.params["timeoutWebSearch"])
		#save the names of the available web search interfaces
		self.interfaces=[a for a in webInterfaces if a != "webInterf" ]
		self.webSearch={}
		self.loadInterfaces()
		
	def createUrl(self):
		return self.url+"?"+"&".join([a+"="+b for a,b in self.urlArgs.iteritems()])
		
	def textFromUrl(self,url):
		try:
			response = urllib2.urlopen(url, timeout=self.urlTimeout)
		except:
			print "[%s] -> error in retriving data from url"%self.name
			return None
		data = response.read()
		try:
			text = data.decode('utf-8')
		except:
			print "[%s] -> bad codification, utf-8 decode failed"%self.name
			return None
		return text
	
	def retrieveUrlFirst(self,search):
		return None
	def retrieveUrlAll(self,search):
		return None
	
	def loadInterfaces(self):
		for q in self.interfaces:
			try:
				_temp=__import__("pybiblio.webimport."+q, globals(), locals(), ["webSearch"], -1)
				self.webSearch[q] = getattr(_temp,"webSearch")()
			except:
				print "pybiblio.webimport.%s import error"%q
		
	def loadBibtexsForTex(self,texsFolder):
		d=os.listdir(texsFolder)
		texs=[]
		for e in d:
			if e.find('.tex')>0 and e.find('.bac')<0 and e.find('~')<0:
				texs.append(e)
		keyscont=""
		for t in texs:
			with open(texsFolder+t) as r:
				keyscont += r.read()
		cite=re.compile('\\\\cite?\{([A-Za-z]*:[0-9]*[a-z]*[,]?[\n ]*|[A-Za-z0-9\-][,]?[\n ]*)*\}',re.MULTILINE)	#find \cite{...}
		bibel=re.compile('@[a-zA-Z]*\{([A-Za-z]*:[0-9]*[a-z]*)?,',re.MULTILINE|re.DOTALL)	#find the @Article(or other)...}, entry for the key "m"
		bibty=re.compile('@[a-zA-Z]*\{',re.MULTILINE|re.DOTALL)	#find the @Article(or other) entry for the key "m"

		citaz=[m for m in cite.finditer(keyscont)]
		strs=[]
		for c in citaz:
			b=c.group().replace(r'\cite{','')
			d=b.replace(' ','')
			b=d.replace('\n','')
			d=b.replace(r'}','')
			a=d.split(',')
			for e in a:
				if e not in strs:
					strs.append(e)
		print "[%s] keys found: %d"%(self.name,len(strs))
		missing=[]				
		notfound=""
		keychange=""
		warnings=0
		for s in strs:
			if not len(pyBiblioDB.extractEntryByBibkey(s))>0:
				tmp=pyBiblioDB.extractEntryByKeyword(s)
				if not len(tmp)>0:
					missing.append(s)
				else:
					keychange+= "[%s] -- warning: %s may have a new key? %s\n"%(self.name,m,tmp['bibkey'])
		print "[%s] missing: %d"%(self.name,len(missing))
		for m in missing:
			new=self.retrieveUrlFirst(m)
			if len(new)>0:
				data=pyBiblioDB.prepareInsertEntry(new)
				pyBiblioDB.insertEntry(data)
				#autoImport()
				#pass
			else:
				notfound+="[%s] -- warning: entry not found for %s\n"%(self.name,m)
				warnings+=1
		print notfound
		print keychange
		print "[%s] -- %d warning(s) occurred!"%(self.name,warnings)
		
pyBiblioWeb=webInterf()
