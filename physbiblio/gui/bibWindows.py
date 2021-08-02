"""Module with the classes and functions that manage
the entries windows and panels.

This file is part of the physbiblio package.
"""
import ast
import datetime
import os
import re
import traceback

import bibtexparser
import matplotlib
import six

matplotlib.use("Qt5Agg")
os.environ["QT_API"] = "pyside2"

from matplotlib.backends.backend_agg import FigureCanvasAgg
from pylatexenc.latex2text import LatexNodes2Text
from pyparsing import ParseException
from PySide2.QtCore import QEvent, Qt, QUrl
from PySide2.QtGui import QCursor, QFont, QIcon, QImage, QTextDocument
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

try:
    import physbiblio.gui.resourcesPyside2
    from physbiblio.config import pbConfig
    from physbiblio.database import pBDB
    from physbiblio.errors import pBLogger
    from physbiblio.gui.basicDialogs import (
        askDirName,
        askFileName,
        askYesNo,
        infoMessage,
    )
    from physbiblio.gui.catWindows import CatsTreeWindow
    from physbiblio.gui.commonClasses import (
        EditObjectWindow,
        ObjListWindow,
        PBAndOrCombo,
        PBComboBox,
        PBDialog,
        PBLabel,
        PBLabelCenter,
        PBLabelRight,
        PBMenu,
        PBTableModel,
        pBGuiView,
    )
    from physbiblio.gui.errorManager import pBGUILogger
    from physbiblio.gui.expWindows import ExpsListWindow
    from physbiblio.gui.marks import pBMarks
    from physbiblio.gui.threadElements import Thread_downloadArxiv, Thread_processLatex
    from physbiblio.parseAccents import texToHtml
    from physbiblio.pdf import pBPDF
    from physbiblio.strings.gui import BibWindowsStrings as bwstr
    from physbiblio.strings.main import DatabaseStrings as dstr
    from physbiblio.webimport.webInterf import physBiblioWeb
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())

convertType = {
    "review": dstr.Bibs.review,
    "proceeding": dstr.Bibs.proceeding,
    "book": dstr.Bibs.book,
    "phd_thesis": dstr.Bibs.phdth,
    "lecture": dstr.Bibs.lecture,
    "exp_paper": dstr.Bibs.experimental,
}


def copyToClipboard(text):
    """Copy the given text to the clipboard

    Parameter:
        text: the string to be copied to clipboard
    """
    pBLogger.info(bwstr.copyToClipb % text)
    clipboard = QApplication.clipboard()
    clipboard.setText(text)


def writeBibtexInfo(entry):
    """Use the database information in order to write a short text
    that contains some relevant info on the bibtex entry,
    such as type, title, authors, journal and identification info.

    Parameter:
        entry: the database record from which to extract the info

    Output:
        a string
    """
    infoText = ""
    nl = "<br/>\n"
    for t in sorted(convertType.keys()):
        try:
            if entry[t] == 1:
                infoText += "(%s) " % convertType[t]
        except KeyError:
            pBLogger.debug("KeyError: '%s' not in %s" % (t, sorted(entry.keys())))
    infoText += (
        "<u>%s</u> " % entry["bibkey"] + bwstr.Info.useWith % entry["bibkey"] + nl
    )
    latexToText = LatexNodes2Text(math_mode="verbatim", keep_comments=False)
    try:
        infoText += (
            bwstr.Info.author
            % (latexToText.latex_to_text(entry["bibtexDict"]["author"]))
            + nl
        )
    except KeyError:
        pBLogger.debug(
            bwstr.Info.keyErr % ("author", sorted(entry["bibtexDict"].keys()))
        )
    try:
        infoText += (
            "%s" % (latexToText.latex_to_text(entry["bibtexDict"]["title"])) + nl
        )
    except KeyError:
        pBLogger.debug(
            bwstr.Info.keyErr % ("title", sorted(entry["bibtexDict"].keys()))
        )
    try:
        infoText += (
            "<i>%s %s (%s) %s</i>"
            % (
                entry["bibtexDict"]["journal"],
                entry["bibtexDict"]["volume"],
                entry["bibtexDict"]["year"],
                entry["bibtexDict"]["pages"],
            )
            + nl
        )
    except KeyError:
        pBLogger.debug(bwstr.Info.pubErr % (sorted(entry["bibtexDict"].keys())))
    infoText += nl
    for k in ["isbn", "doi", "arxiv", "ads", "inspire"]:
        try:
            infoText += (
                ("%s: <u>%s</u>" % (pBDB.descriptions["entries"][k], entry[k]) + nl)
                if (entry[k] is not None and entry[k] != "")
                else ""
            )
        except KeyError:
            pBLogger.debug(bwstr.Info.keyErr % (k, sorted(entry.keys())))
    infoText += nl
    try:
        if entry["citations"] > 0:
            infoText += bwstr.Info.citIns % entry["citations"]
            if entry["citations_no_self"] > 0:
                infoText += bwstr.Info.citNoSelf % entry["citations_no_self"]
            infoText += nl
    except KeyError:
        pass
    cats = pBDB.cats.getByEntry(entry["bibkey"])
    infoText += bwstr.Info.cats % (
        ", ".join([c["name"] for c in cats]) if len(cats) > 0 else "None"
    )
    exps = pBDB.exps.getByEntry(entry["bibkey"])
    infoText += nl + bwstr.Info.exps % (
        ", ".join([e["name"] for e in exps]) if len(exps) > 0 else "None"
    )
    try:
        if (
            isinstance(entry["comments"], six.string_types)
            and entry["comments"].strip() != ""
        ):
            infoText += nl + bwstr.Info.comm % (entry["comments"])
    except KeyError:
        pBLogger.debug(bwstr.Info.keyErr % ("comments", sorted(entry.keys())))
    return infoText


def writeAbstract(mainWin, entry):
    """Process and write the abstract to the dedicated mainWindow panel

    Parameters:
        mainWin: the `mainWindow` instance where to write the abstract
        entry: the database record of the entry
    """
    a = AbstractFormulas(mainWin, entry["abstract"])
    a.doText()


def editBibtex(parentObject, editKey=None):
    """Open a dialog (`EditBibtexDialog`) to edit a bibtex entry
    and process the output.

    Parameters:
        parentObject: the parent widget
        editKey: the key of the entry to be edited,
            or `None` to create a new one
    """
    newBibWin = EditBibtexDialog(
        parentObject,
        bib=pBDB.bibs.getByBibkey(editKey, saveQuery=False)[0]
        if editKey is not None
        else None,
    )
    newBibWin.exec_()
    data = {}
    if newBibWin.result:
        for k in ["citations", "citations_no_self"]:
            try:
                data[k] = getattr(newBibWin, k)
            except AttributeError:
                data[k] = 0
        for k, v in newBibWin.textValues.items():
            try:
                s = "%s" % v.text()
            except AttributeError:
                s = "%s" % v.toPlainText()
            data[k] = s
        for k, v in newBibWin.checkValues.items():
            if v.isChecked():
                data[k] = 1
            else:
                data[k] = 0
        data["marks"] = ""
        for m, ckb in newBibWin.markValues.items():
            if ckb.isChecked():
                data["marks"] += "%s," % m
        failed = False
        data["abstract"] = ""
        if data["bibtex"].strip() != "":
            try:
                tmpBibDict = bibtexparser.loads(data["bibtex"]).entries[0]
            except IndexError:
                tmpBibDict = {}
            except ParseException:
                pBLogger.warning(
                    bwstr.parseBibErr % data["bibtex"],
                    exc_info=True,
                )
                tmpBibDict = {}
            data["bibdict"] = "%s" % tmpBibDict
            # if some fields are empty, use bibtex info:
            if data["arxiv"] == "":
                if "arxiv" in tmpBibDict.keys() and tmpBibDict["arxiv"] != "":
                    data["arxiv"] = tmpBibDict["arxiv"]
                elif "eprint" in tmpBibDict.keys() and tmpBibDict["eprint"] != "":
                    data["arxiv"] = tmpBibDict["eprint"]
            for f in ["year", "doi", "isbn"]:
                if f in tmpBibDict.keys() and tmpBibDict[f] != "":
                    data[f] = tmpBibDict[f]
            if data["firstdate"] == "":
                data["firstdate"] = datetime.date.today().strftime("%Y-%m-%d")
            # if bibkey is empty, compute it from bibtex
            if "bibkey" not in data.keys() or data["bibkey"].strip() == "":
                data = pBDB.bibs.prepareInsert(data["bibtex"].strip())
            if data["bibkey"].strip() != "":
                if editKey is not None:
                    if data["bibkey"].strip() != editKey:
                        if data["bibkey"].strip() != bwstr.ED.notValidTex:
                            pBLogger.info(bwstr.newKey % (data["bibkey"], editKey))
                            if editKey not in data["old_keys"]:
                                data["old_keys"] += " " + editKey
                                data["old_keys"] = data["old_keys"].strip()
                            if pBDB.bibs.updateBibkey(editKey, data["bibkey"].strip()):
                                pBPDF.renameFolder(editKey, data["bibkey"].strip())
                            else:
                                pBGUILogger.warning(bwstr.cantUpdateKey)
                                data["bibtex"] = data["bibtex"].replace(
                                    data["bibkey"], editKey
                                )
                                data["bibkey"] = editKey
                        else:
                            data["bibkey"] = editKey
                    pBLogger.info(bwstr.updateKey % data["bibkey"])
                    if not pBDB.bibs.update(data, data["bibkey"]):
                        failed = True
                else:
                    if not pBDB.bibs.insert(data):
                        failed = True
                if failed:
                    message = bwstr.cantInsMod
                    pBGUILogger.error(message)
                else:
                    message = bwstr.bibSaved
                    try:
                        parentObject.mainWindowTitle(bwstr.winTitleModified)
                    except AttributeError:
                        pBLogger.debug(
                            bwstr.noAttribute % ("parentObject", "mainWindowTitle"),
                            exc_info=True,
                        )
                pBDB.bibs.fetchFromLast()
                try:
                    parentObject.reloadMainContent(pBDB.bibs.lastFetched)
                except AttributeError:
                    pBLogger.debug(
                        bwstr.noAttribute % ("parentObject", "reloadMainContent"),
                        exc_info=True,
                    )
            else:
                message = bwstr.emptyKey
                infoMessage(message)
        else:
            message = bwstr.emptyBib
            infoMessage(message)
    else:
        message = bwstr.noModif
    try:
        parentObject.statusBarMessage(message)
    except AttributeError:
        pBLogger.debug(
            bwstr.noAttribute % ("parentObject", "statusBarMessage"), exc_info=True
        )


def deleteBibtex(parentObject, bibkey):
    """Ask confirmation and eventually delete the selected bibtex entry

    Parameters:
        parentObject: the parent object, which has
            the `currentTabWidget`, `statusBarMessage`
            and `setWindowTitle` methods
        bibkey: the bibtex key of the entry to be deleted
    """
    if askYesNo(bwstr.deleteAsk % (bibkey)):
        pBDB.bibs.delete(bibkey)
        parentObject.setWindowTitle(bwstr.winTitleModified)
        message = bwstr.deleted
        try:
            parentObject.currentTabWidget().recreateTable()
        except AttributeError:
            pBLogger.debug(
                bwstr.noAttribute % ("parentObject", "recreateTable"), exc_info=True
            )
    else:
        message = bwstr.nothingChanged
    try:
        parentObject.statusBarMessage(message)
    except AttributeError:
        pBLogger.debug(
            bwstr.noAttribute % ("parentObject", "statusBarMessage"), exc_info=True
        )


class AbstractFormulas:
    """Class that manages the transformation of the math formulas
    which appear in the abstract into images"""

    def __init__(
        self,
        mainWin,
        text,
        fontsize=pbConfig.params["bibListFontSize"],
        abstractTitle=bwstr.abstractTitle,
        customEditor=None,
        statusMessages=True,
    ):
        """Prepare the settings and the given text

        Parameters:
            mainWin: the main window object
            text: the text to be processed
            fontsize: the size of the font used to write the text
                (default: taken from the configuration parameters)
            abstractTitle: a title which will be written before
                the processed abstract
                (default: "<b>Abstract:</b><br/>")
            customEditor: the place where to save the text
                (default: `mainWin.bottomCenter.text`)
            statusMessages: if True (default), write messages
                in the statusbar
        """
        self.fontsize = fontsize
        self.mainWin = mainWin
        self.statusMessages = statusMessages
        self.thr = None
        self.editor = (
            self.mainWin.bottomCenter.text if customEditor is None else customEditor
        )
        self.document = QTextDocument()
        self.editor.setDocument(self.document)
        self.abstractTitle = abstractTitle
        text = str(text)
        self.text = abstractTitle + texToHtml(text).replace("\n", " ")

    def hasLatex(self):
        """Return a boolean which indicates if there is math
        in the abstract, based on the presence of "$" in the text

        Output:
            a boolean
        """
        return "$" in self.text

    def doText(self):
        """Convert the text using the `Thread_processLatex` thread
        to perform the conversion without freezing the main process
        """
        if self.hasLatex():
            self.mainWin.statusBarMessage(bwstr.parseLatex)
            self.editor.setHtml(bwstr.processLatex % self.abstractTitle)
            self.thr = Thread_processLatex(self.prepareText, self.mainWin)
            self.thr.passData.connect(self.submitText)
            self.thr.start()
        else:
            self.editor.setHtml(self.text)

    def mathTex_to_QPixmap(self, mathTex):
        """Create a `matplotlib` figure with the equation
        that is given as a parameter

        Parameter:
            mathTex: the text to be converted into an image

        Output:
            a `QImage`
        """
        fig = matplotlib.figure.Figure()
        fig.patch.set_facecolor("none")
        fig.set_canvas(FigureCanvasAgg(fig))
        renderer = fig.canvas.get_renderer()

        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("off")
        ax.patch.set_facecolor("none")
        t = ax.text(0, 0, mathTex, ha="left", va="bottom", fontsize=self.fontsize)

        fwidth, fheight = fig.get_size_inches()
        fig_bbox = fig.get_window_extent(renderer)

        try:
            text_bbox = t.get_window_extent(renderer)
        except ValueError:
            pBLogger.exception(bwstr.errorLatexImg)
            return None

        tight_fwidth = text_bbox.width * fwidth / fig_bbox.width
        tight_fheight = text_bbox.height * fheight / fig_bbox.height

        fig.set_size_inches(tight_fwidth, tight_fheight)

        buf, size = fig.canvas.print_to_buffer()
        qimage = QImage.rgbSwapped(QImage(buf, size[0], size[1], QImage.Format_ARGB32))
        return qimage

    def prepareText(self):
        """Split the text into regular text and formulas
        and prepare the the images which will be inserted
        in the `QTextEdit` instead of the formulas
        """
        matchFormula = re.compile("\$.*?\$", re.MULTILINE)
        mathTexts = [q.group() for q in matchFormula.finditer(self.text)]

        images = []
        text = self.text
        for i, t in enumerate(mathTexts):
            images.append(self.mathTex_to_QPixmap(t))
            text = text.replace(t, '<img src="mydata://image%d.png" />' % i)
        return images, text

    def submitText(self, imgs, text):
        """Prepare the `QTextDocument` with all the processed images
        and insert them in the `QTextEdit`
        """
        for i, image in enumerate(imgs):
            self.document.addResource(
                QTextDocument.ImageResource, QUrl("mydata://image%d.png" % i), image
            )
        self.editor.setHtml(text)
        if self.statusMessages:
            self.mainWin.statusBarMessage(bwstr.latexDone)


