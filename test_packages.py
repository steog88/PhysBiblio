#!/usr/bin/env python
"""
Test file for the packages in the PhysBiblio application, a bibliography manager written in Python.

This file is part of the PhysBiblio package.
"""
import sys, datetime, traceback, os
from stat import S_IREAD, S_IRGRP, S_IROTH
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
	from physbiblio.database import pBDB, physbiblioDB
	from physbiblio.webimport.webInterf import physBiblioWeb
	from physbiblio.pdf import pBPDF
	from physbiblio.export import pBExport
	from physbiblio.view import pBView
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

skipLongTests = True
skipOnlineTests = True

today_ymd = datetime.datetime.today().strftime('%y%m%d')

#reload DB using a temporary DB file, will be removed at the end 
global pBDB
tempDBName = os.path.join(pbConfig.path, "tests_%s.db"%today_ymd)
pBDB.closeDB()
pBDB = physbiblioDB(tempDBName)
pBDB.loadSubClasses()

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

@unittest.skipIf(skipOnlineTests, "Online tests")
class TestWebImportMethods(unittest.TestCase):
	"""
	Test the functions that import entries from the web.
	Should not fail if everything works fine.

	Tests also pbWriter._entry_to_bibtex using the other functions
	"""
	def test_methods_success(self):
		"""Test webimport with known results"""
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

	def test_methods_insuccess(self):
		"""Test webimport using missing and/or invalid identifiers"""
		print(physBiblioWeb.webSearch.keys())
		tests = {
			"arxiv": ["1801.15000", ""],
			"doi": ["10.1088/9999-3899/43/a/033001", ""],
			"inspire": ["Gariazzo:2014rra", ""],
			"isbn": ["978019850871a", ""],
			}
		self.assertEqual(physBiblioWeb.webSearch["inspireoai"].retrieveOAIData("1110620"), {'doi': None, 'isbn': None, 'ads': None, 'pubdate': None, 'firstdate': None, 'journal': None, 'arxiv': None, 'id': '1110620', 'volume': None, 'bibtex': None, 'year': None, 'oldkeys': '', 'bibkey': None, 'pages': None})
		self.assertFalse(physBiblioWeb.webSearch["inspireoai"].retrieveOAIData("9999999"))
		for method, strings in tests.items():
			print(method)
			res=physBiblioWeb.webSearch[method].retrieveUrlFirst(strings[0])
			print res
			self.assertEqual(res.strip(), strings[1].strip())
			self.assertEqual(physBiblioWeb.webSearch[method].retrieveUrlAll(strings[0]).strip(), strings[1].strip())
		self.assertEqual(physBiblioWeb.webSearch["inspire"].retrieveInspireID(tests["inspire"][0]), "")

	@unittest.skipIf(skipOnlineTests or skipLongTests, "Long tests")
	def test_inspireoai(self):
		"""test retrieve daily data from inspireOAI"""
		date1 = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
		date2 = datetime.date.today().strftime("%Y-%m-%d")
		yren, monen, dayen = date1.split('-')
		yrst, monst, dayst = date2.split('-')
		date1 = datetime.datetime(int(yren), int(monen), int(dayen))
		date2 = datetime.datetime(int(yrst), int(monst), int(dayst))
		print(physBiblioWeb.webSearch["inspireoai"].retrieveOAIUpdates(date1, date2))

@unittest.skipIf(skipLongTests, "Long tests")
class TestPdfMethods(unittest.TestCase):
	"""
	Test the methods and functions in the pdf module
	"""
	def test_fnames(self):
		"""Test names of folders and directories"""
		self.assertEqual(pBPDF.badFName(r'a\b/c:d*e?f"g<h>i|' + "j'"),
			"a_b_c_d_e_f_g_h_i_j_")
		self.assertEqual(pBPDF.getFileDir(r'a\b/c:d*e?f"g<h>i|' + "j'"),
			os.path.join(pBPDF.pdfDir, "a_b_c_d_e_f_g_h_i_j_"))
		testPaperFolder = pBPDF.getFileDir("abc.def")
		pBDB.bibs.getField = MagicMock(return_value="12345678")
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
		pBDB.bibs.getField = MagicMock(return_value="12345678")
		pBPDF.copyNewFile("abc.fed", emptyPdfName, "arxiv")
		pBPDF.copyNewFile("abc.fed", emptyPdfName,
			customName = "empty.pdf")
		self.assertTrue(os.path.exists(pBPDF.getFilePath("abc.fed", "arxiv")))
		os.remove(emptyPdfName)
		self.assertFalse(os.path.exists(emptyPdfName))
		pBPDF.copyToDir(pBPDF.pdfDir, "abc.fed", "arxiv")
		self.assertTrue(os.path.exists(os.path.join(pBPDF.pdfDir, "12345678.pdf")))
		self.assertTrue(pBPDF.removeFile("abc.fed", "arxiv"))
		self.assertFalse(pBPDF.removeFile("abc.fed", "arxiv"))
		os.remove(os.path.join(pBPDF.pdfDir, "12345678.pdf"))
		shutil.rmtree(pBPDF.getFileDir("abc.fed"))

	@unittest.skipIf(skipOnlineTests, "Long tests")
	def test_download(self):
		"""Test downloadArxiv"""
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
		"""Test finding spare folders"""
		pBDB.bibs.getAll = MagicMock(return_value=[{"bibkey":"abc"}, {"bibkey":"def"}])
		pBPDF.pdfDir = os.path.join(pbConfig.path, "tmppdf_%s"%today_ymd)
		for q in ["abc", "def", "ghi"]:
			pBPDF.createFolder(q)
			self.assertTrue(os.path.exists(pBPDF.getFileDir(q)))
		pBPDF.removeSparePDFFolders()
		for q in ["abc", "def"]:
			self.assertTrue(os.path.exists(pBPDF.getFileDir(q)))
		self.assertFalse(os.path.exists(pBPDF.getFileDir("ghi")))
		shutil.rmtree(pBPDF.pdfDir)

