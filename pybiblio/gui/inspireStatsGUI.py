#!/usr/bin/env python
import sys
from PySide.QtCore import *
from PySide.QtGui  import *
import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

try:
	from pybiblio.database import *
	from pybiblio.config import pbConfig
	from pybiblio.gui.DialogWindows import *
	from pybiblio.gui.CommonClasses import *
except ImportError:
	print("Could not find pybiblio and its contents: configure your PYTHONPATH!")
try:
	import pybiblio.gui.Resources_pyside
except ImportError:
	print("Missing Resources_pyside.py: Run script update_resources.sh")

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

	def updatePlots(self, figs):		
		i = 0
		while True:
			item = self.layout().takeAt(i)
			if item is None: break
			del item
		if hasattr(self, "canvas"): del self.canvas
		self.canvas = []
		for i,fig in enumerate(figs):
			if fig is not None:
				self.canvas.append(FigureCanvas(fig))
				self.layout().addWidget(self.canvas[-1], int(i/2), i%2)
				self.layout()
				self.canvas[-1].draw()
