from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_oauth import OAuth
from forms import NewClassForm
from attrdict import AttrDict
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import plugins
# from plugins import WildApricot
import json
from config import settings
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime
from flask_navbar import Nav
from flask_navbar.elements import *
from dateutil.parser import parse

targets = []
actions = {}
loadedPlugins = {}


populationTypes = ['Everybody']
lastTemplateFile = None

loadedPlugins = plugins.loadAllFromPath()
print(loadedPlugins)

app = Flask(__name__)

db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)

app.config['SECRET_KEY'] = settings.get('General', 'SECRET_KEY')
app.config['GOOGLE_CLIENT_ID'] = settings.get('Google', 'Client ID')
app.config['GOOGLE_CLIENT_SECRET'] = settings.get('Google', 'Client Secret')
app.config['REDIRECT_URI'] = settings.get('Google','OATH Redirect URL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

import routes


def setPlugins(plugins):
    global loadedPlugins
    loadedPlugins = plugins

def _getChildren(parent):
    for i in range(parent.count()):
        yield parent.itemAt(i).widget()

if __name__ == '__main__':
    app.run(debug=True)
