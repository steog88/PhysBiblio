#!/usr/bin/env python
"""Test file for the physbiblio.gui.threadElements module.

This file is part of the physbiblio package.
"""
import os
import sys
import traceback

from PySide2.QtCore import Qt, Signal
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QWidget

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import MagicMock, call, patch
    from Queue import Queue
    from urllib2 import URLError
else:
    import unittest
    from queue import Queue
    from unittest.mock import MagicMock, call, patch
    from urllib.request import URLError

try:
    from physbiblio import __version__
    from physbiblio.database import pBDB
    from physbiblio.gui.setuptests import *
    from physbiblio.gui.threadElements import *
    from physbiblio.inspireStats import pBStats
    from physbiblio.setuptests import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_checkUpdated(GUITestCase):
    """Test the functions in threadElements.Thread_checkUpdated"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        thr = Thread_checkUpdated(p)
        self.assertIsInstance(thr, PBThread)
        self.assertIsInstance(thr.result, Signal)
        self.assertEqual(thr.parent(), p)
        self.assertRaises(NotImplementedError, thr.setStopFlag)

    def test_run(self):
        """test run"""

        def fake_urlerror(x, y):
            raise URLError("no connection")

        p = QWidget()
        h1 = MagicMock()
        thr = Thread_checkUpdated(p)
        thr.result.connect(h1)
        with patch(
            "physbiblio.gui.threadElements.check_outdated",
            return_value=(False, __version__),
            autospec=True,
        ) as _cho:
            thr.run()
            _cho.assert_called_once_with("physbiblio", __version__)
        h1.assert_called_once_with(False, __version__)
        h1.reset_mock()
        with patch(
            "physbiblio.gui.threadElements.check_outdated",
            return_value=(),
            autospec=True,
        ) as _cho, patch("logging.Logger.warning") as _w:
            thr.run()
            _cho.assert_called_once_with("physbiblio", __version__)
            _w.assert_called_once_with(
                "Error when executing check_outdated. "
                + "Maybe you are using a developing version",
                exc_info=True,
            )
        h1.assert_not_called()
        with patch(
            "physbiblio.gui.threadElements.check_outdated", new=fake_urlerror
        ) as _cho, patch("logging.Logger.warning") as _w:
            thr.run()
            _w.assert_called_once_with(
                "Error when trying to check new versions. Are you offline?",
                exc_info=True,
            )
        with patch(
            "physbiblio.gui.threadElements.check_outdated",
            side_effect=ConnectionError,
            autospec=True,
        ) as _cho, patch("logging.Logger.warning") as _w:
            thr.run()
            _w.assert_called_once_with(
                "Error when trying to check new versions. Are you offline?",
                exc_info=True,
            )


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_citationCount(GUITestCase):
    """Test the functions in threadElements.Thread_citationCount"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_citationCount(ws, 123, p, pbMax="m", pbVal="v")
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.inspireID, 123)
        self.assertEqual(thr.receiver, ws)
        self.assertEqual(thr.pbMax, "m")
        self.assertEqual(thr.pbVal, "v")

    def test_run(self):
        """test run"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_citationCount(ws, 123, p, pbMax="m", pbVal="v")
        self.assertTrue(ws.running)
        with patch(
            "physbiblio.database.Entries.citationCount", autospec=True
        ) as _cc, patch("time.sleep") as _sl, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            _cc.assert_called_once_with(
                pBDB.bibs,
                123,
                pbMax="m",
                pbVal="v",
            )
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)
            _sl.assert_called_once_with(0.1)

    def test_setStopFlag(self):
        """test setStopFlag"""
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_citationCount(ws, 0)
        pBDB.bibs.runningCitationCount = True
        self.assertTrue(pBDB.bibs.runningCitationCount)
        thr.setStopFlag()
        self.assertFalse(pBDB.bibs.runningCitationCount)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_updateAllBibtexs(GUITestCase):
    """Test the functions in threadElements.Thread_updateAllBibtexs"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_updateAllBibtexs(ws, 123, p, [[]], True, "r", pbMax="m", pbVal="v")
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.startFrom, 123)
        self.assertEqual(thr.receiver, ws)
        self.assertEqual(thr.useEntries, [[]])
        self.assertEqual(thr.force, True)
        self.assertEqual(thr.reloadAll, "r")
        self.assertEqual(thr.pbMax, "m")
        self.assertEqual(thr.pbVal, "v")

    def test_run(self):
        """test run"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_updateAllBibtexs(
            ws, 123, p, [[]], True, True, pbMax="m", pbVal="v"
        )
        self.assertTrue(ws.running)
        with patch(
            "physbiblio.database.Entries.searchOAIUpdates", autospec=True
        ) as _sou, patch("time.sleep") as _sl, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            _sou.assert_called_once_with(
                pBDB.bibs,
                123,
                entries=[[]],
                force=True,
                reloadAll=True,
                pbMax="m",
                pbVal="v",
            )
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)
            _sl.assert_called_once_with(0.1)

    def test_setStopFlag(self):
        """test setStopFlag"""
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_updateAllBibtexs(ws, 0)
        pBDB.bibs.runningOAIUpdates = True
        self.assertTrue(pBDB.bibs.runningOAIUpdates)
        thr.setStopFlag()
        self.assertFalse(pBDB.bibs.runningOAIUpdates)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_replace(GUITestCase):
    """Test the functions in threadElements.Thread_replace"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_replace(
            ws, "a", ["b"], "1", ["2"], parent=p, regex=True, pbMax="m", pbVal="v"
        )
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.fiOld, "a")
        self.assertEqual(thr.fiNew, ["b"])
        self.assertEqual(thr.old, "1")
        self.assertEqual(thr.new, ["2"])
        self.assertEqual(thr.receiver, ws)
        self.assertEqual(thr.regex, True)
        self.assertEqual(thr.pbMax, "m")
        self.assertEqual(thr.pbVal, "v")

    def test_run(self):
        """test run"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_replace(ws, "a", ["b"], "1", ["2"], p, True, pbMax="m", pbVal="v")
        self.assertTrue(ws.running)
        pBDB.bibs.lastFetched = ["e", "f"]
        with patch(
            "physbiblio.database.Entries.replace",
            return_value=("r1", "r2", "r3"),
            autospec=True,
        ) as _rep, patch("time.sleep") as _sl, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _ffl, patch(
            "physbiblio.database.Entries.fetchCursor",
            return_value="curs",
            autospec=True,
        ) as _fc, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            _rep.assert_called_once_with(
                pBDB.bibs,
                "a",
                ["b"],
                "1",
                ["2"],
                entries="curs",
                lenEntries=2,
                regex=True,
                pbMax="m",
                pbVal="v",
            )
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)
            _sl.assert_called_once_with(0.1)
            _ffl.assert_has_calls([call(pBDB.bibs, doFetch=False), call(pBDB.bibs)])
            _fc.assert_called_once_with(pBDB.bibs)
            self.assertEqual(p.replaceResults, ("r1", "r2", "r3"))

    def test_setStopFlag(self):
        """test setStopFlag"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_replace(ws, "a", ["b"], "1", ["2"], p)
        pBDB.bibs.runningReplace = True
        self.assertTrue(pBDB.bibs.runningReplace)
        thr.setStopFlag()
        self.assertFalse(pBDB.bibs.runningReplace)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_updateInspireInfo(GUITestCase):
    """Test the functions in threadElements.Thread_updateInspireInfo"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_updateInspireInfo(ws, "Gariazzo:2015rra", 1385583, p)
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.bibkey, "Gariazzo:2015rra")
        self.assertEqual(thr.receiver, ws)
        self.assertEqual(thr.inspireID, 1385583)
        self.assertRaises(NotImplementedError, thr.setStopFlag)

    def test_run(self):
        """test run"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_updateInspireInfo(ws, "Gariazzo:2015rra", 1385583, p)
        self.assertTrue(ws.running)
        with patch(
            "physbiblio.database.Entries.updateInfoFromOAI", autospec=True
        ) as _fun, patch("time.sleep") as _sl, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            _fun.assert_called_once_with(
                pBDB.bibs, 1385583, originalKey="Gariazzo:2015rra", verbose=1
            )
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)
            _sl.assert_called_once_with(0.1)
        for iid in [None, False, ""]:
            thr = Thread_updateInspireInfo(ws, "Gariazzo:2015rra", iid, p)
            with patch(
                "physbiblio.database.Entries.updateInfoFromOAI", autospec=True
            ) as _fun, patch(
                "physbiblio.database.Entries.updateInspireID",
                return_value=1385,
                autospec=True,
            ) as _uiid, patch(
                "time.sleep"
            ) as _sl, patch(
                "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
            ) as _st:
                thr.run()
                _uiid.assert_called_once_with(pBDB.bibs, "Gariazzo:2015rra")
                _fun.assert_called_once_with(
                    pBDB.bibs, 1385, originalKey=None, verbose=1
                )
                self.assertFalse(ws.running)
                _st.assert_called_once_with(ws)
                _sl.assert_called_once_with(0.1)

        ws = WriteStream(q)
        thr = Thread_updateInspireInfo(
            ws, ["Gariazzo:2015rra", "Gariazzo:2018mwd"], [1385583, None], p
        )
        self.assertTrue(ws.running)
        with patch(
            "physbiblio.database.Entries.updateInfoFromOAI", autospec=True
        ) as _fun, patch(
            "physbiblio.database.Entries.updateInspireID",
            return_value=1385,
            autospec=True,
        ) as _uiid, patch(
            "time.sleep"
        ) as _sl, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            _fun.assert_has_calls(
                [
                    call(pBDB.bibs, 1385583, originalKey="Gariazzo:2015rra", verbose=1),
                    call(pBDB.bibs, 1385, originalKey=None, verbose=1),
                ]
            )
            _uiid.assert_called_once_with(pBDB.bibs, "Gariazzo:2018mwd")
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)
            _sl.assert_called_once_with(0.1)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_downloadArxiv(GUITestCase):
    """Test the functions in threadElements.Thread_downloadArxiv"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        thr = Thread_downloadArxiv("Gariazzo:2015rra", p)
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.bibkey, "Gariazzo:2015rra")
        self.assertRaises(NotImplementedError, thr.setStopFlag)

    def test_run(self):
        """test run"""
        p = QWidget()
        thr = Thread_downloadArxiv("Gariazzo:2015rra", p)
        with patch("physbiblio.pdf.LocalPDF.downloadArxiv", autospec=True) as _fun:
            thr.run()
            _fun.assert_called_once_with(pBPDF, "Gariazzo:2015rra")


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_processLatex(GUITestCase):
    """Test the functions in threadElements.Thread_processLatex"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        func = MagicMock()
        thr = Thread_processLatex(func, p)
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.func, func)
        self.assertIsInstance(thr.passData, Signal)
        self.assertRaises(NotImplementedError, thr.setStopFlag)

    def test_run(self):
        """test run"""
        p = QWidget()
        func = MagicMock(return_value=(["a", "b"], "text"))
        thr = Thread_processLatex(func, p)
        with MagicMock() as h1:
            thr.passData.connect(h1)
            thr.run()
            func.assert_called_once_with()
            h1.assert_called_once_with(["a", "b"], "text")


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_authorStats(GUITestCase):
    """Test the functions in threadElements.Thread_authorStats"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_authorStats(ws, "Stefano.Gariazzo.1", p, pbMax="m", pbVal="v")
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.authorName, "Stefano.Gariazzo.1")
        self.assertEqual(thr.receiver, ws)
        self.assertFalse(p.lastAuthorStats)
        self.assertEqual(thr.pbMax, "m")
        self.assertEqual(thr.pbVal, "v")
        self.assertRaises(
            Exception, lambda: Thread_authorStats(ws, "Stefano.Gariazzo.1", None)
        )

    def test_run(self):
        """test run"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_authorStats(ws, "Stefano.Gariazzo.1", p, pbMax="m", pbVal="v")
        self.assertTrue(ws.running)
        with patch(
            "physbiblio.inspireStats.InspireStatsLoader.authorStats",
            return_value={"a": "b"},
            autospec=True,
        ) as _fun, patch("time.sleep") as _sl, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            _fun.assert_called_once_with(
                pBStats, "Stefano.Gariazzo.1", pbMax="m", pbVal="v"
            )
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)
            _sl.assert_called_once_with(0.1)
            self.assertEqual(p.lastAuthorStats, {"a": "b"})

    def test_setStopFlag(self):
        """test setStopFlag"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_authorStats(ws, "Stefano.Gariazzo.1", p)
        pBStats.runningAuthorStats = True
        self.assertTrue(pBStats.runningAuthorStats)
        thr.setStopFlag()
        self.assertFalse(pBStats.runningAuthorStats)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_paperStats(GUITestCase):
    """Test the functions in threadElements.Thread_paperStats"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_paperStats(ws, 1385583, p, pbMax="m", pbVal="v")
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.inspireId, 1385583)
        self.assertEqual(thr.receiver, ws)
        self.assertFalse(p.lastPaperStats)
        self.assertEqual(thr.pbMax, "m")
        self.assertEqual(thr.pbVal, "v")
        self.assertRaises(Exception, lambda: Thread_paperStats(ws, 1385583, None))

    def test_run(self):
        """test run"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_paperStats(ws, 1385583, p, pbMax="m", pbVal="v")
        self.assertTrue(ws.running)
        with patch(
            "physbiblio.inspireStats.InspireStatsLoader.paperStats",
            return_value={"a": "b"},
            autospec=True,
        ) as _fun, patch("time.sleep") as _sl, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            _fun.assert_called_once_with(pBStats, 1385583, pbMax="m", pbVal="v")
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)
            _sl.assert_called_once_with(0.1)
            self.assertEqual(p.lastPaperStats, {"a": "b"})

    def test_setStopFlag(self):
        """test setStopFlag"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_paperStats(ws, [1385583], p)
        pBStats.runningAuthorStats = True
        self.assertTrue(pBStats.runningPaperStats)
        thr.setStopFlag()
        self.assertFalse(pBStats.runningPaperStats)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_loadAndInsert(GUITestCase):
    """Test the functions in threadElements.Thread_loadAndInsert"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_loadAndInsert(ws, "Gariazzo:2015rra", p, pbMax="m", pbVal="v")
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.content, "Gariazzo:2015rra")
        self.assertEqual(thr.receiver, ws)
        self.assertEqual(thr.pbMax, "m")
        self.assertEqual(thr.pbVal, "v")
        self.assertRaises(Exception, lambda: Thread_loadAndInsert(ws, 1385583, None))

    def test_run(self):
        """test run"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_loadAndInsert(ws, "Gariazzo:2015rra", p, pbMax="m", pbVal="v")
        self.assertTrue(ws.running)
        pBDB.bibs.lastInserted = ["def"]
        with patch(
            "physbiblio.database.Entries.loadAndInsert",
            side_effect=[True, False],
            autospec=True,
        ) as _fun, patch("time.sleep") as _sl, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            _fun.assert_called_once_with(
                pBDB.bibs, "Gariazzo:2015rra", pbMax="m", pbVal="v"
            )
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)
            _sl.assert_called_once_with(0.1)
            self.assertEqual(p.loadedAndInserted, ["def"])
            thr.run()
            self.assertEqual(p.loadedAndInserted, [])

    def test_setStopFlag(self):
        """test setStopFlag"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_loadAndInsert(ws, "Gariazzo:2015rra", p)
        pBDB.bibs.runningLoadAndInsert = True
        self.assertTrue(pBDB.bibs.runningLoadAndInsert)
        thr.setStopFlag()
        self.assertFalse(pBDB.bibs.runningLoadAndInsert)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_cleanAllBibtexs(GUITestCase):
    """Test the functions in threadElements.Thread_cleanAllBibtexs"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_cleanAllBibtexs(ws, 123, p, [[]], pbMax="m", pbVal="v")
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.startFrom, 123)
        self.assertEqual(thr.receiver, ws)
        self.assertEqual(thr.useEntries, [[]])
        self.assertEqual(thr.pbMax, "m")
        self.assertEqual(thr.pbVal, "v")

    def test_run(self):
        """test run"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_cleanAllBibtexs(ws, 123, p, [[]], pbMax="m", pbVal="v")
        self.assertTrue(ws.running)
        with patch(
            "physbiblio.database.Entries.cleanBibtexs", autospec=True
        ) as _fun, patch("time.sleep") as _sl, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            _fun.assert_called_once_with(
                pBDB.bibs, 123, entries=[[]], pbMax="m", pbVal="v"
            )
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)
            _sl.assert_called_once_with(0.1)

    def test_setStopFlag(self):
        """test setStopFlag"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_cleanAllBibtexs(ws, 123, p, [[]])
        pBDB.bibs.runningCleanBibtexs = True
        self.assertTrue(pBDB.bibs.runningCleanBibtexs)
        thr.setStopFlag()
        self.assertFalse(pBDB.bibs.runningCleanBibtexs)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_findBadBibtexs(GUITestCase):
    """Test the functions in threadElements.Thread_findBadBibtexs"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_findBadBibtexs(ws, 123, p, [[]], pbMax="m", pbVal="v")
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.startFrom, 123)
        self.assertEqual(thr.receiver, ws)
        self.assertEqual(thr.useEntries, [[]])
        self.assertEqual(thr.pbMax, "m")
        self.assertEqual(thr.pbVal, "v")
        self.assertRaises(Exception, lambda: Thread_loadAndInsert(ws, 1385583, None))

    def test_run(self):
        """test run"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_findBadBibtexs(ws, 123, p, [[]], pbMax="m", pbVal="v")
        self.assertTrue(ws.running)
        with patch(
            "physbiblio.database.Entries.findCorruptedBibtexs", autospec=True
        ) as _fun, patch("time.sleep") as _sl, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            _fun.assert_called_once_with(
                pBDB.bibs, 123, entries=[[]], pbMax="m", pbVal="v"
            )
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)
            _sl.assert_called_once_with(0.1)

    def test_setStopFlag(self):
        """test setStopFlag"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_findBadBibtexs(ws, 123, p, [[]])
        pBDB.bibs.runningFindBadBibtexs = True
        self.assertTrue(pBDB.bibs.runningFindBadBibtexs)
        thr.setStopFlag()
        self.assertFalse(pBDB.bibs.runningFindBadBibtexs)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_importFromBib(GUITestCase):
    """Test the functions in threadElements.Thread_importFromBib"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_importFromBib(ws, "tmp.bib", False, p, pbMax="m", pbVal="v")
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.receiver, ws)
        self.assertEqual(thr.bibFile, "tmp.bib")
        self.assertFalse(thr.complete)
        self.assertEqual(thr.pbMax, "m")
        self.assertEqual(thr.pbVal, "v")

    def test_run(self):
        """test run"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_importFromBib(ws, "tmp.bib", False, p, pbMax="m", pbVal="v")
        self.assertTrue(ws.running)
        with patch(
            "physbiblio.database.Entries.importFromBib", autospec=True
        ) as _fun, patch("time.sleep") as _sl, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            _fun.assert_called_once_with(
                pBDB.bibs, "tmp.bib", False, pbMax="m", pbVal="v"
            )
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)
            _sl.assert_called_once_with(0.1)

    def test_setStopFlag(self):
        """test setStopFlag"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_importFromBib(ws, "tmp.bib", False, p)
        pBDB.bibs.importFromBibFlag = True
        self.assertTrue(pBDB.bibs.importFromBibFlag)
        thr.setStopFlag()
        self.assertFalse(pBDB.bibs.importFromBibFlag)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_exportTexBib(GUITestCase):
    """Test the functions in threadElements.Thread_exportTexBib"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_exportTexBib(ws, ["main.tex"], "biblio.bib", p)
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.receiver, ws)
        self.assertEqual(thr.outFName, "biblio.bib")
        self.assertEqual(thr.texFiles, ["main.tex"])
        self.assertFalse(thr.updateExisting)
        self.assertFalse(thr.removeUnused)
        self.assertFalse(thr.reorder)
        thr = Thread_exportTexBib(
            ws,
            ["main.tex"],
            "biblio.bib",
            removeUnused=True,
            updateExisting=True,
            reorder=True,
            parent=p,
        )
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.receiver, ws)
        self.assertEqual(thr.outFName, "biblio.bib")
        self.assertEqual(thr.texFiles, ["main.tex"])
        self.assertTrue(thr.updateExisting)
        self.assertTrue(thr.removeUnused)
        self.assertTrue(thr.reorder)

    def test_run(self):
        """test run"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_exportTexBib(ws, ["main.tex"], "biblio.bib", p)
        self.assertTrue(ws.running)
        with patch(
            "physbiblio.export.PBExport.exportForTexFile", autospec=True
        ) as _fun, patch("time.sleep") as _sl, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            _fun.assert_called_once_with(
                pBExport,
                ["main.tex"],
                "biblio.bib",
                removeUnused=False,
                updateExisting=False,
                reorder=False,
            )
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)
            _sl.assert_called_once_with(0.1)
        ws = WriteStream(q)
        thr = Thread_exportTexBib(
            ws,
            ["main.tex"],
            "biblio.bib",
            p,
            updateExisting=True,
            removeUnused=True,
            reorder=True,
        )
        thr = Thread_exportTexBib(ws, ["main.tex"], "biblio.bib", p, True, True, True)
        self.assertTrue(ws.running)
        with patch(
            "physbiblio.export.PBExport.exportForTexFile", autospec=True
        ) as _fun, patch("time.sleep") as _sl, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            _fun.assert_called_once_with(
                pBExport,
                ["main.tex"],
                "biblio.bib",
                removeUnused=True,
                updateExisting=True,
                reorder=True,
            )
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)
            _sl.assert_called_once_with(0.1)

    def test_setStopFlag(self):
        """test setStopFlag"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_exportTexBib(ws, ["main.tex"], "biblio.bib", p)
        pBExport.exportForTexFlag = True
        self.assertTrue(pBExport.exportForTexFlag)
        thr.setStopFlag()
        self.assertFalse(pBExport.exportForTexFlag)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_cleanSpare(GUITestCase):
    """Test the functions in threadElements.Thread_cleanSpare"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_cleanSpare(ws, p)
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.receiver, ws)
        self.assertRaises(NotImplementedError, thr.setStopFlag)

    def test_run(self):
        """test run"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_cleanSpare(ws, p)
        self.assertTrue(ws.running)
        with patch(
            "physbiblio.database.Utilities.cleanSpareEntries", autospec=True
        ) as _fun, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            _fun.assert_called_once_with(pBDB.utils)
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_cleanSparePDF(GUITestCase):
    """Test the functions in threadElements.Thread_cleanSparePDF"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_cleanSparePDF(ws, p)
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.receiver, ws)
        self.assertRaises(NotImplementedError, thr.setStopFlag)

    def test_run(self):
        """test run"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_cleanSparePDF(ws, p)
        self.assertTrue(ws.running)
        with patch(
            "physbiblio.pdf.LocalPDF.removeSparePDFFolders", autospec=True
        ) as _fun, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            _fun.assert_called_once_with(pBPDF)
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_fieldsArxiv(GUITestCase):
    """Test the functions in threadElements.Thread_fieldsArxiv"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_fieldsArxiv(
            ws, ["a", "b"], ["abstract", "arxiv"], p, pbMax="m", pbVal="v"
        )
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.receiver, ws)
        self.assertEqual(thr.entries, ["a", "b"])
        self.assertEqual(thr.fields, ["abstract", "arxiv"])
        self.assertEqual(thr.pbMax, "m")
        self.assertEqual(thr.pbVal, "v")

    def test_run(self):
        """test run"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_fieldsArxiv(
            ws, ["a", "b"], ["abstract", "arxiv"], p, pbMax="m", pbVal="v"
        )
        self.assertTrue(ws.running)
        with patch(
            "physbiblio.database.Entries.getFieldsFromArxiv", autospec=True
        ) as _fun, patch("time.sleep") as _sl, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            _fun.assert_called_once_with(
                pBDB.bibs, ["a", "b"], ["abstract", "arxiv"], pbMax="m", pbVal="v"
            )
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)
            _sl.assert_called_once_with(0.1)

    def test_setStopFlag(self):
        """test setStopFlag"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_fieldsArxiv(ws, ["a", "b"], ["abstract", "arxiv"], p)
        pBDB.bibs.getArxivFieldsFlag = True
        self.assertTrue(pBDB.bibs.getArxivFieldsFlag)
        thr.setStopFlag()
        self.assertFalse(pBDB.bibs.getArxivFieldsFlag)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_Thread_importDailyArxiv(GUITestCase):
    """Test the functions in threadElements.Thread_importDailyArxiv"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_importDailyArxiv(ws, ["a", "b"], p)
        self.assertIsInstance(thr, PBThread)
        self.assertEqual(thr.parent(), p)
        self.assertEqual(thr.receiver, ws)
        self.assertEqual(thr.found, ["a", "b"])
        self.assertTrue(thr.runningImport)

    def test_run(self):
        """test run"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        self.assertTrue(ws.running)
        thr = Thread_importDailyArxiv(
            ws,
            {
                "12.345": {
                    "bibpars": {
                        "author": "me",
                        "title": "title",
                        "type": "",
                        "eprint": "12.345",
                        "replacement": False,
                        "cross": False,
                        "abstract": "some text",
                        "primaryclass": "astro-ph",
                    },
                    "exist": 1,
                }
            },
            p,
        )
        with patch(
            "physbiblio.database.Entries.loadAndInsert",
            return_value=True,
            autospec=True,
        ) as _lai, patch(
            "physbiblio.database.Entries.getByKey",
            return_value=[{"bibkey": "12.345"}],
            autospec=True,
        ) as _gbk, patch(
            "time.sleep"
        ) as _sl, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st, patch(
            "logging.Logger.info"
        ) as _in:
            thr.run()
            _lai.assert_called_once_with(pBDB.bibs, "12.345")
            _gbk.assert_called_once_with(pBDB.bibs, "12.345")
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)
            _sl.assert_called_once_with(0.1)
            _in.assert_has_calls(
                [
                    call("Entries successfully imported: ['12.345']"),
                    call("Errors for entries:\n[]"),
                ]
            )

        q = Queue()
        ws = WriteStream(q)
        self.assertTrue(ws.running)
        thr = Thread_importDailyArxiv(
            ws,
            {
                "12.345": {
                    "bibpars": {
                        "author": "me1",
                        "title": "title1",
                        "type": "",
                        "eprint": "12.345",
                        "replacement": False,
                        "cross": False,
                        "abstract": "some text",
                        "primaryclass": "astro-ph",
                    },
                    "exist": 1,
                },
                "12.346": {
                    "bibpars": {
                        "author": "me2",
                        "title": "title2",
                        "type": "",
                        "eprint": "12.346",
                        "replacement": False,
                        "cross": True,
                        "abstract": "some other text",
                        "primaryclass": "astro-ph.CO",
                    },
                    "exist": 1,
                },
                "12.348": {
                    "bibpars": {
                        "author": "me4",
                        "title": "title4",
                        "type": "",
                        "eprint": "12.348",
                        "replacement": False,
                        "cross": False,
                        "abstract": "some more text",
                        "primaryclass": "hep-ph",
                    },
                    "exist": 1,
                },
                "12.349": {
                    "bibpars": {
                        "author": "me5",
                        "title": "title5",
                        "type": "",
                        "eprint": "12.349",
                        "replacement": False,
                        "cross": False,
                        "abstract": "some more text",
                        "primaryclass": "hep-ex",
                    },
                    "exist": 1,
                },
            },
            p,
        )
        with patch(
            "physbiblio.database.Entries.loadAndInsert",
            side_effect=[True, False, False, False],
            autospec=True,
        ) as _lai, patch(
            "physbiblio.database.Entries.prepareInsert",
            side_effect=["data1", "data2", "data3"],
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.updateInspireID",
            return_value="123",
            autospec=True,
        ) as _uid, patch(
            "physbiblio.database.Entries.searchOAIUpdates", autospec=True
        ) as _sou, patch(
            "physbiblio.database.Entries.insert",
            side_effect=[False, True, True],
            autospec=True,
        ) as _bi, patch(
            "physbiblio.database.Entries.getByKey",
            side_effect=[[{"bibkey": "12.345"}], [], [{"bibkey": "12.350"}]],
            autospec=True,
        ) as _gbk, patch(
            "physbiblio.database.Entries.getByBibkey",
            return_value=[{"bibkey": "12.346"}],
            autospec=True,
        ) as _gbb, patch(
            "logging.Logger.info"
        ) as _in, patch(
            "logging.Logger.warning"
        ) as _wa, patch(
            "time.sleep"
        ) as _sl, patch(
            "physbiblio.gui.commonClasses.WriteStream.start", autospec=True
        ) as _st:
            thr.run()
            self.assertFalse(ws.running)
            _st.assert_called_once_with(ws)
            _sl.assert_called_once_with(0.1)
            _lai.assert_has_calls(
                [
                    call(pBDB.bibs, "12.345"),
                    call(pBDB.bibs, "12.346"),
                    call(pBDB.bibs, "12.348"),
                    call(pBDB.bibs, "12.349"),
                ]
            )
            _gbk.assert_has_calls(
                [
                    call(pBDB.bibs, "12.345"),
                    call(pBDB.bibs, "12.348"),
                    call(pBDB.bibs, "12.349"),
                ]
            )
            _in.assert_has_calls(
                [
                    call("Element '12.348' successfully inserted.\n"),
                    call("Element '12.349' successfully inserted.\n"),
                    call(
                        "Entries successfully imported: "
                        + "['12.345', '12.348', '12.350']"
                    ),
                    call("Errors for entries:\n['12.346', '12.348']"),
                ]
            )
            _wa.assert_has_calls(
                [
                    call("Failed in inserting entry '12.346'\n"),
                    call(
                        "Failed in completing info for entry '12.348'\n", exc_info=True
                    ),
                ]
            )
            _pi.assert_has_calls(
                [
                    call(
                        pBDB.bibs,
                        '@Article{12.346,\n        author = "me2",\n'
                        + '         title = "{title2}",\n archiveprefix '
                        + '= "arXiv",\n  primaryclass = "astro-ph.CO",\n'
                        + '        eprint = "12.346",\n}\n\n',
                    ),
                    call(
                        pBDB.bibs,
                        '@Article{12.348,\n        author = "me4",\n'
                        + '         title = "{title4}",\n archiveprefix '
                        + '= "arXiv",\n  primaryclass = "hep-ph",\n'
                        + '        eprint = "12.348",\n}\n\n',
                    ),
                    call(
                        pBDB.bibs,
                        '@Article{12.349,\n        author = "me5",\n'
                        + '         title = "{title5}",\n archiveprefix '
                        + '= "arXiv",\n  primaryclass = "hep-ex",\n'
                        + '        eprint = "12.349",\n}\n\n',
                    ),
                ]
            )
            _bi.assert_has_calls([call(pBDB.bibs, "data1"), call(pBDB.bibs, "data2")])
            _uid.assert_has_calls(
                [call(pBDB.bibs, "12.348"), call(pBDB.bibs, "12.349")]
            )
            _sou.assert_has_calls(
                [
                    call(
                        pBDB.bibs,
                        0,
                        entries=[{"bibkey": "12.346"}],
                        force=True,
                        reloadAll=True,
                    ),
                    call(
                        pBDB.bibs,
                        0,
                        entries=[{"bibkey": "12.346"}],
                        force=True,
                        reloadAll=True,
                    ),
                ]
            )
            _gbb.assert_has_calls(
                [call(pBDB.bibs, "12.348"), call(pBDB.bibs, "12.349")]
            )

    def test_setStopFlag(self):
        """test setStopFlag"""
        p = QWidget()
        q = Queue()
        ws = WriteStream(q)
        thr = Thread_importDailyArxiv(ws, ["a", "b"], p)
        self.assertTrue(thr.runningImport)
        thr.setStopFlag()
        self.assertFalse(thr.runningImport)


if __name__ == "__main__":
    unittest.main()
