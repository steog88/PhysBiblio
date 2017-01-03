import sys, ast

config_defaults = {
	"configMainFile":   'data/params.cfg',
	"timeoutWebSearch": 10.,
	"mainDatabaseName": 'data/pybiblio.db',
	"pdfFolder":        'data/pdf/',
	"pdfApplication":   'okular',
	"webApplication":   'google-chrome',
	"askBeforeExit":	False,
	"maxAuthorNames":	3,
	"bibListFontSize":	8,
	"bibtexListColumns":["bibkey", "author", "title", "year", "firstdate", "pubdate", "doi", "arxiv", "isbn", "inspire", "link"]
}
config_descriptions = {
	"configMainFile":   'Name of the configuration file',
	"timeoutWebSearch": 'Timeout for the web queries',
	"mainDatabaseName": 'Name of the database file',
	"pdfFolder":        'Folder where to save the PDF files',
	"pdfApplication":   'Application for opening PDF files',
	"webApplication":   'Web browser',
	"askBeforeExit":	'Confirm before exiting',
	"maxAuthorNames":	'Max number of authors to be displayed in the main list',
	"bibListFontSize":	'Font size in the list of bibtex entries and companion boxes',
	"bibtexListColumns":'The columns to be shown in the entries list',
}
config_special = {
	"timeoutWebSearch": 'float',
	"bibListFontSize":	'float',
	"maxAuthorNames":	'float',
	"askBeforeExit":	'boolean',
	"bibtexListColumns":'list'
}
		
class ConfigVars():
	"""contains all the common settings and the settings stored in the .cfg file"""
	def __init__(self):
		"""initialize variables and read the external file"""
		self.params = {}
		for k, v in config_defaults.items():
			self.params[k] = v
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
		for k, v in config_defaults.items():
			self.params[k] = v
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
					elif config_special[k] == 'list':
						self.params[k] = ast.literal_eval(v.strip())
					else:
						self.params[k] = v
				except Exception:
					self.params[k] = v
		except IOError:
			print("[config] ERROR: config file %s do not exist. Creating it..."%self.configMainFile)
			self.saveConfigFile()
		except Exception:
			print("[config] ERROR: reading %s file failed."%self.configMainFile)
		
	def saveConfigFile(self):
		"""write the current configuration in a file"""
		txt = ""
		for k, v in self.params.items():
			current = "%s = %s\n"%(k, v)
			if current != "%s = %s\n"%(k, config_defaults[k]):
				txt += current
		try:
			with open(self.configMainFile, "w") as w:
				w.write(txt)
		except IOError:
			print("[config] ERROR in saving config file!")
			print(e)

pbConfig = ConfigVars()
