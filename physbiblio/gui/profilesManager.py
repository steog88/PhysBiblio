"""Module with the classes and functions
that enter the profiles management.

This file is part of the physbiblio package.
"""
import glob
import os
import shutil
import traceback

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QRadioButton,
)

try:
    from physbiblio.config import pbConfig
    from physbiblio.database import pBDB
    from physbiblio.errors import pBLogger
    from physbiblio.gui.basicDialogs import askYesNo
    from physbiblio.gui.commonClasses import (
        EditObjectWindow,
        PBComboBox,
        PBDialog,
        PBLabel,
    )
    from physbiblio.gui.errorManager import pBGUIErrorManager, pBGUILogger
    from physbiblio.strings.gui import CommonStrings as bastr
    from physbiblio.strings.gui import ProfilesManagerStrings as pmstr
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())


def editProfile(parentObject):
    """Use `EditProfileWindow` and process the form output

    Parameters:
        parentObject: the parent object,
            which has the function `statusBarMessage`
            (a `MainWindow` instance)
    """
    oldOrder = pbConfig.profileOrder
    newProfWin = EditProfileWindow(parentObject)
    newProfWin.exec()
    data = {}
    if newProfWin.result:
        newProfiles = {}
        deleted = []
        for currEl in newProfWin.elements:
            name = currEl["n"].text()
            try:
                fileName = currEl["f"].text()
            except AttributeError:
                fileName = currEl["f"].currentText()
            if currEl["r"].isChecked() and name != "":
                pbConfig.globalDb.setDefaultProfile(name)
            if name in pbConfig.profiles.keys():
                pbConfig.globalDb.updateProfileField(
                    name, "description", currEl["d"].text()
                )
                if currEl["x"].isChecked() and askYesNo(pmstr.askCancel % name):
                    pbConfig.globalDb.deleteProfile(name)
                    deleted.append(name)
            elif fileName in [
                pbConfig.profiles[k]["db"].split(os.sep)[-1]
                for k in pbConfig.profiles.keys()
            ]:
                pbConfig.globalDb.updateProfileField(
                    fileName,
                    "name",
                    name,
                    identifierField="databasefile",
                )
                pbConfig.globalDb.updateProfileField(
                    name, "description", currEl["d"].text()
                )
                if currEl["x"].isChecked() and askYesNo(pmstr.askCancel % name):
                    pbConfig.globalDb.deleteProfile(name)
                    deleted.append(name)
            else:
                if name.strip() != "":
                    newFileName = (fileName.split(os.sep)[-1] + ".db").replace(
                        ".db.db", ".db"
                    )
                    pbConfig.globalDb.createProfile(
                        name=name,
                        description=currEl["d"].text(),
                        databasefile=newFileName,
                    )
                    if currEl["c"].currentText() != "None":
                        shutil.copy2(
                            os.path.join(pbConfig.dataPath, currEl["c"].currentText()),
                            newFileName,
                        )
                    pBGUIErrorManager.loggerPriority(0).info(pmstr.newCreated)
        pbConfig.globalDb.setProfileOrder(
            [
                e["n"].text()
                for e in newProfWin.elements
                if e["n"].text() != "" and e["n"].text() not in deleted
            ]
        )
        pbConfig.loadProfiles()
        message = pmstr.completed
    else:
        pbConfig.profileOrder = oldOrder
        message = pmstr.noModifications
    try:
        parentObject.statusBarMessage(message)
    except AttributeError:
        pBLogger.debug(
            bastr.noAttribute % ("parentObject", "statusBarMessage"),
            exc_info=True,
        )


