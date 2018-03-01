#!/usr/bin/env python
"""
Test file for the physbiblio.webimport subpackage.

This file is part of the PhysBiblio package.
"""
import sys, datetime, traceback, os

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import MagicMock, patch, call
else:
	import unittest
	from unittest.mock import MagicMock, patch, call

try:
	from physbiblio.setuptests import *
	from physbiblio.errors import pBErrorManager
	from physbiblio.config import pbConfig
	from physbiblio.database import pBDB
	from physbiblio.webimport.webInterf import physBiblioWeb
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

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
			print(res)
			self.assertEqual(res.strip(), strings[1].strip())
			self.assertEqual(physBiblioWeb.webSearch[method].retrieveUrlAll(strings[0]).strip(), strings[1].strip())
		self.assertEqual(physBiblioWeb.webSearch["inspire"].retrieveInspireID(tests["inspire"][0]), "")

	@unittest.skipIf(skipOAITests, "Online tests")
	def test_inspireoai(self):
		"""test retrieve daily data from inspireOAI"""
		date1 = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
		date2 = datetime.date.today().strftime("%Y-%m-%d")
		yren, monen, dayen = date1.split('-')
		yrst, monst, dayst = date2.split('-')
		date1 = datetime.datetime(int(yren), int(monen), int(dayen))
		date2 = datetime.datetime(int(yrst), int(monst), int(dayst))
		print(physBiblioWeb.webSearch["inspireoai"].retrieveOAIUpdates(date1, date2))

if __name__=='__main__':
	print("\nStarting tests...\n")
	unittest.main()