class BibtexInfo(QFrame):
    """`QFrame` extension to create a panel where to write
    some info about the selected bibtex entry"""

    def __init__(self, parent=None):
        """Extension of `QFrame.__init__`, also adds a layout
        and a QTextEdit to the frame

        Parameter:
            parent: the parent widget
        """
        super(BibtexInfo, self).__init__(parent)

        self.currLayout = QHBoxLayout()
        self.setLayout(self.currLayout)

        self.text = QTextEdit("")
        font = QFont()
        font.setPointSize(pbConfig.params["bibListFontSize"])
        self.text.setFont(font)
        self.text.setReadOnly(True)

        self.currLayout.addWidget(self.text)


class BibTableModel(PBTableModel):
    """The model (based on `PBTableModel`)
    which manages the list of bibtex entries
    """

    def __init__(
        self,
        parent,
        bib_list,
        header,
        stdCols=[],
        addCols=[],
        askBibs=False,
        previous=[],
        mainWin=None,
        *args
    ):
        """Constructor of the model, defines some properties
        and uses `PBTableModel.__init__`

        Parameters:
            parent: the parent widget
            bib_list: the list of bibtex entries in the model
            header: the names of the columns to be used
            stdCols (default []): the list of standard columns
                (the ones that are also fields in the database table)
            addCols (default []): the list of non-standard columns
                (the ones that are not fields in the database table,
                as "Type" or "PDF")
            askBibs: if True (default False),
                enable the checkboxes for selection
            previous (default []): the list of initially selected items
            mainWin: None (default) or a MainWindow instance
        """
        self.mainWin = mainWin
        self.latexToText = LatexNodes2Text(math_mode="text", keep_comments=False)
        self.typeClass = "Bibs"
        self.dataList = bib_list
        PBTableModel.__init__(
            self, parent, header + ["bibtex"], askBibs, previous, *args
        )
        self.stdCols = stdCols
        self.addCols = addCols + ["bibtex"]
        self.lenStdCols = len(stdCols)
        self.prepareSelected()

    def getIdentifier(self, element):
        """Get the bibkey that uniquely identifies an element

        Parameter:
            element: the database record of the bibtex entry

        Output:
            the bibtex key
        """
        return element["bibkey"]

    def addTypeCell(self, data):
        """Create cell for describing the type of an entry

        Parameter:
            data: the database record of the entry

        Output:
            a string with the list of types
        """
        someType = False
        string = ""
        for t in sorted(convertType.keys()):
            try:
                if data[t] == 1:
                    if someType:
                        string += ", "
                    string += convertType[t]
                    someType = True
            except KeyError:
                pBLogger.debug(
                    "Key not present: '%s'\nin %s" % (t, sorted(data.keys()))
                )
        return string

    def addPDFCell(self, key):
        """Create cell for the PDF file

        Parameter:
            key: the database key of the entry

        Output:
            a tuple, containing:
                True and an image
                or
                False and the string "no PDF"
        """
        if len(pBPDF.getExisting(key)) > 0:
            return (
                True,
                self.addImage(
                    ":/images/application-pdf.png",
                    self.parentObj.tableview.rowHeight(0) * 0.9,
                ),
            )
        else:
            return False, bwstr.noPDF

    def addMarksCell(self, marks):
        """Create a cell for the marks

        Parameter:
            marks: the marks of the given entry

        Output:
            a tuple, containing:
                True and an image or a list of images
                or
                False and ""
        """
        if marks is not None and isinstance(marks, six.string_types):
            marks = [k for k in sorted(pBMarks.marks.keys()) if k in marks]
            if len(marks) > 1:
                return (
                    True,
                    self.addImages(
                        [pBMarks.marks[img]["icon"] for img in marks],
                        self.parentObj.tableview.rowHeight(0) * 0.9,
                    ),
                )
            elif len(marks) > 0:
                return (
                    True,
                    self.addImage(
                        pBMarks.marks[marks[0]]["icon"],
                        self.parentObj.tableview.rowHeight(0) * 0.9,
                    ),
                )
            else:
                return False, ""
        else:
            return False, ""

    def data(self, index, role):
        """Return the cell data for the given index and role

        Parameters:
            index: the `QModelIndex` for which the data are required
            role: the desired Qt role for the data

        Output:
            None if the index or the role are not valid,
            the cell content or properties otherwise
        """
        if not index.isValid():
            return None
        hasImg = False
        row = index.row()
        column = index.column()
        try:
            rowData = self.dataList[row]
        except IndexError:
            pBGUILogger.exception(bwstr.btmdInvalid % "row")
            return None
        try:
            colName = self.header[column]
        except IndexError:
            pBGUILogger.exception(bwstr.btmdInvalid % "column")
            return None
        if colName == "marks":
            try:
                hasImg, value = self.addMarksCell(rowData["marks"])
            except KeyError:
                pBLogger.debug(bwstr.missMarks % rowData.keys())
                hasImg, value = self.addMarksCell("")
        elif colName == "Type":
            value = self.addTypeCell(rowData)
        elif colName == "PDF":
            hasImg, value = self.addPDFCell(rowData["bibkey"])
        else:
            try:
                value = rowData[colName]
                if colName in ["title", "author"]:
                    value = self.latexToText.latex_to_text(value)
            except KeyError:
                value = ""

        if role == Qt.CheckStateRole and self.ask and column == 0:
            if self.selectedElements[rowData["bibkey"]] == True:
                return Qt.Checked
            else:
                return Qt.Unchecked
        elif role == Qt.EditRole:
            return value
        elif role == Qt.DecorationRole and hasImg:
            return value
        elif role == Qt.DisplayRole and not hasImg:
            return value
        return None

    def setData(self, index, value, role):
        """Set the cell data for the given index and role

        Parameters:
            index: the `QModelIndex` for which the data are required
            value: the new data value
            role: the desired Qt role for the data

        Output:
            True if correctly completed,
            False if the `index` is not valid
        """
        if not index.isValid():
            return False
        if role == Qt.CheckStateRole and index.column() == 0:
            if value == Qt.Checked:
                self.selectedElements[self.dataList[index.row()]["bibkey"]] = True
            else:
                self.selectedElements[self.dataList[index.row()]["bibkey"]] = False

        self.dataChanged.emit(index, index)
        return True