class SelectProfiles(PBDialog):
    """Widget to change the profile"""

    def __init__(self, parent, message=None):
        """Instantiate the class

        Parameters:
            parent: the parent window (a `MainWindow` instance)
            message: a message used as a description
        """
        if not hasattr(parent, "reloadConfig"):
            raise Exception(pmstr.errorInvalidParent % "SelectProfiles")
        PBDialog.__init__(self, parent)
        self.message = message
        self.result = False
        self.combo = None
        self.loadButton = None
        self.cancelButton = None
        self.initUI()

    def onCancel(self):
        """Set result to False and close the window"""
        self.result = False
        self.close()

    def onLoad(self):
        """Get current selection and (eventually) load new profile"""
        prof, desc = self.combo.currentText().split(pmstr.splitter)
        newProfile = pbConfig.profiles[prof]
        if prof != pbConfig.currentProfileName:
            pBLogger.info(pmstr.changingProfile)
            pbConfig.reInit(prof, newProfile)
            pBDB.reOpenDB(pbConfig.currentDatabase)
            self.parent().reloadConfig()
        self.parent().closeAllTabs()
        try:
            self.parent().catListWin.close()
        except AttributeError:
            pass
        try:
            self.parent().expListWin.close()
        except AttributeError:
            pass
        self.parent().reloadMainContent()
        self.close()

    def initUI(self):
        """Create a `QGridLayout` with the `PBComboBox` and
        the two selection buttons
        """
        self.setWindowTitle(pmstr.selectProfile)

        grid = QGridLayout()
        grid.setSpacing(10)

        i = 0
        if self.message is not None:
            grid.addWidget(PBLabel("%s" % self.message), 0, 0)
            i += 1

        grid.addWidget(PBLabel(pmstr.availableProfiles), i, 0)
        self.combo = PBComboBox(
            self,
            [
                "%s%s%s" % (p, pmstr.splitter, pbConfig.profiles[p]["d"])
                for p in pbConfig.profileOrder
            ],
            current="%s%s%s"
            % (
                pbConfig.currentProfileName,
                pmstr.splitter,
                pbConfig.profiles[pbConfig.currentProfileName]["d"],
            ),
        )
        grid.addWidget(self.combo, i, 1)
        i += 1

        # Load and Cancel button
        self.loadButton = QPushButton(bastr.load, self)
        self.loadButton.clicked.connect(self.onLoad)
        grid.addWidget(self.loadButton, i, 0)
        self.cancelButton = QPushButton(bastr.cancel, self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        grid.addWidget(self.cancelButton, i, 1)

        self.setLayout(grid)


class PBOrderPushButton(QPushButton):
    """Define a button to switch two form lines"""

    def __init__(self, parent, data, qicon, text, testing=False):
        """Extend `QPushButton.__init__`

        Parameters:
            parent: the parent object (an `EditProfileWindow` instance)
            data: the index of the row that will be switched
            qicon: the `QIcon` that will be used to build the `QPushButton`
            text: the `QPushButton` text
            testing (boolean, default False):
                if True, do not connect the clicked signal
        """
        self.qicon = qicon
        QPushButton.__init__(self, self.qicon, text)
        self.data = data
        self.parentObj = parent
        if not testing:
            self.clicked.connect(self.onClick)

    def onClick(self):
        """Perform the switchLines action"""
        self.parentObj.switchLines(self.data)

    def parent(self):
        """Return the parent"""
        return self.parentObj


class EditProfileWindow(EditObjectWindow):
    """create a window for editing or creating a profile"""

    def __init__(self, parent=None):
        """Prepare instance and create form"""
        EditObjectWindow.__init__(self, parent)
        self.def_group = None
        self.elements = []
        self.arrows = []
        self.acceptButton = None
        self.cancelButton = None
        self.createForm()

    def onOk(self):
        """In case "Ok" is pressed, decide if the result is valid:
        * if the name or filename of the new profile are empty, reject;
        * if the name or filename of the new profile are already in use,
            reject;
        * in all the other cases, accept and close the dialog.
        """
        if (
            self.elements[-1]["f"].currentText().strip() != ""
            and self.elements[-1]["n"].text().strip() == ""
        ) or (
            self.elements[-1]["f"].currentText().strip() == ""
            and self.elements[-1]["n"].text().strip() != ""
        ):
            pBGUILogger.info(pmstr.cannotCreateEmpty)
            return
        if self.elements[-1]["n"].text().strip() in [
            a["n"].text() for a in self.elements[:-1]
        ]:
            pBGUILogger.info(pmstr.cannotCreateFieldInUse % "name")
            return
        if (
            self.elements[-1]["f"].currentText().strip().split(os.sep)[-1] + ".db"
        ).replace(".db.db", ".db") in [
            a["f"].text().split(os.sep)[-1] for a in self.elements[:-1]
        ]:
            pBGUILogger.info(pmstr.cannotCreateFieldInUse % "filename")
            return
        self.result = True
        self.close()

    def addButtons(self, profilesData=None, profileOrder=None, defaultProfile=None):
        """Read profiles configuration and add `QLineEdits` and buttons
        for the existing profiles, using previous form content if requested

        Parameters:
            profilesData (optional): a dictionary of dictionaries,
                containing the information of each profile.
                Each element has the profile name as key, and this structure:
                    "n": profile name
                    "d": description
                    "f": name of the database file
                    "r": True if the profile was marked as default in the form
                    "x": True if the profile was selected for deletion
                If `None`, use `pbConfig.profiles`
            profileOrder (optional): the list containing the order
                of the profiles, by their name in the database.
                If `None`, use `pbConfig.profileOrder`
            defaultProfile (optional): the name of the default profile.
                If `None`, use `pbConfig.defaultProfileName`
        """
        if profilesData is None:
            profilesData = pbConfig.profiles
        if profileOrder is None:
            profileOrder = pbConfig.profileOrder
        if defaultProfile is None:
            defaultProfile = pbConfig.defaultProfileName
        self.def_group = QButtonGroup(self.currGrid)
        self.elements = []
        self.arrows = []
        i = 0
        j = 0
        missing = []
        for k in profileOrder:
            try:
                prof = profilesData[k]
            except KeyError:
                pBLogger.warning(pmstr.missingProfile % (k, sorted(list(profilesData))))
                missing.append(k)
                continue
            for f in ["db", "d"]:
                if f not in list(prof):
                    pBLogger.warning(pmstr.missingInfo % (f, sorted(list(prof))))
                    prof[f] = ""
            i += 1
            tempEl = {}
            tempEl["r"] = QRadioButton("")
            self.def_group.addButton(tempEl["r"])
            tempEl["r"].setChecked(False)
            self.currGrid.addWidget(tempEl["r"], i, 0)

            tempEl["n"] = QLineEdit(k)
            tempEl["f"] = QLineEdit(prof["db"].split(os.sep)[-1])
            tempEl["f"].setReadOnly(True)
            tempEl["d"] = QLineEdit(prof["d"])
            self.currGrid.addWidget(tempEl["n"], i, 1)
            self.currGrid.addWidget(tempEl["f"], i, 2)
            self.currGrid.addWidget(tempEl["d"], i, 3)
            if i > 1:
                self.arrows.append(
                    [
                        PBOrderPushButton(
                            self, j, QIcon(":/images/arrow-down.png"), ""
                        ),
                        PBOrderPushButton(self, j, QIcon(":/images/arrow-up.png"), ""),
                    ]
                )
                self.currGrid.addWidget(self.arrows[j][0], i - 1, 5)
                self.currGrid.addWidget(self.arrows[j][1], i, 4)
                j += 1
            tempEl["x"] = QCheckBox("", self)
            if "x" in prof.keys() and prof["x"]:
                tempEl["x"].setChecked(True)
            self.currGrid.addWidget(tempEl["x"], i, 6)
            self.elements.append(tempEl)

        # setChecked the radio of the default profile or
        # of the previously selected one
        profileOrder = [k for k in profileOrder if k not in missing]
        for i, k in enumerate(profileOrder):
            if defaultProfile == k:
                self.elements[i]["r"].setChecked(True)
        for i, k in enumerate(profileOrder):
            if "r" in profilesData[k].keys() and profilesData[k]["r"]:
                self.elements[i]["r"].setChecked(True)

    def createForm(
        self,
        profilesData=None,
        profileOrder=None,
        defaultProfile=None,
        newLine={"r": False, "n": "", "db": "", "d": "", "c": "None"},
    ):
        """Create the form for managing profiles,
        using previous form content if requested.

        Parameters:
            profilesData (optional): a dictionary of dictionaries,
                containing the information of each profile.
                Each element has the profile name as key, and this structure:
                    "n": profile name
                    "d": description
                    "db": name of the database file
                    "r": True if the profile was marked as default in the form
                    "x": True if the profile was selected for deletion
                If `None`, use `pbConfig.profiles`
            profileOrder (optional): the list containing the order
                of the profiles, by their name in the database.
                If `None`, use `pbConfig.profileOrder`
            defaultProfile (optional): the name of the default profile.
                If `None`, use `pbConfig.defaultProfileName`
            newLine (optional): the content of the line corresponding
                to the potentially new profile.
                It is a dictionary with the following fields:
                    "n": profile name
                    "d": description
                    "db": name of the database file
                    "r": True if the profile was marked as default in the form
                    "c": previous content of "Copy from:"
        """
        if profilesData is None:
            profilesData = pbConfig.profiles
        if profileOrder is None:
            profileOrder = pbConfig.profileOrder
        if defaultProfile is None:
            defaultProfile = pbConfig.defaultProfileName

        self.setWindowTitle(pmstr.editProfile)

        labels = [
            PBLabel(bastr.default),
            PBLabel(bastr.shortName),
            PBLabel(bastr.filename),
            PBLabel(bastr.description),
        ]
        for i, e in enumerate(labels):
            self.currGrid.addWidget(e, 0, i)
        self.currGrid.addWidget(PBLabel(bastr.order), 0, 4, 1, 2)
        self.currGrid.addWidget(PBLabel(bastr.deleteQ), 0, 6)

        self.addButtons(profilesData, profileOrder)

        for f in ["c", "db", "d", "n", "r"]:
            if f not in newLine.keys():
                pBLogger.warning(pmstr.missingField % (f, sorted(list(newLine))))
                newLine[f] = ""
        i = len(profilesData) + 3
        self.currGrid.addWidget(PBLabel(""), i - 2, 0)
        tempEl = {}
        self.currGrid.addWidget(PBLabel(pmstr.addNew), i - 1, 0)
        tempEl["r"] = QRadioButton("")
        self.def_group.addButton(tempEl["r"])
        if newLine["r"]:
            tempEl["r"].setChecked(True)
        else:
            tempEl["r"].setChecked(False)
        self.currGrid.addWidget(tempEl["r"], i, 0)

        tempEl["n"] = QLineEdit(newLine["n"])
        self.currGrid.addWidget(tempEl["n"], i, 1)

        tempEl["f"] = QComboBox(self)
        tempEl["f"].setEditable(True)
        dbFiles = [
            f.split(os.sep)[-1]
            for f in list(glob.iglob(os.path.join(pbConfig.dataPath, "*.db")))
        ]
        registeredDb = sorted(
            [a["db"].split(os.sep)[-1] for a in profilesData.values()]
        )
        tempEl["f"].addItems(
            [newLine["db"]] + [f for f in dbFiles if f not in registeredDb]
        )
        self.currGrid.addWidget(tempEl["f"], i, 2)

        tempEl["d"] = QLineEdit(newLine["d"])
        self.currGrid.addWidget(tempEl["d"], i, 3)

        self.currGrid.addWidget(PBLabel(pmstr.copyFrom), i, 4, 1, 2)
        tempEl["c"] = QComboBox(self)
        copyElements = ["None"] + registeredDb
        tempEl["c"].addItems(copyElements)
        tempEl["c"].setCurrentIndex(
            copyElements.index(newLine["c"]) if newLine["c"] in copyElements else 0
        )
        self.currGrid.addWidget(tempEl["c"], i, 6)

        self.elements.append(tempEl)

        i += 1
        self.currGrid.addWidget(PBLabel(""), i, 0)
        # OK button
        self.acceptButton = QPushButton(bastr.ok, self)
        self.acceptButton.clicked.connect(self.onOk)
        self.currGrid.addWidget(self.acceptButton, i + 1, 1)

        # cancel button
        self.cancelButton = QPushButton(bastr.cancel, self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        self.currGrid.addWidget(self.cancelButton, i + 1, 2)

    def switchLines(self, ix):
        """Save the current form content,
        switch the order of the rows as required,
        create a new form with the new order.

        Parameter:
            ix: the index of the first of the two rows involved in the switch
                (e.g., to switch the first and second rows, use ix = 0)
        """
        currentValues = {}
        currentOrder = []
        for el in self.elements[: len(pbConfig.profiles)]:
            tmp = {}
            tmp["db"] = el["f"].text()
            tmp["d"] = el["d"].text()
            tmp["r"] = el["r"].isChecked()
            tmp["x"] = el["x"].isChecked()
            currentValues[el["n"].text()] = tmp
            currentOrder.append(el["n"].text())
        newLine = {
            "r": self.elements[-1]["r"].isChecked(),
            "n": self.elements[-1]["n"].text(),
            "db": self.elements[-1]["f"].currentText(),
            "d": self.elements[-1]["d"].text(),
        }
        tempOrder = list(currentOrder)
        try:
            tempOrder[ix] = currentOrder[ix + 1]
            tempOrder[ix + 1] = currentOrder[ix]
        except IndexError:
            pBLogger.warning(pmstr.errorSwitchLines)
            return False
        self.cleanLayout()
        self.createForm(currentValues, tempOrder, newLine)
        return True
