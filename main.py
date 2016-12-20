# -*- coding: utf-8 -*-

import os, sys
import logging, datetime

from PySide import QtCore, QtGui

import ui
import plugins
from config import settings

QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
app = QtGui.QApplication(sys.argv)

logLevels = {
	'Critical': logging.CRITICAL,
	'Error': logging.ERROR,
	'Warning': logging.WARNING,
	'Info': logging.INFO,
	'Debug': logging.DEBUG,
}

if not os.path.exists('logs'):
    os.makedirs('logs')
    
logFile = os.path.join('logs', '{0:%Y-%m-%d_%H%M%S}.log'.format(datetime.datetime.now()))
logging.basicConfig(
	format='%(levelname)-8s %(asctime)s %(message)s',
	filename=logFile,
	level=logLevels[settings.value('logLevel', 'Debug')]
)

logging.debug('Logging started')

ui.setPlugins(plugins.loadAllFromPath())
logging.debug('Plugins loaded')

mainWindow = ui.getMainWindow()
mainWindow.show()

sys.exit(app.exec_())