class CommonBibActions:
    """Class that contains actions and menu functions
    in use inside of other bibWindows classes
    """

    def __init__(self, bibs, parent=None):
        """Set basic properties

        Parameter:
            bibs: the list of bibtex entries to be managed
            parent (default None): the parent widget
        """
        self.bibs = bibs
        self.keys = [e["bibkey"] for e in bibs]
        self.parentObj = parent
        self.menu = None
        self.downArxiv_thr = []

    def parent(self):
        """Return the parent widget"""
        return self.parentObj

    def _createMenuArxiv(self, selection, arxiv):
        """Create part of the right click menu,
        concerning the arXiv-related functions

        Parameters:
            selection: if the menu is for a multiple entries selection
                or for a right-click event on a single entry
            arxiv: the arxiv number of the bibtex record
        """
        if selection or (not selection and (arxiv != "" and arxiv is not None)):
            menuA = []
            menuA.append(QAction(bwstr.Acts.arxLoad, self.menu, triggered=self.onAbs))
            menuA.append(QAction(bwstr.Acts.arxMore, self.menu, triggered=self.onArx))
            self.menu.possibleActions.append([bwstr.Acts.arxTit, menuA])

    def _createMenuCopy(self, selection, initialRecord):
        """Create part of the right click menu,
        concerning the copy to clipboard functions

        Parameters:
            selection: if the menu is for a multiple entries selection
                or for a right-click event on a single entry
            initialRecord: the bibtex record to be used
        """
        menuC = [
            QAction(bwstr.Acts.cpKey, self.menu, triggered=self.onCopyKeys),
            QAction(bwstr.Acts.cpCite, self.menu, triggered=self.onCopyCites),
            QAction(bwstr.Acts.cpBib, self.menu, triggered=self.onCopyBibtexs),
        ]
        subm = []
        latexToText = LatexNodes2Text(math_mode="verbatim", keep_comments=False)
        if not selection:
            for field in [
                "abstract",
                "arXiv",
                "DOI",
                "INSPIRE",
                "link",
                "authors",
                "journal",
                "published",
                "title",
                "bibitem",
            ]:
                convert_to_latex = True
                if field == "published":
                    try:
                        content = "%s %s (%s) %s" % (
                            initialRecord["bibtexDict"]["journal"],
                            initialRecord["bibtexDict"]["volume"],
                            initialRecord["bibtexDict"]["year"],
                            initialRecord["bibtexDict"]["pages"],
                        )
                    except KeyError:
                        pBLogger.debug(
                            bwstr.Acts.notFoundFor
                            % (
                                "journal', 'volume', 'year' or 'pages",
                                initialRecord["bibkey"],
                            )
                        )
                        content = ""
                elif field == "bibitem":
                    convert_to_latex = False
                    content = r"\bibitem{" + "%s" % initialRecord["bibkey"] + "}\n"
                    try:
                        content += initialRecord["bibtexDict"]["authors"] + "\n"
                    except KeyError:
                        pBLogger.debug(
                            bwstr.Acts.notFoundFor
                            % ("authors", initialRecord["bibkey"])
                        )
                        try:
                            content += initialRecord["bibtexDict"]["author"] + "\n"
                        except KeyError:
                            pBLogger.debug(
                                bwstr.Acts.notFoundFor
                                % ("author", initialRecord["bibkey"])
                            )
                    try:
                        content += (
                            "% " + "%s" % initialRecord["bibtexDict"]["title"] + "\n"
                        )
                    except KeyError:
                        pBLogger.debug(
                            bwstr.Acts.notFoundFor % ("title", initialRecord["bibkey"])
                        )
                    try:
                        content += "%s %s (%s) %s\n" % (
                            initialRecord["bibtexDict"]["journal"],
                            initialRecord["bibtexDict"]["volume"],
                            initialRecord["bibtexDict"]["year"],
                            initialRecord["bibtexDict"]["pages"],
                        )
                    except KeyError:
                        pBLogger.debug(
                            bwstr.Acts.notFoundFor
                            % (
                                "journal', 'volume', " + "'year' or 'pages",
                                initialRecord["bibkey"],
                            )
                        )
                    try:
                        if (
                            initialRecord["doi"] is not None
                            and initialRecord["doi"] != ""
                        ):
                            content += "doi: %s\n" % initialRecord["doi"]
                    except KeyError:
                        pBLogger.debug(
                            bwstr.Acts.notFoundFor % ("doi", initialRecord["bibkey"])
                        )
                    try:
                        if (
                            initialRecord["arxiv"] is not None
                            and initialRecord["arxiv"] != ""
                        ):
                            content += "[arxiv:%s]\n" % initialRecord["arxiv"]
                    except KeyError:
                        pBLogger.debug(
                            bwstr.Acts.notFoundFor % ("arxiv", initialRecord["bibkey"])
                        )
                    content = content[:-1] + "."
                else:
                    try:
                        content = initialRecord[field.lower()]
                    except KeyError:
                        try:
                            content = initialRecord["bibtexDict"][field.lower()]
                        except KeyError:
                            pBLogger.debug(
                                bwstr.Acts.notFoundFor
                                % (field, initialRecord["bibkey"])
                            )
                            content = ""
                if content is not None and content.strip() != "":
                    c = (
                        latexToText.latex_to_text(content)
                        if convert_to_latex
                        else content
                    )
                    subm.append(
                        QAction(
                            field, self.menu, triggered=lambda t=c: copyToClipboard(t)
                        )
                    )
        if len(subm) > 0:
            menuC.append(None)
            for s in subm:
                menuC.append(s)
        menuC.append(None)
        menuC.append(
            QAction(bwstr.Acts.cpDir, self.menu, triggered=self.onCopyDir),
        )
        self.menu.possibleActions.append([bwstr.Acts.cpTit, menuC])

    def _createMenuInspire(self, selection, inspireID):
        """Create part of the right click menu,
        concerning the INSPIRE-HEP-related functions

        Parameters:
            selection: if the menu is for a multiple entries selection
                or for a right-click event on a single entry
            inspireID: the inspire ID of the bibtex record
        """
        menuI = []
        menuI.append(
            QAction(
                bwstr.Acts.insCompl,
                self.menu,
                triggered=self.onComplete,
            )
        )
        if selection or (not selection and inspireID):
            menuI.append(
                QAction(
                    bwstr.Acts.insUpd,
                    self.menu,
                    triggered=lambda r=True: self.onUpdate(force=r),
                )
            )
            menuI.append(
                QAction(
                    bwstr.Acts.insRel,
                    self.menu,
                    triggered=lambda f=(not selection), r=True: self.onUpdate(
                        force=f, reloadAll=r
                    ),
                )
            )
            menuI.append(
                QAction(bwstr.Acts.insCit, self.menu, triggered=self.onCitations)
            )
            menuI.append(
                QAction(bwstr.Acts.insCitCo, self.menu, triggered=self.onCitationCount)
            )
            self.menu.possibleActions.append([bwstr.Acts.insTit, menuI])
        else:
            menuI[-1].setToolTip(bwstr.Acts.insComplTip)
            self.menu.possibleActions.append(
                {"title": bwstr.Acts.insTit, "actions": menuI, "toolTipsVisible": True}
            )

    def _createMenuLinks(self, bibkey, arxiv, doi, inspireID):
        """Create part of the right click menu,
        concerning the links-related functions

        Parameters:
            bibkey: the key of the bibtex record
            arxiv: the arXiv ID of the bibtex record
            doi: the DOI of the bibtex record
            inspireID: the inspire ID of the bibtex record
        """
        menuL = []
        if arxiv is not None and arxiv != "":
            menuL.append(
                QAction(
                    bwstr.Acts.lnArx,
                    self.menu,
                    triggered=lambda l=bibkey, t="arxiv": pBGuiView.openLink(l, t),
                )
            )
        if doi is not None and doi != "":
            menuL.append(
                QAction(
                    bwstr.Acts.lnDoi,
                    self.menu,
                    triggered=lambda l=bibkey, t="doi": pBGuiView.openLink(l, t),
                )
            )
        if inspireID is not None and inspireID != "":
            menuL.append(
                QAction(
                    bwstr.Acts.lnIns,
                    self.menu,
                    triggered=lambda l=bibkey, t="inspire": pBGuiView.openLink(l, t),
                )
            )
        if len(menuL) > 0:
            self.menu.possibleActions.append([bwstr.Acts.lnTit, menuL])

    def _createMenuMarkType(self, initialRecord):
        """Create part of the right click menu,
        concerning marks and types

        Parameter:
            initialRecord: the bibtex record to be used
        """
        menuM = []
        for m in sorted(pBMarks.marks.keys()):
            menuM.append(
                QAction(
                    (
                        bwstr.Acts.maRem
                        if m in initialRecord["marks"]
                        else bwstr.Acts.maAdd
                    )
                    % pBMarks.marks[m]["desc"],
                    self.menu,
                    triggered=lambda m=m: self.onUpdateMark(m),
                )
            )
        menuT = []
        for k, v in sorted(convertType.items()):
            menuT.append(
                QAction(
                    (bwstr.Acts.tyRem if initialRecord[k] else bwstr.Acts.tyAdd) % v,
                    self.menu,
                    triggered=lambda t=k: self.onUpdateType(t),
                )
            )
        self.menu.possibleActions.append([bwstr.Acts.maTit, menuM])
        self.menu.possibleActions.append([bwstr.Acts.tyTit, menuT])
        self.menu.possibleActions.append(None)

    def _createMenuMarkTypeList(self):
        """Create part of the right click menu,
        concerning marks and types in case a list of items is selected
        """
        menuM = []
        for m in sorted(pBMarks.marks.keys()):
            menuM.append(
                QAction(
                    bwstr.Acts.maAddL % pBMarks.marks[m]["desc"],
                    self.menu,
                    triggered=lambda m=m: self.onUpdateMark(m, force=1),
                )
            )
            menuM.append(
                QAction(
                    bwstr.Acts.maRemL % pBMarks.marks[m]["desc"],
                    self.menu,
                    triggered=lambda m=m: self.onUpdateMark(m, force=0),
                )
            )
        menuT = []
        for k, v in sorted(convertType.items()):
            menuT.append(
                QAction(
                    bwstr.Acts.tyAddL % v,
                    self.menu,
                    triggered=lambda t=k: self.onUpdateType(t, force=1),
                )
            )
            menuT.append(
                QAction(
                    bwstr.Acts.tyRemL % v,
                    self.menu,
                    triggered=lambda t=k: self.onUpdateType(t, force=0),
                )
            )
        self.menu.possibleActions.append([bwstr.Acts.maTit, menuM])
        self.menu.possibleActions.append([bwstr.Acts.tyTit, menuT])
        self.menu.possibleActions.append(None)

    def _createMenuPDF(self, selection, initialRecord):
        """Create part of the right click menu,
        concerning the PDF functions

        Parameters:
            selection: if the menu is for a multiple entries selection
                or for a right-click event on a single entry
            initialRecord: the bibtex record to be used
        """
        if not selection:
            bibkey = initialRecord["bibkey"]
            arxiv = initialRecord["arxiv"]
            doi = initialRecord["doi"]
            menuP = []
            files = pBPDF.getExisting(bibkey, fullPath=True)
            arxivFile = pBPDF.getFilePath(bibkey, "arxiv")
            doiFile = pBPDF.getFilePath(bibkey, "doi")
            pdfDir = pBPDF.getFileDir(bibkey)
            shortfiles = {f.replace(pdfDir + os.sep, ""): f for f in files}
            if arxivFile in files:
                menuP.append(
                    QAction(
                        bwstr.Acts.pdfO % "arXiv",
                        self.menu,
                        triggered=lambda k=bibkey, t="file", f=arxivFile: pBGuiView.openLink(
                            k, t, fileArg=f
                        ),
                    )
                )
            if doiFile in files:
                menuP.append(
                    QAction(
                        bwstr.Acts.pdfO % "DOI",
                        self.menu,
                        triggered=lambda k=bibkey, t="file", f=doiFile: pBGuiView.openLink(
                            k, t, fileArg=f
                        ),
                    )
                )
            for fn in sorted(shortfiles):
                f = shortfiles[fn]
                if f not in [arxivFile, doiFile]:
                    menuP.append(
                        QAction(
                            bwstr.Acts.pdfOpen % fn,
                            self.menu,
                            triggered=lambda k=bibkey, t="file", f=f: pBGuiView.openLink(
                                k, t, fileArg=f
                            ),
                        )
                    )
            if len(menuP) > 0:
                menuP.append(None)
            menuP.append(QAction(bwstr.Acts.pdfGen, self.menu, triggered=self.onAddPDF))
            if len(files) > 0:
                menuP.append(None)
            if arxivFile in files:
                files.remove(arxivFile)
                tmpM = []
                tmpM.append(
                    QAction(
                        bwstr.Acts.pdfD % "arXiv",
                        self.menu,
                        triggered=lambda k=bibkey, a="arxiv", t="arxiv PDF": self.onDeletePDFFile(
                            k, a, t
                        ),
                    )
                )
                tmpM.append(
                    QAction(
                        bwstr.Acts.pdfC % "arXiv",
                        self.menu,
                        triggered=lambda k=bibkey, a="arxiv": self.onCopyPDFFile(k, a),
                    )
                )
                menuP.append([bwstr.Acts.pdfM % "arXiv", tmpM])
            elif arxiv is not None and arxiv != "":
                menuP.append(
                    QAction(bwstr.Acts.pdfArxW, self.menu, triggered=self.onDown)
                )
            if doiFile in files:
                files.remove(doiFile)
                tmpM = []
                tmpM.append(
                    QAction(
                        bwstr.Acts.pdfD % "DOI",
                        self.menu,
                        triggered=lambda k=bibkey, a="doi", t="DOI PDF": self.onDeletePDFFile(
                            k, a, t
                        ),
                    )
                )
                tmpM.append(
                    QAction(
                        bwstr.Acts.pdfC % "DOI",
                        self.menu,
                        triggered=lambda k=bibkey, a="doi": self.onCopyPDFFile(k, a),
                    )
                )
                menuP.append([bwstr.Acts.pdfM % "DOI", tmpM])
            elif doi is not None and doi != "":
                menuP.append(
                    QAction(
                        bwstr.Acts.pdfDOIA,
                        self.menu,
                        triggered=lambda g="doi": self.onAddPDF(g),
                    )
                )
            shortfiles = {f.replace(pdfDir + os.sep, ""): f for f in files}
            for fn in sorted(shortfiles):
                f = shortfiles[fn]
                tmpM = []
                tmpM.append(
                    QAction(
                        bwstr.Acts.pdfDel % fn,
                        self.menu,
                        triggered=lambda k=bibkey, a=fn, t=f: self.onDeletePDFFile(
                            k, a, a, t
                        ),
                    )
                )
                tmpM.append(
                    QAction(
                        bwstr.Acts.pdfCp % fn,
                        self.menu,
                        triggered=lambda k=bibkey, a=fn, t=f: self.onCopyPDFFile(
                            k, a, t
                        ),
                    )
                )
                menuP.append([bwstr.Acts.pdfMg % fn, tmpM])
            if os.path.exists(pdfDir):
                menuP.append(None)
                menuP.append(
                    QAction(
                        bwstr.Acts.pdfOpenDir,
                        self.menu,
                        triggered=lambda k=bibkey, t="file", f=pdfDir: pBGuiView.openLink(
                            k, t, fileArg=f
                        ),
                    )
                )
            self.menu.possibleActions.append([bwstr.Acts.pdfTit, menuP])
        else:
            self.menu.possibleActions.append(
                QAction(bwstr.Acts.pdfArxW, self.menu, triggered=self.onDown)
            )

    def createContextMenu(self, selection=False):
        """Create a context menu event, for one or multiple entries

        Parameter:
            selection (default False): if True, the menu is for
                a selection of entries. If False, for a single entry
        """
        menu = PBMenu(self.parent())
        self.menu = menu
        if len(self.keys) == 0 or len(self.bibs) == 0:
            return
        if not selection and (len(self.keys) > 1 or len(self.bibs) > 1):
            selection = True

        if not selection:
            self.bibs = [self.bibs[0]]
            self.keys = [self.keys[0]]
            initialRecord = self.bibs[0]
            bibkey = initialRecord["bibkey"]
            if initialRecord["marks"] is None:
                initialRecord["marks"] = ""
                pBDB.bibs.updateField(bibkey, "marks", "")
            arxiv = initialRecord["arxiv"]
            bibtex = initialRecord["bibtex"]
            doi = initialRecord["doi"]
            inspireID = initialRecord["inspire"]

            titAct = QAction(bwstr.Acts.eDesc % bibkey, menu)
            titAct.setDisabled(True)
            menu.possibleActions.append(titAct)
            menu.possibleActions.append(None)
            menu.possibleActions.append(
                QAction(bwstr.Acts.modify, menu, triggered=self.onModify)
            )
        else:
            initialRecord = None
            arxiv = None
            inspireID = None
            if len(self.keys) == 2:
                menu.possibleActions.append(
                    QAction(bwstr.Acts.merge, menu, triggered=self.onMerge)
                )

        menu.possibleActions.append(
            QAction(bwstr.Acts.clean, menu, triggered=self.onClean)
        )
        menu.possibleActions.append(
            QAction(bwstr.Acts.delete, menu, triggered=self.onDelete)
        )
        menu.possibleActions.append(None)

        if not selection:
            self._createMenuMarkType(initialRecord)
        else:
            self._createMenuMarkTypeList()

        menuC = self._createMenuCopy(selection, initialRecord)

        self._createMenuPDF(selection, initialRecord)
        if not selection:
            self._createMenuLinks(bibkey, arxiv, doi, inspireID)
        menu.possibleActions.append(None)

        menu.possibleActions.append(
            QAction(bwstr.Acts.selCat, menu, triggered=self.onCat)
        )
        menu.possibleActions.append(
            QAction(bwstr.Acts.selExp, menu, triggered=self.onExp)
        )
        menu.possibleActions.append(None)

        self._createMenuInspire(selection, inspireID)
        self._createMenuArxiv(selection, arxiv)
        menu.possibleActions.append(None)

        menu.possibleActions.append(
            QAction(bwstr.Acts.expBib, menu, triggered=self.onExport)
        )
        menu.possibleActions.append(
            QAction(bwstr.Acts.cpAllPdf, menu, triggered=self.onCopyAllPDF)
        )

        menu.fillMenu()
        return menu

    def onAddPDF(self, ftype="generic"):
        """Ask and copy in the proper folder a new PDF

        Parameter:
            ftype (default "generic"): if "generic", add a generic PDF
                and keep its initial name.
                Otherwise, it may be e.g. "doi"
                (see `pdf.LocalPDF.copyNewFile:fileType`)
        """
        bibkey = self.keys[0]
        newPdf = askFileName(self.parent(), bwstr.Acts.pdfAddW, filter="Files (*)")
        if newPdf != "" and os.path.isfile(newPdf):
            if ftype == "generic":
                newName = newPdf.split("/")[-1]
                outcome = pBPDF.copyNewFile(bibkey, newPdf, customName=newName)
            else:
                outcome = pBPDF.copyNewFile(bibkey, newPdf, ftype)
            if outcome:
                infoMessage(bwstr.Acts.pdfAddS)
            else:
                pBGUILogger.error(bwstr.Acts.pdfAddF)

    def onAbs(self, message=True):
        """Action performed when the download of
        the abstract is required

        Parameter:
            message (default True): if False, suppress some infoMessages
        """
        self.parent().statusBarMessage(bwstr.Acts.absS)
        for e in self.bibs:
            arxiv = e["arxiv"]
            bibkey = e["bibkey"]
            if arxiv:
                bibtex, full = physBiblioWeb.webSearch["arxiv"].retrieveUrlAll(
                    arxiv, searchType="id", fullDict=True
                )
                abstract = full["abstract"]
                pBDB.bibs.updateField(bibkey, "abstract", abstract)
                if message:
                    infoMessage(abstract, title=bwstr.Acts.absD % arxiv)
            else:
                infoMessage(bwstr.Acts.absF % bibkey)
        self.parent().done()

    def onArx(self):
        """Action to be performed when asking arXiv info.
        Call `gui.mainWindow.MainWindow.infoFromArxiv`
        """
        self.parent().infoFromArxiv(self.bibs)

    def onCat(self):
        """Open a `CatsTreeWindow` to ask the changes to the categories,
        then perform the database changes
        """
        previousAll = [e["idCat"] for e in pBDB.cats.getByEntries(self.keys)]
        if len(self.keys) == 1:
            bibkey = self.keys[0]
            selectCats = CatsTreeWindow(
                parent=self.parent(),
                askCats=True,
                askForBib=bibkey,
                expButton=False,
                previous=previousAll,
            )
        else:
            selectCats = CatsTreeWindow(
                parent=self.parent(),
                askCats=True,
                expButton=False,
                previous=previousAll,
                multipleRecords=True,
            )
        selectCats.exec_()
        if selectCats.result == "Ok":
            if len(self.keys) == 1:
                cats = self.parent().selectedCats
                for p in previousAll:
                    if p not in cats:
                        pBDB.catBib.delete(p, bibkey)
                for c in cats:
                    if c not in previousAll:
                        pBDB.catBib.insert(c, bibkey)
                self.parent().statusBarMessage(bwstr.Acts.catsInsE % bibkey)
            else:
                prevAll = list(previousAll)
                for c in self.parent().previousUnchanged:
                    if c in prevAll:
                        del prevAll[prevAll.index(c)]
                for c in prevAll:
                    if c not in self.parent().selectedCats:
                        pBDB.catBib.delete(c, self.keys)
                pBDB.catBib.insert(self.parent().selectedCats, self.keys)
                self.parent().statusBarMessage(bwstr.Acts.catsIns)

    def onCitationCount(self):
        """Call `inspireStats.InspireStatsLoader.plotStats`
        to obtain the citation info of one or more papers
        """
        self.parent().getInspireCitationCount([e["inspire"] for e in self.bibs])

    def onCitations(self):
        """Call `inspireStats.InspireStatsLoader.plotStats`
        to obtain the citation info of one or more papers
        """
        self.parent().getInspireStats([e["inspire"] for e in self.bibs])

    def onClean(self):
        """Action to be performed when cleaning bibtexs.
        Call `gui.mainWindow.MainWindow.cleanAllBibtexs`
        """
        self.parent().cleanAllBibtexs(useEntries=self.bibs)

    def onComplete(self):
        """Action to be performed when updating info from INSPIRE-HEP.
        Call `gui.mainWindow.MainWindow.updateInspireInfo`
        """
        if len(self.bibs) == 1:
            bibkey = self.bibs[0]["bibkey"]
            inspireID = self.bibs[0]["inspire"]
        else:
            bibkey = []
            inspireID = []
            for e in self.bibs:
                bibkey.append(e["bibkey"])
                try:
                    inspireID.append(e["inspire"])
                except KeyError:
                    inspireID.append(None)
        self.parent().updateInspireInfo(bibkey, inspireID=inspireID)

    def onCopyBibtexs(self):
        """Copy all the bibtexs to the keyboard"""
        copyToClipboard("\n\n".join([e["bibtex"] for e in self.bibs]))

    def onCopyCites(self):
        """Copy '\cite{all the keys}' to the keyboard"""
        copyToClipboard("\cite{%s}" % ",".join([e["bibkey"] for e in self.bibs]))

    def onCopyDir(self):
        """Copy the name of the directory
        where the associated files are stored
        """
        copyToClipboard(" ".join([pBPDF.getFileDir(e["bibkey"]) for e in self.bibs]))

    def onCopyKeys(self):
        """Copy all the keys to the keyboard"""
        copyToClipboard(",".join([e["bibkey"] for e in self.bibs]))

    def onCopyPDFFile(self, bibkey, fileType, custom=None):
        """Ask where and eventually copy a PDF file

        Parameters:
            bibkey: the key of the involved entry
            fileType: the file type or the filename of the custom PDF
            custom (default None): the full path of the custom PDF
        """
        pdfName = (
            os.path.join(pBPDF.getFileDir(bibkey), custom)
            if custom is not None
            else pBPDF.getFilePath(bibkey, fileType)
        )
        outFolder = askDirName(self.parent(), title=bwstr.Acts.pdfSaveS % pdfName)
        if outFolder.strip() != "":
            pBPDF.copyToDir(outFolder, bibkey, fileType=fileType, customName=custom)

    def onCopyAllPDF(self):
        """Ask the destination and copy there all the PDF files
        for the given entries
        """
        outFolder = askDirName(self.parent(), title=bwstr.Acts.pdfSaveM)
        if outFolder.strip() != "":
            for entry in self.bibs:
                key = entry["bibkey"]
                if pBPDF.checkFile(key, "doi"):
                    pBPDF.copyToDir(outFolder, key, fileType="doi")
                elif pBPDF.checkFile(key, "arxiv"):
                    pBPDF.copyToDir(outFolder, key, fileType="arxiv")
                else:
                    existing = pBPDF.getExisting(key)
                    if len(existing) > 0:
                        for ex in existing:
                            pBPDF.copyToDir(outFolder, key, "", customName=ex)

    def onDelete(self):
        """Call `deleteBibtex` on all the entries"""
        deleteBibtex(self.parent(), self.keys)

    def onDeletePDFFile(self, bibkey, fileType, fdesc, custom=None):
        """Ask and eventually delete a PDF file

        Parameters:
            bibkey: the key of the involved entry
            fileType: the file type or the filename of the custom PDF
            fdesc: a short description of the file type
            custom (default None): the full path of the custom PDF
        """
        if askYesNo(bwstr.Acts.pdfDelAsk % (fdesc, bibkey)):
            self.parent().statusBarMessage(bwstr.Acts.pdfDelP % fdesc)
            if custom is not None:
                pBPDF.removeFile(bibkey, "", fileName=custom)
            else:
                pBPDF.removeFile(bibkey, fileType)
            self.parent().reloadMainContent(pBDB.bibs.fetchFromLast().lastFetched)

    def onDown(self):
        """Download the arXiv PDF for each given entry"""
        self.downArxiv_thr = []
        for entry in self.bibs:
            if entry["arxiv"] is not None and entry["arxiv"] != "":
                self.parent().statusBarMessage(bwstr.Acts.arxDowP % entry["arxiv"])
                self.downArxiv_thr.append(
                    Thread_downloadArxiv(entry["bibkey"], self.parent())
                )
                self.downArxiv_thr[-1].finished.connect(
                    lambda a=entry["arxiv"]: self.onDownloadArxivDone(a)
                )
                self.downArxiv_thr[-1].start()

    def onDownloadArxivDone(self, e):
        """Send a message at the end of the arXiv PDF download

        Parameter:
            e: the arXiv identifier of the entry
        """
        self.parent().sendMessage(bwstr.Acts.arxDowD % e)
        self.parent().done()
        self.parent().reloadMainContent(pBDB.bibs.fetchFromLast().lastFetched)

    def onExp(self):
        """Open a `ExpsListWindow` window to obtain the list of
        experiments to be added (also deleted, if for a single entry)
        and perform the database changes
        """
        if len(self.keys) == 1:
            bibkey = self.keys[0]
            previous = [a["idExp"] for a in pBDB.exps.getByEntry(bibkey)]
            selectExps = ExpsListWindow(
                parent=self.parent(), askExps=True, askForBib=bibkey, previous=previous
            )
            selectExps.exec_()
            if selectExps.result == "Ok":
                exps = self.parent().selectedExps
                for p in previous:
                    if p not in exps:
                        pBDB.bibExp.delete(bibkey, p)
                for e in exps:
                    if e not in previous:
                        pBDB.bibExp.insert(bibkey, e)
                self.parent().statusBarMessage(bwstr.Acts.expInsE % bibkey)
        else:
            infoMessage(bwstr.Acts.expW)
            selectExps = ExpsListWindow(parent=self.parent(), askExps=True, previous=[])
            selectExps.exec_()
            if selectExps.result == "Ok":
                pBDB.bibExp.insert(self.keys, self.parent().selectedExps)
                self.parent().statusBarMessage(bwstr.Acts.expIns)

    def onExport(self):
        """Action to be performed when exporting bibtexs.
        Call `gui.mainWindow.MainWindow.exportSelection`
        """
        self.parent().exportSelection(self.bibs)

    def onMerge(self):
        """Open a `MergeBibtexs` window to configure the merging,
        then perform the requested changes, merge the entries and
        delete the previous ones
        """
        mergewin = MergeBibtexs(self.bibs[0], self.bibs[1], self.parent())
        mergewin.exec_()
        if mergewin.result:
            data = {}
            for k, v in mergewin.textValues.items():
                try:
                    s = "%s" % v.text()
                    data[k] = s
                except AttributeError:
                    try:
                        s = "%s" % v.toPlainText()
                        data[k] = s
                    except AttributeError:
                        pass
            for k, v in mergewin.checkValues.items():
                if v.isChecked():
                    data[k] = 1
                else:
                    data[k] = 0
            data["marks"] = ""
            for m, ckb in mergewin.markValues.items():
                if ckb.isChecked():
                    data["marks"] += "%s," % m
            if data["old_keys"].strip() != "":
                data["old_keys"] = ", ".join(
                    [
                        data["old_keys"],
                        self.entries[0]["bibkey"],
                        self.entries[1]["bibkey"],
                    ]
                )
            else:
                data["old_keys"] = ", ".join(
                    [self.bibs[0]["bibkey"], self.bibs[1]["bibkey"]]
                )
            data = pBDB.bibs.prepareInsert(**data)
            if data["bibkey"].strip() != "" and data["bibtex"].strip() != "":
                correct = False
                pBDB.commit()
                try:
                    for key in [self.bibs[0]["bibkey"], self.bibs[1]["bibkey"]]:
                        pBDB.bibs.delete(key)
                except:
                    pBGUILogger.exception(bwstr.Acts.cantDelOld)
                    pBDB.undo()
                else:
                    if not pBDB.bibs.insert(data):
                        pBGUILogger.error(bwstr.Acts.cantInsNew)
                        pBDB.undo()
                    else:
                        self.parent().setWindowTitle(bwstr.winTitleModified)
                        correct = True
                        try:
                            self.parent().reloadMainContent(
                                pBDB.bibs.fetchFromLast().lastFetched
                            )
                        except:
                            pBLogger.warning(bwstr.Acts.reloadFail)
                if correct:
                    for oldkey in [self.bibs[0]["bibkey"], self.bibs[1]["bibkey"]]:
                        for e in pBDB.cats.getByEntry(oldkey):
                            pBDB.catBib.insert(e["idCat"], data["bibkey"])
                            pBDB.catBib.delete(e["idCat"], oldkey)
                        for e in pBDB.exps.getByEntry(oldkey):
                            pBDB.bibExp.insert(data["bibkey"], e["idExp"])
                            pBDB.bibExp.delete(oldkey, e["idExp"])
                        pBPDF.mergePDFFolders(oldkey, data["bibkey"])
            else:
                pBGUILogger.error(bwstr.Acts.emptyKeyBib)
        else:
            self.parent().statusBarMessage(bwstr.nothingToDo)

    def onModify(self):
        """Action to be performed when modifying bibtexs.
        Call `editBibtex`
        """
        editBibtex(self.parent(), self.bibs[0]["bibkey"])

    def onUpdate(self, force=False, reloadAll=False):
        """Action to be performed when updating bibtexs.
        Call `gui.mainWindow.MainWindow.updateAllBibtexs`

        Parameters:
            force (default False): if True, force update also when
                bibliographic information is already present
            reloadAll (default False): if True,
                completely reload the bibtexs
                instead of updating them
        """
        self.parent().updateAllBibtexs(
            startFrom=0, useEntries=self.bibs, force=force, reloadAll=reloadAll
        )

    def onUpdateMark(self, mark, force=None):
        """Update (set or unset) 'mark' for the given entries and
        reload the main table content

        Parameter:
            mark: one of the allowed marks
            force (default None): if 0 (remove) or 1 (add), update
                the field by using this value instead of toggling it
        """
        if mark not in pBMarks.marks.keys():
            pBLogger.warning(bwstr.Acts.maInv % mark)
            return
        pBLogger.debug(bwstr.Acts.maUpd % (mark, [e["bibkey"] for e in self.bibs]))
        for e in self.bibs:
            marks = e["marks"].replace("'", "").split(",")
            marks = [m for m in marks if m.strip() != ""]
            if force == 0:
                if mark in marks:
                    marks.remove(mark)
            elif force == 1:
                if mark not in marks:
                    marks.append(mark)
            elif mark in marks:
                marks.remove(mark)
            else:
                marks.append(mark)
            marks = sorted(marks)
            pBDB.bibs.updateField(e["bibkey"], "marks", ",".join(marks), verbose=0)
        self.parent().reloadMainContent(pBDB.bibs.fetchFromLast().lastFetched)

    def onUpdateType(self, type_, force=None):
        """Toggle the field 'type_' for the given entries and
        reload the main table content

        Parameter:
            type_: one among "review", "proceeding", "book",
                "phd_thesis", "lecture", "exp_paper"
            force (default None): if 0 or 1, update the field by using
                the passed value instead of toggling it
        """
        if type_ not in convertType.keys():
            pBLogger.warning(bwstr.Acts.tyInv % type_)
            return
        for e in self.bibs:
            value = force if force in [0, 1] else (0 if e[type_] else 1)
            pBDB.bibs.updateField(e["bibkey"], type_, value, verbose=0)
        self.parent().reloadMainContent(pBDB.bibs.fetchFromLast().lastFetched)


