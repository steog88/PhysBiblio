#!/usr/bin/env python
"""Test file for the physbiblio.config module.

This file is part of the physbiblio package.
"""
import logging
import logging.handlers
import os
import sys
import traceback
from collections import OrderedDict

import six
from appdirs import AppDirs

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import MagicMock, call, patch
else:
    import unittest
    from unittest.mock import MagicMock, call, patch

try:
    from physbiblio.config import (
        ConfigParameter,
        ConfigParametersList,
        ConfigurationDB,
        ConfigVars,
        GlobalDB,
        addFileHandler,
        configuration_params,
        getLogLevel,
        globalLogName,
        ignoreParameterOrder,
        loggingLevels,
        pbConfig,
        replacePBDATA,
    )
    from physbiblio.databaseCore import PhysBiblioDBCore, PhysBiblioDBSub
    from physbiblio.setuptests import *
    from physbiblio.tablesDef import profilesSettingsTable, searchesTable, tableFields
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())

tempOldCfgName = os.path.join(pbConfig.dataPath, "tests_%s.cfg" % today_ymd)
tempCfgName = os.path.join(pbConfig.dataPath, "tests_cfg_%s.db" % today_ymd)
tempCfgName1 = os.path.join(pbConfig.dataPath, "tests_cfg1_%s.db" % today_ymd)
tempProfName = os.path.join(pbConfig.dataPath, "tests_prof_%s.db" % today_ymd)


@patch("logging.Logger.debug")
@patch("logging.Logger.info")
@patch("logging.Logger.warning")
@patch("logging.Logger.error")
@patch("logging.Logger.exception")
class TestConfigParameter(unittest.TestCase):
    """Tests for ConfigParameter from physbiblio.config"""

    def test_init(self, *args):
        """Test __init__"""
        p = ConfigParameter(
            "name", "abc", description="desc", special="int", isGlobal=True
        )
        self.assertEqual(p.name, "name")
        self.assertEqual(p.default, "abc")
        self.assertEqual(p.description, "desc")
        self.assertEqual(p.special, "int")
        self.assertEqual(p.isGlobal, True)
        p = ConfigParameter("name", "abc")
        self.assertEqual(p.name, "name")
        self.assertEqual(p.default, "abc")
        self.assertEqual(p.description, "")
        self.assertEqual(p.special, None)
        self.assertEqual(p.isGlobal, False)

    def test_getitem(self, *args):
        """test __getitem__"""
        p = ConfigParameter(
            "name", "abc", description="desc", special="int", isGlobal=True
        )
        self.assertEqual(p["name"], "name")
        self.assertEqual(p["default"], "abc")
        self.assertEqual(p["description"], "desc")
        self.assertEqual(p["special"], "int")
        self.assertEqual(p["isGlobal"], True)
        with patch("logging.Logger.warning") as _w:
            self.assertEqual(p["nonexistent"], None)
            _w.assert_called_once_with(
                "Attribute does not exist for current ConfigParameter: nonexistent"
            )


@patch("logging.Logger.debug")
@patch("logging.Logger.info")
@patch("logging.Logger.warning")
@patch("logging.Logger.error")
@patch("logging.Logger.exception")
class TestConfigParametersList(unittest.TestCase):
    """Tests for ConfigParametersList from physbiblio.config"""

    def test_init(self, *args):
        """Test __init__"""
        p = ConfigParametersList()
        self.assertIsInstance(p, OrderedDict)

    def test_add(self, *args):
        """Test add"""
        pl = ConfigParametersList()
        p1 = ConfigParameter("name", "abc")
        p2 = ConfigParameter("other", "def")
        pl.add(p1)
        self.assertEqual(pl["name"], p1)
        pl.add(p2)
        self.assertEqual(pl["other"], p2)
        self.assertEqual(list(pl.keys()), ["name", "other"])


@patch("logging.Logger.debug")
@patch("logging.Logger.info")
@patch("logging.Logger.warning")
@patch("logging.Logger.error")
@patch("logging.Logger.exception")
class TestConfigGlobals(unittest.TestCase):
    """Tests for global variables in physbiblio.config"""

    def test_config(self, *args):
        """test global variables"""
        import physbiblio.config as pbc

        self.assertTrue(hasattr(pbc, "globalLogName"))
        self.assertIsInstance(pbc.configuration_params, ConfigParametersList)
        self.assertIsInstance(pbc.ignoreParameterOrder, list)
        self.assertIsInstance(pbc.loggingLevels, list)
        self.assertIsInstance(pbc.pbConfig, ConfigVars)


