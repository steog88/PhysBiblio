import sys, shutil, urllib2
import os.path as osp
import os
import subprocess

try:
	from pybiblio.config import pbConfig
	from pybiblio.database import pBDB
except ImportError:
	print("[CLI] Could not find pybiblio and its contents: configure your PYTHONPATH!")
	print traceback.format_exc()
	
class localPDF():
	def __init__(self):
		if pbConfig.params["pdfFolder"][0] == "/":
			self.pdfDir = pbConfig.params["pdfFolder"]
		else:
			self.pdfDir = osp.join(osp.split(osp.abspath(sys.argv[0]))[0], pbConfig.params["pdfFolder"])
		self.badFNameCharacters = r'\/:*?"<>|'
		self.pdfApp = pbConfig.params["pdfApplication"]
		
	def badFName(self, value):
		new=""
		for i in value:
			if i not in self.badFNameCharacters:
				new += i
			else:
				new += "_"
		return new
		
	def getFileDir(self, key):
		return osp.join(self.pdfDir, self.badFName(key))
		
	def getFilePath(self, key, ftype):
		fname = pBDB.getEntryField(key, ftype)
		if fname is None:
			print("[localPDF] impossible to get the type '%s' filename for entry %s"%(ftype, key))
			return ""
		else:
			fname = self.badFName(fname)
			return osp.join(self.getFileDir(key), fname + '.pdf')
		
	def createFolder(self, key, noCheck = False):
		directory = self.getFileDir(key)
		if noCheck or not osp.exists(directory):
			os.makedirs(directory)
		
	def copyNewFile(self, key, origFile, ftype = None, customName = None):
		if not osp.exists(self.getFileDir(key)):
			self.createFolder(key, True)
		if customName is not None:
			newFile = customName
		elif ftype is not None:
			newFile = self.getFilePath(key, ftype)
		else:
			print("[localPDF] ERROR: you should supply a ftype ('doi' or 'arxiv') or a customName!")
			return
		try:
			shutil.copy2(origFile, newFile)
			print("[localPDF] %s copied to %s"%(origFile, newFile))
		except:
			print("[localPDF] ERROR: impossible to copy %s to %s"%(origFile, newFile))
		
	def downloadArxiv(self, key, force = False):
		fname = self.getFilePath(key, "arxiv")
		if osp.exists(fname) and not force:
			print("[localPDF] There is already a pdf and overwrite not requested.")
			return
		try:
			self.createFolder(key)
			url = pBDB.getArxivUrl(key, 'pdf')
			print("[localPDF] Downloading arXiv PDF from %s"%url)
			response = urllib2.urlopen(url)
			with open(fname, 'wb') as newF:
				newF.write(response.read())
			print("[localPDF] File saved to %s"%fname)
		except:
			print("[localPDF] Impossible to download the arXiv PDF for '%s'"%key)
	
	def openFile(self, key, arg = None, fileType = None, fileNum = None, fileName = None):
		try:
			if arg == "arxiv" or arg == "doi":
				fileType = arg
			elif float(arg).is_integer():
				fileNum = int(arg)
		except:
			if arg is not None:
				fileName = arg
		try:
			if fileType is not None:
				fName = self.getFilePath(key, fileType)
			elif fileNum is not None:
				fName = self.getExisting(key, True)[fileNum]
			elif fileName is not None:
				fName = osp.join(self.getFileDir(key), fileName)
			else:
				print("[localPDF] ERROR: invalid selection. One among fileType, fileNum or fileName must be given!")
				return
			print("[localPDF] opening '%s'..."%fName)
			subprocess.Popen([self.pdfApp, fName], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		except:
			print("[localPDF] opening PDF for '%s' failed!"%key)
	
	def removeFile(self, key, ftype):
		fname = self.getFilePath(key, ftype)
		try:
			os.remove(fname)
			print("[localPDF] file %s removed"%fname)
		except OSError:
			print("[localPDF] ERROR: impossible to remove file: %s"%fname)
			
	def getExisting(self, key, fullPath = False):
		fileDir = self.getFileDir(key)
		try:
			if fullPath:
				return [ osp.join(fileDir, e) for e in os.listdir(fileDir) ]
			else:
				return os.listdir(fileDir)
		except:
			return []
			
	def printExisting(self, key, fullPath = False):
		print("[localPDF] Listing file for entry '%s', located in %s:"%(key, self.getFileDir(key)))
		for i,e in enumerate(self.getExisting(key, fullPath = fullPath)):
			print("%2d: %s"%(i,e))
	
	def printAllExisting(self, entries = None, fullPath = False):
		if entries is None:
			entries = pBDB.extractEntries(orderBy = "firstdate")
		for e in entries:
			exist = self.getExisting(e["bibkey"], fullPath = fullPath)
			if len(exist) > 0:
				print("%30s: [%s]"%(e["bibkey"], "] [".join(exist)))

pBPDF = localPDF()
