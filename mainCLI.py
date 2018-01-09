#!/usr/bin/env python

import sys, traceback
import logging

try:
	from physbiblio.cli import cli as physBiblioCLI
except:
    print("Could not find physbiblio and its contents: configure your PYTHONPATH!")
    raise

if __name__ == '__main__':
	physBiblioCLI()

