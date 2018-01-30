import sys, traceback, os
import os.path as osp

try:
	from physbiblio.config import pbConfig
except ImportError:
    print("Cannot load physbiblio.config module: check your PYTHONPATH!")

class pBErrorManager():
	def __init__(self, message, trcbk = None, priority = 0):
		if priority > 1:
			message = "****Critical error****\n" + message
		if priority > 0:
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
			with open(osp.join(pbConfig.path, pbConfig.params["logFile"]), "a") as w:
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
