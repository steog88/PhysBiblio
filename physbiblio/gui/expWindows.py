"""Module with the classes and functions that manage
the experiments windows and panels.

This file is part of the physbiblio package.
"""
import traceback

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QCursor
from PySide6.QtWidgets import QLineEdit, QPushButton, QToolTip

try:
    import physbiblio.gui.resourcesPyside6
    from physbiblio.config import pbConfig
    from physbiblio.database import pBDB
    from physbiblio.errors import pBLogger
    from physbiblio.gui.basicDialogs import askYesNo
    from physbiblio.gui.catWindows import CatsTreeWindow
    from physbiblio.gui.commonClasses import (
        EditObjectWindow,
        ObjListWindow,
        PBLabel,
        PBMenu,
        PBTableModel,
        pBGuiView,
    )
    from physbiblio.gui.errorManager import pBGUILogger
    from physbiblio.strings.gui import ExpWindowsStrings as ewstr
    from physbiblio.view import pBView
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())


def editExperiment(parentObject, mainWinObject, editIdExp=None):
    """Open a dialog (`EditExperimentDialog`) to edit an experiment
    and process the output.

    Parameters:
        parentObject: the parent widget
        mainWinObject: the object which has
            the `statusBarMessage` and `setWindowTitle` methods
        editIdCat: the id of the experiment to be edited,
            or `None` to create a new one
    """
    if editIdExp is not None:
        edit = pBDB.exps.getDictByID(editIdExp)
    else:
        edit = None
    newExpWin = EditExperimentDialog(parentObject, experiment=edit)
    newExpWin.exec()
    if newExpWin.result:
        data = {}
        for k, v in newExpWin.textValues.items():
            s = "%s" % v.text()
            data[k] = s
        if data["name"].strip() != "":
            if "idExp" in data.keys():
                pBLogger.info(ewstr.updateExp % data["idExp"])
                pBDB.exps.update(data, data["idExp"])
            else:
                pBDB.exps.insert(data)
            message = ewstr.expSaved
            mainWinObject.setWindowTitle(ewstr.winTitleModified)
            try:
                parentObject.recreateTable()
            except AttributeError:
                pBLogger.debug(
                    ewstr.noAttribute % ("parentObject", "recreateTable"), exc_info=True
                )
        else:
            message = ewstr.emptyName
    else:
        message = ewstr.noModifications
    try:
        mainWinObject.statusBarMessage(message)
    except AttributeError:
        pBLogger.debug(
            ewstr.noAttribute % ("mainWinObject", "statusBarMessage"), exc_info=True
        )


def deleteExperiment(parentObject, mainWinObject, idExp, name):
    """Ask confirmation and eventually delete the selected experiment

    Parameters:
        parentObject: the parent widget
        mainWinObject: the object which has
            the `statusBarMessage` and `setWindowTitle` methods
        idExp: the id of the experiment to be deleted
        name: the name of the experiment to be deleted
    """
    if askYesNo(ewstr.askDelete % (idExp, name)):
        pBDB.exps.delete(int(idExp))
        mainWinObject.setWindowTitle(ewstr.winTitleModified)
        message = ewstr.expDeleted
        try:
            parentObject.recreateTable()
        except AttributeError:
            pBLogger.debug(
                ewstr.noAttribute % ("parentObject", "recreateTable"), exc_info=True
            )
    else:
        message = ewstr.nothingChanged
    try:
        mainWinObject.statusBarMessage(message)
    except AttributeError:
        pBLogger.debug(
            ewstr.noAttribute % ("mainWinObject", "statusBarMessage"), exc_info=True
        )


