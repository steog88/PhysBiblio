import sys, ast, os
from appdirs import AppDirs

configuration_params = [
{"name": "mainDatabaseName",
	"default": 'PBDATAphysbiblio.db',
	"description": 'Name of the database file',
	"special": None},
{"name": "logFile",
	"default": 'PBDATAparams.log',
	"description": 'Name of the log file',
	"special": None},
{"name": "pdfFolder",
	"default": 'PBDATApdf',
	"description": 'Folder where to save the PDF files',
	"special": None},
{"name": "pdfApplication",
	"default": '',
	"description": 'Application for opening PDF files',
	"special": None},
{"name": "webApplication",
	"default": '',
	"description": 'Web browser',
	"special": None},
{"name": "timeoutWebSearch",
	"default": 20.,
	"description": 'Timeout for the web queries',
	"special": 'float'},
{"name": "askBeforeExit",
	"default": False,
	"description": 'Confirm before exiting',
	"special": 'boolean'},
{"name": "defaultLimitBibtexs",
	"default": 50,
	"description": 'Number of bibtex entries in the initial view of the main table',
	"special": 'int'},
{"name": "defaultUpdateFrom",
	"default": 0,
	"description": 'Index of bibtex entries (firstdate ASC) from which I should start when using "Update bibtexs"',
	"special": 'int'},
{"name": "maxAuthorNames",
	"default": 3,
	"description": 'Max number of authors to be displayed in the main list',
	"special": 'int'},
{"name": "maxAuthorSave",
	"default": 6,
	"description": 'Max number of authors to be saved when adding info from arXiv',
	"special": 'int'},
{"name": "fetchAbstract",
	"default": False,
	"description": 'Automatically fetch the abstract from arXiv if an arxiv number is present',
	"special": 'boolean'},
{"name": "defaultCategories",
	"default": [],
	"description": 'Default categories for imported bibtexs',
	"special": 'list'},
{"name": "bibListFontSize",
	"default": 9,
	"description": 'Font size in the list of bibtex entries and companion boxes',
	"special": 'float'},
{"name": "bibtexListColumns",
	"default": ["bibkey", "author", "title", "year", "firstdate", "pubdate", "doi", "arxiv", "isbn", "inspire"],
	"description": 'The columns to be shown in the entries list',
	"special": 'list'},
]

config_paramOrder = [ p["name"] for p in configuration_params ]
config_defaults = {}
config_descriptions = {}
config_special = {}
for p in configuration_params:
	config_defaults[p["name"]] = p["default"]
	config_descriptions[p["name"]] = p["description"]
	config_special[p["name"]] = p["special"]
		
class ConfigVars():
	"""contains all the common settings and the settings stored in the .cfg file"""
	def __init__(self):
		"""initialize variables and read the external file"""
		self.defaultDirs = AppDirs("PhysBiblio")

		self.configPath = self.defaultDirs.user_config_dir + os.sep
		self.dataPath = self.defaultDirs.user_data_dir + os.sep
		print("Default configuration path: %s"%self.configPath)
		if not os.path.exists(self.configPath):
			os.makedirs(self.configPath)
		print("Default data path: %s"%self.dataPath)
		if not os.path.exists(self.dataPath):
			os.makedirs(self.dataPath)
		self.configProfilesFile = os.path.join(self.configPath, "profiles.dat")
		self.checkOldProfiles()

		self.needFirstConfiguration = False
		self.paramOrder = config_paramOrder
		self.params = {}
		for k, v in config_defaults.items():
			if type(v) is str and "PBDATA" in v:
				v = os.path.join(self.dataPath, v.replace("PBDATA", ""))
				config_defaults[k] = v
			self.params[k] = v
		self.descriptions = config_descriptions

		try:
			with open(self.configProfilesFile) as r:
				txtarr = r.readlines()
			txt = "".join(txtarr)
			self.defProf, self.profiles = ast.literal_eval(txt.replace("\n",""))
		except (IOError, ValueError, SyntaxError) as e:
			print(e)
			self.profiles = {"default": {"f": os.path.join(self.configPath, "params.cfg"), "d":""}}
			self.defProf = "default"
			self.writeProfiles()
		#except ...:
			#...

		for k, prof in self.profiles.items():
			self.profiles[k]["f"] = os.path.join(self.configPath, prof["f"])
		self.checkOldPaths()

		self.defaultProfile = self.profiles[self.defProf]
		print "[config] starting with configuration in '%s'"%self.defaultProfile["f"]
		self.configMainFile = self.defaultProfile["f"]
		
		self.readConfigFile()

		self.arxivUrl = "http://arxiv.org/"
		self.doiUrl = "http://dx.doi.org/"
		self.inspireRecord = "http://inspirehep.net/record/"
		self.inspireSearchBase = "http://inspirehep.net/search"

	def checkOldProfiles(self):
		"""
		Check if there is a profiles.dat file in the 'data/' subfolder.
		If yes, move it to the new self.configPath.
		"""
		if os.path.isfile(os.path.join("data", "profiles.dat")):
			print("[config] Moving profiles.dat from old to new location")
			os.rename(os.path.join("data", "profiles.dat"), self.configProfilesFile)

	def checkOldPaths(self):
		"""
		Check if there are configuration files in the 'data/' subfolder.
		If yes, move them to the new self.configPath or self.dataPath.
		"""
		save = False
		for k, prof in self.profiles.items():
			if "data/" in prof["f"]:
				self.profiles[k]["f"] = prof["f"].replace("data/", "")
				if os.path.isfile(prof["f"]):
					os.rename(prof["f"], os.path.join(self.configPath, self.profiles[k]["f"]))
				save = True
		if save:
			self.writeProfiles()

	def writeProfiles(self):
		if not os.path.exists(self.configPath):
			os.makedirs(self.configPath)
		with open(self.configProfilesFile, 'w') as w:
			w.write("'%s',\n%s\n"%(self.defProf, self.profiles))

	def reInit(self, newShort, newProfile):
		self.defProf = newShort
		for k, v in config_defaults.items():
			self.params[k] = v
		self.defaultProfile = newProfile
		print "[config] starting with configuration in '%s'"%self.defaultProfile["f"]
		self.configMainFile = self.defaultProfile["f"]
		self.params = {}
		self.readConfigFile()
		
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
					elif config_special[k] == 'int':
						self.params[k] = int(v)
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
					print(traceback.format_exc())
					self.params[k] = v
		except IOError:
			print("[config] ERROR: config file %s do not exist. Creating it..."%self.configMainFile)
			self.saveConfigFile()
			self.needFirstConfiguration = True
		except Exception:
			print("[config] ERROR: reading %s file failed."%self.configMainFile)
		
	def saveConfigFile(self):
		"""write the current configuration in a file"""
		txt = ""
		for k in self.paramOrder:
			current = "%s = %s\n"%(k, self.params[k])
			if current != "%s = %s\n"%(k, config_defaults[k]):
				txt += current
		try:
			with open(self.configMainFile, "w") as w:
				w.write(txt)
		except IOError:
			print("[config] ERROR in saving config file!")

pbConfig = ConfigVars()
