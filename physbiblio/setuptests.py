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

try:
	from physbiblio.config import pbConfig
	from physbiblio.errors import pBErrorManager, pBLogger
	from physbiblio.database import physbiblioDB
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
	print(traceback.format_exc())
	raise

today_ymd = datetime.datetime.today().strftime('%y%m%d')

skipOnlineTests = False
skipOAITests    = False
skipLongTests   = False
skipDBTests     = False

pbConfig.params["logFileName"] = "tests_%s.log"%today_ymd
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
