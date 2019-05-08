#!/usr/bin/env python
"""Test file for the physbiblio.view module.

This file is part of the physbiblio package.
"""
import sys
import traceback

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import call, patch
else:
    import unittest
    from unittest.mock import call, patch

try:
    from physbiblio.setuptests import *
    from physbiblio.config import pbConfig
    from physbiblio.database import pBDB
    from physbiblio.view import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


@unittest.skipIf(skipTestsSettings.long, "Long tests")
class TestViewMethods(unittest.TestCase):
    """Tests for methods in physbiblio.view"""

    def test_init(self):
        """test instance properties"""
        tmp = ViewEntry()
        self.assertIsInstance(tmp, ViewEntry)
        self.assertEqual(tmp.webApp, pbConfig.params["webApplication"])
        self.assertEqual(tmp.inspireRecord, pbConfig.inspireRecord)
        self.assertEqual(tmp.inspireSearch, pbConfig.inspireSearchBase + "?p=find+")
        with patch.dict(pbConfig.params, {"webApplication": "someapp"}, clear=False):
            tmp = ViewEntry()
            self.assertEqual(tmp.webApp, "someapp")

    def test_getLink(self):
        """Test getLink function with different inputs"""
        with patch(
            "physbiblio.database.Entries.getField",
            autospec=True,
            side_effect=[
                "1507.08204",
                "",
                "",
                "1507.08204",  # test "arxiv"
                "",
                "10.1088/0954-3899/43/3/033001",
                "",
                "10.1088/0954-3899/43/3/033001",  # test "doi"
                "",
                "",
                "1385583",  # test "inspire", inspire ID present
                "1507.08204",
                "",
                "",  # test "inspire",
                # inspire ID not present, arxiv present
                "",
                "",
                False,  # test "inspire",
                # inspire ID not present, arxiv not present
                "",
                "",
                "",  # test "arxiv", no info
                "",
                "",
                "",  # test "doi", no info
            ],
        ) as _mock:
            self.assertEqual(
                pBView.getLink("a", "arxiv"), "%s/abs/1507.08204" % pbConfig.arxivUrl
            )
            self.assertEqual(
                pBView.getLink("a", "doi"),
                "%s10.1088/0954-3899/43/3/033001" % pbConfig.doiUrl,
            )
            self.assertEqual(
                pBView.getLink("a", "inspire"), "https://inspirehep.net/record/1385583"
            )
            self.assertEqual(
                pBView.getLink("a", "inspire"),
                "https://inspirehep.net/search?p=find+1507.08204",
            )
            self.assertEqual(
                pBView.getLink("a", "inspire"), "https://inspirehep.net/search?p=find+a"
            )
            self.assertFalse(pBView.getLink("a", "arxiv"))
            self.assertFalse(pBView.getLink("a", "doi"))

    def test_openLink(self):
        """Test openLink"""
        origwebapp = pBView.webApp
        with patch(
            "physbiblio.view.ViewEntry.getLink", autospec=True, return_value="test_link"
        ) as _gl, patch("logging.Logger.info") as _i, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "subprocess.Popen", autospec=USE_AUTOSPEC_CLASS
        ) as _po:
            pBView.openLink(["a", "b"], arg="file")
            _gl.assert_has_calls(
                [
                    call(pBView, "a", arg="file", fileArg=None),
                    call(pBView, "b", arg="file", fileArg=None),
                ]
            )
            _po.assert_not_called()
            _gl.reset_mock()
            pBView.webApp = "test"
            pBView.openLink("a")
            _gl.assert_called_once_with(pBView, "a", arg="arxiv", fileArg=None)
            _po.assert_called_once_with(
                [pBView.webApp, "test_link"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            _i.assert_called_once_with("Opening 'test_link'...")
            _w.assert_not_called()
            _i.reset_mock()
            pBView.webApp = ""
            pBView.openLink("a")
            _i.assert_not_called()
            _w.assert_not_called()
            _gl.reset_mock()
            _po.reset_mock()
            pBView.webApp = "test"
            pBView.openLink("a", arg="link")
            _po.assert_called_once_with(
                [pBView.webApp, "a"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            _i.assert_called_once_with("Opening 'a'...")
            _po.side_effect = OSError
            pBView.openLink("a", arg="link")
            _w.assert_called_once_with("Opening link for 'a' failed!")
            _w.reset_mock()
            _gl.reset_mock()
            _gl.return_value = ""
            pBView.openLink("a", arg="doi", fileArg="arg")
            _gl.assert_called_once_with(pBView, "a", arg="doi", fileArg="arg")
            _w.assert_called_once_with("Impossible to get the 'doi' link for entry 'a'")
        pBView.webApp = origwebapp


if __name__ == "__main__":
    unittest.main()
