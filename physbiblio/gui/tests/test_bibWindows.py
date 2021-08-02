#!/usr/bin/env python
"""Test file for the physbiblio.gui.bibWindows module.

This file is part of the physbiblio package.
"""
import os
import sys
import traceback

from PySide2.QtCore import QItemSelectionModel, QModelIndex, Qt
from PySide2.QtGui import QMouseEvent, QPixmap
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QMenu, QToolButton, QWidget

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import MagicMock, call, patch
else:
    import unittest
    from unittest.mock import MagicMock, call, patch

try:
    from physbiblio.gui.bibWindows import *
    from physbiblio.gui.mainWindow import MainWindow
    from physbiblio.gui.setuptests import *
    from physbiblio.setuptests import *
    from physbiblio.strings.gui import BibWindowsStrings as bwstr
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestFunctions(GUIwMainWTestCase):
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
        self.maxDiff = None
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
            "comments": "some thing",
            "citations": 12,
            "citations_no_self": 0,
        }
        with patch(
            "physbiblio.database.Categories.getByEntry", return_value=[], autospec=True
        ) as _gc, patch(
            "physbiblio.database.Experiments.getByEntry", return_value=[], autospec=True
        ) as _ge, patch(
            "logging.Logger.debug"
        ) as _d:
            self.assertEqual(
                writeBibtexInfo(entry),
                "<u>mykey</u> (use with '<u>\cite{mykey}</u>')<br/>\n"
                + "<b>sg</b><br/>\nsome title<br/>\n<i>AB 12 (2018) 1</i>"
                + "<br/>\n<br/>\nDOI of the record: <u>a/b/12</u><br/>"
                + "\narXiv ID of the record: <u>1234.5678</u><br/>"
                + "\nINSPIRE-HEP ID of the record: <u>1234</u><br/>\n<br/>\n"
                + "Last citation count obtained from INSPIRE: 12<br/>\n"
                + "Categories: <i>None</i><br/>\nExperiments: <i>None</i>"
                + "<br/>\n<br/>Comments:<br/>some thing",
            )
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
            "citations": 0,
            "citations_no_self": 12,
        }
        with patch(
            "physbiblio.database.Categories.getByEntry",
            return_value=[{"name": "Main"}],
            autospec=True,
        ) as _gc, patch(
            "physbiblio.database.Experiments.getByEntry", return_value=[], autospec=True
        ) as _ge, patch(
            "logging.Logger.debug"
        ) as _d:
            self.assertEqual(
                writeBibtexInfo(entry),
                "(Book) <u>mykey</u> (use with '<u>\cite{mykey}</u>')<br/>\n"
                + "<b>sg</b><br/>\nsome title<br/>\n"
                + "<br/>\nISBN code of the record: <u>123456789</u><br/>\n"
                + "DOI of the record: <u>a/b/12</u><br/>\n"
                + "INSPIRE-HEP ID of the record: <u>1234</u><br/>\n<br/>\n"
                + "Categories: <i>Main</i><br/>\nExperiments: <i>None</i>",
            )
            _d.assert_has_calls(
                [
                    call(
                        "KeyError: 'journal', 'volume', 'year' or 'pages' "
                        + "not in ['author', 'pages', 'title', 'volume', 'year']"
                    ),
                    call(
                        "KeyError: 'ads' not in "
                        + "['arxiv', 'bibkey', 'bibtexDict', 'book', "
                        + "'citations', 'citations_no_self', 'doi', "
                        + "'exp_paper', 'inspire', 'isbn', 'lecture', "
                        + "'phd_thesis', 'proceeding', 'review']"
                    ),
                    call(
                        "KeyError: 'comments' not in ['arxiv', 'bibkey',"
                        + " 'bibtexDict', 'book', 'citations', 'citations_no_self', "
                        + "'doi', 'exp_paper', 'inspire',"
                        + " 'isbn', 'lecture', 'phd_thesis', 'proceeding', "
                        + "'review']"
                    ),
                ]
            )

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
            "citations": 12,
            "citations_no_self": 10,
        }
        with patch(
            "physbiblio.database.Categories.getByEntry",
            return_value=[{"name": "Main"}],
            autospec=True,
        ) as _gc, patch(
            "physbiblio.database.Experiments.getByEntry", return_value=[], autospec=True
        ) as _ge, patch(
            "logging.Logger.debug"
        ) as _d:
            self.assertEqual(
                writeBibtexInfo(entry),
                "(Review) <u>mykey</u> (use with '<u>\cite{mykey}</u>')<br/>\n"
                + "<b>sg</b><br/>\n<i>AB 12 (2018) 1</i><br/>\n<br/>\n"
                + "DOI of the record: <u>a/b/12</u><br/>\n"
                + "INSPIRE-HEP ID of the record: <u>1234</u><br/>\n<br/>\n"
                + "Last citation count obtained from INSPIRE: 12 (10 excluding self citations)<br/>\n"
                + "Categories: <i>Main</i><br/>\nExperiments: <i>None</i>",
            )
            _d.assert_has_calls(
                [
                    call(
                        "KeyError: 'proceeding' not in "
                        + "['arxiv', 'bibkey', 'bibtexDict', 'book', "
                        + "'citations', 'citations_no_self', 'doi', "
                        + "'exp_paper', 'inspire', 'lecture', 'phd_thesis', "
                        + "'review']"
                    ),
                    call(
                        "KeyError: 'title' not in "
                        + "['author', 'journal', 'pages', 'volume', 'year']"
                    ),
                    call(
                        "KeyError: 'isbn' not in "
                        + "['arxiv', 'bibkey', 'bibtexDict', 'book', "
                        + "'citations', 'citations_no_self', 'doi', "
                        + "'exp_paper', 'inspire', 'lecture', 'phd_thesis', "
                        + "'review']"
                    ),
                    call(
                        "KeyError: 'ads' not in "
                        + "['arxiv', 'bibkey', 'bibtexDict', 'book', "
                        + "'citations', 'citations_no_self', 'doi', "
                        + "'exp_paper', 'inspire', 'lecture', 'phd_thesis', "
                        + "'review']"
                    ),
                    call(
                        "KeyError: 'comments' not in ['arxiv', 'bibkey',"
                        + " 'bibtexDict', 'book', 'citations', 'citations_no_self', "
                        + "'doi', 'exp_paper', "
                        + "'inspire', 'lecture', 'phd_thesis', 'review']"
                    ),
                ]
            )

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
            "comments": "",
            "citations": 0,
            "citations_no_self": 0,
        }
        with patch(
            "physbiblio.database.Categories.getByEntry",
            return_value=[{"name": "Main"}, {"name": "second"}],
            autospec=True,
        ) as _gc, patch(
            "physbiblio.database.Experiments.getByEntry",
            return_value=[{"name": "myexp"}],
            autospec=True,
        ) as _ge, patch(
            "logging.Logger.debug"
        ) as _d:
            self.assertEqual(
                writeBibtexInfo(entry),
                "(Experimental paper) (PhD thesis) (Review) "
                + "<u>mykey</u> (use with '<u>\cite{mykey}</u>')<br/>\n"
                + "some title<br/>\n<i>AB 12 (2018) 1</i><br/>\n<br/>\n"
                + "<br/>\nCategories: <i>Main, second</i>"
                + "<br/>\nExperiments: <i>myexp</i>",
            )
            _d.assert_has_calls(
                [
                    call(
                        "KeyError: 'proceeding' not in "
                        + "['ads', 'arxiv', 'bibkey', 'bibtexDict', 'book', "
                        + "'citations', 'citations_no_self', 'comments', "
                        + "'doi', 'exp_paper', 'inspire', 'isbn', "
                        + "'lecture', 'phd_thesis', 'review']"
                    ),
                    call(
                        "KeyError: 'author' not in "
                        + "['journal', 'pages', 'title', 'volume', 'year']"
                    ),
                ]
            )

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
            "comments": None,
            "citations": 0,
            "citations_no_self": 0,
        }
        ltt = LatexNodes2Text(math_mode="verbatim", keep_comments=False)
        with patch(
            "physbiblio.database.Categories.getByEntry",
            return_value=[{"name": "Main"}, {"name": "second"}],
            autospec=True,
        ) as _gc, patch(
            "physbiblio.database.Experiments.getByEntry",
            return_value=[{"name": "exp1"}, {"name": "exp2"}],
            autospec=True,
        ) as _ge, patch(
            "logging.Logger.debug"
        ) as _d, patch(
            "physbiblio.gui.bibWindows.LatexNodes2Text",
            return_value=ltt,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i, patch(
            "pylatexenc.latex2text.LatexNodes2Text.latex_to_text",
            return_value="parsed",
            autospec=True,
        ) as _ltt:
            self.assertEqual(
                writeBibtexInfo(entry),
                "(Lecture) (Proceeding) "
                + "<u>mykey</u> (use with '<u>\cite{mykey}</u>')<br/>\n"
                + "<b>parsed</b><br/>\nparsed<br/>\n"
                + "<i>AB 12 (2018) 1</i><br/>\n<br/>\n<br/>\n"
                + "Categories: <i>Main, second</i>"
                + "<br/>\nExperiments: <i>exp1, exp2</i>",
            )
            _d.assert_not_called()
            _i.assert_called_once_with(math_mode="verbatim", keep_comments=False)
            _ltt.assert_has_calls([call(ltt, "sg"), call(ltt, "some title")])

    def test_writeAbstract(self):
        """test writeAbstract"""
        self.mainW.bottomCenter = BibtexInfo(self.mainW)
        entry = {"abstract": "some random text"}
        af = AbstractFormulas(self.mainW, entry["abstract"])
        af.doText = MagicMock(autospec=True)
        with patch(
            "physbiblio.gui.bibWindows.AbstractFormulas",
            return_value=af,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _af:
            writeAbstract(self.mainW, entry)
            _af.assert_called_once_with(self.mainW, "some random text")
            af.doText.assert_called_once_with()

    def test_editBibtex(self):
        """test editBibtex"""
        pBDB.bibs.lastFetched = ["fake"]
        testentry = {
            "bibkey": "Gariazzo:2015rra",
            "inspire": None,
            "arxiv": "1507.08204",
            "ads": None,
            "scholar": None,
            "doi": None,
            "isbn": None,
            "year": 2015,
            "link": "%s/abs/1507.08204" % pbConfig.arxivUrl,
            "comments": None,
            "old_keys": None,
            "crossref": None,
            "bibtex": "@Article{Gariazzo:2015rra,\n         "
            + 'arxiv = "1507.08204",\n}',
            "firstdate": "2018-09-01",
            "pubdate": "",
            "citations": 1234,
            "citations_no_self": 1111,
            "exp_paper": 0,
            "lecture": 0,
            "phd_thesis": 0,
            "review": 0,
            "proceeding": 0,
            "book": 0,
            "noUpdate": 0,
            "marks": "",
            "abstract": None,
            "bibtexDict": {
                "arxiv": "1507.08204",
                "ENTRYTYPE": "article",
                "ID": "Gariazzo:2015rra",
            },
            "title": "",
            "journal": "",
            "volume": "",
            "number": "",
            "pages": "",
            "published": "  (2015) ",
            "author": "",
            "bibdict": "%s"
            % {"arxiv": "1507.08204", "ENTRYTYPE": "article", "ID": "Gariazzo:2015rra"},
        }
        p = PBDialog()
        ebd = EditBibtexDialog(self.mainW, bib=None)
        ebd.exec_ = MagicMock()
        ebd.onCancel()
        with patch("logging.Logger.debug") as _ld, patch(
            "physbiblio.database.Entries.getByBibkey", autospec=True
        ) as _gbk, patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog",
            return_value=ebd,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            editBibtex(p, editKey=None)
            ebd.exec_.assert_called_once_with()
            _i.assert_called_once_with(p, bib=None)
            _ld.assert_called_once_with(
                "parentObject has no attribute 'statusBarMessage'", exc_info=True
            )
            _gbk.assert_not_called()
        with patch("logging.Logger.debug") as _ld, patch(
            "physbiblio.database.Entries.getByBibkey", autospec=True
        ) as _gbk, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _sbm, patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog",
            return_value=ebd,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            editBibtex(self.mainW, editKey=None)
            _sbm.assert_called_once_with(self.mainW, "No modifications to bibtex entry")
            _ld.assert_not_called()
            _gbk.assert_not_called()

        ebd = EditBibtexDialog(self.mainW, bib=None)
        ebd.exec_ = MagicMock()
        ebd.onCancel()
        with patch("logging.Logger.debug") as _ld, patch(
            "logging.Logger.warning"
        ) as _lw, patch("logging.Logger.info") as _li, patch(
            "physbiblio.database.Entries.getByBibkey",
            return_value=[testentry],
            autospec=True,
        ) as _gbk, patch(
            "physbiblio.database.Entries.prepareInsert",
            return_value={"bibkey": "", "bibtex": ""},
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.updateBibkey", return_value=True, autospec=True
        ) as _ub, patch(
            "physbiblio.database.Entries.update", autospec=True
        ) as _u, patch(
            "physbiblio.database.Entries.insert", autospec=True
        ) as _ins, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _ffl, patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog",
            return_value=ebd,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            editBibtex(p, editKey="Gariazzo:2015rra")
            _ld.assert_called_once_with(
                "parentObject has no attribute 'statusBarMessage'", exc_info=True
            )
            _lw.assert_not_called()
            _li.assert_not_called()
            _gbk.assert_called_once_with(pBDB.bibs, "Gariazzo:2015rra", saveQuery=False)
            _pi.assert_not_called()
            _ub.assert_not_called()
            _u.assert_not_called()
            _ins.assert_not_called()
            _ffl.assert_not_called()
            _i.assert_called_once_with(p, bib=testentry)

        # test creation of entry, empty bibtex
        ebd = EditBibtexDialog(self.mainW, bib=testentry)
        ebd.exec_ = MagicMock()
        ebd.onOk()
        ebd.textValues["bibtex"].setPlainText("")
        with patch("logging.Logger.debug") as _ld, patch(
            "logging.Logger.warning"
        ) as _lw, patch("logging.Logger.info") as _li, patch(
            "physbiblio.database.Entries.getByBibkey",
            return_value=[testentry],
            autospec=True,
        ) as _gbk, patch(
            "physbiblio.database.Entries.prepareInsert",
            return_value={"bibkey": "", "bibtex": "test"},
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.updateBibkey", return_value=True, autospec=True
        ) as _ub, patch(
            "physbiblio.database.Entries.update", autospec=True
        ) as _u, patch(
            "physbiblio.database.Entries.insert", autospec=True
        ) as _ins, patch(
            "physbiblio.pdf.LocalPDF.renameFolder", autospec=True
        ) as _rf, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _ffl, patch(
            "physbiblio.gui.bibWindows.infoMessage", autospec=True
        ) as _im, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _sbm, patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog",
            return_value=ebd,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            editBibtex(self.mainW, editKey=None)
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
            _sbm.assert_called_once_with(self.mainW, "ERROR: empty bibtex!")

        # test creation of entry, empty bibkey inserted
        ebd = EditBibtexDialog(self.mainW, bib=testentry)
        ebd.exec_ = MagicMock()
        ebd.onOk()
        ebd.textValues["bibkey"].setText("")
        with patch("logging.Logger.warning") as _lw, patch(
            "logging.Logger.info"
        ) as _li, patch(
            "physbiblio.database.Entries.getByBibkey",
            return_value=[testentry],
            autospec=True,
        ) as _gbk, patch(
            "physbiblio.database.Entries.prepareInsert",
            return_value={"bibkey": "", "bibtex": "test"},
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.updateBibkey", return_value=True, autospec=True
        ) as _ub, patch(
            "physbiblio.database.Entries.update", autospec=True
        ) as _u, patch(
            "physbiblio.database.Entries.insert", autospec=True
        ) as _ins, patch(
            "physbiblio.pdf.LocalPDF.renameFolder", autospec=True
        ) as _rf, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _ffl, patch(
            "physbiblio.gui.bibWindows.infoMessage", autospec=True
        ) as _im, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _sbm, patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog",
            return_value=ebd,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            editBibtex(self.mainW, editKey=None)
            _lw.assert_not_called()
            _li.assert_not_called()
            _gbk.assert_not_called()
            _pi.assert_called_once_with(pBDB.bibs, testentry["bibtex"])
            _ub.assert_not_called()
            _u.assert_not_called()
            _ins.assert_not_called()
            _rf.assert_not_called()
            _ffl.assert_not_called()
            _im.assert_called_once_with("ERROR: empty bibkey!")
            _sbm.assert_called_once_with(self.mainW, "ERROR: empty bibkey!")

        # test creation of entry, new bibtex
        ebd = EditBibtexDialog(self.mainW, bib=testentry)
        ebd.exec_ = MagicMock()
        ebd.onOk()
        ebd.textValues["bibkey"].setText("")
        with patch("logging.Logger.debug") as _ld, patch(
            "logging.Logger.warning"
        ) as _lw, patch("logging.Logger.info") as _li, patch(
            "physbiblio.database.Entries.getByBibkey",
            return_value=[testentry],
            autospec=True,
        ) as _gbk, patch(
            "physbiblio.database.Entries.prepareInsert",
            return_value=testentry,
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.updateBibkey", return_value=True, autospec=True
        ) as _ub, patch(
            "physbiblio.database.Entries.update", autospec=True
        ) as _u, patch(
            "physbiblio.database.Entries.insert", autospec=True
        ) as _ins, patch(
            "physbiblio.pdf.LocalPDF.renameFolder", autospec=True
        ) as _rf, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _ffl, patch(
            "physbiblio.gui.bibWindows.infoMessage", autospec=True
        ) as _im, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _sbm, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rmc, patch(
            "physbiblio.gui.mainWindow.MainWindow.mainWindowTitle", autospec=True
        ) as _swt, patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog",
            return_value=ebd,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            editBibtex(p, editKey=None)
            _ld.assert_has_calls(
                [
                    call(
                        "parentObject has no attribute 'mainWindowTitle'", exc_info=True
                    ),
                    call(
                        "parentObject has no attribute 'reloadMainContent'",
                        exc_info=True,
                    ),
                    call(
                        "parentObject has no attribute 'statusBarMessage'",
                        exc_info=True,
                    ),
                ]
            )
            _lw.assert_not_called()
            _li.assert_not_called()
            _gbk.assert_not_called()
            _pi.assert_called_once_with(pBDB.bibs, testentry["bibtex"])
            _ub.assert_not_called()
            _u.assert_not_called()
            _ins.assert_called_once_with(pBDB.bibs, testentry)
            _rf.assert_not_called()
            _ffl.assert_called_once_with(pBDB.bibs)
            _im.assert_not_called()
            _sbm.assert_not_called()
            _rmc.assert_not_called()
            _swt.assert_not_called()
        with patch("logging.Logger.warning") as _lw, patch(
            "logging.Logger.info"
        ) as _li, patch(
            "physbiblio.database.Entries.getByBibkey",
            return_value=[testentry],
            autospec=True,
        ) as _gbk, patch(
            "physbiblio.database.Entries.prepareInsert",
            return_value=testentry,
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.updateBibkey", return_value=True, autospec=True
        ) as _ub, patch(
            "physbiblio.database.Entries.update", autospec=True
        ) as _u, patch(
            "physbiblio.database.Entries.insert", autospec=True
        ) as _ins, patch(
            "physbiblio.pdf.LocalPDF.renameFolder", autospec=True
        ) as _rf, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _ffl, patch(
            "physbiblio.gui.bibWindows.infoMessage", autospec=True
        ) as _im, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _sbm, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rmc, patch(
            "physbiblio.gui.mainWindow.MainWindow.mainWindowTitle", autospec=True
        ) as _swt, patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog",
            return_value=ebd,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            editBibtex(self.mainW, editKey=None)
            _lw.assert_not_called()
            _li.assert_not_called()
            _gbk.assert_not_called()
            _pi.assert_called_once_with(pBDB.bibs, testentry["bibtex"])
            _ub.assert_not_called()
            _u.assert_not_called()
            _ins.assert_called_once_with(pBDB.bibs, testentry)
            _rf.assert_not_called()
            _ffl.assert_called_once_with(pBDB.bibs)
            _im.assert_not_called()
            _sbm.assert_called_once_with(self.mainW, "Bibtex entry saved")
            _rmc.assert_called_once_with(self.mainW, ["fake"])
            _swt.assert_called_once_with(self.mainW, "PhysBiblio*")
        with patch("logging.Logger.warning") as _lw, patch(
            "logging.Logger.info"
        ) as _li, patch("logging.Logger.error") as _le, patch(
            "physbiblio.database.Entries.getByBibkey",
            return_value=[testentry],
            autospec=True,
        ) as _gbk, patch(
            "physbiblio.database.Entries.prepareInsert",
            return_value=testentry,
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.updateBibkey", return_value=True, autospec=True
        ) as _ub, patch(
            "physbiblio.database.Entries.update", autospec=True
        ) as _u, patch(
            "physbiblio.database.Entries.insert", return_value=False, autospec=True
        ) as _ins, patch(
            "physbiblio.pdf.LocalPDF.renameFolder", autospec=True
        ) as _rf, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _ffl, patch(
            "physbiblio.gui.bibWindows.infoMessage", autospec=True
        ) as _im, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _sbm, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rmc, patch(
            "physbiblio.gui.mainWindow.MainWindow.mainWindowTitle", autospec=True
        ) as _swt, patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog",
            return_value=ebd,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            editBibtex(self.mainW, editKey=None)
            _lw.assert_not_called()
            _li.assert_not_called()
            _le.assert_called_once_with("Cannot insert/modify the entry!")
            _gbk.assert_not_called()
            _pi.assert_called_once_with(pBDB.bibs, testentry["bibtex"])
            _ub.assert_not_called()
            _u.assert_not_called()
            _ins.assert_called_once_with(pBDB.bibs, testentry)
            _rf.assert_not_called()
            _ffl.assert_called_once_with(pBDB.bibs)
            _im.assert_not_called()
            _sbm.assert_called_once_with(self.mainW, "Cannot insert/modify the entry!")
            _rmc.assert_called_once_with(self.mainW, ["fake"])
            _swt.assert_not_called()

        # test edit with various field contents
        # * no change bibkey: fix code?
        ebd = EditBibtexDialog(self.mainW, bib=testentry)
        ebd.exec_ = MagicMock()
        ebd.citations = 123
        ebd.citations_no_self = 111
        ebd.onOk()
        ebd.textValues["comments"].setPlainText("some text")
        with patch("logging.Logger.warning") as _lw, patch(
            "logging.Logger.info"
        ) as _li, patch(
            "physbiblio.database.Entries.getByBibkey",
            return_value=[testentry],
            autospec=True,
        ) as _gbk, patch(
            "physbiblio.database.Entries.prepareInsert",
            return_value=testentry,
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.updateBibkey", return_value=True, autospec=True
        ) as _ub, patch(
            "physbiblio.database.Entries.update", autospec=True
        ) as _u, patch(
            "physbiblio.database.Entries.insert", autospec=True
        ) as _ins, patch(
            "physbiblio.pdf.LocalPDF.renameFolder", autospec=True
        ) as _rf, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _ffl, patch(
            "physbiblio.gui.bibWindows.infoMessage", autospec=True
        ) as _im, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _sbm, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rmc, patch(
            "physbiblio.gui.mainWindow.MainWindow.mainWindowTitle", autospec=True
        ) as _swt, patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog",
            return_value=ebd,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            editBibtex(self.mainW, editKey="Gariazzo:2015rra")
            _i.assert_called_once_with(self.mainW, bib=testentry)
            _lw.assert_not_called()
            _li.assert_called_once_with("Updating bibtex 'Gariazzo:2015rra'...")
            _gbk.assert_called_once_with(pBDB.bibs, "Gariazzo:2015rra", saveQuery=False)
            _pi.assert_not_called()
            _ub.assert_not_called()
            self.assertEqual(_u.call_count, 1)
            b, d, k = _u.call_args[0]
            self.assertEqual(b, pBDB.bibs)
            self.assertEqual(k, u"Gariazzo:2015rra")
            for k, v in {
                "isbn": u"",
                "inspire": u"",
                "pubdate": u"",
                "year": u"2015",
                "phd_thesis": 0,
                "bibkey": u"Gariazzo:2015rra",
                "proceeding": 0,
                "ads": u"",
                "review": 0,
                "comments": u"some text",
                "book": 0,
                "marks": "",
                "lecture": 0,
                "crossref": u"",
                "noUpdate": 0,
                "link": u"https://arxiv.org/abs/1507.08204",
                "exp_paper": 0,
                "citations": 123,
                "citations_no_self": 111,
                "doi": u"",
                "scholar": u"",
                "arxiv": u"1507.08204",
                "bibtex": u"@Article{Gariazzo:2015rra,\n         arxiv "
                + '= "1507.08204",\n}',
                "abstract": "",
                "firstdate": u"2018-09-01",
                "old_keys": u"",
            }.items():
                self.assertEqual(d[k], v)
            _ins.assert_not_called()
            _rf.assert_not_called()
            _ffl.assert_called_once_with(pBDB.bibs)
            _im.assert_not_called()
            _sbm.assert_called_once_with(self.mainW, "Bibtex entry saved")
            _rmc.assert_called_once_with(self.mainW, ["fake"])
            _swt.assert_called_once_with(self.mainW, "PhysBiblio*")
        with patch("logging.Logger.warning") as _lw, patch(
            "logging.Logger.info"
        ) as _li, patch("logging.Logger.error") as _le, patch(
            "physbiblio.database.Entries.getByBibkey",
            return_value=[testentry],
            autospec=True,
        ) as _gbk, patch(
            "physbiblio.database.Entries.prepareInsert",
            return_value=testentry,
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.updateBibkey", return_value=True, autospec=True
        ) as _ub, patch(
            "physbiblio.database.Entries.update", return_value=False, autospec=True
        ) as _u, patch(
            "physbiblio.database.Entries.insert", autospec=True
        ) as _ins, patch(
            "physbiblio.pdf.LocalPDF.renameFolder", autospec=True
        ) as _rf, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _ffl, patch(
            "physbiblio.gui.bibWindows.infoMessage", autospec=True
        ) as _im, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _sbm, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rmc, patch(
            "physbiblio.gui.mainWindow.MainWindow.mainWindowTitle", autospec=True
        ) as _swt, patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog",
            return_value=ebd,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            editBibtex(self.mainW, editKey="Gariazzo:2015rra")
            _i.assert_called_once_with(self.mainW, bib=testentry)
            _lw.assert_not_called()
            _li.assert_called_once_with("Updating bibtex 'Gariazzo:2015rra'...")
            _le.assert_called_once_with("Cannot insert/modify the entry!")
            _gbk.assert_called_once_with(pBDB.bibs, "Gariazzo:2015rra", saveQuery=False)
            _pi.assert_not_called()
            _ub.assert_not_called()
            self.assertEqual(_u.call_count, 1)
            b, d, k = _u.call_args[0]
            self.assertEqual(b, pBDB.bibs)
            self.assertEqual(k, u"Gariazzo:2015rra")
            for k, v in {
                "isbn": u"",
                "inspire": u"",
                "pubdate": u"",
                "year": u"2015",
                "phd_thesis": 0,
                "bibkey": u"Gariazzo:2015rra",
                "proceeding": 0,
                "ads": u"",
                "review": 0,
                "comments": u"some text",
                "book": 0,
                "marks": "",
                "lecture": 0,
                "crossref": u"",
                "noUpdate": 0,
                "link": u"https://arxiv.org/abs/1507.08204",
                "exp_paper": 0,
                "citations": 123,
                "citations_no_self": 111,
                "doi": u"",
                "scholar": u"",
                "arxiv": u"1507.08204",
                "bibtex": u"@Article{Gariazzo:2015rra,\n         arxiv "
                + '= "1507.08204",\n}',
                "abstract": "",
                "firstdate": u"2018-09-01",
                "old_keys": u"",
            }.items():
                self.assertEqual(d[k], v)
            _ins.assert_not_called()
            _rf.assert_not_called()
            _ffl.assert_called_once_with(pBDB.bibs)
            _im.assert_not_called()
            _sbm.assert_called_once_with(self.mainW, "Cannot insert/modify the entry!")
            _rmc.assert_called_once_with(self.mainW, ["fake"])
            _swt.assert_not_called()

        # * invalid key
        ebd = EditBibtexDialog(self.mainW, bib=testentry)
        ebd.exec_ = MagicMock()
        ebd.onOk()
        ebd.textValues["bibkey"].setText("not valid bibtex!")
        with patch("logging.Logger.warning") as _lw, patch(
            "logging.Logger.info"
        ) as _li, patch(
            "physbiblio.database.Entries.getByBibkey",
            return_value=[testentry],
            autospec=True,
        ) as _gbk, patch(
            "physbiblio.database.Entries.prepareInsert",
            return_value=testentry,
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.updateBibkey", return_value=True, autospec=True
        ) as _ub, patch(
            "physbiblio.database.Entries.update", autospec=True
        ) as _u, patch(
            "physbiblio.database.Entries.insert", autospec=True
        ) as _ins, patch(
            "physbiblio.pdf.LocalPDF.renameFolder", autospec=True
        ) as _rf, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _ffl, patch(
            "physbiblio.gui.bibWindows.infoMessage", autospec=True
        ) as _im, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _sbm, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rmc, patch(
            "physbiblio.gui.mainWindow.MainWindow.mainWindowTitle", autospec=True
        ) as _swt, patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog",
            return_value=ebd,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            editBibtex(self.mainW, editKey="testkey")
            _i.assert_called_once_with(self.mainW, bib=testentry)
            _lw.assert_not_called()
            _li.assert_has_calls([call("Updating bibtex 'testkey'...")])
            _gbk.assert_called_once_with(pBDB.bibs, "testkey", saveQuery=False)
            _pi.assert_not_called()
            _ub.assert_not_called()
            self.assertEqual(_u.call_count, 1)
            b, d, k = _u.call_args[0]
            self.assertEqual(b, pBDB.bibs)
            self.assertEqual(k, u"testkey")
            for k, v in {
                "isbn": u"",
                "inspire": u"",
                "pubdate": u"",
                "year": u"2015",
                "phd_thesis": 0,
                "bibkey": u"testkey",
                "proceeding": 0,
                "ads": u"",
                "review": 0,
                "comments": u"",
                "book": 0,
                "marks": "",
                "lecture": 0,
                "crossref": u"",
                "noUpdate": 0,
                "citations": 1234,
                "citations_no_self": 1111,
                "link": u"https://arxiv.org/abs/1507.08204",
                "exp_paper": 0,
                "doi": u"",
                "scholar": u"",
                "arxiv": u"1507.08204",
                "bibtex": u"@Article{Gariazzo:2015rra,\n         arxiv "
                + '= "1507.08204",\n}',
                "abstract": "",
                "firstdate": u"2018-09-01",
                "old_keys": u"",
            }.items():
                self.assertEqual(d[k], v)
            _ins.assert_not_called()
            _rf.assert_not_called()
            _ffl.assert_called_once_with(pBDB.bibs)
            _im.assert_not_called()
            _sbm.assert_called_once_with(self.mainW, "Bibtex entry saved")
            _rmc.assert_called_once_with(self.mainW, ["fake"])
            _swt.assert_called_once_with(self.mainW, "PhysBiblio*")

        # * with update bibkey, updateBibkey successful
        del testentry["citations"]
        del testentry["citations_no_self"]
        ebd = EditBibtexDialog(self.mainW, bib=testentry)
        ebd.exec_ = MagicMock()
        ebd.onOk()
        ebd.textValues["old_keys"].setText("old")
        with patch("logging.Logger.warning") as _lw, patch(
            "logging.Logger.info"
        ) as _li, patch(
            "physbiblio.database.Entries.getByBibkey",
            return_value=[testentry],
            autospec=True,
        ) as _gbk, patch(
            "physbiblio.database.Entries.prepareInsert",
            return_value=testentry,
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.updateBibkey", return_value=True, autospec=True
        ) as _ub, patch(
            "physbiblio.database.Entries.update", autospec=True
        ) as _u, patch(
            "physbiblio.database.Entries.insert", autospec=True
        ) as _ins, patch(
            "physbiblio.pdf.LocalPDF.renameFolder", autospec=True
        ) as _rf, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _ffl, patch(
            "physbiblio.gui.bibWindows.infoMessage", autospec=True
        ) as _im, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _sbm, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rmc, patch(
            "physbiblio.gui.mainWindow.MainWindow.mainWindowTitle", autospec=True
        ) as _swt, patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog",
            return_value=ebd,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            editBibtex(self.mainW, editKey="testkey")
            _lw.assert_not_called()
            _li.assert_has_calls(
                [
                    call(
                        "New bibtex key (Gariazzo:2015rra) for "
                        + "element 'testkey'..."
                    ),
                    call("Updating bibtex 'Gariazzo:2015rra'..."),
                ]
            )
            _gbk.assert_called_once_with(pBDB.bibs, "testkey", saveQuery=False)
            _pi.assert_not_called()
            _ub.assert_called_once_with(pBDB.bibs, "testkey", u"Gariazzo:2015rra")
            self.assertEqual(_u.call_count, 1)
            b, d, k = _u.call_args[0]
            self.assertEqual(b, pBDB.bibs)
            self.assertEqual(k, u"Gariazzo:2015rra")
            for k, v in {
                "isbn": u"",
                "inspire": u"",
                "pubdate": u"",
                "year": u"2015",
                "phd_thesis": 0,
                "bibkey": u"Gariazzo:2015rra",
                "proceeding": 0,
                "ads": u"",
                "review": 0,
                "comments": u"",
                "book": 0,
                "marks": "",
                "lecture": 0,
                "crossref": u"",
                "noUpdate": 0,
                "link": u"https://arxiv.org/abs/1507.08204",
                "exp_paper": 0,
                "citations": 0,
                "citations_no_self": 0,
                "doi": u"",
                "scholar": u"",
                "arxiv": u"1507.08204",
                "bibtex": u"@Article{Gariazzo:2015rra,\n         arxiv "
                + '= "1507.08204",\n}',
                "abstract": "",
                "firstdate": u"2018-09-01",
                "old_keys": u"old testkey",
            }.items():
                self.assertEqual(d[k], v)
            _ins.assert_not_called()
            _rf.assert_called_once_with(pBPDF, "testkey", u"Gariazzo:2015rra")
            _ffl.assert_called_once_with(pBDB.bibs)
            _im.assert_not_called()
            _sbm.assert_called_once_with(self.mainW, "Bibtex entry saved")
            _rmc.assert_called_once_with(self.mainW, ["fake"])
            _swt.assert_called_once_with(self.mainW, "PhysBiblio*")

        # * with update bibkey, updateBibkey unsuccessful
        ebd = EditBibtexDialog(self.mainW, bib=testentry)
        ebd.exec_ = MagicMock()
        ebd.onOk()
        with patch("logging.Logger.warning") as _lw, patch(
            "logging.Logger.info"
        ) as _li, patch(
            "physbiblio.database.Entries.getByBibkey",
            return_value=[testentry],
            autospec=True,
        ) as _gbk, patch(
            "physbiblio.database.Entries.prepareInsert",
            return_value=testentry,
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.updateBibkey",
            return_value=False,
            autospec=True,
        ) as _ub, patch(
            "physbiblio.database.Entries.update", autospec=True
        ) as _u, patch(
            "physbiblio.database.Entries.insert", autospec=True
        ) as _ins, patch(
            "physbiblio.pdf.LocalPDF.renameFolder", autospec=True
        ) as _rf, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _ffl, patch(
            "physbiblio.gui.bibWindows.infoMessage", autospec=True
        ) as _im, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _sbm, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rmc, patch(
            "physbiblio.gui.mainWindow.MainWindow.mainWindowTitle", autospec=True
        ) as _swt, patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog",
            return_value=ebd,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            editBibtex(self.mainW, editKey="testkey")
            _lw.assert_called_once_with(
                "Cannot update bibtex key: "
                + "already present. Restoring previous one."
            )
            _li.assert_has_calls(
                [
                    call(
                        "New bibtex key (Gariazzo:2015rra) for "
                        + "element 'testkey'..."
                    ),
                    call("Updating bibtex 'testkey'..."),
                ]
            )
            _gbk.assert_called_once_with(pBDB.bibs, "testkey", saveQuery=False)
            _pi.assert_not_called()
            _ub.assert_called_once_with(pBDB.bibs, "testkey", u"Gariazzo:2015rra")
            self.assertEqual(_u.call_count, 1)
            b, d, k = _u.call_args[0]
            self.assertEqual(b, pBDB.bibs)
            self.assertEqual(k, u"testkey")
            for k, v in {
                "isbn": u"",
                "inspire": u"",
                "pubdate": u"",
                "year": u"2015",
                "phd_thesis": 0,
                "bibkey": u"testkey",
                "proceeding": 0,
                "ads": u"",
                "review": 0,
                "comments": u"",
                "book": 0,
                "marks": "",
                "lecture": 0,
                "crossref": u"",
                "noUpdate": 0,
                "link": u"https://arxiv.org/abs/1507.08204",
                "exp_paper": 0,
                "doi": u"",
                "scholar": u"",
                "arxiv": u"1507.08204",
                "bibtex": u"@Article{testkey,\n         arxiv " + '= "1507.08204",\n}',
                "abstract": "",
                "firstdate": u"2018-09-01",
                "old_keys": u"testkey",
            }.items():
                self.assertEqual(d[k], v)
            _ins.assert_not_called()
            _rf.assert_not_called()
            _ffl.assert_called_once_with(pBDB.bibs)
            _im.assert_not_called()
            _sbm.assert_called_once_with(self.mainW, "Bibtex entry saved")
            _rmc.assert_called_once_with(self.mainW, ["fake"])
            _swt.assert_called_once_with(self.mainW, "PhysBiblio*")

        # * with update bibkey, old_keys existing
        ebd = EditBibtexDialog(self.mainW, bib=testentry)
        ebd.exec_ = MagicMock()
        ebd.onOk()
        ebd.textValues["old_keys"].setText("testkey")
        with patch("logging.Logger.warning") as _lw, patch(
            "logging.Logger.info"
        ) as _li, patch(
            "physbiblio.database.Entries.getByBibkey",
            return_value=[testentry],
            autospec=True,
        ) as _gbk, patch(
            "physbiblio.database.Entries.prepareInsert",
            return_value=testentry,
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.updateBibkey",
            return_value=False,
            autospec=True,
        ) as _ub, patch(
            "physbiblio.database.Entries.update", autospec=True
        ) as _u, patch(
            "physbiblio.database.Entries.insert", autospec=True
        ) as _ins, patch(
            "physbiblio.pdf.LocalPDF.renameFolder", autospec=True
        ) as _rf, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _ffl, patch(
            "physbiblio.gui.bibWindows.infoMessage", autospec=True
        ) as _im, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _sbm, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rmc, patch(
            "physbiblio.gui.mainWindow.MainWindow.mainWindowTitle", autospec=True
        ) as _swt, patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog",
            return_value=ebd,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            editBibtex(self.mainW, editKey="testkey")
            _lw.assert_called_once_with(
                "Cannot update bibtex key: "
                + "already present. Restoring previous one."
            )
            _li.assert_has_calls(
                [
                    call(
                        "New bibtex key (Gariazzo:2015rra) for "
                        + "element 'testkey'..."
                    ),
                    call("Updating bibtex 'testkey'..."),
                ]
            )
            _gbk.assert_called_once_with(pBDB.bibs, "testkey", saveQuery=False)
            _pi.assert_not_called()
            _ub.assert_called_once_with(pBDB.bibs, "testkey", u"Gariazzo:2015rra")
            self.assertEqual(_u.call_count, 1)
            b, d, k = _u.call_args[0]
            self.assertEqual(b, pBDB.bibs)
            self.assertEqual(k, u"testkey")
            for k, v in {
                "isbn": u"",
                "inspire": u"",
                "pubdate": u"",
                "year": u"2015",
                "phd_thesis": 0,
                "bibkey": u"testkey",
                "proceeding": 0,
                "ads": u"",
                "review": 0,
                "comments": u"",
                "book": 0,
                "marks": "",
                "lecture": 0,
                "crossref": u"",
                "noUpdate": 0,
                "link": u"https://arxiv.org/abs/1507.08204",
                "exp_paper": 0,
                "doi": u"",
                "scholar": u"",
                "arxiv": u"1507.08204",
                "bibtex": u"@Article{testkey,\n         arxiv " + '= "1507.08204",\n}',
                "abstract": "",
                "firstdate": u"2018-09-01",
                "old_keys": u"testkey",
            }.items():
                self.assertEqual(d[k], v)
            _ins.assert_not_called()
            _rf.assert_not_called()
            _ffl.assert_called_once_with(pBDB.bibs)
            _im.assert_not_called()
            _sbm.assert_called_once_with(self.mainW, "Bibtex entry saved")
            _rmc.assert_called_once_with(self.mainW, ["fake"])
            _swt.assert_called_once_with(self.mainW, "PhysBiblio*")

    def test_deleteBibtex(self):
        """test deleteBibtex"""
        p = QWidget()
        m = self.mainW
        m.bibtexListWindows.append([BibtexListWindow(self.mainW, bibs=[]), "Main Tab"])
        with patch(
            "physbiblio.gui.bibWindows.askYesNo", return_value=False, autospec=True
        ) as _a, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s:
            deleteBibtex(self.mainW, "mykey")
            _a.assert_called_once_with(
                "Do you really want to delete this bibtex entry "
                + "(bibkey = 'mykey')?"
            )
            _s.assert_called_once_with(self.mainW, "Nothing changed")

        with patch(
            "physbiblio.gui.bibWindows.askYesNo", return_value=False, autospec=True
        ) as _a, patch("logging.Logger.debug") as _d:
            deleteBibtex(p, "mykey")
            _a.assert_called_once_with(
                "Do you really want to delete this bibtex entry "
                + "(bibkey = 'mykey')?"
            )
            _d.assert_called_once_with(
                "parentObject has no attribute 'statusBarMessage'", exc_info=True
            )

        with patch(
            "physbiblio.gui.bibWindows.askYesNo", return_value=True, autospec=True
        ) as _a, patch(
            "physbiblio.database.Entries.delete", autospec=True
        ) as _c, patch(
            "PySide2.QtWidgets.QMainWindow.setWindowTitle", autospec=True
        ) as _t, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "logging.Logger.debug"
        ) as _d:
            deleteBibtex(p, "mykey")
            _a.assert_called_once_with(
                "Do you really want to delete this bibtex entry "
                + "(bibkey = 'mykey')?"
            )
            _c.assert_called_once_with(pBDB.bibs, "mykey")
            _t.assert_not_called()
            _s.assert_not_called()
            _d.assert_has_calls(
                [
                    call(
                        "parentObject has no attribute 'recreateTable'", exc_info=True
                    ),
                    call(
                        "parentObject has no attribute 'statusBarMessage'",
                        exc_info=True,
                    ),
                ]
            )

        self.mainW.tabWidget.setCurrentIndex(0)
        with patch(
            "physbiblio.gui.bibWindows.askYesNo", return_value=True, autospec=True
        ) as _a, patch(
            "physbiblio.database.Entries.delete", autospec=True
        ) as _c, patch(
            "PySide2.QtWidgets.QMainWindow.setWindowTitle", autospec=True
        ) as _t, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.recreateTable", autospec=True
        ) as _r:
            deleteBibtex(self.mainW, "mykey")
            _a.assert_called_once_with(
                "Do you really want to delete this bibtex entry "
                + "(bibkey = 'mykey')?"
            )
            _c.assert_called_once_with(pBDB.bibs, "mykey")
            _t.assert_called_once_with("PhysBiblio*")
            _s.assert_called_once_with(self.mainW, "Bibtex entry deleted")
            _r.assert_called_once_with(self.mainW.bibtexListWindows[0][0])


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestAbstractFormulas(GUIwMainWTestCase):
    """test the AbstractFormulas class"""

    def test_init(self):
        """test __init__"""
        self.mainW.bottomCenter = BibtexInfo(self.mainW)
        af = AbstractFormulas(self.mainW, "test text")
        self.assertEqual(af.fontsize, pbConfig.params["bibListFontSize"])
        self.assertEqual(af.mainWin, self.mainW)
        self.assertEqual(af.statusMessages, True)
        self.assertEqual(af.editor, self.mainW.bottomCenter.text)
        self.assertIsInstance(af.document, QTextDocument)
        self.assertEqual(af.editor.document(), af.document)
        self.assertEqual(af.abstractTitle, "<b>Abstract:</b><br/>")
        self.assertEqual(af.text, "<b>Abstract:</b><br/>test text")

        bi = BibtexInfo()
        af = AbstractFormulas(
            self.mainW,
            "test text",
            fontsize=99,
            abstractTitle="Title",
            customEditor=bi.text,
            statusMessages="a",
        )
        self.assertEqual(af.fontsize, 99)
        self.assertEqual(af.mainWin, self.mainW)
        self.assertEqual(af.statusMessages, "a")
        self.assertEqual(af.editor, bi.text)
        self.assertIsInstance(af.document, QTextDocument)
        self.assertEqual(af.editor.document(), af.document)
        self.assertEqual(af.abstractTitle, "Title")
        self.assertEqual(af.text, "Titletest text")

    def test_hasLatex(self):
        """test hasLatex"""
        self.mainW.bottomCenter = BibtexInfo(self.mainW)
        af = AbstractFormulas(self.mainW, "test text")
        self.assertEqual(af.hasLatex(), False)
        af = AbstractFormulas(self.mainW, "test tex $f_e$ equation")
        self.assertEqual(af.hasLatex(), True)

    def test_doText(self):
        """test doText"""
        bi = BibtexInfo(self.mainW)
        af = AbstractFormulas(self.mainW, "test text", customEditor=bi.text)
        with patch("PySide2.QtWidgets.QTextEdit.setHtml", autospec=True) as _ih, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _sbm:
            af.doText()
            _ih.assert_called_once_with(af.text)
            _sbm.assert_not_called()

        af = AbstractFormulas(
            self.mainW, "test text with $f_e$ equation", customEditor=bi.text
        )
        tpl = Thread_processLatex(af.prepareText, self.mainW)
        tpl.passData = 1
        tpl.start = MagicMock()
        with patch("PySide2.QtWidgets.QTextEdit.setHtml", autospec=True) as _ih, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _sbm, patch(
            "physbiblio.gui.bibWindows.Thread_processLatex",
            return_value=tpl,
            autospec=True,
        ) as _pl:
            with self.assertRaises(AttributeError):
                af.doText()
            _sbm.assert_called_once_with(self.mainW, "Parsing LaTeX...")
            _ih.assert_called_once_with(
                "%sProcessing LaTeX formulas..." % af.abstractTitle
            )
            _pl.assert_called_once_with(af.prepareText, self.mainW)
        tpl = Thread_processLatex(af.prepareText, self.mainW)
        with patch("PySide2.QtWidgets.QTextEdit.setHtml", autospec=True) as _ih, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _sbm, patch(
            "physbiblio.gui.commonClasses.PBThread.start", autospec=True
        ) as _s, patch(
            "physbiblio.gui.bibWindows.AbstractFormulas.submitText", autospec=True
        ) as _st:
            af.doText()
            _sbm.assert_called_once_with(self.mainW, "Parsing LaTeX...")
            _ih.assert_called_once_with(
                "%sProcessing LaTeX formulas..." % af.abstractTitle
            )
            _s.assert_called_once_with(af.thr)
            self.assertIsInstance(af.thr, Thread_processLatex)
            images, text = af.prepareText()
            _st.assert_not_called()
            af.thr.passData.emit(images, text)
            _st.assert_called_once_with(af, images, text)

    def test_mathTexToQPixmap(self):
        """test mathTex_to_QPixmap"""
        bi = BibtexInfo(self.mainW)
        af = AbstractFormulas(
            self.mainW, r"test $\nu_\mu$ with $f_e$ equation", customEditor=bi.text
        )
        qi = af.mathTex_to_QPixmap(r"$\nu_\mu$")
        self.assertIsInstance(qi, QImage)
        with patch(
            "matplotlib.figure.Figure", return_value=None, autospec=True
        ) as _fi, self.assertRaises(AttributeError):
            qi = af.mathTex_to_QPixmap(r"$\nu_\mu$")
            _fi.assert_called_once_with()
        with patch(
            "matplotlib.axes.Axes.text", return_value=None, autospec=True
        ) as _t, self.assertRaises(AttributeError):
            qi = af.mathTex_to_QPixmap(r"$\nu_\mu$")
            _t.assert_called_once_with(
                0,
                0,
                r"$\nu_\mu$",
                ha="left",
                va="bottom",
                fontsize=pbConfig.params["bibListFontSize"],
            )
        fc = FigureCanvasAgg(matplotlib.figure.Figure())
        qii = QImage()
        with patch(
            "matplotlib.backends.backend_agg.FigureCanvasAgg.print_to_buffer",
            return_value=("buf", ["size0", "size1"]),
            autospec=True,
        ) as _ptb, patch(
            "physbiblio.gui.bibWindows.FigureCanvasAgg",
            return_value=fc,
            autospec=USE_AUTOSPEC_CLASS,
        ), patch(
            "PySide2.QtGui.QImage", return_value=qii, autospec=True
        ) as _qii, self.assertRaises(
            AttributeError
        ):
            qi = af.mathTex_to_QPixmap(r"$\nu_\mu$")
            _ptb.assert_called_once_with(fc)
            _qii.assert_calle_once_with("buf", "size0", "size1", QImage.Format_ARGB32)

    def test_prepareText(self):
        """test prepareText"""
        bi = BibtexInfo(self.mainW)
        af = AbstractFormulas(
            self.mainW, r"test $\nu_\mu$ with $f_e$ equation", customEditor=bi.text
        )
        with patch(
            "physbiblio.gui.bibWindows.AbstractFormulas.mathTex_to_QPixmap",
            side_effect=["a", "b"],
            autospec=True,
        ) as _mq:
            i, t = af.prepareText()
            self.assertEqual(i, ["a", "b"])
            self.assertEqual(
                t,
                "<b>Abstract:</b><br/>"
                + 'test <img src="mydata://image0.png" /> '
                + 'with <img src="mydata://image1.png" /> equation',
            )
            _mq.assert_has_calls([call(af, r"$\nu_\mu$"), call(af, "$f_e$")])

    def test_submitText(self):
        """test submitText"""
        bi = BibtexInfo(self.mainW)
        af = AbstractFormulas(
            self.mainW, r"test $\nu_\mu$ with $f_e$ equation", customEditor=bi.text
        )
        images, text = af.prepareText()
        with patch(
            "PySide2.QtGui.QTextDocument.addResource", autospec=True
        ) as _ar, patch(
            "PySide2.QtWidgets.QTextEdit.setHtml", autospec=True
        ) as _ih, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _sbm:
            af.submitText(images, text)
            _ar.assert_has_calls(
                [
                    call(
                        QTextDocument.ImageResource,
                        QUrl("mydata://image0.png"),
                        images[0],
                    ),
                    call(
                        QTextDocument.ImageResource,
                        QUrl("mydata://image1.png"),
                        images[1],
                    ),
                ]
            )
            _ih.assert_called_once_with(text)
            _sbm.assert_called_once_with(self.mainW, "Latex processing done!")


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
        self.assertEqual(bi.text.font().pointSize(), pbConfig.params["bibListFontSize"])
        self.assertEqual(bi.text.isReadOnly(), True)
        self.assertEqual(bi.layout().itemAt(0).widget(), bi.text)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestBibTableModel(GUITestCase):
    """test the `BibTableModel` methods"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        biblist = [{"bibkey": "a"}, {"bibkey": "b"}]
        header = ["A", "B", "C"]
        tm = BibTableModel(p, biblist, header)
        self.assertIsInstance(tm, PBTableModel)
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

        ltt = LatexNodes2Text(math_mode="verbatim", keep_comments=False)
        with patch(
            "physbiblio.gui.bibWindows.BibTableModel.prepareSelected", autospec=True
        ) as _ps, patch(
            "physbiblio.gui.bibWindows.LatexNodes2Text",
            return_value=ltt,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _il:
            tm = BibTableModel(
                p,
                biblist,
                header,
                stdCols=["s1", "s2"],
                addCols=["a1", "a2"],
                askBibs=True,
                previous=[1, 2, 3],
                mainWin="m",
            )
            _il.assert_called_once_with(math_mode="text", keep_comments=False)
            _ps.assert_called_once_with(tm)
        self.assertIsInstance(tm, PBTableModel)
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
        tm = BibTableModel(p, biblist, header)
        self.assertEqual(tm.getIdentifier(biblist[0]), "a")
        self.assertEqual(tm.getIdentifier(biblist[1]), "b")

    def test_addTypeCell(self):
        """test addTypeCell"""
        p = QWidget()
        biblist = [
            {
                "bibkey": "a",
                "review": 1,
                "proceeding": 1,
                "book": 1,
                "phd_thesis": 1,
                "lecture": 1,
                "exp_paper": 1,
            }
        ]
        header = ["A", "B", "C"]
        tm = BibTableModel(p, biblist, header)
        self.assertEqual(
            tm.addTypeCell(biblist[0]),
            "Book, Experimental paper, Lecture, PhD thesis, Proceeding, Review",
        )

        biblist = [
            {
                "bibkey": "a",
                "review": 1,
                "proceeding": 0,
                "book": 0,
                "phd_thesis": 0,
                "lecture": 0,
                "exp_paper": 0,
            }
        ]
        self.assertEqual(tm.addTypeCell(biblist[0]), "Review")

        biblist = [
            {
                "bibkey": "a",
                "review": 0,
                "proceeding": 0,
                "book": 0,
                "phd_thesis": 0,
                "lecture": 0,
                "exp_paper": 0,
            }
        ]
        self.assertEqual(tm.addTypeCell(biblist[0]), "")

        biblist = [
            {
                "bibkey": "a",
                "review": 0,
                "proceeding": 0,
                "phd_thesis": 0,
                "lecture": 0,
                "exp_paper": 0,
            }
        ]
        with patch("logging.Logger.debug") as _d:
            self.assertEqual(tm.addTypeCell(biblist[0]), "")
            _d.assert_called_once_with(
                "Key not present: 'book'\nin ['bibkey', 'exp_paper', "
                + "'lecture', 'phd_thesis', 'proceeding', 'review']"
            )

    def test_addPDFCell(self):
        """test addPDFCell"""
        biblist = [{"bibkey": "a"}]
        header = ["A", "B", "C"]
        m = BibtexListWindow(bibs=[])
        tm = BibTableModel(m, biblist, header)
        with patch(
            "physbiblio.pdf.LocalPDF.getExisting", return_value=[], autospec=True
        ) as _ge:
            self.assertEqual(tm.addPDFCell("a"), (False, "no PDF"))
            _ge.assert_called_once_with(pBPDF, "a")
        with patch(
            "physbiblio.pdf.LocalPDF.getExisting", return_value=["a"], autospec=True
        ) as _ge, patch(
            "physbiblio.gui.commonClasses.PBTableModel.addImage",
            return_value="image",
            autospec=True,
        ) as _ai:
            self.assertEqual(tm.addPDFCell("a"), (True, "image"))
            _ge.assert_called_once_with(pBPDF, "a")
            _ai.assert_called_once_with(
                tm, ":/images/application-pdf.png", m.tableview.rowHeight(0) * 0.9
            )

    def test_addMarksCell(self):
        """test addMarksCell"""
        with patch("logging.Logger.debug") as _d:
            m = BibtexListWindow(
                bibs=[
                    {
                        "bibkey": "a",
                        "title": "my title A",
                        "author": r"St{\'e}",
                        "marks": "",
                        "bibtex": "@article{A}",
                        "arxiv": "1809.00000",
                    }
                ]
            )
        biblist = [{"bibkey": "a"}, {"bibkey": "b"}]
        header = ["A", "B", "C"]
        tm = BibTableModel(m, biblist, header)
        self.assertEqual(tm.addMarksCell(None), (False, ""))
        self.assertEqual(tm.addMarksCell(123), (False, ""))
        self.assertEqual(tm.addMarksCell("r a n d o m s t r i n g"), (False, ""))
        with patch(
            "physbiblio.gui.commonClasses.PBTableModel.addImages",
            return_value="called",
            autospec=True,
        ) as _ai:
            self.assertEqual(tm.addMarksCell("new,imp"), (True, "called"))
            _ai.assert_called_once_with(
                tm,
                [":/images/emblem-important-symbolic.png", ":/images/unread-new.png"],
                m.tableview.rowHeight(0) * 0.9,
            )
        with patch(
            "physbiblio.gui.commonClasses.PBTableModel.addImage",
            return_value="called",
            autospec=True,
        ) as _ai:
            self.assertEqual(tm.addMarksCell(u"new"), (True, "called"))
            _ai.assert_called_once_with(
                tm, ":/images/unread-new.png", m.tableview.rowHeight(0) * 0.9
            )

    def test_data(self):
        """test data"""
        m = BibtexListWindow(
            bibs=[
                {
                    "bibkey": "a",
                    "title": "my title A",
                    "author": r"St{\'e}",
                    "marks": "",
                    "bibtex": "@article{A}",
                    "arxiv": "1809.00000",
                }
            ]
        )
        biblist = [
            {
                "bibkey": "a",
                "title": "my title A",
                "author": r"St{\'e}",
                "marks": "",
                "bibtex": "@article{A}",
                "arxiv": "1809.00000",
            },
            {
                "bibkey": "b",
                "title": "my title {\mu}",
                "author": "Gar",
                "bibtex": "@article{B}",
                "book": 1,
                "marks": "new,imp",
            },
        ]
        header = ["bibkey", "marks", "title", "author", "arxiv"]
        addCols = ["Type", "PDF"]
        tm = BibTableModel(
            m, biblist, header + addCols, header, addCols, previous=["b"], askBibs=True
        )
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
        self.assertEqual(tm.data(tm.index(0, 3), Qt.DisplayRole), u"St\xe9")
        self.assertEqual(tm.data(tm.index(0, 4), Qt.DisplayRole), "1809.00000")
        self.assertEqual(tm.data(tm.index(1, 2), Qt.DisplayRole), u"my title \u03bc")
        self.assertEqual(tm.data(tm.index(1, 3), Qt.DisplayRole), "Gar")
        self.assertEqual(tm.data(tm.index(1, 3), Qt.CheckStateRole), None)
        self.assertEqual(tm.data(tm.index(1, 4), Qt.DisplayRole), "")

        # check marks
        with patch(
            "physbiblio.gui.bibWindows.BibTableModel.addMarksCell",
            return_value=(False, ""),
            autospec=True,
        ) as _m:
            self.assertEqual(tm.data(tm.index(0, 1), Qt.DisplayRole), "")
            _m.assert_called_once_with(tm, "")
        with patch(
            "physbiblio.gui.bibWindows.BibTableModel.addMarksCell",
            return_value=(False, ""),
            autospec=True,
        ) as _m:
            self.assertEqual(tm.data(tm.index(1, 1), Qt.DisplayRole), "")
            _m.assert_called_once_with(tm, "new,imp")
        self.assertEqual(tm.data(tm.index(0, 1), Qt.DisplayRole), "")
        self.assertEqual(tm.data(tm.index(0, 1), Qt.DecorationRole), None)
        self.assertEqual(tm.data(tm.index(1, 1), Qt.DisplayRole), None)
        self.assertIsInstance(tm.data(tm.index(1, 1), Qt.DecorationRole), QPixmap)

        # check type
        with patch(
            "physbiblio.gui.bibWindows.BibTableModel.addTypeCell",
            return_value="type A",
            autospec=True,
        ) as _m:
            self.assertEqual(tm.data(tm.index(0, 5), Qt.DisplayRole), "type A")
            _m.assert_called_once_with(tm, biblist[0])
        with patch(
            "physbiblio.gui.bibWindows.BibTableModel.addTypeCell",
            return_value="type B",
            autospec=True,
        ) as _m:
            self.assertEqual(tm.data(tm.index(1, 5), Qt.DisplayRole), "type B")
            _m.assert_called_once_with(tm, biblist[1])
        self.assertEqual(tm.data(tm.index(0, 5), Qt.DisplayRole), "")
        self.assertEqual(tm.data(tm.index(0, 5), Qt.DecorationRole), None)
        self.assertEqual(tm.data(tm.index(1, 5), Qt.DisplayRole), "Book")
        self.assertEqual(tm.data(tm.index(1, 5), Qt.DecorationRole), None)

        # check pdf
        with patch(
            "physbiblio.gui.bibWindows.BibTableModel.addPDFCell",
            return_value=(False, "no PDF"),
            autospec=True,
        ) as _m:
            self.assertEqual(tm.data(tm.index(0, 6), Qt.DisplayRole), "no PDF")
            _m.assert_called_once_with(tm, "a")
        with patch(
            "physbiblio.gui.bibWindows.BibTableModel.addPDFCell",
            return_value=(False, "no PDF"),
            autospec=True,
        ) as _m:
            self.assertEqual(tm.data(tm.index(1, 6), Qt.DisplayRole), "no PDF")
            _m.assert_called_once_with(tm, "b")
        with patch(
            "physbiblio.pdf.LocalPDF.getExisting",
            side_effect=[[], [], ["b"], ["b"]],
            autospec=True,
        ) as _ge:
            self.assertEqual(tm.data(tm.index(0, 6), Qt.DisplayRole), "no PDF")
            _ge.assert_called_once_with(pBPDF, "a")
            self.assertEqual(tm.data(tm.index(0, 6), Qt.DecorationRole), None)
            _ge.reset_mock()
            self.assertEqual(tm.data(tm.index(1, 6), Qt.DisplayRole), None)
            _ge.assert_called_once_with(pBPDF, "b")
            self.assertIsInstance(tm.data(tm.index(1, 6), Qt.DecorationRole), QPixmap)

        tm = BibTableModel(
            m, biblist, header + addCols, header, addCols, previous=[], askBibs=False
        )
        self.assertEqual(tm.data(tm.index(0, 0), Qt.CheckStateRole), None)
        tm = BibTableModel(
            m, biblist, header + addCols, header, addCols, previous=[], askBibs=True
        )
        self.assertEqual(tm.data(tm.index(0, 0), Qt.CheckStateRole), Qt.Unchecked)
        tm = BibTableModel(
            m, biblist, header + addCols, header, addCols, previous=["a"], askBibs=True
        )
        self.assertEqual(tm.data(tm.index(0, 0), Qt.CheckStateRole), Qt.Checked)
        self.assertEqual(tm.setData(tm.index(0, 0), "abc", Qt.CheckStateRole), True)
        self.assertEqual(tm.data(tm.index(0, 0), Qt.CheckStateRole), Qt.Unchecked)
        self.assertEqual(
            tm.setData(tm.index(0, 0), Qt.Checked, Qt.CheckStateRole), True
        )
        self.assertEqual(tm.data(tm.index(0, 0), Qt.CheckStateRole), Qt.Checked)

    def test_setData(self):
        """test setData"""
        p = QWidget()

        def connectEmit(ix1, ix2):
            """used to test dataChanged.emit"""
            self.newEmit = ix1

        biblist = [{"bibkey": "a"}, {"bibkey": "b"}]
        header = ["A", "B", "C"]
        tm = BibTableModel(p, biblist, header)
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

        tm = BibTableModel(p, biblist, header)
        ix = tm.index(1, 0)
        self.assertEqual(tm.setData(ix, "abc", Qt.EditRole), True)
        self.assertEqual(tm.selectedElements, {"a": False, "b": False})
        self.assertEqual(tm.setData(ix, "abc", Qt.CheckStateRole), True)
        self.assertEqual(tm.selectedElements, {"a": False, "b": False})


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestCommonBibActions(GUIwMainWTestCase):
    """test CommonBibActions"""

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
        """test _createMenuArxiv"""
        c = CommonBibActions([{"bibkey": "abc", "arxiv": "1809.00000"}], self.mainW)
        c.menu = PBMenu(self.mainW)
        c._createMenuArxiv(False, "")
        self.assertEqual(c.menu.possibleActions, [])
        c._createMenuArxiv(False, None)
        self.assertEqual(c.menu.possibleActions, [])
        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onAbs", autospec=True
        ) as _a, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onArx", autospec=True
        ) as _b:
            c._createMenuArxiv(False, "1809.00000")
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "arXiv")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            for a in c.menu.possibleActions[0][1]:
                self.assertIsInstance(a, QAction)
            self.assertEqual(c.menu.possibleActions[0][1][0].text(), "Load abstract")
            c.menu.possibleActions[0][1][0].trigger()
            _a.assert_called_once_with(c)
            self.assertEqual(c.menu.possibleActions[0][1][1].text(), "Get more fields")
            c.menu.possibleActions[0][1][1].trigger()
            _b.assert_called_once_with(c)

        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onAbs", autospec=True
        ) as _a, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onArx", autospec=True
        ) as _b:
            c._createMenuArxiv(True, "")
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "arXiv")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            for a in c.menu.possibleActions[0][1]:
                self.assertIsInstance(a, QAction)
            self.assertEqual(c.menu.possibleActions[0][1][0].text(), "Load abstract")
            c.menu.possibleActions[0][1][0].trigger()
            _a.assert_called_once_with(c)
            self.assertEqual(c.menu.possibleActions[0][1][1].text(), "Get more fields")
            c.menu.possibleActions[0][1][1].trigger()
            _a.assert_called_once_with(c)

    def test_createMenuCopy(self):
        """test _createMenuCopy"""
        p = QWidget()
        c = CommonBibActions([{"bibkey": "abc", "abstract": "", "link": ""}], p)
        c.menu = PBMenu(self.mainW)
        c._createMenuCopy(True, c.bibs[0])
        self.assertIsInstance(c.menu.possibleActions[0], list)
        self.assertEqual(c.menu.possibleActions[0][0], "Copy to clipboard")
        self.assertIsInstance(c.menu.possibleActions[0][1], list)
        self.assertEqual(len(c.menu.possibleActions[0][1]), 5)
        for a in c.menu.possibleActions[0][1][:3]:
            self.assertIsInstance(a, QAction)
        self.assertEqual(c.menu.possibleActions[0][1][0].text(), "key(s)")
        self.assertEqual(c.menu.possibleActions[0][1][1].text(), "\cite{key(s)}")
        self.assertEqual(c.menu.possibleActions[0][1][2].text(), "bibtex(s)")
        self.assertEqual(c.menu.possibleActions[0][1][3], None)
        self.assertEqual(c.menu.possibleActions[0][1][4].text(), bwstr.Acts.cpDir)

        c = CommonBibActions([{"bibkey": "abc", "abstract": "", "link": ""}], p)
        c.menu = PBMenu(self.mainW)
        c._createMenuCopy(False, c.bibs[0])
        self.assertIsInstance(c.menu.possibleActions[0], list)
        self.assertEqual(c.menu.possibleActions[0][0], "Copy to clipboard")
        self.assertIsInstance(c.menu.possibleActions[0][1], list)
        self.assertEqual(len(c.menu.possibleActions[0][1]), 7)
        for i, a in enumerate(c.menu.possibleActions[0][1]):
            if i in [3, 5]:
                self.assertEqual(a, None)
            else:
                self.assertIsInstance(a, QAction)
        self.assertEqual(c.menu.possibleActions[0][1][0].text(), "key(s)")
        self.assertEqual(c.menu.possibleActions[0][1][1].text(), "\cite{key(s)}")
        self.assertEqual(c.menu.possibleActions[0][1][2].text(), "bibtex(s)")
        self.assertEqual(c.menu.possibleActions[0][1][4].text(), "bibitem")
        self.assertEqual(c.menu.possibleActions[0][1][6].text(), bwstr.Acts.cpDir)

        c = CommonBibActions([{"bibkey": "abc", "abstract": "abc", "link": "def"}], p)
        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCopyKeys", autospec=True
        ) as _a, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCopyCites", autospec=True
        ) as _b, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCopyBibtexs", autospec=True
        ) as _c, patch(
            "physbiblio.gui.bibWindows.copyToClipboard", autospec=True
        ) as _d, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCopyDir", autospec=True
        ) as _e:
            c._createMenuCopy(False, c.bibs[0])
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "Copy to clipboard")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            self.assertEqual(len(c.menu.possibleActions[0][1]), 9)
            for i, a in enumerate(c.menu.possibleActions[0][1]):
                if i in [3, 7]:
                    self.assertEqual(a, None)
                else:
                    self.assertIsInstance(a, QAction)
            self.assertEqual(c.menu.possibleActions[0][1][0].text(), "key(s)")
            self.assertEqual(c.menu.possibleActions[0][1][1].text(), "\cite{key(s)}")
            self.assertEqual(c.menu.possibleActions[0][1][2].text(), "bibtex(s)")
            self.assertEqual(c.menu.possibleActions[0][1][4].text(), "abstract")
            self.assertEqual(c.menu.possibleActions[0][1][5].text(), "link")
            self.assertEqual(c.menu.possibleActions[0][1][6].text(), "bibitem")
            self.assertEqual(c.menu.possibleActions[0][1][8].text(), bwstr.Acts.cpDir)
            _a.assert_not_called()
            c.menu.possibleActions[0][1][0].trigger()
            _a.assert_called_once_with(c)
            _b.assert_not_called()
            c.menu.possibleActions[0][1][1].trigger()
            _b.assert_called_once_with(c)
            _c.assert_not_called()
            c.menu.possibleActions[0][1][2].trigger()
            _c.assert_called_once_with(c)
            _d.assert_not_called()
            c.menu.possibleActions[0][1][4].trigger()
            _d.assert_called_once_with("abc")
            _d.reset_mock()
            c.menu.possibleActions[0][1][5].trigger()
            _d.assert_called_once_with("def")
            _d.reset_mock()
            c.menu.possibleActions[0][1][6].trigger()
            _d.assert_called_once_with("\\bibitem{abc}.")
            _e.reset_mock()
            c.menu.possibleActions[0][1][8].trigger()
            _e.assert_called_once_with(c)

        c = CommonBibActions(
            [
                {
                    "bibkey": "abc",
                    "abstract": "abc",
                    "link": "def",
                    "arxiv": "1234.5678",
                    "doi": "1/2/3",
                    "inspire": "123456",
                    "bibtexDict": {
                        "author": "me",
                        "title": "some paper",
                        "journal": "jou",
                        "year": "2018",
                        "pages": "12",
                        "volume": "0",
                    },
                }
            ],
            p,
        )
        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCopyKeys", autospec=True
        ) as _a, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCopyCites", autospec=True
        ) as _b, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCopyBibtexs", autospec=True
        ) as _c, patch(
            "physbiblio.gui.bibWindows.copyToClipboard", autospec=True
        ) as _d, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCopyDir", autospec=True
        ) as _e:
            c._createMenuCopy(False, c.bibs[0])
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "Copy to clipboard")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            self.assertEqual(len(c.menu.possibleActions[0][1]), 15)
            for i, a in enumerate(c.menu.possibleActions[0][1]):
                if i in [3, 13]:
                    self.assertEqual(a, None)
                else:
                    self.assertIsInstance(a, QAction)
            self.assertEqual(c.menu.possibleActions[0][1][0].text(), "key(s)")
            self.assertEqual(c.menu.possibleActions[0][1][1].text(), "\cite{key(s)}")
            self.assertEqual(c.menu.possibleActions[0][1][2].text(), "bibtex(s)")
            self.assertEqual(c.menu.possibleActions[0][1][4].text(), "abstract")
            self.assertEqual(c.menu.possibleActions[0][1][5].text(), "arXiv")
            self.assertEqual(c.menu.possibleActions[0][1][6].text(), "DOI")
            self.assertEqual(c.menu.possibleActions[0][1][7].text(), "INSPIRE")
            self.assertEqual(c.menu.possibleActions[0][1][8].text(), "link")
            self.assertEqual(c.menu.possibleActions[0][1][9].text(), "journal")
            self.assertEqual(c.menu.possibleActions[0][1][10].text(), "published")
            self.assertEqual(c.menu.possibleActions[0][1][11].text(), "title")
            self.assertEqual(c.menu.possibleActions[0][1][12].text(), "bibitem")
            self.assertEqual(c.menu.possibleActions[0][1][14].text(), bwstr.Acts.cpDir)
            _a.assert_not_called()
            c.menu.possibleActions[0][1][0].trigger()
            _a.assert_called_once_with(c)
            _b.assert_not_called()
            c.menu.possibleActions[0][1][1].trigger()
            _b.assert_called_once_with(c)
            _c.assert_not_called()
            c.menu.possibleActions[0][1][2].trigger()
            _c.assert_called_once_with(c)
            _d.assert_not_called()
            c.menu.possibleActions[0][1][4].trigger()
            _d.assert_called_once_with("abc")
            _d.reset_mock()
            c.menu.possibleActions[0][1][5].trigger()
            _d.assert_called_once_with("1234.5678")
            _d.reset_mock()
            c.menu.possibleActions[0][1][6].trigger()
            _d.assert_called_once_with("1/2/3")
            _d.reset_mock()
            c.menu.possibleActions[0][1][7].trigger()
            _d.assert_called_once_with("123456")
            _d.reset_mock()
            c.menu.possibleActions[0][1][8].trigger()
            _d.assert_called_once_with("def")
            _d.reset_mock()
            c.menu.possibleActions[0][1][9].trigger()
            _d.assert_called_once_with("jou")
            _d.reset_mock()
            c.menu.possibleActions[0][1][10].trigger()
            _d.assert_called_once_with("jou 0 (2018) 12")
            _d.reset_mock()
            c.menu.possibleActions[0][1][11].trigger()
            _d.assert_called_once_with("some paper")
            _d.reset_mock()
            c.menu.possibleActions[0][1][12].trigger()
            _d.assert_called_once_with(
                "\\bibitem{abc}\nme\n% some paper\njou 0 (2018) 12\ndoi: 1/2/3\n[arxiv:1234.5678]."
            )
            _e.reset_mock()
            c.menu.possibleActions[0][1][14].trigger()
            _e.assert_called_once_with(c)

    def test_createMenuInspire(self):
        """test _createMenuInspire"""
        p = QWidget()
        c = CommonBibActions([{"bibkey": "abc"}], p)
        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onComplete", autospec=True
        ) as _a, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onUpdate", autospec=True
        ) as _b, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCitations", autospec=True
        ) as _c, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCitationCount", autospec=True
        ) as _d:
            c._createMenuInspire(True, "")
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "INSPIRE-HEP")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            self.assertEqual(len(c.menu.possibleActions[0][1]), 5)
            for a in c.menu.possibleActions[0][1]:
                self.assertIsInstance(a, QAction)
            self.assertEqual(
                c.menu.possibleActions[0][1][0].text(),
                "Complete info (ID and auxiliary info)",
            )
            self.assertEqual(c.menu.possibleActions[0][1][1].text(), "Update bibtex")
            self.assertEqual(c.menu.possibleActions[0][1][2].text(), "Reload bibtex")
            self.assertEqual(
                c.menu.possibleActions[0][1][3].text(), "Citation statistics"
            )
            self.assertEqual(
                c.menu.possibleActions[0][1][4].text(), "Update citation count"
            )
            _a.assert_not_called()
            c.menu.possibleActions[0][1][0].trigger()
            _a.assert_called_once_with(c)
            _b.assert_not_called()
            c.menu.possibleActions[0][1][1].trigger()
            _b.assert_called_once_with(c, force=True)
            _b.reset_mock()
            c.menu.possibleActions[0][1][2].trigger()
            _b.assert_called_once_with(c, force=False, reloadAll=True)
            _c.assert_not_called()
            c.menu.possibleActions[0][1][3].trigger()
            _c.assert_called_once_with(c)
            _d.assert_not_called()
            c.menu.possibleActions[0][1][4].trigger()
            _d.assert_called_once_with(c)

        c.menu = PBMenu(self.mainW)
        c._createMenuInspire(False, "")
        self.assertIsInstance(c.menu.possibleActions[0], dict)
        self.assertEqual(c.menu.possibleActions[0]["title"], "INSPIRE-HEP")
        self.assertIsInstance(c.menu.possibleActions[0]["actions"], list)
        self.assertEqual(len(c.menu.possibleActions[0]["actions"]), 1)
        for a in c.menu.possibleActions[0]["actions"]:
            self.assertIsInstance(a, QAction)
        self.assertEqual(
            c.menu.possibleActions[0]["actions"][0].text(),
            "Complete info (ID and auxiliary info)",
        )
        self.assertEqual(c.menu.possibleActions[0]["toolTipsVisible"], True)

        c.menu = PBMenu(self.mainW)
        c._createMenuInspire(False, None)
        self.assertIsInstance(c.menu.possibleActions[0], dict)
        self.assertEqual(c.menu.possibleActions[0]["title"], "INSPIRE-HEP")
        self.assertIsInstance(c.menu.possibleActions[0]["actions"], list)
        self.assertEqual(len(c.menu.possibleActions[0]["actions"]), 1)
        for a in c.menu.possibleActions[0]["actions"]:
            self.assertIsInstance(a, QAction)
        self.assertEqual(
            c.menu.possibleActions[0]["actions"][0].text(),
            "Complete info (ID and auxiliary info)",
        )
        self.assertEqual(c.menu.possibleActions[0]["toolTipsVisible"], True)

        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onComplete", autospec=True
        ) as _a, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onUpdate", autospec=True
        ) as _b, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCitations", autospec=True
        ) as _c, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCitationCount", autospec=True
        ) as _d:
            c._createMenuInspire(False, "123")
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "INSPIRE-HEP")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            self.assertEqual(len(c.menu.possibleActions[0][1]), 5)
            for a in c.menu.possibleActions[0][1]:
                self.assertIsInstance(a, QAction)
            self.assertEqual(
                c.menu.possibleActions[0][1][0].text(),
                "Complete info (ID and auxiliary info)",
            )
            self.assertEqual(c.menu.possibleActions[0][1][1].text(), "Update bibtex")
            self.assertEqual(c.menu.possibleActions[0][1][2].text(), "Reload bibtex")
            self.assertEqual(
                c.menu.possibleActions[0][1][3].text(), "Citation statistics"
            )
            self.assertEqual(
                c.menu.possibleActions[0][1][4].text(), "Update citation count"
            )
            _a.assert_not_called()
            c.menu.possibleActions[0][1][0].trigger()
            _a.assert_called_once_with(c)
            _b.assert_not_called()
            c.menu.possibleActions[0][1][1].trigger()
            _b.assert_called_once_with(c, force=True)
            _b.reset_mock()
            c.menu.possibleActions[0][1][2].trigger()
            _b.assert_called_once_with(c, force=True, reloadAll=True)
            _c.assert_not_called()
            c.menu.possibleActions[0][1][3].trigger()
            _c.assert_called_once_with(c)
            _d.assert_not_called()
            c.menu.possibleActions[0][1][4].trigger()
            _d.assert_called_once_with(c)

    def test_createMenuLinks(self):
        """test _createMenuLinks"""
        p = QWidget()
        c = CommonBibActions([{"bibkey": "abc"}], p)
        c.menu = PBMenu(self.mainW)
        c._createMenuLinks("abc", "", "", "")
        self.assertEqual(c.menu.possibleActions, [])
        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _l:
            c._createMenuLinks("abc", "123", "", "")
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "Links")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            self.assertEqual(len(c.menu.possibleActions[0][1]), 1)
            for a in c.menu.possibleActions[0][1]:
                self.assertIsInstance(a, QAction)
            self.assertEqual(c.menu.possibleActions[0][1][0].text(), "Open into arXiv")
            _l.assert_not_called()
            c.menu.possibleActions[0][1][0].trigger()
            _l.assert_called_once_with(pBGuiView, "abc", "arxiv")
        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _l:
            c._createMenuLinks("abc", "", "123", "")
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "Links")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            self.assertEqual(len(c.menu.possibleActions[0][1]), 1)
            for a in c.menu.possibleActions[0][1]:
                self.assertIsInstance(a, QAction)
            self.assertEqual(c.menu.possibleActions[0][1][0].text(), "Open DOI link")
            _l.assert_not_called()
            c.menu.possibleActions[0][1][0].trigger()
            _l.assert_called_once_with(pBGuiView, "abc", "doi")
        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _l:
            c._createMenuLinks("abc", "", "", "123")
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "Links")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            self.assertEqual(len(c.menu.possibleActions[0][1]), 1)
            for a in c.menu.possibleActions[0][1]:
                self.assertIsInstance(a, QAction)
            self.assertEqual(
                c.menu.possibleActions[0][1][0].text(), "Open into INSPIRE-HEP"
            )
            _l.assert_not_called()
            c.menu.possibleActions[0][1][0].trigger()
            _l.assert_called_once_with(pBGuiView, "abc", "inspire")
        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _l:
            c._createMenuLinks("abc", "123.456", "1/2/3", "123")
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "Links")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            self.assertEqual(len(c.menu.possibleActions[0][1]), 3)
            for a in c.menu.possibleActions[0][1]:
                self.assertIsInstance(a, QAction)
            self.assertEqual(c.menu.possibleActions[0][1][0].text(), "Open into arXiv")
            self.assertEqual(c.menu.possibleActions[0][1][1].text(), "Open DOI link")
            self.assertEqual(
                c.menu.possibleActions[0][1][2].text(), "Open into INSPIRE-HEP"
            )
            _l.assert_not_called()
            c.menu.possibleActions[0][1][0].trigger()
            _l.assert_called_once_with(pBGuiView, "abc", "arxiv")
            _l.reset_mock()
            c.menu.possibleActions[0][1][1].trigger()
            _l.assert_called_once_with(pBGuiView, "abc", "doi")
            _l.reset_mock()
            c.menu.possibleActions[0][1][2].trigger()
            _l.assert_called_once_with(pBGuiView, "abc", "inspire")

    def test_createMenuMarkType(self):
        """test _createMenuMarkType"""
        p = QWidget()
        c = CommonBibActions(
            [
                {
                    "bibkey": "abc",
                    "marks": "imp,new",
                    "review": 0,
                    "proceeding": 0,
                    "book": 1,
                    "phd_thesis": 1,
                    "lecture": 0,
                    "exp_paper": 0,
                }
            ],
            p,
        )
        c.menu = PBMenu(self.mainW)
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
            with patch(
                "physbiblio.gui.bibWindows.CommonBibActions.onUpdateMark", autospec=True
            ) as _a:
                c.menu.possibleActions[0][1][i].trigger()
                _a.assert_called_once_with(c, m)
        self.assertEqual(c.menu.possibleActions[0][1][0].text(), "Mark as 'Bad'")
        self.assertEqual(c.menu.possibleActions[0][1][1].text(), "Mark as 'Favorite'")
        self.assertEqual(
            c.menu.possibleActions[0][1][2].text(), "Unmark as 'Important'"
        )
        self.assertEqual(
            c.menu.possibleActions[0][1][3].text(), "Unmark as 'To be read'"
        )
        self.assertEqual(c.menu.possibleActions[0][1][4].text(), "Mark as 'Unclear'")
        for i, (k, v) in enumerate(sorted(convertType.items())):
            with patch(
                "physbiblio.gui.bibWindows.CommonBibActions.onUpdateType", autospec=True
            ) as _a:
                c.menu.possibleActions[1][1][i].trigger()
                _a.assert_called_once_with(c, k)
        self.assertEqual(c.menu.possibleActions[1][1][0].text(), "Unset 'Book'")
        self.assertEqual(
            c.menu.possibleActions[1][1][1].text(), "Set 'Experimental paper'"
        )
        self.assertEqual(c.menu.possibleActions[1][1][2].text(), "Set 'Lecture'")
        self.assertEqual(c.menu.possibleActions[1][1][3].text(), "Unset 'PhD thesis'")
        self.assertEqual(c.menu.possibleActions[1][1][4].text(), "Set 'Proceeding'")
        self.assertEqual(c.menu.possibleActions[1][1][5].text(), "Set 'Review'")

    def test_createMenuMarkTypeList(self):
        """test _createMenuMarkTypeList"""
        p = QWidget()
        c = CommonBibActions(
            [
                {
                    "bibkey": "abc",
                    "marks": "imp,new",
                    "review": 0,
                    "proceeding": 0,
                    "book": 1,
                    "phd_thesis": 1,
                    "lecture": 0,
                    "exp_paper": 0,
                },
                {
                    "bibkey": "abc",
                    "marks": "imp,bad",
                    "review": 1,
                    "proceeding": 0,
                    "book": 0,
                    "phd_thesis": 0,
                    "lecture": 1,
                    "exp_paper": 0,
                },
            ],
            p,
        )
        c.menu = PBMenu(self.mainW)
        c._createMenuMarkTypeList()
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
            with patch(
                "physbiblio.gui.bibWindows.CommonBibActions.onUpdateMark", autospec=True
            ) as _a:
                c.menu.possibleActions[0][1][i * 2].trigger()
                _a.assert_called_once_with(c, m, force=1)
                _a.reset_mock()
                c.menu.possibleActions[0][1][i * 2 + 1].trigger()
                _a.assert_called_once_with(c, m, force=0)
            self.assertEqual(
                c.menu.possibleActions[0][1][i * 2].text(),
                "Mark all as '%s'" % pBMarks.marks[m]["desc"],
            )
            self.assertEqual(
                c.menu.possibleActions[0][1][i * 2 + 1].text(),
                "Unmark all as '%s'" % pBMarks.marks[m]["desc"],
            )
        for i, (k, v) in enumerate(sorted(convertType.items())):
            with patch(
                "physbiblio.gui.bibWindows.CommonBibActions.onUpdateType", autospec=True
            ) as _a:
                c.menu.possibleActions[1][1][i * 2].trigger()
                _a.assert_called_once_with(c, k, force=1)
                _a.reset_mock()
                c.menu.possibleActions[1][1][i * 2 + 1].trigger()
                _a.assert_called_once_with(c, k, force=0)
            self.assertEqual(
                c.menu.possibleActions[1][1][i * 2 + 0].text(), "Set '%s' for all" % v
            )
            self.assertEqual(
                c.menu.possibleActions[1][1][i * 2 + 1].text(), "Unset '%s' for all" % v
            )

    def test_createMenuPDF(self):
        """test _createMenuPDF"""
        # selection True
        p = QWidget()
        c = CommonBibActions([{"bibkey": "abc"}], p)
        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onDown", autospec=True
        ) as _a:
            c._createMenuPDF(True, c.bibs[0])
            self.assertEqual(len(c.menu.possibleActions), 1)
            self.assertIsInstance(c.menu.possibleActions[0], QAction)
            self.assertEqual(c.menu.possibleActions[0].text(), "Download arXiv PDF")
            _a.assert_not_called()
            c.menu.possibleActions[0].trigger()
            _a.assert_called_once_with(c)

        # no arxiv, no doi
        c = CommonBibActions([{"bibkey": "abc", "arxiv": "", "doi": ""}], p)
        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.pdf.LocalPDF.getExisting", return_value=[], autospec=True
        ) as _ge, patch(
            "physbiblio.pdf.LocalPDF.getFilePath", return_value="", autospec=True
        ) as _gf, patch(
            "physbiblio.pdf.LocalPDF.getFileDir", return_value="", autospec=True
        ) as _gd, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onAddPDF", autospec=True
        ) as _a:
            c._createMenuPDF(False, c.bibs[0])
            _ge.assert_called_once_with(pBPDF, "abc", fullPath=True)
            _gf.assert_has_calls(
                [call(pBPDF, "abc", "arxiv"), call(pBPDF, "abc", "doi")]
            )
            _gd.assert_called_once_with(pBPDF, "abc")
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "Files")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            self.assertEqual(len(c.menu.possibleActions[0][1]), 1)
            self.assertIsInstance(c.menu.possibleActions[0][1][0], QAction)
            self.assertEqual(c.menu.possibleActions[0][1][0].text(), "Add generic file")
            _a.assert_not_called()
            c.menu.possibleActions[0][1][0].trigger()
            _a.assert_called_once_with(c)

        # only arxiv, w/o file
        c = CommonBibActions([{"bibkey": "abc", "arxiv": "1809.00000", "doi": ""}], p)
        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.pdf.LocalPDF.getExisting", return_value=[], autospec=True
        ) as _ge, patch(
            "physbiblio.pdf.LocalPDF.getFilePath", return_value="", autospec=True
        ) as _gf, patch(
            "physbiblio.pdf.LocalPDF.getFileDir", return_value="", autospec=True
        ) as _gd, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onDown", autospec=True
        ) as _b:
            c._createMenuPDF(False, c.bibs[0])
            _ge.assert_called_once_with(pBPDF, "abc", fullPath=True)
            _gf.assert_has_calls(
                [call(pBPDF, "abc", "arxiv"), call(pBPDF, "abc", "doi")]
            )
            _gd.assert_called_once_with(pBPDF, "abc")
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "Files")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            self.assertEqual(len(c.menu.possibleActions[0][1]), 2)
            self.assertIsInstance(c.menu.possibleActions[0][1][0], QAction)
            self.assertEqual(c.menu.possibleActions[0][1][0].text(), "Add generic file")
            self.assertEqual(
                c.menu.possibleActions[0][1][1].text(), "Download arXiv PDF"
            )
            _b.assert_not_called()
            c.menu.possibleActions[0][1][1].trigger()
            _b.assert_called_once_with(c)

        # only arxiv, w file
        c = CommonBibActions([{"bibkey": "abc", "arxiv": "", "doi": ""}], p)
        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.pdf.LocalPDF.getExisting",
            return_value=["arxiv.pdf"],
            autospec=True,
        ) as _ge, patch(
            "physbiblio.pdf.LocalPDF.getFilePath",
            side_effect=["arxiv.pdf", ""],
            autospec=True,
        ) as _gf, patch(
            "physbiblio.pdf.LocalPDF.getFileDir", return_value="/fd", autospec=True
        ) as _gd, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onDeletePDFFile", autospec=True
        ) as _a, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCopyPDFFile", autospec=True
        ) as _b, patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _l:
            c._createMenuPDF(False, c.bibs[0])
            _ge.assert_called_once_with(pBPDF, "abc", fullPath=True)
            _gf.assert_has_calls(
                [call(pBPDF, "abc", "arxiv"), call(pBPDF, "abc", "doi")]
            )
            _gd.assert_called_once_with(pBPDF, "abc")
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "Files")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            self.assertEqual(len(c.menu.possibleActions[0][1]), 5)
            self.assertIsInstance(c.menu.possibleActions[0][1][0], QAction)
            self.assertEqual(c.menu.possibleActions[0][1][0].text(), "Open arXiv PDF")
            self.assertEqual(c.menu.possibleActions[0][1][1], None)
            self.assertEqual(c.menu.possibleActions[0][1][2].text(), "Add generic file")
            self.assertEqual(c.menu.possibleActions[0][1][3], None)
            self.assertIsInstance(c.menu.possibleActions[0][1][4], list)
            self.assertEqual(len(c.menu.possibleActions[0][1][4]), 2)
            self.assertEqual(c.menu.possibleActions[0][1][4][0], "Manage arXiv PDF")
            self.assertIsInstance(c.menu.possibleActions[0][1][4][1], list)
            self.assertEqual(
                c.menu.possibleActions[0][1][4][1][0].text(), "Delete arXiv PDF"
            )
            self.assertEqual(
                c.menu.possibleActions[0][1][4][1][1].text(), "Copy arXiv PDF"
            )
            _l.assert_not_called()
            c.menu.possibleActions[0][1][0].trigger()
            _l.assert_called_once_with(pBGuiView, "abc", "file", fileArg="arxiv.pdf")
            _a.assert_not_called()
            c.menu.possibleActions[0][1][4][1][0].trigger()
            _a.assert_called_once_with(c, "abc", "arxiv", "arxiv PDF")
            _b.assert_not_called()
            c.menu.possibleActions[0][1][4][1][1].trigger()
            _b.assert_called_once_with(c, "abc", "arxiv")

        # only doi, w/o file
        c = CommonBibActions([{"bibkey": "abc", "arxiv": "", "doi": "1/2/3"}], p)
        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.pdf.LocalPDF.getExisting", return_value=[], autospec=True
        ) as _ge, patch(
            "physbiblio.pdf.LocalPDF.getFilePath", return_value="", autospec=True
        ) as _gf, patch(
            "physbiblio.pdf.LocalPDF.getFileDir", return_value="", autospec=True
        ) as _gd, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onAddPDF", autospec=True
        ) as _a, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onDown", autospec=True
        ) as _b:
            c._createMenuPDF(False, c.bibs[0])
            _ge.assert_called_once_with(pBPDF, "abc", fullPath=True)
            _gf.assert_has_calls(
                [call(pBPDF, "abc", "arxiv"), call(pBPDF, "abc", "doi")]
            )
            _gd.assert_called_once_with(pBPDF, "abc")
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "Files")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            self.assertEqual(len(c.menu.possibleActions[0][1]), 2)
            self.assertIsInstance(c.menu.possibleActions[0][1][0], QAction)
            self.assertEqual(c.menu.possibleActions[0][1][0].text(), "Add generic file")
            self.assertEqual(c.menu.possibleActions[0][1][1].text(), "Assign DOI PDF")
            _a.assert_not_called()
            c.menu.possibleActions[0][1][1].trigger()
            _a.assert_called_once_with(c, "doi")

        # only doi, w file
        c = CommonBibActions([{"bibkey": "abc", "arxiv": "", "doi": ""}], p)
        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.pdf.LocalPDF.getExisting",
            return_value=["doi.pdf"],
            autospec=True,
        ) as _ge, patch(
            "physbiblio.pdf.LocalPDF.getFilePath",
            side_effect=["", "doi.pdf"],
            autospec=True,
        ) as _gf, patch(
            "physbiblio.pdf.LocalPDF.getFileDir", return_value="/fd", autospec=True
        ) as _gd, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onDeletePDFFile", autospec=True
        ) as _a, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCopyPDFFile", autospec=True
        ) as _b, patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _l:
            c._createMenuPDF(False, c.bibs[0])
            _ge.assert_called_once_with(pBPDF, "abc", fullPath=True)
            _gf.assert_has_calls(
                [call(pBPDF, "abc", "arxiv"), call(pBPDF, "abc", "doi")]
            )
            _gd.assert_called_once_with(pBPDF, "abc")
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "Files")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            self.assertEqual(len(c.menu.possibleActions[0][1]), 5)
            self.assertIsInstance(c.menu.possibleActions[0][1][0], QAction)
            self.assertEqual(c.menu.possibleActions[0][1][0].text(), "Open DOI PDF")
            self.assertEqual(c.menu.possibleActions[0][1][1], None)
            self.assertEqual(c.menu.possibleActions[0][1][2].text(), "Add generic file")
            self.assertEqual(c.menu.possibleActions[0][1][3], None)
            self.assertIsInstance(c.menu.possibleActions[0][1][4], list)
            self.assertEqual(len(c.menu.possibleActions[0][1][4]), 2)
            self.assertEqual(c.menu.possibleActions[0][1][4][0], "Manage DOI PDF")
            self.assertIsInstance(c.menu.possibleActions[0][1][4][1], list)
            self.assertEqual(
                c.menu.possibleActions[0][1][4][1][0].text(), "Delete DOI PDF"
            )
            self.assertEqual(
                c.menu.possibleActions[0][1][4][1][1].text(), "Copy DOI PDF"
            )
            _l.assert_not_called()
            c.menu.possibleActions[0][1][0].trigger()
            _l.assert_called_once_with(pBGuiView, "abc", "file", fileArg="doi.pdf")
            _a.assert_not_called()
            c.menu.possibleActions[0][1][4][1][0].trigger()
            _a.assert_called_once_with(c, "abc", "doi", "DOI PDF")
            _b.assert_not_called()
            c.menu.possibleActions[0][1][4][1][1].trigger()
            _b.assert_called_once_with(c, "abc", "doi")

        # both, w files, no extra
        c = CommonBibActions([{"bibkey": "abc", "arxiv": "", "doi": ""}], p)
        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.pdf.LocalPDF.getExisting",
            return_value=["arxiv.pdf", "doi.pdf"],
            autospec=True,
        ) as _ge, patch(
            "physbiblio.pdf.LocalPDF.getFilePath",
            side_effect=["arxiv.pdf", "doi.pdf"],
            autospec=True,
        ) as _gf, patch(
            "physbiblio.pdf.LocalPDF.getFileDir", return_value="/fd", autospec=True
        ) as _gd, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onDeletePDFFile", autospec=True
        ) as _a, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCopyPDFFile", autospec=True
        ) as _b, patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _l:
            c._createMenuPDF(False, c.bibs[0])
            _ge.assert_called_once_with(pBPDF, "abc", fullPath=True)
            _gf.assert_has_calls(
                [call(pBPDF, "abc", "arxiv"), call(pBPDF, "abc", "doi")]
            )
            _gd.assert_called_once_with(pBPDF, "abc")
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "Files")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            self.assertEqual(len(c.menu.possibleActions[0][1]), 7)
            self.assertIsInstance(c.menu.possibleActions[0][1][0], QAction)
            self.assertEqual(c.menu.possibleActions[0][1][0].text(), "Open arXiv PDF")
            self.assertEqual(c.menu.possibleActions[0][1][1].text(), "Open DOI PDF")
            self.assertEqual(c.menu.possibleActions[0][1][2], None)
            self.assertEqual(c.menu.possibleActions[0][1][3].text(), "Add generic file")
            self.assertEqual(c.menu.possibleActions[0][1][4], None)
            self.assertIsInstance(c.menu.possibleActions[0][1][5], list)
            self.assertEqual(len(c.menu.possibleActions[0][1][5]), 2)
            self.assertEqual(c.menu.possibleActions[0][1][5][0], "Manage arXiv PDF")
            self.assertIsInstance(c.menu.possibleActions[0][1][5][1], list)
            self.assertEqual(
                c.menu.possibleActions[0][1][5][1][0].text(), "Delete arXiv PDF"
            )
            self.assertEqual(
                c.menu.possibleActions[0][1][5][1][1].text(), "Copy arXiv PDF"
            )
            self.assertIsInstance(c.menu.possibleActions[0][1][6], list)
            self.assertEqual(len(c.menu.possibleActions[0][1][6]), 2)
            self.assertEqual(c.menu.possibleActions[0][1][6][0], "Manage DOI PDF")
            self.assertIsInstance(c.menu.possibleActions[0][1][6][1], list)
            self.assertEqual(
                c.menu.possibleActions[0][1][6][1][0].text(), "Delete DOI PDF"
            )
            self.assertEqual(
                c.menu.possibleActions[0][1][6][1][1].text(), "Copy DOI PDF"
            )

        # no arxiv, no doi, some extra
        c = CommonBibActions([{"bibkey": "abc", "arxiv": "", "doi": ""}], p)
        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.pdf.LocalPDF.getExisting",
            return_value=["a.pdf", "/fd/b.pdf"],
            autospec=True,
        ) as _ge, patch(
            "physbiblio.pdf.LocalPDF.getFilePath", side_effect=["", ""], autospec=True
        ) as _gf, patch(
            "physbiblio.pdf.LocalPDF.getFileDir", return_value="/fd", autospec=True
        ) as _gd, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onDeletePDFFile", autospec=True
        ) as _a, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCopyPDFFile", autospec=True
        ) as _b, patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _l:
            c._createMenuPDF(False, c.bibs[0])
            _ge.assert_called_once_with(pBPDF, "abc", fullPath=True)
            _gf.assert_has_calls(
                [call(pBPDF, "abc", "arxiv"), call(pBPDF, "abc", "doi")]
            )
            _gd.assert_called_once_with(pBPDF, "abc")
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "Files")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            self.assertEqual(len(c.menu.possibleActions[0][1]), 7)
            self.assertIsInstance(c.menu.possibleActions[0][1][0], QAction)
            self.assertEqual(c.menu.possibleActions[0][1][0].text(), "Open a.pdf")
            self.assertEqual(c.menu.possibleActions[0][1][1].text(), "Open b.pdf")
            self.assertEqual(c.menu.possibleActions[0][1][2], None)
            self.assertEqual(c.menu.possibleActions[0][1][3].text(), "Add generic file")
            self.assertEqual(c.menu.possibleActions[0][1][4], None)
            self.assertIsInstance(c.menu.possibleActions[0][1][5], list)
            self.assertEqual(len(c.menu.possibleActions[0][1][5]), 2)
            self.assertEqual(c.menu.possibleActions[0][1][5][0], "Manage a.pdf")
            self.assertIsInstance(c.menu.possibleActions[0][1][5][1], list)
            self.assertEqual(
                c.menu.possibleActions[0][1][5][1][0].text(), "Delete a.pdf"
            )
            self.assertEqual(c.menu.possibleActions[0][1][5][1][1].text(), "Copy a.pdf")
            self.assertIsInstance(c.menu.possibleActions[0][1][6], list)
            self.assertEqual(len(c.menu.possibleActions[0][1][6]), 2)
            self.assertEqual(c.menu.possibleActions[0][1][6][0], "Manage b.pdf")
            self.assertIsInstance(c.menu.possibleActions[0][1][6][1], list)
            self.assertEqual(
                c.menu.possibleActions[0][1][6][1][0].text(), "Delete b.pdf"
            )
            self.assertEqual(c.menu.possibleActions[0][1][6][1][1].text(), "Copy b.pdf")
            _l.assert_not_called()
            c.menu.possibleActions[0][1][0].trigger()
            _l.assert_called_once_with(pBGuiView, "abc", "file", fileArg="a.pdf")
            _a.assert_not_called()
            c.menu.possibleActions[0][1][5][1][0].trigger()
            _a.assert_called_once_with(c, "abc", "a.pdf", "a.pdf", "a.pdf")
            _b.assert_not_called()
            c.menu.possibleActions[0][1][5][1][1].trigger()
            _b.assert_called_once_with(c, "abc", "a.pdf", "a.pdf")
            _l.reset_mock()
            c.menu.possibleActions[0][1][1].trigger()
            _l.assert_called_once_with(pBGuiView, "abc", "file", fileArg="/fd/b.pdf")
            _a.reset_mock()
            c.menu.possibleActions[0][1][6][1][0].trigger()
            _a.assert_called_once_with(c, "abc", "b.pdf", "b.pdf", "/fd/b.pdf")
            _b.reset_mock()
            c.menu.possibleActions[0][1][6][1][1].trigger()
            _b.assert_called_once_with(c, "abc", "b.pdf", "/fd/b.pdf")

        # arxiv, doi, extra
        c = CommonBibActions(
            [{"bibkey": "abc", "arxiv": "1809.00000", "doi": "1/2/3"}], p
        )
        c.menu = PBMenu(self.mainW)
        with patch(
            "physbiblio.pdf.LocalPDF.getExisting",
            return_value=["arxiv.pdf", "doi.pdf", "a.pdf", "/fd/b.pdf", "/fd/c.txt"],
            autospec=True,
        ) as _ge, patch(
            "physbiblio.pdf.LocalPDF.getFilePath",
            side_effect=["arxiv.pdf", "doi.pdf"],
            autospec=True,
        ) as _gf, patch(
            "physbiblio.pdf.LocalPDF.getFileDir", return_value="/fd", autospec=True
        ) as _gd, patch(
            "os.path.exists", return_value=True
        ) as _ope, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onDeletePDFFile", autospec=True
        ) as _a, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCopyPDFFile", autospec=True
        ) as _b, patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _l:
            c._createMenuPDF(False, c.bibs[0])
            _ge.assert_called_once_with(pBPDF, "abc", fullPath=True)
            _gf.assert_has_calls(
                [call(pBPDF, "abc", "arxiv"), call(pBPDF, "abc", "doi")]
            )
            _gd.assert_called_once_with(pBPDF, "abc")
            _ope.assert_called_once_with("/fd")
            self.assertIsInstance(c.menu.possibleActions[0], list)
            self.assertEqual(c.menu.possibleActions[0][0], "Files")
            self.assertIsInstance(c.menu.possibleActions[0][1], list)
            self.assertEqual(len(c.menu.possibleActions[0][1]), 15)
            self.assertIsInstance(c.menu.possibleActions[0][1][0], QAction)
            self.assertEqual(c.menu.possibleActions[0][1][0].text(), "Open arXiv PDF")
            self.assertEqual(c.menu.possibleActions[0][1][1].text(), "Open DOI PDF")
            self.assertEqual(c.menu.possibleActions[0][1][2].text(), "Open a.pdf")
            self.assertEqual(c.menu.possibleActions[0][1][3].text(), "Open b.pdf")
            self.assertEqual(c.menu.possibleActions[0][1][4].text(), "Open c.txt")
            self.assertEqual(c.menu.possibleActions[0][1][5], None)
            self.assertEqual(c.menu.possibleActions[0][1][6].text(), "Add generic file")
            self.assertEqual(c.menu.possibleActions[0][1][7], None)
            self.assertIsInstance(c.menu.possibleActions[0][1][8], list)
            self.assertEqual(len(c.menu.possibleActions[0][1][8]), 2)
            self.assertEqual(c.menu.possibleActions[0][1][8][0], "Manage arXiv PDF")
            self.assertIsInstance(c.menu.possibleActions[0][1][8][1], list)
            self.assertEqual(
                c.menu.possibleActions[0][1][8][1][0].text(), "Delete arXiv PDF"
            )
            self.assertEqual(
                c.menu.possibleActions[0][1][8][1][1].text(), "Copy arXiv PDF"
            )
            self.assertIsInstance(c.menu.possibleActions[0][1][9], list)
            self.assertEqual(len(c.menu.possibleActions[0][1][9]), 2)
            self.assertEqual(c.menu.possibleActions[0][1][9][0], "Manage DOI PDF")
            self.assertIsInstance(c.menu.possibleActions[0][1][9][1], list)
            self.assertEqual(
                c.menu.possibleActions[0][1][9][1][0].text(), "Delete DOI PDF"
            )
            self.assertEqual(
                c.menu.possibleActions[0][1][9][1][1].text(), "Copy DOI PDF"
            )
            self.assertIsInstance(c.menu.possibleActions[0][1][10], list)
            self.assertEqual(len(c.menu.possibleActions[0][1][10]), 2)
            self.assertEqual(c.menu.possibleActions[0][1][10][0], "Manage a.pdf")
            self.assertIsInstance(c.menu.possibleActions[0][1][10][1], list)
            self.assertEqual(
                c.menu.possibleActions[0][1][10][1][0].text(), "Delete a.pdf"
            )
            self.assertEqual(
                c.menu.possibleActions[0][1][10][1][1].text(), "Copy a.pdf"
            )
            self.assertIsInstance(c.menu.possibleActions[0][1][11], list)
            self.assertEqual(len(c.menu.possibleActions[0][1][11]), 2)
            self.assertEqual(c.menu.possibleActions[0][1][11][0], "Manage b.pdf")
            self.assertIsInstance(c.menu.possibleActions[0][1][11][1], list)
            self.assertEqual(
                c.menu.possibleActions[0][1][11][1][0].text(), "Delete b.pdf"
            )
            self.assertEqual(
                c.menu.possibleActions[0][1][11][1][1].text(), "Copy b.pdf"
            )
            self.assertIsInstance(c.menu.possibleActions[0][1][12], list)
            self.assertEqual(len(c.menu.possibleActions[0][1][12]), 2)
            self.assertEqual(c.menu.possibleActions[0][1][12][0], "Manage c.txt")
            self.assertIsInstance(c.menu.possibleActions[0][1][12][1], list)
            self.assertEqual(
                c.menu.possibleActions[0][1][12][1][0].text(), "Delete c.txt"
            )
            self.assertEqual(
                c.menu.possibleActions[0][1][12][1][1].text(), "Copy c.txt"
            )
            self.assertEqual(c.menu.possibleActions[0][1][13], None)
            c.menu.possibleActions[0][1][14].trigger()
            _l.assert_called_once_with(pBGuiView, "abc", "file", fileArg="/fd")

    def test_createContextMenu(self):
        """test createContextMenu"""
        p = QWidget()
        c = CommonBibActions([], p)
        m = c.createContextMenu()
        self.assertEqual(m, None)

        c = CommonBibActions(
            [
                {
                    "bibkey": "abc",
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
                }
            ],
            p,
        )
        with patch(
            "physbiblio.gui.bibWindows.CommonBibActions._createMenuArxiv", autospec=True
        ) as _c1, patch(
            "physbiblio.gui.bibWindows.CommonBibActions._createMenuCopy", autospec=True
        ) as _c2, patch(
            "physbiblio.gui.bibWindows.CommonBibActions._createMenuInspire",
            autospec=True,
        ) as _c3, patch(
            "physbiblio.gui.bibWindows.CommonBibActions._createMenuLinks", autospec=True
        ) as _c4, patch(
            "physbiblio.gui.bibWindows.CommonBibActions._createMenuMarkType",
            autospec=True,
        ) as _c5, patch(
            "physbiblio.gui.bibWindows.CommonBibActions._createMenuPDF", autospec=True
        ) as _c6, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onModify", autospec=True
        ) as _mod, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onClean", autospec=True
        ) as _cle, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onDelete", autospec=True
        ) as _del, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCat", autospec=True
        ) as _cat, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onExp", autospec=True
        ) as _exp, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onExport", autospec=True
        ) as _ext, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCopyAllPDF", autospec=True
        ) as _cap, patch(
            "physbiblio.gui.commonClasses.PBMenu.fillMenu", autospec=True
        ) as _f:
            m = c.createContextMenu()
            self.assertIsInstance(m, PBMenu)
            self.assertEqual(m.parent(), p)
            self.assertIsInstance(m.possibleActions[0], QAction)
            self.assertEqual(m.possibleActions[0].text(), "--Entry: abc--")
            self.assertEqual(m.possibleActions[0].isEnabled(), False)
            self.assertEqual(m.possibleActions[1], None)
            self.assertIsInstance(m.possibleActions[2], QAction)
            self.assertEqual(m.possibleActions[2].text(), "Modify")
            _mod.assert_not_called()
            m.possibleActions[2].trigger()
            _mod.assert_called_once_with(c)
            self.assertIsInstance(m.possibleActions[3], QAction)
            self.assertEqual(m.possibleActions[3].text(), "Clean")
            _cle.assert_not_called()
            m.possibleActions[3].trigger()
            _cle.assert_called_once_with(c)
            self.assertIsInstance(m.possibleActions[4], QAction)
            self.assertEqual(m.possibleActions[4].text(), "Delete")
            _del.assert_not_called()
            m.possibleActions[4].trigger()
            _del.assert_called_once_with(c)
            self.assertEqual(m.possibleActions[5], None)
            _c5.assert_called_once_with(c, c.bibs[0])
            _c2.assert_called_once_with(c, False, c.bibs[0])
            _c6.assert_called_once_with(c, False, c.bibs[0])
            _c4.assert_called_once_with(c, "abc", "1809.00000", "1/2/3/4", "9999999")
            self.assertEqual(m.possibleActions[6], None)
            self.assertIsInstance(m.possibleActions[7], QAction)
            self.assertEqual(m.possibleActions[7].text(), "Select categories")
            _cat.assert_not_called()
            m.possibleActions[7].trigger()
            _cat.assert_called_once_with(c)
            self.assertIsInstance(m.possibleActions[8], QAction)
            self.assertEqual(m.possibleActions[8].text(), "Select experiments")
            _exp.assert_not_called()
            m.possibleActions[8].trigger()
            _exp.assert_called_once_with(c)
            self.assertEqual(m.possibleActions[9], None)
            _c3.assert_called_once_with(c, False, "9999999")
            _c1.assert_called_once_with(c, False, "1809.00000")
            self.assertEqual(m.possibleActions[10], None)
            self.assertIsInstance(m.possibleActions[11], QAction)
            self.assertEqual(m.possibleActions[11].text(), "Export in a .bib file")
            _ext.assert_not_called()
            m.possibleActions[11].trigger()
            _ext.assert_called_once_with(c)
            self.assertIsInstance(m.possibleActions[12], QAction)
            self.assertEqual(
                m.possibleActions[12].text(), "Copy all the corresponding PDF"
            )
            _cap.assert_not_called()
            m.possibleActions[12].trigger()
            _cap.assert_called_once_with(c)
            _f.assert_called_once_with(c.menu)

        c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}], p)
        with patch(
            "physbiblio.gui.bibWindows.CommonBibActions._createMenuArxiv", autospec=True
        ) as _c1, patch(
            "physbiblio.gui.bibWindows.CommonBibActions._createMenuCopy", autospec=True
        ) as _c2, patch(
            "physbiblio.gui.bibWindows.CommonBibActions._createMenuInspire",
            autospec=True,
        ) as _c3, patch(
            "physbiblio.gui.bibWindows.CommonBibActions._createMenuLinks", autospec=True
        ) as _c4, patch(
            "physbiblio.gui.bibWindows.CommonBibActions._createMenuMarkTypeList",
            autospec=True,
        ) as _c5, patch(
            "physbiblio.gui.bibWindows.CommonBibActions._createMenuPDF", autospec=True
        ) as _c6, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onMerge", autospec=True
        ) as _mer, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onClean", autospec=True
        ) as _cle, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onDelete", autospec=True
        ) as _del, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCat", autospec=True
        ) as _cat, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onExp", autospec=True
        ) as _exp, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onExport", autospec=True
        ) as _ext, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onCopyAllPDF", autospec=True
        ) as _cap, patch(
            "physbiblio.gui.commonClasses.PBMenu.fillMenu", autospec=True
        ) as _f:
            m = c.createContextMenu(selection=True)
            self.assertIsInstance(m, PBMenu)
            self.assertEqual(m.parent(), p)
            self.assertIsInstance(m.possibleActions[0], QAction)
            self.assertEqual(m.possibleActions[0].text(), "Merge")
            _mer.assert_not_called()
            m.possibleActions[0].trigger()
            _mer.assert_called_once_with(c)
            self.assertIsInstance(m.possibleActions[1], QAction)
            self.assertEqual(m.possibleActions[1].text(), "Clean")
            _cle.assert_not_called()
            m.possibleActions[1].trigger()
            _cle.assert_called_once_with(c)
            self.assertIsInstance(m.possibleActions[2], QAction)
            self.assertEqual(m.possibleActions[2].text(), "Delete")
            _del.assert_not_called()
            m.possibleActions[2].trigger()
            _del.assert_called_once_with(c)
            self.assertEqual(m.possibleActions[3], None)
            _c5.assert_called_once_with(c)
            _c2.assert_called_once_with(c, True, None)
            _c6.assert_called_once_with(c, True, None)
            _c4.assert_not_called()
            self.assertEqual(m.possibleActions[4], None)
            self.assertIsInstance(m.possibleActions[5], QAction)
            self.assertEqual(m.possibleActions[5].text(), "Select categories")
            _cat.assert_not_called()
            m.possibleActions[5].trigger()
            _cat.assert_called_once_with(c)
            self.assertIsInstance(m.possibleActions[6], QAction)
            self.assertEqual(m.possibleActions[6].text(), "Select experiments")
            _exp.assert_not_called()
            m.possibleActions[6].trigger()
            _exp.assert_called_once_with(c)
            self.assertEqual(m.possibleActions[7], None)
            _c3.assert_called_once_with(c, True, None)
            _c1.assert_called_once_with(c, True, None)
            self.assertEqual(m.possibleActions[8], None)
            self.assertIsInstance(m.possibleActions[9], QAction)
            self.assertEqual(m.possibleActions[9].text(), "Export in a .bib file")
            _ext.assert_not_called()
            m.possibleActions[9].trigger()
            _ext.assert_called_once_with(c)
            self.assertIsInstance(m.possibleActions[10], QAction)
            self.assertEqual(
                m.possibleActions[10].text(), "Copy all the corresponding PDF"
            )
            _cap.assert_not_called()
            m.possibleActions[10].trigger()
            _cap.assert_called_once_with(c)
            _f.assert_called_once_with(c.menu)

        c = CommonBibActions(
            [{"bibkey": "abc"}, {"bibkey": "def"}, {"bibkey": "ghi"}], p
        )
        m = c.createContextMenu(selection=True)
        self.assertEqual(m.possibleActions[0].text(), "Clean")

    def test_onAddPDF(self):
        """test onAddPDF"""
        p = QWidget()
        c = CommonBibActions([{"bibkey": "abc"}], p)
        with patch(
            "physbiblio.pdf.LocalPDF.copyNewFile", return_value=True, autospec=True
        ) as _cp, patch(
            "physbiblio.gui.bibWindows.askFileName",
            return_value="/h/c/file.pdf",
            autospec=True,
        ) as _afn, patch(
            "physbiblio.gui.bibWindows.infoMessage", autospec=True
        ) as _im, patch(
            "os.path.isfile", return_value=True
        ) as _if:
            c.onAddPDF()
            _cp.assert_called_once_with(
                pBPDF, "abc", "/h/c/file.pdf", customName="file.pdf"
            )
            _afn.assert_called_once_with(
                p, "Where is the file located?", filter="Files (*)"
            )
            _im.assert_called_once_with("PDF successfully copied!")
            _if.assert_called_once_with("/h/c/file.pdf")

        with patch(
            "physbiblio.pdf.LocalPDF.copyNewFile", return_value=True, autospec=True
        ) as _cp, patch(
            "physbiblio.gui.bibWindows.askFileName",
            return_value="/h/c/file.pdf",
            autospec=True,
        ) as _afn, patch(
            "physbiblio.gui.bibWindows.infoMessage", autospec=True
        ) as _im, patch(
            "os.path.isfile", return_value=True
        ) as _if:
            c.onAddPDF(ftype="doi")
            _cp.assert_called_once_with(pBPDF, "abc", "/h/c/file.pdf", "doi")
            _afn.assert_called_once_with(
                p, "Where is the file located?", filter="Files (*)"
            )
            _im.assert_called_once_with("PDF successfully copied!")
            _if.assert_called_once_with("/h/c/file.pdf")

        with patch(
            "physbiblio.pdf.LocalPDF.copyNewFile", return_value=False, autospec=True
        ) as _cp, patch(
            "physbiblio.gui.bibWindows.askFileName",
            return_value="/h/c/file.pdf",
            autospec=True,
        ) as _afn, patch(
            "logging.Logger.error"
        ) as _e, patch(
            "os.path.isfile", return_value=True
        ) as _if:
            c.onAddPDF("doi")
            _cp.assert_called_once_with(pBPDF, "abc", "/h/c/file.pdf", "doi")
            _afn.assert_called_once_with(
                p, "Where is the file located?", filter="Files (*)"
            )
            _e.assert_called_once_with("Could not copy the new file!")
            _if.assert_called_once_with("/h/c/file.pdf")

        with patch(
            "physbiblio.pdf.LocalPDF.copyNewFile", return_value=True, autospec=True
        ) as _cp, patch(
            "physbiblio.gui.bibWindows.askFileName", return_value="", autospec=True
        ) as _afn, patch(
            "os.path.isfile", return_value=True
        ) as _if:
            c.onAddPDF()
            _cp.assert_not_called()
            _if.assert_not_called()

        with patch(
            "physbiblio.pdf.LocalPDF.copyNewFile", return_value=True, autospec=True
        ) as _cp, patch(
            "physbiblio.gui.bibWindows.askFileName", return_value="s", autospec=True
        ) as _afn, patch(
            "os.path.isfile", return_value=False
        ) as _if:
            c.onAddPDF()
            _cp.assert_not_called()
            _if.assert_called_once_with("s")

    def test_onAbs(self):
        """test onAbs"""
        c = CommonBibActions(
            [{"bibkey": "abc", "arxiv": "1234.85583"}, {"bibkey": "def", "arxiv": ""}],
            self.mainW,
        )
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.mainWindow.MainWindow.done", autospec=True
        ) as _d, patch(
            "physbiblio.webimport.arxiv.WebSearch.retrieveUrlAll",
            return_value=("text", {"abstract": "some text"}),
            autospec=True,
        ) as _a, patch(
            "physbiblio.database.Entries.updateField", autospec=True
        ) as _u, patch(
            "physbiblio.gui.bibWindows.infoMessage", autospec=True
        ) as _i:
            c.onAbs()
            _i.assert_has_calls(
                [
                    call("some text", title="Abstract of arxiv:1234.85583"),
                    call("No arxiv number for entry 'def'!"),
                ]
            )
            _s.assert_called_once_with(
                self.mainW, "Starting the abstract download process, please wait..."
            )
            _d.assert_called_once_with(self.mainW)
            _a.assert_called_once_with(
                physBiblioWeb.webSearch["arxiv"],
                "1234.85583",
                fullDict=True,
                searchType="id",
            )
            _u.assert_called_once_with(pBDB.bibs, "abc", "abstract", "some text")
            _i.reset_mock()
            _s.reset_mock()
            _d.reset_mock()
            _a.reset_mock()
            _u.reset_mock()
            c.onAbs(message=False)
            _i.assert_called_once_with("No arxiv number for entry 'def'!")
            _s.assert_called_once_with(
                self.mainW, "Starting the abstract download process, please wait..."
            )
            _d.assert_called_once_with(self.mainW)
            _a.assert_called_once_with(
                physBiblioWeb.webSearch["arxiv"],
                "1234.85583",
                fullDict=True,
                searchType="id",
            )
            _u.assert_called_once_with(pBDB.bibs, "abc", "abstract", "some text")

    def test_onArx(self):
        """test onArx"""
        c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.infoFromArxiv", autospec=True
        ) as _i:
            c.onArx()
            _i.assert_called_once_with(
                self.mainW, [{"bibkey": "abc"}, {"bibkey": "def"}]
            )

    def test_onCat(self):
        """test onCat"""
        c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
        self.mainW.selectedCats = []
        self.mainW.previousUnchanged = []
        sc = CatsTreeWindow(
            parent=self.mainW,
            askCats=True,
            expButton=False,
            previous=[],
            multipleRecords=True,
        )
        sc.exec_ = MagicMock()
        self.assertEqual(self.mainW.selectedCats, [])
        with patch(
            "physbiblio.database.Categories.getByEntries",
            return_value=[],
            autospec=True,
        ) as _gc, patch(
            "physbiblio.gui.bibWindows.CatsTreeWindow",
            return_value=sc,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _cwi, patch(
            "physbiblio.database.CatsEntries.insert", autospec=True
        ) as _cei, patch(
            "physbiblio.database.CatsEntries.delete", autospec=True
        ) as _ced, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m:
            c.onCat()
            _cwi.assert_called_once_with(
                parent=self.mainW,
                askCats=True,
                expButton=False,
                previous=[],
                multipleRecords=True,
            )
            _gc.assert_called_once_with(pBDB.cats, ["abc", "def"])
            _cei.assert_not_called()
            _ced.assert_not_called()
            _m.assert_not_called()

        sc = CatsTreeWindow(
            parent=self.mainW,
            askCats=True,
            expButton=False,
            previous=[],
            multipleRecords=True,
        )
        sc.exec_ = MagicMock()
        self.mainW.selectedCats = [999, 1000]
        sc.result = "Ok"
        with patch(
            "physbiblio.database.Categories.getByEntries",
            return_value=[],
            autospec=True,
        ) as _gc, patch(
            "physbiblio.gui.bibWindows.CatsTreeWindow",
            return_value=sc,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _cwi, patch(
            "physbiblio.database.CatsEntries.insert", autospec=True
        ) as _cei, patch(
            "physbiblio.database.CatsEntries.delete", autospec=True
        ) as _ced, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m:
            c.onCat()
            _cwi.assert_called_once_with(
                parent=self.mainW,
                askCats=True,
                expButton=False,
                previous=[],
                multipleRecords=True,
            )
            _gc.assert_called_once_with(pBDB.cats, ["abc", "def"])
            _cei.assert_called_once_with(pBDB.catBib, [999, 1000], ["abc", "def"])
            _ced.assert_not_called()
            _m.assert_called_once_with(self.mainW, "Categories successfully inserted")

        sc = CatsTreeWindow(
            parent=self.mainW,
            askCats=True,
            expButton=False,
            previous=[],
            multipleRecords=True,
        )
        sc.exec_ = MagicMock()
        self.mainW.selectedCats = [999, 1000]
        self.mainW.previousUnchanged = [1002]
        sc.result = "Ok"
        with patch(
            "physbiblio.database.Categories.getByEntries",
            return_value=[{"idCat": 1000}, {"idCat": 1001}, {"idCat": 1002}],
            autospec=True,
        ) as _gc, patch(
            "physbiblio.gui.bibWindows.CatsTreeWindow",
            return_value=sc,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _cwi, patch(
            "physbiblio.database.CatsEntries.insert", autospec=True
        ) as _cei, patch(
            "physbiblio.database.CatsEntries.delete", autospec=True
        ) as _ced, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m:
            c.onCat()
            _cwi.assert_called_once_with(
                parent=self.mainW,
                askCats=True,
                expButton=False,
                previous=[1000, 1001, 1002],
                multipleRecords=True,
            )
            _gc.assert_called_once_with(pBDB.cats, ["abc", "def"])
            _cei.assert_called_once_with(pBDB.catBib, [999, 1000], ["abc", "def"])
            _ced.assert_called_once_with(pBDB.catBib, 1001, ["abc", "def"])
            _m.assert_called_once_with(self.mainW, "Categories successfully inserted")

        c = CommonBibActions([{"bibkey": "abc"}], self.mainW)
        self.mainW.selectedCats = []
        self.mainW.previousUnchanged = []
        sc = CatsTreeWindow(
            parent=self.mainW, askCats=True, expButton=False, previous=[]
        )
        sc.exec_ = MagicMock()
        self.assertEqual(self.mainW.selectedCats, [])
        with patch(
            "physbiblio.database.Categories.getByEntries",
            return_value=[],
            autospec=True,
        ) as _gc, patch(
            "physbiblio.gui.bibWindows.CatsTreeWindow",
            return_value=sc,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _cwi, patch(
            "physbiblio.database.CatsEntries.insert", autospec=True
        ) as _cei, patch(
            "physbiblio.database.CatsEntries.delete", autospec=True
        ) as _ced, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m:
            c.onCat()
            _cwi.assert_called_once_with(
                parent=self.mainW,
                askCats=True,
                askForBib="abc",
                expButton=False,
                previous=[],
            )
            _gc.assert_called_once_with(pBDB.cats, ["abc"])
            _cei.assert_not_called()
            _ced.assert_not_called()
            _m.assert_not_called()

        sc = CatsTreeWindow(
            parent=self.mainW, askCats=True, expButton=False, previous=[]
        )
        sc.exec_ = MagicMock()
        self.mainW.selectedCats = [999, 1000]
        self.mainW.previousUnchanged = [1002]
        sc.result = "Ok"
        with patch(
            "physbiblio.database.Categories.getByEntries",
            return_value=[{"idCat": 1000}, {"idCat": 1001}, {"idCat": 1002}],
            autospec=True,
        ) as _gc, patch(
            "physbiblio.gui.bibWindows.CatsTreeWindow",
            return_value=sc,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _cwi, patch(
            "physbiblio.database.CatsEntries.insert", autospec=True
        ) as _cei, patch(
            "physbiblio.database.CatsEntries.delete", autospec=True
        ) as _ced, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m:
            c.onCat()
            _cwi.assert_called_once_with(
                parent=self.mainW,
                askCats=True,
                askForBib="abc",
                expButton=False,
                previous=[1000, 1001, 1002],
            )
            _gc.assert_called_once_with(pBDB.cats, ["abc"])
            _cei.assert_called_once_with(pBDB.catBib, 999, "abc")
            _ced.assert_has_calls(
                [call(pBDB.catBib, 1001, "abc"), call(pBDB.catBib, 1002, "abc")]
            )
            _m.assert_called_once_with(
                self.mainW, "Categories for 'abc' successfully inserted"
            )

    def test_onCitationCount(self):
        """test onCitationCount"""
        c = CommonBibActions(
            [
                {"bibkey": "abc", "inspire": "1385583"},
                {"bibkey": "def", "inspire": "1358853"},
            ],
            self.mainW,
        )
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.getInspireCitationCount",
            autospec=True,
        ) as _i:
            c.onCitationCount()
            _i.assert_called_once_with(self.mainW, ["1385583", "1358853"])

    def test_onCitations(self):
        """test onCitations"""
        c = CommonBibActions(
            [
                {"bibkey": "abc", "inspire": "1385583"},
                {"bibkey": "def", "inspire": "1358853"},
            ],
            self.mainW,
        )
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.getInspireStats", autospec=True
        ) as _i:
            c.onCitations()
            _i.assert_called_once_with(self.mainW, ["1385583", "1358853"])

    def test_onClean(self):
        """test onClean"""
        c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.cleanAllBibtexs", autospec=True
        ) as _c:
            c.onClean()
            _c.assert_called_once_with(
                self.mainW, useEntries=[{"bibkey": "abc"}, {"bibkey": "def"}]
            )

    def test_onComplete(self):
        """test onComplete"""
        c = CommonBibActions([{"bibkey": "abc", "inspire": "1234"}], self.mainW)
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.updateInspireInfo", autospec=True
        ) as _u:
            c.onComplete()
            _u.assert_called_once_with(self.mainW, "abc", inspireID="1234")
        c = CommonBibActions(
            [{"bibkey": "abc", "inspire": "1234"}, {"bibkey": "def"}], self.mainW
        )
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.updateInspireInfo", autospec=True
        ) as _u:
            c.onComplete()
            _u.assert_called_once_with(
                self.mainW, ["abc", "def"], inspireID=["1234", None]
            )

    def test_onCopyBibtexs(self):
        """test onCopyBibtexs"""
        c = CommonBibActions(
            [
                {"bibkey": "abc", "bibtex": "bibtex 1"},
                {"bibkey": "def", "bibtex": "bibtex 2"},
            ],
            self.mainW,
        )
        with patch("physbiblio.gui.bibWindows.copyToClipboard", autospec=True) as _cp:
            c.onCopyBibtexs()
            _cp.assert_called_once_with("bibtex 1\n\nbibtex 2")

    def test_onCopyCites(self):
        """test onCopyCites"""
        c = CommonBibActions(
            [
                {"bibkey": "abc", "bibtex": "bibtex 1"},
                {"bibkey": "def", "bibtex": "bibtex 2"},
            ],
            self.mainW,
        )
        with patch("physbiblio.gui.bibWindows.copyToClipboard", autospec=True) as _cp:
            c.onCopyCites()
            _cp.assert_called_once_with("\cite{abc,def}")

    def test_onCopyDir(self):
        """test onCopyBibtexs"""
        c = CommonBibActions(
            [
                {"bibkey": "abc", "bibtex": "bibtex 1"},
                {"bibkey": "def", "bibtex": "bibtex 2"},
            ],
            self.mainW,
        )
        with patch(
            "physbiblio.pdf.LocalPDF.getFileDir", side_effect=["dir1", "dir2"]
        ) as _f, patch(
            "physbiblio.gui.bibWindows.copyToClipboard", autospec=True
        ) as _cp:
            c.onCopyDir()
            _f.assert_has_calls([call("abc"), call("def")])
            _cp.assert_called_once_with("dir1 dir2")

    def test_onCopyKeys(self):
        """test onCopyKeys"""
        c = CommonBibActions(
            [
                {"bibkey": "abc", "bibtex": "bibtex 1"},
                {"bibkey": "def", "bibtex": "bibtex 2"},
            ],
            self.mainW,
        )
        with patch("physbiblio.gui.bibWindows.copyToClipboard", autospec=True) as _cp:
            c.onCopyKeys()
            _cp.assert_called_once_with("abc,def")

    def test_onCopyPDFFile(self):
        """test onCopyPDFFile"""
        c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
        pBDB.bibs.lastFetched = ["abc", "def"]
        with patch(
            "physbiblio.gui.bibWindows.askDirName",
            side_effect=["", "/non/exist", "/non/exist"],
            autospec=True,
        ) as _a, patch(
            "physbiblio.pdf.LocalPDF.copyToDir", autospec=True
        ) as _cp, patch(
            "physbiblio.pdf.LocalPDF.getFilePath",
            return_value="/h/e/f.pdf",
            autospec=True,
        ) as _fp:
            c.onCopyPDFFile("abc", "arxiv")
            _a.assert_called_once_with(
                self.mainW, title="Where do you want to save the PDF /h/e/f.pdf?"
            )
            _fp.assert_called_once_with(pBPDF, "abc", "arxiv")
            _cp.assert_not_called()
            _a.reset_mock()
            _fp.reset_mock()
            c.onCopyPDFFile("abc", "arxiv")
            _a.assert_called_once_with(
                self.mainW, title="Where do you want to save the PDF /h/e/f.pdf?"
            )
            _fp.assert_called_once_with(pBPDF, "abc", "arxiv")
            _cp.assert_called_once_with(
                pBPDF, "/non/exist", "abc", fileType="arxiv", customName=None
            )
            _a.reset_mock()
            _cp.reset_mock()
            _fp.reset_mock()
            c.onCopyPDFFile("abc", "new.pdf", "/h/e/new.pdf")
            _a.assert_called_once_with(
                self.mainW, title="Where do you want to save the PDF /h/e/new.pdf?"
            )
            _fp.assert_not_called()
            _cp.assert_called_once_with(
                pBPDF,
                "/non/exist",
                "abc",
                fileType="new.pdf",
                customName="/h/e/new.pdf",
            )

    def test_onCopyAllPDF(self):
        """test onCopyAllPDF"""
        c = CommonBibActions([{"bibkey": "abc"}], self.mainW)
        pBDB.bibs.lastFetched = ["abc", "def"]
        with patch(
            "physbiblio.gui.bibWindows.askDirName", return_value="", autospec=True
        ) as _a, patch("physbiblio.pdf.LocalPDF.checkFile", autospec=True) as _ch:
            c.onCopyAllPDF()
            _a.assert_called_once_with(
                self.mainW, title="Where do you want to save the PDF files?"
            )
            _ch.assert_not_called()
        with patch(
            "physbiblio.gui.bibWindows.askDirName",
            return_value="/non/exist",
            autospec=True,
        ) as _a, patch(
            "physbiblio.pdf.LocalPDF.copyToDir", autospec=True
        ) as _cp, patch(
            "physbiblio.pdf.LocalPDF.getExisting",
            return_value=["a.pdf", "b.pdf"],
            autospec=True,
        ) as _ge, patch(
            "physbiblio.pdf.LocalPDF.checkFile",
            side_effect=[True, False, True, False, False],
            autospec=True,
        ) as _ch:
            c.onCopyAllPDF()
            _ch.assert_called_once_with(pBPDF, "abc", "doi")
            _cp.assert_called_once_with(pBPDF, "/non/exist", "abc", fileType="doi")
            _ge.assert_not_called()
            _ch.reset_mock()
            _cp.reset_mock()
            c.onCopyAllPDF()
            _ch.assert_has_calls(
                [call(pBPDF, "abc", "doi"), call(pBPDF, "abc", "arxiv")]
            )
            _cp.assert_called_once_with(pBPDF, "/non/exist", "abc", fileType="arxiv")
            _ge.assert_not_called()
            _ch.reset_mock()
            _cp.reset_mock()
            c.onCopyAllPDF()
            _ch.assert_has_calls(
                [call(pBPDF, "abc", "doi"), call(pBPDF, "abc", "arxiv")]
            )
            _ge.assert_called_once_with(pBPDF, "abc")
            _cp.assert_has_calls(
                [
                    call(pBPDF, "/non/exist", "abc", "", customName="a.pdf"),
                    call(pBPDF, "/non/exist", "abc", "", customName="b.pdf"),
                ]
            )

        c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
        with patch(
            "physbiblio.gui.bibWindows.askDirName",
            return_value="/non/exist",
            autospec=True,
        ) as _a, patch(
            "physbiblio.pdf.LocalPDF.copyToDir", autospec=True
        ) as _cp, patch(
            "physbiblio.pdf.LocalPDF.checkFile", return_value=True, autospec=True
        ) as _ch:
            c.onCopyAllPDF()
            _ch.assert_has_calls([call(pBPDF, "abc", "doi"), call(pBPDF, "def", "doi")])
            _cp.assert_has_calls(
                [
                    call(pBPDF, "/non/exist", "abc", fileType="doi"),
                    call(pBPDF, "/non/exist", "def", fileType="doi"),
                ]
            )

    def test_onDelete(self):
        """test onDelete"""
        c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
        with patch("physbiblio.gui.bibWindows.deleteBibtex", autospec=True) as _d:
            c.onDelete()
            _d.assert_called_once_with(self.mainW, ["abc", "def"])

    def test_onDeletePDFFile(self):
        """test onDeletePDFFile"""
        c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
        pBDB.bibs.lastFetched = ["abc", "def"]
        with patch(
            "physbiblio.gui.bibWindows.askYesNo",
            side_effect=[False, True, True],
            autospec=True,
        ) as _a, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.pdf.LocalPDF.removeFile", autospec=True
        ) as _rm, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _l, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _r:
            c.onDeletePDFFile("abc", "arxiv", "arxiv PDF")
            _a.assert_called_once_with(
                "Do you really want to delete the %s file for entry %s?"
                % ("arxiv PDF", "abc")
            )
            _s.assert_not_called()
            _rm.assert_not_called()
            c.onDeletePDFFile("abc", "arxiv", "arxiv PDF")
            _s.assert_called_once_with(self.mainW, "deleting arxiv PDF file...")
            _rm.assert_called_once_with(pBPDF, "abc", "arxiv")
            _r.assert_called_once_with(self.mainW, ["abc", "def"])
            _l.assert_called_once_with(pBDB.bibs)
            _rm.reset_mock()
            _s.reset_mock()
            c.onDeletePDFFile("abc", "test.pdf", "test.pdf", "/h/test.pdf")
            _s.assert_called_once_with(self.mainW, "deleting test.pdf file...")
            _rm.assert_called_once_with(pBPDF, "abc", "", fileName="/h/test.pdf")

    def test_onDown(self):
        """test onDown"""
        c = CommonBibActions(
            [{"bibkey": "abc", "arxiv": "1"}, {"bibkey": "def", "arxiv": ""}],
            self.mainW,
        )
        thr = Thread_downloadArxiv("bibkey", self.mainW)
        thr.finished = 1
        thr.start = MagicMock()
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _s, patch(
            "physbiblio.gui.bibWindows.Thread_downloadArxiv",
            return_value=thr,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _i:
            with self.assertRaises(AttributeError):
                c.onDown()
            _s.assert_called_once_with(self.mainW, "downloading PDF for arxiv:1...")
            _i.assert_called_once_with("abc", self.mainW)
        self.assertIsInstance(c.downArxiv_thr, list)
        self.assertEqual(len(c.downArxiv_thr), 1)
        c = CommonBibActions(
            [{"bibkey": "abc", "arxiv": "1"}, {"bibkey": "def", "arxiv": "2"}],
            self.mainW,
        )
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m, patch("PySide2.QtCore.QThread.start", autospec=True) as _s:
            c.onDown()
            self.assertEqual(_s.call_count, 2)
        self.assertIsInstance(c.downArxiv_thr[0], Thread_downloadArxiv)
        self.assertIsInstance(c.downArxiv_thr[1], Thread_downloadArxiv)
        with patch(
            "physbiblio.gui.bibWindows.CommonBibActions.onDownloadArxivDone",
            autospec=True,
        ) as _d:
            c.downArxiv_thr[0].finished.emit()
            _d.assert_called_once_with(c, "1")
            c.downArxiv_thr[1].finished.emit()
            _d.assert_has_calls([call(c, "2")])

    def test_onDownloadArxivDone(self):
        """test onDownloadArxivDone"""
        c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
        pBDB.bibs.lastFetched = ["abc", "def"]
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.done", autospec=True
        ) as _d, patch(
            "physbiblio.gui.mainWindow.MainWindow.sendMessage", autospec=True
        ) as _m, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _l, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _r:
            c.onDownloadArxivDone("1809.00000")
            _m.assert_called_once_with(
                self.mainW,
                "Download of PDF for arXiv:1809.00000 completed! "
                + "Please check that it worked...",
            )
            _d.assert_called_once_with(self.mainW)
            _l.assert_called_once_with(pBDB.bibs)
            _r.assert_called_once_with(self.mainW, ["abc", "def"])

    def test_onExp(self):
        """test onExp"""
        c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
        se = ExpsListWindow(parent=self.mainW, askExps=True, previous=[])
        se.exec_ = MagicMock()
        self.mainW.selectedExps = [999, 1000]
        with patch(
            "physbiblio.gui.bibWindows.infoMessage", autospec=True
        ) as _im, patch(
            "physbiblio.gui.bibWindows.ExpsListWindow",
            return_value=se,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _ewi, patch(
            "physbiblio.database.EntryExps.insert", autospec=True
        ) as _eei, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m:
            c.onExp()
            _im.assert_called_once_with(
                "Warning: you can just add experiments "
                + "to the selected entries, not delete!"
            )
            _ewi.assert_called_once_with(parent=self.mainW, askExps=True, previous=[])
            _eei.assert_not_called()
            _m.assert_not_called()
            se.result = "Ok"
            c.onExp()
            _eei.assert_called_once_with(pBDB.bibExp, ["abc", "def"], [999, 1000])
            _m.assert_called_once_with(self.mainW, "Experiments successfully inserted")

        c = CommonBibActions([{"bibkey": "abc"}], self.mainW)
        se = ExpsListWindow(parent=self.mainW, askExps=True, previous=[])
        se.exec_ = MagicMock()
        self.mainW.selectedExps = [999, 1000]
        with patch(
            "physbiblio.database.Experiments.getByEntry", return_value=[], autospec=True
        ) as _ge, patch(
            "physbiblio.gui.bibWindows.ExpsListWindow",
            return_value=se,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _ewi, patch(
            "physbiblio.database.EntryExps.insert", autospec=True
        ) as _eei, patch(
            "physbiblio.database.EntryExps.delete", autospec=True
        ) as _eed, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m:
            c.onExp()
            _ge.assert_called_once_with(pBDB.exps, "abc")
            _ewi.assert_called_once_with(
                parent=self.mainW, askExps=True, askForBib="abc", previous=[]
            )
            _eei.assert_not_called()
            _eed.assert_not_called()
            _m.assert_not_called()
            se.result = "Ok"
            c.onExp()
            _eed.assert_not_called()
            _eei.assert_has_calls(
                [call(pBDB.bibExp, "abc", 999), call(pBDB.bibExp, "abc", 1000)]
            )
            _m.assert_called_once_with(
                self.mainW, "Experiments for 'abc' successfully inserted"
            )

        with patch(
            "physbiblio.database.Experiments.getByEntry",
            return_value=[{"idExp": 1000}, {"idExp": 1001}],
            autospec=True,
        ) as _ge, patch(
            "physbiblio.gui.bibWindows.ExpsListWindow",
            return_value=se,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _ewi, patch(
            "physbiblio.database.EntryExps.insert", autospec=True
        ) as _eei, patch(
            "physbiblio.database.EntryExps.delete", autospec=True
        ) as _eed, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m:
            c.onExp()
            _ge.assert_called_once_with(pBDB.exps, "abc")
            _ewi.assert_called_once_with(
                parent=self.mainW, askExps=True, askForBib="abc", previous=[1000, 1001]
            )
            _eed.assert_called_once_with(pBDB.bibExp, "abc", 1001)
            _eei.assert_called_once_with(pBDB.bibExp, "abc", 999)
            _m.assert_called_once_with(
                self.mainW, "Experiments for 'abc' successfully inserted"
            )

    def test_onExport(self):
        """test onExport"""
        c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.exportSelection", autospec=True
        ) as _e:
            c.onExport()
            _e.assert_called_once_with(
                self.mainW, [{"bibkey": "abc"}, {"bibkey": "def"}]
            )

    def test_onMerge(self):
        """test onMerge"""
        c = CommonBibActions(
            [
                {
                    "bibkey": "abc",
                    "bibtex": '@article{abc, title="abc"}',
                    "doi": "1/2/3",
                    "old_keys": "",
                    "year": "2018",
                },
                {
                    "bibkey": "def",
                    "bibtex": '@article{def, title="def"}',
                    "doi": "1/2/3",
                    "old_keys": "",
                    "year": 2018,
                },
            ],
            self.mainW,
        )
        e = {
            "bibkey": "new",
            "bibtex": '@article{new, title="new"}',
            "doi": "1/2/3",
            "old_keys": "",
            "year": "2018",
        }
        with patch("logging.Logger.warning") as _w:
            mb = MergeBibtexs(e, e, self.mainW)
        mb.exec_ = MagicMock()
        mb.onCancel()
        # non accepted MergeBibtex form
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m, patch(
            "physbiblio.gui.bibWindows.MergeBibtexs",
            return_value=mb,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _mbi, patch(
            "logging.Logger.warning"
        ) as _w:
            c.onMerge()
            _mbi.assert_called_once_with(c.bibs[0], c.bibs[1], self.mainW)
            _m.assert_called_once_with(self.mainW, "Nothing to do...")
        mb.result = True
        pBDB.bibs.lastFetched = ["last"]
        # empty bibtex or bibkey
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rl, patch(
            "physbiblio.gui.bibWindows.MergeBibtexs",
            return_value=mb,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _mbi, patch(
            "physbiblio.databaseCore.PhysBiblioDBCore.commit",
            return_value=[],
            autospec=True,
        ) as _c, patch(
            "physbiblio.databaseCore.PhysBiblioDBCore.undo",
            return_value=[],
            autospec=True,
        ) as _u, patch(
            "physbiblio.database.Entries.prepareInsert",
            side_effect=[
                {"bibkey": "merged", "bibtex": ""},
                {"bibkey": "", "bibtex": "new bibtex"},
            ],
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.delete", return_value=[], autospec=True
        ) as _de, patch(
            "physbiblio.database.Entries.insert", return_value=[], autospec=True
        ) as _in, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _fl, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.error"
        ) as _e:
            c.onMerge()
            _m.assert_not_called()
            _rl.assert_not_called()
            _mbi.assert_called_once_with(c.bibs[0], c.bibs[1], self.mainW)
            _c.assert_not_called()
            _u.assert_not_called()
            _pi.assert_called_once_with(
                pBDB.bibs,
                bibkey=u"new",
                bibtex=u'@article{new, title="new"}',
                book=0,
                doi=u"1/2/3",
                exp_paper=0,
                lecture=0,
                marks="",
                noUpdate=0,
                old_keys="abc, def",
                phd_thesis=0,
                proceeding=0,
                review=0,
                year=u"2018",
            )
            _de.assert_not_called()
            _in.assert_not_called()
            _fl.assert_not_called()
            _w.assert_not_called()
            _e.assert_called_once_with("Empty bibtex and/or bibkey!")

            _e.reset_mock()
            c.onMerge()
            _e.assert_called_once_with("Empty bibtex and/or bibkey!")

        e = {
            "bibkey": "new",
            "bibtex": '@article{new, title="new"}',
            "doi": "1/2/3",
            "old_keys": "",
            "book": 1,
            "year": "2018",
        }
        with patch("logging.Logger.warning") as _w:
            mb = MergeBibtexs(e, e, self.mainW)
        mb.exec_ = MagicMock()
        mb.result = True
        # cannot delete
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rl, patch(
            "physbiblio.gui.bibWindows.MergeBibtexs",
            return_value=mb,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _mbi, patch(
            "physbiblio.databaseCore.PhysBiblioDBCore.commit",
            return_value=[],
            autospec=True,
        ) as _c, patch(
            "physbiblio.databaseCore.PhysBiblioDBCore.undo",
            return_value=[],
            autospec=True,
        ) as _u, patch(
            "physbiblio.database.Entries.prepareInsert",
            return_value={"bibkey": "merged", "bibtex": "new bibtex"},
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.delete",
            side_effect=Exception("error"),
            autospec=True,
        ) as _de, patch(
            "physbiblio.database.Entries.insert", return_value=False, autospec=True
        ) as _in, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _fl, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.error"
        ) as _er, patch(
            "logging.Logger.exception"
        ) as _ex:
            c.onMerge()
            _m.assert_not_called()
            _rl.assert_not_called()
            _mbi.assert_called_once_with(c.bibs[0], c.bibs[1], self.mainW)
            _c.assert_called_once_with(pBDB)
            _u.assert_called_once_with(pBDB)
            _pi.assert_called_once_with(
                pBDB.bibs,
                bibkey=u"new",
                bibtex=u'@article{new, title="new"}',
                book=0,
                doi=u"1/2/3",
                exp_paper=0,
                lecture=0,
                marks="",
                noUpdate=0,
                old_keys="abc, def",
                phd_thesis=0,
                proceeding=0,
                review=0,
                year=u"2018",
            )
            _de.assert_called_once_with(pBDB.bibs, "abc")
            _in.assert_not_called()
            _fl.assert_not_called()
            _w.assert_not_called()
            _er.assert_not_called()
            _ex.assert_called_once_with("Cannot delete old items!")
        # cannot insert
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rl, patch(
            "physbiblio.gui.bibWindows.MergeBibtexs",
            return_value=mb,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _mbi, patch(
            "physbiblio.databaseCore.PhysBiblioDBCore.commit",
            return_value=[],
            autospec=True,
        ) as _c, patch(
            "physbiblio.databaseCore.PhysBiblioDBCore.undo",
            return_value=[],
            autospec=True,
        ) as _u, patch(
            "physbiblio.database.Entries.prepareInsert",
            return_value={"bibkey": "merged", "bibtex": "new bibtex"},
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.delete", return_value=True, autospec=True
        ) as _de, patch(
            "physbiblio.database.Entries.insert", return_value=False, autospec=True
        ) as _in, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _fl, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.error"
        ) as _er, patch(
            "logging.Logger.exception"
        ) as _ex:
            c.onMerge()
            _m.assert_not_called()
            _rl.assert_not_called()
            _mbi.assert_called_once_with(c.bibs[0], c.bibs[1], self.mainW)
            _c.assert_called_once_with(pBDB)
            _u.assert_called_once_with(pBDB)
            _pi.assert_called_once_with(
                pBDB.bibs,
                bibkey=u"new",
                bibtex=u'@article{new, title="new"}',
                book=0,
                doi=u"1/2/3",
                exp_paper=0,
                lecture=0,
                marks="",
                noUpdate=0,
                old_keys="abc, def",
                phd_thesis=0,
                proceeding=0,
                review=0,
                year=u"2018",
            )
            _de.assert_has_calls([call(pBDB.bibs, "abc"), call(pBDB.bibs, "def")])
            _in.assert_called_once_with(
                pBDB.bibs, {"bibkey": "merged", "bibtex": "new bibtex"}
            )
            _fl.assert_not_called()
            _w.assert_not_called()
            _er.assert_called_once_with("Cannot insert new item!")
            _ex.assert_not_called()
        # cannot reload
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent",
            side_effect=Exception("error"),
            autospec=True,
        ) as _rl, patch(
            "physbiblio.gui.bibWindows.MergeBibtexs",
            return_value=mb,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _mbi, patch(
            "physbiblio.databaseCore.PhysBiblioDBCore.commit",
            return_value=[],
            autospec=True,
        ) as _c, patch(
            "physbiblio.databaseCore.PhysBiblioDBCore.undo",
            return_value=[],
            autospec=True,
        ) as _u, patch(
            "physbiblio.database.Entries.prepareInsert",
            return_value={"bibkey": "merged", "bibtex": "new bibtex"},
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.delete", return_value=True, autospec=True
        ) as _de, patch(
            "physbiblio.database.Entries.insert", return_value=True, autospec=True
        ) as _in, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _fl, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.error"
        ) as _er, patch(
            "logging.Logger.exception"
        ) as _ex:
            c.onMerge()
            _m.assert_not_called()
            _rl.assert_called_once_with(self.mainW, ["last"])
            _mbi.assert_called_once_with(c.bibs[0], c.bibs[1], self.mainW)
            _c.assert_called_once_with(pBDB)
            _u.assert_not_called()
            _pi.assert_called_once_with(
                pBDB.bibs,
                bibkey=u"new",
                bibtex=u'@article{new, title="new"}',
                book=0,
                doi=u"1/2/3",
                exp_paper=0,
                lecture=0,
                marks="",
                noUpdate=0,
                old_keys="abc, def",
                phd_thesis=0,
                proceeding=0,
                review=0,
                year=u"2018",
            )
            _de.assert_has_calls([call(pBDB.bibs, "abc"), call(pBDB.bibs, "def")])
            _in.assert_called_once_with(
                pBDB.bibs, {"bibkey": "merged", "bibtex": "new bibtex"}
            )
            _fl.assert_called_once_with(pBDB.bibs)
            _w.assert_called_once_with("Impossible to reload content.")
            _er.assert_not_called()
            _ex.assert_not_called()
        # working
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _rl, patch(
            "physbiblio.gui.bibWindows.MergeBibtexs",
            return_value=mb,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _mbi, patch(
            "physbiblio.databaseCore.PhysBiblioDBCore.commit",
            return_value=[],
            autospec=True,
        ) as _c, patch(
            "physbiblio.databaseCore.PhysBiblioDBCore.undo",
            return_value=[],
            autospec=True,
        ) as _u, patch(
            "physbiblio.database.Entries.prepareInsert",
            return_value={"bibkey": "merged", "bibtex": "new bibtex"},
            autospec=True,
        ) as _pi, patch(
            "physbiblio.database.Entries.delete", return_value=True, autospec=True
        ) as _de, patch(
            "physbiblio.database.Entries.insert", return_value=True, autospec=True
        ) as _in, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _fl, patch(
            "physbiblio.database.Categories.getByEntry",
            return_value=[{"idCat": 321}, {"idCat": 432}],
            autospec=True,
        ) as _cebk, patch(
            "physbiblio.database.CatsEntries.delete", return_value=True, autospec=True
        ) as _cede, patch(
            "physbiblio.database.CatsEntries.insert", return_value=True, autospec=True
        ) as _cein, patch(
            "physbiblio.database.Experiments.getByEntry",
            return_value=[{"idExp": 4321}, {"idExp": 5432}],
            autospec=True,
        ) as _eebk, patch(
            "physbiblio.database.EntryExps.delete", return_value=True, autospec=True
        ) as _eede, patch(
            "physbiblio.database.EntryExps.insert", return_value=True, autospec=True
        ) as _eein, patch(
            "physbiblio.pdf.LocalPDF.mergePDFFolders", autospec=True
        ) as _mpdf, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "logging.Logger.error"
        ) as _er, patch(
            "logging.Logger.exception"
        ) as _ex:
            c.onMerge()
            _m.assert_not_called()
            _rl.assert_called_once_with(self.mainW, ["last"])
            _mbi.assert_called_once_with(c.bibs[0], c.bibs[1], self.mainW)
            _c.assert_called_once_with(pBDB)
            _u.assert_not_called()
            _pi.assert_called_once_with(
                pBDB.bibs,
                bibkey=u"new",
                bibtex=u'@article{new, title="new"}',
                book=0,
                doi=u"1/2/3",
                exp_paper=0,
                lecture=0,
                marks="",
                noUpdate=0,
                old_keys="abc, def",
                phd_thesis=0,
                proceeding=0,
                review=0,
                year=u"2018",
            )
            _de.assert_has_calls([call(pBDB.bibs, "abc"), call(pBDB.bibs, "def")])
            _in.assert_called_once_with(
                pBDB.bibs, {"bibkey": "merged", "bibtex": "new bibtex"}
            )
            _fl.assert_called_once_with(pBDB.bibs)
            _w.assert_not_called()
            _er.assert_not_called()
            _ex.assert_not_called()
            _cebk.assert_has_calls([call(pBDB.cats, "abc"), call(pBDB.cats, "def")])
            _cede.assert_has_calls(
                [
                    call(pBDB.catBib, 321, "abc"),
                    call(pBDB.catBib, 432, "abc"),
                    call(pBDB.catBib, 321, "def"),
                    call(pBDB.catBib, 432, "def"),
                ]
            )
            _cein.assert_has_calls(
                [
                    call(pBDB.catBib, 321, "merged"),
                    call(pBDB.catBib, 432, "merged"),
                    call(pBDB.catBib, 321, "merged"),
                    call(pBDB.catBib, 432, "merged"),
                ]
            )
            _eebk.assert_has_calls([call(pBDB.exps, "abc"), call(pBDB.exps, "def")])
            _eede.assert_has_calls(
                [
                    call(pBDB.bibExp, "abc", 4321),
                    call(pBDB.bibExp, "abc", 5432),
                    call(pBDB.bibExp, "def", 4321),
                    call(pBDB.bibExp, "def", 5432),
                ]
            )
            _eein.assert_has_calls(
                [
                    call(pBDB.bibExp, "merged", 4321),
                    call(pBDB.bibExp, "merged", 5432),
                    call(pBDB.bibExp, "merged", 4321),
                    call(pBDB.bibExp, "merged", 5432),
                ]
            )
            _mpdf.assert_has_calls(
                [call(pBPDF, "abc", "merged"), call(pBPDF, "def", "merged")]
            )

    def test_onModify(self):
        """test onModify"""
        c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
        with patch("physbiblio.gui.bibWindows.editBibtex", autospec=True) as _e:
            c.onModify()
            _e.assert_called_once_with(self.mainW, "abc")

    def test_onUpdate(self):
        """test onUpdate"""
        c = CommonBibActions([{"bibkey": "abc"}, {"bibkey": "def"}], self.mainW)
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.updateAllBibtexs", autospec=True
        ) as _u:
            c.onUpdate()
            _u.assert_called_once_with(
                self.mainW,
                force=False,
                reloadAll=False,
                startFrom=0,
                useEntries=[{"bibkey": "abc"}, {"bibkey": "def"}],
            )
            _u.reset_mock()
            c.onUpdate(force=True)
            _u.assert_called_once_with(
                self.mainW,
                force=True,
                reloadAll=False,
                startFrom=0,
                useEntries=[{"bibkey": "abc"}, {"bibkey": "def"}],
            )
            _u.reset_mock()
            c.onUpdate(reloadAll=True)
            _u.assert_called_once_with(
                self.mainW,
                force=False,
                reloadAll=True,
                startFrom=0,
                useEntries=[{"bibkey": "abc"}, {"bibkey": "def"}],
            )

    def test_onUpdateMark(self):
        """test onUpdateMark"""
        c = CommonBibActions(
            [{"bibkey": "abc", "marks": "imp"}, {"bibkey": "def", "marks": "imp,new"}],
            self.mainW,
        )
        pBDB.bibs.lastFetched = ["abc", "def"]
        with patch(
            "physbiblio.database.Entries.updateField", autospec=True
        ) as _uf, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _l, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _r:
            c.onUpdateMark("new")
            _uf.assert_has_calls(
                [
                    call(pBDB.bibs, "abc", "marks", "imp,new", verbose=0),
                    call(pBDB.bibs, "def", "marks", "imp", verbose=0),
                ]
            )
            _r.assert_called_once_with(self.mainW, ["abc", "def"])
            _l.assert_called_once_with(pBDB.bibs)
            _uf.reset_mock()
            c.onUpdateMark("bad")
            _uf.assert_has_calls(
                [
                    call(pBDB.bibs, "abc", "marks", "bad,imp", verbose=0),
                    call(pBDB.bibs, "def", "marks", "bad,imp,new", verbose=0),
                ]
            )
            _uf.reset_mock()
            c.onUpdateMark("imp")
            _uf.assert_has_calls(
                [
                    call(pBDB.bibs, "abc", "marks", "", verbose=0),
                    call(pBDB.bibs, "def", "marks", "new", verbose=0),
                ]
            )
            _uf.reset_mock()
            c.onUpdateMark("new", force=0)
            _uf.assert_has_calls(
                [
                    call(pBDB.bibs, "abc", "marks", "imp", verbose=0),
                    call(pBDB.bibs, "def", "marks", "imp", verbose=0),
                ]
            )
            _uf.reset_mock()
            c.onUpdateMark("new", force=1)
            _uf.assert_has_calls(
                [
                    call(pBDB.bibs, "abc", "marks", "imp,new", verbose=0),
                    call(pBDB.bibs, "def", "marks", "imp,new", verbose=0),
                ]
            )
            _uf.reset_mock()
            c.onUpdateMark("imp", force=1)
            _uf.assert_has_calls(
                [
                    call(pBDB.bibs, "abc", "marks", "imp", verbose=0),
                    call(pBDB.bibs, "def", "marks", "imp,new", verbose=0),
                ]
            )
            c.onUpdateMark("imp", force=0)
            _uf.assert_has_calls(
                [
                    call(pBDB.bibs, "abc", "marks", "", verbose=0),
                    call(pBDB.bibs, "def", "marks", "new", verbose=0),
                ]
            )
        with patch("logging.Logger.warning") as _w:
            c.onUpdateMark("mark")
            _w.assert_called_once_with("Invalid mark: 'mark'")

    def test_onUpdateType(self):
        """test onUpdateType"""
        c = CommonBibActions(
            [
                {
                    "bibkey": "abc",
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
                {
                    "bibkey": "def",
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
                },
            ],
            self.mainW,
        )
        pBDB.bibs.lastFetched = ["abc", "def"]
        with patch(
            "physbiblio.database.Entries.updateField", autospec=True
        ) as _uf, patch(
            "physbiblio.database.Entries.fetchFromLast",
            return_value=pBDB.bibs,
            autospec=True,
        ) as _l, patch(
            "physbiblio.gui.mainWindow.MainWindow.reloadMainContent", autospec=True
        ) as _r:
            c.onUpdateType("book")
            _uf.assert_has_calls(
                [
                    call(pBDB.bibs, "abc", "book", 0, verbose=0),
                    call(pBDB.bibs, "def", "book", 1, verbose=0),
                ]
            )
            _r.assert_called_once_with(self.mainW, ["abc", "def"])
            _l.assert_called_once_with(pBDB.bibs)
            _uf.reset_mock()
            c.onUpdateType("proceeding")
            _uf.assert_has_calls(
                [
                    call(pBDB.bibs, "abc", "proceeding", 1, verbose=0),
                    call(pBDB.bibs, "def", "proceeding", 0, verbose=0),
                ]
            )
            _uf.reset_mock()
            c.onUpdateType("phd_thesis")
            _uf.assert_has_calls(
                [
                    call(pBDB.bibs, "abc", "phd_thesis", 1, verbose=0),
                    call(pBDB.bibs, "def", "phd_thesis", 1, verbose=0),
                ]
            )
            _uf.reset_mock()
            c.onUpdateType("book", force=1)
            _uf.assert_has_calls(
                [
                    call(pBDB.bibs, "abc", "book", 1, verbose=0),
                    call(pBDB.bibs, "def", "book", 1, verbose=0),
                ]
            )
            _uf.reset_mock()
            c.onUpdateType("book", force=0)
            _uf.assert_has_calls(
                [
                    call(pBDB.bibs, "abc", "book", 0, verbose=0),
                    call(pBDB.bibs, "def", "book", 0, verbose=0),
                ]
            )
            _uf.reset_mock()
            c.onUpdateType("proceeding", force=0)
            _uf.assert_has_calls(
                [
                    call(pBDB.bibs, "abc", "proceeding", 0, verbose=0),
                    call(pBDB.bibs, "def", "proceeding", 0, verbose=0),
                ]
            )
            _uf.reset_mock()
            c.onUpdateType("phd_thesis", force=1)
            _uf.assert_has_calls(
                [
                    call(pBDB.bibs, "abc", "phd_thesis", 1, verbose=0),
                    call(pBDB.bibs, "def", "phd_thesis", 1, verbose=0),
                ]
            )
        with patch("logging.Logger.warning") as _w:
            c.onUpdateType("books")
            _w.assert_called_once_with("Invalid type: 'books'")


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestBibtexListWindow(GUIwMainWTestCase):
    """test BibtexListWindow"""

    @classmethod
    def setUpClass(self):
        """Define useful things"""
        super(TestBibtexListWindow, self).setUpClass()
        self.mainW.bottomLeft = BibtexInfo(self.mainW)
        self.mainW.bottomCenter = BibtexInfo(self.mainW)
        self.mainW.bottomRight = BibtexInfo(self.mainW)

    def test_init(self):
        """test __init__"""
        with patch(
            "PySide2.QtWidgets.QFrame.__init__", return_value=None, autospec=True
        ) as _fi, patch(
            "physbiblio.gui.commonClasses.ObjListWindow.__init__",
            return_value=None,
            autospec=True,
        ) as _oi, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.createActions", autospec=True
        ) as _ca, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.createTable", autospec=True
        ) as _ct:
            bw = BibtexListWindow(parent=self.mainW, bibs=[])
            _fi.assert_called_once_with(bw, self.mainW)
            _oi.assert_called_once_with(bw, self.mainW)
            _ca.assert_called_once_with(bw)
            _ct.assert_called_once_with(bw)

        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.createActions", autospec=True
        ) as _ca, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.createTable", autospec=True
        ) as _ct:
            bw = BibtexListWindow(bibs=[])
            self.assertIsInstance(bw, QFrame)
            self.assertIsInstance(bw, ObjListWindow)
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
            self.assertEqual(
                bw.colContents, pbConfig.params["bibtexListColumns"] + ["type", "pdf"]
            )

        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.createTable", autospec=True
        ) as _ct:
            bw = BibtexListWindow(
                parent=self.mainW,
                bibs=[{"bibkey": "abc"}],
                askBibs=True,
                previous=["abc"],
            )
        self.assertIsInstance(bw, QFrame)
        self.assertIsInstance(bw, ObjListWindow)
        self.assertEqual(bw.parent(), self.mainW)
        self.assertEqual(bw.mainWin, self.mainW)
        self.assertEqual(bw.bibs, [{"bibkey": "abc"}])
        self.assertEqual(bw.askBibs, True)
        self.assertEqual(bw.previous, ["abc"])

    @patch.dict(pbConfig.params, {"bibtexListColumns": ["bibkey"]}, clear=False)
    def test_getRowBibkey(self):
        """test getRowBibkey"""
        bw = BibtexListWindow(
            bibs=[{"bibkey": "abc"}, {"bibkey": "def"}, {"bibkey": ""}]
        )
        with patch(
            "physbiblio.database.Entries.getByBibkey",
            side_effect=[["Rabc"], ["Rabc"], ["Rdef"], []],
            autospec=True,
        ) as _gbb, patch("logging.Logger.debug") as _d:
            self.assertEqual(
                bw.getRowBibkey(bw.proxyModel, bw.proxyModel.index(1, 0)), "abc"
            )
            self.assertEqual(
                bw.getRowBibkey(bw.tableModel, bw.tableModel.index(1, 3)), "def"
            )
            self.assertEqual(
                bw.getRowBibkey(bw.proxyModel, bw.proxyModel.index(2, 0)), "def"
            )
            # will fail because of no DB correspondence:
            self.assertEqual(
                bw.getRowBibkey(bw.proxyModel, bw.proxyModel.index(2, 0)), None
            )
            _d.assert_called_once_with("The entry cannot be found!")
            _gbb.reset_mock()
            self.assertEqual(
                bw.getRowBibkey(bw.proxyModel, bw.proxyModel.index(0, 0)), None
            )
            _gbb.assert_not_called()
            self.assertEqual(
                bw.getRowBibkey(bw.tableModel, bw.tableModel.index(12, 0)), None
            )
            _gbb.assert_not_called()

    @patch.dict(pbConfig.params, {"bibtexListColumns": ["bibkey"]}, clear=False)
    def test_onSelectionChanged(self):
        """test reloadColumnContents"""
        bw = BibtexListWindow(
            bibs=[{"bibkey": "abc"}, {"bibkey": "def"}, {"bibkey": "ghi"}]
        )
        self.assertEqual(
            bw.tableModel.selectedElements, {"abc": False, "def": False, "ghi": False}
        )
        bw.tableview.selectRow(0)
        self.assertEqual(
            bw.tableModel.selectedElements, {"abc": False, "def": False, "ghi": False}
        )
        self.assertFalse(bw.clearAct.isEnabled())
        self.assertFalse(bw.selAllAct.isEnabled())
        self.assertFalse(bw.unselAllAct.isEnabled())
        self.assertFalse(bw.okAct.isEnabled())
        self.assertFalse(bw.tableModel.ask)
        itemSelection = bw.tableview.selectionModel().selectedRows()
        selectedItems = bw.tableview.selectionModel().selection()
        bw.tableview.selectionModel().clearSelection()
        bw.tableview.selectRow(2)
        self.assertFalse(bw.clearAct.isEnabled())
        self.assertFalse(bw.selAllAct.isEnabled())
        self.assertFalse(bw.unselAllAct.isEnabled())
        self.assertFalse(bw.okAct.isEnabled())
        self.assertFalse(bw.tableModel.ask)
        selectedItems.merge(
            bw.tableview.selectionModel().selection(), QItemSelectionModel.Select
        )
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getRowBibkey",
            autospec=True,
            side_effect=["abc", "ghi", "abc", "ghi"],
        ) as _gb:
            bw.tableview.selectionModel().clearSelection()
            bw.tableview.selectionModel().select(
                selectedItems, QItemSelectionModel.Select
            )
            self.assertTrue(bw.clearAct.isEnabled())
            self.assertTrue(bw.selAllAct.isEnabled())
            self.assertTrue(bw.unselAllAct.isEnabled())
            self.assertTrue(bw.okAct.isEnabled())
            self.assertTrue(bw.tableModel.ask)
            self.assertEqual(
                bw.tableModel.selectedElements, {"abc": True, "def": False, "ghi": True}
            )
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getRowBibkey",
            autospec=True,
            side_effect=["abc", "ghi", "def"],
        ) as _gb, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.restoreSort", autospec=True
        ) as _r:
            bw.tableview.selectionModel().clearSelection()
            _r.reset_mock()
            bw.tableview.selectRow(1)
            _r.assert_called_once_with(bw)
            self.assertTrue(bw.clearAct.isEnabled())
            self.assertTrue(bw.selAllAct.isEnabled())
            self.assertTrue(bw.unselAllAct.isEnabled())
            self.assertTrue(bw.okAct.isEnabled())
            self.assertTrue(bw.tableModel.ask)
            self.assertEqual(
                bw.tableModel.selectedElements,
                {"abc": False, "def": True, "ghi": False},
            )

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
        self.assertEqual(
            bw.colContents, pbConfig.params["bibtexListColumns"] + ["type", "pdf"]
        )

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
        bw.tableModel.ask = False
        bw.changeEnableActions()
        self.assertFalse(bw.clearAct.isEnabled())
        self.assertFalse(bw.selAllAct.isEnabled())
        self.assertFalse(bw.unselAllAct.isEnabled())
        self.assertFalse(bw.okAct.isEnabled())
        bw.tableModel.ask = True
        bw.changeEnableActions(status=False)
        self.assertFalse(bw.clearAct.isEnabled())
        self.assertFalse(bw.selAllAct.isEnabled())
        self.assertFalse(bw.unselAllAct.isEnabled())
        self.assertFalse(bw.okAct.isEnabled())

    def test_changeFilterSort(self):
        """test changeFilterSort"""
        bw = BibtexListWindow(bibs=[])
        with patch(
            "physbiblio.gui.commonClasses.ObjListWindow.changeFilter", autospec=True
        ) as _f, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.restoreSort", autospec=True
        ) as _r:
            bw.changeFilterSort("abc")
            _f.assert_called_once_with(bw, "abc")
            _r.assert_called_once_with(bw)

    def test_clearSelection(self):
        """test clearSelection"""
        bw = BibtexListWindow(bibs=[])
        bw.tableModel.previous = ["abc"]
        with patch(
            "physbiblio.gui.bibWindows.BibTableModel.prepareSelected", autospec=True
        ) as _ps, patch(
            "physbiblio.gui.bibWindows.BibTableModel.changeAsk", autospec=True
        ) as _ca, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.changeEnableActions",
            autospec=True,
        ) as _ea, patch(
            "PySide2.QtWidgets.QTableView.clearSelection", autospec=True
        ) as _cs, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.restoreSort", autospec=True
        ) as _r:
            bw.clearSelection()
            self.assertEqual(bw.tableModel.previous, [])
            _ps.assert_called_once_with(bw.tableModel)
            _ca.assert_called_once_with(bw.tableModel, False)
            _ea.assert_called_once_with(bw, status=False)
            _cs.assert_called_once_with()
            _r.assert_called_once_with(bw)

    def test_createActions(self):
        """test createActions"""
        bw = BibtexListWindow(bibs=[])
        images = [
            QImage(":/images/edit-node.png").convertToFormat(
                QImage.Format_ARGB32_Premultiplied
            ),
            QImage(":/images/dialog-ok-apply.png").convertToFormat(
                QImage.Format_ARGB32_Premultiplied
            ),
            QImage(":/images/edit-clear.png").convertToFormat(
                QImage.Format_ARGB32_Premultiplied
            ),
            QImage(":/images/edit-select-all.png").convertToFormat(
                QImage.Format_ARGB32_Premultiplied
            ),
            QImage(":/images/edit-unselect-all.png").convertToFormat(
                QImage.Format_ARGB32_Premultiplied
            ),
        ]
        self.assertIsInstance(bw.selAct, QAction)
        self.assertEqual(bw.selAct.text(), "&Select entries")
        self.assertEqual(bw.selAct.parent(), bw)
        self.assertEqual(images[0], bw.selAct.icon().pixmap(images[0].size()).toImage())
        self.assertEqual(bw.selAct.statusTip(), "Select entries from the list")
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.enableSelection", autospec=True
        ) as _f:
            bw.selAct.trigger()
            _f.assert_called_once_with(bw)

        self.assertIsInstance(bw.okAct, QAction)
        self.assertEqual(bw.okAct.text(), "Selection &completed")
        self.assertEqual(bw.okAct.parent(), bw)
        self.assertEqual(images[1], bw.okAct.icon().pixmap(images[1].size()).toImage())
        self.assertEqual(bw.okAct.statusTip(), "Selection of elements completed")
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.onOk", autospec=True
        ) as _f:
            bw.okAct.trigger()
            _f.assert_called_once_with(bw)

        self.assertIsInstance(bw.clearAct, QAction)
        self.assertEqual(bw.clearAct.text(), "&Clear selection")
        self.assertEqual(bw.clearAct.parent(), bw)
        self.assertEqual(
            images[2], bw.clearAct.icon().pixmap(images[2].size()).toImage()
        )
        self.assertEqual(
            bw.clearAct.statusTip(), "Discard the current selection and hide checkboxes"
        )
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.clearSelection", autospec=True
        ) as _f:
            bw.clearAct.trigger()
            _f.assert_called_once_with(bw)

        self.assertIsInstance(bw.selAllAct, QAction)
        self.assertEqual(bw.selAllAct.text(), "&Select all")
        self.assertEqual(bw.selAllAct.parent(), bw)
        self.assertEqual(
            images[3], bw.selAllAct.icon().pixmap(images[3].size()).toImage()
        )
        self.assertEqual(bw.selAllAct.statusTip(), "Select all the elements")
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.selectAll", autospec=True
        ) as _f:
            bw.selAllAct.trigger()
            _f.assert_called_once_with(bw)

        self.assertIsInstance(bw.unselAllAct, QAction)
        self.assertEqual(bw.unselAllAct.text(), "&Unselect all")
        self.assertEqual(bw.unselAllAct.parent(), bw)
        self.assertEqual(
            images[4], bw.unselAllAct.icon().pixmap(images[4].size()).toImage()
        )
        self.assertEqual(bw.unselAllAct.statusTip(), "Unselect all the elements")
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.unselectAll", autospec=True
        ) as _f:
            bw.unselAllAct.trigger()
            _f.assert_called_once_with(bw)

    def test_restoreSort(self):
        """test restoreSort"""
        bw = BibtexListWindow(bibs=[])
        cb = bw.columns.index("bibkey")
        cc = bw.proxyModel.sortColumn()
        co = bw.proxyModel.sortOrder()
        with patch(
            "PySide2.QtWidgets.QTableView.sortByColumn", autospec=True
        ) as _st, patch(
            "PySide2.QtCore.QSortFilterProxyModel.sort", autospec=True
        ) as _sf:
            bw.restoreSort()
            _sf.assert_has_calls([call(cb, Qt.AscendingOrder), call(cc, co)])
            _st.assert_has_calls([call(cb, Qt.AscendingOrder), call(cc, co)])

    def test_enableSelection(self):
        """test enableSelection"""
        bw = BibtexListWindow(bibs=[])
        with patch(
            "physbiblio.gui.bibWindows.BibTableModel.changeAsk", autospec=True
        ) as _a, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.changeEnableActions",
            autospec=True,
        ) as _e, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.restoreSort", autospec=True
        ) as _r:
            bw.enableSelection()
            _a.assert_called_once_with(bw.tableModel)
            _e.assert_called_once_with(bw)
            _r.assert_called_once_with(bw)

    def test_selectAll(self):
        """test selectAll"""
        bw = BibtexListWindow(bibs=[])
        with patch(
            "physbiblio.gui.bibWindows.BibTableModel.selectAll", autospec=True
        ) as _f:
            bw.selectAll()
            _f.assert_called_once_with(bw.tableModel)

    def test_unselectAll(self):
        """test unselectAll"""
        bw = BibtexListWindow(bibs=[])
        with patch(
            "physbiblio.gui.bibWindows.BibTableModel.unselectAll", autospec=True
        ) as _f:
            bw.unselectAll()
            _f.assert_called_once_with(bw.tableModel)

    def test_onOk(self):
        """test onOk"""
        bw = BibtexListWindow(parent=self.mainW, bibs=[])
        self.assertFalse(hasattr(self.mainW, "selectedBibs"))
        bw.tableModel.selectedElements = {"abc": False, "def": True, "ghi": True}
        tmp = MagicMock()
        tmp.exec_ = MagicMock()
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.clearSelection", autospec=True
        ) as _cl, patch(
            "physbiblio.gui.bibWindows.CommonBibActions", autospec=USE_AUTOSPEC_CLASS
        ) as _ci, patch(
            "physbiblio.database.Entries.getByBibkey",
            side_effect=[[{"bibkey": "def"}], [{"bibkey": "ghi"}]],
            autospec=True,
        ) as _g:
            bw.onOk()
            _cl.assert_called_once_with(bw)
            _g.assert_has_calls(
                [
                    call(pBDB.bibs, "def", saveQuery=False),
                    call(pBDB.bibs, "ghi", saveQuery=False),
                ]
            )
            _ci.assert_called_once_with(
                [{"bibkey": "def"}, {"bibkey": "ghi"}], self.mainW
            )
            self.assertEqual(self.mainW.selectedBibs, ["def", "ghi"])
        bw.tableModel.selectedElements = {"abc": False, "def": False, "ghi": False}
        cba = CommonBibActions([{"bibkey": "def"}], self.mainW)
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.clearSelection", autospec=True
        ) as _cl, patch(
            "physbiblio.gui.bibWindows.CommonBibActions.createContextMenu",
            return_value=tmp,
            autospec=True,
        ) as _cm, patch(
            "physbiblio.gui.bibWindows.CommonBibActions",
            return_value=cba,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _ci, patch(
            "physbiblio.database.Entries.getByBibkey", side_effect=[], autospec=True
        ) as _g:
            position = QCursor.pos()
            bw.onOk()
            _cl.assert_called_once_with(bw)
            _cm.assert_called_once_with(cba, selection=True)
            _g.assert_not_called()
            tmp.exec_.assert_called_once_with(position)
            self.assertEqual(self.mainW.selectedBibs, [])

    @patch.dict(
        pbConfig.params,
        {
            "bibtexListColumns": [
                "bibkey",
                "author",
                "title",
                "year",
                "firstdate",
                "pubdate",
                "doi",
                "arxiv",
                "isbn",
                "inspire",
            ]
        },
        clear=False,
    )
    def test_createTable(self):
        """test createTable"""
        bw = BibtexListWindow(parent=self.mainW, bibs=[{"bibkey": "abc"}])
        bw.cleanLayout()
        pBDB.bibs.lastQuery = "myquery"
        pBDB.bibs.lastVals = (1, 2, 3)
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.changeEnableActions",
            autospec=True,
        ) as _cea, patch(
            "physbiblio.gui.commonClasses.ObjListWindow.setProxyStuff", autospec=True
        ) as _sps, patch(
            "PySide2.QtWidgets.QTableView.hideColumn", autospec=True
        ) as _hc, patch(
            "physbiblio.gui.bibWindows.BibTableModel", autospec=USE_AUTOSPEC_CLASS
        ) as _tm, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.finalizeTable", autospec=True
        ) as _ft:
            bw.createTable()
            _tm.assert_called_once_with(
                bw,
                bw.bibs,
                bw.columns + bw.additionalCols,
                bw.columns,
                bw.additionalCols,
                askBibs=bw.askBibs,
                mainWin=bw.mainWin,
                previous=bw.previous,
            )
            _cea.assert_called_once_with(bw)
            _sps.assert_called_once_with(
                bw, bw.columns.index("firstdate"), Qt.DescendingOrder
            )
            _hc.assert_called_once_with(len(bw.columns) + len(bw.additionalCols))
            _ft.assert_called_once_with(bw)
        # check mylabel in widget 0
        self.assertIsInstance(bw.lastLabel, PBLabel)
        self.assertEqual(bw.currLayout.itemAt(0).widget(), bw.lastLabel)
        self.assertEqual(
            bw.lastLabel.text(),
            "Last query to bibtex database: \tmyquery\t\t - arguments:\t(1, 2, 3)",
        )
        self.assertIsInstance(bw.mergeLabel, PBLabel)
        self.assertEqual(
            bw.mergeLabel.text(), "(Select exactly two entries to enable merging them)"
        )
        # check toolbar content
        self.assertIsInstance(bw.selectToolBar, QToolBar)
        self.assertEqual(bw.selectToolBar.windowTitle(), "Bibs toolbar")
        self.assertEqual(bw.currLayout.itemAt(1).widget(), bw.selectToolBar)
        macts = bw.selectToolBar.actions()
        self.assertEqual(macts[0], bw.selAct)
        self.assertEqual(macts[1], bw.clearAct)
        self.assertTrue(macts[2].isSeparator())
        self.assertEqual(macts[3], bw.selAllAct)
        self.assertEqual(macts[4], bw.unselAllAct)
        self.assertEqual(macts[5], bw.okAct)
        self.assertEqual(bw.selectToolBar.widgetForAction(macts[6]), bw.mergeLabel)
        self.assertTrue(macts[7].isSeparator())
        self.assertEqual(bw.selectToolBar.widgetForAction(macts[8]), bw.filterInput)
        # check filterinput
        self.assertIsInstance(bw.filterInput, QLineEdit)
        self.assertEqual(bw.filterInput.placeholderText(), "Filter bibliography")
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.changeFilterSort", autospec=True
        ) as _cf:
            bw.filterInput.textChanged.emit("abc")
            _cf.assert_called_once_with(bw, "abc")
        bw.bibs = None
        with patch(
            "physbiblio.database.Entries.getAll",
            return_value=[{"bibkey": "xyz"}],
            autospec=True,
        ) as _ga:
            bw.createTable()
            _ga.assert_called_once_with(
                pBDB.bibs,
                orderType="DESC",
                limitTo=pbConfig.params["defaultLimitBibtexs"],
            )
        # check if firstdate is missing
        with patch.dict(
            pbConfig.params,
            {
                "bibtexListColumns": [
                    "bibkey",
                    "author",
                    "title",
                    "year",
                    "pubdate",
                    "doi",
                    "arxiv",
                    "isbn",
                    "inspire",
                ]
            },
            clear=False,
        ):
            bw = BibtexListWindow(parent=self.mainW, bibs=[{"bibkey": "abc"}])
            with patch(
                "physbiblio.gui.bibWindows.BibtexListWindow.changeEnableActions",
                autospec=True,
            ) as _cea, patch(
                "physbiblio.gui.commonClasses.ObjListWindow.setProxyStuff",
                autospec=True,
            ) as _sps, patch(
                "PySide2.QtWidgets.QTableView.hideColumn", autospec=True
            ) as _hc, patch(
                "physbiblio.gui.bibWindows.BibTableModel", autospec=USE_AUTOSPEC_CLASS
            ) as _tm, patch(
                "physbiblio.gui.bibWindows.BibtexListWindow.finalizeTable",
                autospec=True,
            ) as _ft:
                bw.createTable()
                _sps.assert_called_once_with(
                    bw, bw.columns.index("bibkey"), Qt.AscendingOrder
                )

        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.onSelectionChanged",
            autospec=True,
        ) as _sc:
            self.assertTrue(_sc.call_count == 0)
            bw.tableview.selectionModel().selectionChanged.emit("a", "b")
            self.assertTrue(_sc.call_count > 0)

    def test_updateInfo(self):
        """test updateInfo"""
        bw = BibtexListWindow(parent=self.mainW, bibs=[])
        self.assertEqual(bw.currentAbstractKey, None)
        with patch("PySide2.QtWidgets.QTextEdit.setText", autospec=True) as _st, patch(
            "physbiblio.gui.bibWindows.writeAbstract", autospec=True
        ) as _wa, patch(
            "physbiblio.gui.bibWindows.writeBibtexInfo",
            return_value="info",
            autospec=True,
        ) as _wb:
            bw.updateInfo({"bibkey": "abc", "bibtex": "text"})
            _wb.assert_called_once_with({"bibkey": "abc", "bibtex": "text"})
            _st.assert_has_calls([call("text"), call("info")])
            _wa.assert_called_once_with(self.mainW, {"bibkey": "abc", "bibtex": "text"})
            self.assertEqual(bw.currentAbstractKey, "abc")
        with patch("PySide2.QtWidgets.QTextEdit.setText", autospec=True) as _st, patch(
            "physbiblio.gui.bibWindows.writeAbstract", autospec=True
        ) as _wa, patch(
            "physbiblio.gui.bibWindows.writeBibtexInfo",
            return_value="info",
            autospec=True,
        ) as _wb:
            bw.updateInfo({"bibkey": "abc", "bibtex": "text"})
            _wb.assert_called_once_with({"bibkey": "abc", "bibtex": "text"})
            _st.assert_has_calls([call("text"), call("info")])
            _wa.assert_not_called()
            self.assertEqual(bw.currentAbstractKey, "abc")
            bw.updateInfo({"bibkey": "def", "bibtex": "text"})
            _wa.assert_called_once_with(self.mainW, {"bibkey": "def", "bibtex": "text"})
            self.assertEqual(bw.currentAbstractKey, "def")

    @patch.dict(pbConfig.params, {"bibtexListColumns": ["bibkey"]}, clear=False)
    def test_getEventEntry(self):
        """test getEventEntry"""
        bw = BibtexListWindow(
            bibs=[{"bibkey": "abc"}, {"bibkey": "def"}, {"bibkey": ""}]
        )
        with patch(
            "physbiblio.database.Entries.getByBibkey",
            side_effect=[["Rabc"], ["Rabc"], ["Rdef"], []],
            autospec=True,
        ) as _gbb, patch("logging.Logger.debug") as _d:
            self.assertEqual(
                bw.getEventEntry(bw.proxyModel.index(1, 0)), (1, 0, "abc", "Rabc")
            )
            self.assertEqual(
                bw.getEventEntry(bw.proxyModel.index(1, 3)), (1, 3, "abc", "Rabc")
            )
            self.assertEqual(
                bw.getEventEntry(bw.proxyModel.index(2, 0)), (2, 0, "def", "Rdef")
            )
            # will fail because of no DB correspondence:
            self.assertEqual(bw.getEventEntry(bw.proxyModel.index(2, 0)), None)
            _d.assert_called_once_with("The entry cannot be found!")
            _gbb.reset_mock()
            self.assertEqual(bw.getEventEntry(bw.proxyModel.index(0, 0)), None)
            _gbb.assert_not_called()
            self.assertEqual(bw.getEventEntry(bw.proxyModel.index(12, 0)), None)
            _gbb.assert_not_called()

    @patch.dict(pbConfig.params, {"bibtexListColumns": ["bibkey"]}, clear=False)
    def test_keyPressEvent(self):
        """test keyPressEvent"""
        bw = BibtexListWindow(
            bibs=[{"bibkey": "abc"}, {"bibkey": "def"}, {"bibkey": "ghi"}],
            parent=self.mainW,
        )
        m = PBMenu()
        m.exec_ = MagicMock()
        cba = CommonBibActions([{"bibkey": "ghi"}])
        m.possibleActions = [["copy", ["a", "b"]]]
        with patch(
            "physbiblio.gui.bibWindows.CommonBibActions._createMenuCopy", autospec=True
        ) as _cmc, patch(
            "physbiblio.gui.bibWindows.CommonBibActions",
            return_value=cba,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _cba, patch(
            "physbiblio.database.Entries.getByBibkey",
            side_effect=[[{"bibkey": "ghi"}], [{"bibkey": "ghi"}]],
            autospec=True,
        ) as _gbb, patch(
            "physbiblio.gui.bibWindows.PBMenu",
            return_value=m,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _pbm, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.clearSelection", autospec=True
        ) as _cs:
            QTest.keyPress(bw, "C", Qt.ShiftModifier)
            _cmc.assert_not_called()
            QTest.keyPress(bw, "C", Qt.ControlModifier)
            _cmc.assert_not_called()
            bw.tableview.selectRow(2)
            QTest.keyPress(bw, "C", Qt.ShiftModifier)
            _cmc.assert_not_called()
            QTest.keyPress(bw, "C", Qt.ControlModifier)
            _pbm.assert_called_once_with()
            _cmc.assert_called_once_with(cba, False, {"bibkey": "ghi"})
            cba.menu.exec_.assert_called_once_with(QCursor.pos())
            _cs.assert_called_once_with(bw)
        with patch(
            "physbiblio.gui.mainWindow.MainWindow.keyPressEvent", autospec=True
        ) as _p:
            QTest.keyClick(bw, "W", Qt.ShiftModifier)
            _p.assert_called()
        m = PBMenu()
        m.exec_ = MagicMock()
        cba = CommonBibActions([{"bibkey": "ghi", "bibtex": "@a{ghi}"}])
        with patch(
            "physbiblio.database.Entries.getByBibkey",
            side_effect=[
                [{"bibkey": "ghi", "bibtex": "@a{ghi}"}],
                [{"bibkey": "ghi", "bibtex": "@a{ghi}"}],
            ],
            autospec=True,
        ) as _gbb, patch(
            "physbiblio.gui.bibWindows.CommonBibActions",
            return_value=cba,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _cba, patch(
            "physbiblio.gui.bibWindows.PBMenu",
            return_value=m,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _pbm, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.clearSelection", autospec=True
        ) as _cs:
            QTest.keyPress(bw, "C", Qt.ControlModifier)
            _pbm.assert_called_once_with()
            cba.menu.exec_.assert_called_once_with(QCursor.pos())
            _cs.assert_called_once_with(bw)
        pa = m.possibleActions
        self.assertIsInstance(pa, list)
        for ix in [0, 2, 3, 4]:
            self.assertIsInstance(pa[ix], QAction)
        self.assertEqual(pa[1], None)
        self.assertEqual(pa[0].text(), "--Copy to clipboard--")
        self.assertFalse(pa[0].isEnabled())
        self.assertEqual(pa[2].text(), "key(s)")
        self.assertEqual(pa[3].text(), r"\cite{key(s)}")
        self.assertEqual(pa[4].text(), "bibtex(s)")
        with patch("logging.Logger.info") as _i:
            pa[2].trigger()
            self.assertEqual(QApplication.clipboard().text(), "ghi")
            pa[3].trigger()
            self.assertEqual(QApplication.clipboard().text(), r"\cite{ghi}")
            pa[4].trigger()
            self.assertEqual(QApplication.clipboard().text(), "@a{ghi}")

    def test_triggeredContextMenuEvent(self):
        """test triggeredContextMenuEvent"""
        bw = BibtexListWindow(
            parent=self.mainW, bibs=[{"bibtex": "text", "bibkey": "abc", "marks": ""}]
        )
        position = QCursor.pos()
        ev = QMouseEvent(
            QEvent.MouseButtonPress,
            position,
            Qt.RightButton,
            Qt.NoButton,
            Qt.NoModifier,
        )
        with patch(
            "PySide2.QtCore.QSortFilterProxyModel.index",
            return_value="index",
            autospec=True,
        ) as _ix, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=None,
            autospec=True,
        ) as _ge, patch(
            "logging.Logger.warning"
        ) as _w:
            self.assertEqual(bw.triggeredContextMenuEvent(9999, 101, ev), None)
            _w.assert_called_once_with("The index is not valid!")
            _ix.assert_called_once_with(9999, 101)
            _ge.assert_called_once_with(bw, "index")
        with patch(
            "PySide2.QtCore.QSortFilterProxyModel.index",
            return_value="index",
            autospec=True,
        ) as _ix, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=(0, 0, "abc", {"bibkey": "abc"}),
            autospec=True,
        ) as _ge, patch(
            "logging.Logger.warning"
        ) as _w:
            with patch(
                "physbiblio.gui.bibWindows.CommonBibActions",
                autospec=USE_AUTOSPEC_CLASS,
            ) as _ci:
                self.assertEqual(bw.triggeredContextMenuEvent(9999, 101, ev), None)
                _ci.assert_called_once_with([{"bibkey": "abc"}], self.mainW)
            _w.assert_not_called()
            _ix.assert_called_once_with(9999, 101)
            _ge.assert_called_once_with(bw, "index")
            cba = CommonBibActions([{"bibkey": "abc"}], self.mainW)
            with patch(
                "physbiblio.gui.bibWindows.CommonBibActions.createContextMenu",
                autospec=True,
            ) as _cm, patch(
                "physbiblio.gui.bibWindows.CommonBibActions",
                return_value=cba,
                autospec=USE_AUTOSPEC_CLASS,
            ) as _cba:
                self.assertEqual(bw.triggeredContextMenuEvent(9999, 101, ev), None)
                _cm.assert_called_once_with(cba)
            tmp = MagicMock()
            tmp.exec_ = MagicMock()
            with patch(
                "physbiblio.gui.bibWindows.CommonBibActions.createContextMenu",
                return_value=tmp,
                autospec=True,
            ) as _cm, patch(
                "physbiblio.gui.bibWindows.CommonBibActions",
                return_value=cba,
                autospec=USE_AUTOSPEC_CLASS,
            ) as _cba:
                bw.triggeredContextMenuEvent(9999, 101, ev)
                tmp.exec_.assert_called_once_with(position)
                _cm.assert_called_once_with(cba)

    def test_handleItemEntered(self):
        """test handleItemEntered"""
        bw = BibtexListWindow(bibs=[])
        self.assertEqual(bw.handleItemEntered(QModelIndex()), None)

    def test_cellClick(self):
        """test cellClick"""
        bw = BibtexListWindow(parent=self.mainW, bibs=[])
        ix = QModelIndex()
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=None,
            autospec=True,
        ) as _ge, patch("logging.Logger.warning") as _w:
            self.assertEqual(bw.cellClick(ix), None)
            _w.assert_called_once_with("The index is not valid!")
            _ge.assert_called_once_with(bw, ix)
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=(0, 0, "abc", {"bibkey": "abc"}),
            autospec=True,
        ) as _ge, patch("logging.Logger.warning") as _w, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.updateInfo", autospec=True
        ) as _ui:
            self.assertEqual(bw.cellClick(ix), None)
            _ui.assert_called_once_with(bw, {"bibkey": "abc"})
            _ge.assert_called_once_with(bw, ix)

    def test_cellDoubleClick(self):
        """test cellDoubleClick"""
        defcols = pbConfig.params["bibtexListColumns"]
        defcols.append("ads")
        with patch.dict(pbConfig.params, {"bibtexListColumns": defcols}, clear=False):
            bw = BibtexListWindow(
                parent=self.mainW, bibs=[{"bibtex": "text", "bibkey": "abc"}]
            )
        ix = QModelIndex()
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=None,
            autospec=True,
        ) as _ge, patch("logging.Logger.warning") as _w:
            self.assertEqual(bw.cellDoubleClick(ix), None)
            _w.assert_called_once_with("The index is not valid!")

        currentry = {
            "bibkey": "abc",
            "ads": "abc...123",
            "doi": "1/2/3",
            "arxiv": "1234.56789",
            "inspire": "9876543",
        }
        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=(0, bw.colContents.index("doi"), "abc", currentry),
            autospec=True,
        ) as _ge, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.updateInfo", autospec=True
        ) as _ui:
            bw.cellDoubleClick(ix)
            _ge.assert_called_once_with(bw, ix)
            _ui.assert_called_once_with(bw, currentry)
            _ol.assert_called_once_with(pBGuiView, "abc", "doi")
        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=(0, bw.colContents.index("ads"), "abc", currentry),
            autospec=True,
        ) as _ge, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.updateInfo", autospec=True
        ) as _ui:
            bw.cellDoubleClick(ix)
            _ge.assert_called_once_with(bw, ix)
            _ui.assert_called_once_with(bw, currentry)
            _ol.assert_called_once_with(pBGuiView, "abc", "ads")
        currentry["doi"] = ""
        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=(0, bw.colContents.index("doi"), "abc", currentry),
            autospec=True,
        ) as _ge, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.updateInfo", autospec=True
        ) as _ui:
            bw.cellDoubleClick(ix)
            _ol.assert_not_called()
        currentry["doi"] = None
        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=(0, bw.colContents.index("doi"), "abc", currentry),
            autospec=True,
        ) as _ge, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.updateInfo", autospec=True
        ) as _ui:
            bw.cellDoubleClick(ix)
            _ol.assert_not_called()

        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=(0, bw.colContents.index("arxiv"), "abc", currentry),
            autospec=True,
        ) as _ge, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.updateInfo", autospec=True
        ) as _ui:
            bw.cellDoubleClick(ix)
            _ge.assert_called_once_with(bw, ix)
            _ui.assert_called_once_with(bw, currentry)
            _ol.assert_called_once_with(pBGuiView, "abc", "arxiv")
        currentry["arxiv"] = ""
        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=(0, bw.colContents.index("arxiv"), "abc", currentry),
            autospec=True,
        ) as _ge, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.updateInfo", autospec=True
        ) as _ui:
            bw.cellDoubleClick(ix)
            _ol.assert_not_called()
        currentry["arxiv"] = None
        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=(0, bw.colContents.index("arxiv"), "abc", currentry),
            autospec=True,
        ) as _ge, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.updateInfo", autospec=True
        ) as _ui:
            bw.cellDoubleClick(ix)
            _ol.assert_not_called()

        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=(0, bw.colContents.index("inspire"), "abc", currentry),
            autospec=True,
        ) as _ge, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.updateInfo", autospec=True
        ) as _ui:
            bw.cellDoubleClick(ix)
            _ge.assert_called_once_with(bw, ix)
            _ui.assert_called_once_with(bw, currentry)
            _ol.assert_called_once_with(pBGuiView, "abc", "inspire")
        currentry["inspire"] = ""
        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=(0, bw.colContents.index("inspire"), "abc", currentry),
            autospec=True,
        ) as _ge, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.updateInfo", autospec=True
        ) as _ui:
            bw.cellDoubleClick(ix)
            _ol.assert_not_called()
        currentry["inspire"] = None
        with patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=(0, bw.colContents.index("inspire"), "abc", currentry),
            autospec=True,
        ) as _ge, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.updateInfo", autospec=True
        ) as _ui:
            bw.cellDoubleClick(ix)
            _ol.assert_not_called()

        with patch(
            "physbiblio.pdf.LocalPDF.getExisting",
            return_value=["/tmp/file.pdf"],
            autospec=True,
        ) as _gf, patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=(0, bw.colContents.index("pdf"), "abc", currentry),
            autospec=True,
        ) as _ge, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.updateInfo", autospec=True
        ) as _ui, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m:
            bw.cellDoubleClick(ix)
            _gf.assert_called_once_with(pBPDF, "abc", fullPath=True)
            _ol.assert_called_once_with(
                pBGuiView, "abc", "file", fileArg="/tmp/file.pdf"
            )
            _m.assert_called_once_with(self.mainW, "opening PDF...")

        tmp = MagicMock()
        tmp.exec_ = MagicMock()
        with patch(
            "physbiblio.pdf.LocalPDF.getExisting",
            return_value=["/tmp/file1.pdf", "/tmp/file2.pdf"],
            autospec=True,
        ) as _gf, patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.getEventEntry",
            return_value=(0, bw.colContents.index("pdf"), "abc", currentry),
            autospec=True,
        ) as _ge, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.updateInfo", autospec=True
        ) as _ui, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m, patch(
            "physbiblio.gui.bibWindows.AskPDFAction",
            return_value=tmp,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _apa:
            position = QCursor.pos()
            bw.cellDoubleClick(ix)
            _gf.assert_called_once_with(pBPDF, "abc", fullPath=True)
            _ol.assert_not_called()
            _m.assert_not_called()
            _apa.assert_called_once_with("abc", bw.mainWin)
            tmp.exec_.assert_called_once_with(position)

    def test_finalizeTable(self):
        """test finalizeTable"""
        bw = BibtexListWindow(bibs=[])
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.cellClick", autospec=True
        ) as _f:
            bw.tableview.clicked.emit(QModelIndex())
            self.assertEqual(_f.call_count, 1)
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.cellDoubleClick", autospec=True
        ) as _f:
            bw.tableview.doubleClicked.emit(QModelIndex())
            self.assertEqual(_f.call_count, 1)
        bw.cleanLayout()

        with patch("PySide2.QtGui.QFont.setPointSize", autospec=True) as _sps, patch(
            "PySide2.QtWidgets.QTableView.resizeColumnsToContents", autospec=True
        ) as _rc, patch(
            "PySide2.QtWidgets.QTableView.resizeRowsToContents", autospec=True
        ) as _rr, patch.dict(
            pbConfig.params, {"resizeTable": True}, clear=False
        ):
            bw.finalizeTable()
            _rc.assert_called_once_with()
            _rr.assert_called_once_with()
            _sps.assert_called_once_with(pbConfig.params["bibListFontSize"])
            self.assertEqual(bw.currLayout.itemAt(0).widget(), bw.tableview)
        bw.cleanLayout()
        with patch(
            "PySide2.QtWidgets.QTableView.resizeColumnsToContents", autospec=True
        ) as _rc, patch(
            "PySide2.QtWidgets.QTableView.resizeColumnToContents", autospec=True
        ) as _rsc, patch(
            "PySide2.QtWidgets.QTableView.resizeRowsToContents", autospec=True
        ) as _rr, patch.dict(
            pbConfig.params, {"resizeTable": False}, clear=False
        ):
            bw.finalizeTable()
            _rc.assert_not_called()
            _rr.assert_not_called()
            for f in ["author", "title", "comments"]:
                if f in bw.colContents:
                    _rsc.assert_any_call(bw.colContents.index(f))

    def test_recreateTable(self):
        """test recreateTable"""
        bw = BibtexListWindow(bibs=[])
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.cleanLayout", autospec=True
        ) as _cl, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.createTable", autospec=True
        ) as _ct, patch(
            "PySide2.QtWidgets.QApplication.setOverrideCursor", autospec=True
        ) as _sc, patch(
            "PySide2.QtWidgets.QApplication.restoreOverrideCursor", autospec=True
        ) as _rc, patch(
            "physbiblio.database.Entries.getAll", autospec=True
        ) as _ga:
            bw.recreateTable(bibs="bibs")
            _ga.assert_not_called()
            _cl.assert_called_once_with(bw)
            _ct.assert_called_once_with(bw)
            _rc.assert_called_once_with()
            _sc.assert_called_once_with(Qt.WaitCursor)
            self.assertEqual(bw.bibs, "bibs")
        with patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.cleanLayout", autospec=True
        ) as _cl, patch(
            "physbiblio.gui.bibWindows.BibtexListWindow.createTable", autospec=True
        ) as _ct, patch(
            "PySide2.QtWidgets.QApplication.setOverrideCursor", autospec=True
        ) as _sc, patch(
            "PySide2.QtWidgets.QApplication.restoreOverrideCursor", autospec=True
        ) as _rc, patch(
            "physbiblio.database.Entries.getAll", return_value="getall", autospec=True
        ) as _ga:
            bw.recreateTable()
            _ga.assert_called_once_with(
                pBDB.bibs,
                orderType="DESC",
                limitTo=pbConfig.params["defaultLimitBibtexs"],
            )
            _cl.assert_called_once_with(bw)
            _ct.assert_called_once_with(bw)
            _rc.assert_called_once_with()
            _sc.assert_called_once_with(Qt.WaitCursor)
            self.assertEqual(bw.bibs, "getall")


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestEditBibtexDialog(GUITestCase):
    """test the EditBibtexDialog class"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        with patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog.createForm", autospec=True
        ) as _cf:
            eb = EditBibtexDialog()
            _cf.assert_called_once_with(eb)
        self.assertIsInstance(eb, EditObjectWindow)
        self.assertEqual(eb.parent(), None)
        self.assertEqual(eb.checkValues, {})
        self.assertEqual(eb.markValues, {})
        self.assertEqual(
            eb.checkboxes,
            [
                "exp_paper",
                "lecture",
                "phd_thesis",
                "review",
                "proceeding",
                "book",
                "noUpdate",
            ],
        )
        tmp = {}
        for k in pBDB.tableCols["entries"]:
            if k != "citations" and k != "citations_no_self":
                self.assertEqual(eb.data[k], "")
                tmp[k] = "a"
        self.assertEqual(eb.citations, 0)
        self.assertEqual(eb.citations_no_self, 0)

        tmp["citations"] = 123
        tmp["citations_no_self"] = 111
        with patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog.createForm", autospec=True
        ) as _cf:
            eb = EditBibtexDialog(parent=p, bib=tmp)
        self.assertEqual(eb.parent(), p)
        self.assertEqual(eb.data, tmp)
        self.assertEqual(eb.citations, 123)
        self.assertEqual(eb.citations_no_self, 111)

    def test_onOk(self):
        """test onOk"""
        p = QWidget()
        eb = EditBibtexDialog()
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c, patch(
            "logging.Logger.error"
        ) as _e:
            self.assertEqual(eb.onOk(), False)
            _c.assert_not_called()
            _e.assert_called_once_with("Invalid form contents: empty bibtex!")
        eb.textValues["bibtex"].setPlainText('@article{abc, title="}')
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c, patch(
            "logging.Logger.error"
        ) as _e:
            self.assertEqual(eb.onOk(), False)
            _c.assert_not_called()
            _e.assert_called_once_with(
                "Invalid form contents: cannot read bibtex properly!"
            )
        eb.textValues["bibtex"].setPlainText('@article{abc, title="ABC"}')
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c, patch(
            "logging.Logger.error"
        ) as _e:
            eb.onOk()
            _c.assert_called_once_with()
            _e.assert_not_called()
            self.assertEqual(eb.result, True)

        eb = EditBibtexDialog()
        eb.textValues["bibtex"].setPlainText('@article{abc, title="ABC"}')
        eb.textValues["bibkey"].setReadOnly(False)
        eb.textValues["bibkey"].setText("abc")
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c, patch(
            "logging.Logger.error"
        ) as _e:
            self.assertEqual(eb.onOk(), False)
            _c.assert_not_called()
            _e.assert_called_once_with(
                "Invalid form contents: bibtex key will be taken from bibtex!"
            )

    def test_updateBibkey(self):
        """test updateBibkey"""
        p = QWidget()
        eb = EditBibtexDialog()
        eb.textValues["bibtex"].setPlainText('@article{abc, title="ABC"}')
        eb.textValues["bibkey"].setText("")
        eb.updateBibkey()
        self.assertEqual(eb.textValues["bibkey"].text(), "abc")
        eb.textValues["bibtex"].setPlainText('@article{abc, title="ABC"')
        eb.updateBibkey()
        self.assertEqual(eb.textValues["bibkey"].text(), "not valid bibtex!")
        eb.textValues["bibkey"].setText("")
        eb.textValues["bibtex"].setPlainText('@article{abc, author= title="ABC"}')
        eb.updateBibkey()
        self.assertEqual(eb.textValues["bibkey"].text(), "not valid bibtex!")

    def test_createField(self):
        """test createField"""
        eb = EditBibtexDialog()
        # clean layout
        while True:
            o = eb.layout().takeAt(0)
            if o is None:
                break
            o.widget().deleteLater()
        self.assertEqual(eb.createField("bibdict", 10), 10)
        self.assertEqual(eb.createField("abstract", 10), 10)
        self.assertEqual(eb.createField("bibtex", 10), 10)
        for k in eb.checkboxes:
            self.assertEqual(eb.createField(k, 10), 10)
        self.assertEqual(eb.createField("bibkey", 0), 1)
        self.assertEqual(eb.createField("inspire", 5), 6)
        self.assertEqual(eb.createField("marks", 11), 13)
        self.assertEqual(eb.createField("marks", 20), 21)
        self.assertIsInstance(eb.currGrid.itemAtPosition(2, 0).widget(), QLineEdit)
        self.assertEqual(
            eb.textValues["bibkey"], eb.currGrid.itemAtPosition(2, 0).widget()
        )
        self.assertEqual(eb.textValues["bibkey"].text(), "")
        self.assertEqual(eb.textValues["bibkey"].isReadOnly(), True)
        self.assertIsInstance(eb.currGrid.itemAtPosition(1, 0).widget(), PBLabel)
        self.assertEqual(eb.currGrid.itemAtPosition(1, 0).widget().text(), "bibkey")
        self.assertIsInstance(eb.currGrid.itemAtPosition(1, 1).widget(), PBLabel)
        self.assertEqual(
            eb.currGrid.itemAtPosition(1, 1).widget().text(),
            "(%s)" % pBDB.descriptions["entries"]["bibkey"],
        )

        self.assertIsInstance(eb.currGrid.itemAtPosition(6, 2).widget(), QLineEdit)
        self.assertEqual(
            eb.textValues["inspire"], eb.currGrid.itemAtPosition(6, 2).widget()
        )
        self.assertEqual(eb.textValues["inspire"].text(), "")
        self.assertEqual(eb.textValues["inspire"].isReadOnly(), False)
        self.assertIsInstance(eb.currGrid.itemAtPosition(5, 2).widget(), PBLabel)
        self.assertEqual(eb.currGrid.itemAtPosition(5, 2).widget().text(), "inspire")
        self.assertIsInstance(eb.currGrid.itemAtPosition(5, 3).widget(), PBLabel)
        self.assertEqual(
            eb.currGrid.itemAtPosition(5, 3).widget().text(),
            "(%s)" % pBDB.descriptions["entries"]["inspire"],
        )

        self.assertIsInstance(eb.currGrid.itemAtPosition(14, 0).widget(), QGroupBox)
        self.assertIsInstance(eb.markValues, dict)
        self.assertEqual(sorted(eb.markValues.keys()), sorted(pBMarks.marks.keys()))
        for m in pBMarks.marks.keys():
            self.assertIsInstance(eb.markValues[m], QCheckBox)
            self.assertEqual(eb.markValues[m].isChecked(), False)

        eb = EditBibtexDialog(
            bib={"bibkey": "abc", "inspire": "123", "marks": "new,bad"}
        )
        # clean layout
        while True:
            o = eb.layout().takeAt(0)
            if o is None:
                break
            o.widget().deleteLater()
        self.assertEqual(eb.createField("bibkey", 0), 1)
        self.assertEqual(eb.textValues["bibkey"].text(), "abc")
        self.assertEqual(eb.createField("inspire", 5), 6)
        self.assertEqual(eb.textValues["inspire"].text(), "123")
        self.assertEqual(eb.createField("marks", 10), 11)
        self.assertEqual(eb.markValues["bad"].isChecked(), True)
        self.assertEqual(eb.markValues["new"].isChecked(), True)

    def test_createCheckbox(self):
        """test createCheckbox"""
        eb = EditBibtexDialog()
        # clean layout
        while True:
            o = eb.layout().takeAt(0)
            if o is None:
                break
            o.widget().deleteLater()
        while True:
            o = eb.typeBox.layout().takeAt(0)
            if o is None:
                break
            o.widget().deleteLater()
        self.assertEqual(eb.currGrid.count(), 0)
        for ik, k in enumerate(eb.checkboxes):
            eb.createCheckbox(k)
            self.assertIsInstance(eb.typeBox.layout().itemAt(ik).widget(), QCheckBox)
            self.assertEqual(eb.checkValues[k], eb.typeBox.layout().itemAt(ik).widget())
            self.assertEqual(eb.checkValues[k].isChecked(), False)
            self.assertEqual(eb.checkValues[k].text(), k)
            self.assertEqual(
                eb.checkValues[k].toolTip(), pBDB.descriptions["entries"][k]
            )
        eb = EditBibtexDialog(bib={"book": 1, "review": 1})
        while True:
            o = eb.layout().takeAt(0)
            if o is None:
                break
            o.widget().deleteLater()
        while True:
            o = eb.typeBox.layout().takeAt(0)
            if o is None:
                break
            o.widget().deleteLater()
        for ik, k in enumerate(eb.checkboxes):
            eb.createCheckbox(k)
            self.assertIsInstance(eb.typeBox.layout().itemAt(ik).widget(), QCheckBox)
            self.assertEqual(eb.checkValues[k], eb.typeBox.layout().itemAt(ik).widget())
            self.assertEqual(eb.checkValues[k].text(), k)
            self.assertEqual(
                eb.checkValues[k].toolTip(), pBDB.descriptions["entries"][k]
            )
        self.assertEqual(eb.checkValues["book"].isChecked(), True)
        self.assertEqual(eb.checkValues["review"].isChecked(), True)

    def test_createForm(self):
        """test createForm"""
        with patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog.createField",
            side_effect=[i for i in range(1, 28)],
            autospec=True,
        ) as _cf, patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog.createCheckbox",
            side_effect=[i for i in range(1, 28)],
            autospec=True,
        ) as _cc, patch(
            "physbiblio.gui.commonClasses.EditObjectWindow.centerWindow", autospec=True
        ) as _cw:
            eb = EditBibtexDialog(bib={"bibtex": "@article", "comments": "sometext"})
            _cw.assert_called_once_with(eb)
            _cf.assert_has_calls(
                [
                    call(eb, "bibkey", 0),
                    call(eb, "inspire", 1),
                    call(eb, "arxiv", 2),
                    call(eb, "ads", 3),
                    call(eb, "scholar", 4),
                    call(eb, "doi", 5),
                    call(eb, "isbn", 6),
                    call(eb, "year", 7),
                    call(eb, "link", 8),
                    call(eb, "comments", 9),
                    call(eb, "old_keys", 10),
                    call(eb, "crossref", 11),
                    call(eb, "bibtex", 12),
                    call(eb, "firstdate", 13),
                    call(eb, "pubdate", 14),
                    call(eb, "exp_paper", 15),
                    call(eb, "lecture", 16),
                    call(eb, "phd_thesis", 17),
                    call(eb, "review", 18),
                    call(eb, "proceeding", 19),
                    call(eb, "book", 20),
                    call(eb, "noUpdate", 21),
                    call(eb, "marks", 22),
                    call(eb, "abstract", 23),
                    call(eb, "bibdict", 24),
                ]
            )
            _cc.assert_has_calls(
                [
                    call(eb, "bibkey"),
                    call(eb, "inspire"),
                    call(eb, "arxiv"),
                    call(eb, "ads"),
                    call(eb, "scholar"),
                    call(eb, "doi"),
                    call(eb, "isbn"),
                    call(eb, "year"),
                    call(eb, "link"),
                    call(eb, "comments"),
                    call(eb, "old_keys"),
                    call(eb, "crossref"),
                    call(eb, "bibtex"),
                    call(eb, "firstdate"),
                    call(eb, "pubdate"),
                    call(eb, "exp_paper"),
                    call(eb, "lecture"),
                    call(eb, "phd_thesis"),
                    call(eb, "review"),
                    call(eb, "proceeding"),
                    call(eb, "book"),
                    call(eb, "noUpdate"),
                    call(eb, "marks"),
                    call(eb, "abstract"),
                    call(eb, "bibdict"),
                ]
            )
        self.assertEqual(eb.windowTitle(), "Edit bibtex entry")
        self.assertIsInstance(eb.currGrid.itemAtPosition(28, 0).widget(), QGroupBox)
        self.assertEqual(eb.currGrid.itemAtPosition(28, 0).widget(), eb.typeBox)
        self.assertEqual(eb.typeBox.title(), "Entry type")
        self.assertIsInstance(eb.typeBox.layout(), QHBoxLayout)
        # comments
        self.assertIsInstance(eb.currGrid.itemAtPosition(29, 2).widget(), PBLabel)
        self.assertEqual(
            eb.currGrid.itemAtPosition(29, 2).widget().text(),
            pBDB.descriptions["entries"]["comments"],
        )
        self.assertIsInstance(
            eb.currGrid.itemAtPosition(30, 2).widget(), QPlainTextEdit
        )
        self.assertEqual(
            eb.textValues["comments"], eb.currGrid.itemAtPosition(30, 2).widget()
        )
        self.assertEqual(eb.textValues["comments"].toPlainText(), "sometext")
        # test bibtex field, connect and labels
        self.assertIsInstance(eb.currGrid.itemAtPosition(29, 0).widget(), PBLabel)
        self.assertEqual(
            eb.currGrid.itemAtPosition(29, 0).widget().text(),
            pBDB.descriptions["entries"]["bibtex"],
        )
        self.assertIsInstance(
            eb.currGrid.itemAtPosition(30, 0).widget(), QPlainTextEdit
        )
        self.assertEqual(
            eb.textValues["bibtex"], eb.currGrid.itemAtPosition(30, 0).widget()
        )
        self.assertEqual(eb.textValues["bibtex"].toPlainText(), "@article")
        with patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog.updateBibkey", autospec=True
        ) as _ub:
            eb.textValues["bibtex"].textChanged.emit()
            _ub.assert_called_once_with(eb)
        # test ok cancel buttons
        self.assertEqual(eb.layout().itemAtPosition(45, 0).widget(), eb.acceptButton)
        self.assertEqual(eb.acceptButton.text(), "OK")
        with patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog.onOk", autospec=True
        ) as _f:
            QTest.mouseClick(eb.acceptButton, Qt.LeftButton)
            _f.assert_called_once_with(eb)
        self.assertIsInstance(eb.layout().itemAtPosition(45, 2).widget(), QPushButton)
        self.assertEqual(eb.layout().itemAtPosition(45, 2).widget(), eb.cancelButton)
        self.assertEqual(eb.cancelButton.text(), "Cancel")
        self.assertTrue(eb.cancelButton.autoDefault())
        with patch(
            "physbiblio.gui.commonClasses.EditObjectWindow.onCancel", autospec=True
        ) as _f:
            QTest.mouseClick(eb.cancelButton, Qt.LeftButton)
            _f.assert_called_once_with(eb)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestAskPDFAction(GUIwMainWTestCase):
    """test AskPDFAction"""

    def test_init(self):
        """test __init__"""
        with patch(
            "physbiblio.pdf.LocalPDF.getExisting", return_value=[], autospec=True
        ) as _ge, patch(
            "physbiblio.pdf.LocalPDF.getFilePath", side_effect=["", ""], autospec=True
        ) as _gp, patch(
            "physbiblio.gui.commonClasses.PBMenu.fillMenu", autospec=True
        ) as _fm:
            apa = AskPDFAction("improbablekey", self.mainW)
            _ge.assert_called_once_with(pBPDF, "improbablekey", fullPath=True)
            _gp.assert_has_calls(
                [
                    call(pBPDF, "improbablekey", "doi"),
                    call(pBPDF, "improbablekey", "arxiv"),
                ]
            )
            _fm.assert_called_once_with(apa)
        self.assertEqual(
            apa.message, "What PDF of this entry (improbablekey) do you want to open?"
        )
        self.assertEqual(apa.possibleActions, [])

        with patch(
            "physbiblio.pdf.LocalPDF.getExisting",
            return_value=["a", "b", "d", "e"],
            autospec=True,
        ) as _ge, patch(
            "physbiblio.pdf.LocalPDF.getFilePath", side_effect=["d", "a"], autospec=True
        ) as _gp, patch(
            "physbiblio.gui.commonClasses.PBMenu.fillMenu", autospec=True
        ) as _fm:
            apa = AskPDFAction("improbablekey", self.mainW)
            _ge.assert_called_once_with(pBPDF, "improbablekey", fullPath=True)
            _gp.assert_has_calls(
                [
                    call(pBPDF, "improbablekey", "doi"),
                    call(pBPDF, "improbablekey", "arxiv"),
                ]
            )
            _fm.assert_called_once_with(apa)
        self.assertEqual(
            apa.message, "What PDF of this entry (improbablekey) do you want to open?"
        )
        self.assertIsInstance(apa.possibleActions, list)
        self.assertEqual(len(apa.possibleActions), 4)
        self.assertIsInstance(apa.possibleActions[0], QAction)
        self.assertIsInstance(apa.possibleActions[1], QAction)
        self.assertIsInstance(apa.possibleActions[2], QAction)
        self.assertIsInstance(apa.possibleActions[3], QAction)
        self.assertEqual(apa.possibleActions[0].text(), "Open DOI PDF")
        self.assertEqual(apa.possibleActions[1].text(), "Open arxiv PDF")
        self.assertEqual(apa.possibleActions[2].text(), "Open b")
        self.assertEqual(apa.possibleActions[3].text(), "Open e")
        with patch(
            "physbiblio.gui.bibWindows.AskPDFAction.onOpenDoi", autospec=True
        ) as _r:
            apa.possibleActions[0].triggered.emit()
            _r.assert_called_once_with(apa)
        with patch(
            "physbiblio.gui.bibWindows.AskPDFAction.onOpenArxiv", autospec=True
        ) as _r:
            apa.possibleActions[1].triggered.emit()
            _r.assert_called_once_with(apa)

    def test_onOpenArxiv(self):
        """test onOpenArxiv"""
        with patch("PySide2.QtWidgets.QMenu.close", autospec=True) as _c, patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch(
            "physbiblio.pdf.LocalPDF.getFilePath",
            return_value="/tmp/file.pdf",
            autospec=True,
        ) as _gp, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m, patch(
            "logging.Logger.warning"
        ) as _w:
            apa = AskPDFAction("improbablekey", self.mainW)
            apa.onOpenArxiv()
            _ol.assert_called_once_with(
                pBGuiView, "improbablekey", "file", fileArg="/tmp/file.pdf"
            )
            _c.assert_called_once_with()
            _m.assert_called_once_with(self.mainW, "Opening arXiv PDF...")
            _gp.assert_has_calls(
                [
                    call(pBPDF, "improbablekey", "doi"),
                    call(pBPDF, "improbablekey", "arxiv"),
                    call(pBPDF, "improbablekey", "arxiv"),
                ]
            )

    def test_onOpenDoi(self):
        """test onOpenDoi"""
        with patch("PySide2.QtWidgets.QMenu.close", autospec=True) as _c, patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch(
            "physbiblio.pdf.LocalPDF.getFilePath",
            return_value="/tmp/file.pdf",
            autospec=True,
        ) as _gp, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m, patch(
            "logging.Logger.warning"
        ) as _w:
            apa = AskPDFAction("improbablekey", self.mainW)
            apa.onOpenDoi()
            _ol.assert_called_once_with(
                pBGuiView, "improbablekey", "file", fileArg="/tmp/file.pdf"
            )
            _c.assert_called_once_with()
            _m.assert_called_once_with(self.mainW, "Opening DOI PDF...")
            _gp.assert_has_calls(
                [
                    call(pBPDF, "improbablekey", "doi"),
                    call(pBPDF, "improbablekey", "arxiv"),
                    call(pBPDF, "improbablekey", "doi"),
                ]
            )

    def test_onOpenOther(self):
        """test onOpenOther"""
        with patch(
            "physbiblio.pdf.LocalPDF.getExisting",
            return_value=["a.pdf", "b.pdf"],
            autospec=True,
        ) as _ge, patch(
            "physbiblio.pdf.LocalPDF.getFilePath", side_effect=["c", "d"], autospec=True
        ) as _gp, patch(
            "physbiblio.pdf.LocalPDF.getFileDir", return_value="/tmp", autospec=True
        ) as _gd, patch(
            "physbiblio.gui.commonClasses.GUIViewEntry.openLink", autospec=True
        ) as _ol, patch(
            "physbiblio.gui.mainWindow.MainWindow.statusBarMessage", autospec=True
        ) as _m, patch(
            "PySide2.QtWidgets.QMenu.close", autospec=True
        ) as _c, patch(
            "logging.Logger.warning"
        ) as _w:
            apa = AskPDFAction("improbablekey", self.mainW)
            apa.possibleActions[0].trigger()
            _ol.assert_called_once_with(
                pBGuiView, "improbablekey", "file", fileArg="/tmp/a.pdf"
            )
            _gd.assert_called_once_with(pBPDF, "improbablekey")
            _c.assert_called_once_with()
            _m.assert_called_once_with(self.mainW, "Opening a.pdf...")


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestSearchBibsWindow(GUITestCase):
    """test the SearchBibsWindow class"""

    def test_init(self):
        """test __init__"""
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf, patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.processHistoric",
            side_effect=["a", "b"],
            autospec=True,
        ) as _ph, patch(
            "physbiblio.config.GlobalDB.getSearchList",
            return_value=["abc", "def"],
            autospec=True,
        ) as _sl:
            sbw = SearchBibsWindow()
            _cf.assert_called_once_with(sbw)
            _ph.assert_has_calls([call(sbw, "abc"), call(sbw, "def")])
            _sl.assert_called_once_with(
                pbConfig.globalDb, manual=False, replacement=False
            )
        self.assertEqual(sbw.textValues, [])
        self.assertFalse(sbw.result)
        self.assertFalse(sbw.save)
        self.assertFalse(sbw.replace)
        self.assertEqual(sbw.edit, None)
        self.assertEqual(
            sbw.historic,
            [
                {
                    "nrows": 1,
                    "searchValues": [
                        {
                            "logical": None,
                            "field": None,
                            "type": "Text",
                            "operator": None,
                            "content": "",
                        }
                    ],
                    "limit": "%s" % pbConfig.params["defaultLimitBibtexs"],
                    "offset": "0",
                    "replaceFields": {
                        "regex": False,
                        "double": False,
                        "fieOld": "author",
                        "old": "",
                        "fieNew": "author",
                        "new": "",
                        "fieNew1": "author",
                        "new1": "",
                    },
                },
                "a",
                "b",
            ],
        )
        self.assertEqual(sbw.currentHistoric, 0)
        self.assertEqual(
            sbw.possibleTypes,
            {
                "exp_paper": {"desc": "Experimental paper"},
                "lecture": {"desc": "Lecture"},
                "phd_thesis": {"desc": "PhD thesis"},
                "review": {"desc": "Review"},
                "proceeding": {"desc": "Proceeding"},
                "book": {"desc": "Book"},
                "none": {"desc": "No type"},
            },
        )
        self.assertEqual(
            sbw.operators,
            {
                "text": [
                    "contains",
                    "different from",
                    "does not contain",
                    "exact match",
                ],
                "catexp": [
                    "all the following",
                    "at least one among",
                    "this or subcategories",
                    # "none of the following"
                ],
            },
        )
        self.assertEqual(
            sbw.fields,
            {
                "text": [
                    "bibtex",
                    "bibkey",
                    "arxiv",
                    "doi",
                    "year",
                    "firstdate",
                    "pubdate",
                    "comments",
                    "abstract",
                ]
            },
        )

        self.assertEqual(
            sbw.replaceComboFields,
            {
                "old": [
                    "arxiv",
                    "doi",
                    "year",
                    "author",
                    "title",
                    "journal",
                    "number",
                    "volume",
                    "published",
                ],
                "new": [
                    "arxiv",
                    "doi",
                    "year",
                    "author",
                    "title",
                    "journal",
                    "number",
                    "volume",
                ],
            },
        )
        self.assertEqual(sbw.values, [])
        self.assertEqual(sbw.numberOfRows, 1)
        self.assertEqual(sbw.replOld, None)
        self.assertEqual(sbw.replNew, None)
        self.assertEqual(sbw.replNew1, None)
        self.assertEqual(sbw.limitValue, None)
        self.assertEqual(sbw.limitOffs, None)

        p = QWidget()
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf, patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.processHistoric",
            side_effect=["a", "b"],
            autospec=True,
        ) as _ph, patch(
            "physbiblio.config.GlobalDB.getSearchList",
            return_value=["abc", "def"],
            autospec=True,
        ) as _sl:
            sbw = SearchBibsWindow(parent=p, replace=True)
            _sl.assert_called_once_with(
                pbConfig.globalDb, manual=False, replacement=True
            )
        self.assertTrue(sbw.replace)
        self.assertEqual(sbw.parent(), p)

        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf, patch(
            "physbiblio.config.GlobalDB.getSearchByID",
            return_value=[
                {
                    "idS": 0,
                    "name": "test1",
                    "count": 0,
                    "searchDict": '[{"a": "abc"}, {"b": "def"}]',
                    "limitNum": 1111,
                    "offsetNum": 12,
                    "replaceFields": '["e1"]',
                    "manual": 0,
                    "isReplace": 0,
                }
            ],
            autospec=True,
        ) as _gsbi:
            sbw = SearchBibsWindow(edit="123")
            _cf.assert_called_once_with(sbw, histIndex=0)
            _gsbi.assert_called_once_with(pbConfig.globalDb, "123")
            self.assertEqual(
                sbw.historic,
                [
                    {
                        "limit": "1111",
                        "nrows": 2,
                        "offset": "12",
                        "replaceFields": {},
                        "searchValues": [{"a": "abc"}, {"b": "def"}],
                    }
                ],
            )
            _cf.reset_mock()
            _gsbi.reset_mock()
            sbw = SearchBibsWindow(edit=123)
            _cf.assert_called_once_with(sbw, histIndex=0)
            _gsbi.assert_called_once_with(pbConfig.globalDb, 123)
            self.assertEqual(
                sbw.historic,
                [
                    {
                        "limit": "1111",
                        "nrows": 2,
                        "offset": "12",
                        "replaceFields": {},
                        "searchValues": [{"a": "abc"}, {"b": "def"}],
                    }
                ],
            )
            _cf.reset_mock()
            _gsbi.reset_mock()
            with patch("logging.Logger.error") as _e:
                sbw = SearchBibsWindow(edit="ab1")
                _e.assert_called_once_with("Wrong 'edit', it is not an ID: 'ab1'")
            _cf.assert_not_called()
            _gsbi.assert_not_called()
            self.assertFalse(hasattr(sbw, "historic"))

    def test_processHistoric(self):
        """test processHistoric"""
        records = [
            {
                "idS": 0,
                "name": "test1",
                "count": 0,
                "searchDict": '[{"a": "abc"}, {"b": "def"}]',
                "limitNum": 1111,
                "offsetNum": 12,
                "replaceFields": '["e1"]',
                "manual": 0,
                "isReplace": 0,
            },
            {
                "idS": 1,
                "name": "test2",
                "count": 1,
                "searchDict": '[{"a": "abc"}, {',
                "limitNum": 123,
                "offsetNum": 99,
                "replaceFields": "abc",
                "manual": 0,
                "isReplace": 0,
            },
            {
                "idS": 2,
                "name": "test3",
                "count": 0,
                "searchDict": [{"a": "abc"}, {}],
                "limitNum": 123,
                "offsetNum": 99,
                "replaceFields": '{"old": "e1"}',
                "manual": 0,
                "isReplace": 1,
            },
            {
                "idS": 3,
                "name": "test4",
                "count": 1,
                "searchDict": '[{"a": "abc"}]',
                "limitNum": 123,
                "offsetNum": 99,
                "replaceFields": "abc",
                "manual": 0,
                "isReplace": 1,
            },
            {
                "idS": 4,
                "name": "test4",
                "count": 2,
                "searchDict": '[{"a": "abc"}]',
                "limitNum": 123,
                "offsetNum": 99,
                "replaceFields": '{"abc": ',
                "manual": 0,
                "isReplace": 1,
            },
        ]
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf:
            sbw = SearchBibsWindow()
        self.assertEqual(
            sbw.processHistoric(records[0]),
            {
                "nrows": 2,
                "searchValues": [{"a": "abc"}, {"b": "def"}],
                "limit": "1111",
                "offset": "12",
                "replaceFields": {},
            },
        )
        with patch("logging.Logger.warning") as _w:
            self.assertEqual(
                sbw.processHistoric(records[1]),
                {
                    "nrows": 0,
                    "searchValues": [],
                    "limit": "123",
                    "offset": "99",
                    "replaceFields": {},
                },
            )
            _w.assert_called_once_with(
                "Something went wrong when processing the saved search"
                + ' fields:\n[{"a": "abc"}, {',
                exc_info=True,
            )
        with patch("logging.Logger.warning") as _w:
            self.assertEqual(
                sbw.processHistoric(records[2]),
                {
                    "nrows": 0,
                    "searchValues": [],
                    "limit": "123",
                    "offset": "99",
                    "replaceFields": {"old": "e1"},
                },
            )
            _w.assert_called_once_with(
                "Something went wrong when processing the saved search"
                + " fields:\n[{'a': 'abc'}, {}]",
                exc_info=True,
            )
        with patch("logging.Logger.warning") as _w:
            self.assertEqual(
                sbw.processHistoric(records[3]),
                {
                    "nrows": 1,
                    "searchValues": [{"a": "abc"}],
                    "limit": "123",
                    "offset": "99",
                    "replaceFields": {},
                },
            )
            _w.assert_called_once_with(
                "Something went wrong when processing the saved"
                + " search/replace:\nabc",
                exc_info=True,
            )
        with patch("logging.Logger.warning") as _w:
            self.assertEqual(
                sbw.processHistoric(records[4]),
                {
                    "nrows": 1,
                    "searchValues": [{"a": "abc"}],
                    "limit": "123",
                    "offset": "99",
                    "replaceFields": {},
                },
            )
            _w.assert_called_once_with(
                "Something went wrong when processing the saved "
                + 'search/replace:\n{"abc": ',
                exc_info=True,
            )

    def test_changeCurrentContent(self):
        """test changeCurrentContent"""
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf:
            sbw = SearchBibsWindow()
        self.assertFalse(sbw.save)
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.cleanLayout", autospec=True
        ) as _cl, patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf:
            sbw.changeCurrentContent(2)
            _cl.assert_called_once_with(sbw)
            _cf.assert_called_once_with(sbw, 2)

    def test_onOk(self):
        """test onOk"""
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf:
            sbw = SearchBibsWindow()
        sbw.close = MagicMock()
        self.assertFalse(sbw.result)
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.readForm", autospec=True
        ) as _r:
            sbw.onOk()
            _r.assert_called_once_with(sbw)
        self.assertTrue(sbw.result)
        sbw.close.assert_called_once_with()

    def test_onSave(self):
        """test onSave"""
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf:
            sbw = SearchBibsWindow()
        self.assertFalse(sbw.save)
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.onOk", autospec=True
        ) as _o:
            sbw.onSave()
            _o.assert_called_once_with(sbw)
        self.assertTrue(sbw.save)

    def test_onAskCats(self):
        """test onAskCats"""
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf:
            sbw = SearchBibsWindow()
        sbw.createLine(
            0,
            {
                "logical": None,
                "field": None,
                "type": "Categories",
                "operator": None,
                "content": "",
            },
        )
        sbw.textValues[0]["content"].setText("")

        sc = CatsTreeWindow(parent=sbw, askCats=True, expButton=False, previous=[])
        sc.exec_ = MagicMock()
        sc.result = False
        with patch(
            "physbiblio.gui.bibWindows.CatsTreeWindow",
            return_value=sc,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _sc, patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.readLine",
            return_value={"content": ""},
            autospec=True,
        ) as _cf:
            sbw.onAskCats(0)
            _sc.assert_called_once_with(
                parent=sbw, askCats=True, expButton=False, previous=[]
            )
            sc.exec_.assert_called_once_with()
            self.assertEqual(sbw.textValues[0]["content"].text(), "")

        sbw.textValues[0]["content"].setText("[0]")
        sc = CatsTreeWindow(parent=sbw, askCats=True, expButton=False, previous=[0])
        sbw.selectedCats = [0, 1]
        sc.exec_ = MagicMock()
        sc.result = "Ok"
        with patch(
            "physbiblio.gui.bibWindows.CatsTreeWindow",
            return_value=sc,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _sc:
            sbw.onAskCats(0)
            _sc.assert_called_once_with(
                parent=sbw, askCats=True, expButton=False, previous=[0]
            )
            sc.exec_.assert_called_once_with()
            self.assertEqual(sbw.textValues[0]["content"].text(), "[0, 1]")

    def test_onAskExps(self):
        """test onAskExps"""
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf:
            sbw = SearchBibsWindow()
        sbw.createLine(
            0,
            {
                "logical": None,
                "field": None,
                "type": "Experiments",
                "operator": None,
                "content": "",
            },
        )
        sbw.textValues[0]["content"].setText("")

        se = ExpsListWindow(parent=sbw, askExps=True, previous=[])
        se.exec_ = MagicMock()
        se.result = False
        with patch(
            "physbiblio.gui.bibWindows.ExpsListWindow",
            return_value=se,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _se, patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.readLine",
            return_value={"content": ""},
            autospec=True,
        ) as _cf:
            sbw.onAskExps(0)
            _se.assert_called_once_with(parent=sbw, askExps=True, previous=[])
            se.exec_.assert_called_once_with()
            self.assertEqual(sbw.textValues[0]["content"].text(), "")

        sbw.textValues[0]["content"].setText("[0]")
        se = ExpsListWindow(parent=sbw, askExps=True, previous=[])
        sbw.selectedExps = [0, 1]
        se.exec_ = MagicMock()
        se.result = "Ok"
        with patch(
            "physbiblio.gui.bibWindows.ExpsListWindow",
            return_value=se,
            autospec=USE_AUTOSPEC_CLASS,
        ) as _se:
            sbw.onAskExps(0)
            _se.assert_called_once_with(parent=sbw, askExps=True, previous=[0])
            se.exec_.assert_called_once_with()
            self.assertEqual(sbw.textValues[0]["content"].text(), "[0, 1]")

    def test_keyPressEvent(self):
        """test keyPressEvent"""
        sbw = SearchBibsWindow(replace=True)
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.onCancel", autospec=True
        ) as _oc:
            QTest.keyPress(sbw.acceptButton, "a")
            _oc.assert_not_called()
            QTest.keyPress(sbw.acceptButton, Qt.Key_Enter)
            _oc.assert_not_called()
            QTest.keyPress(sbw.acceptButton, Qt.Key_Escape)
            self.assertEqual(_oc.call_count, 1)
        with patch(
            "physbiblio.config.GlobalDB.getSearchByID",
            return_value=[
                {
                    "idS": 0,
                    "name": "test1",
                    "count": 0,
                    "searchDict": '[{"a": "abc"}, {"b": "def"}]',
                    "limitNum": 1111,
                    "offsetNum": 12,
                    "replaceFields": '["e1"]',
                    "manual": 0,
                    "isReplace": 0,
                }
            ],
            autospec=True,
        ) as _gsbi:
            sbw = SearchBibsWindow(edit="123")
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.readForm", autospec=True
        ) as _rf:
            QTest.keyPress(sbw.acceptButton, "a")
            _rf.assert_not_called()
            QTest.keyPress(sbw.acceptButton, Qt.Key_Up)
            _rf.assert_not_called()
            QTest.keyPress(sbw.acceptButton, Qt.Key_Down)
            _rf.assert_not_called()
        sbw = SearchBibsWindow()
        sbw.historic = ["a", "b", "c", "d"]
        sbw.currentHistoric = 0
        sbw.readForm()
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.readForm", autospec=True
        ) as _rf, patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.cleanLayout", autospec=True
        ) as _cl, patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf:
            QTest.keyPress(sbw, Qt.Key_Down)
            _rf.assert_called_once_with(sbw)
            _cl.assert_called_once_with(sbw)
            self.assertEqual(sbw.currentHistoric, 0)
            self.assertEqual(
                sbw.historic[0],
                {
                    "limit": "100",
                    "nrows": 1,
                    "offset": "0",
                    "replaceFields": {
                        "double": False,
                        "fieNew": "author",
                        "fieNew1": "author",
                        "fieOld": "author",
                        "new": "",
                        "new1": "",
                        "old": "",
                        "regex": False,
                    },
                    "searchValues": [
                        {
                            "content": "",
                            "field": "bibtex",
                            "logical": None,
                            "operator": "contains",
                            "type": "Text",
                        }
                    ],
                },
            )
            _cf.assert_called_once_with(sbw, histIndex=0)
            _cf.reset_mock()
            QTest.keyPress(sbw, Qt.Key_Down)
            _cf.assert_called_once_with(sbw, histIndex=0)
            _cf.reset_mock()
            QTest.keyPress(sbw, Qt.Key_Up)
            self.assertEqual(_rf.call_count, 3)
            self.assertEqual(_cl.call_count, 3)
            self.assertEqual(sbw.currentHistoric, 1)
            _cf.assert_called_once_with(sbw, histIndex=1)
            _cf.reset_mock()
            QTest.keyPress(sbw, Qt.Key_Up)
            self.assertEqual(_rf.call_count, 4)
            self.assertEqual(_cl.call_count, 4)
            self.assertEqual(sbw.currentHistoric, 2)
            _cf.assert_called_once_with(sbw, histIndex=2)
            _cf.reset_mock()
            QTest.keyPress(sbw, Qt.Key_Up)
            self.assertEqual(_rf.call_count, 5)
            self.assertEqual(_cl.call_count, 5)
            self.assertEqual(sbw.currentHistoric, 3)
            _cf.assert_called_once_with(sbw, histIndex=3)
            _cf.reset_mock()
            QTest.keyPress(sbw, Qt.Key_Up)
            self.assertEqual(_rf.call_count, 6)
            self.assertEqual(_cl.call_count, 6)
            self.assertEqual(sbw.currentHistoric, 3)
            _cf.assert_called_once_with(sbw, histIndex=3)
            _cf.reset_mock()
            QTest.keyPress(sbw, Qt.Key_Down)
            self.assertEqual(_rf.call_count, 7)
            self.assertEqual(_cl.call_count, 7)
            self.assertEqual(sbw.currentHistoric, 2)
            _cf.assert_called_once_with(sbw, histIndex=2)
            _cf.reset_mock()
            QTest.keyPress(sbw, Qt.Key_Down)
            self.assertEqual(_rf.call_count, 8)
            self.assertEqual(_cl.call_count, 8)
            self.assertEqual(sbw.currentHistoric, 1)
            _cf.assert_called_once_with(sbw, histIndex=1)
            _cf.reset_mock()
            QTest.keyPress(sbw, Qt.Key_Down)
            self.assertEqual(_rf.call_count, 9)
            self.assertEqual(_cl.call_count, 9)
            self.assertEqual(sbw.currentHistoric, 0)
            _cf.assert_called_once_with(sbw, histIndex=0)
            _cf.reset_mock()
            QTest.keyPress(sbw, Qt.Key_Down)
            self.assertEqual(_rf.call_count, 10)
            self.assertEqual(_cl.call_count, 10)
            self.assertEqual(sbw.currentHistoric, 0)
            _cf.assert_called_once_with(sbw, histIndex=0)

        sbw = SearchBibsWindow(replace=True)
        sbw.historic = ["a", "b", "c"]
        self.assertEqual(sbw.currentHistoric, 0)
        sbw.readForm()
        with patch.object(
            SearchBibsWindow, "readForm", wraps=sbw.readForm, autospec=True
        ) as _rf, patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.cleanLayout", autospec=True
        ) as _cl, patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf:
            QTest.keyPress(sbw, Qt.Key_Down)
            _rf.assert_called_once_with(sbw)
            _cl.assert_called_once_with(sbw)
            self.assertEqual(sbw.currentHistoric, 0)
            self.assertEqual(
                sbw.historic[0],
                {
                    "limit": "100000",
                    "nrows": 1,
                    "offset": "0",
                    "replaceFields": {
                        "double": False,
                        "fieNew": "author",
                        "fieNew1": "author",
                        "fieOld": "author",
                        "new": "",
                        "new1": "",
                        "old": "",
                        "regex": False,
                    },
                    "searchValues": [
                        {
                            "content": "",
                            "field": "bibtex",
                            "logical": None,
                            "operator": "contains",
                            "type": "Text",
                        }
                    ],
                },
            )
            _cf.assert_called_once_with(sbw, histIndex=0)
            _cf.reset_mock()
            QTest.keyPress(sbw, Qt.Key_Down)
            _cf.assert_called_once_with(sbw, histIndex=0)
            _cf.reset_mock()
            QTest.keyPress(sbw, Qt.Key_Up)
            self.assertEqual(_rf.call_count, 3)
            self.assertEqual(_cl.call_count, 3)
            self.assertEqual(sbw.currentHistoric, 1)
            _cf.assert_called_once_with(sbw, histIndex=1)
            _cf.reset_mock()
            QTest.keyPress(sbw, Qt.Key_Up)
            self.assertEqual(_rf.call_count, 4)
            self.assertEqual(_cl.call_count, 4)
            self.assertEqual(sbw.currentHistoric, 2)
            _cf.assert_called_once_with(sbw, histIndex=2)
            _cf.reset_mock()
            QTest.keyPress(sbw, Qt.Key_Up)
            self.assertEqual(_rf.call_count, 5)
            self.assertEqual(_cl.call_count, 5)
            self.assertEqual(sbw.currentHistoric, 2)
            _cf.assert_called_once_with(sbw, histIndex=2)
            _cf.reset_mock()
            QTest.keyPress(sbw, Qt.Key_Down)
            self.assertEqual(_rf.call_count, 6)
            self.assertEqual(_cl.call_count, 6)
            self.assertEqual(sbw.currentHistoric, 1)
            _cf.assert_called_once_with(sbw, histIndex=1)
            _cf.reset_mock()
            QTest.keyPress(sbw, Qt.Key_Down)
            self.assertEqual(_rf.call_count, 7)
            self.assertEqual(_cl.call_count, 7)
            self.assertEqual(sbw.currentHistoric, 0)
            _cf.assert_called_once_with(sbw, histIndex=0)
            _cf.reset_mock()
            QTest.keyPress(sbw, Qt.Key_Down)
            self.assertEqual(_rf.call_count, 8)
            self.assertEqual(_cl.call_count, 8)
            self.assertEqual(sbw.currentHistoric, 0)
            _cf.assert_called_once_with(sbw, histIndex=0)

    def test_eventFilter(self):
        """test eventFilter"""
        sbw = SearchBibsWindow(replace=True)
        w = "123"
        e = MagicMock()
        e.type.return_value = "a"
        e.key.return_value = "b"
        sbw.acceptButton.setFocus = MagicMock()
        with patch(
            "PySide2.QtWidgets.QWidget.eventFilter", return_value="abc", autospec=True
        ) as _ef:
            self.assertEqual(sbw.eventFilter(w, e), "abc")
            _ef.assert_called_once_with(sbw, w, e)
            e.key.assert_not_called()
        e.type.return_value = QEvent.KeyPress
        with patch(
            "PySide2.QtWidgets.QWidget.eventFilter", return_value="abc", autospec=True
        ) as _ef:
            self.assertEqual(sbw.eventFilter(w, e), "abc")
            _ef.assert_called_once_with(sbw, w, e)
            e.key.assert_not_called()
        for x in [
            sbw.textValues[0]["content"],
            sbw.replOld,
            sbw.replNew,
            sbw.replNew1,
            sbw.limitValue,
            sbw.limitOffs,
        ]:
            w = x
            with patch(
                "PySide2.QtWidgets.QWidget.eventFilter",
                return_value="abc",
                autospec=True,
            ) as _ef:
                self.assertEqual(sbw.eventFilter(w, e), "abc")
                _ef.assert_called_once_with(sbw, w, e)
                e.key.assert_called_once_with()
                sbw.acceptButton.setFocus.assert_not_called()
            e.key.reset_mock()
        for x in [Qt.Key_Return, Qt.Key_Enter]:
            e.key.return_value = x
            with patch(
                "PySide2.QtWidgets.QWidget.eventFilter",
                return_value="abc",
                autospec=True,
            ) as _ef:
                self.assertTrue(sbw.eventFilter(w, e))
                _ef.assert_not_called()
                e.key.assert_called_once_with()
                sbw.acceptButton.setFocus.assert_called_once_with()
            e.key.reset_mock()
            sbw.acceptButton.setFocus.reset_mock()

    def test_resetForm(self):
        """test resetForm"""
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf:
            sbw = SearchBibsWindow()
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.cleanLayout", autospec=True
        ) as _cl, patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf:
            sbw.resetForm()
            _cl.assert_called_once_with(sbw)
            _cf.assert_called_once_with(sbw)

    def test_addRow(self):
        """test addRow"""
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf:
            sbw = SearchBibsWindow()
            sbw.numberOfRows = 1
            sbw.textValues = [{"a": "A"}]
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.resetForm", autospec=True
        ) as _f, patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.readForm", autospec=True
        ) as _rf:
            sbw.addRow()
            _f.assert_called_once_with(sbw)
            _rf.assert_called_once_with(sbw)
            self.assertEqual(sbw.numberOfRows, 2)
            self.assertEqual(sbw.textValues, [{"a": "A"}, {}])

    def test_deleteRow(self):
        """test deleteRow"""
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf:
            sbw = SearchBibsWindow()
            sbw.numberOfRows = 4
            sbw.textValues = [{"a": "A"}, {"b": "B"}, {"c": "C"}, {"d": "D"}]
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.resetForm", autospec=True
        ) as _f, patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.readForm", autospec=True
        ) as _rf:
            sbw.deleteRow(11)
            _f.assert_not_called()
            _rf.assert_not_called()
            sbw.deleteRow(2)
            _f.assert_called_once_with(sbw)
            _rf.assert_called_once_with(sbw)
            self.assertEqual(sbw.numberOfRows, 3)
            self.assertEqual(sbw.textValues, [{"a": "A"}, {"b": "B"}, {"d": "D"}])
            sbw.deleteRow(0)
            self.assertEqual(sbw.numberOfRows, 2)
            self.assertEqual(sbw.textValues, [{"b": "B"}, {"d": "D"}])
            sbw.deleteRow(2)
            self.assertEqual(sbw.numberOfRows, 2)
            self.assertEqual(sbw.textValues, [{"b": "B"}, {"d": "D"}])

    def test_saveTypeRow(self):
        """test saveTypeRow"""
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf:
            sbw = SearchBibsWindow()
        sbw.textValues.append({})
        sbw.textValues[0]["type"] = PBComboBox(
            sbw, ["Text", "Categories", "Experiments", "Marks", "Type"], current="Text"
        )
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.readForm", autospec=True
        ) as _a, patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.resetForm", autospec=True
        ) as _s:
            sbw.saveTypeRow(0, "Marks")
            self.assertEqual(sbw.textValues[0]["type"].currentText(), "Marks")
            _a.assert_called_once_with(sbw)
            _s.assert_called_once_with(sbw)

    def test_readLine(self):
        """test readLine"""
        sbw = SearchBibsWindow()
        sbw.addRow()
        default = {
            "logical": None,
            "field": None,
            "type": "Text",
            "operator": None,
            "content": "",
        }
        with patch("logging.Logger.debug") as _d:
            self.assertEqual(sbw.readLine(2), default)
            _d.assert_called_once_with("Missing index 2 (there are 2 elements)")
        self.assertEqual(
            sbw.readLine(0),
            {
                "logical": None,
                "field": "bibtex",
                "type": "Text",
                "operator": "contains",
                "content": "",
            },
        )

        self.assertEqual(
            sbw.readLine(1),
            {
                "logical": "AND",
                "field": "bibtex",
                "type": "Text",
                "operator": "contains",
                "content": "",
            },
        )
        del sbw.textValues[1]["logical"]
        with patch("logging.Logger.debug") as _d:
            self.assertEqual(
                sbw.readLine(1),
                {
                    "logical": None,
                    "field": "bibtex",
                    "type": "Text",
                    "operator": "contains",
                    "content": "",
                },
            )
            _d.assert_called_once_with("Missing or wrong 'logical' in line 1")

        del sbw.textValues[1]["type"]
        with patch("logging.Logger.debug") as _d:
            self.assertEqual(sbw.readLine(1), default)
            _d.assert_called_once_with("Missing or wrong 'type' in line 1")
            sbw.textValues[1]["type"] = None
            _d.reset_mock()
            self.assertEqual(sbw.readLine(1), default)
            _d.assert_called_once_with("Missing or wrong 'type' in line 1")

        # Text
        sbw.textValues[0]["field"].setCurrentText("arxiv")
        sbw.textValues[0]["operator"].setCurrentText("exact match")
        sbw.textValues[0]["content"].setText("myself")
        self.assertEqual(
            sbw.readLine(0),
            {
                "logical": None,
                "field": "arxiv",
                "type": "Text",
                "operator": "exact match",
                "content": "myself",
            },
        )
        sbw.textValues[0]["field"] = PBLabel("")
        sbw.textValues[0]["operator"] = PBLabel("")
        sbw.textValues[0]["content"] = sbw.textValues[1]["field"]
        self.assertEqual(
            sbw.readLine(0),
            {
                "logical": None,
                "field": None,
                "type": "Text",
                "operator": None,
                "content": "",
            },
        )
        sbw.textValues[0]["field"] = MagicMock()
        sbw.textValues[0]["field"].currentText.return_value = "ABC"
        sbw.textValues[0]["operator"] = MagicMock()
        sbw.textValues[0]["operator"].currentText.return_value = "DEF"
        self.assertEqual(
            sbw.readLine(0),
            {
                "logical": None,
                "field": None,
                "type": "Text",
                "operator": None,
                "content": "",
            },
        )

        # Categories or Experiments
        sbw.createLine(
            0,
            {
                "logical": None,
                "field": None,
                "type": "Categories",
                "operator": "at least one among",
                "content": "[0, 1]",
            },
        )
        self.assertEqual(
            sbw.readLine(0),
            {
                "logical": None,
                "field": "",
                "type": "Categories",
                "operator": "at least one among",
                "content": [0, 1],
            },
        )
        sbw.textValues[0]["type"].setCurrentText("Experiments")
        self.assertEqual(
            sbw.readLine(0),
            {
                "logical": None,
                "field": "",
                "type": "Experiments",
                "operator": "at least one among",
                "content": [0, 1],
            },
        )
        sbw.textValues[0]["operator"] = PBLabel("")
        sbw.textValues[0]["content"].setText("[0, 1")
        self.assertEqual(
            sbw.readLine(0),
            {
                "logical": None,
                "field": "",
                "type": "Experiments",
                "operator": None,
                "content": [],
            },
        )
        sbw.textValues[0]["operator"] = MagicMock()
        sbw.textValues[0]["operator"].currentText.return_value = "DEF"
        sbw.textValues[0]["content"].setText("{'0': 1}")
        self.assertEqual(
            sbw.readLine(0),
            {
                "logical": None,
                "field": "",
                "type": "Experiments",
                "operator": None,
                "content": [],
            },
        )
        sbw.textValues[0]["content"] = sbw.textValues[1]["field"]
        self.assertEqual(
            sbw.readLine(0),
            {
                "logical": None,
                "field": "",
                "type": "Experiments",
                "operator": None,
                "content": [],
            },
        )

        # Marks
        sbw.createLine(
            0,
            {
                "logical": None,
                "field": None,
                "type": "Marks",
                "operator": None,
                "content": [],
            },
        )
        sbw.textValues[0]["content"]["new"].setChecked(True)
        self.assertEqual(
            sbw.readLine(0),
            {
                "logical": None,
                "field": None,
                "type": "Marks",
                "operator": None,
                "content": ["new"],
            },
        )
        sbw.textValues[0]["content"] = PBLabel("")
        self.assertEqual(
            sbw.readLine(0),
            {
                "logical": None,
                "field": None,
                "type": "Marks",
                "operator": None,
                "content": [],
            },
        )

        # Types
        sbw.createLine(
            0,
            {
                "logical": None,
                "field": None,
                "type": "Type",
                "operator": None,
                "content": [],
            },
        )
        sbw.textValues[0]["content"]["book"].setChecked(True)
        self.assertEqual(
            sbw.readLine(0),
            {
                "logical": None,
                "field": None,
                "type": "Type",
                "operator": None,
                "content": ["book"],
            },
        )
        sbw.textValues[0]["content"] = PBLabel("")
        self.assertEqual(
            sbw.readLine(0),
            {
                "logical": None,
                "field": None,
                "type": "Type",
                "operator": None,
                "content": [],
            },
        )

    def test_readForm(self):
        """test readForm"""
        sbw = SearchBibsWindow()
        sbw.values = ["a", "b"]
        sbw.numberOfRows = 3
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.readLine",
            side_effect=["A", "B", "C", "D", "E", "F"],
            autospec=True,
        ) as _rl:
            sbw.readForm()
            _rl.assert_has_calls([call(sbw, 0), call(sbw, 1), call(sbw, 2)])
            self.assertEqual(
                sbw.values,
                [
                    "A",
                    "B",
                    {
                        "logical": None,
                        "field": None,
                        "type": "Text",
                        "operator": None,
                        "content": "",
                    },
                ],
            )
            self.assertEqual(sbw.limit, pbConfig.params["defaultLimitBibtexs"])
            self.assertEqual(sbw.offset, 0)
            sbw.limitValue.setText("413")
            sbw.limitOffs.setText("99")
            sbw.readForm()
            self.assertEqual(sbw.limit, 413)
            self.assertEqual(sbw.offset, 99)

        sbw = SearchBibsWindow(replace=True)
        sbw.values = ["a", "b"]
        sbw.numberOfRows = 2
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.readLine",
            side_effect=["A", "B", "C", "D", "E", "F"],
            autospec=True,
        ) as _rl:
            sbw.readForm()
            _rl.assert_has_calls([call(sbw, 0), call(sbw, 1)])
            self.assertEqual(
                sbw.replaceFields,
                {
                    "regex": False,
                    "double": False,
                    "fieOld": "author",
                    "old": "",
                    "fieNew": "author",
                    "new": "",
                    "fieNew1": "author",
                    "new1": "",
                },
            )
            sbw.replRegex.setChecked(True)
            sbw.doubleEdit.setChecked(False)
            sbw.replOldField.setCurrentText("published")
            sbw.replOld.setText("a b c")
            sbw.replNewField.setCurrentText("volume")
            sbw.replNew.setText("AA")
            sbw.replNewField1.setCurrentText("journal")
            sbw.replNew1.setText("BB")
            sbw.readForm()
            _rl.assert_has_calls([call(sbw, 0), call(sbw, 1)])
            self.assertEqual(
                sbw.replaceFields,
                {
                    "regex": True,
                    "double": False,
                    "fieOld": "published",
                    "old": "a b c",
                    "fieNew": "volume",
                    "new": "AA",
                    "fieNew1": "journal",
                    "new1": "BB",
                },
            )

    def test_createLine(self):
        """test createLine"""
        sbw = SearchBibsWindow()
        self.assertEqual(len(sbw.textValues), 1)
        with patch("logging.Logger.debug") as _d:
            sbw.createLine(0, [])
            _d.assert_called_once_with("Invalid previous! set to empty.\n[]")
            sbw.createLine(0, {"content": ""})
            _d.assert_any_call("Invalid previous! set to empty.\n{'content': ''}")
        self.assertEqual(len(sbw.textValues), 1)
        with patch("PySide2.QtCore.QObject.installEventFilter", autospec=True) as _ief:
            sbw.createLine(
                2,
                {
                    "logical": "OR",
                    "field": "doi",
                    "type": "Text",
                    "operator": "exact match",
                    "content": "abc",
                },
            )
            self.assertEqual(_ief.call_count, 1)
        self.assertEqual(len(sbw.textValues), 3)
        self.assertEqual(sbw.textValues[0]["logical"], None)
        self.assertEqual(sbw.currGrid.itemAtPosition(0, 0), None)
        self.assertIsInstance(sbw.textValues[2]["logical"], PBAndOrCombo)
        self.assertEqual(sbw.textValues[2]["logical"].currentText(), "OR")
        self.assertEqual(
            sbw.currGrid.itemAtPosition(2, 0).widget(), sbw.textValues[2]["logical"]
        )
        self.assertIsInstance(sbw.textValues[2]["type"], PBComboBox)
        self.assertEqual(sbw.textValues[2]["type"].currentText(), "Text")
        self.assertEqual(sbw.textValues[2]["type"].count(), 5)
        self.assertEqual(sbw.textValues[2]["type"].itemText(0), "Text")
        self.assertEqual(sbw.textValues[2]["type"].itemText(1), "Categories")
        self.assertEqual(sbw.textValues[2]["type"].itemText(2), "Experiments")
        self.assertEqual(sbw.textValues[2]["type"].itemText(3), "Marks")
        self.assertEqual(sbw.textValues[2]["type"].itemText(4), "Type")
        self.assertEqual(
            sbw.currGrid.itemAtPosition(2, 1).widget(), sbw.textValues[2]["type"]
        )
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.saveTypeRow", autospec=True
        ) as _str:
            sbw.textValues[2]["type"].setCurrentText("Marks")
            _str.assert_called_once_with(sbw, 2, u"Marks")

        # Type
        self.assertIsInstance(sbw.textValues[2]["field"], PBComboBox)
        self.assertEqual(sbw.textValues[2]["field"].currentText(), "doi")
        self.assertEqual(sbw.textValues[2]["field"].count(), len(sbw.fields["text"]))
        for i, c in enumerate(sbw.fields["text"]):
            self.assertEqual(sbw.textValues[2]["field"].itemText(i), c)
        self.assertEqual(
            sbw.currGrid.itemAtPosition(2, 2).widget(), sbw.textValues[2]["field"]
        )

        self.assertIsInstance(sbw.textValues[2]["operator"], PBComboBox)
        self.assertEqual(sbw.textValues[2]["operator"].currentText(), "exact match")
        self.assertEqual(
            sbw.textValues[2]["operator"].count(), len(sbw.operators["text"])
        )
        for i, c in enumerate(sbw.operators["text"]):
            self.assertEqual(sbw.textValues[2]["operator"].itemText(i), c)
        self.assertEqual(
            sbw.currGrid.itemAtPosition(2, 3).widget(), sbw.textValues[2]["operator"]
        )

        self.assertIsInstance(sbw.textValues[2]["content"], QLineEdit)
        self.assertEqual(sbw.textValues[2]["content"].text(), "abc")
        self.assertEqual(
            sbw.currGrid.itemAtPosition(2, 4).widget(), sbw.textValues[2]["content"]
        )

        # Categories
        sbw.cleanLayout()
        sbw.createLine(
            1,
            {
                "logical": "OR",
                "field": None,
                "type": "Categories",
                "operator": "at least one among",
                "content": "",
            },
        )
        self.assertEqual(sbw.textValues[1]["type"].currentText(), "Categories")
        self.assertEqual(sbw.textValues[1]["field"], None)
        self.assertIsInstance(sbw.textValues[1]["operator"], PBComboBox)
        self.assertEqual(
            sbw.textValues[1]["operator"].currentText(), "at least one among"
        )
        self.assertEqual(
            sbw.textValues[1]["operator"].count(), len(sbw.operators["catexp"])
        )
        for i, c in enumerate(sbw.operators["catexp"]):
            self.assertEqual(sbw.textValues[1]["operator"].itemText(i), c)
        self.assertEqual(
            sbw.currGrid.itemAtPosition(1, 2).widget(), sbw.textValues[1]["operator"]
        )
        self.assertIsInstance(sbw.textValues[1]["content"], QPushButton)
        self.assertEqual(sbw.textValues[1]["content"].text(), "[]")
        self.assertEqual(
            sbw.currGrid.itemAtPosition(1, 4).widget(), sbw.textValues[1]["content"]
        )
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.onAskCats", autospec=True
        ) as _oac:
            QTest.mouseClick(sbw.textValues[1]["content"], Qt.LeftButton)
            _oac.assert_called_once_with(sbw, 1)

        sbw.createLine(
            0,
            {
                "logical": "OR",
                "field": None,
                "type": "Experiments",
                "operator": "at least one among",
                "content": [0],
            },
        )
        self.assertEqual(sbw.textValues[0]["type"].currentText(), "Experiments")
        self.assertEqual(sbw.textValues[0]["field"], None)
        self.assertIsInstance(sbw.textValues[0]["operator"], PBComboBox)
        self.assertEqual(
            sbw.textValues[0]["operator"].currentText(), "at least one among"
        )
        self.assertEqual(
            sbw.textValues[0]["operator"].count(), len(sbw.operators["catexp"]) - 1
        )
        for i, c in enumerate(sbw.operators["catexp"][0:2]):
            self.assertEqual(sbw.textValues[0]["operator"].itemText(i), c)
        self.assertEqual(
            sbw.currGrid.itemAtPosition(0, 2).widget(), sbw.textValues[0]["operator"]
        )
        self.assertIsInstance(sbw.textValues[0]["content"], QPushButton)
        self.assertEqual(sbw.textValues[0]["content"].text(), "[0]")
        self.assertEqual(
            sbw.currGrid.itemAtPosition(0, 4).widget(), sbw.textValues[0]["content"]
        )
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.onAskExps", autospec=True
        ) as _oae:
            QTest.mouseClick(sbw.textValues[0]["content"], Qt.LeftButton)
            _oae.assert_called_once_with(sbw, 0)

        # Marks
        sbw.cleanLayout()
        gb, mv = pBMarks.getGroupbox(["new"], description="", radio=True, addAny=True)
        with patch(
            "physbiblio.gui.marks.Marks.getGroupbox",
            return_value=(gb, mv),
            autospec=True,
        ) as _gg:
            sbw.createLine(
                0,
                {
                    "logical": "OR",
                    "field": None,
                    "type": "Marks",
                    "operator": None,
                    "content": ["new"],
                },
            )
            _gg.assert_called_once_with(
                pBMarks, ["new"], description="", radio=True, addAny=True
            )
        self.assertEqual(sbw.textValues[0]["type"].currentText(), "Marks")
        self.assertEqual(sbw.textValues[0]["operator"], None)
        self.assertEqual(sbw.textValues[0]["field"], gb)
        self.assertEqual(sbw.textValues[0]["content"], mv)
        self.assertEqual(sbw.currGrid.itemAtPosition(0, 2).widget(), gb)
        self.assertEqual(sbw.currGrid.itemAtPosition(0, 8), None)

        # Marks
        sbw.createLine(
            1,
            {
                "logical": "OR",
                "field": None,
                "type": "Type",
                "operator": None,
                "content": ["book"],
            },
        )
        self.assertEqual(sbw.textValues[1]["type"].currentText(), "Type")
        self.assertEqual(sbw.textValues[1]["operator"], None)
        self.assertIsInstance(sbw.textValues[1]["field"], QGroupBox)
        self.assertIsInstance(sbw.textValues[1]["content"], dict)
        self.assertEqual(
            sbw.currGrid.itemAtPosition(1, 2).widget(), sbw.textValues[1]["field"]
        )
        self.assertTrue(sbw.textValues[1]["field"].isFlat())
        self.assertIsInstance(sbw.textValues[1]["field"].layout(), QHBoxLayout)
        for i, (m, c) in enumerate(sbw.possibleTypes.items()):
            self.assertIsInstance(sbw.textValues[1]["content"][m], QRadioButton)
            self.assertEqual(sbw.textValues[1]["content"][m].text(), c["desc"])
            if m == "book":
                self.assertTrue(sbw.textValues[1]["content"][m].isChecked())
            else:
                self.assertFalse(sbw.textValues[1]["content"][m].isChecked())
            self.assertEqual(
                sbw.textValues[1]["field"].layout().itemAt(i).widget(),
                sbw.textValues[1]["content"][m],
            )

        # test close buttons
        sbw = SearchBibsWindow()
        sbw.addRow()
        sbw.addRow()
        self.assertIsInstance(sbw.currGrid.itemAtPosition(0, 8).widget(), QToolButton)
        self.assertEqual(sbw.currGrid.itemAtPosition(0, 8).widget().text(), "X")
        self.assertEqual(
            sbw.currGrid.itemAtPosition(0, 8).widget().toolTip(), bwstr.SR.deleteRow
        )
        self.assertIsInstance(sbw.currGrid.itemAtPosition(1, 8).widget(), QToolButton)
        self.assertEqual(sbw.currGrid.itemAtPosition(1, 8).widget().text(), "X")
        self.assertEqual(
            sbw.currGrid.itemAtPosition(1, 8).widget().toolTip(), bwstr.SR.deleteRow
        )
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.deleteRow", autospec=True
        ) as _dr:
            QTest.mouseClick(sbw.currGrid.itemAtPosition(1, 8).widget(), Qt.LeftButton)
            _dr.assert_called_once_with(sbw, 1)
            QTest.mouseClick(sbw.currGrid.itemAtPosition(0, 8).widget(), Qt.LeftButton)
            _dr.assert_any_call(sbw, 0)

    def test_createLimits(self):
        """test createLimits"""
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf:
            sbw = SearchBibsWindow()
        with patch("PySide2.QtCore.QObject.installEventFilter", autospec=True) as _ief:
            sbw.createLimits(12)
            self.assertEqual(_ief.call_count, 2)
        self.assertIsInstance(sbw.currGrid.itemAtPosition(11, 0).widget(), PBLabelRight)
        self.assertEqual(
            sbw.currGrid.itemAtPosition(11, 0).widget().text(), "Max number of results:"
        )
        self.assertIsInstance(sbw.currGrid.itemAtPosition(11, 3).widget(), PBLabelRight)
        self.assertEqual(
            sbw.currGrid.itemAtPosition(11, 3).widget().text(), "Start from:"
        )
        self.assertIsInstance(sbw.currGrid.itemAtPosition(11, 2).widget(), QLineEdit)
        self.assertEqual(sbw.currGrid.itemAtPosition(11, 2).widget(), sbw.limitValue)
        self.assertEqual(
            sbw.currGrid.itemAtPosition(11, 2).widget().text(),
            str(pbConfig.params["defaultLimitBibtexs"]),
        )
        self.assertIsInstance(sbw.currGrid.itemAtPosition(11, 5).widget(), QLineEdit)
        self.assertEqual(sbw.currGrid.itemAtPosition(11, 5).widget(), sbw.limitOffs)
        self.assertEqual(sbw.currGrid.itemAtPosition(11, 5).widget().text(), "0")

        sbw.limitValue.setText("123")
        sbw.limitOffs.setText("321")
        sbw.createLimits(24)
        self.assertEqual(sbw.limitValue.text(), "123")
        self.assertEqual(sbw.limitOffs.text(), "321")
        sbw.createLimits(5, defLim="444", defOffs="22")
        self.assertEqual(sbw.limitValue.text(), "123")
        self.assertEqual(sbw.limitOffs.text(), "321")
        del sbw.limitValue
        del sbw.limitOffs
        sbw.createLimits(5, defLim="444", defOffs="22")
        self.assertEqual(sbw.limitValue.text(), "444")
        self.assertEqual(sbw.limitOffs.text(), "22")
        sbw.createLimits(5, defLim="9999", defOffs="1", override=True)
        self.assertEqual(sbw.limitValue.text(), "9999")
        self.assertEqual(sbw.limitOffs.text(), "1")

    def test_createReplace(self):
        """test createReplace"""
        with patch(
            "physbiblio.gui.bibWindows.SearchBibsWindow.createForm", autospec=True
        ) as _cf:
            sbw = SearchBibsWindow()
        with patch("PySide2.QtCore.QObject.installEventFilter", autospec=True) as _ief:
            self.assertEqual(sbw.createReplace(10), 13)
            self.assertEqual(_ief.call_count, 2)
        self.assertIsInstance(sbw.currGrid.itemAtPosition(9, 0).widget(), PBLabel)
        self.assertEqual(sbw.currGrid.itemAtPosition(9, 0).widget().text(), "Replace:")
        self.assertIsInstance(sbw.currGrid.itemAtPosition(9, 2).widget(), PBLabelRight)
        self.assertEqual(sbw.currGrid.itemAtPosition(9, 2).widget().text(), "regex:")
        self.assertIsInstance(sbw.currGrid.itemAtPosition(9, 3).widget(), QCheckBox)
        self.assertEqual(sbw.currGrid.itemAtPosition(9, 3).widget(), sbw.replRegex)
        self.assertIsInstance(sbw.currGrid.itemAtPosition(10, 0).widget(), PBLabelRight)
        self.assertEqual(
            sbw.currGrid.itemAtPosition(10, 0).widget().text(), "From field:"
        )
        self.assertIsInstance(sbw.currGrid.itemAtPosition(11, 0).widget(), PBLabelRight)
        self.assertEqual(
            sbw.currGrid.itemAtPosition(11, 0).widget().text(), "Into field:"
        )
        self.assertIsInstance(sbw.currGrid.itemAtPosition(12, 0).widget(), QCheckBox)
        self.assertEqual(sbw.currGrid.itemAtPosition(12, 0).widget(), sbw.doubleEdit)
        self.assertEqual(
            sbw.currGrid.itemAtPosition(12, 0).widget().text(), "and also:"
        )
        self.assertIsInstance(sbw.limitValue, QLineEdit)
        self.assertIsInstance(sbw.limitOffs, QLineEdit)
        self.assertEqual(sbw.limitValue.text(), "100000")
        self.assertEqual(sbw.limitOffs.text(), "0")

        self.assertIsInstance(sbw.replOldField, PBComboBox)
        self.assertEqual(sbw.currGrid.itemAtPosition(10, 1).widget(), sbw.replOldField)
        for i, f in enumerate(sbw.replaceComboFields["old"]):
            self.assertEqual(sbw.replOldField.itemText(i), f)
        self.assertIsInstance(sbw.replOld, QLineEdit)
        self.assertEqual(sbw.currGrid.itemAtPosition(10, 3).widget(), sbw.replOld)

        for ix, itemF, item in [
            (11, sbw.replNewField, sbw.replNew),
            (12, sbw.replNewField1, sbw.replNew1),
        ]:
            self.assertIsInstance(itemF, PBComboBox)
            self.assertEqual(sbw.currGrid.itemAtPosition(ix, 1).widget(), itemF)
            for i, f in enumerate(sbw.replaceComboFields["new"]):
                self.assertEqual(itemF.itemText(i), f)
            self.assertIsInstance(item, QLineEdit)
            self.assertEqual(sbw.currGrid.itemAtPosition(ix, 3).widget(), item)

        self.assertFalse(sbw.replRegex.isChecked())
        self.assertEqual(sbw.replOldField.currentText(), "author")
        self.assertEqual(sbw.replNewField.currentText(), "author")
        self.assertEqual(sbw.replNewField1.currentText(), "author")
        self.assertFalse(sbw.doubleEdit.isChecked())
        self.assertEqual(sbw.replOld.text(), "")
        self.assertEqual(sbw.replNew.text(), "")
        self.assertEqual(sbw.replNew1.text(), "")

        # now try with modified values
        sbw.replRegex.setChecked(True)
        sbw.replOldField.setCurrentText("published")
        sbw.replNewField.setCurrentText("journal")
        sbw.replNewField1.setCurrentText("volume")
        sbw.doubleEdit.setChecked(True)
        sbw.replOld.setText("PRD")
        sbw.replNew.setText(r"\1")
        sbw.replNew1.setText(r"\2")
        sbw.cleanLayout()
        self.assertEqual(sbw.createReplace(13), 16)
        self.assertTrue(sbw.replRegex.isChecked())
        self.assertEqual(sbw.replOldField.currentText(), "published")
        self.assertEqual(sbw.replNewField.currentText(), "journal")
        self.assertEqual(sbw.replNewField1.currentText(), "volume")
        self.assertTrue(sbw.doubleEdit.isChecked())
        self.assertEqual(sbw.replOld.text(), "PRD")
        self.assertEqual(sbw.replNew.text(), r"\1")
        self.assertEqual(sbw.replNew1.text(), r"\2")

        # now with previous
        with patch("logging.Logger.debug") as _d:
            self.assertEqual(sbw.createReplace(13, previous={}), 16)
            _d.assert_called_once_with("Invalid previous, some key is missing!\n{}")
        self.assertFalse(sbw.replRegex.isChecked())
        self.assertEqual(sbw.replOldField.currentText(), "author")
        self.assertEqual(sbw.replNewField.currentText(), "author")
        self.assertEqual(sbw.replNewField1.currentText(), "author")
        self.assertFalse(sbw.doubleEdit.isChecked())
        self.assertEqual(sbw.replOld.text(), "")
        self.assertEqual(sbw.replNew.text(), "")
        self.assertEqual(sbw.replNew1.text(), "")
        sbw.createReplace(
            13,
            previous={
                "regex": False,
                "double": True,
                "fieOld": "volume",
                "fieNew": "number",
                "fieNew1": "year",
                "old": "([0-9]{2})([0-9]{2})",
                "new": r"\2",
                "new1": r"20\1",
            },
        )
        self.assertFalse(sbw.replRegex.isChecked())
        self.assertEqual(sbw.replOldField.currentText(), "volume")
        self.assertEqual(sbw.replNewField.currentText(), "number")
        self.assertEqual(sbw.replNewField1.currentText(), "year")
        self.assertTrue(sbw.doubleEdit.isChecked())
        self.assertEqual(sbw.replOld.text(), "([0-9]{2})([0-9]{2})")
        self.assertEqual(sbw.replNew.text(), r"\2")
        self.assertEqual(sbw.replNew1.text(), r"20\1")

    def test_createForm(self):
        """test createForm"""
        clsName = "physbiblio.gui.bibWindows.SearchBibsWindow."
        with patch(clsName + "createForm", autospec=True) as _cf:
            sbw = SearchBibsWindow()
        sbw.historic = [
            {
                "nrows": 1,
                "searchValues": [
                    {
                        "logical": None,
                        "field": None,
                        "type": "Text",
                        "operator": None,
                        "content": "",
                    }
                ],
                "limit": "%s" % pbConfig.params["defaultLimitBibtexs"],
                "offset": "0",
                "replaceFields": {
                    "regex": False,
                    "double": False,
                    "fieOld": "author",
                    "old": "",
                    "fieNew": "author",
                    "new": "",
                    "fieNew1": "author",
                    "new1": "",
                },
            },
            {
                "nrows": 1,
                "searchValues": ["sw"],
                "replaceFields": "av",
                "limit": 321,
                "offset": 22,
            },
            {
                "nrows": 2,
                "searchValues": ["lor", "th"],
                "replaceFields": "hp",
                "limit": 654,
                "offset": 8,
            },
        ]
        sbw.numberOfRows = 2
        with patch(clsName + "createLine", autospec=True) as _crlin, patch(
            clsName + "createLimits", autospec=True
        ) as _crlim, patch(clsName + "createReplace", autospec=True) as _crre:
            sbw.createForm()
            _crlin.assert_has_calls(
                [
                    call(
                        sbw,
                        0,
                        {
                            "operator": None,
                            "field": None,
                            "content": "",
                            "type": "Text",
                            "logical": None,
                        },
                    ),
                    call(
                        sbw,
                        1,
                        {
                            "operator": None,
                            "field": None,
                            "content": "",
                            "type": "Text",
                            "logical": None,
                        },
                    ),
                ]
            )
            _crlim.assert_called_once_with(sbw, 5)
            _crre.assert_not_called()
        sbw.cleanLayout()
        sbw.createForm()
        self.assertEqual(sbw.windowTitle(), "Search bibtex entries")
        # addFieldButton and label
        self.assertIsInstance(sbw.currGrid.itemAtPosition(2, 0).widget(), PBLabelRight)
        self.assertEqual(
            sbw.currGrid.itemAtPosition(2, 0).widget().text(),
            "Click here if you want more fields:",
        )
        self.assertIsInstance(sbw.currGrid.itemAtPosition(2, 2).widget(), QPushButton)
        self.assertEqual(sbw.currGrid.itemAtPosition(2, 2).widget(), sbw.addFieldButton)
        self.assertEqual(
            sbw.currGrid.itemAtPosition(2, 2).widget().text(), "Add another line"
        )
        with patch(clsName + "addRow", autospec=True) as _ar:
            QTest.mouseClick(sbw.addFieldButton, Qt.LeftButton)
            _ar.assert_called_once_with(sbw)
        # newTab
        self.assertEqual(sbw.currGrid.itemAtPosition(6, 0).widget(), sbw.newTabCheck)
        self.assertIsInstance(sbw.newTabCheck, QCheckBox)
        self.assertEqual(sbw.newTabCheck.text(), "Open results in new tab")
        # acceptbutton
        self.assertEqual(sbw.currGrid.itemAtPosition(7, 2).widget(), sbw.acceptButton)
        self.assertIsInstance(sbw.acceptButton, QPushButton)
        self.assertEqual(sbw.acceptButton.text(), "OK")
        with patch(clsName + "onOk", autospec=True) as _o:
            QTest.mouseClick(sbw.acceptButton, Qt.LeftButton)
            _o.assert_called_once_with(sbw)
        # cancelbutton
        self.assertEqual(sbw.currGrid.itemAtPosition(7, 3).widget(), sbw.cancelButton)
        self.assertIsInstance(sbw.cancelButton, QPushButton)
        self.assertEqual(sbw.cancelButton.text(), "Cancel")
        with patch(clsName + "onCancel", autospec=True) as _o:
            QTest.mouseClick(sbw.cancelButton, Qt.LeftButton)
            _o.assert_called_once_with(sbw)
        # savebutton
        self.assertEqual(sbw.currGrid.itemAtPosition(7, 5).widget(), sbw.saveButton)
        self.assertIsInstance(sbw.saveButton, QPushButton)
        self.assertEqual(sbw.saveButton.text(), "Run and save")
        with patch(clsName + "onSave", autospec=True) as _o:
            QTest.mouseClick(sbw.saveButton, Qt.LeftButton)
            _o.assert_called_once_with(sbw)

        sbw.saveTypeRow(0, "Categories")
        with patch(clsName + "createLine", autospec=True) as _crlin:
            sbw.createForm()
            _crlin.assert_has_calls(
                [
                    call(
                        sbw,
                        0,
                        {
                            "operator": u"all the following",
                            "field": "",
                            "content": [],
                            "type": u"Categories",
                            "logical": None,
                        },
                    ),
                    call(
                        sbw,
                        1,
                        {
                            "operator": u"contains",
                            "field": u"bibtex",
                            "content": u"",
                            "type": u"Text",
                            "logical": u"AND",
                        },
                    ),
                ]
            )

        sbw.replace = True
        with patch(clsName + "createLine", autospec=True) as _crlin, patch(
            clsName + "createLimits", autospec=True
        ) as _crlim, patch(clsName + "createReplace", autospec=True) as _crre:
            sbw.createForm()
            _crlin.assert_has_calls(
                [
                    call(
                        sbw,
                        0,
                        {
                            "operator": u"all the following",
                            "field": "",
                            "content": [],
                            "type": u"Categories",
                            "logical": None,
                        },
                    ),
                    call(
                        sbw,
                        1,
                        {
                            "operator": u"contains",
                            "field": u"bibtex",
                            "content": u"",
                            "type": u"Text",
                            "logical": u"AND",
                        },
                    ),
                ]
            )
            _crre.assert_called_once_with(sbw, 5)
            _crlim.assert_not_called()
        with patch(clsName + "createLine", autospec=True) as _crlin, patch(
            clsName + "createLimits", autospec=True
        ) as _crlim, patch(clsName + "createReplace", autospec=True) as _crre:
            sbw.createForm(histIndex=1)
            self.assertEqual(sbw.numberOfRows, 1)
            _crlin.assert_has_calls([call(sbw, 0, "sw")])
            _crre.assert_called_once_with(sbw, 4, previous="av")
            _crlim.assert_not_called()
        with patch(clsName + "createLine", autospec=True) as _crlin, patch(
            clsName + "createLimits", autospec=True
        ) as _crlim, patch(clsName + "createReplace", autospec=True) as _crre:
            sbw.createForm(histIndex=2)
            self.assertEqual(sbw.numberOfRows, 2)
            _crlin.assert_has_calls([call(sbw, 0, "lor"), call(sbw, 1, "th")])
            _crre.assert_called_once_with(sbw, 5, previous="hp")
            _crlim.assert_not_called()

        sbw.replace = False
        with patch(clsName + "createLine", autospec=True) as _crlin, patch(
            clsName + "createLimits", autospec=True
        ) as _crlim, patch(clsName + "createReplace", autospec=True) as _crre:
            sbw.createForm(histIndex=1)
            self.assertEqual(sbw.numberOfRows, 1)
            _crlin.assert_has_calls([call(sbw, 0, "sw")])
            _crlim.assert_called_once_with(
                sbw, 4, defLim=321, defOffs=22, override=True
            )
            _crre.assert_not_called()
        with patch(clsName + "createLine", autospec=True) as _crlin, patch(
            clsName + "createLimits", autospec=True
        ) as _crlim, patch(clsName + "createReplace", autospec=True) as _crre:
            sbw.createForm(histIndex=2)
            self.assertEqual(sbw.numberOfRows, 2)
            _crlin.assert_has_calls([call(sbw, 0, "lor"), call(sbw, 1, "th")])
            _crlim.assert_called_once_with(sbw, 5, defLim=654, defOffs=8, override=True)
            _crre.assert_not_called()


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestMergeBibtexs(GUITestCase):
    """test the MergeBibtexs class"""

    def test_init(self):
        """test __init__"""
        a = {"bibtex": "@article0"}
        b = {"bibtex": "@article1"}
        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.createForm", autospec=True
        ) as _cf:
            mb = MergeBibtexs(a, b)
            _cf.assert_called_once_with(mb)
        self.assertIsInstance(mb, EditBibtexDialog)
        self.assertEqual(mb.parent(), None)
        self.assertEqual(mb.bibtexEditLines, 8)
        self.assertEqual(mb.bibtexWidth, 330)
        self.assertEqual(mb.dataOld, {"0": a, "1": b})
        self.assertIsInstance(mb.data, dict)
        for k in pBDB.tableCols["entries"]:
            if k != "citations" and k != "citations_no_self":
                self.assertEqual(mb.data[k], "")
        self.assertEqual(mb.checkValues, {})
        self.assertEqual(mb.markValues, {})
        self.assertEqual(mb.radioButtons, {"0": {}, "1": {}})
        self.assertEqual(mb.textValues["0"], {})
        self.assertEqual(mb.textValues["1"], {})
        self.assertEqual(
            mb.checkboxes,
            [
                "exp_paper",
                "lecture",
                "phd_thesis",
                "review",
                "proceeding",
                "book",
                "noUpdate",
            ],
        )
        self.assertEqual(
            mb.generic,
            [
                "year",
                "doi",
                "arxiv",
                "inspire",
                "isbn",
                "firstdate",
                "pubdate",
                "ads",
                "scholar",
                "link",
                "comments",
                "old_keys",
                "crossref",
            ],
        )

        p = QWidget()
        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.createForm", autospec=True
        ) as _cf:
            mb = MergeBibtexs(a, b, parent=p)
            _cf.assert_called_once_with(mb)
        self.assertEqual(mb.parent(), p)

    def test_radioToggled(self):
        """test radioToggled"""
        with patch("logging.Logger.warning") as _w:
            mb = MergeBibtexs(
                {"bibkey": "0", "inspire": "0", "bibtex": '@article{0, title="0"}'},
                {"bibkey": "1", "inspire": "1", "bibtex": '@article{1, title="1"}'},
            )
        mb.radioButtons["0"]["inspire"].setChecked(True)
        mb.radioToggled("1", "inspire")
        self.assertEqual(mb.radioButtons["0"]["inspire"].isChecked(), False)
        self.assertEqual(mb.radioButtons["1"]["inspire"].isChecked(), True)
        self.assertEqual(mb.textValues["inspire"].text(), "1")
        mb.radioToggled("0", "inspire")
        self.assertEqual(mb.radioButtons["0"]["inspire"].isChecked(), True)
        self.assertEqual(mb.radioButtons["1"]["inspire"].isChecked(), False)
        self.assertEqual(mb.textValues["inspire"].text(), "0")

        mb.radioToggled("1", "bibtex")
        self.assertEqual(mb.radioButtons["0"]["bibtex"].isChecked(), False)
        self.assertEqual(mb.radioButtons["1"]["bibtex"].isChecked(), True)
        self.assertEqual(mb.textValues["bibkey"].text(), "1")
        self.assertEqual(
            mb.textValues["bibtex"].toPlainText(), '@article{1, title="1"}'
        )
        mb.radioToggled("0", "bibtex")
        self.assertEqual(mb.radioButtons["0"]["bibtex"].isChecked(), True)
        self.assertEqual(mb.radioButtons["1"]["bibtex"].isChecked(), False)
        self.assertEqual(mb.textValues["bibkey"].text(), "0")
        self.assertEqual(
            mb.textValues["bibtex"].toPlainText(), '@article{0, title="0"}'
        )

    def test_textModified(self):
        """test textModified"""
        with patch("logging.Logger.warning") as _w:
            mb = MergeBibtexs(
                {"bibkey": "0", "inspire": "0", "bibtex": "@article0"},
                {"bibkey": "1", "inspire": "1", "bibtex": "@article1"},
            )
        mb.radioButtons["0"]["inspire"].setChecked(True)
        mb.textModified("inspire")
        self.assertEqual(mb.radioButtons["0"]["inspire"].isChecked(), False)
        self.assertEqual(mb.radioButtons["1"]["inspire"].isChecked(), False)
        mb.radioButtons["1"]["inspire"].setChecked(True)
        mb.textModified("inspire")
        self.assertEqual(mb.radioButtons["0"]["inspire"].isChecked(), False)
        self.assertEqual(mb.radioButtons["1"]["inspire"].isChecked(), False)

    def test_addFieldOld(self):
        """test addFieldOld"""
        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.createForm", autospec=True
        ) as _cf:
            mb = MergeBibtexs({"bibtex": "@article0"}, {"bibtex": "@article1"})
        # clean layout
        while True:
            o = mb.layout().takeAt(0)
            if o is None:
                break
            o.widget().deleteLater()
        mb.addFieldOld("0", "year", 123, 0)
        self.assertIsInstance(mb.layout().itemAtPosition(123, 0).widget(), QLineEdit)
        self.assertEqual(
            mb.textValues["0"]["year"], mb.layout().itemAtPosition(123, 0).widget()
        )
        self.assertEqual(mb.textValues["0"]["year"].text(), "")
        self.assertEqual(mb.textValues["0"]["year"].isReadOnly(), True)

        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.createForm", autospec=True
        ) as _cf:
            mb = MergeBibtexs(
                {"bibtex": "@article0", "year": "2018"}, {"bibtex": "@article1"}
            )
        # clean layout
        while True:
            o = mb.layout().takeAt(0)
            if o is None:
                break
            o.widget().deleteLater()
        mb.addFieldOld("0", "year", 123, 0)
        self.assertIsInstance(mb.layout().itemAtPosition(123, 0).widget(), QLineEdit)
        self.assertEqual(
            mb.textValues["0"]["year"], mb.layout().itemAtPosition(123, 0).widget()
        )
        self.assertEqual(mb.textValues["0"]["year"].text(), "2018")
        self.assertEqual(mb.textValues["0"]["year"].isReadOnly(), True)

    def test_addFieldNew(self):
        """test addFieldNew"""
        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.createForm", autospec=True
        ) as _cf:
            mb = MergeBibtexs({"bibtex": "@article0"}, {"bibtex": "@article1"})
        # clean layout
        while True:
            o = mb.layout().takeAt(0)
            if o is None:
                break
            o.widget().deleteLater()
        mb.addFieldNew("year", 123, "123")
        self.assertIsInstance(mb.layout().itemAtPosition(123, 2).widget(), QLineEdit)
        self.assertEqual(
            mb.textValues["year"], mb.layout().itemAtPosition(123, 2).widget()
        )
        self.assertEqual(mb.textValues["year"].text(), "123")
        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.textModified", autospec=True
        ) as _f:
            mb.textValues["year"].textEdited.emit("321")
            _f.assert_called_once_with(mb, "year")

    def test_addRadio(self):
        """test addRadio"""
        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.createForm", autospec=True
        ) as _cf:
            mb = MergeBibtexs({"bibtex": "@article0"}, {"bibtex": "@article1"})
        # clean layout
        while True:
            o = mb.layout().takeAt(0)
            if o is None:
                break
            o.widget().deleteLater()
        mb.addRadio("0", "year", 123, 1)
        self.assertIsInstance(mb.layout().itemAtPosition(123, 1).widget(), QRadioButton)
        self.assertEqual(
            mb.radioButtons["0"]["year"], mb.layout().itemAtPosition(123, 1).widget()
        )
        self.assertEqual(mb.radioButtons["0"]["year"].text(), "")
        self.assertEqual(mb.radioButtons["0"]["year"].autoExclusive(), False)
        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.radioToggled", autospec=True
        ) as _f:
            mb.radioButtons["0"]["year"].clicked.emit()
            _f.assert_called_once_with(mb, "0", "year")

    def test_addBibtexOld(self):
        """test addBibtexOld"""
        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.createForm", autospec=True
        ) as _cf:
            mb = MergeBibtexs({"bibkey": "0"}, {"bibtex": "@article1"})
        # clean layout
        while True:
            o = mb.layout().takeAt(0)
            if o is None:
                break
            o.widget().deleteLater()
        mb.addBibtexOld("0", 123, 0)
        self.assertIsInstance(
            mb.layout().itemAtPosition(123, 0).widget(), QPlainTextEdit
        )
        self.assertEqual(
            mb.textValues["0"]["bibtex"], mb.layout().itemAtPosition(123, 0).widget()
        )
        self.assertEqual(mb.textValues["0"]["bibtex"].toPlainText(), "")
        self.assertEqual(mb.textValues["0"]["bibtex"].isReadOnly(), True)
        self.assertEqual(mb.textValues["0"]["bibtex"].minimumWidth(), mb.bibtexWidth)

        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.createForm", autospec=True
        ) as _cf:
            mb = MergeBibtexs({"bibtex": "@article0"}, {"bibtex": "@article1"})
        # clean layout
        while True:
            o = mb.layout().takeAt(0)
            if o is None:
                break
            o.widget().deleteLater()
        mb.addBibtexOld("0", 123, 0)
        self.assertIsInstance(
            mb.layout().itemAtPosition(123, 0).widget(), QPlainTextEdit
        )
        self.assertEqual(
            mb.textValues["0"]["bibtex"], mb.layout().itemAtPosition(123, 0).widget()
        )
        self.assertEqual(mb.textValues["0"]["bibtex"].toPlainText(), "@article0")
        self.assertEqual(mb.textValues["0"]["bibtex"].isReadOnly(), True)

    def test_addGenericField(self):
        """test addGenericField"""
        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.createForm", autospec=True
        ) as _cf:
            mb = MergeBibtexs(
                {"bibtex": "@article0"}, {"bibtex": "@article1", "year": "2018"}
            )
        with patch("logging.Logger.warning") as _w:
            self.assertEqual(mb.addGenericField("year", 123), 123)
            _w.assert_called_once_with("Key missing: 'year'")

        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.createForm", autospec=True
        ) as _cf:
            mb = MergeBibtexs(
                {"bibtex": "@article0", "year": "2018"},
                {"bibtex": "@article1", "year": "2018"},
            )
        self.assertEqual(mb.addGenericField("year", 123), 123)
        self.assertIsInstance(mb.textValues["year"], QLineEdit)
        self.assertEqual(mb.textValues["year"].text(), "2018")
        self.assertEqual(mb.textValues["year"].isHidden(), True)

        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.createForm", autospec=True
        ) as _cf:
            mb = MergeBibtexs(
                {"bibtex": "@article0", "year": "2017"},
                {"bibtex": "@article1", "year": "2018"},
            )
        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.addFieldOld", autospec=True
        ) as _afo, patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.addFieldNew", autospec=True
        ) as _afn, patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.addRadio", autospec=True
        ) as _ar:
            self.assertEqual(mb.addGenericField("year", 123), 125)
            _afo.assert_has_calls(
                [call(mb, "0", "year", 124, 0), call(mb, "1", "year", 124, 4)]
            )
            _ar.assert_has_calls(
                [call(mb, "0", "year", 124, 1), call(mb, "1", "year", 124, 3)]
            )
            _afn.assert_called_once_with(mb, "year", 124, "")
        self.assertIsInstance(
            mb.layout().itemAtPosition(123, 0).widget(), PBLabelCenter
        )
        self.assertEqual(
            mb.layout().itemAtPosition(123, 0).widget().text(),
            "%s (%s)" % ("year", pBDB.descriptions["entries"]["year"]),
        )

        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.createForm", autospec=True
        ) as _cf:
            mb = MergeBibtexs(
                {"bibtex": "@article0", "year": ""},
                {"bibtex": "@article1", "year": "2018"},
            )
        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.addFieldNew", autospec=True
        ) as _afn:
            self.assertEqual(mb.addGenericField("year", 123), 125)
            _afn.assert_called_once_with(mb, "year", 124, "2018")
            self.assertTrue(mb.radioButtons["1"]["year"].isChecked())
            self.assertFalse(mb.radioButtons["0"]["year"].isChecked())

        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.createForm", autospec=True
        ) as _cf:
            mb = MergeBibtexs(
                {"bibtex": "@article0", "year": "2017"},
                {"bibtex": "@article1", "year": ""},
            )
        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.addFieldNew", autospec=True
        ) as _afn:
            self.assertEqual(mb.addGenericField("year", 123), 125)
            _afn.assert_called_once_with(mb, "year", 124, "2017")
            self.assertTrue(mb.radioButtons["0"]["year"].isChecked())
            self.assertFalse(mb.radioButtons["1"]["year"].isChecked())

    def test_addMarkTypeFields(self):
        """test addMarkTypeFields"""
        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.createForm", autospec=True
        ) as _cf:
            mb = MergeBibtexs({"bibtex": "@article0"}, {"bibtex": "@article1"})
        self.assertEqual(mb.addMarkTypeFields(123), 125)
        self.assertIsInstance(mb.markValues, dict)
        for m in pBMarks.marks.keys():
            self.assertIsInstance(mb.markValues[m], QCheckBox)
        self.assertIsInstance(mb.currGrid.itemAtPosition(124, 0).widget(), QGroupBox)
        self.assertIsInstance(mb.currGrid.itemAtPosition(125, 0).widget(), QGroupBox)
        typesGB = mb.currGrid.itemAtPosition(125, 0).widget()
        self.assertEqual(typesGB.isFlat(), True)
        self.assertIsInstance(typesGB.layout(), QHBoxLayout)
        i = 0
        for k in pBDB.tableCols["entries"]:
            if k in mb.checkboxes:
                self.assertIsInstance(mb.checkValues[k], QCheckBox)
                self.assertIsInstance(typesGB.layout().itemAt(i).widget(), QCheckBox)
                self.assertEqual(mb.checkValues[k], typesGB.layout().itemAt(i).widget())
                i += 1

    def test_addBibtexFields(self):
        """test addBibtexFields"""
        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.createForm", autospec=True
        ) as _cf:
            mb = MergeBibtexs(
                {"bibtex": '@article{0, title="e0"}', "bibkey": "0"},
                {"bibtex": '@article{1, title="e1"}', "bibkey": "1"},
            )

        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.addFieldOld", autospec=True
        ) as _afo, patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.addBibtexOld", autospec=True
        ) as _abo, patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.addRadio", autospec=True
        ) as _ar:
            self.assertEqual(mb.addBibtexFields(123), 135)
            _afo.assert_has_calls(
                [call(mb, "0", "bibkey", 125, 0), call(mb, "1", "bibkey", 125, 4)]
            )
            _abo.assert_has_calls([call(mb, "0", 127, 0), call(mb, "1", 127, 4)])
            _ar.assert_has_calls(
                [call(mb, "0", "bibtex", 127, 1), call(mb, "1", "bibtex", 127, 3)]
            )
        # bibkey
        self.assertIsInstance(
            mb.currGrid.itemAtPosition(124, 0).widget(), PBLabelCenter
        )
        self.assertEqual(
            mb.currGrid.itemAtPosition(124, 0).widget().text(),
            "%s (%s)" % ("bibkey", pBDB.descriptions["entries"]["bibkey"]),
        )
        self.assertIsInstance(mb.currGrid.itemAtPosition(125, 2).widget(), QLineEdit)
        self.assertEqual(
            mb.textValues["bibkey"], mb.currGrid.itemAtPosition(125, 2).widget()
        )
        self.assertEqual(mb.textValues["bibkey"].text(), "")
        self.assertEqual(mb.textValues["bibkey"].isReadOnly(), True)

        # bibtex
        self.assertIsInstance(
            mb.currGrid.itemAtPosition(126, 0).widget(), PBLabelCenter
        )
        self.assertEqual(
            mb.currGrid.itemAtPosition(126, 0).widget().text(),
            "%s (%s)" % ("bibtex", pBDB.descriptions["entries"]["bibtex"]),
        )
        self.assertIsInstance(
            mb.currGrid.itemAtPosition(127, 2).widget(), QPlainTextEdit
        )
        self.assertEqual(
            mb.textValues["bibtex"], mb.currGrid.itemAtPosition(127, 2).widget()
        )
        self.assertEqual(mb.textValues["bibtex"].toPlainText(), "")
        self.assertEqual(mb.textValues["bibtex"].minimumWidth(), mb.bibtexWidth)
        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.textModified", autospec=True
        ) as _tm, patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog.updateBibkey", autospec=True
        ) as _ub:
            mb.textValues["bibtex"].textChanged.emit()
            _tm.assert_called_once_with(mb, "bibtex")
            _ub.assert_called_once_with(mb)

        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.createForm", autospec=True
        ) as _cf:
            mb = MergeBibtexs(
                {"bibtex": '@article{0, title="e0"}', "bibkey": "0"},
                {"bibtex": '@article{0, title="e0"}', "bibkey": "0"},
            )
        self.assertEqual(mb.addBibtexFields(123), 135)
        self.assertEqual(mb.textValues["bibkey"].text(), "0")
        self.assertEqual(
            mb.textValues["bibtex"].toPlainText(), '@article{0, title="e0"}'
        )

    def test_createForm(self):
        """test createForm"""
        with patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.addGenericField",
            side_effect=[i for i in range(1, 28)],
            autospec=True,
        ) as _agf, patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.addMarkTypeFields",
            return_value=29,
            autospec=True,
        ) as _mtf, patch(
            "physbiblio.gui.bibWindows.MergeBibtexs.addBibtexFields",
            return_value=30,
            autospec=True,
        ) as _bf, patch(
            "physbiblio.gui.commonClasses.EditObjectWindow.centerWindow", autospec=True
        ) as _cw:
            mb = MergeBibtexs({"bibtex": "@article0"}, {"bibtex": "@article1"})
            _cw.assert_called_once_with(mb)
            _agf.assert_has_calls(
                [
                    call(mb, "year", 0),
                    call(mb, "doi", 1),
                    call(mb, "arxiv", 2),
                    call(mb, "inspire", 3),
                    call(mb, "isbn", 4),
                    call(mb, "firstdate", 5),
                    call(mb, "pubdate", 6),
                    call(mb, "ads", 7),
                    call(mb, "scholar", 8),
                    call(mb, "link", 9),
                    call(mb, "comments", 10),
                    call(mb, "old_keys", 11),
                    call(mb, "crossref", 12),
                ]
            )
            _mtf.assert_called_once_with(mb, 13)
            _bf.assert_called_once_with(mb, 29)
        self.assertEqual(mb.windowTitle(), "Merge bibtex entries")
        # test ok cancel buttons
        self.assertIsInstance(mb.layout().itemAtPosition(31, 0).widget(), QPushButton)
        self.assertEqual(mb.layout().itemAtPosition(31, 0).widget(), mb.acceptButton)
        self.assertEqual(mb.acceptButton.text(), "OK")
        with patch(
            "physbiblio.gui.bibWindows.EditBibtexDialog.onOk", autospec=True
        ) as _f:
            QTest.mouseClick(mb.acceptButton, Qt.LeftButton)
            _f.assert_called_once_with(mb)
        self.assertIsInstance(mb.layout().itemAtPosition(31, 3).widget(), QPushButton)
        self.assertEqual(mb.layout().itemAtPosition(31, 3).widget(), mb.cancelButton)
        self.assertEqual(mb.cancelButton.text(), "Cancel")
        self.assertTrue(mb.cancelButton.autoDefault())
        with patch(
            "physbiblio.gui.commonClasses.EditObjectWindow.onCancel", autospec=True
        ) as _f:
            QTest.mouseClick(mb.cancelButton, Qt.LeftButton)
            _f.assert_called_once_with(mb)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestFieldsFromArxiv(GUITestCase):
    """test the FieldsFromArxiv class"""

    def test_init(self):
        """test __init__"""
        p = QWidget()
        ffa = FieldsFromArxiv()
        self.assertEqual(ffa.parent(), None)

        ffa = FieldsFromArxiv(p)
        self.assertIsInstance(ffa, PBDialog)
        self.assertEqual(ffa.parent(), p)
        self.assertEqual(ffa.windowTitle(), "Import fields from arXiv")
        self.assertEqual(
            ffa.arxivDict, ["authors", "title", "doi", "primaryclass", "archiveprefix"]
        )
        self.assertIsInstance(ffa.layout(), QVBoxLayout)

        for i, k in enumerate(
            ["authors", "title", "doi", "primaryclass", "archiveprefix"]
        ):
            self.assertIsInstance(ffa.layout().itemAt(i).widget(), QCheckBox)
            self.assertEqual(ffa.layout().itemAt(i).widget(), ffa.checkBoxes[k])
            self.assertEqual(ffa.layout().itemAt(i).widget().text(), k)
            self.assertEqual(ffa.layout().itemAt(i).widget().isChecked(), True)

        self.assertIsInstance(ffa.layout().itemAt(5).widget(), QPushButton)
        self.assertEqual(ffa.layout().itemAt(5).widget(), ffa.acceptButton)
        self.assertEqual(ffa.layout().itemAt(5).widget().text(), "OK")
        with patch(
            "physbiblio.gui.bibWindows.FieldsFromArxiv.onOk", autospec=True
        ) as _c:
            QTest.mouseClick(ffa.acceptButton, Qt.LeftButton)
            _c.assert_called_once_with(ffa)

        self.assertIsInstance(ffa.layout().itemAt(6).widget(), QPushButton)
        self.assertEqual(ffa.layout().itemAt(6).widget(), ffa.cancelButton)
        self.assertEqual(ffa.layout().itemAt(6).widget().autoDefault(), True)
        self.assertEqual(ffa.layout().itemAt(6).widget().text(), "Cancel")
        with patch(
            "physbiblio.gui.bibWindows.FieldsFromArxiv.onCancel", autospec=True
        ) as _c:
            QTest.mouseClick(ffa.cancelButton, Qt.LeftButton)
            _c.assert_called_once_with(ffa)

    def test_onOk(self):
        """test onOk"""
        p = QWidget()
        ffa = FieldsFromArxiv(p)
        ffa.checkBoxes["doi"].setChecked(False)
        ffa.checkBoxes["title"].setChecked(False)
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            ffa.onOk()
            self.assertEqual(_c.call_count, 1)
        self.assertTrue(ffa.result)
        self.assertTrue(hasattr(ffa, "output"))
        self.assertIsInstance(ffa.output, list)
        self.assertEqual(ffa.output, ["archiveprefix", "authors", "primaryclass"])

    def test_onCancel(self):
        """test onCancel"""
        p = QWidget()
        ffa = FieldsFromArxiv(p)
        with patch("PySide2.QtWidgets.QDialog.close", autospec=True) as _c:
            ffa.onCancel()
            self.assertEqual(_c.call_count, 1)
        self.assertFalse(ffa.result)
        self.assertEqual(ffa.output, [])


if __name__ == "__main__":
    unittest.main()
