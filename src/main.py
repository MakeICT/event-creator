from flask import Flask, render_template, url_for, flash, redirect, request
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

    authorizations=authorizationsplugin.getAuthorizations()

    if form.validate_on_submit():
        flash(f'Class created for {form.classTitle.data}!', 'success')

        # FIXME 
        # There must be a better way to do the checkboxes, but this is the only way I have found that works        
        selected_authorizations = request.form.getlist("authorizations")
        form.setSelectedAuthorizations(selected_authorizations)
        event=form.collectEventDetails()
                
        waplugin.createEvent(event)
        return redirect(url_for('home'))
    
    return render_template('createClass.html', title='Create Event', form=form, authorizations=authorizations)


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