"""Module with the classes and functions
that manage the some dialog windows.

This file is part of the physbiblio package.
"""
import ast
import traceback

import six
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QLineEdit,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

try:
    import physbiblio.gui.resourcesPyside2
    from physbiblio.config import configuration_params, pbConfig
    from physbiblio.database import pBDB
    from physbiblio.errors import pBLogger
    from physbiblio.gui.basicDialogs import (
        askDirName,
        askFileNames,
        askSaveFileName,
        askYesNo,
        infoMessage,
    )
    from physbiblio.gui.catWindows import CatsTreeWindow
    from physbiblio.gui.commonClasses import (
        ObjListWindow,
        PBComboBox,
        PBDDTableWidget,
        PBDialog,
        PBImportedTableModel,
        PBLabel,
        PBLabelRight,
        PBTableView,
        PBTrueFalseCombo,
    )
    from physbiblio.gui.errorManager import pBGUILogger
    from physbiblio.strings.gui import DialogWindowsStrings as dwstr
    from physbiblio.webimport.webInterf import physBiblioWeb
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())


class ConfigEditColumns(PBDialog):
    """Extend `PBDialog` to ask the columns
    that must appear in the main table
    """

    excludeCols = [
        "crossref",
        "bibtex",
        "exp_paper",
        "lecture",
        "phd_thesis",
        "review",
        "proceeding",
        "book",
        "noUpdate",
        "bibdict",
        "abstract",
    ]
    moreCols = [
        "title",
        "author",
        "journal",
        "volume",
        "pages",
        "primaryclass",
        "booktitle",
        "reportnumber",
    ]

    def __init__(self, parent=None, previous=None):
        """Extend `PBDialog.__init__` and create the form structure

        Parameters:
            parent: teh parent widget
            previous: list of columns which must appear
                as selected at the beginning
        """
        super(ConfigEditColumns, self).__init__(parent)
        self.gridlayout = None
        self.items = []
        self.listAll = None
        self.listSel = None
        self.allItems = None
        self.selItems = None
        self.previousSelected = (
            previous if previous is not None else pbConfig.params["bibtexListColumns"]
        )
        self.selected = self.previousSelected
        self.result = False
        self.acceptButton = None
        self.cancelButton = None
        self.initUI()

    def onCancel(self):
        """Reject the output (set self.result to False and close)"""
        self.result = False
        self.close()

    def onOk(self):
        """Accept the output and prepare `self.selected`"""
        self.result = True
        self.selected = []
        for row in range(self.listSel.rowCount()):
            self.selected.append(self.listSel.item(row, 0).text())
        self.close()

    def initUI(self):
        """Initialize the `PBDDTableWidget`s and their content,
        plus the buttons and labels
        """
        self.gridlayout = QGridLayout()
        self.setLayout(self.gridlayout)

        self.items = []
        self.listAll = PBDDTableWidget(self, dwstr.colsAvailable)
        self.listSel = PBDDTableWidget(self, dwstr.colsSelected)
        self.gridlayout.addWidget(PBLabel(dwstr.colsDragAndDrop), 0, 0, 1, 2)
        self.gridlayout.addWidget(self.listAll, 1, 0)
        self.gridlayout.addWidget(self.listSel, 1, 1)

        self.allItems = list(pBDB.descriptions["entries"]) + self.moreCols
        self.selItems = self.previousSelected
        isel = 0
        iall = 0
        for col in self.selItems + [i for i in self.allItems if i not in self.selItems]:
            if col in self.excludeCols:
                continue
            item = QTableWidgetItem(col)
            self.items.append(item)
            if col in self.selItems:
                self.listSel.insertRow(isel)
                self.listSel.setItem(isel, 0, item)
                isel += 1
            else:
                self.listAll.insertRow(iall)
                self.listAll.setItem(iall, 0, item)
                iall += 1

        self.acceptButton = QPushButton(dwstr.ok, self)
        self.acceptButton.clicked.connect(self.onOk)
        self.gridlayout.addWidget(self.acceptButton, 2, 0)

        self.cancelButton = QPushButton(dwstr.cancel, self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        self.gridlayout.addWidget(self.cancelButton, 2, 1)


class ConfigWindow(PBDialog):
    """Create a window for editing the configuration settings"""

    def __init__(self, parent=None):
        """Simple extension of `PBDialog.__init__`"""
        super(ConfigWindow, self).__init__(parent)
        self.textValues = []
        self.result = False
        self.selectedCats = None
        self.selectedExps = None
        self.grid = None
        self.acceptButton = None
        self.cancelButton = None
        self.initUI()

    def onCancel(self):
        """Reject the output (set self.result to False and close)"""
        self.result = False
        self.close()

    def onOk(self):
        """Accept the output (set self.result to True and close)"""
        self.result = True
        self.close()

    def editPDFFolder(self):
        """Open a dialog to select a new folder name
        for the PDF path, and save the result
        in the `ConfigWindow` interface
        """
        ix = pbConfig.paramOrder.index("pdfFolder")
        folder = askDirName(
            parent=None,
            dir=self.textValues[ix][1].text(),
            title=dwstr.dirPDFSave,
        )
        if folder.strip() != "":
            self.textValues[ix][1].setText(str(folder))

    def editFile(self, paramkey="logFileName", text=dwstr.logFileName, filter="*.log"):
        """Open a dialog to select a new file name
        for a configuration parameter, and save the result
        in the `ConfigWindow` interface

        Parameters:
            paramkey: the parameter name in the configuration dictionary
            text: description in the file dialog
            filter: filter the folder content in the file dialog
        """
        if paramkey not in pbConfig.paramOrder:
            pBLogger.warning(dwstr.invalidParamkey % paramkey)
            return
        ix = pbConfig.paramOrder.index(paramkey)
        fname = askSaveFileName(
            parent=None, title=text, dir=self.textValues[ix][1].text(), filter=filter
        )
        if fname.strip() != "":
            self.textValues[ix][1].setText(str(fname))

    def editColumns(self):
        """Open a dialog to select and/or reorder the list of columns
        to show in the entries list, and save the result
        in the `ConfigWindow` interface
        """
        ix = pbConfig.paramOrder.index("bibtexListColumns")
        window = ConfigEditColumns(
            self, ast.literal_eval(self.textValues[ix][1].text().strip())
        )
        window.exec_()
        if window.result:
            columns = window.selected
            self.textValues[ix][1].setText(str(columns))

    def editDefCats(self):
        """Open a dialog to select a the default categories
        for the imported entries, and save the result
        in the `ConfigWindow` interface
        """
        ix = pbConfig.paramOrder.index("defaultCategories")
        selectCats = CatsTreeWindow(
            parent=self,
            askCats=True,
            expButton=False,
            previous=ast.literal_eval(self.textValues[ix][1].text().strip()),
        )
        selectCats.exec_()
        if selectCats.result == "Ok":
            self.textValues[ix][1].setText(str(self.selectedCats))

    def initUI(self):
        """Create and fill the `QGridLayout`"""
        self.setWindowTitle(dwstr.config)

        grid = QGridLayout()
        self.grid = grid
        grid.setSpacing(1)

        i = 0
        for k in pbConfig.paramOrder:
            i += 1
            val = (
                pbConfig.params[k]
                if isinstance(pbConfig.params[k], six.string_types)
                else str(pbConfig.params[k])
            )
            grid.addWidget(
                PBLabel(
                    "%s (<i>%s</i>%s)"
                    % (
                        configuration_params[k].description,
                        k,
                        (" - " + dwstr.globalSett)
                        if configuration_params[k].isGlobal
                        else "",
                    )
                ),
                i - 1,
                0,
                1,
                2,
            )
            if k == "bibtexListColumns":
                self.textValues.append([k, QPushButton(val)])
                self.textValues[-1][1].clicked.connect(self.editColumns)
            elif k == "pdfFolder":
                self.textValues.append([k, QPushButton(val)])
                self.textValues[-1][1].clicked.connect(self.editPDFFolder)
            elif k == "loggingLevel":
                try:
                    self.textValues.append(
                        [
                            k,
                            PBComboBox(
                                self,
                                pbConfig.loggingLevels,
                                pbConfig.loggingLevels[int(val)],
                            ),
                        ]
                    )
                except (IndexError, ValueError):
                    pBGUILogger.warning(dwstr.invalidLoggingLevel)
                    self.textValues.append(
                        [
                            k,
                            PBComboBox(
                                self,
                                pbConfig.loggingLevels,
                                pbConfig.loggingLevels[
                                    int(configuration_params["loggingLevel"].default)
                                ],
                            ),
                        ]
                    )
            elif k == "logFileName":
                self.textValues.append([k, QPushButton(val)])
                self.textValues[-1][1].clicked.connect(self.editFile)
            elif k == "defaultCategories":
                self.textValues.append([k, QPushButton(val)])
                self.textValues[-1][1].clicked.connect(self.editDefCats)
            elif configuration_params[k].special == "boolean":
                self.textValues.append([k, PBTrueFalseCombo(self, val)])
            else:
                self.textValues.append([k, QLineEdit(val)])
            grid.addWidget(self.textValues[i - 1][1], i - 1, 2, 1, 2)

        # OK button
        self.acceptButton = QPushButton(dwstr.ok, self)
        self.acceptButton.clicked.connect(self.onOk)
        # width = self.acceptButton.fontMetrics().boundingRect('OK').width() + 7
        # self.acceptButton.setMaximumWidth(width)
        grid.addWidget(self.acceptButton, i, 0)

        # cancel button
        self.cancelButton = QPushButton(dwstr.cancel, self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        # width = self.cancelButton.fontMetrics().boundingRect('Cancel').width() + 7
        # self.cancelButton.setMaximumWidth(width)
        grid.addWidget(self.cancelButton, i, 1)

        self.setGeometry(100, 100, 1000, 30 * i)
        self.setLayout(grid)


class LogFileContentDialog(PBDialog):
    """Create a window for showing the logFile content"""

    title = dwstr.logFileContent

    def __init__(self, parent=None):
        """Instantiate class and create its widgets

        Parameter:
            parent: the parent widget
        """
        PBDialog.__init__(self, parent)
        self.textEdit = None
        self.closeButton = None
        self.clearButton = None
        self.initUI()

    def clearLog(self):
        """Ask confirmation, then eventually clear
        the content of the log file
        """
        if askYesNo(dwstr.clearLogAsk):
            try:
                open(pbConfig.params["logFileName"], "w").close()
            except IOError:
                pBGUILogger.exception(dwstr.clearLogFailClear)
            else:
                infoMessage(dwstr.clearLogDone)
                self.close()

    def initUI(self):
        """Create window layout and buttons,
        read log file content and print it in the `QPlainTextEdit`
        """
        self.setWindowTitle(self.title)

        grid = QVBoxLayout()
        grid.setSpacing(1)

        grid.addWidget(PBLabel(dwstr.logFileRead % pbConfig.params["logFileName"]))
        try:
            with open(pbConfig.params["logFileName"]) as r:
                text = r.read()
        except IOError:
            text = dwstr.clearLogFailRead
            pBLogger.exception(text)
        self.textEdit = QPlainTextEdit(text)
        self.textEdit.setReadOnly(True)
        grid.addWidget(self.textEdit)

        self.closeButton = QPushButton(dwstr.close, self)
        self.closeButton.setAutoDefault(True)
        self.closeButton.clicked.connect(self.close)
        grid.addWidget(self.closeButton)

        self.clearButton = QPushButton(dwstr.clearLogTitle, self)
        self.clearButton.clicked.connect(self.clearLog)
        grid.addWidget(self.clearButton)

        self.setGeometry(100, 100, 800, 800)
        self.setLayout(grid)


class PrintText(PBDialog):
    """Create a window for printing text of command line output"""

    stopped = Signal()
    pbMax = Signal(float)
    pbVal = Signal(float)

    def __init__(
        self, parent=None, title="", progressBar=True, noStopButton=False, message=None
    ):
        """Constructor.
        Set some properties and create the GUI of the dialog

        Parameters:
            parent: the parent widget
            title: the window title. If an empty string,
                "Redirect print" will be used
            progressBar: True (default) if the widget must have a progress bar
            noStopButton (default False): True if the widget must have
                a "stop" button to stop the iterations
            message: a text to be inserted as a `PBLabel` in the dialog
        """
        super(PrintText, self).__init__(parent)
        self._wantToClose = False
        self.grid = None
        self.progressBar = None
        self.textEdit = None
        self.closeButton = None
        self.cancelButton = None
        if title != "":
            self.title = title
        else:
            self.title = dwstr.redirectPrint
        self.setProgressBar = progressBar
        self.noStopButton = noStopButton
        self.message = message
        self.pbMax.connect(self.progressBarMax)
        self.pbVal.connect(self.progressBarValue)
        self.initUI()

    def keyPressEvent(self, e):
        """Intercept press keys and only exit if escape is pressed
        when closing is enabled

        Parameters:
            e: the `PySide2.QtGui.QKeyEvent`
        """
        if e.key() == Qt.Key_Escape and self._wantToClose:
            self.close()

    def closeEvent(self, event):
        """Manage the `closeEvent` of the dialog.
        Reject unless `self._wantToClose` is True

        Parameter:
            event: a `QEvent`
        """
        if self._wantToClose:
            super(PrintText, self).closeEvent(event)
        else:
            event.ignore()

    def initUI(self):
        """Create the main `QTextEdit`, the buttons and the `QProgressBar`"""
        self.setWindowTitle(self.title)

        grid = QGridLayout()
        self.grid = grid
        grid.setSpacing(1)

        if self.message is not None and self.message.strip() != "":
            grid.addWidget(PBLabel("%s" % self.message))

        self.textEdit = QTextEdit()
        grid.addWidget(self.textEdit)

        if self.setProgressBar:
            self.progressBar = QProgressBar(self)
            grid.addWidget(self.progressBar)

        # cancel button...should learn how to connect it with a thread kill
        if not self.noStopButton:
            self.cancelButton = QPushButton(dwstr.stop, self)
            self.cancelButton.clicked.connect(self.stopExec)
            self.cancelButton.setAutoDefault(True)
            grid.addWidget(self.cancelButton)
        self.closeButton = QPushButton(dwstr.close, self)
        self.closeButton.setDisabled(True)
        grid.addWidget(self.closeButton)

        self.setGeometry(100, 100, 600, 600)
        self.setLayout(grid)
        self.centerWindow()

    def appendText(self, text):
        """Add the given text to the end of the `self.textEdit` content.

        Parameter:
            text: the string to be appended
        """
        self.textEdit.moveCursor(QTextCursor.End)
        self.textEdit.insertPlainText(text)

    def progressBarMin(self, minimum):
        """Set the minimum value for the progress bar

        Parameter:
            minimum (int or float): the value
        """
        if self.setProgressBar:
            self.progressBar.setMinimum(minimum)

    def progressBarMax(self, maximum):
        """Set the maximum value for the progress bar

        Parameter:
            maximum (int or float): the value
        """
        if self.setProgressBar:
            self.progressBar.setMaximum(maximum)

    def progressBarValue(self, value):
        """Set the current value for the progress bar

        Parameter:
            value (int or float): the value
        """
        if self.setProgressBar:
            self.progressBar.setValue(value)

    def stopExec(self):
        """Stop the iterations through the `stopped` Signal
        and disable the `cancelButton`
        """
        self.cancelButton.setDisabled(True)
        self.stopped.emit()

    def enableClose(self):
        """Enable the close button and set `self._wantToClose` to True"""
        self._wantToClose = True
        self.closeButton.setEnabled(True)
        try:
            self.cancelButton.setEnabled(False)
        except Exception:
            pass


class AdvancedImportDialog(PBDialog):
    """create a window for the advanced import"""

    def __init__(self, parent=None):
        """Simple extension of `PBDialog.__init__`"""
        super(AdvancedImportDialog, self).__init__(parent)
        self.result = False
        self.grid = None
        self.searchStr = None
        self.comboMethod = None
        self.acceptButton = None
        self.cancelButton = None
        self.initUI()

    def onCancel(self):
        """Reject the output (set self.result to False and close)"""
        self.result = False
        self.close()

    def onOk(self):
        """Accept the output (set self.result to True and close)"""
        self.result = True
        self.close()

    def initUI(self):
        """Create and fill the `QGridLayout`"""
        self.setWindowTitle(dwstr.advImpTitle)

        grid = QGridLayout()
        self.grid = grid
        grid.setSpacing(1)

        ##search
        grid.addWidget(PBLabel(dwstr.advImpSearch), 0, 0)
        self.searchStr = QLineEdit("")
        grid.addWidget(self.searchStr, 0, 1)

        grid.addWidget(PBLabel(dwstr.advImpMethod), 1, 0)
        self.comboMethod = PBComboBox(
            self,
            ["INSPIRE-HEP", "ADS-NASA", "arXiv", "DOI", "ISBN"],
            current="INSPIRE-HEP",
        )
        grid.addWidget(self.comboMethod, 1, 1)

        # OK button
        self.acceptButton = QPushButton(dwstr.ok, self)
        self.acceptButton.clicked.connect(self.onOk)
        grid.addWidget(self.acceptButton, 2, 0)

        # cancel button
        self.cancelButton = QPushButton(dwstr.cancel, self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        grid.addWidget(self.cancelButton, 2, 1)

        self.setGeometry(100, 100, 400, 100)
        self.setLayout(grid)
        self.searchStr.setFocus()
        self.centerWindow()


class AdvancedImportSelect(ObjListWindow):
    """create a window for the advanced import"""

    def __init__(self, bibs={}, parent=None):
        """Set some properties and call `initUI`

        Parameters:
            bibs: a dictionary containing the imported bibtex entries.
                Each element should be a dictionary containing at least
                a "bibpars" item, a dictionary with at least the keys
                ["ID", "title", "author", "eprint", "doi"],
                and a boolean "exist" item.
            parent: the parent widget
        """
        self.bibs = bibs
        super(AdvancedImportSelect, self).__init__(parent, gridLayout=True)
        self.checkBoxes = []
        self.result = False
        self.askCats = None
        self.tableModel = None
        self.askCats = None
        self.acceptButton = None
        self.cancelButton = None
        self.initUI()

    def onCancel(self):
        """Reject the output (set self.result to False and close)"""
        self.result = False
        self.close()

    def onOk(self):
        """Accept the output (set self.result to True and close)"""
        self.selected = self.tableModel.selectedElements
        self.result = True
        self.close()

    def keyPressEvent(self, e):
        """Intercept press keys and exit if escape is pressed

        Parameters:
            e: the `PySide2.QtGui.QKeyEvent`
        """
        if e.key() == Qt.Key_Escape:
            self.result = False
            self.close()

    def initUI(self):
        """Create and fill the `QGridLayout`"""
        self.setWindowTitle(dwstr.advImpResults)

        self.currLayout.setSpacing(1)

        self.currLayout.addWidget(PBLabel(dwstr.importSelRes))

        headers = ["ID", "title", "author", "eprint", "doi"]
        for k in self.bibs.keys():
            try:
                self.bibs[k]["bibpars"]["eprint"] = self.bibs[k]["bibpars"]["arxiv"]
            except KeyError:
                pass
            try:
                self.bibs[k]["bibpars"]["author"] = self.bibs[k]["bibpars"]["authors"]
            except KeyError:
                pass
            for f in headers:
                try:
                    self.bibs[k]["bibpars"][f] = self.bibs[k]["bibpars"][f].replace(
                        "\n", " "
                    )
                except KeyError:
                    pass
        self.tableModel = PBImportedTableModel(self, self.bibs, headers)
        self.addFilterInput(dwstr.filterEntries, gridPos=(1, 0))
        self.setProxyStuff(0, Qt.AscendingOrder)
        self.finalizeTable(gridPos=(2, 0, 1, 2))

        i = 3
        self.askCats = QCheckBox(dwstr.askCats, self)
        self.askCats.toggle()
        self.currLayout.addWidget(self.askCats, i, 0)

        # OK button
        self.acceptButton = QPushButton(dwstr.ok, self)
        self.acceptButton.clicked.connect(self.onOk)
        self.currLayout.addWidget(self.acceptButton, i + 1, 0)

        # cancel button
        self.cancelButton = QPushButton(dwstr.cancel, self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        self.currLayout.addWidget(self.cancelButton, i + 2, 0)

    def triggeredContextMenuEvent(self, row, col, event):
        """Does nothing"""
        pass

    def handleItemEntered(self, index):
        """Does nothing"""
        pass

    def cellClick(self, index):
        """Does nothing"""
        pass

    def cellDoubleClick(self, index):
        """Does nothing"""
        pass


class DailyArxivDialog(PBDialog):
    """create a window for the advanced import"""

    def __init__(self, parent=None):
        """Simple extension of `PBDialog.__init__`"""
        super(DailyArxivDialog, self).__init__(parent)
        self.result = False
        self.grid = None
        self.comboSub = None
        self.comboCat = None
        self.acceptButton = None
        self.cancelButton = None
        self.initUI()

    def onCancel(self):
        """Reject the output (set self.result to False and close)"""
        self.result = False
        self.close()

    def onOk(self):
        """Accept the output (set self.result to True and close)"""
        self.result = True
        self.close()

    def updateCat(self, category):
        """Replace the current content of the `self.comboSub` combobox
        with the new list of subcategories of the given category

        Parameter:
            category: the name of the category in the
                `physBiblioWeb.webSearch["arxiv"].categories` dictionary
        """
        self.comboSub.clear()
        self.comboSub.addItems(
            ["--"] + physBiblioWeb.webSearch["arxiv"].categories[category]
        )

    def initUI(self):
        """Create and fill the `QGridLayout`"""
        self.setWindowTitle(dwstr.arxDailyTitle)

        self.grid = QGridLayout()
        self.grid.setSpacing(1)

        ##combo boxes
        self.grid.addWidget(PBLabel(dwstr.arxCat), 0, 0)
        self.comboCat = PBComboBox(
            self, [""] + sorted(physBiblioWeb.webSearch["arxiv"].categories.keys())
        )
        self.comboCat.currentIndexChanged[str].connect(self.updateCat)
        self.grid.addWidget(self.comboCat, 0, 1)

        self.grid.addWidget(PBLabel(dwstr.arxSub), 1, 0)
        self.comboSub = PBComboBox(self, [""])
        self.grid.addWidget(self.comboSub, 1, 1)

        # OK button
        self.acceptButton = QPushButton(dwstr.ok, self)
        self.acceptButton.clicked.connect(self.onOk)
        self.grid.addWidget(self.acceptButton, 2, 0)

        # cancel button
        self.cancelButton = QPushButton(dwstr.cancel, self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        self.grid.addWidget(self.cancelButton, 2, 1)

        self.setLayout(self.grid)

        self.setGeometry(100, 100, 400, 100)
        self.centerWindow()


class DailyArxivSelect(AdvancedImportSelect):
    """create a window for the advanced import"""

    def __init__(self, bibs={}, parent=None):
        """Set some properties and call `initUI`

        Parameters:
            bibs: a dictionary containing the imported bibtex entries.
                Each element should be a dictionary containing at least
                a "bibpars" item, a dictionary with at least the keys
                ["ID", "title", "author", "eprint", "doi"],
                and a boolean "exist" item.
            parent: the parent widget
        """
        self.tableModel = None
        self.askCats = None
        self.acceptButton = None
        self.cancelButton = None
        self.abstractArea = None
        super(DailyArxivSelect, self).__init__(bibs, parent)

    def initUI(self):
        """Initialize the widget content, with the buttons and labels"""
        self.setWindowTitle(dwstr.arxResTitle)

        self.currLayout.setSpacing(1)

        self.currLayout.addWidget(PBLabel(dwstr.importSelRes))

        headers = ["eprint", "type", "title", "author", "primaryclass"]
        self.tableModel = PBImportedTableModel(
            self, self.bibs, headers + ["abstract"], idName="eprint"
        )
        self.addFilterInput(dwstr.filterEntries, gridPos=(1, 0))
        self.setProxyStuff(0, Qt.AscendingOrder)

        self.finalizeTable(gridPos=(2, 0, 1, 2))

        i = 3
        self.askCats = QCheckBox(dwstr.askCats, self)
        self.askCats.toggle()
        self.currLayout.addWidget(self.askCats, i, 0)

        # OK button
        self.acceptButton = QPushButton(dwstr.ok, self)
        self.acceptButton.clicked.connect(self.onOk)
        self.currLayout.addWidget(self.acceptButton, i + 1, 0)

        # cancel button
        self.cancelButton = QPushButton(dwstr.cancel, self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        self.currLayout.addWidget(self.cancelButton, i + 2, 0)

        self.abstractArea = QTextEdit(dwstr.abstract, self)
        self.currLayout.addWidget(self.abstractArea, i + 3, 0, 4, 2)

    def cellClick(self, index):
        """Click action

        Parameter:
            index: a `QModelIndex` instance
        """
        if not index.isValid():
            return
        row = index.row()
        try:
            eprint = str(self.proxyModel.sibling(row, 0, index).data())
        except AttributeError:
            pBLogger.debug(dwstr.invalidData, exc_info=True)
            return
        if "already existing" in eprint:
            eprint = eprint.replace(dwstr.alreadyExisting, "")
        if hasattr(self, "abstractFormulas") and self.abstractFormulas is not None:
            a = self.abstractFormulas(
                self.parent(),
                self.bibs[eprint]["bibpars"]["abstract"],
                customEditor=self.abstractArea,
                statusMessages=False,
            )
            a.doText()
        else:
            pBLogger.debug(dwstr.errorAF % eprint)


class ExportForTexDialog(PBDialog):
    """create a window for the "export for tex" function"""

    def __init__(self, parent=None):
        """Simple extension of `PBDialog.__init__`"""
        super(ExportForTexDialog, self).__init__(parent)
        self.numTexFields = 1
        self.bibName = ""
        self.texFileNames = [""]
        self.texNames = []
        self.update = False
        self.remove = False
        self.reorder = False
        self.result = False
        self.texButtons = None
        self.bibButton = None
        self.removeCheck = None
        self.reorderCheck = None
        self.updateCheck = None
        self.addTexButton = None
        self.acceptButton = None
        self.cancelButton = None
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.initUI()

    def readForm(self):
        """Read the form content"""
        self.update = self.updateCheck.isChecked()
        self.remove = self.removeCheck.isChecked()
        self.reorder = self.reorderCheck.isChecked()
        self.bibName = self.bibButton.text()
        if self.bibName == dwstr.selFile:
            self.bibName = ""
        self.texFileNames = []
        for button in self.texButtons:
            txt = button.text()
            if "[" in txt:
                try:
                    txt = ast.literal_eval(txt)
                except ValueError:
                    pBLogger.warning(dwstr.invalidText % s)
            self.texFileNames.append(txt)
        tmp = []
        for fn in self.texFileNames:
            if isinstance(fn, list):
                tmp += fn
            else:
                tmp.append(fn)
        self.texNames = [f for f in tmp if f != dwstr.selFile and f != ""]

    def onAddTex(self):
        """Add a new line for the texs"""
        self.numTexFields += 1
        self.readForm()
        for ix in range(self.numTexFields):
            try:
                a = self.texFileNames[ix]
            except IndexError:
                self.texFileNames.append("")
        self.cleanLayout()
        self.initUI()

    def onCancel(self):
        """Reject the output (set self.result to False and close)"""
        self.result = False
        self.close()

    def onOk(self):
        """Accept the output (set self.result to True and close)"""
        self.result = True
        self.readForm()
        self.close()

    def onAskBib(self):
        """Accept the output (set self.result to True and close)"""
        outFName = askSaveFileName(
            self,
            title=dwstr.whereExportBibs,
            filter="Bibtex (*.bib)",
        )
        if outFName != "":
            self.bibButton.setText(outFName)

    def onAskTex(self, ix):
        """Accept the output (set self.result to True and close)"""
        texFile = askFileNames(
            self,
            title=dwstr.whichTexFiles,
            filter="Latex (*.tex)",
        )
        if texFile != "" and texFile != []:
            self.texButtons[ix].setText("%s" % texFile)

    def initUI(self):
        """Create and fill the `QGridLayout`"""
        self.setWindowTitle(dwstr.exportTexFile)
        self.grid.setSpacing(1)

        self.grid.addWidget(PBLabelRight(dwstr.bibName), 0, 0, 1, 2)
        self.bibButton = QPushButton(
            dwstr.selFile if self.bibName == "" else self.bibName, self
        )
        self.bibButton.clicked.connect(self.onAskBib)
        self.grid.addWidget(self.bibButton, 0, 2, 1, 2)

        self.texButtons = []
        for ix in range(self.numTexFields):
            self.grid.addWidget(PBLabelRight(dwstr.texNames), ix + 1, 0, 1, 2)
            self.texButtons.append(
                QPushButton(
                    dwstr.selFile
                    if self.texFileNames[ix] == ""
                    else "%s" % self.texFileNames[ix],
                    self,
                )
            )
            self.texButtons[ix].clicked.connect(lambda s=False, p=ix: self.onAskTex(p))
            self.grid.addWidget(self.texButtons[ix], ix + 1, 2, 1, 2)

        i = 2 + self.numTexFields
        self.addTexButton = QPushButton(dwstr.exportAddTex, self)
        self.addTexButton.clicked.connect(self.onAddTex)
        self.grid.addWidget(self.addTexButton, i - 1, 2)

        self.removeCheck = QCheckBox(dwstr.exportRemove, self)
        if self.remove:
            self.removeCheck.setChecked(True)
        self.grid.addWidget(self.removeCheck, i, 0, 1, 2)
        self.updateCheck = QCheckBox(dwstr.exportUpdate, self)
        if self.update:
            self.updateCheck.setChecked(True)
        self.grid.addWidget(self.updateCheck, i, 2, 1, 2)
        self.reorderCheck = QCheckBox(dwstr.exportReorder, self)
        if self.reorder:
            self.reorderCheck.setChecked(True)
        self.grid.addWidget(self.reorderCheck, i + 1, 0, 1, 4)

        # OK button
        self.acceptButton = QPushButton(dwstr.ok, self)
        self.acceptButton.clicked.connect(self.onOk)
        self.grid.addWidget(self.acceptButton, i + 2, 1)

        # cancel button
        self.cancelButton = QPushButton(dwstr.cancel, self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        self.grid.addWidget(self.cancelButton, i + 2, 2)

        self.setGeometry(100, 100, 400, 25 * (i + 3))
        self.centerWindow()
