#!/usr/bin/env python
"""Test file for the physbiblio.inspireStats module.

This file is part of the physbiblio package.
"""
import datetime
import os
import sys
import traceback

import matplotlib
import pytz

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import MagicMock, call, patch
    from StringIO import StringIO
else:
    import unittest
    from io import StringIO
    from unittest.mock import MagicMock, call, patch

try:
    from physbiblio.errors import pBErrorManager
    from physbiblio.inspireStats import *
    from physbiblio.setuptests import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


@unittest.skipIf(skipTestsSettings.online, "Online tests")
@patch("logging.Logger.debug")
@patch("logging.Logger.info")
@patch("logging.Logger.warning")
@patch("logging.Logger.exception")
class TestInspireStatsMethods(unittest.TestCase):
    """Tests for methods in physbiblio.inspireStats"""

    def test_init(self, *args):
        """test some properties"""
        self.assertIsInstance(pBStats, InspireStatsLoader)
        tpBStats = InspireStatsLoader()
        self.assertEqual(tpBStats.authorPlotInfo, None)
        self.assertEqual(tpBStats.paperPlotInfo, None)

    def test_paperStats(self, *args):
        """Test paperStats function downloading real and fake data"""
        # not a valid record (it was cancelled):
        self.assertEqual(
            pBStats.paperStats("1358853"),
            {
                "aI": {},
                "citList": [
                    [
                        datetime.datetime.fromordinal(
                            datetime.date.today().toordinal()
                        ).replace(tzinfo=pytz.UTC)
                    ],
                    [0],
                ],
                "id": "1358853",
            },
        )

        # needs multiple pages to load all the content
        testGood = pBStats.paperStats("650592")
        self.assertTrue(testGood["id"], "650592")
        self.assertTrue(len(testGood["aI"]) > 950)
        self.assertEqual(len(testGood["aI"]) + 1, len(testGood["citList"][1]))
        self.assertEqual(len(testGood["citList"][0]), len(testGood["citList"][1]))
        self.assertFalse("fig" in testGood.keys())

        testGood = pBStats.paperStats("1385583", plot=True)
        self.assertTrue(testGood["id"], "1385583")
        self.assertTrue(len(testGood["aI"]) > 120)
        self.assertEqual(len(testGood["aI"]) + 1, len(testGood["citList"][1]))
        self.assertEqual(len(testGood["citList"][0]), len(testGood["citList"][1]))
        self.assertIsInstance(testGood["fig"], matplotlib.figure.Figure)

        testGood = pBStats.paperStats(["1358853", "1385583"])
        self.assertTrue(testGood["id"], ["1358853", "1385583"])
        self.assertTrue(len(testGood["aI"]) > 120)
        pbm = MagicMock()
        pbv = MagicMock()
        testGood = pBStats.paperStats(["1358853", "1385583"], pbMax=pbm, pbVal=pbv)
        self.assertTrue(testGood["id"], ["1358853", "1385583"])
        self.assertTrue(len(testGood["aI"]) > 120)
        pbm.assert_called_once_with(2)
        pbv.assert_has_calls([call(1), call(2)])

    def test_authorStats(self, *args):
        """Test paperStats function downloading real and fake data"""
        res = pBStats.authorStats("E.M.Zavanin.1")
        self.assertTrue(res["h"] >= 4)
        self.assertTrue(res["paLi"][1][-1] == 8)
        self.assertTrue(res["allLi"][1][-1] >= 320)
        self.assertTrue(res["meanLi"][1][-1] >= 40)
        with patch(
            "physbiblio.inspireStats.InspireStatsLoader.paperStats",
            return_value={
                "aI": {
                    1653464: {
                        "date": datetime.datetime(2018, 2, 7, 4, 24, 2).replace(
                            tzinfo=pytz.UTC
                        )
                    },
                    1662320: {
                        "date": datetime.datetime(2018, 3, 14, 4, 53, 45).replace(
                            tzinfo=pytz.UTC
                        )
                    },
                    1664547: {
                        "date": datetime.datetime(2018, 3, 29, 5, 8, 58).replace(
                            tzinfo=pytz.UTC
                        )
                    },
                    1663942: {
                        "date": datetime.datetime(2018, 3, 26, 3, 25, 34).replace(
                            tzinfo=pytz.UTC
                        )
                    },
                    1658582: {
                        "date": datetime.datetime(2018, 3, 6, 3, 58, 52).replace(
                            tzinfo=pytz.UTC
                        )
                    },
                },
                "id": "1649081",
                "citList": [
                    [
                        datetime.datetime(2018, 2, 7, 4, 24, 2).replace(
                            tzinfo=pytz.UTC
                        ),
                        datetime.datetime(2018, 3, 6, 3, 58, 52).replace(
                            tzinfo=pytz.UTC
                        ),
                        datetime.datetime(2018, 3, 14, 4, 53, 45).replace(
                            tzinfo=pytz.UTC
                        ),
                        datetime.datetime(2018, 3, 26, 3, 25, 34).replace(
                            tzinfo=pytz.UTC
                        ),
                        datetime.datetime(2018, 3, 29, 5, 8, 58).replace(
                            tzinfo=pytz.UTC
                        ),
                        datetime.date(2018, 4, 16),
                    ],
                    [1, 2, 3, 4, 5, 5],
                ],
            },
            autospec=True,
        ) as _mock:
            testGood = pBStats.authorStats("E.M.Zavanin.1", plot=True)
            for i in [
                "1229039",
                "1345462",
                "1366180",
                "1385583",
                "1387736",
                "1404176",
                "1460832",
                "1519902",
            ]:
                self.assertIn(i, testGood["aI"].keys())
                self.assertIn(i, [a[0][1] for a in _mock.call_args_list])
            self.assertTrue(
                testGood.keys(), ["meanLi", "allLi", "aI", "paLi", "h", "name"]
            )
            self.assertTrue(testGood["h"], 4)
            self.assertTrue(testGood["name"], "E.M.Zavanin.1")
            self.assertEqual(len(testGood["paLi"][0]), len(testGood["aI"]))
            self.assertEqual(len(testGood["paLi"][1]), len(testGood["aI"]))
            self.assertEqual(len(testGood["allLi"][0]), 5 * len(testGood["aI"]))
            self.assertEqual(len(testGood["allLi"][1]), 5 * len(testGood["aI"]))
            self.assertEqual(len(testGood["meanLi"][0]), 5 * len(testGood["aI"]))
            self.assertEqual(len(testGood["meanLi"][1]), 5 * len(testGood["aI"]))
            self.assertEqual(len(testGood["figs"]), 6)
            for f in testGood["figs"]:
                self.assertIsInstance(f, matplotlib.figure.Figure)

            testGood = pBStats.authorStats(["A.Gallego.Cadavid.1", "E.M.Zavanin.1"])
            pbm = MagicMock()
            pbv = MagicMock()
            testGood = pBStats.authorStats(
                ["A.Gallego.Cadavid.1", "E.M.Zavanin.1"], pbMax=pbm, pbVal=pbv
            )
            pbm.assert_called_once_with(2)
            pbv.assert_has_calls([call(1), call(2)])

            testGood = pBStats.authorStats("E.M.Zavanin.1")
            pbm = MagicMock()
            pbv = MagicMock()
            testGood = pBStats.authorStats("E.M.Zavanin.1", pbMax=pbm, pbVal=pbv)
            pbm.assert_called_once_with(8)
            pbv.assert_has_calls([call(i + 1) for i in range(8)])


if __name__ == "__main__":
    unittest.main()
