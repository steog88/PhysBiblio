#!/usr/bin/env python
"""Test file for the physbiblio.gui.bibWindows module.

This file is part of the physbiblio package.
"""
import sys
import traceback
import os
from PySide2.QtCore import Qt, QModelIndex
from PySide2.QtTest import QTest
from PySide2.QtGui import QMouseEvent, QPixmap
from PySide2.QtWidgets import QMenu, QWidget

if sys.version_info[0] < 3:
	import unittest2 as unittest
	from mock import patch, call, MagicMock
else:
	import unittest
	from unittest.mock import patch, call, MagicMock

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
				"<u>mykey</u> (use with '<u>\cite{mykey}</u>')<br/>\n"
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
				"(Book) <u>mykey</u> (use with '<u>\cite{mykey}</u>')<br/>\n"
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
				"(Review) <u>mykey</u> (use with '<u>\cite{mykey}</u>')<br/>\n"
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
				+ "<u>mykey</u> (use with '<u>\cite{mykey}</u>')<br/>\n"
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
				+ "<u>mykey</u> (use with '<u>\cite{mykey}</u>')<br/>\n"
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
		p.bottomCenter = BibtexInfo(p)
		entry = {"abstract": "some random text"}
		with patch("physbiblio.gui.bibWindows.AbstractFormulas.__init__",
				return_value=None) as _af:
			with self.assertRaises(AttributeError):
				writeAbstract(p, entry)
			_af.assert_called_once_with(p, "some random text")
		with patch("physbiblio.gui.bibWindows.AbstractFormulas.doText"
				) as _dt:
			writeAbstract(p, entry)
			_dt.assert_called_once_with()

	def test_editBibtex(self):
		"""test editBibtex"""
		pBDB.bibs.lastFetched = ["fake"]
		testentry = {'bibkey': 'Gariazzo:2015rra', 'inspire': None,
			'arxiv': '1507.08204', 'ads': None, 'scholar': None,
			'doi': None, 'isbn': None, 'year': 2015,
			'link': '%s/abs/1507.08204'%pbConfig.arxivUrl,
			'comments': None, 'old_keys': None, 'crossref': None,
			'bibtex': '@Article{Gariazzo:2015rra,\n         ' \
			+ 'arxiv = "1507.08204",\n}', 'firstdate': "2018-09-01",
			'pubdate': '', 'exp_paper': 0, 'lecture': 0,
			'phd_thesis': 0, 'review': 0, 'proceeding': 0,
			'book': 0, 'noUpdate': 0, 'marks': '',
			'abstract': None, 'bibtexDict': {'arxiv': '1507.08204',
			'ENTRYTYPE': 'article', 'ID': 'Gariazzo:2015rra'},
			'title': '', 'journal': '', 'volume': '', 'number': '',
			'pages': '', 'published': '  (2015) ', 'author': ''}
		p = QDialog()
		m = MainWindow(testing=True)
		ebd = EditBibtexDialog(m, bib=None)
		ebd.onCancel()
		with patch("logging.Logger.debug") as _ld,\
				patch("physbiblio.database.entries.getByKey") as _gbk,\
				patch("physbiblio.gui.bibWindows.EditBibtexDialog.__init__",
					return_value=None) as _i:
			editBibtex(p, editKey=None, testing=ebd)
			_i.assert_called_once_with(p, bib=None)
			_ld.assert_called_once_with(
				"parentObject has no attribute 'statusBarMessage'",
				exc_info=True)
			_gbk.assert_not_called()
		with patch("logging.Logger.debug") as _ld,\
				patch("physbiblio.database.entries.getByKey") as _gbk,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm:
			editBibtex(m, editKey=None, testing=ebd)
			_sbm.assert_called_once_with("No modifications to bibtex entry")
			_ld.assert_not_called()
			_gbk.assert_not_called()

		ebd = EditBibtexDialog(m, bib=None)
		ebd.onCancel()
		with patch("logging.Logger.debug") as _ld,\
				patch("logging.Logger.warning") as _lw,\
				patch("logging.Logger.info") as _li,\
				patch("physbiblio.database.entries.getByKey",
					return_value=[testentry]) as _gbk,\
				patch("physbiblio.database.entries.prepareInsert",
					return_value={"bibkey": "", "bibtex": ""}) as _pi,\
				patch("physbiblio.database.entries.updateBibkey",
					return_value=True) as _ub,\
				patch("physbiblio.database.entries.update") as _u,\
				patch("physbiblio.database.entries.insert") as _ins,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _ffl,\
				patch("physbiblio.gui.bibWindows.EditBibtexDialog.__init__",
					return_value=None) as _i:
			editBibtex(p, editKey='Gariazzo:2015rra', testing=ebd)
			_ld.assert_called_once_with(
				"parentObject has no attribute 'statusBarMessage'",
				exc_info=True)
			_lw.assert_not_called()
			_li.assert_not_called()
			_gbk.assert_called_once_with('Gariazzo:2015rra', saveQuery=False)
			_pi.assert_not_called()
			_ub.assert_not_called()
			_u.assert_not_called()
			_ins.assert_not_called()
			_ffl.assert_not_called()
			_i.assert_called_once_with(p, bib=testentry)

		#test creation of entry, empty bibtex
		ebd = EditBibtexDialog(m, bib=testentry)
		ebd.onOk()
		ebd.textValues["bibtex"].setPlainText("")
		with patch("logging.Logger.debug") as _ld,\
				patch("logging.Logger.warning") as _lw,\
				patch("logging.Logger.info") as _li,\
				patch("physbiblio.database.entries.getByKey",
					return_value=[testentry]) as _gbk,\
				patch("physbiblio.database.entries.prepareInsert",
					return_value={"bibkey": "", "bibtex": "test"}) as _pi,\
				patch("physbiblio.database.entries.updateBibkey",
					return_value=True) as _ub,\
				patch("physbiblio.database.entries.update") as _u,\
				patch("physbiblio.database.entries.insert") as _ins,\
				patch("physbiblio.pdf.LocalPDF.renameFolder") as _rf,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _ffl,\
				patch("physbiblio.gui.bibWindows.infoMessage") as _im,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm:
			editBibtex(m, editKey=None, testing=ebd)
			_ld.assert_not_called()
			_lw.assert_not_called()
			_li.assert_not_called()
			_gbk.assert_not_called()
			_pi.assert_not_called()
			_ub.assert_not_called()
			_u.assert_not_called()
			_ins.assert_not_called()
			_rf.assert_not_called()
			_ffl.assert_not_called()
			_im.assert_called_once_with("ERROR: empty bibtex!")
			_sbm.assert_called_once_with("ERROR: empty bibtex!")

		#test creation of entry, empty bibkey inserted
		ebd = EditBibtexDialog(m, bib=testentry)
		ebd.onOk()
		ebd.textValues["bibkey"].setText("")
		with patch("logging.Logger.warning") as _lw,\
				patch("logging.Logger.info") as _li,\
				patch("physbiblio.database.entries.getByKey",
					return_value=[testentry]) as _gbk,\
				patch("physbiblio.database.entries.prepareInsert",
					return_value={"bibkey": "", "bibtex": "test"}) as _pi,\
				patch("physbiblio.database.entries.updateBibkey",
					return_value=True) as _ub,\
				patch("physbiblio.database.entries.update") as _u,\
				patch("physbiblio.database.entries.insert") as _ins,\
				patch("physbiblio.pdf.LocalPDF.renameFolder") as _rf,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _ffl,\
				patch("physbiblio.gui.bibWindows.infoMessage") as _im,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm:
			editBibtex(m, editKey=None, testing=ebd)
			_lw.assert_not_called()
			_li.assert_not_called()
			_gbk.assert_not_called()
			_pi.assert_called_once_with(testentry["bibtex"])
			_ub.assert_not_called()
			_u.assert_not_called()
			_ins.assert_not_called()
			_rf.assert_not_called()
			_ffl.assert_not_called()
			_im.assert_called_once_with("ERROR: empty bibkey!")
			_sbm.assert_called_once_with("ERROR: empty bibkey!")

		#test creation of entry, new bibtex
		ebd = EditBibtexDialog(m, bib=testentry)
		ebd.onOk()
		ebd.textValues["bibkey"].setText("")
		with patch("logging.Logger.debug") as _ld,\
				patch("logging.Logger.warning") as _lw,\
				patch("logging.Logger.info") as _li,\
				patch("physbiblio.database.entries.getByKey",
					return_value=[testentry]) as _gbk,\
				patch("physbiblio.database.entries.prepareInsert",
					return_value=testentry) as _pi,\
				patch("physbiblio.database.entries.updateBibkey",
					return_value=True) as _ub,\
				patch("physbiblio.database.entries.update") as _u,\
				patch("physbiblio.database.entries.insert") as _ins,\
				patch("physbiblio.pdf.LocalPDF.renameFolder") as _rf,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _ffl,\
				patch("physbiblio.gui.bibWindows.infoMessage") as _im,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent"
					) as _rmc,\
				patch("physbiblio.gui.mainWindow.MainWindow.mainWindowTitle"
					) as _swt:
			editBibtex(p, editKey=None, testing=ebd)
			_ld.assert_has_calls([
				call("parentObject has no attribute 'mainWindowTitle'",
					exc_info=True),
				call("parentObject has no attribute 'reloadMainContent'",
					exc_info=True),
				call("parentObject has no attribute 'statusBarMessage'",
					exc_info=True)])
			_lw.assert_not_called()
			_li.assert_not_called()
			_gbk.assert_not_called()
			_pi.assert_called_once_with(testentry["bibtex"])
			_ub.assert_not_called()
			_u.assert_not_called()
			_ins.assert_called_once_with(testentry)
			_rf.assert_not_called()
			_ffl.assert_called_once_with()
			_im.assert_not_called()
			_sbm.assert_not_called()
			_rmc.assert_not_called()
			_swt.assert_not_called()
		with patch("logging.Logger.warning") as _lw,\
				patch("logging.Logger.info") as _li,\
				patch("physbiblio.database.entries.getByKey",
					return_value=[testentry]) as _gbk,\
				patch("physbiblio.database.entries.prepareInsert",
					return_value=testentry) as _pi,\
				patch("physbiblio.database.entries.updateBibkey",
					return_value=True) as _ub,\
				patch("physbiblio.database.entries.update") as _u,\
				patch("physbiblio.database.entries.insert") as _ins,\
				patch("physbiblio.pdf.LocalPDF.renameFolder") as _rf,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _ffl,\
				patch("physbiblio.gui.bibWindows.infoMessage") as _im,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent"
					) as _rmc,\
				patch("physbiblio.gui.mainWindow.MainWindow.mainWindowTitle"
					) as _swt:
			editBibtex(m, editKey=None, testing=ebd)
			_lw.assert_not_called()
			_li.assert_not_called()
			_gbk.assert_not_called()
			_pi.assert_called_once_with(testentry["bibtex"])
			_ub.assert_not_called()
			_u.assert_not_called()
			_ins.assert_called_once_with(testentry)
			_rf.assert_not_called()
			_ffl.assert_called_once_with()
			_im.assert_not_called()
			_sbm.assert_called_once_with('Bibtex entry saved')
			_rmc.assert_called_once_with(["fake"])
			_swt.assert_called_once_with("PhysBiblio*")

		#test edit with various field contents
		#* no change bibkey: fix code?
		ebd = EditBibtexDialog(m, bib=testentry)
		ebd.onOk()
		ebd.textValues["comments"].setText("some text")
		with patch("logging.Logger.warning") as _lw,\
				patch("logging.Logger.info") as _li,\
				patch("physbiblio.database.entries.getByKey",
					return_value=[testentry]) as _gbk,\
				patch("physbiblio.database.entries.prepareInsert",
					return_value=testentry) as _pi,\
				patch("physbiblio.database.entries.updateBibkey",
					return_value=True) as _ub,\
				patch("physbiblio.database.entries.update") as _u,\
				patch("physbiblio.database.entries.insert") as _ins,\
				patch("physbiblio.pdf.LocalPDF.renameFolder") as _rf,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _ffl,\
				patch("physbiblio.gui.bibWindows.infoMessage") as _im,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent"
					) as _rmc,\
				patch("physbiblio.gui.mainWindow.MainWindow.mainWindowTitle"
					) as _swt:
			editBibtex(m, editKey="Gariazzo:2015rra", testing=ebd)
			_lw.assert_not_called()
			_li.assert_called_once_with(
				"Updating bibtex 'Gariazzo:2015rra'...")
			_gbk.assert_called_once_with('Gariazzo:2015rra', saveQuery=False)
			_pi.assert_not_called()
			_ub.assert_not_called()
			_u.assert_called_once_with(
				{'isbn': u'', 'inspire': u'', 'pubdate': u'',
				'year': u'2015', 'phd_thesis': 0,
				'bibkey': u'Gariazzo:2015rra', 'proceeding': 0,
				'ads': u'', 'review': 0, 'comments': u'some text', 'book': 0,
				'marks': '', 'lecture': 0, 'crossref': u'', 'noUpdate': 0,
				'link': u'https://arxiv.org/abs/1507.08204', 'exp_paper': 0,
				'doi': u'', 'scholar': u'', 'arxiv': u'1507.08204',
				'bibtex': u'@Article{Gariazzo:2015rra,\n         arxiv '
					+ '= "1507.08204",\n}',
				'firstdate': u'2018-09-01', 'old_keys': u'',
				'bibdict': "{u'arxiv': u'1507.08204', 'ENTRYTYPE': "
					+ "u'article', 'ID': u'Gariazzo:2015rra'}"},
				u'Gariazzo:2015rra')
			_ins.assert_not_called()
			_rf.assert_not_called()
			_ffl.assert_called_once_with()
			_im.assert_not_called()
			_sbm.assert_called_once_with('Bibtex entry saved')
			_rmc.assert_called_once_with(["fake"])
			_swt.assert_called_once_with("PhysBiblio*")

		#* invalid key
		ebd = EditBibtexDialog(m, bib=testentry)
		ebd.onOk()
		ebd.textValues["bibkey"].setText("not valid bibtex!")
		with patch("logging.Logger.warning") as _lw,\
				patch("logging.Logger.info") as _li,\
				patch("physbiblio.database.entries.getByKey",
					return_value=[testentry]) as _gbk,\
				patch("physbiblio.database.entries.prepareInsert",
					return_value=testentry) as _pi,\
				patch("physbiblio.database.entries.updateBibkey",
					return_value=True) as _ub,\
				patch("physbiblio.database.entries.update") as _u,\
				patch("physbiblio.database.entries.insert") as _ins,\
				patch("physbiblio.pdf.LocalPDF.renameFolder") as _rf,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _ffl,\
				patch("physbiblio.gui.bibWindows.infoMessage") as _im,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent"
					) as _rmc,\
				patch("physbiblio.gui.mainWindow.MainWindow.mainWindowTitle"
					) as _swt:
			editBibtex(m, editKey="testkey", testing=ebd)
			_lw.assert_not_called()
			_li.assert_has_calls([
				call("Updating bibtex 'testkey'...")])
			_gbk.assert_called_once_with('testkey', saveQuery=False)
			_pi.assert_not_called()
			_ub.assert_not_called()
			_u.assert_called_once_with(
				{'isbn': u'', 'inspire': u'', 'pubdate': u'',
				'year': u'2015', 'phd_thesis': 0,
				'bibkey': u'testkey', 'proceeding': 0,
				'ads': u'', 'review': 0, 'comments': u'', 'book': 0,
				'marks': '', 'lecture': 0, 'crossref': u'', 'noUpdate': 0,
				'link': u'https://arxiv.org/abs/1507.08204', 'exp_paper': 0,
				'doi': u'', 'scholar': u'', 'arxiv': u'1507.08204',
				'bibtex': u'@Article{Gariazzo:2015rra,\n         arxiv '
					+ '= "1507.08204",\n}',
				'firstdate': u'2018-09-01', 'old_keys': u'',
				'bibdict': "{u'arxiv': u'1507.08204', 'ENTRYTYPE': "
					+ "u'article', 'ID': u'Gariazzo:2015rra'}"},
				u'testkey')
			_ins.assert_not_called()
			_rf.assert_not_called()
			_ffl.assert_called_once_with()
			_im.assert_not_called()
			_sbm.assert_called_once_with('Bibtex entry saved')
			_rmc.assert_called_once_with(["fake"])
			_swt.assert_called_once_with("PhysBiblio*")

		#* with update bibkey, updateBibkey successful
		ebd = EditBibtexDialog(m, bib=testentry)
		ebd.onOk()
		ebd.textValues["old_keys"].setText("old")
		with patch("logging.Logger.warning") as _lw,\
				patch("logging.Logger.info") as _li,\
				patch("physbiblio.database.entries.getByKey",
					return_value=[testentry]) as _gbk,\
				patch("physbiblio.database.entries.prepareInsert",
					return_value=testentry) as _pi,\
				patch("physbiblio.database.entries.updateBibkey",
					return_value=True) as _ub,\
				patch("physbiblio.database.entries.update") as _u,\
				patch("physbiblio.database.entries.insert") as _ins,\
				patch("physbiblio.pdf.LocalPDF.renameFolder") as _rf,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _ffl,\
				patch("physbiblio.gui.bibWindows.infoMessage") as _im,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent"
					) as _rmc,\
				patch("physbiblio.gui.mainWindow.MainWindow.mainWindowTitle"
					) as _swt:
			editBibtex(m, editKey="testkey", testing=ebd)
			_lw.assert_not_called()
			_li.assert_has_calls([
				call("New bibtex key (Gariazzo:2015rra) for "
					+ "element 'testkey'..."),
				call("Updating bibtex 'Gariazzo:2015rra'...")])
			_gbk.assert_called_once_with('testkey', saveQuery=False)
			_pi.assert_not_called()
			_ub.assert_called_once_with('testkey', u'Gariazzo:2015rra')
			_u.assert_called_once_with(
				{'isbn': u'', 'inspire': u'', 'pubdate': u'',
				'year': u'2015', 'phd_thesis': 0,
				'bibkey': u'Gariazzo:2015rra', 'proceeding': 0,
				'ads': u'', 'review': 0, 'comments': u'', 'book': 0,
				'marks': '', 'lecture': 0, 'crossref': u'', 'noUpdate': 0,
				'link': u'https://arxiv.org/abs/1507.08204', 'exp_paper': 0,
				'doi': u'', 'scholar': u'', 'arxiv': u'1507.08204',
				'bibtex': u'@Article{Gariazzo:2015rra,\n         arxiv '
					+ '= "1507.08204",\n}',
				'firstdate': u'2018-09-01', 'old_keys': u'old testkey',
				'bibdict': "{u'arxiv': u'1507.08204', 'ENTRYTYPE': "
					+ "u'article', 'ID': u'Gariazzo:2015rra'}"},
				u'Gariazzo:2015rra')
			_ins.assert_not_called()
			_rf.assert_called_once_with('testkey', u'Gariazzo:2015rra')
			_ffl.assert_called_once_with()
			_im.assert_not_called()
			_sbm.assert_called_once_with('Bibtex entry saved')
			_rmc.assert_called_once_with(["fake"])
			_swt.assert_called_once_with("PhysBiblio*")

		#* with update bibkey, updateBibkey unsuccessful
		ebd = EditBibtexDialog(m, bib=testentry)
		ebd.onOk()
		with patch("logging.Logger.warning") as _lw,\
				patch("logging.Logger.info") as _li,\
				patch("physbiblio.database.entries.getByKey",
					return_value=[testentry]) as _gbk,\
				patch("physbiblio.database.entries.prepareInsert",
					return_value=testentry) as _pi,\
				patch("physbiblio.database.entries.updateBibkey",
					return_value=False) as _ub,\
				patch("physbiblio.database.entries.update") as _u,\
				patch("physbiblio.database.entries.insert") as _ins,\
				patch("physbiblio.pdf.LocalPDF.renameFolder") as _rf,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _ffl,\
				patch("physbiblio.gui.bibWindows.infoMessage") as _im,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent"
					) as _rmc,\
				patch("physbiblio.gui.mainWindow.MainWindow.mainWindowTitle"
					) as _swt:
			editBibtex(m, editKey="testkey", testing=ebd)
			_lw.assert_called_once_with("Cannot update bibtex key: "
				+ "already present. Restoring previous one.")
			_li.assert_has_calls([
				call("New bibtex key (Gariazzo:2015rra) for "
					+ "element 'testkey'..."),
				call("Updating bibtex 'testkey'...")])
			_gbk.assert_called_once_with('testkey', saveQuery=False)
			_pi.assert_not_called()
			_ub.assert_called_once_with('testkey', u'Gariazzo:2015rra')
			_u.assert_called_once_with(
				{'isbn': u'', 'inspire': u'', 'pubdate': u'',
				'year': u'2015', 'phd_thesis': 0,
				'bibkey': u'testkey', 'proceeding': 0,
				'ads': u'', 'review': 0, 'comments': u'', 'book': 0,
				'marks': '', 'lecture': 0, 'crossref': u'', 'noUpdate': 0,
				'link': u'https://arxiv.org/abs/1507.08204', 'exp_paper': 0,
				'doi': u'', 'scholar': u'', 'arxiv': u'1507.08204',
				'bibtex': u'@Article{testkey,\n         arxiv '
					+ '= "1507.08204",\n}',
				'firstdate': u'2018-09-01', 'old_keys': u'testkey',
				'bibdict': "{u'arxiv': u'1507.08204', 'ENTRYTYPE': "
					+ "u'article', 'ID': u'Gariazzo:2015rra'}"},
				u'testkey')
			_ins.assert_not_called()
			_rf.assert_not_called()
			_ffl.assert_called_once_with()
			_im.assert_not_called()
			_sbm.assert_called_once_with('Bibtex entry saved')
			_rmc.assert_called_once_with(["fake"])
			_swt.assert_called_once_with("PhysBiblio*")

		#* with update bibkey, old_keys existing
		ebd = EditBibtexDialog(m, bib=testentry)
		ebd.onOk()
		ebd.textValues["old_keys"].setText("testkey")
		with patch("logging.Logger.warning") as _lw,\
				patch("logging.Logger.info") as _li,\
				patch("physbiblio.database.entries.getByKey",
					return_value=[testentry]) as _gbk,\
				patch("physbiblio.database.entries.prepareInsert",
					return_value=testentry) as _pi,\
				patch("physbiblio.database.entries.updateBibkey",
					return_value=False) as _ub,\
				patch("physbiblio.database.entries.update") as _u,\
				patch("physbiblio.database.entries.insert") as _ins,\
				patch("physbiblio.pdf.LocalPDF.renameFolder") as _rf,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _ffl,\
				patch("physbiblio.gui.bibWindows.infoMessage") as _im,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent"
					) as _rmc,\
				patch("physbiblio.gui.mainWindow.MainWindow.mainWindowTitle"
					) as _swt:
			editBibtex(m, editKey="testkey", testing=ebd)
			_lw.assert_called_once_with("Cannot update bibtex key: "
				+ "already present. Restoring previous one.")
			_li.assert_has_calls([
				call("New bibtex key (Gariazzo:2015rra) for "
					+ "element 'testkey'..."),
				call("Updating bibtex 'testkey'...")])
			_gbk.assert_called_once_with('testkey', saveQuery=False)
			_pi.assert_not_called()
			_ub.assert_called_once_with('testkey', u'Gariazzo:2015rra')
			_u.assert_called_once_with(
				{'isbn': u'', 'inspire': u'', 'pubdate': u'',
				'year': u'2015', 'phd_thesis': 0,
				'bibkey': u'testkey', 'proceeding': 0,
				'ads': u'', 'review': 0, 'comments': u'', 'book': 0,
				'marks': '', 'lecture': 0, 'crossref': u'', 'noUpdate': 0,
				'link': u'https://arxiv.org/abs/1507.08204', 'exp_paper': 0,
				'doi': u'', 'scholar': u'', 'arxiv': u'1507.08204',
				'bibtex': u'@Article{testkey,\n         arxiv '
					+ '= "1507.08204",\n}',
				'firstdate': u'2018-09-01', 'old_keys': u'testkey',
				'bibdict': "{u'arxiv': u'1507.08204', 'ENTRYTYPE': "
					+ "u'article', 'ID': u'Gariazzo:2015rra'}"},
				u'testkey')
			_ins.assert_not_called()
			_rf.assert_not_called()
			_ffl.assert_called_once_with()
			_im.assert_not_called()
			_sbm.assert_called_once_with('Bibtex entry saved')
			_rmc.assert_called_once_with(["fake"])
			_swt.assert_called_once_with("PhysBiblio*")

	def test_deleteBibtex(self):
		"""test deleteBibtex"""
		p = QWidget()
		m = MainWindow(testing=True)
		m.bibtexListWindow = BibtexListWindow(m, bibs=[])
		with patch("physbiblio.gui.bibWindows.askYesNo",
				return_value=False) as _a, \
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _s:
			deleteBibtex(m, "mykey")
			_a.assert_called_once_with(
				"Do you really want to delete this bibtex entry "
				+ "(bibkey = 'mykey')?")
			_s.assert_called_once_with("Nothing changed")

		with patch("physbiblio.gui.bibWindows.askYesNo",
				return_value=False) as _a, \
				patch("logging.Logger.debug") as _d:
			deleteBibtex(p, "mykey")
			_a.assert_called_once_with(
				"Do you really want to delete this bibtex entry "
				+ "(bibkey = 'mykey')?")
			_d.assert_called_once_with(
				"parentObject has no attribute 'statusBarMessage'",
				exc_info=True)

		with patch("physbiblio.gui.bibWindows.askYesNo",
				return_value=True) as _a, \
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
				return_value=True) as _a, \
				patch("physbiblio.database.entries.delete") as _c, \
				patch("PySide2.QtWidgets.QMainWindow.setWindowTitle") as _t, \
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _s, \
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
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
class TestAbstractFormulas(GUITestCase):
	"""test the AbstractFormulas class"""

	def test_init(self):
		"""test __init__"""
		m = MainWindow(testing=True)
		m.bottomCenter = BibtexInfo(m)
		af = AbstractFormulas(m, "test text")
		self.assertEqual(af.fontsize, pbConfig.params["bibListFontSize"])
		self.assertEqual(af.mainWin, m)
		self.assertEqual(af.statusMessages, True)
		self.assertEqual(af.editor, m.bottomCenter.text)
		self.assertIsInstance(af.document, QTextDocument)
		self.assertEqual(af.editor.document(), af.document)
		self.assertEqual(af.abstractTitle, "<b>Abstract:</b><br/>")
		self.assertEqual(af.text, "<b>Abstract:</b><br/>test text")

		bi = BibtexInfo()
		af = AbstractFormulas(m, "test text",
			fontsize=99,
			abstractTitle="Title",
			customEditor=bi.text,
			statusMessages="a")
		self.assertEqual(af.fontsize, 99)
		self.assertEqual(af.mainWin, m)
		self.assertEqual(af.statusMessages, "a")
		self.assertEqual(af.editor, bi.text)
		self.assertIsInstance(af.document, QTextDocument)
		self.assertEqual(af.editor.document(), af.document)
		self.assertEqual(af.abstractTitle, "Title")
		self.assertEqual(af.text, "Titletest text")

	def test_hasLatex(self):
		"""test hasLatex"""
		m = MainWindow(testing=True)
		m.bottomCenter = BibtexInfo(m)
		af = AbstractFormulas(m, "test text")
		self.assertEqual(af.hasLatex(), False)
		af = AbstractFormulas(m, "test tex $f_e$ equation")
		self.assertEqual(af.hasLatex(), True)

	def test_doText(self):
		"""test doText"""
		m = MainWindow(testing=True)
		bi = BibtexInfo(m)
		af = AbstractFormulas(m, "test text", customEditor=bi.text)
		with patch("PySide2.QtWidgets.QTextEdit.setHtml") as _ih,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm:
			af.doText()
			_ih.assert_called_once_with(af.text)
			_sbm.assert_not_called()

		af = AbstractFormulas(m, "test text with $f_e$ equation",
			customEditor=bi.text)
		with patch("PySide2.QtWidgets.QTextEdit.setHtml") as _ih,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm,\
				patch("physbiblio.gui.threadElements.thread_processLatex."
					+ "__init__", return_value=None) as _pl:
			with self.assertRaises(AttributeError):
				af.doText()
			_sbm.assert_called_once_with("Parsing LaTeX...")
			_ih.assert_called_once_with(
				"%sProcessing LaTeX formulas..."%af.abstractTitle)
			_pl.assert_called_once_with(af.prepareText, m)
		with patch("PySide2.QtWidgets.QTextEdit.setHtml") as _ih,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm,\
				patch("physbiblio.gui.commonClasses.MyThread.start") as _s,\
				patch("physbiblio.gui.bibWindows.AbstractFormulas."
					+ "submitText") as _st:
			af.doText()
			_sbm.assert_called_once_with("Parsing LaTeX...")
			_ih.assert_called_once_with(
				"%sProcessing LaTeX formulas..."%af.abstractTitle)
			_s.assert_called_once_with()
			self.assertIsInstance(af.thr, thread_processLatex)
			images, text = af.prepareText()
			_st.assert_not_called()
			af.thr.passData.emit(images, text)
			_st.assert_called_once_with(images, text)

	def test_mathTexToQPixmap(self):
		"""test mathTex_to_QPixmap"""
		m = MainWindow(testing=True)
		bi = BibtexInfo(m)
		af = AbstractFormulas(m, r"test $\nu_\mu$ with $f_e$ equation",
			customEditor=bi.text)
		qi = af.mathTex_to_QPixmap(r"$\nu_\mu$")
		self.assertIsInstance(qi, QImage)
		with patch("matplotlib.figure.Figure.__init__",
				return_value=None) as _fi,\
				self.assertRaises(AttributeError):
			qi = af.mathTex_to_QPixmap(r"$\nu_\mu$")
			_fi.assert_called_once_with()
		with patch("matplotlib.axes.Axes.text",
				return_value=None) as _t,\
				self.assertRaises(AttributeError):
			qi = af.mathTex_to_QPixmap(r"$\nu_\mu$")
			_t.assert_called_once_with(0, 0, r"$\nu_\mu$",
				ha='left', va='bottom',
				fontsize=pbConfig.params["bibListFontSize"])
		with patch("matplotlib.backends.backend_agg."
				+ "FigureCanvasAgg.print_to_buffer",
					return_value=("buf", ["size0", "size1"])) as _ptb,\
				patch("PySide2.QtGui.QImage.__init__",
					return_value=None) as _qii,\
				self.assertRaises(AttributeError):
			qi = af.mathTex_to_QPixmap(r"$\nu_\mu$")
			_ptb.assert_called_once_with()
			_qii.assert_calle_once_with("buf",
				"size0", "size1", QImage.Format_ARGB32)

	def test_prepareText(self):
		"""test prepareText"""
		m = MainWindow(testing=True)
		bi = BibtexInfo(m)
		af = AbstractFormulas(m, r"test $\nu_\mu$ with $f_e$ equation",
			customEditor=bi.text)
		with patch("physbiblio.gui.bibWindows.AbstractFormulas."
				+ "mathTex_to_QPixmap", side_effect=["a", "b"]) as _mq:
			i, t = af.prepareText()
			self.assertEqual(i, ["a", "b"])
			self.assertEqual(t,
				"<b>Abstract:</b><br/>"
				+ "test <img src=\"mydata://image0.png\" /> "
				+ "with <img src=\"mydata://image1.png\" /> equation")
			_mq.assert_has_calls([
				call(r"$\nu_\mu$"),
				call("$f_e$")])

	def test_submitText(self):
		"""test submitText"""
		m = MainWindow(testing=True)
		bi = BibtexInfo(m)
		af = AbstractFormulas(m, r"test $\nu_\mu$ with $f_e$ equation",
			customEditor=bi.text)
		images, text = af.prepareText()
		with patch("PySide2.QtGui.QTextDocument.addResource") as _ar,\
				patch("PySide2.QtWidgets.QTextEdit.setHtml") as _ih,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm:
			af.submitText(images, text)
			_ar.assert_has_calls([
				call(QTextDocument.ImageResource,
					QUrl("mydata://image0.png"), images[0]),
				call(QTextDocument.ImageResource,
					QUrl("mydata://image1.png"), images[1])])
			_ih.assert_called_once_with(text)
			_sbm.assert_called_once_with("Latex processing done!")


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestBibtexInfo(GUITestCase):
	"""test BibtexInfo"""

	def test_init(self):
		"""test __init__"""
		p = QWidget()
		bi = BibtexInfo()
		self.assertEqual(bi.parent(), None)

		bi = BibtexInfo(parent=p)
		self.assertIsInstance(bi, QFrame)
		self.assertEqual(bi.parent(), p)
		self.assertIsInstance(bi.layout(), QHBoxLayout)
		self.assertIsInstance(bi.text, QTextEdit)
		self.assertIsInstance(bi.text.font(), QFont)
		self.assertEqual(bi.text.font().pointSize(),
			pbConfig.params["bibListFontSize"])
		self.assertEqual(bi.text.isReadOnly(), True)
		self.assertEqual(bi.layout().itemAt(0).widget(),
			bi.text)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestMyBibTableModel(GUITestCase):
	"""test the `MyBibTableModel` methods"""

	def test_init(self):
		"""test __init__"""
		p = QWidget()
		biblist = [{"bibkey": "a"}, {"bibkey": "b"}]
		header = ["A", "B", "C"]
		tm = MyBibTableModel(p, biblist, header)
		self.assertIsInstance(tm, MyTableModel)
		self.assertEqual(tm.mainWin, None)
		self.assertIsInstance(tm.latexToText, LatexNodes2Text)
		self.assertEqual(tm.typeClass, "Bibs")
		self.assertEqual(tm.dataList, biblist)
		self.assertEqual(tm.stdCols, [])
		self.assertEqual(tm.addCols, ["bibtex"])
		self.assertEqual(tm.lenStdCols, 0)
		self.assertEqual(tm.header, header + ["bibtex"])
		self.assertEqual(tm.parentObj, p)
		self.assertEqual(tm.previous, [])
		self.assertEqual(tm.ask, False)

		with patch("physbiblio.gui.bibWindows.MyBibTableModel.prepareSelected"
				) as _ps,\
				patch("pylatexenc.latex2text.LatexNodes2Text.__init__",
					return_value=None) as _il:
			tm = MyBibTableModel(p, biblist, header,
				stdCols=["s1", "s2"],
				addCols=["a1", "a2"],
				askBibs=True,
				previous=[1, 2, 3],
				mainWin="m")
			_il.assert_called_once_with(
				keep_inline_math=False, keep_comments=False)
			_ps.assert_called_once_with()
		self.assertIsInstance(tm, MyTableModel)
		self.assertEqual(tm.mainWin, "m")
		self.assertIsInstance(tm.latexToText, LatexNodes2Text)
		self.assertEqual(tm.typeClass, "Bibs")
		self.assertEqual(tm.dataList, biblist)
		self.assertEqual(tm.stdCols, ["s1", "s2"])
		self.assertEqual(tm.addCols, ["a1", "a2", "bibtex"])
		self.assertEqual(tm.lenStdCols, 2)
		self.assertEqual(tm.header, header + ["bibtex"])
		self.assertEqual(tm.parentObj, p)
		self.assertEqual(tm.previous, [1, 2, 3])
		self.assertEqual(tm.ask, True)

	def test_getIdentifier(self):
		"""test getIdentifier"""
		p = QWidget()
		biblist = [{"bibkey": "a"}, {"bibkey": "b"}]
		header = ["A", "B", "C"]
		tm = MyBibTableModel(p, biblist, header)
		self.assertEqual(tm.getIdentifier(biblist[0]), "a")
		self.assertEqual(tm.getIdentifier(biblist[1]), "b")

	def test_addTypeCell(self):
		"""test addTypeCell"""
		p = QWidget()
		biblist = [{
			"bibkey": "a",
			"review": 1,
			"proceeding": 1,
			"book": 1,
			"phd_thesis": 1,
			"lecture": 1,
			"exp_paper": 1,
			}]
		header = ["A", "B", "C"]
		tm = MyBibTableModel(p, biblist, header)
		self.assertEqual(tm.addTypeCell(biblist[0]),
			"Book, Experimental paper, Lecture, "
			+ "PhD thesis, Proceeding, Review")

		biblist = [{
			"bibkey": "a",
			"review": 1,
			"proceeding": 0,
			"book": 0,
			"phd_thesis": 0,
			"lecture": 0,
			"exp_paper": 0,
			}]
		self.assertEqual(tm.addTypeCell(biblist[0]), "Review")

		biblist = [{
			"bibkey": "a",
			"review": 0,
			"proceeding": 0,
			"book": 0,
			"phd_thesis": 0,
			"lecture": 0,
			"exp_paper": 0,
			}]
		self.assertEqual(tm.addTypeCell(biblist[0]), "")

		biblist = [{
			"bibkey": "a",
			"review": 0,
			"proceeding": 0,
			"phd_thesis": 0,
			"lecture": 0,
			"exp_paper": 0,
			}]
		with patch("logging.Logger.debug") as _d:
			self.assertEqual(tm.addTypeCell(biblist[0]), "")
			_d.assert_called_once_with(
				"Key not present: 'book'\nin ['bibkey', 'exp_paper', "
				+ "'lecture', 'phd_thesis', 'proceeding', 'review']")

	def test_addPDFCell(self):
		"""test addPDFCell"""
		biblist = [{"bibkey": "a"}]
		header = ["A", "B", "C"]
		m = BibtexListWindow(bibs=[])
		tm = MyBibTableModel(m, biblist, header)
		with patch("physbiblio.pdf.LocalPDF.getExisting",
				return_value=[]) as _ge:
			self.assertEqual(tm.addPDFCell("a"),
				(False, "no PDF"))
			_ge.assert_called_once_with("a")
		with patch("physbiblio.pdf.LocalPDF.getExisting",
				return_value=["a"]) as _ge,\
				patch("physbiblio.gui.commonClasses.MyTableModel.addImage",
					return_value="image") as _ai:
			self.assertEqual(tm.addPDFCell("a"),
				(True, "image"))
			_ge.assert_called_once_with("a")
			_ai.assert_called_once_with(
				":/images/application-pdf.png",
				m.tablewidget.rowHeight(0)*0.9)

	def test_addMarksCell(self):
		"""test addMarksCell"""
		with patch("logging.Logger.debug") as _d:
			m = BibtexListWindow(bibs=[{"bibkey": "a",
				"title": "my title A",
				"author": r"St{\'e}",
				"marks": "",
				"bibtex": "@article{A}",
				"arxiv": "1809.00000"}])
		biblist = [{"bibkey": "a"}, {"bibkey": "b"}]
		header = ["A", "B", "C"]
		tm = MyBibTableModel(m, biblist, header)
		self.assertEqual(tm.addMarksCell(None),
			(False, ""))
		self.assertEqual(tm.addMarksCell(123),
			(False, ""))
		self.assertEqual(tm.addMarksCell("r a n d o m s t r i n g"),
			(False, ""))
		with patch("physbiblio.gui.commonClasses.MyTableModel.addImages",
				return_value="called") as _ai:
			self.assertEqual(tm.addMarksCell("new,imp"),
				(True, "called"))
			_ai.assert_called_once_with(
				[':/images/emblem-important-symbolic.png',
				':/images/unread-new.png'],
				m.tablewidget.rowHeight(0)*0.9)
		with patch("physbiblio.gui.commonClasses.MyTableModel.addImage",
				return_value="called") as _ai:
			self.assertEqual(tm.addMarksCell(u"new"),
				(True, "called"))
			_ai.assert_called_once_with(':/images/unread-new.png',
				m.tablewidget.rowHeight(0)*0.9)

	def test_data(self):
		"""test data"""
		m = BibtexListWindow(bibs=[{"bibkey": "a",
			"title": "my title A",
			"author": r"St{\'e}",
			"marks": "",
			"bibtex": "@article{A}",
			"arxiv": "1809.00000"}])
		biblist = [
			{"bibkey": "a",
			"title": "my title A",
			"author": r"St{\'e}",
			"marks": "",
			"bibtex": "@article{A}",
			"arxiv": "1809.00000"},
			{"bibkey": "b",
			"title": "my title {\mu}",
			"author": "Gar",
			"bibtex": "@article{B}",
			"book": 1,
			"marks": "new,imp"}]
		header = ["bibkey", "marks", "title", "author", "arxiv"]
		addCols = ["Type", "PDF"]
		tm = MyBibTableModel(m, biblist, header+addCols,
			header, addCols, previous=["b"], askBibs=True)
		ix = tm.index(10, 0)
		self.assertEqual(tm.data(ix, Qt.CheckStateRole), None)
		ix = tm.index(0, 0)
		self.assertEqual(tm.data(ix, Qt.CheckStateRole), Qt.Unchecked)
		self.assertEqual(tm.data(ix, Qt.DisplayRole), "a")
		self.assertEqual(tm.data(ix, Qt.EditRole), "a")
		self.assertEqual(tm.data(ix, Qt.DecorationRole), None)
		ix = tm.index(1, 0)
		self.assertEqual(tm.data(ix, Qt.CheckStateRole), Qt.Checked)
		self.assertEqual(tm.data(tm.index(0, 2), Qt.DisplayRole), "my title A")
		self.assertEqual(tm.data(tm.index(0, 3), Qt.DisplayRole), u'St\xe9')
		self.assertEqual(tm.data(tm.index(0, 4), Qt.DisplayRole), "1809.00000")
		self.assertEqual(tm.data(tm.index(1, 2), Qt.DisplayRole),
			u'my title \u03bc')
		self.assertEqual(tm.data(tm.index(1, 3), Qt.DisplayRole), "Gar")
		self.assertEqual(tm.data(tm.index(1, 3), Qt.CheckStateRole), None)
		self.assertEqual(tm.data(tm.index(1, 4), Qt.DisplayRole), "")

		#check marks
		with patch("physbiblio.gui.bibWindows.MyBibTableModel.addMarksCell",
				return_value=(False, "")) as _m:
			self.assertEqual(tm.data(tm.index(0, 1), Qt.DisplayRole),
				"")
			_m.assert_called_once_with("")
		with patch("physbiblio.gui.bibWindows.MyBibTableModel.addMarksCell",
				return_value=(False, "")) as _m:
			self.assertEqual(tm.data(tm.index(1, 1), Qt.DisplayRole),
				"")
			_m.assert_called_once_with('new,imp')
		self.assertEqual(tm.data(tm.index(0, 1), Qt.DisplayRole),
			"")
		self.assertEqual(tm.data(tm.index(0, 1), Qt.DecorationRole),
			None)
		self.assertEqual(tm.data(tm.index(1, 1), Qt.DisplayRole),
			None)
		self.assertIsInstance(tm.data(tm.index(1, 1), Qt.DecorationRole),
			QPixmap)

		#check type
		with patch("physbiblio.gui.bibWindows.MyBibTableModel.addTypeCell",
				return_value="type A") as _m:
			self.assertEqual(tm.data(tm.index(0, 5), Qt.DisplayRole),
				"type A")
			_m.assert_called_once_with(biblist[0])
		with patch("physbiblio.gui.bibWindows.MyBibTableModel.addTypeCell",
				return_value="type B") as _m:
			self.assertEqual(tm.data(tm.index(1, 5), Qt.DisplayRole),
				"type B")
			_m.assert_called_once_with(biblist[1])
		self.assertEqual(tm.data(tm.index(0, 5), Qt.DisplayRole),
			"")
		self.assertEqual(tm.data(tm.index(0, 5), Qt.DecorationRole),
			None)
		self.assertEqual(tm.data(tm.index(1, 5), Qt.DisplayRole),
			"Book")
		self.assertEqual(tm.data(tm.index(1, 5), Qt.DecorationRole),
			None)

		#check pdf
		with patch("physbiblio.gui.bibWindows.MyBibTableModel.addPDFCell",
				return_value=(False, "no PDF")) as _m:
			self.assertEqual(tm.data(tm.index(0, 6), Qt.DisplayRole),
				"no PDF")
			_m.assert_called_once_with("a")
		with patch("physbiblio.gui.bibWindows.MyBibTableModel.addPDFCell",
				return_value=(False, "no PDF")) as _m:
			self.assertEqual(tm.data(tm.index(1, 6), Qt.DisplayRole),
				"no PDF")
			_m.assert_called_once_with("b")
		with patch("physbiblio.pdf.LocalPDF.getExisting",
				side_effect=[[], [], ["b"], ["b"]]) as _ge:
			self.assertEqual(tm.data(tm.index(0, 6), Qt.DisplayRole),
				"no PDF")
			_ge.assert_called_once_with("a")
			self.assertEqual(tm.data(tm.index(0, 6), Qt.DecorationRole),
				None)
			_ge.reset_mock()
			self.assertEqual(tm.data(tm.index(1, 6), Qt.DisplayRole),
				None)
			_ge.assert_called_once_with("b")
			self.assertIsInstance(tm.data(tm.index(1, 6), Qt.DecorationRole),
				QPixmap)

		tm = MyBibTableModel(m, biblist, header+addCols,
			header, addCols, previous=[], askBibs=False)
		self.assertEqual(tm.data(tm.index(0, 0), Qt.CheckStateRole), None)
		tm = MyBibTableModel(m, biblist, header+addCols,
			header, addCols, previous=[], askBibs=True)
		self.assertEqual(tm.data(tm.index(0, 0), Qt.CheckStateRole),
			Qt.Unchecked)
		tm = MyBibTableModel(m, biblist, header+addCols,
			header, addCols, previous=["a"], askBibs=True)
		self.assertEqual(tm.data(tm.index(0, 0), Qt.CheckStateRole),
			Qt.Checked)
		self.assertEqual(
			tm.setData(tm.index(0, 0), "abc", Qt.CheckStateRole), True)
		self.assertEqual(tm.data(tm.index(0, 0), Qt.CheckStateRole),
			Qt.Unchecked)
		self.assertEqual(
			tm.setData(tm.index(0, 0), Qt.Checked, Qt.CheckStateRole), True)
		self.assertEqual(tm.data(tm.index(0, 0), Qt.CheckStateRole),
			Qt.Checked)

	def test_setData(self):
		"""test setData"""
		p = QWidget()
		def connectEmit(ix1, ix2):
			"""used to test dataChanged.emit"""
			self.newEmit = ix1
		biblist = [{"bibkey": "a"}, {"bibkey": "b"}]
		header = ["A", "B", "C"]
		tm = MyBibTableModel(p, biblist, header)
		self.assertEqual(tm.selectedElements, {"a": False, "b": False})
		ix = tm.index(10, 0)
		self.newEmit = False
		tm.dataChanged.connect(connectEmit)
		self.assertEqual(tm.setData(ix, "abc", Qt.CheckStateRole), False)
		self.assertEqual(self.newEmit, False)
		ix = tm.index(0, 0)
		self.assertEqual(tm.setData(ix, Qt.Checked, Qt.CheckStateRole), True)
		self.assertEqual(tm.selectedElements, {"a": True, "b": False})
		self.assertEqual(self.newEmit, ix)
		self.newEmit = False
		self.assertEqual(tm.setData(ix, "abc", Qt.CheckStateRole), True)
		self.assertEqual(tm.selectedElements, {"a": False, "b": False})
		self.assertEqual(self.newEmit, ix)

		tm = MyBibTableModel(p, biblist, header)
		ix = tm.index(1, 0)
		self.assertEqual(tm.setData(ix, "abc", Qt.EditRole), True)
		self.assertEqual(tm.selectedElements, {"a": False, "b": False})
		self.assertEqual(tm.setData(ix, "abc", Qt.CheckStateRole), True)
		self.assertEqual(tm.selectedElements, {"a": False, "b": False})


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestCommonBibActions(GUITestCase):
	"""test CommonBibActions"""

	@classmethod
	def setUpClass(self):
		"""Define useful things"""
		super(TestCommonBibActions, self).setUpClass()
		self.mainW = MainWindow(testing=True)

	def test_init(self):
		"""test init (and `parent`)"""
		p = QWidget()
		c = CommonBibActions([{"bibkey": "abc"}])
		self.assertEqual(c.parentObj, None)
		c = CommonBibActions([{"bibkey": "abc"}], parent=p)
		self.assertEqual(c.parentObj, p)
		c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}], p)
		self.assertEqual(c.parentObj, p)
		self.assertEqual(c.parent(), p)
		self.assertEqual(c.bibs, [{"bibkey": "abc"}, {"bibkey": "def"}])
		self.assertEqual(c.keys, ["abc", "def"])

	def test_createMenuArxiv(self):
		"""test _createMenuMarkType"""
		c = CommonBibActions([
			{"bibkey": "abc", "arxiv": "1809.00000"}], self.mainW)
		c.menu = MyMenu(self.mainW)
		c._createMenuArxiv(False, "")
		self.assertEqual(c.menu.possibleActions, [])
		c._createMenuArxiv(False, None)
		self.assertEqual(c.menu.possibleActions, [])
		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.gui.bibWindows.CommonBibActions."
				+ "onAbs") as _a,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onArx") as _b:
			c._createMenuArxiv(False, "1809.00000")
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "arXiv")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			for a in c.menu.possibleActions[0][1]:
				self.assertIsInstance(a, QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"Load abstract")
			c.menu.possibleActions[0][1][0].trigger()
			_a.assert_called_once_with()
			self.assertEqual(c.menu.possibleActions[0][1][1].text(),
				"Get more fields")
			c.menu.possibleActions[0][1][1].trigger()
			_b.assert_called_once_with()

		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.gui.bibWindows.CommonBibActions."
				+ "onAbs") as _a,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onArx") as _b:
			c._createMenuArxiv(True, "")
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "arXiv")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			for a in c.menu.possibleActions[0][1]:
				self.assertIsInstance(a, QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"Load abstract")
			c.menu.possibleActions[0][1][0].trigger()
			_a.assert_called_once_with()
			self.assertEqual(c.menu.possibleActions[0][1][1].text(),
				"Get more fields")
			c.menu.possibleActions[0][1][1].trigger()
			_a.assert_called_once_with()

	def test_createMenuCopy(self):
		"""test _createMenuCopy"""
		p = QWidget()
		c = CommonBibActions([
			{"bibkey": "abc", "abstract": "", "link": ""}], p)
		c.menu = MyMenu(self.mainW)
		c._createMenuCopy(True, c.bibs[0])
		self.assertIsInstance(c.menu.possibleActions[0], list)
		self.assertEqual(c.menu.possibleActions[0][0], "Copy to clipboard")
		self.assertIsInstance(c.menu.possibleActions[0][1], list)
		self.assertEqual(len(c.menu.possibleActions[0][1]), 3)
		for a in c.menu.possibleActions[0][1]:
			self.assertIsInstance(a, QAction)
		self.assertEqual(c.menu.possibleActions[0][1][0].text(),
			"key(s)")
		self.assertEqual(c.menu.possibleActions[0][1][1].text(),
			"\cite{key(s)}")
		self.assertEqual(c.menu.possibleActions[0][1][2].text(),
			"bibtex(s)")

		c = CommonBibActions([
			{"bibkey": "abc", "abstract": "", "link": ""}], p)
		c.menu = MyMenu(self.mainW)
		c._createMenuCopy(False, c.bibs[0])
		self.assertIsInstance(c.menu.possibleActions[0], list)
		self.assertEqual(c.menu.possibleActions[0][0], "Copy to clipboard")
		self.assertIsInstance(c.menu.possibleActions[0][1], list)
		self.assertEqual(len(c.menu.possibleActions[0][1]), 3)
		for a in c.menu.possibleActions[0][1]:
			self.assertIsInstance(a, QAction)
		self.assertEqual(c.menu.possibleActions[0][1][0].text(),
			"key(s)")
		self.assertEqual(c.menu.possibleActions[0][1][1].text(),
			"\cite{key(s)}")
		self.assertEqual(c.menu.possibleActions[0][1][2].text(),
			"bibtex(s)")

		c = CommonBibActions([
			{"bibkey": "abc", "abstract": "abc", "link": "def"}], p)
		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.gui.bibWindows.CommonBibActions."
				+ "onCopyKeys") as _a,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onCopyCites") as _b,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onCopyBibtexs") as _c,\
				patch("physbiblio.gui.bibWindows."
					+ "copyToClipboard") as _d:
			c._createMenuCopy(False, c.bibs[0])
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "Copy to clipboard")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			self.assertEqual(len(c.menu.possibleActions[0][1]), 5)
			for a in c.menu.possibleActions[0][1]:
				self.assertIsInstance(a, QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"key(s)")
			self.assertEqual(c.menu.possibleActions[0][1][1].text(),
				"\cite{key(s)}")
			self.assertEqual(c.menu.possibleActions[0][1][2].text(),
				"bibtex(s)")
			self.assertEqual(c.menu.possibleActions[0][1][3].text(),
				"abstract")
			self.assertEqual(c.menu.possibleActions[0][1][4].text(),
				"link")
			_a.assert_not_called()
			c.menu.possibleActions[0][1][0].trigger()
			_a.assert_called_once_with()
			_b.assert_not_called()
			c.menu.possibleActions[0][1][1].trigger()
			_b.assert_called_once_with()
			_c.assert_not_called()
			c.menu.possibleActions[0][1][2].trigger()
			_c.assert_called_once_with()
			_d.assert_not_called()
			c.menu.possibleActions[0][1][3].trigger()
			_d.assert_called_once_with("abc")
			_d.reset_mock()
			c.menu.possibleActions[0][1][4].trigger()
			_d.assert_called_once_with("def")

	def test_createMenuInspire(self):
		"""test _createMenuInspire"""
		p = QWidget()
		c = CommonBibActions([{"bibkey": "abc"}], p)
		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.gui.bibWindows.CommonBibActions."
				+ "onComplete") as _a,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onUpdate") as _b,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onCitations") as _c:
			c._createMenuInspire(True, "")
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "INSPIRE-HEP")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			self.assertEqual(len(c.menu.possibleActions[0][1]), 4)
			for a in c.menu.possibleActions[0][1]:
				self.assertIsInstance(a, QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"Complete info (ID and auxiliary info)")
			self.assertEqual(c.menu.possibleActions[0][1][1].text(),
				"Update bibtex")
			self.assertEqual(c.menu.possibleActions[0][1][2].text(),
				"Reload bibtex")
			self.assertEqual(c.menu.possibleActions[0][1][3].text(),
				"Citation statistics")
			_a.assert_not_called()
			c.menu.possibleActions[0][1][0].trigger()
			_a.assert_called_once_with()
			_b.assert_not_called()
			c.menu.possibleActions[0][1][1].trigger()
			_b.assert_called_once_with(force=True)
			_b.reset_mock()
			c.menu.possibleActions[0][1][2].trigger()
			_b.assert_called_once_with(force=False, reloadAll=True)
			_c.assert_not_called()
			c.menu.possibleActions[0][1][3].trigger()
			_c.assert_called_once_with()

		c.menu = MyMenu(self.mainW)
		c._createMenuInspire(False, "")
		self.assertIsInstance(c.menu.possibleActions[0], list)
		self.assertEqual(c.menu.possibleActions[0][0], "INSPIRE-HEP")
		self.assertIsInstance(c.menu.possibleActions[0][1], list)
		self.assertEqual(len(c.menu.possibleActions[0][1]), 1)
		for a in c.menu.possibleActions[0][1]:
			self.assertIsInstance(a, QAction)
		self.assertEqual(c.menu.possibleActions[0][1][0].text(),
			"Complete info (ID and auxiliary info)")

		c.menu = MyMenu(self.mainW)
		c._createMenuInspire(False, None)
		self.assertIsInstance(c.menu.possibleActions[0], list)
		self.assertEqual(c.menu.possibleActions[0][0], "INSPIRE-HEP")
		self.assertIsInstance(c.menu.possibleActions[0][1], list)
		self.assertEqual(len(c.menu.possibleActions[0][1]), 1)
		for a in c.menu.possibleActions[0][1]:
			self.assertIsInstance(a, QAction)
		self.assertEqual(c.menu.possibleActions[0][1][0].text(),
			"Complete info (ID and auxiliary info)")

		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.gui.bibWindows.CommonBibActions."
				+ "onComplete") as _a,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onUpdate") as _b,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onCitations") as _c:
			c._createMenuInspire(False, "123")
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "INSPIRE-HEP")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			self.assertEqual(len(c.menu.possibleActions[0][1]), 4)
			for a in c.menu.possibleActions[0][1]:
				self.assertIsInstance(a, QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"Complete info (ID and auxiliary info)")
			self.assertEqual(c.menu.possibleActions[0][1][1].text(),
				"Update bibtex")
			self.assertEqual(c.menu.possibleActions[0][1][2].text(),
				"Reload bibtex")
			self.assertEqual(c.menu.possibleActions[0][1][3].text(),
				"Citation statistics")
			_a.assert_not_called()
			c.menu.possibleActions[0][1][0].trigger()
			_a.assert_called_once_with()
			_b.assert_not_called()
			c.menu.possibleActions[0][1][1].trigger()
			_b.assert_called_once_with(force=True)
			_b.reset_mock()
			c.menu.possibleActions[0][1][2].trigger()
			_b.assert_called_once_with(force=True, reloadAll=True)
			_c.assert_not_called()
			c.menu.possibleActions[0][1][3].trigger()
			_c.assert_called_once_with()

	def test_createMenuLinks(self):
		"""test _createMenuLinks"""
		p = QWidget()
		c = CommonBibActions([{"bibkey": "abc"}], p)
		c.menu = MyMenu(self.mainW)
		c._createMenuLinks("abc", "", "", "")
		self.assertEqual(c.menu.possibleActions, [])
		with patch("physbiblio.gui.commonClasses.guiViewEntry.openLink") as _l:
			c._createMenuLinks("abc", "123", "", "")
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "Links")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			self.assertEqual(len(c.menu.possibleActions[0][1]), 1)
			for a in c.menu.possibleActions[0][1]:
				self.assertIsInstance(a, QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"Open into arXiv")
			_l.assert_not_called()
			c.menu.possibleActions[0][1][0].trigger()
			_l.assert_called_once_with("abc", "arxiv")
		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.gui.commonClasses.guiViewEntry.openLink") as _l:
			c._createMenuLinks("abc", "", "123", "")
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "Links")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			self.assertEqual(len(c.menu.possibleActions[0][1]), 1)
			for a in c.menu.possibleActions[0][1]:
				self.assertIsInstance(a, QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"Open DOI link")
			_l.assert_not_called()
			c.menu.possibleActions[0][1][0].trigger()
			_l.assert_called_once_with("abc", "doi")
		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.gui.commonClasses.guiViewEntry.openLink") as _l:
			c._createMenuLinks("abc", "", "", "123")
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "Links")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			self.assertEqual(len(c.menu.possibleActions[0][1]), 1)
			for a in c.menu.possibleActions[0][1]:
				self.assertIsInstance(a, QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"Open into INSPIRE-HEP")
			_l.assert_not_called()
			c.menu.possibleActions[0][1][0].trigger()
			_l.assert_called_once_with("abc", "inspire")
		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.gui.commonClasses.guiViewEntry.openLink") as _l:
			c._createMenuLinks("abc", "123.456", "1/2/3", "123")
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "Links")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			self.assertEqual(len(c.menu.possibleActions[0][1]), 3)
			for a in c.menu.possibleActions[0][1]:
				self.assertIsInstance(a, QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"Open into arXiv")
			self.assertEqual(c.menu.possibleActions[0][1][1].text(),
				"Open DOI link")
			self.assertEqual(c.menu.possibleActions[0][1][2].text(),
				"Open into INSPIRE-HEP")
			_l.assert_not_called()
			c.menu.possibleActions[0][1][0].trigger()
			_l.assert_called_once_with("abc", "arxiv")
			_l.reset_mock()
			c.menu.possibleActions[0][1][1].trigger()
			_l.assert_called_once_with("abc", "doi")
			_l.reset_mock()
			c.menu.possibleActions[0][1][2].trigger()
			_l.assert_called_once_with("abc", "inspire")

	def test_createMenuMarkType(self):
		"""test _createMenuMarkType"""
		p = QWidget()
		c = CommonBibActions([
			{"bibkey": "abc",
			"marks": "imp,new",
			"review": 0,
			"proceeding": 0,
			"book": 1,
			"phd_thesis": 1,
			"lecture": 0,
			"exp_paper": 0,
			}], p)
		c.menu = MyMenu(self.mainW)
		c._createMenuMarkType(c.bibs[0])
		self.assertIsInstance(c.menu.possibleActions[0], list)
		self.assertEqual(c.menu.possibleActions[0][0], "Marks")
		self.assertIsInstance(c.menu.possibleActions[0][1], list)
		for a in c.menu.possibleActions[0][1]:
			self.assertIsInstance(a, QAction)
		self.assertIsInstance(c.menu.possibleActions[1], list)
		self.assertEqual(c.menu.possibleActions[1][0], "Type")
		self.assertIsInstance(c.menu.possibleActions[1][1], list)
		for a in c.menu.possibleActions[1][1]:
			self.assertIsInstance(a, QAction)
		self.assertEqual(c.menu.possibleActions[2], None)
		for i, m in enumerate(sorted(pBMarks.marks.keys())):
			with patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onUpdateMark") as _a:
				c.menu.possibleActions[0][1][i].trigger()
				_a.assert_called_once_with(m)
		self.assertEqual(c.menu.possibleActions[0][1][0].text(),
			"Mark as 'Bad'")
		self.assertEqual(c.menu.possibleActions[0][1][1].text(),
			"Mark as 'Favorite'")
		self.assertEqual(c.menu.possibleActions[0][1][2].text(),
			"Unmark as 'Important'")
		self.assertEqual(c.menu.possibleActions[0][1][3].text(),
			"Unmark as 'To be read'")
		self.assertEqual(c.menu.possibleActions[0][1][4].text(),
			"Mark as 'Unclear'")
		for i, (k, v) in enumerate(sorted(convertType.items())):
			with patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onUpdateType") as _a:
				c.menu.possibleActions[1][1][i].trigger()
				_a.assert_called_once_with(k)
		self.assertEqual(c.menu.possibleActions[1][1][0].text(),
			"Unset 'Book'")
		self.assertEqual(c.menu.possibleActions[1][1][1].text(),
			"Set 'Experimental paper'")
		self.assertEqual(c.menu.possibleActions[1][1][2].text(),
			"Set 'Lecture'")
		self.assertEqual(c.menu.possibleActions[1][1][3].text(),
			"Unset 'PhD thesis'")
		self.assertEqual(c.menu.possibleActions[1][1][4].text(),
			"Set 'Proceeding'")
		self.assertEqual(c.menu.possibleActions[1][1][5].text(),
			"Set 'Review'")

	def test_createMenuPDF(self):
		"""test _createMenuPDF"""
		#selection True
		p = QWidget()
		c = CommonBibActions([{"bibkey": "abc"}], p)
		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.gui.bibWindows.CommonBibActions."
				+ "onDown") as _a:
			c._createMenuPDF(True, c.bibs[0])
			self.assertEqual(len(c.menu.possibleActions), 1)
			self.assertIsInstance(c.menu.possibleActions[0], QAction)
			self.assertEqual(c.menu.possibleActions[0].text(),
				"Download PDF from arXiv")
			_a.assert_not_called()
			c.menu.possibleActions[0].trigger()
			_a.assert_called_once_with()

		#no arxiv, no doi
		c = CommonBibActions([
			{"bibkey": "abc",
			"arxiv": "",
			"doi": ""}], p)
		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.pdf.LocalPDF.getExisting",
				return_value=[]) as _ge,\
				patch("physbiblio.pdf.LocalPDF.getFilePath",
					return_value="") as _gf,\
				patch("physbiblio.pdf.LocalPDF.getFileDir",
					return_value="") as _gd,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onAddPDF") as _a:
			c._createMenuPDF(False, c.bibs[0])
			_ge.assert_called_once_with("abc", fullPath=True)
			_gf.assert_has_calls([call("abc", "arxiv"), call("abc", "doi")])
			_gd.assert_called_once_with("abc")
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "PDF")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			self.assertEqual(len(c.menu.possibleActions[0][1]), 1)
			self.assertIsInstance(c.menu.possibleActions[0][1][0], QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"Add generic PDF")
			_a.assert_not_called()
			c.menu.possibleActions[0][1][0].trigger()
			_a.assert_called_once_with()

		#only arxiv, w/o file
		c = CommonBibActions([
			{"bibkey": "abc",
			"arxiv": "1809.00000",
			"doi": ""}], p)
		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.pdf.LocalPDF.getExisting",
				return_value=[]) as _ge,\
				patch("physbiblio.pdf.LocalPDF.getFilePath",
					return_value="") as _gf,\
				patch("physbiblio.pdf.LocalPDF.getFileDir",
					return_value="") as _gd,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onDown") as _b:
			c._createMenuPDF(False, c.bibs[0])
			_ge.assert_called_once_with("abc", fullPath=True)
			_gf.assert_has_calls([call("abc", "arxiv"), call("abc", "doi")])
			_gd.assert_called_once_with("abc")
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "PDF")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			self.assertEqual(len(c.menu.possibleActions[0][1]), 3)
			self.assertIsInstance(c.menu.possibleActions[0][1][0], QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"Add generic PDF")
			self.assertEqual(c.menu.possibleActions[0][1][1], None)
			self.assertEqual(c.menu.possibleActions[0][1][2].text(),
				"Download arXiv PDF")
			_b.assert_not_called()
			c.menu.possibleActions[0][1][2].trigger()
			_b.assert_called_once_with()

		#only arxiv, w file
		c = CommonBibActions([
			{"bibkey": "abc",
			"arxiv": "",
			"doi": ""}], p)
		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.pdf.LocalPDF.getExisting",
				return_value=["arxiv.pdf"]) as _ge,\
				patch("physbiblio.pdf.LocalPDF.getFilePath",
					side_effect=["arxiv.pdf", ""]) as _gf,\
				patch("physbiblio.pdf.LocalPDF.getFileDir",
					return_value="/fd") as _gd,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onDeletePDFFile") as _a,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onCopyPDFFile") as _b,\
				patch("physbiblio.gui.commonClasses.guiViewEntry."
					+ "openLink") as _l:
			c._createMenuPDF(False, c.bibs[0])
			_ge.assert_called_once_with("abc", fullPath=True)
			_gf.assert_has_calls([call("abc", "arxiv"), call("abc", "doi")])
			_gd.assert_called_once_with("abc")
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "PDF")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			self.assertEqual(len(c.menu.possibleActions[0][1]), 5)
			self.assertIsInstance(c.menu.possibleActions[0][1][0], QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"Add generic PDF")
			self.assertEqual(c.menu.possibleActions[0][1][1], None)
			self.assertEqual(c.menu.possibleActions[0][1][2].text(),
				"Open arXiv PDF")
			self.assertEqual(c.menu.possibleActions[0][1][3].text(),
				"Delete arXiv PDF")
			self.assertEqual(c.menu.possibleActions[0][1][4].text(),
				"Copy arXiv PDF")
			_l.assert_not_called()
			c.menu.possibleActions[0][1][2].trigger()
			_l.assert_called_once_with('abc', 'file', fileArg='arxiv.pdf')
			_a.assert_not_called()
			c.menu.possibleActions[0][1][3].trigger()
			_a.assert_called_once_with('abc', 'arxiv', 'arxiv PDF')
			_b.assert_not_called()
			c.menu.possibleActions[0][1][4].trigger()
			_b.assert_called_once_with('abc', 'arxiv')

		#only doi, w/o file
		c = CommonBibActions([
			{"bibkey": "abc",
			"arxiv": "",
			"doi": "1/2/3"}], p)
		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.pdf.LocalPDF.getExisting",
				return_value=[]) as _ge,\
				patch("physbiblio.pdf.LocalPDF.getFilePath",
					return_value="") as _gf,\
				patch("physbiblio.pdf.LocalPDF.getFileDir",
					return_value="") as _gd,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onAddPDF") as _a,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onDown") as _b,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onAddPDF") as _a:
			c._createMenuPDF(False, c.bibs[0])
			_ge.assert_called_once_with("abc", fullPath=True)
			_gf.assert_has_calls([call("abc", "arxiv"), call("abc", "doi")])
			_gd.assert_called_once_with("abc")
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "PDF")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			self.assertEqual(len(c.menu.possibleActions[0][1]), 3)
			self.assertIsInstance(c.menu.possibleActions[0][1][0], QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"Add generic PDF")
			self.assertEqual(c.menu.possibleActions[0][1][1], None)
			self.assertEqual(c.menu.possibleActions[0][1][2].text(),
				"Assign DOI PDF")
			_a.assert_not_called()
			c.menu.possibleActions[0][1][2].trigger()
			_a.assert_called_once_with("doi")

		#only doi, w file
		c = CommonBibActions([
			{"bibkey": "abc",
			"arxiv": "",
			"doi": ""}], p)
		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.pdf.LocalPDF.getExisting",
				return_value=["doi.pdf"]) as _ge,\
				patch("physbiblio.pdf.LocalPDF.getFilePath",
					side_effect=["", "doi.pdf"]) as _gf,\
				patch("physbiblio.pdf.LocalPDF.getFileDir",
					return_value="/fd") as _gd,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onDeletePDFFile") as _a,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onCopyPDFFile") as _b,\
				patch("physbiblio.gui.commonClasses.guiViewEntry."
					+ "openLink") as _l:
			c._createMenuPDF(False, c.bibs[0])
			_ge.assert_called_once_with("abc", fullPath=True)
			_gf.assert_has_calls([call("abc", "arxiv"), call("abc", "doi")])
			_gd.assert_called_once_with("abc")
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "PDF")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			self.assertEqual(len(c.menu.possibleActions[0][1]), 5)
			self.assertIsInstance(c.menu.possibleActions[0][1][0], QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"Add generic PDF")
			self.assertEqual(c.menu.possibleActions[0][1][1], None)
			self.assertEqual(c.menu.possibleActions[0][1][2].text(),
				"Open DOI PDF")
			self.assertEqual(c.menu.possibleActions[0][1][3].text(),
				"Delete DOI PDF")
			self.assertEqual(c.menu.possibleActions[0][1][4].text(),
				"Copy DOI PDF")
			_l.assert_not_called()
			c.menu.possibleActions[0][1][2].trigger()
			_l.assert_called_once_with('abc', 'file', fileArg='doi.pdf')
			_a.assert_not_called()
			c.menu.possibleActions[0][1][3].trigger()
			_a.assert_called_once_with('abc', 'doi', 'DOI PDF')
			_b.assert_not_called()
			c.menu.possibleActions[0][1][4].trigger()
			_b.assert_called_once_with('abc', 'doi')

		#both, w files, no extra
		c = CommonBibActions([
			{"bibkey": "abc",
			"arxiv": "",
			"doi": ""}], p)
		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.pdf.LocalPDF.getExisting",
				return_value=["arxiv.pdf", "doi.pdf"]) as _ge,\
				patch("physbiblio.pdf.LocalPDF.getFilePath",
					side_effect=["arxiv.pdf", "doi.pdf"]) as _gf,\
				patch("physbiblio.pdf.LocalPDF.getFileDir",
					return_value="/fd") as _gd,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onDeletePDFFile") as _a,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onCopyPDFFile") as _b,\
				patch("physbiblio.gui.commonClasses.guiViewEntry."
					+ "openLink") as _l:
			c._createMenuPDF(False, c.bibs[0])
			_ge.assert_called_once_with("abc", fullPath=True)
			_gf.assert_has_calls([call("abc", "arxiv"), call("abc", "doi")])
			_gd.assert_called_once_with("abc")
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "PDF")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			self.assertEqual(len(c.menu.possibleActions[0][1]), 9)
			self.assertIsInstance(c.menu.possibleActions[0][1][0], QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"Add generic PDF")
			self.assertEqual(c.menu.possibleActions[0][1][1], None)
			self.assertEqual(c.menu.possibleActions[0][1][2].text(),
				"Open arXiv PDF")
			self.assertEqual(c.menu.possibleActions[0][1][3].text(),
				"Delete arXiv PDF")
			self.assertEqual(c.menu.possibleActions[0][1][4].text(),
				"Copy arXiv PDF")
			self.assertEqual(c.menu.possibleActions[0][1][5], None)
			self.assertEqual(c.menu.possibleActions[0][1][6].text(),
				"Open DOI PDF")
			self.assertEqual(c.menu.possibleActions[0][1][7].text(),
				"Delete DOI PDF")
			self.assertEqual(c.menu.possibleActions[0][1][8].text(),
				"Copy DOI PDF")

		#no arxiv, no doi, some extra
		c = CommonBibActions([
			{"bibkey": "abc",
			"arxiv": "",
			"doi": ""}], p)
		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.pdf.LocalPDF.getExisting",
				return_value=["a.pdf", "/fd/b.pdf"]) as _ge,\
				patch("physbiblio.pdf.LocalPDF.getFilePath",
					side_effect=["", ""]) as _gf,\
				patch("physbiblio.pdf.LocalPDF.getFileDir",
					return_value="/fd") as _gd,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onDeletePDFFile") as _a,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onCopyPDFFile") as _b,\
				patch("physbiblio.gui.commonClasses.guiViewEntry."
					+ "openLink") as _l:
			c._createMenuPDF(False, c.bibs[0])
			_ge.assert_called_once_with("abc", fullPath=True)
			_gf.assert_has_calls([call("abc", "arxiv"), call("abc", "doi")])
			_gd.assert_called_once_with("abc")
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "PDF")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			self.assertEqual(len(c.menu.possibleActions[0][1]), 8)
			self.assertIsInstance(c.menu.possibleActions[0][1][0], QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"Add generic PDF")
			self.assertEqual(c.menu.possibleActions[0][1][1], None)
			self.assertEqual(c.menu.possibleActions[0][1][2].text(),
				"Open a.pdf")
			self.assertEqual(c.menu.possibleActions[0][1][3].text(),
				"Delete a.pdf")
			self.assertEqual(c.menu.possibleActions[0][1][4].text(),
				"Copy a.pdf")
			self.assertEqual(c.menu.possibleActions[0][1][5].text(),
				"Open b.pdf")
			self.assertEqual(c.menu.possibleActions[0][1][6].text(),
				"Delete b.pdf")
			self.assertEqual(c.menu.possibleActions[0][1][7].text(),
				"Copy b.pdf")
			_l.assert_not_called()
			c.menu.possibleActions[0][1][2].trigger()
			_l.assert_called_once_with('abc', 'file', fileArg='a.pdf')
			_a.assert_not_called()
			c.menu.possibleActions[0][1][3].trigger()
			_a.assert_called_once_with('abc', 'a.pdf', 'a.pdf', 'a.pdf')
			_b.assert_not_called()
			c.menu.possibleActions[0][1][4].trigger()
			_b.assert_called_once_with('abc', 'a.pdf', 'a.pdf')
			_l.reset_mock()
			c.menu.possibleActions[0][1][5].trigger()
			_l.assert_called_once_with('abc', 'file', fileArg='b.pdf')
			_a.reset_mock()
			c.menu.possibleActions[0][1][6].trigger()
			_a.assert_called_once_with('abc', 'b.pdf', 'b.pdf', '/fd/b.pdf')
			_b.reset_mock()
			c.menu.possibleActions[0][1][7].trigger()
			_b.assert_called_once_with('abc', 'b.pdf', '/fd/b.pdf')

		#arxiv, doi, extra
		c = CommonBibActions([
			{"bibkey": "abc",
			"arxiv": "1809.00000",
			"doi": "1/2/3"}], p)
		c.menu = MyMenu(self.mainW)
		with patch("physbiblio.pdf.LocalPDF.getExisting",
				return_value=["arxiv.pdf", "doi.pdf",
					"a.pdf", "/fd/b.pdf"]) as _ge,\
				patch("physbiblio.pdf.LocalPDF.getFilePath",
					side_effect=["arxiv.pdf", "doi.pdf"]) as _gf,\
				patch("physbiblio.pdf.LocalPDF.getFileDir",
					return_value="/fd") as _gd,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onDeletePDFFile") as _a,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onCopyPDFFile") as _b,\
				patch("physbiblio.gui.commonClasses.guiViewEntry."
					+ "openLink") as _l:
			c._createMenuPDF(False, c.bibs[0])
			_ge.assert_called_once_with("abc", fullPath=True)
			_gf.assert_has_calls([call("abc", "arxiv"), call("abc", "doi")])
			_gd.assert_called_once_with("abc")
			self.assertIsInstance(c.menu.possibleActions[0], list)
			self.assertEqual(c.menu.possibleActions[0][0], "PDF")
			self.assertIsInstance(c.menu.possibleActions[0][1], list)
			self.assertEqual(len(c.menu.possibleActions[0][1]), 16)
			self.assertIsInstance(c.menu.possibleActions[0][1][0], QAction)
			self.assertEqual(c.menu.possibleActions[0][1][0].text(),
				"Add generic PDF")
			self.assertEqual(c.menu.possibleActions[0][1][1], None)
			self.assertEqual(c.menu.possibleActions[0][1][2].text(),
				"Open arXiv PDF")
			self.assertEqual(c.menu.possibleActions[0][1][3].text(),
				"Delete arXiv PDF")
			self.assertEqual(c.menu.possibleActions[0][1][4].text(),
				"Copy arXiv PDF")
			self.assertEqual(c.menu.possibleActions[0][1][5], None)
			self.assertEqual(c.menu.possibleActions[0][1][6].text(),
				"Open DOI PDF")
			self.assertEqual(c.menu.possibleActions[0][1][7].text(),
				"Delete DOI PDF")
			self.assertEqual(c.menu.possibleActions[0][1][8].text(),
				"Copy DOI PDF")
			self.assertEqual(c.menu.possibleActions[0][1][9], None)
			self.assertEqual(c.menu.possibleActions[0][1][10].text(),
				"Open a.pdf")
			self.assertEqual(c.menu.possibleActions[0][1][11].text(),
				"Delete a.pdf")
			self.assertEqual(c.menu.possibleActions[0][1][12].text(),
				"Copy a.pdf")
			self.assertEqual(c.menu.possibleActions[0][1][13].text(),
				"Open b.pdf")
			self.assertEqual(c.menu.possibleActions[0][1][14].text(),
				"Delete b.pdf")
			self.assertEqual(c.menu.possibleActions[0][1][15].text(),
				"Copy b.pdf")

	def test_createContextMenu(self):
		"""test createContextMenu"""
		p = QWidget()
		c = CommonBibActions([], p)
		m = c.createContextMenu()
		self.assertEqual(m, None)

		c = CommonBibActions([
			{"bibkey": "abc",
			"marks": "new,imp",
			"abstract": "few words on abc",
			"arxiv": "1809.00000",
			"bibtex": '@article{abc, author="me", title="abc"}',
			"inspire": "9999999",
			"doi": "1/2/3/4",
			"link": "http://some.link.com",
			"review": 0,
			"proceeding": 0,
			"book": 1,
			"phd_thesis": 0,
			"lecture": 0,
			"exp_paper": 0,
			}], p)
		with patch("physbiblio.gui.bibWindows.CommonBibActions."
				+ "_createMenuArxiv") as _c1,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "_createMenuCopy") as _c2,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "_createMenuInspire") as _c3,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "_createMenuLinks") as _c4,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "_createMenuMarkType") as _c5,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "_createMenuPDF") as _c6,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onModify") as _mod,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onClean") as _cle,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onDelete") as _del,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onCat") as _cat,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onExp") as _exp,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onExport") as _ext,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onCopyAllPDF") as _cap,\
				patch("physbiblio.gui.commonClasses.MyMenu.fillMenu") as _f:
			m = c.createContextMenu()
			self.assertIsInstance(m, MyMenu)
			self.assertEqual(m.parent(), p)
			self.assertIsInstance(m.possibleActions[0], QAction)
			self.assertEqual(m.possibleActions[0].text(), "--Entry: abc--")
			self.assertEqual(m.possibleActions[0].isEnabled(), False)
			self.assertEqual(m.possibleActions[1], None)
			self.assertIsInstance(m.possibleActions[2], QAction)
			self.assertEqual(m.possibleActions[2].text(), "Modify")
			_mod.assert_not_called()
			m.possibleActions[2].trigger()
			_mod.assert_called_once_with()
			self.assertIsInstance(m.possibleActions[3], QAction)
			self.assertEqual(m.possibleActions[3].text(), "Clean")
			_cle.assert_not_called()
			m.possibleActions[3].trigger()
			_cle.assert_called_once_with()
			self.assertIsInstance(m.possibleActions[4], QAction)
			self.assertEqual(m.possibleActions[4].text(), "Delete")
			_del.assert_not_called()
			m.possibleActions[4].trigger()
			_del.assert_called_once_with()
			self.assertEqual(m.possibleActions[5], None)
			_c5.assert_called_once_with(c.bibs[0])
			_c2.assert_called_once_with(False, c.bibs[0])
			_c6.assert_called_once_with(False, c.bibs[0])
			_c4.assert_called_once_with(
				'abc', '1809.00000', '1/2/3/4', '9999999')
			self.assertEqual(m.possibleActions[6], None)
			self.assertIsInstance(m.possibleActions[7], QAction)
			self.assertEqual(m.possibleActions[7].text(), "Select categories")
			_cat.assert_not_called()
			m.possibleActions[7].trigger()
			_cat.assert_called_once_with()
			self.assertIsInstance(m.possibleActions[8], QAction)
			self.assertEqual(m.possibleActions[8].text(), "Select experiments")
			_exp.assert_not_called()
			m.possibleActions[8].trigger()
			_exp.assert_called_once_with()
			self.assertEqual(m.possibleActions[9], None)
			_c3.assert_called_once_with(False, "9999999")
			_c1.assert_called_once_with(False, "1809.00000")
			self.assertEqual(m.possibleActions[10], None)
			self.assertIsInstance(m.possibleActions[11], QAction)
			self.assertEqual(m.possibleActions[11].text(),
				"Export in a .bib file")
			_ext.assert_not_called()
			m.possibleActions[11].trigger()
			_ext.assert_called_once_with()
			self.assertIsInstance(m.possibleActions[12], QAction)
			self.assertEqual(m.possibleActions[12].text(),
				"Copy all the corresponding PDF")
			_cap.assert_not_called()
			m.possibleActions[12].trigger()
			_cap.assert_called_once_with()
			_f.assert_called_once_with()

		c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}], p)
		with patch("physbiblio.gui.bibWindows.CommonBibActions."
				+ "_createMenuArxiv") as _c1,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "_createMenuCopy") as _c2,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "_createMenuInspire") as _c3,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "_createMenuLinks") as _c4,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "_createMenuMarkType") as _c5,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "_createMenuPDF") as _c6,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onMerge") as _mer,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onClean") as _cle,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onDelete") as _del,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onCat") as _cat,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onExp") as _exp,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onExport") as _ext,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "onCopyAllPDF") as _cap,\
				patch("physbiblio.gui.commonClasses.MyMenu.fillMenu") as _f:
			m = c.createContextMenu(selection=True)
			self.assertIsInstance(m, MyMenu)
			self.assertEqual(m.parent(), p)
			self.assertIsInstance(m.possibleActions[0], QAction)
			self.assertEqual(m.possibleActions[0].text(), "Merge")
			_mer.assert_not_called()
			m.possibleActions[0].trigger()
			_mer.assert_called_once_with()
			self.assertIsInstance(m.possibleActions[1], QAction)
			self.assertEqual(m.possibleActions[1].text(), "Clean")
			_cle.assert_not_called()
			m.possibleActions[1].trigger()
			_cle.assert_called_once_with()
			self.assertIsInstance(m.possibleActions[2], QAction)
			self.assertEqual(m.possibleActions[2].text(), "Delete")
			_del.assert_not_called()
			m.possibleActions[2].trigger()
			_del.assert_called_once_with()
			self.assertEqual(m.possibleActions[3], None)
			_c5.assert_not_called()
			_c2.assert_called_once_with(True, None)
			_c6.assert_called_once_with(True, None)
			_c4.assert_not_called()
			self.assertEqual(m.possibleActions[4], None)
			self.assertIsInstance(m.possibleActions[5], QAction)
			self.assertEqual(m.possibleActions[5].text(), "Select categories")
			_cat.assert_not_called()
			m.possibleActions[5].trigger()
			_cat.assert_called_once_with()
			self.assertIsInstance(m.possibleActions[6], QAction)
			self.assertEqual(m.possibleActions[6].text(), "Select experiments")
			_exp.assert_not_called()
			m.possibleActions[6].trigger()
			_exp.assert_called_once_with()
			self.assertEqual(m.possibleActions[7], None)
			_c3.assert_called_once_with(True, None)
			_c1.assert_called_once_with(True, None)
			self.assertEqual(m.possibleActions[8], None)
			self.assertIsInstance(m.possibleActions[9], QAction)
			self.assertEqual(m.possibleActions[9].text(),
				"Export in a .bib file")
			_ext.assert_not_called()
			m.possibleActions[9].trigger()
			_ext.assert_called_once_with()
			self.assertIsInstance(m.possibleActions[10], QAction)
			self.assertEqual(m.possibleActions[10].text(),
				"Copy all the corresponding PDF")
			_cap.assert_not_called()
			m.possibleActions[10].trigger()
			_cap.assert_called_once_with()
			_f.assert_called_once_with()

		c = CommonBibActions([
			{"bibkey": "abc"}, {"bibkey": "def"}, {"bibkey": "ghi"}], p)
		m = c.createContextMenu(selection=True)
		self.assertEqual(m.possibleActions[0].text(), "Clean")

	def test_onAddPDF(self):
		"""test onAddPDF"""
		p = QWidget()
		c = CommonBibActions([{"bibkey": "abc"}], p)
		with patch("physbiblio.pdf.LocalPDF.copyNewFile",
				return_value=True) as _cp,\
				patch("physbiblio.gui.bibWindows.askFileName",
					return_value="/h/c/file.pdf") as _afn,\
				patch("physbiblio.gui.bibWindows.infoMessage") as _im,\
				patch("os.path.isfile", return_value=True) as _if:
			c.onAddPDF()
			_cp.assert_called_once_with('abc',
				'/h/c/file.pdf', customName='file.pdf')
			_afn.assert_called_once_with(p,
				"Where is the PDF located?", filter="PDF (*.pdf)")
			_im.assert_called_once_with("PDF successfully copied!")
			_if.assert_called_once_with("/h/c/file.pdf")

		with patch("physbiblio.pdf.LocalPDF.copyNewFile",
				return_value=True) as _cp,\
				patch("physbiblio.gui.bibWindows.askFileName",
					return_value="/h/c/file.pdf") as _afn,\
				patch("physbiblio.gui.bibWindows.infoMessage") as _im,\
				patch("os.path.isfile", return_value=True) as _if:
			c.onAddPDF(ftype="doi")
			_cp.assert_called_once_with('abc', '/h/c/file.pdf', 'doi')
			_afn.assert_called_once_with(p,
				"Where is the PDF located?", filter="PDF (*.pdf)")
			_im.assert_called_once_with("PDF successfully copied!")
			_if.assert_called_once_with("/h/c/file.pdf")

		with patch("physbiblio.pdf.LocalPDF.copyNewFile",
				return_value=False) as _cp,\
				patch("physbiblio.gui.bibWindows.askFileName",
					return_value="/h/c/file.pdf") as _afn,\
				patch("logging.Logger.error") as _e,\
				patch("os.path.isfile", return_value=True) as _if:
			c.onAddPDF("doi")
			_cp.assert_called_once_with('abc', '/h/c/file.pdf', 'doi')
			_afn.assert_called_once_with(p,
				"Where is the PDF located?", filter="PDF (*.pdf)")
			_e.assert_called_once_with("Could not copy the new file!")
			_if.assert_called_once_with("/h/c/file.pdf")

		with patch("physbiblio.pdf.LocalPDF.copyNewFile",
				return_value=True) as _cp,\
				patch("physbiblio.gui.bibWindows.askFileName",
					return_value="") as _afn,\
				patch("os.path.isfile", return_value=True) as _if:
			c.onAddPDF()
			_cp.assert_not_called()
			_if.assert_not_called()

		with patch("physbiblio.pdf.LocalPDF.copyNewFile",
				return_value=True) as _cp,\
				patch("physbiblio.gui.bibWindows.askFileName",
					return_value="s") as _afn,\
				patch("os.path.isfile", return_value=False) as _if:
			c.onAddPDF()
			_cp.assert_not_called()
			_if.assert_called_once_with("s")

	def test_onAbs(self):
		"""test onAbs"""
		c = CommonBibActions([
			{"bibkey": "abc", "arxiv": "1234.85583"},
			{"bibkey": "def", "arxiv": ""}],
			self.mainW)
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _s,\
				patch("physbiblio.gui.mainWindow.MainWindow.done"
					) as _d,\
				patch("physbiblio.webimport.arxiv.webSearch.retrieveUrlAll",
					return_value=("text", {"abstract": "some text"})) as _a,\
				patch("physbiblio.database.entries.updateField") as _u,\
				patch("physbiblio.gui.bibWindows.infoMessage") as _i:
			c.onAbs()
			_i.assert_has_calls([
				call('some text', title='Abstract of arxiv:1234.85583'),
				call("No arxiv number for entry 'def'!")])
			_s.assert_called_once_with(
				'Starting the abstract download process, please wait...')
			_d.assert_called_once_with()
			_a.assert_called_once_with(
				'1234.85583', fullDict=True, searchType='id')
			_u.assert_called_once_with('abc', 'abstract', 'some text')
			_i.reset_mock()
			_s.reset_mock()
			_d.reset_mock()
			_a.reset_mock()
			_u.reset_mock()
			c.onAbs(message=False)
			_i.assert_called_once_with("No arxiv number for entry 'def'!")
			_s.assert_called_once_with(
				'Starting the abstract download process, please wait...')
			_d.assert_called_once_with()
			_a.assert_called_once_with(
				'1234.85583', fullDict=True, searchType='id')
			_u.assert_called_once_with('abc', 'abstract', 'some text')

	def test_onArx(self):
		"""test onArx"""
		c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}],
			self.mainW)
		with patch("physbiblio.gui.mainWindow.MainWindow.infoFromArxiv"
				) as _i:
			c.onArx()
			_i.assert_called_once_with([{"bibkey": "abc"}, {"bibkey": "def"}])

	def test_onCat(self):
		"""test onCat"""
		c = CommonBibActions(
			[{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
		self.mainW.selectedCats = []
		self.mainW.previousUnchanged = []
		sc = catsTreeWindow(parent=self.mainW,
			askCats=True,
			expButton=False,
			previous=[],
			multipleRecords=True)
		self.assertEqual(self.mainW.selectedCats, [])
		with patch("physbiblio.database.categories.getByEntries",
				return_value=[]) as _gc,\
				patch("physbiblio.gui.catWindows.catsTreeWindow.__init__",
					return_value=None) as _cwi,\
				patch("physbiblio.database.catsEntries.insert") as _cei,\
				patch("physbiblio.database.catsEntries.delete") as _ced,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _m:
			c.onCat(testing=sc)
			_cwi.assert_called_once_with(parent=self.mainW,
				askCats=True,
				expButton=False,
				previous=[],
				multipleRecords=True)
			_gc.assert_called_once_with(["abc", "def"])
			_cei.assert_not_called()
			_ced.assert_not_called()
			_m.assert_not_called()

		sc = catsTreeWindow(parent=self.mainW,
			askCats=True,
			expButton=False,
			previous=[],
			multipleRecords=True)
		self.mainW.selectedCats = [999, 1000]
		sc.result = "Ok"
		with patch("physbiblio.database.categories.getByEntries",
				return_value=[]) as _gc,\
				patch("physbiblio.gui.catWindows.catsTreeWindow.__init__",
					return_value=None) as _cwi,\
				patch("physbiblio.database.catsEntries.insert") as _cei,\
				patch("physbiblio.database.catsEntries.delete") as _ced,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _m:
			c.onCat(testing=sc)
			_cwi.assert_called_once_with(parent=self.mainW,
				askCats=True,
				expButton=False,
				previous=[],
				multipleRecords=True)
			_gc.assert_called_once_with(["abc", "def"])
			_cei.assert_called_once_with([999, 1000], ['abc', 'def'])
			_ced.assert_not_called()
			_m.assert_called_once_with("Categories successfully inserted")

		sc = catsTreeWindow(parent=self.mainW,
			askCats=True,
			expButton=False,
			previous=[],
			multipleRecords=True)
		self.mainW.selectedCats = [999, 1000]
		self.mainW.previousUnchanged = [1002]
		sc.result = "Ok"
		with patch("physbiblio.database.categories.getByEntries",
				return_value=[{"idCat": 1000}, {"idCat": 1001},
					{"idCat": 1002}]) as _gc,\
				patch("physbiblio.gui.catWindows.catsTreeWindow.__init__",
					return_value=None) as _cwi,\
				patch("physbiblio.database.catsEntries.insert") as _cei,\
				patch("physbiblio.database.catsEntries.delete") as _ced,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _m:
			c.onCat(testing=sc)
			_cwi.assert_called_once_with(parent=self.mainW,
				askCats=True,
				expButton=False,
				previous=[1000, 1001, 1002],
				multipleRecords=True)
			_gc.assert_called_once_with(["abc", "def"])
			_cei.assert_called_once_with([999, 1000], ['abc', 'def'])
			_ced.assert_called_once_with(1001, ['abc', 'def'])
			_m.assert_called_once_with("Categories successfully inserted")

		c = CommonBibActions(
			[{"bibkey": "abc"}], self.mainW)
		self.mainW.selectedCats = []
		self.mainW.previousUnchanged = []
		sc = catsTreeWindow(parent=self.mainW,
			askCats=True,
			expButton=False,
			previous=[])
		self.assertEqual(self.mainW.selectedCats, [])
		with patch("physbiblio.database.categories.getByEntries",
				return_value=[]) as _gc,\
				patch("physbiblio.gui.catWindows.catsTreeWindow.__init__",
					return_value=None) as _cwi,\
				patch("physbiblio.database.catsEntries.insert") as _cei,\
				patch("physbiblio.database.catsEntries.delete") as _ced,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _m:
			c.onCat(testing=sc)
			_cwi.assert_called_once_with(parent=self.mainW,
				askCats=True,
				askForBib="abc",
				expButton=False,
				previous=[])
			_gc.assert_called_once_with(["abc"])
			_cei.assert_not_called()
			_ced.assert_not_called()
			_m.assert_not_called()

		sc = catsTreeWindow(parent=self.mainW,
			askCats=True,
			expButton=False,
			previous=[])
		self.mainW.selectedCats = [999, 1000]
		self.mainW.previousUnchanged = [1002]
		sc.result = "Ok"
		with patch("physbiblio.database.categories.getByEntries",
				return_value=[{"idCat": 1000}, {"idCat": 1001},
					{"idCat": 1002}]) as _gc,\
				patch("physbiblio.gui.catWindows.catsTreeWindow.__init__",
					return_value=None) as _cwi,\
				patch("physbiblio.database.catsEntries.insert") as _cei,\
				patch("physbiblio.database.catsEntries.delete") as _ced,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _m:
			c.onCat(testing=sc)
			_cwi.assert_called_once_with(parent=self.mainW,
				askCats=True,
				askForBib="abc",
				expButton=False,
				previous=[1000, 1001, 1002])
			_gc.assert_called_once_with(["abc"])
			_cei.assert_called_once_with(999, "abc")
			_ced.assert_has_calls([call(1001, "abc"), call(1002, "abc")])
			_m.assert_called_once_with(
				"Categories for 'abc' successfully inserted")

	def test_onCitations(self):
		"""test onCitations"""
		c = CommonBibActions([
			{"bibkey": "abc", "inspire": "1385583"},
			{"bibkey": "def", "inspire": "1358853"}],
			self.mainW)
		with patch("physbiblio.gui.mainWindow.MainWindow.getInspireStats"
				) as _i:
			c.onCitations()
			_i.assert_called_once_with(["1385583", "1358853"])

	def test_onClean(self):
		"""test onClean"""
		c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}],
			self.mainW)
		with patch("physbiblio.gui.mainWindow.MainWindow.cleanAllBibtexs"
				) as _c:
			c.onClean()
			_c.assert_called_once_with(
				useEntries=[{"bibkey": "abc"}, {"bibkey": "def"}])

	def test_onComplete(self):
		"""test onComplete"""
		c = CommonBibActions([
			{"bibkey": "abc", "inspire": "1234"}],
			self.mainW)
		with patch("physbiblio.gui.mainWindow.MainWindow.updateInspireInfo"
				) as _u:
			c.onComplete()
			_u.assert_called_once_with("abc", inspireID="1234")
		c = CommonBibActions([
			{"bibkey": "abc", "inspire": "1234"},
			{"bibkey": "def"}], self.mainW)
		with patch("physbiblio.gui.mainWindow.MainWindow.updateInspireInfo"
				) as _u:
			c.onComplete()
			_u.assert_called_once_with(["abc", "def"],
				inspireID=["1234", None])

	def test_onCopyBibtexs(self):
		"""test onCopyBibtexs"""
		c = CommonBibActions([
			{"bibkey": "abc", "bibtex": "bibtex 1"},
			{"bibkey": "def", "bibtex": "bibtex 2"}], self.mainW)
		with patch("physbiblio.gui.bibWindows.copyToClipboard"
				) as _cp:
			c.onCopyBibtexs()
			_cp.assert_called_once_with("bibtex 1\n\nbibtex 2")

	def test_onCopyCites(self):
		"""test onCopyCites"""
		c = CommonBibActions([
			{"bibkey": "abc", "bibtex": "bibtex 1"},
			{"bibkey": "def", "bibtex": "bibtex 2"}], self.mainW)
		with patch("physbiblio.gui.bibWindows.copyToClipboard"
				) as _cp:
			c.onCopyCites()
			_cp.assert_called_once_with("\cite{abc,def}")

	def test_onCopyKeys(self):
		"""test onCopyKeys"""
		c = CommonBibActions([
			{"bibkey": "abc", "bibtex": "bibtex 1"},
			{"bibkey": "def", "bibtex": "bibtex 2"}], self.mainW)
		with patch("physbiblio.gui.bibWindows.copyToClipboard"
				) as _cp:
			c.onCopyKeys()
			_cp.assert_called_once_with("abc,def")

	def test_onCopyPDFFile(self):
		"""test onCopyPDFFile"""
		c = CommonBibActions(
			[{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
		pBDB.bibs.lastFetched = ["abc", "def"]
		with patch("physbiblio.gui.bibWindows.askDirName",
				side_effect=["", "/non/exist", "/non/exist"]) as _a,\
				patch("physbiblio.pdf.LocalPDF.copyToDir") as _cp,\
				patch("physbiblio.pdf.LocalPDF.getFilePath",
					return_value="/h/e/f.pdf") as _fp:
			c.onCopyPDFFile("abc", "arxiv")
			_a.assert_called_once_with(self.mainW,
				title='Where do you want to save the PDF /h/e/f.pdf?')
			_fp.assert_called_once_with("abc", "arxiv")
			_cp.assert_not_called()
			_a.reset_mock()
			_fp.reset_mock()
			c.onCopyPDFFile("abc", "arxiv")
			_a.assert_called_once_with(self.mainW,
				title='Where do you want to save the PDF /h/e/f.pdf?')
			_fp.assert_called_once_with("abc", "arxiv")
			_cp.assert_called_once_with('/non/exist', 'abc',
				fileType='arxiv', customName=None)
			_a.reset_mock()
			_cp.reset_mock()
			_fp.reset_mock()
			c.onCopyPDFFile("abc", "new.pdf", "/h/e/new.pdf")
			_a.assert_called_once_with(self.mainW,
				title='Where do you want to save the PDF /h/e/new.pdf?')
			_fp.assert_not_called()
			_cp.assert_called_once_with('/non/exist', 'abc',
				fileType='new.pdf', customName='/h/e/new.pdf')

	def test_onCopyAllPDF(self):
		"""test onCopyAllPDF"""
		c = CommonBibActions(
			[{"bibkey": "abc"}], self.mainW)
		pBDB.bibs.lastFetched = ["abc", "def"]
		with patch("physbiblio.gui.bibWindows.askDirName",
				return_value="") as _a,\
				patch("physbiblio.pdf.LocalPDF.checkFile") as _ch:
			c.onCopyAllPDF()
			_a.assert_called_once_with(self.mainW,
				title='Where do you want to save the PDF files?')
			_ch.assert_not_called()
		with patch("physbiblio.gui.bibWindows.askDirName",
				return_value="/non/exist") as _a,\
				patch("physbiblio.pdf.LocalPDF.copyToDir") as _cp,\
				patch("physbiblio.pdf.LocalPDF.getExisting",
					return_value=["a.pdf", "b.pdf"]) as _ge,\
				patch("physbiblio.pdf.LocalPDF.checkFile",
					side_effect=[True, False, True, False, False]) as _ch:
			c.onCopyAllPDF()
			_ch.assert_called_once_with('abc', 'doi')
			_cp.assert_called_once_with('/non/exist', 'abc', fileType='doi')
			_ge.assert_not_called()
			_ch.reset_mock()
			_cp.reset_mock()
			c.onCopyAllPDF()
			_ch.assert_has_calls([call('abc', 'doi'), call('abc', 'arxiv')])
			_cp.assert_called_once_with('/non/exist', 'abc', fileType='arxiv')
			_ge.assert_not_called()
			_ch.reset_mock()
			_cp.reset_mock()
			c.onCopyAllPDF()
			_ch.assert_has_calls([call('abc', 'doi'), call('abc', 'arxiv')])
			_ge.assert_called_once_with("abc")
			_cp.assert_has_calls([
				call('/non/exist', 'abc', "", customName='a.pdf'),
				call('/non/exist', 'abc', "", customName='b.pdf')])

		c = CommonBibActions(
			[{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
		with patch("physbiblio.gui.bibWindows.askDirName",
				return_value="/non/exist") as _a,\
				patch("physbiblio.pdf.LocalPDF.copyToDir") as _cp,\
				patch("physbiblio.pdf.LocalPDF.checkFile",
					return_value=True) as _ch:
			c.onCopyAllPDF()
			_ch.assert_has_calls([call('abc', 'doi'), call('def', 'doi')])
			_cp.assert_has_calls([
				call('/non/exist', 'abc', fileType='doi'),
				call('/non/exist', 'def', fileType='doi')])

	def test_onDelete(self):
		"""test onDelete"""
		c = CommonBibActions(
			[{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
		with patch("physbiblio.gui.bibWindows.deleteBibtex"
				) as _d:
			c.onDelete()
			_d.assert_called_once_with(self.mainW, ["abc", "def"])

	def test_onDeletePDFFile(self):
		"""test onDeletePDFFile"""
		c = CommonBibActions(
			[{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
		pBDB.bibs.lastFetched = ["abc", "def"]
		with patch("physbiblio.gui.bibWindows.askYesNo",
				side_effect=[False, True, True]) as _a,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _s,\
				patch("physbiblio.pdf.LocalPDF.removeFile") as _rm,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _l,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent"
					) as _r:
			c.onDeletePDFFile("abc", "arxiv", "arxiv PDF")
			_a.assert_called_once_with(
				"Do you really want to delete the %s file for entry %s?"%(
					"arxiv PDF", "abc"))
			_s.assert_not_called()
			_rm.assert_not_called()
			c.onDeletePDFFile("abc", "arxiv", "arxiv PDF")
			_s.assert_called_once_with("deleting arxiv PDF file...")
			_rm.assert_called_once_with("abc", "arxiv")
			_r.assert_called_once_with(['abc', 'def'])
			_l.assert_called_once_with()
			_rm.reset_mock()
			_s.reset_mock()
			c.onDeletePDFFile("abc", "test.pdf", "test.pdf", "/h/test.pdf")
			_s.assert_called_once_with("deleting test.pdf file...")
			_rm.assert_called_once_with("abc", "", fileName="/h/test.pdf")

	def test_onDown(self):
		"""test onDown"""
		c = CommonBibActions(
			[{"bibkey": "abc", "arxiv": "1"},
			{"bibkey": "def", "arxiv": ""}], self.mainW)
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _s,\
				patch("physbiblio.gui.threadElements.thread_downloadArxiv."
					+ "__init__", return_value=None) as _i:
			with self.assertRaises(AttributeError):
				c.onDown()
			_s.assert_called_once_with("downloading PDF for arxiv:1...")
			_i.assert_called_once_with("abc", self.mainW)
		self.assertIsInstance(c.downArxiv_thr, list)
		self.assertEqual(len(c.downArxiv_thr), 1)
		c = CommonBibActions(
			[{"bibkey": "abc", "arxiv": "1"},
			{"bibkey": "def", "arxiv": "2"}], self.mainW)
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _m,\
				patch("PySide2.QtCore.QThread.start") as _s:
			c.onDown()
			self.assertEqual(_s.call_count, 2)
		self.assertIsInstance(c.downArxiv_thr[0], thread_downloadArxiv)
		self.assertIsInstance(c.downArxiv_thr[1], thread_downloadArxiv)
		with patch("physbiblio.gui.bibWindows.CommonBibActions."
				+ "onDownloadArxivDone") as _d:
			c.downArxiv_thr[0].finished.emit()
			_d.assert_called_once_with("1")
			c.downArxiv_thr[1].finished.emit()
			_d.assert_has_calls([call("2")])

	def test_onDownloadArxivDone(self):
		"""test onDownloadArxivDone"""
		c = CommonBibActions(
			[{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
		pBDB.bibs.lastFetched = ["abc", "def"]
		with patch("physbiblio.gui.mainWindow.MainWindow.done"
				) as _d,\
				patch("physbiblio.gui.mainWindow.MainWindow.sendMessage"
					) as _m,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _l,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent"
					) as _r:
			c.onDownloadArxivDone("1809.00000")
			_m.assert_called_once_with(
				"Download of PDF for arXiv:1809.00000 completed! "
				+ "Please check that it worked...")
			_d.assert_called_once_with()
			_l.assert_called_once_with()
			_r.assert_called_once_with(["abc", "def"])

	def test_onExp(self):
		"""test onExp"""
		c = CommonBibActions(
			[{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
		se = ExpsListWindow(parent=self.mainW,
			askExps=True,
			previous=[])
		self.mainW.selectedExps = [999, 1000]
		with patch("physbiblio.gui.bibWindows.infoMessage") as _im,\
				patch("physbiblio.gui.expWindows.ExpsListWindow.__init__",
					return_value=None) as _ewi,\
				patch("physbiblio.database.entryExps.insert") as _eei,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _m:
			c.onExp(testing=se)
			_im.assert_called_once_with(
				"Warning: you can just add experiments "
				+ "to the selected entries, not delete!")
			_ewi.assert_called_once_with(parent=self.mainW,
				askExps=True,
				previous=[])
			_eei.assert_not_called()
			_m.assert_not_called()
			se.result = "Ok"
			c.onExp(testing=se)
			_eei.assert_called_once_with(["abc", "def"], [999, 1000])
			_m.assert_called_once_with("Experiments successfully inserted")

		c = CommonBibActions([{"bibkey": "abc"}], self.mainW)
		se = ExpsListWindow(parent=self.mainW,
			askExps=True,
			previous=[])
		self.mainW.selectedExps = [999, 1000]
		with patch("physbiblio.database.experiments.getByEntry",
				return_value=[]) as _ge,\
				patch("physbiblio.gui.expWindows.ExpsListWindow.__init__",
					return_value=None) as _ewi,\
				patch("physbiblio.database.entryExps.insert") as _eei,\
				patch("physbiblio.database.entryExps.delete") as _eed,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _m:
			c.onExp(testing=se)
			_ge.assert_called_once_with("abc")
			_ewi.assert_called_once_with(parent=self.mainW,
				askExps=True,
				askForBib="abc",
				previous=[])
			_eei.assert_not_called()
			_eed.assert_not_called()
			_m.assert_not_called()
			se.result = "Ok"
			c.onExp(testing=se)
			_eed.assert_not_called()
			_eei.assert_has_calls([call("abc", 999), call("abc", 1000)])
			_m.assert_called_once_with(
				"Experiments for 'abc' successfully inserted")

		with patch("physbiblio.database.experiments.getByEntry",
				return_value=[{"idExp": 1000}, {"idExp": 1001}]) as _ge,\
				patch("physbiblio.gui.expWindows.ExpsListWindow.__init__",
					return_value=None) as _ewi,\
				patch("physbiblio.database.entryExps.insert") as _eei,\
				patch("physbiblio.database.entryExps.delete") as _eed,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _m:
			c.onExp(testing=se)
			_ge.assert_called_once_with("abc")
			_ewi.assert_called_once_with(parent=self.mainW,
				askExps=True,
				askForBib="abc",
				previous=[1000, 1001])
			_eed.assert_called_once_with("abc", 1001)
			_eei.assert_called_once_with("abc", 999)
			_m.assert_called_once_with(
				"Experiments for 'abc' successfully inserted")

	def test_onExport(self):
		"""test onExport"""
		c = CommonBibActions(
			[{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
		with patch("physbiblio.gui.mainWindow.MainWindow.exportSelection"
				) as _e:
			c.onExport()
			_e.assert_called_once_with([{"bibkey": "abc"}, {"bibkey": "def"}])

	def test_onMerge(self):
		"""test onMerge"""
		c = CommonBibActions(
			[{"bibkey": "abc",
			"bibtex": '@article{abc, title="abc"}',
			"doi": "1/2/3",
			"old_keys": "",
			"year": "2018"},
			{"bibkey": "def",
			"bibtex": '@article{def, title="def"}',
			"doi": "1/2/3",
			"old_keys": "",
			"year": 2018}],
			self.mainW)
		e = {"bibkey": "new",
			"bibtex": '@article{new, title="new"}',
			"doi": "1/2/3",
			"old_keys": "",
			"year": "2018"}
		with patch("logging.Logger.warning") as _w:
			mb = MergeBibtexs(e, e, self.mainW)
		mb.onCancel()
		#non accepted MergeBibtex form
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _m,\
				patch("physbiblio.gui.bibWindows.MergeBibtexs.__init__",
					return_value=None) as _mbi,\
				patch("logging.Logger.warning") as _w:
			c.onMerge(testing=mb)
			_mbi.assert_called_once_with(c.bibs[0], c.bibs[1], self.mainW)
			_m.assert_called_once_with('Nothing to do')
		mb.result = True
		pBDB.bibs.lastFetched = ["last"]
		#empty bibtex or bibkey
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _m,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent"
					) as _rl,\
				patch("physbiblio.gui.bibWindows.MergeBibtexs.__init__",
					return_value=None) as _mbi,\
				patch("physbiblio.databaseCore.physbiblioDBCore.commit",
					return_value=[]) as _c,\
				patch("physbiblio.databaseCore.physbiblioDBCore.undo",
					return_value=[]) as _u,\
				patch("physbiblio.database.entries.prepareInsert",
					side_effect=[
						{"bibkey": "merged", "bibtex": ""},
						{"bibkey": "", "bibtex": "new bibtex"}
						]) as _pi,\
				patch("physbiblio.database.entries.delete",
					return_value=[]) as _de,\
				patch("physbiblio.database.entries.insert",
					return_value=[]) as _in,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _fl,\
				patch("logging.Logger.warning") as _w,\
				patch("logging.Logger.error") as _e:
			c.onMerge(testing=mb)
			_m.assert_not_called()
			_rl.assert_not_called()
			_mbi.assert_called_once_with(c.bibs[0], c.bibs[1], self.mainW)
			_c.assert_not_called()
			_u.assert_not_called()
			_pi.assert_called_once_with(
				bibkey=u'new',
				bibtex=u'@article{new, title="new"}',
				book=0,
				doi=u'1/2/3',
				exp_paper=0,
				lecture=0,
				marks='',
				noUpdate=0,
				old_keys='abc, def',
				phd_thesis=0,
				proceeding=0,
				review=0,
				year=u'2018')
			_de.assert_not_called()
			_in.assert_not_called()
			_fl.assert_not_called()
			_w.assert_not_called()
			_e.assert_called_once_with("Empty bibtex and/or bibkey!")

			_e.reset_mock()
			c.onMerge(testing=mb)
			_e.assert_called_once_with("Empty bibtex and/or bibkey!")

		e = {"bibkey": "new",
			"bibtex": '@article{new, title="new"}',
			"doi": "1/2/3",
			"old_keys": "",
			"book": 1,
			"year": "2018"}
		with patch("logging.Logger.warning") as _w:
			mb = MergeBibtexs(e, e, self.mainW)
		mb.result = True
		#cannot delete
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _m,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent"
					) as _rl,\
				patch("physbiblio.gui.bibWindows.MergeBibtexs.__init__",
					return_value=None) as _mbi,\
				patch("physbiblio.databaseCore.physbiblioDBCore.commit",
					return_value=[]) as _c,\
				patch("physbiblio.databaseCore.physbiblioDBCore.undo",
					return_value=[]) as _u,\
				patch("physbiblio.database.entries.prepareInsert",
					return_value=
						{"bibkey": "merged", "bibtex": "new bibtex"}
						) as _pi,\
				patch("physbiblio.database.entries.delete",
					side_effect=Exception("error")) as _de,\
				patch("physbiblio.database.entries.insert",
					return_value=False) as _in,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _fl,\
				patch("logging.Logger.warning") as _w,\
				patch("logging.Logger.error") as _er,\
				patch("logging.Logger.exception") as _ex:
			c.onMerge(testing=mb)
			_m.assert_not_called()
			_rl.assert_not_called()
			_mbi.assert_called_once_with(c.bibs[0], c.bibs[1], self.mainW)
			_c.assert_called_once_with()
			_u.assert_called_once_with()
			_pi.assert_called_once_with(
				bibkey=u'new',
				bibtex=u'@article{new, title="new"}',
				book=0,
				doi=u'1/2/3',
				exp_paper=0,
				lecture=0,
				marks='',
				noUpdate=0,
				old_keys='abc, def',
				phd_thesis=0,
				proceeding=0,
				review=0,
				year=u'2018')
			_de.assert_called_once_with("abc")
			_in.assert_not_called()
			_fl.assert_not_called()
			_w.assert_not_called()
			_er.assert_not_called()
			_ex.assert_called_once_with("Cannot delete old items!")
		#cannot insert
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _m,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent"
					) as _rl,\
				patch("physbiblio.gui.bibWindows.MergeBibtexs.__init__",
					return_value=None) as _mbi,\
				patch("physbiblio.databaseCore.physbiblioDBCore.commit",
					return_value=[]) as _c,\
				patch("physbiblio.databaseCore.physbiblioDBCore.undo",
					return_value=[]) as _u,\
				patch("physbiblio.database.entries.prepareInsert",
					return_value=
						{"bibkey": "merged", "bibtex": "new bibtex"}
						) as _pi,\
				patch("physbiblio.database.entries.delete",
					return_value=True) as _de,\
				patch("physbiblio.database.entries.insert",
					return_value=False) as _in,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _fl,\
				patch("logging.Logger.warning") as _w,\
				patch("logging.Logger.error") as _er,\
				patch("logging.Logger.exception") as _ex:
			c.onMerge(testing=mb)
			_m.assert_not_called()
			_rl.assert_not_called()
			_mbi.assert_called_once_with(c.bibs[0], c.bibs[1], self.mainW)
			_c.assert_called_once_with()
			_u.assert_called_once_with()
			_pi.assert_called_once_with(
				bibkey=u'new',
				bibtex=u'@article{new, title="new"}',
				book=0,
				doi=u'1/2/3',
				exp_paper=0,
				lecture=0,
				marks='',
				noUpdate=0,
				old_keys='abc, def',
				phd_thesis=0,
				proceeding=0,
				review=0,
				year=u'2018')
			_de.assert_has_calls([call("abc"), call("def")])
			_in.assert_called_once_with(
				{'bibkey': 'merged', 'bibtex': 'new bibtex'})
			_fl.assert_not_called()
			_w.assert_not_called()
			_er.assert_called_once_with('Cannot insert new item!')
			_ex.assert_not_called()
		#cannot reload
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _m,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent",
					side_effect=Exception("error")) as _rl,\
				patch("physbiblio.gui.bibWindows.MergeBibtexs.__init__",
					return_value=None) as _mbi,\
				patch("physbiblio.databaseCore.physbiblioDBCore.commit",
					return_value=[]) as _c,\
				patch("physbiblio.databaseCore.physbiblioDBCore.undo",
					return_value=[]) as _u,\
				patch("physbiblio.database.entries.prepareInsert",
					return_value=
						{"bibkey": "merged", "bibtex": "new bibtex"}
						) as _pi,\
				patch("physbiblio.database.entries.delete",
					return_value=True) as _de,\
				patch("physbiblio.database.entries.insert",
					return_value=True) as _in,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _fl,\
				patch("logging.Logger.warning") as _w,\
				patch("logging.Logger.error") as _er,\
				patch("logging.Logger.exception") as _ex:
			c.onMerge(testing=mb)
			_m.assert_not_called()
			_rl.assert_called_once_with(["last"])
			_mbi.assert_called_once_with(c.bibs[0], c.bibs[1], self.mainW)
			_c.assert_called_once_with()
			_u.assert_not_called()
			_pi.assert_called_once_with(
				bibkey=u'new',
				bibtex=u'@article{new, title="new"}',
				book=0,
				doi=u'1/2/3',
				exp_paper=0,
				lecture=0,
				marks='',
				noUpdate=0,
				old_keys='abc, def',
				phd_thesis=0,
				proceeding=0,
				review=0,
				year=u'2018')
			_de.assert_has_calls([call("abc"), call("def")])
			_in.assert_called_once_with(
				{'bibkey': 'merged', 'bibtex': 'new bibtex'})
			_fl.assert_called_once_with()
			_w.assert_called_once_with("Impossible to reload content.")
			_er.assert_not_called()
			_ex.assert_not_called()
		#working
		with patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
				) as _m,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent"
					) as _rl,\
				patch("physbiblio.gui.bibWindows.MergeBibtexs.__init__",
					return_value=None) as _mbi,\
				patch("physbiblio.databaseCore.physbiblioDBCore.commit",
					return_value=[]) as _c,\
				patch("physbiblio.databaseCore.physbiblioDBCore.undo",
					return_value=[]) as _u,\
				patch("physbiblio.database.entries.prepareInsert",
					return_value=
						{"bibkey": "merged", "bibtex": "new bibtex"}
						) as _pi,\
				patch("physbiblio.database.entries.delete",
					return_value=True) as _de,\
				patch("physbiblio.database.entries.insert",
					return_value=True) as _in,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _fl,\
				patch("logging.Logger.warning") as _w,\
				patch("logging.Logger.error") as _er,\
				patch("logging.Logger.exception") as _ex:
			c.onMerge(testing=mb)
			_m.assert_not_called()
			_rl.assert_called_once_with(["last"])
			_mbi.assert_called_once_with(c.bibs[0], c.bibs[1], self.mainW)
			_c.assert_called_once_with()
			_u.assert_not_called()
			_pi.assert_called_once_with(
				bibkey=u'new',
				bibtex=u'@article{new, title="new"}',
				book=0,
				doi=u'1/2/3',
				exp_paper=0,
				lecture=0,
				marks='',
				noUpdate=0,
				old_keys='abc, def',
				phd_thesis=0,
				proceeding=0,
				review=0,
				year=u'2018')
			_de.assert_has_calls([call("abc"), call("def")])
			_in.assert_called_once_with(
				{'bibkey': 'merged', 'bibtex': 'new bibtex'})
			_fl.assert_called_once_with()
			_w.assert_not_called()
			_er.assert_not_called()
			_ex.assert_not_called()

	def test_onModify(self):
		"""test onModify"""
		c = CommonBibActions(
			[{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
		with patch("physbiblio.gui.bibWindows.editBibtex"
				) as _e:
			c.onModify()
			_e.assert_called_once_with(self.mainW, "abc")

	def test_onUpdate(self):
		"""test onUpdate"""
		c = CommonBibActions(
			[{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
		with patch("physbiblio.gui.mainWindow.MainWindow.updateAllBibtexs"
				) as _u:
			c.onUpdate()
			_u.assert_called_once_with(
				force=False, reloadAll=False, startFrom=0,
				useEntries=[{'bibkey': 'abc'}, {'bibkey': 'def'}])
			_u.reset_mock()
			c.onUpdate(force=True)
			_u.assert_called_once_with(
				force=True, reloadAll=False, startFrom=0,
				useEntries=[{'bibkey': 'abc'}, {'bibkey': 'def'}])
			_u.reset_mock()
			c.onUpdate(reloadAll=True)
			_u.assert_called_once_with(
				force=False, reloadAll=True, startFrom=0,
				useEntries=[{'bibkey': 'abc'}, {'bibkey': 'def'}])

	def test_onUpdateMark(self):
		"""test onUpdateMark"""
		c = CommonBibActions([
			{"bibkey": "abc",
			"marks": "imp",
			},
			{"bibkey": "def",
			"marks": "imp,new",
			}], self.mainW)
		pBDB.bibs.lastFetched = ["abc", "def"]
		with patch("physbiblio.database.entries.updateField") as _uf,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _l,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent"
					) as _r:
			c.onUpdateMark("new")
			_uf.assert_has_calls([
				call('abc', 'marks', "imp,new", verbose=0),
				call('def', 'marks', "imp", verbose=0)])
			_r.assert_called_once_with(['abc', 'def'])
			_l.assert_called_once_with()
			_uf.reset_mock()
			c.onUpdateMark("bad")
			_uf.assert_has_calls([
				call('abc', 'marks', "bad,imp", verbose=0),
				call('def', 'marks', "bad,imp,new", verbose=0)])
			_uf.reset_mock()
			c.onUpdateMark("imp")
			_uf.assert_has_calls([
				call('abc', 'marks', "", verbose=0),
				call('def', 'marks', "new", verbose=0)])
		with patch("logging.Logger.warning") as _w:
			c.onUpdateMark("mark")
			_w.assert_called_once_with("Invalid mark: 'mark'")

	def test_onUpdateType(self):
		"""test onUpdateType"""
		c = CommonBibActions([
			{"bibkey": "abc",
			"marks": "new,imp",
			"abstract": "few words on abc",
			"arxiv": "1809.00000",
			"bibtex": '@article{abc, author="me", title="abc"}',
			"inspire": "9999999",
			"doi": "1/2/3/4",
			"link": "http://some.link.com",
			"review": 0,
			"proceeding": 0,
			"book": 1,
			"phd_thesis": 0,
			"lecture": 1,
			"exp_paper": 0,
			},
			{"bibkey": "def",
			"marks": "new,imp",
			"abstract": "few words on abc",
			"arxiv": "1809.00000",
			"bibtex": '@article{abc, author="me", title="abc"}',
			"inspire": "9999999",
			"doi": "1/2/3/4",
			"link": "http://some.link.com",
			"review": 0,
			"proceeding": 1,
			"book": 0,
			"phd_thesis": 0,
			"lecture": 1,
			"exp_paper": 0,
			}], self.mainW)
		pBDB.bibs.lastFetched = ["abc", "def"]
		with patch("physbiblio.database.entries.updateField") as _uf,\
				patch("physbiblio.database.entries.fetchFromLast",
					return_value=pBDB.bibs) as _l,\
				patch("physbiblio.gui.mainWindow.MainWindow.reloadMainContent"
					) as _r:
			c.onUpdateType("book")
			_uf.assert_has_calls([
				call('abc', 'book', 0, verbose=0),
				call('def', 'book', 1, verbose=0)])
			_r.assert_called_once_with(['abc', 'def'])
			_l.assert_called_once_with()
			_uf.reset_mock()
			c.onUpdateType("proceeding")
			_uf.assert_has_calls([
				call('abc', 'proceeding', 1, verbose=0),
				call('def', 'proceeding', 0, verbose=0)])
			_uf.reset_mock()
			c.onUpdateType("phd_thesis")
			_uf.assert_has_calls([
				call('abc', 'phd_thesis', 1, verbose=0),
				call('def', 'phd_thesis', 1, verbose=0)])
		with patch("logging.Logger.warning") as _w:
			c.onUpdateType("books")
			_w.assert_called_once_with("Invalid type: 'books'")


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestBibtexListWindow(GUITestCase):
	"""test BibtexListWindow"""

	@classmethod
	def setUpClass(self):
		"""Define useful things"""
		super(TestBibtexListWindow, self).setUpClass()
		self.mainW = MainWindow(testing=True)
		self.mainW.bottomLeft = BibtexInfo(self.mainW)
		self.mainW.bottomCenter = BibtexInfo(self.mainW)
		self.mainW.bottomRight = BibtexInfo(self.mainW)

	def test_init(self):
		"""test __init__"""
		with patch("PySide2.QtWidgets.QFrame.__init__",
				return_value=None) as _fi,\
				patch("physbiblio.gui.commonClasses.objListWindow."
					+ "__init__", return_value=None) as _oi,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "createActions") as _ca,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "createTable") as _ct:
			bw = BibtexListWindow(parent=self.mainW, bibs=[])
			_fi.assert_called_once_with(bw, self.mainW)
			_oi.assert_called_once_with(bw, self.mainW)
			_ca.assert_called_once_with()
			_ct.assert_called_once_with()

		with patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "createActions") as _ca,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "createTable") as _ct:
			bw = BibtexListWindow(bibs=[])
			self.assertIsInstance(bw, QFrame)
			self.assertIsInstance(bw, objListWindow)
			self.assertEqual(bw.parent(), None)
			self.assertEqual(bw.mainWin, None)
			self.assertEqual(bw.bibs, [])
			self.assertEqual(bw.askBibs, False)
			self.assertEqual(bw.previous, [])
			self.assertEqual(bw.currentAbstractKey, None)
			self.assertEqual(bw.columns, pbConfig.params["bibtexListColumns"])
			self.assertEqual(bw.colcnt, len(bw.columns))
			self.assertEqual(bw.additionalCols, ["Type", "PDF"])
			self.assertIsInstance(bw.colContents, list)
			self.assertEqual(bw.colContents,
				pbConfig.params["bibtexListColumns"] + ["type", "pdf"])

		with patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "createTable") as _ct:
			bw = BibtexListWindow(parent=self.mainW,
				bibs=[{"bibkey": "abc"}],
				askBibs=True,
				previous=["abc"])
		self.assertIsInstance(bw, QFrame)
		self.assertIsInstance(bw, objListWindow)
		self.assertEqual(bw.parent(), self.mainW)
		self.assertEqual(bw.mainWin, self.mainW)
		self.assertEqual(bw.bibs, [{"bibkey": "abc"}])
		self.assertEqual(bw.askBibs, True)
		self.assertEqual(bw.previous, ["abc"])

	def test_reloadColumnContents(self):
		"""test reloadColumnContents"""
		bw = BibtexListWindow(bibs=[])
		bw.columns = ["no"]
		bw.colcnt = 1
		bw.reloadColumnContents()
		self.assertEqual(bw.columns, pbConfig.params["bibtexListColumns"])
		self.assertEqual(bw.colcnt, len(bw.columns))
		self.assertEqual(bw.additionalCols, ["Type", "PDF"])
		self.assertIsInstance(bw.colContents, list)
		self.assertEqual(bw.colContents,
			pbConfig.params["bibtexListColumns"] + ["type", "pdf"])

	def test_changeEnableActions(self):
		"""test changeEnableActions"""
		bw = BibtexListWindow(bibs=[])
		self.assertFalse(bw.clearAct.isEnabled())
		self.assertFalse(bw.selAllAct.isEnabled())
		self.assertFalse(bw.unselAllAct.isEnabled())
		self.assertFalse(bw.okAct.isEnabled())
		self.assertFalse(bw.tableModel.ask)
		bw.tableModel.ask = True
		bw.changeEnableActions()
		self.assertTrue(bw.clearAct.isEnabled())
		self.assertTrue(bw.selAllAct.isEnabled())
		self.assertTrue(bw.unselAllAct.isEnabled())
		self.assertTrue(bw.okAct.isEnabled())

	def test_clearSelection(self):
		"""test clearSelection"""
		bw = BibtexListWindow(bibs=[])
		bw.tableModel.previous = ["abc"]
		with patch("physbiblio.gui.bibWindows.MyBibTableModel."
				+ "prepareSelected") as _ps,\
				patch("physbiblio.gui.bibWindows.MyBibTableModel."
					+ "changeAsk") as _ca,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "changeEnableActions") as _ea:
			bw.clearSelection()
			self.assertEqual(bw.tableModel.previous, [])
			_ps.assert_called_once_with()
			_ca.assert_called_once_with(False)
			_ea.assert_called_once_with()

	def test_createActions(self):
		"""test createActions"""
		bw = BibtexListWindow(bibs=[])
		images = [
			QImage(":/images/edit-node.png"
				).convertToFormat(QImage.Format_ARGB32_Premultiplied),
			QImage(":/images/dialog-ok-apply.png"
				).convertToFormat(QImage.Format_ARGB32_Premultiplied),
			QImage(":/images/edit-clear.png"
				).convertToFormat(QImage.Format_ARGB32_Premultiplied),
			QImage(":/images/edit-select-all.png"
				).convertToFormat(QImage.Format_ARGB32_Premultiplied),
			QImage(":/images/edit-unselect-all.png"
				).convertToFormat(QImage.Format_ARGB32_Premultiplied)
			]
		self.assertIsInstance(bw.selAct, QAction)
		self.assertEqual(bw.selAct.text(), "&Select entries")
		self.assertEqual(bw.selAct.parent(), bw)
		self.assertEqual(images[0],
			bw.selAct.icon().pixmap(images[0].size()).toImage())
		self.assertEqual(bw.selAct.statusTip(),
			"Select entries from the list")
		with patch("physbiblio.gui.bibWindows.BibtexListWindow."
				+ "enableSelection") as _f:
			bw.selAct.trigger()
			_f.assert_called_once_with()

		self.assertIsInstance(bw.okAct, QAction)
		self.assertEqual(bw.okAct.text(), "Selection &completed")
		self.assertEqual(bw.okAct.parent(), bw)
		self.assertEqual(images[1],
			bw.okAct.icon().pixmap(images[1].size()).toImage())
		self.assertEqual(bw.okAct.statusTip(),
			"Selection of elements completed")
		with patch("physbiblio.gui.bibWindows.BibtexListWindow."
				+ "onOk") as _f:
			bw.okAct.trigger()
			_f.assert_called_once_with()

		self.assertIsInstance(bw.clearAct, QAction)
		self.assertEqual(bw.clearAct.text(), "&Clear selection")
		self.assertEqual(bw.clearAct.parent(), bw)
		self.assertEqual(images[2],
			bw.clearAct.icon().pixmap(images[2].size()).toImage())
		self.assertEqual(bw.clearAct.statusTip(),
			"Discard the current selection and hide checkboxes")
		with patch("physbiblio.gui.bibWindows.BibtexListWindow."
				+ "clearSelection") as _f:
			bw.clearAct.trigger()
			_f.assert_called_once_with()

		self.assertIsInstance(bw.selAllAct, QAction)
		self.assertEqual(bw.selAllAct.text(), "&Select all")
		self.assertEqual(bw.selAllAct.parent(), bw)
		self.assertEqual(images[3],
			bw.selAllAct.icon().pixmap(images[3].size()).toImage())
		self.assertEqual(bw.selAllAct.statusTip(),
			"Select all the elements")
		with patch("physbiblio.gui.bibWindows.BibtexListWindow."
				+ "selectAll") as _f:
			bw.selAllAct.trigger()
			_f.assert_called_once_with()

		self.assertIsInstance(bw.unselAllAct, QAction)
		self.assertEqual(bw.unselAllAct.text(), "&Unselect all")
		self.assertEqual(bw.unselAllAct.parent(), bw)
		self.assertEqual(images[4],
			bw.unselAllAct.icon().pixmap(images[4].size()).toImage())
		self.assertEqual(bw.unselAllAct.statusTip(),
			"Unselect all the elements")
		with patch("physbiblio.gui.bibWindows.BibtexListWindow."
				+ "unselectAll") as _f:
			bw.unselAllAct.trigger()
			_f.assert_called_once_with()

	def test_enableSelection(self):
		"""test enableSelection"""
		bw = BibtexListWindow(bibs=[])
		with patch("physbiblio.gui.bibWindows.MyBibTableModel."
				+ "changeAsk") as _a,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "changeEnableActions") as _e:
			bw.enableSelection()
			_a.assert_called_once_with()
			_e.assert_called_once_with()

	def test_selectAll(self):
		"""test selectAll"""
		bw = BibtexListWindow(bibs=[])
		with patch("physbiblio.gui.bibWindows.MyBibTableModel."
				+ "selectAll") as _f:
			bw.selectAll()
			_f.assert_called_once_with()

	def test_unselectAll(self):
		"""test unselectAll"""
		bw = BibtexListWindow(bibs=[])
		with patch("physbiblio.gui.bibWindows.MyBibTableModel."
				+ "unselectAll") as _f:
			bw.unselectAll()
			_f.assert_called_once_with()

	def test_onOk(self):
		"""test onOk"""
		bw = BibtexListWindow(parent=self.mainW, bibs=[])
		self.assertFalse(hasattr(self.mainW, "selectedBibs"))
		bw.tableModel.selectedElements = {
			"abc": False, "def": True, "ghi": True}
		tmp = MagicMock()
		tmp.exec_ = MagicMock()
		with patch("physbiblio.gui.bibWindows.BibtexListWindow."
				+ "clearSelection") as _cl,\
				patch("physbiblio.gui.bibWindows.CommonBibActions",
					autospec=True) as _ci,\
				patch("physbiblio.database.entries.getByKey",
					side_effect=[[{"bibkey": "def"}], [{"bibkey": "ghi"}]]
					) as _g:
			bw.onOk()
			_cl.assert_called_once_with()
			_g.assert_has_calls([
				call("def", saveQuery=False), call("ghi", saveQuery=False)])
			_ci.assert_called_once_with(
				[{"bibkey": "def"}, {"bibkey": "ghi"}],
				self.mainW)
			self.assertEqual(self.mainW.selectedBibs, ["def", "ghi"])
		bw.tableModel.selectedElements = {
			"abc": False, "def": False, "ghi": False}
		with patch("physbiblio.gui.bibWindows.BibtexListWindow."
				+ "clearSelection") as _cl,\
				patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "createContextMenu", return_value=tmp) as _cm,\
				patch("physbiblio.database.entries.getByKey",
					side_effect=[]) as _g:
			bw.onOk()
			_cl.assert_called_once_with()
			_cm.assert_called_once_with(selection=True)
			_g.assert_not_called()
			tmp.exec_.assert_called_once_with(QCursor.pos())
			self.assertEqual(self.mainW.selectedBibs, [])

	def test_createTable(self):
		"""test createTable"""
		bw = BibtexListWindow(parent=self.mainW, bibs=[{"bibkey": "abc"}])
		bw.cleanLayout()
		pBDB.bibs.lastQuery = "myquery"
		pBDB.bibs.lastVals = (1, 2, 3)
		with patch("physbiblio.gui.bibWindows.BibtexListWindow."
				+ "changeEnableActions") as _cea,\
				patch("physbiblio.gui.commonClasses.objListWindow."
					+ "setProxyStuff") as _sps,\
				patch("PySide2.QtWidgets.QTableView.hideColumn") as _hc,\
				patch("physbiblio.gui.bibWindows.MyBibTableModel",
					autospec=True) as _tm,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "finalizeTable") as _ft:
			bw.createTable()
			_tm.assert_called_once_with(bw,
				bw.bibs,
				bw.columns + bw.additionalCols,
				bw.columns,
				bw.additionalCols,
				askBibs=bw.askBibs,
				mainWin=bw.mainWin,
				previous=bw.previous)
			_cea.assert_called_once_with()
			_sps.assert_called_once_with(bw.columns.index("firstdate"),
				Qt.DescendingOrder)
			_hc.assert_called_once_with(
				len(bw.columns) + len(bw.additionalCols))
			_ft.assert_called_once_with()
		# check mylabel in widget 0
		self.assertIsInstance(bw.lastLabel, MyLabel)
		self.assertEqual(bw.currLayout.itemAt(0).widget(), bw.lastLabel)
		self.assertEqual(bw.lastLabel.text(),
			"Last query to bibtex database: \tmyquery\t\t"
			+ " - arguments:\t(1, 2, 3)")
		self.assertIsInstance(bw.mergeLabel, MyLabel)
		self.assertEqual(bw.mergeLabel.text(),
			"(Select exactly two entries to enable merging them)")
		# check toolbar content
		self.assertIsInstance(bw.selectToolBar, QToolBar)
		self.assertEqual(bw.selectToolBar.windowTitle(), 'Bibs toolbar')
		self.assertEqual(bw.currLayout.itemAt(1).widget(), bw.selectToolBar)
		macts = bw.selectToolBar.actions()
		self.assertEqual(macts[0], bw.selAct)
		self.assertEqual(macts[1], bw.clearAct)
		self.assertTrue(macts[2].isSeparator())
		self.assertEqual(macts[3], bw.selAllAct)
		self.assertEqual(macts[4], bw.unselAllAct)
		self.assertEqual(macts[5], bw.okAct)
		self.assertEqual(bw.selectToolBar.widgetForAction(macts[6]),
			bw.mergeLabel)
		self.assertTrue(macts[7].isSeparator())
		self.assertEqual(bw.selectToolBar.widgetForAction(macts[8]),
			bw.filterInput)
		# check filterinput
		self.assertIsInstance(bw.filterInput, QLineEdit)
		self.assertEqual(bw.filterInput.placeholderText(),
			"Filter bibliography")
		with patch("physbiblio.gui.commonClasses.objListWindow."
				+ "changeFilter") as _cf:
			bw.filterInput.textChanged.emit("abc")
			_cf.assert_called_once_with("abc")
		bw.bibs = None
		with patch("physbiblio.database.entries.getAll",
				return_value=[{"bibkey": "xyz"}]) as _ga:
			bw.createTable()
			_ga.assert_called_once_with(orderType="DESC",
				limitTo=pbConfig.params["defaultLimitBibtexs"])

	def test_updateInfo(self):
		"""test updateInfo"""
		bw = BibtexListWindow(parent=self.mainW, bibs=[])
		self.assertEqual(bw.currentAbstractKey, None)
		with patch("PySide2.QtWidgets.QTextEdit.setText") as _st,\
				patch("physbiblio.gui.bibWindows.writeAbstract") as _wa,\
				patch("physbiblio.gui.bibWindows.writeBibtexInfo",
					return_value="info") as _wb:
			bw.updateInfo({"bibkey": "abc", "bibtex": "text"})
			_wb.assert_called_once_with({"bibkey": "abc", "bibtex": "text"})
			_st.assert_has_calls([
				call("text"),
				call("info")])
			_wa.assert_called_once_with(self.mainW,
				{"bibkey": "abc", "bibtex": "text"})
			self.assertEqual(bw.currentAbstractKey, "abc")
		with patch("PySide2.QtWidgets.QTextEdit.setText") as _st,\
				patch("physbiblio.gui.bibWindows.writeAbstract") as _wa,\
				patch("physbiblio.gui.bibWindows.writeBibtexInfo",
					return_value="info") as _wb:
			bw.updateInfo({"bibkey": "abc", "bibtex": "text"})
			_wb.assert_called_once_with({"bibkey": "abc", "bibtex": "text"})
			_st.assert_has_calls([
				call("text"),
				call("info")])
			_wa.assert_not_called()
			self.assertEqual(bw.currentAbstractKey, "abc")
			bw.updateInfo({"bibkey": "def", "bibtex": "text"})
			_wa.assert_called_once_with(self.mainW,
				{"bibkey": "def", "bibtex": "text"})
			self.assertEqual(bw.currentAbstractKey, "def")

	def test_getEventEntry(self):
		"""test getEventEntry"""
		bw = BibtexListWindow(bibs=[
			{"bibkey": "abc"}, {"bibkey": "def"}, {"bibkey": ""}])
		with patch("physbiblio.database.entries.getByBibkey",
				side_effect=[["Rabc"], ["Rabc"], ["Rdef"], []]) as _gbb,\
				patch("logging.Logger.debug") as _d:
			self.assertEqual(bw.getEventEntry(bw.proxyModel.index(0, 0)),
				(0, 0, "abc", "Rabc"))
			self.assertEqual(bw.getEventEntry(bw.proxyModel.index(0, 3)),
				(0, 3, "abc", "Rabc"))
			self.assertEqual(bw.getEventEntry(bw.proxyModel.index(1, 0)),
				(1, 0, "def", "Rdef"))
			#will fail because of no DB correspondence:
			self.assertEqual(bw.getEventEntry(bw.proxyModel.index(1, 0)),
				None)
			_d.assert_called_once_with("The entry cannot be found!")
			self.assertEqual(bw.getEventEntry(bw.proxyModel.index(2, 0)),
				None)
			self.assertEqual(bw.getEventEntry(bw.proxyModel.index(12, 0)),
				None)

	def test_triggeredContextMenuEvent(self):
		"""test triggeredContextMenuEvent"""
		bw = BibtexListWindow(parent=self.mainW,
			bibs=[{"bibtex": "text", "bibkey": "abc", "marks": ""}])
		ev = QMouseEvent(QEvent.MouseButtonPress,
			QCursor.pos(),
			Qt.RightButton,
			Qt.NoButton,
			Qt.NoModifier)
		with patch("PySide2.QtCore.QSortFilterProxyModel.index",
				return_value="index") as _ix,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "getEventEntry", return_value=None) as _ge,\
				patch("logging.Logger.warning") as _w:
			self.assertEqual(bw.triggeredContextMenuEvent(
				9999, 101, ev),
				None)
			_w.assert_called_once_with("The index is not valid!")
			_ix.assert_called_once_with(9999, 101)
			_ge.assert_called_once_with("index")
		with patch("PySide2.QtCore.QSortFilterProxyModel.index",
				return_value="index") as _ix,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "getEventEntry",
					return_value=(0, 0, "abc", {"bibkey": "abc"})) as _ge,\
				patch("logging.Logger.warning") as _w:
			with patch("physbiblio.gui.bibWindows.CommonBibActions",
					autospec=True) as _ci:
				self.assertEqual(bw.triggeredContextMenuEvent(
					9999, 101, ev),
					None)
				_ci.assert_called_once_with([{"bibkey": "abc"}], self.mainW)
			_w.assert_not_called()
			_ix.assert_called_once_with(9999, 101)
			_ge.assert_called_once_with("index")
			with patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "createContextMenu") as _cm:
				self.assertEqual(bw.triggeredContextMenuEvent(
					9999, 101, ev),
					None)
				_cm.assert_called_once_with()
			tmp = MagicMock()
			tmp.exec_ = MagicMock()
			with patch("physbiblio.gui.bibWindows.CommonBibActions."
					+ "createContextMenu", return_value=tmp) as _cm:
				bw.triggeredContextMenuEvent(
					9999, 101, ev)
				tmp.exec_.assert_called_once_with(QCursor.pos())
				_cm.assert_called_once_with()

	def test_handleItemEntered(self):
		"""test handleItemEntered"""
		bw = BibtexListWindow(bibs=[])
		self.assertEqual(bw.handleItemEntered(QModelIndex()), None)

	def test_cellClick(self):
		"""test cellClick"""
		bw = BibtexListWindow(parent=self.mainW, bibs=[])
		ix = QModelIndex()
		with patch("physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
				return_value=None) as _ge,\
				patch("logging.Logger.warning") as _w:
			self.assertEqual(bw.cellClick(ix), None)
			_w.assert_called_once_with("The index is not valid!")
			_ge.assert_called_once_with(ix)
		with patch("physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
				return_value=(0, 0, "abc", {"bibkey": "abc"})) as _ge,\
				patch("logging.Logger.warning") as _w,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "updateInfo") as _ui:
			self.assertEqual(bw.cellClick(ix), None)
			_ui.assert_called_once_with({"bibkey": "abc"})
			_ge.assert_called_once_with(ix)

	def test_cellDoubleClick(self):
		"""test cellDoubleClick"""
		bw = BibtexListWindow(parent=self.mainW,
			bibs=[{"bibtex": "text", "bibkey": "abc"}])
		ix = QModelIndex()
		with patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "getEventEntry", return_value=None) as _ge,\
				patch("logging.Logger.warning") as _w:
			self.assertEqual(bw.cellDoubleClick(ix), None)
			_w.assert_called_once_with("The index is not valid!")

		currentry = {"bibkey": "abc",
			"doi": "1/2/3",
			"arxiv": "1234.56789",
			"inspire": "9876543"}
		with patch("physbiblio.gui.commonClasses.guiViewEntry.openLink"
				) as _ol,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "getEventEntry",
					return_value=(0, bw.colContents.index("doi"),
						"abc", currentry)) as _ge,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "updateInfo") as _ui:
			bw.cellDoubleClick(ix)
			_ge.assert_called_once_with(ix)
			_ui.assert_called_once_with(currentry)
			_ol.assert_called_once_with("abc", "doi")
		currentry["doi"] = ""
		with patch("physbiblio.gui.commonClasses.guiViewEntry.openLink"
				) as _ol,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "getEventEntry",
					return_value=(0, bw.colContents.index("doi"),
						"abc", currentry)) as _ge,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "updateInfo") as _ui:
			bw.cellDoubleClick(ix)
			_ol.assert_not_called()
		currentry["doi"] = None
		with patch("physbiblio.gui.commonClasses.guiViewEntry.openLink"
				) as _ol,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "getEventEntry",
					return_value=(0, bw.colContents.index("doi"),
						"abc", currentry)) as _ge,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "updateInfo") as _ui:
			bw.cellDoubleClick(ix)
			_ol.assert_not_called()

		with patch("physbiblio.gui.commonClasses.guiViewEntry.openLink"
				) as _ol,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "getEventEntry",
					return_value=(0, bw.colContents.index("arxiv"),
						"abc", currentry)) as _ge,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "updateInfo") as _ui:
			bw.cellDoubleClick(ix)
			_ge.assert_called_once_with(ix)
			_ui.assert_called_once_with(currentry)
			_ol.assert_called_once_with("abc", "arxiv")
		currentry["arxiv"] = ""
		with patch("physbiblio.gui.commonClasses.guiViewEntry.openLink"
				) as _ol,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "getEventEntry",
					return_value=(0, bw.colContents.index("arxiv"),
						"abc", currentry)) as _ge,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "updateInfo") as _ui:
			bw.cellDoubleClick(ix)
			_ol.assert_not_called()
		currentry["arxiv"] = None
		with patch("physbiblio.gui.commonClasses.guiViewEntry.openLink"
				) as _ol,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "getEventEntry",
					return_value=(0, bw.colContents.index("arxiv"),
						"abc", currentry)) as _ge,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "updateInfo") as _ui:
			bw.cellDoubleClick(ix)
			_ol.assert_not_called()

		with patch("physbiblio.gui.commonClasses.guiViewEntry.openLink"
				) as _ol,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "getEventEntry",
					return_value=(0, bw.colContents.index("inspire"),
						"abc", currentry)) as _ge,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "updateInfo") as _ui:
			bw.cellDoubleClick(ix)
			_ge.assert_called_once_with(ix)
			_ui.assert_called_once_with(currentry)
			_ol.assert_called_once_with("abc", "inspire")
		currentry["inspire"] = ""
		with patch("physbiblio.gui.commonClasses.guiViewEntry.openLink"
				) as _ol,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "getEventEntry",
					return_value=(0, bw.colContents.index("inspire"),
						"abc", currentry)) as _ge,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "updateInfo") as _ui:
			bw.cellDoubleClick(ix)
			_ol.assert_not_called()
		currentry["inspire"] = None
		with patch("physbiblio.gui.commonClasses.guiViewEntry.openLink"
				) as _ol,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "getEventEntry",
					return_value=(0, bw.colContents.index("inspire"),
						"abc", currentry)) as _ge,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "updateInfo") as _ui:
			bw.cellDoubleClick(ix)
			_ol.assert_not_called()

		with patch("physbiblio.pdf.LocalPDF.getExisting",
				return_value=["/tmp/file.pdf"]) as _gf,\
				patch("physbiblio.gui.commonClasses.guiViewEntry.openLink"
					) as _ol,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "getEventEntry",
					return_value=(0, bw.colContents.index("pdf"),
						"abc", currentry)) as _ge,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "updateInfo") as _ui,\
				patch("physbiblio.gui.mainWindow.MainWindow."
					+ "statusBarMessage") as _m:
			bw.cellDoubleClick(ix)
			_gf.assert_called_once_with("abc", fullPath=True)
			_ol.assert_called_once_with("abc", "file", fileArg="/tmp/file.pdf")
			_m.assert_called_once_with("opening PDF...")

		tmp = MagicMock()
		tmp.exec_ = MagicMock()
		with patch("physbiblio.pdf.LocalPDF.getExisting",
				return_value=["/tmp/file1.pdf", "/tmp/file2.pdf"]) as _gf,\
				patch("physbiblio.gui.commonClasses.guiViewEntry.openLink"
					) as _ol,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "getEventEntry",
					return_value=(0, bw.colContents.index("pdf"),
						"abc", currentry)) as _ge,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "updateInfo") as _ui,\
				patch("physbiblio.gui.mainWindow.MainWindow."
					+ "statusBarMessage") as _m,\
				patch("physbiblio.gui.bibWindows.AskPDFAction",
					return_value=tmp) as _apa:
			bw.cellDoubleClick(ix)
			_gf.assert_called_once_with("abc", fullPath=True)
			_ol.assert_not_called()
			_m.assert_not_called()
			_apa.assert_called_once_with("abc", bw)
			tmp.exec_.assert_called_once_with(QCursor.pos())
		tmp.result = "openArxiv"
		with patch("physbiblio.pdf.LocalPDF.getExisting",
				return_value=["/tmp/file1.pdf", "/tmp/file2.pdf"]) as _gf,\
				patch("physbiblio.pdf.LocalPDF.getFilePath",
					side_effect=["/tmp/arxiv.pdf", "/tmp/doi.pdf"]) as _gp,\
				patch("physbiblio.pdf.LocalPDF.getFileDir",
					return_value="/tmp") as _gd,\
				patch("physbiblio.gui.commonClasses.guiViewEntry.openLink"
					) as _ol,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "getEventEntry",
					return_value=(0, bw.colContents.index("pdf"),
						"abc", currentry)) as _ge,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "updateInfo") as _ui,\
				patch("physbiblio.gui.mainWindow.MainWindow."
					+ "statusBarMessage") as _m,\
				patch("physbiblio.gui.bibWindows.AskPDFAction",
					return_value=tmp) as _apa:
			bw.cellDoubleClick(ix)
			_gp.assert_called_once_with("abc", "arxiv")
			_ol.assert_called_once_with("abc", "file",
				fileArg="/tmp/arxiv.pdf")
			_m.assert_called_once_with("opening arXiv PDF...")
			tmp.result = "openDoi"
			bw.cellDoubleClick(ix)
			_gp.assert_called_with("abc", "doi")
			_ol.assert_called_with("abc", "file",
				fileArg="/tmp/doi.pdf")
			_m.assert_called_with("opening DOI PDF...")
			tmp.result = "openOther_file1.pdf"
			bw.cellDoubleClick(ix)
			_gd.assert_called_with("abc")
			_ol.assert_called_with("abc", "file",
				fileArg="/tmp/file1.pdf")
			_m.assert_called_with("opening file1.pdf...")

	def test_finalizeTable(self):
		"""test finalizeTable"""
		bw = BibtexListWindow(bibs=[])
		with patch("physbiblio.gui.bibWindows.BibtexListWindow."
				+ "cellClick") as _f:
			bw.tablewidget.clicked.emit(QModelIndex())
			_f.assert_called_once()
		with patch("physbiblio.gui.bibWindows.BibtexListWindow."
				+ "cellDoubleClick") as _f:
			bw.tablewidget.doubleClicked.emit(QModelIndex())
			_f.assert_called_once()
		bw.cleanLayout()
		with patch("PySide2.QtGui.QFont.setPointSize") as _sps,\
				patch("PySide2.QtWidgets.QTableView.resizeColumnsToContents"
					) as _rc,\
				patch("PySide2.QtWidgets.QTableView.resizeRowsToContents"
					) as _rr:
			bw.finalizeTable()
			_rc.assert_called_once_with()
			_rr.assert_called_once_with()
			self.assertIsInstance(bw.tablewidget.font(), QFont)
			self.assertEqual(bw.tablewidget.font().pointSize(),
				pbConfig.params["bibListFontSize"])
			self.assertEqual(bw.currLayout.itemAt(0).widget(), bw.tablewidget)

	def test_recreateTable(self):
		"""test recreateTable"""
		bw = BibtexListWindow(bibs=[])
		with patch("physbiblio.gui.bibWindows.BibtexListWindow."
				+ "cleanLayout") as _cl,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "createTable") as _ct,\
				patch("PySide2.QtWidgets.QApplication.setOverrideCursor"
					) as _sc,\
				patch("PySide2.QtWidgets.QApplication.restoreOverrideCursor"
					) as _rc,\
				patch("physbiblio.database.entries.getAll") as _ga:
			bw.recreateTable(bibs="bibs")
			_ga.assert_not_called()
			_cl.assert_called_once_with()
			_ct.assert_called_once_with()
			_rc.assert_called_once_with()
			_sc.assert_called_once_with(Qt.WaitCursor)
			self.assertEqual(bw.bibs, "bibs")
		with patch("physbiblio.gui.bibWindows.BibtexListWindow."
				+ "cleanLayout") as _cl,\
				patch("physbiblio.gui.bibWindows.BibtexListWindow."
					+ "createTable") as _ct,\
				patch("PySide2.QtWidgets.QApplication.setOverrideCursor"
					) as _sc,\
				patch("PySide2.QtWidgets.QApplication.restoreOverrideCursor"
					) as _rc,\
				patch("physbiblio.database.entries.getAll",
					return_value="getall") as _ga:
			bw.recreateTable()
			_ga.assert_called_once_with(orderType="DESC",
				limitTo=pbConfig.params["defaultLimitBibtexs"])
			_cl.assert_called_once_with()
			_ct.assert_called_once_with()
			_rc.assert_called_once_with()
			_sc.assert_called_once_with(Qt.WaitCursor)
			self.assertEqual(bw.bibs, "getall")


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestEditBibtexDialog(GUITestCase):
	"""test the EditBibtexDialog class"""

	def test_init(self):
		"""test __init__"""
		pass

	def test_onOk(self):
		"""test onOk"""
		pass

	def test_updateBibkey(self):
		"""test updateBibkey"""
		pass

	def test_createForm(self):
		"""test createForm"""
		pass


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestMyPDFAction(GUITestCase):
	"""test the MyPDFAction class"""

	def test_init(self):
		"""test init"""
		m = MyMenu()
		pa = MyPDFAction("fname", m)
		self.assertIsInstance(pa, QAction)
		self.assertEqual(pa.filename, "fname")
		self.assertEqual(pa.parentMenu, m)
		with patch("physbiblio.gui.bibWindows.MyPDFAction.returnFileName"
				) as _r:
			pa.triggered.emit()
			_r.assert_called_once_with()

		pa = MyPDFAction("fname", m, "title")
		self.assertEqual(pa.text(), "title")

	def test_returnFileName(self):
		"""test returnFileName"""
		m = MyMenu()
		pa = MyPDFAction("fname", m)
		with patch("PySide2.QtWidgets.QMenu.close") as _c:
			pa.returnFileName()
			self.assertEqual(m.result, "openOther_fname")
			_c.assert_called_once_with()


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestAskPDFAction(GUITestCase):
	"""test AskPDFAction"""

	def test_init(self):
		"""test __init__"""
		p = QWidget()
		with patch("physbiblio.pdf.LocalPDF.getExisting",
				return_value=[]) as _ge,\
				patch("physbiblio.pdf.LocalPDF.getFilePath",
					side_effect=["", ""]) as _gp,\
				patch("physbiblio.gui.commonClasses.MyMenu.fillMenu") as _fm:
			apa = AskPDFAction("improbablekey", p)
			_ge.assert_called_once_with("improbablekey", fullPath=True)
			_gp.assert_has_calls([
				call("improbablekey", "doi"),
				call("improbablekey", "arxiv")])
			_fm.assert_called_once_with()
		self.assertEqual(apa.message,
			"What PDF of this entry (improbablekey) do you want to open?")
		self.assertEqual(apa.possibleActions, [])

		with patch("physbiblio.pdf.LocalPDF.getExisting",
				return_value=["a", "b", "d", "e"]) as _ge,\
				patch("physbiblio.pdf.LocalPDF.getFilePath",
					side_effect=["d", "a"]) as _gp,\
				patch("physbiblio.gui.commonClasses.MyMenu.fillMenu") as _fm:
			apa = AskPDFAction("improbablekey", p)
			_ge.assert_called_once_with("improbablekey", fullPath=True)
			_gp.assert_has_calls([
				call("improbablekey", "doi"),
				call("improbablekey", "arxiv")])
			_fm.assert_called_once_with()
		self.assertEqual(apa.message,
			"What PDF of this entry (improbablekey) do you want to open?")
		self.assertIsInstance(apa.possibleActions, list)
		self.assertEqual(len(apa.possibleActions), 4)
		self.assertIsInstance(apa.possibleActions[0], QAction)
		self.assertIsInstance(apa.possibleActions[1], QAction)
		self.assertIsInstance(apa.possibleActions[2], MyPDFAction)
		self.assertIsInstance(apa.possibleActions[3], MyPDFAction)
		self.assertEqual(apa.possibleActions[0].text(), "Open DOI PDF")
		self.assertEqual(apa.possibleActions[1].text(), "Open arxiv PDF")
		self.assertEqual(apa.possibleActions[2].text(), "Open b")
		self.assertEqual(apa.possibleActions[3].text(), "Open e")
		with patch("physbiblio.gui.bibWindows.AskPDFAction.onOpenDoi"
				) as _r:
			apa.possibleActions[0].triggered.emit()
			_r.assert_called_once_with()
		with patch("physbiblio.gui.bibWindows.AskPDFAction.onOpenArxiv"
				) as _r:
			apa.possibleActions[1].triggered.emit()
			_r.assert_called_once_with()

	def test_onOpenArxiv(self):
		"""test onOpenArxiv"""
		p = QWidget()
		with patch("PySide2.QtWidgets.QMenu.close") as _c,\
				patch("logging.Logger.warning") as _w:
			apa = AskPDFAction("improbablekey", p)
			apa.onOpenArxiv()
			self.assertEqual(apa.result, "openArxiv")
			_c.assert_called_once_with()

	def test_onOpenDoi(self):
		"""test onOpenDoi"""
		p = QWidget()
		with patch("PySide2.QtWidgets.QMenu.close") as _c,\
				patch("logging.Logger.warning") as _w:
			apa = AskPDFAction("improbablekey", p)
			apa.onOpenDoi()
			self.assertEqual(apa.result, "openDoi")
			_c.assert_called_once_with()


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestSearchBibsWindow(GUITestCase):
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

	def test_eventFilter(self):
		"""test"""
		pass

	def test_createForm(self):
		"""test"""
		pass


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestMergeBibtexs(GUITestCase):
	"""test the MergeBibtexs class"""

	def test_init(self):
		"""test __init__"""
		pass

	def test_radioToggled(self):
		"""test radioToggled"""
		pass

	def test_textModified(self):
		"""test textModified"""
		pass

	def test_createForm(self):
		"""test createForm"""
		pass


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestFieldsFromArxiv(GUITestCase):
	"""test the FieldsFromArxiv class"""

	def test_init(self):
		"""test __init__"""
		p = QWidget()
		ffa = FieldsFromArxiv()
		self.assertEqual(ffa.parent(), None)

		ffa = FieldsFromArxiv(p)
		self.assertIsInstance(ffa, QDialog)
		self.assertEqual(ffa.parent(), p)
		self.assertEqual(ffa.windowTitle(), "Import fields from arXiv")
		self.assertEqual(ffa.arxivDict,
			["authors", "title", "doi", "primaryclass", "archiveprefix"])
		self.assertIsInstance(ffa.layout(), QVBoxLayout)

		for i, k in enumerate(
				["authors", "title", "doi", "primaryclass", "archiveprefix"]):
			self.assertIsInstance(ffa.layout().itemAt(i).widget(),
				QCheckBox)
			self.assertEqual(ffa.layout().itemAt(i).widget(),
				ffa.checkBoxes[k])
			self.assertEqual(ffa.layout().itemAt(i).widget().text(), k)
			self.assertEqual(ffa.layout().itemAt(i).widget().isChecked(),
				True)

		self.assertIsInstance(ffa.layout().itemAt(5).widget(),
			QPushButton)
		self.assertEqual(ffa.layout().itemAt(5).widget(),
			ffa.acceptButton)
		self.assertEqual(ffa.layout().itemAt(5).widget().text(), "OK")
		with patch("physbiblio.gui.bibWindows.FieldsFromArxiv.onOk") as _c:
			QTest.mouseClick(ffa.acceptButton, Qt.LeftButton)
			_c.assert_called_once_with()

		self.assertIsInstance(ffa.layout().itemAt(6).widget(),
			QPushButton)
		self.assertEqual(ffa.layout().itemAt(6).widget(),
			ffa.cancelButton)
		self.assertEqual(ffa.layout().itemAt(6).widget().autoDefault(), True)
		self.assertEqual(ffa.layout().itemAt(6).widget().text(), "Cancel")
		with patch("physbiblio.gui.bibWindows.FieldsFromArxiv.onCancel") as _c:
			QTest.mouseClick(ffa.cancelButton, Qt.LeftButton)
			_c.assert_called_once_with()

	def test_onOk(self):
		"""test onOk"""
		p = QWidget()
		ffa = FieldsFromArxiv(p)
		ffa.checkBoxes["doi"].setChecked(False)
		ffa.checkBoxes["title"].setChecked(False)
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			ffa.onOk()
			_c.assert_called_once()
		self.assertTrue(ffa.result)
		self.assertTrue(hasattr(ffa, "output"))
		self.assertIsInstance(ffa.output, list)
		self.assertEqual(ffa.output,
			['archiveprefix', 'primaryclass', 'authors'])

	def test_onCancel(self):
		"""test onCancel"""
		p = QWidget()
		ffa = FieldsFromArxiv(p)
		with patch("PySide2.QtWidgets.QDialog.close") as _c:
			ffa.onCancel()
			_c.assert_called_once()
		self.assertFalse(ffa.result)
		self.assertFalse(hasattr(ffa, "output"))

if __name__=='__main__':
	unittest.main()
