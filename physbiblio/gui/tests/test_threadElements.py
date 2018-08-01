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
	from physbiblio.gui.setuptests import *
	from physbiblio.gui.threadElements import *
	from physbiblio.gui.commonClasses import *
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipGuiTests, "GUI tests")
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
		self.assertEqual(thr.parent, p)
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
			_w.assert_called_once_with('Error when executing check_outdated. Maybe you are using a developing version', exc_info=True)
		h1.assert_not_called()
		h2.assert_called_once_with()
		with patch("physbiblio.gui.threadElements.check_outdated",
				new = fake_urlerror) as _cho,\
				patch("logging.Logger.warning") as _w:
			thr.run()
			_w.assert_called_once_with('Error when trying to check new versions. Are you offline?', exc_info=True)

@unittest.skipIf(skipGuiTests, "GUI tests")
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
		self.assertEqual(thr.parent, p)
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
			_sou.assert_called_once_with(123, entries = [[]], force = True, reloadAll = True)
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

@unittest.skipIf(skipGuiTests, "GUI tests")
class Test_thread_updateInspireInfo(GUITestCase):
	"""
	Test the functions in threadElements.thread_updateInspireInfo
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, "r")
		# self.assertIsInstance(thr, MyThread)
		# self.assertEqual(thr.parent, p)
		# self.assertEqual(thr.startFrom, 123)
		# self.assertEqual(thr.receiver, ws)
		# self.assertEqual(thr.useEntries, [[]])
		# self.assertEqual(thr.force, True)
		# self.assertEqual(thr.reloadAll, "r")

	def test_run(self):
		"""test run"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, True)
		# self.assertTrue(ws.running)
		# h1 = MagicMock()
		# thr.finished.connect(h1)
		# with patch("physbiblio.database.entries.searchOAIUpdates") as _sou,\
				# patch("time.sleep") as _sl,\
				# patch("physbiblio.gui.commonClasses.WriteStream.start") as _st:
			# thr.run()
			# _sou.assert_called_once_with(123, entries = [[]], force = True, reloadAll = True)
			# self.assertFalse(ws.running)
			# _st.assert_called_once_with()
			# _sl.assert_called_once_with(0.1)
			# h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 0)
		# pBDB.bibs.runningOAIUpdates = True
		# self.assertTrue(pBDB.bibs.runningOAIUpdates)
		# thr.setStopFlag()
		# self.assertFalse(pBDB.bibs.runningOAIUpdates)

@unittest.skipIf(skipGuiTests, "GUI tests")
class Test_thread_downloadArxiv(GUITestCase):
	"""
	Test the functions in threadElements.thread_downloadArxiv
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, "r")
		# self.assertIsInstance(thr, MyThread)
		# self.assertEqual(thr.parent, p)
		# self.assertEqual(thr.startFrom, 123)
		# self.assertEqual(thr.receiver, ws)
		# self.assertEqual(thr.useEntries, [[]])
		# self.assertEqual(thr.force, True)
		# self.assertEqual(thr.reloadAll, "r")

	def test_run(self):
		"""test run"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, True)
		# self.assertTrue(ws.running)
		# h1 = MagicMock()
		# thr.finished.connect(h1)
		# with patch("physbiblio.database.entries.searchOAIUpdates") as _sou,\
				# patch("time.sleep") as _sl,\
				# patch("physbiblio.gui.commonClasses.WriteStream.start") as _st:
			# thr.run()
			# _sou.assert_called_once_with(123, entries = [[]], force = True, reloadAll = True)
			# self.assertFalse(ws.running)
			# _st.assert_called_once_with()
			# _sl.assert_called_once_with(0.1)
			# h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 0)
		# pBDB.bibs.runningOAIUpdates = True
		# self.assertTrue(pBDB.bibs.runningOAIUpdates)
		# thr.setStopFlag()
		# self.assertFalse(pBDB.bibs.runningOAIUpdates)

