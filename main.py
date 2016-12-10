# -*- coding: utf-8 -*-

import sys

from PySide import QtCore, QtGui

import plugins
import ui

app = QtGui.QApplication(sys.argv)

mainWindow = ui.getMainWindow()
mainWindow.show()
sys.exit(app.exec_())

#@TODO: allow events to be saved as templates
