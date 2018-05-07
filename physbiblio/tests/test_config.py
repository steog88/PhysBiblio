#!/usr/bin/env python
"""
Test file for the physbiblio.config module.

This file is part of the physbiblio package.
"""
import sys, traceback
import os

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch
else:
	import unittest
	from unittest.mock import patch

try:
	from physbiblio.setuptests import *
	from physbiblio.databaseCore import physbiblioDBCore
	from physbiblio.config import pbConfig, ConfigVars, config_defaults, configurationDB, profilesDB
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

tempOldCfgName = os.path.join(pbConfig.dataPath, "tests_%s.cfg"%today_ymd)
tempCfgName = os.path.join(pbConfig.dataPath, "tests_cfg_%s.db"%today_ymd)
tempCfgName1 = os.path.join(pbConfig.dataPath, "tests_cfg1_%s.db"%today_ymd)
tempProfName = os.path.join(pbConfig.dataPath, "tests_profiles_%s.db"%today_ymd)

class TestConfigMethods(unittest.TestCase):
	"""Tests for methods in physbiblio.config"""

	@patch('sys.stdout', new_callable=StringIO)
	def assert_in_stdout_multi(self, function, expected_output, mock_stdout):
		"""Catch and if test stdout of the function contains a string"""
		pBErrorManager.tempHandler(sys.stdout, format = '%(message)s')
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
				return_value = ("tmp", {"tmp": {"db": tempCfgName, "d":""}}, ["tmp"])) as _mock_readprof:
			self.assertFalse(os.path.exists(tempCfgName))
			tempPbConfig = ConfigVars()
			tempDb = physbiblioDBCore(tempCfgName, tempPbConfig.logger, info = False)
			configDb = configurationDB(tempDb)

			self.assertTrue(os.path.exists(tempCfgName))
			_mock_readprof.assert_called_once_with()
			self.assertEqual(len(configDb.getAll()), 0)

			tempPbConfig1 = ConfigVars()
			self.assertEqual(tempPbConfig1.params, newConfParamsDict)
			tempPbConfig1.params["logFileName"] = "otherfilename"
			tempPbConfig1.params["timeoutWebSearch"] = 10.
			tempPbConfig1.params["askBeforeExit"] = True
			tempPbConfig1.params["maxAuthorNames"] = 5
			tempPbConfig1.params["defaultCategories"] = [1]
			with open(tempOldCfgName, "w") as f:
				f.write("logFileName = otherfilename\n"+
					"timeoutWebSearch = 10.0\n"+
					"askBeforeExit = True\n"+
					"maxAuthorNames = 5\n"+
					"defaultCategories = [1]\n")
			tempPbConfig = ConfigVars()
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
		self.assertEqual(tempPbConfig.defaultProfileName, "default")
		self.assertEqual(tempPbConfig.profiles,
			{u"default": {
				"d": u"",
				"f": u"",
				"n": u"default",
				"db": str(os.path.join(pbConfig.dataPath, config_defaults["mainDatabaseName"].replace("PBDATA", "")))}})
		self.assertEqual(tempPbConfig.profileOrder, ["default"])
		self.assertEqual(tempPbConfig.params, config_defaults)

		tempProfName1 = os.path.join(pbConfig.dataPath, "tests_profiles1_%s.db"%today_ymd)
		self.assertTrue(tempPbConfig.profilesDb.createProfile("temp", "none", tempProfName1))
		self.assertTrue(tempPbConfig.profilesDb.setDefaultProfile("temp"))
		self.assertEqual(tempPbConfig.defaultProfileName, "default")
		self.assertEqual([e["n"] for e in tempPbConfig.profiles.values()], ["default"])
		self.assertEqual(tempPbConfig.profileOrder, ["default"])
		self.assertEqual(tempPbConfig.currentProfileName, "default")
		self.assertEqual(tempPbConfig.currentDatabase,
			str(os.path.join(pbConfig.dataPath, config_defaults["mainDatabaseName"].replace("PBDATA", ""))))
		tempParams = tempPbConfig.params

		default, profiles, ordered = tempPbConfig.readProfiles()
		self.assertEqual(default, "temp")
		self.assertEqual(profiles,
			{u"default": {
				"d": u"",
				"f": u"",
				"n": u"default",
				"db": str(os.path.join(pbConfig.dataPath, config_defaults["mainDatabaseName"].replace("PBDATA", "")))},
			u"temp": {
				"d": u"none",
				"f": u"",
				"n": u"temp",
				"db": tempProfName1}})
		self.assertEqual(ordered, ["default", "temp"])

		tempProfName2 = tempProfName1.replace("profiles1", "profiles2")
		self.assertTrue(tempPbConfig.profilesDb.createProfile("other", "none1", tempProfName2))
		tempPbConfig.reloadProfiles()
		self.assertEqual(tempPbConfig.defaultProfileName, "temp")
		self.assertEqual(sorted([e["n"] for e in tempPbConfig.profiles.values()]), ["default", "other", "temp"])
		self.assertEqual(tempPbConfig.profileOrder, ["default", "other", "temp"])
		self.assertEqual(tempPbConfig.currentProfileName, "temp")
		self.assertEqual(tempPbConfig.currentDatabase, tempProfName1)

		tempPbConfig.reInit("other")
		self.assertEqual(tempPbConfig.defaultProfileName, "temp")
		self.assertEqual(sorted([e["n"] for e in tempPbConfig.profiles.values()]), ["default", "other", "temp"])
		self.assertEqual(tempPbConfig.profileOrder, ["default", "other", "temp"])
		self.assertEqual(tempPbConfig.currentProfileName, "other")
		self.assertEqual(tempPbConfig.currentDatabase, tempProfName2)

		tempPbConfig.reInit("other", tempPbConfig.profiles["temp"])
		self.assertEqual(tempPbConfig.currentProfileName, "other")
		self.assertEqual(tempPbConfig.currentDatabase, tempProfName1)

		tempPbConfig.reInit("temp", tempPbConfig.profiles["temp"])
		self.assertEqual(tempPbConfig.currentProfileName, "temp")
		self.assertEqual(tempPbConfig.currentDatabase, tempProfName1)

		tempPbConfig.reInit("nonexistent")
		self.assertEqual(tempPbConfig.currentProfileName, "temp")
		self.assertEqual(tempPbConfig.currentDatabase, tempProfName1)
		self.assertEqual(tempPbConfig.params, tempParams)

		tempDb = physbiblioDBCore(tempProfName1, tempPbConfig.logger, info = False)
		configDb = configurationDB(tempDb)
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

		tempDb.closeDB(info = False)
		if os.path.exists(tempProfName1):
			os.remove(tempProfName1)
		if os.path.exists(tempProfName2):
			os.remove(tempProfName2)

