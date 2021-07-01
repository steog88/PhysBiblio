#!/usr/bin/env python
"""Test file for the physbiblio.webimport subpackage.

This file is part of the physbiblio package.
"""
import datetime
import json
import os
import sys
import traceback

from ads.tests.stubdata.export import example_export_response
from ads.tests.stubdata.solr import example_solr_response

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import MagicMock, patch
else:
    import unittest
    from unittest.mock import MagicMock, patch

try:
    from physbiblio.config import pbConfig
    from physbiblio.setuptests import *
    from physbiblio.strings.webimport import InspireStrings
    from physbiblio.webimport.inspire import WebSearch
    from physbiblio.webimport.webInterf import WebInterf, physBiblioWeb
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


class TestInspireOnlineMethods(unittest.TestCase):
    """Test the functions that import entries from the ADS.
    Should not fail if everything works fine.
    """

    def test_init(self):
        """Test init and basic class properties"""
        ws = WebSearch()
        self.assertIsInstance(ws, WebInterf)
        self.assertIsInstance(ws, InspireStrings)
        self.assertTrue(hasattr(ws, "name"))
        self.assertTrue(hasattr(ws, "description"))
        self.assertTrue(hasattr(ws, "url"))
        self.assertTrue(hasattr(ws, "urlRecord"))
        self.assertTrue(hasattr(ws, "correspondences"))
        self.assertTrue(hasattr(ws, "bibtexFields"))
        self.assertTrue(hasattr(ws, "metadataLiteratureFields"))
        self.assertTrue(hasattr(ws, "metadataConferenceFields"))
        self.assertTrue(hasattr(ws, "urlArgs"))
        self.assertTrue(hasattr(ws, "defaultSize"))
        self.assertIsInstance(physBiblioWeb.webSearch["inspire"], WebSearch)

    # @unittest.skipIf(skipTestsSettings.online, "Online tests")
    def test_retrieveBibtex(self):
        """Test retrieveBibtex"""
        iws = physBiblioWeb.webSearch["inspire"]
        args = iws.urlArgs.copy()
        args["q"] = "abc"
        args["size"] = "250"
        args["format"] = "bibtex"
        with patch(
            "physbiblio.webimport.inspire.parse_accents_str",
            side_effect=KeyError("exc"),
        ) as _pa, patch(
            "physbiblio.webimport.webInterf.WebInterf.createUrl",
            return_value="mycurrenturl",
        ) as _cu, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            return_value="some output text",
        ) as _tu, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "logging.Logger.exception"
        ) as _e:
            self.assertEqual(iws.retrieveBibtex("abc"), "")
            _cu.assert_called_once_with(args)
            _i.assert_called_once_with(iws.searchInfo % ("abc", "mycurrenturl"))
            _tu.assert_called_once_with("mycurrenturl")
            _pa.assert_called_once_with("some output text")
            _e.assert_called_once_with(iws.genericError)
        args["q"] = "ab%20c"
        args["size"] = "12"
        with patch(
            "physbiblio.webimport.inspire.parse_accents_str", return_value="1234"
        ) as _pa, patch(
            "physbiblio.webimport.webInterf.WebInterf.createUrl",
            return_value="mycurrenturl",
        ) as _cu, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            return_value="some output text",
        ) as _tu, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "logging.Logger.exception"
        ) as _e:
            self.assertEqual(iws.retrieveBibtex("ab c", size=12), "1234")
            _cu.assert_called_once_with(args)
            _i.assert_called_once_with(iws.searchInfo % ("ab c", "mycurrenturl"))
            _tu.assert_called_once_with("mycurrenturl")
            _pa.assert_called_once_with("some output text")
            self.assertEqual(_e.call_count, 0)

    def test_retrieveUrlFirst(self):
        """Test retrieveUrlFirst"""
        with patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveBibtex", return_value="def"
        ) as _f:
            self.assertEqual(
                physBiblioWeb.webSearch["inspire"].retrieveUrlFirst("abc"), "def"
            )
            _f.assert_called_once_with("abc", size=1)

    def test_retrieveUrlAll(self):
        """Test retrieveUrlAll"""
        with patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveBibtex", return_value="def"
        ) as _f:
            self.assertEqual(
                physBiblioWeb.webSearch["inspire"].retrieveUrlAll("abc"), "def"
            )
            _f.assert_called_once_with(
                "abc", size=physBiblioWeb.webSearch["inspire"].defaultSize
            )

    def test_retrieveAPIResults(self):
        """Test retrieveAPIResults"""
        raise NotImplementedError

    def test_retrieveSearchResults(self):
        """Test retrieveSearchResults"""
        raise NotImplementedError

    def test_retrieveInspireID(self):
        """Test retrieveInspireID"""
        raise NotImplementedError

    def test_retrieveCumulativeUpdates(self):
        """Test retrieveCumulativeUpdates"""
        raise NotImplementedError

    def test_retrieveOAIData(self):
        """Test retrieveOAIData"""
        raise NotImplementedError

    def test_readRecord(self):
        """Test readRecord"""
        raise NotImplementedError

    def test_updateBibtex(self):
        """Test updateBibtex"""
        raise NotImplementedError


if __name__ == "__main__":
    unittest.main()
