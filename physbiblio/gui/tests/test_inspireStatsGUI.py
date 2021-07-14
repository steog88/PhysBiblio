#!/usr/bin/env python
"""Test file for the physbiblio.gui.inspireStatsGUI module.

This file is part of the physbiblio package.
"""
import datetime
import logging
import os
import sys
import time
import traceback

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from PySide2.QtCore import QPoint, Qt
from PySide2.QtGui import QFont
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QLineEdit, QMessageBox, QWidget

if sys.version_info[0] < 3:
    import unittest2 as unittest
    from mock import patch
else:
    import unittest
    from unittest.mock import patch

try:
    from physbiblio.gui.basicDialogs import askDirName
    from physbiblio.gui.commonClasses import PBLabel
    from physbiblio.gui.inspireStatsGUI import *
    from physbiblio.gui.setuptests import *
    from physbiblio.setuptests import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())

testData = {  # data as of 180713
    "allLi": [
        [
            datetime.datetime(2015, 2, 3, 4, 55, 48),
            datetime.datetime(2015, 2, 23, 4, 40, 55),
            datetime.datetime(2015, 4, 29, 4, 46, 57),
            datetime.datetime(2015, 7, 2, 4, 44, 49),
            datetime.datetime(2015, 7, 22, 5, 19, 4),
            datetime.datetime(2015, 7, 30, 4, 49, 20),
            datetime.datetime(2015, 8, 4, 5, 2, 28),
            datetime.datetime(2015, 8, 5, 4, 59, 22),
            datetime.datetime(2015, 8, 12, 4, 32, 1),
            datetime.datetime(2015, 8, 13, 4, 38, 37),
            datetime.datetime(2015, 10, 5, 4, 33, 29),
            datetime.datetime(2015, 10, 6, 4, 50, 9),
            datetime.datetime(2015, 10, 21, 4, 40, 31),
            datetime.datetime(2015, 10, 23, 4, 35, 26),
            datetime.datetime(2015, 11, 13, 4, 51, 44),
            datetime.datetime(2015, 11, 13, 4, 51, 44),
            datetime.datetime(2015, 12, 8, 4, 58, 55),
            datetime.datetime(2015, 12, 15, 5, 1, 2),
            datetime.datetime(2015, 12, 16, 4, 35, 24),
            datetime.datetime(2015, 12, 16, 4, 35, 24),
            datetime.datetime(2015, 12, 16, 4, 35, 24),
            datetime.datetime(2015, 12, 21, 4, 42, 38),
            datetime.datetime(2016, 1, 6, 17, 35, 22),
            datetime.datetime(2016, 1, 8, 4, 28, 30),
            datetime.datetime(2016, 1, 21, 4, 39, 38),
            datetime.datetime(2016, 1, 25, 4, 35, 32),
            datetime.datetime(2016, 1, 28, 5, 3, 4),
            datetime.datetime(2016, 1, 29, 4, 31, 28),
            datetime.datetime(2016, 2, 2, 4, 43, 46),
            datetime.datetime(2016, 2, 4, 4, 43, 41),
            datetime.datetime(2016, 2, 4, 4, 43, 41),
            datetime.datetime(2016, 2, 5, 4, 37, 38),
            datetime.datetime(2016, 2, 6, 22, 25, 29),
            datetime.datetime(2016, 2, 6, 22, 25, 29),
            datetime.datetime(2016, 2, 18, 8, 9, 20),
            datetime.datetime(2016, 2, 19, 4, 34, 28),
            datetime.datetime(2016, 3, 14, 4, 36, 35),
            datetime.datetime(2016, 3, 18, 5, 9, 17),
            datetime.datetime(2016, 3, 31, 5, 23, 57),
            datetime.datetime(2016, 4, 11, 4, 56, 41),
            datetime.datetime(2016, 5, 13, 6, 18, 45),
            datetime.datetime(2016, 5, 13, 6, 18, 45),
            datetime.datetime(2016, 5, 16, 4, 50, 43),
            datetime.datetime(2016, 5, 17, 6, 31, 4),
            datetime.datetime(2016, 5, 19, 6, 9, 9),
            datetime.datetime(2016, 5, 19, 6, 9, 9),
            datetime.datetime(2016, 5, 19, 6, 9, 9),
            datetime.datetime(2016, 6, 1, 6, 24, 14),
            datetime.datetime(2016, 6, 9, 7, 29, 11),
            datetime.datetime(2016, 6, 13, 16, 50, 37),
            datetime.datetime(2016, 6, 13, 16, 50, 42),
            datetime.datetime(2016, 6, 13, 16, 50, 44),
            datetime.datetime(2016, 6, 13, 16, 51, 6),
            datetime.datetime(2016, 6, 13, 16, 53, 19),
            datetime.datetime(2016, 6, 20, 17, 59, 30),
            datetime.datetime(2016, 6, 20, 17, 59, 30),
            datetime.datetime(2016, 6, 22, 6, 3, 49),
            datetime.datetime(2016, 6, 24, 6, 9, 31),
            datetime.datetime(2016, 6, 27, 4, 54, 37),
            datetime.datetime(2016, 6, 30, 6, 19, 50),
            datetime.datetime(2016, 7, 1, 7, 10, 18),
            datetime.datetime(2016, 7, 4, 4, 50, 54),
            datetime.datetime(2016, 7, 6, 12, 6, 22),
            datetime.datetime(2016, 7, 6, 12, 6, 24),
            datetime.datetime(2016, 7, 6, 12, 6, 24),
            datetime.datetime(2016, 7, 6, 12, 6, 24),
            datetime.datetime(2016, 7, 20, 6, 9, 21),
            datetime.datetime(2016, 7, 28, 7, 13, 21),
            datetime.datetime(2016, 8, 16, 6, 33, 22),
            datetime.datetime(2016, 9, 8, 9, 31, 18),
            datetime.datetime(2016, 9, 16, 5, 42, 25),
            datetime.datetime(2016, 9, 16, 5, 42, 25),
            datetime.datetime(2016, 9, 16, 5, 42, 25),
            datetime.datetime(2016, 9, 16, 5, 42, 25),
            datetime.datetime(2016, 9, 27, 19, 45, 54),
            datetime.datetime(2016, 10, 6, 6, 26, 46),
            datetime.datetime(2016, 10, 11, 6, 9, 7),
            datetime.datetime(2016, 10, 18, 6, 4, 42),
            datetime.datetime(2016, 10, 28, 6, 20, 32),
            datetime.datetime(2016, 10, 31, 4, 59, 9),
            datetime.datetime(2016, 11, 22, 20, 51, 29),
            datetime.datetime(2016, 11, 22, 20, 51, 29),
            datetime.datetime(2016, 11, 22, 20, 51, 29),
            datetime.datetime(2016, 11, 22, 20, 51, 29),
            datetime.datetime(2016, 11, 28, 5, 18, 24),
            datetime.datetime(2016, 12, 1, 20, 45, 52),
            datetime.datetime(2016, 12, 21, 6, 30, 52),
            datetime.datetime(2016, 12, 23, 6, 10, 10),
            datetime.datetime(2017, 1, 13, 5, 53, 56),
            datetime.datetime(2017, 1, 27, 14, 51, 36),
            datetime.datetime(2017, 2, 9, 6, 27, 53),
            datetime.datetime(2017, 2, 9, 14, 27, 40),
            datetime.datetime(2017, 2, 15, 6, 5, 51),
            datetime.datetime(2017, 3, 1, 6, 22, 39),
            datetime.datetime(2017, 3, 2, 6, 24, 37),
            datetime.datetime(2017, 3, 2, 6, 24, 37),
            datetime.datetime(2017, 3, 3, 5, 29, 31),
            datetime.datetime(2017, 3, 3, 5, 29, 44),
            datetime.datetime(2017, 3, 3, 5, 29, 44),
            datetime.datetime(2017, 3, 3, 5, 29, 44),
            datetime.datetime(2017, 3, 3, 5, 29, 44),
            datetime.datetime(2017, 3, 14, 5, 48, 47),
            datetime.datetime(2017, 3, 17, 22, 39, 50),
            datetime.datetime(2017, 3, 24, 23, 37, 12),
            datetime.datetime(2017, 4, 4, 6, 25, 49),
            datetime.datetime(2017, 4, 18, 5, 41, 28),
            datetime.datetime(2017, 4, 21, 6, 33, 28),
            datetime.datetime(2017, 4, 26, 15, 48, 2),
            datetime.datetime(2017, 4, 26, 15, 48, 3),
            datetime.datetime(2017, 5, 16, 6, 27, 4),
            datetime.datetime(2017, 6, 8, 6, 35, 8),
            datetime.datetime(2017, 6, 12, 14, 32, 15),
            datetime.datetime(2017, 6, 20, 6, 0, 51),
            datetime.datetime(2017, 6, 22, 6, 32, 35),
            datetime.datetime(2017, 6, 23, 12, 6, 58),
            datetime.datetime(2017, 6, 23, 12, 6, 58),
            datetime.datetime(2017, 6, 26, 15, 48, 6),
            datetime.datetime(2017, 6, 26, 15, 48, 6),
            datetime.datetime(2017, 6, 26, 15, 48, 6),
            datetime.datetime(2017, 6, 26, 15, 49, 52),
            datetime.datetime(2017, 6, 26, 15, 49, 52),
            datetime.datetime(2017, 6, 26, 15, 50, 18),
            datetime.datetime(2017, 6, 26, 15, 50, 26),
            datetime.datetime(2017, 6, 30, 5, 50, 25),
            datetime.datetime(2017, 7, 26, 6, 36, 10),
            datetime.datetime(2017, 7, 26, 6, 36, 10),
            datetime.datetime(2017, 8, 4, 6, 9, 39),
            datetime.datetime(2017, 8, 17, 6, 2, 28),
            datetime.datetime(2017, 9, 5, 5, 47, 10),
            datetime.datetime(2017, 10, 3, 7, 36, 7),
            datetime.datetime(2017, 10, 4, 17, 42, 56),
            datetime.datetime(2017, 10, 18, 7, 3, 39),
            datetime.datetime(2017, 10, 18, 7, 9, 51),
            datetime.datetime(2017, 10, 19, 6, 59, 44),
            datetime.datetime(2017, 10, 23, 5, 3, 34),
            datetime.datetime(2017, 10, 23, 5, 3, 34),
            datetime.datetime(2017, 10, 25, 17, 46, 1),
            datetime.datetime(2017, 10, 25, 17, 46, 1),
            datetime.datetime(2017, 10, 25, 17, 46, 1),
            datetime.datetime(2017, 10, 31, 6, 37, 57),
            datetime.datetime(2017, 10, 31, 6, 37, 57),
            datetime.datetime(2017, 11, 9, 7, 34, 7),
            datetime.datetime(2017, 11, 23, 15, 7, 31),
            datetime.datetime(2017, 11, 23, 15, 8, 15),
            datetime.datetime(2017, 11, 27, 14, 44, 16),
            datetime.datetime(2017, 12, 15, 11, 33, 17),
            datetime.datetime(2017, 12, 20, 6, 45, 40),
            datetime.datetime(2017, 12, 20, 6, 46, 3),
            datetime.datetime(2017, 12, 22, 6, 23, 1),
            datetime.datetime(2018, 1, 3, 15, 1, 31),
            datetime.datetime(2018, 1, 3, 15, 1, 38),
            datetime.datetime(2018, 1, 16, 5, 53, 9),
            datetime.datetime(2018, 1, 22, 3, 9, 25),
            datetime.datetime(2018, 1, 31, 12, 44, 55),
            datetime.datetime(2018, 2, 6, 4, 35, 36),
            datetime.datetime(2018, 2, 6, 4, 35, 36),
            datetime.datetime(2018, 2, 6, 4, 35, 36),
            datetime.datetime(2018, 2, 6, 16, 3, 42),
            datetime.datetime(2018, 2, 15, 5, 49, 24),
            datetime.datetime(2018, 2, 15, 16, 54, 24),
            datetime.datetime(2018, 2, 19, 3, 42, 2),
            datetime.datetime(2018, 3, 27, 16, 43, 36),
            datetime.datetime(2018, 4, 4, 12, 26, 18),
            datetime.datetime(2018, 4, 4, 12, 26, 18),
            datetime.datetime(2018, 4, 7, 11, 27, 59),
            datetime.datetime(2018, 4, 9, 3, 44, 15),
            datetime.datetime(2018, 4, 9, 16, 34, 39),
            datetime.datetime(2018, 4, 9, 16, 34, 39),
            datetime.datetime(2018, 4, 9, 16, 34, 39),
            datetime.datetime(2018, 4, 11, 5, 48, 5),
            datetime.datetime(2018, 4, 26, 4, 16, 18),
            datetime.datetime(2018, 4, 26, 4, 20, 21),
            datetime.datetime(2018, 4, 30, 20, 33, 44),
            datetime.datetime(2018, 5, 24, 5, 29, 22),
            datetime.datetime(2018, 5, 30, 4, 5, 11),
            datetime.datetime(2018, 5, 31, 4, 26, 42),
            datetime.datetime(2018, 6, 1, 3, 48, 35),
            datetime.datetime(2018, 6, 7, 5, 19, 4),
            datetime.datetime(2018, 6, 11, 14, 0),
            datetime.datetime(2018, 6, 29, 4, 38, 51),
            datetime.datetime(2018, 6, 29, 4, 38, 51),
        ],
        [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            35,
            36,
            37,
            38,
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77,
            78,
            79,
            80,
            81,
            82,
            83,
            84,
            85,
            86,
            87,
            88,
            89,
            90,
            91,
            92,
            93,
            94,
            95,
            96,
            97,
            98,
            99,
            100,
            101,
            102,
            103,
            104,
            105,
            106,
            107,
            108,
            109,
            110,
            111,
            112,
            113,
            114,
            115,
            116,
            117,
            118,
            119,
            120,
            121,
            122,
            123,
            124,
            125,
            126,
            127,
            128,
            129,
            130,
            131,
            132,
            133,
            134,
            135,
            136,
            137,
            138,
            139,
            140,
            141,
            142,
            143,
            144,
            145,
            146,
            147,
            148,
            149,
            150,
            151,
            152,
            153,
            154,
            155,
            156,
            157,
            158,
            159,
            160,
            161,
            162,
            163,
            164,
            165,
            166,
            167,
            168,
            169,
            170,
            171,
            172,
            173,
            174,
            175,
            176,
            177,
            178,
            179,
            180,
            181,
        ],
    ],
    "name": "E.M.Zavanin.1",
    "aI": {
        "1345462": {
            "date": datetime.datetime(2015, 2, 23, 4, 40, 55),
            "infoDict": {},
            "citingPapersList": [
                [datetime.datetime(2015, 2, 23, 4, 40, 55), datetime.date(2018, 7, 13)],
                [1, 1],
            ],
        },
        "1366180": {
            "date": datetime.datetime(2015, 5, 6, 4, 44, 44),
            "infoDict": {
                1404176: {"date": datetime.datetime(2015, 11, 13, 4, 51, 44)},
                1633444: {"date": datetime.datetime(2017, 10, 31, 6, 37, 57)},
                1632295: {"date": datetime.datetime(2017, 10, 25, 17, 46, 1)},
                1477039: {"date": datetime.datetime(2016, 7, 20, 6, 9, 21)},
                1409712: {"date": datetime.datetime(2015, 12, 16, 4, 35, 24)},
                1515697: {"date": datetime.datetime(2017, 3, 3, 5, 29, 44)},
                1486648: {"date": datetime.datetime(2016, 9, 16, 5, 42, 25)},
                1611578: {"date": datetime.datetime(2017, 7, 26, 6, 36, 10)},
                1680061: {"date": datetime.datetime(2018, 6, 29, 4, 38, 51)},
                1631806: {"date": datetime.datetime(2017, 10, 23, 5, 3, 34)},
                1419893: {"date": datetime.datetime(2016, 2, 6, 22, 25, 29)},
                1396169: {"date": datetime.datetime(2015, 10, 6, 4, 50, 9)},
                1413581: {"date": datetime.datetime(2016, 1, 6, 17, 35, 22)},
                1510991: {"date": datetime.datetime(2017, 1, 27, 14, 51, 36)},
                1458267: {"date": datetime.datetime(2016, 5, 13, 6, 18, 45)},
                1460832: {"date": datetime.datetime(2016, 5, 19, 6, 9, 9)},
                1468769: {"date": datetime.datetime(2016, 6, 13, 16, 50, 37)},
                1666660: {"date": datetime.datetime(2018, 4, 9, 16, 34, 39)},
                1385583: {"date": datetime.datetime(2015, 7, 30, 4, 49, 20)},
                1517173: {"date": datetime.datetime(2017, 3, 14, 5, 48, 47)},
                1499583: {"date": datetime.datetime(2016, 11, 22, 20, 51, 29)},
                1380604: {"date": datetime.datetime(2015, 7, 2, 4, 44, 49)},
            },
            "citingPapersList": [
                [
                    datetime.datetime(2015, 5, 6, 4, 44, 44),
                    datetime.datetime(2015, 7, 2, 4, 44, 49),
                    datetime.datetime(2015, 7, 30, 4, 49, 20),
                    datetime.datetime(2015, 10, 6, 4, 50, 9),
                    datetime.datetime(2015, 11, 13, 4, 51, 44),
                    datetime.datetime(2015, 12, 16, 4, 35, 24),
                    datetime.datetime(2016, 1, 6, 17, 35, 22),
                    datetime.datetime(2016, 2, 6, 22, 25, 29),
                    datetime.datetime(2016, 5, 13, 6, 18, 45),
                    datetime.datetime(2016, 5, 19, 6, 9, 9),
                    datetime.datetime(2016, 6, 13, 16, 50, 37),
                    datetime.datetime(2016, 7, 20, 6, 9, 21),
                    datetime.datetime(2016, 9, 16, 5, 42, 25),
                    datetime.datetime(2016, 11, 22, 20, 51, 29),
                    datetime.datetime(2017, 1, 27, 14, 51, 36),
                    datetime.datetime(2017, 3, 3, 5, 29, 44),
                    datetime.datetime(2017, 3, 14, 5, 48, 47),
                    datetime.datetime(2017, 7, 26, 6, 36, 10),
                    datetime.datetime(2017, 10, 23, 5, 3, 34),
                    datetime.datetime(2017, 10, 25, 17, 46, 1),
                    datetime.datetime(2017, 10, 31, 6, 37, 57),
                    datetime.datetime(2018, 4, 9, 16, 34, 39),
                    datetime.datetime(2018, 6, 29, 4, 38, 51),
                    datetime.date(2018, 7, 13),
                ],
                [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                    23,
                ],
            ],
        },
        "1460832": {
            "date": datetime.datetime(2016, 5, 19, 6, 9, 9),
            "infoDict": {
                1653132: {"date": datetime.datetime(2018, 2, 6, 4, 35, 36)},
                1515697: {"date": datetime.datetime(2017, 3, 3, 5, 29, 44)},
                1606514: {"date": datetime.datetime(2017, 6, 23, 12, 6, 58)},
                1486648: {"date": datetime.datetime(2016, 9, 16, 5, 42, 25)},
                1607385: {"date": datetime.datetime(2017, 6, 26, 15, 48, 6)},
                1499583: {"date": datetime.datetime(2016, 11, 22, 20, 51, 29)},
            },
            "citingPapersList": [
                [
                    datetime.datetime(2016, 5, 19, 6, 9, 9),
                    datetime.datetime(2016, 9, 16, 5, 42, 25),
                    datetime.datetime(2016, 11, 22, 20, 51, 29),
                    datetime.datetime(2017, 3, 3, 5, 29, 44),
                    datetime.datetime(2017, 6, 23, 12, 6, 58),
                    datetime.datetime(2017, 6, 26, 15, 48, 6),
                    datetime.datetime(2018, 2, 6, 4, 35, 36),
                    datetime.date(2018, 7, 13),
                ],
                [1, 2, 3, 4, 5, 6, 7, 7],
            ],
        },
        "1385583": {
            "date": datetime.datetime(2015, 7, 30, 4, 49, 20),
            "infoDict": {
                1614336: {"date": datetime.datetime(2017, 8, 4, 6, 9, 39)},
                1416194: {"date": datetime.datetime(2016, 1, 21, 4, 39, 38)},
                1471494: {"date": datetime.datetime(2016, 6, 22, 6, 3, 49)},
                1384111: {"date": datetime.datetime(2015, 7, 22, 5, 19, 4)},
                1414175: {"date": datetime.datetime(2016, 1, 8, 4, 28, 30)},
                1648161: {"date": datetime.datetime(2018, 1, 16, 5, 53, 9)},
                1589254: {"date": datetime.datetime(2017, 4, 4, 6, 25, 49)},
                1632295: {"date": datetime.datetime(2017, 10, 25, 17, 46, 1)},
                1644074: {"date": datetime.datetime(2017, 12, 20, 6, 45, 40)},
                1410604: {"date": datetime.datetime(2015, 12, 21, 4, 42, 38)},
                1644084: {"date": datetime.datetime(2017, 12, 20, 6, 46, 3)},
                1478202: {"date": datetime.datetime(2016, 7, 28, 7, 13, 21)},
                1631806: {"date": datetime.datetime(2017, 10, 23, 5, 3, 34)},
                1399360: {"date": datetime.datetime(2015, 10, 23, 4, 35, 26)},
                1466433: {"date": datetime.datetime(2016, 6, 1, 6, 24, 14)},
                1644613: {"date": datetime.datetime(2017, 12, 22, 6, 23, 1)},
                1599558: {"date": datetime.datetime(2017, 5, 16, 6, 27, 4)},
                1472072: {"date": datetime.datetime(2016, 6, 27, 4, 54, 37)},
                1418831: {"date": datetime.datetime(2016, 2, 2, 4, 43, 46)},
                1596600: {"date": datetime.datetime(2017, 4, 26, 15, 48, 2)},
                1473106: {"date": datetime.datetime(2016, 7, 1, 7, 10, 18)},
                1649081: {"date": datetime.datetime(2018, 1, 22, 3, 9, 25)},
                1634993: {"date": datetime.datetime(2017, 11, 9, 7, 34, 7)},
                1458267: {"date": datetime.datetime(2016, 5, 13, 6, 18, 45)},
                1670749: {"date": datetime.datetime(2018, 4, 30, 20, 33, 44)},
                1631327: {"date": datetime.datetime(2017, 10, 19, 6, 59, 44)},
                1460832: {"date": datetime.datetime(2016, 5, 19, 6, 9, 9)},
                1485584: {"date": datetime.datetime(2016, 9, 8, 9, 31, 18)},
                1365092: {"date": datetime.datetime(2015, 4, 29, 4, 46, 57)},
                1653356: {"date": datetime.datetime(2018, 2, 6, 16, 3, 42)},
                1512558: {"date": datetime.datetime(2017, 2, 9, 6, 27, 53)},
                1677245: {"date": datetime.datetime(2018, 6, 11, 14, 0)},
                1419893: {"date": datetime.datetime(2016, 2, 6, 22, 25, 29)},
                1387478: {"date": datetime.datetime(2015, 8, 12, 4, 32, 1)},
                1605759: {"date": datetime.datetime(2017, 6, 20, 6, 0, 51)},
                1651329: {"date": datetime.datetime(2018, 1, 31, 12, 44, 55)},
                1387654: {"date": datetime.datetime(2015, 8, 13, 4, 38, 37)},
                1654935: {"date": datetime.datetime(2018, 2, 15, 5, 49, 24)},
                1633444: {"date": datetime.datetime(2017, 10, 31, 6, 37, 57)},
                1515693: {"date": datetime.datetime(2017, 3, 3, 5, 29, 31)},
                1429679: {"date": datetime.datetime(2016, 3, 18, 5, 9, 17)},
                1409712: {"date": datetime.datetime(2015, 12, 16, 4, 35, 24)},
                1515697: {"date": datetime.datetime(2017, 3, 3, 5, 29, 44)},
                1489592: {"date": datetime.datetime(2016, 10, 6, 6, 26, 46)},
                1596601: {"date": datetime.datetime(2017, 4, 26, 15, 48, 3)},
                1444895: {"date": datetime.datetime(2016, 4, 11, 4, 56, 41)},
                1680061: {"date": datetime.datetime(2018, 6, 29, 4, 38, 51)},
                1419638: {"date": datetime.datetime(2016, 2, 5, 4, 37, 38)},
                1494818: {"date": datetime.datetime(2016, 10, 28, 6, 20, 32)},
                1664211: {"date": datetime.datetime(2018, 3, 27, 16, 43, 36)},
                1607385: {"date": datetime.datetime(2017, 6, 26, 15, 48, 6)},
                1666270: {"date": datetime.datetime(2018, 4, 7, 11, 27, 59)},
                1606181: {"date": datetime.datetime(2017, 6, 22, 6, 32, 35)},
                1512674: {"date": datetime.datetime(2017, 2, 9, 14, 27, 40)},
                1488104: {"date": datetime.datetime(2016, 9, 27, 19, 45, 54)},
                1422059: {"date": datetime.datetime(2016, 2, 18, 8, 9, 20)},
                1471212: {"date": datetime.datetime(2016, 6, 20, 17, 59, 30)},
                1665780: {"date": datetime.datetime(2018, 4, 4, 12, 26, 18)},
                1399034: {"date": datetime.datetime(2015, 10, 21, 4, 40, 31)},
                1670017: {"date": datetime.datetime(2018, 4, 26, 4, 20, 21)},
                1676545: {"date": datetime.datetime(2018, 6, 7, 5, 19, 4)},
                1508822: {"date": datetime.datetime(2017, 1, 13, 5, 53, 56)},
                1607430: {"date": datetime.datetime(2017, 6, 26, 15, 49, 52)},
                1645831: {"date": datetime.datetime(2018, 1, 3, 15, 1, 31)},
                1458954: {"date": datetime.datetime(2016, 5, 16, 4, 50, 43)},
                1645835: {"date": datetime.datetime(2018, 1, 3, 15, 1, 38)},
                1386253: {"date": datetime.datetime(2015, 8, 4, 5, 2, 28)},
                1404176: {"date": datetime.datetime(2015, 11, 13, 4, 51, 44)},
                1468179: {"date": datetime.datetime(2016, 6, 9, 7, 29, 11)},
                1473304: {"date": datetime.datetime(2016, 7, 4, 4, 50, 54)},
                1637657: {"date": datetime.datetime(2017, 11, 23, 15, 8, 15)},
                1607450: {"date": datetime.datetime(2017, 6, 26, 15, 50, 18)},
                1473824: {"date": datetime.datetime(2016, 7, 6, 12, 6, 22)},
                1473825: {"date": datetime.datetime(2016, 7, 6, 12, 6, 24)},
                1473826: {"date": datetime.datetime(2016, 7, 6, 12, 6, 24)},
                1607461: {"date": datetime.datetime(2017, 6, 26, 15, 50, 26)},
                1655597: {"date": datetime.datetime(2018, 2, 19, 3, 42, 2)},
                1666660: {"date": datetime.datetime(2018, 4, 9, 16, 34, 39)},
                1638711: {"date": datetime.datetime(2017, 11, 27, 14, 44, 16)},
                1436472: {"date": datetime.datetime(2016, 3, 31, 5, 23, 57)},
                1611578: {"date": datetime.datetime(2017, 7, 26, 6, 36, 10)},
                1666363: {"date": datetime.datetime(2018, 4, 9, 3, 44, 15)},
                1515325: {"date": datetime.datetime(2017, 3, 1, 6, 22, 39)},
                1608002: {"date": datetime.datetime(2017, 6, 30, 5, 50, 25)},
                1637648: {"date": datetime.datetime(2017, 11, 23, 15, 7, 31)},
                1513295: {"date": datetime.datetime(2017, 2, 15, 6, 5, 51)},
                1486648: {"date": datetime.datetime(2016, 9, 16, 5, 42, 25)},
                1603103: {"date": datetime.datetime(2017, 6, 8, 6, 35, 8)},
                1616217: {"date": datetime.datetime(2017, 8, 17, 6, 2, 28)},
                1505628: {"date": datetime.datetime(2016, 12, 23, 6, 10, 10)},
                1471837: {"date": datetime.datetime(2016, 6, 24, 6, 9, 31)},
                1427294: {"date": datetime.datetime(2016, 3, 14, 4, 36, 35)},
                1492322: {"date": datetime.datetime(2016, 10, 18, 6, 4, 42)},
                1422182: {"date": datetime.datetime(2016, 2, 19, 4, 34, 28)},
                1468777: {"date": datetime.datetime(2016, 6, 13, 16, 50, 44)},
                1468781: {"date": datetime.datetime(2016, 6, 13, 16, 51, 6)},
                1606514: {"date": datetime.datetime(2017, 6, 23, 12, 6, 58)},
                1517942: {"date": datetime.datetime(2017, 3, 17, 22, 39, 50)},
                1670014: {"date": datetime.datetime(2018, 4, 26, 4, 16, 18)},
                1459073: {"date": datetime.datetime(2016, 5, 17, 6, 31, 4)},
                1395948: {"date": datetime.datetime(2015, 10, 5, 4, 33, 29)},
                1653132: {"date": datetime.datetime(2018, 2, 6, 4, 35, 36)},
                1655106: {"date": datetime.datetime(2018, 2, 15, 16, 54, 24)},
                1675757: {"date": datetime.datetime(2018, 6, 1, 3, 48, 35)},
                1674566: {"date": datetime.datetime(2018, 5, 24, 5, 29, 22)},
                1643424: {"date": datetime.datetime(2017, 12, 15, 11, 33, 17)},
                1417121: {"date": datetime.datetime(2016, 1, 28, 5, 3, 4)},
                1418146: {"date": datetime.datetime(2016, 1, 29, 4, 31, 28)},
                1628581: {"date": datetime.datetime(2017, 10, 4, 17, 42, 56)},
                1621417: {"date": datetime.datetime(2017, 9, 5, 5, 47, 10)},
                1505200: {"date": datetime.datetime(2016, 12, 21, 6, 30, 52)},
                1472945: {"date": datetime.datetime(2016, 6, 30, 6, 19, 50)},
                1591737: {"date": datetime.datetime(2017, 4, 18, 5, 41, 28)},
                1675707: {"date": datetime.datetime(2018, 5, 31, 4, 26, 42)},
                1468861: {"date": datetime.datetime(2016, 6, 13, 16, 53, 19)},
                1499583: {"date": datetime.datetime(2016, 11, 22, 20, 51, 29)},
                1593761: {"date": datetime.datetime(2017, 4, 21, 6, 33, 28)},
                1628104: {"date": datetime.datetime(2017, 10, 3, 7, 36, 7)},
                1631177: {"date": datetime.datetime(2017, 10, 18, 7, 3, 39)},
                1416652: {"date": datetime.datetime(2016, 1, 25, 4, 35, 32)},
                1342414: {"date": datetime.datetime(2015, 2, 3, 4, 55, 48)},
                1386454: {"date": datetime.datetime(2015, 8, 5, 4, 59, 22)},
                1519067: {"date": datetime.datetime(2017, 3, 24, 23, 37, 12)},
                1409530: {"date": datetime.datetime(2015, 12, 15, 5, 1, 2)},
                1631201: {"date": datetime.datetime(2017, 10, 18, 7, 9, 51)},
                1481189: {"date": datetime.datetime(2016, 8, 16, 6, 33, 22)},
                1501165: {"date": datetime.datetime(2016, 12, 1, 20, 45, 52)},
                1604078: {"date": datetime.datetime(2017, 6, 12, 14, 32, 15)},
                1667055: {"date": datetime.datetime(2018, 4, 11, 5, 48, 5)},
                1419248: {"date": datetime.datetime(2016, 2, 4, 4, 43, 41)},
                1500146: {"date": datetime.datetime(2016, 11, 28, 5, 18, 24)},
                1675257: {"date": datetime.datetime(2018, 5, 30, 4, 5, 11)},
                1515514: {"date": datetime.datetime(2017, 3, 2, 6, 24, 37)},
                1495038: {"date": datetime.datetime(2016, 10, 31, 4, 59, 9)},
            },
            "citingPapersList": [
                [
                    datetime.datetime(2015, 2, 3, 4, 55, 48),
                    datetime.datetime(2015, 4, 29, 4, 46, 57),
                    datetime.datetime(2015, 7, 22, 5, 19, 4),
                    datetime.datetime(2015, 7, 30, 4, 49, 20),
                    datetime.datetime(2015, 8, 4, 5, 2, 28),
                    datetime.datetime(2015, 8, 5, 4, 59, 22),
                    datetime.datetime(2015, 8, 12, 4, 32, 1),
                    datetime.datetime(2015, 8, 13, 4, 38, 37),
                    datetime.datetime(2015, 10, 5, 4, 33, 29),
                    datetime.datetime(2015, 10, 21, 4, 40, 31),
                    datetime.datetime(2015, 10, 23, 4, 35, 26),
                    datetime.datetime(2015, 11, 13, 4, 51, 44),
                    datetime.datetime(2015, 12, 15, 5, 1, 2),
                    datetime.datetime(2015, 12, 16, 4, 35, 24),
                    datetime.datetime(2015, 12, 21, 4, 42, 38),
                    datetime.datetime(2016, 1, 8, 4, 28, 30),
                    datetime.datetime(2016, 1, 21, 4, 39, 38),
                    datetime.datetime(2016, 1, 25, 4, 35, 32),
                    datetime.datetime(2016, 1, 28, 5, 3, 4),
                    datetime.datetime(2016, 1, 29, 4, 31, 28),
                    datetime.datetime(2016, 2, 2, 4, 43, 46),
                    datetime.datetime(2016, 2, 4, 4, 43, 41),
                    datetime.datetime(2016, 2, 5, 4, 37, 38),
                    datetime.datetime(2016, 2, 6, 22, 25, 29),
                    datetime.datetime(2016, 2, 18, 8, 9, 20),
                    datetime.datetime(2016, 2, 19, 4, 34, 28),
                    datetime.datetime(2016, 3, 14, 4, 36, 35),
                    datetime.datetime(2016, 3, 18, 5, 9, 17),
                    datetime.datetime(2016, 3, 31, 5, 23, 57),
                    datetime.datetime(2016, 4, 11, 4, 56, 41),
                    datetime.datetime(2016, 5, 13, 6, 18, 45),
                    datetime.datetime(2016, 5, 16, 4, 50, 43),
                    datetime.datetime(2016, 5, 17, 6, 31, 4),
                    datetime.datetime(2016, 5, 19, 6, 9, 9),
                    datetime.datetime(2016, 6, 1, 6, 24, 14),
                    datetime.datetime(2016, 6, 9, 7, 29, 11),
                    datetime.datetime(2016, 6, 13, 16, 50, 44),
                    datetime.datetime(2016, 6, 13, 16, 51, 6),
                    datetime.datetime(2016, 6, 13, 16, 53, 19),
                    datetime.datetime(2016, 6, 20, 17, 59, 30),
                    datetime.datetime(2016, 6, 22, 6, 3, 49),
                    datetime.datetime(2016, 6, 24, 6, 9, 31),
                    datetime.datetime(2016, 6, 27, 4, 54, 37),
                    datetime.datetime(2016, 6, 30, 6, 19, 50),
                    datetime.datetime(2016, 7, 1, 7, 10, 18),
                    datetime.datetime(2016, 7, 4, 4, 50, 54),
                    datetime.datetime(2016, 7, 6, 12, 6, 22),
                    datetime.datetime(2016, 7, 6, 12, 6, 24),
                    datetime.datetime(2016, 7, 6, 12, 6, 24),
                    datetime.datetime(2016, 7, 28, 7, 13, 21),
                    datetime.datetime(2016, 8, 16, 6, 33, 22),
                    datetime.datetime(2016, 9, 8, 9, 31, 18),
                    datetime.datetime(2016, 9, 16, 5, 42, 25),
                    datetime.datetime(2016, 9, 27, 19, 45, 54),
                    datetime.datetime(2016, 10, 6, 6, 26, 46),
                    datetime.datetime(2016, 10, 18, 6, 4, 42),
                    datetime.datetime(2016, 10, 28, 6, 20, 32),
                    datetime.datetime(2016, 10, 31, 4, 59, 9),
                    datetime.datetime(2016, 11, 22, 20, 51, 29),
                    datetime.datetime(2016, 11, 28, 5, 18, 24),
                    datetime.datetime(2016, 12, 1, 20, 45, 52),
                    datetime.datetime(2016, 12, 21, 6, 30, 52),
                    datetime.datetime(2016, 12, 23, 6, 10, 10),
                    datetime.datetime(2017, 1, 13, 5, 53, 56),
                    datetime.datetime(2017, 2, 9, 6, 27, 53),
                    datetime.datetime(2017, 2, 9, 14, 27, 40),
                    datetime.datetime(2017, 2, 15, 6, 5, 51),
                    datetime.datetime(2017, 3, 1, 6, 22, 39),
                    datetime.datetime(2017, 3, 2, 6, 24, 37),
                    datetime.datetime(2017, 3, 3, 5, 29, 31),
                    datetime.datetime(2017, 3, 3, 5, 29, 44),
                    datetime.datetime(2017, 3, 17, 22, 39, 50),
                    datetime.datetime(2017, 3, 24, 23, 37, 12),
                    datetime.datetime(2017, 4, 4, 6, 25, 49),
                    datetime.datetime(2017, 4, 18, 5, 41, 28),
                    datetime.datetime(2017, 4, 21, 6, 33, 28),
                    datetime.datetime(2017, 4, 26, 15, 48, 2),
                    datetime.datetime(2017, 4, 26, 15, 48, 3),
                    datetime.datetime(2017, 5, 16, 6, 27, 4),
                    datetime.datetime(2017, 6, 8, 6, 35, 8),
                    datetime.datetime(2017, 6, 12, 14, 32, 15),
                    datetime.datetime(2017, 6, 20, 6, 0, 51),
                    datetime.datetime(2017, 6, 22, 6, 32, 35),
                    datetime.datetime(2017, 6, 23, 12, 6, 58),
                    datetime.datetime(2017, 6, 26, 15, 48, 6),
                    datetime.datetime(2017, 6, 26, 15, 49, 52),
                    datetime.datetime(2017, 6, 26, 15, 50, 18),
                    datetime.datetime(2017, 6, 26, 15, 50, 26),
                    datetime.datetime(2017, 6, 30, 5, 50, 25),
                    datetime.datetime(2017, 7, 26, 6, 36, 10),
                    datetime.datetime(2017, 8, 4, 6, 9, 39),
                    datetime.datetime(2017, 8, 17, 6, 2, 28),
                    datetime.datetime(2017, 9, 5, 5, 47, 10),
                    datetime.datetime(2017, 10, 3, 7, 36, 7),
                    datetime.datetime(2017, 10, 4, 17, 42, 56),
                    datetime.datetime(2017, 10, 18, 7, 3, 39),
                    datetime.datetime(2017, 10, 18, 7, 9, 51),
                    datetime.datetime(2017, 10, 19, 6, 59, 44),
                    datetime.datetime(2017, 10, 23, 5, 3, 34),
                    datetime.datetime(2017, 10, 25, 17, 46, 1),
                    datetime.datetime(2017, 10, 31, 6, 37, 57),
                    datetime.datetime(2017, 11, 9, 7, 34, 7),
                    datetime.datetime(2017, 11, 23, 15, 7, 31),
                    datetime.datetime(2017, 11, 23, 15, 8, 15),
                    datetime.datetime(2017, 11, 27, 14, 44, 16),
                    datetime.datetime(2017, 12, 15, 11, 33, 17),
                    datetime.datetime(2017, 12, 20, 6, 45, 40),
                    datetime.datetime(2017, 12, 20, 6, 46, 3),
                    datetime.datetime(2017, 12, 22, 6, 23, 1),
                    datetime.datetime(2018, 1, 3, 15, 1, 31),
                    datetime.datetime(2018, 1, 3, 15, 1, 38),
                    datetime.datetime(2018, 1, 16, 5, 53, 9),
                    datetime.datetime(2018, 1, 22, 3, 9, 25),
                    datetime.datetime(2018, 1, 31, 12, 44, 55),
                    datetime.datetime(2018, 2, 6, 4, 35, 36),
                    datetime.datetime(2018, 2, 6, 16, 3, 42),
                    datetime.datetime(2018, 2, 15, 5, 49, 24),
                    datetime.datetime(2018, 2, 15, 16, 54, 24),
                    datetime.datetime(2018, 2, 19, 3, 42, 2),
                    datetime.datetime(2018, 3, 27, 16, 43, 36),
                    datetime.datetime(2018, 4, 4, 12, 26, 18),
                    datetime.datetime(2018, 4, 7, 11, 27, 59),
                    datetime.datetime(2018, 4, 9, 3, 44, 15),
                    datetime.datetime(2018, 4, 9, 16, 34, 39),
                    datetime.datetime(2018, 4, 11, 5, 48, 5),
                    datetime.datetime(2018, 4, 26, 4, 16, 18),
                    datetime.datetime(2018, 4, 26, 4, 20, 21),
                    datetime.datetime(2018, 4, 30, 20, 33, 44),
                    datetime.datetime(2018, 5, 24, 5, 29, 22),
                    datetime.datetime(2018, 5, 30, 4, 5, 11),
                    datetime.datetime(2018, 5, 31, 4, 26, 42),
                    datetime.datetime(2018, 6, 1, 3, 48, 35),
                    datetime.datetime(2018, 6, 7, 5, 19, 4),
                    datetime.datetime(2018, 6, 11, 14, 0),
                    datetime.datetime(2018, 6, 29, 4, 38, 51),
                    datetime.date(2018, 7, 13),
                ],
                [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                    24,
                    25,
                    26,
                    27,
                    28,
                    29,
                    30,
                    31,
                    32,
                    33,
                    34,
                    35,
                    36,
                    37,
                    38,
                    39,
                    40,
                    41,
                    42,
                    43,
                    44,
                    45,
                    46,
                    47,
                    48,
                    49,
                    50,
                    51,
                    52,
                    53,
                    54,
                    55,
                    56,
                    57,
                    58,
                    59,
                    60,
                    61,
                    62,
                    63,
                    64,
                    65,
                    66,
                    67,
                    68,
                    69,
                    70,
                    71,
                    72,
                    73,
                    74,
                    75,
                    76,
                    77,
                    78,
                    79,
                    80,
                    81,
                    82,
                    83,
                    84,
                    85,
                    86,
                    87,
                    88,
                    89,
                    90,
                    91,
                    92,
                    93,
                    94,
                    95,
                    96,
                    97,
                    98,
                    99,
                    100,
                    101,
                    102,
                    103,
                    104,
                    105,
                    106,
                    107,
                    108,
                    109,
                    110,
                    111,
                    112,
                    113,
                    114,
                    115,
                    116,
                    117,
                    118,
                    119,
                    120,
                    121,
                    122,
                    123,
                    124,
                    125,
                    126,
                    127,
                    128,
                    129,
                    130,
                    131,
                    132,
                    133,
                    134,
                    135,
                    135,
                ],
            ],
        },
        "1404176": {
            "date": datetime.datetime(2015, 11, 13, 4, 51, 44),
            "infoDict": {1408518: {"date": datetime.datetime(2015, 12, 8, 4, 58, 55)}},
            "citingPapersList": [
                [
                    datetime.datetime(2015, 11, 13, 4, 51, 44),
                    datetime.datetime(2015, 12, 8, 4, 58, 55),
                    datetime.date(2018, 7, 13),
                ],
                [1, 2, 2],
            ],
        },
        "1229039": {
            "date": datetime.datetime(2013, 4, 22, 4, 52, 23),
            "infoDict": {1345462: {"date": datetime.datetime(2015, 2, 23, 4, 40, 55)}},
            "citingPapersList": [
                [
                    datetime.datetime(2013, 4, 22, 4, 52, 23),
                    datetime.datetime(2015, 2, 23, 4, 40, 55),
                    datetime.date(2018, 7, 13),
                ],
                [1, 2, 2],
            ],
        },
        "1387736": {
            "date": datetime.datetime(2015, 8, 14, 4, 34, 30),
            "infoDict": {
                1460832: {"date": datetime.datetime(2016, 5, 19, 6, 9, 9)},
                1419248: {"date": datetime.datetime(2016, 2, 4, 4, 43, 41)},
                1473826: {"date": datetime.datetime(2016, 7, 6, 12, 6, 24)},
                1666660: {"date": datetime.datetime(2018, 4, 9, 16, 34, 39)},
                1468773: {"date": datetime.datetime(2016, 6, 13, 16, 50, 42)},
                1607430: {"date": datetime.datetime(2017, 6, 26, 15, 49, 52)},
                1632295: {"date": datetime.datetime(2017, 10, 25, 17, 46, 1)},
                1653132: {"date": datetime.datetime(2018, 2, 6, 4, 35, 36)},
                1471212: {"date": datetime.datetime(2016, 6, 20, 17, 59, 30)},
                1409712: {"date": datetime.datetime(2015, 12, 16, 4, 35, 24)},
                1515697: {"date": datetime.datetime(2017, 3, 3, 5, 29, 44)},
                1490867: {"date": datetime.datetime(2016, 10, 11, 6, 9, 7)},
                1665780: {"date": datetime.datetime(2018, 4, 4, 12, 26, 18)},
                1486648: {"date": datetime.datetime(2016, 9, 16, 5, 42, 25)},
                1607385: {"date": datetime.datetime(2017, 6, 26, 15, 48, 6)},
                1515514: {"date": datetime.datetime(2017, 3, 2, 6, 24, 37)},
                1499583: {"date": datetime.datetime(2016, 11, 22, 20, 51, 29)},
            },
            "citingPapersList": [
                [
                    datetime.datetime(2015, 8, 14, 4, 34, 30),
                    datetime.datetime(2015, 12, 16, 4, 35, 24),
                    datetime.datetime(2016, 2, 4, 4, 43, 41),
                    datetime.datetime(2016, 5, 19, 6, 9, 9),
                    datetime.datetime(2016, 6, 13, 16, 50, 42),
                    datetime.datetime(2016, 6, 20, 17, 59, 30),
                    datetime.datetime(2016, 7, 6, 12, 6, 24),
                    datetime.datetime(2016, 9, 16, 5, 42, 25),
                    datetime.datetime(2016, 10, 11, 6, 9, 7),
                    datetime.datetime(2016, 11, 22, 20, 51, 29),
                    datetime.datetime(2017, 3, 2, 6, 24, 37),
                    datetime.datetime(2017, 3, 3, 5, 29, 44),
                    datetime.datetime(2017, 6, 26, 15, 48, 6),
                    datetime.datetime(2017, 6, 26, 15, 49, 52),
                    datetime.datetime(2017, 10, 25, 17, 46, 1),
                    datetime.datetime(2018, 2, 6, 4, 35, 36),
                    datetime.datetime(2018, 4, 4, 12, 26, 18),
                    datetime.datetime(2018, 4, 9, 16, 34, 39),
                    datetime.date(2018, 7, 13),
                ],
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 18],
            ],
        },
        "1519902": {
            "date": datetime.datetime(2017, 3, 29, 11, 29, 12),
            "infoDict": {},
            "citingPapersList": [
                [
                    datetime.datetime(2017, 3, 29, 11, 29, 12),
                    datetime.date(2018, 7, 13),
                ],
                [1, 1],
            ],
        },
    },
    "h": 4,
    "paLi": [
        [
            datetime.datetime(2013, 4, 22, 4, 52, 23),
            datetime.datetime(2015, 2, 23, 4, 40, 55),
            datetime.datetime(2015, 5, 6, 4, 44, 44),
            datetime.datetime(2015, 7, 30, 4, 49, 20),
            datetime.datetime(2015, 8, 14, 4, 34, 30),
            datetime.datetime(2015, 11, 13, 4, 51, 44),
            datetime.datetime(2016, 5, 19, 6, 9, 9),
            datetime.datetime(2017, 3, 29, 11, 29, 12),
        ],
        [1, 2, 3, 4, 5, 6, 7, 8],
    ],
    "meanLi": [
        [
            datetime.datetime(2015, 2, 3, 4, 55, 48),
            datetime.datetime(2015, 2, 23, 4, 40, 55),
            datetime.datetime(2015, 4, 29, 4, 46, 57),
            datetime.datetime(2015, 7, 2, 4, 44, 49),
            datetime.datetime(2015, 7, 22, 5, 19, 4),
            datetime.datetime(2015, 7, 30, 4, 49, 20),
            datetime.datetime(2015, 8, 4, 5, 2, 28),
            datetime.datetime(2015, 8, 5, 4, 59, 22),
            datetime.datetime(2015, 8, 12, 4, 32, 1),
            datetime.datetime(2015, 8, 13, 4, 38, 37),
            datetime.datetime(2015, 10, 5, 4, 33, 29),
            datetime.datetime(2015, 10, 6, 4, 50, 9),
            datetime.datetime(2015, 10, 21, 4, 40, 31),
            datetime.datetime(2015, 10, 23, 4, 35, 26),
            datetime.datetime(2015, 11, 13, 4, 51, 44),
            datetime.datetime(2015, 11, 13, 4, 51, 44),
            datetime.datetime(2015, 12, 8, 4, 58, 55),
            datetime.datetime(2015, 12, 15, 5, 1, 2),
            datetime.datetime(2015, 12, 16, 4, 35, 24),
            datetime.datetime(2015, 12, 16, 4, 35, 24),
            datetime.datetime(2015, 12, 16, 4, 35, 24),
            datetime.datetime(2015, 12, 21, 4, 42, 38),
            datetime.datetime(2016, 1, 6, 17, 35, 22),
            datetime.datetime(2016, 1, 8, 4, 28, 30),
            datetime.datetime(2016, 1, 21, 4, 39, 38),
            datetime.datetime(2016, 1, 25, 4, 35, 32),
            datetime.datetime(2016, 1, 28, 5, 3, 4),
            datetime.datetime(2016, 1, 29, 4, 31, 28),
            datetime.datetime(2016, 2, 2, 4, 43, 46),
            datetime.datetime(2016, 2, 4, 4, 43, 41),
            datetime.datetime(2016, 2, 4, 4, 43, 41),
            datetime.datetime(2016, 2, 5, 4, 37, 38),
            datetime.datetime(2016, 2, 6, 22, 25, 29),
            datetime.datetime(2016, 2, 6, 22, 25, 29),
            datetime.datetime(2016, 2, 18, 8, 9, 20),
            datetime.datetime(2016, 2, 19, 4, 34, 28),
            datetime.datetime(2016, 3, 14, 4, 36, 35),
            datetime.datetime(2016, 3, 18, 5, 9, 17),
            datetime.datetime(2016, 3, 31, 5, 23, 57),
            datetime.datetime(2016, 4, 11, 4, 56, 41),
            datetime.datetime(2016, 5, 13, 6, 18, 45),
            datetime.datetime(2016, 5, 13, 6, 18, 45),
            datetime.datetime(2016, 5, 16, 4, 50, 43),
            datetime.datetime(2016, 5, 17, 6, 31, 4),
            datetime.datetime(2016, 5, 19, 6, 9, 9),
            datetime.datetime(2016, 5, 19, 6, 9, 9),
            datetime.datetime(2016, 5, 19, 6, 9, 9),
            datetime.datetime(2016, 6, 1, 6, 24, 14),
            datetime.datetime(2016, 6, 9, 7, 29, 11),
            datetime.datetime(2016, 6, 13, 16, 50, 37),
            datetime.datetime(2016, 6, 13, 16, 50, 42),
            datetime.datetime(2016, 6, 13, 16, 50, 44),
            datetime.datetime(2016, 6, 13, 16, 51, 6),
            datetime.datetime(2016, 6, 13, 16, 53, 19),
            datetime.datetime(2016, 6, 20, 17, 59, 30),
            datetime.datetime(2016, 6, 20, 17, 59, 30),
            datetime.datetime(2016, 6, 22, 6, 3, 49),
            datetime.datetime(2016, 6, 24, 6, 9, 31),
            datetime.datetime(2016, 6, 27, 4, 54, 37),
            datetime.datetime(2016, 6, 30, 6, 19, 50),
            datetime.datetime(2016, 7, 1, 7, 10, 18),
            datetime.datetime(2016, 7, 4, 4, 50, 54),
            datetime.datetime(2016, 7, 6, 12, 6, 22),
            datetime.datetime(2016, 7, 6, 12, 6, 24),
            datetime.datetime(2016, 7, 6, 12, 6, 24),
            datetime.datetime(2016, 7, 6, 12, 6, 24),
            datetime.datetime(2016, 7, 20, 6, 9, 21),
            datetime.datetime(2016, 7, 28, 7, 13, 21),
            datetime.datetime(2016, 8, 16, 6, 33, 22),
            datetime.datetime(2016, 9, 8, 9, 31, 18),
            datetime.datetime(2016, 9, 16, 5, 42, 25),
            datetime.datetime(2016, 9, 16, 5, 42, 25),
            datetime.datetime(2016, 9, 16, 5, 42, 25),
            datetime.datetime(2016, 9, 16, 5, 42, 25),
            datetime.datetime(2016, 9, 27, 19, 45, 54),
            datetime.datetime(2016, 10, 6, 6, 26, 46),
            datetime.datetime(2016, 10, 11, 6, 9, 7),
            datetime.datetime(2016, 10, 18, 6, 4, 42),
            datetime.datetime(2016, 10, 28, 6, 20, 32),
            datetime.datetime(2016, 10, 31, 4, 59, 9),
            datetime.datetime(2016, 11, 22, 20, 51, 29),
            datetime.datetime(2016, 11, 22, 20, 51, 29),
            datetime.datetime(2016, 11, 22, 20, 51, 29),
            datetime.datetime(2016, 11, 22, 20, 51, 29),
            datetime.datetime(2016, 11, 28, 5, 18, 24),
            datetime.datetime(2016, 12, 1, 20, 45, 52),
            datetime.datetime(2016, 12, 21, 6, 30, 52),
            datetime.datetime(2016, 12, 23, 6, 10, 10),
            datetime.datetime(2017, 1, 13, 5, 53, 56),
            datetime.datetime(2017, 1, 27, 14, 51, 36),
            datetime.datetime(2017, 2, 9, 6, 27, 53),
            datetime.datetime(2017, 2, 9, 14, 27, 40),
            datetime.datetime(2017, 2, 15, 6, 5, 51),
            datetime.datetime(2017, 3, 1, 6, 22, 39),
            datetime.datetime(2017, 3, 2, 6, 24, 37),
            datetime.datetime(2017, 3, 2, 6, 24, 37),
            datetime.datetime(2017, 3, 3, 5, 29, 31),
            datetime.datetime(2017, 3, 3, 5, 29, 44),
            datetime.datetime(2017, 3, 3, 5, 29, 44),
            datetime.datetime(2017, 3, 3, 5, 29, 44),
            datetime.datetime(2017, 3, 3, 5, 29, 44),
            datetime.datetime(2017, 3, 14, 5, 48, 47),
            datetime.datetime(2017, 3, 17, 22, 39, 50),
            datetime.datetime(2017, 3, 24, 23, 37, 12),
            datetime.datetime(2017, 4, 4, 6, 25, 49),
            datetime.datetime(2017, 4, 18, 5, 41, 28),
            datetime.datetime(2017, 4, 21, 6, 33, 28),
            datetime.datetime(2017, 4, 26, 15, 48, 2),
            datetime.datetime(2017, 4, 26, 15, 48, 3),
            datetime.datetime(2017, 5, 16, 6, 27, 4),
            datetime.datetime(2017, 6, 8, 6, 35, 8),
            datetime.datetime(2017, 6, 12, 14, 32, 15),
            datetime.datetime(2017, 6, 20, 6, 0, 51),
            datetime.datetime(2017, 6, 22, 6, 32, 35),
            datetime.datetime(2017, 6, 23, 12, 6, 58),
            datetime.datetime(2017, 6, 23, 12, 6, 58),
            datetime.datetime(2017, 6, 26, 15, 48, 6),
            datetime.datetime(2017, 6, 26, 15, 48, 6),
            datetime.datetime(2017, 6, 26, 15, 48, 6),
            datetime.datetime(2017, 6, 26, 15, 49, 52),
            datetime.datetime(2017, 6, 26, 15, 49, 52),
            datetime.datetime(2017, 6, 26, 15, 50, 18),
            datetime.datetime(2017, 6, 26, 15, 50, 26),
            datetime.datetime(2017, 6, 30, 5, 50, 25),
            datetime.datetime(2017, 7, 26, 6, 36, 10),
            datetime.datetime(2017, 7, 26, 6, 36, 10),
            datetime.datetime(2017, 8, 4, 6, 9, 39),
            datetime.datetime(2017, 8, 17, 6, 2, 28),
            datetime.datetime(2017, 9, 5, 5, 47, 10),
            datetime.datetime(2017, 10, 3, 7, 36, 7),
            datetime.datetime(2017, 10, 4, 17, 42, 56),
            datetime.datetime(2017, 10, 18, 7, 3, 39),
            datetime.datetime(2017, 10, 18, 7, 9, 51),
            datetime.datetime(2017, 10, 19, 6, 59, 44),
            datetime.datetime(2017, 10, 23, 5, 3, 34),
            datetime.datetime(2017, 10, 23, 5, 3, 34),
            datetime.datetime(2017, 10, 25, 17, 46, 1),
            datetime.datetime(2017, 10, 25, 17, 46, 1),
            datetime.datetime(2017, 10, 25, 17, 46, 1),
            datetime.datetime(2017, 10, 31, 6, 37, 57),
            datetime.datetime(2017, 10, 31, 6, 37, 57),
            datetime.datetime(2017, 11, 9, 7, 34, 7),
            datetime.datetime(2017, 11, 23, 15, 7, 31),
            datetime.datetime(2017, 11, 23, 15, 8, 15),
            datetime.datetime(2017, 11, 27, 14, 44, 16),
            datetime.datetime(2017, 12, 15, 11, 33, 17),
            datetime.datetime(2017, 12, 20, 6, 45, 40),
            datetime.datetime(2017, 12, 20, 6, 46, 3),
            datetime.datetime(2017, 12, 22, 6, 23, 1),
            datetime.datetime(2018, 1, 3, 15, 1, 31),
            datetime.datetime(2018, 1, 3, 15, 1, 38),
            datetime.datetime(2018, 1, 16, 5, 53, 9),
            datetime.datetime(2018, 1, 22, 3, 9, 25),
            datetime.datetime(2018, 1, 31, 12, 44, 55),
            datetime.datetime(2018, 2, 6, 4, 35, 36),
            datetime.datetime(2018, 2, 6, 4, 35, 36),
            datetime.datetime(2018, 2, 6, 4, 35, 36),
            datetime.datetime(2018, 2, 6, 16, 3, 42),
            datetime.datetime(2018, 2, 15, 5, 49, 24),
            datetime.datetime(2018, 2, 15, 16, 54, 24),
            datetime.datetime(2018, 2, 19, 3, 42, 2),
            datetime.datetime(2018, 3, 27, 16, 43, 36),
            datetime.datetime(2018, 4, 4, 12, 26, 18),
            datetime.datetime(2018, 4, 4, 12, 26, 18),
            datetime.datetime(2018, 4, 7, 11, 27, 59),
            datetime.datetime(2018, 4, 9, 3, 44, 15),
            datetime.datetime(2018, 4, 9, 16, 34, 39),
            datetime.datetime(2018, 4, 9, 16, 34, 39),
            datetime.datetime(2018, 4, 9, 16, 34, 39),
            datetime.datetime(2018, 4, 11, 5, 48, 5),
            datetime.datetime(2018, 4, 26, 4, 16, 18),
            datetime.datetime(2018, 4, 26, 4, 20, 21),
            datetime.datetime(2018, 4, 30, 20, 33, 44),
            datetime.datetime(2018, 5, 24, 5, 29, 22),
            datetime.datetime(2018, 5, 30, 4, 5, 11),
            datetime.datetime(2018, 5, 31, 4, 26, 42),
            datetime.datetime(2018, 6, 1, 3, 48, 35),
            datetime.datetime(2018, 6, 7, 5, 19, 4),
            datetime.datetime(2018, 6, 11, 14, 0),
            datetime.datetime(2018, 6, 29, 4, 38, 51),
            datetime.datetime(2018, 6, 29, 4, 38, 51),
        ],
        [
            1.0,
            1.0,
            1.5,
            1.3333333333333333,
            1.6666666666666667,
            1.5,
            1.75,
            2.0,
            2.25,
            2.5,
            2.2,
            2.4,
            2.6,
            2.8,
            2.5,
            2.6666666666666665,
            2.8333333333333335,
            3.0,
            3.1666666666666665,
            3.3333333333333335,
            3.5,
            3.6666666666666665,
            3.8333333333333335,
            4.0,
            4.166666666666667,
            4.333333333333333,
            4.5,
            4.666666666666667,
            4.833333333333333,
            5.0,
            5.166666666666667,
            5.333333333333333,
            5.5,
            5.666666666666667,
            5.833333333333333,
            6.0,
            6.166666666666667,
            6.333333333333333,
            6.5,
            6.666666666666667,
            6.833333333333333,
            7.0,
            7.166666666666667,
            7.333333333333333,
            6.428571428571429,
            6.571428571428571,
            6.714285714285714,
            6.857142857142857,
            7.0,
            7.142857142857143,
            7.285714285714286,
            7.428571428571429,
            7.571428571428571,
            7.714285714285714,
            7.857142857142857,
            8.0,
            8.142857142857142,
            8.285714285714286,
            8.428571428571429,
            8.571428571428571,
            8.714285714285714,
            8.857142857142858,
            9.0,
            9.142857142857142,
            9.285714285714286,
            9.428571428571429,
            9.571428571428571,
            9.714285714285714,
            9.857142857142858,
            10.0,
            10.142857142857142,
            10.285714285714286,
            10.428571428571429,
            10.571428571428571,
            10.714285714285714,
            10.857142857142858,
            11.0,
            11.142857142857142,
            11.285714285714286,
            11.428571428571429,
            11.571428571428571,
            11.714285714285714,
            11.857142857142858,
            12.0,
            12.142857142857142,
            12.285714285714286,
            12.428571428571429,
            12.571428571428571,
            12.714285714285714,
            12.857142857142858,
            13.0,
            13.142857142857142,
            13.285714285714286,
            13.428571428571429,
            13.571428571428571,
            13.714285714285714,
            13.857142857142858,
            14.0,
            14.142857142857142,
            14.285714285714286,
            14.428571428571429,
            14.571428571428571,
            14.714285714285714,
            14.857142857142858,
            13.125,
            13.25,
            13.375,
            13.5,
            13.625,
            13.75,
            13.875,
            14.0,
            14.125,
            14.25,
            14.375,
            14.5,
            14.625,
            14.75,
            14.875,
            15.0,
            15.125,
            15.25,
            15.375,
            15.5,
            15.625,
            15.75,
            15.875,
            16.0,
            16.125,
            16.25,
            16.375,
            16.5,
            16.625,
            16.75,
            16.875,
            17.0,
            17.125,
            17.25,
            17.375,
            17.5,
            17.625,
            17.75,
            17.875,
            18.0,
            18.125,
            18.25,
            18.375,
            18.5,
            18.625,
            18.75,
            18.875,
            19.0,
            19.125,
            19.25,
            19.375,
            19.5,
            19.625,
            19.75,
            19.875,
            20.0,
            20.125,
            20.25,
            20.375,
            20.5,
            20.625,
            20.75,
            20.875,
            21.0,
            21.125,
            21.25,
            21.375,
            21.5,
            21.625,
            21.75,
            21.875,
            22.0,
            22.125,
            22.25,
            22.375,
            22.5,
            22.625,
        ],
    ],
}
pBStats.authorPlotInfo = testData
testData["figs"] = pBStats.plotStats(author=True)


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestAuthorStatsPlots(GUIwMainWTestCase):
    """Test the functions in AuthorStatsPlots"""

    def test_figTitles(self):
        """test figTitles"""
        self.assertEqual(
            figTitles,
            [
                "Paper number",
                "Papers per year",
                "Total citations",
                "Citations per year",
                "Mean citations",
                "Citations for each paper",
            ],
        )

    def test_init(self):
        """Test __init__"""
        self.mainW.lastAuthorStats = {"h": 999}
        self.mainW.lastPaperStats = {}
        with patch(
            "physbiblio.gui.inspireStatsGUI.AuthorStatsPlots.updatePlots", autospec=True
        ) as _up:
            asp = AuthorStatsPlots(["a", "b", "c", "d", "e", "f"])
            self.assertEqual(asp.figs, ["a", "b", "c", "d", "e", "f"])
            _up.assert_called_once_with(asp)
            self.assertIsInstance(asp.layout(), QGridLayout)
            self.assertEqual(asp.layout().columnCount(), 2)
            self.assertEqual(asp.layout().rowCount(), 7)
            w40 = asp.layout().itemAtPosition(4, 0).widget()
            self.assertIsInstance(w40, PBLabel)
            self.assertEqual(w40.text(), "Click on the lines to have more information:")
            self.assertIsInstance(asp.hIndex, PBLabel)
            self.assertEqual(asp.hIndex.font().family(), "Times")
            self.assertEqual(asp.hIndex.font().pointSize(), 15)
            self.assertEqual(asp.hIndex.font().weight(), QFont.Bold)
            self.assertEqual(asp.hIndex.text(), "Author h index: ND")
            self.assertEqual(asp.layout().itemAtPosition(4, 1).widget(), asp.hIndex)
            self.assertIsInstance(asp.textBox, QLineEdit)
            self.assertTrue(asp.textBox.isReadOnly())
            self.assertEqual(asp.layout().itemAtPosition(5, 0).widget(), asp.textBox)
            self.assertIsInstance(asp.saveButton, QPushButton)
            self.assertEqual(asp.saveButton.text(), "Save")
            self.assertEqual(asp.layout().itemAtPosition(6, 0).widget(), asp.saveButton)
            with patch(
                "physbiblio.gui.inspireStatsGUI.AuthorStatsPlots.saveAction",
                autospec=True,
            ) as _sa:
                QTest.mouseClick(asp.saveButton, Qt.LeftButton)
                self.assertEqual(_sa.call_count, 1)
            self.assertIsInstance(asp.clButton, QPushButton)
            self.assertEqual(asp.clButton.text(), "Close")
            self.assertTrue(asp.clButton.autoDefault())
            self.assertEqual(asp.layout().itemAtPosition(6, 1).widget(), asp.clButton)
            with patch(
                "physbiblio.gui.inspireStatsGUI.AuthorStatsPlots.onClose", autospec=True
            ) as _cl:
                QTest.mouseClick(asp.clButton, Qt.LeftButton)
                self.assertEqual(_cl.call_count, 1)

            asp = AuthorStatsPlots(["a", "b", "c", "d", "e", "f"], parent=self.mainW)
            self.assertEqual(asp.parent(), self.mainW)
            self.assertIsInstance(asp.hIndex, PBLabel)
            self.assertEqual(asp.hIndex.text(), "Author h index: 999")
            self.assertEqual(asp.windowTitle(), "")

            asp = AuthorStatsPlots(
                ["a", "b", "c", "d", "e", "f"], title="abcdef", parent=self.mainW
            )
            self.assertEqual(asp.windowTitle(), "abcdef")

    def test_saveAction(self):
        """Test saveAction"""
        self.mainW.lastAuthorStats = {"h": 999}
        with patch(
            "physbiblio.gui.inspireStatsGUI.AuthorStatsPlots.updatePlots", autospec=True
        ) as _up:
            asp = AuthorStatsPlots(["a", "b", "c", "d", "e", "f"], parent=self.mainW)
        self.assertTrue(asp.saveButton.isEnabled())
        with patch(
            "physbiblio.inspireStats.InspireStatsLoader.plotStats",
            return_value="fakeval",
            autospec=True,
        ) as _ps:
            with patch(
                "physbiblio.gui.inspireStatsGUI.askDirName",
                return_value="",
                autospec=True,
            ) as _adn:
                asp.saveAction()
                _adn.assert_called_once_with(
                    asp, "Where do you want to save the plots of the stats?"
                )
                self.assertTrue(asp.saveButton.isEnabled())
                self.assertNotIn("figs", self.mainW.lastAuthorStats.keys())
                _ps.assert_not_called()
            with patch(
                "physbiblio.gui.inspireStatsGUI.askDirName",
                return_value="/tmp",
                autospec=True,
            ), patch(
                "physbiblio.gui.inspireStatsGUI.infoMessage", autospec=True
            ) as _im:
                asp.saveAction()
                _im.assert_called_once_with("Plots saved.")
                self.assertFalse(asp.saveButton.isEnabled())
                _ps.assert_called_once_with(
                    pBStats, author=True, path="/tmp", save=True
                )
                self.assertEqual(self.mainW.lastAuthorStats["figs"], "fakeval")
        asp.saveButton.setEnabled(True)
        with patch(
            "physbiblio.inspireStats.InspireStatsLoader.plotStats",
            side_effect=AttributeError,
            autospec=True,
        ) as _ps, patch(
            "physbiblio.gui.inspireStatsGUI.askDirName",
            return_value="tmp",
            autospec=True,
        ) as _adn, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "physbiblio.gui.inspireStatsGUI.infoMessage", autospec=True
        ) as _im:
            asp.saveAction()
            _w.assert_called_once_with("", exc_info=True)
            _im.assert_not_called()
            self.assertTrue(asp.saveButton.isEnabled())

    def test_pickEvent(self):
        """Test pickEvent"""
        self.mainW.lastAuthorStats = {"h": 999}
        asp = AuthorStatsPlots(testData["figs"], parent=self.mainW)
        evt = MagicMock()
        evt.artist = Line2D((0, 1), (1, 1))
        evt.artist.figure = testData["figs"][2]
        evt.artist.get_xdata = MagicMock()
        evt.artist.get_ydata = MagicMock()
        evt.ind = 0
        with patch(
            "numpy.take", side_effect=[[datetime.datetime(2016, 9, 27)], [75]]
        ) as _t:
            asp.pickEvent(evt)
            _t.assert_any_call(evt.artist.get_xdata(), 0)
            _t.assert_any_call(evt.artist.get_ydata(), 0)
        self.assertEqual(asp.textBox.text(), "Total citations in date 27/09/2016 is 75")
        evt.artist.figure = testData["figs"][4]
        with patch(
            "numpy.take", side_effect=[[datetime.datetime(2016, 9, 8)], [10.0]]
        ) as _t:
            asp.pickEvent(evt)
            _t.assert_any_call(evt.artist.get_xdata(), 0)
            _t.assert_any_call(evt.artist.get_ydata(), 0)
        self.assertEqual(
            asp.textBox.text(), "Mean citations in date 08/09/2016 is 10.00"
        )
        evt.artist = Rectangle((0, 1), 1, 1)
        evt.artist.figure = testData["figs"][1]
        evt.artist.get_x = MagicMock(return_value=2015.5)
        evt.artist.get_height = MagicMock(return_value=5)
        asp.pickEvent(evt)
        self.assertEqual(asp.textBox.text(), "Papers per year in year 2015 is: 5")

    def test_updatePlots(self):
        """Test updatePlots"""
        self.mainW.lastAuthorStats = {"h": 999}
        with patch(
            "physbiblio.gui.inspireStatsGUI.AuthorStatsPlots.updatePlots", autospec=True
        ) as _up:
            asp = AuthorStatsPlots(testData["figs"], parent=self.mainW)
            self.assertEqual(asp.figs, testData["figs"])
            _up.assert_called_once_with(asp)
        asp = AuthorStatsPlots(testData["figs"], parent=self.mainW)
        self.assertEqual(asp.figs, testData["figs"])
        self.assertIsInstance(asp.canvas, list)
        for i in [0, 1, 2]:
            for j in [0, 1]:
                self.assertIsInstance(
                    asp.layout().itemAtPosition(i, j).widget(), FigureCanvasQTAgg
                )
                self.assertEqual(
                    asp.layout().itemAtPosition(i, j).widget().figure,
                    asp.figs[i * 2 + j],
                )
        self.assertEqual(len(asp.canvas), 6)
        self.assertEqual(len(asp.figs), 6)
        asp = AuthorStatsPlots([None] + testData["figs"] + [None], parent=self.mainW)
        self.assertEqual(len(asp.canvas), 6)
        self.assertEqual(len(asp.figs), 8)
        for i in [0, 1, 2]:
            for j in [0, 1]:
                self.assertEqual(
                    asp.layout().itemAtPosition(i, j).widget().figure,
                    asp.figs[1 + i * 2 + j],
                )


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestPaperStatsPlots(GUIwMainWTestCase):
    """Test the functions in PaperStatsPlots"""

    def test_init(self):
        """Test init"""
        self.mainW.lastPaperStats = {}
        asp = PaperStatsPlots(testData["figs"][2])
        self.assertIsInstance(asp.layout(), QGridLayout)
        self.assertEqual(asp.layout().columnCount(), 2)
        self.assertEqual(asp.layout().rowCount(), 5)
        w20 = asp.layout().itemAtPosition(2, 0).widget()
        self.assertIsInstance(w20, PBLabel)
        self.assertEqual(w20.text(), "Click on the line to have more information:")
        self.assertIsInstance(asp.textBox, QLineEdit)
        self.assertTrue(asp.textBox.isReadOnly())
        self.assertEqual(asp.layout().itemAtPosition(3, 0).widget(), asp.textBox)
        self.assertIsInstance(asp.saveButton, QPushButton)
        self.assertEqual(asp.saveButton.text(), "Save")
        self.assertEqual(asp.layout().itemAtPosition(4, 0).widget(), asp.saveButton)
        with patch(
            "physbiblio.gui.inspireStatsGUI.PaperStatsPlots.saveAction", autospec=True
        ) as _sa:
            QTest.mouseClick(asp.saveButton, Qt.LeftButton)
            self.assertEqual(_sa.call_count, 1)
        self.assertIsInstance(asp.clButton, QPushButton)
        self.assertEqual(asp.clButton.text(), "Close")
        self.assertTrue(asp.clButton.autoDefault())
        self.assertEqual(asp.layout().itemAtPosition(4, 1).widget(), asp.clButton)
        with patch(
            "physbiblio.gui.inspireStatsGUI.PaperStatsPlots.onClose", autospec=True
        ) as _cl:
            QTest.mouseClick(asp.clButton, Qt.LeftButton)
            self.assertEqual(_cl.call_count, 1)

        asp = PaperStatsPlots(testData["figs"][2], parent=self.mainW)
        self.assertEqual(asp.parent(), self.mainW)
        self.assertEqual(asp.windowTitle(), "")

        asp = PaperStatsPlots(testData["figs"][2], title="abcdef", parent=self.mainW)
        self.assertEqual(asp.windowTitle(), "abcdef")

    def test_saveAction(self):
        """Test saveAction"""
        self.mainW.lastPaperStats = {}
        asp = PaperStatsPlots(testData["figs"][2], parent=self.mainW)
        self.assertTrue(asp.saveButton.isEnabled())
        with patch(
            "physbiblio.inspireStats.InspireStatsLoader.plotStats",
            return_value="fakeval",
            autospec=True,
        ) as _ps:
            with patch(
                "physbiblio.gui.inspireStatsGUI.askDirName",
                return_value="",
                autospec=True,
            ) as _adn:
                asp.saveAction()
                _adn.assert_called_once_with(
                    asp, "Where do you want to save the plot of the stats?"
                )
                self.assertTrue(asp.saveButton.isEnabled())
                self.assertNotIn("fig", self.mainW.lastPaperStats.keys())
                _ps.assert_not_called()
            with patch(
                "physbiblio.gui.inspireStatsGUI.askDirName",
                return_value="/tmp",
                autospec=True,
            ), patch(
                "physbiblio.gui.inspireStatsGUI.infoMessage", autospec=True
            ) as _im:
                asp.saveAction()
                _im.assert_called_once_with("Plot saved.")
                self.assertFalse(asp.saveButton.isEnabled())
                _ps.assert_called_once_with(pBStats, paper=True, path="/tmp", save=True)
                self.assertEqual(self.mainW.lastPaperStats["fig"], "fakeval")
        asp.saveButton.setEnabled(True)
        with patch(
            "physbiblio.inspireStats.InspireStatsLoader.plotStats",
            side_effect=AttributeError,
            autospec=True,
        ) as _ps, patch(
            "physbiblio.gui.inspireStatsGUI.askDirName",
            return_value="tmp",
            autospec=True,
        ) as _adn, patch(
            "logging.Logger.warning"
        ) as _w, patch(
            "physbiblio.gui.inspireStatsGUI.infoMessage", autospec=True
        ) as _im:
            asp.saveAction()
            _w.assert_called_once_with("", exc_info=True)
            _im.assert_not_called()
            self.assertTrue(asp.saveButton.isEnabled())

    def test_pickEvent(self):
        """Test pickEvent"""
        self.mainW.lastPaperStats = {}
        asp = PaperStatsPlots(testData["figs"][2], parent=self.mainW)
        evt = MagicMock()
        evt.artist = Line2D((0, 1), (1, 1))
        evt.artist.figure = testData["figs"][2]
        evt.artist.get_xdata = MagicMock()
        evt.artist.get_ydata = MagicMock()
        evt.ind = 0
        with patch(
            "numpy.take", side_effect=[[datetime.datetime(2016, 9, 27)], [75]]
        ) as _t:
            asp.pickEvent(evt)
            _t.assert_any_call(evt.artist.get_xdata(), 0)
            _t.assert_any_call(evt.artist.get_ydata(), 0)
        self.assertEqual(asp.textBox.text(), "Citations in date 27/09/2016 is 75")

    def test_updatePlots(self):
        """Test updatePlots"""
        self.mainW.lastPaperStats = {}
        asp = PaperStatsPlots(testData["figs"][2], parent=self.mainW)
        self.assertEqual(asp.fig, testData["figs"][2])
        self.assertIsInstance(asp.canvas, FigureCanvasQTAgg)
        self.assertIsInstance(
            asp.layout().itemAtPosition(0, 0).widget(), FigureCanvasQTAgg
        )
        self.assertEqual(asp.layout().itemAtPosition(0, 0).widget().figure, asp.fig)


if __name__ == "__main__":
    unittest.main()
