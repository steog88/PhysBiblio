#!/usr/bin/env python
"""
Test file for the physbiblio.database module.

This file is part of the PhysBiblio package.
"""
import sys, traceback

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
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseMain(myTestCase):#using cats just for simplicity
	def test_operations(self):
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

	def test_literal_eval(self):
		self.assertEqual(self.pBDB.cats.literal_eval("[1,2]"), [1,2])
		self.assertEqual(self.pBDB.cats.literal_eval("['test','a']"), ["test","a"])
		self.assertEqual(self.pBDB.cats.literal_eval("'test b'"), "'test b'")
		self.assertEqual(self.pBDB.cats.literal_eval("test c"), "test c")
		self.assertEqual(self.pBDB.cats.literal_eval("\"test d\""), '"test d"')
		self.assertEqual(self.pBDB.cats.literal_eval("[test e"), "[test e")
		self.assertEqual(self.pBDB.cats.literal_eval("[test f]"), None)
		self.assertEqual(self.pBDB.cats.literal_eval("'test g','test h'"), ["test g", "test h"])

@unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseLinks(myTestCase):
	def test_catEntries(self):
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
class TestDatabaseExperiments(myTestCase):
	def test_new(self):
		pass

@unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseCategories(myTestCase):
	def test_new(self):
		pass

@unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseEntries(myTestCase):
	def test_new(self):
		pass

@unittest.skipIf(skipDBTests, "Database tests")
class TestDatabaseUtilities(myTestCase):
	def test_new(self):
		pass

if __name__=='__main__':
	print("\nStarting tests...\n")
	unittest.main()