@patch("logging.Logger.debug")
@patch("logging.Logger.info")
@patch("logging.Logger.warning")
@patch("logging.Logger.error")
@patch("logging.Logger.exception")
class TestConfigMethods(unittest.TestCase):
    """Tests for methods in physbiblio.config"""

    def test_config(self, *args):
        """Test config methods for config management"""
        if os.path.exists(tempCfgName):
            os.remove(tempCfgName)
        newConfParamsDict_or = {k: p.default for k, p in configuration_params.items()}
        del newConfParamsDict_or["mainDatabaseName"]
        with patch(
            "physbiblio.config.ConfigVars.readProfiles",
            return_value=("tmp", {"tmp": {"db": tempCfgName, "d": ""}}, ["tmp"]),
            autospec=True,
        ) as _mock_readprof:
            self.assertFalse(os.path.exists(tempCfgName))
            tempPbConfig = ConfigVars()
            tempPbConfig.prepareLogger("physbibliotestlog")
            tempDb = PhysBiblioDBCore(tempCfgName, tempPbConfig.logger, info=False)
            configDb = ConfigurationDB(tempDb)

            self.assertTrue(os.path.exists(tempCfgName))
            _mock_readprof.assert_called_once_with(tempPbConfig)
            self.assertEqual(len(configDb.getAll()), 0)

            tempPbConfig1 = ConfigVars()
            tempPbConfig1.prepareLogger("physbibliotestlog")
            newConfParamsDict = newConfParamsDict_or.copy()
            for k, v in newConfParamsDict.items():
                newConfParamsDict[k] = tempPbConfig1.replacePBDATA(v)
            self.assertEqual(tempPbConfig1.params, newConfParamsDict)
            with open(tempOldCfgName, "w") as f:
                f.write(
                    "logFileName = otherfilename\n"
                    + "timeoutWebSearch = 10.0\n"
                    + "askBeforeExit = True\n"
                    + "maxAuthorNames = 5\n"
                    + "defaultCategories = [1]\n"
                )
            tempPbConfig = ConfigVars()
            tempPbConfig.prepareLogger("physbibliotestlog")
            tempPbConfig.configMainFile = tempOldCfgName
            tempPbConfig.oldReadConfigFile()
            newConfParamsDict = newConfParamsDict_or.copy()
            for k, v in newConfParamsDict.items():
                newConfParamsDict[k] = tempPbConfig.replacePBDATA(v)
            newConfParamsDict["logFileName"] = "otherfilename"
            newConfParamsDict["timeoutWebSearch"] = 10.0
            newConfParamsDict["askBeforeExit"] = True
            newConfParamsDict["maxAuthorNames"] = 5
            newConfParamsDict["defaultCategories"] = [1]
            newConfParamsDict["mainDatabaseName"] = tempPbConfig.replacePBDATA(
                configuration_params["mainDatabaseName"].default
            )
            self.maxDiff = None
            self.assertEqual(tempPbConfig.params, newConfParamsDict)

            with patch.dict(
                os.environ,
                {"PHYSBIBLIO_CONFIG": "", "PHYSBIBLIO_DATA": ""},
                clear=False,
            ), patch(
                "physbiblio.config.GlobalDB", return_value=tempPbConfig.globalDb
            ) as _c:
                tempPbConfig1 = ConfigVars()
                self.assertNotEqual(tempPbConfig1.configPath, ".")
                self.assertNotEqual(tempPbConfig1.dataPath, ".")
            with patch.dict(
                os.environ,
                {"PHYSBIBLIO_CONFIG": ".", "PHYSBIBLIO_DATA": "."},
                clear=False,
            ), patch(
                "physbiblio.config.GlobalDB", return_value=tempPbConfig.globalDb
            ) as _c:
                tempPbConfig1 = ConfigVars()
                self.assertEqual(tempPbConfig1.configPath, ".")
                self.assertEqual(tempPbConfig1.dataPath, ".")
        os.remove(tempCfgName)
        os.remove(tempOldCfgName)

    def test_profiles(self, *args):
        """Test config methods for profiles management"""
        if os.path.exists(tempProfName):
            os.remove(tempProfName)
        tempPbConfig = ConfigVars(tempProfName)
        tempPbConfig.prepareLogger("physbibliotestlog")
        tempPbConfig.reloadProfiles()
        self.assertEqual(tempPbConfig.defaultProfileName, "default")
        self.assertEqual(
            tempPbConfig.profiles,
            {
                u"default": {
                    "d": u"",
                    "f": u"",
                    "n": u"default",
                    "db": str(
                        os.path.join(
                            pbConfig.dataPath,
                            configuration_params["mainDatabaseName"].default.replace(
                                "PBDATA", ""
                            ),
                        )
                    ),
                }
            },
        )
        self.assertEqual(tempPbConfig.profileOrder, ["default"])

        tempProfName1 = os.path.join(pbConfig.dataPath, "tests_prof1_%s.db" % today_ymd)
        self.assertTrue(
            tempPbConfig.globalDb.createProfile("temp", "none", tempProfName1)
        )
        self.assertTrue(tempPbConfig.globalDb.setDefaultProfile("temp"))
        self.assertEqual(tempPbConfig.defaultProfileName, "default")
        self.assertEqual([e["n"] for e in tempPbConfig.profiles.values()], ["default"])
        self.assertEqual(tempPbConfig.profileOrder, ["default"])
        self.assertEqual(tempPbConfig.currentProfileName, "default")
        self.assertEqual(
            tempPbConfig.currentDatabase,
            str(
                os.path.join(
                    pbConfig.dataPath,
                    configuration_params["mainDatabaseName"].default.replace(
                        "PBDATA", ""
                    ),
                )
            ),
        )
        tempPbConfig.setDefaultParams()
        defaultParams = tempPbConfig.params

        default, profiles, ordered = tempPbConfig.readProfiles()
        self.assertEqual(default, "temp")
        self.assertEqual(
            profiles,
            {
                u"default": {
                    "d": u"",
                    "f": u"",
                    "n": u"default",
                    "db": str(
                        os.path.join(
                            pbConfig.dataPath,
                            configuration_params["mainDatabaseName"].default.replace(
                                "PBDATA", ""
                            ),
                        )
                    ),
                },
                u"temp": {"d": u"none", "f": u"", "n": u"temp", "db": tempProfName1},
            },
        )
        self.assertEqual(ordered, ["default", "temp"])
        tempPbConfig.reloadProfiles()
        self.assertEqual(tempPbConfig.params, defaultParams)

        tempProfName2 = tempProfName1.replace("prof1", "prof2")
        self.assertTrue(
            tempPbConfig.globalDb.createProfile("other", "none1", tempProfName2)
        )
        tempPbConfig.reloadProfiles()
        self.assertEqual(tempPbConfig.defaultProfileName, "temp")
        self.assertEqual(
            sorted([e["n"] for e in tempPbConfig.profiles.values()]),
            ["default", "other", "temp"],
        )
        self.assertEqual(tempPbConfig.profileOrder, ["default", "other", "temp"])
        self.assertEqual(tempPbConfig.currentProfileName, "temp")
        self.assertEqual(tempPbConfig.currentProfile, tempPbConfig.profiles["temp"])
        self.assertEqual(tempPbConfig.currentDatabase, tempProfName1)

        tempPbConfig.reInit("other")
        self.assertEqual(tempPbConfig.defaultProfileName, "temp")
        self.assertEqual(
            sorted([e["n"] for e in tempPbConfig.profiles.values()]),
            ["default", "other", "temp"],
        )
        self.assertEqual(tempPbConfig.profileOrder, ["default", "other", "temp"])
        self.assertEqual(tempPbConfig.currentProfileName, "other")
        self.assertEqual(tempPbConfig.currentProfile, tempPbConfig.profiles["other"])
        self.assertEqual(tempPbConfig.currentDatabase, tempProfName2)

        tempPbConfig.reInit("other", tempPbConfig.profiles["temp"])
        self.assertEqual(tempPbConfig.currentProfileName, "other")
        self.assertEqual(tempPbConfig.currentProfile, tempPbConfig.profiles["temp"])
        self.assertEqual(tempPbConfig.currentDatabase, tempProfName1)

        tempPbConfig.reInit("temp", tempPbConfig.profiles["temp"])
        self.assertEqual(tempPbConfig.currentProfileName, "temp")
        self.assertEqual(tempPbConfig.currentProfile, tempPbConfig.profiles["temp"])
        self.assertEqual(tempPbConfig.currentDatabase, tempProfName1)

        tempPbConfig.reInit("nonexistent")
        self.assertEqual(tempPbConfig.currentProfileName, "temp")
        self.assertEqual(tempPbConfig.currentProfile, tempPbConfig.profiles["temp"])
        self.assertEqual(tempPbConfig.currentDatabase, tempProfName1)
        self.assertEqual(tempPbConfig.params, defaultParams)

        tempDb = PhysBiblioDBCore(tempProfName1, tempPbConfig.logger, info=False)
        configDb = ConfigurationDB(tempDb)
        configDb.insert("defaultCategories", "[0")
        configDb.commit()

        with patch("logging.Logger.warning") as _w:
            tempPbConfig.readConfig()
            self.assertEqual(tempPbConfig.params, defaultParams)
            _w.assert_any_call(
                "Failed in reading parameter 'defaultCategories'.", exc_info=True
            )

        configDb.insert("loggingLevel", "4")
        configDb.insert("pdfFolder", "/nonexistent/")
        configDb.insert("askBeforeExit", "True")
        configDb.insert("timeoutWebSearch", "20.")
        configDb.commit()
        defaultParams["loggingLevel"] = 4
        defaultParams["pdfFolder"] = u"/nonexistent/"
        defaultParams["askBeforeExit"] = True
        defaultParams["timeoutWebSearch"] = 20.0
        with patch("logging.Logger.warning") as _w:
            tempPbConfig.readConfig()
            _w.assert_any_call(
                "Failed in reading parameter 'defaultCategories'.", exc_info=True
            )
        self.assertEqual(tempPbConfig.params, defaultParams)

        configDb.insert("defaultCategories", "[0]")
        configDb.commit()
        defaultParams["defaultCategories"] = [0]
        tempPbConfig.readConfig()
        self.assertEqual(tempPbConfig.params, defaultParams)

        tempDb.closeDB(info=False)
        if os.path.exists(tempProfName1):
            os.remove(tempProfName1)
        if os.path.exists(tempProfName2):
            os.remove(tempProfName2)

    def test_searches(self, *args):
        """Test config methods for profiles management"""
        if os.path.exists(tempProfName):
            os.remove(tempProfName)
        tempPbConfig = ConfigVars(tempProfName)
        self.assertEqual(tempPbConfig.globalDb.countSearches(), 0)

        self.assertTrue(
            tempPbConfig.globalDb.insertSearch(
                "testname",
                123,
                {"field": "value"},
                ["a", "b", "c", "d", "e"],
                True,
                True,
                21,
                321,
            )
        )
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

        self.assertTrue(
            tempPbConfig.globalDb.insertSearch("test1", 2, {}, [], True, False)
        )
        self.assertTrue(
            tempPbConfig.globalDb.insertSearch("test2", 1, {}, [], True, True)
        )
        self.assertTrue(
            tempPbConfig.globalDb.insertSearch("test3", 3, {}, [], False, True)
        )
        self.assertTrue(
            tempPbConfig.globalDb.insertSearch("test4", 0, {}, [], False, True)
        )
        self.assertTrue(
            tempPbConfig.globalDb.insertSearch("test5", 122, {}, [], False, True)
        )
        self.assertEqual(tempPbConfig.globalDb.countSearches(), 6)
        self.assertEqual(
            [e["name"] for e in tempPbConfig.globalDb.getAllSearches()],
            ["test4", "test2", "test1", "test3", "test5", "testname"],
        )
        self.assertEqual([e["name"] for e in tempPbConfig.globalDb.getSearchList()], [])
        self.assertEqual(
            [e["name"] for e in tempPbConfig.globalDb.getSearchList(True)], ["test1"]
        )
        self.assertEqual(
            [e["name"] for e in tempPbConfig.globalDb.getSearchList(False, True)],
            ["test4", "test3", "test5"],
        )
        self.assertEqual(
            [e["name"] for e in tempPbConfig.globalDb.getSearchList(True, True)],
            ["test2", "testname"],
        )
        with patch("logging.Logger.warning") as _e:
            self.assertFalse(tempPbConfig.globalDb.updateSearchField(1, "abc", "ab"))
            _e.assert_called_once_with(
                "Empty value or field not in the following list: "
                + "[searchDict, replaceFields, name, limitNum, offsetNum]"
                + ".\nField: abc, value: ab"
            )
            _e.reset_mock()
            self.assertFalse(
                tempPbConfig.globalDb.updateSearchField(1, "searchDict", "")
            )
            _e.assert_called_once_with(
                "Empty value or field not in the following list: "
                + "[searchDict, replaceFields, name, limitNum, offsetNum]"
                + ".\nField: searchDict, value: "
            )
            _e.reset_mock()
            self.assertFalse(
                tempPbConfig.globalDb.updateSearchField(1, "replaceFields", None)
            )
            _e.assert_called_once_with(
                "Empty value or field not in the following list: "
                + "[searchDict, replaceFields, name, limitNum, offsetNum]"
                + ".\nField: replaceFields, value: None"
            )
            _e.reset_mock()
            self.assertTrue(
                tempPbConfig.globalDb.updateSearchField(
                    1, "replaceFields", {}, isReplace=False
                )
            )
            self.assertEqual(_e.call_count, 0)
            search = tempPbConfig.globalDb.getSearchByID(1)[0]
            self.assertEqual(search["replaceFields"], "{}")
            _e.reset_mock()
            self.assertTrue(
                tempPbConfig.globalDb.updateSearchField(1, "searchDict", "ab")
            )
            _e.assert_not_called()
            self.assertTrue(
                tempPbConfig.globalDb.updateSearchField(1, "replaceFields", "cd")
            )
            _e.assert_not_called()
            self.assertTrue(tempPbConfig.globalDb.updateSearchField(1, "name", "BA"))
            _e.assert_not_called()
            self.assertTrue(
                tempPbConfig.globalDb.updateSearchField(1, "limitNum", "91")
            )
            _e.assert_not_called()
            self.assertTrue(
                tempPbConfig.globalDb.updateSearchField(1, "offsetNum", "19")
            )
            _e.assert_not_called()
        search = tempPbConfig.globalDb.getSearchByID(1)[0]
        self.assertEqual(search["searchDict"], "ab")
        self.assertEqual(search["name"], "BA")
        self.assertEqual(search["replaceFields"], "cd")
        self.assertEqual(search["limitNum"], 91)
        self.assertEqual(search["offsetNum"], 19)

        with patch.dict(pbConfig.params, {"maxSavedSearches": 5}, clear=False):
            self.assertTrue(tempPbConfig.globalDb.updateSearchOrder(True))
            self.assertEqual(
                [e["name"] for e in tempPbConfig.globalDb.getSearchList(False, True)],
                ["test4", "test3"],
            )
            self.assertTrue(tempPbConfig.globalDb.updateSearchOrder(True))
            self.assertEqual(
                [e["name"] for e in tempPbConfig.globalDb.getSearchList(False, True)],
                ["test4"],
            )
            self.assertTrue(tempPbConfig.globalDb.updateSearchOrder(True))
            self.assertEqual(
                [e["name"] for e in tempPbConfig.globalDb.getAllSearches()],
                ["test2", "test1", "test4", "BA"],
            )

            self.assertTrue(
                tempPbConfig.globalDb.insertSearch("testA", 1, {}, [], False, False)
            )
            self.assertTrue(tempPbConfig.globalDb.updateSearchOrder(False))
            self.assertEqual(
                [e["count"] for e in tempPbConfig.globalDb.getSearchList(False, False)],
                [2],
            )

            self.assertEqual(tempPbConfig.globalDb.countSearches(), 5)
            for idS in [e["idS"] for e in tempPbConfig.globalDb.getAllSearches()]:
                self.assertTrue(tempPbConfig.globalDb.deleteSearch(idS))
            self.assertEqual(tempPbConfig.globalDb.countSearches(), 0)


