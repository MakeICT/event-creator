from flask import Flask, render_template, url_for, flash, redirect
from forms import NewClassForm
from attrdict import AttrDict
import plugins
from plugins import WildApricot, MakerspaceAuthorizations
import json
from config import settings

targets = []
actions = {}
loadedPlugins = {}

populationTypes = ['Everybody']
lastTemplateFile = None


app = Flask(__name__)

app.config['SECRET_KEY'] = settings.get('General', 'SECRET_KEY')


@app.route("/home")
def home():
    return render_template('home.html', title='Home')

@app.route("/createClass", methods=['GET', 'POST'])
def createClass():
    form = NewClassForm()
    if form.validate_on_submit():
        flash(f'Class created for {form.classTitle.data}!', 'success')
        event=form.collectEventDetails()
        print(event)
        
        waplugin.createEvent(event)
        return redirect(url_for('home'))
    return render_template('createClass.html', title='Create Event', form=form, authorizations=authorizationsplugin.getAuthorizations())


def setPlugins(plugins):
    global loadedPlugins
    loadedPlugins = plugins

def _getChildren(parent):
    for i in range(parent.count()):
        yield parent.itemAt(i).widget()



#setPlugins(plugins.loadAllFromPath())

waplugin = WildApricot.load()
authorizationsplugin = MakerspaceAuthorizations.load();


if __name__ == '__main__':
    app.run(debug=True)