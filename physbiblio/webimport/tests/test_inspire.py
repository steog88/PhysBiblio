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


class TestInspireMethods(unittest.TestCase):
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
        iws = physBiblioWeb.webSearch["inspire"]
        with patch("logging.Logger.info") as _i:
            self.assertEqual(iws.retrieveAPIResults(""), ([], 0))
            self.assertEqual(iws.retrieveAPIResults(None), ([], 0))
            self.assertEqual(_i.call_count, 0)
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch("logging.Logger.exception") as _e, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            return_value="",
        ) as _tu:
            self.assertEqual(iws.retrieveAPIResults("abcd"), ([], 0))
            _tu.assert_called_once_with("abcd")
            _i.assert_any_call(iws.searchResultsFrom % "abcd")
            _w.assert_called_once_with(iws.errorEmptyText)
            self.assertEqual(_e.call_count, 0)
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch("logging.Logger.exception") as _e, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            return_value=None,
        ) as _tu:
            self.assertEqual(iws.retrieveAPIResults("abcd"), ([], 0))
            _i.assert_any_call(iws.searchResultsFrom % "abcd")
            _tu.assert_called_once_with("abcd")
            _w.assert_called_once_with(iws.errorEmptyText)
            self.assertEqual(_e.call_count, 0)
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch("logging.Logger.exception") as _e, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            return_value="['abcd'",
        ) as _tu:
            self.assertEqual(iws.retrieveAPIResults("abcd"), ([], 0))
            _i.assert_called_once_with(iws.searchResultsFrom % "abcd")
            _tu.assert_called_once_with("abcd")
            _e.assert_called_once_with(iws.jsonError)
            self.assertEqual(_w.call_count, 0)
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch("logging.Logger.exception") as _e, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            side_effect=[
                '{"hits":{"hits":["abc"], "total":1}, "links":{"next":"efgh"}}',
                None,
            ],
        ) as _tu:
            self.assertEqual(iws.retrieveAPIResults("abcd"), (["abc"], 1))
            _i.assert_any_call(iws.searchResultsFrom % "abcd")
            _i.assert_any_call(iws.searchResultsFrom % "efgh")
            _tu.assert_any_call("abcd")
            _tu.assert_any_call("efgh")
            _w.assert_called_once_with(iws.errorEmptyText)
            self.assertEqual(_e.call_count, 0)
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch("logging.Logger.exception") as _e, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            side_effect=[
                '{"hits":{"hits":["abc"], "total":4}, "links":{"next":"efgh"}}',
                '{"hits":{"hits":["def", "ghi"], "total":2}}',
            ],
        ) as _tu:
            self.assertEqual(iws.retrieveAPIResults("abcd"), (["abc", "def", "ghi"], 4))
            _i.assert_any_call(iws.searchResultsFrom % "abcd")
            _i.assert_any_call(iws.searchResultsFrom % "efgh")
            _tu.assert_any_call("abcd")
            _tu.assert_any_call("efgh")
            self.assertEqual(_e.call_count, 0)
            self.assertEqual(_w.call_count, 0)
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch("logging.Logger.exception") as _e, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            return_value='{"id":"aA","hits":4}',
        ) as _tu:
            self.assertEqual(
                iws.retrieveAPIResults("abcd"),
                (
                    [{"id": "aA", "hits": 4}],
                    1,
                ),
            )
            _i.assert_called_once_with(iws.searchResultsFrom % "abcd")
            _tu.assert_called_once_with("abcd")
            self.assertEqual(_e.call_count, 0)
            self.assertEqual(_w.call_count, 0)
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch("logging.Logger.exception") as _e, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            return_value='{"message":"bla","status":"404", "id": "aA","hits":{"hits":["abc"], "total":4}, "links":{"next":"efgh"}}',
        ) as _tu:
            self.assertEqual(iws.retrieveAPIResults("abcd"), ([], 0))
            _i.assert_called_once_with(iws.searchResultsFrom % "abcd")
            _tu.assert_called_once_with("abcd")
            _e.assert_called_once_with(iws.apiResponseError % ("404", "bla"))
            self.assertEqual(_w.call_count, 0)
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch("logging.Logger.exception") as _e, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            return_value='{"hits":{"hits":["abc"], "total":4}, "links":{"next":"abcd"}}',
        ) as _tu:
            self.assertEqual(iws.retrieveAPIResults("abcd"), (["abc"] * 20, 4))
            _i.assert_any_call(iws.searchResultsFrom % "abcd")
            _tu.assert_any_call("abcd")
            self.assertEqual(_i.call_count, 20)
            self.assertEqual(_tu.call_count, 20)
            self.assertEqual(_e.call_count, 0)
            self.assertEqual(_w.call_count, 0)
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch("logging.Logger.exception") as _e, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            return_value='{"hits":{"hits":["abc"], "total":4}, "links":{"next":"abcd"}}',
        ) as _tu:
            self.assertEqual(
                iws.retrieveAPIResults("abcd", max_iterations=10), (["abc"] * 10, 4)
            )
            _i.assert_any_call(iws.searchResultsFrom % "abcd")
            _tu.assert_any_call("abcd")
            self.assertEqual(_i.call_count, 10)
            self.assertEqual(_tu.call_count, 10)
            self.assertEqual(_e.call_count, 0)
            self.assertEqual(_w.call_count, 0)

    def test_retrieveSearchResults(self):
        """Test retrieveSearchResults"""
        iws = physBiblioWeb.webSearch["inspire"]
        self.assertIn("page", iws.urlArgs.keys())
        args = iws.urlArgs.copy()
        del args["page"]
        args["q"] = "ab%20c"
        args["size"] = "500"
        args["fields"] = ",".join(iws.metadataLiteratureFields)
        with patch(
            "physbiblio.webimport.webInterf.WebInterf.createUrl",
            return_value="mycurrenturl",
        ) as _cu, patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveAPIResults",
            return_value="output",
        ) as _rar:
            self.assertEqual(iws.retrieveSearchResults("ab c"), "output")
            _cu.assert_called_once_with(args)
            _rar.assert_called_once_with("mycurrenturl", max_iterations=20)
            args["q"] = "abc"
            args["size"] = "1000"
            args["fields"] = ",".join(["a", "b"])
            self.assertEqual(
                iws.retrieveSearchResults("abc", size=1111, fields=["a", "b"]), "output"
            )
            _cu.assert_any_call(args)
            _rar.assert_any_call("mycurrenturl", max_iterations=20)
            args["size"] = "200"
            args["fields"] = ",".join(iws.metadataLiteratureFields + ["a", "b"])
            self.assertEqual(
                iws.retrieveSearchResults(
                    "abc", size=200, addfields=["a", "b"], max_iterations=2
                ),
                "output",
            )
            _cu.assert_any_call(args)
            _rar.assert_any_call("mycurrenturl", max_iterations=2)

    def test_retrieveInspireID(self):
        """Test retrieveInspireID"""
        iws = physBiblioWeb.webSearch["inspire"]
        args = iws.urlArgs.copy()
        args["size"] = "1"
        args["fields"] = "control_number"
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch("logging.Logger.exception") as _e, patch(
            "physbiblio.webimport.webInterf.WebInterf.createUrl",
            return_value="mycurrenturl",
        ) as _cu, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            side_effect=[
                "",
                '["abc"',
                '{"hits":{"hits":[{"metadata":{"abc":1}}], "total":4}}',
                '{"hits":{"hits":[{"metadata":{"control_number":123}}], "total":4}}',
            ],
        ) as _tu:
            self.assertEqual(iws.retrieveInspireID("ab c"), "")
            args["q"] = "ab%20c"
            _cu.assert_called_once_with(args)
            _tu.assert_called_once_with("mycurrenturl")
            _w.assert_called_once_with(iws.errorEmptyText)
            del args["page"]
            self.assertEqual(iws.retrieveInspireID("ab c", number=0), "")
            _cu.assert_any_call(args)
            _e.assert_called_once_with(iws.jsonError)
            args["page"] = 2
            self.assertEqual(iws.retrieveInspireID("ab c", number=2), "")
            _cu.assert_any_call(args)
            _e.assert_any_call(iws.genericError)
            del args["page"]
            self.assertEqual(iws.retrieveInspireID("ab c"), "123")
            _cu.assert_any_call(args)

    @unittest.skipIf(skipTestsSettings.online, "Online tests")
    def test_retrieveInspireID_online(self):
        """Online test retrieveInspireID"""
        iws = physBiblioWeb.webSearch["inspire"]
        test = [
            ["Gariazzo:2015rra", u"1385583", {}],
            ["10.1088/0954-3899/43/3/033001", u"1385583", {"isDoi": True}],
            ["1507.08204", u"1385583", {"isArxiv": True}],
            ["arxiv:1507.08204", u"1385583", {"isArxiv": True}],
        ]
        for q in test:
            self.assertEqual(iws.retrieveInspireID(q[0], **q[2]), q[1])
        self.assertEqual(
            iws.retrieveInspireID("oWBWESFLkasjdnaksjae12314161AEHWBV"),
            "",
        )

    def test_retrieveCumulativeUpdates(self):
        """Test retrieveCumulativeUpdates"""
        iws = physBiblioWeb.webSearch["inspire"]
        d1 = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
        d2 = (datetime.date.today()).strftime("%Y-%m-%d")
        with patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveSearchResults",
            return_value=([], 0),
        ) as _s, patch(
            "physbiblio.webimport.inspire.WebSearch.readRecord", return_value={"k": "a"}
        ) as _r, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.exception"
        ) as _e:
            res = iws.retrieveCumulativeUpdates(
                d1,
                d2,
                max_iterations=2,
            )
            self.assertEqual(res, [])
            _s.assert_called_once_with(
                "du%3E%3D" + d1 + " and du%3C%3D" + d2, max_iterations=2
            )
            self.assertEqual(_r.call_count, 0)
        hits = [
            {"metadata": {"control_number": 123}},
            {"metadata": {"control_number": 456}},
            {"metadata": {"control_number": 789}},
        ]
        with patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveSearchResults",
            return_value=(hits, 2),
        ) as _s, patch(
            "physbiblio.webimport.inspire.WebSearch.readRecord",
            side_effect=[{"k": "a"}, {"k": "b"}, {"k": "c"}],
        ) as _r, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.exception"
        ) as _e:
            res = iws.retrieveCumulativeUpdates(
                d1,
                d2,
                max_iterations=2,
            )
            self.assertEqual(
                res,
                [{"k": "a", "id": 123}, {"k": "b", "id": 456}, {"k": "c", "id": 789}],
            )
            _s.assert_called_once_with(
                "du%3E%3D" + d1 + " and du%3C%3D" + d2, max_iterations=2
            )
            for h in hits:
                _r.assert_any_call(h)

    @unittest.skipIf(skipTestsSettings.online, "Online tests")
    def test_retrieveCumulativeUpdates_online(self):
        """Online test retrieveCumulativeUpdates"""
        physBiblioWeb.webSearch["inspire"].retrieveCumulativeUpdates(
            (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d"),
            (datetime.date.today()).strftime("%Y-%m-%d"),
            max_iterations=2,
        )

    def test_retrieveOAIData(self):
        """Test retrieveOAIData"""
        iws = physBiblioWeb.webSearch["inspire"]
        with patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveAPIResults",
            return_value=([], 0),
        ) as _s, patch(
            "physbiblio.webimport.inspire.WebSearch.readRecord", return_value={"k": "a"}
        ) as _r, patch(
            "physbiblio.webimport.inspire.WebSearch.updateBibtex", return_value=True
        ) as _u, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.exception"
        ) as _e:
            self.assertFalse(iws.retrieveOAIData("abc"))
            _s.assert_called_once_with("%sabc" % iws.url)
            _e.assert_called_once_with(iws.errorEmptySearch)
            self.assertEqual(_r.call_count, 0)
            self.assertEqual(_u.call_count, 0)
        with patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveAPIResults",
            return_value=([{"ABC": "abc"}], 0),
        ) as _s, patch(
            "physbiblio.webimport.inspire.WebSearch.readRecord",
            side_effect=Exception("abc"),
        ) as _r, patch(
            "physbiblio.webimport.inspire.WebSearch.updateBibtex", return_value=True
        ) as _u, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.exception"
        ) as _e:
            self.assertFalse(iws.retrieveOAIData("abc"))
            _s.assert_called_once_with("%sabc" % iws.url)
            _r.assert_called_once_with({"ABC": "abc"}, readConferenceTitle=False)
            _e.assert_called_once_with(iws.errorReadRecord)
            self.assertEqual(_u.call_count, 0)
        with patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveAPIResults",
            return_value=([{"ABC": "abc"}], 0),
        ) as _s, patch(
            "physbiblio.webimport.inspire.WebSearch.readRecord", return_value={"k": "a"}
        ) as _r, patch(
            "physbiblio.webimport.inspire.WebSearch.updateBibtex", return_value=True
        ) as _u, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.exception"
        ) as _e:
            self.assertEqual(iws.retrieveOAIData("abc"), {"k": "a"})
            _s.assert_called_once_with("%sabc" % iws.url)
            self.assertEqual(_e.call_count, 0)
            _r.assert_called_once_with({"ABC": "abc"}, readConferenceTitle=False)
            self.assertFalse(iws.retrieveOAIData("abc", bibtex="bibtex"))
            _e.assert_called_once_with(iws.errorUpdateBibtex)
            _u.assert_called_once_with({"k": "a"}, "bibtex")
        with patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveAPIResults",
            return_value=([{"ABC": "abc"}], 0),
        ) as _s, patch(
            "physbiblio.webimport.inspire.WebSearch.readRecord", return_value={"k": "a"}
        ) as _r, patch(
            "physbiblio.webimport.inspire.WebSearch.updateBibtex",
            return_value=(True, "mybibtex"),
        ) as _u, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.exception"
        ) as _e:
            self.assertEqual(iws.retrieveOAIData("abc"), {"k": "a"})
            _s.assert_called_once_with("%sabc" % iws.url)
            self.assertEqual(_e.call_count, 0)
            _r.assert_called_once_with({"ABC": "abc"}, readConferenceTitle=False)
            self.assertEqual(_u.call_count, 0)
            res = iws.retrieveOAIData("abc", bibtex="bibtex")
            self.assertEqual(res, {"k": "a", "bibtex": "mybibtex"})
            self.assertEqual(_e.call_count, 0)
            _u.assert_called_once_with(res, "bibtex")
        with patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveAPIResults",
            return_value=([{"ABC": "abc"}], 0),
        ) as _s, patch(
            "physbiblio.webimport.inspire.WebSearch.readRecord", return_value={"k": "a"}
        ) as _r, patch(
            "physbiblio.webimport.inspire.WebSearch.updateBibtex",
            return_value=(False, "mybibtex"),
        ) as _u, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.exception"
        ) as _e:
            self.assertEqual(iws.retrieveOAIData("abc"), {"k": "a"})
            _s.assert_called_once_with("%sabc" % iws.url)
            self.assertEqual(_e.call_count, 0)
            _r.assert_called_once_with({"ABC": "abc"}, readConferenceTitle=False)
            self.assertEqual(_u.call_count, 0)
            res = iws.retrieveOAIData("abc", bibtex="bibtex")
            self.assertEqual(res, {"k": "a"})
            self.assertEqual(_e.call_count, 0)
            _u.assert_called_once_with(res, "bibtex")

    def test_readRecord(self):
        """Test readRecord"""
        raise NotImplementedError

    def test_updateBibtex(self):
        """Test updateBibtex"""
        raise NotImplementedError


if __name__ == "__main__":
    unittest.main()
