#!/usr/bin/env python
"""
Test file for the physbiblio.database module.

This file is part of the PhysBiblio package.
"""
import sys, traceback
import six

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import MagicMock, patch, call
	from StringIO import StringIO
else:
	import unittest
	from unittest.mock import MagicMock, patch, call
	from io import StringIO

try:
	from physbiblio.setuptests import *
	from physbiblio.errors import pBErrorManager
	from physbiblio.config import pbConfig
	from physbiblio.database import dbStats, catString, cats_alphabetical
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

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
		self.assertEqual(len(self.pBDB.exps.getAll()), number)

	@patch('sys.stdout', new_callable=StringIO)
	def assert_stdout(self, function, expected_output, mock_stdout):
		"""Catch and test stdout of the function"""
		function()
		self.assertEqual(mock_stdout.getvalue(), expected_output)

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
		self.assertTrue(self.pBDB.bibs.insert(data))
		self.assertTrue(self.pBDB.exps.insert({"name": "exp1", "comments": "", "homepage": "", "inspire": ""}))
		self.assertTrue(self.pBDB.catExp.insert(0, 1))
		self.assertTrue(self.pBDB.bibExp.insert("abc", 1))
		self.assertEqual(self.pBDB.exps.getByEntry("def"), [])
		self.assertEqual([dict(e) for e in self.pBDB.exps.getByEntry("abc")],
			[{'inspire': u'', 'comments': u'', 'name': u'exp1', 'bibkey': u'abc', 'idEnEx': 1, 'homepage': u'', 'idExp': 1}])
		self.assertEqual(self.pBDB.exps.getByCat("1"), [])
		self.assertEqual([dict(e) for e in self.pBDB.exps.getByCat(0)],
			[{'idCat': 0, 'inspire': u'', 'comments': u'', 'name': u'exp1', 'idExC': 1, 'homepage': u'', 'idExp': 1}])

@unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseCategories(DBTestCase):
	"""Tests for the methods in the categories subclass"""
	def checkNumberCategories(self, number):
		"""Check the number of experiments"""
		self.assertEqual(len(self.pBDB.cats.getAll()), number)

	@patch('sys.stdout', new_callable=StringIO)
	def assert_stdout(self, function, expected_output, mock_stdout):
		"""Catch and test stdout of the function"""
		function()
		self.assertEqual(mock_stdout.getvalue(), expected_output)

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
		self.assert_stdout(lambda: self.pBDB.cats.delete(0), "[DB] Error: should not delete the category with id: 0.\n")
		self.checkNumberCategories(2)
		self.assert_stdout(lambda: self.pBDB.cats.delete(1), "[DB] Error: should not delete the category with id: 1.\n")
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

	def test_catString(self):
		"""Test catString with existing and non existing records"""
		self.assertEqual(catString(1, self.pBDB), "   1: Tags")
		self.assertEqual(catString(1, self.pBDB, True), "   1: Tags - <i>Use this category to store tags (such as: ongoing projects, temporary cats,...)</i>")
		self.assertEqual(catString(2, self.pBDB), "")
		self.assert_stdout(lambda: catString(2, self.pBDB),
			"[DB][catString] category '2' not in database\n\n")

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
			"[DB][cats_alphabetical] category '5' not in database\n\n")

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

