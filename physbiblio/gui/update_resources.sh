#!/bin/bash
pyrcc5 -o resourcesPyside2.py resources.qrc
sed -i s#PyQt5#PySide2#g resourcesPyside2.py
