#!/usr/bin/env python
"""
Test file for the packages in the PhysBiblio application, a bibliography manager written in Python.

This file is part of the PhysBiblio package.
"""
import sys, datetime, traceback, os
import shutil
if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import MagicMock
else:
	import unittest
	from unittest.mock import MagicMock

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

skipLongTests = False
skipOnlineTests = False

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

# @unittest.skipIf(skipOnlineTests, "Long tests")
class TestWebImportMethods(unittest.TestCase):
	"""
	Test the functions that import entries from the web.
	Should not fail if everything works fine.

	Tests also pbWriter._entry_to_bibtex using the other functions
	"""
	def test_methods_success(self):
		print(physBiblioWeb.webSearch.keys())
		tests = {
			"arxiv": ["1507.08204", """@Article{1507.08204,
         title = "{Light sterile neutrinos}",
          year = "2015",
 archiveprefix = "arXiv",
  primaryclass = "hep-ph",
           doi = "10.1088/0954-3899/43/3/033001",
      abstract = "{The theory and phenomenology of light sterile neutrinos at the eV mass scale
is reviewed. The reactor, Gallium and LSND anomalies are briefly described and
interpreted as indications of the existence of short-baseline oscillations
which require the existence of light sterile neutrinos. The global fits of
short-baseline oscillation data in 3+1 and 3+2 schemes are discussed, together
with the implications for beta-decay and neutrinoless double-beta decay. The
cosmological effects of light sterile neutrinos are briefly reviewed and the
implications of existing cosmological data are discussed. The review concludes
with a summary of future perspectives.}",
         arxiv = "1507.08204",
       authors = "S. Gariazzo and C. Giunti and M. Laveder and Y. F. Li and E. M. Zavanin",
}"""],
			"doi": ["10.1088/0954-3899/43/3/033001", """@article{Gariazzo_2015,
	doi = {10.1088/0954-3899/43/3/033001},
	url = {https://doi.org/10.1088%2F0954-3899%2F43%2F3%2F033001},
	year = 2015,
	month = {mar},
	publisher = {{IOP} Publishing},
	volume = {43},
	number = {3},
	pages = {033001},
	author = {S Gariazzo and C Giunti and M Laveder and Y F Li and E M Zavanin},
	title = {Light sterile neutrinos},
	journal = {Journal of Physics G: Nuclear and Particle Physics}
}"""],
			"inspire": ["Gariazzo:2015rra", """@article{Gariazzo:2015rra,
      author         = "Gariazzo, S. and Giunti, C. and Laveder, M. and Li, Y. F.
                        and Zavanin, E. M.",
      title          = "{Light sterile neutrinos}",
      journal        = "J. Phys.",
      volume         = "G43",
      year           = "2016",
      pages          = "033001",
      doi            = "10.1088/0954-3899/43/3/033001",
      eprint         = "1507.08204",
      archivePrefix  = "arXiv",
      primaryClass   = "hep-ph",
      SLACcitation   = "%%CITATION = ARXIV:1507.08204;%%"
}"""],
			"inspireoai": ["1385583", {'doi': u'10.1088/0954-3899/43/3/033001', 'isbn': None, 'ads': u'2015JPhG...43c3001G', 'pubdate': u'2016-01-13', 'firstdate': u'2015-07-29', 'journal': u'J.Phys.', 'arxiv': u'1507.08204', 'id': '1385583', 'volume': u'G43', 'bibtex': None, 'year': u'2016', 'oldkeys': '', 'bibkey': u'Gariazzo:2015rra', 'pages': u'033001'}],
			"isbn": ["9780198508717", """@book{9780198508717,
  Author = {Carlo Giunti, Chung W. Kim},
  Title = {Fundamentals of Neutrino Physics and Astrophysics},
  Publisher = {OXFORD UNIV PR},
  Year = {2007},
  Date = {2007-05-11},
  PageTotal = {710 Seiten},
  EAN = {9780198508717},
  ISBN = {0198508719},
  URL = {https://www.ebook.de/de/product/7616244/carlo_giunti_chung_w_kim_fundamentals_of_neutrino_physics_and_astrophysics.html}
}"""],
			}
		for method, strings in tests.items():
			print(method)
			if method == "inspireoai":
				self.assertEqual(physBiblioWeb.webSearch[method].retrieveOAIData(strings[0]), strings[1])
			else:
				self.assertEqual(physBiblioWeb.webSearch[method].retrieveUrlFirst(strings[0]).strip(), strings[1].strip())
				self.assertEqual(physBiblioWeb.webSearch[method].retrieveUrlAll(strings[0]).strip(), strings[1].strip())
		self.assertEqual(physBiblioWeb.webSearch["inspire"].retrieveInspireID(tests["inspire"][0]), u'1385583')

	@unittest.skipIf(skipOnlineTests or skipLongTests, "Long tests")
	def test_inspireoai(self):
		date1 = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
		date2 = datetime.date.today().strftime("%Y-%m-%d")
		yren, monen, dayen = date1.split('-')
		yrst, monst, dayst = date2.split('-')
		date1 = datetime.datetime(int(yren), int(monen), int(dayen))
		date2 = datetime.datetime(int(yrst), int(monst), int(dayst))
		print(physBiblioWeb.webSearch["inspireoai"].retrieveOAIUpdates(date1, date2))

@unittest.skipIf(skipLongTests, "Long tests")
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
		self.assertTrue(pBPDF.removeFile("abc.fed", "arxiv"))
		self.assertFalse(pBPDF.removeFile("abc.fed", "arxiv"))
		os.remove(os.path.join(pBPDF.pdfDir, "12345678.pdf"))
		shutil.rmtree(pBPDF.getFileDir("abc.fed"))

	@unittest.skipIf(skipOnlineTests, "Long tests")
	def test_download(self):
		pBDB.bibs.getField = MagicMock(return_value="1507.08204")
		self.assertTrue(pBPDF.downloadArxiv("abc.def"))
		self.assertTrue(pBPDF.checkFile("abc.def", "arxiv"))
		self.assertEqual(pBPDF.getExisting("abc.def", fullPath = False),
			["1507.08204.pdf"])
		self.assertEqual(pBPDF.getExisting("abc.def", fullPath = True),
			[os.path.join(pBPDF.getFileDir("abc.def"), "1507.08204.pdf")])
		self.assertTrue(pBPDF.removeFile("abc.def", "arxiv"))
		self.assertFalse(pBPDF.checkFile("abc.def", "arxiv"))
		pBDB.bibs.getField = MagicMock(return_value="1801.15000")
		self.assertFalse(pBPDF.downloadArxiv("abc.def"))
		pBDB.bibs.getField = MagicMock(return_value="")
		self.assertFalse(pBPDF.downloadArxiv("abc.def"))
		pBDB.bibs.getField = MagicMock(return_value=None)
		self.assertFalse(pBPDF.downloadArxiv("abc.def"))
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

class TestBuilding(unittest.TestCase):
	def test_new(self):
		pass

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
