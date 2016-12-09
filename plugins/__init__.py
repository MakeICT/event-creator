# -*- coding: utf-8 -*-

import importlib

from PySide import QtCore
from config import settings

import ui

dirs = ['WildApricot', 'GoogleCalendar', 'Facebook', 'Meetup', 'Gmail', 'MakerspaceAuthorizations']

loaded = {}

for p in dirs:
	mod = importlib.import_module('plugins.%s' % p)
	plugin = mod.load()
	loaded[plugin.name] = plugin
	
def get(name):
	return loaded[name]
