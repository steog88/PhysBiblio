import sys
import logging
import traceback
from PySide.QtCore import *
from PySide.QtGui  import *

if sys.version_info[0] < 3:
	from StringIO import StringIO
else:
	from io import StringIO

try:
	from physbiblio.errors import pBErrorManagerClass, pBLogger
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")

class ErrorStream(StringIO):
	def __init__(self, *args, **kwargs):
		StringIO.__init__(self, *args, **kwargs)
		self.priority = 1

	def setPriority(self, prio):
		self.priority = prio

	def write(self, text):
		if text.strip() == "":
			return
		text = text.replace('\n', '<br>')
		if self.priority == 0:
			QMessageBox.information(None, "Information", text)
		elif self.priority > 1:
			QMessageBox.critical(None, "Error", text)
		else:
			QMessageBox.warning(None, "Warning", text)
		self.priority = 1

class pBErrorManagerClassGui(pBErrorManagerClass):
	"""
	Extends the error manager class to show gui messages
	"""
	def __init__(self):
		"""
		Init the class, storing the name of the external web application
		and the base strings to build some links
		"""
		pBErrorManagerClass.__init__(self, "physbiblioguilog")
		self.guiStream = ErrorStream()
		self.tempHandler(self.guiStream, level = logging.DEBUG, format = '%(message)s')

	def loggerPriority(self, prio):
		self.guiStream.priority = prio
		return self.logger

pBGUIErrorManager = pBErrorManagerClassGui()
pBGUILogger = pBGUIErrorManager.logger
