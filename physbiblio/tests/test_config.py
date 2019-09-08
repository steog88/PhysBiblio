#!/usr/bin/env python
"""Test file for the physbiblio.config module.

This file is part of the physbiblio package.
"""
from collections import OrderedDict
import os
import sys
import traceback

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import call, patch
else:
    import unittest
    from unittest.mock import call, patch

try:
    from physbiblio.setuptests import *
    from physbiblio.databaseCore import PhysBiblioDBCore
    from physbiblio.config import (
        pbConfig,
        ConfigParameter,
        ConfigParametersList,
        ConfigurationDB,
        configuration_params,
        ConfigVars,
        GlobalDB,
    )
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())

tempOldCfgName = os.path.join(pbConfig.dataPath, "tests_%s.cfg" % today_ymd)
tempCfgName = os.path.join(pbConfig.dataPath, "tests_cfg_%s.db" % today_ymd)
tempCfgName1 = os.path.join(pbConfig.dataPath, "tests_cfg1_%s.db" % today_ymd)
tempProfName = os.path.join(pbConfig.dataPath, "tests_prof_%s.db" % today_ymd)


class TestConfigParameter(unittest.TestCase):
    """Tests for ConfigParameter from physbiblio.config"""

    def test_init(self):
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

    def test_getitem(self):
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


class TestConfigParametersList(unittest.TestCase):
    """Tests for ConfigParametersList from physbiblio.config"""

    def test_init(self):
        """Test __init__"""
        p = ConfigParametersList()
        self.assertIsInstance(p, OrderedDict)

    def test_add(self):
        """Test add"""
        pl = ConfigParametersList()
        p1 = ConfigParameter("name", "abc")
        p2 = ConfigParameter("other", "def")
        pl.add(p1)
        self.assertEqual(pl["name"], p1)
        pl.add(p2)
        self.assertEqual(pl["other"], p2)
        self.assertEqual(list(pl.keys()), ["name", "other"])


class TestConfigMethods(unittest.TestCase):
    """Tests for methods in physbiblio.config"""

    def test_config(self):
        """Test config methods for config management"""
        if os.path.exists(tempCfgName):
            os.remove(tempCfgName)
        newConfParamsDict = {k: p.default for k, p in configuration_params.items()}
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
            self.assertEqual(tempPbConfig1.params, newConfParamsDict)
            tempPbConfig1.params["logFileName"] = "otherfilename"
            tempPbConfig1.params["timeoutWebSearch"] = 10.0
            tempPbConfig1.params["askBeforeExit"] = True
            tempPbConfig1.params["maxAuthorNames"] = 5
            tempPbConfig1.params["defaultCategories"] = [1]
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
            self.assertEqual(tempPbConfig.params, tempPbConfig1.params)

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

    def test_profiles(self):
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
        tempParams = tempPbConfig.params

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
        self.assertEqual(
            tempPbConfig.params, {k: p.default for k, p in configuration_params.items()}
        )

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
        self.assertEqual(tempPbConfig.params, tempParams)

        tempDb = PhysBiblioDBCore(tempProfName1, tempPbConfig.logger, info=False)
        configDb = ConfigurationDB(tempDb)
        configDb.insert("defaultCategories", "[0")
        configDb.commit()

        with patch("logging.Logger.warning") as _w:
            tempPbConfig.readConfig()
            self.assertEqual(tempPbConfig.params, tempParams)
            _w.assert_any_call(
                "Failed in reading parameter 'defaultCategories'.", exc_info=True
            )

        configDb.insert("loggingLevel", "4")
        configDb.insert("pdfFolder", "/nonexistent/")
        configDb.insert("askBeforeExit", "True")
        configDb.insert("timeoutWebSearch", "20.")
        configDb.commit()
        tempParams["loggingLevel"] = 4
        tempParams["pdfFolder"] = u"/nonexistent/"
        tempParams["askBeforeExit"] = True
        tempParams["timeoutWebSearch"] = 20.0
        with patch("logging.Logger.warning") as _w:
            tempPbConfig.readConfig()
            _w.assert_any_call(
                "Failed in reading parameter 'defaultCategories'.", exc_info=True
            )
        self.assertEqual(tempPbConfig.params, tempParams)

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
            )
            _e.reset_mock()
            self.assertFalse(
                tempPbConfig.globalDb.updateSearchField(1, "searchDict", "")
            )
            _e.assert_called_once_with(
                "Empty value or field not in the following list: "
                + "[searchDict, replaceFields, name, limitNum, offsetNum]"
            )
            _e.reset_mock()
            self.assertFalse(
                tempPbConfig.globalDb.updateSearchField(1, "replaceFields", None)
            )
            _e.assert_called_once_with(
                "Empty value or field not in the following list: "
                + "[searchDict, replaceFields, name, limitNum, offsetNum]"
            )
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
        self.assertEqual(search["replaceFIelds"], "cd")
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


class TestProfilesDB(unittest.TestCase):
    """Test GlobalDB"""

    def test_GlobalDB(self):
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
                        os.path.join(
                            pbConfig.dataPath,
                            configuration_params["mainDatabaseName"].default.replace(
                                "PBDATA", ""
                            ),
                        )
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