class ExpTableModel(PBTableModel):
    """Model for the experiment list"""

    typeClass = "Exps"

    def __init__(self, parent, exp_list, header, askExps=False, previous=[], *args):
        """Extension of `PBTableModel`
        Initialize the model, save the data and the initial selection

        Parameters:
            parent: the parent widget
            exp_list: the list of experiments records from the database
            header: the names of the column fields
            askExps (default False): if True, enable checkboxes for
                selection of experiments
            previous: the list of previously selected experiments
                (default: an empty list)
        """
        self.dataList = exp_list
        super(ExpTableModel, self).__init__(parent, header, askExps, previous, *args)
        self.prepareSelected()

    def getIdentifier(self, element):
        """Get the string that identifies the given element
        in the database

        Parameter:
            element: the database record
        """
        return element["idExp"]

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
        row = index.row()
        column = index.column()
        try:
            value = self.dataList[row][self.header[column]]
        except IndexError:
            return None

        if role == Qt.CheckStateRole and self.ask and column == 0:
            if not self.selectedElements[self.dataList[row][self.header[0]]]:
                return Qt.Unchecked
            else:
                return Qt.Checked
        if role == Qt.EditRole:
            return value
        if role == Qt.DisplayRole:
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
            if Qt.CheckState(value) == Qt.Checked:
                self.selectedElements[self.dataList[index.row()]["idExp"]] = True
            else:
                self.selectedElements[self.dataList[index.row()]["idExp"]] = False

        self.dataChanged.emit(index, index)
        return True


