"""Module that manages the command line calls of PhysBiblio.

This file is part of the physbiblio package.
"""
import sys
import datetime
import argparse

try:
	from physbiblio import __version__, __version_date__
	from physbiblio.config import pbConfig
except ImportError:
	print("Could not find physbiblio and its modules!")
	raise


def call_clean(args):
	"""Function used when the "clean" subcommand is called"""
	from physbiblio.database import pBDB
	pBDB.bibs.cleanBibtexs(startFrom=args.startFrom)
	pBDB.commit()


def call_cli(args):
	"""Function used when the "cli" subcommand is called"""
	from physbiblio.cli import cli as physBiblioCLI
	physBiblioCLI()


def call_export(args):
	"""Function used when the "export" subcommand is called"""
	from physbiblio.export import pBExport
	pBExport.exportAll(args.filename)


def call_tests(args):
	"""Function used when the "test" subcommand is called"""
	from physbiblio.setuptests import skipTestsSettings
	if args.database:
		skipTestsSettings.db = True
	if args.gui:
		skipTestsSettings.gui = True
	if args.long:
		skipTestsSettings.long = True
	if args.online_oai:
		skipTestsSettings.oai = True
	if args.online:
		skipTestsSettings.online = True
		skipTestsSettings.oai = True

	from physbiblio.testLoader import PBScanningLoader
	if sys.version_info[0] < 3:
		import unittest2 as unittest
	else:
		import unittest
	suite = PBScanningLoader().discover('physbiblio')
	testRunner = unittest.runner.TextTestRunner()
	testRunner.run(suite)


def call_tex(args):
	"""Function used when the "tex" subcommand is called"""
	from physbiblio.export import pBExport
	pBExport.exportForTexFile(
		args.texFiles,
		args.bibFile,
		overwrite=args.overwrite,
		autosave=args.save,
		updateExisting=args.updateExisting,
		removeUnused=args.removeUnused
		)


def call_update(args):
	"""Function used when the "update" subcommand is called"""
	from physbiblio.database import pBDB
	pBDB.bibs.searchOAIUpdates(startFrom=args.startFrom, force=args.force)
	pBDB.commit()


def call_oaiDates(date1, date2):
	"""Wrapper for getDailyInfoFromOAI + commit of the changes"""
	from physbiblio.database import pBDB
	pBDB.bibs.getDailyInfoFromOAI(date1, date2)
	pBDB.commit()


dateLast = datetime.date.today().strftime("%Y-%m-%d")


def call_dates(args):
	"""Use call_oaiDates to fetch updates between two dates
	specified in the command line
	"""
	call_oaiDates(args.start, args.end)


