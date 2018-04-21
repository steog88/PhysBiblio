#!/usr/bin/env python
"""
Test file for the physbiblio.firstOpen module.

This file is part of the physbiblio package.
"""
import sys, traceback

if sys.version_info[0] < 3:
	import unittest2 as unittest
else:
	import unittest

try:
	from physbiblio.setuptests import *
	from physbiblio.config import pbConfig
	from physbiblio.database import physbiblioDB
	from physbiblio.firstOpen import createTables
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

tempFDBName = os.path.join(pbConfig.dataPath, "tests_first_%s.db"%today_ymd)

@unittest.skipIf(skipLongTests, "Long tests")
class TestFirstOpenMethods(unittest.TestCase):
	"""Tests for methods in physbiblio.firstOpen"""

	def test_createTables(self):
		"""Test that all the tables are created at first time, if DB is empty"""
		if os.path.exists(tempFDBName):
			os.remove(tempFDBName)
		open(tempFDBName, 'a').close()
		self.pBDB = physbiblioDB(tempFDBName, noOpen = True)
		self.pBDB.openDB()

		self.assertTrue(self.pBDB.cursExec("SELECT name FROM sqlite_master WHERE type='table';"))
		self.assertEqual([name[0] for name in self.pBDB.cursor()], [])
		createTables(self.pBDB)
		self.assertTrue(self.pBDB.cursExec("SELECT name FROM sqlite_master WHERE type='table';"))
		self.assertEqual(sorted([name[0] for name in self.pBDB.cursor()]), ["categories", "entries", "entryCats", "entryExps", "expCats", "experiments"])
		self.assertTrue([e["name"] for e in self.pBDB.cats.getAll()], ["Main", "Tags"])

		os.remove(tempFDBName)
		open(tempFDBName, 'a').close()
		self.pBDB = physbiblioDB(tempFDBName)
		self.assertTrue(self.pBDB.cursExec("SELECT name FROM sqlite_master WHERE type='table';"))
		self.assertEqual(sorted([name[0] for name in self.pBDB.cursor()]), ["categories", "entries", "entryCats", "entryExps", "expCats", "experiments"])
		self.assertTrue([e["name"] for e in self.pBDB.cats.getAll()], ["Main", "Tags"])

def tearDownModule():
	if os.path.exists(tempFDBName):
		os.remove(tempFDBName)

if __name__=='__main__':
	unittest.main()
