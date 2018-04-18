"""
Manages the configuration of PhysBiblio, from saving to reading.

This file is part of the PhysBiblio package.
"""
import sys, ast, os

#these are the default parameter values, descriptions and types
configuration_params = [
{"name": "mainDatabaseName",
	"default": 'data/physbiblio.db',
	"description": 'Name of the database file',
	"special": None},
{"name": "logFileName",
	"default": 'data/params.log',
	"description": 'Name of the log file',
	"special": None},
{"name": "pdfFolder",
	"default": 'data/pdf/',
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
	"""
	Contains all the common settings and the settings stored in the .cfg file.
	Includes also the functions to read and write the config file.
	"""
	def __init__(self):
		"""
		Initialize the configuration.
		Check the profiles first, then for the default profile start with the default parameter values and read the external file.
		"""
		self.needFirstConfiguration = False
		self.paramOrder = config_paramOrder
		self.params = {}
		self.path = os.path.realpath(__file__).replace("physbiblio/config.pyc","").replace("physbiblio/config.py","")
		for k, v in config_defaults.items():
			self.params[k] = v
		self.descriptions = config_descriptions
		self.configProfilesFile = "data/profiles.dat"
		try:
			self.defProf, self.profiles = self.readProfiles()
		except (IOError, ValueError, SyntaxError) as e:
			print(e)
			self.profiles = {"default": {"f": "data/params.cfg", "d":""}}
			self.defProf = "default"
			self.writeProfiles()
		#except ...:
			#...
		self.defaultProfile = self.profiles[self.defProf]
		print("[config] starting with configuration in '%s'"%self.defaultProfile["f"])
		self.configMainFile = self.defaultProfile["f"]
		
		self.readConfigFile()

		#some urls
		self.arxivUrl = "http://arxiv.org/"
		self.doiUrl = "http://dx.doi.org/"
		self.inspireRecord = "http://inspirehep.net/record/"
		self.inspireSearchBase = "http://inspirehep.net/search"

	def readProfiles(self):
		"""
		Reads the list of profiles and the related parameters in the profiles file.
		"""
		with open(self.configProfilesFile) as r:
			txtarr = r.readlines()
		txt = "".join(txtarr)
		return ast.literal_eval(txt.replace("\n",""))

	def writeProfiles(self):
		"""
		Writes the list of profiles and the related parameters in the profiles file.
		"""
		if not os.path.exists("data/"):
			os.makedirs("data/")
		with open(self.configProfilesFile, 'w') as w:
			w.write("'%s',\n%s\n"%(self.defProf, self.profiles))

	def reInit(self, newShort, newProfile):
		"""
		Used when changing profile.
		Reloads all the configuration from scratch given the new profile name.

		Parameters:
			newShort (str): short name for the new profile to be loaded
			newProfile (dict): the profile file dictionary
		"""
		self.defProf = newShort
		for k, v in config_defaults.items():
			self.params[k] = v
		self.defaultProfile = newProfile
		print("[config] starting with configuration in '%s'"%self.defaultProfile["f"])
		self.configMainFile = self.defaultProfile["f"]
		self.params = {}
		self.readConfigFile()
		
	def readConfigFile(self):
		"""
		Read the configuration from a file, whose name is stored in self.configMainFile.
		Parses the various parameters given their declared type.
		"""
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
					self.params[k] = v
		except IOError:
			print("[config] ERROR: config file %s do not exist. Creating it..."%self.configMainFile)
			self.saveConfigFile()
			self.needFirstConfiguration = True
		except Exception:
			print("[config] ERROR: reading %s file failed."%self.configMainFile)
		
	def saveConfigFile(self):
		"""
		Write the current configuration in a file, whose name is stored in self.configMainFile.
		"""
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
