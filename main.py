# -*- coding: utf-8 -*-

import sys

from PySide import QtCore, QtGui

import plugins
import ui

QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
app = QtGui.QApplication(sys.argv)

mainWindow = ui.getMainWindow()
mainWindow.show()
sys.exit(app.exec_())

#@TODO: allow events to be saved as templates
#@TODO: logging EVERYWHERE
