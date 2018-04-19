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

class pBErrorManager():
	"""Class that manages the output of the errors and stores the messages into a log file"""
	def __init__(self):
		"""
		Constructor for PBErrorManager.

		Parameters:
			message: a text containing a description of the error
			trcbk: the traceback of the error
			priority (int): the importance of the error
		"""
		if pbConfig.params["loggingLevel"] == 0:
			loglevel=logging.ERROR
		elif pbConfig.params["loggingLevel"] == 1:
			loglevel=logging.WARNING
		elif pbConfig.params["loggingLevel"] == 2:
			loglevel=logging.INFO
		else:
			level=logging.DEBUG
		formatter = logging.Formatter('%(levelname)s %(asctime)s:%(message)s')
		logging.basicConfig(
			format=formatter,
			level=loglevel)
		#the main logger, will save to stdout and log file
		self.logger = logging.getLogger("physbibliolog")
		fh = logging.FileHandler(pbConfig.params["logFileName"])
		fh.setFormatter(formatter)
		self.logger.addHandler(fh)

		#other logger, will be used instead of print and redirected
		self.out = logging.getLogger("physbiblioout")
		self.out.setLevel(logging.INFO)
		self.out.setFormatter('%(message)s')

	def log(self, message, trcbk = None, priority = 0):
		message += "\n"
		if trcbk is not None:
			message += trcbk.format_exc()

		self.logger.log(priority*10, message)

	def out(self, message):
		message += "\n"
		self.out.info(message)
