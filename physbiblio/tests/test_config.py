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
	from physbiblio.config import pbConfig, ConfigVars, config_defaults
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

tempCfgName = os.path.join(pbConfig.dataPath, "tests_%s.cfg"%today_ymd)
tempProfName = os.path.join(pbConfig.dataPath, "tests_%s.dat"%today_ymd)
class TestConfigMethods(unittest.TestCase):
	"""Tests for methods in physbiblio.config"""

	def test_config(self):
		"""Test config methods for config management"""
		if os.path.exists(tempCfgName):
			os.remove(tempCfgName)
		newConfParamsDict = dict(config_defaults)
		with patch("physbiblio.config.ConfigVars.readProfiles",
				return_value = ("tmp", {"tmp": {"f": tempCfgName, "d":""}})) as _mock_readprof:
			self.assertFalse(os.path.exists(tempCfgName))
			tempPbConfig = ConfigVars()
			self.assertTrue(os.path.exists(tempCfgName))
			_mock_readprof.assert_called_once_with()
			with open(tempCfgName) as r:
				self.assertEqual(r.readlines(), [])

			self.assertEqual(tempPbConfig.params, newConfParamsDict)
			tempPbConfig.params["logFileName"] = "newfilename"
			newConfParamsDict["logFileName"] = "newfilename"
			tempPbConfig.saveConfigFile()
			with open(tempCfgName) as r:
				self.assertEqual(r.readlines(), ["logFileName = newfilename\n"])

			tempPbConfig1 = ConfigVars()
			self.assertEqual(tempPbConfig1.params, newConfParamsDict)
			tempPbConfig1.params["logFileName"] = "otherfilename"
			newConfParamsDict["logFileName"] = "otherfilename"
			tempPbConfig1.saveConfigFile()
			with open(tempCfgName) as r:
				self.assertEqual(r.readlines(), ["logFileName = otherfilename\n"])

			tempPbConfig.reInit("tmp", {"f": tempCfgName, "d":""})
			self.assertEqual(tempPbConfig.params, newConfParamsDict)
			os.remove(tempCfgName)
			tempPbConfig.reInit("tmp", {"f": tempCfgName, "d":""})
			self.assertEqual(tempPbConfig.params, config_defaults)

			tempPbConfig1.params["timeoutWebSearch"] = 10.
			tempPbConfig1.params["askBeforeExit"] = True
			tempPbConfig1.params["maxAuthorNames"] = 5
			tempPbConfig1.params["defaultCategories"] = [1]
			tempPbConfig1.saveConfigFile()
			with open(tempCfgName) as r:
				self.assertEqual(r.readlines(),
					["logFileName = otherfilename\n",
					"timeoutWebSearch = 10.0\n",
					"askBeforeExit = True\n",
					"maxAuthorNames = 5\n",
					"defaultCategories = [1]\n"])
			tempPbConfig.reInit("tmp", {"f": tempCfgName, "d":""})
			self.assertEqual(tempPbConfig.params, tempPbConfig1.params)

			os.remove(tempCfgName)
			self.assertFalse(tempPbConfig1.needFirstConfiguration)
			tempPbConfig1.readConfigFile()
			self.assertTrue(tempPbConfig1.needFirstConfiguration)

	def test_profiles(self):
		"""Test config methods for profiles management"""
		tempPbConfig = ConfigVars()
		if os.path.exists(tempProfName):
			os.remove(tempProfName)
		origDef, origProfiles = tempPbConfig.defProf, tempPbConfig.profiles

		tempPbConfig.defProf, tempPbConfig.profiles = ("tmp", {"tmp": {"f": tempCfgName, "d":""}})
		tempPbConfig.configProfilesFile = tempProfName
		tempPbConfig.writeProfiles()
		with open(tempProfName) as r:
			lines = r.readlines()
		self.assertEqual(lines[0], "'tmp',\n")
		self.assertIn(lines[1],
			["{'tmp': {'f': '%s', 'd': ''}}\n"%tempCfgName,
			"{'tmp': {'d': '', 'f': '%s'}}\n"%tempCfgName])

		tempPbConfig.defProf, tempPbConfig.profiles = origDef, origProfiles
		self.assertEqual(tempPbConfig.defProf, origDef)
		self.assertEqual(tempPbConfig.profiles, origProfiles)
		tempPbConfig.defProf, tempPbConfig.profiles = tempPbConfig.readProfiles()
		self.assertEqual(tempPbConfig.defProf, "tmp")
		self.assertEqual(tempPbConfig.profiles, {"tmp": {"f": tempCfgName, "d":""}})

def tearDownModule():
	if os.path.exists(tempCfgName):
		os.remove(tempCfgName)
	if os.path.exists(tempProfName):
		os.remove(tempProfName)

if __name__=='__main__':
	unittest.main()
