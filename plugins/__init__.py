# -*- coding: utf-8 -*-

import os
import importlib

from PySide import QtCore
from config import settings

import ui

from importlib.machinery import SourceFileLoader

loaded = {}

def loadAllFromPath(base='plugins'):
	global loaded
	pluginDirs = []
	for p in os.listdir(base):
		if p[:2] != '__' and os.path.isdir(os.path.join(base, p)):
			pluginDirs.append(p)

	leftover = len(pluginDirs) + 1 # add 1 to make sure it's ran at least once
	while len(pluginDirs) > 0 and len(pluginDirs) != leftover:
		leftover = len(pluginDirs)
		for p in list(pluginDirs):
			print('Loading plugin: %s' % p)
			try:
				path = os.path.join(base, p)
				mod = SourceFileLoader("plugins.%s" % p, os.path.join(path, "__init__.py")).load_module()
				plugin = mod.load()
				loaded[plugin.name] = plugin
				pluginDirs.remove(p)
			except Exception as exc:
				print('Failed to load plugin: ' + p)
				print(exc)
				
	if len(pluginDirs) > 0:
		print('Failed to load plugins: %s' % pluginDirs)
		
	return loaded
		
class Plugin(QtCore.QObject):
	def __init__(self, name):
		super().__init__()
		self.name = name
		
	def getSetting(self, setting, default=''):
		return settings.value('plugin-%s/%s' % (self.name, setting), default)
		
	def saveSetting(self, setting, value):
		return settings.setValue('plugin-%s/%s' % (self.name, setting), value)

	def checkForInterruption(self):
		if QtCore.QThread.currentThread().isInterruptionRequested():
			raise Interruption(self)
			
	def prepare(self):
		pass

class Interruption(Exception):
	def __init__(self, plugin):
		super().__init__('Interruption detected by plugin: ' + plugin.name)
		self.plugin = plugin
	
