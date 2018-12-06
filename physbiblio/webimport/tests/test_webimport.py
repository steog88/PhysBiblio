#!/usr/bin/env python
"""Test file for the physbiblio.webimport subpackage.

This file is part of the physbiblio package.
"""
import sys
import datetime
import traceback
import os

if sys.version_info[0] < 3:
	import unittest2 as unittest
else:
	import unittest

try:
	from physbiblio.setuptests import *
	from physbiblio.webimport.webInterf import physBiblioWeb
	from physbiblio.webimport.inspireoai import get_journal_ref_xml
	from physbiblio.config import pbConfig
except ImportError:
	print("Could not find physbiblio and its modules!")
	raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipTestsSettings.online, "Online tests")
class TestWebImportMethods(unittest.TestCase):
	"""Test the functions that import entries from the web.
	Should not fail if everything works fine.
	"""

	def test_methods_success(self):
		"""Test webimport with known results"""
		print(physBiblioWeb.webSearch.keys())
		tests = {
			"arxiv": ["1507.08204",
				u'@Article{1507.08204,\n         title = ' \
				+ '"{Light sterile neutrinos}",\n          year = "2015",' \
				+ '\n archiveprefix = "arXiv",\n  primaryclass = ' \
				+ '"hep-ph",\n           doi = ' \
				+ '"10.1088/0954-3899/43/3/033001",\n      abstract = ' \
				+ '"{The theory and phenomenology of light sterile neutrinos' \
				+ ' at the eV mass scale is reviewed. The reactor, Gallium ' \
				+ 'and LSND anomalies are briefly described and interpreted ' \
				+ 'as indications of the existence of short-baseline ' \
				+ 'oscillations which require the existence of light sterile' \
				+ ' neutrinos. The global fits of short-baseline oscillation' \
				+ ' data in 3+1 and 3+2 schemes are discussed, together ' \
				+ 'with the implications for beta-decay and neutrinoless ' \
				+ 'double-beta decay. The cosmological effects of light ' \
				+ 'sterile neutrinos are briefly reviewed and the ' \
				+ 'implications of existing cosmological data are discussed.' \
				+ ' The review concludes with a summary of future ' \
				+ 'perspectives.}",\n         arxiv = "1507.08204",\n    ' \
				+ '   authors = "S. Gariazzo and C. Giunti and M. Laveder ' \
				+ 'and Y. F. Li and E. M. Zavanin",\n}'],
			"doi": ["10.1088/0954-3899/43/3/033001", '''@article{Gariazzo_2015,
	doi = {10.1088/0954-3899/43/3/033001},
	url = {''' + pbConfig.doiUrl + '''10.1088%2F0954-3899%2F43%2F3%2F033001},
	year = 2015,
	month = {mar},
	publisher = {{IOP} Publishing},
	volume = {43},
	number = {3},
	pages = {033001},
	author = {S Gariazzo and C Giunti and M Laveder and Y F Li and E M Zavanin},
	title = {Light sterile neutrinos},
	journal = {Journal of Physics G: Nuclear and Particle Physics}
}'''],
			"inspire": ["Gariazzo:2015rra", '''@article{Gariazzo:2015rra,
      author         = "Gariazzo, S. and Giunti, C. ''' \
+ '''and Laveder, M. and Li, Y. F.
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
}'''],
			"inspireoai": ["1385583",
				{'doi': '10.1088/0954-3899/43/3/033001',
				'arxiv': '1507.08204', 'bibkey': 'Gariazzo:2015rra',
				'ads': '2015JPhG...43c3001G', 'journal': 'J.Phys.',
				'volume': 'G43', 'year': '2016', 'pages': '033001',
				'firstdate': '2015-07-29', 'pubdate': '2016-01-13',
				'author': 'Gariazzo, S. and Giunti, C. and Laveder, M. ' \
				+ 'and Li, Y.F. and Zavanin, E.M.', 'collaboration': None,
				'primaryclass': 'hep-ph', 'archiveprefix': 'arXiv',
				'eprint': '1507.08204', 'title': 'Light sterile neutrinos',
				'isbn': None, 'ENTRYTYPE': 'article', 'oldkeys': '',
				'bibtex': '@Article{Gariazzo:2015rra,\n        ' \
				+ 'author = "Gariazzo, S. and Giunti, C. and ' \
				+ 'Laveder, M. and Li, Y.F. and Zavanin, E.M.",\n  ' \
				+ '       title = "{Light sterile neutrinos}",\n   ' \
				+ '    journal = "J.Phys.",\n        volume = "G43",\n ' \
				+ '         year = "2016",\n         pages = "033001",\n ' \
				+ 'archiveprefix = "arXiv",\n  primaryclass = "hep-ph",\n ' \
				+ '       eprint = "1507.08204",\n           doi = ' \
				+ '"10.1088/0954-3899/43/3/033001",\n}\n\n',
				'id': '1385583',
				'link': '%s10.1088/0954-3899/43/3/033001'%pbConfig.doiUrl,
				'reportnumber': None}],
			"isbn": ["9780191523229", '''@book{9780191523229,
  Author = {Carlo Giunti, Chung W. Kim},
  Title = {Fundamentals of Neutrino Physics and Astrophysics},
  Publisher = {OUP Oxford},
  Year = {2007},
  Date = {2007-03-15},
  PageTotal = {},
  EAN = {9780191523229},
  URL = {https://www.ebook.de/de/product/21360145/carlo_giunti_''' \
+ '''chung_w_kim_fundamentals_of_neutrino_physics_and_astrophysics.html}
}'''],
			}
		for method, strings in tests.items():
			print(method)
			if method == "inspireoai":
				self.assertEqual(
					physBiblioWeb.webSearch[method].retrieveOAIData(
					strings[0]), strings[1])
			elif method == "arxiv":
				self.assertEqual(
					physBiblioWeb.webSearch[method].retrieveUrlFirst(
						strings[0], searchType = "id").strip(),
					strings[1].strip())
				self.assertEqual(
					physBiblioWeb.webSearch[method].retrieveUrlAll(
						strings[0], searchType = "id").strip(),
					strings[1].strip())
			else:
				self.assertEqual(
					physBiblioWeb.webSearch[method].retrieveUrlFirst(
						strings[0]).strip(),
					strings[1].strip())
				self.assertEqual(
					physBiblioWeb.webSearch[method].retrieveUrlAll(
						strings[0]).strip(),
					strings[1].strip())
		self.assertEqual(
			physBiblioWeb.webSearch["inspire"].retrieveInspireID(
				tests["inspire"][0]), u'1385583')

	def test_methods_insuccess(self):
		"""Test webimport using missing and/or invalid identifiers"""
		print(physBiblioWeb.webSearch.keys())
		tests = {
			"arxiv": ["1801.15000", ""],
			"doi": ["10.1088/9999-3899/43/a/033001", ""],
			"inspire": ["Gariazzo:2014rra", ""],
			"isbn": ["978019850871a", ""],
			}
		self.assertEqual(
			physBiblioWeb.webSearch["inspireoai"].retrieveOAIData("1110620"),
			{'doi': None, 'arxiv': None, 'bibkey': None, 'ads': None,
			'journal': None, 'volume': None, 'year': None, 'pages': None,
			'firstdate': None, 'pubdate': None, 'author': ' and Tauber, Jan',
			'collaboration': 'Planck',
			'title': 'Anisotropies of the Cosmic Background Radiation Field',
			'isbn': None, 'ENTRYTYPE': 'article', 'oldkeys': '',
			'bibtex': '@Article{,\n        author = " and Tauber, Jan",' \
			+ '\n collaboration = "Planck",\n         title = "' \
			+ '{Anisotropies of the Cosmic Background Radiation Field}",\n}' \
			+ '\n\n',
			'id': '1110620', 'archiveprefix': None, 'eprint': None,
			'link': None, 'primaryclass': None, 'reportnumber': None,})
		self.assertFalse(
			physBiblioWeb.webSearch["inspireoai"].retrieveOAIData("9999999"))
		for method, strings in tests.items():
			print(method)
			res=physBiblioWeb.webSearch[method].retrieveUrlFirst(strings[0])
			print(res)
			self.assertEqual(res.strip(), strings[1].strip())
			self.assertEqual(
				physBiblioWeb.webSearch[method].retrieveUrlAll(
				strings[0]).strip(), strings[1].strip())
		self.assertEqual(
			physBiblioWeb.webSearch["inspire"].retrieveInspireID(
			tests["inspire"][0]), "")

	def test_inspireoai_other(self):
		"""test auxiliary functions in inspireoai module"""
		self.maxDiff = None
		marcxmlRecord1 = physBiblioWeb.webSearch["inspireoai"].oai.getRecord(
			metadataPrefix = 'marcxml',
			identifier = "oai:inspirehep.net:1385583")[1]
		marcxmlRecord2 = physBiblioWeb.webSearch["inspireoai"].oai.getRecord(
			metadataPrefix = 'marcxml',
			identifier = "oai:inspirehep.net:1414175")[1]
		self.assertEqual(get_journal_ref_xml(marcxmlRecord1),
			(['J.Phys.'], ['G43'], ['2016'], ['033001'],
			[None], [None], [None], [None]))
		self.assertEqual(get_journal_ref_xml(marcxmlRecord2),
			([None], [None], ['2017'], ['469-475'], [None],
			[None], [None], ['C15-08-20']))
		dict1a = physBiblioWeb.webSearch["inspireoai"].readRecord(
			marcxmlRecord1)
		dict1b = physBiblioWeb.webSearch["inspireoai"].readRecord(
			marcxmlRecord1, readConferenceTitle = True)
		self.assertEqual(dict1a, dict1b)
		self.assertEqual(dict1a,
			{'doi': '10.1088/0954-3899/43/3/033001',
			'arxiv': '1507.08204', 'bibkey': 'Gariazzo:2015rra',
			'ads': '2015JPhG...43c3001G', 'journal': 'J.Phys.',
			'volume': 'G43', 'year': '2016', 'pages': '033001',
			'firstdate': '2015-07-29', 'pubdate': '2016-01-13',
			'author': 'Gariazzo, S. and Giunti, C. and Laveder, M. and ' \
			+ 'Li, Y.F. and Zavanin, E.M.',
			'collaboration': None, 'primaryclass': 'hep-ph',
			'archiveprefix': 'arXiv', 'eprint': '1507.08204',
			'reportnumber': None, 'title': 'Light sterile neutrinos',
			'isbn': None, 'ENTRYTYPE': 'article', 'oldkeys': '',
			'link': '%s10.1088/0954-3899/43/3/033001'%pbConfig.doiUrl,
			'bibtex': '@Article{Gariazzo:2015rra,\n        ' \
			+ 'author = "Gariazzo, S. and Giunti, C. and Laveder, M. ' \
			+ 'and Li, Y.F. and Zavanin, E.M.",\n         title = "' \
			+ '{Light sterile neutrinos}",\n       journal = ' \
			+ '"J.Phys.",\n        volume = "G43",\n          year = ' \
			+ '"2016",\n         pages = "033001",\n archiveprefix = ' \
			+ '"arXiv",\n  primaryclass = "hep-ph",\n        eprint = ' \
			+ '"1507.08204",\n           doi = ' \
			+ '"10.1088/0954-3899/43/3/033001",\n}\n\n'})
		dict2 = physBiblioWeb.webSearch["inspireoai"].readRecord(
			marcxmlRecord2, readConferenceTitle = True)
		self.assertEqual(dict2,
			{'doi': '10.1142/9789813224568_0076', 'arxiv': '1601.01475',
			'bibkey': 'Gariazzo:2016ehl', 'ads': None, 'journal': None,
			'volume': None, 'year': '2017', 'pages': '469-475',
			'firstdate': '2016-01-07', 'pubdate': '2017',
			'author': 'Gariazzo, Stefano', 'collaboration': None,
			'primaryclass': 'astro-ph.CO', 'archiveprefix': 'arXiv',
			'eprint': '1601.01475', 'reportnumber': None,
			'title': 'Light Sterile Neutrinos In Cosmology',
			'isbn': None, 'booktitle': 'Proceedings, 17th Lomonosov ' \
			+ 'Conference on Elementary Particle Physics: Moscow, ' \
			+ 'Russia, August 20-26, 2015', 'ENTRYTYPE': 'inproceedings',
			'oldkeys': '',
			'link': '%s10.1142/9789813224568_0076'%pbConfig.doiUrl,
			'bibtex': '@Inproceedings{Gariazzo:2016ehl,\n        ' \
			+ 'author = "Gariazzo, Stefano",\n         ' \
			+ 'title = "{Light Sterile Neutrinos In Cosmology}",' \
			+ '\n     booktitle = "{Proceedings, 17th Lomonosov ' \
			+ 'Conference on Elementary Particle Physics: Moscow, ' \
			+ 'Russia, August 20-26, 2015}",\n          year = ' \
			+ '"2017",\n         pages = "469-475",\n archiveprefix = ' \
			+ '"arXiv",\n  primaryclass = "astro-ph.CO",\n        ' \
			+ 'eprint = "1601.01475",\n           doi = ' \
			+ '"10.1142/9789813224568_0076",\n}\n\n'})
		dict1a["id"] = "1385583"
		dict2["id"] = "1414175"
		bibtex1 = '@article{abc,\nauthor="me",}'
		bibtex2 = '@article{abc,'
		self.assertEqual(physBiblioWeb.webSearch["inspireoai"].updateBibtex(
			dict2, bibtex1), (False, bibtex1))
		self.assertEqual(physBiblioWeb.webSearch["inspireoai"].updateBibtex(
			dict1a, bibtex2), (False, bibtex2))
		self.assertEqual(physBiblioWeb.webSearch["inspireoai"].updateBibtex(
			dict1a, bibtex1),
			(True, '@Article{abc,\n        author = "me",\n       ' \
			+ 'journal = "J.Phys.",\n        volume = "G43",\n          ' \
			+ 'year = "2016",\n         pages = "033001",\n           ' \
			+ 'doi = "10.1088/0954-3899/43/3/033001",\n}\n\n'))

	@unittest.skipIf(skipTestsSettings.oai, "Online tests with OAI")
	def test_inspireoai(self):
		"""test retrieve daily data from inspireOAI"""
		date1 = (datetime.date.today() - datetime.timedelta(1)
			).strftime("%Y-%m-%d")
		date2 = datetime.date.today().strftime("%Y-%m-%d")
		yren, monen, dayen = date1.split('-')
		yrst, monst, dayst = date2.split('-')
		date1 = datetime.datetime(int(yren), int(monen), int(dayen))
		date2 = datetime.datetime(int(yrst), int(monst), int(dayst))
		result = physBiblioWeb.webSearch["inspireoai"].retrieveOAIUpdates(
			date1, date2)
		self.assertEqual(type(result), list)
		print(len(result), result[0])


