#!/usr/bin/env python
"""Test file for the physbiblio.config module.

This file is part of the physbiblio package.
"""
import sys
import traceback
import os

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch
else:
	import unittest
	from unittest.mock import patch

try:
	from physbiblio.setuptests import *
	from physbiblio.databaseCore import PhysBiblioDBCore
	from physbiblio.config import \
		pbConfig, ConfigVars, config_defaults, ConfigurationDB, GlobalDB
except ImportError:
	print("Could not find physbiblio and its modules!")
	raise
except Exception:
	print(traceback.format_exc())

tempOldCfgName = os.path.join(pbConfig.dataPath, "tests_%s.cfg"%today_ymd)
tempCfgName = os.path.join(pbConfig.dataPath, "tests_cfg_%s.db"%today_ymd)
tempCfgName1 = os.path.join(pbConfig.dataPath, "tests_cfg1_%s.db"%today_ymd)
tempProfName = os.path.join(pbConfig.dataPath, "tests_prof_%s.db"%today_ymd)

class TestConfigMethods(unittest.TestCase):
	"""Tests for methods in physbiblio.config"""

	@patch('sys.stdout', new_callable=StringIO)
	def assert_in_stdout_multi(self, function, expected_output, mock_stdout):
		"""Catch and if test stdout of the function contains a string"""
		pBErrorManager.tempHandler(sys.stdout, format='%(message)s')
		function()
		pBErrorManager.rmTempHandler()
		for e in expected_output:
			self.assertIn(e, mock_stdout.getvalue())

	def test_config(self):
		"""Test config methods for config management"""
		if os.path.exists(tempCfgName):
			os.remove(tempCfgName)
		newConfParamsDict = dict(config_defaults)
		with patch("physbiblio.config.ConfigVars.readProfiles",
				return_value=("tmp", {"tmp": {"db": tempCfgName, "d":""}},
				["tmp"])) as _mock_readprof:
			self.assertFalse(os.path.exists(tempCfgName))
			tempPbConfig = ConfigVars()
			tempPbConfig.prepareLogger("physbibliotestlog")
			tempDb = PhysBiblioDBCore(tempCfgName,
				tempPbConfig.logger, info=False)
			configDb = ConfigurationDB(tempDb)

			self.assertTrue(os.path.exists(tempCfgName))
			_mock_readprof.assert_called_once_with()
			self.assertEqual(len(configDb.getAll()), 0)

			tempPbConfig1 = ConfigVars()
			tempPbConfig1.prepareLogger("physbibliotestlog")
			self.assertEqual(tempPbConfig1.params, newConfParamsDict)
			tempPbConfig1.params["logFileName"] = "otherfilename"
			tempPbConfig1.params["timeoutWebSearch"] = 10.
			tempPbConfig1.params["askBeforeExit"] = True
			tempPbConfig1.params["maxAuthorNames"] = 5
			tempPbConfig1.params["defaultCategories"] = [1]
			with open(tempOldCfgName, "w") as f:
				f.write("logFileName = otherfilename\n"
					+ "timeoutWebSearch = 10.0\n"
					+ "askBeforeExit = True\n"
					+ "maxAuthorNames = 5\n"
					+ "defaultCategories = [1]\n")
			tempPbConfig = ConfigVars()
			tempPbConfig.prepareLogger("physbibliotestlog")
			tempPbConfig.configMainFile = tempOldCfgName
			tempPbConfig.oldReadConfigFile()
			self.assertEqual(tempPbConfig.params, tempPbConfig1.params)
		os.remove(tempCfgName)
		os.remove(tempOldCfgName)

	def test_profiles(self):
		"""Test config methods for profiles management"""
		if os.path.exists(tempProfName):
			os.remove(tempProfName)
		tempPbConfig = ConfigVars(tempProfName)
		tempPbConfig.prepareLogger("physbibliotestlog")
		tempPbConfig.reloadProfiles()
		self.assertEqual(tempPbConfig.defaultProfileName, "default")
		self.assertEqual(tempPbConfig.profiles,
			{u"default": {
				"d": u"",
				"f": u"",
				"n": u"default",
				"db": str(os.path.join(pbConfig.dataPath,
				config_defaults["mainDatabaseName"].replace("PBDATA", "")))}})
		self.assertEqual(tempPbConfig.profileOrder, ["default"])

		tempProfName1 = os.path.join(pbConfig.dataPath,
			"tests_prof1_%s.db"%today_ymd)
		self.assertTrue(tempPbConfig.globalDb.createProfile("temp",
			"none", tempProfName1))
		self.assertTrue(tempPbConfig.globalDb.setDefaultProfile("temp"))
		self.assertEqual(tempPbConfig.defaultProfileName, "default")
		self.assertEqual([e["n"] for e in tempPbConfig.profiles.values()],
			["default"])
		self.assertEqual(tempPbConfig.profileOrder, ["default"])
		self.assertEqual(tempPbConfig.currentProfileName, "default")
		self.assertEqual(tempPbConfig.currentDatabase,
			str(os.path.join(pbConfig.dataPath,
			config_defaults["mainDatabaseName"].replace("PBDATA", ""))))
		tempParams = tempPbConfig.params

		default, profiles, ordered = tempPbConfig.readProfiles()
		self.assertEqual(default, "temp")
		self.assertEqual(profiles,
			{u"default": {
				"d": u"",
				"f": u"",
				"n": u"default",
				"db": str(os.path.join(pbConfig.dataPath,
				config_defaults["mainDatabaseName"].replace("PBDATA", "")))},
			u"temp": {
				"d": u"none",
				"f": u"",
				"n": u"temp",
				"db": tempProfName1}})
		self.assertEqual(ordered, ["default", "temp"])
		tempPbConfig.reloadProfiles()
		self.assertEqual(tempPbConfig.params, config_defaults)

		tempProfName2 = tempProfName1.replace("prof1", "prof2")
		self.assertTrue(tempPbConfig.globalDb.createProfile("other",
			"none1", tempProfName2))
		tempPbConfig.reloadProfiles()
		self.assertEqual(tempPbConfig.defaultProfileName, "temp")
		self.assertEqual(sorted(
			[e["n"] for e in tempPbConfig.profiles.values()]),
			["default", "other", "temp"])
		self.assertEqual(tempPbConfig.profileOrder,
			["default", "other", "temp"])
		self.assertEqual(tempPbConfig.currentProfileName, "temp")
		self.assertEqual(tempPbConfig.currentProfile,
			tempPbConfig.profiles["temp"])
		self.assertEqual(tempPbConfig.currentDatabase, tempProfName1)

		tempPbConfig.reInit("other")
		self.assertEqual(tempPbConfig.defaultProfileName, "temp")
		self.assertEqual(sorted(
			[e["n"] for e in tempPbConfig.profiles.values()]),
			["default", "other", "temp"])
		self.assertEqual(tempPbConfig.profileOrder,
			["default", "other", "temp"])
		self.assertEqual(tempPbConfig.currentProfileName, "other")
		self.assertEqual(tempPbConfig.currentProfile,
			tempPbConfig.profiles["other"])
		self.assertEqual(tempPbConfig.currentDatabase, tempProfName2)

		tempPbConfig.reInit("other", tempPbConfig.profiles["temp"])
		self.assertEqual(tempPbConfig.currentProfileName, "other")
		self.assertEqual(tempPbConfig.currentProfile,
			tempPbConfig.profiles["temp"])
		self.assertEqual(tempPbConfig.currentDatabase, tempProfName1)

		tempPbConfig.reInit("temp", tempPbConfig.profiles["temp"])
		self.assertEqual(tempPbConfig.currentProfileName, "temp")
		self.assertEqual(tempPbConfig.currentProfile,
			tempPbConfig.profiles["temp"])
		self.assertEqual(tempPbConfig.currentDatabase, tempProfName1)

		tempPbConfig.reInit("nonexistent")
		self.assertEqual(tempPbConfig.currentProfileName, "temp")
		self.assertEqual(tempPbConfig.currentProfile,
			tempPbConfig.profiles["temp"])
		self.assertEqual(tempPbConfig.currentDatabase, tempProfName1)
		self.assertEqual(tempPbConfig.params, tempParams)

		tempDb = PhysBiblioDBCore(tempProfName1,
			tempPbConfig.logger, info=False)
		configDb = ConfigurationDB(tempDb)
		configDb.insert("defaultCategories", "[0")
		configDb.commit()

		tempPbConfig.readConfig()
		self.assertEqual(tempPbConfig.params, tempParams)
		self.assert_in_stdout_multi(tempPbConfig.readConfig,
			["Failed in reading parameter 'defaultCategories'."])

		configDb.insert("loggingLevel", "4")
		configDb.insert("pdfFolder", "/nonexistent/")
		configDb.insert("askBeforeExit", "True")
		configDb.insert("timeoutWebSearch", "20.")
		configDb.commit()
		tempParams["loggingLevel"] = 4
		tempParams["pdfFolder"] = u"/nonexistent/"
		tempParams["askBeforeExit"] = True
		tempParams["timeoutWebSearch"] = 20.
		tempPbConfig.readConfig()
		self.assertEqual(tempPbConfig.params, tempParams)
		self.assert_in_stdout_multi(tempPbConfig.readConfig,
			["Failed in reading parameter 'defaultCategories'."])

		configDb.insert("defaultCategories", "[0]")
		configDb.commit()
		tempParams["defaultCategories"] = [0]
		tempPbConfig.readConfig()
		self.assertEqual(tempPbConfig.params, tempParams)

		tempDb.closeDB(info=False)
		if os.path.exists(tempProfName1):
			os.remove(tempProfName1)
		if os.path.exists(tempProfName2):
			os.remove(tempProfName2)

	def test_searches(self):
		"""Test config methods for profiles management"""
		if os.path.exists(tempProfName):
			os.remove(tempProfName)
		tempPbConfig = ConfigVars(tempProfName)
		self.assertEqual(tempPbConfig.globalDb.countSearches(), 0)

		self.assertTrue(tempPbConfig.globalDb.insertSearch(
			"testname", 123, {"field": "value"},
			["a", "b", "c", "d", "e"], True, True, 21, 321))
		self.assertEqual(tempPbConfig.globalDb.countSearches(), 1)
		search = tempPbConfig.globalDb.getSearchByID(1)[0]
		self.assertEqual(search["name"], "testname")
		self.assertEqual(search["count"], 123)
		self.assertEqual(search["manual"], 1)
		self.assertEqual(search["isReplace"], 1)
		self.assertEqual(search["limitNum"], 21)
		self.assertEqual(search["offsetNum"], 321)
		self.assertEqual(search["searchDict"], "{'field': 'value'}")
		self.assertEqual(search["replaceFIelds"], "['a', 'b', 'c', 'd', 'e']")
		searchN = tempPbConfig.globalDb.getSearchByName("testname")[0]
		self.assertEqual(search, searchN)

		self.assertTrue(tempPbConfig.globalDb.insertSearch(
			"test1", 2, {}, [], True, False))
		self.assertTrue(tempPbConfig.globalDb.insertSearch(
			"test2", 1, {}, [], True, True))
		self.assertTrue(tempPbConfig.globalDb.insertSearch(
			"test3", 3, {}, [], False, True))
		self.assertTrue(tempPbConfig.globalDb.insertSearch(
			"test4", 0, {}, [], False, True))
		self.assertTrue(tempPbConfig.globalDb.insertSearch(
			"test5", 122, {}, [], False, True))
		self.assertEqual(tempPbConfig.globalDb.countSearches(), 6)
		self.assertEqual(
			[e["name"] for e in tempPbConfig.globalDb.getAllSearches()],
			["test4", "test2", "test1", "test3", "test5", "testname"])
		self.assertEqual(
			[e["name"] for e in tempPbConfig.globalDb.getSearchList()],
			[])
		self.assertEqual(
			[e["name"] for e in tempPbConfig.globalDb.getSearchList(True)],
			["test1"])
		self.assertEqual(
			[e["name"] for e in \
				tempPbConfig.globalDb.getSearchList(False, True)],
			["test4", "test3", "test5"])
		self.assertEqual(
			[e["name"] for e in \
				tempPbConfig.globalDb.getSearchList(True, True)],
			["test2", "testname"])

		pbConfig.params["maxSavedSearches"] = 5
		self.assertTrue(tempPbConfig.globalDb.updateSearchOrder(True))
		self.assertEqual([e["name"] for e in \
			tempPbConfig.globalDb.getSearchList(False, True)],
			["test4", "test3"])
		self.assertTrue(tempPbConfig.globalDb.updateSearchOrder(True))
		self.assertEqual([e["name"] for e in \
			tempPbConfig.globalDb.getSearchList(False, True)],
			["test4"])
		self.assertTrue(tempPbConfig.globalDb.updateSearchOrder(True))
		self.assertEqual([e["name"] for e in \
			tempPbConfig.globalDb.getAllSearches()],
			["test2", "test1", "test4", "testname"])

		self.assertTrue(tempPbConfig.globalDb.insertSearch(
			"testA", 1, {}, [], False, False))
		self.assertTrue(tempPbConfig.globalDb.updateSearchOrder(False))
		self.assertEqual([e["count"] for e in \
			tempPbConfig.globalDb.getSearchList(False, False)], [2])

		self.assertEqual(tempPbConfig.globalDb.countSearches(), 5)
		for idS in [e["idS"] for e in tempPbConfig.globalDb.getAllSearches()]:
			self.assertTrue(tempPbConfig.globalDb.deleteSearch(idS))
		self.assertEqual(tempPbConfig.globalDb.countSearches(), 0)

