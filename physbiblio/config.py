"""
Manages the configuration of PhysBiblio, from saving to reading.

This file is part of the physbiblio package.
"""
import sys, ast, os
import logging
import glob
from appdirs import AppDirs

#these are the default parameter values, descriptions and types
configuration_params = [
{"name": "mainDatabaseName",
	"default": 'PBDATAphysbiblio.db',
	"description": 'Name of the database file',
	"special": None},
{"name": "loggingLevel",
	"default": 1,
	"description": 'How many messages to save in the log file (will have effects only after closing the application)',
	"special": 'int'},
{"name": "logFileName",
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

loggingLevels = [
	"0 - errors",
	"1 - warnings",
	"2 - info",
	"3 - all"
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
		#needed because the main logger will be loaded later!
		logging.basicConfig(format = '[%(module)s.%(funcName)s] %(message)s', level = logging.INFO)
		self.logger = logging.getLogger("physbibliolog")
		self.defaultDirs = AppDirs("PhysBiblio")

		self.configPath = self.defaultDirs.user_config_dir + os.sep
		self.dataPath = self.defaultDirs.user_data_dir + os.sep
		self.logger.info("Default configuration path: %s"%self.configPath)
		if not os.path.exists(self.configPath):
			os.makedirs(self.configPath)
		self.logger.info("Default data path: %s"%self.dataPath)
		if not os.path.exists(self.dataPath):
			os.makedirs(self.dataPath)
		self.configProfilesFile = os.path.join(self.configPath, "profiles.dat")
		self.checkOldProfiles()

		self.needFirstConfiguration = False
		self.paramOrder = config_paramOrder
		self.specialTypes = config_special
		self.defaultsParams = config_defaults
		self.loggingLevels = loggingLevels
		self.params = {}
		for k, v in config_defaults.items():
			if type(v) is str and "PBDATA" in v:
				v = os.path.join(self.dataPath, v.replace("PBDATA", ""))
				config_defaults[k] = v
			self.params[k] = v
		self.descriptions = config_descriptions

		try:
			self.defProf, self.profiles, self.profileOrder = self.readProfiles()
		except (IOError, ValueError, SyntaxError) as e:
			self.logger.warning(e)
			self.createDefaultProfile()

		self.verifyProfiles()

		self.checkOldPaths()
		for k, prof in self.profiles.items():
			self.profiles[k]["f"] = os.path.join(self.configPath, prof["f"])

		self.defaultProfile = self.profiles[self.defProf]
		self.logger.info("starting with configuration in '%s'"%self.defaultProfile["f"])
		self.configMainFile = self.defaultProfile["f"]
		
		self.readConfigFile()

		#some urls
		self.arxivUrl = "http://arxiv.org/"
		self.doiUrl = "http://dx.doi.org/"
		self.inspireRecord = "http://inspirehep.net/record/"
		self.inspireSearchBase = "http://inspirehep.net/search"

	def verifyProfiles(self):
		"""
		Sync the list of profiles with the config folder content
		"""
		changed = False
		files = [ p["f"].split(os.sep)[-1] for p in self.profiles.values()]
		keys = list(self.profiles.keys())
		for p in keys:
			if not os.path.exists(self.profiles[p]["f"]):
				self.logger.warning("The profile configuration file %s does not exist. Removing profile."%self.profiles[p]["f"])
				del self.profiles[p]
				changed = True
		for f in glob.iglob(self.configPath + os.sep + "*.cfg"):
			s = f.split(os.sep)[-1]
			if s not in files:
				self.logger.warning("New profile configuration file %s found. Adding profile."%f)
				new = s.replace(".cfg", "")
				self.profiles[new] = {"f": f, "d":""}
				changed = True
		if len(self.profiles) == 0:
			self.createDefaultProfile()
			changed = True
		if self.defProf not in self.profiles.keys():
			self.logger.warning("Bad default profile name. Using another existing one.")
			self.defProf = list(self.profiles.keys())[0]
		if self.profileOrder == []:
			self.logger.warning("Empty profile order. Using alphabetic order.")
			self.profileOrder = sorted(self.profiles.keys())
			changed = True
		if changed:
			self.logger.warning("The list of profiles has been updated to match the content of the config folder.")
			self.writeProfiles()

	def createDefaultProfile(self):
		"""
		Create the default profile
		"""
		self.profiles = {"default": {"f": os.path.join(self.configPath, "params.cfg"), "d":""}}
		open(self.profiles["default"]["f"], "a").close()
		self.defProf = "default"
		self.profileOrder = []
		self.writeProfiles()

	def readProfiles(self):
		"""
		Reads the list of profiles and the related parameters in the profiles file.
		"""
		with open(self.configProfilesFile) as r:
			txtarr = r.readlines()
		txt = "".join(txtarr)
		parsed = ast.literal_eval(txt.replace("\n",""))
		if len(parsed) < 3:
			parsed = parsed + tuple(sorted(parsed[1].keys()))
		return parsed

	def renameProfile(self, name, fileName):
		"""
		Rename a profile given the name of the config file

		Parameters:
			* name
			* fileName
		"""
		oldName = None
		for k in self.profiles.keys():
			if self.profiles[k]["f"].split(os.sep)[-1] == fileName:
				oldName = k
		self.profiles[name] = dict(self.profiles[oldName])
		del self.profiles[oldName]
		for i, k in enumerate(self.profileOrder):
			if k == oldName:
				self.profileOrder[i] = name
		self.logger.info("Profile renamed: %s -> %s"%(oldName, name))

	def setProfileOrder(self, new, save = True):
		"""
		Update the profile order and save

		Parameters:
			* new: the ordered list of profile names
			* save (boolean, default False): write the new settings in the profiles.dat
		"""
		if self.profileOrder != new:
			self.profileOrder = new
			self.logger.warning("The order of profiles has been updated.")
			if save:
				self.writeProfiles()

	def checkOldProfiles(self):
		"""
		Intended for backwards compatibility.
		Check if there is a profiles.dat file in the 'data/' subfolder.
		If yes, move it to the new self.configPath.
		"""
		if os.path.isfile(os.path.join("data", "profiles.dat")):
			self.logger.info("Moving profiles.dat from old to new location")
			os.rename(os.path.join("data", "profiles.dat"), self.configProfilesFile)

	def checkOldPaths(self):
		"""
		Intended for backwards compatibility.
		Check if there are configuration files in the 'data/' subfolder.
		If yes, move them to the new self.configPath or self.dataPath.
		"""
		save = False
		for k, prof in self.profiles.items():
			if "data/" in prof["f"]:
				if os.path.isfile(prof["f"]):
					new = os.path.join(self.configPath, self.profiles[k]["f"].replace("data/", ""))
					self.logger.info("Moving file %s to %s"%(prof["f"], new))
					os.rename(prof["f"], new)
				self.profiles[k]["f"] = prof["f"].replace("data/", "")
				save = True
		if save:
			self.writeProfiles()

	def writeProfiles(self):
		"""
		Writes the list of profiles and the related parameters in the profiles file.
		"""
		if not os.path.exists(self.configPath):
			os.makedirs(self.configPath)
		with open(self.configProfilesFile, 'w') as w:
			w.write("'%s',\n%s,\n%s\n"%(self.defProf, self.profiles, self.profileOrder))

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
		self.logger.info("Starting with configuration in '%s'"%self.defaultProfile["f"])
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
					self.logger.warning("Failed in reading parameter", exc_info = True)
					self.params[k] = v
		except IOError:
			self.logger.warning("ERROR: config file %s do not exist. Creating it..."%self.configMainFile)
			self.saveConfigFile()
			self.needFirstConfiguration = True
		except Exception:
			self.logger.error("ERROR: reading %s file failed."%self.configMainFile)
		
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
			self.logger.error("ERROR in saving config file!")

pbConfig = ConfigVars()
