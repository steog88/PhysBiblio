"""
Utilities for in the tests of the physbiblio modules.

This file is part of the PhysBiblio package.
"""
import sys, traceback, datetime, os

if sys.version_info[0] < 3:
	import unittest2 as unittest
else:
	import unittest

try:
	from physbiblio.config import pbConfig
	from physbiblio.database import physbiblioDB
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise

today_ymd = datetime.datetime.today().strftime('%y%m%d')

skipOnlineTests = False
skipOAITests    = False
skipLongTests   = False
skipDBTests     = False

pbConfig.params["logFileName"] = "tests_%s.log"%today_ymd
logFileName = os.path.join(pbConfig.path, pbConfig.params["logFileName"])

tempDBName = os.path.join(pbConfig.path, "tests_%s.db"%today_ymd)
if os.path.exists(tempDBName):
	os.remove(tempDBName)

class DBTestCase(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		self.pBDB = physbiblioDB(tempDBName)

	def tearDown(self):
		self.pBDB.undo(verbose = False)