class TestProfilesDB(unittest.TestCase):
	"""Test GlobalDB"""
	@patch('sys.stdout', new_callable=StringIO)
	def assert_in_stdout(self, function, expected_output, mock_stdout):
		"""Catch and if test stdout of the function contains a string"""
		pBErrorManager.tempHandler(sys.stdout, format='%(message)s')
		function()
		pBErrorManager.rmTempHandler()
		self.assertIn(expected_output, mock_stdout.getvalue())

	def test_GlobalDB(self):
		"""Test database for profiles"""
		if os.path.exists(tempProfName):
			os.remove(tempProfName)
		self.globalDb = GlobalDB(tempProfName,
			pbConfig.logger, pbConfig.dataPath, info=False)
		self.assertEqual(self.globalDb.countProfiles(), 1)
		self.assertEqual(self.globalDb.getDefaultProfile(), "default")

		with self.assertRaises(SystemExit):
			self.assertFalse(self.globalDb.createProfile())
		with self.assertRaises(SystemExit):
			self.assertFalse(self.globalDb.createProfile("default1"))
		with self.assertRaises(SystemExit):
			self.assertFalse(self.globalDb.createProfile(
				databasefile="database1.db"))

		self.assertEqual(self.globalDb.countProfiles(), 1)
		self.assertTrue(self.globalDb.createProfile("temp1",
			"d", "somefile.db", "old"))
		self.assertEqual(self.globalDb.countProfiles(), 2)
		self.assertEqual(self.globalDb.getDefaultProfile(), "default")
		self.assertEqual(self.globalDb.getProfileOrder(), ["default", "temp1"])

		output = {"name": "temp1",
			"description": "d",
			"databasefile": "somefile.db",
			"oldCfg": "old",
			"isDefault": 0,
			"ord": 100}
		self.assertEqual(dict(self.globalDb.getProfile("temp1")), output)
		self.assertTrue(self.globalDb.updateProfileField("temp1",
			"description", "desc"))
		output["description"] = "desc"
		self.assertEqual(dict(self.globalDb.getProfile("temp1")), output)
		self.assertTrue(self.globalDb.updateProfileField("somefile.db",
			"name", "temp", "databasefile"))
		output["name"] = "temp"

		self.assertEqual(dict(self.globalDb.getProfile("temp")), output)
		self.assertEqual(dict(self.globalDb.getProfile(
			filename="somefile.db")), output)
		self.assertEqual(dict(self.globalDb.getProfile()), {})
		self.assertEqual(dict(self.globalDb.getProfile("temp", "somefile.db")),
			{})

		self.assertFalse(self.globalDb.updateProfileField("tmp",
			"name", "temp", "name"))
		self.assertFalse(self.globalDb.updateProfileField("tmp",
			"databasefile", "temp", "isDefault"))
		self.assertFalse(self.globalDb.updateProfileField("tmp",
			"name", "temp", "isDefault"))
		self.assertFalse(self.globalDb.updateProfileField("tmp",
			"name1", "temp"))

		self.assertTrue(self.globalDb.updateProfileField(1,
			"description", "newsomething", "isDefault"))
		output["name"] = "temp"
		self.assertEqual(dict(self.globalDb.getProfile("temp")), output)

		output = [dict(e) for e in self.globalDb.getProfiles()]
		self.assertEqual(output, [{"name": u"default",
			"description": u"newsomething",
			"databasefile": str(os.path.join(pbConfig.dataPath,
				config_defaults["mainDatabaseName"].replace("PBDATA", ""))),
			"oldCfg": u"",
			"isDefault": 1,
			"ord": 100},
			{"name": u"temp",
			"description": u"desc",
			"databasefile": u"somefile.db",
			"oldCfg": u"old",
			"isDefault": 0,
			"ord": 100}])

		self.assertEqual(self.globalDb.getProfileOrder(),
			["default", "temp"])
		self.assertTrue(self.globalDb.updateProfileField(
			"somefile.db", "name", "abc", "databasefile"))
		self.assertEqual(self.globalDb.getProfileOrder(), ["abc", "default"])
		self.assertTrue(self.globalDb.setProfileOrder(["default", "abc"]))
		self.assertEqual(self.globalDb.getProfileOrder(), ["default", "abc"])
		self.assertFalse(self.globalDb.setProfileOrder())
		self.assert_in_stdout(self.globalDb.setProfileOrder, "No order given!")
		self.assertFalse(self.globalDb.setProfileOrder(["default", "temp"]))
		self.assert_in_stdout(lambda: self.globalDb.setProfileOrder(
			["default", "temp"]),
			"List of profile names does not match existing profiles!")
		with patch("physbiblio.databaseCore.PhysBiblioDBCore.connExec",
				side_effect=[True, False, True, False]) as _mock:
			self.assertFalse(self.globalDb.setProfileOrder(["abc", "default"]))
			self.assert_in_stdout(lambda: self.globalDb.setProfileOrder(
				["abc", "default"]),
				"Something went wrong when setting new profile order. "
				+ "Undoing...")

		self.assertEqual(self.globalDb.getDefaultProfile(), "default")
		self.assertTrue(self.globalDb.setDefaultProfile("abc"))
		self.assertEqual(self.globalDb.getDefaultProfile(), "abc")
		self.assertFalse(self.globalDb.setDefaultProfile())
		self.assert_in_stdout(self.globalDb.setDefaultProfile,
			"No name given!")
		self.assertFalse(self.globalDb.setDefaultProfile("temp"))
		self.assert_in_stdout(lambda: self.globalDb.setDefaultProfile("temp"),
			"No profiles with the given name!")
		with patch("physbiblio.databaseCore.PhysBiblioDBCore.connExec",
				side_effect=[True, False, True, False]) as _mock:
			self.assertFalse(self.globalDb.setDefaultProfile("abc"))
			self.assert_in_stdout(
				lambda: self.globalDb.setDefaultProfile("abc"),
				"Something went wrong when setting new default profile. "
				+ "Undoing...")
		self.assertEqual(self.globalDb.getDefaultProfile(), "abc")

		self.assertFalse(self.globalDb.deleteProfile(""))
		self.assertTrue(self.globalDb.deleteProfile("temp1"))
		self.assertEqual(self.globalDb.countProfiles(), 2)
		self.assertTrue(self.globalDb.deleteProfile("abc"))
		self.assertEqual(self.globalDb.countProfiles(), 1)
		self.assertEqual(self.globalDb.getDefaultProfile(), "default")

