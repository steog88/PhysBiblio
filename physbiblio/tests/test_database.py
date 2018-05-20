#!/usr/bin/env python
"""
Test file for the physbiblio.database module.

This file is part of the physbiblio package.
"""
import sys, traceback
import six
import datetime

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch, call
	from StringIO import StringIO
else:
	import unittest
	from unittest.mock import patch, call
	from io import StringIO

try:
	from physbiblio.setuptests import *
	from physbiblio.errors import pBLogger
	from physbiblio.export import pBExport
	from physbiblio.config import pbConfig
	from physbiblio.database import dbStats, catString, cats_alphabetical
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

fullRecordAde = {'bibkey': 'Ade:2013zuv', 'inspire': '1224741', 'arxiv': '1303.5076', 'ads': '2014A&A...571A..16P', 'scholar': None, 'doi': '10.1051/0004-6361/201321591', 'isbn': None, 'year': '2014', 'link': 'http://dx.doi.org/10.1051/0004-6361/201321591', 'comments': None, 'old_keys': '', 'crossref': None, 'bibtex': '@Article{Ade:2013zuv,\n        author = "Ade, P.A.R. and others",\n collaboration = "Planck",\n         title = "{Planck 2013 results. XVI. Cosmological parameters}",\n       journal = "Astron.Astrophys.",\n        volume = "571",\n          year = "2014",\n         pages = "A16",\n archiveprefix = "arXiv",\n  primaryclass = "astro-ph.CO",\n        eprint = "1303.5076",\n           doi = "10.1051/0004-6361/201321591",\n  reportnumber = "CERN-PH-TH-2013-129",\n}', 'firstdate': '2013-03-20', 'pubdate': '2014-10-29', 'exp_paper': 0, 'lecture': 0, 'phd_thesis': 0, 'review': 0, 'proceeding': 0, 'book': 0, 'noUpdate': 0, 'marks': '', 'abstract': None, 'bibtexDict': {'reportnumber': 'CERN-PH-TH-2013-129', 'doi': '10.1051/0004-6361/201321591', 'eprint': '1303.5076', 'primaryclass': 'astro-ph.CO', 'archiveprefix': 'arXiv', 'pages': 'A16', 'year': '2014', 'volume': '571', 'journal': 'Astron.Astrophys.', 'title': '{Planck 2013 results. XVI. Cosmological parameters}', 'collaboration': 'Planck', 'author': 'Ade, P.A.R. and others', 'ENTRYTYPE': 'article', 'ID': 'Ade:2013zuv'}, 'title': '{Planck 2013 results. XVI. Cosmological parameters}', 'journal': 'Astron.Astrophys.', 'volume': '571', 'number': '', 'pages': 'A16', 'published': 'Astron.Astrophys. 571 (2014) A16', 'author': 'Ade, P.A.R. and others'}
fullRecordGariazzo = {'bibkey': 'Gariazzo:2015rra', 'inspire': '1385583', 'arxiv': '1507.08204', 'ads': '2015JPhG...43c3001G', 'scholar': None, 'doi': '10.1088/0954-3899/43/3/033001', 'isbn': None, 'year': '2016', 'link': 'http://dx.doi.org/10.1088/0954-3899/43/3/033001', 'comments': None, 'old_keys': '', 'crossref': None, 'bibtex': '@Article{Gariazzo:2015rra,\n        author = "Gariazzo, S. and Giunti, C. and Laveder, M. and Li, Y.F. and Zavanin, E.M.",\n         title = "{Light sterile neutrinos}",\n       journal = "J.Phys.",\n        volume = "G43",\n          year = "2016",\n         pages = "033001",\n archiveprefix = "arXiv",\n  primaryclass = "hep-ph",\n        eprint = "1507.08204",\n           doi = "10.1088/0954-3899/43/3/033001",\n}', 'firstdate': '2015-07-29', 'pubdate': '2016-01-13', 'exp_paper': 0, 'lecture': 0, 'phd_thesis': 0, 'review': 0, 'proceeding': 0, 'book': 0, 'noUpdate': 0, 'marks': '', 'abstract': None, 'bibtexDict': {'doi': '10.1088/0954-3899/43/3/033001', 'eprint': '1507.08204', 'primaryclass': 'hep-ph', 'archiveprefix': 'arXiv', 'pages': '033001', 'year': '2016', 'volume': 'G43', 'journal': 'J.Phys.', 'title': '{Light sterile neutrinos}', 'author': 'Gariazzo, S. and Giunti, C. and Laveder, M. and Li, Y.F. and Zavanin, E.M.', 'ENTRYTYPE': 'article', 'ID': 'Gariazzo:2015rra'}, 'title': '{Light sterile neutrinos}', 'journal': 'J.Phys.', 'volume': 'G43', 'number': '', 'pages': '033001', 'published': 'J.Phys. G43 (2016) 033001', 'author': 'Gariazzo, S. et al.'}
tempFDBName = os.path.join(pbConfig.dataPath, "tests_first_%s.db"%today_ymd)

@unittest.skipIf(skipDBTests, "Database tests")
class TestCreateTables(unittest.TestCase):
	"""Test creation of tables"""
	def test_createTables(self):
		"""Test that all the tables are created at first time, if DB is empty"""
		if os.path.exists(tempFDBName):
			os.remove(tempFDBName)
		open(tempFDBName, 'a').close()
		self.pBDB = physbiblioDB(tempFDBName, pBLogger, noOpen = True)
		self.pBDB.openDB()

		self.assertTrue(self.pBDB.cursExec("SELECT name FROM sqlite_master WHERE type='table';"))
		self.assertEqual([name[0] for name in self.pBDB.cursor()], [])
		self.pBDB.createTables()
		self.assertTrue(self.pBDB.cursExec("SELECT name FROM sqlite_master WHERE type='table';"))
		self.assertEqual(sorted([name[0] for name in self.pBDB.cursor()]), ["categories", "entries", "entryCats", "entryExps", "expCats", "experiments", "settings"])
		self.assertTrue([e["name"] for e in self.pBDB.cats.getAll()], ["Main", "Tags"])

		os.remove(tempFDBName)
		open(tempFDBName, 'a').close()
		self.pBDB = physbiblioDB(tempFDBName, pBLogger)
		self.assertTrue(self.pBDB.cursExec("SELECT name FROM sqlite_master WHERE type='table';"))
		self.assertEqual(sorted([name[0] for name in self.pBDB.cursor()]), ["categories", "entries", "entryCats", "entryExps", "expCats", "experiments", "settings"])
		self.assertTrue([e["name"] for e in self.pBDB.cats.getAll()], ["Main", "Tags"])

	@classmethod
	def tearDownClass(self):
		if os.path.exists(tempFDBName):
			os.remove(tempFDBName)

@unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseMain(DBTestCase):#using cats just for simplicity
	"""Test main database class physbiblioDB and physbiblioDBSub structures"""
	def test_operations(self):
		"""Test main database functions (open/close, basic commands)"""
		print(self.pBDB.dbname)
		self.assertFalse(self.pBDB.checkUncommitted())
		self.assertTrue(self.pBDB.cursExec("SELECT * from categories"))
		self.assertTrue(self.pBDB.cursExec("SELECT * from categories where idCat=?", (1,)))
		self.assertTrue(self.pBDB.closeDB())
		self.assertTrue(self.pBDB.reOpenDB())
		self.assertFalse(self.pBDB.cursExec("SELECT * from categories where idCat=?",()))
		self.assertFalse(self.pBDB.cats.cursExec("SELECT * from categories where "))
		self.assertFalse(self.pBDB.checkUncommitted())
		self.assertTrue(self.pBDB.connExec("""
				INSERT into categories (name, description, parentCat, comments, ord)
					values (:name, :description, :parentCat, :comments, :ord)
				""", {"name":"abc","description":"d","parentCat":0,"comments":"", "ord":0}))
		self.assertTrue(self.pBDB.checkUncommitted())
		self.assertEqual(len(self.pBDB.cats.getAll()), 3)
		self.assertTrue(self.pBDB.undo())
		self.assertEqual(len(self.pBDB.cats.getAll()), 2)
		self.assertTrue(self.pBDB.cats.connExec("""
				INSERT into categories (name, description, parentCat, comments, ord)
					values (:name, :description, :parentCat, :comments, :ord)
				""", {"name":"abc","description":"d","parentCat":0,"comments":"", "ord":0}))
		self.assertTrue(self.pBDB.commit())
		self.assertTrue(self.pBDB.undo())
		self.assertEqual(len(self.pBDB.cats.getAll()), 3)
		self.assertTrue(self.pBDB.connExec("""
				INSERT into categories (name, description, parentCat, comments, ord)
					values (:name, :description, :parentCat, :comments, :ord)
				""", {"name":"abcd","description":"e","parentCat":0,"comments":"", "ord":0}))
		self.assertEqual(len(self.pBDB.cats.getAll()), 4)
		self.assertFalse(self.pBDB.cursExec("SELECT * from categories where "))
		self.assertEqual(len(self.pBDB.cats.getAll()), 4)
		self.assertFalse(self.pBDB.connExec("""
				INSERT into categories (name, description, parentCat, comments, ord)
					values (:name, :description, :parentCat, :comments, :ord)
				""", {"name":"abcd","description":"e","parentCat":0,"comments":""}))
		self.assertEqual(len(self.pBDB.cats.getAll()), 4)
		self.assertRaises(AttributeError, lambda: self.pBDB.stats)
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats,
			{"bibs": 0, "cats": 4, "exps": 0, "catBib": 0, "catExp": 0, "bibExp": 0})
		self.pBDB.cats.delete([2, 3])
		self.assertEqual(len(self.pBDB.cats.getAll()), 2)
		self.pBDB.commit()

	def test_literal_eval(self):
		"""Test literal_eval in physbiblioDBSub"""
		self.assertEqual(self.pBDB.cats.literal_eval("[1,2]"), [1,2])
		self.assertEqual(self.pBDB.cats.literal_eval("['test','a']"), ["test","a"])
		self.assertEqual(self.pBDB.cats.literal_eval("'test b'"), "'test b'")
		self.assertEqual(self.pBDB.cats.literal_eval("test c"), "test c")
		self.assertEqual(self.pBDB.cats.literal_eval("\"test d\""), '"test d"')
		self.assertEqual(self.pBDB.cats.literal_eval("[test e"), "[test e")
		self.assertEqual(self.pBDB.cats.literal_eval("[test f]"), None)
		self.assertEqual(self.pBDB.cats.literal_eval("'test g','test h'"), ["test g", "test h"])

@unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseLinks(DBTestCase):
	"""Test subclasses connecting categories, experiments, entries"""
	def test_catsEntries(self):
		"""Test catsEntries functions"""
		self.pBDB.utils.cleanSpareEntries()
		self.assertTrue(self.pBDB.catBib.insert(1, "test"))
		self.assertFalse(self.pBDB.catBib.insert(1, "test"))#already present
		self.assertEqual(tuple(self.pBDB.catBib.getOne(1, "test")[0]), (1,"test",1))
		self.assertTrue(self.pBDB.catBib.delete(1, "test"))
		self.assertEqual(self.pBDB.catBib.getOne(1, "test"), [])
		self.assertEqual(self.pBDB.catBib.insert(1, ["test1", "test2"]), None)
		self.assertEqual([tuple(a) for a in self.pBDB.catBib.getAll()], [(1,"test1",1), (2,"test2",1)])
		self.assertEqual(self.pBDB.catBib.delete(1, ["test1", "test2"]), None)
		self.assertEqual([tuple(a) for a in self.pBDB.catBib.getAll()], [])
		self.assertEqual(self.pBDB.catBib.insert([1,2], ["test1", "testA"]), None)
		self.assertTrue(self.pBDB.catBib.updateBibkey("test2", "testA"))
		self.assertEqual([tuple(a) for a in self.pBDB.catBib.getAll()],
			[(1,"test1",1), (2,"test2",1), (3,"test1",2), (4,"test2",2)])
		self.pBDB.utils.cleanSpareEntries()
		with patch('six.moves.input', return_value='[1,2]') as _input:
			self.pBDB.catBib.askCats("test1")
			_input.assert_called_once_with("categories for 'test1': ")
		with patch('six.moves.input', return_value='1,2') as _input:
			self.pBDB.catBib.askCats("test1")
			_input.assert_called_once_with("categories for 'test1': ")
		with patch('six.moves.input', return_value='test2') as _input:
			self.pBDB.catBib.askKeys([1,2])
			_input.assert_has_calls([call("entries for '1': "), call("entries for '2': ")])
		self.assertEqual([tuple(a) for a in self.pBDB.catBib.getAll()],
			[(1,"test1",1), (2,"test1",2), (3,"test2",1), (4,"test2",2)])
		self.assertTrue(self.pBDB.catBib.insert("test", "test"))

	def test_catExps(self):
		"""Test catsExps functions"""
		self.pBDB.utils.cleanSpareEntries()
		self.assertTrue(self.pBDB.catExp.insert(1, 10))
		self.assertFalse(self.pBDB.catExp.insert(1, 10))#already present
		self.assertEqual(tuple(self.pBDB.catExp.getOne(1, 10)[0]), (1,10,1))
		self.assertTrue(self.pBDB.catExp.delete(1, 10))
		self.assertEqual(self.pBDB.catExp.getOne(1, 10), [])
		self.assertEqual(self.pBDB.catExp.insert(1, [10, 11]), None)
		self.assertEqual([tuple(a) for a in self.pBDB.catExp.getAll()], [(1, 10, 1), (2, 11, 1)])
		self.assertEqual(self.pBDB.catExp.delete(1, [10, 11]), None)
		self.assertEqual([tuple(a) for a in self.pBDB.catExp.getAll()], [])
		self.assertEqual(self.pBDB.catExp.insert([1,2], [10, 11]), None)
		self.assertEqual([tuple(a) for a in self.pBDB.catExp.getAll()],
			[(1, 10, 1), (2, 11, 1), (3, 10, 2), (4, 11, 2)])
		self.pBDB.utils.cleanSpareEntries()
		with patch('six.moves.input', return_value='[1,2]') as _input:
			self.pBDB.catExp.askCats(10)
			_input.assert_called_once_with("categories for '10': ")
		with patch('six.moves.input', return_value='11') as _input:
			self.pBDB.catExp.askExps([1,2])
			_input.assert_has_calls([call("experiments for '1': "), call("experiments for '2': ")])
		self.assertEqual([tuple(a) for a in self.pBDB.catExp.getAll()],
			[(1, 10, 1), (2, 10, 2), (3, 11, 1), (4, 11, 2)])
		self.assertTrue(self.pBDB.catExp.insert("test", "test"))

	def test_entryExps(self):
		"""Test entryExps functions"""
		self.pBDB.utils.cleanSpareEntries()
		self.assertTrue(self.pBDB.bibExp.insert("test", 1))
		self.assertFalse(self.pBDB.bibExp.insert("test", 1))#already present
		self.assertEqual(tuple(self.pBDB.bibExp.getOne("test", 1)[0]), (1,"test",1))
		self.assertTrue(self.pBDB.bibExp.delete("test", 1))
		self.assertEqual(self.pBDB.bibExp.getOne("test", 1), [])
		self.assertEqual(self.pBDB.bibExp.insert(["test1", "test2"], 1), None)
		self.assertEqual([tuple(a) for a in self.pBDB.bibExp.getAll()], [(1,"test1",1), (2,"test2",1)])
		self.assertEqual(self.pBDB.bibExp.delete(["test1", "test2"], 1), None)
		self.assertEqual([tuple(a) for a in self.pBDB.bibExp.getAll()], [])
		self.assertEqual(self.pBDB.bibExp.insert(["test1", "testA"], [1,2]), None)
		self.assertTrue(self.pBDB.bibExp.updateBibkey("test2", "testA"))
		self.assertEqual([tuple(a) for a in self.pBDB.bibExp.getAll()],
			[(1,"test1",1), (2,"test1",2), (3,"test2",1), (4,"test2",2)])
		self.pBDB.utils.cleanSpareEntries()
		with patch('six.moves.input', return_value='[1,2]') as _input:
			self.pBDB.bibExp.askExps("test1")
			_input.assert_called_once_with("experiments for 'test1': ")
		with patch('six.moves.input', return_value='1,2') as _input:
			self.pBDB.bibExp.askExps("test1")
			_input.assert_called_once_with("experiments for 'test1': ")
		with patch('six.moves.input', return_value='test2') as _input:
			self.pBDB.bibExp.askKeys([1,2])
			_input.assert_has_calls([call("entries for '1': "), call("entries for '2': ")])
		self.assertEqual([tuple(a) for a in self.pBDB.bibExp.getAll()],
			[(1,"test1",1), (2,"test1",2), (3,"test2",1), (4,"test2",2)])
		self.assertTrue(self.pBDB.bibExp.insert("test", "test"))

@unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseExperiments(DBTestCase):
	"""Tests for the methods in the experiments subclass"""
	def checkNumberExperiments(self, number):
		"""Check the number of experiments"""
		self.assertEqual(self.pBDB.exps.count(), number)

	def test_insertUpdateDelete(self):
		"""Test insert, update, updateField, delete for an experiment"""
		self.checkNumberExperiments(0)
		self.assertFalse(self.pBDB.exps.insert({"name": "exp1"}))
		self.assertTrue(self.pBDB.exps.insert({"name": "exp1", "comments": "", "homepage": "", "inspire": ""}))
		self.checkNumberExperiments(1)
		self.assertTrue(self.pBDB.exps.insert({"name": "exp1", "comments": "", "homepage": "", "inspire": ""}))
		self.checkNumberExperiments(2)
		self.assertEqual({e["idExp"]: e["name"] for e in self.pBDB.exps.getAll()}, {1: "exp1", 2: "exp1"})
		self.assertEqual({e["idExp"]: e["inspire"] for e in self.pBDB.exps.getAll()}, {1: "", 2: ""})
		self.assertTrue(self.pBDB.exps.update({"name": "exp2", "comments": "", "homepage": "", "inspire": "123"}, 2))
		self.assertEqual({e["idExp"]: e["name"] for e in self.pBDB.exps.getAll()}, {1: "exp1", 2: "exp2"})
		self.assertTrue(self.pBDB.exps.updateField(1, "inspire", "456"))
		self.assertEqual({e["idExp"]: e["inspire"] for e in self.pBDB.exps.getAll()}, {1: "456", 2: "123"})
		self.assertFalse(self.pBDB.exps.update({"name": "exp2", "inspire": "123"}, 2))
		self.assertFalse(self.pBDB.exps.updateField(1, "inspires", "456"))
		self.assertFalse(self.pBDB.exps.updateField(1, "idExp", "2"))
		self.assertFalse(self.pBDB.exps.updateField(1, "inspire", None))
		self.checkNumberExperiments(2)
		self.assertTrue(self.pBDB.catExp.insert(1, 1))
		self.assertTrue(self.pBDB.bibExp.insert("test", 1))
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats["exps"], 2)
		self.assertEqual(self.pBDB.stats["catExp"], 1)
		self.assertEqual(self.pBDB.stats["bibExp"], 1)
		self.pBDB.exps.delete([1, 2])
		self.checkNumberExperiments(0)
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats["catExp"], 0)
		self.assertEqual(self.pBDB.stats["bibExp"], 0)

	def test_get(self):
		"""Test get methods"""
		self.assertTrue(self.pBDB.exps.insert({"name": "exp1", "comments": "", "homepage": "", "inspire": ""}))
		self.assertTrue(self.pBDB.exps.insert({"name": "exp2", "comments": "", "homepage": "", "inspire": ""}))
		self.checkNumberExperiments(2)
		self.assertEqual([dict(e) for e in self.pBDB.exps.getAll()],
			[{"idExp": 1, "name": "exp1", "comments": "", "homepage": "", "inspire": ""},
			{"idExp": 2, "name": "exp2", "comments": "", "homepage": "", "inspire": ""}])
		self.assertEqual([dict(e) for e in self.pBDB.exps.getByID(1)],
			[{"idExp": 1, "name": "exp1", "comments": "", "homepage": "", "inspire": ""}])
		self.assertEqual([dict(e) for e in self.pBDB.exps.getByName("exp2")],
			[{"idExp": 2, "name": "exp2", "comments": "", "homepage": "", "inspire": ""}])
		self.assertEqual(self.pBDB.exps.getDictByID(1),
			{"idExp": 1, "name": "exp1", "comments": "", "homepage": "", "inspire": ""})

	def test_filterAll(self):
		"""test the filterAll function, that looks into all the fields for a matching string"""
		self.assertTrue(self.pBDB.exps.insert({"name": "exp1match", "comments": "", "homepage": "", "inspire": ""}))
		self.assertTrue(self.pBDB.exps.insert({"name": "exp2", "comments": "match", "homepage": "", "inspire": ""}))
		self.assertTrue(self.pBDB.exps.insert({"name": "exp3", "comments": "", "homepage": "match", "inspire": ""}))
		self.assertTrue(self.pBDB.exps.insert({"name": "exp4", "comments": "", "homepage": "", "inspire": "match"}))
		self.checkNumberExperiments(4)
		self.assertEqual([dict(e) for e in self.pBDB.exps.filterAll("match")],
			[{"idExp": 1, "name": "exp1match", "comments": "", "homepage": "", "inspire": ""},
			{"idExp": 2, "name": "exp2", "comments": "match", "homepage": "", "inspire": ""},
			{"idExp": 3, "name": "exp3", "comments": "", "homepage": "match", "inspire": ""},
			{"idExp": 4, "name": "exp4", "comments": "", "homepage": "", "inspire": "match"}])
		self.assertEqual(len(self.pBDB.exps.filterAll("nonmatch")), 0)

	def test_print(self):
		"""Test to_str, printAll and printInCats"""
		self.assertTrue(self.pBDB.exps.insert(
			{"name": "exp1", "comments": "comment", "homepage": "http://some.url.org/", "inspire": "12"}))
		self.assertEqual(self.pBDB.exps.to_str(self.pBDB.exps.getByID(1)[0]),
			u'  1: exp1                 [http://some.url.org/                    ] [12]')
		self.assertTrue(self.pBDB.exps.insert(
			{"name": "exp2", "comments": "", "homepage": "", "inspire": ""}))
		self.assert_stdout(self.pBDB.exps.printAll,
			"  1: exp1                 [http://some.url.org/                    ] [12]\n  2: exp2                 [                                        ] []\n")
		self.assertTrue(self.pBDB.catExp.insert(0, 1))
		self.assertTrue(self.pBDB.catExp.insert(1, 2))
		self.assert_stdout(self.pBDB.exps.printInCats,
			"   0: Main\n          -> exp1 (1)\n        1: Tags\n               -> exp2 (2)\n")

	def test_getByOthers(self):
		"""Test getByCat and getByEntry creating some fake records"""
		data = self.pBDB.bibs.prepareInsert(u'\n\n%comment\n@article{abc,\nauthor = "me",\ntitle = "title",}', bibkey = "abc")
		data = self.pBDB.bibs.prepareInsert(u'\n\n%comment\n@article{defghi,\nauthor = "me",\ntitle = "title",}', bibkey = "defghi")
		self.assertTrue(self.pBDB.bibs.insert(data))
		self.assertTrue(self.pBDB.exps.insert({"name": "exp1", "comments": "", "homepage": "", "inspire": ""}))
		self.assertTrue(self.pBDB.catExp.insert(0, 1))
		self.assertTrue(self.pBDB.bibExp.insert("abc", 1))
		self.assertEqual(self.pBDB.exps.getByEntry("def"), [])
		self.assertEqual([dict(e) for e in self.pBDB.exps.getByEntry("abc")],
			[{'inspire': u'', 'comments': u'', 'name': u'exp1', 'bibkey': u'abc', 'idEnEx': 1, 'homepage': u'', 'idExp': 1}])
		self.assertEqual([dict(e) for e in self.pBDB.exps.getByEntries(["abc", "defghi"])],
			[{'inspire': u'', 'comments': u'', 'name': u'exp1', 'bibkey': u'abc', 'idEnEx': 1, 'homepage': u'', 'idExp': 1}])
		self.assertEqual(self.pBDB.exps.getByCat("1"), [])
		self.assertEqual([dict(e) for e in self.pBDB.exps.getByCat(0)],
			[{'idCat': 0, 'inspire': u'', 'comments': u'', 'name': u'exp1', 'idExC': 1, 'homepage': u'', 'idExp': 1}])
		self.assertTrue(self.pBDB.exps.insert({"name": "exp2", "comments": "", "homepage": "", "inspire": ""}))
		self.assertTrue(self.pBDB.bibExp.insert("defghi", 2))
		self.assertEqual([dict(e) for e in self.pBDB.exps.getByEntries(["abc", "defghi"])],
			[{'inspire': u'', 'comments': u'', 'name': u'exp1', 'bibkey': u'abc', 'idEnEx': 1, 'homepage': u'', 'idExp': 1},
			{'inspire': u'', 'comments': u'', 'name': u'exp2', 'bibkey': u'defghi', 'idEnEx': 2, 'homepage': u'', 'idExp': 2}])

@unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseCategories(DBTestCase):
	"""Tests for the methods in the categories subclass"""
	def checkNumberCategories(self, number):
		"""Check the number of experiments"""
		self.assertEqual(self.pBDB.cats.count(), number)

	def test_insertUpdateDelete(self):
		"""Test insert, update, updateField, delete for an experiment"""
		self.checkNumberCategories(2)
		self.assertFalse(self.pBDB.cats.insert({"name": "cat1"}))
		self.assertTrue(self.pBDB.cats.insert({"name": "cat1", "comments": "", "description": "", "parentCat": "0", "ord": "0"}))
		self.checkNumberCategories(3)
		self.assertFalse(self.pBDB.cats.insert({"name": "cat1", "comments": "", "description": "", "parentCat": "0", "ord": "1"}))
		self.assert_stdout(lambda: self.pBDB.cats.insert({"name": "cat1", "comments": "", "description": "", "parentCat": "0", "ord": "1"}),
			"An entry with the same name is already present in the same category!\n")
		self.assertTrue(self.pBDB.cats.insert({"name": "cat1", "comments": "", "description": "", "parentCat": "1", "ord": "1"}))
		self.checkNumberCategories(4)
		self.assertEqual({e["idCat"]: e["name"] for e in self.pBDB.cats.getAll()},
			{0: "Main", 1: "Tags", 2: "cat1", 3: "cat1"})
		self.assertEqual({e["idCat"]: e["parentCat"] for e in self.pBDB.cats.getAll()},
			{0: 0, 1: 0, 2: 0, 3: 1})
		self.assertTrue(self.pBDB.cats.update({"name": "cat2", "comments": "", "description": "", "parentCat": "1", "ord": 0}, 2))
		self.assertEqual({e["idCat"]: e["name"] for e in self.pBDB.cats.getAll()},
			{0: "Main", 1: "Tags", 2: "cat2", 3: "cat1"})
		self.assertTrue(self.pBDB.cats.updateField(1, "description", "abcd"))
		self.assertEqual({e["idCat"]: e["description"] for e in self.pBDB.cats.getAll()},
			{0: "This is the main category. All the other ones are subcategories of this one", 1: "abcd", 2: "", 3: ""})
		self.assertFalse(self.pBDB.cats.update({"name": "cat2", "comments": ""}, 2))
		self.assertFalse(self.pBDB.cats.updateField(1, "inspires", "abc"))
		self.assertFalse(self.pBDB.cats.updateField(1, "idCat", "2"))
		self.assertFalse(self.pBDB.cats.updateField(1, "parentCat", None))
		self.checkNumberCategories(4)
		self.assertTrue(self.pBDB.catExp.insert(2, 1))
		self.assertTrue(self.pBDB.catBib.insert(2, "test"))
		self.assertTrue(self.pBDB.cats.insert({"name": "cat3", "comments": "", "description": "", "parentCat": "3", "ord": "1"}))
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats["cats"], 5)
		self.assertEqual(self.pBDB.stats["catExp"], 1)
		self.assertEqual(self.pBDB.stats["catBib"], 1)
		self.pBDB.cats.delete([2, 3])
		self.checkNumberCategories(2)
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats["catExp"], 0)
		self.assertEqual(self.pBDB.stats["catBib"], 0)
		self.assert_stdout(lambda: self.pBDB.cats.delete(0), "You should not delete the category with id: 0.\n")
		self.checkNumberCategories(2)
		self.assert_stdout(lambda: self.pBDB.cats.delete(1), "You should not delete the category with id: 1.\n")
		self.checkNumberCategories(2)

	def test_get(self):
		"""Test get methods"""
		self.assertTrue(self.pBDB.cats.insert({"name": "cat1", "comments": "", "description": "", "parentCat": "1", "ord": "0"}))
		self.assertTrue(self.pBDB.cats.insert({"name": "cat2", "comments": "", "description": "", "parentCat": "1", "ord": "0"}))
		self.checkNumberCategories(4)
		self.assertEqual([dict(e) for e in self.pBDB.cats.getAll()],
			[{"idCat": 0, "name": "Main", "comments": "", "description": "This is the main category. All the other ones are subcategories of this one", "parentCat": 0, "ord": 0},
			{"idCat": 1, "name": "Tags", "comments": "", "description": "Use this category to store tags (such as: ongoing projects, temporary cats,...)", "parentCat": 0, "ord": 0},
			{"idCat": 2, "name": "cat1", "comments": "", "description": "", "parentCat": 1, "ord": 0},
			{"idCat": 3, "name": "cat2", "comments": "", "description": "", "parentCat": 1, "ord": 0}])
		self.assertEqual([dict(e) for e in self.pBDB.cats.getByID(2)],
			[{"idCat": 2, "name": "cat1", "comments": "", "description": "", "parentCat": 1, "ord": 0}])
		self.assertEqual([dict(e) for e in self.pBDB.cats.getByName("cat2")],
			[{"idCat": 3, "name": "cat2", "comments": "", "description": "", "parentCat": 1, "ord": 0}])
		self.assertEqual(self.pBDB.cats.getDictByID(2),
			{"idCat": 2, "name": "cat1", "comments": "", "description": "", "parentCat": 1, "ord": 0})
		self.assertEqual([dict(e) for e in self.pBDB.cats.getChild(0)],
			[{"idCat": 0, "name": "Main", "comments": "", "description": "This is the main category. All the other ones are subcategories of this one", "parentCat": 0, "ord": 0},
			{"idCat": 1, "name": "Tags", "comments": "", "description": "Use this category to store tags (such as: ongoing projects, temporary cats,...)", "parentCat": 0, "ord": 0}])
		self.assertEqual([dict(e) for e in self.pBDB.cats.getChild(2)], [])
		self.assertEqual([dict(e) for e in self.pBDB.cats.getParent(1)],
			[{"idCat": 0, "name": "Main", "comments": "", "description": "This is the main category. All the other ones are subcategories of this one", "parentCat": 0, "ord": 0}])

	def test_getByOthers(self):
		"""Test getByExp and getByEntry creating some fake records"""
		data = self.pBDB.bibs.prepareInsert(u'\n\n%comment\n@article{abc,\nauthor = "me",\ntitle = "title",}', bibkey = "abc")
		self.assertTrue(self.pBDB.bibs.insert(data))
		self.assertTrue(self.pBDB.exps.insert({"name": "exp1", "comments": "", "homepage": "", "inspire": ""}))
		self.assertTrue(self.pBDB.catExp.insert(1, 1))
		self.assertTrue(self.pBDB.catBib.insert(1, "abc"))
		self.assertEqual(self.pBDB.cats.getByEntry("def"), [])
		self.assertEqual([dict(e) for e in self.pBDB.cats.getByEntry("abc")],
			[{'idCat': 1, 'parentCat': 0, 'description': u'Use this category to store tags (such as: ongoing projects, temporary cats,...)', 'comments': u'', 'idEnC': 1, 'ord': 0, 'bibkey': u'abc', 'name': u'Tags'}])
		self.assertEqual(self.pBDB.cats.getByExp("2"), [])
		self.assertEqual([dict(e) for e in self.pBDB.cats.getByExp(1)],
			[{'idCat': 1, 'idExp': 1, 'parentCat': 0, 'description': u'Use this category to store tags (such as: ongoing projects, temporary cats,...)', 'comments': u'', 'idExC': 1, 'ord': 0, 'name': u'Tags'}])
		self.assertEqual(self.pBDB.cats.getByExp("2"), [])
		self.assertEqual([dict(e) for e in self.pBDB.cats.getByEntries(["abc", "defghi"])],
			[{'idCat': 1, 'parentCat': 0, 'description': u'Use this category to store tags (such as: ongoing projects, temporary cats,...)', 'comments': u'', 'idEnC': 1, 'ord': 0, 'bibkey': u'abc', 'name': u'Tags'}])
		data = self.pBDB.bibs.prepareInsert(u'\n\n%comment\n@article{defghi,\nauthor = "me",\ntitle = "title",}', bibkey = "defghi")
		self.assertTrue(self.pBDB.catBib.insert(0, "defghi"))
		self.assertEqual([dict(e) for e in self.pBDB.cats.getByEntries(["abc", "defghi"])],
			[{'idCat': 1, 'parentCat': 0, 'description': u'Use this category to store tags (such as: ongoing projects, temporary cats,...)', 'comments': u'', 'idEnC': 1, 'ord': 0, 'bibkey': u'abc', 'name': u'Tags'},
			{"idCat": 0, "name": "Main", "comments": "", "description": "This is the main category. All the other ones are subcategories of this one", "parentCat": 0, "ord": 0, 'idEnC': 2, 'bibkey': u'defghi'}])

	def test_catString(self):
		"""Test catString with existing and non existing records"""
		self.assertEqual(catString(1, self.pBDB), "   1: Tags")
		self.assertEqual(catString(1, self.pBDB, True), "   1: Tags - <i>Use this category to store tags (such as: ongoing projects, temporary cats,...)</i>")
		self.assertEqual(catString(2, self.pBDB), "")
		self.assert_stdout(lambda: catString(2, self.pBDB),
			"Category '2' not in database\n")

	def test_cats_alphabetical(self):
		"""Test alphabetical ordering of idCats with cats_alphabetical"""
		self.assertTrue(self.pBDB.cats.insert({"name": "c", "comments": "", "description": "", "parentCat": "1", "ord": "0"}))
		self.assertTrue(self.pBDB.cats.insert({"name": "g", "comments": "", "description": "", "parentCat": "1", "ord": "0"}))
		self.assertTrue(self.pBDB.cats.insert({"name": "d", "comments": "", "description": "", "parentCat": "1", "ord": "0"}))
		listId = [a["idCat"] for a in self.pBDB.cats.getChild(1)]
		self.assertEqual(listId, [2, 3, 4])
		self.assertEqual(cats_alphabetical(listId, self.pBDB), [2, 4, 3])
		self.assertEqual(cats_alphabetical([3, 4, 5], self.pBDB), [4, 3])
		self.assertEqual(cats_alphabetical([], self.pBDB), [])
		self.assert_stdout(lambda: cats_alphabetical([5], self.pBDB),
			"Category '5' not in database\n")

	def test_hierarchy(self):
		"""Testing the construction and print of the category hierarchies"""
		self.assertTrue(self.pBDB.cats.insert({"name": "c", "comments": "", "description": "1", "parentCat": "1", "ord": "0"}))
		self.assertTrue(self.pBDB.cats.insert({"name": "d", "comments": "", "description": "2", "parentCat": "2", "ord": "0"}))
		self.assertTrue(self.pBDB.cats.insert({"name": "e", "comments": "", "description": "3", "parentCat": "1", "ord": "0"}))
		self.assertEqual(self.pBDB.cats.getHier(), {0: {1: {2: {3: {}}, 4: {}}}})
		self.assertEqual(self.pBDB.cats.getHier(replace = False), {0: {1: {2: {3: {}}, 4: {}}}})
		self.assertEqual(self.pBDB.cats.getHier(startFrom = 2), {2: {3: {}}})
		self.assertEqual(self.pBDB.cats.getHier(self.pBDB.cats.getChild(2)), {0: {}})#as 0 is not in the original list!
		self.assertEqual(self.pBDB.cats.getHier(self.pBDB.cats.getChild(2), startFrom = 2), {2: {3: {}}})
		self.assertEqual(self.pBDB.cats.getHier(), {0: {1: {2: {3: {}}, 4: {}}}})
		self.assert_stdout(lambda: self.pBDB.cats.printHier(replace = True),
			"   0: Main\n        1: Tags\n             2: c\n                  3: d\n             4: e\n")
		self.assert_stdout(lambda: self.pBDB.cats.printHier(replace = True, sp = 3*" "),
			"   0: Main\n      1: Tags\n         2: c\n            3: d\n         4: e\n")
		self.assert_stdout(lambda: self.pBDB.cats.printHier(replace = True, startFrom = 2, withDesc = True),
			"   2: c - <i>1</i>\n        3: d - <i>2</i>\n")
		self.assert_stdout(lambda: self.pBDB.cats.printHier(replace = True, depth = 2),
			"   0: Main\n        1: Tags\n             2: c\n             4: e\n")

@unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseEntries(DBTestCase):
	"""Tests for the methods in the entries subclass"""
	def insert_three(self):
		"""Insert three elements in the DB for testing"""
		data = self.pBDB.bibs.prepareInsert(u'@article{abc,\nauthor = "me",\ntitle = "abc",}', arxiv="abc")
		self.assertTrue(self.pBDB.bibs.insert(data))
		data = self.pBDB.bibs.prepareInsert(u'@article{def,\nauthor = "me",\ntitle = "def",}', arxiv="def")
		self.assertTrue(self.pBDB.bibs.insert(data))
		data = self.pBDB.bibs.prepareInsert(u'@article{ghi,\nauthor = "me",\ntitle = "ghi",}', arxiv="ghi")
		self.assertTrue(self.pBDB.bibs.insert(data))

	def test_delete(self):
		"""Test delete a bibtex entry from the DB"""
		self.insert_three()
		self.assertTrue(self.pBDB.catBib.insert(1, "abc"))
		self.assertTrue(self.pBDB.bibExp.insert("abc", 1))
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats,
			{"bibs": 3, "cats": 2, "exps": 0, "catBib": 1, "catExp": 0, "bibExp": 1})
		self.pBDB.bibs.delete("aaa")
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats,
			{"bibs": 3, "cats": 2, "exps": 0, "catBib": 1, "catExp": 0, "bibExp": 1})
		self.pBDB.bibs.delete("abc")
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats,
			{"bibs": 2, "cats": 2, "exps": 0, "catBib": 0, "catExp": 0, "bibExp": 0})
		self.pBDB.bibs.delete(["def","ghi"])
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats,
			{"bibs": 0, "cats": 2, "exps": 0, "catBib": 0, "catExp": 0, "bibExp": 0})

	def test_prepareInsert(self):
		"""test prepareInsert"""
		#multiple entries in bibtex:
		self.assertEqual(self.pBDB.bibs.prepareInsert(
			u'@article{abc,\nauthor = "me",\ntitle = "mytit",}\n@article{def,\nauthor = "you",\ntitle = "other",}')["bibkey"], "abc")
		self.assertEqual(self.pBDB.bibs.prepareInsert(
			u'@article{abc,\nauthor = "me",\ntitle = "mytit",}\n@article{def,\nauthor = "you",\ntitle = "other",}', number = 1)["bibkey"], "def")

		#different fields
		bibtex = u'@article{abc,\nauthor = "me",\ntitle = "mytit",\narxiv="1801.00000",\n}'
		self.assertEqual(self.pBDB.bibs.prepareInsert(bibtex, bibkey = "def")["bibkey"], "def")
		self.assertIn("rticle{def,", self.pBDB.bibs.prepareInsert(bibtex, bibkey = "def")["bibtex"])

		data = self.pBDB.bibs.prepareInsert(bibtex)
		self.assertEqual(data["bibkey"], "abc")
		self.assertEqual(data["arxiv"], "1801.00000")

		#test simple fields
		bibtex = u'@article{abc,\nauthor = "me",\ntitle = "mytit",\n}'
		for k in ["inspire", "ads", "scholar", "comments", "old_keys", "abstract"]:
			self.assertEqual(data[k], None)
			tmp = {}
			tmp[k] = "try"
			self.assertEqual(self.pBDB.bibs.prepareInsert(bibtex, **tmp)[k], "try")
		for k in ["pubdate", "marks"]:
			self.assertEqual(data[k], "")
			tmp = {}
			tmp[k] = "try"
			self.assertEqual(self.pBDB.bibs.prepareInsert(bibtex, **tmp)[k], "try")
		for k in ["exp_paper", "lecture", "phd_thesis", "review", "proceeding", "book", "noUpdate"]:
			self.assertEqual(data[k], 0)
			tmp = {}
			tmp[k] = 1
			self.assertEqual(self.pBDB.bibs.prepareInsert(bibtex, **tmp)[k], 1)

		#test arxiv
		self.assertEqual(self.pBDB.bibs.prepareInsert(bibtex, arxiv = "1801.00000")["arxiv"],
			"1801.00000")
		bibtexA = u'@article{abc,\nauthor = "me",\ntitle = "mytit",\neprint="1801.00000",\n}'
		self.assertEqual(self.pBDB.bibs.prepareInsert(bibtexA)["arxiv"], "1801.00000")
		self.assertEqual(self.pBDB.bibs.prepareInsert(bibtex)["arxiv"], "")

		#more tests
		self.assertEqual(data["doi"], None)
		self.assertEqual(data["crossref"], None)
		self.assertEqual(data["abstract"], None)
		for k in ["doi", "isbn", "crossref", "abstract"]:
			bibtexA = u'@article{abc,\nauthor = "me",\ntitle = "mytit",\n%s="something",\n}'%k
			self.assertEqual(self.pBDB.bibs.prepareInsert(bibtexA)[k], "something")
			tmp = {}
			tmp[k] = "something"
			self.assertEqual(self.pBDB.bibs.prepareInsert(bibtex, **tmp)[k], "something")

		#test year
		self.assertEqual(data["year"], "2018")
		self.assertEqual(self.pBDB.bibs.prepareInsert(bibtex, year = "1999")["year"], "1999")
		self.assertEqual(self.pBDB.bibs.prepareInsert(bibtex, arxiv = "hep-ph/9901000")["year"], "1999")
		self.assertEqual(self.pBDB.bibs.prepareInsert(
			u'@article{abc,\nauthor = "me",\ntitle = "mytit",\nyear="2005",\n}')["year"],
			"2005")
		self.assertEqual(self.pBDB.bibs.prepareInsert(bibtex)["year"], None)

		#test link
		self.assertEqual(data["link"],
			pbConfig.arxivUrl + "abs/" + "1801.00000")
		self.assertEqual(self.pBDB.bibs.prepareInsert(bibtex, link = "http://some.thing")["link"],
			"http://some.thing")
		self.assertEqual(self.pBDB.bibs.prepareInsert(bibtex, doi = "somedoi")["link"],
			pbConfig.doiUrl + "somedoi")
		self.assertEqual(self.pBDB.bibs.prepareInsert(bibtex)["link"], "")

		#test firstdate
		self.assertEqual(data["firstdate"], datetime.date.today().strftime("%Y-%m-%d"))
		self.assertEqual(self.pBDB.bibs.prepareInsert(bibtex, firstdate = "2018-01-01")["firstdate"],
			"2018-01-01")

		#test abstract
		bibtex = u'@article{abc,\nauthor = "me",\ntitle = "mytit",\nabstract="try",\n}'
		self.assertEqual(self.pBDB.bibs.prepareInsert(bibtex)["abstract"], "try")

		#empty bibtex
		self.assertEqual(self.pBDB.bibs.prepareInsert(""), {"bibkey": ""})
		self.assert_in_stdout(lambda: self.pBDB.bibs.prepareInsert(""),
			"No elements found?")
		self.assertEqual(self.pBDB.bibs.prepareInsert("@article{abc,"), {"bibkey": ""})
		self.assert_in_stdout(lambda: self.pBDB.bibs.prepareInsert("@article{abc,"),
			"Impossible to parse bibtex!")

	def test_insert(self):
		"""Test insertion and of bibtex items"""
		self.assertFalse(self.pBDB.bibs.getField("abc", "bibkey"))
		data = self.pBDB.bibs.prepareInsert(u'@article{abc,\nauthor = "me",\ntitle = "abc",}', arxiv="abc")
		self.assertTrue(self.pBDB.bibs.insert(data))
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibkey"), "abc")
		self.pBDB.undo(verbose = False)
		del data["arxiv"]
		self.assertFalse(self.pBDB.bibs.insert(data))
		self.assert_in_stdout(lambda:self.pBDB.bibs.insert(data), 'ProgrammingError: You did not supply a value for binding 3.')
		self.assertTrue(self.pBDB.bibs.insertFromBibtex(u'@article{ghi,\nauthor = "me",\ntitle = "ghi",}'))

	def test_update(self):
		"""Test general update, field update, bibkey update"""
		self.assertFalse(self.pBDB.bibs.getField("abc", "bibkey"))
		data = self.pBDB.bibs.prepareInsert(u'@article{abc,\nauthor = "me",\ntitle = "abc",}', arxiv="abc")
		self.assertTrue(self.pBDB.bibs.insert(data))
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibkey"), "abc")
		datanew = self.pBDB.bibs.prepareInsert(u'@article{cde,\nauthor = "me",\ntitle = "abc",}', arxiv="cde")
		self.assertTrue(self.pBDB.bibs.update(datanew, "abc"))
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibkey"), "abc")
		self.assertEqual(self.pBDB.bibs.getField("abc", "arxiv"), "cde")
		del data["arxiv"]
		self.assertTrue(self.pBDB.bibs.update(data, "abc"))
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibkey"), "abc")
		self.assertEqual(self.pBDB.bibs.getField("abc", "arxiv"), None)
		e1 = self.pBDB.bibs.getByBibkey("abc")
		self.assertFalse(self.pBDB.bibs.update({"bibkey": "cde"}, "abc"))
		self.assert_in_stdout(lambda: self.pBDB.bibs.update({"bibkey": "cde"}, "abc"),
			'IntegrityError: NOT NULL constraint failed: entries.bibtex')
		self.assertFalse(self.pBDB.bibs.update({"bibkey": "cde", "bibtex": u'@article{abc,\nauthor = "me",\ntitle = "abc",}'}, "abc"))
		self.assertEqual(self.pBDB.bibs.getByBibkey("abc"), e1)

		self.assertTrue(self.pBDB.bibExp.insert("abc", 1))
		self.assertTrue(self.pBDB.catBib.insert(1, "abc"))
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats,
			{"bibs": 1, "cats": 2, "exps": 0, "catBib": 1, "catExp": 0, "bibExp": 1})
		self.assertTrue(self.pBDB.bibs.updateBibkey("abc", "def"))
		self.assertEqual(self.pBDB.bibs.getByBibkey("def")[0]["bibtex"], '@Article{abc,\n        author = "me",\n         title = "{abc}",\n}')
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats,
			{"bibs": 1, "cats": 2, "exps": 0, "catBib": 1, "catExp": 0, "bibExp": 1})

		self.assertEqual(self.pBDB.bibs.getByBibkey("def")[0]["inspire"], None)
		self.assertTrue(self.pBDB.bibs.updateField("def", "inspire", "1234", verbose = 0))
		self.assert_stdout(lambda: self.pBDB.bibs.updateField("def", "inspire", "1234"),
			"Updating 'inspire' for entry 'def'\n")
		self.assertEqual(self.pBDB.bibs.getByBibkey("def")[0]["inspire"], '1234')
		self.assertFalse(self.pBDB.bibs.updateField("def", "inspires", "1234", verbose = 0))
		self.assertFalse(self.pBDB.bibs.updateField("def", "inspire", None, verbose = 0))
		self.assert_stdout(lambda: self.pBDB.bibs.updateField("def", "inspires", "1234"),
			"Updating 'inspires' for entry 'def'\n")
		self.assert_stdout(lambda: self.pBDB.bibs.updateField("def", "inspires", "1234", verbose = 2),
			"Updating 'inspires' for entry 'def'\nNon-existing field or unappropriated value: (def, inspires, 1234)\n")

	def test_prepareUpdate(self):
		"""test prepareUpdate and related functions"""
		bibtexA = u'@article{abc,\nauthor="me",\ntitle="abc",\n}'
		bibtexB = u'@article{abc1,\nauthor="me",\ntitle="ABC",\narxiv="1234",\n}'
		bibtexE = "@article{,}"
		resultA = u'@Article{abc,\n        author = "me",\n         title = "{ABC}",\n         arxiv = "1234",\n}'
		resultB = u'@Article{abc1,\n        author = "me",\n         title = "{abc}",\n         arxiv = "1234",\n}'

		self.assertEqual(self.pBDB.bibs.prepareUpdate(bibtexA, bibtexE), "")
		self.assert_in_stdout(lambda: self.pBDB.bibs.prepareUpdate(bibtexA, bibtexE),
			"Parsing exception in prepareUpdate")
		self.assertEqual(self.pBDB.bibs.prepareUpdate(bibtexE, bibtexA), "")
		self.assert_in_stdout(lambda: self.pBDB.bibs.prepareUpdate(bibtexE, bibtexA),
			"Parsing exception in prepareUpdate")
		self.assertEqual(self.pBDB.bibs.prepareUpdate("", bibtexA), "")
		self.assert_in_stdout(lambda: self.pBDB.bibs.prepareUpdate("", bibtexA),
			"Empty bibtex?")

		bibtex = self.pBDB.bibs.prepareUpdate(bibtexA, bibtexB)
		self.assertEqual(bibtex, resultA + "\n\n")
		bibtex = self.pBDB.bibs.prepareUpdate(bibtexB, bibtexA)
		self.assertEqual(bibtex, resultB + "\n\n")

		self.pBDB.bibs.insertFromBibtex(bibtexA)
		self.pBDB.bibs.insertFromBibtex(bibtexB)
		data = self.pBDB.bibs.prepareUpdateByKey("abc", "abc1")
		self.assertEqual(data["bibkey"], "abc")
		self.assertEqual(data["arxiv"], "1234")
		self.assertEqual(data["bibtex"], resultA)
		data = self.pBDB.bibs.prepareUpdateByKey("abc1", "abc")
		self.assertEqual(data["bibkey"], "abc1")
		self.assertEqual(data["arxiv"], "1234")
		self.assertEqual(data["bibtex"], resultB)

		data = self.pBDB.bibs.prepareUpdateByBibtex("abc", bibtexB)
		self.assertEqual(data["bibkey"], "abc")
		self.assertEqual(data["arxiv"], "1234")
		self.assertEqual(data["bibtex"], resultA)
		data = self.pBDB.bibs.prepareUpdateByBibtex("abc1", bibtexA)
		self.assertEqual(data["bibkey"], "abc1")
		self.assertEqual(data["arxiv"], "1234")
		self.assertEqual(data["bibtex"], resultB)

	def test_replace(self):
		"""test replace functions"""
		#replaceInBibtex
		bibtexIn = u'@article{abc,\nauthor = "me",\ntitle = "abc",\njournal="jcap",\nvolume="1803",\nyear="2018",\npages="1",\narxiv="1234.56789",\n}'
		bibtexOut = u'@article{abc,\nauthor = "me",\ntitle = "abc",\njournal="jcap",\nvolume="1803",\nyear="2018",\npages="1",\narxiv="1234.56789",\n}'
		self.assertTrue(self.pBDB.bibs.insertFromBibtex(bibtexIn))
		bibtexOut = self.pBDB.bibs.getField("abc", "bibtex")
		self.assertEqual(self.pBDB.bibs.replaceInBibtex("abcd", "abcde"), [])
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibtex"), bibtexOut)
		self.assertEqual(self.pBDB.bibs.replaceInBibtex("jcap", "JCAP"), ["abc"])
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibtex"), bibtexOut.replace("jcap", "JCAP"))
		self.assertEqual(self.pBDB.bibs.replaceInBibtex("JCAP", "jcap"), ["abc"])

		self.assertEqual(self.pBDB.bibs.replaceInBibtex("jcap", ["JCAP"]), False)
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibtex"), bibtexOut)
		self.assert_in_stdout(lambda: self.pBDB.bibs.replaceInBibtex("jcap", ["JCAP"]),
			"InterfaceError: Error binding parameter :new - probably unsupported type.")
		self.assertEqual(self.pBDB.bibs.replaceInBibtex(["jcap"], "JCAP"), False)
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibtex"), bibtexOut)
		self.assert_in_stdout(lambda: self.pBDB.bibs.replaceInBibtex(["jcap"], "JCAP"),
			"InterfaceError: Error binding parameter :old - probably unsupported type.")

		# replace
		bibtexOut = u'@Article{abc,\n        author = "me",\n         title = "{abc}",\n       journal = "jcap",\n        volume = "1803",\n          year = "2018",\n         pages = "1",\n         arxiv = "1234.56789",\n}'
		self.assertEqual(self.pBDB.bibs.replace("bibtex", ["bibtex"], "abcd", ["abcde"]),
			(["abc"], [], []))
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibtex"), bibtexOut)

		self.assertEqual(self.pBDB.bibs.replace("volume", ["volume"], "([0-9]{2})([0-9]{2})", [r'\2'], regex = True),
			(["abc"], ["abc"], []))
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibtex"), bibtexOut.replace("1803", "03"))

		self.assertEqual(self.pBDB.bibs.replace("volume", ["volume"], "03", [r'1803']),
			(["abc"], ["abc"], []))
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibtex"), bibtexOut)

		self.assertEqual(self.pBDB.bibs.replace("volume", ["volume", "journal"], "1803", ["03", "1803"]),
			(["abc"], ["abc"], []))
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibtex"), bibtexOut.replace("1803", "03").replace("jcap", "1803"))

		bibtexIn = u'@article{def,\nauthor = "me",\ntitle = "def",\njournal="Phys. Rev.",\nvolume="D95",\nyear="2018",\npages="1",\narxiv="1234.56789",\n}'
		bibtexOut = u'@Article{def,\n        author = "me",\n         title = "{def}",\n       journal = "Phys. Rev. D",\n        volume = "95",\n          year = "2018",\n         pages = "1",\n         arxiv = "1234.56789",\n}'
		self.assertTrue(self.pBDB.bibs.insertFromBibtex(bibtexIn))
		self.assertEqual(self.pBDB.bibs.replace("published", ["journal", "volume"], "(Phys. Rev. [A-Z]{1})([0-9]{2}).*", [r'\1', r'\2'], regex = True),
			(["abc", "def"], ["def"], []))
		self.assertEqual(self.pBDB.bibs.getField("def", "bibtex"), bibtexOut)

		self.assertEqual(self.pBDB.bibs.replace("published", ["journal", "volume"], "(Phys. Rev. [A-Z]{1})([0-9]{2}).*", [r'\1', r'\2'],
			regex = True),
			(["abc", "def"], [], []))
		self.assertEqual(self.pBDB.bibs.replace("published", ["journal", "volume"], "(Phys. Rev. [A-Z]{1})([0-9]{2}).*", [r'\1', r'\2'],
			entries = self.pBDB.bibs.getByBibkey("abc"), regex = True),
			(["abc"], [], []))
		self.assertEqual(self.pBDB.bibs.replace("published", ["journal", "volume"], "(Phys. Rev. [A-Z]{1})([0-9]{2}).*", [r'\1', r'\2'],
			entries = self.pBDB.bibs.getByBibkey("abc"), regex = False),
			(["abc"], ["abc"], []))

		self.assertEqual(self.pBDB.bibs.replace("bibtex", "bibtex", "abcd", "abcde"),
			([], [], []))
		self.assert_in_stdout(lambda: self.pBDB.bibs.replace("bibtex", "bibtex", "abcd", "abcde"),
			"Invalid 'fiNews' or 'news' (they must be lists)")
		self.assertEqual(self.pBDB.bibs.replace("abcd", ["abcd"], "1234.00000", ['56789']),
			([], [], ["abc", "def"]))
		self.assert_in_stdout(lambda: self.pBDB.bibs.replace("abcd", ["abcd"], "1234.00000", ['56789']),
			"Something wrong in replace")

		bibtexIn = u'@article{ghi,\nauthor = "me",\ntitle = "ghi",\neprint="1234.56789",\n}'
		self.assertTrue(self.pBDB.bibs.insertFromBibtex(bibtexIn))
		self.assertEqual(self.pBDB.bibs.replace("eprint", ["volume"], "1234.00000", ['56789']),
			(["ghi"], ["ghi"], ["abc", "def"]))
		self.assert_in_stdout(lambda: self.pBDB.bibs.replace("eprint", ["volume"], "1234.00000", ['56789']),
			"Field eprint not found in entry ")
		self.assertEqual(self.pBDB.bibs.replace("arxiv", ["eprint"], "1234.00000", ['56789']),
			(["ghi"], [], ["abc", "def"]))
		self.assert_in_stdout(lambda: self.pBDB.bibs.replace("arxiv", ["eprint"], "1234.00000", ['56789']),
			"Something wrong in replace")

	def test_completeFetched(self):
		self.assertTrue(self.pBDB.bibs.insertFromBibtex(
			u'@article{abc,\nauthor = "me",\ntitle = "abc",\njournal="jcap",\nvolume="3",\nyear="2018",\npages="1",\narxiv="1234.56789",\n}'))
		fetched = self.pBDB.bibs.getByBibkey("abc")
		completed = self.pBDB.bibs.completeFetched(fetched)[0]
		self.assertEqual(completed["author"], "me")
		self.assertEqual(completed["title"], "{abc}")
		self.assertEqual(completed["journal"], "jcap")
		self.assertEqual(completed["volume"], "3")
		self.assertEqual(completed["year"], "2018")
		self.assertEqual(completed["pages"], "1")
		self.assertEqual(completed["published"], "jcap 3 (2018) 1")

		self.pBDB.undo(verbose = 0)
		self.assertTrue(self.pBDB.bibs.insertFromBibtex(u'@article{abc,\nauthor = "me and you and him and them",\ntitle = "abc",\n}'))
		fetched = self.pBDB.bibs.getByBibkey("abc")
		completed = self.pBDB.bibs.completeFetched(fetched)[0]
		self.assertEqual(completed["author"], "me et al.")
		self.assertEqual(completed["title"], "{abc}")
		self.assertEqual(completed["journal"], "")
		self.assertEqual(completed["volume"], "")
		self.assertEqual(completed["year"], "")
		self.assertEqual(completed["pages"], "")
		self.assertEqual(completed["published"], "")

		data = self.pBDB.bibs.prepareInsert(u'@article{def,\nauthor = "me",\ntitle = "def",}')
		data["bibtex"] = u'@article{abc,\nauthor = "me",\ntitle = "de"f",}'
		self.assertTrue(self.pBDB.bibs.insert(data))
		fetched = self.pBDB.bibs.getAll()
		completed = self.pBDB.bibs.completeFetched(fetched)
		self.assertEqual(completed[0]["bibtexDict"],
			{'ENTRYTYPE': 'article', 'ID': 'abc', 'author': 'me and you and him and them', 'title': '{abc}'})
		self.assertEqual(completed[1]["bibtexDict"], {})

	def test_fetchFromLast(self):
		"""Test the function fetchFromLast for the DB entries"""
		self.insert_three()
		self.pBDB.bibs.lastQuery = "SELECT * FROM entries"
		self.pBDB.bibs.lastVals = ()
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromLast().lastFetched],
			["abc", "def", "ghi"])
		self.pBDB.bibs.fetchByBibkey("def")
		self.pBDB.bibs.lastVals = ("def",)
		self.pBDB.bibs.lastQuery = "select * from entries  where bibkey=?"
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromLast().lastFetched],
			["def"])

	def test_fetchFromDict(self):
		"""test the pretty complicated function fetchFromDict"""
		self.insert_three()
		self.pBDB.bibExp.insert(["abc", "def"], 0)
		self.pBDB.catBib.insert(0, ["abc"])
		self.pBDB.catBib.insert(1, ["def", "ghi"])
		self.assertTrue(self.pBDB.exps.insert({"name": "exp1", "comments": "", "homepage": "", "inspire": ""}))

		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"bibkey": {"str": "ab", "operator": "like"}}).lastFetched],
			["abc"])
		self.assertEqual(self.pBDB.bibs.lastQuery,
			"select * from entries  where  bibkey like ?  order by firstdate ASC")

		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"exps": {"operator": "and", "id": 0}}, saveQuery = False).lastFetched],
			["abc", "def"])
		self.assertEqual(self.pBDB.bibs.lastQuery,
			"select * from entries  where  bibkey like ?  order by firstdate ASC")

		#try with different cats and exps
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"exps": {"operator": "and", "id": 0},
			"cats": {"operator": "or", "id": [0, 1]}},
			catExpOperator = "and").lastFetched],
			["abc", "def"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"exps": {"operator": "and", "id": 0},
			"cats": {"operator": "or", "id": [0, 1]}},
			catExpOperator = "or").lastFetched],
			["abc", "def", "ghi"])
		self.pBDB.catBib.insert(0, ["def"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"cats": {"operator": "and", "id": [0, 1]}}).lastFetched],
			["def"])
		self.pBDB.catBib.delete(0, "def")

		#check limitTo, limitOffset
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"exps": {"operator": "and", "id": 0},
			"cats": {"operator": "or", "id": [0, 1]}},
			catExpOperator = "or", limitTo = 2).lastFetched],
			["abc", "def"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"exps": {"operator": "and", "id": 0},
			"cats": {"operator": "or", "id": [0, 1]}},
			catExpOperator = "or", limitTo = 1, limitOffset = 2).lastFetched],
			["ghi"])

		#check orderBy, orderType
		self.pBDB.bibs.updateField("def", "firstdate", "2018-01-01")
		self.pBDB.bibs.updateField("abc", "firstdate", "2018-01-02")
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"exps": {"operator": "and", "id": 0}}, orderBy = "bibkey").lastFetched],
			["abc", "def"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"exps": {"operator": "and", "id": 0}}, orderType = "DESC").lastFetched],
			["abc", "def"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"exps": {"operator": "and", "id": 0}}, orderBy = "bibkey", orderType = "DESC").lastFetched],
			["def", "abc"])

		#check connection operator and multiple match
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"bibkey#0": {"str": "a", "operator": "like"},
			"bibkey#1": {"str": "b", "operator": "like"}}).lastFetched],
			["abc"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"bibkey#0": {"str": "abc", "operator": "="},
			"arxiv": {"str": "abc", "operator": "="}}).lastFetched],
			["abc"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"bibkey#0": {"str": "a", "operator": "like"},
			"bibkey#1": {"str": "d", "operator": "like"}}).lastFetched],
			[])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"bibkey#0": {"str": "a", "operator": "like", "connection": "or"},
			"bibkey#1": {"str": "d", "operator": "like", "connection": "or"}}).lastFetched],
			["def", "abc"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"bibkey#0": {"str": "a", "operator": "like"},
			"bibkey#1": {"str": "d", "operator": "like"}}, defaultConnection = "or").lastFetched],
			["def", "abc"])

		#check wrong behaviour with a list in "str"
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"bibkey": {"str": ["a", "b"], "operator": "like"}}).lastFetched], [])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchFromDict(
			{"bibkey": {"str": ["a", "b"], "operator": "="}}).lastFetched], [])
		self.assert_in_stdout(lambda: self.pBDB.bibs.fetchFromDict(
			{"bibkey": {"str": ["a", "b"], "operator": "="}}),
			"InterfaceError: Error binding parameter 0 - probably unsupported type.")

	def test_fetchAll(self):
		"""Test the fetchAll and getAll functions"""
		#generic
		self.insert_three()
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll()],
			["abc", "def", "ghi"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchAll().lastFetched],
			["abc", "def", "ghi"])
		self.assertEqual(self.pBDB.bibs.lastQuery, "select * from entries  order by firstdate ASC")
		#saveQuery
		self.pBDB.bibs.lastQuery = ""
		self.pBDB.bibs.getAll(saveQuery = False)
		self.assertEqual(self.pBDB.bibs.lastQuery, "")
		self.pBDB.bibs.fetchAll(saveQuery = False)
		self.assertEqual(self.pBDB.bibs.lastQuery, "")
		#limitTo
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(limitTo = 1)],
			["abc"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchAll(limitTo = 1).lastFetched],
			["abc"])
		self.assertEqual(self.pBDB.bibs.lastQuery, "select * from entries  order by firstdate ASC LIMIT 1")
		#limitTo + limitOffset
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(limitTo = 5, limitOffset = 1)],
			["def", "ghi"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchAll(limitTo = 5, limitOffset = 1).lastFetched],
			["def", "ghi"])
		self.assertEqual(self.pBDB.bibs.lastQuery, "select * from entries  order by firstdate ASC LIMIT 5 OFFSET 1")
		#limitOffset alone (no effect)
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(limitOffset = 1)],
			["abc", "def", "ghi"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchAll(limitOffset = 1).lastFetched],
			["abc", "def", "ghi"])
		self.assertEqual(self.pBDB.bibs.lastQuery, "select * from entries  order by firstdate ASC")
		#orderType
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(orderType = "DESC")],
			["abc", "def", "ghi"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchAll(orderType = "DESC").lastFetched],
			["abc", "def", "ghi"])
		self.assertEqual(self.pBDB.bibs.lastQuery, "select * from entries  order by firstdate DESC")
		#orderBy
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(orderBy = "bibkey", orderType = "DESC")],
			["ghi", "def", "abc"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchAll(orderBy = "bibkey", orderType = "DESC").lastFetched],
			["ghi", "def", "abc"])
		self.assertEqual(self.pBDB.bibs.lastQuery, "select * from entries  order by bibkey DESC")

		#some parameter combinations
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(
			params = {"bibkey": "abc"})],
			["abc"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchAll(
			params = {"bibkey": "abc"}).lastFetched],
			["abc"])
		self.assertEqual(self.pBDB.bibs.lastQuery,
			"select * from entries  where bibkey = ?  order by firstdate ASC")
		self.assertEqual(self.pBDB.bibs.lastVals, ("abc",))
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(
			params = {"bibkey": "abc", "arxiv": "def"})],
			[])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchAll(
			params = {"bibkey": "abc", "arxiv": "def"}).lastFetched],
			[])
		self.assertIn(self.pBDB.bibs.lastQuery,
			["select * from entries  where bibkey = ?  and arxiv = ?  order by firstdate ASC",
			"select * from entries  where arxiv = ?  and bibkey = ?  order by firstdate ASC"])
		self.assertEqual(sorted(self.pBDB.bibs.lastVals), sorted(("abc", "def")))
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(
			params = {"bibkey": "abc", "arxiv": "def"}, connection = "or")],
			["abc", "def"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchAll(
			params = {"bibkey": "abc", "arxiv": "def"}, connection = "or").lastFetched],
			["abc", "def"])
		self.assertIn(self.pBDB.bibs.lastQuery,
			["select * from entries  where bibkey = ?  or arxiv = ?  order by firstdate ASC",
			"select * from entries  where arxiv = ?  or bibkey = ?  order by firstdate ASC"])
		self.assertEqual(sorted(self.pBDB.bibs.lastVals), sorted(("abc", "def")))
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(
			params = {"bibkey": "ab", "arxiv": "ef"}, connection = "or", operator = "like")],
			["abc", "def"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchAll(
			params = {"bibkey": "ab", "arxiv": "ef"}, connection = "or", operator = "like").lastFetched],
			["abc", "def"])
		self.assertIn(self.pBDB.bibs.lastQuery,
			["select * from entries  where bibkey like ?  or arxiv like ?  order by firstdate ASC",
			"select * from entries  where arxiv like ?  or bibkey like ?  order by firstdate ASC"])
		self.assertEqual(sorted(self.pBDB.bibs.lastVals), sorted(("%ab%", "%ef%")))

		#test some bad connection or operator
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(
			params = {"bibkey": "abc", "arxiv": "def"}, connection = "o r")],
			[])
		self.assertIn(self.pBDB.bibs.lastQuery,
			["select * from entries  where bibkey = ?  and arxiv = ?  order by firstdate ASC",
			"select * from entries  where arxiv = ?  and bibkey = ?  order by firstdate ASC"])
		self.assertEqual(sorted(self.pBDB.bibs.lastVals), sorted(("abc", "def")))
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchAll(
			params = {"bibkey": "ab", "arxiv": "ef"}, connection = "or", operator = "lik").lastFetched],
			[])
		self.assertIn(self.pBDB.bibs.lastQuery,
			["select * from entries  where bibkey = ?  or arxiv = ?  order by firstdate ASC",
			"select * from entries  where arxiv = ?  or bibkey = ?  order by firstdate ASC"])
		self.assertEqual(sorted(self.pBDB.bibs.lastVals), sorted(("ab", "ef")))

		#generate some errors
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(limitTo = "a")], [])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(limitTo = "bibkey")], [])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(limitTo = 1, limitOffset = "a")], [])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(orderBy = "a")], [])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(orderType = "abc")], ["abc", "def", "ghi"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(params = {"abc": "bibkey"})], [])

		#test different cursors
		self.pBDB.bibs.lastFetched = "test"
		self.pBDB.bibs.fetchAll(doFetch = False)
		self.assertEqual([e["bibkey"] for e in self.pBDB.curs], [])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchCurs], ["abc", "def", "ghi"])
		self.assertEqual(self.pBDB.bibs.lastFetched, "test")

		testBibName = os.path.join(pbConfig.dataPath, "tests_%s.bib"%today_ymd)
		sampleTxt = '@Article{abc,\n        author = "me",\n         title = "{abc}",\n}\n@Article{def,\n        author = "me",\n         title = "{def}",\n}\n@Article{ghi,\n        author = "me",\n         title = "{ghi}",\n}\n'
		self.pBDB.bibs.fetchAll(doFetch = False)
		with patch('physbiblio.database.entries.fetchCursor', return_value = self.pBDB.bibs.fetchCursor()) as _curs:
			pBExport.exportAll(testBibName)
		with open(testBibName) as f:
			self.assertEqual(f.read(), sampleTxt)
		os.remove(testBibName)

	def test_fetchByBibkey(self):
		"""Test the fetchByBibkey and getByBibkey functions"""
		self.insert_three()
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchByBibkey("abcdef").lastFetched],
			[])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getByBibkey("abcdef")],
			[])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchByBibkey("abc").lastFetched],
			["abc"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getByBibkey("abc")],
			["abc"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchByBibkey(["abc", "def"]).lastFetched],
			["abc", "def"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getByBibkey(["abc", "def"])],
			["abc", "def"])
		self.assertEqual(self.pBDB.bibs.lastQuery,
			"select * from entries  where bibkey =  ?  or bibkey =  ?  order by firstdate ASC")
		self.assertEqual(self.pBDB.bibs.lastVals, ("abc", "def"))
		self.pBDB.bibs.lastQuery = ""
		self.pBDB.bibs.lastVals = ()
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchByBibkey("abc", saveQuery = False).lastFetched],
			["abc"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getByBibkey("abc", saveQuery = False)],
			["abc"])
		self.assertEqual(self.pBDB.bibs.lastQuery, "")
		self.assertEqual(self.pBDB.bibs.lastVals, ())

	def test_fetchByKey(self):
		"""Test the fetchByKey and getByKey functions"""
		self.insert_three()
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchByKey("abcdef").lastFetched],
			[])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getByKey("abcdef")],
			[])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchByKey("abc").lastFetched],
			["abc"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getByKey("abc")],
			["abc"])
		self.pBDB.bibs.updateField("ghi", "old_keys", "abc")
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchByKey(["abc", "def"]).lastFetched],
			["abc", "def", "ghi"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getByKey(["abc", "def"])],
			["abc", "def", "ghi"])
		self.assertRegex(self.pBDB.bibs.lastQuery, "select \* from entries  where .*")
		self.assertRegex(self.pBDB.bibs.lastQuery, ".*bibkey  like   \?  or  bibkey  like   \?.*")
		self.assertRegex(self.pBDB.bibs.lastQuery, ".*old_keys  like   \?  or  old_keys  like   \?.*")
		self.assertRegex(self.pBDB.bibs.lastQuery, ".*bibtex  like   \?  or  bibtex  like   \?.*")
		self.assertRegex(self.pBDB.bibs.lastQuery, ".* order by firstdate ASC")
		self.assertEqual(self.pBDB.bibs.lastVals,
			('%abc%', '%def%', '%abc%', '%def%', '%abc%', '%def%'))
		self.pBDB.bibs.lastQuery = ""
		self.pBDB.bibs.lastVals = ()
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchByKey("abc", saveQuery = False).lastFetched],
			["abc", "ghi"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getByKey("abc", saveQuery = False)],
			["abc", "ghi"])
		self.assertEqual(self.pBDB.bibs.lastQuery, "")
		self.assertEqual(self.pBDB.bibs.lastVals, ())

	def test_fetchByBibtex(self):
		"""Test the fetchByBibtex and getByBibtex functions"""
		self.insert_three()
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchByBibtex("abcdef").lastFetched],
			[])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getByBibtex("abcdef")],
			[])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchByBibtex("me").lastFetched],
			["abc", "def", "ghi"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getByBibtex("me")],
			["abc", "def", "ghi"])
		self.pBDB.bibs.updateField("ghi", "old_keys", "abc")
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchByBibtex(["abc", "def"]).lastFetched],
			["abc", "def"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getByBibtex(["abc", "def"])],
			["abc", "def"])
		self.assertEqual(self.pBDB.bibs.lastQuery,
			"select * from entries  where bibtex  like   ?  or bibtex  like   ?  order by firstdate ASC")
		self.assertEqual(self.pBDB.bibs.lastVals,
			('%abc%', '%def%'))
		self.pBDB.bibs.lastQuery = ""
		self.pBDB.bibs.lastVals = ()
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchByBibtex("abc", saveQuery = False).lastFetched],
			["abc"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getByBibtex("abc", saveQuery = False)],
			["abc"])
		self.assertEqual(self.pBDB.bibs.lastQuery, "")
		self.assertEqual(self.pBDB.bibs.lastVals, ())

	def test_getField(self):
		data = self.pBDB.bibs.prepareInsert(u'@article{abc,\nauthor = "me",\ntitle = "abc",}',
			arxiv = "abc", doi = "1", isbn = 9)
		self.assertTrue(self.pBDB.bibs.insert(data))
		self.assertEqual(self.pBDB.bibs.getField("abc", "doi"), "1")
		self.assertEqual(self.pBDB.bibs.getField("abc", "arxiv"), "abc")
		self.assertEqual(self.pBDB.bibs.getField("abc", "isbn"), "9")
		self.assertFalse(self.pBDB.bibs.getField("def", "isbn"))
		self.assert_stdout(lambda: self.pBDB.bibs.getField("def", "isbn"),
			"Error in getEntryField('def', 'isbn'): no element found?\n")
		self.assertFalse(self.pBDB.bibs.getField("abc", "def"))
		self.assert_stdout(lambda: self.pBDB.bibs.getField("abc", "def"),
			"Error in getEntryField('abc', 'def'): the field is missing?\n")

	def test_toDataDict(self):
		self.insert_three()
		a = self.pBDB.bibs.toDataDict("abc")
		self.assertEqual(a["bibkey"], "abc")
		self.assertEqual(a["bibtex"], u'@Article{abc,\n        author = "me",\n         title = "{abc}",\n}')

	def test_getUrl(self):
		data = self.pBDB.bibs.prepareInsert(u'@article{abc,\nauthor = "me",\ntitle = "abc",}',
			arxiv = "1234.5678", doi = "1/2/3")
		self.assertTrue(self.pBDB.bibs.insert(data))
		self.assertEqual(self.pBDB.bibs.getArxivUrl("abc"), "http://arxiv.org/abs/1234.5678")
		self.assertEqual(self.pBDB.bibs.getDoiUrl("abc"), "http://dx.doi.org/1/2/3")
		self.assertFalse(self.pBDB.bibs.getArxivUrl("def"))
		self.assertFalse(self.pBDB.bibs.getDoiUrl("def"))
		self.assertTrue(self.pBDB.bibs.insertFromBibtex(u'@article{def,\nauthor = "me",\ntitle = "def",}'))
		self.assertFalse(self.pBDB.bibs.getArxivUrl("def"))
		self.assertFalse(self.pBDB.bibs.getDoiUrl("def"))

	def test_fetchByCat(self):
		"""test bibs.fetchByCat e bibs.getByCat"""
		self.insert_three()
		self.pBDB.catBib.insert(1, ["abc", "def"])
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats,
			{"bibs": 3, "cats": 2, "exps": 0, "catBib": 2, "catExp": 0, "bibExp": 0})
		entries = self.pBDB.bibs.fetchByCat(1).lastFetched
		self.assertEqual([e["bibkey"] for e in entries], ["abc", "def"])
		entries = self.pBDB.bibs.getByCat(1)
		self.assertEqual([e["bibkey"] for e in entries], ["abc", "def"])

		entries = self.pBDB.bibs.fetchByCat(1, orderBy = "entries.bibkey", orderType = "DESC").lastFetched
		self.assertEqual([e["bibkey"] for e in entries], ["def", "abc"])
		entries = self.pBDB.bibs.getByCat(1, orderBy = "entries.bibkey", orderType = "DESC")
		self.assertEqual([e["bibkey"] for e in entries], ["def", "abc"])

		entries = self.pBDB.bibs.getByCat(2)
		self.assertEqual([e["bibkey"] for e in entries], [])

		entries = self.pBDB.bibs.getByCat(1, orderBy = "entries.bib")
		self.assertEqual([e["bibkey"] for e in entries], [])
		self.assert_in_stdout(lambda: self.pBDB.bibs.getByCat(1, orderBy = "entries.bib"),
			"Cursor error: no such column: entries.bib")
		self.assert_in_stdout(lambda: self.pBDB.bibs.getByCat(1, orderBy = "entries.bib"),
			"OperationalError: no such column: entries.bib")

		entries = self.pBDB.bibs.getByCat(1, orderType = "wrong")
		self.assertEqual([e["bibkey"] for e in entries], [])
		self.assert_in_stdout(lambda: self.pBDB.bibs.getByCat(1, orderType = "wrong"),
			'Cursor error: near "wrong": syntax error')
		self.assert_in_stdout(lambda: self.pBDB.bibs.getByCat(1, orderType = "wrong"),
			'OperationalError: near "wrong": syntax error')

	def test_fetchByExp(self):
		"""test bibs.fetchByExp e bibs.getByExp"""
		self.insert_three()
		self.pBDB.bibExp.insert(["abc", "def"], 0)
		self.assertTrue(self.pBDB.exps.insert({"name": "exp1", "comments": "", "homepage": "", "inspire": ""}))
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats,
			{"bibs": 3, "cats": 2, "exps": 1, "catBib": 0, "catExp": 0, "bibExp": 2})
		entries = self.pBDB.bibs.fetchByExp(0).lastFetched
		self.assertEqual([e["bibkey"] for e in entries], ["abc", "def"])
		entries = self.pBDB.bibs.getByExp(0)
		self.assertEqual([e["bibkey"] for e in entries], ["abc", "def"])

		entries = self.pBDB.bibs.fetchByExp(0, orderBy = "entries.bibkey", orderType = "DESC").lastFetched
		self.assertEqual([e["bibkey"] for e in entries], ["def", "abc"])
		entries = self.pBDB.bibs.getByExp(0, orderBy = "entries.bibkey", orderType = "DESC")
		self.assertEqual([e["bibkey"] for e in entries], ["def", "abc"])

		entries = self.pBDB.bibs.getByExp(2)
		self.assertEqual([e["bibkey"] for e in entries], [])

		entries = self.pBDB.bibs.getByExp(0, orderBy = "entries.bib")
		self.assertEqual([e["bibkey"] for e in entries], [])
		self.assert_in_stdout(lambda: self.pBDB.bibs.getByExp(0, orderBy = "entries.bib"),
			"Cursor error: no such column: entries.bib")
		self.assert_in_stdout(lambda: self.pBDB.bibs.getByExp(0, orderBy = "entries.bib"),
			"OperationalError: no such column: entries.bib")

		entries = self.pBDB.bibs.getByExp(0, orderType = "wrong")
		self.assertEqual([e["bibkey"] for e in entries], [])
		self.assert_in_stdout(lambda: self.pBDB.bibs.getByExp(0, orderType = "wrong"),
			'Cursor error: near "wrong": syntax error')
		self.assert_in_stdout(lambda: self.pBDB.bibs.getByExp(0, orderType = "wrong"),
			'OperationalError: near "wrong": syntax error')

	def test_cleanBibtexs(self):
		"""test cleanBibtexs"""
		self.insert_three()
		bibtexIn = u'%comment\n@article{abc,\n\nauthor = "me",\ntitle = "ab\nc",\njournal="jcap",\nvolume="1803",\nyear="2018",\npages="1",\narxiv="1234.56789",\n}'
		bibtexOut = u'@Article{abc,\n        author = "me",\n         title = "{ab c}",\n       journal = "jcap",\n        volume = "1803",\n          year = "2018",\n         pages = "1",\n         arxiv = "1234.56789",\n}'
		self.pBDB.bibs.updateField("abc", "bibtex", bibtexIn)
		self.assert_in_stdout(lambda: self.pBDB.bibs.cleanBibtexs(startFrom = 1),
			"CleanBibtexs will process 2 total entries")
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibtex"), bibtexIn)
		self.assert_in_stdout(lambda: self.pBDB.bibs.cleanBibtexs(entries = self.pBDB.bibs.getByBibkey("def")),
			"CleanBibtexs will process 1 total entries")
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibtex"), bibtexIn)
		self.assert_in_stdout(lambda: self.pBDB.bibs.cleanBibtexs(startFrom = "a"),
			"Invalid startFrom in cleanBibtexs")
		self.assertEqual(self.pBDB.bibs.cleanBibtexs(startFrom = 5),
			(0, 0, []))

		self.assert_in_stdout(lambda: self.pBDB.bibs.cleanBibtexs(),
			"CleanBibtexs will process 3 total entries")
		self.pBDB.bibs.updateField("abc", "bibtex", bibtexIn)
		self.assertEqual(self.pBDB.bibs.cleanBibtexs(), (3, 0, ["abc"]))
		self.pBDB.bibs.updateField("abc", "bibtex", bibtexIn)
		self.assert_in_stdout(lambda: self.pBDB.bibs.cleanBibtexs(),
			"3 entries processed\n0 errors occurred\n1 entries changed")
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibtex"), bibtexOut)

		self.pBDB.bibs.updateField("def", "bibtex", '@book{def,\ntitle="some",')
		self.assert_in_stdout(lambda: self.pBDB.bibs.cleanBibtexs(),
			"Error while cleaning entry 'def'")
		self.assert_in_stdout(lambda: self.pBDB.bibs.cleanBibtexs(),
			"3 entries processed\n1 errors occurred\n0 entries changed")
		self.pBDB.bibs.cleanBibtexs()

	def test_printAll(self):
		self.insert_three()
		self.assert_stdout(lambda: self.pBDB.bibs.printAllBibkeys(),
			"   0 abc\n   1 def\n   2 ghi\n3 elements found\n")
		self.assert_stdout(lambda: self.pBDB.bibs.printAllBibkeys(entriesIn = self.pBDB.bibs.getByBibkey("abc")),
			"   0 abc\n1 elements found\n")

		self.assert_stdout(lambda: self.pBDB.bibs.printAllBibtexs(),
			'   0 - @Article{abc,\n        author = "me",\n         title = "{abc}",\n}\n\n   1 - @Article{def,\n        author = "me",\n         title = "{def}",\n}\n\n   2 - @Article{ghi,\n        author = "me",\n         title = "{ghi}",\n}\n\n3 elements found\n')
		self.assert_stdout(lambda: self.pBDB.bibs.printAllBibtexs(entriesIn = self.pBDB.bibs.getByBibkey("abc")),
			'   0 - @Article{abc,\n        author = "me",\n         title = "{abc}",\n}\n\n1 elements found\n')

		today = datetime.date.today().strftime("%Y-%m-%d")
		self.pBDB.bibs.setReview("abc")
		self.pBDB.bibs.updateField("abc", "arxiv", "1234")
		self.pBDB.bibs.updateField("abc", "doi", "somedoi")
		self.pBDB.bibs.printAllInfo()
		self.assert_stdout(lambda: self.pBDB.bibs.printAllInfo(),
			'[   0 - '+today+' ]  (rev) abc                            1234                 somedoi             \n[   1 - '+today+' ]        def                            def                  -                   \n[   2 - '+today+' ]        ghi                            ghi                  -                   \n3 elements found\n')
		self.pBDB.bibs.updateField("ghi", "firstdate", "2018-01-01")
		self.pBDB.bibs.updateField("def", "firstdate", "2018-03-01")
		self.assert_stdout(lambda: self.pBDB.bibs.printAllInfo(),
			'[   0 - 2018-01-01 ]        ghi                            ghi                  -                   \n[   1 - 2018-03-01 ]        def                            def                  -                   \n[   2 - '+today+' ]  (rev) abc                            1234                 somedoi             \n3 elements found\n')
		self.assert_stdout(lambda: self.pBDB.bibs.printAllInfo(entriesIn = self.pBDB.bibs.getByBibkey("abc")),
			'[   0 - '+today+' ]  (rev) abc                            1234                 somedoi             \n1 elements found\n')
		self.assert_stdout(lambda: self.pBDB.bibs.printAllInfo(entriesIn = self.pBDB.bibs.getByBibkey("abc"), addFields = "author"),
			'[   0 - '+today+' ]  (rev) abc                            1234                 somedoi             \n   author: me\n1 elements found\n')
		self.assert_stdout(lambda: self.pBDB.bibs.printAllInfo(entriesIn = self.pBDB.bibs.getByBibkey("abc"), addFields = ["author"]),
			'[   0 - '+today+' ]  (rev) abc                            1234                 somedoi             \n   author: me\n1 elements found\n')
		self.assert_stdout(lambda: self.pBDB.bibs.printAllInfo(entriesIn = self.pBDB.bibs.getByBibkey("abc"), addFields = "title"),
			'[   0 - '+today+' ]  (rev) abc                            1234                 somedoi             \n   title: {abc}\n1 elements found\n')
		self.assert_stdout(lambda: self.pBDB.bibs.printAllInfo(entriesIn = self.pBDB.bibs.getByBibkey("abc"), addFields = ["eprint", "journals"]),
			'[   0 - '+today+' ]  (rev) abc                            1234                 somedoi             \n1 elements found\n')

	def test_setStuff(self):
		"""test ["setBook", "setLecture", "setPhdThesis", "setProceeding", "setReview", "setNoUpdate"]"""
		self.insert_three()
		for procedure, field in zip(
				["setBook", "setLecture", "setPhdThesis", "setProceeding", "setReview", "setNoUpdate"],
				["book", "lecture", "phd_thesis", "proceeding", "review", "noUpdate"]):
			self.assertEqual(self.pBDB.bibs.getField("abc", field), 0)
			self.assertTrue(getattr(self.pBDB.bibs, procedure)("abc"))
			self.assertEqual(self.pBDB.bibs.getField("abc", field), 1)
			self.assertTrue(getattr(self.pBDB.bibs, procedure)("abc", 0))
			self.assertEqual(self.pBDB.bibs.getField("abc", field), 0)
			self.assertTrue(getattr(self.pBDB.bibs, procedure)("abc1"))

			self.assertEqual(self.pBDB.bibs.getField("def", field), 0)
			self.assertEqual(self.pBDB.bibs.getField("ghi", field), 0)
			self.assertEqual(getattr(self.pBDB.bibs, procedure)(["def", "ghi"]), None)
			self.assertEqual(self.pBDB.bibs.getField("def", field), 1)
			self.assertEqual(self.pBDB.bibs.getField("ghi", field), 1)
			self.assertEqual(getattr(self.pBDB.bibs, procedure)(["def", "ghi"], 0), None)
			self.assertEqual(self.pBDB.bibs.getField("def", field), 0)
			self.assertEqual(self.pBDB.bibs.getField("ghi", field), 0)

	def test_rmBibtexStuff(self):
		"""Test rmBibtexComments and rmBibtexACapo"""
		self.assertEqual(self.pBDB.bibs.rmBibtexComments(u'%comment\n@article{ghi,\nauthor = "me",\ntitle = "ghi",}'),
			u'@article{ghi,\nauthor = "me",\ntitle = "ghi",}')
		self.assertEqual(self.pBDB.bibs.rmBibtexComments(u' %comment\n@article{ghi,\nauthor = "me",\ntitle = "ghi",}'),
			u'@article{ghi,\nauthor = "me",\ntitle = "ghi",}')
		self.assertEqual(self.pBDB.bibs.rmBibtexComments(u'@article{ghi,\nauthor = "%me",\ntitle = "ghi",}'),
			u'@article{ghi,\nauthor = "%me",\ntitle = "ghi",}')
		self.assertEqual(self.pBDB.bibs.rmBibtexComments(u'@article{ghi,\nauthor = "me",\ntitle = "ghi",\n  %journal="JCAP",\n}'),
			u'@article{ghi,\nauthor = "me",\ntitle = "ghi",\n}')

		self.assertEqual(self.pBDB.bibs.rmBibtexACapo(u'@article{ghi,\nauthor = "me",\ntitle = "gh\ni",\n}'),
			u'@Article{ghi,\n        author = "me",\n         title = "{gh i}",\n}\n\n')
		self.assertEqual(self.pBDB.bibs.rmBibtexACapo(u'@article{ghi,\nauthor = "me",\ntitle = "ghi",\n}'),
			u'@Article{ghi,\n        author = "me",\n         title = "{ghi}",\n}\n\n')

	def test_importFromBib(self):
		with open("tmpbib.bib", "w") as f:
			f.write(u'@article{abc,\nauthor = "me",\ntitle = "abc",}\n@article{def,\nauthor = "me",\ntitle = "def",}\n')
		self.pBDB.bibs.importFromBib("tmpbib.bib", completeInfo = False)
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll()], ["abc", "def"])

		self.pBDB.undo(verbose = 0)
		with open("tmpbib.bib", "w") as f:
			f.write(u'@article{abc,\nauthor = "me",\ntitle = "abc",\n}\n@article{def,\n}\n')
		self.pBDB.bibs.importFromBib("tmpbib.bib", completeInfo = False)
		self.assert_in_stdout(lambda: self.pBDB.bibs.importFromBib("tmpbib.bib", completeInfo = False),
			"Impossible to parse text:")
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll()], [])

		#test with completeInfo
		pbConfig.params["fetchAbstract"] = True
		pbConfig.params["defaultCategories"] = 1
		with open("tmpbib.bib", "w") as f:
			f.write(u'@article{Gariazzo:2015rra,\nauthor = "me",\narxiv = "1507.08204",\n}\n@article{Gariazzo:2014rra,\nauthor="me",\n}\n')
		with patch('physbiblio.webimport.arxiv.webSearch.retrieveUrlAll', side_effect = [
				("bibtex_not_used", {"abstract": "some fake abstract"})]) as _retrieve:
			with patch('physbiblio.database.entries.updateInspireID', side_effect = ["1385583", False]) as _inspireid:
				with patch('physbiblio.webimport.inspireoai.webSearch.retrieveOAIData', side_effect=[
						{'doi': u'10.1088/0954-3899/43/3/033001', 'isbn': None, 'ads': u'2015JPhG...43c3001G', 'pubdate': u'2016-01-13', 'firstdate': u'2015-07-29', 'journal': u'J.Phys.', 'arxiv': u'1507.08204', 'id': '1385583', 'volume': u'G43', 'bibtex': None, 'year': u'2016', 'oldkeys': '', 'bibkey': u'Gariazzo:2015rra', 'pages': u'033001'},
						[]]) as _oai:
					self.pBDB.bibs.importFromBib("tmpbib.bib")
					self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll()], ["Gariazzo:2015rra", "Gariazzo:2014rra"])
					self.assertEqual([e["inspire"] for e in self.pBDB.bibs.getAll()], ["1385583", None])
					self.assertEqual([len(e["abstract"]) > 10 if e["abstract"] is not None else 0 for e in self.pBDB.bibs.getAll()], [True, False])
					self.assertEqual([e["firstdate"] for e in self.pBDB.bibs.getAll()], ['2015-07-29', datetime.date.today().strftime("%Y-%m-%d")])
					self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getByCat(1)], ["Gariazzo:2015rra", "Gariazzo:2014rra"])

		self.pBDB.undo(verbose = 0)
		pbConfig.params["fetchAbstract"] = False
		pbConfig.params["defaultCategories"] = {"ab"}
		self.pBDB.bibs.importFromBib("tmpbib.bib", completeInfo = False)
		self.assert_in_stdout(lambda: self.pBDB.bibs.importFromBib("tmpbib.bib", completeInfo = False),
			"2 entries processed, of which 2 existing")

		self.pBDB.undo(verbose = 0)
		self.assert_in_stdout(lambda: self.pBDB.bibs.importFromBib("tmpbib.bib", completeInfo = False),
			"Error binding parameter :idCat - probably unsupported type.")
		self.assertEqual([dict(e) for e in self.pBDB.catBib.getAll()], [])

		os.remove("tmpbib.bib")

	@unittest.skipIf(skipOnlineTests, "Online tests")
	def test_loadAndInsert_online(self):
		"""tests for loadAndInsert with online connection"""
		self.assertTrue(self.pBDB.bibs.loadAndInsert(['Gariazzo:2015rra', 'Ade:2013zuv']))
		self.assertEqual(self.pBDB.bibs.getAll(), [fullRecordAde, fullRecordGariazzo])

	def test_loadAndInsert(self):
		"""tests for loadAndInsert and loadAndInsertWithCats (mocked)"""
		# loadAndInsert
		self.assertFalse(self.pBDB.bibs.loadAndInsert(None))
		self.assert_in_stdout(lambda: self.pBDB.bibs.loadAndInsert(None),
			"Invalid arguments!")
		#methods
		for method in ["inspire", "doi", "arxiv", "isbn", "inspireoai"]:
			with patch('physbiblio.webimport.%s.webSearch.retrieveUrlAll'%method, return_value = "") as _mock:
				self.assertFalse(self.pBDB.bibs.loadAndInsert("abcdef", method = method))
				_mock.assert_called_once_with("abcdef")
		self.assertFalse(self.pBDB.bibs.loadAndInsert("abcdef", method = "nonexistent"))
		self.assert_in_stdout(lambda: self.pBDB.bibs.loadAndInsert("abcdef", method = "nonexistent"),
			"Method not valid:")
		self.assertTrue(self.pBDB.bibs.loadAndInsert('@article{abc,\nauthor="me",\ntitle="abc",\n}', method = "bibtex"))
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll()], ["abc"])
		#childProcess
		self.assertEqual(self.pBDB.bibs.lastInserted, ["abc"])
		#imposeKey
		self.assertTrue(self.pBDB.bibs.loadAndInsert('@article{abc,\nauthor="me",\ntitle="abc",\n}',
			imposeKey = "def", method = "bibtex", childProcess = True))
		self.assertEqual(self.pBDB.bibs.lastInserted, ["abc", "def"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll()], ["abc", "def"])
		allBibtexs = [e["bibtex"] for e in self.pBDB.bibs.getAll()]
		self.assertEqual(allBibtexs[0].replace("{abc,", "{def,"), allBibtexs[1])
		#existing
		self.assertEqual(self.pBDB.bibs.count(), 2)
		self.assertTrue(self.pBDB.bibs.loadAndInsert('@article{abc,\nauthor="me",\ntitle="abc",\n}',
			method = "bibtex"))
		self.assertEqual(self.pBDB.bibs.count(), 2)
		self.assertEqual(self.pBDB.bibs.loadAndInsert('@article{abc,\nauthor="me",\ntitle="abc",\n}',
			method = "bibtex", returnBibtex = True),
			'@Article{abc,\n        author = "me",\n         title = "{abc}",\n}')
		#returnBibtex
		self.assertEqual(self.pBDB.bibs.loadAndInsert('@article{ghi,\nauthor="me",\ntitle="ghi",\n}',
			method = "bibtex", returnBibtex = True),
			'@Article{ghi,\n        author = "me",\n         title = "{ghi}",\n}')
		self.assertEqual(self.pBDB.bibs.lastInserted, ["ghi"])
		#unreadable bibtex (bibtex method)
		self.assertFalse(self.pBDB.bibs.loadAndInsert('@article{jkl,', method = "bibtex"))
		self.assert_in_stdout(lambda: self.pBDB.bibs.loadAndInsert('@article{jkl,', method = "bibtex"),
			"Error while reading the bibtex ")

		self.pBDB.undo(verbose = 0)
		pbConfig.params["defaultCategories"] = [1]
		pbConfig.params["fetchAbstract"] = False
		with patch('physbiblio.database.entries.updateInspireID', return_value = "1") as _mock_uiid:
			with patch('physbiblio.database.entries.updateInfoFromOAI', return_value = True) as _mock_uio:
				#test add categories
				with patch('physbiblio.webimport.inspire.webSearch.retrieveUrlAll',
						return_value = u'\n@article{key0,\nauthor = "Gariazzo",\ntitle = "{title}",}\n') as _mock:
					self.assertTrue(self.pBDB.bibs.loadAndInsert("key0"))
					self.assertEqual([e["idCat"] for e in self.pBDB.cats.getByEntry("key0")],
						pbConfig.params["defaultCategories"])
				self.pBDB.undo(verbose = 0)
				#test with list entry (also nested lists)
				with patch('physbiblio.webimport.inspire.webSearch.retrieveUrlAll',
						side_effect = [
						u'\n@article{key0,\nauthor = "Gariazzo",\ntitle = "{title}",}\n',
						u'\n@article{key0,\nauthor = "Gariazzo",\ntitle = "{title}",}\n']) as _mock:
					self.assert_in_stdout(lambda: self.pBDB.bibs.loadAndInsert(["key0", "key1"]),
						"Already existing: key0")
					_mock.assert_has_calls([call("key0"), call("key1")])
					self.assertEqual(self.pBDB.bibs.count(), 1)
				self.pBDB.undo(verbose = 0)
				#test with number>0
				with patch('physbiblio.webimport.inspire.webSearch.retrieveUrlAll',
						side_effect = [
						u'@article{key0,\nauthor = "Gariazzo",\ntitle = "{title}",}\n@article{key1,\nauthor = "Gariazzo",\ntitle = "{title}",}\n',
						u'@article{key0,\nauthor = "Gariazzo",\ntitle = "{title}",}\n@article{key1,\nauthor = "Gariazzo",\ntitle = "{title}",}\n']) as _mock:
					self.assertTrue(self.pBDB.bibs.loadAndInsert("key0", number = 1))
					self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll()],
						["key1"])
					self.assertTrue(self.pBDB.bibs.loadAndInsert("key0", number = 0))
					self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll()],
						["key1", "key0"])
				self.pBDB.undo(verbose = 0)
				#test setBook when using isbn
				with patch('physbiblio.webimport.isbn.webSearch.retrieveUrlAll',
						return_value = u'@article{key0,\nauthor = "Gariazzo",\ntitle = "{title}",}') as _mock:
					self.assertTrue(self.pBDB.bibs.loadAndInsert("key0", method = "isbn"))
					self.assertEqual([e["book"] for e in self.pBDB.bibs.getAll()],
						[1])
				self.pBDB.undo(verbose = 0)
				#test abstract download
				pbConfig.params["fetchAbstract"] = True
				with patch('physbiblio.webimport.inspire.webSearch.retrieveUrlAll',
						side_effect = [
						u'\n@article{key0,\nauthor = "Gariazzo",\ntitle = "{title}",}\n',
						u'\n@article{key1,\nauthor = "Gariazzo",\ntitle = "{title}",\narxiv="1234.5678",}\n']) as _mock:
					with patch('physbiblio.webimport.arxiv.webSearch.retrieveUrlAll',
							return_value = (u'\n@article{key0,\nauthor = "Gariazzo",\ntitle = "{title}",}\n', {"abstract": "some fake abstract"})) as _mock:
						self.assertTrue(self.pBDB.bibs.loadAndInsert("key0"))
						self.assertEqual(self.pBDB.bibs.getByBibkey("key0")[0]["abstract"], None)
						self.assertTrue(self.pBDB.bibs.loadAndInsert("key1"))
						self.assertEqual(self.pBDB.bibs.getByBibkey("key1")[0]["abstract"], "some fake abstract")
				pbConfig.params["fetchAbstract"] = False
				self.pBDB.undo(verbose = 0)
				#unreadable bibtex, empty bibkey (any other method)
				with patch('physbiblio.webimport.inspire.webSearch.retrieveUrlAll',
						side_effect = [
						u'\n@article{key0,\nauthor = ',
						u'\n@article{key0,\nauthor = ',
						u'\n@article{ ,\nauthor = "Gariazzo",\ntitle = "{title}",}\n',
						u'\n@article{ ,\nauthor = "Gariazzo",\ntitle = "{title}",}\n',]) as _mock:
					self.assertFalse(self.pBDB.bibs.loadAndInsert('key0'))
					self.assert_in_stdout(lambda: self.pBDB.bibs.loadAndInsert("key0"),
						"Impossible to parse bibtex!\nImpossible to insert an entry with empty bibkey")
					self.pBDB.undo(verbose = 0)
					self.assertFalse(self.pBDB.bibs.loadAndInsert('key0'))
					self.assert_in_stdout(lambda: self.pBDB.bibs.loadAndInsert("key0"),
						"Wrong type or value for field ID (None)?\nImpossible to insert an entry with empty bibkey")
				self.pBDB.undo(verbose = 0)
				_mock_uiid.reset_mock()
				_mock_uio.reset_mock()
				#test updateInspireID, updateInfoFromOAI are called
				with patch('physbiblio.webimport.inspire.webSearch.retrieveUrlAll',
						return_value = u'\n@article{key0,\nauthor = "Gariazzo",\ntitle = "{title}",\narxiv="1234.5678",}') as _mock:
					self.assertTrue(self.pBDB.bibs.loadAndInsert("key0"))
					_mock_uiid.assert_called_once_with('key0', 'key0')
					_mock_uio.assert_called_once_with('1')
				self.pBDB.undo(verbose = 0)
				_mock_uiid.reset_mock()
				_mock_uio.reset_mock()
				#test updateInspireID, updateInfoFromOAI are called
				with patch('physbiblio.webimport.inspire.webSearch.retrieveUrlAll',
						return_value = u'@article{key0,\nauthor = "Gariazzo",\ntitle = "{title}",\narxiv="1234.5678",}\n@article{key1,\nauthor = "Gariazzo",\ntitle = "{title}",\narxiv="1234.5678",}\n') as _mock:
					self.assertTrue(self.pBDB.bibs.loadAndInsert("key0", number = 0))
					_mock_uiid.assert_called_once_with('key0', 'key0', number = 0)
					_mock_uio.assert_called_once_with('1')
				self.pBDB.undo(verbose = 0)
				_mock_uiid.reset_mock()
				_mock_uio.reset_mock()
				#test updateInspireID, updateInfoFromOAI are called
				with patch('physbiblio.webimport.arxiv.webSearch.retrieveUrlAll',
						return_value = u'@article{key0,\nauthor = "Gariazzo",\ntitle = "{title}",\narxiv="1234.5678",}') as _mock:
					self.assertTrue(self.pBDB.bibs.loadAndInsert("key0", method = "arxiv"))
					_mock_uiid.assert_not_called()
					_mock_uio.assert_not_called()

		# loadAndInsertWithCats
		self.pBDB.bibs.lastInserted = ["abc"]
		with patch('six.moves.input', return_value='[1,2]') as _input:
			with patch('physbiblio.database.entries.loadAndInsert', autospec = True) as _mock:
				self.pBDB.bibs.loadAndInsertWithCats(["acb"], "doi", True, 1, True, "yes")
				_input.assert_called_once_with("categories for 'abc': ")
				_mock.assert_called_once_with(self.pBDB.bibs, ["acb"], childProcess='yes', imposeKey=True, method='doi', number=1, returnBibtex=True)

	@unittest.skipIf(skipOnlineTests, "Online tests")
	def test_getFieldsFromArxiv(self):
		"""tests for getFieldsFromArxiv (online)"""
		pbConfig.params["maxAuthorSave"] = 5
		self.pBDB.bibs.insertFromBibtex(u'@article{Gariazzo:2015rra,\narxiv="1507.08204"\n}')
		self.pBDB.bibs.insertFromBibtex(u'@article{Ade:2013zuv,\narxiv="1303.5076"\n}')
		self.assertNotIn("Aghanim", self.pBDB.bibs.getField("Ade:2013zuv", "bibtex"))
		self.assertFalse(self.pBDB.bibs.getFieldsFromArxiv("abcd", "authors"))
		self.assertTrue(self.pBDB.bibs.getFieldsFromArxiv("Ade:2013zuv", "authors"))
		self.assertIn("Aghanim", self.pBDB.bibs.getField("Ade:2013zuv", "bibtex"))
		self.assertEqual(self.pBDB.bibs.getFieldsFromArxiv(["Gariazzo:2015rra", "Ade:2013zuv"], "primaryclass"),
			(["Gariazzo:2015rra", "Ade:2013zuv"], []))
		self.assertIn("astro-ph", self.pBDB.bibs.getField("Ade:2013zuv", "bibtex"))
		self.assertIn("hep-ph", self.pBDB.bibs.getField("Gariazzo:2015rra", "bibtex"))

	@unittest.skipIf(skipOnlineTests, "Online tests")
	def test_updateInspireID(self):
		"""tests for updateInspireID (online)"""
		self.pBDB.bibs.insertFromBibtex(u'@article{Gariazzo:2015rra,\narxiv="1507.08204"\n}')
		self.assertEqual(self.pBDB.bibs.updateInspireID("Gariazzo:2015rra"), "1385583")
		self.assertEqual(self.pBDB.bibs.updateInspireID("Gariazzo 2015", "Gariazzo:2015rra", number = 3), "1385583")
		self.assertFalse(self.pBDB.bibs.updateInspireID("Gariazzo:2015", "Gariazzo:2015rra"))
		self.assertFalse(self.pBDB.bibs.updateInspireID("abcdefghi"))

	@unittest.skipIf(skipOnlineTests, "Online tests")
	def test_searchOAIUpdates_online(self):
		"""tests for searchOAIUpdates, with real connection"""
		self.assertEqual(self.pBDB.bibs.searchOAIUpdates(startFrom = 1), (0, [], []))
		self.pBDB.bibs.insert(self.pBDB.bibs.prepareInsert(
			u'@article{Gariazzo:2015rra,\narxiv="1507.08204"\n}', inspire = "1385583"))
		self.pBDB.bibs.insert(self.pBDB.bibs.prepareInsert(
			u'@article{Ade:2013zuv,\narxiv="1303.5076"\n}', inspire = "1224741"))
		self.assertEqual(self.pBDB.bibs.searchOAIUpdates(),
			(2, [], ["Gariazzo:2015rra", "Ade:2013zuv"]))
		self.assertEqual(self.pBDB.bibs.getAll(), [fullRecordAde, fullRecordGariazzo])

	def test_searchOAIUpdates(self):
		"""tests for searchOAIUpdates, with mock functions"""
		self.assertEqual(self.pBDB.bibs.searchOAIUpdates(startFrom = 1), (0, [], []))
		self.pBDB.bibs.insert(self.pBDB.bibs.prepareInsert(
			u'@article{Gariazzo:2015rra,\narxiv="1507.08204"\n}', inspire = "1385583"))
		self.pBDB.bibs.insert(self.pBDB.bibs.prepareInsert(
			u'@article{Ade:2013zuv,\narxiv="1303.5076"\n}', inspire = "1224741"))
		entry1 = self.pBDB.bibs.getByBibkey("Gariazzo:2015rra")[0]
		entry2 = self.pBDB.bibs.getByBibkey("Ade:2013zuv")[0]
		entry1a = dict(entry1)
		entry2a = dict(entry2)
		entry1a["doi"] = "1/2/3/4"
		entry2a["doi"] = "1/2/3/4"
		entry1a["bibtexDict"]["journal"] = "jcap"
		entry2a["bibtexDict"]["journal"] = "jcap"
		with patch('physbiblio.database.entries.updateInfoFromOAI', side_effect=[
				True, True,
				True, True,
				True, True,
				False, True,
				]) as _mock_uioai:
			with patch("physbiblio.database.entries.fetchCursor", side_effect = [
					[entry1, entry2],#1
					[entry1a, entry2a],#2
					[entry1a, entry2a],#3
					[entry2],#4
					[entry1, entry2],#6
					]) as _mock_ga:
				with patch("physbiblio.database.entries.getByBibkey", side_effect = [
						[entry1a], [entry2a],#1
						[entry1a], [entry2a],#3
						[entry1a], [entry2a],#4,5
						[entry2a]#6
						]) as _mock_gbk:
					self.assertEqual(self.pBDB.bibs.searchOAIUpdates(),
						(2, [], ["Gariazzo:2015rra", "Ade:2013zuv"]))#1
					self.assertEqual(self.pBDB.bibs.searchOAIUpdates(),
						(0, [], []))#2
					self.assertEqual(self.pBDB.bibs.searchOAIUpdates(force = True),
						(2, [], []))#3
					self.assertEqual(self.pBDB.bibs.searchOAIUpdates(startFrom = 1),
						(1, [], ["Ade:2013zuv"]))#4
					self.assertEqual(self.pBDB.bibs.searchOAIUpdates(entries = [entry1]),
						(1, [], ["Gariazzo:2015rra"]))#5
					self.assertEqual(self.pBDB.bibs.searchOAIUpdates(),
						(2, ["Gariazzo:2015rra"], ["Ade:2013zuv"]))#6

	@unittest.skipIf(skipOnlineTests, "Online tests")
	def test_updateInfoFromOAI_online(self):
		"""test updateInfoFromOAI, with online connection"""
		expected = [fullRecordGariazzo]
		self.pBDB.bibs.insert(self.pBDB.bibs.prepareInsert(u'@article{Gariazzo:2015rra,\narxiv="1507.08204"\n}', inspire = "1385583"))
		self.assertTrue(self.pBDB.bibs.updateInfoFromOAI("Gariazzo:2015rra"))
		self.assertEqual(self.pBDB.bibs.getByBibkey("Gariazzo:2015rra"), expected)
		self.pBDB.undo(verbose = 0)
		self.pBDB.bibs.insert(self.pBDB.bibs.prepareInsert(u'@article{Gariazzo:2015rra,\narxiv="1507.08204"\n}', inspire = "1385583"))
		self.assertTrue(self.pBDB.bibs.updateInfoFromOAI("1385583"))
		self.assertEqual(self.pBDB.bibs.getByBibkey("Gariazzo:2015rra"), expected)

	def test_updateInfoFromOAI(self):
		"""test updateInfoFromOAI, but with mocked methods"""
		dt = datetime.date.today().strftime("%Y-%m-%d")
		mockOut = {'doi': u'10.1088/0954-3899/43/3/033001', 'isbn': None, 'ads': u'2015JPhG...43c3001G', 'pubdate': u'2016-01-13', 'firstdate': u'2015-07-29', 'journal': u'J.Phys.', 'arxiv': u'1507.08204', 'id': '1385583', 'volume': u'G43', 'bibtex': None, 'year': u'2016', 'oldkeys': '', 'bibkey': u'Gariazzo:2015rra', 'pages': u'033001'}
		self.assertFalse(self.pBDB.bibs.updateInfoFromOAI(False))
		self.assertFalse(self.pBDB.bibs.updateInfoFromOAI(""))
		self.assertFalse(self.pBDB.bibs.updateInfoFromOAI(None))
		with patch('physbiblio.database.entries.getField', side_effect = ["abcd", False, "12345"]) as mock:
			self.assertFalse(self.pBDB.bibs.updateInfoFromOAI("abc"))
			self.assertFalse(self.pBDB.bibs.updateInfoFromOAI("abc"))

			self.assertEqual(self.pBDB.bibs.getByBibkey("Gariazzo:2015rra"), [])
			with patch('physbiblio.webimport.inspireoai.webSearch.retrieveOAIData', side_effect=[
					False,
					mockOut, mockOut, mockOut,
					{'doi': u'10.1088/0954-3899/43/3/033001', 'isbn': None, 'ads': u'2015JPhG...43c3001G', 'pubdate': u'2016-01-13', 'firstdate': u'2015-07-29', 'journal': u'J.Phys.', 'arxiv': u'1507.08204', 'id': '1385583', 'volume': u'G43', 'bibtex': '@Article{Gariazzo:2015rra,\nauthor="Gariazzo",\ntitle="{Light Sterile Neutrinos}"\n}', 'year': u'2016', 'oldkeys': '', 'bibkey': u'Gariazzo:2015rra', 'pages': u'033001'},
					{'doi': u'10.1088/0954-3899/43/3/033001', 'isbn': None, }, {'doi': u'10.1088/0954-3899/43/3/033001', 'isbn': None, },
					{'doi': u'10.1088/0954-3899/43/3/033001', 'bibkey': "Gariazzo:2015rra", }, {'doi': u'10.1088/0954-3899/43/3/033001', 'bibkey': "Gariazzo:2015rra", },
					]) as mock_function:
				self.assertFalse(self.pBDB.bibs.updateInfoFromOAI("abc", verbose = 2))
				mock_function.assert_called_once_with("12345", bibtex = None, readConferenceTitle=False, verbose = 2)
				self.assertTrue(self.pBDB.bibs.updateInfoFromOAI("12345", verbose = 2))
				mock_function.reset_mock()
				self.assert_in_stdout(lambda: self.pBDB.bibs.updateInfoFromOAI("12345", verbose = 2),
					"Inspire OAI info for 12345 saved.")
				mock_function.assert_called_once_with("12345", bibtex = None, readConferenceTitle=False, verbose = 2)
				self.assertEqual(self.pBDB.bibs.getByBibkey("Gariazzo:2015rra"), [])
				self.pBDB.bibs.insertFromBibtex(u'@article{Gariazzo:2015rra,\narxiv="1507.08204"\n}')
				self.assertEqual(self.pBDB.bibs.getByBibkey("Gariazzo:2015rra"),
					[{'bibkey': 'Gariazzo:2015rra', 'inspire': None, 'arxiv': '1507.08204', 'ads': None, 'scholar': None, 'doi': None, 'isbn': None, 'year': 2015, 'link': 'http://arxiv.org/abs/1507.08204', 'comments': None, 'old_keys': None, 'crossref': None, 'bibtex': '@Article{Gariazzo:2015rra,\n         arxiv = "1507.08204",\n}', 'firstdate': dt, 'pubdate': '', 'exp_paper': 0, 'lecture': 0, 'phd_thesis': 0, 'review': 0, 'proceeding': 0, 'book': 0, 'noUpdate': 0, 'marks': '', 'abstract': None, 'bibtexDict': {'arxiv': '1507.08204', 'ENTRYTYPE': 'article', 'ID': 'Gariazzo:2015rra'}, 'title': '', 'journal': '', 'volume': '', 'number': '', 'pages': '', 'published': '  (2015) ', 'author': ''}])
				mock_function.reset_mock()
				self.assert_in_stdout(lambda: self.pBDB.bibs.updateInfoFromOAI("12345", bibtex = u'@article{Gariazzo:2015rra,\narxiv="1507.08204"\n}', verbose = 2),
					"doi = 10.1088/0954-3899/43/3/033001 (None)")
				mock_function.assert_called_once_with("12345", bibtex =  u'@article{Gariazzo:2015rra,\narxiv="1507.08204"\n}', readConferenceTitle=False, verbose = 2)
				self.assertEqual(self.pBDB.bibs.getByBibkey("Gariazzo:2015rra"),
					[{'bibkey': 'Gariazzo:2015rra', 'inspire': '1385583', 'arxiv': '1507.08204', 'ads': '2015JPhG...43c3001G', 'scholar': None, 'doi': '10.1088/0954-3899/43/3/033001', 'isbn': None, 'year': 2016, 'link': 'http://arxiv.org/abs/1507.08204', 'comments': None, 'old_keys': '', 'crossref': None, 'bibtex': '@Article{Gariazzo:2015rra,\n         arxiv = "1507.08204",\n}', 'firstdate': '2015-07-29', 'pubdate': '2016-01-13', 'exp_paper': 0, 'lecture': 0, 'phd_thesis': 0, 'review': 0, 'proceeding': 0, 'book': 0, 'noUpdate': 0, 'marks': '', 'abstract': None, 'bibtexDict': {'arxiv': '1507.08204', 'ENTRYTYPE': 'article', 'ID': 'Gariazzo:2015rra'}, 'title': '', 'journal': '', 'volume': '', 'number': '', 'pages': '', 'published': '  (2016) ', 'author': ''}])
				self.assertTrue(self.pBDB.bibs.updateInfoFromOAI("12345"))
				self.assertEqual(self.pBDB.bibs.getByBibkey("Gariazzo:2015rra"),
					[{'bibkey': 'Gariazzo:2015rra', 'inspire': '1385583', 'arxiv': '1507.08204', 'ads': '2015JPhG...43c3001G', 'scholar': None, 'doi': '10.1088/0954-3899/43/3/033001', 'isbn': None, 'year': 2016, 'link': 'http://arxiv.org/abs/1507.08204', 'comments': None, 'old_keys': '', 'crossref': None, 'bibtex': '@Article{Gariazzo:2015rra,\n        author = "Gariazzo",\n         title = "{Light Sterile Neutrinos}",\n}', 'firstdate': '2015-07-29', 'pubdate': '2016-01-13', 'exp_paper': 0, 'lecture': 0, 'phd_thesis': 0, 'review': 0, 'proceeding': 0, 'book': 0, 'noUpdate': 0, 'marks': '', 'abstract': None, 'bibtexDict': {'ENTRYTYPE': 'article', 'ID': 'Gariazzo:2015rra', 'author': 'Gariazzo', 'title': '{Light Sterile Neutrinos}'}, 'title': '{Light Sterile Neutrinos}', 'journal': '', 'volume': '', 'number': '', 'pages': '', 'published': '  (2016) ', 'author': 'Gariazzo'}])
				self.assertFalse(self.pBDB.bibs.updateInfoFromOAI("12345"))
				self.assert_in_stdout(lambda: self.pBDB.bibs.updateInfoFromOAI("12345"),
					"Something missing in entry")
				self.assertTrue(self.pBDB.bibs.updateInfoFromOAI("12345"))
				self.assert_in_stdout(lambda: self.pBDB.bibs.updateInfoFromOAI("12345"),
					"Key error")

	@unittest.skipIf(skipOnlineTests, "Online tests")
	def test_updateFromOAI_online(self):
		"""test updateFromOAI with online connection"""
		expected = [fullRecordGariazzo]
		self.pBDB.bibs.insertFromBibtex(u'@article{Gariazzo:2015rra,\narxiv="1507.08204"\n}')
		self.assertTrue(self.pBDB.bibs.updateFromOAI("Gariazzo:2015rra"))
		self.assertEqual(self.pBDB.bibs.getByBibkey("Gariazzo:2015rra"), expected)
		self.pBDB.undo(verbose = 0)
		self.pBDB.bibs.insert(self.pBDB.bibs.prepareInsert(u'@article{Gariazzo:2015rra,\narxiv="1507.08204"\n}', inspire = "1385583"))
		self.assertTrue(self.pBDB.bibs.updateFromOAI("1385583"))
		self.assertEqual(self.pBDB.bibs.getByBibkey("Gariazzo:2015rra"), expected)

	def test_updateFromOAI(self):
		"""test updateFromOAI without relying on the true pBDB.bibs.updateInfoFromOAI (mocked)"""
		self.pBDB.bibs.insert(self.pBDB.bibs.prepareInsert(u'@article{abc,\narxiv="1234.56789"\n}', inspire = "12345"))
		with patch('physbiblio.database.entries.updateInfoFromOAI', autospec = True,
				side_effect = ["a", "b", "c", "d", "e", "f"]) as mock_function:
			with patch('physbiblio.database.entries.updateInspireID', side_effect = ["54321", False]) as _updateid:
				self.assertEqual(self.pBDB.bibs.updateFromOAI("abc"), "a")
				mock_function.assert_called_once_with(self.pBDB.bibs, "12345", verbose = 0)
				mock_function.reset_mock()
				self.assertEqual(self.pBDB.bibs.updateFromOAI("1234"), "b")
				mock_function.assert_called_once_with(self.pBDB.bibs, "1234", verbose = 0)
				mock_function.reset_mock()
				self.assertEqual(self.pBDB.bibs.updateFromOAI(["abc", "1234"]), ["c", "d"])
				self.assertEqual(mock_function.call_count, 2)
				mock_function.assert_called_with(self.pBDB.bibs, "1234", verbose = 0)
				mock_function.reset_mock()
				self.pBDB.bibs.insertFromBibtex(u'@article{def,\narxiv="1234.56789"\n}')
				self.assertEqual(self.pBDB.bibs.updateFromOAI("def", verbose = 1), "e")
				mock_function.assert_called_once_with(self.pBDB.bibs, "54321", verbose = 1)
				mock_function.reset_mock()
				self.assertEqual(self.pBDB.bibs.updateFromOAI("abcdef"), "f")
				mock_function.assert_called_once_with(self.pBDB.bibs, False, verbose = 0)

	def test_getDailyInfoFromOAI(self):
		"""test the function getDailyInfoFromOAI, without relying on the true physBiblioWeb.webSearch["inspireoai"].retrieveOAIUpdates (mocked)"""
		self.maxDiff = None
		self.pBDB.bibs.insertFromBibtex(u'@article{Gariazzo:2015rra,\narxiv="1507.08204"\n}')
		self.pBDB.bibs.insertFromBibtex(u'@article{Ade:2013zuv,\narxiv="1303.5076"\n}')
		d1 = "2018-01-01"
		d2 = "2018-01-02"
		d1t = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
		d2t = datetime.date.today().strftime("%Y-%m-%d")
		self.assertEqual(self.pBDB.bibs.getByBibkey("Ade:2013zuv"),
			[{'bibkey': 'Ade:2013zuv', 'inspire': None, 'arxiv': '1303.5076', 'ads': None, 'scholar': None, 'doi': None, 'isbn': None, 'year': 2013, 'link': 'http://arxiv.org/abs/1303.5076', 'comments': None, 'old_keys': None, 'crossref': None, 'bibtex': '@Article{Ade:2013zuv,\n         arxiv = "1303.5076",\n}', 'firstdate': d2t, 'pubdate': '', 'exp_paper': 0, 'lecture': 0, 'phd_thesis': 0, 'review': 0, 'proceeding': 0, 'book': 0, 'noUpdate': 0, 'marks': '', 'abstract': None, 'bibtexDict': {'arxiv': '1303.5076', 'ENTRYTYPE': 'article', 'ID': 'Ade:2013zuv'}, 'title': '', 'journal': '', 'volume': '', 'number': '', 'pages': '', 'published': '  (2013) ', 'author': ''}])
		self.assertEqual(self.pBDB.bibs.getByBibkey("Gariazzo:2015rra"),
			[{'bibkey': 'Gariazzo:2015rra', 'inspire': None, 'arxiv': '1507.08204', 'ads': None, 'scholar': None, 'doi': None, 'isbn': None, 'year': 2015, 'link': 'http://arxiv.org/abs/1507.08204', 'comments': None, 'old_keys': None, 'crossref': None, 'bibtex': '@Article{Gariazzo:2015rra,\n         arxiv = "1507.08204",\n}', 'firstdate': d2t, 'pubdate': '', 'exp_paper': 0, 'lecture': 0, 'phd_thesis': 0, 'review': 0, 'proceeding': 0, 'book': 0, 'noUpdate': 0, 'marks': '', 'abstract': None, 'bibtexDict': {'arxiv': '1507.08204', 'ENTRYTYPE': 'article', 'ID': 'Gariazzo:2015rra'}, 'title': '', 'journal': '', 'volume': '', 'number': '', 'pages': '', 'published': '  (2015) ', 'author': ''}])
		with patch('physbiblio.webimport.inspireoai.webSearch.retrieveOAIUpdates',
				side_effect=[[], [], [], [],
				[{'doi': u'10.1088/0954-3899/43/3/033001', 'isbn': None, 'ads': u'2015JPhG...43c3001G', 'pubdate': u'2016-01-13', 'firstdate': u'2015-07-29', 'journal': u'J.Phys.', 'arxiv': u'1507.08204', 'id': '1385583', 'volume': u'G43', 'bibtex': None, 'year': u'2016', 'oldkeys': '', 'bibkey': u'Gariazzo:2015rra', 'pages': u'033001'}]
				]) as _mock:
			self.assert_in_stdout(lambda: self.pBDB.bibs.getDailyInfoFromOAI(),
				"Calling INSPIRE-HEP OAI harvester between dates %s and %s"%(d1t, d2t))
			self.assert_in_stdout(lambda: self.pBDB.bibs.getDailyInfoFromOAI(d1, d2),
				"Calling INSPIRE-HEP OAI harvester between dates %s and %s"%(d1, d2))
			self.assert_in_stdout(lambda: self.pBDB.bibs.getDailyInfoFromOAI(date2 = d2),
				"Calling INSPIRE-HEP OAI harvester between dates %s and %s"%(d1t, d2))
			self.assert_in_stdout(lambda: self.pBDB.bibs.getDailyInfoFromOAI(date1 = d1),
				"Calling INSPIRE-HEP OAI harvester between dates %s and %s"%(d1, d2t))
			self.pBDB.bibs.getDailyInfoFromOAI(date1 = d1)
			self.assertEqual(self.pBDB.bibs.getByBibkey("Ade:2013zuv"),
				[{'bibkey': 'Ade:2013zuv', 'inspire': None, 'arxiv': '1303.5076', 'ads': None, 'scholar': None, 'doi': None, 'isbn': None, 'year': 2013, 'link': 'http://arxiv.org/abs/1303.5076', 'comments': None, 'old_keys': None, 'crossref': None, 'bibtex': '@Article{Ade:2013zuv,\n         arxiv = "1303.5076",\n}', 'firstdate': d2t, 'pubdate': '', 'exp_paper': 0, 'lecture': 0, 'phd_thesis': 0, 'review': 0, 'proceeding': 0, 'book': 0, 'noUpdate': 0, 'marks': '', 'abstract': None, 'bibtexDict': {'arxiv': '1303.5076', 'ENTRYTYPE': 'article', 'ID': 'Ade:2013zuv'}, 'title': '', 'journal': '', 'volume': '', 'number': '', 'pages': '', 'published': '  (2013) ', 'author': ''}])
			self.assertEqual(self.pBDB.bibs.getByBibkey("Gariazzo:2015rra"),
				[{'bibkey': 'Gariazzo:2015rra', 'inspire': '1385583', 'arxiv': '1507.08204', 'ads': '2015JPhG...43c3001G', 'scholar': None, 'doi': '10.1088/0954-3899/43/3/033001', 'isbn': None, 'year': '2016', 'link': 'http://arxiv.org/abs/1507.08204', 'comments': None, 'old_keys': '', 'crossref': None, 'bibtex': '@Article{Gariazzo:2015rra,\n       journal = "J.Phys.",\n        volume = "G43",\n          year = "2016",\n         pages = "033001",\n           doi = "10.1088/0954-3899/43/3/033001",\n         arxiv = "1507.08204",\n}', 'firstdate': '2015-07-29', 'pubdate': '2016-01-13', 'exp_paper': 0, 'lecture': 0, 'phd_thesis': 0, 'review': 0, 'proceeding': 0, 'book': 0, 'noUpdate': 0, 'marks': '', 'abstract': None, 'bibtexDict': {'arxiv': '1507.08204', 'doi': '10.1088/0954-3899/43/3/033001', 'pages': '033001', 'year': '2016', 'volume': 'G43', 'journal': 'J.Phys.', 'ENTRYTYPE': 'article', 'ID': 'Gariazzo:2015rra'}, 'title': '', 'journal': 'J.Phys.', 'volume': 'G43', 'number': '', 'pages': '033001', 'published': 'J.Phys. G43 (2016) 033001', 'author': ''}])
		self.pBDB.undo(verbose = 0)
		self.pBDB.bibs.insertFromBibtex(u'@article{Gariazzo:2015rra,\narxiv="1507.08204"\n}')
		self.pBDB.bibs.insertFromBibtex(u'@article{Ade:2013zuv,\narxiv="1303.5076"\n}')
		self.pBDB.bibs.setNoUpdate("Ade:2013zuv")
		d1 = "2018-01-01"
		d2 = "2018-01-02"
		self.assertEqual(self.pBDB.bibs.getByBibkey("Ade:2013zuv"),
			[{'bibkey': 'Ade:2013zuv', 'inspire': None, 'arxiv': '1303.5076', 'ads': None, 'scholar': None, 'doi': None, 'isbn': None, 'year': 2013, 'link': 'http://arxiv.org/abs/1303.5076', 'comments': None, 'old_keys': None, 'crossref': None, 'bibtex': '@Article{Ade:2013zuv,\n         arxiv = "1303.5076",\n}', 'firstdate': d2t, 'pubdate': '', 'exp_paper': 0, 'lecture': 0, 'phd_thesis': 0, 'review': 0, 'proceeding': 0, 'book': 0, 'noUpdate': 1, 'marks': '', 'abstract': None, 'bibtexDict': {'arxiv': '1303.5076', 'ENTRYTYPE': 'article', 'ID': 'Ade:2013zuv'}, 'title': '', 'journal': '', 'volume': '', 'number': '', 'pages': '', 'published': '  (2013) ', 'author': ''}])
		self.assertEqual(self.pBDB.bibs.getByBibkey("Gariazzo:2015rra"),
			[{'bibkey': 'Gariazzo:2015rra', 'inspire': None, 'arxiv': '1507.08204', 'ads': None, 'scholar': None, 'doi': None, 'isbn': None, 'year': 2015, 'link': 'http://arxiv.org/abs/1507.08204', 'comments': None, 'old_keys': None, 'crossref': None, 'bibtex': '@Article{Gariazzo:2015rra,\n         arxiv = "1507.08204",\n}', 'firstdate': d2t, 'pubdate': '', 'exp_paper': 0, 'lecture': 0, 'phd_thesis': 0, 'review': 0, 'proceeding': 0, 'book': 0, 'noUpdate': 0, 'marks': '', 'abstract': None, 'bibtexDict': {'arxiv': '1507.08204', 'ENTRYTYPE': 'article', 'ID': 'Gariazzo:2015rra'}, 'title': '', 'journal': '', 'volume': '', 'number': '', 'pages': '', 'published': '  (2015) ', 'author': ''}])
		with patch('physbiblio.webimport.inspireoai.webSearch.retrieveOAIUpdates',
				side_effect=[
				[{'doi': u'10.1088/0954-3899/43/3/033001', 'isbn': None, 'ads': u'2015JPhG...43c3001G', 'pubdate': u'2016-01-13', 'firstdate': u'2015-07-29', 'journal': u'J.Phys.', 'arxiv': u'1507.08204', 'id': '1385583', 'volume': u'G43', 'bibtex': None, 'year': u'2016', 'oldkeys': '', 'bibkey': u'Gariazzo:2015rra', 'pages': u'033001'}]
				]) as _mock:
			self.assert_in_stdout(lambda: self.pBDB.bibs.getDailyInfoFromOAI(d1, d2),
				"Calling INSPIRE-HEP OAI harvester between dates %s and %s"%(d1, d2))
			self.assertEqual(self.pBDB.bibs.getByBibkey("Ade:2013zuv"),
				[{'bibkey': 'Ade:2013zuv', 'inspire': None, 'arxiv': '1303.5076', 'ads': None, 'scholar': None, 'doi': None, 'isbn': None, 'year': 2013, 'link': 'http://arxiv.org/abs/1303.5076', 'comments': None, 'old_keys': None, 'crossref': None, 'bibtex': '@Article{Ade:2013zuv,\n         arxiv = "1303.5076",\n}', 'firstdate': d2t, 'pubdate': '', 'exp_paper': 0, 'lecture': 0, 'phd_thesis': 0, 'review': 0, 'proceeding': 0, 'book': 0, 'noUpdate': 1, 'marks': '', 'abstract': None, 'bibtexDict': {'arxiv': '1303.5076', 'ENTRYTYPE': 'article', 'ID': 'Ade:2013zuv'}, 'title': '', 'journal': '', 'volume': '', 'number': '', 'pages': '', 'published': '  (2013) ', 'author': ''}])
			self.assertEqual(self.pBDB.bibs.getByBibkey("Gariazzo:2015rra"),
				[{'bibkey': 'Gariazzo:2015rra', 'inspire': '1385583', 'arxiv': '1507.08204', 'ads': '2015JPhG...43c3001G', 'scholar': None, 'doi': '10.1088/0954-3899/43/3/033001', 'isbn': None, 'year': '2016', 'link': 'http://arxiv.org/abs/1507.08204', 'comments': None, 'old_keys': '', 'crossref': None, 'bibtex': '@Article{Gariazzo:2015rra,\n       journal = "J.Phys.",\n        volume = "G43",\n          year = "2016",\n         pages = "033001",\n           doi = "10.1088/0954-3899/43/3/033001",\n         arxiv = "1507.08204",\n}', 'firstdate': '2015-07-29', 'pubdate': '2016-01-13', 'exp_paper': 0, 'lecture': 0, 'phd_thesis': 0, 'review': 0, 'proceeding': 0, 'book': 0, 'noUpdate': 0, 'marks': '', 'abstract': None, 'bibtexDict': {'arxiv': '1507.08204', 'doi': '10.1088/0954-3899/43/3/033001', 'pages': '033001', 'year': '2016', 'volume': 'G43', 'journal': 'J.Phys.', 'ENTRYTYPE': 'article', 'ID': 'Gariazzo:2015rra'}, 'title': '', 'journal': 'J.Phys.', 'volume': 'G43', 'number': '', 'pages': '033001', 'published': 'J.Phys. G43 (2016) 033001', 'author': ''}])

@unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseUtilities(DBTestCase):
	"""Tests for the methods in the utilities subclass"""
	def test_spare(self):
		"""create spare connections just to delete them with cleanSpareEntries"""
		self.pBDB.utils.cleanSpareEntries()
		self.assertTrue(self.pBDB.catBib.insert(1, "test"))
		self.assertEqual(self.pBDB.catExp.insert(1, [0, 1]), None)
		self.pBDB.exps.insert({"name": "testExp", "comments": "", "homepage":"", "inspire": "1"})
		self.assertTrue(self.pBDB.bibExp.insert("test", 1))
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats,
			{"bibs": 0, "cats": 2, "exps": 1, "catBib": 1, "catExp": 2, "bibExp": 1})
		self.assert_stdout(self.pBDB.utils.cleanSpareEntries,
			'Cleaning (test, 1)\nCleaning (1, test)\nCleaning (1, 0)\n')
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats,
			{"bibs": 0, "cats": 2, "exps": 1, "catBib": 0, "catExp": 1, "bibExp": 0})

	def test_bibtexs(self):
		"""Create and clean a bibtex entry"""
		data = self.pBDB.bibs.prepareInsert(u'\n\n%comment\n@article{abc,\nauthor = "me",\ntitle = "\u00E8\n\u00F1",}', bibkey = "abc")
		self.assertTrue(self.pBDB.bibs.insert(data))
		self.assertEqual(self.pBDB.utils.cleanAllBibtexs(), None)
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibtex"),
			u'@Article{abc,\n        author = "me",\n         title = "{{\`e} {\~n}}",\n}\n\n')
		self.pBDB.bibs.delete("abc")

def tearDownModule():
	if os.path.exists(tempDBName):
		os.remove(tempDBName)

if __name__=='__main__':
	unittest.main()