@unittest.skipIf(skipGuiTests, "GUI tests")
class Test_thread_processLatex(GUITestCase):
	"""
	Test the functions in threadElements.thread_processLatex
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, "r")
		# self.assertIsInstance(thr, MyThread)
		# self.assertEqual(thr.parent, p)
		# self.assertEqual(thr.startFrom, 123)
		# self.assertEqual(thr.receiver, ws)
		# self.assertEqual(thr.useEntries, [[]])
		# self.assertEqual(thr.force, True)
		# self.assertEqual(thr.reloadAll, "r")

	def test_run(self):
		"""test run"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, True)
		# self.assertTrue(ws.running)
		# h1 = MagicMock()
		# thr.finished.connect(h1)
		# with patch("physbiblio.database.entries.searchOAIUpdates") as _sou,\
				# patch("time.sleep") as _sl,\
				# patch("physbiblio.gui.commonClasses.WriteStream.start") as _st:
			# thr.run()
			# _sou.assert_called_once_with(123, entries = [[]], force = True, reloadAll = True)
			# self.assertFalse(ws.running)
			# _st.assert_called_once_with()
			# _sl.assert_called_once_with(0.1)
			# h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 0)
		# pBDB.bibs.runningOAIUpdates = True
		# self.assertTrue(pBDB.bibs.runningOAIUpdates)
		# thr.setStopFlag()
		# self.assertFalse(pBDB.bibs.runningOAIUpdates)

@unittest.skipIf(skipGuiTests, "GUI tests")
class Test_thread_authorStats(GUITestCase):
	"""
	Test the functions in threadElements.thread_authorStats
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, "r")
		# self.assertIsInstance(thr, MyThread)
		# self.assertEqual(thr.parent, p)
		# self.assertEqual(thr.startFrom, 123)
		# self.assertEqual(thr.receiver, ws)
		# self.assertEqual(thr.useEntries, [[]])
		# self.assertEqual(thr.force, True)
		# self.assertEqual(thr.reloadAll, "r")

	def test_run(self):
		"""test run"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, True)
		# self.assertTrue(ws.running)
		# h1 = MagicMock()
		# thr.finished.connect(h1)
		# with patch("physbiblio.database.entries.searchOAIUpdates") as _sou,\
				# patch("time.sleep") as _sl,\
				# patch("physbiblio.gui.commonClasses.WriteStream.start") as _st:
			# thr.run()
			# _sou.assert_called_once_with(123, entries = [[]], force = True, reloadAll = True)
			# self.assertFalse(ws.running)
			# _st.assert_called_once_with()
			# _sl.assert_called_once_with(0.1)
			# h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 0)
		# pBDB.bibs.runningOAIUpdates = True
		# self.assertTrue(pBDB.bibs.runningOAIUpdates)
		# thr.setStopFlag()
		# self.assertFalse(pBDB.bibs.runningOAIUpdates)

@unittest.skipIf(skipGuiTests, "GUI tests")
class Test_thread_paperStats(GUITestCase):
	"""
	Test the functions in threadElements.thread_paperStats
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, "r")
		# self.assertIsInstance(thr, MyThread)
		# self.assertEqual(thr.parent, p)
		# self.assertEqual(thr.startFrom, 123)
		# self.assertEqual(thr.receiver, ws)
		# self.assertEqual(thr.useEntries, [[]])
		# self.assertEqual(thr.force, True)
		# self.assertEqual(thr.reloadAll, "r")

	def test_run(self):
		"""test run"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, True)
		# self.assertTrue(ws.running)
		# h1 = MagicMock()
		# thr.finished.connect(h1)
		# with patch("physbiblio.database.entries.searchOAIUpdates") as _sou,\
				# patch("time.sleep") as _sl,\
				# patch("physbiblio.gui.commonClasses.WriteStream.start") as _st:
			# thr.run()
			# _sou.assert_called_once_with(123, entries = [[]], force = True, reloadAll = True)
			# self.assertFalse(ws.running)
			# _st.assert_called_once_with()
			# _sl.assert_called_once_with(0.1)
			# h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 0)
		# pBDB.bibs.runningOAIUpdates = True
		# self.assertTrue(pBDB.bibs.runningOAIUpdates)
		# thr.setStopFlag()
		# self.assertFalse(pBDB.bibs.runningOAIUpdates)

