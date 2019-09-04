# -*- coding: utf-8 -*-

import logging
import os

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
        enabled_plugins = settings.get('General', 'Plugin priority').split(',')
        # print("enabled:", enabled_plugins)

        # for p in list(pluginDirs):
        for p in enabled_plugins:
            logging.debug('Loading plugin module: %s...' % p)
            # print('Loading plugin module: %s...' % p)
            path = os.path.join(base, p)
            source_file = SourceFileLoader("plugins.%s" % p,
                                           os.path.join(path, "__init__.py"))
            mod = source_file.load_module()
            modules[p] = mod
            plugins.__dict__[p] = mod
            # pluginDirs.remove(p)

        # print(modules.items())
        for name, mod in modules.items():
            if name in enabled_plugins:
                logging.debug('Initializing plugin: %s...' % name)
                plugin = mod.load()
                loaded[plugin.name] = plugin
            else:
                logging.debug('Skipping disabled plugin: %s...' % name)

    # if len(pluginDirs) > 0:
    #     logging.error('Failed to load plugin modules: %s' % pluginDirs)

    return loaded


class Plugin():
    def __init__(self, name):
        self.name = name

    def getSetting(self, setting, default=''):
        value = settings.get('plugin-' + self.name, setting)
        #value = settings['plugin-%s/%s' % (self.name, setting)]
        if value == '':
            value = default

        return value

    def getGeneralSetting(self, setting, default=''):
        value = settings.get('General', setting)
        #value = settings['plugin-%s/%s' % (self.name, setting)]
        if value == '':
            value = default

        return value

    def saveSetting(self, setting, value):
        settings['plugin-%s/%s' % (self.name, setting)]: value

    def prepare(self, callback=None):
        if callback:
            callback()


class EventPlugin(Plugin):
    def __init__(self, name):
        super().__init__(name)


class DependencyMissingException(Exception):
    pass
