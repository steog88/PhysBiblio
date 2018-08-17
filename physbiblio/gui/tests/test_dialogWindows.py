#!/usr/bin/env python
"""
Test file for the physbiblio.gui.dialogWindows module.

This file is part of the physbiblio package.
"""
import sys, traceback
import os
from PySide2.QtCore import Qt, QEvent, QModelIndex
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
	from physbiblio.database import pBDB
	from physbiblio.config import pbConfig, configuration_params
	from physbiblio.gui.setuptests import *
	from physbiblio.gui.dialogWindows import *
	from physbiblio.gui.bibWindows import abstractFormulas
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
	print(traceback.format_exc())

class fake_abstractFormulas():
	"""Used to test `dailyArxivSelect.cellClick`"""
	def __init__(self):
		"""empty constructor"""
		return

	def __call__(self, p, abstract, customEditor = None, statusMessages = True):
		"""
		Save some attributes and return self.el

		Parameters: (see also `physbiblio.gui.bibWindows.abstractFormulas`)
			p: parent widget
			ab: abstract
			customEditor: widget where to store the processed text
			statusMessages: print status messages
		"""
		self.par = p
		self.abstract = abstract
		self.ce = customEditor
		self.sm = statusMessages
		self.el = abstractFormulas(p, abstract,
			customEditor = self.ce,
			statusMessages = self.sm)
		return self.el

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestConfigEditColumns(GUITestCase):
	"""
	Test configEditColumns
	"""
	@classmethod
	def setUpClass(self):
		"""set temporary settings"""
		self.oldColumns = pbConfig.params["bibtexListColumns"]
		self.defCols = [a["default"] for a in configuration_params \
			if a["name"] == "bibtexListColumns"][0]
		pbConfig.params["bibtexListColumns"] = self.defCols

	@classmethod
	def tearDownClass(self):
		"""restore previous settings"""
		pbConfig.params["bibtexListColumns"] = self.oldColumns

	def test_init(self):
		"""Test __init__"""
		p = QWidget()
		with patch("physbiblio.gui.dialogWindows.configEditColumns.initUI") \
				as _u:
			cec = configEditColumns()
			self.assertIsInstance(cec, QDialog)
			self.assertEqual(cec.parent(), None)
			_u.assert_called_once_with()
			cec = configEditColumns(p)
			self.assertIsInstance(cec, QDialog)
			self.assertEqual(cec.parent(), p)
			self.assertEqual(cec.excludeCols, [
				"crossref", "bibtex", "exp_paper", "lecture",
				"phd_thesis", "review", "proceeding", "book", "noUpdate"])
			self.assertEqual(cec.moreCols, [
				"title", "author", "journal", "volume", "pages",
				"primaryclass", "booktitle", "reportnumber"])
			self.assertEqual(cec.previousSelected,
				self.defCols)
			self.assertEqual(cec.selected,
				self.defCols)
			cec = configEditColumns(p, ['bibkey', 'author', 'title'])
			self.assertEqual(cec.previousSelected,
				['bibkey', 'author', 'title'])

	def test_onCancel(self):
		"""test onCancel"""
		cec = configEditColumns()
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			cec.onCancel()
			self.assertFalse(cec.result)
			_c.assert_called_once()

	def test_onOk(self):
		"""test onOk"""
		p = QWidget()
		cec = configEditColumns(p, ['bibkey', 'author', 'title'])
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			cec.onOk()
			self.assertTrue(cec.result)
			_c.assert_called_once()
		self.assertEqual(cec.selected,
			['bibkey', 'author', 'title'])
		item = QTableWidgetItem("arxiv")
		cec.listSel.insertRow(3)
		cec.listSel.setItem(3, 0, item)
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			cec.onOk()
		self.assertEqual(cec.selected,
			['bibkey', 'author', 'title', 'arxiv'])

	def test_initUI(self):
		"""test initUI"""
		p = QWidget()
		cec = configEditColumns(p, ['bibkey', 'author', 'title'])
		self.assertIsInstance(cec.layout(), QGridLayout)
		self.assertEqual(cec.layout(), cec.gridlayout)
		self.assertIsInstance(cec.items, list)
		self.assertIsInstance(cec.allItems, list)
		self.assertIsInstance(cec.selItems, list)
		self.assertIsInstance(cec.listAll, MyDDTableWidget)
		self.assertIsInstance(cec.listSel, MyDDTableWidget)
		self.assertIsInstance(cec.layout().itemAtPosition(0, 0).widget(),
			QLabel)
		self.assertEqual(cec.layout().itemAtPosition(0, 0).widget().text(),
			"Drag and drop items to order visible columns")
		self.assertEqual(cec.layout().itemAtPosition(1, 0).widget(),
			cec.listAll)
		self.assertEqual(cec.layout().itemAtPosition(1, 1).widget(),
			cec.listSel)
		self.assertEqual(cec.allItems,
			pBDB.descriptions["entries"].keys() + cec.moreCols)
		self.assertEqual(cec.selItems, cec.previousSelected)

		self.assertEqual(cec.listSel.rowCount(), 3)
		for ix, col in enumerate(['bibkey', 'author', 'title']):
			item = cec.listSel.item(ix, 0)
			self.assertEqual(item.text(), col)
			self.assertIs(item, cec.items[ix])

		allCols = [i for i in cec.allItems
			if i not in cec.selItems and i not in cec.excludeCols]
		self.assertEqual(cec.listAll.rowCount(), len(allCols))
		for ix, col in enumerate(allCols):
			item = cec.listAll.item(ix, 0)
			self.assertEqual(item.text(), col)
			self.assertIs(item, cec.items[ix + 3])

		self.assertIsInstance(cec.acceptButton, QPushButton)
		self.assertIsInstance(cec.cancelButton, QPushButton)
		self.assertEqual(cec.acceptButton.text(), "OK")
		self.assertEqual(cec.cancelButton.text(), "Cancel")
		self.assertTrue(cec.cancelButton.autoDefault())
		self.assertEqual(cec.layout().itemAtPosition(2, 0).widget(),
			cec.acceptButton)
		self.assertEqual(cec.layout().itemAtPosition(2, 1).widget(),
			cec.cancelButton)
		with patch("physbiblio.gui.dialogWindows.configEditColumns.onOk") \
				as _f:
			QTest.mouseClick(cec.acceptButton, Qt.LeftButton)
			_f.assert_called_once_with()
		with patch("physbiblio.gui.dialogWindows.configEditColumns.onCancel") \
				as _f:
			QTest.mouseClick(cec.cancelButton, Qt.LeftButton)
			_f.assert_called_once_with()

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestConfigWindow(GUITestCase):
	"""
	Test configWindow
	"""
	@classmethod
	def setUpClass(self):
		"""set temporary settings"""
		pass

	@classmethod
	def tearDownClass(self):
		"""restore previous settings"""
		pass

	def test_init(self):
		"""Test __init__"""
		p = QWidget()
		with patch("physbiblio.gui.dialogWindows.configWindow.initUI") as _iu:
			cw = configWindow(p)
			self.assertIsInstance(cw, QDialog)
			self.assertEqual(cw.parent(), p)
			self.assertEqual(cw.textValues, [])
			_iu.assert_called_once_with()

	def test_onCancel(self):
		"""test onCancel"""
		cw = configWindow()
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			cw.onCancel()
			self.assertFalse(cw.result)
			_c.assert_called_once()

	def test_onOk(self):
		"""test onOk"""
		cw = configWindow()
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			cw.onOk()
			self.assertTrue(cw.result)
			_c.assert_called_once()

	def test_editFolder(self):
		"""test"""
		pass

	def test_editFile(self):
		"""test"""
		pass

	def test_editColumns(self):
		"""test"""
		pass

	def test_editDefCats(self):
		"""test"""
		pass

	def test_initUI(self):
		"""test"""
		pass

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestLogFileContentDialog(GUITestCase):
	"""
	Test LogFileContentDialog
	"""
	def test_init(self):
		"""test __init__"""
		p = QWidget()
		with patch("physbiblio.gui.dialogWindows." +
				"LogFileContentDialog.initUI") as _u:
			lf = LogFileContentDialog(p)
			self.assertIsInstance(lf, QDialog)
			self.assertEqual(lf.parent(), p)
			self.assertEqual(lf.title, "Log File Content")
			_u.assert_called_once_with()
		if os.path.exists(pbConfig.params["logFileName"]):
			os.remove(pbConfig.params["logFileName"])

	def test_clearLog(self):
		"""test clearLog"""
		p = QWidget()
		with open(pbConfig.params["logFileName"], "w") as _f:
			_f.write("test content")
		lf = LogFileContentDialog(p)
		ayn_str = "physbiblio.gui.dialogWindows.askYesNo"
		with patch(ayn_str, return_value = False) as _ayn:
			lf.clearLog()
			with open(pbConfig.params["logFileName"]) as _f:
				text = _f.read()
			self.assertEqual(text, "test content")
		with patch(ayn_str, return_value = True) as _ayn,\
				patch("physbiblio.gui.dialogWindows.infoMessage") as _in,\
				patch("PySide2.QtWidgets.QDialog.close") as _c:
			lf.clearLog()
			with open(pbConfig.params["logFileName"]) as _f:
				text = _f.read()
			self.assertEqual(text, "")
			_in.assert_called_once_with("Log file cleared.")
			_c.assert_called_once_with()
		if os.path.exists(pbConfig.params["logFileName"]):
			os.remove(pbConfig.params["logFileName"])
		with patch(ayn_str, return_value = True) as _ayn,\
				patch("__builtin__.open", side_effect = IOError("fake")) as _op,\
				patch("logging.Logger.exception") as _ex,\
				patch("PySide2.QtWidgets.QDialog.close") as _c:
			lf.clearLog()
			_ex.assert_called_once_with("Impossible to clear log file!")
			_c.assert_not_called()
		if os.path.exists(pbConfig.params["logFileName"]):
			os.remove(pbConfig.params["logFileName"])

	def test_initUI(self):
		"""test initUI"""
		p = QWidget()
		if os.path.exists(pbConfig.params["logFileName"]):
			os.remove(pbConfig.params["logFileName"])
		with patch("logging.Logger.exception") as _ex:
			lf = LogFileContentDialog(p)
			_ex.assert_called_once_with("Impossible to read log file!")
			self.assertIsInstance(lf.textEdit, QPlainTextEdit)
			self.assertEqual(lf.textEdit.toPlainText(),
				"Impossible to read log file!")
		with open(pbConfig.params["logFileName"], "w") as _f:
			_f.write("test content")
		lf = LogFileContentDialog(p)
		self.assertEqual(lf.windowTitle(), lf.title)
		self.assertIsInstance(lf.layout(), QVBoxLayout)
		self.assertEqual(lf.layout().spacing(), 1)
		self.assertIsInstance(lf.layout().itemAt(0).widget(), QLabel)
		self.assertEqual(lf.layout().itemAt(0).widget().text(),
			"Reading %s"%pbConfig.params["logFileName"])
		self.assertIsInstance(lf.textEdit, QPlainTextEdit)
		self.assertTrue(lf.textEdit.isReadOnly())
		self.assertEqual(lf.textEdit.toPlainText(), "test content")
		self.assertIsInstance(lf.layout().itemAt(1).widget(), QPlainTextEdit)
		self.assertEqual(lf.textEdit, lf.layout().itemAt(1).widget())
		self.assertIsInstance(lf.layout().itemAt(2).widget(), QPushButton)
		self.assertEqual(lf.layout().itemAt(2).widget(), lf.closeButton)
		self.assertTrue(lf.closeButton.autoDefault())
		self.assertEqual(lf.closeButton.text(), "Close")
		self.assertIsInstance(lf.layout().itemAt(3).widget(), QPushButton)
		self.assertEqual(lf.layout().itemAt(3).widget(), lf.clearButton)
		self.assertEqual(lf.clearButton.text(), "Clear log file")
		if os.path.exists(pbConfig.params["logFileName"]):
			os.remove(pbConfig.params["logFileName"])

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestPrintText(GUITestCase):
	"""
	Test printText
	"""
	def test_init(self):
		"""test init"""
		with patch("physbiblio.gui.dialogWindows.printText.initUI") as _u:
			pt = printText()
			_u.assert_called_once_with()
		self.assertIsInstance(pt, QDialog)
		self.assertIsInstance(pt.stopped, Signal)
		self.assertEqual(pt._wantToClose, False)
		self.assertEqual(pt.parent(), None)
		self.assertEqual(pt.title, "Redirect print")
		self.assertEqual(pt.setProgressBar, True)
		self.assertEqual(pt.totString, "emptyString")
		self.assertEqual(pt.progressString, "emptyString")
		self.assertEqual(pt.noStopButton, False)
		self.assertEqual(pt.message, None)

		p = QWidget()
		pt = printText(p, "title", False, "some tot string",
			"some progr string", True, "mymessage")
		self.assertEqual(pt.parent(), p)
		self.assertEqual(pt.title, "title")
		self.assertEqual(pt.setProgressBar, False)
		self.assertEqual(pt.totString, "some tot string")
		self.assertEqual(pt.progressString, "some progr string")
		self.assertEqual(pt.noStopButton, True)
		self.assertEqual(pt.message, "mymessage")

	def test_closeEvent(self):
		"""test closeEvent"""
		p = QWidget()
		pt = printText(p)
		e = QEvent(QEvent.Close)
		with patch("PySide2.QtCore.QEvent.ignore") as _i:
			pt.closeEvent(e)
			_i.assert_called_once_with()
		pt._wantToClose = True
		with patch("PySide2.QtWidgets.QDialog.closeEvent") as _c:
			pt.closeEvent(e)
			_c.assert_called_once_with(e)

	def test_initUI(self):
		"""test initUI"""
		p = QWidget()
		pt = printText(p, progressBar = False, noStopButton = True)
		self.assertEqual(pt.windowTitle(), "Redirect print")
		self.assertIsInstance(pt.layout(), QGridLayout)
		self.assertEqual(pt.layout(), pt.grid)
		self.assertEqual(pt.grid.spacing(), 1)
		self.assertIsInstance(pt.grid.itemAtPosition(0, 0).widget(),
			QTextEdit)
		self.assertEqual(pt.grid.itemAtPosition(0, 0).widget(),
			pt.textEdit)
		self.assertEqual(pt.textEdit.toPlainText(), "")
		self.assertIsInstance(pt.grid.itemAtPosition(1, 0).widget(),
			QPushButton)
		self.assertEqual(pt.grid.itemAtPosition(1, 0).widget(),
			pt.closeButton)
		self.assertEqual(pt.closeButton.text(), "Close")
		self.assertFalse(pt.closeButton.isEnabled())

		pt = printText(p, "title", True, "some tot string",
			"some progr string", False, "mymessage")
		self.assertIsInstance(pt.grid.itemAtPosition(0, 0).widget(),
			QLabel)
		self.assertEqual(pt.grid.itemAtPosition(0, 0).widget().text(),
			pt.message)
		self.assertIsInstance(pt.grid.itemAtPosition(1, 0).widget(),
			QTextEdit)
		self.assertEqual(pt.grid.itemAtPosition(1, 0).widget(),
			pt.textEdit)
		self.assertEqual(pt.textEdit.toPlainText(), "")
		self.assertIsInstance(pt.grid.itemAtPosition(2, 0).widget(),
			QProgressBar)
		self.assertEqual(pt.grid.itemAtPosition(2, 0).widget(),
			pt.progressBar)
		self.assertEqual(pt.progressBar.value(), -1)
		self.assertEqual(pt.progressBar.minimum(), 0)
		self.assertEqual(pt.progressBar.maximum(), 100)
		self.assertIsInstance(pt.grid.itemAtPosition(3, 0).widget(),
			QPushButton)
		self.assertEqual(pt.grid.itemAtPosition(3, 0).widget(),
			pt.cancelButton)
		self.assertEqual(pt.cancelButton.text(), "Stop")
		self.assertTrue(pt.cancelButton.autoDefault())
		with patch("physbiblio.gui.dialogWindows.printText.stopExec") as _s:
			QTest.mouseClick(pt.cancelButton, Qt.LeftButton)
			_s.assert_called_once_with()
		self.assertIsInstance(pt.grid.itemAtPosition(4, 0).widget(),
			QPushButton)
		self.assertEqual(pt.grid.itemAtPosition(4, 0).widget(),
			pt.closeButton)
		self.assertEqual(pt.closeButton.text(), "Close")
		self.assertFalse(pt.closeButton.isEnabled())
		with patch("PySide2.QtWidgets.QDialog.reject") as _s:
			QTest.mouseClick(pt.closeButton, Qt.LeftButton)
			_s.assert_not_called()
			pt.enableClose()
			self.assertTrue(pt.closeButton.isEnabled())
			QTest.mouseClick(pt.closeButton, Qt.LeftButton, delay = 10)
			_s.assert_called_once_with()

	def test_appendText(self):
		"""test appendText"""
		p = QWidget()
		pt = printText(p)
		self.assertEqual(pt.textEdit.toPlainText(), "")
		pt.appendText("abcd")
		self.assertEqual(pt.textEdit.toPlainText(), "abcd")
		pt.textEdit.moveCursor(QTextCursor.Start)
		pt.appendText("\nefgh")
		self.assertEqual(pt.textEdit.toPlainText(), "abcd\nefgh")

		pt = printText(p,
			progressBar = True,
			totStr = "process events: ",
			progrStr = "step: ")
		self.assertEqual(pt.progressBar.value(), -1)
		self.assertEqual(pt.progressBar.maximum(), 100)
		self.assertEqual(pt.textEdit.toPlainText(), "")
		pt.appendText("process events: 123 45.6\n")
		self.assertEqual(pt.textEdit.toPlainText(),
			"process events: 123 45.6\n")
		self.assertEqual(pt.progressBar.maximum(), 123)
		with patch("logging.Logger.warning") as _l:
			pt.appendText("process events: 45.6\n")
			_l.assert_called_once_with(
				'printText.progressBar cannot work with float numbers')
		self.assertEqual(pt.textEdit.toPlainText(),
			"process events: 123 45.6\n" +
			"process events: 45.6\n")
		self.assertEqual(pt.progressBar.maximum(), 123)
		self.assertEqual(pt.progressBar.value(), -1)
		pt.appendText("step: 98.7 6 54\n")
		self.assertEqual(pt.textEdit.toPlainText(),
			"process events: 123 45.6\n" +
			"process events: 45.6\n" +
			"step: 98.7 6 54\n")
		self.assertEqual(pt.progressBar.value(), 6)
		with patch("logging.Logger.warning") as _l:
			pt.appendText("step: 98.7\n")
			_l.assert_called_once_with(
				'printText.progressBar cannot work with float numbers')
		self.assertEqual(pt.textEdit.toPlainText(),
			"process events: 123 45.6\n" +
			"process events: 45.6\n" +
			"step: 98.7 6 54\n"+
			"step: 98.7\n")
		self.assertEqual(pt.progressBar.value(), 6)
		self.assertEqual(pt.progressBar.maximum(), 123)

	def test_progressBarMin(self):
		"""test progressBarMin"""
		pt = printText()
		self.assertIsInstance(pt.progressBar, QProgressBar)
		pt.progressBarMin(1234.)
		self.assertEqual(pt.progressBar.minimum(), 1234.)

	def test_progressBarMax(self):
		"""test progressBarMax"""
		pt = printText()
		self.assertIsInstance(pt.progressBar, QProgressBar)
		pt.progressBarMax(1234)
		self.assertEqual(pt.progressBar.maximum(), 1234)

	def test_stopExec(self):
		"""test stopExec"""
		self.stop = False
		def stoppedAct(a = self):
			a.stop = True
		pt = printText()
		pt.stopped.connect(stoppedAct)
		self.assertTrue(pt.cancelButton.isEnabled())
		self.assertFalse(self.stop)
		pt.stopExec()
		self.assertFalse(pt.cancelButton.isEnabled())
		self.assertTrue(self.stop)

	def test_enableClose(self):
		"""test enableClose"""
		pt = printText()
		self.assertFalse(pt.closeButton.isEnabled())
		self.assertFalse(pt._wantToClose)
		pt.enableClose()
		self.assertTrue(pt.closeButton.isEnabled())
		self.assertTrue(pt._wantToClose)

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestAdvImportDialog(GUITestCase):
	"""
	Test advImportDialog
	"""
	def test_init(self):
		"""Test __init__"""
		p = QWidget()
		with patch("physbiblio.gui.dialogWindows.advImportDialog.initUI") \
				as _iu:
			aid = advImportDialog(p)
			self.assertIsInstance(aid, QDialog)
			self.assertEqual(aid.parent(), p)
			_iu.assert_called_once_with()

	def test_onCancel(self):
		"""test onCancel"""
		aid = advImportDialog()
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			aid.onCancel()
			self.assertFalse(aid.result)
			_c.assert_called_once()

	def test_onOk(self):
		"""test onOk"""
		aid = advImportDialog()
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			aid.onOk()
			self.assertTrue(aid.result)
			_c.assert_called_once()

	def test_initUI(self):
		"""test initUI"""
		aid = advImportDialog()
		self.assertEqual(aid.windowTitle(), 'Advanced import')
		self.assertIsInstance(aid.layout(), QGridLayout)
		self.assertEqual(aid.grid, aid.layout())
		self.assertEqual(aid.grid.spacing(), 1)

		self.assertIsInstance(aid.grid.itemAtPosition(0, 0).widget(), QLabel)
		self.assertEqual(aid.grid.itemAtPosition(0, 0).widget().text(),
			"Search string: ")
		self.assertIsInstance(aid.grid.itemAtPosition(1, 0).widget(), QLabel)
		self.assertEqual(aid.grid.itemAtPosition(1, 0).widget().text(),
			"Select method: ")

		le = aid.grid.itemAtPosition(0, 1).widget()
		self.assertIsInstance(le, QLineEdit)
		self.assertEqual(le, aid.searchStr)
		self.assertEqual(le.text(), "")
		cm = aid.grid.itemAtPosition(1, 1).widget()
		self.assertIsInstance(cm, MyComboBox)
		self.assertEqual(cm, aid.comboMethod)
		self.assertEqual(cm.count(), 4)
		self.assertEqual(cm.itemText(0), "INSPIRE-HEP")
		self.assertEqual(cm.currentText(), "INSPIRE-HEP")
		self.assertEqual(cm.itemText(1), "arXiv")
		self.assertEqual(cm.itemText(2), "DOI")
		self.assertEqual(cm.itemText(3), "ISBN")

		self.assertIsInstance(aid.grid.itemAtPosition(2, 0).widget(),
			QPushButton)
		self.assertEqual(aid.grid.itemAtPosition(2, 0).widget(),
			aid.acceptButton)
		self.assertEqual(aid.acceptButton.text(), "OK")
		with patch("physbiblio.gui.dialogWindows.advImportDialog.onOk") \
				as _o:
			QTest.mouseClick(aid.acceptButton, Qt.LeftButton)
			_o.assert_called_once_with()

		self.assertIsInstance(aid.grid.itemAtPosition(2, 1).widget(),
			QPushButton)
		self.assertEqual(aid.grid.itemAtPosition(2, 1).widget(),
			aid.cancelButton)
		self.assertEqual(aid.cancelButton.text(), "Cancel")
		self.assertTrue(aid.cancelButton.autoDefault())
		with patch("physbiblio.gui.dialogWindows.advImportDialog.onCancel") \
				as _c:
			QTest.mouseClick(aid.cancelButton, Qt.LeftButton)
			_c.assert_called_once_with()

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestAdvImportSelect(GUITestCase):
	"""
	Test advImportSelect
	"""
	def test_init(self):
		"""test init"""
		p = QWidget()
		with patch("physbiblio.gui.dialogWindows.advImportSelect.initUI") as _i:
			ais = advImportSelect({"abc": "def"}, p)
			_i.assert_called_once_with()
		self.assertIsInstance(ais, objListWindow)
		self.assertEqual(ais.bibs, {"abc": "def"})
		self.assertEqual(ais.parent(), p)
		self.assertEqual(ais.checkBoxes, [])

	def test_onCancel(self):
		"""test onCancel"""
		ais = advImportSelect()
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			ais.onCancel()
			self.assertFalse(ais.result)
			_c.assert_called_once()

	def test_onOk(self):
		"""test onOk"""
		ais = advImportSelect()
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			ais.onOk()
			self.assertTrue(ais.result)
			_c.assert_called_once()

	def test_keyPressEvent(self):
		"""test keyPressEvent"""
		ais = advImportSelect()
		ais.result = True
		with patch("PySide2.QtWidgets.QDialog.close") as _oc:
			QTest.keyPress(ais, "a")
			_oc.assert_not_called()
			self.assertTrue(ais.result)
			QTest.keyPress(ais, Qt.Key_Enter)
			_oc.assert_not_called()
			self.assertTrue(ais.result)
			QTest.keyPress(ais, Qt.Key_Escape)
			_oc.assert_called_once()
			self.assertFalse(ais.result)

	def test_initUI(self):
		"""test initUI"""
		p = QWidget()
		ais = advImportSelect({
			"abc": {
				"exist": True,
				"bibpars": {
					"ID": "abc",
					"title": "Abc",
					"authors": "s\ng",
					"eprint": "1807.15000",
					"doi": "1/2/3",
				}},
			"def": {
				"exist": False,
				"bibpars": {
					"ID": "def",
					"title": "De\nf",
					"author": "SG",
					"arxiv": "1807.16000",
					"doi": "3/2/1",
				}},
			}, p)
		self.assertEqual(ais.windowTitle(), 'Advanced import - results')
		self.assertEqual(ais.layout(), ais.currLayout)
		self.assertEqual(ais.currLayout.spacing(), 1)
		self.assertIsInstance(ais.layout().itemAtPosition(0, 0).widget(),
			QLabel)
		self.assertEqual(ais.layout().itemAtPosition(0, 0).widget().text(),
			"This is the list of elements found." +
			"\nSelect the ones that you want to import:")
		self.assertIsInstance(ais.tableModel, MyImportedTableModel)
		self.assertEqual(ais.tableModel.header,
			["ID", "title", "author", "eprint", "doi"])
		self.assertEqual(ais.tableModel.bibsOrder, ["abc", "def"])
		self.assertEqual(ais.tableModel.dataList,
			[{
				"ID": "abc",
				"title": "Abc",
				"authors": "s\ng",
				"author": "s g",
				"eprint": "1807.15000",
				"doi": "1/2/3",
			},
			{
				"ID": "def",
				"title": "De f",
				"author": "SG",
				"eprint": "1807.16000",
				"arxiv": "1807.16000",
				"doi": "3/2/1",
			}])
		self.assertEqual(ais.tableModel.existList,
			[True, False])

		self.assertIsInstance(ais.layout().itemAtPosition(3, 0).widget(),
			QCheckBox)
		self.assertEqual(ais.layout().itemAtPosition(3, 0).widget().text(),
			"Ask categories at the end?")
		self.assertEqual(ais.layout().itemAtPosition(3, 0).widget(),
			ais.askCats)
		self.assertTrue(ais.layout().itemAtPosition(3, 0).widget().isChecked())
		self.assertIsInstance(
			ais.layout().itemAtPosition(4, 0).widget(),
			QPushButton)
		self.assertEqual(
			ais.layout().itemAtPosition(4, 0).widget(),
			ais.acceptButton)
		self.assertEqual(
			ais.acceptButton.text(),
			"OK")
		self.assertIsInstance(
			ais.layout().itemAtPosition(5, 0).widget(),
			QPushButton)
		self.assertEqual(
			ais.layout().itemAtPosition(5, 0).widget(),
			ais.cancelButton)
		self.assertEqual(
			ais.cancelButton.text(),
			"Cancel")
		self.assertTrue(ais.cancelButton.autoDefault())
		with patch("physbiblio.gui.dialogWindows.advImportSelect.onOk") as _o:
			QTest.mouseClick(ais.acceptButton, Qt.LeftButton)
			_o.assert_called_once_with()
		with patch("physbiblio.gui.dialogWindows.advImportSelect.onCancel") \
				as _o:
			QTest.mouseClick(ais.cancelButton, Qt.LeftButton)
			_o.assert_called_once_with()

		with patch("physbiblio.gui.commonClasses.objListWindow." +
				"addFilterInput") as _afi,\
				patch("physbiblio.gui.commonClasses.objListWindow." +
					"setProxyStuff") as _sps,\
				patch("physbiblio.gui.commonClasses.objListWindow." +
					"finalizeTable") as _ft:
			ais.initUI()
			_afi.assert_called_once_with("Filter entries", gridPos = (1, 0))
			_sps.assert_called_once_with(0, Qt.AscendingOrder)
			_ft.assert_called_once_with(gridPos = (2, 0, 1, 2))

	def test_more(self):
		"""test some empty functions"""
		ais = advImportSelect()
		self.assertEqual(None,
			ais.triggeredContextMenuEvent(0, 0, QEvent(QEvent.ContextMenu)))
		self.assertEqual(None,
			ais.handleItemEntered(QModelIndex()))
		self.assertEqual(None,
			ais.cellClick(QModelIndex()))
		self.assertEqual(None,
			ais.cellDoubleClick(QModelIndex()))

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestDailyArxivDialog(GUITestCase):
	"""
	Test dailyArxivDialog
	"""
	def test_init(self):
		"""Test __init__"""
		p = QWidget()
		with patch("physbiblio.gui.dialogWindows.dailyArxivDialog.initUI") \
				as _iu:
			dad = dailyArxivDialog(p)
			self.assertIsInstance(dad, QDialog)
			self.assertEqual(dad.parent(), p)
			_iu.assert_called_once_with()

	def test_onCancel(self):
		"""test onCancel"""
		dad = dailyArxivDialog()
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			dad.onCancel()
			self.assertFalse(dad.result)
			_c.assert_called_once()

	def test_onOk(self):
		"""test onOk"""
		dad = dailyArxivDialog()
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			dad.onOk()
			self.assertTrue(dad.result)
			_c.assert_called_once()

	def test_updateCat(self):
		"""test updateCat"""
		dad = dailyArxivDialog()
		self.assertEqual(dad.comboSub.count(), 1)
		self.assertEqual(dad.comboSub.itemText(0), "")
		for c in physBiblioWeb.webSearch["arxiv"].categories.keys():
			dad.updateCat(c)
			self.assertEqual(dad.comboSub.count(),
				1 + len(physBiblioWeb.webSearch["arxiv"].categories[c]))
			self.assertEqual(dad.comboSub.itemText(0), "--")
			for ix, sc in enumerate(
					physBiblioWeb.webSearch["arxiv"].categories[c]):
				self.assertEqual(dad.comboSub.itemText(ix + 1), sc)

	def test_initUI(self):
		"""test initUI"""
		dad = dailyArxivDialog()
		self.assertEqual(dad.windowTitle(), 'Browse arxiv daily')
		self.assertIsInstance(dad.layout(), QGridLayout)
		self.assertEqual(dad.grid, dad.layout())
		self.assertEqual(dad.grid.spacing(), 1)

		self.assertIsInstance(dad.grid.itemAtPosition(0, 0).widget(), QLabel)
		self.assertEqual(dad.grid.itemAtPosition(0, 0).widget().text(),
			"Select category: ")
		self.assertIsInstance(dad.grid.itemAtPosition(1, 0).widget(), QLabel)
		self.assertEqual(dad.grid.itemAtPosition(1, 0).widget().text(),
			"Subcategory: ")

		cc = dad.grid.itemAtPosition(0, 1).widget()
		self.assertIsInstance(cc, MyComboBox)
		self.assertEqual(cc, dad.comboCat)
		self.assertEqual(cc.count(),
			len(physBiblioWeb.webSearch["arxiv"].categories) + 1)
		self.assertEqual(cc.itemText(0), "")
		for ix, c in enumerate(sorted(
				physBiblioWeb.webSearch["arxiv"].categories.keys())):
			self.assertEqual(cc.itemText(ix + 1), c)
		with patch("physbiblio.gui.dialogWindows.dailyArxivDialog.updateCat") \
				as _cic:
			dad.comboCat.setCurrentText("hep-ph")
			_cic.assert_called_once_with("hep-ph")
		cs = dad.grid.itemAtPosition(1, 1).widget()
		self.assertIsInstance(cs, MyComboBox)
		self.assertEqual(cs, dad.comboSub)
		self.assertEqual(cs.count(), 1)
		self.assertEqual(cs.itemText(0), "")

		self.assertIsInstance(dad.grid.itemAtPosition(2, 0).widget(),
			QPushButton)
		self.assertEqual(dad.grid.itemAtPosition(2, 0).widget(),
			dad.acceptButton)
		self.assertEqual(dad.acceptButton.text(), "OK")
		with patch("physbiblio.gui.dialogWindows.dailyArxivDialog.onOk") \
				as _o:
			QTest.mouseClick(dad.acceptButton, Qt.LeftButton)
			_o.assert_called_once_with()

		self.assertIsInstance(dad.grid.itemAtPosition(2, 1).widget(),
			QPushButton)
		self.assertEqual(dad.grid.itemAtPosition(2, 1).widget(),
			dad.cancelButton)
		self.assertEqual(dad.cancelButton.text(), "Cancel")
		self.assertTrue(dad.cancelButton.autoDefault())
		with patch("physbiblio.gui.dialogWindows.dailyArxivDialog.onCancel") \
				as _c:
			QTest.mouseClick(dad.cancelButton, Qt.LeftButton)
			_c.assert_called_once_with()

