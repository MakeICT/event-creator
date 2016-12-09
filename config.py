import logging

from PySide import QtCore

#settings = QtCore.QSettings('Green Light Go', 'Event Creator')
settings = QtCore.QSettings('settings.ini', QtCore.QSettings.IniFormat)

def checkBool(value):
	return value not in [ False, 'False', 'false', 'F', 'f', 0, '0', None ]
