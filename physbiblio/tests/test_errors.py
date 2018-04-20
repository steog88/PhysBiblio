#!/usr/bin/env python
"""
Test file for the physbiblio.errors module.

This file is part of the PhysBiblio package.
"""
import sys, traceback

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch
	from StringIO import StringIO
else:
	import unittest
	from unittest.mock import patch
	from io import StringIO

try:
	from physbiblio.setuptests import *
	from physbiblio.errors import pBErrorManagerClass
	from physbiblio.config import pbConfig
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

class TestBuilding(unittest.TestCase):
	"""Test pBErrorManager outputs"""
	@classmethod
	def setUpClass(self):
		"""settings"""
		pbConfig.params["loggingLevel"] = 3
		pbConfig.params["logFileName"] = logFileName
		self.pBErrorManager = pBErrorManagerClass()

	@patch('logging.Logger.log')
	def assert_notraceback(self, message, priority, mock_log):
		"""Test print to stderr with traceback"""
		try:
			raise Exception(message)
		except Exception as e:
			self.pBErrorManager(str(e), priority = priority)
		mock_log.assert_called_once_with((2+priority)*10, message)

	@patch('logging.Logger.log')
	def assert_withtraceback(self, message, priority, mock_log):
		"""Test print to stderr with traceback"""
		try:
			raise Exception(message)
		except Exception as e:
			tracebackText = traceback.format_exc()
			self.pBErrorManager(str(e), trcbk = traceback, priority = priority)
		mock_log.assert_called_once_with((2+priority)*10, message + "\n" + tracebackText)

	def test_errors(self):
		"""Test pBErrorManager with different input combinations"""
		open(logFileName, 'w').close()
		self.assert_notraceback("test warning", 0)
		self.assert_notraceback("test error", 1)
		try:
			raise Exception(message)
		except Exception as e:
			self.pBErrorManager(str(e), priority = 2)
		with open(logFileName) as logFile:
			log_new = logFile.read()
		self.assertIn(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), log_new)
		self.assertTrue("      ERROR : [errors.__call__] global name 'message' is not defined" in log_new
			or "      ERROR : [errors.__call__] name 'message' is not defined" in log_new)

	def test_logger_stuff(self):
		"""Test some stuff related to the logger"""
		self.assertFalse("NYI")
		#test traceback inclusion and levels in logfile

	def test_tempHandler(self):
		"""Test stuff as the temporary handler"""
		self.assertFalse("NYI")
		#test additional handler using a StringIO
