#!/usr/bin/env python
"""Test file for the physbiblio.gui.bibWindows module.

This file is part of the physbiblio package.
"""
import sys
import traceback
import os
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest
from PySide2.QtGui import QPixmap
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
			editBibtex(m, editKey=None, testing=ebd)
			_ld.assert_not_called()
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
			editBibtex(m, editKey="Gariazzo:2015rra", testing=ebd)
			_ld.assert_not_called()
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
				'firstdate': u'2018-09-01', 'old_keys': u''},
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
			editBibtex(m, editKey="testkey", testing=ebd)
			_ld.assert_not_called()
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
				'firstdate': u'2018-09-01', 'old_keys': u''},
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
			editBibtex(m, editKey="testkey", testing=ebd)
			_ld.assert_not_called()
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
				'firstdate': u'2018-09-01', 'old_keys': u'old testkey'},
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
		with patch("logging.Logger.debug") as _ld,\
				patch("logging.Logger.warning") as _lw,\
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
			_ld.assert_not_called()
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
				'firstdate': u'2018-09-01', 'old_keys': u'testkey'},
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
		with patch("logging.Logger.debug") as _ld,\
				patch("logging.Logger.warning") as _lw,\
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
			_ld.assert_not_called()
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
				'firstdate': u'2018-09-01', 'old_keys': u'testkey'},
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
		m = MainWindow(testing = True)
		m.bibtexListWindow = BibtexListWindow(m)
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
		m = MainWindow(testing = True)
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
			fontsize = 99,
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
		m = MainWindow(testing = True)
		m.bottomCenter = BibtexInfo(m)
		af = AbstractFormulas(m, "test text")
		self.assertEqual(af.hasLatex(), False)
		af = AbstractFormulas(m, "test tex $f_e$ equation")
		self.assertEqual(af.hasLatex(), True)

	def test_doText(self):
		"""test doText"""
		m = MainWindow(testing = True)
		bi = BibtexInfo(m)
		af = AbstractFormulas(m, "test text", customEditor=bi.text)
		with patch("PySide2.QtWidgets.QTextEdit.insertHtml") as _ih,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm:
			af.doText()
			_ih.assert_called_once_with(af.text)
			_sbm.assert_not_called()

		af = AbstractFormulas(m, "test text with $f_e$ equation",
			customEditor=bi.text)
		with patch("PySide2.QtWidgets.QTextEdit.insertHtml") as _ih,\
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
		with patch("PySide2.QtWidgets.QTextEdit.insertHtml") as _ih,\
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
		m = MainWindow(testing = True)
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
		m = MainWindow(testing = True)
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
		m = MainWindow(testing = True)
		bi = BibtexInfo(m)
		af = AbstractFormulas(m, r"test $\nu_\mu$ with $f_e$ equation",
			customEditor=bi.text)
		images, text = af.prepareText()
		with patch("PySide2.QtGui.QTextDocument.addResource") as _ar,\
				patch("PySide2.QtWidgets.QTextEdit.insertHtml") as _ih,\
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

	def test_createContextMenu(self):
		"""test createContextMenu"""
		p = QWidget()
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
		with patch("physbiblio.pdf.LocalPDF.getExisting",
				return_value=[]) as _ge,\
				patch("physbiblio.pdf.LocalPDF.getFilePath",
					side_effect=[[],[],[]]) as _ge:
			m = c.createContextMenu()

		c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}], p)
		m = c.createContextMenu(selection=True)
		raise NotImplementedError

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
				"Where is the PDF located?", filter = "PDF (*.pdf)")
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
				"Where is the PDF located?", filter = "PDF (*.pdf)")
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
				"Where is the PDF located?", filter = "PDF (*.pdf)")
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
		raise NotImplementedError

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
		raise NotImplementedError

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
			{"bibkey": "abc", "inspire": "1234"},
			{"bibkey": "def"}], self.mainW)
		with patch("physbiblio.gui.mainWindow.MainWindow.updateInspireInfo"
				) as _u:
			c.onComplete()
			_u.assert_called_once_with("abc", inspireID="1234")

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
		raise NotImplementedError

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
		raise NotImplementedError

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

	def test_init(self):
		"""test __init__"""
		pass

	def test_reloadColumnContents(self):
		"""test reloadColumnContents"""
		pass

	def test_changeEnableActions(self):
		"""test changeEnableActions"""
		pass

	def test_addMark(self):
		"""test addMark"""
		pass

	def test_clearSelection(self):
		"""test clearSelection"""
		pass

	def test_enableSelection(self):
		"""test enableSelection"""
		pass

	def test_selectAll(self):
		"""test selectAll"""
		pass

	def test_unselectAll(self):
		"""test unselectAll"""
		pass

	def test_onOk(self):
		"""test onOk"""
		pass

	def test_createTable(self):
		"""test createTable"""
		pass

	def test_updateInfo(self):
		"""test updateInfo"""
		pass

	def test_getEventEntry(self):
		"""test getEventEntry"""
		pass

	def test_triggeredContextMenuEvent(self):
		"""test triggeredContextMenuEvent"""
		pass

	def test_handleItemEntered(self):
		"""test handleItemEntered"""
		pass

	def test_cellClick(self):
		"""test cellClick"""
		pass

	def test_cellDoubleClick(self):
		"""test cellDoubleClick"""
		pass

	def test_finalizeTable(self):
		"""test"""
		pass

	def test_recreateTable(self):
		"""test"""
		pass


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
