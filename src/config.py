import configparser

filename = 'settings.ini'
settings = configparser.ConfigParser()
settings.read(filename)


def checkBool(value):
    return value not in [False, 'False', 'false', 'F', 'f', 0, '0', '', None]


def save(section, setting, value):
    settings.set(section, setting, value)
    print("<<SAVED>>")

    with open(filename, 'w') as settings_file:
        settings.write(settings_file)