@unittest.skipIf(skipLongTests, "Long tests")
class TestExportMethods(unittest.TestCase):
	def test_backup(self):
		emptyFileName = os.path.join(pbConfig.path, "tests_%s.bib"%today_ymd)
		if os.path.exists(emptyFileName): os.remove(emptyFileName)
		if os.path.exists(emptyFileName + pBExport.backupExtension): os.remove(emptyFileName + pBExport.backupExtension)
		self.assertFalse(pBExport.backupCopy(emptyFileName))
		self.assertFalse(os.path.exists(emptyFileName))
		self.assertFalse(os.path.exists(emptyFileName + pBExport.backupExtension))
		open(emptyFileName, 'a').close()
		self.assertTrue(pBExport.backupCopy(emptyFileName))
		self.assertTrue(os.path.exists(emptyFileName + pBExport.backupExtension))
		os.remove(emptyFileName)
		self.assertFalse(os.path.exists(emptyFileName))
		self.assertTrue(pBExport.restoreBackupCopy(emptyFileName))
		self.assertTrue(os.path.exists(emptyFileName))
		os.chmod(emptyFileName, S_IREAD)
		self.assertFalse(pBExport.restoreBackupCopy(emptyFileName))
		os.remove(emptyFileName)
		self.assertTrue(pBExport.rmBackupCopy(emptyFileName))
		self.assertFalse(os.path.exists(emptyFileName + pBExport.backupExtension))

	def test_offlineExports(self):
		testBibName = os.path.join(pbConfig.path, "tests_%s.bib"%today_ymd)
		sampleList = [{"bibtex": '@Article{empty,\nauthor="me",\ntitle="no"\n}'}, {"bibtex": '@Article{empty2,\nauthor="me2",\ntitle="yes"\n}'}]
		sampleTxt = '@Article{empty,\nauthor="me",\ntitle="no"\n}\n@Article{empty2,\nauthor="me2",\ntitle="yes"\n}\n'
		pBDB.bibs.lastFetched = sampleList
		pBExport.exportLast(testBibName)
		self.assertEqual(open(testBibName).read(), sampleTxt)
		os.remove(testBibName)

		pBDB.bibs.getAll = MagicMock(return_value = sampleList)
		pBExport.exportAll(testBibName)
		self.assertEqual(open(testBibName).read(), sampleTxt)
		os.remove(testBibName)

		sampleList = [{"bibtex": '@Article{empty2,\nauthor="me2",\ntitle="{yes}",\n}'}]
		sampleTxt = '@Article{empty2,\nauthor="me2",\ntitle="{yes}",\n}\n'
		pBExport.exportSelected(testBibName, sampleList)
		self.assertEqual(open(testBibName).read(), sampleTxt)

		pBDB.bibs.getByBibkey = MagicMock(return_value = [{"bibtexDict": {"ID": "empty2", "ENTRYTYPE": "Article", "author": "me et al", "title": "yes"}}])
		pBExport.updateExportedBib(testBibName, overwrite = True)
		self.assertEqual(open(testBibName).read().replace(" ","").replace("\n",""),
			 sampleTxt.replace("me2", 'me et al').replace(" ","").replace("\n",""))
		pBExport.rmBackupCopy(testBibName)
		os.remove(testBibName)

	def test_exportForTexFile(self):
		testBibName = os.path.join(pbConfig.path, "tests_%s.bib"%today_ymd)
		self.assertFalse(os.path.exists(testBibName))
		testTexName = os.path.join(pbConfig.path, "tests_%s.tex"%today_ymd)
		texString = "\cite{empty}\citep{empty2}\citet{Gariazzo:2015rra}, \citet{Gariazzo:2017rra}\n"
		open(testTexName, "w").write(texString)
		self.assertEqual(open(testTexName).read(), texString)
		sampleList = [{"bibkey": "empty", "bibtex": '@Article{empty,\nauthor="me",\ntitle="no"\n}'}, {"bibkey": "empty2", "bibtex": '@Article{empty2,\nauthor="me2",\ntitle="yes"\n}'}]
		pBDB.catBib.insert = MagicMock(return_value = True)
		pBDB.bibs.getAll = MagicMock(return_value = sampleList)
		pBDB.bibs.getByBibkey = MagicMock(side_effect = [
			[{"bibkey": "empty", "bibtex": '@Article{empty,\nauthor="me",\ntitle="no"\n}'}],
			[{"bibkey": "empty2", "bibtex": '@Article{empty2,\nauthor="me2",\ntitle="yes"\n}'}],
			[{"bibkey": "Gariazzo:2015rra", "bibtex": '@article{Gariazzo:2015rra,\nauthor= "Gariazzo, S. and others",\ntitle="{Light sterile neutrinos}",\n}'}],
			[{"bibkey": "Gariazzo:2015rra", "bibtex": '@article{Gariazzo:2015rra,\nauthor= "Gariazzo, S. and others",\ntitle="{Light sterile neutrinos}",\n}'}],
			[]])
		pBDB.bibs.loadAndInsert = MagicMock(side_effect = ['@article{Gariazzo:2015rra,\nauthor= "Gariazzo, S. and others",\ntitle="{Light sterile neutrinos}",\n}', ''])
		pBExport.exportForTexFile(testTexName, testBibName, overwrite = True, autosave = False)
		self.assertTrue(os.path.exists(testBibName))
		self.assertEqual(open(testBibName).read(), '%file written by PhysBiblio\n@Article{empty,\nauthor="me",\ntitle="no"\n}\n@Article{empty2,\nauthor="me2",\ntitle="yes"\n}\n@article{Gariazzo:2015rra,\nauthor= "Gariazzo, S. and others",\ntitle="{Light sterile neutrinos}",\n}\n')
		os.remove(testBibName)
		os.remove(testTexName)

