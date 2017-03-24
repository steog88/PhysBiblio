import sys, traceback

try:
	from pybiblio.config import pbConfig
except ImportError:
    print("Cannot load pybiblio.config module: check your PYTHONPATH!")

class ErrorManager():
	def __init__(self, message, trcbk = None):
		pass
		
		try:
			with open(pbConfig.params["logFile"], "a") as w:
				w.write(message)
				if trcbk is not None:
					w.write(trcbk.format_exc())
		except IOError:
			print("[errorlog] ERROR in saving log file!")