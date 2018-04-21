#!/usr/bin/env python
"""
Test file for the physbiblio.export module.

This file is part of the physbiblio package.
"""
import sys, traceback, os
from stat import S_IREAD, S_IRGRP, S_IROTH

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch
else:
	import unittest
	from unittest.mock import patch

try:
	from physbiblio.setuptests import *
	from physbiblio.config import pbConfig
	from physbiblio.database import pBDB
	from physbiblio.export import pBExport
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipLongTests, "Long tests")
class TestExportMethods(unittest.TestCase):
	"""Tests for methods in physbiblio.export"""
	def test_backup(self):
		"""Test backup file creation and related"""
		emptyFileName = os.path.join(pbConfig.dataPath, "tests_%s.bib"%today_ymd)
		if os.path.exists(emptyFileName): os.remove(emptyFileName)
		if os.path.exists(emptyFileName + pBExport.backupExtension): os.remove(emptyFileName + pBExport.backupExtension)
		self.assertFalse(pBExport.backupCopy(emptyFileName))
		self.assertFalse(os.path.exists(emptyFileName))
		self.assertFalse(os.path.exists(emptyFileName + pBExport.backupExtension))
		open(emptyFileName, 'a').close()
		self.assertTrue(pBExport.backupCopy(emptyFileName))
		self.assertTrue(os.path.exists(emptyFileName + pBExport.backupExtension))
		os.remove(emptyFileName)
		self.assertFalse(os.path.exists(emptyFileName))
		self.assertTrue(pBExport.restoreBackupCopy(emptyFileName))
		self.assertTrue(os.path.exists(emptyFileName))
		os.chmod(emptyFileName, S_IREAD)
		self.assertFalse(pBExport.restoreBackupCopy(emptyFileName))
		os.remove(emptyFileName)
		self.assertTrue(pBExport.rmBackupCopy(emptyFileName))
		self.assertFalse(os.path.exists(emptyFileName + pBExport.backupExtension))

	def test_offlineExports(self):
		"""Test of offline export functions exportSelected, updateExportedBib"""
		testBibName = os.path.join(pbConfig.dataPath, "tests_%s.bib"%today_ymd)
		sampleList = [{"bibtex": '@Article{empty,\nauthor="me",\ntitle="no"\n}'}, {"bibtex": '@Article{empty2,\nauthor="me2",\ntitle="yes"\n}'}]
		sampleTxt = '@Article{empty,\nauthor="me",\ntitle="no"\n}\n@Article{empty2,\nauthor="me2",\ntitle="yes"\n}\n'
		pBDB.bibs.lastFetched = sampleList
		pBExport.exportLast(testBibName)
		self.assertEqual(open(testBibName).read(), sampleTxt)
		os.remove(testBibName)

		sampleList = [{"bibtex": '@Article{empty2,\nauthor="me2",\ntitle="{yes}",\n}'}]
		sampleTxt = '@Article{empty2,\nauthor="me2",\ntitle="{yes}",\n}\n'
		pBExport.exportSelected(testBibName, sampleList)
		self.assertEqual(open(testBibName).read(), sampleTxt)

		with patch('physbiblio.database.entries.getByBibkey', return_value = [{"bibtexDict": {"ID": "empty2", "ENTRYTYPE": "Article", "author": "me et al", "title": "yes"}}]) as _mock:
			pBExport.updateExportedBib(testBibName, overwrite = True)
		self.assertEqual(open(testBibName).read().replace(" ","").replace("\n",""),
			 sampleTxt.replace("me2", 'me et al').replace(" ","").replace("\n",""))
		pBExport.rmBackupCopy(testBibName)
		os.remove(testBibName)

	def test_exportAll(self):
		"""Test of exportAll"""
		testBibName = os.path.join(pbConfig.dataPath, "tests_%s.bib"%today_ymd)
		sampleList = [{"bibtex": '@Article{empty,\nauthor="me",\ntitle="no"\n}'}, {"bibtex": '@Article{empty2,\nauthor="me2",\ntitle="yes"\n}'}]
		sampleTxt = '@Article{empty,\nauthor="me",\ntitle="no"\n}\n@Article{empty2,\nauthor="me2",\ntitle="yes"\n}\n'
		with patch('physbiblio.database.entries.fetchCursor', return_value = sampleList) as _curs:
			pBExport.exportAll(testBibName)
		self.assertEqual(open(testBibName).read(), sampleTxt)
		os.remove(testBibName)

	def test_exportForTexFile(self):
		"""test exportForTexFile function with a fake tex and database"""
		testBibName = os.path.join(pbConfig.dataPath, "tests_%s.bib"%today_ymd)
		self.assertFalse(os.path.exists(testBibName))
		testTexName = os.path.join(pbConfig.dataPath, "tests_%s.tex"%today_ymd)
		texString = "\cite{empty}\citep{empty2}\citet{Gariazzo:2015rra}, \citet{Gariazzo:2017rra}\n"
		open(testTexName, "w").write(texString)
		self.assertEqual(open(testTexName).read(), texString)
		sampleList = [{"bibkey": "empty", "bibtex": '@Article{empty,\nauthor="me",\ntitle="no"\n}'}, {"bibkey": "empty2", "bibtex": '@Article{empty2,\nauthor="me2",\ntitle="yes"\n}'}]

		with patch('physbiblio.database.catsEntries.insert', return_value = True) as _ceins:
			with patch('physbiblio.database.entries.getByBibkey', side_effect = [
					[{"bibkey": "empty", "bibtex": '@Article{empty,\nauthor="me",\ntitle="no"\n}'}],
					[{"bibkey": "empty2", "bibtex": '@Article{empty2,\nauthor="me2",\ntitle="yes"\n}'}],
					[{"bibkey": "Gariazzo:2015rra", "bibtex": '@article{Gariazzo:2015rra,\nauthor= "Gariazzo, S. and others",\ntitle="{Light sterile neutrinos}",\n}'}],
					[{"bibkey": "Gariazzo:2015rra", "bibtex": '@article{Gariazzo:2015rra,\nauthor= "Gariazzo, S. and others",\ntitle="{Light sterile neutrinos}",\n}'}],
					[], []]) as _getbbibk:
				with patch('physbiblio.database.entries.getByBibtex', side_effect = [
						[{"bibkey": "empty", "bibtex": '@Article{empty,\nauthor="me",\ntitle="no"\n}'}],
						[{"bibkey": "empty2", "bibtex": '@Article{empty2,\nauthor="me2",\ntitle="yes"\n}'}],
						[], []]) as _getbbibt:
					with patch('physbiblio.database.entries.loadAndInsert',
							side_effect = ['@article{Gariazzo:2015rra,\nauthor= "Gariazzo, S. and others",\ntitle="{Light sterile neutrinos}",\n}', '']) as _mock:
						pBExport.exportForTexFile(testTexName, testBibName, overwrite = True, autosave = False)
		self.assertTrue(os.path.exists(testBibName))
		self.assertEqual(open(testBibName).read(), '%file written by PhysBiblio\n@Article{empty,\nauthor="me",\ntitle="no"\n}\n@Article{empty2,\nauthor="me2",\ntitle="yes"\n}\n@article{Gariazzo:2015rra,\nauthor= "Gariazzo, S. and others",\ntitle="{Light sterile neutrinos}",\n}\n')
		os.remove(testBibName)
		os.remove(testTexName)

if __name__=='__main__':
	unittest.main()
