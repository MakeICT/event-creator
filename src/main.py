import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import plugins
from config import settings



targets = []
actions = {}
loadedPlugins = {}


populationTypes = ['Everybody']
lastTemplateFile = None

loadedPlugins = plugins.loadAllFromPath()
# print(loadedPlugins)

app = Flask(__name__)
plugins.logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('wa.log')
plugins.logger.addHandler(handler)

app.config['SECRET_KEY'] = settings.get('General', 'SECRET_KEY')
# app.config['GOOGLE_CLIENT_ID'] = settings.get('Google', 'Client ID')
# app.config['GOOGLE_CLIENT_SECRET'] = settings.get('Google', 'Client Secret')
# app.config['REDIRECT_URI'] = settings.get('Google', 'OAUTH Redirect URL')
app.config['SQLALCHEMY_DATABASE_URI'] = settings.get('Database', 'URL') or 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)


from routes import *
import auth


def setPlugins(plugins):
    global loadedPlugins
    loadedPlugins = plugins


def _getChildren(parent):
    for i in range(parent.count()):
        yield parent.itemAt(i).widget()


if __name__ == '__main__':
    app.run(debug=True, load_dotenv=True)
