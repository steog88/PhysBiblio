#!/usr/bin/env python
"""
Test file for the physbiblio.argParser module.

This file is part of the physbiblio package.
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
	from physbiblio import __version__, __version_date__
	from physbiblio.setuptests import *
	from physbiblio.argParser import *
	from physbiblio.config import pbConfig
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

class TestParser(unittest.TestCase):
	"""Tests for main parser and stuff"""
	@patch('sys.stdout', new_callable=StringIO)
	def assert_in_stdout(self, function, expected_output, mock_stdout):
		"""Catch and if test stdout of the function contains a string"""
		pBErrorManager.tempHandler(sys.stdout, format = '%(message)s')
		function()
		pBErrorManager.rmTempHandler()
		string = mock_stdout.getvalue()
		for text in expected_output:
			self.assertIn(text, string)

	@patch('sys.stdout', new_callable=StringIO)
	def assert_in_stdout_sysexit(self, function, expected_output, mock_stdout):
		"""Catch and if test stdout of the function contains a string"""
		with self.assertRaises(SystemExit):
			function()
		string = mock_stdout.getvalue()
		for text in expected_output:
			self.assertIn(text, string)

	@patch('sys.stderr', new_callable=StringIO)
	def assert_in_stderr_sysexit(self, function, expected_output, mock_stderr):
		"""Catch and if test stderr of the function contains a string"""
		with self.assertRaises(SystemExit):
			function()
		string = mock_stderr.getvalue()
		for text in expected_output:
			self.assertIn(text, string)

	def test_global(self):
		"""Test that the options are recognised correctly"""
		parser = setParser()
		for opt in ["-v", "--version"]:
			with self.assertRaises(SystemExit):
				parser.parse_args([opt])
			if sys.version_info[0] < 3:
				self.assert_in_stderr_sysexit(lambda: parser.parse_args([opt]),
					['PhysBiblio %s (%s)'%(__version__, __version_date__)])
			else:
				self.assert_in_stdout_sysexit(lambda: parser.parse_args([opt]),
					['PhysBiblio %s (%s)'%(__version__, __version_date__)])
		for opt in ["-h", "--help"]:
			with self.assertRaises(SystemExit):
				parser.parse_args([opt])
			self.assert_in_stdout_sysexit(lambda: parser.parse_args([opt]),
				['usage: PhysBiblio [-h] [-p ',
				'{clean,cli,daily,dates,export,test,tex,update,weekly,gui}'])
		for opt in ["-p", "--profile"]:
			profile = list(pbConfig.profiles.keys())[0]
			with patch("physbiblio.cli.cli") as mock:
				self.assert_in_stdout(lambda: parser.parse_args([opt, "%s"%profile, "cli"]),
					["Changing profile to '%s'"%profile,
					"Closing database...",
					"Opening database:"])
				args = parser.parse_args([opt, "%s"%profile, "cli"])
				args.func(args)
				mock.assert_called_once_with()

	def test_subcommands_ok(self):
		"""Test that the options are recognised correctly"""
		parser = setParser()
		tests = [
			["gui", call_gui],
			["test", call_tests],
		]
		for sub, func in tests:
			args = parser.parse_args([sub])
			self.assertIs(args.func, func)
		tests = [
			["clean", "physbiblio.database.entries.cleanBibtexs", [], ([], {"startFrom": 0})],
			["clean", "physbiblio.database.entries.cleanBibtexs", ["-s", "100"], ([], {"startFrom": 100})],
			["clean", "physbiblio.database.entries.cleanBibtexs", ["--startFrom", "1000"], ([], {"startFrom": 1000})],
			["cli", "physbiblio.cli.cli", [], ([], {})],
			["daily", "physbiblio.database.entries.getDailyInfoFromOAI", [],
				([(datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d"), datetime.date.today().strftime("%Y-%m-%d")], {})],
			["dates", "physbiblio.database.entries.getDailyInfoFromOAI", ["2018-04-01", "2018-05-01"],
				(["2018-04-01", "2018-05-01"], {})],
			["export", "physbiblio.export.pbExport.exportAll", ["testname"], (["testname"], {})],
			["tex", "physbiblio.export.pbExport.exportForTexFile", ["f1", "f2"], (["f1", "f2"], {"autosave": True, "overwrite": False})],
			["tex", "physbiblio.export.pbExport.exportForTexFile", ["f1", "f2", "-o"], (["f1", "f2"], {"autosave": True, "overwrite": True})],
			["tex", "physbiblio.export.pbExport.exportForTexFile", ["f1", "f2", "--overwrite"], (["f1", "f2"], {"autosave": True, "overwrite": True})],
			["tex", "physbiblio.export.pbExport.exportForTexFile", ["f1", "f2", "--ov"], (["f1", "f2"], {"autosave": True, "overwrite": True})],
			["tex", "physbiblio.export.pbExport.exportForTexFile", ["f1", "f2", "-s"], (["f1", "f2"], {"autosave": False, "overwrite": False})],
			["tex", "physbiblio.export.pbExport.exportForTexFile", ["f1", "f2", "--save"], (["f1", "f2"], {"autosave": False, "overwrite": False})],
			["tex", "physbiblio.export.pbExport.exportForTexFile", ["f1", "f2", "--sa"], (["f1", "f2"], {"autosave": False, "overwrite": False})],
			["update", "physbiblio.database.entries.searchOAIUpdates", [], ([], {"startFrom": 0, "force": False})],
			["update", "physbiblio.database.entries.searchOAIUpdates", ["-f"], ([], {"startFrom": 0, "force": True})],
			["update", "physbiblio.database.entries.searchOAIUpdates", ["--force"], ([], {"startFrom": 0, "force": True})],
			["update", "physbiblio.database.entries.searchOAIUpdates", ["-s", "100"], ([], {"startFrom": 100, "force": False})],
			["update", "physbiblio.database.entries.searchOAIUpdates", ["--startFrom", "100"], ([], {"startFrom": 100, "force": False})],
			["weekly", "physbiblio.database.entries.getDailyInfoFromOAI", [],
				([(datetime.date.today() - datetime.timedelta(7)).strftime("%Y-%m-%d"), datetime.date.today().strftime("%Y-%m-%d")], {})],
		]
		with patch("physbiblio.database.physbiblioDB.commit") as _comm_mock:
			for sub, func, options, expected in tests:
				with patch(func) as mock:
					args = parser.parse_args([sub] + options)
					args.func(args)
					mock.assert_called_once_with(*expected[0], **expected[1])

	def test_subcommands_fail(self):
		"""Test that the options are recognised correctly."""
		parser = setParser()
		tests = [
			["clean", ["-f"]],
			["clean", ["-s"]],
			["clean", ["-s", "abc"]],
			["clean", ["--startfrom", "1000"]],
			["cli", ["-t"]],
			["daily", ["date"]],
			["dates", ["date1"]],
			["export", ["testname1", "testname2"]],
			["gui", ["-p"]],
			["test", ["-f"]],
			["tex", ["f1"]],
			["tex", ["f1", "f2", "f3"]],
			["tex", ["f1", "f2", "--overWrite"]],
			["tex", ["f1", "f2", "-save"]],
			["update", ["-o"]],
			["update", ["-s", "abc"]],
			["update", ["--startFrom"]],
			["weekly", ["any"]],
		]
		with patch("physbiblio.database.physbiblioDB.commit") as _comm_mock:
			for sub, options in tests:
				with self.assertRaises(SystemExit):
					args = parser.parse_args([sub] + options)		

if __name__=='__main__':
	unittest.main()