def call_daily(args):
	"""Use call_oaiDates to fetch daily updates"""
	call_oaiDates(
		(datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d"),
		dateLast)


def call_weekly(args):
	"""Use call_oaiDates to fetch weekly updates"""
	call_oaiDates(
		(datetime.date.today() - datetime.timedelta(7)).strftime("%Y-%m-%d"),
		dateLast)


def call_gui(args = None):
	"""Function that runs the PhysBiblio GUI"""
	from PySide2.QtWidgets import QApplication
	try:
		from physbiblio.errors import pBLogger
		from physbiblio.database import pBDB
		from physbiblio.gui.mainWindow import MainWindow
		from physbiblio.gui.errorManager import pBGUIErrorManager
	except ImportError:
		print("Could not find physbiblio and its modules!")
		raise
	try:
		app = QApplication(sys.argv)
		sys.excepthook = pBGUIErrorManager.excepthook
		mainWin = MainWindow()
		mainWin.show()
		mainWin.raise_()
		sys.exit(app.exec_())
	except NameError:
		pBLogger.critical("NameError:", exc_info=True)
	except SystemExit:
		pBDB.closeDB()
		pBLogger.info("Closing main window...")


class NewProfileAction(argparse.Action):
	"""Used to trigger a reload of the settings
	if a profile is specified as an argument
	"""

	def __init__(self, option_strings, dest, **kwargs):
		super(NewProfileAction, self).__init__(option_strings, dest, **kwargs)

	def __call__(self, parser, namespace, values, option_string=None):
		prof = values[0]
		if prof in pbConfig.profiles.keys():
			pbConfig.reloadProfiles(prof)
		setattr(namespace, self.dest, values)


def setParser():
	"""Contains the argparse definition of sub-commands and options"""
	parser = argparse.ArgumentParser(prog='PhysBiblio.exe')
	parser.add_argument(
		'-p',
		'--profile',
		action=NewProfileAction,
		nargs=1,
		choices=pbConfig.profiles.keys(),
		help='define the profile that must be used'
		)
	parser.add_argument(
		'-v',
		'--version',
		action='version',
		version='PhysBiblio %s (%s)'%(__version__, __version_date__)
		)
	subparsers = parser.add_subparsers(
		help='sub-command help',
		dest='cmd'
		)

	parser_clean = subparsers.add_parser(
		'clean',
		help='clean the entries in the database'
		)
	parser_clean.add_argument(
		'-s',
		'--startFrom',
		type=int,
		help='the index from which the cleaning should start',
		default=0
		)
	parser_clean.set_defaults(func=call_clean)

	parser_cli = subparsers.add_parser(
		'cli',
		help='open the internal command line interface'
		)
	parser_cli.set_defaults(func=call_cli)

	parser_daily = subparsers.add_parser(
		'daily',
		help='fetch the daily updates from INSPIRE-HEP OAI'
		)
	parser_daily.set_defaults(func=call_daily)

	parser_dates = subparsers.add_parser(
		'dates',
		help='fetch the updates from INSPIRE-HEP OAI between the given dates'
		)
	parser_dates.add_argument(
		'start',
		metavar='startdate',
		help='the starting date (format as yyyy-mm-dd)',
		default=(datetime.date.today() - datetime.timedelta(1))\
			.strftime("%Y-%m-%d")
		)
	parser_dates.add_argument(
		'end',
		metavar='enddate',
		help='the ending date (format as yyyy-mm-dd)',
		default=dateLast
		)
	parser_dates.set_defaults(func=call_dates)

	parser_export = subparsers.add_parser(
		'export',
		help='export all the entries in the database in a file'
		)
	parser_export.add_argument(
		'filename',
		help='the filename where to save the entries'
		)
	parser_export.set_defaults(func=call_export)

	parser_test = subparsers.add_parser(
		'test',
		help='run the test suite'
		)
	parser_test.add_argument(
		'-d',
		'--database',
		dest='database',
		action='store_true',
		help='do not perform database tests'
		)
	parser_test.add_argument(
		'-g',
		'--gui',
		dest='gui',
		action='store_true',
		help='do not perform gui tests'
		)
	parser_test.add_argument(
		'-l',
		'--long',
		dest='long',
		action='store_true',
		help='do not perform long tests'
		)
	parser_test.add_argument(
		'-o',
		'--online',
		dest='online',
		action='store_true',
		help='do not perform online tests'
		)
	parser_test.add_argument(
		'--online_oai',
		dest='online_oai',
		action='store_true',
		help='do not perform online tests with INSPIRE OAI'
		)
	parser_test.set_defaults(func=call_tests)

	parser_tex = subparsers.add_parser(
		'tex',
		help='read .tex file(s) and create a *.bib file '
			+ 'with the cited bibtexs')
	parser_tex.add_argument(
		'bibFile',
		metavar='bibfilename',
		help='the filename of the bib file where to write'
		)
	parser_tex.add_argument(
		'texFiles',
		metavar='texfilename',
		help='the filename of the tex file to read. '
			+ 'A folder or wildcards are admitted',
		nargs='+'
		)
	parser_tex.add_argument(
		'-o',
		'--overwrite',
		dest='overwrite',
		action='store_true',
		help='overwrite the bib file, if existing'
		)
	parser_tex.add_argument(
		'-r',
		'--removeUnused',
		dest='removeUnused',
		action='store_true',
		help='remove from the .bib file those elements '
			+ 'that are not more used in the tex'
		)
	parser_tex.add_argument(
		'-s',
		'--save',
		dest='save',
		action='store_false',
		help='save the changes in the database'
		)
	parser_tex.add_argument(
		'-u',
		'--updateExisting',
		dest='updateExisting',
		action='store_true',
		help='update the elements in the .bib file if they changed '
			+ 'in the database and remove duplicated entries'
		)
	parser_tex.set_defaults(func=call_tex)

	parser_update = subparsers.add_parser(
		'update',
		help='use INSPIRE to update the information in the database'
		)
	parser_update.add_argument(
		'-s',
		'--startFrom',
		type=int,
		help='the index from which the updating should start',
		default=0
		)
	parser_update.add_argument(
		'-f',
		'--force',
		action='store_true',
		help='force the update'
		)
	parser_update.set_defaults(func=call_update)

	parser_weekly = subparsers.add_parser(
		'weekly',
		help='fetch the weekly updates from INSPIRE-HEP OAI'
		)
	parser_weekly.set_defaults(func=call_weekly)

	parser_gui = subparsers.add_parser('gui', help='open the gui')
	parser_gui.set_defaults(func=call_gui)

	return parser
