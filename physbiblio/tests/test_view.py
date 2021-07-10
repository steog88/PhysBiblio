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
    from physbiblio.config import pbConfig
    from physbiblio.database import pBDB
    from physbiblio.setuptests import *
    from physbiblio.view import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


@unittest.skipIf(skipTestsSettings.long, "Long tests")
@patch("logging.Logger.debug")
@patch("logging.Logger.info")
@patch("logging.Logger.warning")
@patch("logging.Logger.exception")
class TestViewMethods(unittest.TestCase):
    """Tests for methods in physbiblio.view"""

    def test_init(self, *args):
        """test instance properties"""
        tmp = ViewEntry()
        self.assertIsInstance(tmp, ViewEntry)
        self.assertEqual(tmp.webApp, pbConfig.params["webApplication"])
        self.assertEqual(tmp.inspireRecord, pbConfig.inspireLiteratureLink)
        self.assertEqual(
            tmp.inspireSearch,
            pbConfig.inspireLiteratureLink + "?p=",
        )
        with patch.dict(pbConfig.params, {"webApplication": "someapp"}, clear=False):
            tmp = ViewEntry()
            self.assertEqual(tmp.webApp, "someapp")

    def test_getLink(self, *args):
        """Test getLink function with different inputs"""
        with patch(
            "physbiblio.database.Entries.getField",
            autospec=True,
            side_effect=["abc...123", "1507.08204", "", "", "abc...123"],
        ) as _mock:
            self.assertEqual(
                pBView.getLink("a", "ads"), "%sabc...123" % pbConfig.adsUrl
            )
        with patch(
            "physbiblio.database.Entries.getField",
            autospec=True,
            side_effect=["", "1507.08204", "", "", "1507.08204"],
        ) as _mock:
            self.assertEqual(
                pBView.getLink("a", "arxiv"), "%s/abs/1507.08204" % pbConfig.arxivUrl
            )
        with patch(
            "physbiblio.database.Entries.getField",
            autospec=True,
            side_effect=[
                "abc...123",
                "1234.56789",
                "10.1088/0954-3899/43/3/033001",
                "123456789",
                "10.1088/0954-3899/43/3/033001",
            ],
        ) as _mock:
            self.assertEqual(
                pBView.getLink("a", "doi"),
                "%s10.1088/0954-3899/43/3/033001" % pbConfig.doiUrl,
            )
        with patch(
            "physbiblio.database.Entries.getField",
            autospec=True,
            side_effect=[
                "abc...123",
                "1234.56789",
                "10.1088/0954-3899/43/3/033001",
                "1385583",
                "1385583",
            ],
        ) as _mock:
            self.assertEqual(
                pBView.getLink("a", "inspire"),
                pbConfig.inspireLiteratureLink + "1385583",
            )
        with patch(
            "physbiblio.database.Entries.getField",
            autospec=True,
            side_effect=[
                "abc...123",
                "1507.08204",
                "10.1088/0954-3899/43/3/033001",
                "",
            ],
        ) as _mock:
            self.assertEqual(
                pBView.getLink("a", "inspire"),
                pbConfig.inspireLiteratureLink + "?p=arxiv:1507.08204",
            )
        with patch(
            "physbiblio.database.Entries.getField",
            autospec=True,
            side_effect=["abc...123", "", "10.1088/0954-3899/43/3/033001", False],
        ) as _mock:
            self.assertEqual(
                pBView.getLink("a", "inspire"),
                pbConfig.inspireLiteratureLink + "?p=a",
            )
        with patch(
            "physbiblio.database.Entries.getField",
            autospec=True,
            side_effect=["", "", "", ""],
        ) as _mock:
            self.assertFalse(pBView.getLink("a", "arxiv"))
        with patch(
            "physbiblio.database.Entries.getField",
            autospec=True,
            side_effect=["", "", "", ""],
        ) as _mock:
            self.assertFalse(pBView.getLink("a", "arxiv"))

    def test_openLink(self, *args):
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
