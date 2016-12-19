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
	dirs = []
	for p in os.listdir(base):
		if p[:2] != '__' and os.path.isdir(os.path.join(base, p)):
			dirs.append(p)

	leftover = len(dirs) + 1 # add 1 to make sure it's ran at least once
	while len(dirs) > 0 and len(dirs) != leftover:
		leftover = len(dirs)
		for p in dirs:
			path = os.path.join(base, p)
			print('Loading plugin: %s' % p)
			try:
				mod = SourceFileLoader("plugins.%s" % p, os.path.join(path, "__init__.py")).load_module()
				plugin = mod.load()
				loaded[plugin.name] = plugin
				dirs.remove(p)
			except Exception as exc:
				print('Failed to load plugin: ' + p)
				print(exc)
				
	if len(dirs) > 0:
		print('Failed to load plugins: %s' % dirs)
		
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
	