@unittest.skipIf(skipLongTests, "Long tests")
class TestViewMethods(unittest.TestCase):
	def test_printLink(self):
		pBDB.bibs.getField = MagicMock(side_effect = [
			'1507.08204', '', '', '1507.08204', #test "arxiv"
			'', '10.1088/0954-3899/43/3/033001', '', '10.1088/0954-3899/43/3/033001', #test "doi"
			'', '', '1385583', #test "inspire", inspire ID present
			'1507.08204', '', '', #test "inspire", inspire ID not present, arxiv present
			'', '', False, #test "inspire", inspire ID not present, arxiv not present
			'', '', '', #test "arxiv", no info
			'', '', '', #test "doi", no info
			])
		self.assertEqual(pBView.printLink("a", "arxiv"), "http://arxiv.org/abs/1507.08204")
		self.assertEqual(pBView.printLink("a", "doi"), "http://dx.doi.org/10.1088/0954-3899/43/3/033001")
		self.assertEqual(pBView.printLink("a", "inspire"), "http://inspirehep.net/record/1385583")
		self.assertEqual(pBView.printLink("a", "inspire"), "http://inspirehep.net/search?p=find+1507.08204")
		self.assertEqual(pBView.printLink("a", "inspire"), "http://inspirehep.net/search?p=find+a")
		self.assertFalse(pBView.printLink("a", "arxiv"))
		self.assertFalse(pBView.printLink("a", "doi"))

class TestBuilding(unittest.TestCase):
	def test_new(self):
		pass

if __name__=='__main__':
	pbConfig.params["logFileName"] = "test_packages.log"
	logFileName = os.path.join(pbConfig.path, pbConfig.params["logFileName"])
	os.remove(logFileName) if os.path.exists(logFileName) else None
	try:
		test_pBErrorManager()
	except:
		print("#"*40 + "\nException encountered during execution!\n" + "#"*40)
		print(traceback.format_exc())
	else:
		print("\nStarting tests...\n")
		try:
			unittest.main()
		except:#just to be able to exec operations after unittest.main()
			os.remove(logFileName)
			os.remove(tempDBName)
			print("#"*29 + "\nAll the tests were completed!\nSee above for the output.\n" + "#"*29)
