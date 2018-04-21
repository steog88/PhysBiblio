#!/usr/bin/env python
"""
Test file for the physbiblio.inspireStats module.

This file is part of the physbiblio package.
"""
import sys, traceback, os, datetime
import matplotlib

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch, call
	from StringIO import StringIO
else:
	import unittest
	from unittest.mock import patch, call
	from io import StringIO

try:
	from physbiblio.errors import pBErrorManager
	from physbiblio.setuptests import *
	from physbiblio.inspireStats import pBStats
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipOnlineTests, "Online tests")
class TestInspireStatsMethods(unittest.TestCase):
	"""Tests for methods in physbiblio.inspireStats"""
	@patch('sys.stdout', new_callable=StringIO)
	def assert_in_stdout(self, function, expected_output, mock_stdout):
		"""Catch and if test stdout of the function contains a string"""
		pBErrorManager.tempHandler(sys.stdout, format = '%(message)s')
		function()
		pBErrorManager.rmTempHandler()
		self.assertIn(expected_output, mock_stdout.getvalue())

	def test_paperStats(self):
		"""Test paperStats function downloading real and fake data"""
		#not a valid record (it was cancelled):
		self.assertEqual(pBStats.paperStats("1358853"),
			{'aI': {}, 'citList': [[datetime.date.today()], [0]], 'id': '1358853'})
		self.assert_in_stdout(lambda: pBStats.paperStats("1358853"),
			"Cannot read the page content!")

		#needs multiple pages to load all the content
		testGood = pBStats.paperStats("650592")
		self.assertTrue(testGood["id"], "650592")
		self.assertTrue(len(testGood["aI"])>950)
		self.assertEqual(len(testGood["aI"]) + 1, len(testGood["citList"][1]))
		self.assertEqual(len(testGood["citList"][0]), len(testGood["citList"][1]))
		self.assertFalse("fig" in testGood.keys())

		testGood = pBStats.paperStats("1385583", plot = True)
		self.assertTrue(testGood["id"], "1385583")
		self.assertTrue(len(testGood["aI"])>120)
		self.assertEqual(len(testGood["aI"]) + 1, len(testGood["citList"][1]))
		self.assertEqual(len(testGood["citList"][0]), len(testGood["citList"][1]))
		self.assertIsInstance(testGood["fig"], matplotlib.figure.Figure)

	def test_authorStats(self):
		"""Test paperStats function downloading real and fake data"""
		with patch("physbiblio.inspireStats.inspireStatsLoader.paperStats",
				return_value = {'aI': {1653464: {'date': datetime.datetime(2018, 2, 7, 4, 24, 2)}, 1662320: {'date': datetime.datetime(2018, 3, 14, 4, 53, 45)}, 1664547: {'date': datetime.datetime(2018, 3, 29, 5, 8, 58)}, 1663942: {'date': datetime.datetime(2018, 3, 26, 3, 25, 34)}, 1658582: {'date': datetime.datetime(2018, 3, 6, 3, 58, 52)}}, 'id': '1649081', 'citList': [[datetime.datetime(2018, 2, 7, 4, 24, 2), datetime.datetime(2018, 3, 6, 3, 58, 52), datetime.datetime(2018, 3, 14, 4, 53, 45), datetime.datetime(2018, 3, 26, 3, 25, 34), datetime.datetime(2018, 3, 29, 5, 8, 58), datetime.date(2018, 4, 16)], [1, 2, 3, 4, 5, 5]]}) as _mock:
			testGood = pBStats.authorStats("Stefano.Gariazzo.1", plot = True)
			for i in ['1253830', '1288846', '1292085', '1335389', '1347111', '1376456', '1385583', '1389136', '1399034', '1414175', '1418146', '1419638', '1422182', '1436472', '1467191', '1472072', '1489592', '1502879', '1508822', '1511397', '1515697', '1591119', '1608002', '1631308', '1641344', '1641345', '1642197', '1648424', '1649081', '1654819', '1667240']:
				self.assertIn(i, testGood["aI"].keys())
			_mock.assert_has_calls([call(i, paperDate = testGood["aI"][i]["date"], verbose = 0) for i in sorted(testGood["aI"].keys())])
			self.assertTrue(testGood.keys(), ['meanLi', 'allLi', 'aI', 'paLi', 'h', 'name'])
			self.assertTrue(testGood["h"], 4)
			self.assertTrue(testGood['name'], 'Stefano.Gariazzo.1')
			self.assertEqual(len(testGood['paLi'][0]), len(testGood["aI"]))
			self.assertEqual(len(testGood['paLi'][1]), len(testGood["aI"]))
			self.assertEqual(len(testGood['allLi'][0]), 5 * len(testGood["aI"]))
			self.assertEqual(len(testGood['allLi'][1]), 5 * len(testGood["aI"]))
			self.assertEqual(len(testGood['meanLi'][0]), 5 * len(testGood["aI"]))
			self.assertEqual(len(testGood['meanLi'][1]), 5 * len(testGood["aI"]))
			self.assertEqual(len(testGood['figs']), 6)
			for f in testGood["figs"]:
				self.assertIsInstance(f, matplotlib.figure.Figure)

if __name__=='__main__':
	unittest.main()