class TestWebImportOffline(unittest.TestCase):
	"""Offline test for some functions of the webImport package."""

	def test_arxivYear(self):
		"""test the arxivDaily method in the arxiv module"""
		self.assertEqual(physBiblioWeb.webSearch["arxiv"].getYear("abc"), None)
		self.assertEqual(physBiblioWeb.webSearch["arxiv"].getYear("0123.345"),
			None)
		self.assertEqual(physBiblioWeb.webSearch["arxiv"].getYear(
			"hep-ph/9900000"), "1999")
		self.assertEqual(physBiblioWeb.webSearch["arxiv"].getYear(
			"hep-ph/990000"), None)
		self.assertEqual(physBiblioWeb.webSearch["arxiv"].getYear("1234.5678"),
			"2012")
		self.assertEqual(physBiblioWeb.webSearch["arxiv"].getYear(
			"1678.56789"), "2016")

	def test_arxivDaily(self):
		"""test the arxivDaily method in the arxiv module"""
		self.assertFalse(physBiblioWeb.webSearch["arxiv"].arxivDaily(
			"missing"))
		self.assertFalse(physBiblioWeb.webSearch["arxiv"].arxivDaily(
			"physics.missing"))
		content_example='''<?xml version="1.0" encoding="UTF-8"?>

<rdf:RDF
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns="http://purl.org/rss/1.0/"
 xmlns:content="http://purl.org/rss/1.0/modules/content/"
 xmlns:taxo="http://purl.org/rss/1.0/modules/taxonomy/"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:syn="http://purl.org/rss/1.0/modules/syndication/"
 xmlns:admin="http://webns.net/mvcb/"
>

<channel rdf:about="http://arxiv.org/">
<title>hep-ex updates on arXiv.org</title>
<link>http://arxiv.org/</link>
<description rdf:parseType="Literal">High Energy Physics - ''' \
+ '''Experiment (hep-ex) updates on the arXiv.org e-print archive</description>
<dc:language>en-us</dc:language>
<dc:date>2018-05-23T20:30:00-05:00</dc:date>
<dc:publisher>www-admin@arxiv.org</dc:publisher>
<dc:subject>High Energy Physics - Experiment</dc:subject>
<syn:updateBase>1901-01-01T00:00+00:00</syn:updateBase>
<syn:updateFrequency>1</syn:updateFrequency>
<syn:updatePeriod>daily</syn:updatePeriod>
<items>
 <rdf:Seq>
  <rdf:li rdf:resource="http://arxiv.org/abs/1805.08875" />
  <rdf:li rdf:resource="http://arxiv.org/abs/1805.09166" />
  <rdf:li rdf:resource="http://arxiv.org/abs/1805.06430" />
 </rdf:Seq>
</items>
<image rdf:resource="http://arxiv.org/icons/sfx.gif" />
</channel>
<image rdf:about="http://arxiv.org/icons/sfx.gif">
<title>arXiv.org</title>
<url>http://arxiv.org/icons/sfx.gif</url>
<link>http://arxiv.org/</link>
</image>
<item rdf:about="http://arxiv.org/abs/1805.08875">
<title>Measurement of Transverse Single Spin Asymmetries. ''' \
+ '''(arXiv:1805.08875v1 [hep-ex])</title>
<link>http://arxiv.org/abs/1805.08875</link>
<description rdf:parseType="Literal">&lt;p&gt;In 2015 the first ''' \
+ '''collisions between polarized protons and nuclei occurred at
the Relativistic Heavy Ion Collider (RHIC), at a center-of-mass energy of
$\sqrt{s_{NN}}=200$ GeV. Comparisons between spin asymmetries and
cross-sections in $p+p$ production to those in $p+A$ production provide insight
into nuclear structure, namely nuclear modification factors, nuclear dependence
of spin asymmetries, and comparison to models with saturation effects. The
transverse single-spin asymmetry, $A_{N}$, has been measured in $\pi^{0}$
production in the STAR Forward Meson Spectrometer (FMS), an electromagnetic
calorimeter covering a forward psuedorapidity range ''' \
+ '''of $2.6&amp;lt;\eta&amp;lt;4$. Within
this kinematic range, STAR has previously reported the persistence of large
$\pi^0$ asymmetries with unexpected dependences on $p_T$ and event topology in
$p+p$ collisions. This talk will compare these dependences to those in $p+A$
production.
&lt;/p&gt;
</description>
<dc:creator> &lt;a href=&quot;http://arxiv.org/find/hep-ex/1/''' \
+ '''au:+Dilks_C/0/1/0/all/0/1&quot;&gt;Christopher Dilks&lt;/a&gt; ''' \
+ '''(STAR Collaboration)</dc:creator>
</item>
<item rdf:about="http://arxiv.org/abs/1805.09166">
<title>Recent Top quark results from the Tevatron. ''' \
+ '''(arXiv:1805.09166v1 [hep-ex] CROSS LISTED)</title>
<link>http://arxiv.org/abs/1805.09166</link>
<description rdf:parseType="Literal">&lt;p&gt;We present recent measurements
&lt;/p&gt;
</description>
<dc:creator> &lt;a href=&quot;http://arxiv.org/find/''' \
+ '''hep-ex/1/au:+Tuchming_B/0/1/0/all/0/1&quot;&gt;''' \
+ '''Boris Tuchming&lt;/a&gt;</dc:creator>
</item>
<item rdf:about="http://arxiv.org/abs/1805.06430">
<title>New Perspective on Hybrid Mesons. (arXiv:1805.06430v2 ''' \
+ '''[nucl-th] UPDATED)</title>
<link>http://arxiv.org/abs/1805.06430</link>
<description rdf:parseType="Literal">&lt;p&gt;It is thought that ''' \
+ '''strong interactions within the Standard Model can generate
bound-states in which non-Abelian gauge-bosons play a dual role, serving both
as force and matter fields.
&lt;/p&gt;
</description>
<dc:creator> &lt;a href=&quot;http://arxiv.org/find/''' \
+ '''nucl-th/1/au:+Xu_S/0/1/0/all/0/''' \
+ '''1&quot;&gt;Shu-Sheng Xu&lt;/a&gt;, &lt;a ''' \
+ '''href=&quot;http://arxiv.org/find/''' \
+ '''nucl-th/1/au:+Cui_Z/0/1/0/all/''' \
+ '''0/1&quot;&gt;Zhu-Fang Cui&lt;/a&gt;, &lt;a ''' \
+ '''href=&quot;http://arxiv.org/find/nucl-th/1/au:+''' \
+ '''Chang_L/0/1/0/all/0/1&quot;&gt;Lei Chang&lt;/''' \
+ '''a&gt;, &lt;a href=&quot;http://arxiv.org/find/nucl-th/1/au:+''' \
+ '''Papavassiliou_J/0/1/0/all/0/1&quot;&gt;Joannis ''' \
+ '''Papavassiliou&lt;/a&gt;, &lt;a href=&quot;http://arxiv.org/find/''' \
+ '''nucl-th/1/au:+Roberts_C/0/1/0/all/0/1&quot;''' \
+ '''&gt;Craig D. Roberts&lt;/a&gt;, &lt;a ''' \
+ '''href=&quot;http://arxiv.org/find/nucl-th/''' \
+ '''1/au:+Zong_H/0/1/0/all/0/1&quot;&gt;Hong-Shi Zong''' \
+ '''&lt;/a&gt;</dc:creator>
</item>
</rdf:RDF>'''
		with patch('physbiblio.webimport.webInterf.WebInterf.textFromUrl',
				return_value=content_example) as _fromUrl:
			result = physBiblioWeb.webSearch["arxiv"].arxivDaily("hep-ex")
			_fromUrl.assert_called_once_with(
				"https://export.arxiv.org/rss/hep-ex")
			pbConfig.params["maxAuthorNames"] = 3
			self.assertEqual(result[0],
				{'primaryclass': u'hep-ex', 'author': u'Christopher Dilks',
				'title': u'Measurement of Transverse Single ' \
				+ 'Spin Asymmetries.',
				'abstract': u'In 2015 the first collisions between ' \
				+ 'polarized protons and nuclei occurred at the ' \
				+ 'Relativistic Heavy Ion Collider (RHIC), at a ' \
				+ 'center-of-mass energy of $\\sqrt{s_{NN}}=200$ GeV. ' \
				+ 'Comparisons between spin asymmetries and cross-sections ' \
				+ 'in $p+p$ production to those in $p+A$ production ' \
				+ 'provide insight into nuclear structure, namely ' \
				+ 'nuclear modification factors, nuclear dependence ' \
				+ 'of spin asymmetries, and comparison to models ' \
				+ 'with saturation effects. The transverse single-spin ' \
				+ 'asymmetry, $A_{N}$, has been measured in $\\pi^{0}$ ' \
				+ 'production in the STAR Forward Meson Spectrometer ' \
				+ '(FMS), an electromagnetic calorimeter covering a ' \
				+ 'forward psuedorapidity range of $2.6&lt;\\eta&lt;4$. ' \
				+ 'Within this kinematic range, STAR has previously ' \
				+ 'reported the persistence of large $\\pi^0$ asymmetries ' \
				+ 'with unexpected dependences on $p_T$ and event topology ' \
				+ 'in $p+p$ collisions. This talk will compare ' \
				+ 'these dependences to those in $p+A$ production. ',
				'cross': False, 'version': u'1805.08875v1',
				'eprint': u'1805.08875',
				'authors': [u'Christopher Dilks'], 'replacement': False})
			self.assertEqual(result[1],
				{'primaryclass': u'hep-ex', 'author': u'Boris Tuchming',
				'title': u'Recent Top quark results from the Tevatron.',
				'abstract': u'We present recent measurements ',
				'cross': True, 'version': u'1805.09166v1',
				'eprint': u'1805.09166', 'authors': [u'Boris Tuchming'],
				'replacement': False})
			self.assertEqual(result[2],
				{'primaryclass': u'nucl-th',
				'author': u'Shu-Sheng Xu and Zhu-Fang Cui and ' \
				+ 'Lei Chang and others',
				'title': u'New Perspective on Hybrid Mesons.',
				'abstract': u'It is thought that strong interactions ' \
				+ 'within the Standard Model can generate bound-states ' \
				+ 'in which non-Abelian gauge-bosons play a dual role, ' \
				+ 'serving both as force and matter fields. ',
				'cross': True, 'version': u'1805.06430v2',
				'eprint': u'1805.06430',
				'authors': [u'Shu-Sheng Xu', u'Zhu-Fang Cui', u'Lei Chang',
					u'Joannis Papavassiliou', u'Craig D. Roberts',
					u'Hong-Shi Zong'],
				'replacement': True})


if __name__=='__main__':
	unittest.main()
