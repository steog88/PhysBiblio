#!/bin/bash
pyrcc5 -o Resources_pyside2.py Resources.qrc
sed -i s#PyQt5#PySide2#g Resources_pyside2.py
