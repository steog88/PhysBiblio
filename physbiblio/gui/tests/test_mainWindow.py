#!/usr/bin/env python
"""
Test file for the physbiblio.gui.mainWindow module.

This file is part of the physbiblio package.
"""
import sys, traceback
import os
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch, call
else:
	import unittest
	from unittest.mock import patch, call

try:
	from physbiblio.setuptests import *
	from physbiblio.gui.setuptests import *
	from physbiblio.gui.mainWindow import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestMainWindow(GUITestCase):
	"""test"""
	def test_init(self):
		"""test"""
		pass

	def test_printNewVersion(self):
		"""test"""
		pass

	def test_setIcon(self):
		"""test"""
		pass

	def test_createActions(self):
		"""test"""
		pass

	def test_closeEvent(self):
		"""test"""
		pass

	def test_createMenusAndToolBar(self):
		"""test"""
		pass

	def test_createMainLayout(self):
		"""test"""
		pass

	def test_undoDB(self):
		"""test"""
		pass

	def test_refreshMainContent(self):
		"""test"""
		pass

	def test_reloadMainContent(self):
		"""test"""
		pass

	def test_manageProfiles(self):
		"""test"""
		pass

	def test_editProfiles(self):
		"""test"""
		pass

	def test_config(self):
		"""test"""
		pass

	def test_logfile(self):
		"""test"""
		pass

	def test_reloadConfig(self):
		"""test"""
		pass

	def test_showAbout(self):
		"""test"""
		pass

	def test_showDBStats(self):
		"""test"""
		pass

	def test_runInThread(self):
		"""test"""
		pass

	def test_cleanSpare(self):
		"""test"""
		pass

	def test_cleanSparePDF(self):
		"""test"""
		pass

	def test_createStatusBar(self):
		"""test"""
		pass

	def test_statusBarMessage(self):
		"""test"""
		pass

	def test_save(self):
		"""test"""
		pass

	def test_importFromBib(self):
		"""test"""
		pass

	def test_export(self):
		"""test"""
		pass

	def test_exportSelection(self):
		"""test"""
		pass

	def test_exportFile(self):
		"""test"""
		pass

	def test_exportUpdate(self):
		"""test"""
		pass

	def test_exportAll(self):
		"""test"""
		pass

	def test_categories(self):
		"""test"""
		pass

	def test_newCategory(self):
		"""test"""
		pass

	def test_experimentList(self):
		"""test"""
		pass

	def test_newExperiment(self):
		"""test"""
		pass

	def test_newBibtex(self):
		"""test"""
		pass

	def test_searchBiblio(self):
		"""test"""
		pass

	def test_runSearchBiblio(self):
		"""test"""
		pass

	def test_runSearchReplaceBiblio(self):
		"""test"""
		pass

	def test_delSearchBiblio(self):
		"""test"""
		pass

	def test_searchAndReplace(self):
		"""test"""
		pass

	def test_runReplace(self):
		"""test"""
		pass

	def test_updateAllBibtexsAsk(self):
		"""test"""
		pass

	def test_updateAllBibtexs(self):
		"""test"""
		pass

	def test_updateInspireInfo(self):
		"""test"""
		pass

	def test_authorStats(self):
		"""test"""
		pass

	def test_getInspireStats(self):
		"""test"""
		pass

	def test_inspireLoadAndInsert(self):
		"""test"""
		pass

	def test_askCatsForEntries(self):
		"""test"""
		pass

	def test_inspireLoadAndInsertWithCats(self):
		"""test"""
		pass

	def test_advancedImport(self):
		"""test"""
		pass

	def test_cleanAllBibtexsAsk(self):
		"""test"""
		pass

	def test_cleanAllBibtexs(self):
		"""test"""
		pass

	def test_findBadBibtexs(self):
		"""test"""
		pass

	def test_infoFromArxiv(self):
		"""test"""
		pass

	def test_browseDailyArxiv(self):
		"""test"""
		pass

	def test_sendMessage(self):
		"""test"""
		pass

	def test_done(self):
		"""test"""
		pass

if __name__=='__main__':
	unittest.main()
