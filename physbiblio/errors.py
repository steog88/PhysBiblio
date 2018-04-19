"""
Module that only contains the pBErrorManager definition.

This file is part of the PhysBiblio package.
"""
import sys, traceback, os
import logging

try:
	from physbiblio.config import pbConfig
except ImportError:
    print("Cannot load physbiblio.config module: check your PYTHONPATH!")

class pBErrorManagerClass():
	"""Class that manages the output of the errors and stores the messages into a log file"""
	def __init__(self):
		"""
		Constructor for PBErrorManager.
		"""
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
		self.logger.setLevel(self.loglevel)

		fh = logging.FileHandler(pbConfig.params["logFileName"])
		formatter = logging.Formatter('%(asctime)s %(levelname)10s : [%(module)s.%(funcName)s] %(message)s')
		fh.setFormatter(formatter)
		self.logger.addHandler(fh)

		sh = logging.StreamHandler()
		formatter = logging.Formatter('[%(module)s.%(funcName)s] %(message)s')
		sh.setFormatter(formatter)
		self.logger.addHandler(sh)

		#other logger, will be used instead of print and redirected
		self.toOut = logging.getLogger("physbiblioout")
		self.toOut.propagate = False
		self.toOut.setLevel(logging.INFO)
		sh = logging.StreamHandler()
		formatter = logging.Formatter('%(message)s')
		sh.setFormatter(formatter)
		self.toOut.addHandler(sh)

	def log(self, message, trcbk = None, priority = 0):
		"""
		Uses a logger for printing and storing the messages in the log file.

		Parameters:
			message: a text containing a description of the error
			trcbk: the traceback of the error
			priority (int): the importance of the error
		"""
		if trcbk is not None:
			message += "\n" + trcbk.format_exc()
		self.logger.log((2+priority)*10, message)

	def out(self, message):
		"""
		Uses a logger for printing the messages.

		Parameters:
			message: a text containing a description of the error
		"""
		message += "\n"
		self.toOut.info(message)

	def __call__(self, *args, **kwargs):
		"""
		Redirect to self.log for backwards compatibility
		"""
		self.log(*args, **kwargs)

pBErrorManager = pBErrorManagerClass()
