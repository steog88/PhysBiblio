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
	from physbiblio.errors import pBErrorManager
	from physbiblio.config import pbConfig
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

class TestBuilding(unittest.TestCase):
	"""Test pBErrorManager outputs"""
	@patch('sys.stdout', new_callable=StringIO)
	def assert_notraceback(self, message, priority, expected_output, mock_stdout):
		"""Test print to stdout without traceback"""
		try:
			raise Exception(message)
		except Exception as e:
			pBErrorManager(str(e), priority = priority)
		self.assertEqual(mock_stdout.getvalue(), expected_output)

	@patch('sys.stdout', new_callable=StringIO)
	def assert_withtraceback(self, message, priority, expected_output, mock_stdout):
		"""Test print to stdout with traceback"""
		try:
			raise Exception(message)
		except Exception as e:
			pBErrorManager(str(e), traceback, priority = priority)
		self.assertEqual(mock_stdout.getvalue(), expected_output + traceback.format_exc() + "\n")

	@patch('sys.stderr', new_callable=StringIO)
	def assert_stderr(self, message, priority, expected_output, mock_stdout):
		"""Test print to stderr without traceback"""
		try:
			raise Exception(message)
		except Exception as e:
			pBErrorManager(str(e), priority = priority)
		self.assertEqual(mock_stdout.getvalue(), expected_output)

	@patch('sys.stderr', new_callable=StringIO)
	def assert_fullstderr(self, message, priority, expected_output, mock_stdout):
		"""Test print to stderr with traceback"""
		try:
			raise Exception(message)
		except Exception as e:
			pBErrorManager(str(e), traceback, priority = priority)
		self.assertEqual(mock_stdout.getvalue(), expected_output + traceback.format_exc())

	def test_errors(self):
		"""Test pBErrorManager with different input combinations"""
		try:
			with open(logFileName) as logFile:
				log_old = logFile.read()
		except IOError:
			log_old = ""
		self.assert_notraceback("test warning", 0, "test warning\n\n")
		self.assert_notraceback("test error", 1, "**Error**\ntest error\n\n")
		with open(logFileName) as logFile:
			log_new = logFile.read()
		self.assertEqual(log_new, log_old + "test warning\n" + "**Error**\ntest error\n")
		self.assert_notraceback("test critical", 2, "****Critical error****\ntest critical\n\n")
		self.assert_withtraceback("test warning", 0, "test warning\n\n")
		self.assert_stderr("test warning", 0, "test warning\n")
		self.assert_fullstderr("test warning", 0, "test warning\n")

if __name__=='__main__':
	print("\nStarting tests...\n")
	unittest.main()
