import sys, shutil, urllib2
import os.path as osp
import os

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
		
	def createFolder(self, key):
		directory = self.getFileDir(key)
		if not osp.exists(directory):
			os.makedirs(directory)
		
	def copyNewFile(self, key, ftype, origFile):
		newFile = self.getFilePath(key, ftype)
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
	
	def openFile(self, key, ftype):
		pass
	
	def removeFile(self, key, ftype):
		fname = self.getFilePath(key, ftype)
		try:
			os.remove(fname)
			print("[localPDF] file %s removed"%fname)
		except OSError:
			print("[localPDF] ERROR: impossible to remove file: %s"%fname)

pBPDF = localPDF()
