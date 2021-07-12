"""Module that manages the command line calls of PhysBiblio.

This file is part of the physbiblio package.
"""
import argparse
import datetime
import sys

from PySide2.QtWidgets import QApplication

try:
    from physbiblio import __version__, __version_date__
    from physbiblio.config import pbConfig
    from physbiblio.errors import pBLogger
    from physbiblio.gui.errorManager import pBGUIErrorManager
    from physbiblio.strings.main import ArgParserStrings as apstr
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise


def call_citationCount(args):
    """Wrapper for citationCount + commit of the changes"""
    from physbiblio.database import pBDB

    inspireID = [e["inspire"] for e in pBDB.bibs.getAll()]
    pBDB.bibs.citationCount(inspireID)
    pBDB.commit()


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
    if args.online:
        skipTestsSettings.online = True

    from physbiblio.testLoader import PBScanningLoader

    if sys.version_info[0] < 3:
        import unittest2 as unittest
    else:
        import unittest
    suite = PBScanningLoader().discover("physbiblio")
    testRunner = unittest.runner.TextTestRunner()
    result = testRunner.run(suite)
    if not result.wasSuccessful():
        raise Exception(apstr.testFailed)


def call_tex(args):
    """Function used when the "tex" subcommand is called"""
    from physbiblio.export import pBExport

    pBExport.exportForTexFile(
        args.texFiles,
        args.bibFile,
        overwrite=args.overwrite,
        autosave=args.save,
        updateExisting=args.updateExisting,
        removeUnused=args.removeUnused,
        reorder=args.reorder,
    )


def call_update(args):
    """Function used when the "update" subcommand is called"""
    from physbiblio.database import pBDB

    pBDB.bibs.searchOAIUpdates(startFrom=args.startFrom, force=args.force)
    pBDB.commit()


def cumulativeInspireDates(date1, date2):
    """Wrapper for getDailyInfoFromOAI + commit of the changes"""
    from physbiblio.database import pBDB

    pBDB.bibs.getDailyInfoFromOAI(date1, date2)
    pBDB.commit()


dateLast = datetime.date.today().strftime("%Y-%m-%d")


def call_dates(args):
    """Use cumulativeInspireDates to fetch updates between two dates
    specified in the command line
    """
    cumulativeInspireDates(args.start, args.end)


