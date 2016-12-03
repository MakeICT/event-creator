# -*- coding: utf-8 -*-

import importlib

dirs = ['WildApricot']

loaded = {}

for p in dirs:
	mod = importlib.import_module('plugins.%s' % p)
	loaded[p] = mod.load()
	
def get(name):
	return loaded[name]