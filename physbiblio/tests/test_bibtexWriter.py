#!/usr/bin/env python
"""Test file for the physbiblio.bibtexWriter module.

This file is part of the physbiblio package.
"""
import sys, traceback
import bibtexparser

if sys.version_info[0] < 3:
	import unittest2 as unittest
else:
	import unittest

try:
	from physbiblio.setuptests import *
	from physbiblio.config import pbConfig
	from physbiblio.bibtexWriter import pbWriter
except ImportError:
	print("Could not find physbiblio and its modules!")
	raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipTestsSettings.long, "Online tests")
class TestWebImportMethods(unittest.TestCase):
	"""Test the functions that writes bibtexs."""

	def test_bibtexWrite(self):
		"""Test _entry_to_bibtex"""
		basicEntry = {"ID": "test", "ENTRYTYPE": "article",
			"author": "me", "title": "My title"}
		db = bibtexparser.bibdatabase.BibDatabase()
		db.entries = [basicEntry]
		self.assertEqual(pbWriter.write(db).strip(),
			'@Article{test,\n        author = "me",\n         ' \
			+ 'title = "{My title}",\n}')
		entry = dict(basicEntry)
		entry["ENTRYTYPE"] = "proceeding"
		entry["eprint"] = "1721"
		entry["slaccitation"] = "1721"
		entry["title"] = "{my title}"
		db.entries = [entry]
		self.assertEqual(pbWriter.write(db).strip(),
			'@Proceeding{test,\n        author = "me",\n         ' \
			+ 'title = "{my title}",\n        eprint = "1721",\n}')
		entry = dict(basicEntry)
		entry["ENTRYTYPE"] = "custom"
		entry["myfield"] = "abcd"
		entry["journal"] = "JCAP"
		entry["title"] = "{My} title"
		db.entries = [entry]
		self.assertEqual(pbWriter.write(db).strip(),
			'@Custom{test,\n        author = "me",\n         ' \
			+ 'title = "{{My} title}",\n       journal = "JCAP",' \
			+ '\n       myfield = "abcd",\n}')

if __name__=='__main__':
	unittest.main()
