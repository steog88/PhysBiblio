#!/usr/bin/env python

import sys
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
	def __init__(self, queue, app):
		super(thread_updateAllBibtexs, self).__init__()
		self.queue = queue
		self.app = app

	def run(self):
		sys.stdout = WriteStream(self.queue)
		thread = QThread()
		my_receiver = MyReceiver(self.queue)
		my_receiver.mysignal.connect(self.app.append_text)
		my_receiver.moveToThread(thread)
		thread.started.connect(my_receiver.run)
		thread.start()
		pBDB.bibs.searchOAIUpdates()
		sys.stdout = sys.__stdout__
		
class thread_downloadArxiv(MyThread):
	def __init__(self, bibkey):
		super(thread_downloadArxiv, self).__init__()
		self.bibkey = bibkey

	def run(self):
		pBPDF.downloadArxiv(self.bibkey)
