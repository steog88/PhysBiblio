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
		ebd = editBibtexDialog(m, bib=None)
		ebd.onCancel()
		with patch("logging.Logger.debug") as _ld,\
				patch("physbiblio.database.entries.getByKey") as _gbk,\
				patch("physbiblio.gui.bibWindows.editBibtexDialog.__init__",
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

		ebd = editBibtexDialog(m, bib=None)
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
				patch("physbiblio.gui.bibWindows.editBibtexDialog.__init__",
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
		ebd = editBibtexDialog(m, bib=testentry)
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
				patch("physbiblio.pdf.localPDF.renameFolder") as _rf,\
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
		ebd = editBibtexDialog(m, bib=testentry)
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
				patch("physbiblio.pdf.localPDF.renameFolder") as _rf,\
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
		ebd = editBibtexDialog(m, bib=testentry)
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
				patch("physbiblio.pdf.localPDF.renameFolder") as _rf,\
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
				patch("physbiblio.pdf.localPDF.renameFolder") as _rf,\
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
		ebd = editBibtexDialog(m, bib=testentry)
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
				patch("physbiblio.pdf.localPDF.renameFolder") as _rf,\
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
		ebd = editBibtexDialog(m, bib=testentry)
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
				patch("physbiblio.pdf.localPDF.renameFolder") as _rf,\
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
		ebd = editBibtexDialog(m, bib=testentry)
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
				patch("physbiblio.pdf.localPDF.renameFolder") as _rf,\
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
		ebd = editBibtexDialog(m, bib=testentry)
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
				patch("physbiblio.pdf.localPDF.renameFolder") as _rf,\
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
		ebd = editBibtexDialog(m, bib=testentry)
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
				patch("physbiblio.pdf.localPDF.renameFolder") as _rf,\
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
	"""test the abstractFormulas class"""

	def test_init(self):
		"""test __init__"""
		m = MainWindow(testing = True)
		m.bottomCenter = bibtexInfo(m)
		af = abstractFormulas(m, "test text")
		self.assertEqual(af.fontsize, pbConfig.params["bibListFontSize"])
		self.assertEqual(af.mainWin, m)
		self.assertEqual(af.statusMessages, True)
		self.assertEqual(af.editor, m.bottomCenter.text)
		self.assertIsInstance(af.document, QTextDocument)
		self.assertEqual(af.editor.document(), af.document)
		self.assertEqual(af.abstractTitle, "<b>Abstract:</b><br/>")
		self.assertEqual(af.text, "<b>Abstract:</b><br/>test text")

		bi = bibtexInfo()
		af = abstractFormulas(m, "test text",
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
		m.bottomCenter = bibtexInfo(m)
		af = abstractFormulas(m, "test text")
		self.assertEqual(af.hasLatex(), False)
		af = abstractFormulas(m, "test tex $f_e$ equation")
		self.assertEqual(af.hasLatex(), True)

	def test_doText(self):
		"""test doText"""
		m = MainWindow(testing = True)
		bi = bibtexInfo(m)
		af = abstractFormulas(m, "test text", customEditor=bi.text)
		with patch("PySide2.QtWidgets.QTextEdit.insertHtml") as _ih,\
				patch("physbiblio.gui.mainWindow.MainWindow.statusBarMessage"
					) as _sbm:
			af.doText()
			_ih.assert_called_once_with(af.text)
			_sbm.assert_not_called()

		af = abstractFormulas(m, "test text with $f_e$ equation",
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
				patch("physbiblio.gui.bibWindows.abstractFormulas."
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
		bi = bibtexInfo(m)
		af = abstractFormulas(m, r"test $\nu_\mu$ with $f_e$ equation",
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
		bi = bibtexInfo(m)
		af = abstractFormulas(m, r"test $\nu_\mu$ with $f_e$ equation",
			customEditor=bi.text)
		with patch("physbiblio.gui.bibWindows.abstractFormulas."
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
		bi = bibtexInfo(m)
		af = abstractFormulas(m, r"test $\nu_\mu$ with $f_e$ equation",
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
	"""test bibtexInfo"""

	def test_init(self):
		"""test __init__"""
		p = QWidget()
		bi = bibtexInfo()
		self.assertEqual(bi.parent(), None)

		bi = bibtexInfo(parent=p)
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
