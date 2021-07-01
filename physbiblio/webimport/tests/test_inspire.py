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
        self.assertIsInstance(physBiblioWeb.webSearch["inspire"], WebSearch)

    # @unittest.skipIf(skipTestsSettings.online, "Online tests")
    def test_retrieveBibtex(self):
        """Test retrieveBibtex"""
        raise NotImplementedError

    def test_retrieveUrlFirst(self):
        """Test retrieveUrlFirst"""
        raise NotImplementedError

    def test_retrieveUrlAll(self):
        """Test retrieveUrlAll"""
        raise NotImplementedError

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
