#!/usr/bin/env python
"""Test file for the physbiblio.webimport subpackage.

This file is part of the physbiblio package.
"""
import datetime
import sys
import traceback

import bibtexparser

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
    from physbiblio.strings.webimport import InspireStrings
    from physbiblio.webimport.inspire import WebSearch
    from physbiblio.webimport.webInterf import WebInterf, physBiblioWeb
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


class TestInspireMethods(unittest.TestCase):
    """Test the functions that import entries from INSPIRE.
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
        self.assertTrue(hasattr(ws, "updateBibtexFields"))
        self.assertTrue(hasattr(ws, "metadataLiteratureFields"))
        self.assertTrue(hasattr(ws, "metadataConferenceFields"))
        self.assertTrue(hasattr(ws, "metadataCitationFields"))
        self.assertTrue(hasattr(ws, "urlArgs"))
        self.assertTrue(hasattr(ws, "defaultSize"))
        self.assertIsInstance(physBiblioWeb.webSearch["inspire"], WebSearch)

    def test_fixAccents(self):
        """Test _fixAccents"""
        iws = physBiblioWeb.webSearch["inspire"]
        self.assertEqual(iws._fixAccents("abc"), "abc")
        self.assertEqual(iws._fixAccents(r"ab\"c"), r"ab{\"c}")
        self.assertEqual(iws._fixAccents(r"\"Abc\"0def\"G"), r"{\"A}bc\"0def{\"G}")

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
        with patch(
            "physbiblio.webimport.inspire.parse_accents_str", return_value="1234"
        ) as _pa, patch(
            "physbiblio.webimport.webInterf.WebInterf.createUrl",
            return_value="mycurrenturl",
        ) as _cu, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            return_value=r"some o\"utput text",
        ) as _tu, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "logging.Logger.exception"
        ) as _e:
            self.assertEqual(iws.retrieveBibtex("ab c", size=12), "1234")
            _cu.assert_called_once_with(args)
            _i.assert_called_once_with(iws.searchInfo % ("ab c", "mycurrenturl"))
            _tu.assert_called_once_with("mycurrenturl")
            _pa.assert_called_once_with(r"some o{\"u}tput text")
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
            return_value='{"message":"bla","status":"404", "id": "aA",'
            + '"hits":{"hits":["abc"], "total":4},'
            + ' "links":{"next":"efgh"}}',
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

    def test_retrieveBatchQuery(self):
        """test retrieveBatchQuery"""
        iws = physBiblioWeb.webSearch["inspire"]
        with patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveSearchResults",
            return_value="output",
        ) as _rsr:
            self.assertEqual(iws.retrieveBatchQuery(["123", "456", "789"]), "output")
            _rsr.assert_called_once_with("123 or 456 or 789")
            _rsr.reset_mock()
            self.assertEqual(
                iws.retrieveBatchQuery(["123", "456", "789"], searchFormat="recid:%s"),
                "output",
            )
            _rsr.assert_called_once_with("recid:123 or recid:456 or recid:789")
            _rsr.reset_mock()
            self.assertEqual(
                iws.retrieveBatchQuery(["123", "", "789"], searchFormat="recid:%s"),
                "output",
            )
            _rsr.assert_called_once_with("recid:123 or recid:789")
            _rsr.reset_mock()
            self.assertEqual(
                iws.retrieveBatchQuery(["123", "asd", None], searchFormat="filter:%s"),
                "output",
            )
            _rsr.assert_called_once_with("filter:123 or filter:asd")
            _rsr.reset_mock()
            self.assertEqual(
                iws.retrieveBatchQuery(
                    ["De:2011abc", "Da:456", "Xe:789"], searchFormat="texkeys:%s"
                ),
                "output",
            )
            _rsr.assert_called_once_with(
                "texkeys:De:2011abc or texkeys:Da:456 or texkeys:Xe:789"
            )
            _rsr.reset_mock()
            self.assertEqual(
                iws.retrieveBatchQuery(["De:2011abc", "Da:456", "Xe:789"]), "output"
            )
            _rsr.assert_called_once_with("texkeys:De:2011abc or Da:456 or Xe:789")
            _rsr.reset_mock()
            self.assertEqual(
                iws.retrieveBatchQuery(["De:2011abc", 456, "Xe:789"]), "output"
            )
            _rsr.assert_called_once_with("De:2011abc or 456 or Xe:789")
            _rsr.reset_mock()
            self.assertEqual(
                iws.retrieveBatchQuery(["De:2011abc", "456", None]), "output"
            )
            _rsr.assert_called_once_with("texkeys:De:2011abc or 456")

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
                [
                    {"k": "a", "id": "123"},
                    {"k": "b", "id": "456"},
                    {"k": "c", "id": "789"},
                ],
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

    def test_processRecord(self):
        """test processRecord"""
        iws = physBiblioWeb.webSearch["inspire"]
        with patch(
            "physbiblio.webimport.inspire.WebSearch.readRecord",
            side_effect=Exception("abc"),
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
            self.assertFalse(iws.processRecord("abc"))
            _r.assert_called_once_with("abc", readConferenceTitle=False)
            _e.assert_called_once_with(iws.errorReadRecord)
        with patch(
            "physbiblio.webimport.inspire.WebSearch.readRecord",
            return_value={"k": "a"},
        ) as _r, patch(
            "physbiblio.webimport.inspire.WebSearch.updateBibtex",
            side_effect=Exception("def"),
        ) as _u, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.exception"
        ) as _e:
            self.assertEqual(iws.processRecord("abc"), {"k": "a"})
            self.assertEqual(_e.call_count, 0)
            _r.assert_called_once_with("abc", readConferenceTitle=False)
            self.assertEqual(iws.processRecord("abc", bibtex="bibtex"), False)
            _e.assert_called_once_with(iws.errorUpdateBibtex)
            _u.assert_called_once_with({"k": "a"}, "bibtex")
        with patch(
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
            self.assertEqual(iws.processRecord("abc"), {"k": "a"})
            self.assertEqual(_e.call_count, 0)
            _r.assert_called_once_with("abc", readConferenceTitle=False)
            self.assertEqual(_u.call_count, 0)
            res = iws.processRecord("abc", bibtex="bibtex")
            self.assertEqual(res, {"k": "a", "bibtex": "mybibtex"})
            self.assertEqual(_e.call_count, 0)
            _u.assert_called_once_with(res, "bibtex")
        with patch(
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
            self.assertEqual(iws.processRecord("abc"), {"k": "a"})
            self.assertEqual(_e.call_count, 0)
            _r.assert_called_once_with("abc", readConferenceTitle=False)
            self.assertEqual(_u.call_count, 0)
            res = iws.processRecord("abc", bibtex="bibtex")
            self.assertEqual(res, {"k": "a"})
            self.assertEqual(_e.call_count, 0)
            _u.assert_called_once_with(res, "bibtex")

    def test_retrieveOAIData(self):
        """Test retrieveOAIData"""
        iws = physBiblioWeb.webSearch["inspire"]
        iws = physBiblioWeb.webSearch["inspire"]
        with patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveAPIResults",
            return_value=([], 0),
        ) as _s, patch(
            "physbiblio.webimport.inspire.WebSearch.processRecord",
            return_value={"k": "a"},
        ) as _r, patch(
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
        with patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveAPIResults",
            return_value=([{"ABC": "abc"}], 0),
        ) as _s, patch(
            "physbiblio.webimport.inspire.WebSearch.processRecord",
            side_effect=Exception("abc"),
        ) as _r, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.exception"
        ) as _e:
            self.assertFalse(iws.retrieveOAIData("abc"))
            _s.assert_called_once_with("%sabc" % iws.url)
            _r.assert_called_once_with(
                {"ABC": "abc"}, bibtex=None, readConferenceTitle=False
            )
            _e.assert_called_once_with(iws.errorReadRecord)
        with patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveAPIResults",
            return_value=([{"ABC": "abc"}], 0),
        ) as _s, patch(
            "physbiblio.webimport.inspire.WebSearch.processRecord",
            return_value={"k": "a"},
        ) as _r, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.exception"
        ) as _e:
            self.assertEqual(iws.retrieveOAIData("abc"), {"k": "a"})
            _s.assert_called_once_with("%sabc" % iws.url)
            self.assertEqual(_e.call_count, 0)
            _r.assert_called_once_with(
                {"ABC": "abc"}, bibtex=None, readConferenceTitle=False
            )
            self.assertEqual(iws.retrieveOAIData("abc", bibtex="bibtex"), {"k": "a"})
        with patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveAPIResults",
            return_value=([{"ABC": "abc"}], 0),
        ) as _s, patch(
            "physbiblio.webimport.inspire.WebSearch.processRecord",
            return_value={"k": "a"},
        ) as _r, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.exception"
        ) as _e:
            self.assertEqual(iws.retrieveOAIData("abc"), {"k": "a"})
            _s.assert_called_once_with("%sabc" % iws.url)
            self.assertEqual(_e.call_count, 0)
            _r.assert_called_once_with(
                {"ABC": "abc"}, bibtex=None, readConferenceTitle=False
            )
            res = iws.retrieveOAIData("abc", bibtex="bibtex")
            _r.assert_any_call(
                {"ABC": "abc"}, bibtex="bibtex", readConferenceTitle=False
            )
            self.assertEqual(res, {"k": "a"})
            self.assertEqual(_e.call_count, 0)
        with patch(
            "physbiblio.webimport.inspire.WebSearch.retrieveAPIResults",
            return_value=([{"ABC": "abc"}], 0),
        ) as _s, patch(
            "physbiblio.webimport.inspire.WebSearch.processRecord",
            return_value={"k": "a"},
        ) as _r, patch(
            "logging.Logger.info"
        ) as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.exception"
        ) as _e:
            self.assertEqual(iws.retrieveOAIData("abc"), {"k": "a"})
            _s.assert_called_once_with("%sabc" % iws.url)
            self.assertEqual(_e.call_count, 0)
            _r.assert_called_once_with(
                {"ABC": "abc"}, bibtex=None, readConferenceTitle=False
            )
            res = iws.retrieveOAIData("abc", bibtex="bibtex")
            _r.assert_any_call(
                {"ABC": "abc"}, bibtex="bibtex", readConferenceTitle=False
            )
            self.assertEqual(res, {"k": "a"})
            self.assertEqual(_e.call_count, 0)

    @unittest.skipIf(skipTestsSettings.online, "Online tests")
    def test_getProceedingsTitle_online(self):
        """Online test getProceedingsTitle"""
        iws = physBiblioWeb.webSearch["inspire"]
        self.assertEqual(iws.getProceedingsTitle("C00-00-00"), None)
        self.assertEqual(
            iws.getProceedingsTitle("C15-08-20"),
            "Proceedings, 17th Lomonosov "
            + "Conference on Elementary Particle Physics: Moscow, "
            + "Russia, August 20-26, 2015",
        )

    def test_getProceedingsTitle(self):
        """Test getProceedingsTitle"""
        iws = physBiblioWeb.webSearch["inspire"]
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch("logging.Logger.exception") as _e, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            side_effect=[
                None,
                "",
                '{"hits":{"hits":["abc"], "total":1}',
                '{"hits":{"hits":["abc"], "total":1}}',
                '{"hits":{"hits":[{"metadata": {"cnum":"abc"}}], "total":1}}',
                (
                    '{"hits":{"hits":['
                    + '{"metadata": {"cnum":"abc"}},'
                    + '{"metadata": {"cnum":"C21-01-00", "proceedings":[]}},'
                    + ' {"metadata": {"cnum":"abc"}}'
                    + '], "total":1}}'
                ),
                (
                    '{"hits":{"hits":['
                    + '{"metadata": {"cnum":"abc"}},'
                    + '{"metadata": {"cnum":"C21-01-00", "proceedings":[{"abc":"abc"}]}},'
                    + '{"metadata": {"cnum":"abc"}}'
                    + '], "total":1}}'
                ),
            ],
        ) as _tu:
            self.assertEqual(iws.getProceedingsTitle("C21-01-00"), None)
            _tu.assert_called_once_with(
                pbConfig.inspireConferencesAPI
                + "?q=C21-01-00"
                + "&fields="
                + (",".join(iws.metadataConferenceFields))
            )
            _e.assert_called_once_with(iws.jsonError)
            _e.reset_mock()
            self.assertEqual(iws.getProceedingsTitle("C21-01-00"), None)
            _e.assert_called_once_with(iws.jsonError)
            _e.reset_mock()
            self.assertEqual(iws.getProceedingsTitle("C21-01-00"), None)
            _e.assert_called_once_with(iws.jsonError)
            _e.reset_mock()
            self.assertEqual(iws.getProceedingsTitle("C21-01-00"), None)
            self.assertEqual(iws.getProceedingsTitle("C21-01-00"), None)
            self.assertEqual(iws.getProceedingsTitle("C21-01-00"), None)
            self.assertEqual(iws.getProceedingsTitle("C21-01-00"), None)
            self.assertEqual(_e.call_count, 0)
        res1 = (
            '{"hits":{"hits":['
            + '{"metadata": {"cnum":"abc"}}, '
            + '{"metadata": {"cnum":"C21-01-00", "proceedings":[{"control_number":"1234"}]}}, '
            + '{"metadata": {"cnum":"abc"}}'
            + '], "total":1}}'
        )
        res2 = (
            '{"hits":{"hits":['
            + '{"metadata": {"cnum":"abc"}}, '
            + '{"metadata": {"cnum":"C21-01-00", "proceedings":[{"control_number":"2345"}]}},'
            + '{"metadata": {"cnum":"C21-01-00", "proceedings":[{"control_number":"1234"}]}}'
            + '], "total":1}}'
        )
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch("logging.Logger.exception") as _e, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            side_effect=[
                res1,
                "a",  # literature
                res2,
                ('{"metadata": {"titles": "abc"}}'),  # literature
                res2,
                ('{"metadata": {"titles": [{"abc":"abc"}]}}'),  # literature
                res2,
                ('{"metadata": {"titles": []}}'),  # literature
                res2,
                ('{"metadata": {"titles": [{"title":"abc"}]}}'),  # literature
                res2,
                (  # literature
                    '{"metadata": {"titles": [{"title":"abc", "subtitle": "def"}]}}'
                ),
            ],
        ) as _tu:
            self.assertEqual(iws.getProceedingsTitle("C21-01-00"), None)
            _tu.assert_any_call(
                pbConfig.inspireConferencesAPI
                + "?q=C21-01-00"
                + "&fields="
                + (",".join(iws.metadataConferenceFields))
            )
            _tu.assert_any_call("%s%s" % (pbConfig.inspireLiteratureAPI, "1234"))
            _e.assert_called_once_with(iws.jsonError)
            _tu.reset_mock()
            _e.reset_mock()
            self.assertEqual(iws.getProceedingsTitle("C21-01-00"), None)
            _tu.assert_any_call("%s%s" % (pbConfig.inspireLiteratureAPI, "2345"))
            with self.assertRaises(AssertionError):
                _tu.assert_called_with("%s%s" % (pbConfig.inspireLiteratureAPI, "1234"))
            self.assertEqual(iws.getProceedingsTitle("C21-01-00"), None)
            self.assertEqual(iws.getProceedingsTitle("C21-01-00"), None)
            self.assertEqual(iws.getProceedingsTitle("C21-01-00"), None)
            self.assertEqual(iws.getProceedingsTitle("C21-01-00"), "abc: def")
            self.assertEqual(_e.call_count, 0)
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch("logging.Logger.exception") as _e, patch(
            "physbiblio.webimport.webInterf.WebInterf.textFromUrl",
            return_value='{"metadata": {"titles": [{"title":"abc", "subtitle": "def"}]}}',
        ) as _tu:
            self.assertEqual(
                iws.getProceedingsTitle("C21-01-00", useUrl="abcd"), "abc: def"
            )
            _tu.assert_called_once_with("abcd")

    def test_readRecord(self):
        """Test readRecord"""
        self.maxDiff = None
        iws = physBiblioWeb.webSearch["inspire"]

        def getBibtex(res):
            bibtexDict = {"ENTRYTYPE": res["ENTRYTYPE"], "ID": res["bibkey"]}
            for k in iws.bibtexFields:
                if k in res.keys() and res[k] is not None and res[k] != "":
                    bibtexDict[k] = res[k]
            db = bibtexparser.bibdatabase.BibDatabase()
            db.entries = [bibtexDict]
            return pbWriter.write(db)

        record1 = {
            "metadata": {
                "texkeys": [],
                "dois": [],
                "arxiv_eprints": [],
                "primary_arxiv_category": [],
                "external_system_identifiers": [],
                "first_author": {},
                "collaborations": ["abc"],
                "titles": [],
                "publication_info": [],
            }
        }
        res1 = {
            "ENTRYTYPE": "article",
            "bibkey": None,
            "oldkeys": "",
            "id": None,
            "doi": None,
            "eprint": None,
            "archiveprefix": None,
            "primaryclass": None,
            "ads": None,
            "author": "",
            "collaboration": None,
            "title": None,
            "journal": None,
            "volume": None,
            "year": None,
            "pages": None,
            "firstdate": None,
            "pubdate": None,
            "reportnumber": None,
            "isbn": None,
            "cit": None,
            "cit_no_self": None,
            "link": None,
        }
        res1["bibtex"] = getBibtex(res1)
        record2 = {
            "metadata": {
                "control_number": "123",
                "texkeys": ["key1", "key2", "key3"],
                "dois": [{"value": "doi1"}, {"value": "doi2"}],
                "arxiv_eprints": [{"value": "arxiv1"}, {"value": "arxiv2"}],
                "primary_arxiv_category": ["hep-ph", "hep-ex"],
                "external_system_identifiers": [
                    {"value": "ads1", "schema": "abc"},
                    {"value": "ads2", "schema": "ADS"},
                    {"value": "ads3", "schema": "ADS"},
                ],
                "first_author": {"full_name": "author1à"},
                "collaborations": [
                    {"value": "coll1"},
                    {"value": "coll2"},
                    {"value": "coll3"},
                ],
                "titles": [{"title": "title1"}, {"title": "title2"}],
                "publication_info": [
                    {
                        "journal_title": "jt1",
                        "journal_volume": "jv1",
                        "year": "2021",
                        "artid": "123",
                    }
                ],
                "earliest_date": "2021-06-30",
                "preprint_date": "2021-07-01",
                "legacy_creation_date": "2021-07-02",
                "imprints": [{"date": "2021-06-20"}, {"date": "2021-06-10"}],
                "isbns": [{"value": "isbn1"}, {"value": "isbn2"}],
                "report_numbers": [
                    {"value": "rn1"},
                    {"value": "rn2"},
                    {"value": "rn3"},
                ],
                "citation_count_without_self_citations": 111,
                "citation_count": 122,
            }
        }
        res2 = {
            "ENTRYTYPE": "book",
            "id": "123",
            "bibkey": "key1",
            "oldkeys": "key2,key3",
            "doi": "doi1",
            "eprint": "arxiv1",
            "archiveprefix": "arXiv",
            "primaryclass": "hep-ph",
            "ads": "ads2",
            "author": "author1{\`a}",
            "collaboration": "coll1, coll2, coll3",
            "title": "title1",
            "journal": "jt1",
            "volume": "jv1",
            "year": "2021",
            "pages": "123",
            "firstdate": "2021-07-01",
            "pubdate": "2021-06-20",
            "isbn": "isbn1",
            "reportnumber": "rn1, rn2, rn3",
            "link": "https://doi.org/doi1",
            "cit": 122,
            "cit_no_self": 111,
        }
        res2["bibtex"] = getBibtex(res2)
        record3 = {"metadata": {}}
        res3 = {
            "ENTRYTYPE": "article",
            "id": None,
            "bibkey": None,
            "oldkeys": "",
            "doi": None,
            "eprint": None,
            "archiveprefix": None,
            "primaryclass": None,
            "ads": None,
            "author": "",
            "collaboration": None,
            "title": None,
            "journal": None,
            "volume": None,
            "year": None,
            "pages": None,
            "firstdate": None,
            "pubdate": None,
            "reportnumber": None,
            "isbn": None,
            "cit": None,
            "cit_no_self": None,
            "link": None,
        }
        res3["bibtex"] = getBibtex(res3)
        record4 = {
            "metadata": {
                "dois": ["doi1"],
                "titles": ["titles1"],
                "arxiv_eprints": [
                    {"value": "arxiv1", "categories": []},
                    {"value": "arxiv2"},
                ],
                "primary_arxiv_category": [],
                "external_system_identifiers": [
                    {"value": "ads1"},
                    {"value": "ads2", "schema": "ADS"},
                ],
                "authors": [{"full_name": "author1"}, {"full_name": "author2"}],
                "collaborations": [{"value": "coll1"}],
                "publication_info": [{"cnum": "123"}],
                "isbns": ["isbn1"],
                "earliest_date": "2021-06-30",
                "legacy_creation_date": "2021-07-02",
                "imprints": ["2021-06-20"],
                "report_numbers": ["rn1"],
            }
        }
        res4 = {
            **res1,
            **{
                "ENTRYTYPE": "inproceedings",
                "eprint": "arxiv1",
                "archiveprefix": "arXiv",
                "author": "author1 and author2",
                "collaboration": "coll1",
                "firstdate": "2021-07-02",
                "link": "https://arxiv.org/abs/arxiv1",
            },
        }
        res4["bibtex"] = getBibtex(res4)
        record5 = {
            "metadata": {
                "arxiv_eprints": [
                    {"value": "arxiv1", "categories": ["hep-ex", "astro-ph"]},
                    {"value": "arxiv2"},
                ],
                "publication_info": [{"cnum": "123", "parent_record": {"$ref": "abc"}}],
                "earliest_date": "2021-06-30",
                "authors": [
                    {"full_name": "author%d" % (i + 1)}
                    for i in range(pbConfig.params["maxAuthorSave"])
                ],
            }
        }
        res5 = {
            **res1,
            **{
                "ENTRYTYPE": "inproceedings",
                "eprint": "arxiv1",
                "archiveprefix": "arXiv",
                "primaryclass": "hep-ex",
                "author": "author1 and others",
                "firstdate": "2021-06-30",
                "link": "https://arxiv.org/abs/arxiv1",
            },
        }
        res5["bibtex"] = getBibtex(res5)
        record6 = {
            "metadata": {
                "thesis_info": {"institutions": ["A", "B"], "date": "2013"},
                "document_type": ["thesis"],
                "authors": [
                    {"full_name": "author%d" % (i + 1)}
                    for i in range(pbConfig.params["maxAuthorSave"] - 1)
                ],
            }
        }
        res6 = {
            **res3,
            **{
                "ENTRYTYPE": "phdthesis",
                "year": "2013",
                "school": "A, B",
                "author": " and ".join(
                    [
                        "author%d" % (i + 1)
                        for i in range(pbConfig.params["maxAuthorSave"] - 1)
                    ]
                ),
            },
        }
        res6["bibtex"] = getBibtex(res6)
        record7 = {
            "metadata": {
                "author_count": pbConfig.params["maxAuthorSave"] + 1,
                "authors": [
                    {"full_name": "author%d" % (i + 1)}
                    for i in range(pbConfig.params["maxAuthorSave"] - 1)
                ],
            }
        }
        res7 = {
            **res3,
            **{
                "ENTRYTYPE": "article",
                "author": "author1 and others",
            },
        }
        res7["bibtex"] = getBibtex(res7)
        with patch("logging.Logger.warning") as _w:
            for i, (inp, res) in enumerate(
                [
                    [record1, res1],
                    [record2, res2],
                    [record3, res3],
                    [record4, res4],
                    [record5, res5],
                    [record6, res6],
                    [record7, res7],
                ]
            ):
                r = iws.readRecord(inp)
                self.assertEqual(r, res)
            with patch(
                "physbiblio.webimport.inspire.WebSearch.getProceedingsTitle",
                return_value="proctitle",
            ) as _pt:
                r = iws.readRecord(record2, readConferenceTitle=True)
                self.assertEqual(r, res2)
                r = iws.readRecord(record4, readConferenceTitle=True, noWarning=True)
                _pt.assert_called_once_with("123", useUrl=None)
                res4["booktitle"] = "proctitle"
                res4["bibtex"] = getBibtex(res4)
                self.assertEqual(r, res4)
                r = iws.readRecord(record5, readConferenceTitle=True)
                _pt.assert_called_with("123", useUrl="abc")
                res5["booktitle"] = "proctitle"
                res5["bibtex"] = getBibtex(res5)
                self.assertEqual(r, res5)

    @unittest.skipIf(skipTestsSettings.online, "Online tests")
    def test_readRecord_online(self):
        """Online test readRecord"""
        self.maxDiff = None
        iws = physBiblioWeb.webSearch["inspire"]
        record1 = iws.retrieveAPIResults("%s%s" % (iws.url, "1385583"))[0][0]
        record2 = iws.retrieveAPIResults("%s%s" % (iws.url, "1414175"))[0][0]
        dict1a = iws.readRecord(record1)
        dict1b = iws.readRecord(record1, readConferenceTitle=True)
        self.assertEqual(dict1a, dict1b)
        del dict1a["cit"]
        del dict1a["cit_no_self"]
        self.assertEqual(
            dict1a,
            {
                "doi": "10.1088/0954-3899/43/3/033001",
                "id": "1385583",
                "bibkey": "Gariazzo:2015rra",
                "ads": "2015JPhG...43c3001G",
                "journal": "J.Phys.G",
                "volume": "43",
                "year": "2016",
                "pages": "033001",
                "firstdate": "2015-07-29",
                "pubdate": "2016-01-13",
                "author": "Gariazzo, S. and Giunti, C. and Laveder, M. and "
                + "Li, Y.F. and Zavanin, E.M.",
                "collaboration": None,
                "primaryclass": "hep-ph",
                "archiveprefix": "arXiv",
                "eprint": "1507.08204",
                "reportnumber": None,
                "title": "Light sterile neutrinos",
                "isbn": None,
                "ENTRYTYPE": "article",
                "oldkeys": "",
                "link": "%s10.1088/0954-3899/43/3/033001" % pbConfig.doiUrl,
                "bibtex": "@Article{Gariazzo:2015rra,\n        "
                + 'author = "Gariazzo, S. and Giunti, C. and Laveder, M. '
                + 'and Li, Y.F. and Zavanin, E.M.",\n         title = "'
                + '{Light sterile neutrinos}",\n       journal = '
                + '"J.Phys.G",\n        volume = "43",\n          year = '
                + '"2016",\n         pages = "033001",\n archiveprefix = '
                + '"arXiv",\n  primaryclass = "hep-ph",\n        eprint = '
                + '"1507.08204",\n           doi = '
                + '"10.1088/0954-3899/43/3/033001",\n}\n\n',
            },
        )
        dict2 = iws.readRecord(record2, readConferenceTitle=True)
        del dict2["cit"]
        del dict2["cit_no_self"]
        self.assertEqual(
            dict2,
            {
                "doi": "10.1142/9789813224568_0076",
                "id": "1414175",
                "bibkey": "Gariazzo:2016ehl",
                "ads": None,
                "journal": None,
                "volume": None,
                "year": "2017",
                "pages": "469-475",
                "firstdate": "2016-01-07",
                "pubdate": "2017",
                "author": "Gariazzo, Stefano",
                "collaboration": None,
                "primaryclass": "astro-ph.CO",
                "archiveprefix": "arXiv",
                "eprint": "1601.01475",
                "reportnumber": None,
                "title": "Light Sterile Neutrinos In Cosmology",
                "isbn": None,
                "booktitle": "Proceedings, 17th Lomonosov "
                + "Conference on Elementary Particle Physics: Moscow, "
                + "Russia, August 20-26, 2015",
                "ENTRYTYPE": "inproceedings",
                "oldkeys": "",
                "link": "%s10.1142/9789813224568_0076" % pbConfig.doiUrl,
                "bibtex": "@Inproceedings{Gariazzo:2016ehl,\n        "
                + 'author = "Gariazzo, Stefano",\n         '
                + 'title = "{Light Sterile Neutrinos In Cosmology}",'
                + '\n     booktitle = "{Proceedings, 17th Lomonosov '
                + "Conference on Elementary Particle Physics: Moscow, "
                + 'Russia, August 20-26, 2015}",\n          year = '
                + '"2017",\n         pages = "469-475",\n archiveprefix = '
                + '"arXiv",\n  primaryclass = "astro-ph.CO",\n        '
                + 'eprint = "1601.01475",\n           doi = '
                + '"10.1142/9789813224568_0076",\n}\n\n',
            },
        )

    def test_updateBibtex(self):
        """Test updateBibtex"""
        iws = physBiblioWeb.webSearch["inspire"]
        with patch("logging.Logger.info") as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch("logging.Logger.exception") as _e:
            self.assertEqual(iws.updateBibtex({}, ""), (False, ""))
            _w.assert_called_once_with(iws.errorInvalidBibtex % "")
            self.assertEqual(
                iws.updateBibtex({}, "@article{bla,"), (False, "@article{bla,")
            )
            _w.assert_any_call(iws.errorInvalidBibtex % "@article{bla,")
            bib = '@article{bla,\ntitle="test",\narxiv="2101.00000",\n}\n\n'
            self.assertEqual(iws.updateBibtex({"id": 123}, bib), (False, bib))
            _w.assert_any_call(iws.warningJournal % (123))
            bib = '@article{bla,\ntitle="test",\narxiv="2101.00000",\n}\n\n'
            self.assertEqual(
                iws.updateBibtex({"id": 123, "eprint": "2102.00000"}, bib), (False, bib)
            )
            self.assertEqual(
                iws.updateBibtex({"id": 123, "eprint": "2102.00000"}, bib, force=True),
                (
                    True,
                    '@Article{bla,\n         title = "{test}",\n        eprint = "2102.00000",\n}\n\n',
                ),
            )
            _w.assert_any_call(iws.warningJournal % (123))
            res = {
                "id": 123,
                "author": "me",
                "title": "mywork",
                "year": "2000",
                "journal": "j",
            }
            bibu = (
                '@Article{bla,\n        author = "me",\n         title = "{mywork}",\n'
                + '       journal = "j",\n          year = "2000",\n'
                + '        eprint = "2101.00000",\n}\n\n'
            )
            self.assertEqual(iws.updateBibtex(res, bib), (True, bibu))
            _w.assert_any_call(
                iws.warningMissingField
                % (
                    [k for k in iws.updateBibtexFields if k not in res.keys()],
                    res["id"],
                )
            )
            res = {
                "id": 123,
                "author": "me",
                "title": "mywork",
                "year": "2000",
                "journal": "j",
                "doi": "1234",
                "volume": "1",
                "pages": "2",
            }
            _w.reset_mock()
            self.assertEqual(
                iws.updateBibtex(res, bib),
                (
                    True,
                    "@Article{bla,\n"
                    + '        author = "me",\n'
                    + '         title = "{mywork}",\n'
                    + '       journal = "j",\n'
                    + '        volume = "1",\n'
                    + '          year = "2000",\n'
                    + '         pages = "2",\n'
                    + '        eprint = "2101.00000",\n'
                    + '           doi = "1234",\n'
                    + "}\n"
                    + "\n",
                ),
            )
            _w.assert_called_once()
            res = {
                "id": 123,
                "author": "me",
                "title": "mywork",
                "year": "2000",
                "journal": "j",
                "doi": "1234",
                "volume": "1",
                "pages": "2",
                "arxiv": "1234.56789",
            }
            self.assertEqual(
                iws.updateBibtex(res, bib),
                (
                    True,
                    "@Article{bla,\n"
                    + '        author = "me",\n'
                    + '         title = "{mywork}",\n'
                    + '       journal = "j",\n'
                    + '        volume = "1",\n'
                    + '          year = "2000",\n'
                    + '         pages = "2",\n'
                    + '        eprint = "2101.00000",\n'
                    + '           doi = "1234",\n'
                    + "}\n"
                    + "\n",
                ),
            )
            bib = '@article{bla,\ntitle="test",\narxiv="2101.00000",\neprint="2103.00000"\n}\n\n'
            self.assertEqual(
                iws.updateBibtex(
                    {"id": 123, "eprint": "2102.00000", "arxiv": "1234.5678"},
                    bib,
                    force=True,
                ),
                (
                    True,
                    '@Article{bla,\n         title = "{test}",\n        eprint = "2102.00000",\n}\n\n',
                ),
            )
            res = {
                "id": 123,
                "author": "me",
                "title": "mywork",
                "year": "2000",
                "journal": "j",
                "bibtex": '@article{bla,\ntitle="test",\npages="1234",\neprint="2103.00000"\n}\n\n',
            }
            bib = '@article{bla,\ntitle="test",\neprint="2103.00000"\n}\n\n'
            bibu = (
                '@Article{bla,\n        author = "me",\n         title = "{mywork}",\n'
                + '       journal = "j",\n          year = "2000",\n'
                + '         pages = "1234",\n'
                + '        eprint = "2103.00000",\n}\n\n'
            )
            self.assertEqual(iws.updateBibtex(res, bib), (True, bibu))
            res = {
                "id": 123,
                "author": "me",
                "title": "mywork",
                "year": "2000",
                "journal": "j",
                "bibtex": "@article{bla,\n",
            }
            bib = '@article{bla,\ntitle="test",\neprint="2103.00000"\n}\n\n'
            bibu = (
                '@Article{bla,\n        author = "me",\n         title = "{mywork}",\n'
                + '       journal = "j",\n          year = "2000",\n'
                + '        eprint = "2103.00000",\n}\n\n'
            )
            self.assertEqual(iws.updateBibtex(res, bib), (True, bibu))


if __name__ == "__main__":
    unittest.main()
