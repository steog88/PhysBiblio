#!/usr/bin/env python
"""
Test file for the physbiblio.webimport subpackage.

This file is part of the physbiblio package.
"""
import sys, datetime, traceback, os

if sys.version_info[0] < 3:
	import unittest2 as unittest
else:
	import unittest

try:
	from physbiblio.setuptests import *
	from physbiblio.webimport.webInterf import physBiblioWeb
	from physbiblio.webimport.inspireoai import get_journal_ref_xml
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
      abstract = "{The theory and phenomenology of light sterile neutrinos at the eV mass scale is reviewed. The reactor, Gallium and LSND anomalies are briefly described and interpreted as indications of the existence of short-baseline oscillations which require the existence of light sterile neutrinos. The global fits of short-baseline oscillation data in 3+1 and 3+2 schemes are discussed, together with the implications for beta-decay and neutrinoless double-beta decay. The cosmological effects of light sterile neutrinos are briefly reviewed and the implications of existing cosmological data are discussed. The review concludes with a summary of future perspectives.}",
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
			"inspireoai": ["1385583",
				{'doi': '10.1088/0954-3899/43/3/033001', 'arxiv': '1507.08204', 'bibkey': 'Gariazzo:2015rra', 'ads': '2015JPhG...43c3001G', 'journal': 'J.Phys.', 'volume': 'G43', 'year': '2016', 'pages': '033001', 'firstdate': '2015-07-29', 'pubdate': '2016-01-13', 'author': 'Gariazzo, S. and Giunti, C. and Laveder, M. and Li, Y.F. and Zavanin, E.M.', 'collaboration': None, 'primaryclass': 'hep-ph', 'archiveprefix': 'arXiv', 'eprint': '1507.08204', 'title': 'Light sterile neutrinos', 'isbn': None, 'ENTRYTYPE': 'article', 'oldkeys': '', 'bibtex': '@Article{Gariazzo:2015rra,\n        author = "Gariazzo, S. and Giunti, C. and Laveder, M. and Li, Y.F. and Zavanin, E.M.",\n         title = "{Light sterile neutrinos}",\n       journal = "J.Phys.",\n        volume = "G43",\n          year = "2016",\n         pages = "033001",\n archiveprefix = "arXiv",\n  primaryclass = "hep-ph",\n        eprint = "1507.08204",\n           doi = "10.1088/0954-3899/43/3/033001",\n}\n\n', 'id': '1385583', 'link': 'http://dx.doi.org/10.1088/0954-3899/43/3/033001', 'reportnumber': None}],
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
			elif method == "arxiv":
				self.assertEqual(physBiblioWeb.webSearch[method].retrieveUrlFirst(strings[0], searchType = "id").strip(), strings[1].strip())
				self.assertEqual(physBiblioWeb.webSearch[method].retrieveUrlAll(strings[0], searchType = "id").strip(), strings[1].strip())
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
		self.assertEqual(physBiblioWeb.webSearch["inspireoai"].retrieveOAIData("1110620"),
			{'doi': None, 'arxiv': None, 'bibkey': None, 'ads': None, 'journal': None, 'volume': None, 'year': None, 'pages': None, 'firstdate': None, 'pubdate': None, 'author': ' and Tauber, Jan', 'collaboration': 'Planck', 'title': 'Anisotropies of the Cosmic Background Radiation Field', 'isbn': None, 'ENTRYTYPE': 'article', 'oldkeys': '', 'bibtex': '@Article{,\n        author = " and Tauber, Jan",\n collaboration = "Planck",\n         title = "{Anisotropies of the Cosmic Background Radiation Field}",\n}\n\n', 'id': '1110620', 'archiveprefix': None, 'eprint': None, 'link': None, 'primaryclass': None, 'reportnumber': None,})
		self.assertFalse(physBiblioWeb.webSearch["inspireoai"].retrieveOAIData("9999999"))
		for method, strings in tests.items():
			print(method)
			res=physBiblioWeb.webSearch[method].retrieveUrlFirst(strings[0])
			print(res)
			self.assertEqual(res.strip(), strings[1].strip())
			self.assertEqual(physBiblioWeb.webSearch[method].retrieveUrlAll(strings[0]).strip(), strings[1].strip())
		self.assertEqual(physBiblioWeb.webSearch["inspire"].retrieveInspireID(tests["inspire"][0]), "")

	def test_inspireoai_other(self):
		"""test auxiliary functions in inspireoai module"""
		marcxmlRecord1 = physBiblioWeb.webSearch["inspireoai"].oai.getRecord(metadataPrefix = 'marcxml', identifier = "oai:inspirehep.net:1385583")[1]
		marcxmlRecord2 = physBiblioWeb.webSearch["inspireoai"].oai.getRecord(metadataPrefix = 'marcxml', identifier = "oai:inspirehep.net:1414175")[1]
		self.assertEqual(get_journal_ref_xml(marcxmlRecord1),
			(['J.Phys.'], ['G43'], ['2016'], ['033001'], [None], [None], [None], [None]))
		self.assertEqual(get_journal_ref_xml(marcxmlRecord2),
			([None], [None], ['2017'], ['469-475'], [None], [None], [None], ['C15-08-20']))
		dict1a = physBiblioWeb.webSearch["inspireoai"].readRecord(marcxmlRecord1)
		dict1b = physBiblioWeb.webSearch["inspireoai"].readRecord(marcxmlRecord1, readConferenceTitle = True)
		self.assertEqual(dict1a, dict1b)
		self.assertEqual(dict1a,
			{'doi': '10.1088/0954-3899/43/3/033001', 'arxiv': '1507.08204', 'bibkey': 'Gariazzo:2015rra', 'ads': '2015JPhG...43c3001G', 'journal': 'J.Phys.', 'volume': 'G43', 'year': '2016', 'pages': '033001', 'firstdate': '2015-07-29', 'pubdate': '2016-01-13', 'author': 'Gariazzo, S. and Giunti, C. and Laveder, M. and Li, Y.F. and Zavanin, E.M.', 'collaboration': None, 'primaryclass': 'hep-ph', 'archiveprefix': 'arXiv', 'eprint': '1507.08204', 'reportnumber': None, 'title': 'Light sterile neutrinos', 'isbn': None, 'ENTRYTYPE': 'article', 'oldkeys': '', 'link': 'http://dx.doi.org/10.1088/0954-3899/43/3/033001', 'bibtex': '@Article{Gariazzo:2015rra,\n        author = "Gariazzo, S. and Giunti, C. and Laveder, M. and Li, Y.F. and Zavanin, E.M.",\n         title = "{Light sterile neutrinos}",\n       journal = "J.Phys.",\n        volume = "G43",\n          year = "2016",\n         pages = "033001",\n archiveprefix = "arXiv",\n  primaryclass = "hep-ph",\n        eprint = "1507.08204",\n           doi = "10.1088/0954-3899/43/3/033001",\n}\n\n'})
		dict2 = physBiblioWeb.webSearch["inspireoai"].readRecord(marcxmlRecord2, readConferenceTitle = True)
		self.assertEqual(dict2, {'doi': '10.1142/9789813224568_0076', 'arxiv': '1601.01475', 'bibkey': 'Gariazzo:2016ehl', 'ads': None, 'journal': None, 'volume': None, 'year': '2017', 'pages': '469-475', 'firstdate': '2016-01-07', 'pubdate': '2017', 'author': 'Gariazzo, Stefano', 'collaboration': None, 'primaryclass': 'astro-ph.CO', 'archiveprefix': 'arXiv', 'eprint': '1601.01475', 'reportnumber': None, 'title': 'Light Sterile Neutrinos In Cosmology', 'isbn': None, 'booktitle': 'Proceedings, 17th Lomonosov Conference on Elementary Particle Physics: Moscow, Russia, August 20-26, 2015', 'ENTRYTYPE': 'inproceedings', 'oldkeys': '', 'link': 'http://dx.doi.org/10.1142/9789813224568_0076', 'bibtex': '@Inproceedings{Gariazzo:2016ehl,\n        author = "Gariazzo, Stefano",\n         title = "{Light Sterile Neutrinos In Cosmology}",\n     booktitle = "{Proceedings, 17th Lomonosov Conference on Elementary Particle Physics: Moscow, Russia, August 20-26, 2015}",\n          year = "2017",\n         pages = "469-475",\n archiveprefix = "arXiv",\n  primaryclass = "astro-ph.CO",\n        eprint = "1601.01475",\n           doi = "10.1142/9789813224568_0076",\n}\n\n'})
		dict1a["id"] = "1385583"
		dict2["id"] = "1414175"
		bibtex1 = '@article{abc,\nauthor="me",}'
		bibtex2 = '@article{abc,'
		self.assertEqual(physBiblioWeb.webSearch["inspireoai"].updateBibtex(dict2, bibtex1), bibtex1)
		self.assertEqual(physBiblioWeb.webSearch["inspireoai"].updateBibtex(dict1a, bibtex2), bibtex2)
		self.assertEqual(physBiblioWeb.webSearch["inspireoai"].updateBibtex(dict1a, bibtex1),
			'@Article{abc,\n        author = "me",\n       journal = "J.Phys.",\n        volume = "G43",\n          year = "2016",\n         pages = "033001",\n           doi = "10.1088/0954-3899/43/3/033001",\n}\n\n')

	@unittest.skipIf(skipOAITests, "Online tests with OAI")
	def test_inspireoai(self):
		"""test retrieve daily data from inspireOAI"""
		date1 = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
		date2 = datetime.date.today().strftime("%Y-%m-%d")
		yren, monen, dayen = date1.split('-')
		yrst, monst, dayst = date2.split('-')
		date1 = datetime.datetime(int(yren), int(monen), int(dayen))
		date2 = datetime.datetime(int(yrst), int(monst), int(dayst))
		result = physBiblioWeb.webSearch["inspireoai"].retrieveOAIUpdates(date1, date2)
		self.assertEqual(type(result), list)
		print(len(result), result[0])

if __name__=='__main__':
	unittest.main()
