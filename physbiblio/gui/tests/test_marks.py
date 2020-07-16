#!/usr/bin/env python
"""Test file for the physbiblio.gui.marks module.

This file is part of the physbiblio package.
"""
import os
import sys
import traceback

from PySide2.QtCore import Qt
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QHBoxLayout

try:
    from physbiblio.gui.marks import *
    from physbiblio.gui.setuptests import *
    from physbiblio.setuptests import *
except ImportError:
    print("Could not find physbiblio and its modules!")
    raise
except Exception:
    print(traceback.format_exc())


@unittest.skipIf(skipTestsSettings.gui, "GUI tests")
class TestMarks(GUITestCase):
    """Test the functions in marks.Marks"""

    def test_pbmarks(self):
        """test that pBMarks exists"""
        self.assertIsInstance(pBMarks, Marks)

    def testInit(self):
        """tests for the marks.__init__ function"""
        m = Marks()
        self.assertEqual(len(m.marks.keys()), 5)
        for q in ["imp", "fav", "bad", "que", "new"]:
            self.assertIn(q, m.marks.keys())
        self.assertEqual(
            m.marks["imp"],
            {"desc": "Important", "icon": ":/images/emblem-important-symbolic.png"},
        )
        self.assertEqual(
            m.marks["fav"],
            {"desc": "Favorite", "icon": ":/images/emblem-favorite-symbolic.png"},
        )
        self.assertEqual(
            m.marks["bad"], {"desc": "Bad", "icon": ":/images/emblem-remove.png"}
        )
        self.assertEqual(
            m.marks["que"], {"desc": "Unclear", "icon": ":/images/emblem-question.png"}
        )
        self.assertEqual(
            m.marks["new"], {"desc": "To be read", "icon": ":/images/unread-new.png"}
        )

    def testNewMark(self):
        """tests for the marks.newMark function"""
        m = Marks()
        m.newMark("abc", "desc", "icon")
        self.assertEqual(m.marks["abc"], {"desc": "desc", "icon": ":/images/icon.png"})

    def testGetGroupbox(self):
        """tests for the marks.getGroupbox function"""
        m = Marks()
        gb, mv = m.getGroupbox(None)
        self.assertTrue(gb.isFlat())
        self.assertEqual(gb.title(), "Marks")
        self.assertIsInstance(gb.layout(), QHBoxLayout)
        self.assertIsInstance(mv, dict)
        for q in ["imp", "fav", "bad", "que", "new"]:
            self.assertIn(q, mv.keys())
        self.assertNotIn("any", mv.keys())
        for qcb in mv.values():
            self.assertIsInstance(qcb, QCheckBox)
            self.assertFalse(qcb.isChecked())

        gb, mv = m.getGroupbox(["new", "imp"])
        for q, qcb in mv.items():
            self.assertIsInstance(mv[q], QCheckBox)
            if q in ["new", "imp"]:
                self.assertTrue(qcb.isChecked())
            else:
                self.assertFalse(qcb.isChecked())

        gb, mv = m.getGroupbox(["imp"], "try", radio=True)
        self.assertEqual(gb.title(), "try")
        for q, qcb in mv.items():
            self.assertIsInstance(mv[q], QRadioButton)
            if q in ["imp"]:
                self.assertTrue(qcb.isChecked())
            else:
                self.assertFalse(qcb.isChecked())

        gb, mv = m.getGroupbox([], radio=True, addAny=True)
        self.assertIn("any", mv.keys())
        for q, qcb in mv.items():
            self.assertIsInstance(mv[q], QRadioButton)
            self.assertFalse(qcb.isChecked())


if __name__ == "__main__":
    unittest.main()
