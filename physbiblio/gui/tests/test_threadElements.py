#!/usr/bin/env python
"""
Test file for the physbiblio.gui.threadElements module.

This file is part of the physbiblio package.
"""
import sys, traceback
import os
from PySide2.QtCore import Qt, Signal
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QWidget

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch, MagicMock
	from urllib2 import URLError
	from Queue import Queue
else:
	import unittest
	from unittest.mock import patch, MagicMock
	from urllib.request import URLError
	from queue import Queue

try:
	from physbiblio import __version__
	from physbiblio.setuptests import *
	from physbiblio.database import pBDB
	from physbiblio.inspireStats import pBStats
	from physbiblio.gui.setuptests import *
	from physbiblio.gui.threadElements import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_thread_checkUpdated(GUITestCase):
	"""
	Test the functions in threadElements.thread_checkUpdated
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		thr = thread_checkUpdated(p)
		self.assertIsInstance(thr, MyThread)
		self.assertIsInstance(thr.result, Signal)
		self.assertEqual(thr.parent(), p)
		self.assertRaises(NotImplementedError, thr.setStopFlag)

	def test_run(self):
		"""test run"""
		def fake_urlerror(x, y):
			raise URLError("no connection")
		p = QWidget()
		thr = thread_checkUpdated(p)
		h1 = MagicMock()
		thr.result.connect(h1)
		h2 = MagicMock()
		thr.finished.connect(h2)
		with patch("physbiblio.gui.threadElements.check_outdated",
				return_value = (False, __version__)) as _cho:
			thr.run()
			_cho.assert_called_once_with('physbiblio', __version__)
		h1.assert_called_once_with(False, __version__)
		h2.assert_called_once_with()
		h1.reset_mock()
		h2.reset_mock()
		with patch("physbiblio.gui.threadElements.check_outdated",
				return_value = ()) as _cho,\
				patch("logging.Logger.warning") as _w:
			thr.run()
			_cho.assert_called_once_with('physbiblio', __version__)
			_w.assert_called_once_with('Error when executing check_outdated. ' +
				'Maybe you are using a developing version', exc_info=True)
		h1.assert_not_called()
		h2.assert_called_once_with()
		with patch("physbiblio.gui.threadElements.check_outdated",
				new = fake_urlerror) as _cho,\
				patch("logging.Logger.warning") as _w:
			thr.run()
			_w.assert_called_once_with('Error when trying to check ' +
				'new versions. Are you offline?', exc_info=True)

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_thread_updateAllBibtexs(GUITestCase):
	"""
	Test the functions in threadElements.thread_updateAllBibtexs
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, "r")
		self.assertIsInstance(thr, MyThread)
		self.assertEqual(thr.parent(), p)
		self.assertEqual(thr.startFrom, 123)
		self.assertEqual(thr.receiver, ws)
		self.assertEqual(thr.useEntries, [[]])
		self.assertEqual(thr.force, True)
		self.assertEqual(thr.reloadAll, "r")

	def test_run(self):
		"""test run"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, True)
		self.assertTrue(ws.running)
		h1 = MagicMock()
		thr.finished.connect(h1)
		with patch("physbiblio.database.entries.searchOAIUpdates") as _sou,\
				patch("time.sleep") as _sl,\
				patch("physbiblio.gui.commonClasses.WriteStream.start") as _st:
			thr.run()
			_sou.assert_called_once_with(
				123,
				entries = [[]],
				force = True,
				reloadAll = True)
			self.assertFalse(ws.running)
			_st.assert_called_once_with()
			_sl.assert_called_once_with(0.1)
			h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		q = Queue()
		ws = WriteStream(q)
		thr = thread_updateAllBibtexs(ws, 0)
		pBDB.bibs.runningOAIUpdates = True
		self.assertTrue(pBDB.bibs.runningOAIUpdates)
		thr.setStopFlag()
		self.assertFalse(pBDB.bibs.runningOAIUpdates)

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_thread_updateInspireInfo(GUITestCase):
	"""
	Test the functions in threadElements.thread_updateInspireInfo
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_updateInspireInfo(ws, "Gariazzo:2015rra", 1385583, p)
		self.assertIsInstance(thr, MyThread)
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
		thr = thread_updateInspireInfo(ws, "Gariazzo:2015rra", 1385583, p)
		self.assertTrue(ws.running)
		with patch("physbiblio.database.entries.updateInfoFromOAI") as _fun,\
				patch("time.sleep") as _sl,\
				patch("physbiblio.gui.commonClasses.WriteStream.start") as _st,\
				MagicMock() as h1:
			thr.finished.connect(h1)
			thr.run()
			_fun.assert_called_once_with(
				1385583,
				originalKey = 'Gariazzo:2015rra',
				verbose = 1)
			self.assertFalse(ws.running)
			_st.assert_called_once_with()
			_sl.assert_called_once_with(0.1)
			h1.assert_called_once_with()
		thr = thread_updateInspireInfo(ws, "Gariazzo:2015rra", None, p)
		with patch("physbiblio.database.entries.updateInfoFromOAI") as _fun,\
				patch("physbiblio.database.entries.updateInspireID",
					return_value= 1385) as _uiid,\
				patch("time.sleep") as _sl,\
				patch("physbiblio.gui.commonClasses.WriteStream.start") as _st,\
				MagicMock() as h1:
			thr.finished.connect(h1)
			thr.run()
			_uiid.assert_called_once_with('Gariazzo:2015rra')
			_fun.assert_called_once_with(1385, originalKey = None, verbose = 1)
			self.assertFalse(ws.running)
			_st.assert_called_once_with()
			_sl.assert_called_once_with(0.1)
			h1.assert_called_once_with()

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_thread_downloadArxiv(GUITestCase):
	"""
	Test the functions in threadElements.thread_downloadArxiv
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		thr = thread_downloadArxiv("Gariazzo:2015rra", p)
		self.assertIsInstance(thr, MyThread)
		self.assertEqual(thr.parent(), p)
		self.assertEqual(thr.bibkey, "Gariazzo:2015rra")
		self.assertRaises(NotImplementedError, thr.setStopFlag)

	def test_run(self):
		"""test run"""
		p = QWidget()
		thr = thread_downloadArxiv("Gariazzo:2015rra", p)
		with patch("physbiblio.pdf.localPDF.downloadArxiv") as _fun,\
				MagicMock() as h1:
			thr.finished.connect(h1)
			thr.run()
			_fun.assert_called_once_with("Gariazzo:2015rra")
			h1.assert_called_once_with()

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_thread_processLatex(GUITestCase):
	"""
	Test the functions in threadElements.thread_processLatex
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		func = MagicMock()
		thr = thread_processLatex(func, p)
		self.assertIsInstance(thr, MyThread)
		self.assertEqual(thr.parent(), p)
		self.assertEqual(thr.func, func)
		self.assertIsInstance(thr.passData, Signal)
		self.assertRaises(NotImplementedError, thr.setStopFlag)

	def test_run(self):
		"""test run"""
		p = QWidget()
		func = MagicMock(return_value = (["a", "b"], "text"))
		thr = thread_processLatex(func, p)
		with MagicMock() as h1,\
				MagicMock() as h2:
			thr.finished.connect(h1)
			thr.passData.connect(h2)
			thr.run()
			func.assert_called_once_with()
			h1.assert_called_once_with()
			h2.assert_called_once_with(["a", "b"], "text")

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_thread_authorStats(GUITestCase):
	"""
	Test the functions in threadElements.thread_authorStats
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_authorStats(ws, "Stefano.Gariazzo.1", p)
		self.assertIsInstance(thr, MyThread)
		self.assertEqual(thr.parent(), p)
		self.assertEqual(thr.authorName, "Stefano.Gariazzo.1")
		self.assertEqual(thr.receiver, ws)
		self.assertFalse(p.lastAuthorStats)
		self.assertRaises(Exception,
			lambda: thread_authorStats(ws, "Stefano.Gariazzo.1", None))

	def test_run(self):
		"""test run"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_authorStats(ws, "Stefano.Gariazzo.1", p)
		self.assertTrue(ws.running)
		with patch("physbiblio.inspireStats.inspireStatsLoader.authorStats",
					return_value = {"a": "b"}) as _fun,\
				patch("time.sleep") as _sl,\
				patch("physbiblio.gui.commonClasses.WriteStream.start") as _st,\
				MagicMock() as h1:
			thr.finished.connect(h1)
			thr.run()
			_fun.assert_called_once_with("Stefano.Gariazzo.1")
			self.assertFalse(ws.running)
			_st.assert_called_once_with()
			_sl.assert_called_once_with(0.1)
			h1.assert_called_once_with()
			self.assertEqual(p.lastAuthorStats, {"a": "b"})

	def test_setStopFlag(self):
		"""test setStopFlag"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_authorStats(ws, "Stefano.Gariazzo.1", p)
		pBStats.runningAuthorStats = True
		self.assertTrue(pBStats.runningAuthorStats)
		thr.setStopFlag()
		self.assertFalse(pBStats.runningAuthorStats)

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_thread_paperStats(GUITestCase):
	"""
	Test the functions in threadElements.thread_paperStats
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_paperStats(ws, 1385583, p)
		self.assertIsInstance(thr, MyThread)
		self.assertEqual(thr.parent(), p)
		self.assertEqual(thr.inspireId, 1385583)
		self.assertEqual(thr.receiver, ws)
		self.assertFalse(p.lastPaperStats)
		self.assertRaises(Exception,
			lambda: thread_paperStats(ws, 1385583, None))
		self.assertRaises(NotImplementedError, thr.setStopFlag)

	def test_run(self):
		"""test run"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_paperStats(ws, 1385583, p)
		self.assertTrue(ws.running)
		with patch("physbiblio.inspireStats.inspireStatsLoader.paperStats",
					return_value = {"a": "b"}) as _fun,\
				patch("time.sleep") as _sl,\
				patch("physbiblio.gui.commonClasses.WriteStream.start") as _st,\
				MagicMock() as h1:
			thr.finished.connect(h1)
			thr.run()
			_fun.assert_called_once_with(1385583)
			self.assertFalse(ws.running)
			_st.assert_called_once_with()
			_sl.assert_called_once_with(0.1)
			h1.assert_called_once_with()
			self.assertEqual(p.lastPaperStats, {"a": "b"})

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_thread_loadAndInsert(GUITestCase):
	"""
	Test the functions in threadElements.thread_loadAndInsert
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_loadAndInsert(ws, "Gariazzo:2015rra", p)
		self.assertIsInstance(thr, MyThread)
		self.assertEqual(thr.parent(), p)
		self.assertEqual(thr.content, "Gariazzo:2015rra")
		self.assertEqual(thr.receiver, ws)
		self.assertRaises(Exception,
			lambda: thread_loadAndInsert(ws, 1385583, None))

	def test_run(self):
		"""test run"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_loadAndInsert(ws, "Gariazzo:2015rra", p)
		self.assertTrue(ws.running)
		pBDB.bibs.lastInserted = ["def"]
		with patch("physbiblio.database.entries.loadAndInsert",
					side_effect = [True, False]) as _fun,\
				patch("time.sleep") as _sl,\
				patch("physbiblio.gui.commonClasses.WriteStream.start") as _st,\
				MagicMock() as h1:
			thr.finished.connect(h1)
			thr.run()
			_fun.assert_called_once_with("Gariazzo:2015rra")
			self.assertFalse(ws.running)
			_st.assert_called_once_with()
			_sl.assert_called_once_with(0.1)
			h1.assert_called_once_with()
			self.assertEqual(p.loadedAndInserted, ["def"])
			thr.run()
			self.assertEqual(p.loadedAndInserted, [])

	def test_setStopFlag(self):
		"""test setStopFlag"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_loadAndInsert(ws, "Gariazzo:2015rra", p)
		pBDB.bibs.runningLoadAndInsert = True
		self.assertTrue(pBDB.bibs.runningLoadAndInsert)
		thr.setStopFlag()
		self.assertFalse(pBDB.bibs.runningLoadAndInsert)

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_thread_cleanAllBibtexs(GUITestCase):
	"""
	Test the functions in threadElements.thread_cleanAllBibtexs
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_cleanAllBibtexs(ws, 123, p, [[]])
		self.assertIsInstance(thr, MyThread)
		self.assertEqual(thr.parent(), p)
		self.assertEqual(thr.startFrom, 123)
		self.assertEqual(thr.receiver, ws)
		self.assertEqual(thr.useEntries, [[]])

	def test_run(self):
		"""test run"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_cleanAllBibtexs(ws, 123, p, [[]])
		self.assertTrue(ws.running)
		with patch("physbiblio.database.entries.cleanBibtexs") as _fun,\
				patch("time.sleep") as _sl,\
				patch("physbiblio.gui.commonClasses.WriteStream.start") as _st,\
				MagicMock() as h1:
			thr.finished.connect(h1)
			thr.run()
			_fun.assert_called_once_with(123, entries = [[]])
			self.assertFalse(ws.running)
			_st.assert_called_once_with()
			_sl.assert_called_once_with(0.1)
			h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_cleanAllBibtexs(ws, 123, p, [[]])
		pBDB.bibs.runningCleanBibtexs = True
		self.assertTrue(pBDB.bibs.runningCleanBibtexs)
		thr.setStopFlag()
		self.assertFalse(pBDB.bibs.runningCleanBibtexs)

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_thread_findBadBibtexs(GUITestCase):
	"""
	Test the functions in threadElements.thread_findBadBibtexs
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_findBadBibtexs(ws, 123, p, [[]])
		self.assertIsInstance(thr, MyThread)
		self.assertEqual(thr.parent(), p)
		self.assertEqual(thr.startFrom, 123)
		self.assertEqual(thr.receiver, ws)
		self.assertEqual(thr.useEntries, [[]])
		self.assertRaises(Exception,
			lambda: thread_loadAndInsert(ws, 1385583, None))

	def test_run(self):
		"""test run"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_findBadBibtexs(ws, 123, p, [[]])
		self.assertTrue(ws.running)
		with patch("physbiblio.database.entries.findCorruptedBibtexs") as _fun,\
				patch("time.sleep") as _sl,\
				patch("physbiblio.gui.commonClasses.WriteStream.start") as _st,\
				MagicMock() as h1:
			thr.finished.connect(h1)
			thr.run()
			_fun.assert_called_once_with(123, entries = [[]])
			self.assertFalse(ws.running)
			_st.assert_called_once_with()
			_sl.assert_called_once_with(0.1)
			h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_findBadBibtexs(ws, 123, p, [[]])
		pBDB.bibs.runningFindBadBibtexs = True
		self.assertTrue(pBDB.bibs.runningFindBadBibtexs)
		thr.setStopFlag()
		self.assertFalse(pBDB.bibs.runningFindBadBibtexs)

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_thread_importFromBib(GUITestCase):
	"""
	Test the functions in threadElements.thread_importFromBib
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_importFromBib(ws, "tmp.bib", False, p)
		self.assertIsInstance(thr, MyThread)
		self.assertEqual(thr.parent(), p)
		self.assertEqual(thr.receiver, ws)
		self.assertEqual(thr.bibFile, "tmp.bib")
		self.assertFalse(thr.complete)

	def test_run(self):
		"""test run"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_importFromBib(ws, "tmp.bib", False, p)
		self.assertTrue(ws.running)
		with patch("physbiblio.database.entries.importFromBib") as _fun,\
				patch("time.sleep") as _sl,\
				patch("physbiblio.gui.commonClasses.WriteStream.start") as _st,\
				MagicMock() as h1:
			thr.finished.connect(h1)
			thr.run()
			_fun.assert_called_once_with("tmp.bib", False)
			self.assertFalse(ws.running)
			_st.assert_called_once_with()
			_sl.assert_called_once_with(0.1)
			h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_importFromBib(ws, "tmp.bib", False, p)
		pBDB.bibs.importFromBibFlag = True
		self.assertTrue(pBDB.bibs.importFromBibFlag)
		thr.setStopFlag()
		self.assertFalse(pBDB.bibs.importFromBibFlag)

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_thread_exportTexBib(GUITestCase):
	"""
	Test the functions in threadElements.thread_exportTexBib
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_exportTexBib(ws, ["main.tex"], "biblio.bib", p)
		self.assertIsInstance(thr, MyThread)
		self.assertEqual(thr.parent(), p)
		self.assertEqual(thr.receiver, ws)
		self.assertEqual(thr.outFName, "biblio.bib")
		self.assertEqual(thr.texFiles, ["main.tex"])

	def test_run(self):
		"""test run"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_exportTexBib(ws, ["main.tex"], "biblio.bib", p)
		self.assertTrue(ws.running)
		with patch("physbiblio.export.pbExport.exportForTexFile") as _fun,\
				patch("time.sleep") as _sl,\
				patch("physbiblio.gui.commonClasses.WriteStream.start") as _st,\
				MagicMock() as h1:
			thr.finished.connect(h1)
			thr.run()
			_fun.assert_called_once_with(["main.tex"], "biblio.bib")
			self.assertFalse(ws.running)
			_st.assert_called_once_with()
			_sl.assert_called_once_with(0.1)
			h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_exportTexBib(ws, ["main.tex"], "biblio.bib", p)
		pBExport.exportForTexFlag = True
		self.assertTrue(pBExport.exportForTexFlag)
		thr.setStopFlag()
		self.assertFalse(pBExport.exportForTexFlag)

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_thread_cleanSpare(GUITestCase):
	"""
	Test the functions in threadElements.thread_cleanSpare
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_cleanSpare(ws, p)
		self.assertIsInstance(thr, MyThread)
		self.assertEqual(thr.parent(), p)
		self.assertEqual(thr.receiver, ws)
		self.assertRaises(NotImplementedError, thr.setStopFlag)

	def test_run(self):
		"""test run"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_cleanSpare(ws, p)
		self.assertTrue(ws.running)
		with patch("physbiblio.database.utilities.cleanSpareEntries") as _fun,\
				patch("physbiblio.gui.commonClasses.WriteStream.start") as _st,\
				MagicMock() as h1:
			thr.finished.connect(h1)
			thr.run()
			_fun.assert_called_once_with()
			self.assertFalse(ws.running)
			_st.assert_called_once_with()
			h1.assert_called_once_with()

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_thread_cleanSparePDF(GUITestCase):
	"""
	Test the functions in threadElements.thread_cleanSparePDF
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_cleanSparePDF(ws, p)
		self.assertIsInstance(thr, MyThread)
		self.assertEqual(thr.parent(), p)
		self.assertEqual(thr.receiver, ws)
		self.assertRaises(NotImplementedError, thr.setStopFlag)

	def test_run(self):
		"""test run"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_cleanSparePDF(ws, p)
		self.assertTrue(ws.running)
		with patch("physbiblio.pdf.localPDF.removeSparePDFFolders") as _fun,\
				patch("physbiblio.gui.commonClasses.WriteStream.start") as _st,\
				MagicMock() as h1:
			thr.finished.connect(h1)
			thr.run()
			_fun.assert_called_once_with()
			self.assertFalse(ws.running)
			_st.assert_called_once_with()
			h1.assert_called_once_with()

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class Test_thread_fieldsArxiv(GUITestCase):
	"""
	Test the functions in threadElements.thread_fieldsArxiv
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_fieldsArxiv(ws, ["a", "b"], ["abstract", "arxiv"], p)
		self.assertIsInstance(thr, MyThread)
		self.assertEqual(thr.parent(), p)
		self.assertEqual(thr.receiver, ws)
		self.assertEqual(thr.entries, ["a", "b"])
		self.assertEqual(thr.fields, ["abstract", "arxiv"])

	def test_run(self):
		"""test run"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_fieldsArxiv(ws, ["a", "b"], ["abstract", "arxiv"], p)
		self.assertTrue(ws.running)
		with patch("physbiblio.database.entries.getFieldsFromArxiv") as _fun,\
				patch("time.sleep") as _sl,\
				patch("physbiblio.gui.commonClasses.WriteStream.start") as _st,\
				MagicMock() as h1:
			thr.finished.connect(h1)
			thr.run()
			_fun.assert_called_once_with(["a", "b"], ["abstract", "arxiv"])
			self.assertFalse(ws.running)
			_st.assert_called_once_with()
			_sl.assert_called_once_with(0.1)
			h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		p = QWidget()
		q = Queue()
		ws = WriteStream(q)
		thr = thread_fieldsArxiv(ws, ["a", "b"], ["abstract", "arxiv"], p)
		pBDB.bibs.getArxivFieldsFlag = True
		self.assertTrue(pBDB.bibs.getArxivFieldsFlag)
		thr.setStopFlag()
		self.assertFalse(pBDB.bibs.getArxivFieldsFlag)

if __name__=='__main__':
	unittest.main()