@patch("logging.Logger.debug")
@patch("logging.Logger.info")
@patch("logging.Logger.warning")
@patch("logging.Logger.error")
@patch("logging.Logger.exception")
class TestGlobalDBOperations(unittest.TestCase):
    """Test GlobalDB"""

    def test_operations(self, *args):
        """Test database for profiles"""
        if os.path.exists(tempProfName):
            os.remove(tempProfName)
        self.globalDb = GlobalDB(
            tempProfName, pbConfig.logger, pbConfig.dataPath, info=False
        )
        self.assertEqual(self.globalDb.countProfiles(), 1)
        self.assertEqual(self.globalDb.getDefaultProfile(), "default")
        self.assertIsInstance(self.globalDb.config, ConfigurationDB)
        self.assertEqual(self.globalDb.config.mainDB, self.globalDb)

        with self.assertRaises(SystemExit):
            self.assertFalse(self.globalDb.createProfile())
        with self.assertRaises(SystemExit):
            self.assertFalse(self.globalDb.createProfile("default1"))
        with self.assertRaises(SystemExit):
            self.assertFalse(self.globalDb.createProfile(databasefile="database1.db"))

        self.assertEqual(self.globalDb.countProfiles(), 1)
        self.assertTrue(self.globalDb.createProfile("temp1", "d", "somefile.db", "old"))
        self.assertEqual(self.globalDb.countProfiles(), 2)
        self.assertEqual(self.globalDb.getDefaultProfile(), "default")
        self.assertEqual(self.globalDb.getProfileOrder(), ["default", "temp1"])

        output = {
            "name": "temp1",
            "description": "d",
            "databasefile": "somefile.db",
            "oldCfg": "old",
            "isDefault": 0,
            "ord": 100,
        }
        self.assertEqual(dict(self.globalDb.getProfile("temp1")), output)
        self.assertTrue(
            self.globalDb.updateProfileField("temp1", "description", "desc")
        )
        output["description"] = "desc"
        self.assertEqual(dict(self.globalDb.getProfile("temp1")), output)
        self.assertTrue(
            self.globalDb.updateProfileField(
                "somefile.db", "name", "temp", "databasefile"
            )
        )
        output["name"] = "temp"

        self.assertEqual(dict(self.globalDb.getProfile("temp")), output)
        self.assertEqual(dict(self.globalDb.getProfile(filename="somefile.db")), output)
        self.assertEqual(dict(self.globalDb.getProfile()), {})
        self.assertEqual(dict(self.globalDb.getProfile("temp", "somefile.db")), {})

        self.assertFalse(
            self.globalDb.updateProfileField("tmp", "name", "temp", "name")
        )
        self.assertFalse(
            self.globalDb.updateProfileField("tmp", "databasefile", "temp", "isDefault")
        )
        self.assertFalse(
            self.globalDb.updateProfileField("tmp", "name", "temp", "isDefault")
        )
        self.assertFalse(self.globalDb.updateProfileField("tmp", "name1", "temp"))

        self.assertTrue(
            self.globalDb.updateProfileField(
                1, "description", "newsomething", "isDefault"
            )
        )
        output["name"] = "temp"
        self.assertEqual(dict(self.globalDb.getProfile("temp")), output)

        output = [dict(e) for e in self.globalDb.getProfiles()]
        self.assertEqual(
            output,
            [
                {
                    "name": u"default",
                    "description": u"newsomething",
                    "databasefile": str(
                        configuration_params["mainDatabaseName"]
                        .default.replace("PBDATA", "")
                        .replace(pbConfig.dataPath, "")
                    ),
                    "oldCfg": u"",
                    "isDefault": 1,
                    "ord": 100,
                },
                {
                    "name": u"temp",
                    "description": u"desc",
                    "databasefile": u"somefile.db",
                    "oldCfg": u"old",
                    "isDefault": 0,
                    "ord": 100,
                },
            ],
        )

        self.assertEqual(self.globalDb.getProfileOrder(), ["default", "temp"])
        self.assertTrue(
            self.globalDb.updateProfileField(
                "somefile.db", "name", "abc", "databasefile"
            )
        )
        self.assertEqual(self.globalDb.getProfileOrder(), ["abc", "default"])
        self.assertTrue(self.globalDb.setProfileOrder(["default", "abc"]))
        self.assertEqual(self.globalDb.getProfileOrder(), ["default", "abc"])
        with patch("logging.Logger.warning") as _w:
            self.assertFalse(self.globalDb.setProfileOrder())
            _w.assert_called_once_with("No order given!")
        with patch("logging.Logger.warning") as _w:
            self.assertFalse(self.globalDb.setProfileOrder(["default", "temp"]))
            _w.assert_called_once_with(
                "List of profile names does not match existing profiles!"
            )
        with patch(
            "physbiblio.databaseCore.PhysBiblioDBCore.connExec",
            side_effect=[True, False, True, False],
            autospec=True,
        ) as _mock, patch("logging.Logger.error") as _e:
            self.assertFalse(self.globalDb.setProfileOrder(["abc", "default"]))
            _e.assert_called_once_with(
                "Something went wrong when setting new profile order. Undoing..."
            )

        self.assertEqual(self.globalDb.getDefaultProfile(), "default")
        self.assertTrue(self.globalDb.setDefaultProfile("abc"))
        self.assertEqual(self.globalDb.getDefaultProfile(), "abc")
        with patch("logging.Logger.warning") as _w:
            self.assertFalse(self.globalDb.setDefaultProfile())
            _w.assert_called_once_with("No name given!")
        with patch("logging.Logger.warning") as _w:
            self.assertFalse(self.globalDb.setDefaultProfile("temp"))
            _w.assert_called_once_with("No profiles with the given name!")
        with patch(
            "physbiblio.databaseCore.PhysBiblioDBCore.connExec",
            side_effect=[True, False, True, False],
            autospec=True,
        ) as _mock, patch("logging.Logger.error") as _w:
            self.assertFalse(self.globalDb.setDefaultProfile("abc"))
            _w.assert_called_once_with(
                "Something went wrong when setting new default profile. " + "Undoing..."
            )
        self.assertEqual(self.globalDb.getDefaultProfile(), "abc")

        self.assertFalse(self.globalDb.deleteProfile(""))
        self.assertTrue(self.globalDb.deleteProfile("temp1"))
        self.assertEqual(self.globalDb.countProfiles(), 2)
        self.assertTrue(self.globalDb.deleteProfile("abc"))
        self.assertEqual(self.globalDb.countProfiles(), 1)
        self.assertEqual(self.globalDb.getDefaultProfile(), "default")


