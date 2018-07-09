import sys
import logging
import traceback
from PySide2.QtWidgets import QMessageBox

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
		self.lastMBox = None

	def setPriority(self, prio):
		self.priority = prio

	def write(self, text, testing = False):
		if text.strip() == "":
			return
		text = text.replace('\n', '<br>')
		self.lastMBox = QMessageBox(QMessageBox.Information, "Information", "")
		self.lastMBox.setText(text)
		if self.priority == 0:
			self.lastMBox.setIcon(QMessageBox.Information)
			self.lastMBox.setWindowTitle("Information")
		elif self.priority > 1:
			self.lastMBox.setIcon(QMessageBox.Critical)
			self.lastMBox.setWindowTitle("Error")
		else:
			self.lastMBox.setIcon(QMessageBox.Warning)
			self.lastMBox.setWindowTitle("Warning")
		self.priority = 1
		if testing:
			return self.lastMBox
		self.lastMBox.exec_()

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
