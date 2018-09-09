#!/usr/bin/env python
"""
Test file for the physbiblio.gui.expWindows module.

This file is part of the physbiblio package.
"""
import sys
import traceback
import os
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QWidget

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch, call
else:
	import unittest
	from unittest.mock import patch, call

try:
	from physbiblio.setuptests import *
	from physbiblio.gui.setuptests import *
	from physbiblio.gui.expWindows import *
	from physbiblio.gui.mainWindow import MainWindow
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
	print(traceback.format_exc())

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestFunctions(GUITestCase):
	"""Test the editExperiment and deleteExperiment functions"""
	def test_editExperiment(self):
		"""test editExperiment"""
		p = QWidget()
		m = MainWindow(testing=True)
		ncw = editExperimentDialog(p)
		ncw.onCancel()
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _s,\
				patch("physbiblio.gui.expWindows.editExperimentDialog."
					+ "__init__", return_value=None) as _i:
			editExperiment(p, m, testing=ncw)
			_i.assert_called_once_with(p, experiment=None)
			_s.assert_called_once_with("No modifications to experiments")

		with patch("physbiblio.gui.expWindows.editExperimentDialog."
					+ "__init__", return_value=None) as _i,\
				patch("logging.Logger.debug") as _l:
			editExperiment(p, p, testing=ncw)
			_i.assert_called_once_with(p, experiment=None)
			_l.assert_called_once_with(
				"mainWinObject has no attribute 'statusBarMessage'",
				exc_info=True)

		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _s,\
				patch("physbiblio.gui.expWindows.editExperimentDialog."
					+ "__init__", return_value=None) as _i,\
				patch("physbiblio.database.experiments.getDictByID",
					return_value="abc") as _g:
			editExperiment(p, m, 9999, testing=ncw)
			_i.assert_called_once_with(p, experiment="abc")
			_g.assert_called_once_with(9999)
			_s.assert_called_once_with("No modifications to experiments")

		ncw = editExperimentDialog(p)
		ncw.selectedExps = [9999]
		ncw.textValues["homepage"].setText("www.some.thing.com")
		ncw.textValues["comments"].setText("comm")
		ncw.textValues["inspire"].setText("1234")
		ncw.onOk()
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _s,\
				patch("physbiblio.gui.expWindows.editExperimentDialog."
					+ "__init__", return_value=None) as _i,\
				patch("physbiblio.database.experiments.getDictByID",
					return_value="abc") as _g:
			editExperiment(p, m, editIdExp=9999, testing=ncw)
			_i.assert_called_once_with(p, experiment="abc")
			_g.assert_called_once_with(9999)
			_s.assert_called_once_with("ERROR: empty experiment name")

		ncw.textValues["name"].setText("myexp")
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _s,\
				patch("physbiblio.gui.expWindows.editExperimentDialog."
					+ "__init__", return_value=None) as _i,\
				patch("physbiblio.database.experiments.getDictByID",
					return_value="abc") as _g,\
				patch("physbiblio.database.experiments.insert",
					return_value="abc") as _n,\
				patch("logging.Logger.debug") as _l:
			editExperiment(p, m, 9999, testing=ncw)
			_i.assert_called_once_with(p, experiment="abc")
			_g.assert_called_once_with(9999)
			_n.assert_called_once_with(
				{'name': u'myexp', 'inspire': u'1234',
				'homepage': 'www.some.thing.com', 'comments': u'comm'})
			_s.assert_called_once_with("Experiment saved")
			_l.assert_called_once_with(
				"parentObject has no attribute 'recreateTable'", exc_info=True)

		ncw.textValues["name"].setText("myexp")
		ctw = expsListWindow(p)
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _s,\
				patch("physbiblio.gui.expWindows.editExperimentDialog."
					+ "__init__", return_value=None) as _i,\
				patch("physbiblio.database.experiments.getDictByID",
					return_value="abc") as _g,\
				patch("physbiblio.database.experiments.insert",
					return_value="abc") as _n,\
				patch("logging.Logger.debug") as _l,\
				patch("physbiblio.gui.expWindows.expsListWindow.recreateTable"
					) as _r:
			editExperiment(ctw, m, 9999, testing=ncw)
			_i.assert_called_once_with(ctw, experiment="abc")
			_g.assert_called_once_with(9999)
			_n.assert_called_once_with(
				{'name': u'myexp', 'inspire': u'1234',
				'homepage': 'www.some.thing.com', 'comments': u'comm'})
			_s.assert_called_once_with("Experiment saved")
			_l.assert_not_called()
			_r.assert_called_once_with()

		exp = {
			'idExp': 9999,
			'homepage': "www.some.page.com",
			'comments': "no comment",
			'inspire': "1234",
			'name': "myexp"
		}
		ncw = editExperimentDialog(p, exp)
		ncw.selectedCats = []
		ncw.textValues["inspire"].setText("4321")
		ncw.textValues["name"].setText("myexp1")
		ncw.textValues["comments"].setText("comm")
		ncw.textValues["homepage"].setText("www.page.com")
		ncw.onOk()
		ctw = expsListWindow(p)
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _s,\
				patch("physbiblio.gui.expWindows.editExperimentDialog."
					+ "__init__", return_value=None) as _i,\
				patch("physbiblio.database.experiments.getDictByID",
					return_value="abc") as _g,\
				patch("physbiblio.database.experiments.update",
					return_value="abc") as _n,\
				patch("logging.Logger.info") as _l,\
				patch("physbiblio.gui.expWindows.expsListWindow.recreateTable"
					) as _r:
			editExperiment(ctw, m, 9999, testing=ncw)
			_i.assert_called_once_with(ctw, experiment="abc")
			_g.assert_called_once_with(9999)
			_n.assert_called_once_with(
				{'idExp': u'9999', 'name': u'myexp1',
				'homepage': u'www.page.com', 'comments': u'comm',
				'inspire': u'4321'}, '9999')
			_s.assert_called_once_with("Experiment saved")
			_l.assert_called_once_with("Updating experiment 9999...")
			_r.assert_called_once_with()

	def test_deleteExperiment(self):
		"""test deleteExperiment"""
		p = QWidget()
		m = MainWindow(testing=True)
		with patch("physbiblio.gui.expWindows.askYesNo",
				return_value = False) as _a, \
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _s:
			deleteExperiment(p, m, 9999, "myexp")
			_a.assert_called_once_with(
				"Do you really want to delete this experiment "
				+ "(ID = '9999', name = 'myexp')?")
			_s.assert_called_once_with("Nothing changed")

		with patch("physbiblio.gui.expWindows.askYesNo",
				return_value = False) as _a, \
				patch("logging.Logger.debug") as _d:
			deleteExperiment(p, p, 9999, "myexp")
			_a.assert_called_once_with(
				"Do you really want to delete this experiment "
				+ "(ID = '9999', name = 'myexp')?")
			_d.assert_called_once_with(
				"mainWinObject has no attribute 'statusBarMessage'",
				exc_info=True)

		with patch("physbiblio.gui.expWindows.askYesNo",
				return_value = True) as _a, \
				patch("physbiblio.database.experiments.delete") as _c, \
				patch("PySide2.QtWidgets.QMainWindow.setWindowTitle") as _t, \
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _s, \
				patch("logging.Logger.debug") as _d:
			deleteExperiment(p, m, 9999, "myexp")
			_a.assert_called_once_with(
				"Do you really want to delete this experiment "
				+ "(ID = '9999', name = 'myexp')?")
			_c.assert_called_once_with(9999)
			_t.assert_called_once_with("PhysBiblio*")
			_s.assert_called_once_with("Experiment deleted")
			_d.assert_called_once_with(
				"parentObject has no attribute 'recreateTable'",
				exc_info=True)

		elw = expsListWindow(p)
		with patch("physbiblio.gui.expWindows.askYesNo",
				return_value = True) as _a, \
				patch("physbiblio.database.experiments.delete") as _c, \
				patch("PySide2.QtWidgets.QMainWindow.setWindowTitle") as _t, \
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _s, \
				patch("physbiblio.gui.expWindows.expsListWindow.recreateTable"
					) as _r:
			deleteExperiment(elw, m, 9999, "myexp")
			_a.assert_called_once_with(
				"Do you really want to delete this experiment "
				+ "(ID = '9999', name = 'myexp')?")
			_c.assert_called_once_with(9999)
			_t.assert_called_once_with("PhysBiblio*")
			_s.assert_called_once_with("Experiment deleted")
			_r.assert_called_once_with()

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestExpTableModel(GUITestCase):
	"""Test ExpTableModel"""
	def test_init(self):
		"""test init"""
		p = QWidget()
		exp_list = [{"idExp": 0, "name": "no"}]
		header = ["id", "name"]
		em = ExpTableModel(p, exp_list, header, askExps=False, previous=[])
		self.assertIsInstance(em, MyTableModel)
		self.assertEqual(em.typeClass, "Exps")
		self.assertEqual(em.dataList, exp_list)
		with patch("physbiblio.gui.commonClasses.MyTableModel.__init__"
				) as _i,\
				patch("physbiblio.gui.commonClasses.MyTableModel."
					+ "prepareSelected") as _s:
			em = ExpTableModel(p, exp_list, header,
				askExps=True, previous=[9999])
			_i.assert_called_once_with(p, ['id', 'name'], True, [9999])
			_s.assert_called_once_with()

	def test_getIdentifier(self):
		"""test getIdentifier"""
		p = QWidget()
		exp_list = [{"idExp": 0, "name": "no"}]
		header = ["id", "name"]
		em = ExpTableModel(p, exp_list, header, askExps=False, previous=[])
		self.assertEqual(em.getIdentifier({"idExp": 9999, "name": "no"}),
			9999)

	def test_data(self):
		"""test data"""
		p = QWidget()
		exp_list = [{"idExp": 0, "name": "myexp"},
			{"idExp": 9999, "name": "exp"}]
		header = ["idExp", "name"]
		em = ExpTableModel(p, exp_list, header, askExps=False, previous=[])
		ix = em.index(10, 0)
		self.assertEqual(em.data(ix, Qt.CheckStateRole), None)
		ix = em.index(0, 0)
		self.assertEqual(em.data(ix, Qt.DisplayRole), 0)
		self.assertEqual(em.data(ix, Qt.EditRole), 0)
		self.assertEqual(em.data(ix, Qt.DecorationRole), None)
		ix = em.index(0, 1)
		self.assertEqual(em.data(ix, Qt.DisplayRole), "myexp")
		self.assertEqual(em.data(ix, Qt.EditRole), "myexp")
		self.assertEqual(em.data(ix, Qt.DecorationRole), None)

		ix = em.index(0, 0)
		self.assertEqual(em.data(ix, Qt.CheckStateRole), None)
		p = QWidget()
		p.askExps = False
		em = ExpTableModel(p, exp_list, header, askExps=False, previous=[])
		self.assertEqual(em.data(em.index(0, 0), Qt.CheckStateRole), None)
		em = ExpTableModel(p, exp_list, header, askExps=True, previous=[])
		self.assertEqual(em.data(em.index(0, 0), Qt.CheckStateRole),
			Qt.Unchecked)
		em = ExpTableModel(p, exp_list, header, askExps=True, previous=[0])
		self.assertEqual(em.data(em.index(0, 0), Qt.CheckStateRole),
			Qt.Checked)
		self.assertEqual(em.setData(ix, "abc", Qt.CheckStateRole), True)
		self.assertEqual(em.data(em.index(0, 0), Qt.CheckStateRole),
			Qt.Unchecked)
		self.assertEqual(em.setData(ix, Qt.Checked, Qt.CheckStateRole), True)
		self.assertEqual(em.data(em.index(0, 0), Qt.CheckStateRole),
			Qt.Checked)

	def test_setData(self):
		"""test setData"""
		p = QWidget()
		def connectEmit(ix1, ix2):
			"""used to test dataChanged.emit"""
			self.newEmit = ix1
		exp_list = [{"idExp": 0, "name": "no"}, {"idExp": 9999, "name": "yes"}]
		header = ["idExp", "name"]
		cm = ExpTableModel(p, exp_list, header)
		ix = cm.index(10, 0)
		self.newEmit = False
		cm.dataChanged.connect(connectEmit)
		self.assertEqual(cm.setData(ix, "abc", Qt.CheckStateRole), False)
		self.assertEqual(self.newEmit, False)
		ix = cm.index(0, 0)
		self.assertEqual(cm.setData(ix, Qt.Checked, Qt.CheckStateRole), True)
		self.assertEqual(cm.selectedElements[0], True)
		self.assertEqual(self.newEmit, ix)
		self.newEmit = False
		self.assertEqual(cm.setData(ix, "abc", Qt.CheckStateRole), True)
		self.assertEqual(cm.selectedElements[0], False)
		self.assertEqual(self.newEmit, ix)

		cm = ExpTableModel(p, exp_list, header)
		ix = cm.index(0, 0)
		self.assertEqual(cm.setData(ix, "abc", Qt.EditRole), True)
		self.assertEqual(cm.selectedElements[0], False)
		self.assertEqual(cm.setData(ix, "abc", Qt.CheckStateRole), True)
		self.assertEqual(cm.selectedElements[0], False)

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestExpsListWindow(GUITestCase):
	"""Test expsListWindow"""
	def test_init(self):
		"""test"""
		pass

	def test_populateAskExp(self):
		"""test"""
		pass

	def test_onCancel(self):
		"""test"""
		pass

	def test_onOk(self):
		"""test"""
		pass

	def test_onNewExp(self):
		"""test"""
		pass

	def test_keyPressEvent(self):
		"""test"""
		pass

	def test_changeFilter(self):
		"""test"""
		pass

	def test_createTable(self):
		"""test"""
		pass

	def test_triggeredContextMenuEvent(self):
		"""test"""
		pass

	def test_handleItemEntered(self):
		"""test"""
		pass

	def test_cellClick(self):
		"""test"""
		pass

	def test_cellDoubleClick(self):
		"""test"""
		pass

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestEditExperimentDialog(GUITestCase):
	"""Test editExperimentDialog"""
	def test_init(self):
		"""test"""
		pass

	def test_createForm(self):
		"""test"""
		pass

if __name__=='__main__':
	unittest.main()