class ExpsListWindow(ObjListWindow):
    """create a window for printing the list of experiments"""

    colcnt = len(pBDB.tableCols["experiments"])
    colContents = [
        pBDB.tableCols["experiments"][j]
        for j in range(len(pBDB.tableCols["experiments"]))
    ]

    def __init__(
        self, parent=None, askExps=False, askForBib=None, askForCat=None, previous=[]
    ):
        """Constructor, extends `ObjListWindow.__init__`
        with more settings and parameters

        Parameters:
            parent: the parent widget
            askExps: if True, checkboxes will be used
            askForBib: the key identifying the bibtex entry for which
                the experiments are asked
            askForCat: the ID identifying the category for which
                the experiments are asked
            previous: the list (default empty) of initially selected
                experiments
        """
        self.askExps = askExps
        self.askForBib = askForBib
        self.askForCat = askForCat
        self.previous = previous
        self.marked = []
        self.result = False
        self.exps = []
        self.newExpButton = None
        self.acceptButton = None
        self.cancelButton = None
        self.menu = None
        self.timer = None

        ObjListWindow.__init__(self, parent)
        self.setWindowTitle(ewstr.listTitle)

        self.createTable()

    def populateAskExp(self):
        """If selection of experiments is allowed, add some information
        on the bibtex/category for which the experiments are requested
        and a simple message, then create few required empty lists
        """
        if self.askExps:
            if self.askForBib is not None:
                try:
                    bibitem = pBDB.bibs.getByBibkey(
                        self.askForBib, saveQuery=False, verbose=False
                    )[0]
                except IndexError:
                    pBGUILogger.warning(
                        ewstr.entryNotInDb % self.askForBib,
                        exc_info=True,
                    )
                    return
                try:
                    if bibitem["inspire"] != "" and bibitem["inspire"] is not None:
                        link = "<a href='%s'>%s</a>" % (
                            pBView.getLink(self.askForBib, "inspire"),
                            self.askForBib,
                        )
                    elif bibitem["arxiv"] != "" and bibitem["arxiv"] is not None:
                        link = "<a href='%s'>%s</a>" % (
                            pBView.getLink(self.askForBib, "arxiv"),
                            self.askForBib,
                        )
                    elif bibitem["doi"] != "" and bibitem["doi"] is not None:
                        link = "<a href='%s'>%s</a>" % (
                            pBView.getLink(self.askForBib, "doi"),
                            self.askForBib,
                        )
                    else:
                        link = self.askForBib
                    bibtext = PBLabel(
                        ewstr.markExpKAT % (link, bibitem["author"], bibitem["title"])
                    )
                except KeyError:
                    bibtext = PBLabel(ewstr.markExpK % (self.askForBib))
                self.currLayout.addWidget(bibtext)
            elif self.askForCat is not None:
                raise NotImplementedError(ewstr.featureNYI)
            else:
                self.currLayout.addWidget(PBLabel(ewstr.selectDesired))
            self.marked = []
            self.parent().selectedExps = []
        return True

    def onCancel(self):
        """Reject the dialog content and close the window"""
        self.result = False
        self.close()

    def onOk(self):
        """Accept the dialog content
        (update the list of selected experiments)
        and close the window.
        """
        self.parent().selectedExps = [
            idE
            for idE in self.tableModel.selectedElements.keys()
            if self.tableModel.selectedElements[idE] == True
        ]
        self.result = "Ok"
        self.close()

    def onNewExp(self):
        """Action to perform when the creation
        of a new experiment is requested
        """
        editExperiment(self, self.parent())

    def keyPressEvent(self, e):
        """Manage the key press events.
        Do nothing unless `Esc` is pressed:
        in this case close the dialog
        """
        if e.key() == Qt.Key_Escape:
            self.close()
        elif (
            e.key() in (Qt.Key_Return, Qt.Key_Enter)
            and e.modifiers() == Qt.ControlModifier
        ):
            self.onOk()
        elif e.key() == Qt.Key_F and e.modifiers() == Qt.ControlModifier:
            self.filterInput.setFocus()

    def createTable(self):
        """Create the dialog content, connect the model to the view
        and eventually add the buttons at the end
        """
        self.populateAskExp()

        self.exps = pBDB.exps.getAll()

        self.tableModel = ExpTableModel(
            self,
            self.exps,
            pBDB.tableCols["experiments"],
            askExps=self.askExps,
            previous=self.previous,
        )
        self.addFilterInput(ewstr.filterExp)
        self.setProxyStuff(1, Qt.AscendingOrder)

        self.finalizeTable()

        self.newExpButton = QPushButton(ewstr.addNew, self)
        self.newExpButton.clicked.connect(self.onNewExp)
        self.currLayout.addWidget(self.newExpButton)

        if self.askExps:
            self.acceptButton = QPushButton(ewstr.ok, self)
            self.acceptButton.clicked.connect(self.onOk)
            self.currLayout.addWidget(self.acceptButton)

            # cancel button
            self.cancelButton = QPushButton(ewstr.cancel, self)
            self.cancelButton.clicked.connect(self.onCancel)
            self.cancelButton.setAutoDefault(True)
            self.currLayout.addWidget(self.cancelButton)

    def triggeredContextMenuEvent(self, row, col, event):
        """Process event when mouse right-clicks an item.
        Opens a menu with a number of actions

        Parameter:
            row: the row number
            col: a the column number
            event: a `QEvent` instance, used to obtain the mouse
                position where to open the menu
        """
        index = self.proxyModel.index(row, col)
        if not index.isValid():
            return
        try:
            idExp = str(self.proxyModel.sibling(row, 0, index).data())
            expName = str(self.proxyModel.sibling(row, 1, index).data())
        except AttributeError:
            return

        menu = PBMenu()
        self.menu = menu
        titAction = QAction(ewstr.expDescr % expName)
        titAction.setDisabled(True)
        bibAction = QAction(ewstr.openEntryList)
        bntAction = QAction(ewstr.openEntryListNewTab)
        modAction = QAction(ewstr.modify)
        delAction = QAction(ewstr.delete)
        catAction = menu.addAction(ewstr.cats)
        menu.possibleActions = [
            titAction,
            None,
            bibAction,
            bntAction,
            None,
            modAction,
            delAction,
            None,
            catAction,
        ]
        menu.fillMenu()

        action = menu.exec(event.globalPos())

        if action == bibAction:
            self.parent().reloadMainContent(pBDB.bibs.getByExp(idExp))
        elif action == bntAction:
            self.parent().reloadMainContent(pBDB.bibs.getByExp(idExp), newTab=expName)
        elif action == modAction:
            editExperiment(self, self.parent(), idExp)
        elif action == delAction:
            deleteExperiment(self, self.parent(), idExp, expName)
        elif action == catAction:
            previous = [a["idCat"] for a in pBDB.cats.getByExp(idExp)]
            selectCats = CatsTreeWindow(
                parent=self.parent(),
                askCats=True,
                askForExp=idExp,
                expButton=False,
                previous=previous,
            )
            selectCats.exec()
            if selectCats.result == "Ok":
                cats = self.parent().selectedCats
                for p in previous:
                    if p not in cats:
                        pBDB.catExp.delete(p, idExp)
                for c in cats:
                    if c not in previous:
                        pBDB.catExp.insert(c, idExp)
                self.parent().statusBarMessage(ewstr.catsInserted % expName)
        return True

    def handleItemEntered(self, index):
        """Process event when mouse enters an item and
        create a `QTooltip` which describes the category, with a timer

        Parameter:
            index: a `QModelIndex` instance
        """
        if index.isValid():
            row = index.row()
        else:
            return
        idExp = str(self.proxyModel.sibling(row, 0, index).data())
        try:
            self.timer.stop()
            QToolTip.showText(QCursor.pos(), "", self.tableview.viewport())
        except AttributeError:
            pass
        try:
            expData = pBDB.exps.getByID(idExp)[0]
        except IndexError:
            pBGUILogger.exception(ewstr.failedFind)
            return
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(
            lambda: QToolTip.showText(
                QCursor.pos(),
                ewstr.expId.format(idE=idExp, exp=expData["name"])
                + ewstr.entriesCorrespondent.format(en=pBDB.bibExp.countByExp(idExp))
                + ewstr.catsAssociated.format(ca=pBDB.catExp.countByExp(idExp)),
                self.tableview.viewport(),
                self.tableview.visualRect(index),
                3000,
            )
        )
        self.timer.start(500)

    def cellClick(self, index):
        """Process event when mouse clicks an item.
        Currently not used

        Parameter:
            index: a `QModelIndex` instance
        """
        if index.isValid():
            row = index.row()
        else:
            return
        idExp = str(self.proxyModel.sibling(row, 0, index).data())
        return True

    def cellDoubleClick(self, index):
        """Process event when mouse double clicks an item.
        Opens a link if some columns

        Parameter:
            index: a `QModelIndex` instance
        """
        if index.isValid():
            row = index.row()
            col = index.column()
        else:
            return
        idExp = str(self.proxyModel.sibling(row, 0, index).data())
        if self.colContents[col] in ("inspire", "homepage"):
            link = self.proxyModel.sibling(row, col, index).data()
            if link == "" or link is None:
                self.parent().reloadMainContent(pBDB.bibs.getByExp(idExp))
                return
            if self.colContents[col] == "inspire":
                link = pbConfig.inspireExperimentsLink + link
            pBLogger.debug(ewstr.opening % link)
            try:
                pBGuiView.openLink(link, "link")
            except Exception:
                pBLogger.warning(ewstr.openLinkFailed % link, exc_info=True)
        else:
            self.parent().reloadMainContent(pBDB.bibs.getByExp(idExp))
        return True