def call_daily(args):
    """Use cumulativeInspireDates to fetch daily updates"""
    cumulativeInspireDates(
        (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d"), dateLast
    )


def call_weekly(args):
    """Use cumulativeInspireDates to fetch weekly updates"""
    cumulativeInspireDates(
        (datetime.date.today() - datetime.timedelta(7)).strftime("%Y-%m-%d"), dateLast
    )


def call_gui(args=None):
    """Function that runs the PhysBiblio GUI"""
    # these two imports must stay here,
    # so they start after the profile has been loaded properly:
    try:
        import physbiblio.gui.mainWindow
        from physbiblio.database import pBDB
    except ImportError:
        print("Could not find physbiblio and its modules!")
        raise
    try:
        app = QApplication(sys.argv)
        mainWin = physbiblio.gui.mainWindow.MainWindow()
        sys.excepthook = mainWin.errormessage.emit
        mainWin.show()
        mainWin.raise_()
        if pbConfig.params["openSinceLastUpdate"] != __version__:
            mainWin.recentChanges()
            pbConfig.globalDb.config.update("openSinceLastUpdate", __version__)
            pbConfig.globalDb.commit()
        sys.exit(app.exec_())
    except NameError:
        pBLogger.critical("NameError:", exc_info=True)
    except SystemExit:
        pBDB.closeDB()
        pBLogger.info(apstr.closeMainW)


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
    parser = argparse.ArgumentParser(prog="PhysBiblio.exe")
    parser.add_argument(
        "-p",
        "--profile",
        action=NewProfileAction,
        nargs=1,
        choices=pbConfig.profiles.keys(),
        help=apstr.profileHelp,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="PhysBiblio %s (%s)" % (__version__, __version_date__),
    )
    subparsers = parser.add_subparsers(help=apstr.subHelp, dest="cmd")

    parser_cit = subparsers.add_parser("citations", help=apstr.cleanHelp)
    parser_cit.set_defaults(func=call_citationCount)

    parser_clean = subparsers.add_parser("clean", help=apstr.cleanHelp)
    parser_clean.add_argument(
        "-s",
        "--startFrom",
        type=int,
        help=apstr.cleanStartHelp,
        default=0,
    )
    parser_clean.set_defaults(func=call_clean)

    parser_cli = subparsers.add_parser("cli", help=apstr.cliHelp)
    parser_cli.set_defaults(func=call_cli)

    parser_daily = subparsers.add_parser("daily", help=apstr.dailyHelp)
    parser_daily.set_defaults(func=call_daily)

    parser_dates = subparsers.add_parser("dates", help=apstr.datesHelp)
    parser_dates.add_argument(
        "start",
        metavar="startdate",
        help=apstr.datesStartHelp,
        default=(datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d"),
    )
    parser_dates.add_argument(
        "end",
        metavar="enddate",
        help=apstr.datesEndHelp,
        default=dateLast,
    )
    parser_dates.set_defaults(func=call_dates)

    parser_export = subparsers.add_parser("export", help=apstr.exportHelp)
    parser_export.add_argument("filename", help=apstr.exportFilenameHelp)
    parser_export.set_defaults(func=call_export)

    parser_test = subparsers.add_parser("test", help=apstr.testHelp)
    parser_test.add_argument(
        "-d",
        "--database",
        dest="database",
        action="store_true",
        help=apstr.testDbHelp,
    )
    parser_test.add_argument(
        "-g", "--gui", dest="gui", action="store_true", help=apstr.testGuiHelp
    )
    parser_test.add_argument(
        "-l",
        "--long",
        dest="long",
        action="store_true",
        help=apstr.testLongHelp,
    )
    parser_test.add_argument(
        "-o",
        "--online",
        dest="online",
        action="store_true",
        help=apstr.testOnlineHelp,
    )
    parser_test.set_defaults(func=call_tests)

    parser_tex = subparsers.add_parser("tex", help=apstr.texHelp)
    parser_tex.add_argument(
        "bibFile",
        metavar="bibfilename",
        help=apstr.texBibHelp,
    )
    parser_tex.add_argument(
        "texFiles",
        metavar="texfilename",
        help=apstr.texTexsHelp,
        nargs="+",
    )
    parser_tex.add_argument(
        "-o",
        "--overwrite",
        dest="overwrite",
        action="store_true",
        help=apstr.texOverwriteHelp,
    )
    parser_tex.add_argument(
        "-r",
        "--removeUnused",
        dest="removeUnused",
        action="store_true",
        help=apstr.texRemoveHelp,
    )
    parser_tex.add_argument(
        "--reorder",
        dest="reorder",
        action="store_true",
        help=apstr.texReorderHelp,
    )
    parser_tex.add_argument(
        "-s",
        "--save",
        dest="save",
        action="store_false",
        help=apstr.texSaveHelp,
    )
    parser_tex.add_argument(
        "-u",
        "--updateExisting",
        dest="updateExisting",
        action="store_true",
        help=apstr.texUpdateHelp,
    )
    parser_tex.set_defaults(func=call_tex)

    parser_update = subparsers.add_parser("update", help=apstr.updateHelp)
    parser_update.add_argument(
        "-s",
        "--startFrom",
        type=int,
        help=apstr.updateStartHelp,
        default=0,
    )
    parser_update.add_argument(
        "-f", "--force", action="store_true", help=apstr.updateForceHelp
    )
    parser_update.set_defaults(func=call_update)

    parser_weekly = subparsers.add_parser("weekly", help=apstr.weeklyHelp)
    parser_weekly.set_defaults(func=call_weekly)

    parser_gui = subparsers.add_parser("gui", help=apstr.guiHelp)
    parser_gui.set_defaults(func=call_gui)

    return parser
