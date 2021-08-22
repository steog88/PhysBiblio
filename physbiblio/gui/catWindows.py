"""Module with the classes and functions that manage
the categories windows and panels.

This file is part of the physbiblio package.
"""
import traceback

from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import (
    QAction,
    QLineEdit,
    QPushButton,
    QToolTip,
    QTreeView,
    QVBoxLayout,
)

try:
    import physbiblio.gui.resourcesPyside2
    from physbiblio.config import pbConfig
    from physbiblio.database import cats_alphabetical, pBDB
    from physbiblio.errors import pBLogger
    from physbiblio.gui.basicDialogs import askYesNo
    from physbiblio.gui.commonClasses import (
        EditObjectWindow,
        LeafFilterProxyModel,
        NamedElement,
        NamedNode,
        PBDialog,
        PBLabel,
        PBMenu,
        TreeModel,
        TreeNode,
    )
    from physbiblio.gui.errorManager import pBGUILogger
    from physbiblio.strings.gui import CatWindowsStrings as cwstr
    from physbiblio.view import pBView
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())


def editCategory(parentObject, mainWinObject, editIdCat=None, useParentCat=None):
    """Open a dialog (`EditCategoryDialog`) to edit a category
    and process the output.

    Parameters:
        parentObject: the parent widget
        mainWinObject: the object which has
            the `statusBarMessage` and `setWindowTitle` methods
        editIdCat: the id of the category to be edited,
            or `None` to create a new category
        useParentCat: the parent category (if any)
            of the one to be edited
    """
    if editIdCat is not None:
        edit = pBDB.cats.getDictByID(editIdCat)
    else:
        edit = None
    newCatWin = EditCategoryDialog(
        parentObject, category=edit, useParentCat=useParentCat
    )
    newCatWin.exec_()
    if newCatWin.result:
        data = {}
        for k, v in newCatWin.textValues.items():
            if k == "parentCat":
                try:
                    s = str(newCatWin.selectedCats[0])
                except IndexError:
                    s = "0"
            else:
                s = "%s" % v.text()
            data[k] = s
        if data["name"].strip() != "":
            if "idCat" in data.keys():
                pBLogger.info(cwstr.updateCat % data["idCat"])
                pBDB.cats.update(data, data["idCat"])
            else:
                pBDB.cats.insert(data)
            message = cwstr.catSaved
            mainWinObject.setWindowTitle(cwstr.winTitleModified)
            try:
                parentObject.recreateTable()
            except AttributeError:
                pBLogger.debug(
                    cwstr.noAttribute % ("parentObject", "recreateTable"), exc_info=True
                )
        else:
            message = cwstr.emptyName
    else:
        message = cwstr.noModifications
    try:
        mainWinObject.statusBarMessage(message)
    except AttributeError:
        pBLogger.debug(
            cwstr.noAttribute % ("mainWinObject", "statusBarMessage"), exc_info=True
        )


def deleteCategory(parentObject, mainWinObject, idCat, name):
    """Ask confirmation and eventually delete the selected category

    Parameters:
        parentObject: the parent widget
        mainWinObject: the object which has
            the `statusBarMessage` and `setWindowTitle` methods
        idCat: the id of the category to be deleted
        name: the name of the category to be deleted
    """
    if askYesNo(cwstr.askDelete % (idCat, name)):
        pBDB.cats.delete(int(idCat))
        mainWinObject.setWindowTitle(cwstr.winTitleModified)
        message = cwstr.catDeleted
        try:
            parentObject.recreateTable()
        except AttributeError:
            pBLogger.debug(
                cwstr.noAttribute % ("parentObject", "recreateTable"), exc_info=True
            )
    else:
        message = cwstr.nothingChanged
    try:
        mainWinObject.statusBarMessage(message)
    except AttributeError:
        pBLogger.debug(
            cwstr.noAttribute % ("mainWinObject", "statusBarMessage"), exc_info=True
        )


