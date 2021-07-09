#!/usr/bin/env python
"""Test file for the physbiblio.webimport subpackage.

This file is part of the physbiblio package.
"""
import datetime
import sys
import traceback

import bibtexparser
import six

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import MagicMock, patch
else:
    import unittest
    from unittest.mock import MagicMock, patch

try:
    from physbiblio.bibtexWriter import pbWriter
    from physbiblio.config import pbConfig
    from physbiblio.setuptests import *
    from physbiblio.strings.webimport import ArxivStrings
    from physbiblio.webimport.arxiv import WebSearch
    from physbiblio.webimport.webInterf import WebInterf, physBiblioWeb
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


class TestArxivMethods(unittest.TestCase):
    """Test the functions that import entries from arxiv.
    Should not fail if everything works fine.
    """

    def test_init(self):
        """Test init and basic class properties"""
        ws = WebSearch()
        self.assertIsInstance(ws, WebInterf)
        self.assertIsInstance(ws, ArxivStrings)
        self.assertTrue(hasattr(ws, "name"))
        self.assertTrue(hasattr(ws, "description"))
        self.assertTrue(hasattr(ws, "url"))
        self.assertTrue(hasattr(ws, "urlRss"))
        self.assertTrue(hasattr(ws, "categories"))
        self.assertIsInstance(ws.categories, dict)
        for k, v in ws.categories.items():
            self.assertIsInstance(v, list)
        self.assertTrue(hasattr(ws, "urlArgs"))
        self.assertIsInstance(physBiblioWeb.webSearch["arxiv"], WebSearch)

    def test_getYear(self):
        """test getYear"""
        aws = physBiblioWeb.webSearch["arxiv"]
        with patch("physbiblio.webimport.arxiv.getYear", return_value="abc") as _g:
            self.assertEqual(aws.getYear("AAA"), "abc")
            _g.assert_called_once_with("AAA")
        with patch("logging.Logger.warning") as _w:
            self.assertEqual(aws.getYear("123456"), None)
            self.assertEqual(aws.getYear("abcde"), None)
            self.assertEqual(aws.getYear(None), None)
            _w.assert_called_once()
            self.assertEqual(aws.getYear("hep-ex/1234567"), "2012")
            self.assertEqual(aws.getYear("hep-ph/9876543"), "1998")
            self.assertEqual(aws.getYear("hep-ex/1234567 hep-ex/9876543"), "2012")
            self.assertEqual(aws.getYear("astro-ph/9876543 hep-ex/1234567"), "1998")
            self.assertEqual(aws.getYear("9876543 hep-ex/1234567"), "2012")
            self.assertEqual(aws.getYear("hep-ph/9876543"), "1998")
            self.assertEqual(aws.getYear("151234567 hep-ph/9876543"), "1998")
            self.assertEqual(aws.getYear("1512.34567 1234567"), "2015")
            self.assertEqual(aws.getYear("astro-ph/1234.34567 1234567"), "2012")
            self.assertEqual(aws.getYear("1512.34567 1234567"), "2015")
            self.assertEqual(aws.getYear("1301.0001 2005.12345"), "2013")
            self.assertEqual(aws.getYear("0001.0001"), "2000")

    def test_retrieveUrlFirst(self):
        """test retrieveUrlFirst"""
        aws = physBiblioWeb.webSearch["arxiv"]
        with patch(
            "physbiblio.webimport.arxiv.WebSearch.arxivRetriever", return_value="abc"
        ) as _g:
            self.assertEqual(aws.retrieveUrlAll("AAA"), "abc")
            _g.assert_called_once_with(
                "AAA",
                "all",
                additionalArgs={
                    "max_results": pbConfig.params["maxExternalAPIResults"]
                },
            )
            self.assertEqual(aws.retrieveUrlAll("AAA", searchType="boh"), "abc")
            _g.assert_called_with(
                "AAA",
                "boh",
                additionalArgs={
                    "max_results": pbConfig.params["maxExternalAPIResults"]
                },
            )

    def test_retrieveUrlAll(self):
        """test retrieveUrlAll"""
        aws = physBiblioWeb.webSearch["arxiv"]
        with patch(
            "physbiblio.webimport.arxiv.WebSearch.arxivRetriever", return_value="abc"
        ) as _g:
            self.assertEqual(aws.retrieveUrlFirst("AAA"), "abc")
            _g.assert_called_once_with(
                "AAA", "all", additionalArgs={"max_results": "1"}
            )
            self.assertEqual(aws.retrieveUrlFirst("AAA", searchType="boh"), "abc")
            _g.assert_called_with("AAA", "boh", additionalArgs={"max_results": "1"})

    def test_arxivRetriever(self):
        """test arxivRetriever"""
        aws = physBiblioWeb.webSearch["arxiv"]
        raise NotImplementedError

    @unittest.skipIf(skipTestsSettings.online, "Online tests")
    def test_arxivRetriever_online(self):
        """Online test arxivRetriever"""
        aws = physBiblioWeb.webSearch["arxiv"]
        with patch("logging.Logger.debug") as _d:
            res = aws.arxivRetriever("Zavanin", searchType="au")
        self.assertIsInstance(res, six.string_types)

    def test_arxivDaily(self):
        """test arxivDaily"""
        aws = physBiblioWeb.webSearch["arxiv"]
        raise NotImplementedError

    @unittest.skipIf(skipTestsSettings.online, "Online tests")
    def test_arxivDaily_online(self):
        """Online test arxivDaily"""
        aws = physBiblioWeb.webSearch["arxiv"]
        res = aws.arxivDaily("astro-ph.CO")
        self.assertIsInstance(res, list)


if __name__ == "__main__":
    unittest.main()
