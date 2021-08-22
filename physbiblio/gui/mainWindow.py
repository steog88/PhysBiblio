"""Module that contains the class for the main window of PhysBiblio.

This file is part of the physbiblio package.
"""
import ast
import glob
import os
import signal
import sys
import traceback

import bibtexparser
import six
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QGuiApplication, QIcon, QPixmap
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    QFrame,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QTabBar,
    QTabWidget,
    QWidget,
)

if sys.version_info[0] < 3:
    from Queue import Queue
else:
    from queue import Queue


try:
    from physbiblio.bibtexWriter import pbWriter
    from physbiblio.config import configuration_params, pbConfig
    from physbiblio.database import dbStats, pBDB
    from physbiblio.errors import pBErrorManager, pBLogger
    from physbiblio.export import pBExport
    from physbiblio.gui.basicDialogs import (
        LongInfoMessage,
        askFileName,
        askFileNames,
        askGenericText,
        askSaveFileName,
        askYesNo,
        infoMessage,
    )
    from physbiblio.gui.bibWindows import (
        AbstractFormulas,
        BibtexInfo,
        BibtexListWindow,
        FieldsFromArxiv,
        SearchBibsWindow,
        editBibtex,
    )
    from physbiblio.gui.catWindows import CatsTreeWindow, editCategory
    from physbiblio.gui.commonClasses import ObjectWithSignal, PBComboBox, WriteStream
    from physbiblio.gui.dialogWindows import (
        AdvancedImportDialog,
        AdvancedImportSelect,
        ConfigWindow,
        DailyArxivDialog,
        DailyArxivSelect,
        ExportForTexDialog,
        LogFileContentDialog,
        PrintText,
    )
    from physbiblio.gui.errorManager import pBGUILogger
    from physbiblio.gui.expWindows import (
        EditExperimentDialog,
        ExpsListWindow,
        editExperiment,
    )
    from physbiblio.gui.inspireStatsGUI import AuthorStatsPlots, PaperStatsPlots
    from physbiblio.gui.profilesManager import SelectProfiles, editProfile
    from physbiblio.gui.threadElements import (
        Thread_authorStats,
        Thread_checkUpdated,
        Thread_citationCount,
        Thread_cleanAllBibtexs,
        Thread_cleanSpare,
        Thread_cleanSparePDF,
        Thread_exportTexBib,
        Thread_fieldsArxiv,
        Thread_findBadBibtexs,
        Thread_importDailyArxiv,
        Thread_importFromBib,
        Thread_loadAndInsert,
        Thread_paperStats,
        Thread_replace,
        Thread_updateAllBibtexs,
        Thread_updateInspireInfo,
    )
    from physbiblio.inspireStats import pBStats
    from physbiblio.pdf import pBPDF
    from physbiblio.strings.gui import MainWindowStrings as mwstr
    from physbiblio.strings.main import DatabaseStrings as dbstr
    from physbiblio.view import pBView
    from physbiblio.webimport.webInterf import physBiblioWeb
except ImportError as e:
    print("Could not find physbiblio and its modules!", e)
    print(traceback.format_exc())
try:
    import physbiblio.gui.resourcesPyside2
except ImportError as e:
    print("Missing Resources_pyside2: run script update_resources.sh", e)


