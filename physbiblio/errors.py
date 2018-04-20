"""
Module that only contains the pBErrorManager definition.

This file is part of the PhysBiblio package.
"""
import sys, traceback, os
import logging

try:
	from physbiblio.config import pbConfig
except ImportError:
	print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
	print(traceback.format_exc())
	raise

class pBErrorManagerClass():
	"""Class that manages the output of the errors and stores the messages into a log file"""
	def __init__(self):
		"""
		Constructor for PBErrorManager.
		"""
		self.tempsh = None
		if pbConfig.params["loggingLevel"] == 0:
			self.loglevel = logging.ERROR
		elif pbConfig.params["loggingLevel"] == 1:
			self.loglevel = logging.WARNING
		elif pbConfig.params["loggingLevel"] == 2:
			self.loglevel = logging.INFO
		else:
			self.loglevel = logging.DEBUG
		#the main logger, will save to stdout and log file
		self.logger = logging.getLogger("physbibliolog")
		self.logger.propagate = False
		self.logger.setLevel(min(logging.INFO, self.loglevel))

		fh = logging.FileHandler(pbConfig.params["logFileName"])
		fh.setLevel(self.loglevel)
		formatter = logging.Formatter('%(asctime)s %(levelname)10s : [%(module)s.%(funcName)s] %(message)s')
		fh.setFormatter(formatter)
		self.logger.addHandler(fh)

		sh = logging.StreamHandler()
		sh.setLevel(logging.INFO)
		formatter = logging.Formatter('[%(module)s.%(funcName)s] %(message)s')
		sh.setFormatter(formatter)
		self.logger.addHandler(sh)

	def tempHandler(self, stream = sys.stdout, level = logging.INFO, format = '[%(module)s.%(funcName)s] %(message)s'):
		"""
		Set a temporary StreamHandler for the logger, given the stream, with default level logging.INFO.
		Useful when redirecting stdout

		Parameters:
			stream: the stream to be used (default: sys.stdout)
			level: the level to be used (default: logging.INFO)
			format: the format, using the logging syntax (default: '[%(module)s.%(funcName)s] %(message)s')
		"""
		if self.tempsh is not None:
			self.logger.warning("There is already a temporary handler. More than one is currently not supported")
			return
		self.tempsh = logging.StreamHandler(stream)
		self.tempsh.setLevel(level)
		formatter = logging.Formatter(format)
		self.tempsh.setFormatter(formatter)
		self.logger.addHandler(self.tempsh)

	def rmTempHandler(self):
		self.logger.removeHandler(self.tempsh)
		self.tempsh = None

	def __call__(self, message, trcbk = None, priority = 0):
		"""
		Directly calls the logger for printing and storing the messages in the log file, for backwards compatibility only. Will be removed.

		Parameters:
			message: a text containing a description of the error
			trcbk: the traceback of the error
			priority (int): the importance of the error
		"""
		if trcbk is not None:
			message += "\n" + trcbk.format_exc()
		self.logger.log((2+priority)*10, message)

pBErrorManager = pBErrorManagerClass()
pBLogger = pBErrorManager.logger
