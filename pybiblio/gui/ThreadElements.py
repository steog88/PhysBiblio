#!/usr/bin/env python

import sys, time
from PySide.QtCore import *
from PySide.QtGui  import *

try:
	from pybiblio.database import *
	from pybiblio.pdf import pBPDF
	#import pybiblio.export as bibexport
	#import pybiblio.webimport.webInterf as webInt
	#from pybiblio.cli import cli as pyBiblioCLI
	#from pybiblio.config import pbConfig
	#from pybiblio.gui.DialogWindows import *
	#from pybiblio.gui.BibWindows import *
	#from pybiblio.gui.CatWindows import *
	from pybiblio.gui.CommonClasses import *
except ImportError:
	print("Could not find pybiblio and its contents: configure your PYTHONPATH!")

class thread_updateAllBibtexs(MyThread):
	def __init__(self, queue, app, thr, parent = None):
		super(thread_updateAllBibtexs, self).__init__(parent)
		self.parent = parent
		self.queue = queue
		self.thr = thr
		self.app = app

	def run(self):
		my_receiver = MyReceiver(self.queue)
		my_receiver.mysignal.connect(self.app.append_text)
		my_receiver.moveToThread(self.thr)
		self.thr.started.connect(my_receiver.run)
		self.connect(my_receiver, SIGNAL("finished()"), my_receiver.deleteLater)
		self.connect(my_receiver, SIGNAL("finished()"), self.thr.terminate)
		self.connect(self.thr, SIGNAL("finished()"), self.thr.deleteLater)
		self.thr.start()
		pBDB.bibs.searchOAIUpdates()
		time.sleep(1)
		my_receiver.running = False
		self.finished.emit()

	def setStopFlag(self):
		pBDB.bibs.runningOAIUpdates = False

class thread_downloadArxiv(MyThread):
	def __init__(self, bibkey):
		super(thread_downloadArxiv, self).__init__()
		self.bibkey = bibkey

	def run(self):
		pBPDF.downloadArxiv(self.bibkey)