@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestDailyArxivSelect(GUITestCase):
	"""
	Test dailyArxivSelect
	"""
	def test_init(self):
		"""test init"""
		p = QWidget()
		das = dailyArxivSelect({}, p)
		self.assertIsInstance(das, advImportSelect)

	def test_initUI(self):
		"""test initUI"""
		p = QWidget()
		with patch("PySide2.QtCore.QSortFilterProxyModel.sort") as _s,\
				patch("physbiblio.gui.commonClasses." +
					"objListWindow.finalizeTable") as _f:
			das = dailyArxivSelect({}, p)
			_s.assert_called_once_with(0, Qt.AscendingOrder)
			_f.assert_called_once_with(gridPos = (2, 0, 1, 2))
		das = dailyArxivSelect({}, p)
		self.assertEqual(das.windowTitle(), 'ArXiv daily listing - results')
		self.assertEqual(das.layout().spacing(), 1)
		self.assertIsInstance(das.layout().itemAt(0).widget(), QLabel)
		self.assertEqual(das.layout().itemAt(0).widget().text(),
			"This is the list of elements found.\n" +
				"Select the ones that you want to import:")
		self.assertIsInstance(das.tableModel, MyImportedTableModel)
		self.assertEqual(das.tableModel.header,
			["eprint", "type", "title", "author", "primaryclass"])
		self.assertEqual(das.tableModel.idName, "eprint")
		self.assertIsInstance(das.layout().itemAt(1).widget(), QLineEdit)
		self.assertEqual(das.layout().itemAt(1).widget(), das.filterInput)
		self.assertIsInstance(das.layout().itemAt(2).widget(), MyTableView)
		self.assertEqual(das.layout().itemAt(2).widget(), das.tablewidget)
		self.assertIsInstance(das.askCats, QCheckBox)
		self.assertEqual(das.askCats.text(), "Ask categories at the end?")
		self.assertTrue(das.askCats.isChecked())
		self.assertEqual(das.layout().itemAt(3).widget(), das.askCats)
		self.assertIsInstance(
			das.layout().itemAt(4).widget(),
			QPushButton)
		self.assertEqual(
			das.layout().itemAt(4).widget(),
			das.acceptButton)
		self.assertEqual(
			das.acceptButton.text(),
			"OK")
		self.assertIsInstance(
			das.layout().itemAt(5).widget(),
			QPushButton)
		self.assertEqual(
			das.layout().itemAt(5).widget(),
			das.cancelButton)
		self.assertEqual(
			das.cancelButton.text(),
			"Cancel")
		self.assertTrue(das.cancelButton.autoDefault())
		with patch("physbiblio.gui.dialogWindows.advImportSelect.onOk") as _o:
			QTest.mouseClick(das.acceptButton, Qt.LeftButton)
			_o.assert_called_once_with()
		with patch("physbiblio.gui.dialogWindows.advImportSelect.onCancel") \
				as _o:
			QTest.mouseClick(das.cancelButton, Qt.LeftButton)
			_o.assert_called_once_with()
		self.assertIsInstance(
			das.layout().itemAt(6).widget(),
			QTextEdit)
		self.assertEqual(
			das.layout().itemAt(6).widget(),
			das.abstractArea)
		self.assertEqual(das.abstractArea.toPlainText(), "Abstract")

	def test_cellClick(self):
		"""test cellClick"""
		p = QWidget()
		bibs = {"1808.00000": {
			"bibpars": {
				"eprint": "1808.00000",
				"type": "art",
				"title": "empty",
				"author": "me",
				"primaryclass": "physics",
				"abstract": "no text"
			},
			"exist": False
			},
			"1507.08204": {
			"bibpars": {
				"eprint": "1507.08204",
				"type": "art",
				"title": "Light sterile neutrinos",
				"author": "SG",
				"primaryclass": "hep-ph",
				"abstract": "some text"
			},
			"exist": False
			}}
		das = dailyArxivSelect(bibs, p)
		with patch("PySide2.QtCore.QModelIndex.isValid",
				return_value = False) as _iv:
			self.assertEqual(das.cellClick(QModelIndex()), None)
		self.assertFalse(hasattr(das, "abstractFormulas"))
		#the first row will contain the 1507.08204 entry,
		#as the order is Qt.AscendingOrder on the first column (eprint)
		ix = das.tablewidget.model().index(1, 0)
		with patch("logging.Logger.debug") as _d:
			das.cellClick(ix)
			_d.assert_called_once_with("self.abstractFormulas not present " +
				"in dailyArxivSelect. Eprint: 1808.00000")
		with patch("PySide2.QtCore.QSortFilterProxyModel.sibling",
					return_value = None) as _s,\
				patch("logging.Logger.debug") as _d:
			self.assertEqual(das.cellClick(ix), None)
			_d.assert_called_once_with('Data not valid', exc_info=True)
			_s.assert_called_once_with(1, 0, ix)
		ix = das.tablewidget.model().index(0, 0)
		das.abstractFormulas = fake_abstractFormulas()
		with patch("physbiblio.gui.bibWindows.abstractFormulas.doText") as _d:
			das.cellClick(ix)
			self.assertIsInstance(das.abstractFormulas.el, abstractFormulas)
			self.assertEqual(das.abstractFormulas.par, p)
			self.assertEqual(das.abstractFormulas.abstract,
				"some text")
			self.assertEqual(das.abstractFormulas.ce, das.abstractArea)
			self.assertEqual(das.abstractFormulas.sm, False)
			_d.assert_called_once_with()

if __name__=='__main__':
	unittest.main()
