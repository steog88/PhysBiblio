import sys

config_defaults = {
	"configMainFile":   'data/params.cfg',
	"timeoutWebSearch": 10.,
	"mainDatabaseName": 'data/pybiblio.db',
	"pdfFolder":        'data/pdf/',
	"pdfApplication":   'okular',
}
		
class ConfigVars():
	def __init__(self):
		self.params = config_defaults
		self.configMainFile = self.params["configMainFile"]
		if len(sys.argv) > 1:
			self.configMainFile = sys.argv[1]
		
		self.readConfigFile()
	
	def readConfigFile(self):
		try:
			with open(self.configMainFile) as r:
				txt = r.readlines()
			for l in txt:
				k, v = l.replace("\n", "").split(" = ")
				self.params[k] = v
		except IOError:
			print("[config] ERROR: config file %s do not exist. Creating it..."%self.configMainFile)
			self.saveConfigFile()
		except:
			print("[config] ERROR: reading %s file failed."%self.configMainFile)
		
	def saveConfigFile(self):
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
