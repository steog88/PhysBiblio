"""Utilities for in the tests of the physbiblio modules.

This file is part of the physbiblio package.
"""
import datetime
import os
import sys
import traceback

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import patch
    from StringIO import StringIO

    USE_AUTOSPEC_CLASS = False
else:
    import unittest
    from io import StringIO
    from unittest.mock import patch

    USE_AUTOSPEC_CLASS = True

today_ymd = datetime.datetime.today().strftime("%y%m%d_%H%M%S")
tempLogFileName = "tests_%s.log" % today_ymd

try:
    from physbiblio.config import pbConfig

    pbConfig.overWritelogFileName = os.path.join(pbConfig.dataPath, tempLogFileName)
    pbConfig.prepareLogger("physbibliotestlog")
    pbConfig.reloadProfiles()
    from physbiblio.database import PhysBiblioDB
    from physbiblio.errors import pBErrorManager, pBLogger
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise


class SkipTestsSettingsClass:
    """Store settings for deciding the tests to skip"""

    def __init__(self):
        """Define non-gui skip settings"""
        self.default()

    def copy(self):
        """create a new instance, copy of the previous one"""
        new = SkipTestsSettingsClass()
        new.db = bool(self.db)
        new.gui = bool(self.gui)
        new.long = bool(self.long)
        new.online = bool(self.online)
        return new

    def default(self):
        """Default settings"""
        self.db = False
        self.gui = False
        self.long = False
        self.online = False

    def __str__(self):
        """print current settings"""
        return "DB: %s\nGUI: %s\nlong: %s\nOnline: %s" % (
            self.db,
            self.gui,
            self.long,
            self.online,
        )


skipTestsSettings = SkipTestsSettingsClass()

pbConfig.params["logFileName"] = tempLogFileName
logFileName = os.path.join(pbConfig.dataPath, pbConfig.params["logFileName"])

tempDBName = os.path.join(pbConfig.dataPath, "tests_%s.db" % today_ymd)
if os.path.exists(tempDBName):
    os.remove(tempDBName)
tempFDBName = os.path.join(pbConfig.dataPath, "tests_first_%s.db" % today_ymd)
if os.path.exists(tempFDBName):
    os.remove(tempFDBName)


class NameSpace:
    pass


class DBTestCase(unittest.TestCase):
    """define the class that will be used for database tests"""

    @classmethod
    @patch("logging.Logger.debug")
    @patch("logging.Logger.info")
    @patch("logging.Logger.warning")
    @patch("logging.Logger.exception")
    def setUpClass(self, *args):
        """Create a temporary database"""
        self.maxDiff = None
        self.pBDB = PhysBiblioDB(tempDBName, pBLogger)

    def tearDown(self):
        """Clean temporary database"""
        self.pBDB.undo(verbose=False)

    @patch("sys.stdout", new_callable=StringIO)
    def assert_stdout(self, function, expected_output, mock_stdout):
        """Catch and test stdout of the function"""
        pBErrorManager.tempHandler(sys.stdout, format="%(message)s")
        function()
        pBErrorManager.rmTempHandler()
        self.assertEqual(mock_stdout.getvalue(), expected_output)


def tearDownModule():
    """Clean temporary files at the end"""
    if os.path.exists(logFileName):
        os.remove(logFileName)
    if os.path.exists(tempDBName):
        os.remove(tempDBName)
    if os.path.exists(tempFDBName):
        os.remove(tempFDBName)
