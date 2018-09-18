#!/usr/bin/env python
"""Test file for the physbiblio.gui.bibWindows module.

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
	from physbiblio.gui.bibWindows import *
	from physbiblio.gui.mainWindow import MainWindow
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
	print(traceback.format_exc())


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestFunctions(GUITestCase):
	"""Test various functions:
	copyToClipboard, writeBibtexInfo, writeAbstract,
	editBibtex, deleteBibtex
	"""

	def test_copyToClipboard(self):
		"""test copyToClipboard"""
		with patch("logging.Logger.info") as _l:
			copyToClipboard("some text")
			_l.assert_called_once_with("Copying to clipboard: 'some text'")
		self.assertEqual(QApplication.clipboard().text(), "some text")

	def test_writeBibtexInfo(self):
		"""test writeBibtexInfo"""
		entry = {
			"bibkey": "mykey",
			"review": 0,
			"proceeding": 0,
			"book": 0,
			"phd_thesis": 0,
			"lecture": 0,
			"exp_paper": 0,
			"bibtexDict": {
				"author": "sg",
				"title": "some title",
				"journal": "AB",
				"volume": "12",
				"year": "2018",
				"pages": "1",
			},
			"ads": "",
			"isbn": "",
			"arxiv": "1234.5678",
			"doi": "a/b/12",
			"inspire": "1234",
			}
		with patch("physbiblio.database.categories.getByEntry",
				return_value=[]) as _gc,\
				patch("physbiblio.database.experiments.getByEntry",
					return_value=[]) as _ge,\
				patch("logging.Logger.debug") as _d:
			self.assertEqual(writeBibtexInfo(entry),
				"<u>mykey</u>  (use with '<u>\cite{mykey}</u>')<br/>\n"
				+ "<b>sg</b><br/>\nsome title<br/>\n<i>AB 12 (2018) 1</i>"
				+ "<br/>\n<br/>DOI of the record: <u>a/b/12</u><br/>"
				+ "arXiv ID of the record: <u>1234.5678</u><br/>"
				+ "INSPIRE-HEP ID of the record: <u>1234</u><br/>\n<br/>"
				+ "Categories: <i>None</i>\n<br/>Experiments: <i>None</i>")
			_d.assert_not_called()

		entry = {
			"bibkey": "mykey",
			"review": 0,
			"proceeding": 0,
			"book": 1,
			"phd_thesis": 0,
			"lecture": 0,
			"exp_paper": 0,
			"bibtexDict": {
				"author": "sg",
				"title": "some title",
				"volume": "12",
				"year": "2018",
				"pages": "1",
			},
			"isbn": "123456789",
			"arxiv": "",
			"doi": "a/b/12",
			"inspire": "1234",
			}
		with patch("physbiblio.database.categories.getByEntry",
				return_value=[{"name": "Main"}]) as _gc,\
				patch("physbiblio.database.experiments.getByEntry",
					return_value=[]) as _ge,\
				patch("logging.Logger.debug") as _d:
			self.assertEqual(writeBibtexInfo(entry),
				"(Book) <u>mykey</u>  (use with '<u>\cite{mykey}</u>')<br/>\n"
				+ "<b>sg</b><br/>\nsome title<br/>\n"
				+ "<br/>ISBN code of the record: <u>123456789</u><br/>"
				+ "DOI of the record: <u>a/b/12</u><br/>"
				+ "INSPIRE-HEP ID of the record: <u>1234</u><br/>\n<br/>"
				+ "Categories: <i>Main</i>\n<br/>Experiments: <i>None</i>")
			_d.assert_has_calls([
				call("KeyError: 'journal', 'volume', 'year' or 'pages' "
					+ "not in ['author', 'pages', 'title', 'volume', 'year']"),
				call("KeyError: 'ads' not in "
					+ "['arxiv', 'bibkey', 'bibtexDict', 'book', 'doi', "
					+ "'exp_paper', 'inspire', 'isbn', 'lecture', "
					+ "'phd_thesis', 'proceeding', 'review']"),
				])

		entry = {
			"bibkey": "mykey",
			"review": 1,
			"book": 0,
			"phd_thesis": 0,
			"lecture": 0,
			"exp_paper": 0,
			"bibtexDict": {
				"author": "sg",
				"journal": "AB",
				"volume": "12",
				"year": "2018",
				"pages": "1",
			},
			"arxiv": "",
			"doi": "a/b/12",
			"inspire": "1234",
			}
		with patch("physbiblio.database.categories.getByEntry",
				return_value=[{"name": "Main"}]) as _gc,\
				patch("physbiblio.database.experiments.getByEntry",
					return_value=[]) as _ge,\
				patch("logging.Logger.debug") as _d:
			self.assertEqual(writeBibtexInfo(entry),
				"(Review) <u>mykey</u>  (use with '<u>\cite{mykey}</u>')<br/>\n"
				+ "<b>sg</b><br/>\n<i>AB 12 (2018) 1</i><br/>\n<br/>"
				+ "DOI of the record: <u>a/b/12</u><br/>"
				+ "INSPIRE-HEP ID of the record: <u>1234</u><br/>\n<br/>"
				+ "Categories: <i>Main</i>\n<br/>Experiments: <i>None</i>")
			_d.assert_has_calls([
				call("KeyError: 'proceeding' not in "
					+ "['arxiv', 'bibkey', 'bibtexDict', 'book', 'doi', "
					+ "'exp_paper', 'inspire', 'lecture', 'phd_thesis', "
					+ "'review']"),
				call("KeyError: 'title' not in "
					+ "['author', 'journal', 'pages', 'volume', 'year']"),
				call("KeyError: 'isbn' not in "
					+ "['arxiv', 'bibkey', 'bibtexDict', 'book', 'doi', "
					+ "'exp_paper', 'inspire', 'lecture', 'phd_thesis', "
					+ "'review']"),
				call("KeyError: 'ads' not in "
					+ "['arxiv', 'bibkey', 'bibtexDict', 'book', 'doi', "
					+ "'exp_paper', 'inspire', 'lecture', 'phd_thesis', "
					+ "'review']"),
				])

		entry = {
			"bibkey": "mykey",
			"review": 1,
			"book": 0,
			"phd_thesis": 1,
			"lecture": 0,
			"exp_paper": 1,
			"bibtexDict": {
				"title": "some title",
				"journal": "AB",
				"volume": "12",
				"year": "2018",
				"pages": "1",
			},
			"arxiv": "",
			"ads": "",
			"isbn": "",
			"doi": "",
			"inspire": "",
			}
		with patch("physbiblio.database.categories.getByEntry",
				return_value=[{"name": "Main"}, {"name": "second"}]) as _gc,\
				patch("physbiblio.database.experiments.getByEntry",
					return_value=[{"name": "myexp"}]) as _ge,\
				patch("logging.Logger.debug") as _d:
			self.assertEqual(writeBibtexInfo(entry),
				"(Review) (PhD thesis) (Experimental paper) "
				+ "<u>mykey</u>  (use with '<u>\cite{mykey}</u>')<br/>\n"
				+ "some title<br/>\n<i>AB 12 (2018) 1</i><br/>\n<br/>"
				+ "\n<br/>"
				+ "Categories: <i>Main, second</i>\n"
				+ "<br/>Experiments: <i>myexp</i>")
			_d.assert_has_calls([
				call("KeyError: 'proceeding' not in "
					+ "['ads', 'arxiv', 'bibkey', 'bibtexDict', 'book', "
					+ "'doi', 'exp_paper', 'inspire', 'isbn', "
					+ "'lecture', 'phd_thesis', 'review']"),
				call("KeyError: 'author' not in "
					+ "['journal', 'pages', 'title', 'volume', 'year']"),
				])

		entry = {
			"bibkey": "mykey",
			"review": 0,
			"proceeding": 1,
			"book": 0,
			"phd_thesis": 0,
			"lecture": 1,
			"exp_paper": 0,
			"bibtexDict": {
				"title": "some title",
				"author": "sg",
				"journal": "AB",
				"volume": "12",
				"year": "2018",
				"pages": "1",
			},
			"arxiv": None,
			"ads": None,
			"isbn": None,
			"doi": None,
			"inspire": None,
			}
		with patch("physbiblio.database.categories.getByEntry",
				return_value=[{"name": "Main"}, {"name": "second"}]) as _gc,\
				patch("physbiblio.database.experiments.getByEntry",
					return_value=[{"name": "exp1"}, {"name": "exp2"}]) as _ge,\
				patch("logging.Logger.debug") as _d,\
				patch("pylatexenc.latex2text.LatexNodes2Text.latex_to_text",
					return_value="parsed") as _ltt,\
				patch("pylatexenc.latex2text.LatexNodes2Text.__init__",
					return_value=None) as _i:
			self.assertEqual(writeBibtexInfo(entry),
				"(Proceeding) (Lecture) "
				+ "<u>mykey</u>  (use with '<u>\cite{mykey}</u>')<br/>\n"
				+ "<b>parsed</b><br/>\nparsed<br/>\n"
				+ "<i>AB 12 (2018) 1</i><br/>\n<br/>"
				+ "\n<br/>"
				+ "Categories: <i>Main, second</i>\n"
				+ "<br/>Experiments: <i>exp1, exp2</i>")
			_d.assert_not_called()
			_i.assert_called_once_with(
				keep_inline_math=True, keep_comments=False)
			_ltt.assert_has_calls([call("sg"), call("some title")])

	def test_writeAbstract(self):
		"""test writeAbstract"""
		p = MainWindow(testing=True)
		p.bottomCenter = bibtexInfo(p)
		entry = {"abstract": "some random text"}
		with patch("physbiblio.gui.bibWindows.abstractFormulas.__init__",
				return_value=None) as _af:
			with self.assertRaises(AttributeError):
				writeAbstract(p, entry)
			_af.assert_called_once_with(p, "some random text")
		with patch("physbiblio.gui.bibWindows.abstractFormulas.doText"
				) as _dt:
			writeAbstract(p, entry)
			_dt.assert_called_once_with()

	def test_editBibtex(self):
		"""test editBibtex"""
		pass

	def test_deleteBibtex(self):
		"""test deleteBibtex"""
		p = QWidget()
		m = MainWindow(testing = True)
		m.bibtexListWindow = bibtexListWindow(m)
		with patch("physbiblio.gui.bibWindows.askYesNo",
				return_value = False) as _a, \
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _s:
			deleteBibtex(m, "mykey")
			_a.assert_called_once_with(
				"Do you really want to delete this bibtex entry "
				+ "(bibkey = 'mykey')?")
			_s.assert_called_once_with("Nothing changed")

		with patch("physbiblio.gui.bibWindows.askYesNo",
				return_value = False) as _a, \
				patch("logging.Logger.debug") as _d:
			deleteBibtex(p, "mykey")
			_a.assert_called_once_with(
				"Do you really want to delete this bibtex entry "
				+ "(bibkey = 'mykey')?")
			_d.assert_called_once_with(
				"parentObject has no attribute 'statusBarMessage'",
				exc_info=True)

		with patch("physbiblio.gui.bibWindows.askYesNo",
				return_value = True) as _a, \
				patch("physbiblio.database.entries.delete") as _c, \
				patch("PySide2.QtWidgets.QMainWindow.setWindowTitle") as _t, \
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _s, \
				patch("logging.Logger.debug") as _d:
			deleteBibtex(p, "mykey")
			_a.assert_called_once_with(
				"Do you really want to delete this bibtex entry "
				+ "(bibkey = 'mykey')?")
			_c.assert_called_once_with("mykey")
			_t.assert_not_called()
			_s.assert_not_called()
			_d.assert_has_calls([
				call("parentObject has no attribute 'recreateTable'",
					exc_info=True),
				call("parentObject has no attribute 'statusBarMessage'",
					exc_info=True)
				])

		with patch("physbiblio.gui.bibWindows.askYesNo",
				return_value = True) as _a, \
				patch("physbiblio.database.entries.delete") as _c, \
				patch("PySide2.QtWidgets.QMainWindow.setWindowTitle") as _t, \
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _s, \
				patch("physbiblio.gui.mainWindow.bibtexListWindow."
					+ "recreateTable") as _r:
			deleteBibtex(m, "mykey")
			_a.assert_called_once_with(
				"Do you really want to delete this bibtex entry "
				+ "(bibkey = 'mykey')?")
			_c.assert_called_once_with("mykey")
			_t.assert_called_once_with("PhysBiblio*")
			_s.assert_called_once_with("Bibtex entry deleted")
			_r.assert_called_once_with()


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestabstractFormulas(GUITestCase):
	"""test"""

	def test_init(self):
		"""test"""
		pass

	def test_hasLatex(self):
		"""test"""
		pass

	def test_doText(self):
		"""test"""
		pass

	def test_mathTexToQPixmap(self):
		"""test"""
		pass

	def test_prepareText(self):
		"""test"""
		pass

	def test_submitText(self):
		"""test"""
		pass


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestBibtexInfo(GUITestCase):
	"""test bibtexInfo"""

	def test_init(self):
		"""test __init__"""
		p = QWidget()
		bi = bibtexInfo(p)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestMyBibTableModel(GUITestCase):
	"""test"""

	def test_init(self):
		"""test"""
		pass

	def test_getIdentifier(self):
		"""test"""
		pass

	def test_addTypeCell(self):
		"""test"""
		pass

	def test_addPdfCell(self):
		"""test"""
		pass

	def test_addMarksCell(self):
		"""test"""
		pass

	def test_data(self):
		"""test"""
		pass

	def test_setData(self):
		"""test"""
		pass


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestBibtexList(GUITestCase):
	"""test"""

	def test_init(self):
		"""test"""
		pass

	def test_reloadColumnContents(self):
		"""test"""
		pass

	def test_changeEnableActions(self):
		"""test"""
		pass

	def test_addMark(self):
		"""test"""
		pass

	def test_enableSelection(self):
		"""test"""
		pass

	def test_clearSelection(self):
		"""test"""
		pass

	def test_selectAll(self):
		"""test"""
		pass

	def test_unselectAll(self):
		"""test"""
		pass

	def test_onOk(self):
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

	def test_downloadArxivDone(self):
		"""test"""
		pass

	def test_arxivAbstract(self):
		"""test"""
		pass

	def test_finalizeTable(self):
		"""test"""
		pass

	def test_recreateTable(self):
		"""test"""
		pass


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TesteditBibtexDialog(GUITestCase):
	"""test"""

	def test_init(self):
		"""test"""
		pass

	def test_onOk(self):
		"""test"""
		pass

	def test_updateBibkey(self):
		"""test"""
		pass

	def test_createForm(self):
		"""test"""
		pass


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestMyPdfAction(GUITestCase):
	"""test"""

	def test_init(self):
		"""test"""
		pass

	def test_returnFileName(self):
		"""test"""
		pass


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestaskPdfAction(GUITestCase):
	"""test"""

	def test_init(self):
		"""test"""
		pass

	def test_onOpenOther(self):
		"""test"""
		pass

	def test_onOpenArxiv(self):
		"""test"""
		pass

	def test_onOpenDoi(self):
		"""test"""
		pass


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestaskSelBibAction(GUITestCase):
	"""test"""

	def test_init(self):
		"""test"""
		pass

	def test_onCopyKeys(self):
		"""test"""
		pass

	def test_onCopyCites(self):
		"""test"""
		pass

	def test_onCopyBibtexs(self):
		"""test"""
		pass

	def test_onMerge(self):
		"""test"""
		pass

	def test_onClean(self):
		"""test"""
		pass

	def test_onUpdate(self):
		"""test"""
		pass

	def test_onDelete(self):
		"""test"""
		pass

	def test_onAbs(self):
		"""test"""
		pass

	def test_onArx(self):
		"""test"""
		pass

	def test_onDown(self):
		"""test"""
		pass

	def test_onExport(self):
		"""test"""
		pass

	def test_copyAllPdf(self):
		"""test"""
		pass

	def test_onCat(self):
		"""test"""
		pass

	def test_onExp(self):
		"""test"""
		pass


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestsearchBibsWindow(GUITestCase):
	"""test"""

	def test_init(self):
		"""test"""
		pass

	def test_processHistoric(self):
		"""test"""
		pass

	def test_cleanLayout(self):
		"""test"""
		pass

	def test_changeCurrentContent(self):
		"""test"""
		pass

	def test_onSave(self):
		"""test"""
		pass

	def test_onAskCats(self):
		"""test"""
		pass

	def test_onAskExps(self):
		"""test"""
		pass

	def test_onComboCatsChange(self):
		"""test"""
		pass

	def test_onComboExpsChange(self):
		"""test"""
		pass

	def test_onComboCEChange(self):
		"""test"""
		pass

	def test_getMarksValues(self):
		"""test"""
		pass

	def test_getTypeValues(self):
		"""test"""
		pass

	def test_onAddField(self):
		"""test"""
		pass

	def test_keyPressEvent(self):
		"""test"""
		pass

	def test_eventFilter(self):
		"""test"""
		pass

	def test_createForm(self):
		"""test"""
		pass


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestmergeBibtexs(GUITestCase):
	"""test"""

	def test_init(self):
		"""test"""
		pass

	def test_radioToggled(self):
		"""test"""
		pass

	def test_textModified(self):
		"""test"""
		pass

	def test_createForm(self):
		"""test"""
		pass


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestfieldsFromArxiv(GUITestCase):
	"""test"""

	def test_init(self):
		"""test"""
		pass

	def test_onOk(self):
		"""test"""
		pass

	def test_onCancel(self):
		"""test"""
		pass


if __name__=='__main__':
	unittest.main()
