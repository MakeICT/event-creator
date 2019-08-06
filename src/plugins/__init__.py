import plugins

# from PySide2 import QtCore
from config import settings

class Plugin():
    def __init__(self, name):
        super().__init__()
        self.name = name

    def getGeneralSetting(self, setting, default=''):
        value = settings.get('General', setting)
        #value = settings['plugin-%s/%s' % (self.name, setting)]
        if value == '':
            value = default
            
        return value
        
    def getSetting(self, setting, default=''):
        value = settings.get('plugin-' + self.name, setting)
        #value = settings['plugin-%s/%s' % (self.name, setting)]
        if value == '':
            value = default
            
        return value
        
    def saveSetting(self, setting, value):
        settings['plugin-%s/%s' % (self.name, setting)]: value

    #def loadPlugins(self): 
        
        
        
class DependencyMissingException(Exception):
    pass
    
class Interruption(Exception):
    def __init__(self, plugin):
        super().__init__('Interruption detected by plugin: ' + plugin.name)
        self.plugin = plugin
    