class MainWindow(QMainWindow):
    """This is the class that manages the main window of the PhysBiblio
    graphical interface
    """

    errormessage = Signal(type, type, Exception, traceback)

    def __init__(self, testing=False):
        """Main window constructor.
        Call many functions to set all the widgets and the properties

        Parameter:
            testing (default False): if True, return without
                executing all the creation of objects (used for tests)
        """
        QMainWindow.__init__(self)
        self.errormessage.connect(self.excepthook)
        availableWidth = QGuiApplication.primaryScreen().availableGeometry().width()
        availableHeight = QGuiApplication.primaryScreen().availableGeometry().height()
        self.setWindowTitle(mwstr.winTitle)
        # x,y of topleft corner, width, height
        self.setGeometry(0, 0, availableWidth, availableHeight)
        self.setMinimumHeight(400)
        self.setMinimumWidth(600)
        self.mainStatusBar = QStatusBar()
        self.lastAuthorStats = None
        self.lastPaperStats = None
        self.fileMenu = None
        self.bibMenu = None
        self.catMenu = None
        self.expMenu = None
        self.toolMenu = None
        self.searchMenu = None
        self.replaceMenu = None
        self.helpMenu = None
        self.mainToolBar = None
        self.bibtexListWindows = []
        self.bottomLeft = None
        self.bottomCenter = None
        self.bottomRight = None
        self.replaceResults = []
        self.loadedAndInserted = []
        self.selectedCats = []
        self.selectedExps = []
        self.badBibtexs = []
        self.importArXivResults = []
        self.tabWidget = QTabWidget(self)
        self.tabWidget.setTabBarAutoHide(True)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.currentChanged.connect(self.newTabAtEnd)
        self.tabWidget.tabBarDoubleClicked.connect(self.renameTab)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)
        if testing:
            return
        self.createActions()
        self.createMenusAndToolBar()
        self.createMainLayout()
        self.setIcon()
        self.createStatusBar()

        # When the DB is locked, ask if the user wants to close the PB instance
        self.onIsLockedClass = ObjectWithSignal()
        pBDB.onIsLocked = self.onIsLockedClass.customSignal
        pBDB.onIsLocked.connect(self.lockedDatabase)

        # Catch Ctrl+C in shell
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.checkUpdated = Thread_checkUpdated(self)
        self.checkUpdated.finished.connect(self.checkUpdated.deleteLater)
        self.checkUpdated.result.connect(self.printNewVersion)
        self.checkUpdated.start()

    def closeEvent(self, event):
        """Intercept close events. If uncommitted changes exist,
        ask before closing the application

        Parameter:
            event: a QEvent
        """
        if pBDB.checkUncommitted():
            if not askYesNo("%s\n%s" % (mwstr.unsavedChanges, mwstr.wantToExit)):
                event.ignore()
            else:
                event.accept()
        elif pbConfig.params["askBeforeExit"] and not askYesNo(mwstr.wantToExit):
            event.ignore()
        else:
            event.accept()

    def excepthook(self, cls, exception, trcbk):
        """Function that will replace `sys.excepthook` to log
        any error that occurs

        Parameters:
            cls, exception, trcbk as in `sys.excepthook`
        """
        pBGUILogger.error(mwstr.unhandled, exc_info=(cls, exception, trcbk))

    def mainWindowTitle(self, title):
        """Set the window title

        Parameter:
            title: the window title
        """
        self.setWindowTitle(title)

    def printNewVersion(self, outdated, newVersion):
        """Open a warning notifying the existence of a new version,
        if present, or just save an info in the log

        Parameters:
            outdated: boolean, tells if there is a new version available
                in the PyPI repositories for update
            newVersion: the number of the new version or an empty string
        """
        if outdated:
            if pbConfig.params["notifyUpdate"]:
                pBGUILogger.warning(mwstr.newVersion % newVersion)
            else:
                self.statusBarMessage(
                    (mwstr.newVersion.replace("\n", " ")) % newVersion
                )
        else:
            pBLogger.info(mwstr.noNewVersion)

    def lockedDatabase(self):
        """Action to be performed when the database is locked
        by another instance of the program.
        Ask what to do and close the main window.
        """
        if askYesNo(
            mwstr.dbLockedAskClose,
            title=mwstr.attentionE,
        ):
            raise SystemExit

    def setIcon(self):
        """Set the icon of the main window"""
        appIcon = QIcon(":/images/icon.png")
        self.setWindowIcon(appIcon)

    def keyPressEvent(self, e):
        """Manage the key press events.

        Parameters:
            e: the `PySide2.QtGui.QKeyEvent`
        """
        modifiers = QApplication.keyboardModifiers()
        if e.key() == Qt.Key_W and modifiers == Qt.ControlModifier:
            self.closeTab(self.tabWidget.currentIndex())
        elif e.key() == Qt.Key_N and modifiers == (
            Qt.ControlModifier | Qt.ShiftModifier
        ):
            self.newTabAtEnd(self.tabWidget.count() - 1)
        elif e.key() == Qt.Key_Tab and modifiers == (Qt.ControlModifier):
            index = self.tabWidget.currentIndex()
            self.tabWidget.setCurrentIndex(
                index + 1 if index < self.tabWidget.count() - 2 else 0
            )
        elif (e.key() == Qt.Key_Backtab and modifiers == Qt.ControlModifier) or (
            e.key() == Qt.Key_Backtab
            and modifiers == (Qt.ControlModifier | Qt.ShiftModifier)
        ):
            index = self.tabWidget.currentIndex()
            self.tabWidget.setCurrentIndex(
                index - 1 if index > 0 else self.tabWidget.count() - 2
            )

    def createActions(self):
        """Create the QActions used in menu and in the toolbar."""
        self.exitAct = QAction(
            QIcon(":/images/application-exit.png"),
            mwstr.Act.exitT,
            self,
            shortcut="Ctrl+Q",
            statusTip=mwstr.Act.exitD,
            triggered=self.close,
        )

        self.profilesAct = QAction(
            QIcon(":/images/profiles.png"),
            mwstr.Act.profT,
            self,
            shortcut="Ctrl+P",
            statusTip=mwstr.Act.profD,
            triggered=self.manageProfiles,
        )

        self.editProfileWindowsAct = QAction(
            mwstr.Act.editProfT,
            self,
            shortcut="Ctrl+Alt+P",
            statusTip=mwstr.Act.editProfD,
            triggered=self.editProfile,
        )

        self.undoAct = QAction(
            QIcon(":/images/edit-undo.png"),
            mwstr.Act.undoT,
            self,
            shortcut="Ctrl+Z",
            statusTip=mwstr.Act.undoD,
            triggered=self.undoDB,
        )

        self.saveAct = QAction(
            QIcon(":/images/file-save.png"),
            mwstr.Act.saveT,
            self,
            shortcut="Ctrl+S",
            statusTip=mwstr.Act.saveD,
            triggered=self.save,
        )

        self.importBibAct = QAction(
            mwstr.Act.impT,
            self,
            shortcut="Ctrl+B",
            statusTip=mwstr.Act.impD,
            triggered=self.importFromBib,
        )

        self.exportAct = QAction(
            QIcon(":/images/export.png"),
            mwstr.Act.expLT,
            self,
            statusTip=mwstr.Act.expLD,
            triggered=self.export,
        )

        self.exportAllAct = QAction(
            QIcon(":/images/export-table.png"),
            mwstr.Act.expAT,
            self,
            shortcut="Ctrl+A",
            statusTip=mwstr.Act.expAD,
            triggered=self.exportAll,
        )

        self.exportFileAct = QAction(
            mwstr.Act.expTT,
            self,
            shortcut="Ctrl+X",
            statusTip=mwstr.Act.expTD,
            triggered=self.exportFile,
        )

        self.exportUpdateAct = QAction(
            mwstr.Act.updT,
            self,
            shortcut="Ctrl+Shift+X",
            statusTip=mwstr.Act.updD,
            triggered=self.exportUpdate,
        )

        self.catAct = QAction(
            mwstr.Act.catT,
            self,
            shortcut="Ctrl+T",
            statusTip=mwstr.Act.catD,
            triggered=self.categories,
        )

        self.newCatAct = QAction(
            mwstr.Act.catNT,
            self,
            shortcut="Ctrl+Shift+T",
            statusTip=mwstr.Act.catND,
            triggered=self.newCategory,
        )

        self.expAct = QAction(
            mwstr.Act.expT,
            self,
            shortcut="Ctrl+E",
            statusTip=mwstr.Act.expD,
            triggered=self.experiments,
        )

        self.newExpAct = QAction(
            mwstr.Act.expNT,
            self,
            shortcut="Ctrl+Shift+E",
            statusTip=mwstr.Act.expND,
            triggered=self.newExperiment,
        )

        self.searchBibAct = QAction(
            QIcon(":/images/find.png"),
            mwstr.Act.findT,
            self,
            shortcut="Ctrl+F",
            statusTip=mwstr.Act.findD,
            triggered=self.searchBiblio,
        )

        self.searchReplaceAct = QAction(
            QIcon(":/images/edit-find-replace.png"),
            mwstr.Act.srT,
            self,
            shortcut="Ctrl+H",
            statusTip=mwstr.Act.srD,
            triggered=self.searchAndReplace,
        )

        self.newBibAct = QAction(
            QIcon(":/images/file-add.png"),
            mwstr.Act.bibNT,
            self,
            shortcut="Ctrl+N",
            statusTip=mwstr.Act.bibND,
            triggered=self.newBibtex,
        )

        self.inspireLoadAndInsertAct = QAction(
            mwstr.Act.loadInsT,
            self,
            shortcut="Ctrl+Shift+I",
            statusTip=mwstr.Act.loadInsD,
            triggered=self.inspireLoadAndInsert,
        )

        self.inspireLoadAndInsertWithCatsAct = QAction(
            mwstr.Act.loadInsCatT,
            self,
            shortcut="Ctrl+I",
            statusTip=mwstr.Act.loadInsCatD,
            triggered=self.inspireLoadAndInsertWithCats,
        )

        self.advImportAct = QAction(
            mwstr.Act.advImpT,
            self,
            shortcut="Ctrl+Alt+I",
            statusTip=mwstr.Act.advImpD,
            triggered=self.advancedImport,
        )

        self.updateAllBibtexsAct = QAction(
            mwstr.Act.updBT,
            self,
            shortcut="Ctrl+U",
            statusTip=mwstr.Act.updBD,
            triggered=self.updateAllBibtexs,
        )

        self.updateAllBibtexsAskAct = QAction(
            mwstr.Act.updPT,
            self,
            shortcut="Ctrl+Shift+U",
            statusTip=mwstr.Act.updPD,
            triggered=self.updateAllBibtexsAsk,
        )

        self.updateCitationCountAct = QAction(
            mwstr.Act.ccT,
            self,
            statusTip=mwstr.Act.ccD,
            triggered=self.getInspireCitationCount,
        )

        self.cleanAllBibtexsAct = QAction(
            mwstr.Act.cleBT,
            self,
            shortcut="Ctrl+L",
            statusTip=mwstr.Act.cleBD,
            triggered=self.cleanAllBibtexs,
        )

        self.findBadBibtexsAct = QAction(
            mwstr.Act.corrT,
            self,
            shortcut="Ctrl+Shift+B",
            statusTip=mwstr.Act.corrD,
            triggered=self.findBadBibtexs,
        )

        self.infoFromArxivAct = QAction(
            mwstr.Act.arxIT,
            self,
            shortcut="Ctrl+V",
            statusTip=mwstr.Act.arxID,
            triggered=self.infoFromArxiv,
        )

        self.dailyArxivAct = QAction(
            mwstr.Act.arxBT,
            self,
            shortcut="Ctrl+D",
            statusTip=mwstr.Act.arxBD,
            triggered=self.browseDailyArxiv,
        )

        self.cleanAllBibtexsAskAct = QAction(
            mwstr.Act.cleFT,
            self,
            shortcut="Ctrl+Shift+L",
            statusTip=mwstr.Act.cleFD,
            triggered=self.cleanAllBibtexsAsk,
        )

        self.authorStatsAct = QAction(
            mwstr.Act.autT,
            self,
            shortcut="Ctrl+Shift+A",
            statusTip=mwstr.Act.autD,
            triggered=self.authorStats,
        )

        self.configAct = QAction(
            QIcon(":/images/settings.png"),
            mwstr.Act.settT,
            self,
            shortcut="Ctrl+Shift+S",
            statusTip=mwstr.Act.settD,
            triggered=self.config,
        )

        self.refreshAct = QAction(
            QIcon(":/images/refresh2.png"),
            mwstr.Act.refT,
            self,
            shortcut="F5",
            statusTip=mwstr.Act.refD,
            triggered=self.refreshMainContent,
        )

        self.reloadAct = QAction(
            QIcon(":/images/refresh.png"),
            mwstr.Act.resT,
            self,
            shortcut="Shift+F5",
            statusTip=mwstr.Act.resD,
            triggered=self.reloadMainContent,
        )

        self.changesAct = QAction(
            mwstr.Act.chaT,
            self,
            statusTip=mwstr.Act.chaD,
            triggered=self.recentChanges,
        )

        self.aboutAct = QAction(
            QIcon(":/images/help-about.png"),
            mwstr.Act.abT,
            self,
            statusTip=mwstr.Act.abD,
            triggered=self.showAbout,
        )

        self.logfileAct = QAction(
            mwstr.Act.logT,
            self,
            shortcut="Ctrl+G",
            statusTip=mwstr.Act.logD,
            triggered=self.logfile,
        )

        self.dbstatsAct = QAction(
            QIcon(":/images/stats.png"),
            mwstr.Act.dbT,
            self,
            statusTip=mwstr.Act.dbD,
            triggered=self.showDBStats,
        )

        self.cleanSpareAct = QAction(
            mwstr.Act.cleET,
            self,
            statusTip=mwstr.Act.cleED,
            triggered=self.cleanSpare,
        )

        self.cleanSparePDFAct = QAction(
            mwstr.Act.clePT,
            self,
            statusTip=mwstr.Act.clePD,
            triggered=self.cleanSparePDF,
        )

    def createMenusAndToolBar(self):
        """Set the content of the menus and of the toolbar."""
        self.menuBar().clear()
        self.fileMenu = self.menuBar().addMenu(mwstr.Act.fileM)
        self.fileMenu.addAction(self.undoAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exportAct)
        self.fileMenu.addAction(self.exportFileAct)
        self.fileMenu.addAction(self.exportAllAct)
        self.fileMenu.addAction(self.exportUpdateAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.profilesAct)
        self.fileMenu.addAction(self.editProfileWindowsAct)
        self.fileMenu.addAction(self.configAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.bibMenu = self.menuBar().addMenu(mwstr.Act.bibM)
        self.bibMenu.addAction(self.newBibAct)
        self.bibMenu.addAction(self.importBibAct)
        self.bibMenu.addAction(self.inspireLoadAndInsertWithCatsAct)
        self.bibMenu.addAction(self.inspireLoadAndInsertAct)
        self.bibMenu.addAction(self.advImportAct)
        self.bibMenu.addSeparator()
        self.bibMenu.addAction(self.cleanAllBibtexsAct)
        self.bibMenu.addAction(self.cleanAllBibtexsAskAct)
        self.bibMenu.addAction(self.findBadBibtexsAct)
        self.bibMenu.addSeparator()
        self.bibMenu.addAction(self.infoFromArxivAct)
        self.bibMenu.addAction(self.updateAllBibtexsAct)
        self.bibMenu.addAction(self.updateAllBibtexsAskAct)
        self.bibMenu.addAction(self.updateCitationCountAct)
        self.bibMenu.addSeparator()
        self.bibMenu.addAction(self.searchBibAct)
        self.bibMenu.addAction(self.searchReplaceAct)
        self.bibMenu.addSeparator()
        self.bibMenu.addAction(self.refreshAct)
        self.bibMenu.addAction(self.reloadAct)

        self.catMenu = self.menuBar().addMenu(mwstr.Act.catM)
        self.catMenu.addAction(self.catAct)
        self.catMenu.addAction(self.newCatAct)

        self.expMenu = self.menuBar().addMenu(mwstr.Act.expM)
        self.expMenu.addAction(self.expAct)
        self.expMenu.addAction(self.newExpAct)

        self.toolMenu = self.menuBar().addMenu(mwstr.Act.toolsM)
        self.toolMenu.addAction(self.dailyArxivAct)
        self.toolMenu.addSeparator()
        self.toolMenu.addAction(self.cleanSpareAct)
        self.toolMenu.addAction(self.cleanSparePDFAct)
        self.toolMenu.addSeparator()
        self.toolMenu.addAction(self.authorStatsAct)

        pBDB.convertSearchFormat()
        freqSearches = pbConfig.globalDb.getSearchList(manual=True, replacement=False)
        if len(freqSearches) > 0:
            self.searchMenu = self.menuBar().addMenu(mwstr.Act.freqSM)
            for fs in freqSearches:
                self.searchMenu.addAction(
                    QAction(
                        fs["name"],
                        self,
                        triggered=lambda sD=ast.literal_eval(fs["searchDict"]), l=fs[
                            "limitNum"
                        ], o=fs["offsetNum"], n=fs["name"]: self.runSearchBiblio(
                            sD, l, o, newTab=n
                        ),
                    )
                )
            self.searchMenu.addSeparator()
            for fs in freqSearches:
                tmp = self.searchMenu.addMenu(mwstr.Act.manage % fs["name"])
                tmp.addAction(
                    QAction(
                        mwstr.Act.edit % fs["name"],
                        self,
                        triggered=lambda idS=fs["idS"], n=fs[
                            "name"
                        ]: self.editSearchBiblio(idS, n),
                    )
                )
                tmp.addAction(
                    QAction(
                        mwstr.Act.rename % fs["name"],
                        self,
                        triggered=lambda idS=fs["idS"], n=fs[
                            "name"
                        ]: self.renameSearchBiblio(idS, n),
                    )
                )
                tmp.addAction(
                    QAction(
                        mwstr.Act.delete % fs["name"],
                        self,
                        triggered=lambda idS=fs["idS"], n=fs[
                            "name"
                        ]: self.delSearchBiblio(idS, n),
                    )
                )
        else:
            self.searchMenu = None

        freqReplaces = pbConfig.globalDb.getSearchList(manual=True, replacement=True)
        if len(freqReplaces) > 0:
            self.replaceMenu = self.menuBar().addMenu(mwstr.Act.freqRM)
            for fs in freqReplaces:
                self.replaceMenu.addAction(
                    QAction(
                        fs["name"],
                        self,
                        triggered=lambda sD=ast.literal_eval(
                            fs["searchDict"]
                        ), r=ast.literal_eval(fs["replaceFields"]), o=fs[
                            "offsetNum"
                        ], n=fs[
                            "name"
                        ]: self.runSearchReplaceBiblio(
                            sD, r, o, newTab=n
                        ),
                    )
                )
            self.replaceMenu.addSeparator()
            for fs in freqReplaces:
                tmp = self.replaceMenu.addMenu(mwstr.Act.manage % fs["name"])
                tmp.addAction(
                    QAction(
                        mwstr.Act.edit % fs["name"],
                        self,
                        triggered=lambda idS=fs["idS"], n=fs[
                            "name"
                        ]: self.editSearchBiblio(idS, n),
                    )
                )
                tmp.addAction(
                    QAction(
                        mwstr.Act.rename % fs["name"],
                        self,
                        triggered=lambda idS=fs["idS"], n=fs[
                            "name"
                        ]: self.renameSearchBiblio(idS, n),
                    )
                )
                tmp.addAction(
                    QAction(
                        mwstr.Act.delete % fs["name"],
                        self,
                        triggered=lambda idS=fs["idS"], n=fs[
                            "name"
                        ]: self.delSearchBiblio(idS, n),
                    )
                )
        else:
            self.replaceMenu = None

        self.helpMenu = self.menuBar().addMenu(mwstr.Act.helpM)
        self.helpMenu.addAction(self.dbstatsAct)
        self.helpMenu.addAction(self.logfileAct)
        self.helpMenu.addSeparator()
        self.helpMenu.addAction(self.changesAct)
        self.helpMenu.addAction(self.aboutAct)

        try:
            self.removeToolBar(self.mainToolBar)
        except AttributeError:
            pass
        self.mainToolBar = self.addToolBar(mwstr.Act.toolbar)
        self.mainToolBar.addAction(self.undoAct)
        self.mainToolBar.addAction(self.saveAct)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.newBibAct)
        self.mainToolBar.addAction(self.searchBibAct)
        self.mainToolBar.addAction(self.searchReplaceAct)
        self.mainToolBar.addAction(self.exportAct)
        self.mainToolBar.addAction(self.exportAllAct)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.refreshAct)
        self.mainToolBar.addAction(self.reloadAct)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.configAct)
        self.mainToolBar.addAction(self.dbstatsAct)
        self.mainToolBar.addAction(self.aboutAct)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.exitAct)

    def createMainLayout(self):
        """Set the layout of the main window, i.e. create the splitters
        and locate the bibtex list widget and the info panels
        """
        # tabs with the bibtex tables
        self.fillTabs()
        self.tabWidget.setCurrentIndex(0)

        # will contain the bibtex code:
        self.bottomLeft = BibtexInfo(self)
        self.bottomLeft.setFrameShape(QFrame.StyledPanel)

        # will contain the abstract of the bibtex entry:
        self.bottomCenter = BibtexInfo(self)
        self.bottomCenter.setFrameShape(QFrame.StyledPanel)

        # will contain other info on the bibtex entry:
        self.bottomRight = BibtexInfo(self)
        self.bottomRight.setFrameShape(QFrame.StyledPanel)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.tabWidget)
        splitterBottom = QSplitter(Qt.Horizontal)
        splitterBottom.addWidget(self.bottomLeft)
        splitterBottom.addWidget(self.bottomCenter)
        splitterBottom.addWidget(self.bottomRight)
        splitter.addWidget(splitterBottom)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        availableWidth = QGuiApplication.primaryScreen().availableGeometry().width()
        availableHeight = QGuiApplication.primaryScreen().availableGeometry().height()
        splitter.setGeometry(0, 0, availableWidth, availableHeight)

        self.setCentralWidget(splitter)

    def addBibtexListWindow(self, label, bibs=None, askBibs=False, previous=[]):
        """Function that creates a new BibtexListWindow and add its
        (with a label) to the list bibtexListWindows.

        Parameters:
            label: a string that identifies the tab
            bibs, askBibs, previous: directly passed to BibtexListWindow
        """
        self.bibtexListWindows.append(
            [
                BibtexListWindow(
                    parent=self, bibs=bibs, askBibs=askBibs, previous=previous
                ),
                label,
            ]
        )

    def currentTabWidget(self):
        """Return the current BibtexListWindow in the self.tabWidget

        Output:
            a BibtexListWindow item, currently displayed in the QTabWidget
        """
        return self.bibtexListWindows[self.tabWidget.currentIndex()][0]

    def fillTabs(self):
        """Create as many tabs as the number of bibtexListWindows items"""
        # will contain the list of bibtex entries
        if len(self.bibtexListWindows) < 1:
            self.addBibtexListWindow(mwstr.mainTab)

        self.tabWidget.blockSignals(True)
        self.tabWidget.clear()
        for tab, lab in self.bibtexListWindows:
            self.tabWidget.addTab(tab, lab)
        # add fake tab that will allow to add new ones
        self.tabWidget.addTab(QWidget(self), QIcon(":/images/file-add.png"), "")
        # hide close buttons for first and last tabs
        for i in [0, self.tabWidget.count() - 1]:
            try:
                self.tabWidget.tabBar().tabButton(i, QTabBar.RightSide).deleteLater()
            except AttributeError:
                pBLogger.debug("", exc_info=True)
            self.tabWidget.tabBar().setTabButton(i, QTabBar.RightSide, None)
        self.tabWidget.blockSignals(False)

    def closeAllTabs(self):
        """Close all the available tabs,
        except the main and the "new tab" one:
        delete the corresponding BibtexListWindow item
        and recreate the tabs
        """
        for index in range(self.tabWidget.count() - 2, 0, -1):
            try:
                del self.bibtexListWindows[index]
            except IndexError:
                pass
        self.fillTabs()

    def closeTab(self, index):
        """Close a tab, if it is not the main nor the "new tab" one:
        delete the corresponding BibtexListWindow item
        and recreate the tabs

        Parameter:
            index: the index of the tab to be deleted
        """
        closed = False
        if index != 0 and index != self.tabWidget.count() - 1:
            try:
                del self.bibtexListWindows[index]
            except IndexError:
                pass
            else:
                closed = True
        self.fillTabs()
        if closed:
            self.tabWidget.setCurrentIndex(index - 1)

    def newTabAtEnd(self, index, label=None, bibs=None, askBibs=False, previous=[]):
        """Function that checks if the "open new tab" tab is triggered.
        If yes, create a new bibtexListWindow and recreate the tabWidget

        Parameters:
            index: the index of the clicked tab
            label (default None): if not None, the label of the new tab
            bibs, askBibs, previous: directly passed to BibtexListWindow
        """
        if self.tabWidget.count() > 1 and index == self.tabWidget.count() - 1:
            self.addBibtexListWindow(
                mwstr.newTab if label is None else label,
                bibs=bibs,
                askBibs=askBibs,
                previous=previous,
            )
            self.fillTabs()
            self.tabWidget.setCurrentIndex(index)

    def renameTab(self, index):
        """Rename a tab, if it is not the main nor the "new tab" one

        Parameter:
            index: the index of the tab to be renamed
        """
        if index != 0 and index != self.tabWidget.count() - 1:
            try:
                oldname = self.bibtexListWindows[index][1]
            except IndexError:
                return
            newname, res = askGenericText(
                mwstr.newTabAsk, mwstr.newTabName, previous=oldname
            )
            if res:
                self.tabWidget.setTabText(index, newname)
                self.bibtexListWindows[index][1] = newname

    def undoDB(self):
        """Reset database changes, window title and table content"""
        pBDB.undo()
        self.mainWindowTitle(mwstr.winTitle)
        self.reloadMainContent()

    def refreshMainContent(self):
        """Delete the previous table widget and create a new one,
        using last used query
        """
        self.statusBarMessage(mwstr.reloadMain)
        self.currentTabWidget().recreateTable(pBDB.bibs.fetchFromLast().lastFetched)
        self.done()

    def reloadMainContent(self, bibs=None, newTab=None):
        """Delete the previous table widget and create a new one,
        using the default query

        Parameters:
            bibs (default None): the list of bibtexs to show in the table
            newTab (default None): if not None, the label of the new tab
        """
        if newTab:
            self.newTabAtEnd(self.tabWidget.count() - 1, label=newTab)
        self.statusBarMessage(mwstr.reloadMain)
        self.currentTabWidget().recreateTable(bibs)
        self.done()

    def manageProfiles(self):
        """Ask and change profile"""
        profilesWin = SelectProfiles(self)
        profilesWin.exec_()

    def editProfile(self):
        """Wrapper for profilesManager.editProfile"""
        editProfile(self)

    def config(self):
        """Open a window to manage the configuration of PhysBiblio,
        then read its output and save the results
        """
        cfgWin = ConfigWindow(self)
        cfgWin.exec_()
        if cfgWin.result:
            changed = False
            for q in cfgWin.textValues:
                if isinstance(q[1], PBComboBox):
                    s = "%s" % q[1].currentText()
                else:
                    s = "%s" % q[1].text()
                if q[0] == "loggingLevel":
                    s = s.split(" - ")[0]
                if str(pbConfig.params[q[0]]) != s:
                    pBLogger.info(mwstr.configNewVal % (q[0], s, pbConfig.params[q[0]]))
                    pbConfig.params[q[0]] = s
                    if configuration_params[q[0]].isGlobal:
                        pbConfig.globalDb.config.update(q[0], s)
                        pbConfig.globalDb.commit()
                    else:
                        pBDB.config.update(q[0], s)
                    changed = True
                pBLogger.debug(mwstr.configUseVal % (q[0], s))
            if changed:
                pBDB.commit()
                pbConfig.readConfig()
                self.reloadConfig()
                self.refreshMainContent()
                self.statusBarMessage(mwstr.configSave)
            else:
                self.statusBarMessage(mwstr.configNoChanges)
        else:
            self.statusBarMessage(mwstr.configDiscard)

    def logfile(self):
        """Open a dialog to see the content of the log file"""
        logfileWin = LogFileContentDialog(self)
        logfileWin.exec_()

    def reloadConfig(self):
        """Reload the configuration from the database.
        Typically used when a new profile has been opened
        """
        self.statusBarMessage(mwstr.configReload)
        pBView.webApp = pbConfig.params["webApplication"]
        pBPDF.pdfApp = pbConfig.params["pdfApplication"]
        if pbConfig.params["pdfFolder"][0] == "/":
            pBPDF.pdfDir = pbConfig.params["pdfFolder"]
        else:
            pBPDF.pdfDir = os.path.join(
                os.path.split(os.path.abspath(sys.argv[0]))[0],
                pbConfig.params["pdfFolder"],
            )
        pBPDF.checkFolderExists()
        self.currentTabWidget().reloadColumnContents()

    def recentChanges(self):
        """Function to show the recent changes in the current version"""
        mbox = QMessageBox(
            QMessageBox.Information,
            mwstr.recentCh,
            mwstr.recentNew % (physbiblio.__version__, physbiblio.__version_date__)
            + "%s<br>" % physbiblio.__recent_changes__,
            parent=self,
        )
        mbox.setTextFormat(Qt.RichText)
        mbox.setIconPixmap(QPixmap(":/images/icon.png"))
        mbox.exec_()

    def showAbout(self):
        """Function to show the About dialog"""
        mbox = QMessageBox(
            QMessageBox.Information,
            mwstr.aboutTitle,
            mwstr.aboutText.format(
                cp=pbConfig.configPath,
                dp=pbConfig.dataPath,
                ver=physbiblio.__version__,
                vd=physbiblio.__version_date__,
                pyv=sys.version,
            ),
            parent=self,
        )
        mbox.setTextFormat(Qt.RichText)
        mbox.setIconPixmap(QPixmap(":/images/icon.png"))
        mbox.exec_()

    def showDBStats(self):
        """Function to show a dialog with the statistics
        of the database content and on the number of stored PDF files
        """
        dbStats(pBDB)
        onlyfiles = pBPDF.numberOfFiles(pBPDF.pdfDir)
        mbox = QMessageBox(
            QMessageBox.Information,
            mwstr.dbStatsTitle,
            mwstr.dbStatsText.format(
                bib=pBDB.stats["bibs"],
                cat=pBDB.stats["cats"],
                exp=pBDB.stats["exps"],
                catbib=pBDB.stats["catBib"],
                catexp=pBDB.stats["catExp"],
                bibexp=pBDB.stats["bibExp"],
                nf=onlyfiles,
                pdfs=pBPDF.getSizeWUnits(pBPDF.dirSize(pBPDF.pdfDir)),
            ),
            parent=self,
        )
        mbox.setIconPixmap(QPixmap(":/images/icon.png"))
        mbox.show()

    def _runInThread(self, Thread_func, title, *args, **kwargs):
        """Function which simplifies the creation of the objects which
        are needed to run a function in a thread

        Parameters:
            Thread_func: the thread class name
            title: the title of the window where the output is shown
            *args, **kwargs: all the other parameters which will
                be passed to the thread constructor
        """

        def getDelKwargs(key):
            """Extract a parameter from kwargs and delete it
            from the original dictionary
            """
            if key in kwargs.keys():
                tmp = kwargs.get(key)
                del kwargs[key]
                return tmp
            else:
                return None

        def closePrintText(a, t):
            try:
                t.wait()
            except RuntimeError:
                pass
            a.reject()

        addMessage = getDelKwargs("addMessage")
        stopFlag = getDelKwargs("stopFlag")
        app = PrintText(title=title, noStopButton=stopFlag == False)

        outMessage = getDelKwargs("outMessage")
        minProgress = getDelKwargs("minProgress")
        if minProgress:
            app.progressBarMin(minProgress)
        queue = Queue()
        ws = WriteStream(queue)
        ws.newText.connect(app.appendText)
        kwargs["pbMax"] = app.pbMax.emit
        kwargs["pbVal"] = app.pbVal.emit
        thr = Thread_func(ws, *args, parent=self, **kwargs)

        ws.finished.connect(ws.deleteLater)
        thr.finished.connect(app.enableClose)
        thr.finished.connect(thr.deleteLater)
        app.closeButton.clicked.connect(lambda a=app, t=thr: closePrintText(a, t))
        if stopFlag:
            app.stopped.connect(thr.setStopFlag)

        pBErrorManager.tempHandler(ws, format="%(message)s")
        if addMessage:
            pBLogger.info(addMessage)
        thr.start()
        app.exec_()
        pBLogger.info(mwstr.closing)
        pBErrorManager.rmTempHandler()
        if outMessage:
            self.statusBarMessage(outMessage)
        else:
            self.done()

    def cleanSpare(self):
        """Run a thread to clean the spare connections and records
        in the database (if something has not been properly deleted)
        """
        self._runInThread(Thread_cleanSpare, mwstr.cleanSpareT)

    def cleanSparePDF(self):
        """Ask and run a thread to remove the spare PDF files/folder
        in the database (if something has not been properly deleted)
        """
        if askYesNo(mwstr.cleanPDFAsk):
            self._runInThread(Thread_cleanSparePDF, mwstr.cleanPDFT)

    def createStatusBar(self):
        """Function to create Status Bar"""
        self.mainStatusBar.showMessage(mwstr.ready, 0)
        self.setStatusBar(self.mainStatusBar)

    def statusBarMessage(self, message, time=4000):
        """Show a message in the status bar

        Parameters:
            message: the message text
            time (default 4000): how long (in ms) to display the message
        """
        pBLogger.info(message)
        self.mainStatusBar.showMessage(message, time)

    def save(self):
        """Ask and save the database changes"""
        if askYesNo(mwstr.saveAsk):
            pBDB.commit()
            self.mainWindowTitle(mwstr.winTitle)
            self.statusBarMessage(mwstr.saveCh)
        else:
            self.statusBarMessage(mwstr.saveNoth)

    def importFromBib(self):
        """Ask and import (from a thread) the entries in a .bib file"""
        filename = askFileName(
            self, title=mwstr.importFromWhere, filter="Bibtex (*.bib)"
        )
        if filename != "":
            self._runInThread(
                Thread_importFromBib,
                mwstr.importing,
                filename,
                askYesNo(mwstr.importInspire),
                minProgress=0,
                stopFlag=True,
                outMessage=mwstr.importAllDone % filename,
            )
            self.statusBarMessage(mwstr.importFile % filename)
            self.reloadMainContent()
        else:
            self.statusBarMessage(mwstr.emptyFN)

    def export(self):
        """Ask and export the last database query result in a .bib file"""
        filename = askSaveFileName(
            self,
            title=mwstr.exportWhereG,
            filter="Bibtex (*.bib)",
        )
        if filename != "":
            pBExport.exportLast(filename)
            self.statusBarMessage(mwstr.exportLastDone % filename)
        else:
            self.statusBarMessage(mwstr.emptyFN)

    def exportSelection(self, entries):
        """Ask and export the last selected entries in a .bib file

        Parameter:
            entries: the list of entries to be exported
        """
        filename = askSaveFileName(
            self,
            title=mwstr.exportWhereS,
            filter="Bibtex (*.bib)",
        )
        if filename != "":
            pBExport.exportSelected(filename, entries)
            self.statusBarMessage(mwstr.exportSelDone % filename)
        else:
            self.statusBarMessage(mwstr.emptyFN)

    def exportFile(self):
        """Ask and export in a .bib file the bibtex entries
        which are needed to compile one or more tex files
        """
        eft = ExportForTexDialog(self)
        eft.exec_()
        if eft.result:
            outFName = eft.bibName
            if outFName != "":
                texFNames = eft.texNames
                if (not isinstance(texFNames, list) and texFNames != "") or (
                    isinstance(texFNames, list) and len(texFNames) > 0
                ):
                    self._runInThread(
                        Thread_exportTexBib,
                        mwstr.exporting,
                        texFNames,
                        outFName,
                        minProgress=0,
                        stopFlag=True,
                        updateExisting=eft.update,
                        removeUnused=eft.remove,
                        reorder=eft.reorder,
                        outMessage=mwstr.exportAllSaved % outFName,
                    )
                else:
                    self.statusBarMessage(mwstr.emptyInFNs)
            else:
                self.statusBarMessage(mwstr.emptyOutFN)
        else:
            self.statusBarMessage(mwstr.nothingToDo)

    def exportUpdate(self):
        """Ask and update a .bib file
        which already contains bibtex entries
        with the newer information from the database
        """
        filename = askSaveFileName(
            self, title=mwstr.updateFileQ, filter="Bibtex (*.bib)"
        )
        if filename != "":
            overwrite = askYesNo(mwstr.askOverwriteBib, mwstr.overwrite)
            pBExport.updateExportedBib(filename, overwrite=overwrite)
            self.statusBarMessage(mwstr.updateFileD % filename)
        else:
            self.statusBarMessage(mwstr.emptyOutFN)

    def exportAll(self):
        """Ask and export all the entries in a .bib file"""
        filename = askSaveFileName(
            self,
            title=mwstr.exportWhereG,
            filter="Bibtex (*.bib)",
        )
        if filename != "":
            pBExport.exportAll(filename)
            self.statusBarMessage(mwstr.exportAllSaved % filename)
        else:
            self.statusBarMessage(mwstr.emptyOutFN)

    def categories(self):
        """Open a window to show the list categories"""
        self.statusBarMessage(mwstr.trigCat)
        try:
            self.catListWin.close()
        except AttributeError:
            pass
        self.catListWin = CatsTreeWindow(self)
        self.catListWin.show()

    def newCategory(self):
        """Wrapper for catWindows.editCategory"""
        editCategory(self, self)

    def experiments(self):
        """Open a window to show the list experiments"""
        self.statusBarMessage(mwstr.trigExp)
        try:
            self.expListWin.close()
        except AttributeError:
            pass
        self.expListWin = ExpsListWindow(self)
        self.expListWin.show()

    def newExperiment(self):
        """Wrapper for expWindows.editExperiment"""
        editExperiment(self, self)

    def newBibtex(self):
        """Wrapper for bibWindows.editBibtex"""
        editBibtex(self)

    def searchBiblio(self, replace=False):
        """Open a dialog for performing searches in the database

        Parameter:
            replace (default False): to be passed to SearchBibsWindow,
                in order to show (or not) the replace field inputs
        """
        newSearchWin = SearchBibsWindow(self, replace=replace)
        newSearchWin.exec_()
        if newSearchWin.result:
            searchFields = newSearchWin.values
            lim = newSearchWin.limit
            offs = newSearchWin.offset
            if replace:
                replaceFields = newSearchWin.replaceFields
                if newSearchWin.save:
                    name = ""
                    cancel = False
                    while name.strip() == "":
                        res = askGenericText(
                            mwstr.replaceAskName,
                            mwstr.replaceName,
                            parent=self,
                        )
                        if res[1]:
                            name = res[0]
                        else:
                            cancel = True
                            break
                    if not cancel:
                        pbConfig.globalDb.insertSearch(
                            name=name,
                            count=0,
                            searchFields=searchFields,
                            manual=True,
                            replacement=True,
                            limit=lim,
                            offset=offs,
                            replaceFields=replaceFields,
                        )
                        self.createMenusAndToolBar()
                else:
                    pbConfig.globalDb.updateSearchOrder(replacement=True)
                    pbConfig.globalDb.insertSearch(
                        count=0,
                        searchFields=searchFields,
                        manual=False,
                        replacement=True,
                        limit=lim,
                        offset=offs,
                        replaceFields=replaceFields,
                    )
                if newSearchWin.newTabCheck.isChecked():
                    self.newTabAtEnd(self.tabWidget.count() - 1, label=mwstr.newTab)
                noLim = pBDB.bibs.fetchFromDict(
                    searchFields, limitOffset=offs, doFetch=False
                )
                return replaceFields
            if newSearchWin.save:
                name = ""
                cancel = False
                while name.strip() == "":
                    res = askGenericText(
                        mwstr.searchAskName,
                        mwstr.searchName,
                        parent=self,
                    )
                    if res[1]:
                        name = res[0]
                    else:
                        cancel = True
                        break
                if not cancel:
                    pbConfig.globalDb.insertSearch(
                        name=name,
                        count=0,
                        searchFields=searchFields,
                        manual=True,
                        replacement=False,
                        limit=lim,
                        offset=offs,
                    )
                    self.createMenusAndToolBar()
            else:
                pbConfig.globalDb.updateSearchOrder()
                pbConfig.globalDb.insertSearch(
                    count=0,
                    searchFields=searchFields,
                    manual=False,
                    replacement=False,
                    limit=lim,
                    offset=offs,
                )
            self.runSearchBiblio(
                searchFields,
                lim,
                offs,
                newTab=mwstr.newTab if newSearchWin.newTabCheck.isChecked() else None,
            )
        elif replace:
            return False

    def runSearchBiblio(self, searchFields, lim, offs, newTab=None):
        """Run a search with some parameters

        Parameters:
            searchFields: the lsit of dictionaries
                with the search parameters
                to be used in `database.Entries.fetchFromDict`
            lim: the maximum number of entries to fetch
            offs: the offset for the search
            newTab (default None): if not None, the label of the new tab
        """
        if newTab is not None:
            self.newTabAtEnd(self.tabWidget.count() - 1, label=newTab)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        noLim = pBDB.bibs.fetchFromDict(searchFields, limitOffset=offs).lastFetched
        lastFetched = pBDB.bibs.fetchFromDict(
            searchFields, limitTo=lim, limitOffset=offs
        ).lastFetched
        if len(noLim) > len(lastFetched):
            infoMessage(mwstr.srMoreEntries % (len(lastFetched), len(noLim)))
        self.reloadMainContent(lastFetched)
        QApplication.restoreOverrideCursor()

    def runSearchReplaceBiblio(self, searchFields, replaceFields, offs, newTab=None):
        """Run a search&replace with some parameters

        Parameters:
            searchFields: the list of dictionaries
                with the search parameters
                to be used in `database.Entries.fetchFromDict`
            replaceFields: a tuple/list of 5 elements,
                as in the output of `self.searchBiblio`
            offs: the offset for the search
            newTab (default None): if not None, the label of the new tab
        """
        pBDB.bibs.fetchFromDict(searchFields, limitOffset=offs)
        self.runReplace(replaceFields, newTab=newTab)

    def renameSearchBiblio(self, idS, oldname):
        """Rename a saved search

        Parameters:
            idS: the search id in the database
            oldname: the old search name
        """
        name = ""
        cancel = False
        while name.strip() == "":
            res = askGenericText(
                mwstr.srAskNewName % oldname,
                mwstr.srNewName,
                parent=self,
                previous=oldname,
            )
            if res[1]:
                name = res[0]
            else:
                cancel = True
                break
        if not cancel:
            pbConfig.globalDb.updateSearchField(idS, "name", name)
            pbConfig.globalDb.commit()
            self.createMenusAndToolBar()

    def editSearchBiblio(self, idS, name):
        """Edit a saved search

        Parameters:
            idS: the search id in the database
            name: the search name
        """
        record = pbConfig.globalDb.getSearchByID(idS)
        if len(record) < 1:
            pBLogger.error(mwstr.searchCantFind % idS)
            return
        newSearchWin = SearchBibsWindow(replace=record[0]["isReplace"], edit=idS)
        newSearchWin.exec_()
        if newSearchWin.result:
            searchFields = newSearchWin.values
            lim = newSearchWin.limit
            offs = newSearchWin.offset
            if newSearchWin.replace:
                replaceFields = newSearchWin.replaceFields
                if newSearchWin.save:
                    pbConfig.globalDb.updateSearchField(idS, "searchDict", searchFields)
                    pbConfig.globalDb.updateSearchField(
                        idS, "replaceFields", replaceFields
                    )
                    pbConfig.globalDb.commit()
                pBDB.bibs.fetchFromDict(searchFields, limitOffset=offs)
                self.runReplace(
                    replaceFields,
                    newTab=mwstr.newTab
                    if newSearchWin.newTabCheck.isChecked()
                    else None,
                )
            else:
                if newSearchWin.save:
                    pbConfig.globalDb.updateSearchField(idS, "searchDict", searchFields)
                    pbConfig.globalDb.updateSearchField(idS, "limitNum", lim)
                    pbConfig.globalDb.updateSearchField(idS, "offsetNum", offs)
                    pbConfig.globalDb.commit()
                self.runSearchBiblio(
                    searchFields,
                    lim,
                    offs,
                    newTab=mwstr.newTab
                    if newSearchWin.newTabCheck.isChecked()
                    else None,
                )

    def delSearchBiblio(self, idS, name):
        """Delete a saved search from the database

        Parameters:
            idS: the search id in the database
            name: the search name
        """
        if askYesNo(mwstr.searchAskDelete % name):
            pbConfig.globalDb.deleteSearch(idS)
            self.createMenusAndToolBar()

    def searchAndReplace(self):
        """Open a search+replace form,
        then use the result to run the replace function
        """
        result = self.searchBiblio(replace=True)
        if not result:
            return
        self.runReplace(result)

    def runReplace(self, replace, newTab=None):
        """Run the `database.Entries.replace` function,
        then print some output in a dialog

        Parameter:
            replace: a tuple/list of 5 elements,
                as in the output of `self.searchBiblio`
            newTab (default None): if not None, the label of the new tab
        """
        regex = replace["regex"]
        fiOld = replace["fieOld"]
        old = replace["old"]
        if replace["double"]:
            fiNew = [replace["fieNew"], replace["fieNew1"]]
            new = [replace["new"], replace["new1"]]
        else:
            fiNew = [replace["fieNew"]]
            new = [replace["new"]]
        if old == "":
            infoMessage(mwstr.replaceEmptyStr)
            return
        if any(n == "" for n in new):
            if not askYesNo(mwstr.replaceEmptyStrAsk):
                return
        self._runInThread(
            Thread_replace,
            mwstr.replace,
            fiOld,
            fiNew,
            old,
            new,
            regex=regex,
            minProgress=0.0,
            stopFlag=True,
        )
        success, changed, failed = self.replaceResults
        LongInfoMessage(
            mwstr.replaceCompl.format(
                suc=len(success),
                ncha=len(changed),
                nfai=len(failed),
                cha=changed,
                fai=failed,
            )
        )
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.reloadMainContent(pBDB.bibs.fetchFromLast().lastFetched, newTab=newTab)
        QApplication.restoreOverrideCursor()

    def updateAllBibtexsAsk(self):
        """Same as updateAllBibtexs, but ask the values of
        `startFrom` and `force` before the execution
        """
        force = askYesNo(
            mwstr.forceUpdText,
            mwstr.forceUpdTitle,
        )
        text, out = askGenericText(
            mwstr.updINumText,
            mwstr.updINumTitle,
            self,
        )
        if not out:
            return
        try:
            startFrom = int(text)
        except ValueError:
            if askYesNo(mwstr.invalidIntAsk, mwstr.invalidEntry):
                startFrom = 0
            else:
                return
        self.updateAllBibtexs(startFrom, force=force)

    def updateAllBibtexs(
        self,
        startFrom=pbConfig.params["defaultUpdateFrom"],
        useEntries=None,
        force=False,
        reloadAll=False,
    ):
        """Use INSPIRE to obtain updated information of a list of papers
        and update their bibtex with the new data.
        Typically used to add journal information to arXiv papers.

        Parameters (see `physbiblio.database.Entries.searchOAIUpdates`):
            startFrom (default from the app settings): the index
                of the entry where to start from
            useEntries (default None): None (then use all)
                or a list of entries
            force (default False): if True, force the update
                also of entries which already have journal information
            reloadAll (default False): if True, completely reload
                the bibtex instead of updating it
                (may solve some format problems)
        """
        self.statusBarMessage(mwstr.updateStartFrom % startFrom)
        self._runInThread(
            Thread_updateAllBibtexs,
            mwstr.updateTitle,
            startFrom,
            useEntries=useEntries,
            force=force,
            reloadAll=reloadAll,
            minProgress=0.0,
            stopFlag=True,
        )
        self.refreshMainContent()

    def updateInspireInfo(self, bibkey, inspireID=None):
        """Use a thread to look for the INSPIRE ID of one or more papers
        and then use it to obtain more information
        (identifiers like DOI/arXiv, first appearance date, publication)

        Parameters:
            bibkey: the (list of) bibtex key of the entry
            inspireID (default None): the (list of) INSPIRE ID,
                if already known
        """
        self.statusBarMessage(mwstr.updateInfoStart)
        self._runInThread(
            Thread_updateInspireInfo,
            mwstr.updateInfo,
            bibkey,
            inspireID,
            minProgress=0.0,
            stopFlag=False,
        )
        self.refreshMainContent()

    def authorStats(self):
        """Ask the author name(s) and then
        use a thread to obtain the citation statistics
        for one or more authors using the INSPIRE-HEP database
        """
        authorName, out = askGenericText(
            mwstr.authorStNameAsk,
            mwstr.authorStNameTit,
            self,
        )
        if not out:
            return False
        else:
            authorName = str(authorName)
        if authorName == "":
            pBGUILogger.warning(mwstr.authorStEmptyName)
            return False
        if "[" in authorName:
            try:
                authorName = ast.literal_eval(authorName.strip())
            except (ValueError, SyntaxError):
                pBGUILogger.exception(mwstr.listSyntax)
                return False
        self.statusBarMessage(mwstr.authorStStart)

        self._runInThread(
            Thread_authorStats,
            mwstr.authorStatsTitle,
            authorName,
            minProgress=0.0,
            stopFlag=True,
        )

        if self.lastAuthorStats is None or len(self.lastAuthorStats["paLi"][0]) == 0:
            infoMessage(mwstr.importInspNoRes)
            return False
        self.lastAuthorStats["figs"] = pBStats.plotStats(author=True)
        aSP = AuthorStatsPlots(
            self.lastAuthorStats["figs"],
            title=mwstr.authorStStats % authorName,
            parent=self,
        )
        aSP.show()
        self.done()
        return True

    def getInspireCitationCount(self, inspireID=[]):
        """Use a thread to obtain the citation statistics
        of a paper using the INSPIRE-HEP database

        Parameter:
            inspireID: the ID of the paper in the INSPIRE database
        """
        if not isinstance(inspireID, list):
            inspireID = [inspireID]
        if inspireID == []:
            inspireID = [e["inspire"] for e in pBDB.bibs.getAll()]
        inspireID = [i for i in inspireID if i != "" and i is not None]
        self._runInThread(
            Thread_citationCount,
            mwstr.citCount,
            inspireID,
            minProgress=0.0,
            stopFlag=True,
        )
        self.done()

    def getInspireStats(self, inspireId):
        """Use a thread to obtain the citation statistics
        of a paper using the INSPIRE-HEP database

        Parameter:
            inspireId: the ID of the paper in the INSPIRE database
        """
        self._runInThread(
            Thread_paperStats,
            mwstr.paperStats,
            inspireId,
            minProgress=0.0,
            stopFlag=True,
        )
        if self.lastPaperStats is None:
            infoMessage(mwstr.paperStError)
            return False
        self.lastPaperStats["fig"] = pBStats.plotStats(paper=True)
        pSP = PaperStatsPlots(
            self.lastPaperStats["fig"],
            title=mwstr.paperStStats % inspireId,
            parent=self,
        )
        pSP.show()
        self.done()

    def inspireLoadAndInsert(self, doReload=True):
        """Ask a search string, then use inspire to import the entries
        which correspond, if unique results are obtained

        Parameter:
            doReload (default True): if True, reload
                the main entries list at the end
        """
        queryStr, out = askGenericText(
            mwstr.importInspAskStr,
            mwstr.queryStr,
            self,
        )
        if not out:
            return False
        if queryStr == "":
            pBGUILogger.warning(mwstr.emptyCantProceed)
            return False
        self.loadedAndInserted = []
        self.statusBarMessage(mwstr.importInspStarting)
        if "," in queryStr:
            try:
                queryStr = ast.literal_eval("[" + queryStr.strip() + "]")
            except (ValueError, SyntaxError):
                pBGUILogger.exception(mwstr.listSyntax)
                return False

        self._runInThread(
            Thread_loadAndInsert,
            mwstr.importInspTit,
            queryStr,
            minProgress=0.0,
            stopFlag=True,
            addMessage=mwstr.searching % queryStr,
        )

        if self.loadedAndInserted == []:
            infoMessage(mwstr.importInspNoRes)
            return False
        if doReload:
            self.reloadMainContent()
        return True

    def askCatsForEntries(self, entriesList):
        """Open a selection dialog for asking the categories
        for a given list of entries

        Parameter:
            entriesList: the list of entries to be used
        """
        for entry in entriesList:
            selectCats = CatsTreeWindow(
                parent=self,
                askCats=True,
                askForBib=entry,
                previous=[a[0] for a in pBDB.cats.getByEntry(entry)],
            )
            selectCats.exec_()
            if selectCats.result in ["Ok", "Exps"]:
                pBDB.catBib.insert(self.selectedCats, entry)
                self.statusBarMessage(mwstr.catInserted % entry)
            if selectCats.result == "Exps":
                selectExps = ExpsListWindow(parent=self, askExps=True, askForBib=entry)
                selectExps.exec_()
                if selectExps.result == "Ok":
                    pBDB.bibExp.insert(entry, self.selectedExps)
                    self.statusBarMessage(mwstr.expInserted % entry)

    def inspireLoadAndInsertWithCats(self):
        """Extend `self.inspireLoadAndInsert` to ask the categories
        to associate the entry with, if the import was successful
        """
        if (
            self.inspireLoadAndInsert(doReload=False)
            and len(self.loadedAndInserted) > 0
        ):
            for key in self.loadedAndInserted:
                pBDB.catBib.delete(pbConfig.params["defaultCategories"], key)
            self.askCatsForEntries(self.loadedAndInserted)
            self.reloadMainContent()

    def advancedImport(self):
        """Advanced import dialog.
        Open a dialog where you can select which method to use
        and insert the search string,
        then import a selection among the obtained results
        """
        adIm = AdvancedImportDialog()
        adIm.exec_()
        method = adIm.comboMethod.currentText().lower().replace("-", "")
        if method == "inspirehep":
            method = "inspire"
        if method == "adsnasa":
            if not self.checkAdsToken():
                return False
        string = adIm.searchStr.text().strip()
        db = bibtexparser.bibdatabase.BibDatabase()
        if adIm.result == True and string != "":
            QApplication.setOverrideCursor(Qt.WaitCursor)
            cont = physBiblioWeb.webSearch[method].retrieveUrlAll(string)
            if cont.strip() != "":
                elements = pBDB.bibs.readEntries(cont)
            else:
                elements = []
            found = {}
            for el in elements:
                if not isinstance(el["ID"], six.string_types) or el["ID"].strip() == "":
                    db.entries = [el]
                    entry = pbWriter.write(db)
                    pBLogger.warning(dbstr.Bibs.laiEmptyKey % entry)
                else:
                    try:
                        el["arxiv"] = el["eprint"]
                    except KeyError:
                        pass
                    exist = len(pBDB.bibs.getByBibkey(el["ID"], saveQuery=False)) > 0
                    for f in ["arxiv", "doi"]:
                        try:
                            exist = exist or (
                                el[f].strip() != ""
                                and len(
                                    pBDB.bibs.getAll(params={f: el[f]}, saveQuery=False)
                                )
                                > 0
                            )
                        except KeyError:
                            pBLogger.debug("KeyError '%s', entry: %s" % (f, el["ID"]))
                    found[el["ID"]] = {"bibpars": el, "exist": exist}
            QApplication.restoreOverrideCursor()
            if len(found) == 0:
                infoMessage(mwstr.noRes)
                return False
            if method == "adsnasa":
                self.statusBarMessage(physBiblioWeb.webSearch[method].getLimitInfo())

            selImpo = AdvancedImportSelect(found, self)
            selImpo.exec_()
            if selImpo.result == True:
                newFound = {}
                for ch in sorted(selImpo.selected):
                    if selImpo.selected[ch]:
                        newFound[ch] = found[ch]
                found = newFound
                inserted = []
                for key in sorted(found):
                    el = found[key]
                    db.entries = [el["bibpars"]]
                    entry = pbWriter.write(db)
                    data = pBDB.bibs.prepareInsert(entry)
                    if data == {"bibkey": ""}:
                        pBGUILogger.warning(mwstr.elementFailedBibtex % key)
                        continue
                    if method == "adsnasa":
                        data["ads"] = key
                    if not pBDB.bibs.insert(data):
                        pBGUILogger.warning(mwstr.elementFailed % key)
                        continue
                    try:
                        if method == "inspire":
                            eid = pBDB.bibs.updateInspireID(key)
                            pBDB.bibs.updateInfoFromOAI(eid)
                        elif method == "isbn":
                            pBDB.bibs.setBook(key)
                        pBLogger.info(mwstr.elementInserted % key)
                        inserted.append(key)
                    except Exception:
                        pBLogger.warning(mwstr.failedComplete % key, exc_info=True)
                self.statusBarMessage(mwstr.elementImported % (inserted))
                if selImpo.askCats.isChecked():
                    for key in inserted:
                        pBDB.catBib.delete(pbConfig.params["defaultCategories"], key)
                    self.askCatsForEntries(inserted)
            self.reloadMainContent()
        else:
            return False

    def cleanAllBibtexsAsk(self):
        """Use a thread to clean and reformat the bibtex entries.
        Ask the index of the entry where to start from,
        before proceeding
        """
        text, out = askGenericText(
            mwstr.cleBibStartAsk,
            mwstr.cleBibStartTit,
            self,
        )
        if not out:
            return
        try:
            startFrom = int(text)
        except ValueError:
            if askYesNo(
                mwstr.invalidIntAsk,
                mwstr.invalidEntry,
            ):
                startFrom = 0
            else:
                return
        self.cleanAllBibtexs(startFrom)

    def cleanAllBibtexs(self, startFrom=0, useEntries=None):
        """Use a thread to clean and reformat the bibtex entries

        Parameters:
            startFrom (default 0): the list index of the entry
                where to start from
            useEntries (default None): if not None, it must be a list
                of entries to be processed, otherwise the full database
                content will be used
        """
        self.statusBarMessage(mwstr.cleBibStart)
        self._runInThread(
            Thread_cleanAllBibtexs,
            mwstr.cleBib,
            startFrom,
            useEntries=useEntries,
            minProgress=0.0,
            stopFlag=True,
        )

    def findBadBibtexs(self, startFrom=0, useEntries=None):
        """Use a thread to scan the database for bad bibtex entries.
        If the user wants, a dialog for fixing each of them one by one
        may appear at the end of the search

        Parameters:
            startFrom (default 0): the list index of the entry
                where to start from
            useEntries (default None): if not None, it must be a list
                of entries to be processed, otherwise the full database
                content will be used
        """
        self.statusBarMessage(mwstr.cheBibStart)
        self.badBibtexs = []
        self._runInThread(
            Thread_findBadBibtexs,
            mwstr.cheBib,
            startFrom,
            useEntries=useEntries,
            minProgress=0.0,
            stopFlag=True,
        )
        if len(self.badBibtexs) > 0:
            if askYesNo(mwstr.cheBibFound % len(self.badBibtexs)):
                for bibkey in self.badBibtexs:
                    editBibtex(self, bibkey)
            else:
                infoMessage(mwstr.cheBibSumNoAct % ", ".join(self.badBibtexs))
        else:
            infoMessage(mwstr.cheBibNoInv)

    def infoFromArxiv(self, useEntries=None):
        """Use arXiv to obtain more information
        on a specific selection of entries

        Parameter:
            useEntries (default None): if not None, it must be a list
                of entries to be completed, otherwise the full database
                content will be used
        """
        iterator = useEntries
        if useEntries is None:
            pBDB.bibs.fetchAll(doFetch=False)
            iterator = pBDB.bibs.fetchCursor()
        askFieldsWin = FieldsFromArxiv()
        askFieldsWin.exec_()
        if askFieldsWin.result:
            self.statusBarMessage(mwstr.arxInStart)
            self._runInThread(
                Thread_fieldsArxiv,
                mwstr.arxIn,
                [e["bibkey"] for e in iterator],
                askFieldsWin.output,
                minProgress=0.0,
                stopFlag=True,
            )

    def browseDailyArxiv(self):
        """Browse daily news from arXiv after showing
        a dialog for asking the category,
        and import the selection of entries
        """
        bDA = DailyArxivDialog()
        bDA.exec_()
        cat = bDA.comboCat.currentText().lower()
        if bDA.result and cat != "":
            sub = bDA.comboSub.currentText()
            try:
                physBiblioWeb.webSearch["arxiv"].categories[cat]
            except KeyError:
                pBGUILogger.warning(mwstr.arxBrNoCat % cat)
                return False
            QApplication.setOverrideCursor(Qt.WaitCursor)
            content = physBiblioWeb.webSearch["arxiv"].arxivDaily(
                cat if sub == "--" else "%s.%s" % (cat, sub)
            )
            found = {}
            for el in content:
                el["type"] = ""
                if el["replacement"]:
                    el["type"] += "[replacement]"
                if el["cross"]:
                    el["type"] += "[cross-listed]"
                found[el["eprint"]] = {
                    "bibpars": el,
                    "exist": len(pBDB.bibs.getByBibkey(el["eprint"], saveQuery=False))
                    > 0,
                }
            if len(found) == 0:
                infoMessage(mwstr.noRes)
                return False

            QApplication.restoreOverrideCursor()
            selImpo = DailyArxivSelect(found, self)
            selImpo.abstractFormulas = AbstractFormulas
            selImpo.exec_()
            if selImpo.result == True:
                newFound = {}
                for ch in sorted(selImpo.selected):
                    if selImpo.selected[ch]:
                        newFound[ch] = found[ch]
                found = newFound
                self._runInThread(
                    Thread_importDailyArxiv, mwstr.arxIm, found, stopFlag=True
                )
                inserted, failed = self.importArXivResults
                self.statusBarMessage(
                    mwstr.elementImported.replace("\n", " ") % (inserted)
                )
                if selImpo.askCats.isChecked():
                    for key in inserted:
                        pBDB.catBib.delete(pbConfig.params["defaultCategories"], key)
                    self.askCatsForEntries(inserted)
            self.reloadMainContent()
        else:
            return False

    def sendMessage(self, message):
        """Show a simple infoMessage

        Parameter:
            message: the message content
        """
        infoMessage(message)

    def done(self):
        """Send a "done" message to the status bar"""
        self.statusBarMessage(mwstr.doneDD)

    def checkAdsToken(self):
        """Check that the ADS token is stored in the configuration"""
        while (
            not isinstance(pbConfig.params["ADSToken"], six.string_types)
        ) or pbConfig.params["ADSToken"].strip() == "":
            newkey, out = askGenericText(
                mwstr.askADSTokenText,
                mwstr.askADSTokenTitle,
            )
            if not out:
                return False
            if newkey.strip() != "":
                pBDB.config.insert("ADSToken", newkey)
                pBDB.commit()
                pbConfig.readConfig()
                return True
        return True


if __name__ == "__main__":
    try:
        myApp = QApplication(sys.argv)
        myApp.setAttribute(Qt.AA_X11InitThreads)
        myWindow = MainWindow()
        myWindow.show()
        sys.exit(myApp.exec_())
    except NameError:
        print("NameError:", sys.exc_info()[1])
    except SystemExit:
        print(mwstr.closeMainW)
    except Exception:
        print(sys.exc_info()[1])
