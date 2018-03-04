#!/usr/bin/env python
"""
Test file for the physbiblio.database module.

This file is part of the PhysBiblio package.
"""
import sys, traceback

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
		self.pBDB.undo()

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
		with patch('__builtin__.raw_input', return_value='[1,2]') as _raw_input:
			self.pBDB.catBib.askCats("test1")
			_raw_input.assert_called_once_with("categories for 'test1': ")
		with patch('__builtin__.raw_input', return_value='1,2') as _raw_input:
			self.pBDB.catBib.askCats("test1")
			_raw_input.assert_called_once_with("categories for 'test1': ")
		with patch('__builtin__.raw_input', return_value='test2') as _raw_input:
			self.pBDB.catBib.askKeys([1,2])
			_raw_input.assert_has_calls([call("entries for '1': "), call("entries for '2': ")])
		self.assertEqual([tuple(a) for a in self.pBDB.catBib.getAll()],
			[(1,"test1",1), (2,"test1",2), (3,"test2",1), (4,"test2",2)])
		self.assertTrue(self.pBDB.catBib.insert("test", "test"))
		self.pBDB.undo()

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
		with patch('__builtin__.raw_input', return_value='[1,2]') as _raw_input:
			self.pBDB.catExp.askCats(10)
			_raw_input.assert_called_once_with("categories for '10': ")
		with patch('__builtin__.raw_input', return_value='11') as _raw_input:
			self.pBDB.catExp.askExps([1,2])
			_raw_input.assert_has_calls([call("experiments for '1': "), call("experiments for '2': ")])
		self.assertEqual([tuple(a) for a in self.pBDB.catExp.getAll()],
			[(1, 10, 1), (2, 10, 2), (3, 11, 1), (4, 11, 2)])
		self.assertTrue(self.pBDB.catExp.insert("test", "test"))
		self.pBDB.undo()

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
		with patch('__builtin__.raw_input', return_value='[1,2]') as _raw_input:
			self.pBDB.bibExp.askExps("test1")
			_raw_input.assert_called_once_with("experiments for 'test1': ")
		with patch('__builtin__.raw_input', return_value='1,2') as _raw_input:
			self.pBDB.bibExp.askExps("test1")
			_raw_input.assert_called_once_with("experiments for 'test1': ")
		with patch('__builtin__.raw_input', return_value='test2') as _raw_input:
			self.pBDB.bibExp.askKeys([1,2])
			_raw_input.assert_has_calls([call("entries for '1': "), call("entries for '2': ")])
		self.assertEqual([tuple(a) for a in self.pBDB.bibExp.getAll()],
			[(1,"test1",1), (2,"test1",2), (3,"test2",1), (4,"test2",2)])
		self.assertTrue(self.pBDB.bibExp.insert("test", "test"))
		self.pBDB.undo()

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
		self.assertFalse(self.pBDB.exps.updateField(1, "inspire", ""))
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
		self.pBDB.undo()

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
		self.pBDB.undo()

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
		self.pBDB.undo()

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
		self.pBDB.undo()

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
		self.pBDB.undo()

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
		self.assertFalse(self.pBDB.cats.updateField(1, "parentCat", ""))
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
		self.pBDB.undo()

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
		self.pBDB.undo()

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
		self.pBDB.undo()

	def test_catString(self):
		"""Test catString with existing and non existing records"""
		self.assertEqual(catString(1, self.pBDB), "   1: Tags")
		self.assertEqual(catString(1, self.pBDB, True), "   1: Tags - <i>Use this category to store tags (such as: ongoing projects, temporary cats,...)</i>")
		self.assertEqual(catString(2, self.pBDB), "")
		self.assert_stdout(lambda: catString(2, self.pBDB),
			"[DB][catString] category '2' not in database\n\n")
		self.pBDB.undo()

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
		self.pBDB.undo()

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
		self.pBDB.undo()

@unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseEntries(DBTestCase):
	"""Tests for the methods in the entries subclass"""
	def test_new(self):
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
		self.pBDB.undo()

	def test_bibtexs(self):
		"""Create and clean a bibtex entry"""
		data = self.pBDB.bibs.prepareInsert(u'\n\n%comment\n@article{abc,\nauthor = "me",\ntitle = "\u00E8\n\u00F1",}', bibkey = "abc")
		self.assertTrue(self.pBDB.bibs.insert(data))
		self.assertEqual(self.pBDB.utils.cleanAllBibtexs(), None)
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibtex"),
			u'@Article{abc,\n        author = "me",\n         title = "{\`{e} \~{n}}",\n}\n\n')
		self.pBDB.bibs.delete("abc")
		self.pBDB.undo()

def tearDownModule():
	if os.path.exists(tempDBName):
		os.remove(tempDBName)

if __name__=='__main__':
	print("\nStarting tests...\n")
	unittest.main()
