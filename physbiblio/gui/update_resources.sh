#!/bin/bash
pyrcc5 -o resources_pyside2.py resources.qrc
sed -i s#PyQt5#PySide2#g resources_pyside2.py
