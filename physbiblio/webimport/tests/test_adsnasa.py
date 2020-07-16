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
    from physbiblio.webimport.adsnasa import WebSearch
    from physbiblio.webimport.webInterf import WebInterf, physBiblioWeb
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


class TestADSOnlineMethods(unittest.TestCase):
    """Test the functions that import entries from the ADS.
    Should not fail if everything works fine.
    """

    def test_init(self):
        """Test init and basic class properties"""
        ws = WebSearch()
        self.assertIsInstance(ws, WebInterf)
        self.assertTrue(hasattr(ws, "name"))
        self.assertTrue(hasattr(ws, "url"))
        self.assertTrue(hasattr(ws, "loadFields"))
        self.assertTrue(hasattr(ws, "fewFields"))
        self.assertIsInstance(physBiblioWeb.webSearch["adsnasa"], WebSearch)

    @unittest.skipIf(skipTestsSettings.online, "Online tests")
    def test_getGenericInfo(self):
        """Test getGenericInfo"""
        with patch("ads.SearchQuery", return_value=("abc", "def")) as _sq, patch(
            "logging.Logger.info"
        ) as _in, patch("logging.Logger.exception") as _ex, patch(
            "physbiblio.webimport.adsnasa.WebSearch.getLimitInfo",
            autospec=True,
            return_value="nolimit",
        ) as _gl:
            a = physBiblioWeb.webSearch["adsnasa"].getGenericInfo("star", ["bibcode"])
            self.assertEqual(a, ["abc", "def"])
            _sq.assert_called_once_with(
                q="star", fl=["bibcode"], rows=pbConfig.params["maxExternalAPIResults"]
            )
            self.assertEqual(_in.call_count, 1)
            self.assertEqual(_gl.call_count, 1)
            self.assertEqual(_ex.call_count, 0)
        with patch.dict(pbConfig.params, {"ADSToken": [""]}, clear=False), patch(
            "logging.Logger.exception"
        ) as _ex:
            a = physBiblioWeb.webSearch["adsnasa"].getGenericInfo("star", ["bibcode"])
            self.assertEqual(a, [])
            _ex.assert_called_once_with(
                "Unauthorized use of ADS API. Is your token valid?"
            )

    @unittest.skipIf(skipTestsSettings.online, "Online tests")
    def test_getBibtexs(self):
        """Test getBibtexs"""
        fr = MagicMock()
        fr.execute = MagicMock(return_value="exported")
        with patch("ads.ExportQuery", return_value=fr) as _eq, patch(
            "logging.Logger.info"
        ) as _in, patch("logging.Logger.exception") as _ex, patch(
            "physbiblio.webimport.adsnasa.WebSearch.getLimitInfo",
            autospec=True,
            return_value="nolimit",
        ) as _gl:
            a = physBiblioWeb.webSearch["adsnasa"].getBibtexs(["bibcode"])
            _eq.assert_called_once_with(bibcodes=["bibcode"], format="bibtex")
            _in.assert_called_once_with("nolimit")
            _gl.assert_called_once_with(physBiblioWeb.webSearch["adsnasa"])
            self.assertEqual(_ex.call_count, 0)
            fr.execute.assert_called_once_with()
            self.assertEqual(a, "exported")
        with patch.dict(pbConfig.params, {"ADSToken": [""]}, clear=False), patch(
            "logging.Logger.exception"
        ) as _ex:
            a = physBiblioWeb.webSearch["adsnasa"].getBibtexs(["bibcode"])
            self.assertEqual(a, "")
            _ex.assert_called_once_with(
                "Unauthorized use of ADS API. Is your token valid?"
            )

    def test_retrieveUrl(self):
        """Test retrieveUrlFirst and retrieveUrlAll"""
        a1 = MagicMock()
        a1.bibcode = "a1"
        a2 = MagicMock()
        a2.bibcode = "a2"
        with patch(
            "physbiblio.webimport.adsnasa.WebSearch.getGenericInfo",
            autospec=True,
            return_value=[a1, a2],
        ) as _ggi, patch(
            "physbiblio.webimport.adsnasa.WebSearch.getBibtexs",
            autospec=True,
            return_value="bibtex",
        ) as _gb:
            a = physBiblioWeb.webSearch["adsnasa"].retrieveUrlFirst("star")
            _ggi.assert_called_once_with(
                physBiblioWeb.webSearch["adsnasa"],
                "star",
                physBiblioWeb.webSearch["adsnasa"].fewFields,
            )
            _gb.assert_called_once_with(physBiblioWeb.webSearch["adsnasa"], "a1")
            self.assertEqual(a, "bibtex")
            _ggi.reset_mock()
            _gb.reset_mock()
            a = physBiblioWeb.webSearch["adsnasa"].retrieveUrlAll("star")
            _ggi.assert_called_once_with(
                physBiblioWeb.webSearch["adsnasa"],
                "star",
                physBiblioWeb.webSearch["adsnasa"].fewFields,
            )
            _gb.assert_called_once_with(
                physBiblioWeb.webSearch["adsnasa"], ["a1", "a2"]
            )
            self.assertEqual(a, "bibtex")
        with patch(
            "physbiblio.webimport.adsnasa.WebSearch.getGenericInfo",
            autospec=True,
            return_value=[],
        ) as _ggi, patch(
            "physbiblio.webimport.adsnasa.WebSearch.getBibtexs",
            autospec=True,
            return_value="abc",
        ) as _gb:
            a = physBiblioWeb.webSearch["adsnasa"].retrieveUrlFirst("star")
            self.assertEqual(a, "")
            a = physBiblioWeb.webSearch["adsnasa"].retrieveUrlAll("star")
            self.assertEqual(a, "abc")

    def test_getField(self):
        """Test getField"""
        pa = physBiblioWeb.webSearch["adsnasa"]
        a1 = MagicMock()
        a1.bibcode = "a1"
        a2 = MagicMock()
        a2.bibcode = "a2"
        with patch(
            "physbiblio.webimport.adsnasa.WebSearch.getGenericInfo",
            autospec=True,
            return_value=[a1, a2],
        ) as _ggi, patch("logging.Logger.warning") as _w:
            a = pa.getField("star", "bibcode")
            _ggi.assert_called_once_with(pa, "star", pa.loadFields)
            self.assertEqual(a, ["a1", "a2"])
            self.assertEqual(_w.call_count, 0)
            a = pa.getField("star", "somefield")
            _ggi.assert_called_once_with(pa, "star", pa.loadFields)
            self.assertEqual(a, [])
            _w.assert_called_once_with(
                "Invalid requested field in ADS query: somefield"
            )

    def test_getLimitInfo(self):
        """Test getLimitInfo"""
        pa = physBiblioWeb.webSearch["adsnasa"]
        pa.q = MagicMock()
        pa.q.response = MagicMock()
        pa.q.response.get_ratelimits = MagicMock(
            return_value={"limit": "a", "remaining": "123"}
        )
        self.assertEqual(pa.getLimitInfo(), "Remaining queries: 123/a")


if __name__ == "__main__":
    unittest.main()