@unittest.skipIf(skipGuiTests, "GUI tests")
class Test_thread_loadAndInsert(GUITestCase):
	"""
	Test the functions in threadElements.thread_loadAndInsert
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, "r")
		# self.assertIsInstance(thr, MyThread)
		# self.assertEqual(thr.parent, p)
		# self.assertEqual(thr.startFrom, 123)
		# self.assertEqual(thr.receiver, ws)
		# self.assertEqual(thr.useEntries, [[]])
		# self.assertEqual(thr.force, True)
		# self.assertEqual(thr.reloadAll, "r")

	def test_run(self):
		"""test run"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, True)
		# self.assertTrue(ws.running)
		# h1 = MagicMock()
		# thr.finished.connect(h1)
		# with patch("physbiblio.database.entries.searchOAIUpdates") as _sou,\
				# patch("time.sleep") as _sl,\
				# patch("physbiblio.gui.commonClasses.WriteStream.start") as _st:
			# thr.run()
			# _sou.assert_called_once_with(123, entries = [[]], force = True, reloadAll = True)
			# self.assertFalse(ws.running)
			# _st.assert_called_once_with()
			# _sl.assert_called_once_with(0.1)
			# h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 0)
		# pBDB.bibs.runningOAIUpdates = True
		# self.assertTrue(pBDB.bibs.runningOAIUpdates)
		# thr.setStopFlag()
		# self.assertFalse(pBDB.bibs.runningOAIUpdates)

@unittest.skipIf(skipGuiTests, "GUI tests")
class Test_thread_cleanAllBibtexs(GUITestCase):
	"""
	Test the functions in threadElements.thread_cleanAllBibtexs
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, "r")
		# self.assertIsInstance(thr, MyThread)
		# self.assertEqual(thr.parent, p)
		# self.assertEqual(thr.startFrom, 123)
		# self.assertEqual(thr.receiver, ws)
		# self.assertEqual(thr.useEntries, [[]])
		# self.assertEqual(thr.force, True)
		# self.assertEqual(thr.reloadAll, "r")

	def test_run(self):
		"""test run"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, True)
		# self.assertTrue(ws.running)
		# h1 = MagicMock()
		# thr.finished.connect(h1)
		# with patch("physbiblio.database.entries.searchOAIUpdates") as _sou,\
				# patch("time.sleep") as _sl,\
				# patch("physbiblio.gui.commonClasses.WriteStream.start") as _st:
			# thr.run()
			# _sou.assert_called_once_with(123, entries = [[]], force = True, reloadAll = True)
			# self.assertFalse(ws.running)
			# _st.assert_called_once_with()
			# _sl.assert_called_once_with(0.1)
			# h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 0)
		# pBDB.bibs.runningOAIUpdates = True
		# self.assertTrue(pBDB.bibs.runningOAIUpdates)
		# thr.setStopFlag()
		# self.assertFalse(pBDB.bibs.runningOAIUpdates)

@unittest.skipIf(skipGuiTests, "GUI tests")
class Test_thread_findBadBibtexs(GUITestCase):
	"""
	Test the functions in threadElements.thread_findBadBibtexs
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, "r")
		# self.assertIsInstance(thr, MyThread)
		# self.assertEqual(thr.parent, p)
		# self.assertEqual(thr.startFrom, 123)
		# self.assertEqual(thr.receiver, ws)
		# self.assertEqual(thr.useEntries, [[]])
		# self.assertEqual(thr.force, True)
		# self.assertEqual(thr.reloadAll, "r")

	def test_run(self):
		"""test run"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, True)
		# self.assertTrue(ws.running)
		# h1 = MagicMock()
		# thr.finished.connect(h1)
		# with patch("physbiblio.database.entries.searchOAIUpdates") as _sou,\
				# patch("time.sleep") as _sl,\
				# patch("physbiblio.gui.commonClasses.WriteStream.start") as _st:
			# thr.run()
			# _sou.assert_called_once_with(123, entries = [[]], force = True, reloadAll = True)
			# self.assertFalse(ws.running)
			# _st.assert_called_once_with()
			# _sl.assert_called_once_with(0.1)
			# h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 0)
		# pBDB.bibs.runningOAIUpdates = True
		# self.assertTrue(pBDB.bibs.runningOAIUpdates)
		# thr.setStopFlag()
		# self.assertFalse(pBDB.bibs.runningOAIUpdates)