class EditExperimentDialog(EditObjectWindow):
    """create a window for editing or creating an experiment"""

    def __init__(self, parent=None, experiment=None):
        """Extend `EditObjectWindow.__init__` to define self.data
        and call createForm

        Parameters:
            parent: the parent widget
            experiment: the database record or dictionary which
                contains the experiment information
        """
        super(EditExperimentDialog, self).__init__(parent)
        if experiment is None:
            self.data = {}
            for k in pBDB.tableCols["experiments"]:
                self.data[k] = ""
        else:
            self.data = experiment
        self.acceptButton = None
        self.cancelButton = None
        self.createForm()

    def createForm(self):
        """Create the form labels, fields, buttons"""
        self.setWindowTitle(ewstr.expEdit)

        i = 0
        for k in pBDB.tableCols["experiments"]:
            val = self.data[k]
            if k != "idExp" or (k == "idExp" and self.data[k] != ""):
                i += 1
                self.currGrid.addWidget(PBLabel(k), i * 2 - 1, 0)
                self.currGrid.addWidget(
                    PBLabel("(%s)" % pBDB.descriptions["experiments"][k]), i * 2 - 1, 1
                )
                self.textValues[k] = QLineEdit(str(val))
                if k == "idExp":
                    self.textValues[k].setEnabled(False)
                self.currGrid.addWidget(self.textValues[k], i * 2, 0, 1, 2)

        # OK button
        self.acceptButton = QPushButton(ewstr.ok, self)
        self.acceptButton.clicked.connect(self.onOk)
        self.currGrid.addWidget(self.acceptButton, i * 2 + 1, 0)

        # cancel button
        self.cancelButton = QPushButton(ewstr.cancel, self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        self.currGrid.addWidget(self.cancelButton, i * 2 + 1, 1)

        self.setGeometry(100, 100, 400, 50 * i)
        self.centerWindow()
