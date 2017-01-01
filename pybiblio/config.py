import sys

config_defaults = {
	"configMainFile":   'data/params.cfg',
	"timeoutWebSearch": 10.,
	"mainDatabaseName": 'data/pybiblio.db',
	"pdfFolder":        'data/pdf/',
	"pdfApplication":   'okular',
	"webApplication":   'google-chrome',
	"askBeforeExit":	False
}
config_descriptions = {
	"configMainFile":   'Name of the configuration file',
	"timeoutWebSearch": 'Timeout for the web queries',
	"mainDatabaseName": 'Name of the database file',
	"pdfFolder":        'Folder where to save the PDF files',
	"pdfApplication":   'Application for opening PDF files',
	"webApplication":   'Web browser',
	"askBeforeExit":	'Confirm before exiting',
}
config_special = {
	"timeoutWebSearch": 'float',
	"askBeforeExit":	'boolean',
}
		
class ConfigVars():
	"""contains all the common settings and the settings stored in the .cfg file"""
	def __init__(self):
		"""initialize variables and read the external file"""
		self.params = config_defaults
		self.descriptions = config_descriptions
		self.configMainFile = self.params["configMainFile"]
		if len(sys.argv) > 1:
			self.configMainFile = sys.argv[1]
		
		self.readConfigFile()

		self.arxivUrl = "http://arxiv.org/"
		self.doiUrl = "http://dx.doi.org/"
		self.inspireRecord = "http://inspirehep.net/record/"
		self.inspireSearchBase = "http://inspirehep.net/search"
	
	def readConfigFile(self):
		"""read all the configuration from an external file"""
		try:
			with open(self.configMainFile) as r:
				txt = r.readlines()
			for l in txt:
				k, v = l.replace("\n", "").split(" = ")
				try:
					if config_special[k] == 'float':
						self.params[k] = float(v)
					elif config_special[k] == 'boolean':
						if v.lower() in ('true','1','yes','on'):
							self.params[k] = True
						elif v.lower() in ('false','0','no','off'):
							self.params[k] = False
						else:
							raise ValueError
					else:
						self.params[k] = float(v)
				except:
					self.params[k] = v
		except IOError:
			print("[config] ERROR: config file %s do not exist. Creating it..."%self.configMainFile)
			self.saveConfigFile()
		except:
			print("[config] ERROR: reading %s file failed."%self.configMainFile)
		
	def saveConfigFile(self):
		"""write the current configuration in a file"""
		txt = ""
		for k, v in self.params.items():
			txt += "%s = %s\n"%(k, v)
		try:
			with open(self.configMainFile, "w") as w:
				w.write(txt)
		except e:
			print("[config] ERROR in saving config file!")
			print(e)

pbConfig = ConfigVars()
