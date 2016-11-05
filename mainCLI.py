#!/usr/bin/env python

import sys, traceback
import logging

try:
	from pybiblio.cli import cli as pyBiblioCLI
except:
    print("Could not find pybiblio and its contents: configure your PYTHONPATH!")
    raise
    
pyBiblioCLI()

