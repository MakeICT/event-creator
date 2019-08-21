# -*- coding: utf-8 -*-

import logging
import os, sys
import importlib
import traceback

from PySide import QtCore
from config import settings

import plugins

from importlib.machinery import SourceFileLoader

loaded = {}


def loadAllFromPath(base='plugins'):
    global loaded
    pluginDirs = []
    for p in os.listdir(base):
        if p[:2] != '__' and os.path.isdir(os.path.join(base, p)):
            pluginDirs.append(p)

    leftover = len(pluginDirs) + 1  # add 1 to make sure it's ran at least once
    while len(pluginDirs) > 0 and len(pluginDirs) != leftover:
        leftover = len(pluginDirs)
        modules = {}
        for p in list(pluginDirs):
            logging.debug('Loading plugin module: %s...' % p)
            path = os.path.join(base, p)
            source_file = SourceFileLoader("plugins.%s" % p,
                                           os.path.join(path, "__init__.py"))
            mod = source_file.load_module()
            modules[p] = mod
            plugins.__dict__[p] = mod
            pluginDirs.remove(p)

        for name, mod in modules.items():
            logging.debug('Initializing plugin: %s...' % name)
            plugin = mod.load()
            loaded[plugin.name] = plugin

    if len(pluginDirs) > 0:
        logging.error('Failed to load plugin modules: %s' % pluginDirs)

    return loaded


class Plugin(QtCore.QObject):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def getSetting(self, setting, default=''):
        value = settings.value('plugin-%s/%s' % (self.name, setting), default)
        if value == '':
            value = default

        return value

    def saveSetting(self, setting, value):
        return settings.setValue('plugin-%s/%s' % (self.name, setting), value)

    def checkForInterruption(self):
        if QtCore.QThread.currentThread().isInterruptionRequested():
            raise Interruption(self)

    def prepare(self, callback=None):
        if callback:
            callback()


class DependencyMissingException(Exception):
    pass
