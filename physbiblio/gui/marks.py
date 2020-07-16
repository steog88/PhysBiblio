"""Module with the class that manages marks for the bibtex entries.

This file is part of the physbiblio package.
"""
import traceback

from PySide2.QtWidgets import QCheckBox, QGroupBox, QHBoxLayout, QRadioButton

try:
    import physbiblio.gui.resourcesPyside2
    from physbiblio.strings.gui import MarksStrings as mstr
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())


class Marks:
    """Class that manages the marks of bibtex entries"""

    def __init__(self):
        """Class constructor. Creates the 5 default marks."""
        self.marks = {}
        self.newMark("imp", mstr.important, "emblem-important-symbolic")
        self.newMark("fav", mstr.favorite, "emblem-favorite-symbolic")
        self.newMark("bad", mstr.bad, "emblem-remove")
        self.newMark("que", mstr.unclear, "emblem-question")
        self.newMark("new", mstr.toBeRead, "unread-new")

    def newMark(self, key, desc, icon):
        """Add a new mark.

        Parameters:
            key: the key to be used in the self.marks dictionary
            desc: the mark description
            icon: the name of the icon file (omitting the .png extension),
                which must be present in ":/images/"
        """
        self.marks[key] = {"desc": desc, "icon": ":/images/%s.png" % icon}

    def getGroupbox(self, marksData, description=mstr.marks, radio=False, addAny=False):
        """Create a `QGroupBox` containing `QCheckBox`s or `QRadioButton`s
        for marks selection

        Parameters:
            marksData: a list containing the keys of the elements
                that must be checked at the beginning
            description: the description/title of the `QGroupBox`
            radio (boolean, optional, default False):
                if True, use `QRadioButton` instead of `QCheckBox`
            addAny (boolean, optional, default False):
                add the "any" button to the `QGroupBox`

        Output:
            a list: (groupBox, markValues)
            groupBox: the `QGroupBox` object
            markValues: the list of `QCheckBox`s or `QRadioButton`s,
                for further values extraction
        """
        groupBox = QGroupBox(description)
        markValues = {}
        groupBox.setFlat(True)
        boxlayout = QHBoxLayout()
        for m, cont in self.marks.items():
            if radio:
                markValues[m] = QRadioButton(cont["desc"])
            else:
                markValues[m] = QCheckBox(cont["desc"])
            if marksData is not None and m in marksData:
                markValues[m].setChecked(True)
            boxlayout.addWidget(markValues[m])
        if addAny:
            markValues["any"] = QRadioButton(mstr.anys)
            boxlayout.addWidget(markValues["any"])
        groupBox.setLayout(boxlayout)
        return groupBox, markValues


pBMarks = Marks()
