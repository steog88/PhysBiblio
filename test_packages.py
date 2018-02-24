#!/usr/bin/env python
"""
Test file for the packages in the PhysBiblio application, a bibliography manager written in Python.

This file is part of the PhysBiblio package.
"""
import sys, datetime, traceback, os
import shutil
if sys.version_info[0] < 3:
	import unittest2 as unittest
else:
	import unittest
from mock import MagicMock

try:
	from physbiblio.errors import pBErrorManager
	from physbiblio.config import pbConfig
	from physbiblio.webimport.webInterf import physBiblioWeb
	from physbiblio.pdf import pBPDF
	from physbiblio.database import pBDB
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

shortTests = True

def test_pBErrorManager():
	"""
	Test pBErrorManager raising few exceptions.
	"""
	print("Raising some test exceptions:")
	try:
		raise Exception("Test warning")
	except Exception as e:
		pBErrorManager(str(e), traceback, priority = 0)
	try:
		raise Exception("Test error")
	except Exception as e:
		pBErrorManager(str(e), traceback, priority = 1)
	try:
		raise Exception("Test critical error")
	except Exception as e:
		pBErrorManager(str(e), traceback, priority = 2)
	print("Done!")

@unittest.skipIf(shortTests, "Long tests")
class TestWebImportMethods(unittest.TestCase):
	"""
	Test the functions that import entries from the web.
	Should not fail if everything works fine.

	Tests also pbWriter._entry_to_bibtex using the other functions
	"""
	def test_methods(self):
		print(physBiblioWeb.webSearch.keys())
		tests = {
			"arxiv": "1507.08204",
			"doi": "10.1088/0954-3899/43/3/033001",
			"inspire": "Gariazzo:2015rra",
			"inspireoai": "1385583",
			"isbn": "9780198508717",
			}
		for method, string in tests.items():
			print(method)
			if method == "inspireoai":
				print(physBiblioWeb.webSearch[method].retrieveOAIData(string))
			else:
				print(physBiblioWeb.webSearch[method].retrieveUrlFirst(string))
				print(physBiblioWeb.webSearch[method].retrieveUrlAll(string))
		print(physBiblioWeb.webSearch["inspire"].retrieveInspireID(tests["inspire"]))

	def test_inspireoai(self):
		date1 = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
		date2 = datetime.date.today().strftime("%Y-%m-%d")
		yren, monen, dayen = date1.split('-')
		yrst, monst, dayst = date2.split('-')
		date1 = datetime.datetime(int(yren), int(monen), int(dayen))
		date2 = datetime.datetime(int(yrst), int(monst), int(dayst))
		print(physBiblioWeb.webSearch["inspireoai"].retrieveOAIUpdates(date1, date2))

@unittest.skipIf(shortTests, "Long tests")
class TestPdfMethods(unittest.TestCase):
	def test_fnames(self):
		self.assertEqual(pBPDF.badFName(r'a\b/c:d*e?f"g<h>i|' + "j'"),
			"a_b_c_d_e_f_g_h_i_j_")
		self.assertEqual(pBPDF.getFileDir(r'a\b/c:d*e?f"g<h>i|' + "j'"),
			os.path.join(pBPDF.pdfDir, "a_b_c_d_e_f_g_h_i_j_"))
		testPaperFolder = pBPDF.getFileDir("abc.def")
		pBDB.bibs.getField = MagicMock(return_value="12345678")
		self.assertEqual(pBPDF.getFilePath("abc.def", "arxiv"),
			os.path.join(testPaperFolder, "12345678.pdf"))

	def test_createFolder(self):
		pBPDF.createFolder("abc.def")
		self.assertTrue(os.path.exists(pBPDF.getFileDir("abc.def")))
		pBPDF.renameFolder("abc.def", "abc.fed")
		self.assertFalse(os.path.exists(pBPDF.getFileDir("abc.def")))
		self.assertTrue(os.path.exists(pBPDF.getFileDir("abc.fed")))
		open(os.path.join(pBPDF.pdfDir, "empty.pdf"), 'a').close()
		pBDB.bibs.getField = MagicMock(return_value="12345678")
		pBPDF.copyNewFile("abc.fed", os.path.join(pBPDF.pdfDir, "empty.pdf"), "arxiv")
		pBPDF.copyNewFile("abc.fed", os.path.join(pBPDF.pdfDir, "empty.pdf"),
			customName = "empty.pdf")
		self.assertTrue(os.path.exists(pBPDF.getFilePath("abc.fed", "arxiv")))
		os.remove(os.path.join(pBPDF.pdfDir, "empty.pdf"))
		self.assertFalse(os.path.exists(os.path.join(pBPDF.pdfDir, "empty.pdf")))
		pBPDF.copyToDir(pBPDF.pdfDir, "abc.fed", "arxiv")
		self.assertTrue(os.path.exists(os.path.join(pBPDF.pdfDir, "12345678.pdf")))
		os.remove(os.path.join(pBPDF.pdfDir, "12345678.pdf"))
		shutil.rmtree(pBPDF.getFileDir("abc.fed"))

	def test_download(self):
		pBDB.bibs.getField = MagicMock(return_value="1507.08204")
		pBPDF.downloadArxiv("abc.def")
		self.assertTrue(pBPDF.checkFile("abc.def", "arxiv"))
		self.assertEqual(pBPDF.getExisting("abc.def", fullPath = False),
			["1507.08204.pdf"])
		self.assertEqual(pBPDF.getExisting("abc.def", fullPath = True),
			[os.path.join(pBPDF.getFileDir("abc.def"), "1507.08204.pdf")])
		pBPDF.removeFile("abc.def", "arxiv")
		self.assertFalse(pBPDF.checkFile("abc.def", "arxiv"))
		shutil.rmtree(pBPDF.getFileDir("abc.def"))

	def test_removeSpare(self):
		pBDB.bibs.getAll = MagicMock(return_value=[{"bibkey":"abc"}, {"bibkey":"def"}])
		pBPDF.pdfDir = os.path.join(pbConfig.path, "tmppdf")
		for q in ["abc", "def", "ghi"]:
			pBPDF.createFolder(q)
			self.assertTrue(os.path.exists(pBPDF.getFileDir(q)))
		pBPDF.removeSparePDFFolders()
		for q in ["abc", "def"]:
			self.assertTrue(os.path.exists(pBPDF.getFileDir(q)))
		self.assertFalse(os.path.exists(pBPDF.getFileDir("ghi")))
		shutil.rmtree(pBPDF.pdfDir)

if __name__=='__main__':
	pbConfig.params["logFile"] = "test_packages.log"
	logFileName = os.path.join(pbConfig.path, pbConfig.params["logFile"])
	os.remove(logFileName) if os.path.exists(logFileName) else None
	try:
		test_pBErrorManager()
	except:
		print("#"*40 + "\nException encountered during execution!\n" + "#"*40)
		print(traceback.format_exc())
		print("Please read the traceback and try to discover what went wrong.")
		print("To get support, you may open an issue here: https://github.com/steog88/physBiblio/issues\n" + "#"*40)
	else:
		print("\nStarting tests...\n")
		unittest.main()
		print("#"*20 + "\nAll the tests were completed!\n" + "#"*20)
