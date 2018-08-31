"""
Utilities for in the tests of the physbiblio modules.

This file is part of the physbiblio package.
"""
import sys, traceback, datetime, os

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch
	from StringIO import StringIO
else:
	import unittest
	from unittest.mock import patch
	from io import StringIO

today_ymd = datetime.datetime.today().strftime('%y%m%d')
tempLogFileName = "tests_%s.log"%today_ymd

try:
	from physbiblio.config import pbConfig
	pbConfig.overWritelogFileName = os.path.join(
		pbConfig.dataPath, tempLogFileName)
	pbConfig.prepareLogger("physbibliotestlog")
	pbConfig.reloadProfiles()
	from physbiblio.errors import pBErrorManager, pBLogger
	from physbiblio.database import physbiblioDB
except ImportError:
	print("Could not find physbiblio and its modules!")
	print(traceback.format_exc())
	raise

class skipTestsSettingsClass():
	"""Store settings for deciding the tests to skip"""
	def __init__(self):
		"""Define non-gui skip settings"""
		self.default()

	def copy(self):
		"""create a new instance, copy of the previous one"""
		new = skipTestsSettingsClass()
		new.db = bool(self.db)
		new.gui = bool(self.gui)
		new.long = bool(self.long)
		new.oai = bool(self.oai)
		new.online = bool(self.online)
		return new

	def default(self):
		"""Default settings"""
		self.db = False
		self.gui = False
		self.long = False
		self.oai = False
		self.online = False

	def __str__(self):
		"""print current settings"""
		return "DB: %s\nGUI: %s\nlong: %s\nOnline: %s (OAI: %s)"%(
			self.db, self.gui, self.long, self.online, self.oai)

skipTestsSettings = skipTestsSettingsClass()

pbConfig.params["logFileName"] = tempLogFileName
logFileName = os.path.join(pbConfig.dataPath, pbConfig.params["logFileName"])

tempDBName = os.path.join(pbConfig.dataPath, "tests_%s.db"%today_ymd)
if os.path.exists(tempDBName):
	os.remove(tempDBName)

class DBTestCase(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		self.maxDiff = None
		self.pBDB = physbiblioDB(tempDBName, pBLogger)

	def tearDown(self):
		self.pBDB.undo(verbose = False)

	@patch('sys.stdout', new_callable=StringIO)
	def assert_stdout(self, function, expected_output, mock_stdout):
		"""Catch and test stdout of the function"""
		pBErrorManager.tempHandler(sys.stdout, format = '%(message)s')
		function()
		pBErrorManager.rmTempHandler()
		self.assertEqual(mock_stdout.getvalue(), expected_output)

	@patch('sys.stdout', new_callable=StringIO)
	def assert_in_stdout(self, function, expected_output, mock_stdout):
		"""Catch and if test stdout of the function contains a string"""
		pBErrorManager.tempHandler(sys.stdout, format = '%(message)s')
		function()
		pBErrorManager.rmTempHandler()
		self.assertIn(expected_output, mock_stdout.getvalue())

def tearDownModule():
	if os.path.exists(logFileName):
		os.remove(logFileName)
