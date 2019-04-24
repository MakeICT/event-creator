import configparser

settings = configparser.ConfigParser()
settings.read('settings.ini')

def checkBool(value):
    return value not in [ False, 'False', 'false', 'F', 'f', 0, '0', '', None ]
