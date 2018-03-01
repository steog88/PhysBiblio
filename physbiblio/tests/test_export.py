#!/usr/bin/env python
"""
Test file for the packages in the PhysBiblio application, a bibliography manager written in Python.

This file is part of the PhysBiblio package.
"""
import sys, traceback, os
from stat import S_IREAD, S_IRGRP, S_IROTH

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
	from physbiblio.database import pBDB
	from physbiblio.export import pBExport
except ImportError:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipLongTests, "Long tests")
class TestExportMethods(unittest.TestCase):
	def test_backup(self):
		emptyFileName = os.path.join(pbConfig.path, "tests_%s.bib"%today_ymd)
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
		testBibName = os.path.join(pbConfig.path, "tests_%s.bib"%today_ymd)
		sampleList = [{"bibtex": '@Article{empty,\nauthor="me",\ntitle="no"\n}'}, {"bibtex": '@Article{empty2,\nauthor="me2",\ntitle="yes"\n}'}]
		sampleTxt = '@Article{empty,\nauthor="me",\ntitle="no"\n}\n@Article{empty2,\nauthor="me2",\ntitle="yes"\n}\n'
		pBDB.bibs.lastFetched = sampleList
		pBExport.exportLast(testBibName)
		self.assertEqual(open(testBibName).read(), sampleTxt)
		os.remove(testBibName)

		pBDB.bibs.getAll = MagicMock(return_value = sampleList)
		pBExport.exportAll(testBibName)
		self.assertEqual(open(testBibName).read(), sampleTxt)
		os.remove(testBibName)

		sampleList = [{"bibtex": '@Article{empty2,\nauthor="me2",\ntitle="{yes}",\n}'}]
		sampleTxt = '@Article{empty2,\nauthor="me2",\ntitle="{yes}",\n}\n'
		pBExport.exportSelected(testBibName, sampleList)
		self.assertEqual(open(testBibName).read(), sampleTxt)

		pBDB.bibs.getByBibkey = MagicMock(return_value = [{"bibtexDict": {"ID": "empty2", "ENTRYTYPE": "Article", "author": "me et al", "title": "yes"}}])
		pBExport.updateExportedBib(testBibName, overwrite = True)
		self.assertEqual(open(testBibName).read().replace(" ","").replace("\n",""),
			 sampleTxt.replace("me2", 'me et al').replace(" ","").replace("\n",""))
		pBExport.rmBackupCopy(testBibName)
		os.remove(testBibName)

	def test_exportForTexFile(self):
		testBibName = os.path.join(pbConfig.path, "tests_%s.bib"%today_ymd)
		self.assertFalse(os.path.exists(testBibName))
		testTexName = os.path.join(pbConfig.path, "tests_%s.tex"%today_ymd)
		texString = "\cite{empty}\citep{empty2}\citet{Gariazzo:2015rra}, \citet{Gariazzo:2017rra}\n"
		open(testTexName, "w").write(texString)
		self.assertEqual(open(testTexName).read(), texString)
		sampleList = [{"bibkey": "empty", "bibtex": '@Article{empty,\nauthor="me",\ntitle="no"\n}'}, {"bibkey": "empty2", "bibtex": '@Article{empty2,\nauthor="me2",\ntitle="yes"\n}'}]
		pBDB.catBib.insert = MagicMock(return_value = True)
		pBDB.bibs.getAll = MagicMock(return_value = sampleList)
		pBDB.bibs.getByBibkey = MagicMock(side_effect = [
			[{"bibkey": "empty", "bibtex": '@Article{empty,\nauthor="me",\ntitle="no"\n}'}],
			[{"bibkey": "empty2", "bibtex": '@Article{empty2,\nauthor="me2",\ntitle="yes"\n}'}],
			[{"bibkey": "Gariazzo:2015rra", "bibtex": '@article{Gariazzo:2015rra,\nauthor= "Gariazzo, S. and others",\ntitle="{Light sterile neutrinos}",\n}'}],
			[{"bibkey": "Gariazzo:2015rra", "bibtex": '@article{Gariazzo:2015rra,\nauthor= "Gariazzo, S. and others",\ntitle="{Light sterile neutrinos}",\n}'}],
			[]])
		pBDB.bibs.loadAndInsert = MagicMock(side_effect = ['@article{Gariazzo:2015rra,\nauthor= "Gariazzo, S. and others",\ntitle="{Light sterile neutrinos}",\n}', ''])
		pBExport.exportForTexFile(testTexName, testBibName, overwrite = True, autosave = False)
		self.assertTrue(os.path.exists(testBibName))
		self.assertEqual(open(testBibName).read(), '%file written by PhysBiblio\n@Article{empty,\nauthor="me",\ntitle="no"\n}\n@Article{empty2,\nauthor="me2",\ntitle="yes"\n}\n@article{Gariazzo:2015rra,\nauthor= "Gariazzo, S. and others",\ntitle="{Light sterile neutrinos}",\n}\n')
		os.remove(testBibName)
		os.remove(testTexName)

if __name__=='__main__':
	print("\nStarting tests...\n")
	unittest.main()
