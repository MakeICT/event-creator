# -*- coding: utf-8 -*-

import sys

from PySide import QtCore, QtGui

import ui
import plugins

QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
app = QtGui.QApplication(sys.argv)


ui.setPlugins(plugins.loadAllFromPath())

mainWindow = ui.getMainWindow()
mainWindow.show()
sys.exit(app.exec_())

#@TODO: allow events to be saved as templates
#@TODO: logging EVERYWHERE