class TestProfilesDB(unittest.TestCase):
	"""Test profilesDB"""
	@patch('sys.stdout', new_callable=StringIO)
	def assert_in_stdout(self, function, expected_output, mock_stdout):
		"""Catch and if test stdout of the function contains a string"""
		pBErrorManager.tempHandler(sys.stdout, format = '%(message)s')
		function()
		pBErrorManager.rmTempHandler()
		self.assertIn(expected_output, mock_stdout.getvalue())

	def test_profilesDB(self):
		"""Test database for profiles"""
		if os.path.exists(tempProfName):
			os.remove(tempProfName)
		self.profilesDb = profilesDB(tempProfName, pbConfig.logger, pbConfig.dataPath, info = False)
		self.assertEqual(self.profilesDb.countProfiles(), 1)
		self.assertEqual(self.profilesDb.getDefaultProfile(), "default")

		with self.assertRaises(SystemExit):
			self.assertFalse(self.profilesDb.createProfile())
		with self.assertRaises(SystemExit):
			self.assertFalse(self.profilesDb.createProfile("default1"))
		with self.assertRaises(SystemExit):
			self.assertFalse(self.profilesDb.createProfile(databasefile = "database1.db"))

		self.assertEqual(self.profilesDb.countProfiles(), 1)
		self.assertTrue(self.profilesDb.createProfile("temp1", "d", "somefile.db", "old"))
		self.assertEqual(self.profilesDb.countProfiles(), 2)
		self.assertEqual(self.profilesDb.getDefaultProfile(), "default")
		self.assertEqual(self.profilesDb.getProfileOrder(), ["default", "temp1"])

		output = {"name": "temp1",
			"description": "d",
			"databasefile": "somefile.db",
			"oldCfg": "old",
			"isDefault": 0,
			"ord": 100}
		self.assertEqual(dict(self.profilesDb.getProfile("temp1")), output)
		self.assertTrue(self.profilesDb.updateProfileField("temp1", "description", "desc"))
		output["description"] = "desc"
		self.assertEqual(dict(self.profilesDb.getProfile("temp1")), output)
		self.assertTrue(self.profilesDb.updateProfileField("somefile.db", "name", "temp", "databasefile"))
		output["name"] = "temp"

		self.assertEqual(dict(self.profilesDb.getProfile("temp")), output)
		self.assertEqual(dict(self.profilesDb.getProfile(filename = "somefile.db")), output)
		self.assertEqual(dict(self.profilesDb.getProfile()), {})
		self.assertEqual(dict(self.profilesDb.getProfile("temp", "somefile.db")), {})

		self.assertFalse(self.profilesDb.updateProfileField("tmp", "name", "temp", "name"))
		self.assertFalse(self.profilesDb.updateProfileField("tmp", "databasefile", "temp", "isDefault"))
		self.assertFalse(self.profilesDb.updateProfileField("tmp", "name", "temp", "isDefault"))
		self.assertFalse(self.profilesDb.updateProfileField("tmp", "name1", "temp"))

		self.assertTrue(self.profilesDb.updateProfileField(1, "description", "newsomething", "isDefault"))
		output["name"] = "temp"
		self.assertEqual(dict(self.profilesDb.getProfile("temp")), output)

		output = [dict(e) for e in self.profilesDb.getProfiles()]
		self.assertEqual(output, [{"name": u"default",
			"description": u"newsomething",
			"databasefile": str(os.path.join(pbConfig.dataPath, config_defaults["mainDatabaseName"].replace("PBDATA", ""))),
			"oldCfg": u"",
			"isDefault": 1,
			"ord": 100},
			{"name": u"temp",
			"description": u"desc",
			"databasefile": u"somefile.db",
			"oldCfg": u"old",
			"isDefault": 0,
			"ord": 100}])

		self.assertEqual(self.profilesDb.getProfileOrder(), ["default", "temp"])
		self.assertTrue(self.profilesDb.updateProfileField("somefile.db", "name", "abc", "databasefile"))
		self.assertEqual(self.profilesDb.getProfileOrder(), ["abc", "default"])
		self.assertTrue(self.profilesDb.setProfileOrder(["default", "abc"]))
		self.assertEqual(self.profilesDb.getProfileOrder(), ["default", "abc"])
		self.assertFalse(self.profilesDb.setProfileOrder())
		self.assert_in_stdout(self.profilesDb.setProfileOrder, "No order given!")
		self.assertFalse(self.profilesDb.setProfileOrder(["default", "temp"]))
		self.assert_in_stdout(lambda: self.profilesDb.setProfileOrder(["default", "temp"]),
			"List of profile names does not match existing profiles!")
		with patch("physbiblio.databaseCore.physbiblioDBCore.connExec",
				side_effect = [True, False, True, False]) as _mock:
			self.assertFalse(self.profilesDb.setProfileOrder(["abc", "default"]))
			self.assert_in_stdout(lambda: self.profilesDb.setProfileOrder(["abc", "default"]),
				"Something went wrong when setting new profile order. Undoing...")

		self.assertEqual(self.profilesDb.getDefaultProfile(), "default")
		self.assertTrue(self.profilesDb.setDefaultProfile("abc"))
		self.assertEqual(self.profilesDb.getDefaultProfile(), "abc")
		self.assertFalse(self.profilesDb.setDefaultProfile())
		self.assert_in_stdout(self.profilesDb.setDefaultProfile,
			"No name given!")
		self.assertFalse(self.profilesDb.setDefaultProfile("temp"))
		self.assert_in_stdout(lambda: self.profilesDb.setDefaultProfile("temp"),
			"No profiles with the given name!")
		with patch("physbiblio.databaseCore.physbiblioDBCore.connExec",
				side_effect = [True, False, True, False]) as _mock:
			self.assertFalse(self.profilesDb.setDefaultProfile("abc"))
			self.assert_in_stdout(lambda: self.profilesDb.setDefaultProfile("abc"),
				"Something went wrong when setting new default profile. Undoing...")
		self.assertEqual(self.profilesDb.getDefaultProfile(), "abc")

		self.assertFalse(self.profilesDb.deleteProfile(""))
		self.assertTrue(self.profilesDb.deleteProfile("temp1"))
		self.assertEqual(self.profilesDb.countProfiles(), 2)
		self.assertTrue(self.profilesDb.deleteProfile("abc"))
		self.assertEqual(self.profilesDb.countProfiles(), 1)

@unittest.skipIf(skipDBTests, "Database tests")
class TestConfigDB(DBTestCase):
	"""Test configurationDB"""
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
		self.assertEqual({e["name"]: e["value"] for e in self.pBDB.config.getAll()},
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
