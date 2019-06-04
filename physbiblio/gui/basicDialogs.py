"""Module with the classes and functions that manage many generic
simple dialog windows of the PhysBiblio application.

This file is part of the physbiblio package.
"""
import sys
from PySide2.QtWidgets import (
    QDesktopWidget,
    QDialog,
    QFileDialog,
    QGridLayout,
    QInputDialog,
    QMessageBox,
    QTextEdit,
    QPushButton,
)

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO


def askYesNo(message, title="Question"):
    """Uses `QMessageBox` to ask "Yes" or "No" for a given question.

    Parameters:
        message: the question to be displayed
        title: the window title

    Output:
        return True if the "Yes" button has been clicked,
            False otherwise
    """
    mbox = QMessageBox(QMessageBox.Question, title, message)
    yesButton = mbox.addButton(QMessageBox.Yes)
    noButton = mbox.addButton(QMessageBox.No)
    mbox.setDefaultButton(noButton)
    mbox.exec_()
    if mbox.clickedButton() == yesButton:
        return True
    else:
        return False


def infoMessage(message, title="Information"):
    """Uses `QMessageBox` to show a simple message.

    Parameters:
        message: the question to be displayed
        title: the window title
    """
    mbox = QMessageBox(QMessageBox.Information, title, message)
    mbox.exec_()


class LongInfoMessage(QDialog):
    """`infoMessage` version when a long text is expected"""

    def __init__(self, message, title="Information"):
        """Class constructor.

        Parameters:
            message: the question to be displayed
            title: the window title
        """
        QDialog.__init__(self)
        self.setWindowTitle(title)
        self.gridlayout = QGridLayout()
        self.textarea = QTextEdit(message)
        self.textarea.setReadOnly(True)
        self.gridlayout.addWidget(self.textarea, 0, 0, 1, 2)
        self.okbutton = QPushButton("OK", self)
        self.okbutton.clicked.connect(lambda: QDialog.close(self))
        self.gridlayout.addWidget(self.okbutton, 1, 1)
        self.setLayout(self.gridlayout)
        self.setGeometry(100, 100, 600, 400)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.exec_()


def askGenericText(message, title, parent=None):
    """Uses `QInputDialog` to ask a text answer for a given question.

    Parameters:
        message: the question to be displayed
        title: the window title
        parent (optional, default None): the parent of the window

    Output:
        return a tuple containing the text as first element
        and True/False
            (depending if the user selected "Ok" or "Cancel")
            as the second element
    """
    dialog = QInputDialog(parent)
    dialog.setInputMode(QInputDialog.TextInput)
    dialog.setWindowTitle(title)
    dialog.setLabelText(message)
    out = dialog.exec_()
    return dialog.textValue(), out


def askFileName(parent=None, title="Filename to use:", filter="", dir=""):
    """Uses `QFileDialog` to ask the name of a single, existing file

    Parameters (all optional):
        parent (default None): the parent of the window
        title: the window title
        filter: the filter to be used when displaying files
        dir: the initial directory

    Output:
        return the filename
        or an empty string if the user selected "Cancel"
    """
    dialog = QFileDialog(parent, title, dir, filter)
    dialog.setFileMode(QFileDialog.ExistingFile)
    if dialog.exec_():
        fileNames = dialog.selectedFiles()
        try:
            return fileNames[0]
        except IndexError:
            return ""
    else:
        return ""


def askFileNames(parent=None, title="Filename to use:", filter="", dir=""):
    """Uses `QFileDialog` to ask the names of a set of existing files

    Parameters (all optional):
        parent (default None): the parent of the window
        title: the window title
        filter: the filter to be used when displaying files
        dir: the initial directory

    Output:
        return the filenames list
        or an empty list depending if the user selected "Ok" or "Cancel"
    """
    dialog = QFileDialog(parent, title, dir, filter)
    dialog.setFileMode(QFileDialog.ExistingFiles)
    dialog.setOption(QFileDialog.DontConfirmOverwrite, True)
    if dialog.exec_():
        fileNames = dialog.selectedFiles()
        return fileNames
    else:
        return []


def askSaveFileName(parent=None, title="Filename to use:", filter="", dir=""):
    """Uses `QFileDialog` to ask the names of a single file
    where something will be saved (the file may not exist)

    Parameters (all optional):
        parent (default None): the parent of the window
        title: the window title
        filter: the filter to be used when displaying files
        dir: the initial directory

    Output:
        return the filename
        or an empty string depending if the user selected "Ok" or "Cancel"
    """
    dialog = QFileDialog(parent, title, dir, filter)
    dialog.setFileMode(QFileDialog.AnyFile)
    dialog.setOption(QFileDialog.DontConfirmOverwrite, True)
    if dialog.exec_():
        fileNames = dialog.selectedFiles()
        try:
            return fileNames[0]
        except IndexError:
            return ""
    else:
        return ""


def askDirName(parent=None, title="Directory to use:", dir=""):
    """Uses `QFileDialog` to ask the names of a single directory

    Parameters (all optional):
        parent (default None): the parent of the window
        title: the window title
        dir: the initial directory

    Output:
        return the directory name
        or an empty string depending if the user selected "Ok" or "Cancel"
    """
    dialog = QFileDialog(parent, title, dir)
    dialog.setFileMode(QFileDialog.Directory)
    dialog.setOption(QFileDialog.ShowDirsOnly, True)
    if dialog.exec_():
        fileNames = dialog.selectedFiles()
        try:
            return fileNames[0]
        except IndexError:
            return ""
    else:
        return ""
