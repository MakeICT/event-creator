# -*- coding: utf-8 -*-

import os, sys
import datetime

import logging
import Logger

from PySide import QtCore, QtGui

import ui
import plugins
from config import settings

QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
app = QtGui.QApplication(sys.argv)

logging.debug('Logging started')

ui.setPlugins(plugins.loadAllFromPath())
logging.debug('Plugins loaded')

mainWindow = ui.getMainWindow()
mainWindow.show()

sys.exit(app.exec_())
