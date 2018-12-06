#!/usr/bin/env python
"""Test file for the physbiblio.view module.

This file is part of the physbiblio package.
"""
import sys
import traceback

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
	print("Could not find physbiblio and its modules!")
	raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipTestsSettings.long, "Long tests")
class TestViewMethods(unittest.TestCase):
	"""Tests for methods in physbiblio.view"""
	def test_getLink(self):
		"""Test getLink function with different inputs"""
		with patch('physbiblio.database.Entries.getField', side_effect=[
				'1507.08204', '', '', '1507.08204', #test "arxiv"
				'', '10.1088/0954-3899/43/3/033001',
					'', '10.1088/0954-3899/43/3/033001', #test "doi"
				'', '', '1385583', #test "inspire", inspire ID present
				'1507.08204', '', '', #test "inspire",
					# inspire ID not present, arxiv present
				'', '', False, #test "inspire",
					# inspire ID not present, arxiv not present
				'', '', '', #test "arxiv", no info
				'', '', '', #test "doi", no info
				]) as _mock:
			self.assertEqual(pBView.getLink("a", "arxiv"),
				"%s/abs/1507.08204"%pbConfig.arxivUrl)
			self.assertEqual(pBView.getLink("a", "doi"),
				"%s10.1088/0954-3899/43/3/033001"%pbConfig.doiUrl)
			self.assertEqual(pBView.getLink("a", "inspire"),
				"https://inspirehep.net/record/1385583")
			self.assertEqual(pBView.getLink("a", "inspire"),
				"https://inspirehep.net/search?p=find+1507.08204")
			self.assertEqual(pBView.getLink("a", "inspire"),
				"https://inspirehep.net/search?p=find+a")
			self.assertFalse(pBView.getLink("a", "arxiv"))
			self.assertFalse(pBView.getLink("a", "doi"))

if __name__=='__main__':
	unittest.main()