class BibtexListWindow(QFrame, ObjListWindow):
    """Class that constructs the main bibtex table"""

    def __init__(self, parent=None, bibs=None, askBibs=False, previous=[]):
        """Define some properties and create the table

        Parameters:
            parent (default None): the parent widget
            bibs (default None): list of bibtex entries to display.
                if None, database information will be retrieved later
            askBibs (default False): if True, activate checkboxes
                for selecting the entries
            previous (default []): list with the initial selection
                of entries (used if askBibs is True)
        """
        self.mainWin = parent
        self.bibs = bibs
        self.askBibs = askBibs
        self.previous = previous

        self.currentAbstractKey = None
        self.columns = pbConfig.params["bibtexListColumns"]
        self.colcnt = len(self.columns)
        self.additionalCols = [bwstr.LW.typec, bwstr.LW.pdfc]
        self.colContents = []
        for j in range(self.colcnt):
            self.colContents.append(self.columns[j])
        self.colContents += [a.lower() for a in self.additionalCols]
        self.tableModel = None
        self.selAct = None
        self.okAct = None
        self.clearAct = None
        self.selAllAct = None
        self.unselAllAct = None
        self.lastLabel = None
        self.mergeLabel = None
        self.filterInput = None
        self.tableModel = None

        QFrame.__init__(self, parent)
        ObjListWindow.__init__(self, parent)

        self.createActions()
        self.createTable()

    def getRowBibkey(self, model, index):
        """Use the model index to return the bibkey for the given row

        Parameter:
            model: the model to use
                (e.g. self.tableModel or self.proxyModel)
            index: a `QModelIndex` instance

        Output:
            None for invalid rows or missing content,
            a string otherwise
        """
        if not index.isValid():
            return
        row = index.row()
        col = index.column()
        try:
            newidx = model.sibling(row, self.columns.index("bibkey"), index)
        except AttributeError:
            pBLogger.debug(bwstr.LW.errReadTab)
            return
        if not newidx.isValid():
            return
        try:
            bibkey = str(newidx.data())
        except AttributeError:
            pBLogger.debug(bwstr.LW.errReadTab)
            return
        if bibkey is None or bibkey == "" or bibkey == "None":
            return
        try:
            entry = pBDB.bibs.getByBibkey(bibkey, saveQuery=False)[0]
        except IndexError:
            pBGUILogger.debug(bwstr.LW.errEntry)
            return
        return bibkey

    def onSelectionChanged(self, sel, unsel):
        """When the selection is changed,
        if more than one row is currently selected,
        enable the checkboxes and mark the selected rows as checked.
        Following selections with e.g. Ctrl+click will update
        the checkboxes until the selection is cleared
        or an action performed

        Parameters:
            sel: list of QItemSelection objects that have been selected
                with the last action
            unsel: list of QItemSelection objects that have been
                unselected with the last action
        """
        selectionModel = self.tableview.selectionModel()
        currentSelRows = selectionModel.selectedRows(self.columns.index("bibkey"))
        if len(currentSelRows) > 1:
            bibkeys = [ix.data() for ix in currentSelRows]
            self.tableModel.changeAsk(new=True)
            self.changeEnableActions(status=True)
            self.tableModel.layoutAboutToBeChanged.emit()
            for bibkey in bibkeys:
                if (
                    bibkey is not None
                    and isinstance(bibkey, six.string_types)
                    and bibkey != ""
                ):
                    self.tableModel.selectedElements[bibkey] = True
            self.tableModel.layoutChanged.emit()
        if self.tableModel.ask:
            self.tableModel.layoutAboutToBeChanged.emit()
            for un in sel:
                for ix in un.indexes():
                    if ix.column() == self.columns.index("bibkey"):
                        bibkey = self.getRowBibkey(self.proxyModel, ix)
                        if bibkey is not None:
                            self.tableModel.selectedElements[bibkey] = True
            for un in unsel:
                for ix in un.indexes():
                    if ix.column() == self.columns.index("bibkey"):
                        bibkey = self.getRowBibkey(self.proxyModel, ix)
                        if bibkey is not None:
                            self.tableModel.selectedElements[bibkey] = False
            self.tableModel.layoutChanged.emit()
        self.restoreSort()

    def reloadColumnContents(self):
        """Reload the list of column names
        (it may have been changed if a profile change occurred)
        """
        self.columns = pbConfig.params["bibtexListColumns"]
        self.colcnt = len(self.columns)
        self.colContents = []
        for j in range(self.colcnt):
            self.colContents.append(self.columns[j])
        self.colContents += [a.lower() for a in self.additionalCols]

    def changeEnableActions(self, status=None):
        """Enable or disable the buttons related
        to the bibtex selection
        """
        status = self.tableModel.ask if status is None else status
        self.clearAct.setEnabled(status)
        self.selAllAct.setEnabled(status)
        self.unselAllAct.setEnabled(status)
        self.okAct.setEnabled(status)

    def changeFilterSort(self, string):
        """Change the filter of the current view.

        Parameter:
            string: the filter string to be matched
        """
        self.changeFilter(string)
        self.restoreSort()

    def clearSelection(self):
        """Clear the current selection of bibtex entries"""
        self.tableModel.previous = []
        self.tableModel.prepareSelected()
        self.tableModel.changeAsk(False)
        self.restoreSort()
        self.tableview.clearSelection()
        self.changeEnableActions(status=False)

    def createActions(self):
        """Create a number of `QAction`s related to bibtex selection"""
        self.selAct = QAction(
            QIcon(":/images/edit-node.png"),
            bwstr.LW.selEnT,
            self,
            statusTip=bwstr.LW.selEnD,
            triggered=self.enableSelection,
        )
        self.okAct = QAction(
            QIcon(":/images/dialog-ok-apply.png"),
            bwstr.LW.selComT,
            self,
            statusTip=bwstr.LW.selComD,
            triggered=self.onOk,
        )
        self.clearAct = QAction(
            QIcon(":/images/edit-clear.png"),
            bwstr.LW.selCleT,
            self,
            statusTip=bwstr.LW.selCleD,
            triggered=self.clearSelection,
        )
        self.selAllAct = QAction(
            QIcon(":/images/edit-select-all.png"),
            bwstr.LW.selAllT,
            self,
            statusTip=bwstr.LW.selAllD,
            triggered=self.selectAll,
        )
        self.unselAllAct = QAction(
            QIcon(":/images/edit-unselect-all.png"),
            bwstr.LW.selNonT,
            self,
            statusTip=bwstr.LW.selNonD,
            triggered=self.unselectAll,
        )

    def restoreSort(self):
        """Re-establish current sort status for the table:
        first use the default (ascending on column 0),
        then apply last settings
        """
        ccol = self.proxyModel.sortColumn()
        cord = self.proxyModel.sortOrder()
        self.proxyModel.sort(self.columns.index("bibkey"), Qt.AscendingOrder)
        self.proxyModel.sort(ccol, cord)
        self.tableview.sortByColumn(self.columns.index("bibkey"), Qt.AscendingOrder)
        self.tableview.sortByColumn(ccol, cord)

    def enableSelection(self):
        """Enable the selection of entries"""
        self.tableModel.changeAsk()
        self.restoreSort()
        self.changeEnableActions()

    def selectAll(self):
        """Select all the available entries"""
        self.tableModel.selectAll()

    def unselectAll(self):
        """Unselect all the available entries"""
        self.tableModel.unselectAll()

    def onOk(self):
        """Used when a selection of entries is completed.
        Show the right click menu, then clean the selection
        independently on which action has been chosen
        """
        position = QCursor.pos()
        self.mainWin.selectedBibs = sorted(
            [
                key
                for key in self.tableModel.selectedElements.keys()
                if self.tableModel.selectedElements[key] == True
            ]
        )
        commonActions = CommonBibActions(
            [
                pBDB.bibs.getByBibkey(k, saveQuery=False)[0]
                for k in self.mainWin.selectedBibs
            ],
            self.mainWin,
        )
        ask = commonActions.createContextMenu(selection=True)
        ask.exec_(position)
        self.clearSelection()

    def createTable(self):
        """Create the table model, the toolbar for the selection,
        the filter input box, set some properties.
        Retrieve the list of bibtex entries from the database
        if not already given.
        """
        if self.bibs is None:
            self.bibs = pBDB.bibs.getAll(
                orderType="DESC", limitTo=pbConfig.params["defaultLimitBibtexs"]
            )
        rowcnt = len(self.bibs)

        commentStr = bwstr.LW.lastQuery % (pBDB.bibs.lastQuery)
        if len(pBDB.bibs.lastVals) > 0:
            commentStr += bwstr.LW.lastQueryA % (pBDB.bibs.lastVals,)
        self.lastLabel = PBLabel(commentStr)
        self.currLayout.addWidget(self.lastLabel)

        self.selectToolBar = QToolBar(bwstr.LW.toolBar)
        self.selectToolBar.addAction(self.selAct)
        self.selectToolBar.addAction(self.clearAct)
        self.selectToolBar.addSeparator()
        self.selectToolBar.addAction(self.selAllAct)
        self.selectToolBar.addAction(self.unselAllAct)
        self.selectToolBar.addAction(self.okAct)
        self.mergeLabel = PBLabel(bwstr.LW.selTwo)
        self.selectToolBar.addWidget(self.mergeLabel)
        self.selectToolBar.addSeparator()

        self.filterInput = QLineEdit("", self)
        self.filterInput.setPlaceholderText(bwstr.LW.filterBib)
        self.filterInput.textChanged.connect(self.changeFilterSort)
        self.selectToolBar.addWidget(self.filterInput)
        self.filterInput.setFocus()

        self.currLayout.addWidget(self.selectToolBar)

        self.tableModel = BibTableModel(
            self,
            self.bibs,
            self.columns + self.additionalCols,
            self.columns,
            self.additionalCols,
            askBibs=self.askBibs,
            mainWin=self.mainWin,
            previous=self.previous,
        )

        self.changeEnableActions()
        if "firstdate" in self.columns:
            self.setProxyStuff(self.columns.index("firstdate"), Qt.DescendingOrder)
        else:
            self.setProxyStuff(self.columns.index("bibkey"), Qt.AscendingOrder)
        self.tableview.hideColumn(len(self.columns) + len(self.additionalCols))
        self.tableview.selectionModel().selectionChanged.connect(
            self.onSelectionChanged
        )

        self.finalizeTable()

    def updateInfo(self, entry):
        """Update the info about the current entry on the bottom panels

        Parameter:
            entry: the bibtex entry to be processed
        """
        self.mainWin.bottomLeft.text.setText(entry["bibtex"])
        self.mainWin.bottomRight.text.setText(writeBibtexInfo(entry))
        if self.currentAbstractKey != entry["bibkey"]:
            self.currentAbstractKey = entry["bibkey"]
            writeAbstract(self.mainWin, entry)

    def getEventEntry(self, index):
        """Use the model index to return bibkey and entry record

        Parameter:
            index: a `QModelIndex` instance
        """
        if not index.isValid():
            return
        row = index.row()
        col = index.column()
        try:
            bibkey = str(
                self.proxyModel.sibling(row, self.columns.index("bibkey"), index).data()
            )
        except AttributeError:
            pBLogger.debug(bwstr.LW.errReadTab)
            return
        if bibkey is None or bibkey == "":
            return
        try:
            entry = pBDB.bibs.getByBibkey(bibkey, saveQuery=False)[0]
        except IndexError:
            pBGUILogger.debug(bwstr.LW.errEntry)
            return
        return row, col, bibkey, entry

    def keyPressEvent(self, e):
        """Manage the key press events.
        Do nothing unless `Ctrl+c` is pressed:
        in this case open a "copy to clipboard" menu
        for the current selection

        Parameters:
            e: the `PySide2.QtGui.QKeyEvent`
        """
        if (
            e.key() == Qt.Key_C
            and QApplication.keyboardModifiers() == Qt.ControlModifier
        ):
            currentRows = self.tableview.selectionModel().selectedRows(
                self.columns.index("bibkey")
            )
            if len(currentRows) > 0:
                bibkeys = [ix.data() for ix in currentRows if ix.data() is not None]
                ac = CommonBibActions([pBDB.bibs.getByBibkey(k)[0] for k in bibkeys])
                ac.menu = PBMenu()
                selection = len(bibkeys) > 1
                ac._createMenuCopy(selection, ac.bibs[0] if not selection else None)
                ac.menu.possibleActions = [
                    QAction(bwstr.LW.copyToClipT, ac.menu),
                    None,
                ] + ac.menu.possibleActions[0][1]
                ac.menu.possibleActions[0].setDisabled(True)
                ac.menu.fillMenu()
                position = QCursor.pos()
                ac.menu.exec_(position)
                self.clearSelection()
        else:
            self.mainWin.keyPressEvent(e)

    def triggeredContextMenuEvent(self, row, col, event):
        """Process event when mouse right-clicks an item.
        Opens a menu with a number of actions

        Parameter:
            row: the row number
            col: a the column number
            event: a `QEvent` instance, used to obtain the mouse
                position where to open the menu
        """
        index = self.tableview.model().index(row, col)
        try:
            row, col, bibkey, entry = self.getEventEntry(index)
        except TypeError:
            pBLogger.warning(bwstr.LW.errIdx)
            return

        commonActions = CommonBibActions([entry], self.mainWin)
        menu = commonActions.createContextMenu()
        menu.exec_(event.globalPos())

    def handleItemEntered(self, index):
        """Currently does nothing

        Parameter:
            index: a `QModelIndex` instance
        """
        return

    def cellClick(self, index):
        """Process event when mouse clicks an item.
        Currently not used

        Parameter:
            index: a `QModelIndex` instance
        """
        try:
            row, col, bibkey, entry = self.getEventEntry(index)
        except TypeError:
            pBLogger.warning(bwstr.LW.errIdx)
            return
        self.updateInfo(entry)

    def cellDoubleClick(self, index):
        """Process event when mouse double clicks an item.
        Opens a link if some columns

        Parameters:
            index: a `QModelIndex` instance
        """
        try:
            row, col, bibkey, entry = self.getEventEntry(index)
        except TypeError:
            pBLogger.warning(bwstr.LW.errIdx)
            return
        self.updateInfo(entry)
        for column in ["ads", "arxiv", "doi", "inspire"]:
            if (
                self.colContents[col] == column
                and entry[column] is not None
                and entry[column] != ""
            ):
                pBGuiView.openLink(bibkey, column)
        if self.colContents[col] == "pdf":
            pdfFiles = pBPDF.getExisting(bibkey, fullPath=True)
            if len(pdfFiles) == 1:
                self.mainWin.statusBarMessage(bwstr.LW.openPDF)
                pBGuiView.openLink(bibkey, "file", fileArg=pdfFiles[0])
            elif len(pdfFiles) > 1:
                ask = AskPDFAction(bibkey, self.mainWin)
                ask.exec_(QCursor.pos())

    def finalizeTable(self):
        """Set the font size, resize the table to fit the contents,
        connect click and doubleclick functions, add layout
        """
        font = QFont()
        font.setPointSize(pbConfig.params["bibListFontSize"])
        self.tableview.setFont(font)

        if pbConfig.params["resizeTable"]:
            self.tableview.resizeColumnsToContents()
            self.tableview.resizeRowsToContents()
        else:
            for f in ["author", "title", "comments"]:
                if f in self.colContents:
                    self.tableview.resizeColumnToContents(self.colContents.index(f))

        self.tableview.clicked.connect(self.cellClick)
        self.tableview.doubleClicked.connect(self.cellDoubleClick)

        self.currLayout.addWidget(self.tableview)

    def recreateTable(self, bibs=None):
        """Call `self.cleanLayout` and `self.createTable`
        to renew the main table content.

        Parameter:
            bibs (default None): the list of bibtex entries to use.
                if None, use `getAll` on the database
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if bibs is not None:
            self.bibs = bibs
        else:
            self.bibs = pBDB.bibs.getAll(
                orderType="DESC", limitTo=pbConfig.params["defaultLimitBibtexs"]
            )
        self.cleanLayout()
        self.createTable()
        QApplication.restoreOverrideCursor()


class EditBibtexDialog(EditObjectWindow):
    """Create a window for editing or creating a new bibtex entry"""

    checkboxes = [
        "exp_paper",
        "lecture",
        "phd_thesis",
        "review",
        "proceeding",
        "book",
        "noUpdate",
    ]

    def __init__(self, parent=None, bib=None):
        """Set some basic properties.
        If `bib` is None, prepare a new empty record.

        Parameters:
            parent (default None): the parent widget
            bib (default None): the bibtex record from the database,
                or None to create a new entry
        """
        self.acceptButton = None
        self.cancelButton = None
        self.textValues = {}
        self.typeBox = None
        self.currGrid = None
        self.result = False
        super(EditBibtexDialog, self).__init__(parent)
        if bib is None:
            self.data = {}
        else:
            self.data = bib
        for k in pBDB.tableCols["entries"]:
            if k != "citations" and k != "citations_no_self":
                try:
                    self.data[k]
                except KeyError:
                    self.data[k] = ""
            else:
                try:
                    setattr(self, k, self.data[k])
                except KeyError:
                    setattr(self, k, 0)

        self.checkValues = {}
        self.markValues = {}
        self.createForm()

    def onOk(self):
        """Validate the form content. Close the dialog only
        if the bibtex field is not empty and the bibtex key has not
        been manually modified in the 'bibkey' QTextEdit.
        """
        if self.textValues["bibtex"].toPlainText() == "":
            pBGUILogger.error(bwstr.ED.bibEmpty)
            return False
        elif self.textValues["bibkey"].text() == bwstr.ED.notValidTex:
            pBGUILogger.error(bwstr.ED.bibNotValid)
            return False
        elif (
            not self.textValues["bibkey"].isReadOnly()
            and self.textValues["bibkey"].text() != ""
            and self.textValues["bibtex"].toPlainText() != ""
        ):
            pBGUILogger.error(bwstr.ED.bibKeyErr)
            return False
        self.result = True
        self.close()

    def updateBibkey(self):
        """When the bibtex text is changed, update
        the 'bibkey' QTextEdit according to the bibtex content
        """
        bibtex = self.textValues["bibtex"].toPlainText()
        try:
            element = bibtexparser.loads(bibtex).entries[0]
            bibkey = element["ID"]
        except (
            ValueError,
            IndexError,
            KeyError,
            ParseException,
            bibtexparser.bibdatabase.UndefinedString,
        ):
            bibkey = bwstr.ED.notValidTex
        self.textValues["bibkey"].setText(bibkey)

    def createField(self, k, i):
        """Create a `QLineEdit` with the field content
        and the corresponding labels,
        or a Groupbox in case of "marks"

        Parameters:
            k: the field name
            i: the index to be used

        Output:
            the updated index
        """
        if (
            k == "bibdict"
            or k == "abstract"
            or k == "bibtex"
            or k == "comments"
            or k in self.checkboxes
        ):
            return i
        i += 1
        if k != "marks":
            self.currGrid.addWidget(PBLabel(k), i + i % 2 - 1, ((i + 1) % 2) * 2)
            self.currGrid.addWidget(
                PBLabel("(%s)" % pBDB.descriptions["entries"][k]),
                i + i % 2 - 1,
                ((i + 1) % 2) * 2 + 1,
            )
            self.textValues[k] = QLineEdit(
                str(self.data[k]) if self.data[k] is not None else ""
            )
            if k == "bibkey":
                self.textValues[k].setReadOnly(True)
            self.currGrid.addWidget(
                self.textValues[k], i + i % 2, ((i + 1) % 2) * 2, 1, 2
            )
        else:
            groupBox, markValues = pBMarks.getGroupbox(
                self.data["marks"], description=pBDB.descriptions["entries"]["marks"]
            )
            self.markValues = markValues
            if (i + 1) % 2 != 0:
                i += 1
            self.currGrid.addWidget(groupBox, i + i % 2, 0, 1, 4)
        return i

    def createCheckbox(self, k):
        """Create a QCheckBox (eventually checked)
        and the corresponding labels

        Parameters:
            k: the field name
            i: the number of previous rows already filled
            j: the index to be used

        Output:
            the updated index
        """
        if k in self.checkboxes:
            self.checkValues[k] = QCheckBox(k, self)
            if self.data[k] == 1:
                self.checkValues[k].toggle()
            self.typeBox.layout().addWidget(self.checkValues[k])
            self.checkValues[k].setToolTip(pBDB.descriptions["entries"][k])

    def createForm(self):
        """Create the form content:
        input fields, labels, checkboxes and buttons
        """
        self.setWindowTitle(bwstr.ED.title)

        i = 0
        for k in pBDB.tableCols["entries"]:
            if k != "citations" and k != "citations_no_self":
                i = self.createField(k, i)

        i += 3 + i % 2
        self.typeBox = QGroupBox(bwstr.ED.type_)
        self.typeBox.setFlat(True)
        vbox = QHBoxLayout()
        self.typeBox.setLayout(vbox)
        for k in pBDB.tableCols["entries"]:
            self.createCheckbox(k)
        self.currGrid.addWidget(self.typeBox, i - 2 + i % 2, 0, 1, 4)

        # bibtex text editor
        k = "bibtex"
        self.currGrid.addWidget(
            PBLabel(pBDB.descriptions["entries"][k]), i + i % 2 - 1, 0
        )
        self.textValues[k] = QPlainTextEdit(self.data[k])
        self.textValues[k].textChanged.connect(self.updateBibkey)
        self.currGrid.addWidget(self.textValues[k], i + i % 2, 0, 14, 2)

        # comments editor
        k = "comments"
        self.currGrid.addWidget(
            PBLabel(pBDB.descriptions["entries"][k]), i + i % 2 - 1, 2, 1, 2
        )
        self.textValues[k] = QPlainTextEdit(self.data[k])
        self.currGrid.addWidget(self.textValues[k], i + i % 2, 2, 14, 2)

        # OK button
        i += 14
        self.acceptButton = QPushButton(bwstr.ok, self)
        self.acceptButton.clicked.connect(self.onOk)
        self.currGrid.addWidget(self.acceptButton, i + i % 2 + 1, 0, 1, 2)

        # cancel button
        self.cancelButton = QPushButton(bwstr.cancel, self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        self.currGrid.addWidget(self.cancelButton, i + i % 2 + 1, 2, 1, 2)

        self.setGeometry(100, 100, 400, 25 * i)
        self.centerWindow()


class AskPDFAction(PBMenu):
    """Menu used to ask which PDF file must be opened"""

    def __init__(self, key, parent=None):
        """Prepare the menu, reading the list of existing PDF files
        and creating an action for each of them

        Parameters:
            key: the bibtex key of the item to consider
            parent (default None): the parent widget
        """
        super(AskPDFAction, self).__init__(parent)
        self.key = key
        self.mainWin = parent
        self.message = bwstr.whatPDF % (key)
        self.possibleActions = []
        files = pBPDF.getExisting(key, fullPath=True)
        doiFile = pBPDF.getFilePath(key, "doi")
        arxivFile = pBPDF.getFilePath(key, "arxiv")
        if doiFile != "" and doiFile in files:
            self.possibleActions.append(
                QAction(bwstr.Acts.pdfO % "DOI", self, triggered=self.onOpenDoi)
            )
            files.remove(doiFile)
        if arxivFile != "" and arxivFile in files:
            self.possibleActions.append(
                QAction(bwstr.Acts.pdfO % "arxiv", self, triggered=self.onOpenArxiv)
            )
            files.remove(arxivFile)
        for f in files:
            fname = f.split(os.sep)[-1]
            self.possibleActions.append(
                QAction(
                    bwstr.Acts.pdfOpen % fname,
                    self,
                    triggered=lambda fn=fname: self.onOpenOther(fn),
                )
            )
        self.fillMenu()

    def onOpenArxiv(self):
        """Set the result for opening the arXiv PDF"""
        self.mainWin.statusBarMessage(bwstr.pdfOg % "arXiv")
        pBGuiView.openLink(
            self.key, "file", fileArg=pBPDF.getFilePath(self.key, "arxiv")
        )
        self.close()

    def onOpenDoi(self):
        """Set the result for opening the DOI PDF"""
        self.mainWin.statusBarMessage(bwstr.pdfOg % "DOI")
        pBGuiView.openLink(self.key, "file", fileArg=pBPDF.getFilePath(self.key, "doi"))
        self.close()

    def onOpenOther(self, filename):
        """Set the result for opening the DOI PDF"""
        self.mainWin.statusBarMessage(bwstr.pdfOpen % filename)
        pBGuiView.openLink(
            self.key, "file", fileArg=os.path.join(pBPDF.getFileDir(self.key), filename)
        )
        self.close()


class SearchBibsWindow(EditObjectWindow):
    """Create a window for searching a bibtex entry"""

    def __init__(self, parent=None, replace=False, edit=None):
        """Create the window and save some properties

        Parameters:
            parent (default None): the parent widget
            replace (default False): if True, add the replace fields
                in the dialog
            edit (default None): if not None, it should be the index
                of the search/replace to be modified
        """
        self.acceptButton = None
        self.cancelButton = None
        self.saveButton = None
        self.currGrid = None
        self.addFieldButton = None
        self.selectedCats = []
        self.selectedExps = []
        super(SearchBibsWindow, self).__init__(parent)
        self.textValues = []
        self.result = False
        self.save = False
        self.replace = replace
        self.edit = edit
        self.possibleTypes = pBDB.bibs.searchPossibleTypes
        self.operators = {
            k: sorted([e for e in v.keys()])
            for k, v in pBDB.bibs.searchOperators.items()
        }
        self.fields = pBDB.bibs.searchFields
        self.replaceComboFields = pBDB.bibs.validReplaceFields
        self.values = []
        self.numberOfRows = 1
        self.replOld = None
        self.replNew = None
        self.replNew1 = None
        self.limitValue = None
        self.limitOffs = None
        self.limit = None
        self.offset = None
        self.replRegex = None
        self.replOldField = None
        self.replNewField = None
        self.replNewField1 = None
        self.doubleEdit = None
        self.replaceFields = {}
        self.currentHistoric = 0
        if self.edit is not None:
            if not (isinstance(self.edit, int) or self.edit.isdigit()):
                pBGUILogger.error(bwstr.wrongEdit % self.edit)
                return
            else:
                self.historic = [
                    self.processHistoric(a)
                    for a in pbConfig.globalDb.getSearchByID(self.edit)
                ]
                self.createForm(histIndex=0)
        else:
            self.historic = [
                self.processHistoric(a)
                for a in pbConfig.globalDb.getSearchList(
                    manual=False, replacement=replace
                )
            ]
            self.historic.insert(
                0,
                {
                    "nrows": 1,
                    "searchValues": [
                        {
                            "logical": None,
                            "field": None,
                            "type": bwstr.SR.text,
                            "operator": None,
                            "content": "",
                        }
                    ],
                    "limit": "100000"
                    if replace
                    else "%s" % pbConfig.params["defaultLimitBibtexs"],
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
            )
            self.createForm()

    def processHistoric(self, record):
        """Process the information stored in the database
        to later use it for restoring a previous search/replace

        Parameter:
            record: the database record
        """
        try:
            searchValues = ast.literal_eval(record["searchDict"])
        except (ValueError, SyntaxError):
            pBLogger.warning(
                bwstr.SR.errorProcessSavedF % record["searchDict"],
                exc_info=True,
            )
            searchValues = []
        if record["isReplace"] == 1:
            try:
                replaceFields = ast.literal_eval(record["replaceFields"])
            except (ValueError, SyntaxError):
                pBLogger.warning(
                    bwstr.SR.errorProcessSaved % record["replaceFields"],
                    exc_info=True,
                )
                replaceFields = {}
        else:
            replaceFields = {}
        return {
            "nrows": len(searchValues),
            "searchValues": searchValues,
            "limit": "%s" % record["limitNum"],
            "offset": "%s" % record["offsetNum"],
            "replaceFields": replaceFields,
        }

    def changeCurrentContent(self, index):
        """Reset the form content using the selected historical search

        Parameter:
            index: the search index in the history
        """
        self.cleanLayout()
        self.createForm(index)

    def onOk(self):
        """Set that the result should be considered and exit"""
        self.readForm()
        self.result = True
        self.close()

    def onSave(self):
        """Set for saving the search/replace and run `self.onOk`"""
        self.save = True
        self.onOk()

    def onAskCats(self, ix):
        """When clicking on a Categories button, open a dialog
        to select the required categories.
        If confirmed, save the selection in the button text.

        Parameter:
            ix: the line index
        """
        previous = self.readLine(ix)
        if previous["content"] == "":
            previous["content"] = []
        selectCats = CatsTreeWindow(
            parent=self, askCats=True, expButton=False, previous=previous["content"]
        )
        selectCats.exec_()
        if selectCats.result == "Ok":
            self.textValues[ix]["content"].setText("%s" % self.selectedCats)

    def onAskExps(self, ix):
        """When clicking on an Experiments button, open a dialog
        to select the required experiments.
        If confirmed, save the selection in the button text.

        Parameter:
            ix: the line index
        """
        previous = self.readLine(ix)
        if previous["content"] == "":
            previous["content"] = []
        selectExps = ExpsListWindow(
            parent=self, askExps=True, previous=previous["content"]
        )
        selectExps.exec_()
        if selectExps.result == "Ok":
            self.textValues[ix]["content"].setText("%s" % self.selectedExps)

    def keyPressEvent(self, e):
        """Intercept press keys and exit if escape is pressed

        Parameters:
            e: the `PySide2.QtGui.QKeyEvent`
        """
        if e.key() == Qt.Key_Escape:
            self.onCancel()
        elif self.edit is None and (e.key() == Qt.Key_Up or e.key() == Qt.Key_Down):
            self.readForm()
            if self.replace:
                replace = self.replaceFields.copy()
            else:
                replace = {
                    "regex": False,
                    "double": False,
                    "fieOld": "author",
                    "old": "",
                    "fieNew": "author",
                    "new": "",
                    "fieNew1": "author",
                    "new1": "",
                }
            self.historic[self.currentHistoric] = {
                "nrows": len(self.values),
                "searchValues": [v.copy() for v in self.values],
                "limit": "%s" % self.limit,
                "offset": "%s" % self.offset,
                "replaceFields": replace,
            }
            if e.key() == Qt.Key_Up and self.currentHistoric < len(self.historic) - 1:
                self.currentHistoric += 1
            elif e.key() == Qt.Key_Down and self.currentHistoric > 0:
                self.currentHistoric -= 1
            self.cleanLayout()
            self.createForm(histIndex=self.currentHistoric)

    def eventFilter(self, widget, event):
        """Filter the "enter" events in a text widget.
        If 'Enter' or "Return" is pressed, set focus on the "Ok" button

        Parameters:
            widget: the widget of the event
            event: a `QEvent` instance
        """
        if event.type() == QEvent.KeyPress and (
            widget
            in [a["content"] for a in self.textValues]
            + [
                self.replOld,
                self.replNew,
                self.replNew1,
                self.limitValue,
                self.limitOffs,
            ]
        ):
            key = event.key()
            if key == Qt.Key_Return or key == Qt.Key_Enter:
                self.acceptButton.setFocus()
                return True
        return QWidget.eventFilter(self, widget, event)

    def resetForm(self):
        """Clear the current form content and recreate the form"""
        self.cleanLayout()
        self.createForm()

    def addRow(self):
        """Function called when a new line is requested.
        Increase the line number and recreate the form
        """
        self.readForm()
        self.numberOfRows = self.numberOfRows + 1
        self.textValues.append({})
        self.resetForm()

    def deleteRow(self, ix):
        """Function called when a line is deleted.
        Decrease the line number, remove arguments from the values list
        and recreate the form

        Parameter:
            ix: the index of the line to delete
        """
        try:
            del self.textValues[ix]
        except IndexError:
            return
        self.numberOfRows = self.numberOfRows - 1
        self.readForm()
        self.resetForm()

    def saveTypeRow(self, ix, text):
        """Function called when the type of a row is changed.
        Clear the layout after having saved the row type

        Parameters:
            ix: the line index
            text: the new value
        """
        self.textValues[ix]["type"].setCurrentText(text)
        self.readForm()
        self.resetForm()

    def readLine(self, ix):
        """Read the content of a line in the form and
        return a dictionary with the field contents, or the default ones
        if the line is empty or its type has been changed

        Parameter:
            ix: the line index

        Output:
            a dictionary
        """
        default = {
            "logical": None,
            "field": None,
            "type": bwstr.SR.text,
            "operator": None,
            "content": "",
        }
        try:
            line = self.textValues[ix]
        except IndexError:
            pBLogger.debug(bwstr.SR.missingIx % (ix, len(self.textValues)))
            return default

        try:
            previous = {"type": "%s" % line["type"].currentText()}
        except (KeyError, AttributeError):
            pBLogger.debug(bwstr.SR.missingType % ix)
            return default

        if ix > 0:
            try:
                previous["logical"] = "%s" % (line["logical"].currentText())
            except (KeyError, AttributeError):
                pBLogger.debug(bwstr.SR.missingLog % ix)
                previous["logical"] = None
        else:
            previous["logical"] = None

        if previous["type"] == bwstr.SR.text:
            try:
                previous["field"] = "%s" % line["field"].currentText()
            except AttributeError:
                previous["field"] = None
            else:
                if previous["field"] not in self.fields["text"]:
                    previous["field"] = None
            try:
                previous["operator"] = "%s" % (line["operator"].currentText())
            except AttributeError:
                previous["operator"] = None
            else:
                if previous["operator"] not in self.operators["text"]:
                    previous["operator"] = None
            try:
                previous["content"] = "%s" % line["content"].text()
            except AttributeError:
                previous["content"] = ""

        elif previous["type"] == bwstr.SR.cats or previous["type"] == bwstr.SR.exps:
            previous["field"] = ""
            try:
                previous["operator"] = "%s" % line["operator"].currentText()
            except AttributeError:
                previous["operator"] = None
            else:
                if previous["operator"] not in self.operators["catexp"]:
                    previous["operator"] = None
            try:
                previous["content"] = ast.literal_eval(line["content"].text())
            except (AttributeError, SyntaxError, ValueError):
                previous["content"] = []
            else:
                if not isinstance(previous["content"], list):
                    previous["content"] = []

        elif previous["type"] == bwstr.SR.marks:
            previous["field"] = None
            previous["operator"] = None
            previous["content"] = []
            try:
                for m in line["content"].keys():
                    if line["content"][m].isChecked():
                        previous["content"].append(m)
            except AttributeError:
                pass

        elif previous["type"] == bwstr.SR.type_:
            previous["field"] = None
            previous["operator"] = None
            previous["content"] = []
            try:
                for m in line["content"].keys():
                    if line["content"][m].isChecked():
                        previous["content"].append(m)
            except AttributeError:
                pass

        return previous

    def readForm(self):
        """Read the form content and save the values in self.values"""
        for ix in range(self.numberOfRows):
            try:
                self.values[ix] = self.readLine(ix)
            except IndexError:
                self.values.append(
                    {
                        "logical": None,
                        "field": None,
                        "type": bwstr.SR.text,
                        "operator": None,
                        "content": "",
                    }
                )
        if self.replace:
            self.replaceFields = {
                "regex": self.replRegex.isChecked(),
                "double": self.doubleEdit.isChecked(),
                "fieOld": self.replOldField.currentText(),
                "old": self.replOld.text(),
                "fieNew": self.replNewField.currentText(),
                "new": self.replNew.text(),
                "fieNew1": self.replNewField1.currentText(),
                "new1": self.replNew1.text(),
            }
        else:
            self.replaceFields = {}
        try:
            self.limit = int(self.limitValue.text())
        except ValueError:
            self.limit = pbConfig.params["defaultLimitBibtexs"]
        try:
            self.offset = int(self.limitOffs.text())
        except ValueError:
            self.offset = 0

    def createLine(self, ix, previous):
        """Create a new line in the form, with the necessary fields
        depending on the line type

        Parameters:
            i: the line index
            previous: a dictionary with the initial content of the line
        """
        if not isinstance(previous, dict) or sorted(previous) != [
            "content",
            "field",
            "logical",
            "operator",
            "type",
        ]:
            pBLogger.debug(bwstr.SR.invalidPrev % previous)
            previous = {
                "logical": None,
                "field": None,
                "type": bwstr.SR.text,
                "operator": None,
                "content": "",
            }

        while ix >= len(self.textValues):
            self.textValues.append({})

        if ix > 0:
            self.textValues[ix]["logical"] = PBAndOrCombo(
                self, current=previous["logical"]
            )
            self.currGrid.addWidget(self.textValues[ix]["logical"], ix, 0)
        else:
            self.textValues[ix]["logical"] = None

        self.textValues[ix]["type"] = PBComboBox(
            self,
            [
                bwstr.SR.text,
                bwstr.SR.cats,
                bwstr.SR.exps,
                bwstr.SR.marks,
                bwstr.SR.type_,
            ],
            current=previous["type"],
        )
        self.textValues[ix]["type"].currentTextChanged.connect(
            lambda t, x=ix: self.saveTypeRow(x, t)
        )
        self.currGrid.addWidget(self.textValues[ix]["type"], ix, 1)

        if previous["type"] == bwstr.SR.text:
            self.textValues[ix]["field"] = PBComboBox(
                self, self.fields["text"], current=previous["field"]
            )
            self.currGrid.addWidget(self.textValues[ix]["field"], ix, 2)

            self.textValues[ix]["operator"] = PBComboBox(
                self, self.operators["text"], current=previous["operator"]
            )
            self.currGrid.addWidget(self.textValues[ix]["operator"], ix, 3)

            self.textValues[ix]["content"] = QLineEdit(previous["content"])
            self.currGrid.addWidget(self.textValues[ix]["content"], ix, 4, 1, 4)
            self.textValues[ix]["content"].installEventFilter(self)

        elif previous["type"] == bwstr.SR.cats or previous["type"] == bwstr.SR.exps:
            self.textValues[ix]["field"] = None

            self.textValues[ix]["operator"] = PBComboBox(
                self,
                self.operators["catexp"]
                if previous["type"] == bwstr.SR.cats
                else self.operators["catexp"][0:2],
                current=previous["operator"],
            )
            self.currGrid.addWidget(self.textValues[ix]["operator"], ix, 2, 1, 2)

            if previous["content"] == "":
                previous["content"] = []
            self.textValues[ix]["content"] = QPushButton(
                "%s" % previous["content"], self
            )
            self.currGrid.addWidget(self.textValues[ix]["content"], ix, 4, 1, 4)
            if previous["type"] == bwstr.SR.cats:
                self.textValues[ix]["content"].clicked.connect(
                    lambda s=False, l=ix: self.onAskCats(l)
                )
            elif previous["type"] == bwstr.SR.exps:
                self.textValues[ix]["content"].clicked.connect(
                    lambda s=False, l=ix: self.onAskExps(l)
                )

        elif previous["type"] == bwstr.SR.marks:
            self.textValues[ix]["operator"] = None
            groupBox, markValues = pBMarks.getGroupbox(
                previous["content"], description="", radio=True, addAny=True
            )
            self.textValues[ix]["field"] = groupBox
            self.textValues[ix]["content"] = markValues
            self.currGrid.addWidget(groupBox, ix, 2, 1, 6)

        elif previous["type"] == bwstr.SR.type_:
            self.textValues[ix]["operator"] = None
            groupBox = QGroupBox()
            typeValues = {}
            groupBox.setFlat(True)
            vbox = QHBoxLayout()
            for m, cont in self.possibleTypes.items():
                typeValues[m] = QRadioButton(cont["desc"])
                if m in previous["content"]:
                    typeValues[m].setChecked(True)
                vbox.addWidget(typeValues[m])
            vbox.addStretch(1)
            groupBox.setLayout(vbox)
            self.textValues[ix]["field"] = groupBox
            self.textValues[ix]["content"] = typeValues
            self.currGrid.addWidget(groupBox, ix, 2, 1, 6)

        if self.numberOfRows > 1:
            delButton = QToolButton(self)
            delButton.setText("X")
            delButton.setToolTip(bwstr.SR.deleteRow)
            delButton.clicked.connect(lambda idx=ix: self.deleteRow(ix))
            self.currGrid.addWidget(delButton, ix, 8)

    def createLimits(
        self,
        ix,
        defLim=str(pbConfig.params["defaultLimitBibtexs"]),
        defOffs="0",
        override=False,
    ):
        """Create the fields for "limit to" and "limit offset"

        Parameter:
            ix: the line index
            defLim (default from configuration): the default value for
                the limit of results
            defOffs (default "0"): the default value for the offset
            override (default False):
                if True, ignore previous form content
        """
        try:
            lim = self.limitValue.text()
            offs = self.limitOffs.text()
        except AttributeError:
            lim = defLim
            offs = defOffs
        if override:
            lim = defLim
            offs = defOffs
        self.currGrid.addWidget(PBLabelRight(bwstr.SR.maxRes), ix - 1, 0, 1, 2)
        self.limitValue = QLineEdit(lim)
        self.limitValue.setMaxLength(6)
        self.limitValue.setFixedWidth(75)
        self.currGrid.addWidget(self.limitValue, ix - 1, 2)
        self.currGrid.addWidget(PBLabelRight(bwstr.SR.startFrom), ix - 1, 3, 1, 2)
        self.limitOffs = QLineEdit(offs)
        self.limitOffs.setMaxLength(6)
        self.limitOffs.setFixedWidth(75)
        self.currGrid.addWidget(self.limitOffs, ix - 1, 5)
        self.limitValue.installEventFilter(self)
        self.limitOffs.installEventFilter(self)

    def createReplace(self, ix, previous=None):
        """Create the form fields for a replace action

        Parameter:
            ix: the initial row index for the first field
            previous (default None): the previous content
                (used when restoring previous save)

        Output:
            the row index for the last field plus one
        """
        if previous is not None:
            try:
                regex = previous["regex"]
                double = previous["double"]
                fieOld = previous["fieOld"]
                old = previous["old"]
                fieNew = previous["fieNew"]
                new = previous["new"]
                fieNew1 = previous["fieNew1"]
                new1 = previous["new1"]
            except (TypeError, KeyError):
                pBLogger.debug(bwstr.SR.invalidPrevKey % previous)
                regex = False
                fieOld = "author"
                fieNew = "author"
                fieNew1 = "author"
                double = False
                old = ""
                new = ""
                new1 = ""
        else:
            try:
                regex = self.replRegex.isChecked()
                fieOld = self.replOldField.currentText()
                fieNew = self.replNewField.currentText()
                fieNew1 = self.replNewField1.currentText()
                double = self.doubleEdit.isChecked()
                old = self.replOld.text()
                new = self.replNew.text()
                new1 = self.replNew1.text()
            except AttributeError:
                regex = False
                fieOld = "author"
                fieNew = "author"
                fieNew1 = "author"
                double = False
                old = ""
                new = ""
                new1 = ""
        self.currGrid.addWidget(PBLabel(bwstr.SR.replace), ix - 1, 0)
        self.currGrid.addWidget(PBLabelRight(bwstr.SR.regex), ix - 1, 2)
        self.replRegex = QCheckBox("", self)
        self.replRegex.setChecked(regex)
        self.currGrid.addWidget(self.replRegex, ix - 1, 3)
        self.currGrid.addWidget(PBLabelRight(bwstr.SR.fromField), ix, 0)
        self.replOldField = PBComboBox(
            self, self.replaceComboFields["old"], current=fieOld
        )
        self.currGrid.addWidget(self.replOldField, ix, 1, 1, 2)
        self.replOld = QLineEdit(old)
        self.currGrid.addWidget(self.replOld, ix, 3, 1, 3)
        ix += 1
        self.currGrid.addWidget(PBLabelRight(bwstr.SR.intoField), ix, 0)
        self.replNewField = PBComboBox(
            self, self.replaceComboFields["new"], current=fieNew
        )
        self.currGrid.addWidget(self.replNewField, ix, 1, 1, 2)
        self.replNew = QLineEdit(new)
        self.currGrid.addWidget(self.replNew, ix, 3, 1, 3)
        ix += 1
        self.doubleEdit = QCheckBox(bwstr.SR.andAlso)
        self.doubleEdit.setChecked(double)
        self.currGrid.addWidget(self.doubleEdit, ix, 0)
        self.replNewField1 = PBComboBox(
            self, self.replaceComboFields["new"], current=fieNew1
        )
        self.currGrid.addWidget(self.replNewField1, ix, 1, 1, 2)
        self.replNew1 = QLineEdit(new1)
        self.currGrid.addWidget(self.replNew1, ix, 3, 1, 3)
        self.replOld.installEventFilter(self)
        self.replNew.installEventFilter(self)
        self.limitValue = QLineEdit("100000")
        self.limitOffs = QLineEdit("0")
        return ix + 1

    def createForm(self, histIndex=-1, spaceRowHeight=25):
        """Create the form structure,
        using history information if required

        Parameters:
            histIndex (default 0): if >0, the index in the history
                of the search/replace to use to build the form
            spaceRowHeight (default 25): used as height for some rows
        """
        self.setWindowTitle(bwstr.searchBibs)

        if histIndex > len(self.historic):
            histIndex = -1

        if histIndex > -1:
            self.numberOfRows = self.historic[histIndex]["nrows"]
            for i in range(self.numberOfRows):
                previous = self.historic[histIndex]["searchValues"][i]
                try:
                    self.values[i] = previous
                except IndexError:
                    self.values.append(previous)
                self.createLine(i, previous)
        else:
            for i in range(self.numberOfRows):
                try:
                    previous = self.values[i]
                except IndexError:
                    previous = {
                        "logical": None,
                        "field": None,
                        "type": "Text",
                        "operator": None,
                        "content": "",
                    }
                    self.values.append(previous)
                self.createLine(i, previous)

        try:
            self.textValues[-1]["content"].setFocus()
        except (IndexError, AttributeError):
            pass

        i = self.numberOfRows + 1
        self.currGrid.addWidget(PBLabelRight(bwstr.addLineDesc), i - 1, 0, 1, 2)
        self.addFieldButton = QPushButton(bwstr.addLine, self)
        self.addFieldButton.clicked.connect(self.addRow)
        self.currGrid.addWidget(self.addFieldButton, i - 1, 2, 1, 2)

        self.currGrid.setRowMinimumHeight(i, spaceRowHeight)

        i += 2
        if self.replace:
            if histIndex > -1:
                i = self.createReplace(
                    i, previous=self.historic[histIndex]["replaceFields"]
                )
            else:
                i = self.createReplace(i)
        else:
            if histIndex > -1:
                self.createLimits(
                    i,
                    defLim=self.historic[histIndex]["limit"],
                    defOffs=self.historic[histIndex]["offset"],
                    override=True,
                )
            else:
                self.createLimits(i)

        self.currGrid.setRowMinimumHeight(i, spaceRowHeight)
        i += 1

        self.newTabCheck = QCheckBox(bwstr.newTab, self)
        self.currGrid.addWidget(self.newTabCheck, i, 0, 1, 6)
        i += 1

        # OK button
        self.acceptButton = QPushButton(bwstr.ok, self)
        self.acceptButton.clicked.connect(self.onOk)
        self.currGrid.addWidget(self.acceptButton, i, 2)
        self.acceptButton.setFixedWidth(80)

        # cancel button
        self.cancelButton = QPushButton(bwstr.cancel, self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        self.currGrid.addWidget(self.cancelButton, i, 3)
        self.cancelButton.setFixedWidth(80)

        # save button
        self.saveButton = QPushButton(bwstr.runASave, self)
        self.saveButton.clicked.connect(self.onSave)
        self.currGrid.addWidget(self.saveButton, i, 5)
        self.saveButton.setFixedWidth(120)

        self.currGrid.setColumnStretch(6, 1)


class MergeBibtexs(EditBibtexDialog):
    """Dialog used to merge two bibtex entries"""

    checkboxes = [
        "exp_paper",
        "lecture",
        "phd_thesis",
        "review",
        "proceeding",
        "book",
        "noUpdate",
    ]
    generic = [
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
    ]
    bibtexEditLines = 8
    bibtexWidth = 330

    def __init__(self, bib1, bib2, parent=None):
        """Initialize some parameters that are later used to construct
        the merge dialog form

        Parameters:
            bib1, bib2: the two bibtex records from the database
                containing the info on the items to be merged
            parent (default None): the parent widget
        """
        super(EditBibtexDialog, self).__init__(parent)
        self.dataOld = {"0": bib1, "1": bib2}
        self.data = {}
        for k in pBDB.tableCols["entries"]:
            if k != "citations" and k != "citations_no_self":
                self.data[k] = ""
        self.checkValues = {}
        self.markValues = {}
        self.textValues = {}
        self.radioButtons = {"0": {}, "1": {}}
        self.textValues["0"] = {}
        self.textValues["1"] = {}
        self.acceptButton = None
        self.cancelButton = None
        self.createForm()

    def radioToggled(self, ix, k):
        """When a radio button is clicked, update the central field
        value and uncheck the other corresponding radio button

        Parameter:
            ix: "0" or "1" for the left or right record
            k: the field name
        """
        self.radioButtons[ix][k].setChecked(True)
        self.radioButtons[str((int(ix) + 1) % 2)][k].setChecked(False)
        if k == "bibtex":
            self.textValues[k].blockSignals(True)
            self.textValues[k].setPlainText(self.dataOld[ix][k])
            self.textValues[k].blockSignals(False)
            self.updateBibkey()
        else:
            self.textValues[k].setText(str(self.dataOld[ix][k]))

    def textModified(self, k):
        """When the merged record field is modified,
        untoggle both the radio buttons associated to the field

        Parameter:
            k: the field name
        """
        for ix in ["0", "1"]:
            self.radioButtons[ix][k].setChecked(False)

    def addFieldOld(self, ix, k, r, c):
        """Create a QLineEdit for a field of one of the two old records

        Parameter:
            ix: "0" or "1" for the left or right record
            k: the field name
            r: the row index for the new widget in the layout
            c: the column index for the new widget in the layout
        """
        try:
            val = self.dataOld[ix][k] if self.dataOld[ix][k] is not None else ""
        except KeyError:
            val = ""
        self.textValues[ix][k] = QLineEdit(str(val))
        self.textValues[ix][k].setReadOnly(True)
        self.currGrid.addWidget(self.textValues[ix][k], r, c)

    def addFieldNew(self, k, r, v):
        """Create a QLineEdit for a field of the merged record

        Parameter:
            k: the field name
            r: the row index for the new widget in the layout
            v: the field current content
        """
        self.textValues[k] = QLineEdit(str(v))
        self.textValues[k].textEdited.connect(lambda x, f=k: self.textModified(f))
        self.currGrid.addWidget(self.textValues[k], r, 2)

    def addRadio(self, ix, k, r, c):
        """Create a QRadioButton for one field of one of the two records

        Parameter:
            ix: "0" or "1" for the left or right record
            k: the field name
            r: the row index for the new widget in the layout
            c: the column index for the new widget in the layout
        """
        self.radioButtons[ix][k] = QRadioButton("")
        self.radioButtons[ix][k].setAutoExclusive(False)
        self.radioButtons[ix][k].clicked.connect(
            lambda x=False, f=k, i=ix: self.radioToggled(i, f)
        )
        self.currGrid.addWidget(self.radioButtons[ix][k], r, c)

    def addBibtexOld(self, ix, r, c):
        """Create a QPlainTextEdit for a bibtex field
        of one of the two old records

        Parameter:
            ix: "0" or "1" for the left or right record
            r: the row index for the new widget in the layout
            c: the column index for the new widget in the layout
        """
        k = "bibtex"
        try:
            val = self.dataOld[ix][k] if self.dataOld[ix][k] is not None else ""
        except KeyError:
            val = ""
        self.textValues[ix][k] = QPlainTextEdit(str(val))
        self.textValues[ix][k].setReadOnly(True)
        self.textValues[ix][k].setMinimumWidth(self.bibtexWidth)
        self.currGrid.addWidget(self.textValues[ix][k], r, c, self.bibtexEditLines, 1)

    def addGenericField(self, k, r):
        """Create fields for a specific key
        for the new and old records and
        the corresponding radio buttons.
        One of the radio buttons is checked if one of the two records
        have a null field.

        Parameter:
            k: the field name
            r: the row index for the new widget in the layout
        """
        try:
            old0 = self.dataOld["0"][k]
            old1 = self.dataOld["1"][k]
        except KeyError:
            pBLogger.warning(bwstr.keyMiss % k)
            return r
        if old0 == old1:
            self.textValues[k] = QLineEdit(str(old0))
            self.textValues[k].hide()
        else:
            self.currGrid.addWidget(
                PBLabelCenter("%s (%s)" % (k, pBDB.descriptions["entries"][k])),
                r,
                0,
                1,
                5,
            )
            r += 1
            self.addFieldOld("0", k, r, 0)
            self.addRadio("0", k, r, 1)
            self.addFieldOld("1", k, r, 4)
            self.addRadio("1", k, r, 3)

            # add radio
            if old0 != "" and old1 == "":
                self.radioButtons["0"][k].toggle()
                val = old0
            elif old0 == "" and old1 != "":
                self.radioButtons["1"][k].toggle()
                val = old1
            else:
                val = ""
            self.addFieldNew(k, r, val)
            r += 1
        return r

    def addMarkTypeFields(self, r):
        """Create fields for the marks and types of the merged entry

        Parameter:
            r: the row index for the new widget in the layout
        """
        r += 1
        groupBox, markValues = pBMarks.getGroupbox(
            self.data["marks"], description=pBDB.descriptions["entries"]["marks"]
        )
        self.markValues = markValues
        self.currGrid.addWidget(groupBox, r, 0, 1, 5)
        r += 1
        groupBox = QGroupBox(bwstr.types)
        groupBox.setFlat(True)
        hbox = QHBoxLayout()
        for k in pBDB.tableCols["entries"]:
            if k in self.checkboxes:
                self.checkValues[k] = QCheckBox(k, self)
                hbox.addWidget(self.checkValues[k])
        groupBox.setLayout(hbox)
        self.currGrid.addWidget(groupBox, r, 0, 1, 5)
        return r

    def addBibtexFields(self, r):
        """Create "bibkey" and "bibtex" fields for the given records,
        and corresponding radio buttons

        Parameter:
            r: the row index for the new widget in the layout
        """
        r += 1
        k = "bibkey"
        self.currGrid.addWidget(
            PBLabelCenter("%s (%s)" % (k, pBDB.descriptions["entries"][k])), r, 0, 1, 5
        )
        r += 1
        self.addFieldOld("0", k, r, 0)
        self.addFieldOld("1", k, r, 4)
        if self.dataOld["0"][k] == self.dataOld["1"][k]:
            self.textValues[k] = QLineEdit(str(self.dataOld["0"][k]))
        else:
            self.textValues[k] = QLineEdit("")
        self.textValues[k].setReadOnly(True)
        self.currGrid.addWidget(self.textValues[k], r, 2)

        r += 1
        k = "bibtex"
        self.currGrid.addWidget(
            PBLabelCenter("%s (%s)" % (k, pBDB.descriptions["entries"][k])), r, 0, 1, 5
        )
        r += 1
        self.addBibtexOld("0", r, 0)
        self.addRadio("0", k, r, 1)
        self.addBibtexOld("1", r, 4)
        self.addRadio("1", k, r, 3)
        # radio and connection
        if self.dataOld["0"][k] == self.dataOld["1"][k]:
            self.data[k] = self.dataOld["0"][k]
        self.textValues[k] = QPlainTextEdit(
            str(self.data[k] if self.data[k] is not None else "")
        )
        self.textValues[k].setMinimumWidth(self.bibtexWidth)
        self.textValues[k].textChanged.connect(self.updateBibkey)
        self.textValues[k].textChanged.connect(lambda f="bibtex": self.textModified(f))
        self.currGrid.addWidget(self.textValues[k], r, 2, self.bibtexEditLines, 1)
        return r + self.bibtexEditLines

    def createForm(self):
        """Call the function that create the form fields,
        add window title and OK/Cancel buttons,
        set the window geometry and center it.
        """
        self.setWindowTitle(bwstr.mergeBibs)

        i = 0
        for k in self.generic:
            i = self.addGenericField(k, i)

        i = self.addMarkTypeFields(i)

        # bibkey and bibtex text editor
        i = self.addBibtexFields(i)

        # OK button
        i += 1
        self.acceptButton = QPushButton(bwstr.ok, self)
        self.acceptButton.clicked.connect(self.onOk)
        self.currGrid.addWidget(self.acceptButton, i, 0, 1, 2)

        # cancel button
        self.cancelButton = QPushButton(bwstr.cancel, self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        self.currGrid.addWidget(self.cancelButton, i, 3, 1, 2)

        self.setGeometry(100, 100, 3 * self.bibtexWidth + 50, 25 * i)
        self.centerWindow()


class FieldsFromArxiv(PBDialog):
    """Dialog windows used to ask which fields should be imported
    from the arXiv record of the field"""

    def __init__(self, parent=None):
        """Initialize the properties and the layout of the widget

        Parameter:
            parent: the parent widget
        """
        super(FieldsFromArxiv, self).__init__(parent)
        self.result = False
        self.output = []
        self.setWindowTitle(bwstr.fieldsFromArx)
        self.checkBoxes = {}
        self.arxivDict = ["authors", "title", "doi", "primaryclass", "archiveprefix"]
        vbox = QVBoxLayout()
        for k in self.arxivDict:
            self.checkBoxes[k] = QCheckBox(k, self)
            self.checkBoxes[k].setChecked(True)
            vbox.addWidget(self.checkBoxes[k])
        self.acceptButton = QPushButton(bwstr.ok, self)
        self.acceptButton.clicked.connect(self.onOk)
        vbox.addWidget(self.acceptButton)
        self.cancelButton = QPushButton(bwstr.cancel, self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        vbox.addWidget(self.cancelButton)
        self.setLayout(vbox)

    def onOk(self):
        """Accept the dialog output and prepare self.output"""
        self.output = []
        for k in sorted(self.checkBoxes.keys()):
            if self.checkBoxes[k].isChecked():
                self.output.append(k)
        self.result = True
        self.close()

    def onCancel(self):
        """Reject the dialog output"""
        self.result = False
        self.close()
