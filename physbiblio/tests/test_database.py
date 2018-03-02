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
		self.assertEqual(len(self.pBDB.cats.getAll()), 3)
		self.assertRaises(AttributeError, lambda: self.pBDB.stats)
		dbStats(self.pBDB)
		self.assertEqual(self.pBDB.stats,
			{"bibs": 0, "cats": 3, "exps": 0, "catBib": 0, "catExp": 0, "bibExp": 0})

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

# @unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseExperiments(DBTestCase):
	"""Tests for the methods in the experiments subclass"""
	def checkNumberExperiments(self, number):
		"""Check the number of experiments"""
		self.assertEqual(len(self.pBDB.exps.getAll()), number)

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

	def test_get(self):
		# getByID
		# getDictByID
		# getAll
		# getByName
		pass
	def filter(self):
		# filterAll
		pass
	def test_print(self):
		# to_str
		# printAll
		# printInCats
		pass
	def test_getByOthers(self):
		# getByEntry
		# getByCat
		pass

@unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseCategories(DBTestCase):
	"""Tests for the methods in the categories subclass"""
	def test_catString(self):
		pass
	def test_cats_alphabetical(self):
		pass
	def test_insert(self):
		pass
	def test_delete(self):
		pass
	def test_update(self):
		pass
		# update
		# updateField
	def test_get(self):
		pass
		# getAll
		# getByID
		# getDictByID
		# getByName
		# getChild
		# getParent
	def test_hierarchy(self):
		pass
		# getHier
		# printHier
	def test_getByOthers(self):
		# getByEntry
		# getByExp
		pass

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

	def test_bibtexs(self):
		"""Create and clean a bibtex entry"""
		data = self.pBDB.bibs.prepareInsert(u'\n\n%comment\n@article{abc,\nauthor = "me",\ntitle = "\u00E8\n\u00F1",}', bibkey = "abc")
		self.assertTrue(self.pBDB.bibs.insert(data))
		self.assertEqual(self.pBDB.utils.cleanAllBibtexs(), None)
		self.assertEqual(self.pBDB.bibs.getField("abc", "bibtex"),
			u'@Article{abc,\n        author = "me",\n         title = "{\`{e} \~{n}}",\n}\n\n')
		self.pBDB.bibs.delete("abc")

def tearDownModule():
	os.remove(tempDBName)

if __name__=='__main__':
	print("\nStarting tests...\n")
	unittest.main()
