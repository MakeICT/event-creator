from PySide import QtCore

from config import settings

class Plugin(QtCore.QObject):
	def __init__(self, name):
		super().__init__()
		self.name = name
		
	def getSetting(self, setting, default=''):
		return settings.value('plugin-%s/%s' % (self.name, setting), default)
		
	def saveSetting(self, setting, value):
		return settings.setValue('plugin-%s/%s' % (self.name, setting), value)