@patch("logging.Logger.debug")
@patch("logging.Logger.info")
@patch("logging.Logger.warning")
@patch("logging.Logger.error")
@patch("logging.Logger.exception")
class TestGlobalDB(unittest.TestCase):
    """Test GlobalDB"""

    @classmethod
    def setUpClass(self):
        """Create a GlobalDB instance for saving time"""
        if os.path.exists(tempProfName):
            os.remove(tempProfName)
        self.globalDb = GlobalDB(
            tempProfName, pbConfig.logger, pbConfig.dataPath, info=False
        )

    def setUp(self):
        """overwrite curs"""
        self.origcurs = self.globalDb.curs
        self.globalDb.curs = MagicMock()

    def tearDown(self):
        """restore curs"""
        self.globalDb.curs = self.origcurs

    def test_init(self, *args):
        """test __init__"""
        if os.path.exists(tempProfName):
            os.remove(tempProfName)
        with patch(
            "physbiblio.databaseCore.PhysBiblioDBCore.openDB", autospec=True
        ) as _op, patch(
            "physbiblio.config.GlobalDB.cursExec", autospec=True
        ) as _ce, self.assertRaises(
            TypeError
        ):
            globalDb = GlobalDB(
                tempProfName, pbConfig.logger, pbConfig.dataPath, info="i"
            )
            _op.assert_called_once_with(globalDb, info="i")
            _ce.assert_called_once_with(
                globalDb, "SELECT name FROM sqlite_master WHERE type='table';"
            )
        with patch(
            "physbiblio.config.GlobalDB.createTables", autospec=True
        ) as _ct, patch(
            "physbiblio.config.GlobalDB.countProfiles", return_value=0, autospec=True
        ) as _co, patch(
            "physbiblio.config.GlobalDB.createProfile", autospec=True
        ) as _cp:
            globalDb = GlobalDB(
                tempProfName, pbConfig.logger, pbConfig.dataPath, info="i"
            )
            _ct.assert_called_once_with(globalDb, [])
            _co.assert_called_once_with(globalDb)
            _cp.assert_called_once_with(globalDb)
        globalDb = GlobalDB(tempProfName, pbConfig.logger, pbConfig.dataPath, info="i")
        with patch(
            "physbiblio.config.GlobalDB.createTables", autospec=True
        ) as _ct, patch(
            "physbiblio.config.GlobalDB.countProfiles", return_value=1, autospec=True
        ) as _co, patch(
            "physbiblio.config.GlobalDB.createProfile", autospec=True
        ) as _cp:
            globalDb = GlobalDB(
                tempProfName, pbConfig.logger, pbConfig.dataPath, info="i"
            )
            self.assertEqual(_ct.call_count, 0)
            _co.assert_called_once_with(globalDb)
            self.assertEqual(_cp.call_count, 0)
        self.assertIsInstance(globalDb, PhysBiblioDBCore)
        self.assertIsInstance(globalDb.config, ConfigurationDB)
        self.assertEqual(globalDb.dataPath, pbConfig.dataPath)

    def test_createTables(self, *args):
        """test createTables"""
        with patch("physbiblio.config.GlobalDB.createTable", autospec=True) as _ct:
            self.globalDb.createTables(["profiles", "searches"])
            _ct.assert_called_once_with(
                self.globalDb, "settings", tableFields["settings"], critical=True
            )
            self.globalDb.createTables(["profiles", "settings"])
            _ct.assert_any_call(self.globalDb, "searches", searchesTable, critical=True)
            self.globalDb.createTables(["searches", "settings"])
            _ct.assert_any_call(
                self.globalDb, "profiles", profilesSettingsTable, critical=True
            )

    def test_countProfiles(self, *args):
        """test countProfiles"""
        self.globalDb.curs.fetchall = MagicMock(return_value=[[12]])
        with patch("physbiblio.config.GlobalDB.cursExec", autospec=True) as _ct:
            self.assertEqual(self.globalDb.countProfiles(), 12)
            _ct.assert_called_once_with(self.globalDb, "SELECT Count(*) FROM profiles")

    def test_createProfile(self, *args):
        """test createProfile"""
        cmd = (
            "INSERT into profiles "
            + "(name, description, databasefile, oldCfg, isDefault, ord) "
            + "values (:name, :description, :databasefile, "
            + ":oldCfg, :isDefault, :ord)"
        )
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.exception"
        ) as _ex, patch("sys.exit") as _se, patch(
            "physbiblio.config.GlobalDB.connExec",
            side_effect=[True, False],
            autospec=True,
        ) as _ce, patch(
            "physbiblio.config.GlobalDB.commit", autospec=True
        ) as _co, patch(
            "physbiblio.config.GlobalDB.countProfiles", side_effect=[0, 1]
        ) as _cp:
            self.globalDb.createProfile()
            data = {
                "name": "default",
                "description": "",
                "databasefile": (
                    configuration_params["mainDatabaseName"].default.replace(
                        "PBDATA", ""
                    ),
                ),
                "oldCfg": "",
                "isDefault": 1,
                "ord": 100,
            }
            _i.assert_called_once()
            _co.assert_called_once_with(self.globalDb, verbose=False)
            self.globalDb.createProfile(
                name="test",
                description="a test",
                databasefile="somefilename",
                oldCfg="what",
            )
            data = {
                "name": "test",
                "description": "a test",
                "databasefile": "somefilename",
                "oldCfg": "what",
                "isDefault": 0,
                "ord": 100,
            }
            _ce.assert_any_call(self.globalDb, cmd, data)
            _ex.assert_called_once_with("Cannot insert profile")
            _se.assert_called_once_with(1)

    def test_updateProfileField(self, *args):
        """test updateProfileField"""
        with patch("logging.Logger.error") as _e:
            self.assertFalse(
                self.globalDb.updateProfileField(1, "databasefile", "new", "a")
            )
            _e.assert_called_once_with(
                "Invalid field or identifierField: %s, %s" % ("databasefile", "a")
            )
            self.assertFalse(self.globalDb.updateProfileField(1, "name", "new"))
            _e.assert_any_call(
                "Invalid field or identifierField: %s, %s" % ("name", "name")
            )
            self.assertFalse(
                self.globalDb.updateProfileField(0, "name", "new", "isDefault")
            )
            _e.assert_any_call(
                "Invalid field or identifierField: %s, %s" % ("name", "isDefault")
            )
            self.assertFalse(
                self.globalDb.updateProfileField(
                    1, "name", "new", identifierField="abc"
                )
            )
            _e.assert_any_call(
                "Invalid field or identifierField: %s, %s" % ("name", "abc")
            )
            self.assertFalse(self.globalDb.updateProfileField(1, "abc", "new"))
            _e.assert_any_call(
                "Invalid field or identifierField: %s, %s" % ("abc", "name")
            )
        with patch("logging.Logger.debug") as _d, patch(
            "logging.Logger.error"
        ) as _e, patch(
            "physbiblio.config.GlobalDB.connExec",
            side_effect=[False, True],
            autospec=True,
        ) as _ce, patch(
            "physbiblio.config.GlobalDB.commit", autospec=True
        ) as _co:
            self.assertFalse(self.globalDb.updateProfileField(1, "databasefile", "new"))
            _d.assert_called_once()
            _e.assert_called_once_with("Cannot update profile")
            _ce.assert_called_once_with(
                self.globalDb,
                "update profiles set %s = :val " % "databasefile"
                + " where %s = :iden\n" % "name",
                data={"val": "new", "iden": 1},
            )
            self.assertEqual(_co.call_count, 0)
            self.assertTrue(self.globalDb.updateProfileField(1, "databasefile", "new"))
            _co.assert_called_once_with(self.globalDb, verbose=False)

    def test_deleteProfile(self, *args):
        """test deleteProfile"""
        with patch("logging.Logger.error") as _e:
            self.assertFalse(self.globalDb.deleteProfile(""))
            _e.assert_called_once_with("You must provide the profile name!")
        with patch("logging.Logger.debug") as _d, patch(
            "logging.Logger.error"
        ) as _e, patch(
            "physbiblio.config.GlobalDB.connExec",
            side_effect=[False, True, True],
            autospec=True,
        ) as _ce, patch(
            "physbiblio.config.GlobalDB.getDefaultProfile",
            autospec=True,
            side_effect=["a", "a", "a", "b"],
        ) as _gd, patch(
            "physbiblio.config.GlobalDB.commit", autospec=True
        ) as _co:
            self.assertFalse(self.globalDb.deleteProfile("a"))
            _d.assert_called_once()
            _e.assert_called_once_with("Cannot delete profile")
            _ce.assert_called_once_with(
                self.globalDb,
                "delete from profiles where name = :name\n",
                {"name": "a"},
            )
            self.assertEqual(_co.call_count, 0)
            _gd.assert_called_once_with(self.globalDb)
            self.assertTrue(self.globalDb.deleteProfile("a"))
            _co.assert_called_once_with(self.globalDb, verbose=False)
            self.assertEqual(_gd.call_count, 3)
            self.assertTrue(self.globalDb.deleteProfile("a"))
            self.assertEqual(_gd.call_count, 4)

    def test_getProfiles(self, *args):
        """test getProfiles"""
        self.globalDb.curs.fetchall = MagicMock(return_value=[[12]])
        with patch("physbiblio.config.GlobalDB.cursExec", autospec=True) as _ct:
            self.assertEqual(self.globalDb.getProfiles(), [[12]])
            _ct.assert_called_once_with(
                self.globalDb, "SELECT * FROM profiles order by ord ASC, name ASC\n"
            )

    def test_getProfile(self, *args):
        """test getProfile"""
        with patch("logging.Logger.warning") as _w:
            self.assertEqual(self.globalDb.getProfile(), {})
            _w.assert_called_once_with(
                "You should specify the name or the filename"
                + " associated with the profile"
            )
            self.assertEqual(self.globalDb.getProfile("a", "b"), {})
            _w.assert_any_call(
                "You should specify only the name "
                + "or only the filename associated with the profile"
            )
        self.globalDb.curs.fetchall = MagicMock(return_value=[[12]])
        with patch("physbiblio.config.GlobalDB.cursExec", autospec=True) as _ct:
            self.assertEqual(self.globalDb.getProfile(name="a"), [12])
            _ct.assert_called_once_with(
                self.globalDb,
                "SELECT * FROM profiles WHERE name = :name or databasefile = :file\n",
                {"name": "a", "file": ""},
            )
            self.assertEqual(self.globalDb.getProfile(filename="a"), [12])
            _ct.assert_any_call(
                self.globalDb,
                "SELECT * FROM profiles WHERE name = :name or databasefile = :file\n",
                {"name": "", "file": "a"},
            )

    def test_getProfileOrder(self, *args):
        """test getProfileOrder"""
        self.globalDb.curs.fetchall = MagicMock(
            return_value=[{"name": "a"}, {"name": "b"}]
        )
        with patch("physbiblio.config.GlobalDB.cursExec", autospec=True) as _ct, patch(
            "physbiblio.config.GlobalDB.countProfiles",
            autospec=True,
            side_effect=[1, 0],
        ) as _co, patch(
            "physbiblio.config.GlobalDB.createProfile", autospec=True
        ) as _cp, patch(
            "physbiblio.config.GlobalDB.setDefaultProfile", autospec=True
        ) as _se:
            self.assertEqual(self.globalDb.getProfileOrder(), ["a", "b"])
            _ct.assert_called_once_with(
                self.globalDb, "SELECT * FROM profiles order by ord ASC, name ASC\n"
            )
            _co.assert_called_once_with(self.globalDb)
            self.assertEqual(_cp.call_count, 0)
            self.assertEqual(_se.call_count, 0)
            self.assertEqual(self.globalDb.getProfileOrder(), ["a", "b"])
            _cp.assert_called_once_with(self.globalDb)
            _se.assert_called_once_with(self.globalDb, "default")

    def test_setProfileOrder(self, *args):
        """test setProfileOrder"""
        with patch("logging.Logger.warning") as _w:
            self.assertFalse(self.globalDb.setProfileOrder())
            _w.assert_called_once_with("No order given!")
        with patch("logging.Logger.warning") as _w, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "physbiblio.config.GlobalDB.getProfiles",
            autospec=True,
            return_value=[{"name": "a"}, {"name": "b"}, {"name": "c"}],
        ) as _gp:
            self.assertFalse(self.globalDb.setProfileOrder(["b", "a"]))
            _i.assert_any_call(["a", "b"])
            _i.assert_any_call(["a", "b", "c"])
            _gp.assert_any_call(self.globalDb)
            _w.assert_called_once_with(
                "List of profile names does not match existing profiles!"
            )
        with patch("logging.Logger.error") as _e, patch(
            "physbiblio.config.GlobalDB.getProfiles",
            autospec=True,
            return_value=[{"name": "a"}, {"name": "b"}, {"name": "c"}],
        ) as _gp, patch(
            "physbiblio.config.GlobalDB.connExec",
            autospec=True,
            side_effect=[True, True, False],
        ) as _ce, patch(
            "physbiblio.config.GlobalDB.undo", autospec=True
        ) as _u, patch(
            "physbiblio.config.GlobalDB.commit", autospec=True
        ) as _co:
            self.assertFalse(self.globalDb.setProfileOrder(["b", "a", "c"]))
            _ce.assert_has_calls(
                [
                    call(
                        self.globalDb,
                        "update profiles set ord=:ord where name=:name\n",
                        {"name": "b", "ord": 0},
                    ),
                    call(
                        self.globalDb,
                        "update profiles set ord=:ord where name=:name\n",
                        {"name": "a", "ord": 1},
                    ),
                    call(
                        self.globalDb,
                        "update profiles set ord=:ord where name=:name\n",
                        {"name": "c", "ord": 2},
                    ),
                ]
            )
            _e.assert_called_once_with(
                "Something went wrong when setting new profile order. Undoing..."
            )
            _u.assert_called_once_with(self.globalDb, verbose=False)
            self.assertEqual(_co.call_count, 0)
        with patch("logging.Logger.error") as _e, patch(
            "physbiblio.config.GlobalDB.getProfiles",
            autospec=True,
            return_value=[{"name": "a"}, {"name": "b"}, {"name": "c"}],
        ) as _gp, patch(
            "physbiblio.config.GlobalDB.connExec", autospec=True, return_value=True
        ) as _ce, patch(
            "physbiblio.config.GlobalDB.undo", autospec=True
        ) as _u, patch(
            "physbiblio.config.GlobalDB.commit", autospec=True
        ) as _co:
            self.assertTrue(self.globalDb.setProfileOrder(order=["b", "a", "c"]))
            _ce.assert_has_calls(
                [
                    call(
                        self.globalDb,
                        "update profiles set ord=:ord where name=:name\n",
                        {"name": "b", "ord": 0},
                    ),
                    call(
                        self.globalDb,
                        "update profiles set ord=:ord where name=:name\n",
                        {"name": "a", "ord": 1},
                    ),
                    call(
                        self.globalDb,
                        "update profiles set ord=:ord where name=:name\n",
                        {"name": "c", "ord": 2},
                    ),
                ]
            )
            _co.assert_called_once_with(self.globalDb, verbose=False)
            self.assertEqual(_e.call_count, 0)
            self.assertEqual(_u.call_count, 0)

    def test_getDefaultProfile(self, *args):
        """test getDefaultProfile"""
        self.globalDb.curs.fetchall = MagicMock(
            return_value=[{"name": "b"}, {"name": "a"}]
        )
        with patch("physbiblio.config.GlobalDB.cursExec", autospec=True) as _ct, patch(
            "physbiblio.config.GlobalDB.countProfiles", autospec=True, return_value=1
        ) as _co, patch(
            "physbiblio.config.GlobalDB.createProfile", autospec=True
        ) as _cp, patch(
            "physbiblio.config.GlobalDB.setDefaultProfile", autospec=True
        ) as _se:
            self.assertEqual(self.globalDb.getDefaultProfile(), "b")
            _ct.assert_called_once_with(
                self.globalDb, "SELECT * FROM profiles WHERE isDefault = 1\n"
            )
            _co.assert_called_once_with(self.globalDb)
            self.assertEqual(_cp.call_count, 0)
            self.assertEqual(_se.call_count, 0)
        self.globalDb.curs.fetchall = MagicMock(side_effect=[[], [{"name": "c"}]])
        with patch("physbiblio.config.GlobalDB.cursExec", autospec=True) as _ct, patch(
            "physbiblio.config.GlobalDB.countProfiles", autospec=True, return_value=0
        ) as _co, patch(
            "physbiblio.config.GlobalDB.createProfile", autospec=True
        ) as _cp, patch(
            "physbiblio.config.GlobalDB.setDefaultProfile",
            autospec=True,
            return_value=True,
        ) as _se, patch(
            "logging.Logger.info"
        ) as _i:
            self.assertEqual(self.globalDb.getDefaultProfile(), "c")
            _ct.assert_any_call(self.globalDb, "SELECT * FROM profiles\n")
            _cp.assert_called_once_with(self.globalDb)
            _se.assert_any_call(self.globalDb, "default")
            _se.assert_any_call(self.globalDb, "c")
            _i.assert_called_once_with("Default profile changed to %s" % "c")

    def test_setDefaultProfile(self, *args):
        """test setDefaultProfile"""
        with patch("logging.Logger.warning") as _w:
            self.assertFalse(self.globalDb.setDefaultProfile())
            _w.assert_called_once_with("No name given!")
        self.globalDb.curs.fetchall = MagicMock(return_value=[])
        with patch("logging.Logger.warning") as _w, patch(
            "physbiblio.config.GlobalDB.cursExec", autospec=True
        ) as _ce:
            self.assertFalse(self.globalDb.setDefaultProfile("a"))
            _ce.assert_called_once_with(
                self.globalDb,
                "SELECT * FROM profiles WHERE name = :name\n",
                {"name": "a"},
            )
            _w.assert_called_once_with("No profiles with the given name!")
        self.globalDb.curs.fetchall = MagicMock(return_value=[1])
        with patch("logging.Logger.error") as _e, patch(
            "physbiblio.config.GlobalDB.cursExec", autospec=True
        ) as _cu, patch(
            "physbiblio.config.GlobalDB.connExec",
            autospec=True,
            side_effect=[True, True, True, False, False, True],
        ) as _ce, patch(
            "physbiblio.config.GlobalDB.undo", autospec=True
        ) as _u, patch(
            "physbiblio.config.GlobalDB.commit", autospec=True
        ) as _co:
            self.assertTrue(self.globalDb.setDefaultProfile(name="a"))
            _co.assert_called_once_with(self.globalDb, verbose=False)
            _cu.assert_called_once_with(
                self.globalDb,
                "SELECT * FROM profiles WHERE name = :name\n",
                {"name": "a"},
            )
            _ce.assert_any_call(
                self.globalDb, "update profiles set isDefault=0 where 1\n"
            )
            _ce.assert_any_call(
                self.globalDb,
                "update profiles set isDefault=1 where name = :name\n",
                {"name": "a"},
            )
            self.assertEqual(_e.call_count, 0)
            self.assertEqual(_u.call_count, 0)
            self.assertFalse(self.globalDb.setDefaultProfile("a"))
            _e.assert_called_once_with(
                "Something went wrong when setting new default profile." + " Undoing..."
            )
            _u.assert_called_once_with(self.globalDb, verbose=False)
            self.assertFalse(self.globalDb.setDefaultProfile("a"))
            self.assertEqual(_e.call_count, 2)
            self.assertEqual(_u.call_count, 2)

    def test_countSearches(self, *args):
        """test countSearches"""
        self.globalDb.curs.fetchall = MagicMock(return_value=[[12]])
        with patch("physbiblio.config.GlobalDB.cursExec", autospec=True) as _ct:
            self.assertEqual(self.globalDb.countSearches(), 12)
            _ct.assert_called_once_with(self.globalDb, "SELECT Count(*) FROM searches")

    def test_insertSearch(self, *args):
        """test insertSearch"""
        with patch(
            "physbiblio.config.GlobalDB.connExec",
            autospec=True,
            side_effect=[True, False],
        ) as _ce, patch("physbiblio.config.GlobalDB.commit", autospec=True) as _co:
            self.assertTrue(self.globalDb.insertSearch(replacement=True))
            _ce.assert_called_once_with(
                self.globalDb,
                "INSERT into searches "
                + "(name, count, searchDict, limitNum, offsetNum, replaceFields,"
                + " manual, isReplace) values (:name, :count, :searchFields,"
                + " :limit, :offset, :replaceFields, :manual, :isReplace)\n",
                {
                    "name": "",
                    "count": 0,
                    "searchFields": "%s" % [],
                    "limit": pbConfig.params["defaultLimitBibtexs"],
                    "offset": 0,
                    "replaceFields": "%s" % [],
                    "manual": 0,
                    "isReplace": 1,
                },
            )
            _co.assert_called_once_with(self.globalDb)
            self.assertFalse(
                self.globalDb.insertSearch(
                    name="myname",
                    count=12,
                    searchFields=["a"],
                    replaceFields=["b"],
                    manual=True,
                    replacement=False,
                    limit=34,
                    offset=56,
                )
            )
            _ce.assert_any_call(
                self.globalDb,
                "INSERT into searches "
                + "(name, count, searchDict, limitNum, offsetNum, replaceFields,"
                + " manual, isReplace) values (:name, :count, :searchFields,"
                + " :limit, :offset, :replaceFields, :manual, :isReplace)\n",
                {
                    "name": "myname",
                    "count": 12,
                    "searchFields": "%s" % ["a"],
                    "limit": 34,
                    "offset": 56,
                    "replaceFields": "%s" % ["b"],
                    "manual": 1,
                    "isReplace": 0,
                },
            )

    def test_deleteSearch(self, *args):
        """test deleteSearch"""
        with patch(
            "physbiblio.config.GlobalDB.cursExec", autospec=True, return_value="abcd"
        ) as _ct, patch("physbiblio.config.GlobalDB.commit", autospec=True) as _co:
            self.assertEqual(self.globalDb.deleteSearch(123), "abcd")
            _ct.assert_called_once_with(
                self.globalDb, "delete from searches where idS=?\n", (123,)
            )
            _co.assert_called_once_with(self.globalDb)

    def test_getAllSearches(self, *args):
        """test getAllSearches"""
        self.globalDb.curs.fetchall = MagicMock(return_value=[[12]])
        with patch("physbiblio.config.GlobalDB.cursExec", autospec=True) as _ct:
            self.assertEqual(self.globalDb.getAllSearches(), [[12]])
            _ct.assert_called_once_with(
                self.globalDb, "select * from searches order by count asc\n"
            )

    def test_getSearchByID(self, *args):
        """test getSearchByID"""
        self.globalDb.curs.fetchall = MagicMock(return_value=[[12]])
        with patch("physbiblio.config.GlobalDB.cursExec", autospec=True) as _ct:
            self.assertEqual(self.globalDb.getSearchByID(123), [[12]])
            _ct.assert_called_once_with(
                self.globalDb, "select * from searches where idS=?\n", (123,)
            )

    def test_getSearchByName(self, *args):
        """test getSearchByName"""
        self.globalDb.curs.fetchall = MagicMock(return_value=[[12]])
        with patch("physbiblio.config.GlobalDB.cursExec", autospec=True) as _ct:
            self.assertEqual(self.globalDb.getSearchByName("abc"), [[12]])
            _ct.assert_called_once_with(
                self.globalDb, "select * from searches where name=?\n", ("abc",)
            )

    def test_getSearchList(self, *args):
        """test getSearchList"""
        self.globalDb.curs.fetchall = MagicMock(return_value=[[12]])
        with patch("physbiblio.config.GlobalDB.cursExec", autospec=True) as _ct:
            self.assertEqual(self.globalDb.getSearchList(True, True), [[12]])
            _ct.assert_called_once_with(
                self.globalDb,
                "select * from searches where manual=? "
                + "and isReplace=? order by count ASC\n",
                (1, 1),
            )
            _ct.reset_mock()
            self.assertEqual(self.globalDb.getSearchList(True, False), [[12]])
            _ct.assert_called_once_with(
                self.globalDb,
                "select * from searches where manual=? "
                + "and isReplace=? order by count ASC\n",
                (1, 0),
            )
            _ct.reset_mock()
            self.assertEqual(
                self.globalDb.getSearchList(manual=False, replacement=False), [[12]]
            )
            _ct.assert_called_once_with(
                self.globalDb,
                "select * from searches where manual=? "
                + "and isReplace=? order by count ASC\n",
                (0, 0),
            )

    def test_updateSearchOrder(self, *args):
        """test updateSearchOrder"""
        self.globalDb.curs.fetchall = MagicMock(
            return_value=[
                {"idS": 14, "count": 3},
                {"idS": 11, "count": 0},
                {"idS": 12, "count": 1},
                {"idS": 13, "count": 2},
            ]
        )
        with patch.dict(pbConfig.params, {"maxSavedSearches": 3}, clear=False), patch(
            "physbiblio.config.GlobalDB.cursExec", autospec=True
        ) as _ct, patch(
            "physbiblio.config.GlobalDB.connExec", autospec=True, return_value=True
        ) as _ce, patch(
            "physbiblio.config.GlobalDB.commit", autospec=True
        ) as _co, patch(
            "physbiblio.config.GlobalDB.undo", autospec=True
        ) as _u, patch(
            "physbiblio.config.GlobalDB.deleteSearch", autospec=True
        ) as _d:
            self.assertTrue(self.globalDb.updateSearchOrder())
            _ct.assert_called_once_with(
                self.globalDb,
                "select * from searches where manual=? and isReplace=?\n",
                (0, 0),
            )
            _co.assert_called_once_with(self.globalDb)
            self.assertEqual(_u.call_count, 0)
            self.assertEqual(_ce.call_count, 2)
            _ce.assert_any_call(
                self.globalDb,
                "update searches set count = :count where idS=:idS\n",
                {"idS": 11, "count": 1},
            )
            _ce.assert_any_call(
                self.globalDb,
                "update searches set count = :count where idS=:idS\n",
                {"idS": 12, "count": 2},
            )
            self.assertEqual(_d.call_count, 2)
            _d.assert_any_call(self.globalDb, 13)
            _d.assert_any_call(self.globalDb, 14)
        with patch.dict(pbConfig.params, {"maxSavedSearches": 3}, clear=False), patch(
            "physbiblio.config.GlobalDB.cursExec", autospec=True
        ) as _ct, patch(
            "physbiblio.config.GlobalDB.connExec", autospec=True, return_value=False
        ) as _ce, patch(
            "physbiblio.config.GlobalDB.commit", autospec=True
        ) as _co, patch(
            "physbiblio.config.GlobalDB.undo", autospec=True
        ) as _u, patch(
            "physbiblio.config.GlobalDB.deleteSearch", autospec=True
        ) as _d:
            self.assertFalse(self.globalDb.updateSearchOrder(replacement=True))
            _ct.assert_called_once_with(
                self.globalDb,
                "select * from searches where manual=? and isReplace=?\n",
                (0, 1),
            )
            _u.assert_called_once_with(self.globalDb)
            self.assertEqual(_co.call_count, 0)
            _ce.assert_called_once_with(
                self.globalDb,
                "update searches set count = :count where idS=:idS\n",
                {"idS": 11, "count": 1},
            )
            _d.assert_called_once_with(self.globalDb, 14)

    def test_updateSearchField(self, *args):
        """test updateSearchField"""
        with patch("logging.Logger.warning") as _w:
            self.assertFalse(self.globalDb.updateSearchField(1, "test", "abc"))
            _w.assert_called_once_with(
                "Empty value or field not in the following list: "
                + "[searchDict, replaceFields, name, limitNum, offsetNum]"
                + ".\nField: test, value: abc"
            )
            self.assertFalse(self.globalDb.updateSearchField(1, "name", ""))
            self.assertEqual(_w.call_count, 2)
            self.assertFalse(self.globalDb.updateSearchField(1, "name", " "))
            self.assertEqual(_w.call_count, 3)
            self.assertFalse(self.globalDb.updateSearchField(1, "name", None))
            self.assertEqual(_w.call_count, 4)
            self.assertFalse(self.globalDb.updateSearchField(1, "name", []))
            self.assertEqual(_w.call_count, 5)
            self.assertFalse(self.globalDb.updateSearchField(1, "name", {}))
            self.assertEqual(_w.call_count, 6)
        with patch(
            "physbiblio.config.GlobalDB.connExec", autospec=True, return_value="r"
        ) as _ce:
            self.assertEqual(self.globalDb.updateSearchField(1, "name", "abc"), "r")
            _ce.assert_called_once_with(
                self.globalDb,
                "update searches set name=:field where idS=:idS\n",
                {"field": "abc", "idS": 1},
            )


