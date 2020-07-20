"""Module with the classes that manage the authorStats
and paperStats plots.

This file is part of the physbiblio package.
"""
import traceback

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QDialog, QGridLayout, QLineEdit, QPushButton

plt.switch_backend("Qt5Agg")

try:
    from physbiblio.config import pbConfig
    from physbiblio.database import pBDB
    from physbiblio.gui.basicDialogs import askDirName, infoMessage
    from physbiblio.gui.commonClasses import PBDialog, PBLabel
    from physbiblio.gui.errorManager import pBGUILogger
    from physbiblio.inspireStats import pBStats
    from physbiblio.strings.gui import InspireStatsGUIStrings as igstr
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())

figTitles = [
    igstr.paperNumber,
    igstr.paperYear,
    igstr.totalCitations,
    igstr.citationsYear,
    igstr.meanCitations,
    igstr.citationsPaper,
]


class AuthorStatsPlots(PBDialog):
    """Class that constructs a window to show
    the results of `authorStats`
    """

    def __init__(self, figs, title=None, parent=None):
        """Constructor.

        Parameters:
            figs: the list of figures
            title (optional): the window title
            parent (default None): the parent object,
                which should have a property `lastAuthorStats`
        """
        super(AuthorStatsPlots, self).__init__(parent)
        self.figs = figs
        self.canvas = None
        if title is not None:
            self.setWindowTitle(title)
        layout = QGridLayout(self)
        layout.setSpacing(1)
        self.setLayout(layout)
        self.updatePlots()

        nlines = int(len(figs) / 2)
        self.layout().addWidget(PBLabel(igstr.linesMoreInfo), nlines + 1, 0)

        try:
            hIndex = "%d" % self.parent().lastAuthorStats["h"]
        except (TypeError, AttributeError):
            hIndex = igstr.hIndexE
        self.hIndex = PBLabel(igstr.hIndexV % hIndex)
        largerFont = QFont("Times", 15, QFont.Bold)
        self.hIndex.setFont(largerFont)
        self.layout().addWidget(self.hIndex, nlines + 1, 1)

        self.textBox = QLineEdit("")
        self.textBox.setReadOnly(True)
        self.layout().addWidget(self.textBox, nlines + 2, 0, 1, 2)
        self.saveButton = QPushButton(igstr.save, self)
        self.saveButton.clicked.connect(self.saveAction)
        self.layout().addWidget(self.saveButton, nlines + 3, 0)

        self.clButton = QPushButton(igstr.close, self)
        self.clButton.clicked.connect(self.onClose)
        self.clButton.setAutoDefault(True)
        self.layout().addWidget(self.clButton, nlines + 3, 1)

    def onClose(self):
        """Close dialog"""
        QDialog.close(self)

    def saveAction(self):
        """Save the plot into a file,
        after asking the directory where to save them
        """
        savePath = askDirName(self, igstr.whereSavePlots)
        if savePath != "":
            try:
                self.parent().lastAuthorStats["figs"] = pBStats.plotStats(
                    author=True, save=True, path=savePath
                )
            except AttributeError:
                pBGUILogger.warning("", exc_info=True)
            else:
                infoMessage(igstr.plotsSaved)
                self.saveButton.setDisabled(True)

    def onPress(self, event):
        """Print the plot coordinates where a click was performed.
        To be connected through `mpl_connect`.
        Used for testing.

        Parameter:
            a `matplotlib.backend_bases.Event`
        """
        print(event.xdata, event.ydata)

    def pickEvent(self, event):
        """Save into `self.textBox` the coordinates
        of the clicked object (`Line2D` or `Rectangle`) in the plot.

        Parameter:
            a `matplotlib.backend_bases.Event`
        """
        ob = event.artist
        ix = -1
        for i, f in enumerate(self.figs):
            if f == ob.figure:
                ix = i
        if isinstance(ob, Rectangle):
            self.textBox.setText(
                igstr.xInYearIs % (figTitles[ix], int(ob.get_x()), int(ob.get_height()))
            )
        elif isinstance(ob, Line2D):
            xdata = ob.get_xdata()
            ydata = ob.get_ydata()
            ind = event.ind
            if ix == 4:
                formatString = igstr.xInDateIsF
            else:
                formatString = igstr.xInDateIsD
            self.textBox.setText(
                formatString
                % (
                    figTitles[ix],
                    np.take(xdata, ind)[0].strftime(igstr.datefmt),
                    np.take(ydata, ind)[0],
                )
            )

    def updatePlots(self):
        """Reset the dialog window removing all the previous items
        and create new canvas for the figures.
        """
        i = 0
        while True:
            item = self.layout().takeAt(i)
            if item is None:
                break
            del item
        if hasattr(self, "canvas"):
            del self.canvas
        self.canvas = []
        for fig in self.figs:
            if fig is not None:
                self.canvas.append(FigureCanvas(fig))
                self.layout().addWidget(self.canvas[-1], int(i / 2), i % 2)
                self.canvas[-1].mpl_connect("pick_event", self.pickEvent)
                self.canvas[-1].draw()
                i += 1


