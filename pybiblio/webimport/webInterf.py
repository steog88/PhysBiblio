import sys,re,os
from urllib2 import Request
import urllib2
import pkgutil
import pybiblio.webimport as wi
pkgpath = os.path.dirname(wi.__file__)
webInterfaces=[name for _, name, _ in pkgutil.iter_modules([pkgpath])]

class webInterf():
	def __init__(self):
		self.url=None
		self.urlArgs=None
		#save the names of the available web search interfaces
		self.interfaces=[a for a in webInterfaces if a != "webInterf" ]
		self.webSearch={}
		
	def createUrl(self):
		return self.url+"?"+"&".join([a+"="+b for a,b in self.urlArgs.iteritems()])
		
	def textFromUrl(self,url):
		try:
			response = urllib2.urlopen(url)
		except:
			print "error in retriving data from url"
			return None
		data = response.read()
		try:
			text = data.decode('utf-8')
		except:
			print "bad codification, utf-8 decode failed"
			return None
			
		return text
	
	def loadInterfaces(self):
		for q in self.interfaces:
			try:
				_temp=__import__("pybiblio.webimport."+q, globals(), locals(), ["webSearch"], -1)
				self.webSearch[q] = getattr(_temp,"webSearch")()
			except:
				print "pybiblio.webimport.%s import error"%q
		
