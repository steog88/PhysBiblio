#!/usr/bin/env python
import sys
from PySide.QtCore import *
from PySide.QtGui  import *
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

try:
	from physbiblio.database import *
	from physbiblio.config import pbConfig
	from physbiblio.inspireStats import pBStats
	from physbiblio.gui.DialogWindows import *
	from physbiblio.gui.CommonClasses import *
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
try:
	if sys.version_info[0] < 3:
		import physbiblio.gui.Resources_pyside
	else:
		import physbiblio.gui.Resources_pyside3
except ImportError:
	print("Missing Resources_pyside: Run script update_resources.sh")

figTitles = [
"Paper number",
"Papers per year",
"Total citations",
"Citations per year",
"Mean citations",
"Citations for each paper"
]

class authorStatsPlots(QDialog):
	def __init__(self, figs, title = None, parent = None):
		super(authorStatsPlots, self).__init__(parent)
		if title is not None:
			self.setWindowTitle(title)
		self.parent = parent
		layout = QGridLayout(self)
		layout.setSpacing(1)
		self.setLayout(layout)
		self.updatePlots(figs)

		nlines = int(len(figs)/2)
		self.layout().addWidget(QLabel("Click on the lines to have more information:"), nlines + 1, 0)

		self.hIndex = QLabel("Author h index: %d"%self.parent.lastAuthorStats["h"])
		largerFont = QFont("Times", 15, QFont.Bold)
		self.hIndex.setFont(largerFont)
		self.layout().addWidget(self.hIndex, nlines + 1, 1)

		self.textBox = QLineEdit("")
		self.textBox.setReadOnly(True)
		self.layout().addWidget(self.textBox, nlines + 2, 0, 1, 2)
		self.saveButton = QPushButton('Save', self)
		self.saveButton.clicked.connect(self.saveAction)
		self.layout().addWidget(self.saveButton, nlines + 3, 0)

		self.clButton = QPushButton('Close', self)
		self.clButton.clicked.connect(self.close)
		self.clButton.setAutoDefault(True)
		self.layout().addWidget(self.clButton, nlines + 3, 1)

	def saveAction(self):
		savePath = askDirName(self, "Where do you want to save the plots of the stats?")
		if savePath != "":
			self.parent.lastAuthorStats["figs"] = pBStats.plotStats(author = True, save = True, path = savePath)
			infoMessage("Plots saved.")
			self.saveButton.setDisabled(True)

	def pickEvent(self,event):
		ob = event.artist
		ix = -1
		for i, f in enumerate(self.figs):
			if f == ob.figure: ix = i
		if isinstance(ob, Rectangle):
			self.textBox.setText("%s in year %d is: %d"%(figTitles[ix], int(ob._x), int(ob._height)))
		elif isinstance(ob, Line2D):
			xdata = ob.get_xdata()
			ydata = ob.get_ydata()
			ind = event.ind
			if ix == 4:
				formatString = "%s in date %s is %f"
			else:
				formatString = "%s in date %s is %d"
			self.textBox.setText(formatString%(figTitles[ix], np.take(xdata, ind)[0].strftime("%d/%m/%Y"), np.take(ydata, ind)[0]))

	def updatePlots(self, figs):
		i = 0
		while True:
			item = self.layout().takeAt(i)
			if item is None: break
			del item
		if hasattr(self, "canvas"): del self.canvas
		self.figs = figs
		self.canvas = []
		for i,fig in enumerate(figs):
			if fig is not None:
				self.canvas.append(FigureCanvas(fig))
				self.layout().addWidget(self.canvas[-1], int(i/2), i%2)
				self.canvas[-1].mpl_connect("pick_event", self.pickEvent)
				self.canvas[-1].draw()

class paperStatsPlots(QDialog):
	def __init__(self, fig, title = None, parent = None):
		super(paperStatsPlots, self).__init__(parent)
		if title is not None:
			self.setWindowTitle(title)
		self.parent = parent
		layout = QGridLayout(self)
		layout.setSpacing(1)
		self.setLayout(layout)
		self.updatePlots(fig)

		nlines = 1
		self.layout().addWidget(QLabel("Click on the line to have more information:"), nlines + 1, 0)

		self.textBox = QLineEdit("")
		self.textBox.setReadOnly(True)
		self.layout().addWidget(self.textBox, nlines + 2, 0, 1, 2)
		self.saveButton = QPushButton('Save', self)
		self.saveButton.clicked.connect(self.saveAction)
		self.layout().addWidget(self.saveButton, nlines + 3, 0)

		self.clButton = QPushButton('Close', self)
		self.clButton.clicked.connect(self.close)
		self.clButton.setAutoDefault(True)
		self.layout().addWidget(self.clButton, nlines + 3, 1)

	def saveAction(self):
		savePath = askDirName(self, "Where do you want to save the plot of the stats?")
		if savePath != "":
			self.parent.lastPaperStats["fig"] = pBStats.plotStats(paper = True, save = True, path = savePath)
			infoMessage("Plot saved.")
			self.saveButton.setDisabled(True)

	def pickEvent(self,event):
		ob = event.artist
		ix = -1
		if isinstance(ob, Line2D):
			xdata = ob.get_xdata()
			ydata = ob.get_ydata()
			ind = event.ind
			formatString = "%s in date %s is %d"
			self.textBox.setText(formatString%("Citations", np.take(xdata, ind)[0].strftime("%d/%m/%Y"), np.take(ydata, ind)[0]))

	def updatePlots(self, fig):
		i = 0
		while True:
			item = self.layout().takeAt(i)
			if item is None: break
			del item
		if hasattr(self, "canvas"): del self.canvas
		self.fig = fig
		if fig is not None:
			self.canvas = FigureCanvas(fig)
			self.layout().addWidget(self.canvas, 0, 0, 1, 2)
			self.canvas.mpl_connect("pick_event", self.pickEvent)
			self.canvas.draw()
