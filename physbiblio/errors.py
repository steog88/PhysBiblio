"""Module that contains the pBErrorManager and pBLogger definitions.

This file is part of the physbiblio package.
"""
import sys
import traceback
import logging
import logging.handlers

try:
	from physbiblio.config import pbConfig
except ImportError:
	print("Could not find physbiblio and its modules!")
	print(traceback.format_exc())
	raise


class PBErrorManagerClass():
	"""Class that manages the output of the errors and
	stores the messages into a log file
	"""

	def __init__(self, loggerString = "physbibliolog"):
		"""Constructor for PBErrorManagerClass.

		Parameter:
			loggerString: the `Logger` identifier string to use
				(default = "physbibliolog")
		"""
		self.tempsh = []
		if pbConfig.params["loggingLevel"] == 0:
			self.loglevel = logging.ERROR
		elif pbConfig.params["loggingLevel"] == 1:
			self.loglevel = logging.WARNING
		elif pbConfig.params["loggingLevel"] == 2:
			self.loglevel = logging.INFO
		else:
			self.loglevel = logging.DEBUG
		#the main logger, will save to stdout and log file
		self.loggerString = loggerString
		self.logger = logging.getLogger(loggerString)
		self.logger.propagate = False
		self.logger.setLevel(min(logging.INFO, self.loglevel))

		try:
			fh = logging.handlers.RotatingFileHandler(
				pbConfig.overWritelogFileName,
				maxBytes=5. * 2**20,
				backupCount=5)
		except AttributeError:
			fh = logging.handlers.RotatingFileHandler(
				pbConfig.params["logFileName"],
				maxBytes=5. * 2**20,
				backupCount=5)
		fh.setLevel(self.loglevel)
		formatter = logging.Formatter(
			'%(asctime)s %(levelname)10s : '
			+ '[%(module)s.%(funcName)s] %(message)s')
		fh.setFormatter(formatter)
		self.logger.addHandler(fh)

		self.defaultStream = logging.StreamHandler()
		self.defaultStream.setLevel(min(logging.INFO, self.loglevel))
		formatter = logging.Formatter('[%(module)s.%(funcName)s] %(message)s')
		self.defaultStream.setFormatter(formatter)
		self.logger.addHandler(self.defaultStream)

	def tempHandler(self,
			stream = sys.stdout,
			level = logging.INFO,
			format = '[%(module)s.%(funcName)s] %(message)s'):
		"""Set a temporary StreamHandler for the logger,
		given the stream, with default level logging.INFO.
		Useful when redirecting stdout

		Parameters:
			stream: the stream to be used (default: sys.stdout)
			level: the level to be used (default: logging.INFO)
			format: the format, using the logging syntax
				(default: '[%(module)s.%(funcName)s] %(message)s')
		"""
		try:
			self.tempsh.append(logging.StreamHandler(stream))
			self.tempsh[-1].setLevel(level)
			formatter = logging.Formatter(format)
			self.tempsh[-1].setFormatter(formatter)
			self.logger.addHandler(self.tempsh[-1])
			return True
		except Exception:
			self.logger.exception("Failed while trying to add a new handler")
			return False

	def rmTempHandler(self):
		"""Delete the last temporary handler that has been created"""
		self.logger.removeHandler(self.tempsh[-1])
		del self.tempsh[-1]

	def rmAllTempHandlers(self):
		"""Delete the all the temporary handlers that have been created"""
		for temp in self.tempsh:
			self.logger.removeHandler(temp)
		self.tempsh = []

	def excepthook(self, cls, exception, trcbk):
		"""Function that will replace `sys.excepthook` to log
		any error that occurs

		Parameters:
			cls, exception, trcbk as in `sys.excepthook`
		"""
		self.logger.error("Unhandled exception",
			exc_info = (cls, exception, trcbk))


pBErrorManager = PBErrorManagerClass(pbConfig.loggerString)
pBLogger = pBErrorManager.logger
sys.excepthook = pBErrorManager.excepthook
