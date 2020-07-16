"""Module that contains the pBErrorManager and pBLogger definitions.

This file is part of the physbiblio package.
"""
import logging
import logging.handlers
import sys
import traceback

try:
    from physbiblio.config import addFileHandler, getLogLevel, pbConfig
    from physbiblio.strings.main import ErrorsStrings as estr
except ImportError:
    print("Could not find physbiblio and its modules!")
    print(traceback.format_exc())
    raise


class PBErrorManagerClass:
    """Class that manages the output of the errors and
    stores the messages into a log file
    """

    def __init__(self, loggerString="physbibliolog"):
        """Constructor for PBErrorManagerClass.

        Parameter:
            loggerString: the `Logger` identifier string to use
                (default="physbibliolog")
        """
        self.tempsh = []
        self.loglevel = getLogLevel(pbConfig.params["loggingLevel"])
        # the main logger, will save to stdout and log file
        self.loggerString = loggerString
        self.logger = logging.getLogger(loggerString)
        self.logger.propagate = False
        self.logger.setLevel(min(logging.INFO, self.loglevel))

        try:
            # this part is used only for tests
            logFileName = pbConfig.overWritelogFileName
        except AttributeError:
            logFileName = pbConfig.params["logFileName"]
        addFileHandler(self.logger, logFileName)

        self.defaultStream = logging.StreamHandler()
        self.defaultStream.setLevel(min(logging.INFO, self.loglevel))
        formatter = logging.Formatter("[%(module)s.%(funcName)s] %(message)s")
        self.defaultStream.setFormatter(formatter)
        self.logger.addHandler(self.defaultStream)

    def tempHandler(
        self,
        stream=sys.stdout,
        level=logging.INFO,
        format="[%(module)s.%(funcName)s] %(message)s",
    ):
        """Set a temporary StreamHandler for the logger,
        given the stream, with default level logging.INFO.
        Useful when redirecting stdout

        Parameters:
            stream: the stream to be used (default: sys.stdout)
            level: the level to be used (default: logging.INFO)
            format: the format, using the logging syntax
                (default: '[%(module)s.%(funcName)s] %(message)s')
        """
        try:
            self.tempsh.append(logging.StreamHandler(stream))
            self.tempsh[-1].setLevel(level)
            formatter = logging.Formatter(format)
            self.tempsh[-1].setFormatter(formatter)
            self.logger.addHandler(self.tempsh[-1])
            return True
        except Exception:
            self.logger.exception(estr.errorAddHandler)
            return False

    def rmTempHandler(self):
        """Delete the last temporary handler that has been created"""
        self.logger.removeHandler(self.tempsh[-1])
        del self.tempsh[-1]

    def rmAllTempHandlers(self):
        """Delete the all the temporary handlers that have been created"""
        for temp in self.tempsh:
            self.logger.removeHandler(temp)
        self.tempsh = []

    def excepthook(self, cls, exception, trcbk):
        """Function that will replace `sys.excepthook` to log
        any error that occurs

        Parameters:
            cls, exception, trcbk as in `sys.excepthook`
        """
        self.logger.error(estr.unhandled, exc_info=(cls, exception, trcbk))


pBErrorManager = PBErrorManagerClass(pbConfig.loggerString)
pBLogger = pBErrorManager.logger
sys.excepthook = pBErrorManager.excepthook
