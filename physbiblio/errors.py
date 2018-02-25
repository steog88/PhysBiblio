"""
Module that only contains the pBErrorManager definition.

This file is part of the PhysBiblio package.
"""
import sys, traceback, os

try:
	from physbiblio.config import pbConfig
except ImportError:
    print("Cannot load physbiblio.config module: check your PYTHONPATH!")

class pBErrorManager():
	"""Class that manages the output of the errors and stores the messages into a log file"""
	def __init__(self, message, trcbk = None, priority = 0):
		"""
		Constructor for PBErrorManager.

		Parameters:
			message: a text containing a description of the error
			trcbk: the traceback of the error
			priority (int): the importance of the error
		"""
		if priority > 1:
			message = "****Critical error****\n" + message
		elif priority > 0:
			message = "**Error**\n" + message
		message += "\n"
		if sys.stdout == sys.__stdout__:
			sys.stderr.write(message)
			if trcbk is not None:
				sys.stderr.write(trcbk.format_exc())
		else:
			print(message)
			if trcbk is not None:
				print(trcbk.format_exc())

		try:
			with open(os.path.join(pbConfig.path, pbConfig.params["logFileName"]), "a") as w:
				w.write(message)
				if trcbk is not None:
					w.write(trcbk.format_exc())
		except IOError:
			if sys.stdout == sys.__stdout__:
				sys.stderr.write("[errorlog] ERROR in saving log file!")
				sys.stderr.write(traceback.format_exc())
			else:
				print("[errorlog] ERROR in saving log file!")
				print(traceback.format_exc())