@unittest.skipIf(skipTestsSettings.db, "Database tests")
@patch("logging.Logger.debug")
@patch("logging.Logger.info")
@patch("logging.Logger.warning")
@patch("logging.Logger.error")
@patch("logging.Logger.exception")
class TestConfigurationDBOperations(DBTestCase):
    """Test ConfigurationDB"""

    def test_operations(self, *args):
        """Test count, insert and update, delete and get methods"""
        self.assertIsInstance(self.pBDB.config, ConfigurationDB)
        self.assertIsInstance(self.pBDB.config, PhysBiblioDBSub)
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
            ["test2", "somevalue"],
        ]:
            self.assertEqual(self.pBDB.config.getByName(n)[0]["value"], v)
        self.assertEqual(
            {e["name"]: e["value"] for e in self.pBDB.config.getAll()},
            {"test": "somevalue1", "test1": "somevalueA", "test2": "somevalue"},
        )
        self.assertTrue(self.pBDB.config.delete("test3"))
        self.assertEqual(self.pBDB.config.count(), 3)
        self.assertTrue(self.pBDB.config.delete("test2"))
        self.assertEqual(self.pBDB.config.count(), 2)
        if os.path.exists(tempDBName):
            os.remove(tempDBName)


@unittest.skipIf(skipTestsSettings.db, "Database tests")
@patch("logging.Logger.debug")
@patch("logging.Logger.info")
@patch("logging.Logger.warning")
@patch("logging.Logger.error")
@patch("logging.Logger.exception")
class TestConfigurationDB(DBTestCase):
    """Test ConfigurationDB"""

    def setUp(self):
        """overwrite curs"""
        self.origcurs = self.pBDB.config.curs
        self.pBDB.config.curs = MagicMock()

    def tearDown(self):
        """restore curs"""
        self.pBDB.config.curs = self.origcurs

    def test_count(self, *args):
        """test count"""
        self.pBDB.config.curs.fetchall = MagicMock(return_value=[[12]])
        with patch(
            "physbiblio.databaseCore.PhysBiblioDBSub.cursExec", autospec=True
        ) as _ce:
            self.assertEqual(self.pBDB.config.count(), 12)
            _ce.assert_called_once_with(
                self.pBDB.config, "SELECT Count(*) FROM settings"
            )

    def test_insert(self, *args):
        """test insert"""
        self.pBDB.config.curs.fetchall = MagicMock(return_value=[[12]])
        with patch(
            "physbiblio.databaseCore.PhysBiblioDBSub.cursExec", autospec=True
        ) as _cu, patch("logging.Logger.info") as _i, patch(
            "physbiblio.config.ConfigurationDB.update", return_value="u", autospec=True
        ) as _u:
            self.assertEqual(self.pBDB.config.insert("abc", "def"), "u")
            _cu.assert_called_once_with(
                self.pBDB.config, "select * from settings where name=?\n", ("abc",)
            )
            _i.assert_called_once_with(
                "An entry with the same name is already present. Updating it"
            )
            _u.assert_called_once_with(self.pBDB.config, "abc", "def")
        self.pBDB.config.curs.fetchall = MagicMock(return_value=[])
        with patch(
            "physbiblio.databaseCore.PhysBiblioDBSub.cursExec", autospec=True
        ) as _cu, patch("logging.Logger.info") as _i, patch(
            "physbiblio.databaseCore.PhysBiblioDBSub.connExec",
            return_value="u",
            autospec=True,
        ) as _co:
            self.assertEqual(self.pBDB.config.insert("abc", "def"), "u")
            _cu.assert_called_once_with(
                self.pBDB.config, "select * from settings where name=?\n", ("abc",)
            )
            self.assertEqual(_i.call_count, 0)
            _co.assert_called_once_with(
                self.pBDB.config,
                "INSERT into settings (name, value) values (:name, :value)\n",
                {"name": "abc", "value": "def"},
            )

    def test_update(self, *args):
        """test update"""
        self.pBDB.config.curs.fetchall = MagicMock(return_value=[])
        with patch(
            "physbiblio.databaseCore.PhysBiblioDBSub.cursExec", autospec=True
        ) as _cu, patch("logging.Logger.info") as _i, patch(
            "physbiblio.config.ConfigurationDB.insert", return_value="i", autospec=True
        ) as _u:
            self.assertEqual(self.pBDB.config.update("abc", "def"), "i")
            _cu.assert_called_once_with(
                self.pBDB.config, "select * from settings where name=?\n", ("abc",)
            )
            _i.assert_called_once_with(
                "No settings found with this name (abc). Inserting it."
            )
            _u.assert_called_once_with(self.pBDB.config, "abc", "def")
        self.pBDB.config.curs.fetchall = MagicMock(return_value=[[12]])
        with patch(
            "physbiblio.databaseCore.PhysBiblioDBSub.cursExec", autospec=True
        ) as _cu, patch("logging.Logger.info") as _i, patch(
            "physbiblio.databaseCore.PhysBiblioDBSub.connExec",
            return_value="i",
            autospec=True,
        ) as _co:
            self.assertEqual(self.pBDB.config.update("abc", "def"), "i")
            _cu.assert_called_once_with(
                self.pBDB.config, "select * from settings where name=?\n", ("abc",)
            )
            self.assertEqual(_i.call_count, 0)
            _co.assert_called_once_with(
                self.pBDB.config,
                "update settings set value = :value where name = :name\n",
                {"name": "abc", "value": "def"},
            )

    def test_delete(self, *args):
        """test delete"""
        with patch(
            "physbiblio.databaseCore.PhysBiblioDBSub.cursExec",
            autospec=True,
            return_value="u",
        ) as _cu:
            self.assertEqual(self.pBDB.config.delete("abc"), "u")
            _cu.assert_called_once_with(
                self.pBDB.config, "delete from settings where name=?\n", ("abc",)
            )

    def test_getAll(self, *args):
        """test getAll"""
        self.pBDB.config.curs.fetchall = MagicMock(return_value=[[12]])
        with patch(
            "physbiblio.databaseCore.PhysBiblioDBSub.cursExec", autospec=True
        ) as _cu:
            self.assertEqual(self.pBDB.config.getAll(), [[12]])
            _cu.assert_called_once_with(self.pBDB.config, "select * from settings\n")

    def test_getByName(self, *args):
        """test getByName"""
        self.pBDB.config.curs.fetchall = MagicMock(return_value=[[12]])
        with patch(
            "physbiblio.databaseCore.PhysBiblioDBSub.cursExec", autospec=True
        ) as _cu:
            self.assertEqual(self.pBDB.config.getByName("abc"), [[12]])
            _cu.assert_called_once_with(
                self.pBDB.config, "select * from settings where name=?\n", ("abc",)
            )