class PaperStatsPlots(PBDialog):
    """Class that constructs a window
    to show the results of `paperStats`
    """

    def __init__(self, fig, title=None, parent=None):
        """Constructor.
        Defines some properties and buttons

        Parameters:
            fig: the figure to be shown
            title (optional): the window title
            parent (default None): the parent object,
                which should have a property lastPaperStats
        """
        super(PaperStatsPlots, self).__init__(parent)
        self.fig = fig
        self.canvas = None
        if title is not None:
            self.setWindowTitle(title)
        layout = QGridLayout(self)
        layout.setSpacing(1)
        self.setLayout(layout)
        self.updatePlots()

        nlines = 1
        self.layout().addWidget(PBLabel(igstr.lineMoreInfo), nlines + 1, 0)

        self.textBox = QLineEdit("")
        self.textBox.setReadOnly(True)
        self.layout().addWidget(self.textBox, nlines + 2, 0, 1, 2)
        self.saveButton = QPushButton(igstr.save, self)
        self.saveButton.clicked.connect(self.saveAction)
        self.layout().addWidget(self.saveButton, nlines + 3, 0)

        self.clButton = QPushButton(igstr.close, self)
        self.clButton.clicked.connect(self.onClose)
        self.clButton.setAutoDefault(True)
        self.layout().addWidget(self.clButton, nlines + 3, 1)

    def onClose(self):
        """Close dialog"""
        QDialog.close(self)

    def saveAction(self):
        """Save the plot into a file,
        after asking the directory where to save them
        """
        savePath = askDirName(self, igstr.whereSavePlot)
        if savePath != "":
            try:
                self.parent().lastPaperStats["fig"] = pBStats.plotStats(
                    paper=True, save=True, path=savePath
                )
            except AttributeError:
                pBGUILogger.warning("", exc_info=True)
            else:
                infoMessage(igstr.plotSaved)
                self.saveButton.setDisabled(True)

    def pickEvent(self, event):
        """Save into `self.textBox` the coordinates
        of the clicked object (`Line2D`) in the plot.

        Parameter:
            a `matplotlib.backend_bases.Event`
        """
        ob = event.artist
        ix = -1
        if isinstance(ob, Line2D):
            xdata = ob.get_xdata()
            ydata = ob.get_ydata()
            ind = event.ind
            formatString = igstr.xInDateIsD
            self.textBox.setText(
                formatString
                % (
                    igstr.citations,
                    np.take(xdata, ind)[0].strftime(igstr.datefmt),
                    np.take(ydata, ind)[0],
                )
            )

    def updatePlots(self):
        """Reset the dialog window removing all the previous items
        and create a new canvas for the figure.
        """
        i = 0
        while True:
            item = self.layout().takeAt(i)
            if item is None:
                break
            del item
        if hasattr(self, "canvas"):
            del self.canvas
        if self.fig is not None:
            self.canvas = FigureCanvas(self.fig)
            self.layout().addWidget(self.canvas, 0, 0, 1, 2)
            self.canvas.mpl_connect("pick_event", self.pickEvent)
            self.canvas.draw()