class CatsModel(TreeModel):
    """Model for the categories tree"""

    def __init__(
        self, cats, rootElements, parent=None, previous=[], multipleRecords=False
    ):
        """Initialize the model, save the data and the initial selection

        Parameters:
            cats: the list of categories records from the database
            rootElements: the list of root elements of the tree
            parent: the parent widget
                (default: None)
            previous: the list of previously selected categories
                (default: an empty list)
            multipleRecords: activate tristate for selecting categories
                for multiple records
                (default False)
        """
        self.cats = cats
        self.rootElements = rootElements
        TreeModel.__init__(self)
        self.parentObj = parent
        self.selectedCats = {}
        self.previousSaved = {}
        for cat in self.cats:
            self.selectedCats[cat["idCat"]] = False
            self.previousSaved[cat["idCat"]] = False
        for prevIx in previous:
            if prevIx in [cat["idCat"] for cat in self.cats]:
                if multipleRecords:
                    self.previousSaved[prevIx] = True
                    self.selectedCats[prevIx] = "p"
                else:
                    self.selectedCats[prevIx] = True
            else:
                pBLogger.warning(cwstr.invalidCat % prevIx)

    def _getRootNodes(self):
        """Obtain the list of named nodes which represent the root
        elements of the tree

        Output:
            a list of `NamedNode`s
        """
        return [
            NamedNode(elem, None, index) for index, elem in enumerate(self.rootElements)
        ]

    def columnCount(self, parent):
        """Return the number of columns, fixed to one"""
        return 1

    def data(self, index, role):
        """Return the cell data for the given index and role

        Parameters:
            index: the `QModelIndex` for which the data are required
            role: the desired Qt role for the data

        Output:
            None if the index or the role are not valid,
            the cell content of properties otherwise
        """
        if not index.isValid():
            return None
        row = index.row()
        column = index.column()
        item = TreeNode.cast(index)
        if item is None:
            return None
        value = item.element.text
        idCat = item.element.idCat
        if (
            role == Qt.CheckStateRole
            and column == 0
            and hasattr(self.parentObj, "askCats")
            and self.parentObj.askCats
        ):
            if self.previousSaved[idCat] == True and self.selectedCats[idCat] == "p":
                return Qt.PartiallyChecked
            elif self.selectedCats[idCat] == False:
                return Qt.Unchecked
            else:
                return Qt.Checked
        if role == Qt.EditRole:
            return value
        if role == Qt.DisplayRole:
            return value
        return None

    def flags(self, index):
        """Return the cell flags for the given index

        Parameter:
            index: the `QModelIndex` for which the data are required

        Output:
            None if the index or the role are not valid,
            the cell flags otherwise
        """
        if not index.isValid():
            return Qt.NoItemFlags
        if index.column() == 0 and (
            hasattr(self.parentObj, "askCats") and self.parentObj.askCats
        ):
            return (
                Qt.ItemIsUserCheckable
                | Qt.ItemIsEditable
                | Qt.ItemIsEnabled
                | Qt.ItemIsSelectable
            )
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        """Return the header data given section, orientation and role

        Parameters:
            section: the section number
            orientation: horizontal or vertical header
            role: the requested role

        Output:
            the column name ("Name", if the parameters correspond)
            or None
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section == 0:
            return "Name"
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
        node = TreeNode.cast(index)
        if node is None:
            return False
        element = node.element
        if element is None:
            return False
        idCat = element.idCat
        if role == Qt.CheckStateRole and index.column() == 0:
            self.previousSaved[idCat] = False
            if value == Qt.Checked:
                self.selectedCats[idCat] = True
            else:
                self.selectedCats[idCat] = False
        self.dataChanged.emit(index, index)
        return True


class CatsTreeWindow(PBDialog):
    """Extension of `PBDialog` that shows the categories tree"""

    def __init__(
        self,
        parent=None,
        askCats=False,
        askForBib=None,
        askForExp=None,
        expButton=True,
        previous=[],
        single=False,
        multipleRecords=False,
    ):
        """Initialize instance parameters and call the function that
        creates the layout.

        Parameters:
            parent (default None): the parent widget
            askCats (default False): if True, enable checkboxes for
                selection of categories
            askForBib (default None): the optional key which identifies
                in the database the bibtex entry for which categories
                are being selected
            askForExp (default None): the optional ID which identifies
                in the database the experiment for which categories
                are being selected
            expButton (default True): if True, add a button to accept
                the widget content and later ask for experiments
            previous (default []): the list of categories that
                must be selected at the beginning
            single (default False): if True, only allow the selection
                of a single category (the parent category, typically).
                Multiple checkboxes can be selected,
                but only the first one will be considered
            multipleRecords: used when dealing with categories
                corresponding to multiple records. Activate a tristate
                checkbox for the initial list of categories, which are
                typically not the same for all the elements in the list
        """
        PBDialog.__init__(self, parent)
        self.setWindowTitle(cwstr.cats)
        self.currLayout = QVBoxLayout(self)
        self.setLayout(self.currLayout)
        self.askCats = askCats
        self.askForBib = askForBib
        self.askForExp = askForExp
        self.expButton = expButton
        self.previous = previous
        self.single = single
        self.multipleRecords = multipleRecords
        self.result = False
        self.marked = []
        self.root_model = None
        self.proxyModel = None
        self.tree = None
        self.menu = None
        self.timer = None
        self.expsButton = None
        self.filterInput = None
        self.newCatButton = None
        self.acceptButton = None
        self.cancelButton = None

        self.setMinimumWidth(400)
        self.setMinimumHeight(600)

        self.createForm()

    def populateAskCat(self):
        """If selection of categories is allowed, add some information
        on the bibtex/experiment for which the categories are requested
        and a simple message, then create few required empty lists
        """
        if self.askCats:
            if self.askForBib is not None:
                try:
                    bibitem = pBDB.bibs.getByBibkey(self.askForBib, saveQuery=False)[0]
                except IndexError:
                    pBGUILogger.warning(
                        cwstr.entryNotInDb % self.askForBib,
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
                        cwstr.markCatBibKAT
                        % (link, bibitem["author"], bibitem["title"])
                    )
                except KeyError:
                    bibtext = PBLabel(cwstr.markCatBibK % (self.askForBib))
                self.currLayout.addWidget(bibtext)
            elif self.askForExp is not None:
                try:
                    expitem = pBDB.exps.getByID(self.askForExp)[0]
                except IndexError:
                    pBGUILogger.warning(
                        cwstr.expNotInDb % self.askForExp,
                        exc_info=True,
                    )
                    return
                try:
                    exptext = PBLabel(
                        cwstr.markCatExpINC
                        % (self.askForExp, expitem["name"], expitem["comments"])
                    )
                except KeyError:
                    exptext = PBLabel(cwstr.markCatExpI % (self.askForExp))
                self.currLayout.addWidget(exptext)
            else:
                if self.single:
                    comment = PBLabel(cwstr.selectCat)
                else:
                    comment = PBLabel(cwstr.selectCats)
                self.currLayout.addWidget(comment)
            self.marked = []
            self.parent().selectedCats = []
        return True

    def onCancel(self):
        """Reject the dialog content and close the window"""
        self.result = False
        self.close()

    def onOk(self, exps=False):
        """Accept the dialog content
        (update the list of selected categories)
        and close the window.
        May set `self.result` to "Exps"
        for later opening of a new dialog to ask for experiments.

        Parameter:
            exps (default False): if True, set the result to "Exps",
                otherwise to "Ok"
        """
        self.parent().selectedCats = [
            idC
            for idC in self.root_model.selectedCats.keys()
            if self.root_model.selectedCats[idC] == True
        ]
        self.parent().previousUnchanged = [
            idC
            for idC in self.root_model.previousSaved.keys()
            if self.root_model.previousSaved[idC] == True
        ]

        if (
            self.single
            and len(self.parent().selectedCats) > 1
            and self.parent().selectedCats[0] == 0
        ):
            self.parent().selectedCats.pop(0)
            self.parent().selectedCats = [self.parent().selectedCats[0]]
        self.result = "Exps" if exps else "Ok"
        self.close()

    def changeFilter(self, string):
        """When the filter `QLineEdit` is changed,
        update the `LeafFilterProxyModel` regexp filter

        Parameter:
            string: the new filter string
        """
        self.proxyModel.setFilterRegExp(str(string))
        self.tree.expandAll()

    def onAskExps(self):
        """Action to perform when the selection of categories
        will be folloed by the selection of experiments.
        Call `self.onOk` with `exps = True`.
        """
        self.onOk(exps=True)

    def onNewCat(self):
        """Action to perform when the creation
        of a new category is requested
        """
        editCategory(self, self.parent())

    def keyPressEvent(self, e):
        """Manage the key press events.
        Do nothing unless `Esc` is pressed:
        in this case close the dialog
        """
        if e.key() == Qt.Key_Escape:
            self.close()

    def createForm(self):
        """Create the dialog content, connect the model to the view
        and eventually add the buttons at the end
        """
        self.populateAskCat()

        catsTree = pBDB.cats.getHier()

        self.filterInput = QLineEdit("", self)
        self.filterInput.setPlaceholderText(cwstr.filterCat)
        self.filterInput.textChanged.connect(self.changeFilter)
        self.currLayout.addWidget(self.filterInput)
        self.filterInput.setFocus()

        self.tree = QTreeView(self)
        self.currLayout.addWidget(self.tree)
        self.tree.setMouseTracking(True)
        self.tree.entered.connect(self.handleItemEntered)
        self.tree.doubleClicked.connect(self.cellDoubleClick)
        self.tree.setExpandsOnDoubleClick(False)

        catsNamedTree = self._populateTree(catsTree[0], 0)

        self.root_model = CatsModel(
            pBDB.cats.getAll(),
            [catsNamedTree],
            self,
            self.previous,
            multipleRecords=self.multipleRecords,
        )
        self.proxyModel = LeafFilterProxyModel(self)
        self.proxyModel.setSourceModel(self.root_model)
        self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxyModel.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.proxyModel.setFilterKeyColumn(-1)
        self.tree.setModel(self.proxyModel)

        self.tree.expandAll()

        self.tree.setHeaderHidden(True)
        # self.tree.doubleClicked.connect(self.askAndPerformAction)

        self.newCatButton = QPushButton(cwstr.addNew, self)
        self.newCatButton.clicked.connect(self.onNewCat)
        self.currLayout.addWidget(self.newCatButton)

        if self.askCats:
            self.acceptButton = QPushButton(cwstr.ok, self)
            self.acceptButton.clicked.connect(self.onOk)
            self.currLayout.addWidget(self.acceptButton)

            if self.expButton:
                self.expsButton = QPushButton(cwstr.askExp, self)
                self.expsButton.clicked.connect(self.onAskExps)
                self.currLayout.addWidget(self.expsButton)

            # cancel button
            self.cancelButton = QPushButton(cwstr.cancel, self)
            self.cancelButton.clicked.connect(self.onCancel)
            self.cancelButton.setAutoDefault(True)
            self.currLayout.addWidget(self.cancelButton)

    def _populateTree(self, children, idCat):
        """Read the list of categories recursively and
        populate the categories tree

        Parameters:
            children: the list of children categories
                of the currently considered one
            idCat: the id of the current category
        """
        name = pBDB.cats.getByID(idCat)[0]["name"]
        children_list = []
        for child in cats_alphabetical(children, pBDB):
            child_item = self._populateTree(children[child], child)
            children_list.append(child_item)
        return NamedElement(idCat, name, children_list)

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
        try:
            idString = self.proxyModel.sibling(row, 0, index).data()
        except AttributeError:
            pBLogger.debug("", exc_info=True)
            return
        try:
            idCat, catName = idString.split(": ")
        except AttributeError:
            pBLogger.debug("", exc_info=True)
            return
        idCat = idCat.strip()
        try:
            self.timer.stop()
            QToolTip.showText(QCursor.pos(), "", self.tree.viewport())
        except AttributeError:
            pass
        try:
            catData = pBDB.cats.getByID(idCat)[0]
        except IndexError:
            pBGUILogger.exception(cwstr.failedFind)
            return
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(
            lambda: QToolTip.showText(
                QCursor.pos(),
                cwstr.catId.format(idC=idCat, cat=catData["name"])
                + cwstr.entriesCorrespondent.format(en=pBDB.catBib.countByCat(idCat))
                + cwstr.expsAssociated.format(ex=pBDB.catExp.countByCat(idCat)),
                self.tree.viewport(),
                self.tree.visualRect(index),
                3000,
            )
        )
        self.timer.start(500)

    def contextMenuEvent(self, event):
        """Create a right click menu with few actions
        on the selected category

        Parameter:
            event: a `QEvent`
        """
        indexes = self.tree.selectedIndexes()
        try:
            index = indexes[0]
        except IndexError:
            pBLogger.debug(cwstr.clickMissingIndex)
            return
        if index.isValid():
            row = index.row()
        else:
            return
        try:
            idString = self.proxyModel.sibling(row, 0, index).data()
        except AttributeError:
            pBLogger.debug("", exc_info=True)
            return
        try:
            idCat, catName = idString.split(": ")
        except AttributeError:
            pBLogger.debug("", exc_info=True)
            return
        idCat = idCat.strip()

        menu = PBMenu()
        self.menu = menu
        titAction = QAction(cwstr.catDescr % catName)
        titAction.setDisabled(True)
        bibAction = QAction(cwstr.openEntryList)
        bntAction = QAction(cwstr.openEntryListNewTab)
        modAction = QAction(cwstr.modify)
        delAction = QAction(cwstr.delete)
        subAction = QAction(cwstr.addSub)
        menu.possibleActions = [
            titAction,
            None,
            bibAction,
            bntAction,
            None,
            modAction,
            delAction,
            None,
            subAction,
        ]
        menu.fillMenu()

        action = menu.exec_(event.globalPos())

        if action == bibAction:
            self.parent().reloadMainContent(pBDB.bibs.getByCat(idCat))
        elif action == bntAction:
            self.parent().reloadMainContent(pBDB.bibs.getByCat(idCat), newTab=catName)
        elif action == modAction:
            editCategory(self, self.parent(), idCat)
        elif action == delAction:
            deleteCategory(self, self.parent(), idCat, catName)
        elif action == subAction:
            editCategory(self, self.parent(), useParentCat=idCat)
        return

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
        try:
            idString = self.proxyModel.sibling(row, 0, index).data()
        except AttributeError:
            pBLogger.debug("", exc_info=True)
            return
        try:
            idCat, catName = idString.split(": ")
        except AttributeError:
            pBLogger.debug("", exc_info=True)
            return
        idCat = idCat.strip()
        self.parent().reloadMainContent(pBDB.bibs.getByCat(idCat))
        return

    def recreateTable(self):
        """Delete the previous widgets and recreate them with new data"""
        self.cleanLayout()
        self.createForm()


class EditCategoryDialog(EditObjectWindow):
    """Create a window for editing or creating a category"""

    def __init__(self, parent=None, category=None, useParentCat=None):
        """Set some properties and create the form content

        Parameters:
            parent: the parent widget
            category: a category record from the database
            useParentCat: the id of the parent category
                of the given one in the tree
        """
        self.acceptButton = None
        self.cancelButton = None
        self.textValues = None
        super(EditCategoryDialog, self).__init__(parent)
        if category is None:
            self.data = {}
            for k in pBDB.tableCols["categories"]:
                self.data[k] = ""
        else:
            self.data = category
        if useParentCat is not None:
            self.data["parentCat"] = useParentCat
            self.selectedCats = [useParentCat]
        elif category is not None:
            try:
                self.selectedCats = [pBDB.cats.getParent(category["idCat"])[0][0]]
            except IndexError:
                self.selectedCats = [0]
        else:
            self.selectedCats = [0]
        self.createForm()

    def onAskParent(self):
        """Open a `CatsTreeWindow` and process its output"""
        selectCats = CatsTreeWindow(
            parent=self,
            askCats=True,
            expButton=False,
            single=True,
            previous=self.selectedCats,
        )
        selectCats.exec_()
        if selectCats.result == "Ok":
            try:
                val = self.selectedCats[0]
                self.textValues["parentCat"].setText(
                    "%s - %s" % (str(val), pBDB.cats.getByID(val)[0]["name"])
                )
            except IndexError:
                self.textValues["parentCat"].setText(cwstr.selectParent)

    def createForm(self):
        """Prepare the window widgets"""
        self.setWindowTitle(cwstr.catEdit)

        i = 0
        for k in pBDB.tableCols["categories"]:
            val = self.data[k]
            if k != "idCat" or (k == "idCat" and self.data[k] != ""):
                i += 1
                self.currGrid.addWidget(
                    PBLabel(pBDB.descriptions["categories"][k]), i * 2 - 1, 0
                )
                self.currGrid.addWidget(PBLabel("(%s)" % k), i * 2 - 1, 1)
                if k == "parentCat":
                    try:
                        val = self.selectedCats[0]
                        self.textValues[k] = QPushButton(
                            "%s - %s" % (str(val), pBDB.cats.getByID(val)[0]["name"]),
                            self,
                        )
                    except IndexError:
                        self.textValues[k] = QPushButton(cwstr.selectParent, self)
                    self.textValues[k].clicked.connect(self.onAskParent)
                else:
                    self.textValues[k] = QLineEdit(str(val))
                if k == "idCat":
                    self.textValues[k].setEnabled(False)
                self.currGrid.addWidget(self.textValues[k], i * 2, 0, 1, 2)

        # OK button
        self.acceptButton = QPushButton(cwstr.ok, self)
        self.acceptButton.clicked.connect(self.onOk)
        self.currGrid.addWidget(self.acceptButton, i * 2 + 1, 1)

        # cancel button
        self.cancelButton = QPushButton(cwstr.cancel, self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        self.currGrid.addWidget(self.cancelButton, i * 2 + 1, 0)

        self.setGeometry(100, 100, 400, 50 * i)
        self.centerWindow()