@patch("logging.Logger.debug")
@patch("logging.Logger.info")
@patch("logging.Logger.warning")
@patch("logging.Logger.error")
@patch("logging.Logger.exception")
class TestConfigVars(unittest.TestCase):
    """Tests for ConfigVars"""

    def test_init(self, *args):
        """test __init__"""
        self.assertTrue(hasattr(ConfigVars, "adsUrl"))
        self.assertTrue(hasattr(ConfigVars, "arxivUrl"))
        self.assertTrue(hasattr(ConfigVars, "doiUrl"))
        self.assertTrue(hasattr(ConfigVars, "inspireAPI"))
        self.assertTrue(hasattr(ConfigVars, "inspireConferencesAPI"))
        self.assertTrue(hasattr(ConfigVars, "inspireExperimentsLink"))
        self.assertTrue(hasattr(ConfigVars, "inspireLiteratureAPI"))
        self.assertTrue(hasattr(ConfigVars, "inspireLiteratureLink"))
        if os.path.exists(tempProfName):
            os.remove(tempProfName)
        with patch("logging.Logger.info") as _i, patch(
            "os.path.exists", return_value=False
        ) as _ope, patch("os.makedirs") as _omd, patch(
            "physbiblio.config.GlobalDB", return_value="globaldb"
        ) as _gdb, patch(
            "physbiblio.config.ConfigVars.checkOldProfiles", autospec=True
        ) as _cop, patch(
            "physbiblio.config.ConfigVars.loadProfiles", autospec=True
        ) as _lp, patch(
            "physbiblio.config.ConfigVars.setDefaultParams", autospec=True
        ) as _dp:
            cv = ConfigVars(tempProfName)
            self.assertEqual(_i.call_count, 2)
            _ope.assert_has_calls([call(cv.configPath), call(cv.dataPath)])
            _omd.assert_has_calls([call(cv.configPath), call(cv.dataPath)])
            _gdb.assert_called_once_with(
                cv.globalDbFile, cv.logger, cv.dataPath, info=False
            )
            _cop.assert_called_once_with(cv)
            _lp.assert_called_once_with(cv)
            _dp.assert_called_once_with(cv)
        self.assertIsInstance(cv.defaultDirs, AppDirs)
        self.assertIsInstance(cv.configPath, six.string_types)
        self.assertIsInstance(cv.dataPath, six.string_types)
        self.assertEqual(cv.loggerString, globalLogName)
        self.assertIsInstance(cv.logger, logging.Logger)
        self.assertEqual(cv.loggingLevels, loggingLevels)
        self.assertEqual(
            cv.paramOrder,
            [
                p.name
                for p in configuration_params.values()
                if p.name not in ignoreParameterOrder
            ],
        )
        self.assertEqual(
            cv.oldConfigProfilesFile, os.path.join(cv.configPath, "profiles.dat")
        )
        self.assertEqual(cv.globalDbFile, os.path.join(cv.configPath, tempProfName))
        self.assertEqual(cv.globalDb, "globaldb")

        ad = AppDirs("PhysBiblio")
        with patch("logging.Logger.info") as _i, patch(
            "os.path.exists", return_value=True
        ) as _ope, patch("os.makedirs") as _omd, patch(
            "physbiblio.config.GlobalDB", return_value="globaldb"
        ) as _gdb, patch(
            "physbiblio.config.AppDirs", return_value=ad
        ) as _ad, patch(
            "physbiblio.config.ConfigVars.checkOldProfiles", autospec=True
        ) as _cop, patch(
            "physbiblio.config.ConfigVars.loadProfiles", autospec=True
        ) as _lp:
            cv = ConfigVars()
            self.assertEqual(_i.call_count, 2)
            _ope.assert_has_calls([call(cv.configPath), call(cv.dataPath)])
            self.assertEqual(_omd.call_count, 0)
            _gdb.assert_called_once_with(
                cv.globalDbFile, cv.logger, cv.dataPath, info=False
            )
            _cop.assert_called_once_with(cv)
            _lp.assert_called_once_with(cv)
            _ad.assert_called_once_with("PhysBiblio")
        self.assertEqual(cv.globalDbFile, os.path.join(cv.configPath, "profiles.db"))
        self.assertIsInstance(cv.params, dict)
        self.assertEqual(len(cv.params), len(configuration_params) - 1)

    def test_loadProfiles(self, *args):
        """test loadProfiles"""
        if os.path.exists(tempProfName):
            os.remove(tempProfName)
        cv = ConfigVars(tempProfName)
        with patch(
            "physbiblio.config.ConfigVars.readProfiles", return_value=["a", "b", "c"]
        ) as _rp:
            cv.loadProfiles()
            self.assertEqual(cv.defaultProfileName, "a")
            self.assertEqual(cv.profiles, "b")
            self.assertEqual(cv.profileOrder, "c")
        for e in (IOError, ValueError, SyntaxError):
            with patch(
                "physbiblio.config.ConfigVars.readProfiles", side_effect=e
            ) as _rp, patch("logging.Logger.warning") as _w, patch(
                "physbiblio.config.GlobalDB.createProfile", autospec=True
            ) as _cp:
                cv.loadProfiles()
                _w.assert_called_once()
                _cp.assert_called_once_with(cv.globalDb)

    def test_prepareLogger(self, *args):
        """test prepareLogger"""
        if os.path.exists(tempProfName):
            os.remove(tempProfName)
        cv = ConfigVars(tempProfName)
        self.assertEqual(cv.loggerString, globalLogName)
        with patch("logging.getLogger") as _gl:
            cv.prepareLogger("abcd")
            _gl.assert_called_once_with("abcd")
        self.assertEqual(cv.loggerString, "abcd")

    def test_readConfig(self, *args):
        """test readConfig"""
        if os.path.exists(tempProfName):
            os.remove(tempProfName)
        cv = ConfigVars(tempProfName)
        tempDb = PhysBiblioDBCore(tempCfgName, cv.logger, info=False)
        tempDb.closeDB = MagicMock()
        configDb = ConfigurationDB(tempDb)
        with patch("logging.Logger.debug") as _d, patch(
            "logging.Logger.exception"
        ) as _e, patch(
            "physbiblio.config.ConfigVars.setDefaultParams", autospec=True
        ) as _sdp, patch(
            "physbiblio.config.PhysBiblioDBCore", return_value=tempDb
        ) as _dbc, patch(
            "physbiblio.config.ConfigurationDB", return_value=configDb
        ) as _cdb, patch(
            "physbiblio.config.addFileHandler", autospec=True
        ) as _afh, patch(
            "physbiblio.config.ConfigVars.readParam", autospec=True
        ) as _rp:
            cv.readConfig()
            _d.assert_has_calls(
                [call("Reading configuration.\n"), call("Configuration loaded.\n")]
            )
            self.assertEqual(_e.call_count, 0)
            _sdp.assert_called_once_with(cv)
            _dbc.assert_called_once_with(cv.currentDatabase, cv.logger, info=False)
            _cdb.assert_called_once_with(tempDb)
            _rp.assert_has_calls([call(cv, k, configDb) for k in configuration_params])
            _afh.assert_called_once_with(
                cv.logger, cv.params["logFileName"], defaultPath=cv.dataPath
            )
            tempDb.closeDB.assert_called_once_with(info=False)
        with patch("logging.Logger.debug") as _d, patch(
            "logging.Logger.exception"
        ) as _e, patch(
            "physbiblio.config.ConfigVars.setDefaultParams", autospec=True
        ) as _sdp, patch(
            "physbiblio.config.PhysBiblioDBCore", return_value=tempDb
        ) as _dbc, patch(
            "physbiblio.config.ConfigurationDB", return_value=configDb
        ) as _cdb, patch(
            "physbiblio.config.ConfigVars.readParam", autospec=True
        ) as _rp:
            cv.readConfig()
        lh = len(cv.logger.handlers)
        with patch("logging.Logger.debug") as _d, patch(
            "logging.Logger.exception"
        ) as _e, patch(
            "physbiblio.config.ConfigVars.setDefaultParams", autospec=True
        ) as _sdp, patch(
            "physbiblio.config.PhysBiblioDBCore", return_value=tempDb
        ) as _dbc, patch(
            "physbiblio.config.ConfigurationDB", return_value=configDb
        ) as _cdb, patch(
            "physbiblio.config.ConfigVars.readParam", autospec=True
        ) as _rp:
            cv.readConfig()
        self.assertEqual(lh, len(cv.logger.handlers))
        tempDb.closeDB.reset_mock()

        with patch("logging.Logger.debug") as _d, patch(
            "logging.Logger.exception"
        ) as _e, patch(
            "physbiblio.config.ConfigVars.setDefaultParams", autospec=True
        ) as _sdp, patch(
            "physbiblio.config.PhysBiblioDBCore", return_value=tempDb
        ) as _dbc, patch(
            "physbiblio.config.ConfigurationDB", return_value=configDb
        ) as _cdb, patch(
            "physbiblio.config.ConfigVars.readParam",
            autospec=True,
            side_effect=ValueError,
        ) as _rp:
            cv.readConfig()
            _d.assert_has_calls(
                [call("Reading configuration.\n"), call("Configuration loaded.\n")]
            )
            _e.assert_called_once_with(
                "ERROR: reading config from '%s' failed." % (cv.currentDatabase)
            )
            _sdp.assert_called_once_with(cv)
            _dbc.assert_called_once_with(cv.currentDatabase, cv.logger, info=False)
            _cdb.assert_called_once_with(tempDb)
            tempDb.closeDB.assert_called_once_with(info=False)
            _rp.assert_called_once_with(
                cv, list(configuration_params.keys())[0], configDb
            )

    def test_readParam(self, *args):
        """test readConfig"""
        if os.path.exists(tempProfName):
            os.remove(tempProfName)
        cv = ConfigVars(tempProfName)
        cv.globalDb.config.getByName = MagicMock(return_value=[{"value": "global"}])
        tempDb = PhysBiblioDBCore(tempCfgName, cv.logger, info=False)
        configDb = ConfigurationDB(tempDb)
        configDb.getByName = MagicMock(return_value=[])
        cv.params = {}

        # ignored
        cv.readParam("mainDatabaseName", configDb)
        self.assertNotIn("mainDatabaseName", cv.params.keys())
        self.assertEqual(cv.globalDb.config.getByName.call_count, 0)
        self.assertEqual(configDb.getByName.call_count, 0)

        # not found
        cv.readParam("pdfFolder", configDb)
        self.assertEqual(
            cv.params["pdfFolder"],
            os.path.join(
                cv.dataPath,
                configuration_params["pdfFolder"].default.replace("PBDATA", ""),
            ),
        )
        configDb.getByName.assert_called_once_with("pdfFolder")
        cv.readParam("timeoutWebSearch", configDb)
        self.assertEqual(
            cv.params["timeoutWebSearch"],
            configuration_params["timeoutWebSearch"].default,
        )
        cv.readParam("pdfApplication", configDb)
        self.assertEqual(
            cv.params["pdfApplication"], configuration_params["pdfApplication"].default
        )

        # global
        configDb.getByName.reset_mock()
        cv.readParam("notifyUpdate", configDb)
        cv.globalDb.config.getByName.assert_called_once_with("notifyUpdate")
        self.assertEqual(configDb.getByName.call_count, 0)

        # float
        key = "timeoutWebSearch"
        configDb.getByName = MagicMock(return_value=[{"value": "local"}])
        with patch("logging.Logger.warning") as _w:
            cv.readParam(key, configDb)
            _w.assert_called_once_with(
                "Failed in reading parameter '%s'." % key, exc_info=True
            )
        self.assertEqual(cv.params[key], configuration_params[key].default)
        configDb.getByName = MagicMock(return_value=[{"value": "123.123"}])
        with patch("logging.Logger.warning") as _w:
            cv.readParam(key, configDb)
            self.assertEqual(_w.call_count, 0)
        self.assertEqual(cv.params[key], 123.123)

        # int
        key = "defaultLimitBibtexs"
        configDb.getByName = MagicMock(return_value=[{"value": "local"}])
        with patch("logging.Logger.warning") as _w:
            cv.readParam(key, configDb)
            _w.assert_called_once_with(
                "Failed in reading parameter '%s'." % key, exc_info=True
            )
        self.assertEqual(cv.params[key], configuration_params[key].default)
        configDb.getByName = MagicMock(return_value=[{"value": "123.13"}])
        with patch("logging.Logger.warning") as _w:
            cv.readParam(key, configDb)
            _w.assert_called_once_with(
                "Failed in reading parameter '%s'." % key, exc_info=True
            )
        self.assertEqual(cv.params[key], configuration_params[key].default)
        configDb.getByName = MagicMock(return_value=[{"value": "123"}])
        with patch("logging.Logger.warning") as _w:
            cv.readParam(key, configDb)
            self.assertEqual(_w.call_count, 0)
        self.assertEqual(cv.params[key], 123)

        # boolean
        key = "fetchAbstract"
        configDb.getByName = MagicMock(return_value=[{"value": "local"}])
        with patch("logging.Logger.warning") as _w:
            cv.readParam(key, configDb)
            _w.assert_called_once_with(
                "Failed in reading parameter '%s'." % key, exc_info=True
            )
        self.assertEqual(cv.params[key], configuration_params[key].default)
        for v in ("True", "1", "yes", "On"):
            configDb.getByName = MagicMock(return_value=[{"value": v}])
            with patch("logging.Logger.warning") as _w:
                cv.readParam(key, configDb)
                self.assertEqual(_w.call_count, 0)
            self.assertEqual(cv.params[key], True)
        for v in ("False", "0", "no", "Off"):
            configDb.getByName = MagicMock(return_value=[{"value": v}])
            with patch("logging.Logger.warning") as _w:
                cv.readParam(key, configDb)
                self.assertEqual(_w.call_count, 0)
            self.assertEqual(cv.params[key], False)

        # list
        key = "defaultCategories"
        configDb.getByName = MagicMock(return_value=[{"value": "local"}])
        with patch("logging.Logger.warning") as _w:
            cv.readParam(key, configDb)
            _w.assert_called_once_with(
                "Failed in reading parameter '%s'." % key, exc_info=True
            )
        self.assertEqual(cv.params[key], configuration_params[key].default)
        configDb.getByName = MagicMock(return_value=[{"value": "['a'"}])
        with patch("logging.Logger.warning") as _w:
            cv.readParam(key, configDb)
            _w.assert_called_once_with(
                "Failed in reading parameter '%s'." % key, exc_info=True
            )
        self.assertEqual(cv.params[key], configuration_params[key].default)
        configDb.getByName = MagicMock(return_value=[{"value": "['a', 'b']"}])
        with patch("logging.Logger.warning") as _w:
            cv.readParam(key, configDb)
            self.assertEqual(_w.call_count, 0)
        self.assertEqual(cv.params[key], ["a", "b"])
        configDb.getByName = MagicMock(return_value=[{"value": "('a', 'b')"}])
        with patch("logging.Logger.warning") as _w:
            cv.readParam(key, configDb)
            self.assertEqual(_w.call_count, 0)
        self.assertEqual(cv.params[key], ("a", "b"))

        # str
        key = "pdfApplication"
        configDb.getByName = MagicMock(return_value=[{"value": "local"}])
        with patch("logging.Logger.warning") as _w:
            cv.readParam(key, configDb)
            self.assertEqual(_w.call_count, 0)
        self.assertEqual(cv.params[key], "local")
        key = "logFileName"
        configDb.getByName = MagicMock(return_value=[{"value": "PBDATAlocal"}])
        with patch("logging.Logger.warning") as _w:
            cv.readParam(key, configDb)
            self.assertEqual(_w.call_count, 0)
        self.assertEqual(cv.params[key], os.path.join(cv.dataPath, "local"))

    def test_readProfiles(self, *args):
        """test readProfiles"""
        if os.path.exists(tempProfName):
            os.remove(tempProfName)
        cv = ConfigVars(tempProfName)
        with patch(
            "physbiblio.config.GlobalDB.getProfiles",
            autospec=True,
            return_value=[
                {
                    "name": "a",
                    "description": "desc",
                    "oldCfg": "no",
                    "databasefile": "test.db",
                }
            ],
        ) as _gp, patch(
            "physbiblio.config.GlobalDB.getDefaultProfile",
            autospec=True,
            return_value="def",
        ) as _gd, patch(
            "physbiblio.config.GlobalDB.getProfileOrder",
            autospec=True,
            return_value="ord",
        ) as _go:
            res = cv.readProfiles()
            _gp.assert_called_once_with(cv.globalDb)
            _gd.assert_called_once_with(cv.globalDb)
            _go.assert_called_once_with(cv.globalDb)
            self.assertEqual(res[0], "def")
            self.assertEqual(
                res[1],
                {
                    "a": {
                        "n": "a",
                        "d": "desc",
                        "f": "no",
                        "db": os.path.join(cv.dataPath, "test.db"),
                    }
                },
            )
            self.assertEqual(res[2], "ord")

    def test_reInit(self, *args):
        """test reInit"""
        if os.path.exists(tempProfName):
            os.remove(tempProfName)
        cv = ConfigVars(tempProfName)
        cv.defaultProfileName = "b"
        cv.profiles = {
            "a": {"n": "a", "d": "desc", "f": "no", "db": "test.db"},
            "b": {"n": "b", "d": "ript", "f": "si", "db": os.sep + "tset.db"},
        }
        with patch("logging.Logger.error") as _e, patch(
            "physbiblio.config.ConfigVars.readConfig", autospec=True
        ) as _rc:
            cv.reInit("c")
            _e.assert_called_once_with("Profile not found!")
            self.assertEqual(_rc.call_count, 0)

        with patch("logging.Logger.error") as _e, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "physbiblio.config.ConfigVars.readConfig", autospec=True
        ) as _rc, patch(
            "physbiblio.config.ConfigVars.setDefaultParams", autospec=True
        ) as _sd:
            cv.reInit("a")
            self.assertEqual(_e.call_count, 0)
            _rc.assert_called_once_with(cv)
            _sd.assert_called_once_with(cv)
            _i.assert_called_once()
        self.assertEqual(cv.currentProfileName, "a")
        self.assertEqual(cv.currentProfile, cv.profiles["a"])
        self.assertEqual(
            cv.currentDatabase, os.path.join(cv.dataPath, cv.profiles["a"]["db"])
        )

        with patch("logging.Logger.error") as _e, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "physbiblio.config.ConfigVars.readConfig", autospec=True
        ) as _rc, patch(
            "physbiblio.config.ConfigVars.setDefaultParams", autospec=True
        ) as _sd:
            cv.reInit("c", newProfile=cv.profiles["b"])
            self.assertEqual(_e.call_count, 0)
            _rc.assert_called_once_with(cv)
            _sd.assert_called_once_with(cv)
            _i.assert_called_once()
        self.assertEqual(cv.currentProfileName, "c")
        self.assertEqual(cv.currentProfile, cv.profiles["b"])
        self.assertEqual(cv.currentDatabase, cv.profiles["b"]["db"])

    def test_reloadProfiles(self, *args):
        """test reloadProfiles"""
        if os.path.exists(tempProfName):
            os.remove(tempProfName)
        cv = ConfigVars(tempProfName)
        with patch("logging.Logger.critical") as _c, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "physbiblio.config.ConfigVars.loadProfiles", autospec=True
        ) as _lp, patch(
            "physbiblio.config.ConfigVars.readConfig", autospec=True
        ) as _rc:
            cv.reloadProfiles("no")
            _lp.assert_called_once_with(cv)
            _c.assert_called_once_with(
                "The profile '%s' does not exist!" % "no"
                + " Back to the default one ('%s')" % cv.defaultProfileName
            )
            _i.assert_called_once()
            _rc.assert_called_once_with(cv)
        self.assertEqual(cv.currentProfileName, cv.defaultProfileName)
        self.assertEqual(cv.currentProfile, cv.profiles[cv.defaultProfileName])
        self.assertEqual(cv.currentDatabase, cv.profiles[cv.defaultProfileName]["db"])

        cv.defaultProfileName = "b"
        cv.profiles = {
            "a": {"n": "a", "d": "desc", "f": "no", "db": "test.db"},
            "b": {"n": "b", "d": "ript", "f": "si", "db": os.sep + "tset.db"},
        }
        with patch("logging.Logger.critical") as _c, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "physbiblio.config.ConfigVars.loadProfiles", autospec=True
        ) as _lp, patch(
            "physbiblio.config.ConfigVars.readConfig", autospec=True
        ) as _rc:
            cv.reloadProfiles(useProfile="a")
            _lp.assert_called_once_with(cv)
            self.assertEqual(_c.call_count, 0)
            _i.assert_called_once()
            _rc.assert_called_once_with(cv)
        self.assertEqual(cv.currentProfileName, "a")
        self.assertEqual(cv.currentProfile, cv.profiles["a"])
        self.assertEqual(
            cv.currentDatabase, os.path.join(cv.dataPath, cv.profiles["a"]["db"])
        )

        with patch("logging.Logger.critical") as _c, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "physbiblio.config.ConfigVars.loadProfiles", autospec=True
        ) as _lp, patch(
            "physbiblio.config.ConfigVars.readConfig", autospec=True
        ) as _rc:
            cv.reloadProfiles()
            _lp.assert_called_once_with(cv)
            self.assertEqual(_c.call_count, 0)
            _i.assert_called_once()
            _rc.assert_called_once_with(cv)
        self.assertEqual(cv.currentProfileName, "b")
        self.assertEqual(cv.currentProfile, cv.profiles["b"])
        self.assertEqual(cv.currentDatabase, cv.profiles["b"]["db"])

    def test_replacePBDATA(self, *args):
        """test replacePBDATA"""
        if os.path.exists(tempProfName):
            os.remove(tempProfName)
        cv = ConfigVars(tempProfName)
        self.assertEqual(cv.replacePBDATA(123), 123)
        self.assertEqual(cv.replacePBDATA("abcd"), "abcd")
        self.assertEqual(
            cv.replacePBDATA("PBDATAabcd"), os.path.join(cv.dataPath, "abcd")
        )

        self.assertEqual(replacePBDATA("ab", 123), 123)
        self.assertEqual(replacePBDATA("AB", "abcd"), "abcd")
        self.assertEqual(
            replacePBDATA("ABC", "PBDATAabcd"), os.path.join("ABC", "abcd")
        )

    def test_setDefaultParams(self, *args):
        """test setDefaultParams"""
        if os.path.exists(tempProfName):
            os.remove(tempProfName)
        cv = ConfigVars(tempProfName)
        cv.params["mainDatabaseName"] = "no"
        cv.params["pdfFolder"] = "PBDATA"
        cv.setDefaultParams()
        self.assertIsInstance(cv.params, dict)
        for k, p in configuration_params.items():
            if k == "mainDatabaseName":
                self.assertNotIn(k, cv.params.keys())
            else:
                if isinstance(p.default, str) and "PBDATA" in p.default:
                    v = os.path.join(cv.dataPath, p.default.replace("PBDATA", ""))
                else:
                    v = p.default
                self.assertEqual(cv.params[k], v)


