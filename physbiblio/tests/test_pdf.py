#!/usr/bin/env python
"""Test file for the physbiblio.pdf module.

This file is part of the physbiblio package.
"""
import sys
import traceback
import os
import shutil

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch, call
else:
	import unittest
	from unittest.mock import patch, call

try:
	from physbiblio.setuptests import *
	from physbiblio.config import pbConfig
	from physbiblio.database import pBDB, PhysBiblioDB
	from physbiblio.pdf import pBPDF
except ImportError:
	print("Could not find physbiblio and its modules!")
	raise
except Exception:
	print(traceback.format_exc())


pBPDF.pdfDir = os.path.join(pbConfig.dataPath, "testpdf_%s"%today_ymd)


@unittest.skipIf(skipTestsSettings.long, "Long tests")
class TestPdfMethods(unittest.TestCase):
	"""Test the methods and functions in the pdf module"""

	def test_fnames(self):
		"""Test names of folders and directories"""
		self.assertEqual(pBPDF.badFName(r'a\b/c:d*e?f"g<h>i|' + "j'"),
			"a_b_c_d_e_f_g_h_i_j_")
		self.assertEqual(pBPDF.badFName(True), "")
		self.assertEqual(pBPDF.getFileDir(r'a\b/c:d*e?f"g<h>i|' + "j'"),
			os.path.join(pBPDF.pdfDir, "a_b_c_d_e_f_g_h_i_j_"))
		testPaperFolder = pBPDF.getFileDir("abc.def")
		with patch('physbiblio.database.Entries.getField',
				return_value="12345678") as _mock:
			self.assertEqual(pBPDF.getFilePath("abc.def", "arxiv"),
				os.path.join(testPaperFolder, "12345678.pdf"))

	def test_manageFiles(self):
		"""Test creation, copy and deletion of files and folders"""
		emptyPdfName = os.path.join(pBPDF.pdfDir, "tests_%s.pdf"%today_ymd)
		pBPDF.createFolder("abc.def")
		self.assertTrue(os.path.exists(pBPDF.getFileDir("abc.def")))
		pBPDF.renameFolder("abc.def", "abc.fed")
		self.assertFalse(os.path.exists(pBPDF.getFileDir("abc.def")))
		self.assertTrue(os.path.exists(pBPDF.getFileDir("abc.fed")))
		open(emptyPdfName, 'a').close()
		with patch('physbiblio.database.Entries.getField',
				return_value="12345678") as _mock:
			pBPDF.copyNewFile("abc.fed", emptyPdfName, "arxiv")
			pBPDF.copyNewFile("abc.fed", emptyPdfName,
				customName="empty.pdf")
			self.assertTrue(os.path.exists(
				pBPDF.getFilePath("abc.fed", "arxiv")))
			os.remove(emptyPdfName)
			self.assertFalse(os.path.exists(emptyPdfName))
			pBPDF.copyToDir(pBPDF.pdfDir, "abc.fed", "arxiv")
			self.assertTrue(os.path.exists(
				os.path.join(pBPDF.pdfDir, "12345678.pdf")))
			pBPDF.mergePDFFolders("abc.fed", "cba.fed")
			self.assertTrue(os.path.exists(
				pBPDF.getFilePath("cba.fed", "arxiv")))
			self.assertTrue(pBPDF.removeFile("abc.fed", "arxiv"))
			self.assertFalse(pBPDF.removeFile("abc.fed", "arxiv"))
			os.remove(os.path.join(pBPDF.pdfDir, "12345678.pdf"))
			shutil.rmtree(pBPDF.getFileDir("abc.fed"))
			shutil.rmtree(pBPDF.getFileDir("cba.fed"))

	@unittest.skipIf(skipTestsSettings.online, "Online tests")
	def test_download(self):
		"""Test downloadArxiv"""
		with patch('physbiblio.database.Entries.getField',
				return_value="1806.11344") as _mock:
			self.assertTrue(pBPDF.downloadArxiv("abc.def"))
			self.assertTrue(pBPDF.checkFile("abc.def", "arxiv"))
			self.assertEqual(pBPDF.getExisting("abc.def", fullPath=False),
				["1806.11344.pdf"])
			self.assertEqual(pBPDF.getExisting("abc.def", fullPath=True),
				[os.path.join(pBPDF.getFileDir("abc.def"), "1806.11344.pdf")])
			open(os.path.join(pBPDF.getFileDir("abc.def"), "1806.11344"),
				"w").close()
			self.assertEqual(pBPDF.getExisting("abc.def", fullPath=False),
				["1806.11344.pdf"])
			self.assertTrue(pBPDF.removeFile("abc.def", "arxiv"))
			self.assertTrue(pBPDF.removeFile("abc.def", "file",
				os.path.join(pBPDF.getFileDir("abc.def"), "1806.11344")))
			self.assertFalse(pBPDF.checkFile("abc.def", "arxiv"))
		with patch('physbiblio.database.Entries.getField',
				side_effect=["1801.15000", "1801.15000", "", "", None, None]
				) as _mock:
			self.assertFalse(pBPDF.downloadArxiv("abc.def"))
			self.assertFalse(pBPDF.downloadArxiv("abc.def"))
			self.assertFalse(pBPDF.downloadArxiv("abc.def"))
		shutil.rmtree(pBPDF.getFileDir("abc.def"))

	def test_removeSpare(self):
		"""Test finding spare folders"""
		with patch('physbiblio.database.Entries.fetchCursor',
				return_value=[{"bibkey":"abc"}, {"bibkey":"def"}]) as _mock:
			for q in ["abc", "def", "ghi"]:
				pBPDF.createFolder(q)
				self.assertTrue(os.path.exists(pBPDF.getFileDir(q)))
			pBPDF.removeSparePDFFolders()
			for q in ["abc", "def"]:
				self.assertTrue(os.path.exists(pBPDF.getFileDir(q)))
			self.assertFalse(os.path.exists(pBPDF.getFileDir("ghi")))
		shutil.rmtree(pBPDF.pdfDir)

	def test_dirSize(self):
		"""test dirSize"""
		if sys.version_info[0] < 3:
			with patch("os.path.getsize",
					side_effect=[1, 100, 1, 100, 100]) as _gs,\
					patch("os.listdir",
						side_effect=[["a", "b"], ["c", "d", "e"]]) as _ld,\
					patch("os.path.isfile",
						side_effect=[True, False, True, True, False]) as _if,\
					patch("os.path.isdir",
						side_effect=[True, False]) as _id:
				self.assertEqual(pBPDF.dirSize("f"), 302)
				_gs.assert_has_calls([
					call('f'),
					call('f/a'),
					call('f/b'),
					call('f/b/c'),
					call('f/b/d')])
				_ld.assert_has_calls([call('f'), call('f/b')])
				_if.assert_has_calls([
					call('f/a'), call('f/b'), call('f/b/c'),
					call('f/b/d'), call('f/b/e')])
				_id.assert_has_calls([call('f/b'), call('f/b/e')])
			with patch("os.path.getsize",
						return_value=100) as _gs,\
					patch("os.listdir",
						side_effect=[["a", "b"], ["c", "d", "e"]]) as _ld,\
					patch("os.path.isfile",
						side_effect=[True, False, True, True, False]) as _if,\
					patch("os.path.isdir",
						side_effect=[True, False]) as _id:
				self.assertEqual(pBPDF.dirSize("f", dirs=False), 300)
				_gs.assert_has_calls([
					call('f/a'),
					call('f/b/c'),
					call('f/b/d')])
				_ld.assert_has_calls([call('f'), call('f/b')])
				_if.assert_has_calls([
					call('f/a'), call('f/b'), call('f/b/c'),
					call('f/b/d'), call('f/b/e')])
				_id.assert_has_calls([call('f/b'), call('f/b/e')])
		else:
			with patch("os.path.getsize",
					side_effect=[1, 1, 100, 100, 100]) as _gs,\
					patch("os.walk",
						return_value=[["f", ["b"],
							["a", "b/c", "b/d", "b/e"]]]) as _wa,\
					patch("os.path.isfile",
						side_effect=[True, True, True, False]) as _if:
				self.assertEqual(pBPDF.dirSize("f"), 302)
				_gs.assert_has_calls([
					call('f'),
					call('f/b'),
					call('f/a'),
					call('f/b/c'),
					call('f/b/d')])
				_wa.assert_called_once_with('f')
				_if.assert_has_calls([
					call('f/a'), call('f/b/c'),
					call('f/b/d'), call('f/b/e')])
			with patch("os.path.getsize",
					side_effect=[100, 100, 100]) as _gs,\
					patch("os.walk",
						return_value=[["f", ["b"],
							["a", "b/c", "b/d", "b/e"]]]) as _wa,\
					patch("os.path.isfile",
						side_effect=[True, True, True, False]) as _if:
				self.assertEqual(pBPDF.dirSize("f", dirs=False), 300)
				_gs.assert_has_calls([
					call('f/a'),
					call('f/b/c'),
					call('f/b/d')])
				_wa.assert_called_once_with('f')
				_if.assert_has_calls([
					call('f/a'), call('f/b/c'),
					call('f/b/d'), call('f/b/e')])

	def test_getSizeWUnits(self):
		"""test getSizeWUnits"""
		with patch("logging.Logger.warning") as _w:
			self.assertEqual(pBPDF.getSizeWUnits(2048**2), "4.00MB")
			self.assertEqual(pBPDF.getSizeWUnits(2048**2, units="mb"),
				"4.00MB")
			self.assertEqual(pBPDF.getSizeWUnits(2048**2, units="kb"),
				"4096.00KB")
			self.assertEqual(pBPDF.getSizeWUnits(2048**2, units="PB"),
				"0.00PB")
			self.assertEqual(
				pBPDF.getSizeWUnits(2048**2, units="gb", fmt="%.3f"),
				"0.004GB")
			_w.assert_not_called()
		with patch("logging.Logger.warning") as _w:
			self.assertEqual(pBPDF.getSizeWUnits(2048**2, units="m"),
				"4.00MB")
			_w.assert_called_once_with("Invalid units. Changing to 'MB'.")
		with patch("logging.Logger.warning") as _w:
			self.assertEqual(pBPDF.getSizeWUnits("a"), "nan")
			_w.assert_called_once_with('Invalid size. It must be a number!')
		with patch("logging.Logger.warning") as _w:
			self.assertEqual(pBPDF.getSizeWUnits(2048**2, fmt="%"), "4.00MB")
			_w.assert_called_once_with("Invalid format. Using '%.2f'")


if __name__=='__main__':
	unittest.main()
