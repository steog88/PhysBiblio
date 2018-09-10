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
		ncw = EditExperimentDialog(p)
		ncw.onCancel()
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _s,\
				patch("physbiblio.gui.expWindows.EditExperimentDialog."
					+ "__init__", return_value=None) as _i:
			editExperiment(p, m, testing=ncw)
			_i.assert_called_once_with(p, experiment=None)
			_s.assert_called_once_with("No modifications to experiments")

		with patch("physbiblio.gui.expWindows.EditExperimentDialog."
					+ "__init__", return_value=None) as _i,\
				patch("logging.Logger.debug") as _l:
			editExperiment(p, p, testing=ncw)
			_i.assert_called_once_with(p, experiment=None)
			_l.assert_called_once_with(
				"mainWinObject has no attribute 'statusBarMessage'",
				exc_info=True)

		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _s,\
				patch("physbiblio.gui.expWindows.EditExperimentDialog."
					+ "__init__", return_value=None) as _i,\
				patch("physbiblio.database.experiments.getDictByID",
					return_value="abc") as _g:
			editExperiment(p, m, 9999, testing=ncw)
			_i.assert_called_once_with(p, experiment="abc")
			_g.assert_called_once_with(9999)
			_s.assert_called_once_with("No modifications to experiments")

		ncw = EditExperimentDialog(p)
		ncw.selectedExps = [9999]
		ncw.textValues["homepage"].setText("www.some.thing.com")
		ncw.textValues["comments"].setText("comm")
		ncw.textValues["inspire"].setText("1234")
		ncw.onOk()
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _s,\
				patch("physbiblio.gui.expWindows.EditExperimentDialog."
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
				patch("physbiblio.gui.expWindows.EditExperimentDialog."
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
		ctw = ExpsListWindow(p)
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _s,\
				patch("physbiblio.gui.expWindows.EditExperimentDialog."
					+ "__init__", return_value=None) as _i,\
				patch("physbiblio.database.experiments.getDictByID",
					return_value="abc") as _g,\
				patch("physbiblio.database.experiments.insert",
					return_value="abc") as _n,\
				patch("logging.Logger.debug") as _l,\
				patch("physbiblio.gui.expWindows.ExpsListWindow.recreateTable"
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
		ncw = EditExperimentDialog(p, exp)
		ncw.selectedCats = []
		ncw.textValues["inspire"].setText("4321")
		ncw.textValues["name"].setText("myexp1")
		ncw.textValues["comments"].setText("comm")
		ncw.textValues["homepage"].setText("www.page.com")
		ncw.onOk()
		ctw = ExpsListWindow(p)
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _s,\
				patch("physbiblio.gui.expWindows.EditExperimentDialog."
					+ "__init__", return_value=None) as _i,\
				patch("physbiblio.database.experiments.getDictByID",
					return_value="abc") as _g,\
				patch("physbiblio.database.experiments.update",
					return_value="abc") as _n,\
				patch("logging.Logger.info") as _l,\
				patch("physbiblio.gui.expWindows.ExpsListWindow.recreateTable"
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

		elw = ExpsListWindow(p)
		with patch("physbiblio.gui.expWindows.askYesNo",
				return_value = True) as _a, \
				patch("physbiblio.database.experiments.delete") as _c, \
				patch("PySide2.QtWidgets.QMainWindow.setWindowTitle") as _t, \
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _s, \
				patch("physbiblio.gui.expWindows.ExpsListWindow.recreateTable"
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
	"""Test ExpsListWindow"""
	def setUp(self):
		"""define common parameters for test use"""
		self.exps = [
			{"idExp": 0, "name": "test0",
				"homepage": "", "comments": "", "inspire": ""},
			{"idExp": 1, "name": "test1",
				"homepage": "", "comments": "", "inspire": ""},
			{"idExp": 2, "name": "test2",
				"homepage": "", "comments": "", "inspire": ""},
			{"idExp": 3, "name": "test3",
				"homepage": "", "comments": "", "inspire": ""},
			]

	def test_init(self):
		"""test init"""
		p = QWidget()
		with patch("physbiblio.database.experiments.getAll",
				return_value=self.exps) as _gh,\
				patch("physbiblio.gui.expWindows.ExpsListWindow.createTable"
					) as _cf:
			elw = ExpsListWindow(p)
			_cf.assert_called_once_with()
		self.assertIsInstance(elw, objListWindow)
		self.assertEqual(elw.parent(), p)
		self.assertEqual(elw.colcnt, 5)
		self.assertEqual(elw.colContents,
			['idExp', 'name', 'comments', 'homepage', 'inspire'])
		self.assertEqual(elw.askExps, False)
		self.assertEqual(elw.askForBib, None)
		self.assertEqual(elw.askForCat, None)
		self.assertEqual(elw.previous, [])
		self.assertEqual(elw.windowTitle(), 'List of experiments')

		with patch("physbiblio.database.experiments.getAll",
				return_value=self.exps) as _gh,\
				patch("physbiblio.gui.expWindows.ExpsListWindow.createTable"
					) as _cf:
			elw = ExpsListWindow(parent=p,
				askExps=True,
				askForBib="mybib",
				askForCat="mycat",
				previous=[9999])
			_cf.assert_called_once_with()
		self.assertIsInstance(elw, objListWindow)
		self.assertEqual(elw.parent(), p)
		self.assertEqual(elw.colcnt, 5)
		self.assertEqual(elw.colContents,
			['idExp', 'name', 'comments', 'homepage', 'inspire'])
		self.assertEqual(elw.askExps, True)
		self.assertEqual(elw.askForBib, "mybib")
		self.assertEqual(elw.askForCat, "mycat")
		self.assertEqual(elw.previous, [9999])
		self.assertEqual(elw.windowTitle(), 'List of experiments')

	def test_populateAskExp(self):
		"""test populateAskExp"""
		raise NotImplementedError()

	def test_onCancel(self):
		"""test onCancel"""
		elw = ExpsListWindow()
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			elw.onCancel()
		self.assertFalse(elw.result)

	def test_onOk(self):
		"""test onOk"""
		raise NotImplementedError()
		p = QWidget()
		with patch("physbiblio.database.experiments.getAll",
					return_value=self.exps) as _gh:
			elw = ExpsListWindow(p)
		# with patch("physbiblio.database.categories.getHier",
				# return_value=self.cathier) as _gh,\
				# patch("physbiblio.database.categories.getAll",
					# return_value=self.cats) as _gh,\
				# patch("physbiblio.gui.catWindows.catsTreeWindow."
					# + "_populateTree",
					# return_value=self.rootElements[0]) as _pt:
			# ctw = catsTreeWindow(p)
		# self.assertFalse(hasattr(p, "selectedCats"))
		# self.assertFalse(hasattr(p, "previousUnchanged"))
		# ctw.root_model.selectedCats[0] = True
		# ctw.root_model.selectedCats[3] = True
		# ctw.root_model.previousSaved[0] = True
		# with patch("physbiblio.gui.catWindows.QDialog.close") as _c:
			# ctw.onOk()
			# _c.assert_called_once_with()
		# self.assertEqual(hasattr(p, "selectedCats"), True)
		# self.assertEqual(p.selectedCats, [0, 3])
		# self.assertEqual(p.previousUnchanged, [0])
		# self.assertEqual(ctw.result, "Ok")

	def test_onNewExp(self):
		"""test onNewExp"""
		p = QWidget()
		elw = ExpsListWindow(p)
		with patch("physbiblio.gui.expWindows.editExperiment") as _ec, \
				patch("physbiblio.gui.expWindows.ExpsListWindow.recreateTable"
					) as _rt:
			elw.onNewExp()
			_ec.assert_called_once_with(p, p)
			_rt.assert_called_once()

	def test_keyPressEvent(self):
		"""test keyPressEvent"""
		elw = ExpsListWindow()
		with patch("PySide2.QtWidgets.QDialog.close") as _oc:
			QTest.keyPress(elw, "a")
			_oc.assert_not_called()
			QTest.keyPress(elw, Qt.Key_Enter)
			_oc.assert_not_called()
			QTest.keyPress(elw, Qt.Key_Escape)
			_oc.assert_called_once()

	def test_createTable(self):
		"""test createTable"""
		p = QWidget()
		with patch("physbiblio.database.experiments.getAll",
					return_value=self.exps) as _gh:
			elw = ExpsListWindow(p)
		raise NotImplementedError()

	def test_triggeredContextMenuEvent(self):
		"""test triggeredContextMenuEvent"""
		p = QWidget()
		with patch("physbiblio.database.experiments.getAll",
					return_value=self.exps) as _gh:
			elw = ExpsListWindow(p)
		raise NotImplementedError()

	def test_handleItemEntered(self):
		"""test handleItemEntered"""
		p = QWidget()
		with patch("physbiblio.database.experiments.getAll",
					return_value=self.exps) as _gh:
			elw = ExpsListWindow(p)
		ix = elw.proxyModel.index(0, 0)
		with patch("logging.Logger.exception") as _l,\
				patch("PySide2.QtCore.QTimer.start") as _st,\
				patch("PySide2.QtWidgets.QToolTip.showText") as _sh,\
				patch("physbiblio.database.experiments.getByID",
					return_value=[]) as _gbi:
			self.assertEqual(elw.handleItemEntered(ix), None)
			_l.assert_called_once_with("Failed in finding experiment")
			_gbi.assert_called_once_with('0')
			_st.assert_not_called()
			_sh.assert_not_called()
		with patch("logging.Logger.exception") as _l,\
				patch("PySide2.QtCore.QTimer.start") as _st,\
				patch("PySide2.QtWidgets.QToolTip.showText") as _sh,\
				patch("physbiblio.database.experiments.getByID",
					return_value=[self.exps[0]]) as _gbi,\
				patch("physbiblio.database.entryExps.countByExp",
					return_value=33) as _cb,\
				patch("physbiblio.database.catsExps.countByExp",
					return_value=12) as _ce:
			self.assertEqual(elw.handleItemEntered(ix), None)
			_l.assert_not_called()
			self.assertIsInstance(elw.timer, QTimer)
			self.assertTrue(elw.timer.isSingleShot())
			_gbi.assert_called_once_with('0')
			_st.assert_called_once_with(500)
			_sh.assert_not_called()
			elw.timer.timeout.emit()
			_sh.assert_called_once_with(QCursor.pos(),
				'0: test0\nCorresponding entries: 33\n'
				+ 'Associated categories: 12',
				elw.tablewidget.viewport(),
				elw.tablewidget.visualRect(ix),
				3000)
		with patch("logging.Logger.exception") as _l,\
				patch("PySide2.QtCore.QTimer.start") as _st,\
				patch("PySide2.QtWidgets.QToolTip.showText") as _sh,\
				patch("physbiblio.database.experiments.getByID",
					return_value=[self.exps[0]]) as _gbi,\
				patch("physbiblio.database.entryExps.countByExp",
					return_value=33) as _cb,\
				patch("physbiblio.database.catsExps.countByExp",
					return_value=12) as _ce:
			self.assertEqual(elw.handleItemEntered(ix), None)
			_sh.assert_called_once_with(
				QCursor.pos(), '', elw.tablewidget.viewport())

	def test_cellClick(self):
		"""test cellClick"""
		p = QWidget()
		with patch("physbiblio.database.experiments.getAll",
					return_value=self.exps) as _gh:
			elw = ExpsListWindow(p)
		raise NotImplementedError()

	def test_cellDoubleClick(self):
		"""test cellDoubleClick"""
		p = QWidget()
		with patch("physbiblio.database.experiments.getAll",
					return_value=self.exps) as _gh:
			elw = ExpsListWindow(p)
		raise NotImplementedError()

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestEditExperimentDialog(GUITestCase):
	"""Test EditExperimentDialog"""
	def test_init(self):
		"""test init"""
		p = QWidget()
		with patch("physbiblio.gui.expWindows.EditExperimentDialog.createForm"
				) as _cf:
			eed = EditExperimentDialog(p)
			_cf.assert_called_once_with()
		self.assertIsInstance(eed, editObjectWindow)
		self.assertEqual(eed.parent(), p)
		self.assertIsInstance(eed.data, dict)
		self.assertEqual(eed.data, {"idExp": "",
			"name": "", "homepage": "", "inspire": "", "comments": ""})
		exp = {"idExp": "9999", "name": "myexp", "homepage": "www.some.exp",
			"inspire": "1234", "comments": "no comments"}
		with patch("physbiblio.gui.expWindows.EditExperimentDialog.createForm"
				) as _cf:
			eed = EditExperimentDialog(parent=p, experiment=exp)
			_cf.assert_called_once_with()
		self.assertEqual(eed.data, exp)

	def test_createForm(self):
		"""test createForm"""
		p = QWidget()
		eed = EditExperimentDialog(p)
		self.assertEqual(eed.windowTitle(), 'Edit experiment')

		self.assertIsInstance(eed.layout().itemAtPosition(1, 0).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(1, 0).widget().text(),
			"name")
		self.assertIsInstance(eed.layout().itemAtPosition(1, 1).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(1, 1).widget().text(),
			"(Name of the experiment)")
		self.assertIsInstance(eed.layout().itemAtPosition(2, 0).widget(),
			QLineEdit)
		self.assertEqual(eed.layout().itemAtPosition(2, 0).widget(),
			eed.textValues["name"])
		self.assertEqual(eed.textValues["name"].text(), "")
		self.assertEqual(eed.textValues["name"].isEnabled(), True)

		self.assertIsInstance(eed.layout().itemAtPosition(3, 0).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(3, 0).widget().text(),
			"comments")
		self.assertIsInstance(eed.layout().itemAtPosition(3, 1).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(3, 1).widget().text(),
			"(Description or comments)")
		self.assertIsInstance(eed.layout().itemAtPosition(4, 0).widget(),
			QLineEdit)
		self.assertEqual(eed.layout().itemAtPosition(4, 0).widget(),
			eed.textValues["comments"])
		self.assertEqual(eed.textValues["comments"].text(), "")
		self.assertEqual(eed.textValues["comments"].isEnabled(), True)

		self.assertIsInstance(eed.layout().itemAtPosition(5, 0).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(5, 0).widget().text(),
			"homepage")
		self.assertIsInstance(eed.layout().itemAtPosition(5, 1).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(5, 1).widget().text(),
			"(Web link to the experiment homepage)")
		self.assertIsInstance(eed.layout().itemAtPosition(6, 0).widget(),
			QLineEdit)
		self.assertEqual(eed.layout().itemAtPosition(6, 0).widget(),
			eed.textValues["homepage"])
		self.assertEqual(eed.textValues["homepage"].text(), "")
		self.assertEqual(eed.textValues["homepage"].isEnabled(), True)

		self.assertIsInstance(eed.layout().itemAtPosition(7, 0).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(7, 0).widget().text(),
			"inspire")
		self.assertIsInstance(eed.layout().itemAtPosition(7, 1).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(7, 1).widget().text(),
			"(INSPIRE-HEP ID of the experiment record)")
		self.assertIsInstance(eed.layout().itemAtPosition(8, 0).widget(),
			QLineEdit)
		self.assertEqual(eed.layout().itemAtPosition(8, 0).widget(),
			eed.textValues["inspire"])
		self.assertEqual(eed.textValues["inspire"].text(), "")
		self.assertEqual(eed.textValues["inspire"].isEnabled(), True)

		self.assertIsInstance(eed.layout().itemAtPosition(9, 0).widget(),
			QPushButton)
		self.assertEqual(eed.layout().itemAtPosition(9, 0).widget(),
			eed.acceptButton)
		self.assertEqual(eed.acceptButton.text(), "OK")
		self.assertIsInstance(eed.layout().itemAtPosition(9, 1).widget(),
			QPushButton)
		self.assertEqual(eed.layout().itemAtPosition(9, 1).widget(),
			eed.cancelButton)
		self.assertEqual(eed.cancelButton.text(), "Cancel")
		self.assertTrue(eed.cancelButton.autoDefault())
		with patch("physbiblio.gui.commonClasses.editObjectWindow.onOk"
				) as _f:
			QTest.mouseClick(eed.acceptButton, Qt.LeftButton)
			_f.assert_called_once_with()
		with patch("physbiblio.gui.commonClasses.editObjectWindow.onCancel"
				) as _f:
			QTest.mouseClick(eed.cancelButton, Qt.LeftButton)
			_f.assert_called_once_with()

		exp = {"idExp": "9999", "name": "myexp", "homepage": "www.some.exp",
			"inspire": "1234", "comments": "no comments"}
		eed = EditExperimentDialog(parent=p, experiment=exp)

		self.assertIsInstance(eed.layout().itemAtPosition(1, 0).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(1, 0).widget().text(),
			"idExp")
		self.assertIsInstance(eed.layout().itemAtPosition(1, 1).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(1, 1).widget().text(),
			"(Unique ID that identifies the experiment)")
		self.assertIsInstance(eed.layout().itemAtPosition(2, 0).widget(),
			QLineEdit)
		self.assertEqual(eed.layout().itemAtPosition(2, 0).widget(),
			eed.textValues["idExp"])
		self.assertEqual(eed.textValues["idExp"].text(), "9999")
		self.assertEqual(eed.textValues["idExp"].isEnabled(), False)

		self.assertIsInstance(eed.layout().itemAtPosition(3, 0).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(3, 0).widget().text(),
			"name")
		self.assertIsInstance(eed.layout().itemAtPosition(3, 1).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(3, 1).widget().text(),
			"(Name of the experiment)")
		self.assertIsInstance(eed.layout().itemAtPosition(4, 0).widget(),
			QLineEdit)
		self.assertEqual(eed.layout().itemAtPosition(4, 0).widget(),
			eed.textValues["name"])
		self.assertEqual(eed.textValues["name"].text(), "myexp")
		self.assertEqual(eed.textValues["name"].isEnabled(), True)

		self.assertIsInstance(eed.layout().itemAtPosition(5, 0).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(5, 0).widget().text(),
			"comments")
		self.assertIsInstance(eed.layout().itemAtPosition(5, 1).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(5, 1).widget().text(),
			"(Description or comments)")
		self.assertIsInstance(eed.layout().itemAtPosition(6, 0).widget(),
			QLineEdit)
		self.assertEqual(eed.layout().itemAtPosition(6, 0).widget(),
			eed.textValues["comments"])
		self.assertEqual(eed.textValues["comments"].text(), "no comments")
		self.assertEqual(eed.textValues["comments"].isEnabled(), True)

		self.assertIsInstance(eed.layout().itemAtPosition(7, 0).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(7, 0).widget().text(),
			"homepage")
		self.assertIsInstance(eed.layout().itemAtPosition(7, 1).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(7, 1).widget().text(),
			"(Web link to the experiment homepage)")
		self.assertIsInstance(eed.layout().itemAtPosition(8, 0).widget(),
			QLineEdit)
		self.assertEqual(eed.layout().itemAtPosition(8, 0).widget(),
			eed.textValues["homepage"])
		self.assertEqual(eed.textValues["homepage"].text(), "www.some.exp")
		self.assertEqual(eed.textValues["homepage"].isEnabled(), True)

		self.assertIsInstance(eed.layout().itemAtPosition(9, 0).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(9, 0).widget().text(),
			"inspire")
		self.assertIsInstance(eed.layout().itemAtPosition(9, 1).widget(),
			MyLabel)
		self.assertEqual(eed.layout().itemAtPosition(9, 1).widget().text(),
			"(INSPIRE-HEP ID of the experiment record)")
		self.assertIsInstance(eed.layout().itemAtPosition(10, 0).widget(),
			QLineEdit)
		self.assertEqual(eed.layout().itemAtPosition(10, 0).widget(),
			eed.textValues["inspire"])
		self.assertEqual(eed.textValues["inspire"].text(), "1234")
		self.assertEqual(eed.textValues["inspire"].isEnabled(), True)
		self.assertEqual(eed.layout().itemAtPosition(11, 0).widget(),
			eed.acceptButton)
		self.assertEqual(eed.layout().itemAtPosition(11, 1).widget(),
			eed.cancelButton)

if __name__=='__main__':
	unittest.main()