@patch("logging.Logger.debug")
@patch("logging.Logger.info")
@patch("logging.Logger.warning")
@patch("logging.Logger.error")
@patch("logging.Logger.exception")
class TestFunctions(unittest.TestCase):
    """Tests for more functions in config module"""

    def test_getLogLevel(self, *args):
        """test getLogLevel"""
        for v, e in [
            [0, logging.ERROR],
            [1, logging.WARNING],
            [2, logging.INFO],
            [3, logging.DEBUG],
            ["a", logging.DEBUG],
        ]:
            self.assertEqual(getLogLevel(v), e)

    def test_addFileHandler(self, *args):
        """test addFileHandler"""
        log = logging.Logger("testAFH")
        h = logging.handlers.RotatingFileHandler(pbConfig.overWritelogFileName)
        with patch("logging.handlers.RotatingFileHandler", return_value=h) as _rfh:
            addFileHandler(log, "myfn.log")
            _rfh.assert_called_once_with(
                "myfn.log", maxBytes=5.0 * 2 ** 20, backupCount=5
            )
        self.assertEqual(h.level, getLogLevel(pbConfig.params["loggingLevel"]))
        self.assertIn(h, log.handlers)
        log = logging.Logger("testAFH1")
        with patch(
            "physbiblio.config.replacePBDATA",
            return_value=pbConfig.overWritelogFileName,
        ) as _rfh:
            addFileHandler(
                log,
                "/can/not/create/this/log/file/myfn.log",
                defaultPath=pbConfig.dataPath,
            )
            _rfh.assert_called_once_with(
                pbConfig.dataPath, configuration_params["logFileName"].default
            )


def tearDownModule():
    """actions to perform at the end: remove temporary test files"""
    if os.path.exists(tempCfgName):
        os.remove(tempCfgName)
    if os.path.exists(tempCfgName1):
        os.remove(tempCfgName1)
    if os.path.exists(tempProfName):
        os.remove(tempProfName)
    if os.path.exists(tempOldCfgName):
        os.remove(tempOldCfgName)


if __name__ == "__main__":
    unittest.main()
