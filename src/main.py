from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_oauth import OAuth
from forms import NewClassForm
from attrdict import AttrDict
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
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
app.config['GOOGLE_CLIENT_ID'] = settings.get('Google', 'Client ID')
app.config['GOOGLE_CLIENT_SECRET'] = settings.get('Google', 'Client Secret')
app.config['REDIRECT_URI'] = settings.get('Google','OATH Redirect URL')

oauth = OAuth()

google = oauth.remote_app('google',
base_url='https://www.google.com/accounts/',
authorize_url='https://accounts.google.com/o/oauth2/auth',
request_token_url=None,
request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
'response_type': 'code'},
access_token_url='https://accounts.google.com/o/oauth2/token',
access_token_method='POST',
access_token_params={'grant_type': 'authorization_code'},
consumer_key=app.config['GOOGLE_CLIENT_ID'],
consumer_secret=app.config['GOOGLE_CLIENT_SECRET'])


@app.route("/home")
def home():
    access_token = session.get('access_token')
    if access_token is None:
      return redirect(url_for('login'))
    
    access_token = access_token[0]
    
    
    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo', None, headers)
    try:
      res = urlopen(req)
      response = json.load(res) 
    except URLError as e:
      if e.code == 401:
        # Unauthorized - bad token
        session.pop('access_token', None)
        return redirect(url_for('login'))
    
    return render_template('home.html', title='Home')

@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route(app.config['REDIRECT_URI'])
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('createClass'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')

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