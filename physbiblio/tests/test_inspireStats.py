#!/usr/bin/env python
"""Test file for the physbiblio.inspireStats module.

This file is part of the physbiblio package.
"""
import sys
import traceback
import os
import datetime
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
	print("Could not find physbiblio and its modules!")
	raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipTestsSettings.online, "Online tests")
class TestInspireStatsMethods(unittest.TestCase):
	"""Tests for methods in physbiblio.inspireStats"""
	@patch('sys.stdout', new_callable=StringIO)
	def assert_in_stdout(self, function, expected_output, mock_stdout):
		"""Catch and if test stdout of the function contains a string"""
		pBErrorManager.tempHandler(sys.stdout, format='%(message)s')
		function()
		pBErrorManager.rmTempHandler()
		self.assertIn(expected_output, mock_stdout.getvalue())

	def test_paperStats(self):
		"""Test paperStats function downloading real and fake data"""
		#not a valid record (it was cancelled):
		self.assertEqual(pBStats.paperStats("1358853"),
			{'aI': {}, 'citList': [[datetime.datetime.fromordinal(
				datetime.date.today().toordinal())], [0]],
				'id': '1358853'})

		#needs multiple pages to load all the content
		testGood = pBStats.paperStats("650592")
		self.assertTrue(testGood["id"], "650592")
		self.assertTrue(len(testGood["aI"])>950)
		self.assertEqual(len(testGood["aI"]) + 1,
			len(testGood["citList"][1]))
		self.assertEqual(len(testGood["citList"][0]),
			len(testGood["citList"][1]))
		self.assertFalse("fig" in testGood.keys())

		testGood = pBStats.paperStats("1385583", plot=True)
		self.assertTrue(testGood["id"], "1385583")
		self.assertTrue(len(testGood["aI"])>120)
		self.assertEqual(len(testGood["aI"]) + 1,
			len(testGood["citList"][1]))
		self.assertEqual(len(testGood["citList"][0]),
			len(testGood["citList"][1]))
		self.assertIsInstance(testGood["fig"], matplotlib.figure.Figure)

		testGood = pBStats.paperStats(["1358853", "1385583"])
		self.assertTrue(testGood["id"], ["1358853", "1385583"])
		self.assertTrue(len(testGood["aI"]) > 120)

	def test_authorStats(self):
		"""Test paperStats function downloading real and fake data"""
		with patch("physbiblio.inspireStats.InspireStatsLoader.paperStats",
				return_value={'aI':
				{1653464: {'date':
					datetime.datetime(2018, 2, 7, 4, 24, 2)},
				1662320: {'date': datetime.datetime(2018, 3, 14, 4, 53, 45)},
				1664547: {'date': datetime.datetime(2018, 3, 29, 5, 8, 58)},
				1663942: {'date': datetime.datetime(2018, 3, 26, 3, 25, 34)},
				1658582: {'date': datetime.datetime(2018, 3, 6, 3, 58, 52)}},
				'id': '1649081',
				'citList': [[datetime.datetime(2018, 2, 7, 4, 24, 2),
				datetime.datetime(2018, 3, 6, 3, 58, 52),
				datetime.datetime(2018, 3, 14, 4, 53, 45),
				datetime.datetime(2018, 3, 26, 3, 25, 34),
				datetime.datetime(2018, 3, 29, 5, 8, 58),
				datetime.date(2018, 4, 16)], [1, 2, 3, 4, 5, 5]]}) as _mock:
			testGood = pBStats.authorStats("E.M.Zavanin.1", plot=True)
			for i in ['1229039', '1345462', '1366180',
					'1385583', '1387736', '1404176',
					'1460832', '1519902']:
				self.assertIn(i, testGood["aI"].keys())
			_mock.assert_has_calls(
				[call(i, paperDate=testGood["aI"][i]["date"], verbose=0)
					for i in sorted(testGood["aI"].keys())])
			self.assertTrue(testGood.keys(),
				['meanLi', 'allLi', 'aI', 'paLi', 'h', 'name'])
			self.assertTrue(testGood["h"], 4)
			self.assertTrue(testGood['name'], 'E.M.Zavanin.1')
			self.assertEqual(len(testGood['paLi'][0]), len(testGood["aI"]))
			self.assertEqual(len(testGood['paLi'][1]), len(testGood["aI"]))
			self.assertEqual(len(testGood['allLi'][0]),
				5 * len(testGood["aI"]))
			self.assertEqual(len(testGood['allLi'][1]),
				5 * len(testGood["aI"]))
			self.assertEqual(len(testGood['meanLi'][0]),
				5 * len(testGood["aI"]))
			self.assertEqual(len(testGood['meanLi'][1]),
				5 * len(testGood["aI"]))
			self.assertEqual(len(testGood['figs']), 6)
			for f in testGood["figs"]:
				self.assertIsInstance(f, matplotlib.figure.Figure)

if __name__=='__main__':
	unittest.main()
