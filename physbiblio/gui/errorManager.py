"""Module with the class that manages errors when the GUI is active.

This file is part of the physbiblio package.
"""
import sys
import logging
import traceback
from PySide2.QtWidgets import QMessageBox

if sys.version_info[0] < 3:
	from StringIO import StringIO
else:
	from io import StringIO

try:
	from physbiblio.errors import PBErrorManagerClass, pBLogger
except ImportError:
	print("Could not find physbiblio and its modules!")
	print(traceback.format_exc())


class ErrorStream(StringIO):
	"""Define a stream based on StringIO, which opens a `QMessageBox`
	when `write` is called
	"""

	def __init__(self, *args, **kwargs):
		"""The constructor, which passes the `*args, **kwargs` method
		to `StringIO.__init__`.
		"""
		StringIO.__init__(self, *args, **kwargs)
		self.priority = 1
		self.lastMBox = None

	def setPriority(self, prio):
		"""Set the priority level to be adopted
		when opening the `QMessageBox`.

		Parameter:
			prio: the priority level. 0, 1, 2+ correspond
				to `Information`, `Warning`, `Error`
		"""
		self.priority = prio

	def write(self, text, testing = False):
		"""Override the `write` method of `StringIO`
		to show a `QMessageBox`,
		with icon according to the current priority.
		The priority is set to 1 after execution.

		Parameters:
			text: the text to display. "\n" is replaced with "<br>".
			testing (boolean, optional, default False): when doing tests,
				interrupt the execution before `exec_` is run and
				return the `QMessageBox` object.

		Output:
			if text is empty or testing is False, return None
			if testing is True, return the `QMessageBox` object
		"""
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
		return


class PBErrorManagerClassGui(PBErrorManagerClass):
	"""Extends the error manager class to show
	gui messages through ErrorStream
	"""

	def __init__(self):
		"""Init the class, using PBErrorManagerClass.__init__ and
		the gui logger name,
		then add a new handler which uses ErrorStream
		"""
		PBErrorManagerClass.__init__(self, "physbiblioguilog")
		self.guiStream = ErrorStream()
		self.tempHandler(self.guiStream,
			level = logging.DEBUG,
			format = '%(message)s')

	def loggerPriority(self, prio):
		"""Define the priority level that must be used by
		the `ErrorStream` class in the first call of its `write` method.

		Parameter:
			prio: the priority level. 0, 1, 2+ correspond
				to Information, Warning, Error

		Output:
			the logger [so it can be used as
				`pBGUIErrorManager.loggerPriority(prio).info(message)`]
		"""
		self.guiStream.priority = prio
		return self.logger


pBGUIErrorManager = PBErrorManagerClassGui()
pBGUILogger = pBGUIErrorManager.logger
