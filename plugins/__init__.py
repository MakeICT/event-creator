# -*- coding: utf-8 -*-

import importlib

dirs = ['WildApricot', 'GoogleCalendar', 'Facebook', 'Meetup', 'Gmail']

loaded = {}

for p in dirs:
	mod = importlib.import_module('plugins.%s' % p)
	loaded[p] = mod.load()
	
def get(name):
	return loaded[name]
