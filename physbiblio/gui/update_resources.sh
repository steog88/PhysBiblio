#!/bin/bash

# If Qt module is PySide
pyside-rcc -o Resources_pyside.py Resources.qrc
pyside-rcc -py3 -o Resources_pyside3.py Resources.qrc

