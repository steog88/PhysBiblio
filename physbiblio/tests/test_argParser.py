#!/usr/bin/env python
"""Test file for the physbiblio.argParser module.

This file is part of the physbiblio package.
"""
import sys
import traceback

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
	print("Could not find physbiblio and its modules!")
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
				['usage: PhysBiblio.exe [-h] [-p ',
				'{clean,cli,daily,dates,export,test,tex,update,weekly,gui}'])
		for opt in ["-p", "--profile"]:
			profile = list(pbConfig.profiles.keys())[0]
			with patch("physbiblio.cli.cli") as mock:
				self.assert_in_stdout(lambda: parser.parse_args(
					[opt, "%s"%profile, "cli"]),
					["Starting with profile '%s', database"%profile])
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
			["clean", "physbiblio.database.Entries.cleanBibtexs", [],
				([], {"startFrom": 0})],
			["clean", "physbiblio.database.Entries.cleanBibtexs",
				["-s", "100"], ([], {"startFrom": 100})],
			["clean", "physbiblio.database.Entries.cleanBibtexs",
				["--startFrom", "1000"], ([], {"startFrom": 1000})],
			["cli", "physbiblio.cli.cli", [], ([], {})],
			["daily", "physbiblio.database.Entries.getDailyInfoFromOAI", [],
				([(datetime.date.today() - \
					datetime.timedelta(1)).strftime("%Y-%m-%d"),
				datetime.date.today().strftime("%Y-%m-%d")], {})],
			["dates", "physbiblio.database.Entries.getDailyInfoFromOAI",
				["2018-04-01", "2018-05-01"],
				(["2018-04-01", "2018-05-01"], {})],
			["export", "physbiblio.export.PBExport.exportAll", ["testname"],
				(["testname"], {})],
			["tex", "physbiblio.export.PBExport.exportForTexFile", ["f1", "f2"],
				([["f2"], "f1"], {"autosave": True, "overwrite": False,
					"removeUnused": False, "updateExisting": False})],
			["tex", "physbiblio.export.PBExport.exportForTexFile",
				["f1", "f2", "-o"],
				([["f2"], "f1"], {"autosave": True, "overwrite": True,
					"removeUnused": False, "updateExisting": False})],
			["tex", "physbiblio.export.PBExport.exportForTexFile",
				["f1", "f2", "--overwrite"], ([["f2"], "f1"],
				{"autosave": True, "overwrite": True,
				"removeUnused": False, "updateExisting": False})],
			["tex", "physbiblio.export.PBExport.exportForTexFile",
				["f1", "f2", "--ov"], ([["f2"], "f1"],
				{"autosave": True, "overwrite": True, "removeUnused": False,
				"updateExisting": False})],
			["tex", "physbiblio.export.PBExport.exportForTexFile",
				["f1", "f2", "-s"], ([["f2"], "f1"],
					{"autosave": False, "overwrite": False,
					"removeUnused": False, "updateExisting": False})],
			["tex", "physbiblio.export.PBExport.exportForTexFile",
				["f1", "f2", "--save"], ([["f2"], "f1"],
				{"autosave": False, "overwrite": False, "removeUnused": False,
				"updateExisting": False})],
			["tex", "physbiblio.export.PBExport.exportForTexFile",
				["f1", "f2", "--sa"], ([["f2"], "f1"],
				{"autosave": False, "overwrite": False, "removeUnused": False,
				"updateExisting": False})],
			["tex", "physbiblio.export.PBExport.exportForTexFile",
				["f1", "f2", "f3", "--sa"], ([["f2", "f3"], "f1"],
				{"autosave": False, "overwrite": False, "removeUnused": False,
				"updateExisting": False})],
			["tex", "physbiblio.export.PBExport.exportForTexFile",
				["f1", "f2", "-u"], ([["f2"], "f1"],
				{"autosave": True, "overwrite": False, "removeUnused": False,
				"updateExisting": True})],
			["tex", "physbiblio.export.PBExport.exportForTexFile",
				["f1", "f2", "--updateExisting"], ([["f2"], "f1"],
				{"autosave": True, "overwrite": False, "removeUnused": False,
				"updateExisting": True})],
			["tex", "physbiblio.export.PBExport.exportForTexFile",
				["f1", "f2", "-r"], ([["f2"], "f1"],
				{"autosave": True, "overwrite": False, "removeUnused": True,
				"updateExisting": False})],
			["tex", "physbiblio.export.PBExport.exportForTexFile",
				["f1", "f2", "--removeUnused"], ([["f2"], "f1"],
				{"autosave": True, "overwrite": False, "removeUnused": True,
				"updateExisting": False})],
			["update", "physbiblio.database.Entries.searchOAIUpdates", [],
				([], {"startFrom": 0, "force": False})],
			["update", "physbiblio.database.Entries.searchOAIUpdates", ["-f"],
				([], {"startFrom": 0, "force": True})],
			["update", "physbiblio.database.Entries.searchOAIUpdates",
				["--force"], ([], {"startFrom": 0, "force": True})],
			["update", "physbiblio.database.Entries.searchOAIUpdates",
				["-s", "100"], ([], {"startFrom": 100, "force": False})],
			["update", "physbiblio.database.Entries.searchOAIUpdates",
				["--startFrom", "100"],
				([], {"startFrom": 100, "force": False})],
			["weekly", "physbiblio.database.Entries.getDailyInfoFromOAI", [],
				([(datetime.date.today() - datetime.timedelta(7)
				).strftime("%Y-%m-%d"),
				datetime.date.today().strftime("%Y-%m-%d")], {})],
		]
		with patch("physbiblio.database.PhysBiblioDB.commit") as _comm_mock:
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
			["tex", ["f1", "f2", "--overWrite"]],
			["tex", ["f1", "f2", "-save"]],
			["update", ["-o"]],
			["update", ["-s", "abc"]],
			["update", ["--startFrom"]],
			["weekly", ["any"]],
		]
		with patch("physbiblio.database.PhysBiblioDB.commit") as _comm_mock:
			for sub, options in tests:
				with self.assertRaises(SystemExit):
					args = parser.parse_args([sub] + options)

	def test_subcommand_tests(self):
		"""Test that the options are recognised correctly"""
		from physbiblio.setuptests import skipTestsSettings
		if sys.version_info[0] < 3:
			patchString = "unittest2.runner.TextTestRunner.run"
		else:
			patchString = "unittest.runner.TextTestRunner.run"
		oldSettings = skipTestsSettings.copy()
		parser = setParser()
		tests = [
			[["test"], False, False, False, False, False],
			[["test", "-d"], True, False, False, False, False],
			[["test", "--database"], True, False, False, False, False],
			[["test", "-g"], False, True, False, False, False],
			[["test", "--gui"], False, True, False, False, False],
			[["test", "-l"], False, False, True, False, False],
			[["test", "--long"], False, False, True, False, False],
			[["test", "-o"], False, False, False, True, True],
			[["test", "--online"], False, False, False, True, True],
			[["test", "--online_oai"], False, False, False, True, False],
			[["test", "-d", "--online"], True, False, False, True, True],
		]
		for options, _db, _gui, _lon, _oai, _onl in tests:
			skipTestsSettings.default()
			with patch(patchString) as _run:
				args = parser.parse_args(options)
				call_tests(args)
				self.assertEqual(skipTestsSettings.db, _db)
				self.assertEqual(skipTestsSettings.gui, _gui)
				self.assertEqual(skipTestsSettings.long, _lon)
				self.assertEqual(skipTestsSettings.oai, _oai)
				self.assertEqual(skipTestsSettings.online, _onl)
				self.assertEqual(_run.call_count, 1)
		with self.assertRaises(SystemExit):
			args = parser.parse_args(["test", "-a"])
		skipTestsSettings = oldSettings

if __name__=='__main__':
	unittest.main()