@unittest.skipIf(skipGuiTests, "GUI tests")
class Test_thread_importFromBib(GUITestCase):
	"""
	Test the functions in threadElements.thread_importFromBib
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, "r")
		# self.assertIsInstance(thr, MyThread)
		# self.assertEqual(thr.parent, p)
		# self.assertEqual(thr.startFrom, 123)
		# self.assertEqual(thr.receiver, ws)
		# self.assertEqual(thr.useEntries, [[]])
		# self.assertEqual(thr.force, True)
		# self.assertEqual(thr.reloadAll, "r")

	def test_run(self):
		"""test run"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, True)
		# self.assertTrue(ws.running)
		# h1 = MagicMock()
		# thr.finished.connect(h1)
		# with patch("physbiblio.database.entries.searchOAIUpdates") as _sou,\
				# patch("time.sleep") as _sl,\
				# patch("physbiblio.gui.commonClasses.WriteStream.start") as _st:
			# thr.run()
			# _sou.assert_called_once_with(123, entries = [[]], force = True, reloadAll = True)
			# self.assertFalse(ws.running)
			# _st.assert_called_once_with()
			# _sl.assert_called_once_with(0.1)
			# h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 0)
		# pBDB.bibs.runningOAIUpdates = True
		# self.assertTrue(pBDB.bibs.runningOAIUpdates)
		# thr.setStopFlag()
		# self.assertFalse(pBDB.bibs.runningOAIUpdates)

@unittest.skipIf(skipGuiTests, "GUI tests")
class Test_thread_exportTexBib(GUITestCase):
	"""
	Test the functions in threadElements.thread_exportTexBib
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, "r")
		# self.assertIsInstance(thr, MyThread)
		# self.assertEqual(thr.parent, p)
		# self.assertEqual(thr.startFrom, 123)
		# self.assertEqual(thr.receiver, ws)
		# self.assertEqual(thr.useEntries, [[]])
		# self.assertEqual(thr.force, True)
		# self.assertEqual(thr.reloadAll, "r")

	def test_run(self):
		"""test run"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, True)
		# self.assertTrue(ws.running)
		# h1 = MagicMock()
		# thr.finished.connect(h1)
		# with patch("physbiblio.database.entries.searchOAIUpdates") as _sou,\
				# patch("time.sleep") as _sl,\
				# patch("physbiblio.gui.commonClasses.WriteStream.start") as _st:
			# thr.run()
			# _sou.assert_called_once_with(123, entries = [[]], force = True, reloadAll = True)
			# self.assertFalse(ws.running)
			# _st.assert_called_once_with()
			# _sl.assert_called_once_with(0.1)
			# h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 0)
		# pBDB.bibs.runningOAIUpdates = True
		# self.assertTrue(pBDB.bibs.runningOAIUpdates)
		# thr.setStopFlag()
		# self.assertFalse(pBDB.bibs.runningOAIUpdates)