@unittest.skipIf(skipTestsSettings.db, "Database tests")
class TestConfigDB(DBTestCase):
	"""Test ConfigurationDB"""
	def test_configDB(self):
		"""Test count, insert and update, delete and get methods"""
		self.assertEqual(self.pBDB.config.count(), 0)
		self.assertTrue(self.pBDB.config.insert("test", "somevalue"))
		self.assertEqual(self.pBDB.config.count(), 1)
		self.assertTrue(self.pBDB.config.insert("test1", "somevalue"))
		self.assertEqual(self.pBDB.config.count(), 2)
		self.assertTrue(self.pBDB.config.insert("test", "somevalue1"))
		self.assertEqual(self.pBDB.config.count(), 2)
		self.assertTrue(self.pBDB.config.update("test1", "somevalueA"))
		self.assertEqual(self.pBDB.config.count(), 2)
		self.assertTrue(self.pBDB.config.update("test2", "somevalue"))
		self.assertEqual(self.pBDB.config.count(), 3)
		for n, v in [
				["test", "somevalue1"],
				["test1", "somevalueA"],
				["test2", "somevalue"]]:
			self.assertEqual(self.pBDB.config.getByName(n)[0]["value"], v)
		self.assertEqual({e["name"]: e["value"] for e in \
			self.pBDB.config.getAll()},
			{"test": "somevalue1",
			"test1": "somevalueA",
			"test2": "somevalue"})
		self.assertTrue(self.pBDB.config.delete("test3"))
		self.assertEqual(self.pBDB.config.count(), 3)
		self.assertTrue(self.pBDB.config.delete("test2"))
		self.assertEqual(self.pBDB.config.count(), 2)
		if os.path.exists(tempDBName):
			os.remove(tempDBName)

def tearDownModule():
	if os.path.exists(tempCfgName):
		os.remove(tempCfgName)
	if os.path.exists(tempCfgName1):
		os.remove(tempCfgName1)
	if os.path.exists(tempProfName):
		os.remove(tempProfName)
	if os.path.exists(tempOldCfgName):
		os.remove(tempOldCfgName)

if __name__=='__main__':
	unittest.main()
