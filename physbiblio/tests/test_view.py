#!/usr/bin/env python
"""
Test file for the physbiblio.view module.

This file is part of the physbiblio package.
"""
import sys, traceback

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch
else:
	import unittest
	from unittest.mock import patch

try:
	from physbiblio.setuptests import *
	from physbiblio.config import pbConfig
	from physbiblio.database import pBDB
	from physbiblio.view import pBView
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipLongTests, "Long tests")
class TestViewMethods(unittest.TestCase):
	"""Tests for methods in physbiblio.view"""
	def test_getLink(self):
		"""Test getLink function with different inputs"""
		with patch('physbiblio.database.entries.getField', side_effect = [
				'1507.08204', '', '', '1507.08204', #test "arxiv"
				'', '10.1088/0954-3899/43/3/033001', '', '10.1088/0954-3899/43/3/033001', #test "doi"
				'', '', '1385583', #test "inspire", inspire ID present
				'1507.08204', '', '', #test "inspire", inspire ID not present, arxiv present
				'', '', False, #test "inspire", inspire ID not present, arxiv not present
				'', '', '', #test "arxiv", no info
				'', '', '', #test "doi", no info
				]) as _mock:
			self.assertEqual(pBView.getLink("a", "arxiv"), "http://arxiv.org/abs/1507.08204")
			self.assertEqual(pBView.getLink("a", "doi"), "http://dx.doi.org/10.1088/0954-3899/43/3/033001")
			self.assertEqual(pBView.getLink("a", "inspire"), "http://inspirehep.net/record/1385583")
			self.assertEqual(pBView.getLink("a", "inspire"), "http://inspirehep.net/search?p=find+1507.08204")
			self.assertEqual(pBView.getLink("a", "inspire"), "http://inspirehep.net/search?p=find+a")
			self.assertFalse(pBView.getLink("a", "arxiv"))
			self.assertFalse(pBView.getLink("a", "doi"))

if __name__=='__main__':
	unittest.main()