@unittest.skipIf(skipGuiTests, "GUI tests")
class Test_thread_cleanSpare(GUITestCase):
	"""
	Test the functions in threadElements.thread_cleanSpare
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, "r")
		# self.assertIsInstance(thr, MyThread)
		# self.assertEqual(thr.parent, p)
		# self.assertEqual(thr.startFrom, 123)
		# self.assertEqual(thr.receiver, ws)
		# self.assertEqual(thr.useEntries, [[]])
		# self.assertEqual(thr.force, True)
		# self.assertEqual(thr.reloadAll, "r")

	def test_run(self):
		"""test run"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, True)
		# self.assertTrue(ws.running)
		# h1 = MagicMock()
		# thr.finished.connect(h1)
		# with patch("physbiblio.database.entries.searchOAIUpdates") as _sou,\
				# patch("time.sleep") as _sl,\
				# patch("physbiblio.gui.commonClasses.WriteStream.start") as _st:
			# thr.run()
			# _sou.assert_called_once_with(123, entries = [[]], force = True, reloadAll = True)
			# self.assertFalse(ws.running)
			# _st.assert_called_once_with()
			# _sl.assert_called_once_with(0.1)
			# h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 0)
		# pBDB.bibs.runningOAIUpdates = True
		# self.assertTrue(pBDB.bibs.runningOAIUpdates)
		# thr.setStopFlag()
		# self.assertFalse(pBDB.bibs.runningOAIUpdates)

@unittest.skipIf(skipGuiTests, "GUI tests")
class Test_thread_cleanSparePDF(GUITestCase):
	"""
	Test the functions in threadElements.thread_cleanSparePDF
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, "r")
		# self.assertIsInstance(thr, MyThread)
		# self.assertEqual(thr.parent, p)
		# self.assertEqual(thr.startFrom, 123)
		# self.assertEqual(thr.receiver, ws)
		# self.assertEqual(thr.useEntries, [[]])
		# self.assertEqual(thr.force, True)
		# self.assertEqual(thr.reloadAll, "r")

	def test_run(self):
		"""test run"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, True)
		# self.assertTrue(ws.running)
		# h1 = MagicMock()
		# thr.finished.connect(h1)
		# with patch("physbiblio.database.entries.searchOAIUpdates") as _sou,\
				# patch("time.sleep") as _sl,\
				# patch("physbiblio.gui.commonClasses.WriteStream.start") as _st:
			# thr.run()
			# _sou.assert_called_once_with(123, entries = [[]], force = True, reloadAll = True)
			# self.assertFalse(ws.running)
			# _st.assert_called_once_with()
			# _sl.assert_called_once_with(0.1)
			# h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 0)
		# pBDB.bibs.runningOAIUpdates = True
		# self.assertTrue(pBDB.bibs.runningOAIUpdates)
		# thr.setStopFlag()
		# self.assertFalse(pBDB.bibs.runningOAIUpdates)

@unittest.skipIf(skipGuiTests, "GUI tests")
class Test_thread_fieldsArxiv(GUITestCase):
	"""
	Test the functions in threadElements.thread_fieldsArxiv
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, "r")
		# self.assertIsInstance(thr, MyThread)
		# self.assertEqual(thr.parent, p)
		# self.assertEqual(thr.startFrom, 123)
		# self.assertEqual(thr.receiver, ws)
		# self.assertEqual(thr.useEntries, [[]])
		# self.assertEqual(thr.force, True)
		# self.assertEqual(thr.reloadAll, "r")

	def test_run(self):
		"""test run"""
		p = QWidget()
		# q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 123, p, [[]], True, True)
		# self.assertTrue(ws.running)
		# h1 = MagicMock()
		# thr.finished.connect(h1)
		# with patch("physbiblio.database.entries.searchOAIUpdates") as _sou,\
				# patch("time.sleep") as _sl,\
				# patch("physbiblio.gui.commonClasses.WriteStream.start") as _st:
			# thr.run()
			# _sou.assert_called_once_with(123, entries = [[]], force = True, reloadAll = True)
			# self.assertFalse(ws.running)
			# _st.assert_called_once_with()
			# _sl.assert_called_once_with(0.1)
			# h1.assert_called_once_with()

	def test_setStopFlag(self):
		"""test setStopFlag"""
		q = Queue()
		# ws = WriteStream(q)
		# thr = thread_updateAllBibtexs(ws, 0)
		# pBDB.bibs.runningOAIUpdates = True
		# self.assertTrue(pBDB.bibs.runningOAIUpdates)
		# thr.setStopFlag()
		# self.assertFalse(pBDB.bibs.runningOAIUpdates)

if __name__=='__main__':
	unittest.main()