# @unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseEntries(DBTestCase):
	"""Tests for the methods in the entries subclass"""
	@patch('sys.stdout', new_callable=StringIO)
	def assert_stdout(self, function, expected_output, mock_stdout):
		"""Catch and test stdout of the function"""
		function()
		self.assertEqual(mock_stdout.getvalue(), expected_output)

	@patch('sys.stdout', new_callable=StringIO)
	def assert_in_stdout(self, function, expected_output, mock_stdout):
		"""Catch and if test stdout of the function contains a string"""
		function()
		self.assertIn(expected_output, mock_stdout.getvalue())

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
		pass

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
			"[DB] updating 'inspire' for entry 'def'\n")
		self.assertEqual(self.pBDB.bibs.getByBibkey("def")[0]["inspire"], '1234')
		self.assertFalse(self.pBDB.bibs.updateField("def", "inspires", "1234", verbose = 0))
		self.assertFalse(self.pBDB.bibs.updateField("def", "inspire", None, verbose = 0))
		self.assert_stdout(lambda: self.pBDB.bibs.updateField("def", "inspires", "1234"),
			"[DB] updating 'inspires' for entry 'def'\n")
		self.assert_stdout(lambda: self.pBDB.bibs.updateField("def", "inspires", "1234", verbose = 2),
			"[DB] updating 'inspires' for entry 'def'\n[DB] non-existing field or unappropriated value: (def, inspires, 1234)\n")

	def test_prepareUpdate(self):
		# prepareUpdateByKey
		# prepareUpdateByBibtex
		# prepareUpdate
		pass

	def test_replace(self):
		# replace
		# replaceInBibtex
		pass

	def test_completeFetched(self):
		pass

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
		pass

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
		self.assertEqual(self.pBDB.bibs.lastQuery,
			"select * from entries  where bibkey = ?  and arxiv = ?  order by firstdate ASC")
		self.assertEqual(self.pBDB.bibs.lastVals, ("abc", "def"))
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(
			params = {"bibkey": "abc", "arxiv": "def"}, connection = "or")],
			["abc", "def"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchAll(
			params = {"bibkey": "abc", "arxiv": "def"}, connection = "or").lastFetched],
			["abc", "def"])
		self.assertEqual(self.pBDB.bibs.lastQuery,
			"select * from entries  where bibkey = ?  or arxiv = ?  order by firstdate ASC")
		self.assertEqual(self.pBDB.bibs.lastVals, ("abc", "def"))
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(
			params = {"bibkey": "ab", "arxiv": "ef"}, connection = "or", operator = "like")],
			["abc", "def"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchAll(
			params = {"bibkey": "ab", "arxiv": "ef"}, connection = "or", operator = "like").lastFetched],
			["abc", "def"])
		self.assertEqual(self.pBDB.bibs.lastQuery,
			"select * from entries  where bibkey like ?  or arxiv like ?  order by firstdate ASC")
		self.assertEqual(self.pBDB.bibs.lastVals, ("%ab%", "%ef%"))

		#test some bad connection or operator
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(
			params = {"bibkey": "abc", "arxiv": "def"}, connection = "o r")],
			[])
		self.assertEqual(self.pBDB.bibs.lastQuery,
			"select * from entries  where bibkey = ?  and arxiv = ?  order by firstdate ASC")
		self.assertEqual(self.pBDB.bibs.lastVals, ("abc", "def"))
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.fetchAll(
			params = {"bibkey": "ab", "arxiv": "ef"}, connection = "or", operator = "lik").lastFetched],
			[])
		self.assertEqual(self.pBDB.bibs.lastQuery,
			"select * from entries  where bibkey = ?  or arxiv = ?  order by firstdate ASC")
		self.assertEqual(self.pBDB.bibs.lastVals, ("ab", "ef"))

		#generate some errors
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(limitTo = "a")], [])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(limitTo = "bibkey")], [])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(limitTo = 1, limitOffset = "a")], [])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(orderBy = "a")], [])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(orderType = "abc")], ["abc", "def", "ghi"])
		self.assertEqual([e["bibkey"] for e in self.pBDB.bibs.getAll(params = {"abc": "bibkey"})], [])

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
			"[DB] ERROR in getEntryField('def', 'isbn'): no element found?\n")
		self.assertFalse(self.pBDB.bibs.getField("abc", "def"))
		self.assert_stdout(lambda: self.pBDB.bibs.getField("abc", "def"),
			"[DB] ERROR in getEntryField('abc', 'def'): the field is missing?\n")

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
		data = self.pBDB.bibs.prepareInsert(u'@article{abc,\nauthor = "me",\ntitle = "abc",}')
		self.assertFalse(self.pBDB.bibs.getArxivUrl("def"))
		self.assertFalse(self.pBDB.bibs.getDoiUrl("def"))

	def test_fetchByCat(self):
		# fetchByCat
		# getByCat
		pass

	def test_fetchByExp(self):
		# fetchByExp
		# getByExp
		pass

	def test_cleanBibtexs(self):
		pass

	def test_printAll(self):
		# printAllBibtexs
		# printAllBibkeys
		# printAllInfo
		pass

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

	def test_importFromBib(self):
		pass

	def test_loadAndInsert(self):
		# loadAndInsert
		# loadAndInsertWithCats
		pass

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

	def test_getFieldsFromArxiv(self):
		pass

	def test_updateInspireID(self):
		pass

	def test_searchOAIUpdates(self):
		pass

	def test_updateInfoFromOAI(self):
		pass

	def test_updateFromOAI(self):
		pass

	def test_getDailyInfoFromOAI(self):
		pass


@unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseUtilities(DBTestCase):
	"""Tests for the methods in the utilities subclass"""

	@patch('sys.stdout', new_callable=StringIO)
	def assert_cleanSpare(self, function, expected_output, mock_stdout):
		"""Catch and test stdout of the function"""
		function()
		self.assertEqual(mock_stdout.getvalue(), expected_output)

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
		self.assert_cleanSpare(self.pBDB.utils.cleanSpareEntries,
			'[DB] cleaning (test, 1)\n[DB] cleaning (1, test)\n[DB] cleaning (1, 0)\n')
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats,
			{"bibs": 0, "cats": 2, "exps": 1, "catBib": 0, "catExp": 1, "bibExp": 0})

	def test_bibtexs(self):
		"""Create and clean a bibtex entry"""
		data = self.pBDB.bibs.prepareInsert(u'\n\n%comment\n@article{abc,\nauthor = "me",\ntitle = "\u00E8\n\u00F1",}', bibkey = "abc")
		self.assertTrue(self.pBDB.bibs.insert(data))
		self.assertEqual(self.pBDB.utils.cleanAllBibtexs(), None)
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibtex"),
			u'@Article{abc,\n        author = "me",\n         title = "{\`{e} \~{n}}",\n}\n\n')
		self.pBDB.bibs.delete("abc")

def tearDownModule():
	if os.path.exists(tempDBName):
		os.remove(tempDBName)

if __name__=='__main__':
	print("\nStarting tests...\n")
	unittest.main()
