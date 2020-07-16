#!/usr/bin/env python
"""Test file for the physbiblio.errors module.

This file is part of the physbiblio package.
"""
import logging
import sys
import traceback

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import patch
    from StringIO import StringIO
else:
    import unittest
    from io import StringIO
    from unittest.mock import patch

try:
    from physbiblio.config import pbConfig
    from physbiblio.errors import PBErrorManagerClass
    from physbiblio.setuptests import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


class TestErrors(unittest.TestCase):
    """Test PBErrorManagerClass stuff"""

    @classmethod
    def setUpClass(self):
        """settings"""
        with patch.dict(
            pbConfig.params,
            {"loggingLevel": 3, "logFileName": logFileName},
            clear=False,
        ):
            self.pBErrorManager = PBErrorManagerClass("testlogger")

    def reset(self, m):
        """Clear a StringIO object"""
        m.seek(0)
        m.truncate(0)

    def resetLogFile(self):
        """Reset the logfile content"""
        open(logFileName, "w").close()

    def readLogFile(self):
        """Read the logfile content"""
        with open(logFileName) as logFile:
            log_new = logFile.read()
        return log_new

    def test_init(self):
        """test PBErrorManagerClass.__init__"""
        owf = pbConfig.overWritelogFileName
        del pbConfig.overWritelogFileName
        with patch("physbiblio.errors.getLogLevel", return_value=88) as _gll, patch(
            "physbiblio.errors.addFileHandler"
        ) as _afh:
            a = PBErrorManagerClass("test")
            self.assertEqual(a.loggerString, "test")
            self.assertIsInstance(a.logger, logging.Logger)
            self.assertEqual(a.tempsh, [])
            self.assertEqual(a.loglevel, 88)
            _gll.assert_called_once_with(pbConfig.params["loggingLevel"])
            _afh.assert_called_once_with(a.logger, pbConfig.params["logFileName"])
        pbConfig.overWritelogFileName = owf
        with patch("physbiblio.errors.getLogLevel", return_value=88) as _gll, patch(
            "physbiblio.errors.addFileHandler"
        ) as _afh:
            a = PBErrorManagerClass("test")
            self.assertEqual(a.loggerString, "test")
            self.assertIsInstance(a.logger, logging.Logger)
            self.assertEqual(a.tempsh, [])
            self.assertEqual(a.loglevel, 88)
            _gll.assert_called_once_with(pbConfig.params["loggingLevel"])
            _afh.assert_called_once_with(a.logger, pbConfig.overWritelogFileName)

    def test_critical(self):
        """Test pBLogger.critical with and without exception"""
        self.resetLogFile()
        try:
            raise Exception("Fake error")
        except Exception as e:
            self.pBErrorManager.logger.critical(str(e))
        log_new = self.readLogFile()
        self.assertIn(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), log_new)
        self.assertIn("CRITICAL : [test_errors.test_critical] Fake error", log_new)
        self.assertNotIn("Traceback (most recent call last):", log_new)
        try:
            raise Exception("Fake error")
        except Exception as e:
            self.pBErrorManager.logger.critical(str(e), exc_info=True)
        log_new = self.readLogFile()
        self.assertIn("Traceback (most recent call last):", log_new)

    def test_exception(self):
        """Test pBLogger.exception"""
        self.resetLogFile()
        try:
            raise Exception("Fake error")
        except Exception as e:
            self.pBErrorManager.logger.exception(str(e))
        try:
            raise Exception("New fake error")
        except Exception as e:
            self.pBErrorManager.logger.error(str(e))
        log_new = self.readLogFile()
        self.assertIn(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), log_new)
        self.assertIn("ERROR : [test_errors.test_exception] Fake error", log_new)
        self.assertIn("ERROR : [test_errors.test_exception] New fake error", log_new)
        self.assertIn("Traceback (most recent call last):", log_new)

    def test_warning(self):
        """Test pBLogger.warning"""
        self.resetLogFile()
        try:
            raise Exception("Fake warning")
        except Exception as e:
            self.pBErrorManager.logger.warning(str(e))
        log_new = self.readLogFile()
        self.assertIn(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), log_new)
        self.assertIn("WARNING : [test_errors.test_warning] Fake warning", log_new)

    def test_info(self):
        """Test pBLogger.info"""
        self.resetLogFile()
        self.pBErrorManager.logger.info("Some info")
        log_new = self.readLogFile()
        self.assertIn(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), log_new)
        self.assertIn("INFO : [test_errors.test_info] Some info", log_new)

    def test_tempHandler(self):
        """Test stuff as the temporary handler"""
        self.assertEqual(self.pBErrorManager.tempsh, [])
        self.assertEqual(len(self.pBErrorManager.logger.handlers), 2)
        with patch("sys.stdout", new_callable=StringIO) as _mock:
            self.assertTrue(
                self.pBErrorManager.tempHandler(sys.stdout, format="%(message)s")
            )
            self.assertEqual(len(self.pBErrorManager.logger.handlers), 3)
            self.assertEqual(len(self.pBErrorManager.tempsh), 1)
            self.reset(_mock)
            self.pBErrorManager.logger.critical("Fake critical")
            self.assertEqual(_mock.getvalue(), "Fake critical\n")
            self.pBErrorManager.rmTempHandler()
            self.assertEqual(self.pBErrorManager.tempsh, [])
            self.assertEqual(len(self.pBErrorManager.logger.handlers), 2)
            self.assertEqual(len(self.pBErrorManager.tempsh), 0)
            self.reset(_mock)
            self.assertEqual(_mock.getvalue(), "")
            self.pBErrorManager.logger.critical("Fake critical")
            self.assertEqual(_mock.getvalue(), "")
            self.assertTrue(
                self.pBErrorManager.tempHandler(sys.stdout, format="%(message)s")
            )
            self.assertEqual(len(self.pBErrorManager.logger.handlers), 3)
            self.assertTrue(
                self.pBErrorManager.tempHandler(sys.stdout, format="%(message)s")
            )
            self.assertEqual(len(self.pBErrorManager.logger.handlers), 4)
            self.assertTrue(
                self.pBErrorManager.tempHandler(sys.stdout, format="%(message)s")
            )
            self.assertEqual(len(self.pBErrorManager.logger.handlers), 5)
            self.assertEqual(len(self.pBErrorManager.tempsh), 3)
            self.pBErrorManager.rmTempHandler()
            self.assertEqual(len(self.pBErrorManager.logger.handlers), 4)
            self.assertEqual(len(self.pBErrorManager.tempsh), 2)
            self.pBErrorManager.rmAllTempHandlers()
            self.assertEqual(len(self.pBErrorManager.logger.handlers), 2)
            self.assertEqual(len(self.pBErrorManager.tempsh), 0)


if __name__ == "__main__":
    unittest.main()
