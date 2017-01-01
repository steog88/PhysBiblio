#!/usr/bin/env python

import sys
from PySide.QtCore import *
from PySide.QtGui  import *
import signal

#try:
	#from pybiblio.database import *
	#import pybiblio.export as bibexport
	#import pybiblio.webimport.webInterf as webInt
	#from pybiblio.cli import cli as pyBiblioCLI
	#from pybiblio.config import pbConfig
#except ImportError:
	#print("Could not find pybiblio and its contents: configure your PYTHONPATH!")
try:
	import pybiblio.gui.Resources_pyside
except ImportError:
	print("Missing Resources_pyside.py: Run script update_resources.sh")

def askYesNo(message, title = ""):
	reply = QMessageBox.question(None, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
	if reply == QMessageBox.Yes:
		return True
	if reply == QMessageBox.No:
		return False

def askFileName(message = "Filename to use:", title = "Enter filename"):
	reply = QInputDialog.getText(None, title, message)
	if reply[1]:
		# user clicked OK
		replyText = reply[0]
	else:
		# user clicked Cancel
		replyText = reply[0] # which will be "" if they clicked Cancel 
	return replyText

def infoMessage(message, title = ""):
	reply = QMessageBox.information(None, title, message)

class configWindow(QDialog):
	"""create a window for editing the configuration settings"""
	def __init__(self):
		pass
	
	
	
